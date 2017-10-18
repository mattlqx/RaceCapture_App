#
# Race Capture App
#
# Copyright (C) 2014-2017 Autosport Labs
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

import kivy
kivy.require('1.10.0')
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.app import Builder
from kivy.metrics import sp
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from autosportlabs.uix.track.trackmap import TrackMapView
from autosportlabs.uix.track.racetrackview import RaceTrackView
from autosportlabs.racecapture.tracks.trackmanager import TrackMap
from autosportlabs.racecapture.geo.geopoint import GeoPoint
from autosportlabs.racecapture.geo.geoprovider import GeoProvider
from autosportlabs.racecapture.views.util.alertview import confirmPopup
from autosportlabs.racecapture.config.rcpconfig import GpsConfig
from autosportlabs.racecapture.theme.color import ColorScheme
from autosportlabs.uix.button.betterbutton import BetterButton
from autosportlabs.uix.toast.kivytoast import toast
from autosportlabs.racecapture.views.configuration.rcp.track.trackdata import SimulatedTrackmap
TRACK_BUILDER_KV = """
<TrackBuilderView>:
    ScreenManager:
        id: screen_manager        
"""

class TrackBuilderView(BoxLayout):
    '''
    This view guides the user through selecting an existing track or interactively creating a new track map.
    
    When using, specify a current point for the option to select an existing track. If any tracks are nearby,
    a track selection view will be presented. If no tracks are nearby, the view steps the user through interactively
    making a new track map.
    '''
    Builder.load_string(TRACK_BUILDER_KV)
    def __init__(self, rc_api, databus, track_manager, current_point=None, prompt_track_creation=False, ** kwargs):
        super(TrackBuilderView, self).__init__(**kwargs)
        self.register_event_type('on_track_complete')
        self.register_event_type('on_title')
        self._rc_api = rc_api
        self._databus = databus
        self._prompt_track_creation = prompt_track_creation
        self._track_manager = track_manager
        self._current_point = current_point
        self._screens = []
        self._track = TrackMap.create_new()
        self._track.custom = True

    def on_parent(self, instance, value):
        self._init_view()

    def on_title(self, title):
        pass

    def on_track_complete(self, track_map):
        pass

    def cleanup(self):
        """
        Called when this view is no longer needed. The cleanup methods in each screen
        should unbind/disconnect resources and shut down Clock callbacks as needed. 
        """
        for screen in self._screens:
            screen.cleanup()

    def _init_view(self):
        # show the track builder immediately, or select an existing track, if any are in the area
        if self._current_point is None or len(self._track_manager.find_nearby_tracks(self._current_point)) == 0:
            if self._prompt_track_creation:
                self._switch_to_screen(self._get_track_creator_prompt())
                self.dispatch('on_title', 'Create a new track?')
            else:
                self._switch_to_screen(self._get_track_type_selector())
                self.dispatch('on_title', 'Select a track type')
        else:
            self._switch_to_screen(self._get_existing_track_selector())
            self.dispatch('on_title', 'Select an existing track')

    def _get_existing_track_selector(self):
        screen = ExistingTrackSelectorScreen(self._track_manager, self._current_point)
        screen.bind(on_track_selected=self._on_existing_track_selected)
        self._screens.append(screen)
        return screen

    def _get_track_map_creator(self, track_type):
        screen = TrackMapCreatorScreen(rc_api=self._rc_api, databus=self._databus, track=self._track, track_type=track_type)
        screen.bind(on_trackmap_complete=self._on_trackmap_complete)
        self._screens.append(screen)
        return screen

    def _get_track_creator_prompt(self):
        screen = TrackCreationPromptScreen()
        screen.bind(on_track_creation_prompt=self._on_track_creation_prompt)
        return screen

    def _get_track_type_selector(self):
        screen = TrackTypeSelectorScreen()
        screen.bind(on_track_type_selected=self._on_track_type_selected)
        self._screens.append(screen)
        return screen

    def _get_track_customization_view(self, track):
        screen = TrackCustomizationScreen(track=track)
        screen.bind(on_track_customized=self._on_track_customized)
        self._screens.append(screen)
        return screen

    def _on_track_creation_prompt(self, instance, response):
        if response:
            self._switch_to_screen(self._get_track_type_selector())
            self.dispatch('on_title', 'Select a track type')
        else:
            self.dispatch('on_track_complete', None)

    def _on_track_type_selected(self, instance, type):
        screen = self._get_track_map_creator(type)
        self.dispatch('on_title', 'Build your track')
        self._switch_to_screen(screen)

    def _on_trackmap_complete(self, instance, track):
        screen = self._get_track_customization_view(track)
        self.dispatch('on_title', 'Name your track')
        self._switch_to_screen(screen)

    def _on_track_customized(self, instance, track):
        self.dispatch('on_track_complete', track)

    def _on_existing_track_selected(self, instance, track):
        self.dispatch('on_track_complete', track)

    def _switch_to_screen(self, screen):
        if self.ids.screen_manager.current_screen != screen:
            self.ids.screen_manager.switch_to(screen)

