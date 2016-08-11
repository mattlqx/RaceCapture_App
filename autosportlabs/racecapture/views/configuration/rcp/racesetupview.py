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

RACE_SETUP_VIEW = """
<RaceSetupView>:
    TracksBrowser:
        id: track_browser
"""


class RaceSetupView(StackLayout):

    Builder.load_string(RACE_SETUP_VIEW)

    def __init__(self, track_manager, **kwargs):
        Logger.info("RaceSetupView: __init__")
        super(RaceSetupView, self).__init__(**kwargs)
        self._track_manager = track_manager
        self.selected_track = None

        self.ids.track_browser.multi_select = False
        self.ids.track_browser.set_trackmanager(self._track_manager)
        Logger.info("RaceSetupView: __init__ done")
        self.ids.track_browser.init_view()
        self.ids.track_browser.bind(on_track_selected=self.on_track_selected)

    def on_track_selected(self, instance, tracks):
        if len(tracks) > 0:
            # Tracks are a set, we only want 1 but we don't want to modify the original
            tracks_copy = tracks.copy()
            id = tracks_copy.pop()
            track = self._track_manager.get_track_by_id(id)
            self.selected_track = track
        else:
            self.selected_track = None
