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

from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import NumericProperty

__all__ = ('toast')

TOAST_KV='''
<_Toast@Label>:
    size_hint: (None, None)
    halign: 'center'
    valign: 'middle'
    font_name: "resource/fonts/ASL_light.ttf"
    color: (1.0, 1.0, 1.0, self._transparency)
    canvas:
        Color:
            rgba: (0.3, 0.3, 0.3, self._transparency)
        Rectangle:
            size: self.size
            pos: self.pos
        Color:
            rgba: (0.0, 0.0, 0.0, 1.0)
        Rectangle:
            size: (self.size[0] - 2, self.size[1] - 2)
            pos: (self.pos[0] + 1, self.pos[1] + 1)
        Color:
            rgba: self.color
        Rectangle:
            texture: self.texture
            size: self.texture_size
            pos: int(self.center_x - self.texture_size[0] / 2.), int(self.center_y - self.texture_size[1] / 2.)

'''

class _Toast(Label):
    _transparency = NumericProperty(1.0)
    Builder.load_string(TOAST_KV)

    def __init__(self, text, *args, **kwargs):
        '''Show the toast in the main window.  The attatch_to logic from 
        :class:`~kivy.uix.modalview` isn't necessary because a toast really
        does need to go on top of everything.
        '''
        self._bound = False
        self._center_on = kwargs.get('center_on')
        super(_Toast, self).__init__(text=text, *args, **kwargs)
    
    def show(self, length_long, *largs):
        duration = 5000 if length_long else 1000
        rampdown = duration * 0.1
        if rampdown > 500:
            rampdown = 500
        if rampdown < 100:
            rampdown = 100
        self._rampdown = rampdown
        self._duration = duration - rampdown
        Window.add_widget(self)
        Clock.schedule_interval(self._in_out, 1/60.0)

    def on_texture_size(self, instance, size):
        self.size = map(lambda i: i * 1.3, size)
        if not self._bound:
            Window.bind(on_resize=self._align)
            self._bound = True
        self._align(None, Window.size)
            
    def _align(self, win, size):
        self.x = (size[0] - self.width) / 2.0
        if self._center_on:
            self.y = self._center_on.y + self._center_on.size[1] * 0.1
        else:
            self.y = size[1] * 0.1

    def _in_out(self, dt):
        self._duration -= dt * 1000
        if self._duration <= 0:
            self._transparency = 1.0 + (self._duration / self._rampdown)
        if -(self._duration) > self._rampdown:
            Window.remove_widget(self)
            return False

def toast(text, length_long=False, center_on=None):
    """Display a short message on the screen that will automatically dismiss
    :param text the text to display
    :type text String
    :param length_long True if the display should persist longer
    :type length_long bool
    :param center_on The widget to center on. if not specified, centers on the window
    :type center_on Widget
    :return None
    """
    _Toast(text=text, center_on=center_on).show(length_long)
