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
from iconbutton import TileIconButton
from kivy.app import Builder

Builder.load_file('autosportlabs/uix/button/featurebutton.kv')

class FeatureButton(TileIconButton):
    def __init__(self, **kwargs):
        super(FeatureButton, self).__init__(**kwargs)
        self.tile_color =  (1.0, 1.0, 1.0, 1.0)

class DisabledFeatureButton(FeatureButton):
    def __init__(self, **kwargs):
        super(DisabledFeatureButton, self).__init__(**kwargs)
        self.tile_color = (1.0, 1.0, 1.0, 1.0)
