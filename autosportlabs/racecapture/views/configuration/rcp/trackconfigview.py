import kivy
import time
kivy.require('1.9.1')

from kivy.properties import ObjectProperty
from kivy.core.clipboard import Clipboard
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.logger import Logger
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.app import Builder
from helplabel import HelpLabel
from fieldlabel import FieldLabel
from settingsview import *
from valuefield import FloatValueField
from autosportlabs.racecapture.config.rcpconfig import GpsConfig
from autosportlabs.racecapture.views.util.alertview import alertPopup
from autosportlabs.racecapture.views.tracks.tracksview import TrackInfoView, TracksView
from autosportlabs.racecapture.views.configuration.rcp.trackselectview import TrackSelectView
from autosportlabs.racecapture.views.configuration.baseconfigview import BaseConfigView
from autosportlabs.racecapture.config.rcpconfig import *
from autosportlabs.uix.toast.kivytoast import toast
from autosportlabs.widgets.scrollcontainer import ScrollContainer
from autosportlabs.racecapture.views.util.alertview import editor_popup
from autosportlabs.racecapture.tracks.trackmanager import TrackManager, TrackMap
from autosportlabs.racecapture.views.configuration.rcp.track.trackbuilder import TrackBuilderView

TRACK_CONFIG_VIEW_KV = 'autosportlabs/racecapture/views/configuration/rcp/trackconfigview.kv'


GPS_STATUS_POLL_INTERVAL = 1.0
GPS_NOT_LOCKED_COLOR = [0.7, 0.7, 0.0, 1.0]
GPS_LOCKED_COLOR = [0.0, 1.0, 0.0, 1.0]

class SectorPointView(BoxLayout):
    databus = None
    point = None
    def __init__(self, **kwargs):
        super(SectorPointView, self).__init__(**kwargs)
        self.databus = kwargs.get('databus')
        self.register_event_type('on_config_changed')
        title = kwargs.get('title', None)
        if title:
            self.setTitle(title)
        Clock.schedule_interval(lambda dt: self.update_gps_status(), GPS_STATUS_POLL_INTERVAL)

    def _get_gps_quality(self):
        gps_quality = self.databus.channel_data.get('GPSQual')
        return 0 if gps_quality is None else int(gps_quality)

    def update_gps_status(self, *args):
        gps_quality = self._get_gps_quality()
        self.ids.gps_target.color = GPS_NOT_LOCKED_COLOR if gps_quality < GpsConfig.GPS_QUALITY_2D else GPS_LOCKED_COLOR

    def on_config_changed(self):
        pass

    def setTitle(self, title):
        kvFind(self, 'rcid', 'title').text = title

    def on_update_target(self, *args):
        try:
            if self._get_gps_quality() >= GpsConfig.GPS_QUALITY_2D:
                channel_data = self.databus.channel_data
                point = self.point
                point.latitude = channel_data.get('Latitude')
                point.longitude = channel_data.get('Longitude')
                self._refresh_point_view()
                self.dispatch('on_config_changed')
                toast('Target updated')
            else:
                toast('No GPS Fix', True)
        except Exception as e:
            toast('Error reading GPS target')

    def _on_edited(self, instance, value):
        self.set_point(value)
        self.dispatch('on_config_changed')

    def on_customize(self, *args):
        if self.point:
            content = GeoPointEditor(point=self.point, databus=self.databus)
            popup = Popup(title='Edit Track Target',
                          content=content,
                          size_hint=(None, None), size=(dp(500), dp(220)))
            content.bind(on_close=lambda *args:popup.dismiss())
            content.bind(on_point_edited=self._on_edited)
            popup.open()

    def _refresh_point_view(self):
        self.ids.lat.text = str(self.point.latitude)
        self.ids.lon.text = str(self.point.longitude)

    def set_point(self, point):
        self.point = point
        self._refresh_point_view()

