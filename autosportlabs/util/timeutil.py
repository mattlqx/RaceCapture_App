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

__all__ = ('time_to_epoch', 'format_time')
import calendar
from datetime import datetime
from kivy import platform

def time_to_epoch(timestamp):
    """
    convert a timestamp to a Unix epoch
    :param timestamp in "YYYY-MM-DDTHH:MM:SSS" format
    :type string
    :return returns the epoch time as int
    """
    return int(calendar.timegm(datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").timetuple()))

def format_time(dt=datetime.now()):
    """
    format the supplied datetime to the current locale
    :param the time to format. If not speified, defaults to now
    :type datetime
    :return returns the formatted string
    """
    format = '%x %X' if platform == 'win' else '%Ex %EX'
    return dt.strftime(format)



