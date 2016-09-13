#
# Race Capture App
#
# Copyright (C) 2014-2016 Autosport Labs
#
# This file is part of the Race Capture App
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the GNU General Public License for more details. You should
# have received a copy of the GNU General Public License along with
# this code. If not, see <http://www.gnu.org/licenses/>.
import os.path
import kivy
kivy.require('1.9.1')
from kivy.logger import Logger
from kivy.app import Builder
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from autosportlabs.racecapture.views.analysis.analysisdata import CachingAnalysisDatastore
from autosportlabs.racecapture.views.analysis.analysismap import AnalysisMap
from autosportlabs.racecapture.views.analysis.channelvaluesview import ChannelValuesView
from autosportlabs.racecapture.views.analysis.addstreamview import AddStreamView
from autosportlabs.racecapture.views.analysis.sessionlistview import SessionListView
from autosportlabs.racecapture.views.analysis.flyinpanel import FlyinPanel
from autosportlabs.racecapture.views.analysis.markerevent import MarkerEvent, SourceRef
from autosportlabs.racecapture.views.analysis.linechart import LineChart
from autosportlabs.racecapture.views.file.loaddialogview import LoadDialog
from autosportlabs.racecapture.views.file.savedialogview import SaveDialog
from autosportlabs.racecapture.views.util.alertview import alertPopup
from autosportlabs.uix.color.colorsequence import ColorSequence
from autosportlabs.racecapture.theme.color import ColorScheme
from autosportlabs.help.helpmanager import HelpInfo
from autosportlabs.racecapture.views.analysis.analysisdata import CachingAnalysisDatastore
from kivy.core.window import Window

ANALYSIS_VIEW_KV = '''
<AnalysisView>:
    AnchorLayout:
        BoxLayout:
            orientation: 'vertical'
            BoxLayout:
                padding: (sp(10), sp(10), sp(10), sp(5))
                spacing: sp(10)       
                size_hint_y: 0.5
                orientation: 'horizontal'
                AnalysisMap:
                    id: analysismap
            AnchorLayout:
                spacing: sp(10)       
                padding: (sp(10), sp(5), sp(10), sp(10))
                size_hint_y: 0.5            
                AnchorLayout:
                    LineChart:
                        id: mainchart
                        on_channel_selected: root.on_channel_selected(*args)
                        on_marker: root.on_marker(*args)
                AnchorLayout:
                    anchor_x: 'right'
                    anchor_y: 'top'
                    ChannelValuesView:
                        size_hint_x: None
                        width: min(dp(320), 0.5 * root.width)
                        id: channelvalues

        FlyinPanel:
            id: laps_flyin
            BoxLayout:
                orientation: 'vertical'
                SessionListView:
                    size_hint_y: 0.9
                    id: sessions_view
                IconButton:
                    size_hint_y: 0.1
                    font_size: root.height * 0.1
                    text: u'\uf0fe'
                    on_release: root.on_add_stream()

            Label:
                text: 'Sessions'
                size_hint_y: 0.05
'''