class GeoPointEditor(BoxLayout):
    def __init__(self, point, databus, **kwargs):
        super(GeoPointEditor, self).__init__(**kwargs)
        self.point = point
        self.databus = databus
        self.register_event_type('on_point_edited')
        self.register_event_type('on_close')
        self._refresh_view(self.point.latitude, self.point.longitude)
        self.ids.lat.set_next(self.ids.lon)
        self.ids.lon.set_next(self.ids.lat)
        Clock.schedule_interval(self.update_gps_status, GPS_STATUS_POLL_INTERVAL)

    def on_latitude(self, instance, value):
        pass

    def on_longitude(self, instance, value):
        pass

    def _refresh_view(self, latitude, longitude):
        self.ids.lat.text = str(latitude)
        self.ids.lon.text = str(longitude)

    def on_point_edited(self, *args):
        pass

    def on_close(self, *args):
        pass

    def on_paste_point(self, *args):
        try:
            point_string = Clipboard.get('UTF8_STRING')
            lat_lon = point_string.split(",")
            lat = float(lat_lon[0])
            lon = float(lat_lon[1])
            self.ids.lat.text = str(lat)
            self.ids.lon.text = str(lon)
        except ValueError as e:
            Logger.error("GeoPointEditor: error handling paste: {}".format(e))
            toast('Required format is: Latitude, Longitude\nin NN.NNNNN decimal format', True)

    def update_gps_status(self, dt, *args):
        gps_quality = self._get_gps_quality()
        self.ids.gps_target.color = GPS_NOT_LOCKED_COLOR if gps_quality < GpsConfig.GPS_QUALITY_2D else GPS_LOCKED_COLOR

    def _get_gps_quality(self):
        gps_quality = self.databus.channel_data.get('GPSQual')
        return 0 if gps_quality is None else int(gps_quality)

    def on_update_target(self, *args):
        try:
            if self._get_gps_quality() >= GpsConfig.GPS_QUALITY_2D:
                channel_data = self.databus.channel_data
                self._refresh_view(channel_data.get('Latitude'), channel_data.get('Longitude'))
            else:
                toast('No GPS Fix', True)
        except Exception:
            toast('Error reading GPS target')

    def close(self):
        Clock.unschedule(self.update_gps_status)
        point = self.point
        try:
            point.latitude = float(self.ids.lat.text)
            point.longitude = float(self.ids.lon.text)
            self.dispatch('on_point_edited', self.point)
        except ValueError as e:
            Logger.error("GeoPointEditor: error closing: {}".format(e))
            toast('NN.NNNNN decimal latitude/longitude format required', True)
        self.dispatch('on_close')


class EmptyTrackDbView(BoxLayout):
    def __init__(self, **kwargs):
        super(EmptyTrackDbView, self).__init__(**kwargs)

class TrackDbItemView(BoxLayout):
    track = None
    trackInfoView = None
    index = 0
    def __init__(self, **kwargs):
        super(TrackDbItemView, self).__init__(**kwargs)
        track = kwargs.get('track', None)
        self.index = kwargs.get('index', 0)
        trackInfoView = kvFind(self, 'rcid', 'trackinfo')
        trackInfoView.setTrack(track)
        self.track = track
        self.trackInfoView = trackInfoView
        self.register_event_type('on_remove_track')

    def on_remove_track(self, index):
        pass

    def removeTrack(self):
        self.dispatch('on_remove_track', self.index)

class TrackSelectionPopup(BoxLayout):
    track_browser = None
    def __init__(self, **kwargs):
        super(TrackSelectionPopup, self).__init__(**kwargs)
        self.register_event_type('on_tracks_selected')
        track_manager = kwargs.get('track_manager', None)
        track_browser = kvFind(self, 'rcid', 'browser')
        track_browser.set_trackmanager(track_manager)
        track_browser.init_view()
        self.track_browser = track_browser

    def on_tracks_selected(self, selectedTrackIds):
        pass

    def confirmAddTracks(self):
        self.dispatch('on_tracks_selected', self.track_browser.selectedTrackIds)

