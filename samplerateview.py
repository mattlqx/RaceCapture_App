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
from kivy.uix.boxlayout import BoxLayout
from utils import *
from sampleratespinner import SampleRateSpinner

from kivy.app import Builder
Builder.load_file('samplerateview.kv')            


class SampleRateSelectorView(BoxLayout):
    def __init__(self, **kwargs):
        super(SampleRateSelectorView, self).__init__(**kwargs)
        self.register_event_type('on_sample_rate')

    def on_sample_rate(self, value):
        pass
    
    def setValue(self, value, max_rate = None):
        if max_rate:
            self.set_max_rate(max_rate)
        kvFind(self, 'rcid', 'sampleRate').setFromValue(value)

    def onSelect(self, instance, value):
        selectedValue = instance.getSelectedValue()
        self.dispatch('on_sample_rate', int(selectedValue) if selectedValue is not None else 0)
        
    def set_max_rate(self, max):
        kvFind(self, 'rcid', 'sampleRate').set_max_rate(max)