TRACK_CREATOR_PROMPT_KV = """
<TrackCreationPromptScreen>:
    Image:
        source: 'resource/trackmap/track_prompt.jpg'
        allow_stretch: True
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            canvas.before:
                Color:
                    rgba: ColorScheme.get_dark_background_translucent()
                Rectangle:
                    pos: self.pos
                    size: self.size
            size_hint_y: 0.2
            FieldLabel:
                size_hint_y: 0.5
                text: 'We did not detect a race track nearby. Create a custom track?'
                font_size: self.height * 0.7
                shorten: False
                halign: 'center'
        BoxLayout:
            orientation: 'horizontal'
            padding: (dp(70), dp(10))
            spacing: dp(50)
            size_hint_y: 0.6
            BetterButton:
                on_release: root.track_prompt(False)
                text: 'No thanks'
                size_hint: (0.2, 0.3)
            BetterButton:
                on_release: root.track_prompt(True)
                text: 'Let\\'s go'
                size_hint: (0.2, 0.3)
        BoxLayout:
            size_hint_y: 0.2

"""

class TrackCreationPromptScreen(Screen):
    """
    Screen to select an existing track map
    """
    Builder.load_string(TRACK_CREATOR_PROMPT_KV)

    def __init__(self, **kwargs):
        super(TrackCreationPromptScreen, self).__init__(**kwargs)
        self.register_event_type('on_track_creation_prompt')

    def track_prompt(self, response):
        self.dispatch('on_track_creation_prompt', response)

    def on_track_creation_prompt(self, response):
        pass

    def cleanup(self):
        pass


EXISTING_TRACK_SELECTOR_KV = """
<ExistingTrackSelectorScreen>:
    TrackSelectView:
        id: track_select
"""

class ExistingTrackSelectorScreen(Screen):
    """
    Screen to select an existing track map
    """
    Builder.load_string(EXISTING_TRACK_SELECTOR_KV)

    def __init__(self, track_manager, current_point, **kwargs):
        super(ExistingTrackSelectorScreen, self).__init__(**kwargs)
        self.register_event_type('on_track_selected')
        self.ids.track_select.bind(on_track_selected=self.track_selected)
        self.ids.track_select.init_view(track_manager, current_point)

    def track_selected(self, instance, track):
        self.dispatch('on_track_selected', track)

    def on_track_selected(self, track):
        pass

    def cleanup(self):
        pass



TRACK_TYPE_SELECTOR_KV = """
<TrackTypeSelectorScreen>:
    BoxLayout:
        orientation: 'vertical'
        spacing: sp(10)
        AnchorLayout:
            anchor_x: 'right'
            Image:
                allow_stretch: True
                keep_ratio: False
                source: 'resource/trackmap/circuit_racing.jpg'
            BetterButton:
                text: 'Circuit'
                size_hint: (0.3, 0.3)
                on_press: root.select_track_type('circuit')
        AnchorLayout:
            anchor_x: 'right'
            Image:
                allow_stretch: True
                keep_ratio: False
                source: 'resource/trackmap/point_point_racing.jpg'
            BetterButton:
                text: 'Autocross'
                size_hint: (0.3, 0.3)
                on_press: root.select_track_type('point2point')
"""

