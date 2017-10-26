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
import json
from autosportlabs.racecapture.data.sampledata import Sample

TEST_SAMPLE1 = '{"s":{"t":33,"meta":[{"nm":"Battery","ut":"Volts","sr":1},{"nm":"AccelX","ut":"G","sr":25},{"nm":"AccelY","ut":"G","sr":25},{"nm":"AccelZ","ut":"G","sr":25},{"nm":"Yaw","ut":"Deg/Sec","sr":25},{"nm":"Latitude","ut":"Degrees","sr":50},{"nm":"Longitude","ut":"Degrees","sr":50},{"nm":"Speed","ut":"MPH","sr":50},{"nm":"Time","ut":"","sr":50},{"nm":"Distance","ut":"Miles","sr":50},{"nm":"LapCount","ut":"Count","sr":1},{"nm":"LapTime","ut":"Min","sr":1},{"nm":"Sector","ut":"Count","sr":1},{"nm":"SectorTime","ut":"Min","sr":1}],"d":[0.00,2.50,2.50,-2.50,397.0,0.000000,0.000000,0.00,0.000000,0.000,0,0.0000,0,0.0000,16383]}}'

class SampleDataTest(unittest.TestCase):

    def test_sample_data(self):
        sampleJson = json.loads(TEST_SAMPLE1)
        sample = Sample()
        sample.fromJson(sampleJson)
        
        self.assertEqual(sampleJson['s']['t'], sample.tick)
        sampleCount = len(sampleJson['s']['meta'])
        self.assertEqual(sampleCount, len(sample.metas.channel_metas))
        self.assertEqual(sampleCount, len(sample.samples))
        
        metaJson = sampleJson["s"]["meta"]
        
        sampleIndex = 0
        for m in metaJson:
            self.assertEqual(m['nm'], sample.samples[sampleIndex].channelMeta.name)
            self.assertEqual(m['ut'], sample.samples[sampleIndex].channelMeta.units)
            self.assertEqual(m['sr'], sample.samples[sampleIndex].channelMeta.sampleRate)
            sampleIndex += 1
        
        sampleIndex = 0
        dataJson = sampleJson['s']['d']
        
        for sampleItem in sample.samples:
            value = dataJson[sampleIndex]
            self.assertEqual(value, sampleItem.value)
            sampleIndex += 1
    
    def test_meta_data(self):
        pass
        
def main():
    unittest.main()

if __name__ == "__main__":
    main()
