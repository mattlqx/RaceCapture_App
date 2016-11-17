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

from kivy import platform

__all__ = 'comms_factory'


def comms_factory(device, conn_type):
    # Connection type can be overridden by user or for testing purposes
    if conn_type is not None:
        conn_type = conn_type.lower()
        if conn_type == 'bluetooth':
            return android_comm(device)
        if conn_type == 'wifi':
            return socket_comm(device)
        if conn_type == 'serial':
            return serial_comm(device)
    else:
        if platform == 'android':
            return android_comm(device)
        elif platform == 'ios':
            return socket_comm(device)
        else:
            return serial_comm(device)


def socket_comm(device):
    from autosportlabs.comms.socket.socketconnection import SocketConnection
    from autosportlabs.comms.socket.socketcomm import SocketComm
    return SocketComm(SocketConnection(), device)


def serial_comm(device):
    from autosportlabs.comms.serial.serialconnection import SerialConnection
    from autosportlabs.comms.comms import Comms
    return Comms(device, SerialConnection())


def android_comm(device):
    from autosportlabs.comms.androidcomms import AndroidComms
    return AndroidComms(device)