class TrackTypeSelectorScreen(Screen):
    """
    Screen to select different track types
    """
    TRACK_TYPE_CIRCUIT = 'circuit'
    TRACK_TYPE_POINT_POINT = 'point2point'

    Builder.load_string(TRACK_TYPE_SELECTOR_KV)

    def __init__(self, **kwargs):
        super(TrackTypeSelectorScreen, self).__init__(**kwargs)
        self.register_event_type('on_track_type_selected')

    def on_track_type_selected(self, type):
        pass

    def cleanup(self):
        pass

    def select_track_type(self, type):
        self.dispatch('on_track_type_selected', type)


TRACK_MAP_CREATOR_KV = """
<TrackMapCreatorScreen>:
    BoxLayout:
        spacing: dp(10)
        padding: (dp(10),dp(10)) 
        orientation: 'horizontal'
        canvas.before:
            Color:
                rgba: ColorScheme.get_widget_translucent_background()
            Rectangle:
                pos: self.pos
                size: self.size
        AnchorLayout:
            size_hint_x: 0.7
            AnchorLayout:
                anchor_y: 'bottom'
                FieldLabel:
                    id: help_message
                    size_hint_y: 0.2
                    font_size: self.height * 0.3
                    halign: 'center'
                    shorten: False
            FieldLabel:
                id: info_message
                size_hint_y: 0.1
                font_size: self.height * 0.9
                halign: 'center'
            TrackMapView:
                id: track
            AnchorLayout:
                anchor_y: 'top'
                anchor_x: 'left'
                GridLayout:
                    spacing: dp(10)
                    cols:2
                    rows:1
                    size_hint_y: 0.12
                    size_hint_x: 0.1
                    IconButton:
                        id: internal_status
                        text: u'\uf10b'
                        color: [0.3, 0.3, 0.3, 0.2]        
                        font_size: self.height
                    IconButton:
                        id: gps_status
                        text: u'\uf041'
                        color: [0.3, 0.3, 0.3, 0.2]
                        font_size: self.height * 0.8
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.3
            spacing: dp(20)
            padding: (dp(5), dp(5))
            
            BetterButton:
                id: start_button
                text: 'Start'
                on_press: root.on_set_start_point(*args)
                font_size: self.height * 0.4
            BetterButton:
                id: add_sector_button
                text: 'Sector'
                on_press: root.on_add_sector_point(*args)
                font_size: self.height * 0.4
            BetterButton:
                id: finish_button
                text: 'Finish'
                on_press: root.on_finish(*args)
                font_size: self.height * 0.4
"""

