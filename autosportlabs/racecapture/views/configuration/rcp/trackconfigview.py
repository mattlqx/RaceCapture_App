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
from iconbutton import LabelIconButton
from autosportlabs.racecapture.config.rcpconfig import GpsConfig, GpsSample
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
    def __init__(self, **kwargs):
        super(SectorPointView, self).__init__(**kwargs)
        self.gps_sample = kwargs.get('gps_sample')
        self.register_event_type('on_config_changed')
        self.point = None
        title = kwargs.get('title', None)
        if title:
            self.set_title(title)
        Clock.schedule_interval(self.update_gps_status, GPS_STATUS_POLL_INTERVAL)

    def _get_gps_quality(self):
        return 0 if self.gps_sample is None else self.gps_sample.gps_qual

    def update_gps_status(self, *args):
        self.ids.gps_target.color = GPS_NOT_LOCKED_COLOR if self._get_gps_quality() < GpsConfig.GPS_QUALITY_2D else GPS_LOCKED_COLOR

    def on_config_changed(self):
        pass

    def set_title(self, title):
        self.ids.title.text = title

    def on_update_target(self, *args):
        try:
            if self._get_gps_quality() >= GpsConfig.GPS_QUALITY_2D:
                point = self.point
                point.latitude = self.gps_sample.latitude
                point.longitude = self.gps_sample.longitude
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
            content = GeoPointEditor(self.point, self.gps_sample)
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
    def __init__(self, point, gps_sample, **kwargs):
        super(GeoPointEditor, self).__init__(**kwargs)
        self.point = point
        self._gps_sample = gps_sample
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

    def update_gps_status(self, *args):
        gps_quality = self._get_gps_quality()
        self.ids.gps_target.color = GPS_NOT_LOCKED_COLOR if gps_quality < GpsConfig.GPS_QUALITY_2D else GPS_LOCKED_COLOR

    def _get_gps_quality(self):
        return 0 if self._gps_sample is None else self._gps_sample.gps_qual

    def on_update_target(self, *args):
        try:
            if self._get_gps_quality() >= GpsConfig.GPS_QUALITY_2D:
                self._refresh_view(self._gps_sample.latitude, self._gps_sample.longitude)
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
    def __init__(self, **kwargs):
        super(TrackDbItemView, self).__init__(**kwargs)
        track = kwargs.get('track', None)
        self.index = kwargs.get('index', 0)
        self.ids.trackinfo.setTrack(track)
        self.track = track
        self.register_event_type('on_remove_track')

    def on_remove_track(self, index):
        pass

    def remove_track(self):
        self.dispatch('on_remove_track', self.index)

class TrackSelectionPopup(BoxLayout):
    def __init__(self, **kwargs):
        super(TrackSelectionPopup, self).__init__(**kwargs)
        self.register_event_type('on_tracks_selected')
        track_manager = kwargs.get('track_manager', None)
        track_browser = self.ids.browser
        track_browser.set_trackmanager(track_manager)
        track_browser.init_view()
        self.track_browser = track_browser

    def on_tracks_selected(self, selectedTrackIds):
        pass

    def confirm_add_tracks(self):
        self.dispatch('on_tracks_selected', self.track_browser.selectedTrackIds)

