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
from autosportlabs.util.timeutil import *
from datetime import datetime, timedelta

class TimeUtilTest(unittest.TestCase):

    def test_timeutil(self):
        t1 = time_to_epoch('2016-10-10T23:43:44.131298')
        t2 = time_to_epoch('2016-10-10T23:43:44.131298Z')
        t3 = time_to_epoch('2016-10-10T23:43:44')
        t4 = time_to_epoch('2016-10-10T23:43:44Z')

        self.assertTrue(t1 == t2 == t3 == t4)

    def test_friendly_format_time_ago(self):
        n = datetime.now()
        self.assertEqual('Just now', friendly_format_time_ago(n - timedelta(seconds=1))) 
        self.assertEqual('1 min ago', friendly_format_time_ago(n - timedelta(minutes=1)))
        self.assertEqual('2 mins ago', friendly_format_time_ago(n - timedelta(minutes=2)))
        self.assertEqual('1 hour 1 min ago', friendly_format_time_ago(n - timedelta(minutes=61)))
        self.assertEqual('2 hours 2 mins ago', friendly_format_time_ago(n - timedelta(minutes=122)))
        long_ago = n - timedelta(days=30)
        self.assertEqual(format_time(long_ago), friendly_format_time_ago(long_ago))
        
def main():
    unittest.main()

if __name__ == "__main__":
    main()