class AutomaticTrackConfigScreen(Screen):
    trackDb = None
    tracksGrid = None
    track_manager = ObjectProperty(None)
    TRACK_ITEM_MIN_HEIGHT = 200
    trackSelectionPopup = None
    def __init__(self, **kwargs):
        super(AutomaticTrackConfigScreen, self).__init__(**kwargs)
        self.tracksGrid = kvFind(self, 'rcid', 'tracksgrid')
        self.register_event_type('on_tracks_selected')
        self.register_event_type('on_modified')

    def on_modified(self, *args):
        pass

    def on_config_updated(self, trackDb):
        self.trackDb = trackDb
        self.init_tracks_list()

    def on_track_manager(self, instance, value):
        self.track_manager = value
        self.init_tracks_list()

    def on_tracks_selected(self, instance, selectedTrackIds):
        if self.trackDb:
            failures = False
            for trackId in selectedTrackIds:
                trackMap = self.track_manager.get_track_by_id(trackId)
                if trackMap:
                    startFinish = trackMap.start_finish_point
                    if startFinish and startFinish.latitude and startFinish.longitude:
                        Logger.info("TrackConfigView:  adding track " + str(trackMap))
                        track = Track.fromTrackMap(trackMap)
                        self.trackDb.tracks.append(track)
                    else:
                        failures = True
            if failures:
                alertPopup('Cannot Add Tracks', 'One or more tracks could not be added due to missing start/finish points.\n\nPlease check for track map updates and try again.')
            self.init_tracks_list()
            self.trackSelectionPopup.dismiss()
            self.trackDb.stale = True
            self.dispatch('on_modified')

    def on_add_track_db(self):
        trackSelectionPopup = TrackSelectionPopup(track_manager=self.track_manager)
        popup = Popup(title='Add Race Tracks', content=trackSelectionPopup, size_hint=(0.9, 0.9))
        trackSelectionPopup.bind(on_tracks_selected=self.on_tracks_selected)
        popup.open()
        self.trackSelectionPopup = popup

    def init_tracks_list(self):
        if self.track_manager and self.trackDb:
            matchedTracks = []
            for track in self.trackDb.tracks:
                matchedTrack = self.track_manager.find_track_by_short_id(track.trackId)
                if matchedTrack:
                    matchedTracks.append(matchedTrack)

            grid = kvFind(self, 'rcid', 'tracksgrid')
            grid.clear_widgets()
            if len(matchedTracks) == 0:
                grid.add_widget(EmptyTrackDbView())
                self.tracksGrid.height = dp(self.TRACK_ITEM_MIN_HEIGHT)
            else:
                self.tracksGrid.height = dp(self.TRACK_ITEM_MIN_HEIGHT) * (len(matchedTracks) + 1)
                index = 0
                for track in matchedTracks:
                    trackDbView = TrackDbItemView(track=track, index=index)
                    trackDbView.bind(on_remove_track=self.on_remove_track)
                    trackDbView.size_hint_y = None
                    trackDbView.height = dp(self.TRACK_ITEM_MIN_HEIGHT)
                    grid.add_widget(trackDbView)
                    index += 1

            self.disableView(False)

    def on_remove_track(self, instance, index):
            try:
                del self.trackDb.tracks[index]
                self.init_tracks_list()
                self.trackDb.stale = True
                self.dispatch('on_modified')

            except Exception as detail:
                Logger.error('AutomaticTrackConfigScreen: Error removing track from list ' + str(detail))

    def disableView(self, disabled):
        kvFind(self, 'rcid', 'addtrack').disabled = disabled

class SingleAutoConfigScreen(Screen):
    def __init__(self, track_manager, **kwargs):
        super(SingleAutoConfigScreen, self).__init__(**kwargs)
        self._track_manager = track_manager
        self.track_cfg = None

    def _update_track(self):
        if self.track_cfg is None:
            return
        track = self._track_manager.find_track_by_short_id(self.track_cfg.track.trackId)
        self.ids.track_info.setTrack(track)
        self.ids.info_message.text = 'Waiting to detect track' if track is None else ''

    def on_config_updated(self, track_cfg):
        self.track_cfg = track_cfg
        self._update_track()

    def on_pre_enter(self, *args):
        self._update_track()

class CustomTrackConfigScreen(Screen):

    def __init__(self, track_manager, databus, rc_api, **kwargs):
        super(CustomTrackConfigScreen, self).__init__(**kwargs)
        self._track_manager = track_manager
        self._databus = databus
        self._rc_api = rc_api
        self.register_event_type('on_advanced_editor')
        self.track_cfg = None
        self._init_ui()

    def on_advanced_track_editor(self, *args):
        self.dispatch('on_advanced_editor')

    def on_advanced_editor(self):
        pass

    def _init_ui(self):
        # if we're on a mobile platform we get a tool to interactively design a track map
        track_builder_button = Button(size_hint=(0.2, 0.2), text='Create Track', on_press=self.track_builder)
        self.ids.create_track_container.add_widget(track_builder_button)

    def track_builder(self, *args):
        def popup_dismissed(instance):
            content.cleanup()
            
        def on_track_complete(instance, track_map):
            popup.dismiss()
            self._track_manager.add_track(track_map)
            self.track_cfg.track.import_trackmap(track_map)
            self._update_track()
            
        content = TrackBuilderView(databus=self._databus, rc_api=self._rc_api)
        popup = Popup(title='Track Builder', content=content, size_hint=(1.0, 1.0), auto_dismiss=True)
        popup.bind(on_dismiss=popup_dismissed)
        content.bind(on_track_complete=on_track_complete)
        popup.open()

    def _update_track(self):
        if self.track_cfg is None:
            return

        track = self._track_manager.find_track_by_short_id(self.track_cfg.track.trackId)
        self.ids.track_info.setTrack(track)
        self.ids.info_message.text = 'No track map defined' if track is None else ''

    def on_pre_enter(self, *args):
        self._update_track()

    def on_config_updated(self, track_cfg):
        self.track_cfg = track_cfg
        self._update_track()

