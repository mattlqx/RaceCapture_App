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
kivy.require('1.9.0')
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, ListProperty
from autosportlabs.uix.color.colorgradient import SimpleColorGradient, HeatColorGradient
from autosportlabs.uix.legends.colorlegends import GradientBox
from kivy.graphics import Color, Rectangle
from kivy.app import Builder

class GradientLapLegend(BoxLayout):
    '''
    A compound widget that presents a gradient color legend including session/lap and min/max values
    '''
    Builder.load_string('''
<GradientLapLegend>:
    orientation: 'horizontal'
    spacing: sp(5)
    FieldLabel:
        id: lap
        size_hint_x: 0.5
        halign: 'right'
        valign: 'middle'
        text: '{} :: {}'.format(root.session, root.lap)
    FieldLabel:
        id: min_value
        text: str(root.min_value)
        size_hint_x: 0.2
        halign: 'right'
        valign: 'middle'
        font_size: 0.5 * self.height
    GradientLegend:
        id: legend
        size_hint_x: 0.1
        height_pct: root.height_pct
        color: root.color
    FieldLabel:
        id: max_value
        text: str(root.max_value)
        size_hint_x: 0.2
        halign: 'left'
        valign: 'middle'
        font_size: 0.5 * self.height
''')
    color = ObjectProperty([1.0, 1.0, 1.0], allownone=True)
    min_value = NumericProperty(0.0)
    max_value = NumericProperty(100.0)
    session = StringProperty('')
    lap = StringProperty('')
    height_pct = NumericProperty(0.3)

class LapLegend(BoxLayout):
    '''
    A compound widget that presents a colored legend with session/lap information
    '''
    Builder.load_string('''
<LapLegend>:
    orientation: 'horizontal'
    spacing: sp(5)
    FieldLabel:
        id: lap
        size_hint_x: 0.7
        halign: 'right'
        valign: 'middle'
        text: '{} :: {}'.format(root.session, root.lap)
        color: root.color
    FieldLabel:
        id: laptime
        size_hint_x: 0.3
        halign: 'right'
        valign: 'middle'
        text: '{}'.format(root.lap_time)
    ''')
    color = ListProperty([1.0, 1.0, 1.0, 1.0])
    session = StringProperty('')
    lap = StringProperty('')
    lap_time = StringProperty('')
