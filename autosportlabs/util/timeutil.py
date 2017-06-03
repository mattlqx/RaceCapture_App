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

__all__ = ('time_to_epoch', 'format_time', 'format_date', 'epoch_to_time')
import calendar
from datetime import datetime
from kivy import platform

# DO NOT REMOVE
# dummy call to ensure strptime is loaded
# before any threads attempt to call it
# see python issue http://bugs.python.org/issue7980
datetime.strptime('2010-01-01', '%Y-%m-%d')
# DO NOT REMOVE


def time_to_epoch(timestamp):
    """
    convert a timestamp to a Unix epoch. Timestamp formats supported
    "YYYY-MM-DDTHH:MM:SSSZ"
    "YYYY-MM-DDTHH:MM:SSS.SSSZ"
    "YYYY-MM-DDTHH:MM:SSS"
    "YYYY-MM-DDTHH:MM:SSS.SSS"
    :param timestamp  
    :type string
    :return returns the epoch time as int
    """
    if len(timestamp) and timestamp[-1] == 'Z':
        timestamp = timestamp[:-1]
    try:
        t = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        t = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")

    return int(calendar.timegm(t.timetuple()))

def format_time(dt=datetime.now()):
    """
    format the supplied datetime to the current locale
    :param the time to format. If not speified, defaults to now
    :type datetime
    :return returns the formatted date and time string
    """
    format = '%x %X' if platform == 'win' else '%Ex %EX'
    return dt.strftime(format)

def format_date(dt=datetime.now()):
    """
    format the supplied datetime to the current locale
    :param the time to format. If not speified, defaults to now
    :type datetime
    :return returns the formatted date and time string
    """
    format = '%x' if platform == 'win' else '%Ex'
    return dt.strftime(format)
    
def epoch_to_time(epoch):
    """
    convert an epoch time to formatting time string
    :param epoch the epoch time
    :type epoch int
    :return returns the formatted string
    """    
    dt = datetime.utcfromtimestamp(float(epoch))
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")



