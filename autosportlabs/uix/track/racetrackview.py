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
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.app import Builder
from kivy.metrics import dp
from kivy.graphics import Color, Line
from autosportlabs.racecapture.geo.geopoint import GeoPoint
from autosportlabs.uix.track.trackmap import TrackMapView
from utils import *

Builder.load_file('autosportlabs/uix/track/racetrackview.kv')

class RaceTrackView(BoxLayout):
    def __init__(self, **kwargs):
        super(RaceTrackView, self).__init__(**kwargs)

    def loadTrack(self, track):
        self.initMap(track)

    def initMap(self, track):
        self.ids.trackmap.setTrackPoints(track.map_points)

    def remove_reference_mark(self, key):
        self.ids.trackmap.remove_marker(key)

    def add_reference_mark(self, key, color):
        trackmap = self.ids.trackmap
        if trackmap.get_marker(key) is None:
            trackmap.add_marker(key, color)

    def update_reference_mark(self, key, geo_point):
        self.ids.trackmap.update_marker(key, geo_point)

    def add_map_path(self, key, path, color):
        self.ids.trackmap.add_path(key, path, color)

    def remove_map_path(self, key):
        self.ids.trackmap.remove_path(key)

    def add_heat_values(self, key, heat_values):
        self.ids.trackmap.add_heat_values(key, heat_values)

    def remove_heat_values(self, key):
        self.ids.trackmap.remove_heat_values(key)
