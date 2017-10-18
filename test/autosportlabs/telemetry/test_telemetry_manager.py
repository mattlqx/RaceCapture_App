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
from mock import patch
import mock
from autosportlabs.telemetry.telemetryconnection import *
import asyncore
import math

@patch.object(asyncore, 'loop')
@patch('autosportlabs.telemetry.telemetryconnection.TelemetryConnection', autospec=True)
@patch('autosportlabs.racecapture.databus.databus.DataBus', autospec=True)
class TelemetryManagerTest(unittest.TestCase):

    def test_no_start(self, mock_data_bus_pump, mock_telemetry_connection, mock_asyncore):
        data_bus = mock_data_bus_pump()
        device_id = "ADER45"
        host = 'foobar.com'
        port = 5555

        data_bus.rcp_meta_read = False

        telemetry_manager = TelemetryManager(data_bus, device_id=device_id, host=host, port=port)
        telemetry_manager.start()
        self.assertFalse(mock_telemetry_connection.called, "Does not connect if no meta")

        telemetry_manager = TelemetryManager(data_bus, host=host, port=port)
        telemetry_manager._on_meta({
            'Foo': 'bar',
            'Bar': 'baz',
            'Fizz': 'buzz'
        })
        telemetry_manager.start()
        self.assertFalse(mock_telemetry_connection.called, "Does not connect if no device id")

    @patch('autosportlabs.telemetry.telemetryconnection.threading.Thread')
    def test_auto_start(self, mock_thread, mock_data_bus_pump, mock_telemetry_connection, mock_asyncore):
        data_bus = mock_data_bus_pump()
        device_id = "ADER45"
        host = 'foobar.com'
        port = 5555

        telemetry_manager = TelemetryManager(data_bus, device_id=device_id, host=host, port=port, telemetry_enabled=True)
        telemetry_manager._on_meta({
            'Foo': 'bar',
            'Bar': 'baz',
            'Fizz': 'buzz'
        })

        telemetry_manager.telemetry_enabled = True
        telemetry_manager.data_connected = True

        args, kwargs = mock_telemetry_connection.call_args
        host_arg, port_arg, device_id_arg, meta_arg, bus_arg, status_arg = args

        self.assertEqual(host_arg, host, "Host is passed to TelemetryConnection")
        self.assertEqual(port_arg, port, "Port is passed to TelemetryConnection")

        self.assertTrue(mock_telemetry_connection.called, "Connects automatically")
        self.assertTrue(telemetry_manager._connection_process.start.called, "Telemetry connection started")

    @patch('autosportlabs.telemetry.telemetryconnection.threading.Timer')
    def test_reconnect(self, mock_timer, mock_data_bus_pump, mock_telemetry_connection, mock_asyncore):
        mock_telemetry_connection.STATUS_DISCONNECTED = 0

        data_bus = mock_data_bus_pump()
        device_id = "ADER45"
        host = 'foobar.com'
        port = 5555

        telemetry_manager = TelemetryManager(data_bus, device_id=device_id, host=host, port=port,
                                             telemetry_enabled=True)
        telemetry_manager.data_connected = True
        telemetry_manager._on_meta({
            'Foo': 'bar',
            'Bar': 'baz',
            'Fizz': 'buzz'
        })

        self.assertTrue(mock_telemetry_connection.called)
        telemetry_manager.status("error", "Disconnected", TelemetryConnection.STATUS_DISCONNECTED)

        args, kwargs = mock_timer.call_args
        timeout, connect = args

        self.assertEqual('_connect', connect.__name__)
        self.assertEqual(TelemetryManager.RETRY_WAIT_START, timeout)
        self.assertTrue(mock_timer.called)

        telemetry_manager.status("error", "Disconnected", TelemetryConnection.STATUS_DISCONNECTED)
        args, kwargs = mock_timer.call_args
        timeout, connect = args

        self.assertEqual(TelemetryManager.RETRY_WAIT_START * TelemetryManager.RETRY_MULTIPLIER, timeout)

        telemetry_manager.status("error", "Disconnected", TelemetryConnection.STATUS_DISCONNECTED)
        args, kwargs = mock_timer.call_args
        timeout, connect = args

        self.assertEqual(TelemetryManager.RETRY_WAIT_START * (math.pow(TelemetryManager.RETRY_MULTIPLIER, 2)), timeout)

        telemetry_manager.status("error", "Disconnected", TelemetryConnection.STATUS_DISCONNECTED)
        args, kwargs = mock_timer.call_args
        timeout, connect = args

        self.assertEqual(TelemetryManager.RETRY_WAIT_START * (math.pow(TelemetryManager.RETRY_MULTIPLIER, 2)), timeout)