class AutomaticTrackConfigScreen(Screen):
    track_manager = ObjectProperty(None)
    TRACK_ITEM_MIN_HEIGHT = 200
    def __init__(self, **kwargs):
        super(AutomaticTrackConfigScreen, self).__init__(**kwargs)
        self._track_select_popup = None
        self._track_db = None
        self._tracks_grid = self.ids.tracksgrid
        self.register_event_type('on_tracks_selected')
        self.register_event_type('on_modified')

    def on_modified(self, *args):
        pass

    def on_config_updated(self, track_db):
        self._track_db = track_db
        self.init_tracks_list()

    def on_track_manager(self, instance, value):
        self.track_manager = value
        self.init_tracks_list()

    def on_tracks_selected(self, instance, selected_track_ids):
        if self._track_db:
            failures = False
            for trackId in selected_track_ids:
                trackMap = self.track_manager.get_track_by_id(trackId)
                if trackMap:
                    startFinish = trackMap.start_finish_point
                    if startFinish and startFinish.latitude and startFinish.longitude:
                        Logger.info("TrackConfigView:  adding track " + str(trackMap))
                        track = Track.fromTrackMap(trackMap)
                        self._track_db.tracks.append(track)
                    else:
                        failures = True
            if failures:
                alertPopup('Cannot Add Tracks', 'One or more tracks could not be added due to missing start/finish points.\n\nPlease check for track map updates and try again.')
            self.init_tracks_list()
            self._track_select_popup.dismiss()
            self._track_db.stale = True
            self.dispatch('on_modified')

    def on_add_track_db(self):
        content = TrackSelectionPopup(track_manager=self.track_manager)
        popup = Popup(title='Add Race Tracks', content=content, size_hint=(0.9, 0.9))
        content.bind(on_tracks_selected=self.on_tracks_selected)
        popup.open()
        self._track_select_popup = popup

    def init_tracks_list(self):
        if self.track_manager and self._track_db:
            matched_tracks = []
            for track in self._track_db.tracks:
                matched_track = self.track_manager.find_track_by_short_id(track.trackId)
                if matched_track:
                    matched_tracks.append(matched_track)

            grid = self.ids.tracksgrid
            grid.clear_widgets()
            if len(matched_tracks) == 0:
                grid.add_widget(EmptyTrackDbView())
                self._tracks_grid.height = dp(self.TRACK_ITEM_MIN_HEIGHT)
            else:
                self._tracks_grid.height = dp(self.TRACK_ITEM_MIN_HEIGHT) * (len(matched_tracks) + 1)
                index = 0
                for track in matched_tracks:
                    track_db_view = TrackDbItemView(track=track, index=index)
                    track_db_view.bind(on_remove_track=self.on_remove_track)
                    track_db_view.size_hint_y = None
                    track_db_view.height = dp(self.TRACK_ITEM_MIN_HEIGHT)
                    grid.add_widget(track_db_view)
                    index += 1

            self.disableView(False)

    def on_remove_track(self, instance, index):
            try:
                del self._track_db.tracks[index]
                self.init_tracks_list()
                self._track_db.stale = True
                self.dispatch('on_modified')

            except Exception as detail:
                Logger.error('AutomaticTrackConfigScreen: Error removing track from list ' + str(detail))

    def disableView(self, disabled):
        self.ids.addtrack.disabled = disabled

class SingleAutoConfigScreen(Screen):
    def __init__(self, track_manager, gps_sample, **kwargs):
        super(SingleAutoConfigScreen, self).__init__(**kwargs)
        self.register_event_type('on_modified')
        self._track_manager = track_manager
        self._gps_sample = gps_sample
        self._track_cfg = None

    def on_modified(self, *args):
        pass

    def _update_track(self):
        if self._track_cfg is None:
            return
        track = self._track_manager.find_track_by_short_id(self._track_cfg.track.trackId)
        self.ids.track_info.setTrack(track)
        self.ids.info_message.text = 'Waiting to detect track' if track is None else ''

    def on_config_updated(self, track_cfg):
        self._track_cfg = track_cfg
        self._update_track()

    def on_pre_enter(self, *args):
        self._update_track()

    def on_set_track_press(self, *args):
        def on_track_select_close(instance, answer):
            if answer:
                selected_track = content.selected_track
                if selected_track is None:
                    toast('Please select a track')
                    return
                if self._track_cfg:
                    Logger.info("SingleAutoConfigScreen: setting track: {}".format(selected_track.name))
                    track_cfg = Track.fromTrackMap(selected_track)
                    self._track_cfg.track = track_cfg
                    self._track_cfg.stale = True
                    self._update_track()
                    self.dispatch('on_modified')
            popup.dismiss()

        # use the current location, if available
        current_point = self._gps_sample.geopoint if self._gps_sample.is_locked else None
        content = TrackSelectView(track_manager=self._track_manager, current_location=current_point)
        popup = editor_popup("Select a track", content, on_track_select_close)
        popup.open()


