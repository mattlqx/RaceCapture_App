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
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stencilview import StencilView
from fieldlabel import FieldLabel
from kivy.properties import NumericProperty, ListProperty
from kivy.app import Builder
from kivy.graphics import Color, Rectangle
from utils import *
from random import random as r

Builder.load_file('autosportlabs/uix/gauge/bargraphgauge.kv')
        
class BarGraphGauge(AnchorLayout):    
    minval = NumericProperty(0)
    maxval = NumericProperty(100)
    value = NumericProperty(0, allownone=True)
    color = ListProperty([1, 1, 1, 0.5])
    
    def __init__(self, **kwargs):
        super(BarGraphGauge, self).__init__(**kwargs)        
        
    def on_minval(self, instance, value):
        self._refresh_value()
        
    def on_maxval(self, instance, value):
        self._refresh_value()
        
    def on_value(self, instance, value):
        self._refresh_value()
        
    def _refresh_value(self):
        stencil = self.ids.stencil
        value = self.value
        width = 0
        if value is None:
            value = '- - -'
        else:
            minval = self.minval
            maxval = self.maxval
            channel_range = (maxval - minval)
            pct = 0 if channel_range == 0 else ((value - minval) / channel_range) 
            width = self.width * pct
        stencil.width = width
        self.ids.value.text = str(value)
