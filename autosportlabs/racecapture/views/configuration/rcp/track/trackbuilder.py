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

import kivy
kivy.require('1.9.1')
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
TRACK_BUILDER_KV = """
<TrackBuilderView>:
    ScreenManager:
        id: screen_manager        
"""

class TrackBuilderView(BoxLayout):
    Builder.load_string(TRACK_BUILDER_KV)
    def __init__(self, rc_api, databus, track_manager, current_point = None, **kwargs):
        super(TrackBuilderView, self).__init__(**kwargs)
        self._rc_api = rc_api
        self._databus = databus
        self._track_manager = track_manager
        self._current_point = current_point
        self._screens = []
        self._init_view()
        self._track = TrackMap.create_new()
        self._track.custom = True
        self.register_event_type('on_track_complete')

    def on_track_complete(self, track_map):
        pass

    def cleanup(self):
        for screen in self._screens:
            screen.cleanup()

    def _init_view(self):
        # show the track builder immediately, or select an existing track, if any are in the area
        if self._current_point is None or len(self._track_manager.find_nearby_tracks(self._current_point)) == 0:
            self._switch_to_screen(self._get_track_type_selector())
        else:
            self._switch_to_screen(self._get_existing_track_selector())

    def _get_existing_track_selector(self):
        screen = ExistingTrackSelector(self._track_manager, self._current_point)
        screen.bind(on_track_selected = self._on_existing_track_selected)
        self._screens.append(screen)
        return screen
        
    def _get_track_map_creator(self, track_type):
        screen = TrackMapCreator(rc_api=self._rc_api, databus=self._databus, track=self._track, track_type=track_type)
        screen.bind(on_trackmap_complete=self._on_trackmap_complete)
        self._screens.append(screen)
        return screen

    def _get_track_type_selector(self):
        screen = TrackTypeSelector()
        screen.bind(on_track_type_selected=self._on_track_type_selected)
        self._screens.append(screen)
        return screen

    def _get_track_customization_view(self, track):
        screen = TrackCustomizationView(track=track)
        screen.bind(on_track_customized=self._on_track_customized)
        self._screens.append(screen)
        return screen

    def _on_track_type_selected(self, instance, type):
        screen = self._get_track_map_creator(type)
        self._switch_to_screen(screen)

    def _on_trackmap_complete(self, instance, track):
        screen = self._get_track_customization_view(track)
        self._switch_to_screen(screen)

    def _on_track_customized(self, instance, track):
        self.dispatch('on_track_complete', track)

    def _on_existing_track_selected(self, instance, track):
        self.dispatch('on_track_complete', track)
        
    def _switch_to_screen(self, screen):
        if self.ids.screen_manager.current_screen != screen:
            self.ids.screen_manager.switch_to(screen)

EXISTING_TRACK_SELECTOR_KV = """
<ExistingTrackSelector>:
    TrackSelectView:
        id: track_select
"""
class ExistingTrackSelector(Screen):

    Builder.load_string(EXISTING_TRACK_SELECTOR_KV)

    def __init__(self, track_manager, current_point, **kwargs):
        super(ExistingTrackSelector, self).__init__(**kwargs)
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
<TrackTypeSelector>:
    BoxLayout:
        orientation: 'vertical'
        FieldLabel:
            size_hint_y: 0.1
            text: 'Setup Race Track'
            font_size: self.height * 0.7
        BoxLayout:
            size_hint_y: 0.9
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

class TrackTypeSelector(Screen):
    TRACK_TYPE_CIRCUIT = 'circuit'
    TRACK_TYPE_POINT_POINT = 'point2point'

    Builder.load_string(TRACK_TYPE_SELECTOR_KV)

    def __init__(self, **kwargs):
        super(TrackTypeSelector, self).__init__(**kwargs)
        self.register_event_type('on_track_type_selected')

    def on_track_type_selected(self, type):
        pass

    def cleanup(self):
        pass

    def select_track_type(self, type):
        self.dispatch('on_track_type_selected', type)


