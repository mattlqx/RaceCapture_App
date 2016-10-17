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
from utils import kvFind
from kivy.core.window import Window
from kivy.properties import NumericProperty
from autosportlabs.racecapture.views.dashboard.widgets.gauge import CustomizableGauge

class GraphicalGauge(CustomizableGauge):
    _gaugeView = None
    gauge_size = NumericProperty(0)
    
    def _update_gauge_size(self, size):
        self.gauge_size = size
            
    def __init__(self, **kwargs):
        super(GraphicalGauge, self).__init__(**kwargs)

    def on_size(self, instance, value):
        width = value[0]
        height = value[1]
        size = width if width < height else height
        self._update_gauge_size(size)
        
    @property
    def graphView(self):
        if not self._gaugeView:
            self._gaugeView = kvFind(self, 'rcid', 'gauge')
        return self._gaugeView
    
