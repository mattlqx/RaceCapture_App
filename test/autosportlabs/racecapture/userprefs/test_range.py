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
import os
from autosportlabs.racecapture.settings.prefs import Range


class RangeTest(unittest.TestCase):

    def test_range_constructor(self):
        min = 0
        max = 10
        color = [2, 2, 2, 2]
        range = Range(minimum=min, maximum=max, color=color)

        self.assertEquals(min, range.min, msg="Range did not set min property")
        self.assertEquals(max, range.max, msg="Range did not set max property")
        self.assertEquals(color, range.color, msg="Range did not set color property")

    def test_range_is_in_range(self):
        min = 0
        max = 10
        color = [2, 2, 2, 2]
        range = Range(min, max, color=color)

        self.assertTrue(range.is_in_range(0))
        self.assertTrue(range.is_in_range(10))
        self.assertTrue(range.is_in_range(5))
        self.assertFalse(range.is_in_range(-1))
        self.assertFalse(range.is_in_range(11))

    def test_range_to_json(self):
        expected = '{"color": [2, 2, 2, 2], "max": 10, "min": 0}'
        min = 0
        max = 10
        color = [2, 2, 2, 2]
        range = Range(min, max, color=color)
        range_json = range.to_json()

        self.assertEquals(expected, range_json, "Range to_json output does not match expected output")

    def test_range_from_json(self):
        min = 0
        max = 10
        color = [2, 2, 2, 2]
        original_range = Range(min, max, color=color)
        range_json = original_range.to_json()

        new_range = Range.from_json(range_json)

        self.assertEquals(original_range.max, new_range.max, "New and old range max do not match")
        self.assertEquals(original_range.min, new_range.min, "New and old range min do not match")
        self.assertEquals(original_range.color, new_range.color, "New and old range color does not match")

    def test_range_from_dict(self):
        min = 0
        max = 10
        color = [2, 2, 2, 2]
        original_range = Range(min, max, color=color)
        range_dict = original_range.to_dict()

        new_range = Range.from_dict(range_dict)

        self.assertEquals(original_range.max, new_range.max, "New and old range max do not match")
        self.assertEquals(original_range.min, new_range.min, "New and old range min do not match")
        self.assertEquals(original_range.color, new_range.color, "New and old range color does not match")