class TrackMapCreatorScreen(Screen):
    """
    Screen to interactively draw a track map based on GPS data.
    """
    GPS_ACTIVE_COLOR = [0.0, 1.0, 0.0, 1.0]
    GPS_INACTIVE_COLOR = [1.0, 0.0, 0.0, 1.0]
    INTERNAL_ACTIVE_COLOR = [0.0, 1.0, 1.0, 1.0]
    INTERNAL_INACTIVE_COLOR = [0.3, 0.3, 0.3, 0.3]

    # minimum separation needed between start, finish and sector targets
    MINIMUM_TARGET_SEPARATION_METERS = 50

    # default minimum distance needed to travel before registering a trackmap point
    DEFAULT_MINIMUM_TRAVEL_DISTANCE_METERS = 1

    # how long until we time out
    STATUS_LINGER_DURATION_SEC = 2.0

    minimum_travel_distance = NumericProperty(DEFAULT_MINIMUM_TRAVEL_DISTANCE_METERS)

    Builder.load_string(TRACK_MAP_CREATOR_KV)

    def __init__(self, rc_api, databus, track, track_type, **kwargs):
        super(TrackMapCreatorScreen, self).__init__(**kwargs)
        self._databus = databus
        self._rc_api = rc_api
        self._track_type = track_type
        self._geo_provider = GeoProvider(rc_api=rc_api, databus=databus)
        self._geo_provider.bind(on_location=self._on_location)
        self._geo_provider.bind(on_internal_gps_available=self._on_internal_gps_available)
        self._geo_provider.bind(on_gps_source=self._on_gps_source)
        self.register_event_type('on_trackmap_complete')
        self.current_point = None
        self.last_point = None
        self._is_finished = False
        self._track = track
        self._update_trackmap()
        self._init_status_monitor()
        self._update_button_states()
        Window.bind(on_key_down=self.key_action)

    def cleanup(self):
        Window.unbind(on_key_down=self.key_action)
        self._geo_provider.shutdown()

    def on_trackmap_complete(self, track):
        pass

    def _init_status_monitor(self):
        self._status_decay = Clock.create_trigger(self._on_status_decay, TrackMapCreatorScreen.STATUS_LINGER_DURATION_SEC)
        self._status_decay()

    def _on_status_decay(self, *args):
        self.ids.internal_status.color = TrackMapCreatorScreen.INTERNAL_INACTIVE_COLOR
        self.ids.gps_status.color = TrackMapCreatorScreen.GPS_INACTIVE_COLOR

    def _update_status_indicators(self):
        self._status_decay.cancel()
        internal_active = self._geo_provider.location_source_internal
        self.ids.internal_status.color = TrackMapCreatorScreen.INTERNAL_ACTIVE_COLOR if internal_active else TrackMapCreatorScreen.INTERNAL_INACTIVE_COLOR
        self.ids.gps_status.color = TrackMapCreatorScreen.GPS_ACTIVE_COLOR
        self._status_decay()

    def _update_button_states(self):
        current_point = self.current_point
        track = self._track
        start_point = track.start_finish_point
        finish_point = track.finish_point

        sector_points = track.sector_points
        # to determine if we can add another sector, we reference the start line
        # or the last sector point, if it exists
        last_sector_point = None if len(sector_points) == 0 else sector_points[-1]
        reference_point = last_sector_point if last_sector_point is not None else start_point

        # Can only add a sector if we're the minimum distance from the reference point
        can_add_sector = (start_point is not None and
                current_point is not None and
                current_point.dist_pythag(reference_point) >= TrackMapCreatorScreen.MINIMUM_TARGET_SEPARATION_METERS)

        # we can't add a sector if the finish point is defined
        can_add_sector = False if finish_point is not None else can_add_sector

        can_add_sector = False if self._is_finished else can_add_sector

        self.ids.add_sector_button.disabled = not can_add_sector

        # must be minimum distance from start point to create a finish point
        can_finish = (start_point is not None and
                    current_point is not None and
                    current_point.dist_pythag(start_point) >= TrackMapCreatorScreen.MINIMUM_TARGET_SEPARATION_METERS)

        # also must be minimum distance from last sector point, if it exists
        can_finish = (False if (last_sector_point is not None and
                    current_point.dist_pythag(last_sector_point) < TrackMapCreatorScreen.MINIMUM_TARGET_SEPARATION_METERS)
                    else can_finish)

        # However, we can finish if we're making a minimal track with only the start/finish defined
        # The user will be prompted later if they're sure about making a minimal trackmap
        can_finish = (True if start_point is not None and
                    len(track.sector_points) == 0 and
                    self._track_type == TrackTypeSelectorScreen.TRACK_TYPE_CIRCUIT
                    else can_finish)

        self.ids.finish_button.disabled = not can_finish

        # can we start?
        can_start = self.current_point is not None
        self.ids.start_button.disabled = not can_start

        self.ids.start_button.text = 'Re-start' if len(track.map_points) > 1 else 'Start'

        if current_point is None:
            self.ids.info_message.text = 'Waiting for GPS'
        elif track.start_finish_point is None:
            self.ids.info_message.text = 'Go to start line and press Start!'
        else:
            self.ids.info_message.text = ''

        if current_point is not None and start_point is not None and current_point.dist_pythag(start_point) < TrackMapCreatorScreen.MINIMUM_TARGET_SEPARATION_METERS:
            self.ids.help_message.text = 'Now start your track walk. You can optionally mark sector points as you go'
        else:
            self.ids.help_message.text = ''

    def _update_trackmap(self):
        self.ids.track.setTrackPoints(self._track.map_points)
        self.ids.track.sector_points = self._track.sector_points

    def _add_trackmap_point(self, point):
        self._track.map_points.append(point)
        self.last_point = point

    def _on_location(self, instance, point):
        self._update_current_point(point)
        self._update_status_indicators()

    def _on_internal_gps_available(self, instance, available):
        if not available:
            toast("Could not activate internal GPS on this device", length_long=True)

    def _on_gps_source(self, instance, source):
        msg = None
        if source == GeoProvider.GPS_SOURCE_RACECAPTURE:
            msg = "GPS Source: RaceCapture"
        elif source == GeoProvider.GPS_SOURCE_INTERNAL:
            msg = "GPS source: this device"
        if msg is not None:
            toast(msg, length_long=True)

    def _update_current_point(self, point):
        self.current_point = point
        track = self.ids.track

        # we can add a point if we have started
        can_add_point = track.start_point is not None

        # however, we can't add a point if we're too close to the last point
        can_add_point = False if (self.last_point is not None and
                                  self.last_point.dist_pythag(point) < self.minimum_travel_distance) else can_add_point

        # but ultimately, we can't add points if we're finished
        can_add_point = False if self._is_finished else can_add_point

        if can_add_point:
            self._add_trackmap_point(point)
            self._update_trackmap()

        self._update_button_states()

    def on_set_start_point(self, *args):
        popup = None
        def confirm_restart(instance, restart):
            if restart:
                self._start_new_track()
            popup.dismiss()

        if len(self._track.map_points) > 1 and self._track.start_finish_point is not None:
            popup = confirmPopup("Restart", "Restart Track Map?", confirm_restart)
        else:
            self._start_new_track()

    def _start_new_track(self):
        self._is_finished = False
        self.ids.finish_button.text = 'Finish'
        self._track.map_points = []
        self._track.sector_points = []
        self._track.finish_point = None
        start_point = self.current_point
        self._track.start_finish_point = start_point
        self.ids.track.start_point = start_point
        self.ids.track.finish_point = None
        self._add_trackmap_point(start_point)
        self._update_button_states()
        self._update_trackmap()

    def _on_finish_circuit(self):
        # close the circuit by adding the start point as the last point,
        # so there's no gap in the circuit
        first_point = self._track.map_points[0]
        self._add_trackmap_point(GeoPoint.fromPoint(first_point.latitude, first_point.longitude))

    def _on_finish_point_point(self):
        finish_point = self.current_point
        self.ids.track.finish_point = finish_point
        self._track.finish_point = finish_point

    def on_finish(self, *args):
        self._process_finish()

    def _validate_finish(self):
        def confirm_minimal_track(instance, confirm):
            if confirm:
                self._process_finish(force=True)
            popup.dismiss()

        if (self._track_type == TrackTypeSelectorScreen.TRACK_TYPE_CIRCUIT and
                self.current_point.dist_pythag(self._track.start_finish_point) < TrackMapCreatorScreen.MINIMUM_TARGET_SEPARATION_METERS):
            popup = confirmPopup("Confirm", "There's no track map - create a minimal track with just start/finish defined?", confirm_minimal_track)
            return False

        return True

    def _process_finish(self, force=False):
        if self._is_finished:
            self.dispatch('on_trackmap_complete', self._track)
            return

        if not force and not self._validate_finish():
            return

        # add one more point of the current location
        finish_point = self.current_point
        self._add_trackmap_point(finish_point)

        if self._track_type == TrackTypeSelectorScreen.TRACK_TYPE_CIRCUIT:
            self._on_finish_circuit()
        elif self._track_type == TrackTypeSelectorScreen.TRACK_TYPE_POINT_POINT:
            self._on_finish_point_point()

        # finish button turns into next button
        self.ids.finish_button.text = 'Next >'
        self._update_trackmap()
        self._is_finished = True
        self._update_button_states()

    def on_add_sector_point(self, *args):
        self._track.sector_points.append(self.current_point)
        self._update_trackmap()
        self._update_button_states()

    # test key sequence to simulate walking a course - needed for testing
    # the special key is '`'
    def key_action(self, instance, keyboard, keycode, text, modifiers):
        if text == '`':  # sekret!
            lat, lon = SimulatedTrackmap.get_simulated_point()
            point = GeoPoint.fromPoint(lat, lon)
            self._update_current_point(point)

