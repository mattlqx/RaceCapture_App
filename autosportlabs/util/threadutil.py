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

from threading import RLock
from kivy import platform
__all__ = ('safe_thread_exit')


if platform == 'android':
    import jnius

def safe_thread_exit():
    if platform == 'android':
        jnius.detach()  # detach the current thread from pyjnius, else hard crash occurs


class ThreadSafeDict(dict) :
    def __init__(self, * p_arg, ** n_arg) :
        dict.__init__(self, * p_arg, ** n_arg)
        self._lock = RLock()

    def __enter__(self) :
        self._lock.acquire()
        return self

    def __exit__(self, type, value, traceback) :
        self._lock.release()
