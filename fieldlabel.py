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

from kivy.uix.label import Label
from kivy.metrics import sp
from kivy.app import Builder
from kivy.clock import Clock

class FieldLabel(Label):
    def __init__(self, **kwargs):
        super(FieldLabel, self).__init__(**kwargs)
        self.bind(width=self.width_changed)
        self.spacing = (20, 3)
        self.font_name = "resource/fonts/ASL_regular.ttf"
        self.font_size = sp(20)
        self.shorten = True
        self.shorten_from = 'right'

    def width_changed(self, instance, size):
        self.text_size = (size, None)

class AutoShrinkFieldLabel(Label):
    Builder.load_string("""
<AutoShrinkFieldLabel>:
    font_name: "resource/fonts/ASL_regular.ttf"
    font_size: self.height
    on_texture: root._change_font_size()
    on_size: root._change_font_size()
    #on_width: self._width_changed()
    shorten: False
    max_lines: 1
    """)

    def __init__(self, **kwargs):
        super(AutoShrinkFieldLabel, self).__init__(**kwargs)

    def _width_changed(self, instance, size):
        self.text_size = (size, None)

    def on_text(self, instance, value):
        Clock.schedule_once(self._change_font_size, 0.1)

    def _change_font_size(self, *args):
        try:
            if self.texture_size[0] > self.width:  # or v.texture_size[1] > v.height:
                self.font_size -= 1
                Clock.schedule_once(self._change_font_size, 0.1)
        except Exception as e:
            Logger.warn('Failed to change font size: {}'.format(e))