class ManualTrackConfigScreen(Screen):
    trackCfg = None
    sectorViews = []
    startLineView = None
    finishLineView = None
    separateStartFinish = False
    _databus = None

    def __init__(self, databus, rc_api, **kwargs):
        super(ManualTrackConfigScreen, self).__init__(**kwargs)
        self._databus = databus
        self._rc_api = rc_api
        sepStartFinish = kvFind(self, 'rcid', 'sepStartFinish')
        sepStartFinish.bind(on_setting=self.on_separate_start_finish)
        sepStartFinish.setControl(SettingsSwitch())

        self.startLineView = self.ids.start_line
        self.startLineView.databus = self._databus
        self.finishLineView = self.ids.finish_line
        self.finishLineView.databus = self._databus

        self.separateStartFinish = False
        sectorsContainer = self.ids.sectors_grid
        self.sectorsContainer = sectorsContainer
        self.initSectorViews()

        sectorsContainer.height = dp(35) * CONFIG_SECTOR_COUNT
        sectorsContainer.size_hint = (1.0, None)

        self.register_event_type('on_modified')

    def on_modified(self, *args):
        pass

    def on_separate_start_finish(self, instance, value):
        if self.trackCfg:
            self.trackCfg.track.trackType = 1 if value else 0
            self.trackCfg.stale = True
            self.dispatch('on_modified')
            self.separateStartFinish = value
            self.updateTrackViewState()

    def initSectorViews(self):

        sectorsContainer = self.sectorsContainer
        sectorsContainer.clear_widgets()

        self.startLineView.bind(on_config_changed=self.on_config_changed)
        self.finishLineView.bind(on_config_changed=self.on_config_changed)

        self.updateTrackViewState()

    def on_config_changed(self, *args):
        self.trackCfg.stale = True
        self.dispatch('on_modified')

    def updateTrackViewState(self):
        if not self.separateStartFinish:
            self.startLineView.setTitle('Start / Finish')
            self.finishLineView.setTitle('- - -')
            self.finishLineView.disabled = True
        else:
            self.startLineView.setTitle('Start Line')
            self.finishLineView.setTitle('Finish Line')
            self.finishLineView.disabled = False

    def on_config_updated(self, trackCfg):
        separateStartFinishSwitch = kvFind(self, 'rcid', 'sepStartFinish')
        self.separateStartFinish = trackCfg.track.trackType == TRACK_TYPE_STAGE
        separateStartFinishSwitch.setValue(self.separateStartFinish)

        sectorsContainer = self.sectorsContainer

        sectorsContainer.clear_widgets()
        for i in range(0, len(trackCfg.track.sectors)):
            sectorView = SectorPointView(title='Sector ' + str(i), databus=self._databus)
            sectorView.bind(on_config_changed=self.on_config_changed)
            sectorsContainer.add_widget(sectorView)
            sectorView.set_point(trackCfg.track.sectors[i])
            self.sectorViews.append(sectorView)

        self.startLineView.set_point(trackCfg.track.startLine)
        self.finishLineView.set_point(trackCfg.track.finishLine)

        self.trackCfg = trackCfg
        self.updateTrackViewState()


