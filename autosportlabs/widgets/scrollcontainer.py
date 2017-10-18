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

from functools import partial
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.metrics import dp


class ScrollContainer(ScrollView):
    '''
    A custom ScrollView that makes some improvements in touch selection.

    ScrollContainer better tracks the difference in scroll distance so imprecise touch events
    aren't registered as scrolling, but an actual touch event; making selection within a
    scrolling container easier on mobile devices.

    This scroll container is oriented towards vertically scrolling windows.
    '''

    def __init__(self, **kwargs):
        # The starting vertical scroll position
        self._start_y = None
        super(ScrollContainer, self).__init__(**kwargs)
        self.scroll_type = ['bars', 'content']
        self.scroll_wheel_distance = dp(114)
        self.bar_width = dp(20)

