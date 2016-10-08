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
from kivy.properties import NumericProperty
from autosportlabs.uix.track.trackmap import TrackMapView
from autosportlabs.racecapture.tracks.trackmanager import TrackMap
from autosportlabs.racecapture.geo.geopoint import GeoPoint
from autosportlabs.racecapture.geo.geoprovider import GeoProvider
from autosportlabs.racecapture.views.util.alertview import confirmPopup
from autosportlabs.racecapture.config.rcpconfig import GpsConfig
from autosportlabs.racecapture.theme.color import ColorScheme
from autosportlabs.uix.toast.kivytoast import toast
from plyer import gps

TRACK_BUILDER_KV = """
<TrackBuilderView>:
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
        TrackMapView:
            id: track
        AnchorLayout:
            anchor_y: 'top'
            anchor_x: 'right'
            GridLayout:
                cols:2
                rows:1
                size_hint_y: 0.1
                size_hint_x: 0.1
                IconButton:
                    id: internal_status
                    text: u'\uf10a'
                    color: [0.3, 0.3, 0.3, 0.2]        
                    font_size: self.height * 0.8            
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
        Button:
            id: start_button
            text: 'Start'
            on_press: root.on_set_start_point(*args)
        Button:
            id: add_sector_button
            text: 'Sector'
            on_press: root.on_add_sector_point(*args)
        Button:
            id: add_finish_button
            text: 'Finish'
            on_press: root.on_set_finish_point(*args)
"""

class TrackBuilderView(BoxLayout):
    GPS_ACTIVE_COLOR = [0.0, 1.0, 0.0, 1.0]
    GPS_INACTIVE_COLOR = [1.0, 0.0, 0.0, 1.0]
    INTERNAL_ACTIVE_COLOR = [0.0, 1.0, 1.0, 1.0]
    INTERNAL_INACTIVE_COLOR = [0.3, 0.3, 0.3, 0.3]

    Builder.load_string(TRACK_BUILDER_KV)

    # minimum separation needed between start, finish and sector targets
    MINIMUM_TARGET_SEPARATION_METERS = 50

    # default minimum distance needed to travel before registering a trackmap point
    DEFAULT_MINIMUM_TRAVEL_DISTANCE_METERS = 1

    # how long until we time out
    STATUS_LINGER_DURATION = 2.0

    minimum_travel_distance = NumericProperty(DEFAULT_MINIMUM_TRAVEL_DISTANCE_METERS)

    def __init__(self, rc_api, databus, **kwargs):
        super(TrackBuilderView, self).__init__(**kwargs)
        self._databus = databus
        self._rc_api = rc_api
        self._geo_provider = GeoProvider(rc_api=rc_api, databus=databus)
        self._geo_provider.bind(on_location=self._on_location)
        self._geo_provider.bind(on_internal_gps_available=self._on_internal_gps_available)
        self._geo_provider.bind(on_gps_source=self._on_gps_source)
        self.current_point = None
        self.last_point = None
        self.track = TrackMap()
        self._update_trackmap()
        self._init_status_monitor()
        self._update_button_states()
        if not self._rc_api.connected:
            self._geo_provider._start_internal_gps()

    def _init_status_monitor(self):
        self._status_decay = Clock.create_trigger(self._on_status_decay, TrackBuilderView.STATUS_LINGER_DURATION)
        self._status_decay()

    def _on_status_decay(self, *args):
        self.ids.internal_status.color = TrackBuilderView.INTERNAL_INACTIVE_COLOR
        self.ids.gps_status.color = TrackBuilderView.GPS_INACTIVE_COLOR

    def _update_status_indicators(self):
        self._status_decay.cancel()
        internal_active = self._geo_provider.location_source_internal
        self.ids.internal_status.color = TrackBuilderView.INTERNAL_ACTIVE_COLOR if internal_active else TrackBuilderView.INTERNAL_INACTIVE_COLOR
        self.ids.gps_status.color = TrackBuilderView.GPS_ACTIVE_COLOR
        self._status_decay()

    def _update_button_states(self):
        current_point = self.current_point
        start_point = self.track.start_finish_point
        finish_point = self.track.finish_point

        sector_points = self.track.sector_points
        # to determine if we can add another sector, we reference the start line
        # or the last sector point, if it exists
        last_sector_point = None if len(sector_points) == 0 else self.track.sector_points[-1]
        reference_point = last_sector_point if last_sector_point is not None else start_point

        # Can only add a sector if we're the minimum distance from the reference point
        can_add_sector = (start_point is not None and
                current_point is not None and
                current_point.dist_pythag(reference_point) >= TrackBuilderView.MINIMUM_TARGET_SEPARATION_METERS)

        # we can't add a sector if the finish point is defined
        can_add_sector = False if finish_point is not None else can_add_sector

        self.ids.add_sector_button.disabled = not can_add_sector

        # must be minimum distance from start point to create a finish point
        can_finish = (start_point is not None and
                    current_point is not None and
                    current_point.dist_pythag(start_point) >= TrackBuilderView.MINIMUM_TARGET_SEPARATION_METERS)

        # also must be minimum distance from last sector point, if it exists
        can_finish = False if (last_sector_point is not None and
                    current_point.dist_pythag(last_sector_point) < TrackBuilderView.MINIMUM_TARGET_SEPARATION_METERS) else can_finish

        # can't finish twice
        can_finish = False if finish_point is not None else can_finish

        self.ids.add_finish_button.disabled = not can_finish

        # can we start?
        can_start = self.current_point is not None
        self.ids.start_button.disabled = not can_start

    def _update_trackmap(self):
        self.ids.track.setTrackPoints(self.track.map_points)
        self.ids.track.sector_points = self.track.sector_points

    def _add_trackmap_point(self, point):
        self.track.map_points.append(point)
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

        # we can add a point if we have started, but not finished yet
        can_add_point = track.start_point is not None and track.finish_point is None

        # however, we can't add a point if we're too close to the last point
        can_add_point = False if (self.last_point is not None and
                                  self.last_point.dist_pythag(point) < self.minimum_travel_distance) else can_add_point

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

        if len(self.track.map_points) > 1 and self.track.start_finish_point is not None:
            popup = confirmPopup("Restart", "Restart Track Map?", confirm_restart)
        else:
            self._start_new_track()

    def _start_new_track(self):
        self.track.map_points = []
        self.track.sector_points = []
        self.track.finish_point = None
        start_point = self.current_point
        self.track.start_finish_point = start_point
        self.ids.track.start_point = start_point
        self.ids.track.finish_point = None
        self._add_trackmap_point(start_point)
        self._update_button_states()
        self._update_trackmap()

    def on_set_finish_point(self, *args):
        finish_point = self.current_point
        self._add_trackmap_point(finish_point)
        self.ids.track.finish_point = finish_point
        self.track.finish_point = finish_point
        self._update_trackmap()
        self._update_button_states()

    def on_add_sector_point(self, *args):
        self.track.sector_points.append(self.current_point)
        self._update_trackmap()
        self._update_button_states()


