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
from kivy.uix.widget import Widget
from kivy.app import Builder
from autosportlabs.uix.baselabel import BaseLabel

Builder.load_file('autosportlabs/widgets/separator.kv')

class HLineSeparator(BaseLabel):
    pass

class HSeparator(BaseLabel):
    pass
    
class VSeparator(Widget):
    pass
    
class HSeparatorMinor(BaseLabel):
    def __init__(self, **kwargs):
        super(HSeparatorMinor, self).__init__(**kwargs)
