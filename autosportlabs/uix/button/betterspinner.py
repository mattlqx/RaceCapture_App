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
from kivy.uix.spinner import Spinner
from kivy.app import Builder

BETTER_SPINNER_KV = """
#:import Factory kivy.factory.Factory
<BetterSpinnerOption@SpinnerOption>:
    font_name: 'resource/fonts/ASL_regular.ttf'
    font_size: self.height * 0.5

<BetterSpinner>:
    font_name: 'resource/fonts/ASL_regular.ttf'
    font_size: self.height * 0.5
    option_cls: Factory.get('BetterSpinnerOption')
"""

class BetterSpinner(Spinner):
    """An improved Spinner with customizations we want.
    """
    Builder.load_string(BETTER_SPINNER_KV)
    def __init__(self, **kwargs):
        super(BetterSpinner, self).__init__(**kwargs)

