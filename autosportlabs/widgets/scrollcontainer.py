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

from functools import partial
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
class ScrollContainer(ScrollView):
	'''
	A custom ScrollView that makes some improvements in touch selection. 
	
	ScrollContainer better tracks the difference in scroll distance so imprecise touch events
	aren't registered as scrolling, but an actual touch event; making selection within a 
	scrolling container easier on mobile devices.
	
	This scroll container is oriented towards vertically scrolling windows.
	'''	
	def __init__(self, **kwargs):
		#The starting vertical scroll position
		self._start_y = None
		super(ScrollContainer, self).__init__(**kwargs)

	def on_scroll_start(self, touch, check_children=True):
		'''
		Override the on_scroll_start so that we can capture the original start position
		'''
		self._start_y = touch.y
		return super(ScrollContainer, self).on_scroll_start(touch, check_children)

	def on_scroll_stop(self, touch, check_children=True):
		'''
		Override the on_scroll_stop so that we can fire a full 
		touch event if we haven't scrolled too far
		'''
		super(ScrollContainer, self).on_scroll_stop(touch,check_children)
		ud = touch.ud.get(self._get_uid())
		if ud:				
			start_y = self._start_y
			self._start_y = None
			#if we're handling a scroll stop event and the total distance is less than the
			#configured scroll distance, then register it as a full touch event (down and up)
			if ud['mode'] == 'scroll' and start_y and abs(start_y - touch.y) < self.scroll_distance:
				self.simulate_touch_down(touch)
				Clock.schedule_once(partial(self._do_touch_up, touch), .1)
			
		