TRACK_CUSTOMIZATION_KV = """
<TrackCustomizationScreen>:
    BoxLayout:
        padding: (sp(20), sp(20))
        spacing: sp(20)
        orientation: 'horizontal'
        RaceTrackView:
            id: track
            size_hint_x: 0.4
        BoxLayout:
            canvas.before:
                Color:
                    rgba: ColorScheme.get_dark_background()
                Rectangle:
                    pos: self.pos
                    size: self.size
            size_hint_x: 0.6
            padding: (sp(10), sp(10))
            spacing: sp(10)
            orientation: 'vertical'
            BoxLayout:
                spacing: sp(5)
                size_hint_y: 0.15
                orientation: 'horizontal'
                FieldLabel:
                    size_hint_x: 0.4
                    text: 'Name'
                    halign: 'right'
                    valign: 'middle'
                    font_size: self.height * 0.5
                TextValueField:
                    id: track_name
                    size_hint_x: 0.6
                    max_len: 60
                    text: root.track_name
                    hint_text: 'Give your track a name'
            BoxLayout:
                spacing: sp(5)
                size_hint_y: 0.15
                orientation: 'horizontal'
                FieldLabel:
                    size_hint_x: 0.4
                    text: 'Configuration'
                    halign: 'right'
                    valign: 'middle'
                    font_size: self.height * 0.5
                TextValueField:
                    id: track_configuration
                    size_hint_x: 0.6
                    max_len: 60                        
                    text: root.track_configuration
                    hint_text: 'Main / short-track / etc.'
            BoxLayout:
                size_hint_y: 0.7
                BoxLayout:
                    size_hint_x: 0.4
                AnchorLayout:
                    size_hint_x: 0.7
                    BetterButton:
                        text: 'Finish'
                        size_hint: (0.7, 0.5)
                        on_press: root.on_finish()
                        font_size: self.height * 0.4
"""

