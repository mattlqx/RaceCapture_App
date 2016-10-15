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
from kivy.app import Builder
from kivy.uix.stacklayout import StackLayout
from kivy.logger import Logger
from kivy.properties import ObjectProperty
from autosportlabs.racecapture.views.tracks.tracksview import TracksBrowser

TRACK_SELECT_VIEW = """
<TrackSelectView>:
    TracksBrowser:
        id: track_browser
"""


class TrackSelectView(StackLayout):

    Builder.load_string(TRACK_SELECT_VIEW)

    def __init__(self, **kwargs):
        super(TrackSelectView, self).__init__(**kwargs)
        current_location = kwargs.get('current_location')
        track_manager = kwargs.get('track_manager')
        self.selected_track = None
        self.register_event_type('on_track_selected')
        self.init_view(track_manager, current_location)

    def init_view(self, track_manager, current_location):
        if track_manager is None:
            # can't init if we don't have track_manager
            # presumably it will happen later
            return
        self.ids.track_browser.multi_select = False
        self.ids.track_browser.bind(on_track_selected=self.track_selected)
        self.ids.track_browser.set_trackmanager(track_manager)
        self._track_manager = track_manager
        self.ids.track_browser.current_location = current_location
        self.ids.track_browser.init_view()
        
    def on_track_selected(self, track):
        pass
    
    def track_selected(self, instance, tracks):
        if len(tracks) > 0:
            # Tracks are a set, we only want 1 but we don't want to modify the original
            tracks_copy = tracks.copy()
            track_id = tracks_copy.pop()
            track = self._track_manager.get_track_by_id(track_id)
            self.selected_track = track
            self.dispatch('on_track_selected', track)
        else:
            self.selected_track = None
