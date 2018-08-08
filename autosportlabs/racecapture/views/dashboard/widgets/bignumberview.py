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
kivy.require('1.10.0')
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.app import Builder
from collections import OrderedDict
from kivy.metrics import dp, sp
from kivy.graphics import Color
from utils import kvFind
from iconbutton import TileIconButton
from fieldlabel import AutoShrinkFieldLabel, FieldLabel
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from autosportlabs.racecapture.views.dashboard.widgets.gauge import CustomizableGauge

DEFAULT_NORMAL_COLOR = [0.2, 0.2 , 0.2, 1.0]
DEFAULT_VALUE_FONT_SIZE = sp(180)
DEFAULT_TITLE_FONT_SIZE = sp(25)

class BigNumberView(CustomizableGauge):
    Builder.load_string("""
<BigNumberView>:
    rcid: 'bignumberview'
    RoundedRect:
        id: bg
        rect_color: root.tile_color
    BoxLayout:
        orientation: 'vertical'
        AutoShrinkFieldLabel:
            id: value
            color: root.title_color
            size_hint_y: 0.8
            font_size: self.height * root.value_font_scale
        FieldLabel:
            id: title
            color: root.title_color
            size_hint_y: 0.1
            font_size: self.height
            text: root.title
            halign: 'center'
        BoxLayout:
            size_hint_y: 0.1    
    """)

    value_font_scale = NumericProperty(1.0)

    tile_color = ObjectProperty((0.2, 0.2, 0.2, 1.0))
    value_color = ObjectProperty((1.0, 1.0, 1.0, 1.0))
    title_color = ObjectProperty((1.0, 1.0, 1.0, 1.0))

    def __init__(self, **kwargs):

        super(BigNumberView, self).__init__(**kwargs)
        self.normal_color = DEFAULT_NORMAL_COLOR
        self.initWidgets()

    def initWidgets(self):
        self.alert = 0
        self.warning = 0
        self.max = 0


    def on_title(self, instance, value):
        self.ids.bg.text = str(value) if value else ''

    def on_tile_color(self, instance, value):
        self.ids.bg.rect_color = value

    def on_value_color(self, instance, value):
        self.valueView.color = value

    def update_colors(self):
        self.ids.bg.rect_color = self.select_alert_color()

    def on_channel(self, instance, value):
        self.valueView.font_size = self.height * self.value_font_scale
        return super(BigNumberView, self).on_channel(instance, value)

    def update_title(self, channel, channel_meta):
        try:
            self.title = channel if channel else ''
        except Exception as e:
            Logger.warn('Failed to update digital gauge title: {}'.format(e))

