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
import traceback
kivy.require('1.9.1')
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

class AnalysisPageCollection(object):
    """
    Wrapper for a collection of AnalysisPage objects.
    """

    def __init__(self, **kwargs):
        self._screens = []

    def add_screen(self, screen):
        self._screens.append(screen)

    def select_map(self, latitude, longitude):
        for s in self._screens:
            s.select_map(latitude, longitude)

    def refresh_view(self):
        for s in self._screens:
            s.refresh_view()

    def add_reference_mark(self, source, color):
        for s in self._screens:
            s.add_reference_mark(source, color)

    def remove_reference_mark(self, source):
        for s in self._screens:
            s.remove_reference_mark(source)

    def update_reference_mark(self, source, point):
        for s in self._screens:
            s.update_reference_mark(source, point)

    def add_map_path(self, source_ref, path, color):
        for s in self._screens:
            s.add_map_path(source_ref, path, color)

    def remove_map_path(self, source_ref):
        for s in self._screens:
            s.remove_map_path(source_ref)

    def add_lap(self, source_ref):
        for s in self._screens:
            s.add_lap(source_ref)

    def remove_lap(self, source_ref):
        for s in self._screens:
            s.remove_lap(source_ref)

    def set_selected_channels(self, channels):
        for s in self._screens:
            s.set_selected_channels(channels)

class AnalysisPage(Screen):
    """
    Base Class for an Analysis Screen. Extend this class to create a new Page for the analysis view
    """
    track = ObjectProperty()
    track_manager = ObjectProperty()
    datastore = ObjectProperty()

    def select_map(self, latitude, longitude):
        """
        Find and display a nearby track by latitude / longitude
        :param latitude
        :type  latitude float
        :param longitude
        :type longitude float
        :returns the selected track
        :type Track 
        """
        pass

    def refresh_view(self):
        """
        Refresh the current view
        """
        pass

    def add_reference_mark(self, source, color):
        """
        Add a reference mark for the specified source
        :param source the key representing the reference mark
        :type source string
        :param color the color of the reference mark
        :type color list
        """
        pass

    def remove_reference_mark(self, source):
        """
        Removes the specified reference mark
        :param source the key for the reference mark to remove
        :type source string
        """
        pass

    def update_reference_mark(self, source, point):
        """
        Update the specified reference mark
        :param source the key for the reference mark
        :type source string
        :param point the updated point
        :type GeoPoint
        """
        pass

    def add_map_path(self, source_ref, path, color):
        """
        Add a map path for the specified session/lap source reference
        :param source_ref the lap/session reference
        :type source_ref SourceRef
        :param path a list of points representing the map path
        :type path list
        :param color the path of the color
        :type color list
        """
        pass

    def remove_map_path(self, source_ref):
        """
        Remove the map path for the specified session/lap source reference
        :param source_ref the source session/lap reference
        :type source_ref SourceRef
        """
        pass

    def add_lap(self, source_ref):
        '''
        Add a lap specified by the source reference
        :param source_ref indicating the selected session / lap
        :type SourceRef
        '''
        pass

    def remove_lap(self, source_ref):
        '''
        Remove a lap specified by the source reference
        :param source_ref indicating the selected session / lap
        :type SourceRef
        '''
        pass
    
    def set_selected_channels(self, channels):
        """
        Update the list of selected channels
        :param channels the list of selected channels
        :type channels
        """
