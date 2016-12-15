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
from kivy.clock import Clock
from fieldlabel import FieldLabel
from kivy.properties import NumericProperty, ListProperty, StringProperty
from kivy.app import Builder
from kivy.graphics import Color, Rectangle
from utils import *
from random import random as r

BAR_GRAPH_GAUGE_KV = """
<BarGraphGauge>:
    RelativeLayout:
        StencilView:
            size_hint: (None, 0.9)
            id: stencil
            canvas.after:
                Color:
                    rgba: root.color
                Rectangle:
                    pos: self.pos
                    size: self.size
    FieldLabel:
        id: value
        font_size: min(dp(18), max(1,self.height * 1.0))
"""

class BarGraphGauge(AnchorLayout):
    Builder.load_string(BAR_GRAPH_GAUGE_KV)
    minval = NumericProperty(0)
    maxval = NumericProperty(100)
    value = NumericProperty(0, allownone=True)
    color = ListProperty([1, 1, 1, 0.5])
    orientation = StringProperty('left-right')

    def __init__(self, **kwargs):
        self.left_right = True
        self.zero_centered = False
        super(BarGraphGauge, self).__init__(**kwargs)
        self.bind(pos=self._refresh_value)
        self.bind(size=self._refresh_value)

    def on_precision(self, instance, value):
        self._refresh_format()

    def on_minval(self, instance, value):
        self.zero_centered = value < 0
        self._refresh_value()

    def on_maxval(self, instance, value):
        self._refresh_value()

    def on_value(self, instance, value):
        self._refresh_value()

    def on_orientation(self, instance, value):
        Clock.schedule_once(lambda dt: self._refresh_orientation())

    def _refresh_orientation(self):
        self.left_right = True if self.orientation == 'left-right' else False
        self.ids.value.halign = 'left' if self.left_right == True else 'right'
        self._refresh_value()

    def _refresh_value(self, *args):
        stencil = self.ids.stencil
        value = self.value
        width = 0
        x = 0
        if value is None:
            value = '- - -'
        else:
            minval = self.minval
            maxval = self.maxval
            channel_range = (maxval - minval)
            if self.zero_centered:
                channel_range = max(abs(minval), abs(maxval))
            else:
                channel_range = (maxval - minval)
            pct = 0 if channel_range == 0 else abs(value) / channel_range
            if self.zero_centered:
                center = self.width / 2.0
                width = center * pct
                x = center - width if value < 0 else center
            else:
                width = self.width * pct
                x = 0 if self.left_right == True else self.width - width
        stencil.width = width
        stencil.x = x
        self.ids.value.text = '{:.2f}'.format(value).rstrip('0').rstrip('.')