class TrackConfigView(BaseConfigView):

    Builder.load_file(TRACK_CONFIG_VIEW_KV)

    def __init__(self, settings, databus, rc_api, track_manager, **kwargs):
        super(TrackConfigView, self).__init__(**kwargs)

        self._track_db_capable = False

        self.trackCfg = None
        self.trackDb = None

        self._databus = databus
        self._rc_api = rc_api
        self._settings = settings
        self._track_manager = track_manager

        self.autoConfigView = None
        self.manualTrackConfigView = None
        self.single_autoconfig_screen = None
        self._custom_track_screen = None

        self.register_event_type('on_config_updated')

        screenMgr = kvFind(self, 'rcid', 'screenmgr')
        self.screenManager = screenMgr

        autoDetect = self.ids.auto_detect
        autoDetect.bind(on_setting=self.on_auto_detect)
        autoDetect.setControl(SettingsSwitch())

    def _get_track_db_view(self):
        if self.autoConfigView is None:
            self.autoConfigView = AutomaticTrackConfigScreen(name='trackdb')
            self.autoConfigView.bind(on_modified=self.on_modified)
            self.autoConfigView.track_manager = self._track_manager
            if self.trackDb is not None:
                self.autoConfigView.on_config_updated(self.trackDb)
        return self.autoConfigView

    def _get_single_track_view(self):
        if self.single_autoconfig_screen is None:
            self.single_autoconfig_screen = SingleAutoConfigScreen(name='single', track_manager=self._track_manager)
            if self.trackCfg is not None:
                self.single_autoconfig_screen.on_config_updated(self.trackCfg)
        return self.single_autoconfig_screen

    def _get_custom_track_screen(self):
        if self._custom_track_screen is None:
            self._custom_track_screen = CustomTrackConfigScreen(name='custom', track_manager=self._track_manager, rc_api=self._rc_api, databus=self._databus)
            self._custom_track_screen.bind(on_advanced_editor=self._on_advanced_editor)
            self._custom_track_screen.on_config_updated(self.trackCfg)
        return self._custom_track_screen

    def _get_advanced_editor_screen(self, *args):
        if self.manualTrackConfigView is None:
            self.manualTrackConfigView = ManualTrackConfigScreen(name='advanced', databus=self._databus, rc_api=self._rc_api)
            self.manualTrackConfigView.bind(on_modified=self.on_modified)
            if self.trackCfg is not None:
                self.manualTrackConfigView.on_config_updated(self.trackCfg)
        return self.manualTrackConfigView

    def on_tracks_updated(self, track_manager):
        if self.autoConfigView is not None:
            self.autoConfigView.track_manager = track_manager

    def on_config_updated(self, rcpCfg):
        trackCfg = rcpCfg.trackConfig
        trackDb = rcpCfg.trackDb

        self._track_db_capable = rcpCfg.capabilities.storage.tracks > 0

        self.ids.auto_detect.setValue(trackCfg.autoDetect)

        if self.manualTrackConfigView is not None:
            self.manualTrackConfigView.on_config_updated(trackCfg)

        if self.autoConfigView is not None:
            self.autoConfigView.on_config_updated(trackDb)

        if self.single_autoconfig_screen is not None:
            self.single_autoconfig_screen.on_config_updated(trackCfg)

        if self._custom_track_screen is not None:
            self._custom_track_screen.on_config_updated(trackCfg)

        self.trackCfg = trackCfg
        self.trackDb = trackDb

        self._select_screen()

    def _select_screen(self):
        auto_detect_enabled = self.ids.auto_detect.control.active

        next_screen = None
        if auto_detect_enabled:
            if self._track_db_capable:
                next_screen = self._get_track_db_view()
            else:
                next_screen = self._get_single_track_view()
        else:
            next_screen = self._get_custom_track_screen()

        self._switch_to_screen(next_screen)

    def _switch_to_screen(self, screen):
        if self.screenManager.current_screen != screen:
            self.screenManager.switch_to(screen)

    def on_auto_detect(self, instance, value):
        track_cfg = self.trackCfg
        if track_cfg:
            if value == False and track_cfg.autoDetect == True:
                track_cfg.track.trackId = 0
            track_cfg.autoDetect = value
            track_cfg.stale = True
            self.dispatch('on_modified')
        self._select_screen()

    def _on_advanced_editor(self, *args):
        self._switch_to_screen(self._get_advanced_editor_screen())

SIMPLE_TRACK_CONFIG_VIEW = """
<SimpleTrackConfigView>:
    GridLayout:
        spacing: [0, dp(20)]
        padding: dp(20)
        id: content
        cols: 1
        GridLayout:
            cols: 1
            size_hint_y: 0.3
            SettingsView:
                id: current_track
                label_text: 'Track: Unknown'
            SettingsView:
                id: custom_track
                label_text: 'Custom Track'
        AnchorLayout:
            id: custom
            size_hint_y: 0.7
            TrackMapView:
                id: custom_track_view
            FieldLabel:
                size_hint_y: 0.1
                id: custom_track_note
                text: 'No Custom Track defined'
            AnchorLayout:
                anchor_x: 'right'
                Button:
                    size_hint: (0.3, 0.3)
                    text: 'Build Track'
                    on_press: root.track_builder(*args)

"""

