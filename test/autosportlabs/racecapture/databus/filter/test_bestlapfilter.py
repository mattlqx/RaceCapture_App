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

import unittest
from autosportlabs.racecapture.databus.filter.bestlapfilter import BestLapFilter
from autosportlabs.racecapture.data.channels import SystemChannels

class BestLapFilterTest(unittest.TestCase):
    system_channels = SystemChannels()
    
    def test_bestlap_meta(self):
        sample_filter = BestLapFilter(self.system_channels)
        meta = sample_filter.get_channel_meta({'LapTime': {'foo': 'bar'}})
        self.assertTrue(BestLapFilter.BEST_LAPTIME_KEY in meta)
        
    def test_best_lap_default(self):
        sample_filter = BestLapFilter(self.system_channels)
        channel_data = {}
        
        sample_filter.filter(channel_data)
        self.assertIsNone(channel_data.get(BestLapFilter.BEST_LAPTIME_KEY))

    def test_first_best_lap(self):
        sample_filter = BestLapFilter(self.system_channels)
        channel_data = {'LapTime':111.111}
        
        sample_filter.filter(channel_data)
        self.assertEqual(111.111, channel_data.get(BestLapFilter.BEST_LAPTIME_KEY))

    def test_next_best_lap(self):
        sample_filter = BestLapFilter(self.system_channels)
        channel_data = {'LapTime':111.111}
        
        sample_filter.filter(channel_data)
        self.assertEqual(111.111, channel_data.get(BestLapFilter.BEST_LAPTIME_KEY))
        
        channel_data['LapTime'] = 110.111
        sample_filter.filter(channel_data)
        self.assertEqual(110.111, channel_data.get(BestLapFilter.BEST_LAPTIME_KEY))
        
    def test_best_lap_preserved(self):
        sample_filter = BestLapFilter(self.system_channels)
        channel_data = {'LapTime':111.111}
        
        sample_filter.filter(channel_data)
        self.assertEqual(111.111, channel_data.get(BestLapFilter.BEST_LAPTIME_KEY))
        
        channel_data['LapTime'] = 112.111
        sample_filter.filter(channel_data)
        self.assertEqual(111.111, channel_data.get(BestLapFilter.BEST_LAPTIME_KEY))
