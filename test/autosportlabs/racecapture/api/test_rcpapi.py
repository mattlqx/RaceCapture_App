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
from mock import Mock
from autosportlabs.racecapture.api.rcpapi import RcpApi

class TestRcpApi(unittest.TestCase):
    def setUp(self):
        self.settings = Mock()
        self.comms = Mock()

    def test_is_firmware_update_available_no_comms(self):
        rcpapi = RcpApi(settings=self.settings, comms=None)
        self.assertFalse(rcpapi.is_firmware_update_supported())

    def test_is_firmware_update_available_on_wired(self):
        self.comms.is_wireless = Mock(return_value=False)
        rcpapi = RcpApi(settings=self.settings, comms=self.comms)
        self.assertTrue(rcpapi.is_firmware_update_supported())

    def test_is_firmware_update_available_on_wireless(self):
        self.comms.is_wireless = Mock(return_value=True)
        rcpapi = RcpApi(settings=self.settings, comms=self.comms)
        self.assertFalse(rcpapi.is_firmware_update_supported())


def main():
    unittest.main()

if __name__ == "__main__":
    main()