class SimpleTrackConfigView(BaseConfigView):

    Builder.load_string(SIMPLE_TRACK_CONFIG_VIEW)

    def __init__(self, rc_api, databus, settings, track_manager, **kwargs):
        super(SimpleTrackConfigView, self).__init__(**kwargs)

        self._databus = databus
        self._rc_api = rc_api
        self._settings = settings
        self._track_manager = track_manager
        self._track_config = None

        self.register_event_type('on_config_updated')

        button = Button(text='Set Track')
        button.bind(on_press=self.on_set_track_press)
        self.ids.current_track.setControl(button)

        self.ids.custom_track.bind(on_setting=self.on_custom_track)
        self.ids.custom_track.setControl(SettingsSwitch())

        self._track_select_view = None
        self._popup = None
        self._manual_track_config_view = None
        self._old_track_id = None

    def on_set_track_press(self, instance):
        content = TrackSelectView(self._track_manager)
        self._track_select_view = content
        self._popup = editor_popup("Select your track", content, self._on_track_select_close)
        self._popup.open()

    def _on_track_select_close(self, instance, answer):
        if answer:
            if self._track_config:
                selected_track = self._track_select_view.selected_track
                Logger.info("TempTrackConfigView: setting track: {}".format(selected_track))
                track_config = Track.fromTrackMap(selected_track)
                self._track_config.track = track_config
                self._track_config.stale = True
                self.dispatch('on_modified')

                track_name = selected_track.name
                configuration_name = selected_track.configuration
                if configuration_name and len(configuration_name):
                    track_name += ' (' + configuration_name + ')'

                self.ids.current_track.label_text = 'Track: ' + track_name
        self._popup.dismiss()

    def on_custom_track(self, instance, value):
        # Show or hide custom start/finish points
        if value:
            if self._track_config:
                if self._track_config.track.trackId > 0:
                    self._old_track_id = self._track_config.track.trackId

            track = Track()
            track.trackId = 0
            track.startLine = self._start_line.point

            self._track_config.track = track
            self._track_config.stale = True
            self.dispatch('on_modified')

            self.ids.current_track.control.disabled = True
            self.ids.current_track.label_text = 'Track: Custom'
        else:
            # Revert
            if self._old_track_id:
                track_map = self._track_manager.find_track_by_short_id(self._old_track_id)
                track = Track.fromTrackMap(track_map)

                if track_map is None:
                    track_name = 'Track not found'
                else:
                    track_name = track_map.name
                    configuration_name = track_map.configuration
                    if configuration_name and len(configuration_name):
                        track_name += ' (' + configuration_name + ')'

                self.ids.current_track.label_text = 'Track: ' + track_name
            else:
                self.ids.current_track.label_text = 'Track: Unknown'

                track = Track()
                track.trackId = -1
                track.startLine = GeoPoint()

            self._track_config.track = track
            self._track_config.stale = True
            self.dispatch('on_modified')
            self.ids.current_track.control.disabled = False

    def _on_custom_change(self, *args):
        Logger.info("TempTrackConfig: on_custom_modified: {}".format(args))

        if self._track_config:
            # Get point, use it to set custom start/finish
            track = Track()
            track.trackId = 0
            track.startLine = self._start_line.point

            self._track_config.track = track
            self._track_config.stale = True
            self.dispatch('on_modified')

    def on_config_updated(self, rcp_config):
        self._track_config = rcp_config.trackConfig

        if rcp_config.trackConfig.track.trackId > 0 or (rcp_config.trackConfig.track.startLine.latitude == 0 and
                                                        rcp_config.trackConfig.track.startLine.latitude == 0):
            track = self._track_manager.find_track_by_short_id(rcp_config.trackConfig.track.trackId)

            if track is None:
                track_name = 'Track not found'
            else:
                track_name = track.name
                configuration_name = track.configuration
                if configuration_name and len(configuration_name):
                    track_name += ' (' + configuration_name + ')'

            self.ids.current_track.label_text = 'Track: ' + track_name
        elif rcp_config.trackConfig.track.trackId == 0:
            Logger.info("TempTrackConfig: custom start/finish: {}".format(rcp_config.trackConfig.track.startLine.toJson()))
            self._start_line.set_point(rcp_config.trackConfig.track.startLine)
            self.ids.custom_track.setValue(True)
