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

from kivy.logger import Logger
import socket
import json
import errno

READ_TIMEOUT = 2
SCAN_TIMEOUT = 3

class InvalidAddressException(Exception):

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class SocketConnection(object):
    MSG_RECEIVE_BUFFER_SIZE = 32
    BEACON_RECEIVE_BUFFER_SIZE = 4096
    PORT = 7223
    def __init__(self):
        self.socket = None
        self._data = ''

    def get_available_devices(self):
        """
        Listens for RC WiFi's UDP beacon, if found it returns the ips that the RC wifi beacon says it's available on
        :return: List of ip addresses
        """
        Logger.info("SocketConnection: listening for RC wifi...")
        # Listen for UDP beacon from RC wifi
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(SCAN_TIMEOUT)

        # Bind the socket to the port
        server_address = ('', SocketConnection.PORT)
        sock.bind(server_address)

        try:
            data, address = sock.recvfrom(SocketConnection.BEACON_RECEIVE_BUFFER_SIZE)

            if data:
                Logger.info("SocketConnection: got UDP data {}".format(data))
                message = json.loads(data)
                if message['beacon'] and message['beacon']['ip']:
                    sock.close()
                    return message['beacon']['ip']
        except socket.timeout:
            sock.close()
            Logger.info("SocketConnection: found no RC wifi (timeout listening for UDP beacon)")
            return []

    def isOpen(self):
        """
        Returns True or False if socket is open or not
        :return: Boolean
        """
        return self.socket is not None

    def open(self, address):
        """
        Opens a socket connection to the specified address
        :param address: IP address to connect to
        :return: None
        """
        # Check if we've been given a valid IP

        try:
            socket.inet_aton(address)
        except socket.error:
            raise InvalidAddressException("{} is not a valid IP address".format(address))

        # Connect to ip address here
        rc_address = (address, SocketConnection.PORT)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(READ_TIMEOUT)
        self.socket.connect(rc_address)

    def close(self):
        """
        Closes the socket connection
        :return: None
        """
        if self.socket is not None:
            self.socket.close()
        self.socket = None
        self._data = ''

    def read_line(self, keep_reading):
        """
        Reads data from the socket. Will continue to read until either "\r\n" is found in the data read from the
        socket or keep_reading.is_set() returns false
        :param keep_reading: Event object that is checked while data is read
        :type keep_reading: threading.Event
        :return: String or None
        """

        timeout_count = 0
        max_timeouts = 3

        while keep_reading.is_set():
            try:
                data = self.socket.recv(SocketConnection.MSG_RECEIVE_BUFFER_SIZE)

                if data == '':
                    return None

                self._data += data

                if '\r\n' in self._data:
                    lines = self._data.split('\r\n', 1)
                    msg = lines[0]
                    self._data = lines[1]

                    Logger.debug("SocketConnection: returning data {}".format(msg))
                    return msg

            except socket.timeout:
                Logger.error("SocketConnection: timeout")
                timeout_count += 1

                if timeout_count > max_timeouts:
                    Logger.error("SocketConnection: max timeouts when reading, closing")
                    self.close()
                    raise
                else:
                    pass
            except socket.error, e:
                if e.errno == errno.ECONNRESET:
                    Logger.error("SocketConnection: connection reset: {}".format(e))
                    self.close()
                    raise
                Logger.error("SocketConnection: error: {}".format(e))

    def write(self, data):
        """
        Writes data to the socket
        :param data: Data to write
        :type data: String
        :return: None
        """
        self.socket.sendall(data)

    def flushInput(self):
        pass

    def flushOutput(self):
        pass
