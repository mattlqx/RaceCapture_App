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
import unittest
from autosportlabs.racecapture.tracks.trackmanager import TrackMap
from autosportlabs.util.timeutil import time_to_epoch

class TrackMapTest(unittest.TestCase):

    def test_create_trackmap(self):
        tm = TrackMap.create_new()
        self.assertEqual(tm.name, TrackMap.DEFAULT_TRACK_NAME)
        self.assertEqual(tm.configuration, TrackMap.DEFAULT_CONFIGURATION)
        self.assertEqual(len(tm.track_id), 32)
        epoch_time = time_to_epoch(tm.created)
        self.assertTrue(epoch_time > 0)
        self.assertTrue(len(tm.map_points) == 0)
        self.assertTrue(len(tm.sector_points) == 0)

def main():
    unittest.main()

if __name__ == "__main__":
    main()