TRACK_MAP_CREATOR_KV = """
<TrackMapCreator>:
    BoxLayout:
        spacing: sp(25)
        padding: (sp(25),sp(25)) 
        orientation: 'horizontal'
        canvas.before:
            Color:
                rgba: ColorScheme.get_widget_translucent_background()
            Rectangle:
                pos: self.pos
                size: self.size
        AnchorLayout:
            size_hint_x: 0.7
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
                    spacing: sp(10)
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
            spacing: sp(20)
            padding: (sp(5), sp(5))
            
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

class TrackMapCreator(Screen):
    GPS_ACTIVE_COLOR = [0.0, 1.0, 0.0, 1.0]
    GPS_INACTIVE_COLOR = [1.0, 0.0, 0.0, 1.0]
    INTERNAL_ACTIVE_COLOR = [0.0, 1.0, 1.0, 1.0]
    INTERNAL_INACTIVE_COLOR = [0.3, 0.3, 0.3, 0.3]

    # minimum separation needed between start, finish and sector targets
    MINIMUM_TARGET_SEPARATION_METERS = 50

    # default minimum distance needed to travel before registering a trackmap point
    DEFAULT_MINIMUM_TRAVEL_DISTANCE_METERS = 1

    # how long until we time out
    STATUS_LINGER_DURATION = 2.0

    minimum_travel_distance = NumericProperty(DEFAULT_MINIMUM_TRAVEL_DISTANCE_METERS)

    Builder.load_string(TRACK_MAP_CREATOR_KV)

    def __init__(self, rc_api, databus, track, track_type, **kwargs):
        super(TrackMapCreator, self).__init__(**kwargs)
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

    def on_trackmap_complete(self, track):
        pass

    def _init_status_monitor(self):
        self._status_decay = Clock.create_trigger(self._on_status_decay, TrackMapCreator.STATUS_LINGER_DURATION)
        self._status_decay()

    def _on_status_decay(self, *args):
        self.ids.internal_status.color = TrackMapCreator.INTERNAL_INACTIVE_COLOR
        self.ids.gps_status.color = TrackMapCreator.GPS_INACTIVE_COLOR

    def _update_status_indicators(self):
        self._status_decay.cancel()
        internal_active = self._geo_provider.location_source_internal
        self.ids.internal_status.color = TrackMapCreator.INTERNAL_ACTIVE_COLOR if internal_active else TrackMapCreator.INTERNAL_INACTIVE_COLOR
        self.ids.gps_status.color = TrackMapCreator.GPS_ACTIVE_COLOR
        self._status_decay()

    def _update_button_states(self):
        current_point = self.current_point
        track = self._track
        start_point = track.start_finish_point
        finish_point = track.finish_point

        sector_points = track.sector_points
        # to determine if we can add another sector, we reference the start line
        # or the last sector point, if it exists
        last_sector_point = None if len(sector_points) == 0 else track.sector_points[-1]
        reference_point = last_sector_point if last_sector_point is not None else start_point

        # Can only add a sector if we're the minimum distance from the reference point
        can_add_sector = (start_point is not None and
                current_point is not None and
                current_point.dist_pythag(reference_point) >= TrackMapCreator.MINIMUM_TARGET_SEPARATION_METERS)

        # we can't add a sector if the finish point is defined
        can_add_sector = False if finish_point is not None else can_add_sector

        can_add_sector = False if self._is_finished else can_add_sector

        self.ids.add_sector_button.disabled = not can_add_sector

        # must be minimum distance from start point to create a finish point
        can_finish = (start_point is not None and
                    current_point is not None and
                    current_point.dist_pythag(start_point) >= TrackMapCreator.MINIMUM_TARGET_SEPARATION_METERS)

        # also must be minimum distance from last sector point, if it exists
        can_finish = False if (last_sector_point is not None and
                    current_point.dist_pythag(last_sector_point) < TrackMapCreator.MINIMUM_TARGET_SEPARATION_METERS) else can_finish

        self.ids.finish_button.disabled = not can_finish

        # can we start?
        can_start = self.current_point is not None
        self.ids.start_button.disabled = not can_start

        self.ids.start_button.text = 'Re-start' if len(track.map_points) > 1 else 'Start'

        if current_point is None:
            self.ids.info_message.text = 'Waiting for GPS'
        else:
            self.ids.info_message.text = 'Go to start line and press Start!' if track.start_finish_point is None else ''

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
        if self._is_finished:
            self.dispatch('on_trackmap_complete', self._track)
            return

        # add one more point of the current location
        finish_point = self.current_point
        self._add_trackmap_point(finish_point)

        if self._track_type == TrackTypeSelector.TRACK_TYPE_CIRCUIT:
            self._on_finish_circuit()
        elif self._track_type == TrackTypeSelector.TRACK_TYPE_POINT_POINT:
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

# fake GPS data source - this is for debugging.
    _simulated_trackmap_index = 0

    # test key sequence to simulate walking a course - needed for testing
    # the special key is '`'
    def key_action(self, instance, keyboard, keycode, text, modifiers):
        if text == '`':
            point = GeoPoint.fromPoint(SIMULATED_TRACKMAP_POINTS[self._simulated_trackmap_index][0],
                                       SIMULATED_TRACKMAP_POINTS[self._simulated_trackmap_index][1])
            self._update_current_point(point)
            self._simulated_trackmap_index += 1
            if self._simulated_trackmap_index >= len(SIMULATED_TRACKMAP_POINTS):
                self._simulated_trackmap_index = 0

TRACK_CUSTOMIZATION_VIEW_KV = """
<TrackCustomizationView>:

    BoxLayout:
        orientation: 'vertical'
        FieldLabel:
            size_hint_y: 0.1
            text: 'Name your track'
            font_size: self.height * 0.7
        BoxLayout:
            size_hint_y: 0.9
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

