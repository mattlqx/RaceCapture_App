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
kivy.require('1.9.0')
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, ListProperty
from autosportlabs.uix.color.colorgradient import SimpleColorGradient, HeatColorGradient
from kivy.graphics import Color, Rectangle
from kivy.app import Builder

class GradientBox(BoxLayout):
    '''
    Draws a color gradient box with the specified base color
    '''
    color = ObjectProperty([1.0, 1.0, 1.0], allownone=True)
    GRADIENT_STEP = 0.01

    def __init__(self, **kwargs):
        super(GradientBox, self).__init__(**kwargs)
        self.bind(pos=self._update_gradient, size=self._update_gradient)
        self._update_gradient()

    def on_color(self, instance, value):
        self._update_gradient()

    def _update_gradient(self, *args):
        '''
        Actually draws the gradient
        '''
        color_gradient = HeatColorGradient() if self.color is None else SimpleColorGradient(max_color=self.color)
        self.canvas.clear()
        step = GradientBox.GRADIENT_STEP
        pct = step
        with self.canvas:
            while pct < 1.0:
                color = color_gradient.get_color_value(pct)
                Color(*color)
                slice_width = self.width * step
                pos = (self.x + (self.width * pct), self.y)
                size = (slice_width, self.height)
                Rectangle(pos=pos, size=size)
                pct += step


class ColorLegend(BoxLayout):
    '''
    Represents a single color legend. The entire layout is drawn with the color specified.
    '''
    Builder.load_string('''
<ColorLegend>:
    orientation: 'vertical'
    BoxLayout:
        size_hint_y: (1.0 - root.height_pct) / 2.0
    BoxLayout:
        id: legend
        canvas.before:
            Color:
                rgba: root.bar_color
            Rectangle:
                pos: self.pos
                size: self.size
        id: color_bar
        size_hint_y: root.height_pct
    BoxLayout:
        size_hint_y: (1.0 - root.height_pct) / 2.0
''')
    bar_color = ListProperty([1.0, 1.0, 1.0, 1.0])
    height_pct = NumericProperty(0.1)


class GradientLegend(BoxLayout):
    '''
        Represents a gradient legend, specified by min / max colors
    '''
    Builder.load_string('''
<GradientLegend>:
    orientation: 'vertical'
    BoxLayout:
        size_hint_y: (1.0 - root.height_pct) / 2.0
    GradientBox:
        size_hint_y: root.height_pct
        color: root.color
        id: gradient
    BoxLayout:
        size_hint_y: (1.0 - root.height_pct) / 2.0
    ''')

    color = ObjectProperty([0.0, 0.0, 0.0, 1.0], allownone=True)
    height_pct = NumericProperty(0.1)
