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
kivy.require('1.9.1')
from utils import kvFind
from kivy.properties import NumericProperty
from autosportlabs.racecapture.views.dashboard.widgets.graphicalgauge import GraphicalGauge
class FontGraphicalGauge(GraphicalGauge):
    
    def __init__(self, **kwargs):
        super(FontGraphicalGauge, self).__init__(**kwargs)

    def on_min(self, instance, value):
        self._refresh_gauge()
        
    def on_max(self, instance, value):
        self._refresh_gauge()
        
    def update_colors(self):
        self.graphView.color = self.select_alert_color()
        return super(FontGraphicalGauge, self).update_colors()
        
    def _refresh_gauge(self):
        try:
            value = self.value
            min = self.min
            max = self.max
            railedValue = value
            view = self.graphView
            if railedValue > max:
                railedValue = max
            if railedValue < min:
                railedValue = min
    
            range = max - min
            offset = railedValue - min
            view.text = '' if offset == 0 else unichr(ord(u'\uE600') + int(((offset * 100) / range)) - 1)
                
        except Exception as e:
            print('error setting font gauge value ' + str(e))
        
    def on_value(self, instance, value):
        self._refresh_gauge()
        return super(FontGraphicalGauge, self).on_value(instance, value)