class CustomTrackConfigScreen(Screen):
    def __init__(self, track_manager, databus, rc_api, **kwargs):
        super(CustomTrackConfigScreen, self).__init__(**kwargs)
        self._track_manager = track_manager
        self._databus = databus
        self._rc_api = rc_api
        self.register_event_type('on_advanced_editor')
        self._track_cfg = None
        self.register_event_type('on_modified')

    def on_modified(self, *args):
        pass

    def on_advanced_track_editor(self, *args):
        self.dispatch('on_advanced_editor')

    def on_advanced_editor(self):
        pass

    def track_builder(self, *args):
        def popup_dismissed(instance):
            content.cleanup()

        def on_track_complete(instance, track_map):
            popup.dismiss()
            self._track_manager.add_track(track_map)
            self._track_cfg.track.import_trackmap(track_map)
            self._track_cfg.stale = True
            self._update_track()
            self.dispatch('on_modified')
        
        def on_close(instance, answer):
            popup.dismiss()
            
        content = TrackBuilderView(databus=self._databus, rc_api=self._rc_api, track_manager=self._track_manager)
        popup = editor_popup("Track Builder", content, on_close, hide_ok=True, size_hint=(1.0,1.0))        
        content.bind(on_track_complete=on_track_complete)
        popup.open()

    def _update_track(self):
        if self._track_cfg is None:
            return

        track = self._track_manager.find_track_by_short_id(self._track_cfg.track.trackId)
        self.ids.track_info.setTrack(track)
        self.ids.info_message.text = 'Press (+) to create a your first track map' if track is None else ''

    def on_pre_enter(self, *args):
        self._update_track()

    def on_config_updated(self, track_cfg):
        self._track_cfg = track_cfg
        self._update_track()

class ManualTrackConfigScreen(Screen):
    def __init__(self, gps_sample, **kwargs):
        super(ManualTrackConfigScreen, self).__init__(**kwargs)
        self._track_cfg = None
        self._gps_sample = gps_sample
        self.ids.sep_startfinish.bind(on_setting=self.on_separate_start_finish)
        self.ids.sep_startfinish.setControl(SettingsSwitch())

        self.ids.start_line.gps_sample = gps_sample
        self.ids.finish_line.gps_sample = gps_sample

        self.separate_startfinish = False
        self._init_sector_views()

        sectors_container = self.ids.sectors_grid
        sectors_container.height = dp(35) * CONFIG_SECTOR_COUNT
        sectors_container.size_hint = (1.0, None)

        self.register_event_type('on_modified')

    def on_modified(self, *args):
        pass

    def on_separate_start_finish(self, instance, value):
        if self._track_cfg:
            self._track_cfg.track.trackType = 1 if value else 0
            self._track_cfg.stale = True
            self.dispatch('on_modified')
            self.separate_startfinish = value
            self.update_trackview_state()

    def _init_sector_views(self):

        self.ids.sectors_grid.clear_widgets()

        self.ids.start_line.bind(on_config_changed=self.on_config_changed)
        self.ids.finish_line.bind(on_config_changed=self.on_config_changed)

        self.update_trackview_state()

    def on_config_changed(self, *args):
        self._track_cfg.stale = True
        self.dispatch('on_modified')

    def update_trackview_state(self):
        if not self.separate_startfinish:
            self.ids.start_line.set_title('Start / Finish')
            self.ids.finish_line.set_title('- - -')
            self.ids.finish_line.disabled = True
        else:
            self.ids.start_line.set_title('Start Line')
            self.ids.finish_line.set_title('Finish Line')
            self.ids.finish_line.disabled = False

    def on_config_updated(self, track_cfg):
        separateStartFinishSwitch = self.ids.sep_startfinish
        self.separate_startfinish = track_cfg.track.trackType == TRACK_TYPE_STAGE
        separateStartFinishSwitch.setValue(self.separate_startfinish)

        sectors_container = self.ids.sectors_grid

        sectors_container.clear_widgets()
        for i in range(0, len(track_cfg.track.sectors)):
            sectorView = SectorPointView(title='Sector {}'.format(i + 1), gps_sample=self._gps_sample)
            sectorView.bind(on_config_changed=self.on_config_changed)
            sectors_container.add_widget(sectorView)
            sectorView.set_point(track_cfg.track.sectors[i])

        self.ids.start_line.set_point(track_cfg.track.startLine)
        self.ids.finish_line.set_point(track_cfg.track.finishLine)

        self._track_cfg = track_cfg
        self.update_trackview_state()


