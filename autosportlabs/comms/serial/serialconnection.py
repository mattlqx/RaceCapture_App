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

import serial
from serial import SerialException
from serial.tools import list_ports
from autosportlabs.comms.commscommon import PortNotOpenException, CommsErrorException
from kivy.logger import Logger


class SerialConnection():
    DEFAULT_WRITE_TIMEOUT = 3
    DEFAULT_READ_TIMEOUT = 1
    timeout = DEFAULT_READ_TIMEOUT
    writeTimeout = DEFAULT_WRITE_TIMEOUT

    ser = None

    def __init__(self, **kwargs):
        pass

    def get_available_devices(self):
        Logger.debug("SerialConnection: getting available devices")
        devices = [x[0] for x in list_ports.comports()]
        devices.sort()
        filtered_devices = filter(lambda device: not device.startswith('/dev/ttyUSB') 
                                  and not device.startswith('/dev/ttyS') 
                                  and not device.startswith('/dev/cu.Bluetooth-Incoming-Port')
                                  and not device.startswith('/dev/ttyAMA0'), devices)
        return filtered_devices

    def isOpen(self):
        return self.ser != None

    def open(self, device):
        self.ser = serial.Serial(device, timeout=self.timeout, write_timeout=self.writeTimeout)

    def close(self):
        if self.ser != None:
            self.ser.close()
        self.ser = None

    def read(self, count):
        ser = self.ser
        if ser == None: raise PortNotOpenException()
        try:
            return ser.read(count)
        except SerialException as e:
            if str(e).startswith('device reports readiness'):
                return ''
            else:
                raise

    def read_line(self):
        msg = ''
        while True:
            c = self.read(1)
            if c == '':
                return None
            msg += c
            if msg[-2:] == '\r\n':
                msg = msg[:-2]
                return msg

    def write(self, data):
        try:
            return self.ser.write(data)
        except SerialException as e:
            raise CommsErrorException(cause=e)

    def flushInput(self):
        try:
            self.ser.flushInput()
        except SerialException as e:
            raise CommsErrorException(cause=e)

    def flushOutput(self):
        try:
            self.ser.flushOutput()
        except SerialException as e:
            raise CommsErrorException(cause=e)