class AnalysisView(Screen):
    SUGGESTED_CHART_CHANNELS = ['Speed']
    INIT_DATASTORE_TIMEOUT = 10.0
    _settings = None
    _databus = None
    _track_manager = None
    _popup = None
    _color_sequence = ColorSequence()
    sessions = ObjectProperty(None)
    Builder.load_string(ANALYSIS_VIEW_KV)

    def __init__(self, **kwargs):
        super(AnalysisView, self).__init__(**kwargs)
        self._datastore = CachingAnalysisDatastore()
        self.register_event_type('on_tracks_updated')
        self._databus = kwargs.get('dataBus')
        self._settings = kwargs.get('settings')
        self._track_manager = kwargs.get('track_manager')
        self.ids.sessions_view.bind(on_lap_selection=self.lap_selection)
        self.ids.channelvalues.color_sequence = self._color_sequence
        self.ids.mainchart.color_sequence = self._color_sequence
        self.stream_connecting = False
        Window.bind(mouse_pos=self.on_mouse_pos)
        Window.bind(on_motion=self.on_motion)
        self._layout_complete = False
        
    def on_motion(self, instance, event, motion_event):
        flyin = self.ids.laps_flyin
        if self.collide_point(motion_event.x, motion_event.y):
            if not flyin.flyin_collide_point(motion_event.x, motion_event.y):
                flyin.schedule_hide()

    def on_mouse_pos(self, x, pos):
        flyin = self.ids.laps_flyin
        x = pos[0]
        y = pos[1]
        self_collide = self.collide_point(x, y)
        flyin_collide = flyin.flyin_collide_point(x, y)
        laps_selected = self.ids.sessions_view.selected_count > 0

        if self_collide and not flyin_collide and laps_selected:
            flyin.schedule_hide()
        return False

    def on_sessions(self, instance, value):
        self.ids.channelvalues.sessions = value

    def lap_selection(self, instance, source_ref, selected):
        source_key = str(source_ref)
        if selected:
            self.ids.mainchart.add_lap(source_ref)
            self.ids.channelvalues.add_lap(source_ref)
            map_path_color = self._color_sequence.get_color(source_key)
            self.ids.analysismap.add_reference_mark(source_key, map_path_color)
            self._sync_analysis_map(source_ref.session)
            self._datastore.get_location_data(source_ref, lambda x: self.ids.analysismap.add_map_path(source_ref, x, map_path_color))

        else:
            self.ids.mainchart.remove_lap(source_ref)
            self.ids.channelvalues.remove_lap(source_ref)
            self.ids.analysismap.remove_reference_mark(source_key)
            self.ids.analysismap.remove_map_path(source_ref)

    def on_tracks_updated(self, track_manager):
        self.ids.analysismap.track_manager = track_manager

    def on_channel_selected(self, instance, value):
        self.ids.channelvalues.merge_selected_channels(value)

    def on_marker(self, instance, marker):
        source = marker.sourceref
        self.ids.channelvalues.update_reference_mark(source, marker.data_index)
        cache = self._datastore.get_location_data(source)
        if cache != None:
            try:
                point = cache[marker.data_index]
            except IndexError:
                point = cache[len(cache) - 1]
            self.ids.analysismap.update_reference_mark(source, point)

    def _sync_analysis_map(self, session):
        analysis_map = self.ids.analysismap
        current_track = analysis_map.track

        lat_avg, lon_avg = self._datastore.get_location_center([session])
        new_track = analysis_map.select_map(lat_avg, lon_avg)

        if current_track != new_track:
            # if a new track is selected, then
            # unselect all laps for all other sessions
            sessions_view = self.ids.sessions_view
            sessions_view.deselect_other_laps(session)

    def open_datastore(self):
        pass

    def on_add_stream(self, *args):
        self.show_add_stream_dialog()

    def on_stream_connected(self, instance, new_session_id):
        self.stream_connecting = False
        self._dismiss_popup()
        session = self._datastore.get_session_by_id(new_session_id)
        self.ids.sessions_view.append_session(session)
        self.check_load_suggested_lap(new_session_id)

    # The following selects a best lap if there are no other laps currently selected
    def check_load_suggested_lap(self, new_session_id):
        sessions_view = self.ids.sessions_view
        if len(sessions_view.selected_laps) == 0:
            best_lap = self._datastore.get_channel_min('LapTime', [new_session_id], ['LapCount'])
            best_lap_id = best_lap[1]
            if best_lap_id:
                Logger.info('AnalysisView: Convenience selected a suggested session {} / lap {}'.format(new_session_id, best_lap_id))
                main_chart = self.ids.mainchart
                main_chart.select_channels(AnalysisView.SUGGESTED_CHART_CHANNELS)
                self.ids.channelvalues.select_channels(AnalysisView.SUGGESTED_CHART_CHANNELS)
                sessions_view.select_lap(new_session_id, best_lap_id, True)
                HelpInfo.help_popup('suggested_lap', main_chart, arrow_pos='left_mid')
            else:
                Logger.info('AnalysisView: No best lap could be determined; selecting first lap by default for session {}'.format(new_session_id))
                sessions_view.select_lap(new_session_id, 0, True)

    def on_stream_connecting(self, *args):
        self.stream_connecting = True

    def show_add_stream_dialog(self):
        self.stream_connecting = False
        content = AddStreamView(settings=self._settings, datastore=self._datastore)
        content.bind(on_connect_stream_start=self.on_stream_connecting)
        content.bind(on_connect_stream_complete=self.on_stream_connected)
        content.bind(on_add_session=self.on_add_session)
        content.bind(on_delete_session=self.on_delete_session)
        content.bind(on_close=self.close_popup)

        popup = Popup(title="Add Session", content=content, size_hint=(0.8, 0.7))
        popup.bind(on_dismiss=self.popup_dismissed)
        popup.open()
        self._popup = popup

    def close_popup(self, *args):
        self._popup.dismiss()

    def on_add_session(self, instance, session):
        Logger.info("AnalysisView: on_add_session: {}".format(session))
        self.check_load_suggested_lap(session.session_id)
        self.ids.sessions_view.append_session(session)
        self.check_load_suggested_lap(session.session_id)        

    def on_delete_session(self, instance, session):
        self.ids.sessions_view.session_deleted(session)

    def init_view(self):
        self._init_datastore()
        mainchart = self.ids.mainchart
        mainchart.settings = self._settings
        mainchart.datastore = self._datastore
        channelvalues = self.ids.channelvalues
        channelvalues.datastore = self._datastore
        channelvalues.settings = self._settings
        self.ids.analysismap.track_manager = self._track_manager
        self.ids.analysismap.datastore = self._datastore
        self.ids.sessions_view.datastore = self._datastore
        self.ids.sessions_view.settings = self._settings
        self.ids.sessions_view.init_view()
        Clock.schedule_once(lambda dt: HelpInfo.help_popup('beta_analysis_welcome', self, arrow_pos='right_mid'), 0.5)

    def do_layout(self, *largs):
        super(AnalysisView, self).do_layout(largs)
        if not self._layout_complete:
            Clock.schedule_once(lambda dt: self.init_view(), 0.5)
        self._layout_complete = True
        
    def _init_datastore(self):
        dstore_path = self._settings.userPrefs.datastore_location
        if os.path.isfile(dstore_path):
            self._datastore.open_db(dstore_path)
        else:
            Logger.info('AnalysisView: creating datastore...')
            self._datastore.new(dstore_path)

    def popup_dismissed(self, *args):
        if self.stream_connecting:
            return True
        self._popup = None

    def _dismiss_popup(self, *args):
        if self._popup is not None:
            self._popup.dismiss()
            self._popup = None