class TrackConfigView(BaseConfigView):
    Builder.load_file(TRACK_CONFIG_VIEW_KV)

    def __init__(self, status_pump, settings, databus, rc_api, track_manager, **kwargs):
        super(TrackConfigView, self).__init__(**kwargs)

        self._track_db_capable = False

        self._track_cfg = None
        self._track_db = None

        self._databus = databus
        self._rc_api = rc_api
        self._settings = settings
        self._track_manager = track_manager

        self._auto_config_screen = None
        self._advanced_config_screen = None
        self._single_autoconfig_screen = None
        self._custom_track_screen = None

        self.register_event_type('on_config_updated')

        self.ids.auto_detect.bind(on_setting=self.on_auto_detect)
        self.ids.auto_detect.setControl(SettingsSwitch())

        self._gps_sample = GpsSample()
        status_pump.add_listener(self.status_updated)

    def status_updated(self, status):
        status = status['status']['GPS']

        quality = status['qual']
        latitude = status['lat']
        longitude = status['lon']
        self._gps_sample.gps_qual = quality
        self._gps_sample.latitude = latitude
        self._gps_sample.longitude = longitude


    def _get_track_db_view(self):
        if self._auto_config_screen is None:
            self._auto_config_screen = AutomaticTrackConfigScreen()
            self._auto_config_screen.bind(on_modified=self.on_editor_modified)
            self._auto_config_screen.track_manager = self._track_manager
            if self._track_db is not None:
                self._auto_config_screen.on_config_updated(self._track_db)
        return self._auto_config_screen

    def _get_single_track_view(self):
        if self._single_autoconfig_screen is None:
            self._single_autoconfig_screen = SingleAutoConfigScreen(track_manager=self._track_manager, gps_sample=self._gps_sample)
            self._single_autoconfig_screen.bind(on_modified=self.on_editor_modified)
            if self._track_cfg is not None:
                self._single_autoconfig_screen.on_config_updated(self._track_cfg)
        return self._single_autoconfig_screen

    def _get_custom_track_screen(self):
        if self._custom_track_screen is None:
            self._custom_track_screen = CustomTrackConfigScreen(track_manager=self._track_manager, rc_api=self._rc_api, databus=self._databus)
            self._custom_track_screen.bind(on_advanced_editor=self._on_advanced_editor)
            self._custom_track_screen.bind(on_modified=self.on_editor_modified)
            self._custom_track_screen.on_config_updated(self._track_cfg)
        return self._custom_track_screen

    def _get_advanced_editor_screen(self, *args):
        if self._advanced_config_screen is None:
            self._advanced_config_screen = ManualTrackConfigScreen(gps_sample=self._gps_sample, rc_api=self._rc_api)
            self._advanced_config_screen.bind(on_modified=self.on_editor_modified)
            if self._track_cfg is not None:
                self._advanced_config_screen.on_config_updated(self._track_cfg)
        return self._advanced_config_screen

    def on_editor_modified(self, *args):
        if self._advanced_config_screen is not None:
            # synchronize the advanced config view with the updated track config
            self._advanced_config_screen.on_config_updated(self._track_cfg)

        self.dispatch('on_modified')

    def on_tracks_updated(self, track_manager):
        if self._auto_config_screen is not None:
            self._auto_config_screen.track_manager = track_manager

    def on_config_updated(self, rcp_cfg):
        track_cfg = rcp_cfg.trackConfig
        track_db = rcp_cfg.trackDb

        self._track_db_capable = rcp_cfg.capabilities.storage.tracks > 0

        self.ids.auto_detect.setValue(track_cfg.autoDetect)

        if self._advanced_config_screen is not None:
            self._advanced_config_screen.on_config_updated(track_cfg)

        if self._auto_config_screen is not None:
            self._auto_config_screen.on_config_updated(track_db)

        if self._single_autoconfig_screen is not None:
            self._single_autoconfig_screen.on_config_updated(track_cfg)

        if self._custom_track_screen is not None:
            self._custom_track_screen.on_config_updated(track_cfg)

        self._track_cfg = track_cfg
        self._track_db = track_db

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
        if self.ids.screen_manager.current_screen != screen:
            self.ids.screen_manager.switch_to(screen)

    def on_auto_detect(self, instance, value):
        track_cfg = self._track_cfg
        if track_cfg:
            track_cfg.autoDetect = value
            track_cfg.stale = True
            self.dispatch('on_modified')
            self.ids.auto_detect.help_text = 'Automatically detect and configure your favorite tracks' if value else 'Build and customize your own track map'
        self._select_screen()

    def _on_advanced_editor(self, *args):
        self._switch_to_screen(self._get_advanced_editor_screen())
