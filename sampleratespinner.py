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
from mappedspinner import MappedSpinner

class SampleRateSpinner(MappedSpinner):
    all_sample_rates = {0:'Disabled', 1:'1 Hz', 5:'5 Hz', 10:'10 Hz', 25:'25 Hz', 50:'50 Hz', 100:'100 Hz', 200:'200 Hz', 500:'500 Hz', 1000:'1000 Hz'}
    
    def __init__(self, **kwargs):
        super(SampleRateSpinner, self).__init__(**kwargs)

    def set_max_rate(self, max):
        rates = dict((k, v) for k, v in self.all_sample_rates.items() if k <= max)
        self.setValueMap(rates, 'Disabled')
