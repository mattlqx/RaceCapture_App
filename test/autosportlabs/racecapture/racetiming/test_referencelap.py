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
from autosportlabs.racecapture.racetiming.referencelap import ReferenceLap
class ReferenceLapTest(unittest.TestCase):

    data = [(0.5, 100),
            (0.6, 123),
            (0.7, 33),
            (0.8, 454),
            (0.9, 11),
            (1.0, 333),
            (1.1, 22)]

    def test_load_sample_data(self):
        rl = ReferenceLap(self.data)

    def test_get_sample_at_distance(self):
        rl = ReferenceLap(self.data)
        self.assertEqual(rl.get_sample_at_distance(0), 100)
        self.assertEqual(rl.get_sample_at_distance(0.1), 100)
        self.assertEqual(rl.get_sample_at_distance(0.5), 100)
        self.assertEqual(rl.get_sample_at_distance(1.0), 333)
        self.assertEqual(rl.get_sample_at_distance(1.01), 333)
        self.assertEqual(rl.get_sample_at_distance(1.06), 22)
        self.assertEqual(rl.get_sample_at_distance(0.81), 454)
        self.assertEqual(rl.get_sample_at_distance(0.79), 454)
        self.assertEqual(rl.get_sample_at_distance(330), 22)
        self.assertEqual(rl.get_sample_at_distance(1.1), 22)
        self.assertEqual(rl.get_sample_at_distance(None), None)

def main():
    unittest.main()

if __name__ == "__main__":
    main()