class TrackCustomizationView(Screen):

    DEFAULT_TRACK_NAME = 'Track'
    track_name = StringProperty()
    track_configuration = StringProperty()

    Builder.load_string(TRACK_CUSTOMIZATION_VIEW_KV)

    def __init__(self, track, **kwargs):
        super(TrackCustomizationView, self).__init__(**kwargs)
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
        self._track.name = TrackCustomizationView.DEFAULT_TRACK_NAME
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
            self._track.name = TrackCustomizationView.DEFAULT_TRACK_NAME

    def on_finish(self, *args):
        self._validate_configuration()
        self.dispatch('on_track_customized', self._track)

    def cleanup(self):
        pass

SIMULATED_TRACKMAP_POINTS = [
[
  38.1615364765,
  - 122.454711706
],
[
  38.1618961152,
  - 122.45529075
],
[
  38.1620356606,
  - 122.455512906
],
[
  38.162083768,
  - 122.455620329
],
[
  38.1621258294,
  - 122.455779566
],
[
  38.1621370103,
  - 122.455913682
],
[
  38.1621300361,
  - 122.456644236
],
[
  38.1621282845,
  - 122.456947255
],
[
  38.1621213556,
  - 122.457231342
],
[
  38.162115054,
  - 122.457299596
],
[
  38.1621046852,
  - 122.457367811
],
[
  38.1620909629,
  - 122.457432311
],
[
  38.1620587271,
  - 122.457522105
],
[
  38.1620196392,
  - 122.457612566
],
[
  38.1619751252,
  - 122.457699966
],
[
  38.1619066519,
  - 122.457811037
],
[
  38.1618332817,
  - 122.457920974
],
[
  38.1617559607,
  - 122.458028245
],
[
  38.1616770054,
  - 122.458129851
],
[
  38.1616134981,
  - 122.458189909
],
[
  38.1615437122,
  - 122.458246818
],
[
  38.1614697918,
  - 122.458298562
],
[
  38.1613921382,
  - 122.45834483
],
[
  38.1613084984,
  - 122.458386683
],
[
  38.1612581267,
  - 122.458415124
],
[
  38.1612097682,
  - 122.458450418
],
[
  38.1611654785,
  - 122.458491427
],
[
  38.1611258848,
  - 122.458537738
],
[
  38.1610901419,
  - 122.45859102
],
[
  38.1610597631,
  - 122.4586622
],
[
  38.1610366624,
  - 122.45873251
],
[
  38.1610196194,
  - 122.458804809
],
[
  38.1610088157,
  - 122.458878505
],
[
  38.1610043708,
  - 122.458952973
],
[
  38.161006335,
  - 122.459027568
],
[
  38.1610152997,
  - 122.459107083
],
[
  38.1610429458,
  - 122.459188524
],
[
  38.1610739147,
  - 122.459262005
],
[
  38.1611099523,
  - 122.459332866
],
[
  38.1611492355,
  - 122.459398092
],
[
  38.1612386405,
  - 122.459552738
],
[
  38.161343588,
  - 122.45971138
],
[
  38.1614512255,
  - 122.459860605
],
[
  38.1615528678,
  - 122.459981608
],
[
  38.1616847625,
  - 122.460147076
],
[
  38.1618202473,
  - 122.460306754
],
[
  38.1619144393,
  - 122.460410607
],
[
  38.1619824635,
  - 122.460485238
],
[
  38.1620570067,
  - 122.460556179
],
[
  38.1621362483,
  - 122.460621528
],
[
  38.1622179336,
  - 122.460679668
],
[
  38.1622769074,
  - 122.460723051
],
[
  38.1623315763,
  - 122.460769368
],
[
  38.1623826307,
  - 122.460819024
],
[
  38.1624297826,
  - 122.46087252
],
[
  38.16247302,
  - 122.460929176
],
[
  38.1625120239,
  - 122.460988544
],
[
  38.1625473423,
  - 122.461051585
],
[
  38.1625709221,
  - 122.46109688
],
[
  38.1625887939,
  - 122.461141582
],
[
  38.1626020156,
  - 122.461187445
],
[
  38.162610551,
  - 122.461234079
],
[
  38.1626146022,
  - 122.461283755
],
[
  38.1626188478,
  - 122.461385909
],
[
  38.1626196243,
  - 122.461488401
],
[
  38.1626169493,
  - 122.461589758
],
[
  38.1625952834,
  - 122.461842526
],
[
  38.1625952834,
  - 122.461903695
],
[
  38.1625921734,
  - 122.461906805
],
[
  38.1625942033,
  - 122.462003122
],
[
  38.1626015188,
  - 122.462068167
],
[
  38.162614671,
  - 122.462132088
],
[
  38.1626334907,
  - 122.46219428
],
[
  38.1626577488,
  - 122.462254182
],
[
  38.1626877618,
  - 122.462312442
],
[
  38.1627271788,
  - 122.462369628
],
[
  38.1627691847,
  - 122.462422111
],
[
  38.1628146773,
  - 122.462471293
],
[
  38.1628628514,
  - 122.462516431
],
[
  38.1629815358,
  - 122.462618161
],
[
  38.1632814166,
  - 122.462867662
],
[
  38.163931058,
  - 122.463406767
],
[
  38.1639761972,
  - 122.463417205
],
[
  38.164014546,
  - 122.463419997
],
[
  38.164052873,
  - 122.463416853
],
[
  38.1640904422,
  - 122.463407802
],
[
  38.1641265196,
  - 122.463392931
],
[
  38.1641603274,
  - 122.463372412
],
[
  38.1642017584,
  - 122.463337643
],
[
  38.1642381432,
  - 122.463296697
],
[
  38.1642687181,
  - 122.463250067
],
[
  38.1642939637,
  - 122.463195632
],
[
  38.1644281125,
  - 122.462563541
],
[
  38.1645182252,
  - 122.462112978
],
[
  38.164533903,
  - 122.46200553
],
[
  38.1645425197,
  - 122.461896637
],
[
  38.1645439448,
  - 122.461787382
],
[
  38.1645381703,
  - 122.461678283
],
[
  38.1645253216,
  - 122.461570641
],
[
  38.1645083851,
  - 122.461469834
],
[
  38.1644858672,
  - 122.461369881
],
[
  38.1644579047,
  - 122.461271422
],
[
  38.1644241297,
  - 122.461173408
],
[
  38.1643760294,
  - 122.461066802
],
[
  38.1643246709,
  - 122.460964085
],
[
  38.164267872,
  - 122.460860961
],
[
  38.1642158263,
  - 122.460789339
],
[
  38.1641610709,
  - 122.460722851
],
[
  38.1641024431,
  - 122.460659848
],
[
  38.1640437293,
  - 122.46060429
],
[
  38.1639823773,
  - 122.460552258
],
[
  38.1639202978,
  - 122.460505163
],
[
  38.1636409941,
  - 122.460277251
],
[
  38.1632374646,
  - 122.459952186
],
[
  38.1630110118,
  - 122.45977506
],
[
  38.1629489491,
  - 122.459726361
],
[
  38.1628923435,
  - 122.45967461
],
[
  38.1628399495,
  - 122.459618917
],
[
  38.1627920505,
  - 122.459559635
],
[
  38.162748897,
  - 122.459497136
],
[
  38.1627107049,
  - 122.459431803
],
[
  38.1626776551,
  - 122.459364029
],
[
  38.162649894,
  - 122.459294204
],
[
  38.1626275356,
  - 122.459222718
],
[
  38.1626106642,
  - 122.459149953
],
[
  38.1625993381,
  - 122.459076281
],
[
  38.1625935318,
  - 122.459001269
],
[
  38.1625919472,
  - 122.458922484
],
[
  38.1625958962,
  - 122.458844362
],
[
  38.1626053557,
  - 122.458766646
],
[
  38.1626202974,
  - 122.458689678
],
[
  38.1626406744,
  - 122.4586138
],
[
  38.1626664183,
  - 122.458539364
],
[
  38.1626974365,
  - 122.458466728
],
[
  38.162733523,
  - 122.458396422
],
[
  38.1627695761,
  - 122.45833764
],
[
  38.1628102404,
  - 122.458281691
],
[
  38.1628553412,
  - 122.458228881
],
[
  38.1629046223,
  - 122.458179576
],
[
  38.1629577935,
  - 122.458134123
],
[
  38.1630137553,
  - 122.458093408
],
[
  38.1630653764,
  - 122.458064309
],
[
  38.1631202418,
  - 122.458040318
],
[
  38.1631774261,
  - 122.458021928
],
[
  38.1632363041,
  - 122.458009375
],
[
  38.1632962284,
  - 122.458002818
],
[
  38.1633563493,
  - 122.458002343
],
[
  38.16341527,
  - 122.458008364
],
[
  38.1634742777,
  - 122.458018911
],
[
  38.163532271,
  - 122.458033836
],
[
  38.1635889053,
  - 122.458053039
],
[
  38.1636448032,
  - 122.4580768
],
[
  38.163712458,
  - 122.458108132
],
[
  38.163776765,
  - 122.458143709
],
[
  38.163838241,
  - 122.458183716
],
[
  38.1638965658,
  - 122.45822792
],
[
  38.1639514396,
  - 122.458276062
],
[
  38.1640025853,
  - 122.458327862
],
[
  38.1640476508,
  - 122.458380565
],
[
  38.1646071233,
  - 122.459316735
],
[
  38.1651009335,
  - 122.460284762
],
[
  38.1654361548,
  - 122.461155946
],
[
  38.1654403098,
  - 122.461172409
],
[
  38.1654441424,
  - 122.461182353
],
[
  38.1655774049,
  - 122.461520269
],
[
  38.1657335481,
  - 122.461924334
],
[
  38.1658373965,
  - 122.462172616
],
[
  38.1659457736,
  - 122.462435129
],
[
  38.1660069122,
  - 122.462550902
],
[
  38.1660272037,
  - 122.46257473
],
[
  38.166048765,
  - 122.462592981
],
[
  38.1660722594,
  - 122.46260705
],
[
  38.1660971424,
  - 122.462616892
],
[
  38.1661229069,
  - 122.462622485
],
[
  38.1661490637,
  - 122.462623815
],
[
  38.1661751298,
  - 122.462620882
],
[
  38.166200621,
  - 122.46261369
],
[
  38.1662271901,
  - 122.46260125
],
[
  38.1662705284,
  - 122.462565384
],
[
  38.1663023439,
  - 122.462528748
],
[
  38.1667371253,
  - 122.462070055
],
[
  38.1667565353,
  - 122.462057115
],
[
  38.1667826863,
  - 122.46200245
],
[
  38.16679647,
  - 122.461955022
],
[
  38.1668024464,
  - 122.461905231
],
[
  38.1668002381,
  - 122.461854978
],
[
  38.1667899879,
  - 122.46180624
],
[
  38.1667723089,
  - 122.461760748
],
[
  38.1667480999,
  - 122.46171981
],
[
  38.1667183586,
  - 122.461684314
],
[
  38.1666840756,
  - 122.461654846
],
[
  38.1666457497,
  - 122.461631525
],
[
  38.1664714562,
  - 122.461565708
],
[
  38.166260454,
  - 122.461419013
],
[
  38.1662558225,
  - 122.461415862
],
[
  38.1662221141,
  - 122.461386022
],
[
  38.1661935468,
  - 122.46135339
],
[
  38.1661515124,
  - 122.461299586
],
[
  38.1660694619,
  - 122.461178923
],
[
  38.1659788959,
  - 122.461045457
],
[
  38.1658764948,
  - 122.460890256
],
[
  38.1658337711,
  - 122.460819432
],
[
  38.1657944973,
  - 122.460746069
],
[
  38.1657589817,
  - 122.460670677
],
[
  38.1657272651,
  - 122.460593289
],
[
  38.165704479,
  - 122.460527477
],
[
  38.1656860706,
  - 122.460459596
],
[
  38.165672312,
  - 122.460390417
],
[
  38.1656612984,
  - 122.460303965
],
[
  38.1656451754,
  - 122.460224503
],
[
  38.1656232144,
  - 122.460146267
],
[
  38.1655954958,
  - 122.46006965
],
[
  38.1655618682,
  - 122.45999447
],
[
  38.1655268463,
  - 122.459926684
],
[
  38.1654874491,
  - 122.459861572
],
[
  38.1654436401,
  - 122.459799077
],
[
  38.1653954489,
  - 122.459739319
],
[
  38.1653431512,
  - 122.459681844
],
[
  38.1651788122,
  - 122.459502394
],
[
  38.1651232519,
  - 122.459436334
],
[
  38.1650721488,
  - 122.459365122
],
[
  38.165026515,
  - 122.459289956
],
[
  38.1649860165,
  - 122.459209991
],
[
  38.1649516851,
  - 122.459117444
],
[
  38.1649229494,
  - 122.459025326
],
[
  38.1648990937,
  - 122.458931718
],
[
  38.1648801982,
  - 122.458836893
],
[
  38.1648659758,
  - 122.458738703
],
[
  38.1648629012,
  - 122.45865056
],
[
  38.1648643061,
  - 122.458564895
],
[
  38.1648700978,
  - 122.458479431
],
[
  38.1648795408,
  - 122.458400406
],
[
  38.1648824466,
  - 122.45830829
],
[
  38.1648800504,
  - 122.458214836
],
[
  38.164872441,
  - 122.458123151
],
[
  38.1648591254,
  - 122.458047773
],
[
  38.1648407651,
  - 122.457972043
],
[
  38.1648176301,
  - 122.457897479
],
[
  38.164789787,
  - 122.457824365
],
[
  38.1647573209,
  - 122.457752984
],
[
  38.1647206091,
  - 122.457684135
],
[
  38.1646253089,
  - 122.457535228
],
[
  38.164545551,
  - 122.457411332
],
[
  38.1645352623,
  - 122.45739535
],
[
  38.164469589,
  - 122.457293333
],
[
  38.1642850457,
  - 122.457010257
],
[
  38.163685078,
  - 122.456094433
],
[
  38.1632980054,
  - 122.455504306
],
[
  38.1629972564,
  - 122.455057931
],
[
  38.1629549725,
  - 122.454999384
],
[
  38.1629491947,
  - 122.454989793
],
[
  38.1629469723,
  - 122.45498723
],
[
  38.1629434171,
  - 122.454984332
],
[
  38.1629386074,
  - 122.454981631
],
[
  38.1629327949,
  - 122.454979578
],
[
  38.1629263453,
  - 122.45497849
],
[
  38.1629196859,
  - 122.454978525
],
[
  38.162913263,
  - 122.454979677
],
[
  38.1629075016,
  - 122.454981779
],
[
  38.1629027619,
  - 122.454984506
],
[
  38.1629006243,
  - 122.454986286
],
[
  38.1628749281,
  - 122.455020253
],
[
  38.162757086,
  - 122.455153301
],
[
  38.1627312414,
  - 122.455166128
],
[
  38.1627099086,
  - 122.455172587
],
[
  38.1626880892,
  - 122.455175381
],
[
  38.1626661689,
  - 122.455174518
],
[
  38.1626445303,
  - 122.455169997
],
[
  38.1626235653,
  - 122.455161801
],
[
  38.1626036908,
  - 122.455149906
],
[
  38.1625853749,
  - 122.45513429
],
[
  38.1625668541,
  - 122.455112217
],
[
  38.1625315444,
  - 122.455035129
],
[
  38.1625037759,
  - 122.454962533
],
[
  38.1624806697,
  - 122.454888141
],
[
  38.16246298,
  - 122.454814892
],
[
  38.1624290003,
  - 122.454673962
],
[
  38.1623996144,
  - 122.45453051
],
[
  38.1623751944,
  - 122.454386097
],
[
  38.1623559109,
  - 122.454241935
],
[
  38.1623337931,
  - 122.454062234
],
[
  38.1623173226,
  - 122.453886481
],
[
  38.1623006423,
  - 122.453798558
],
[
  38.1622777234,
  - 122.453710724
],
[
  38.1622488545,
  - 122.453624475
],
[
  38.1622141366,
  - 122.453540194
],
[
  38.1621736974,
  - 122.453458265
],
[
  38.1621276931,
  - 122.45337907
],
[
  38.162077219,
  - 122.453304336
],
[
  38.1620183833,
  - 122.453236131
],
[
  38.1619547346,
  - 122.453169072
],
[
  38.1618876083,
  - 122.453104767
],
[
  38.1618384413,
  - 122.453060706
],
[
  38.161787035,
  - 122.453020688
],
[
  38.1617328536,
  - 122.452984232
],
[
  38.1616761604,
  - 122.452951541
],
[
  38.1616169733,
  - 122.45292267
],
[
  38.1612501415,
  - 122.452768949
],
[
  38.1609111578,
  - 122.452640732
],
[
  38.1607053619,
  - 122.452554544
],
[
  38.1603608524,
  - 122.452418828
],
[
  38.1601010486,
  - 122.452353877
],
[
  38.1595795344,
  - 122.452152342
],
[
  38.1589060636,
  - 122.451866467
],
[
  38.1588587767,
  - 122.451850665
],
[
  38.1588107906,
  - 122.451841215
],
[
  38.1587618852,
  - 122.451837965
],
[
  38.1587176947,
  - 122.451840695
],
[
  38.1586814532,
  - 122.451855992
],
[
  38.158643975,
  - 122.451878141
],
[
  38.1586102467,
  - 122.451904758
],
[
  38.1585808717,
  - 122.451935152
],
[
  38.1585563089,
  - 122.451968558
],
[
  38.1585368552,
  - 122.452004196
],
[
  38.1585226491,
  - 122.452041337
],
[
  38.1585131105,
  - 122.452081895
],
[
  38.1585058414,
  - 122.452127829
],
[
  38.1585043571,
  - 122.452172007
],
[
  38.1585083263,
  - 122.452216099
],
[
  38.1585177632,
  - 122.452259701
],
[
  38.1585326778,
  - 122.452302336
],
[
  38.1585530306,
  - 122.452343429
],
[
  38.1585786878,
  - 122.452382315
],
[
  38.1586093937,
  - 122.452418285
],
[
  38.1586447626,
  - 122.452450634
],
[
  38.1586821357,
  - 122.452477172
],
[
  38.1590456338,
  - 122.452626032
],
[
  38.1598166186,
  - 122.452935128
],
[
  38.1602241867,
  - 122.453100263
],
[
  38.1605242773,
  - 122.45325048
],
[
  38.1606204858,
  - 122.453329851
],
[
  38.1607130459,
  - 122.45340745
],
[
  38.1608010063,
  - 122.453526129
],
[
  38.1613378138,
  - 122.454391849
],
[
  38.1615271294,
  - 122.454696657
]
]