class TrackCustomizationScreen(Screen):
    """
    Screen to customize a track map
    """
    DEFAULT_TRACK_NAME = 'Track'
    track_name = StringProperty()
    track_configuration = StringProperty()

    Builder.load_string(TRACK_CUSTOMIZATION_KV)

    def __init__(self, track, **kwargs):
        super(TrackCustomizationScreen, self).__init__(**kwargs)
        self.register_event_type('on_track_customized')
        self._track = track
        self._init_view()

    def on_track_customized(self, track):
        pass

    def _init_view(self):
        self.ids.track_name.bind(text=self._on_track_name)
        self.ids.track_configuration.bind(text=self._on_track_configuration)
        self.ids.track_name.next = self.ids.track_configuration
        self.ids.track_configuration.next = self.ids.track_name
        self._track.name = TrackCustomizationScreen.DEFAULT_TRACK_NAME
        self.track_name = self._track.name
        self.track_configuration = self._track.configuration
        self.ids.track.loadTrack(self._track)

    def _on_track_name(self, instance, value):
        self.track_name = value

    def _on_track_configuration(self, instance, value):
        self.track_configuration = value

    def on_track_name(self, instance, value):
        self._track.name = value

    def on_track_configuration(self, instance, value):
        self._track.configuration = value

    def _validate_configuration(self):
        if self._track.name == '':
            self._track.name = TrackCustomizationScreen.DEFAULT_TRACK_NAME

    def on_finish(self, *args):
        self._validate_configuration()
        self.dispatch('on_track_customized', self._track)

    def cleanup(self):
        pass

