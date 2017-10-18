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

class ChainableException(Exception):
    def __init__(self, cause=None):
        m = ''

        if cause is not None:
            m += 'caused by {}'.format(repr(cause))
            m.strip()

        super(Exception, self).__init__(m)
        self.cause = cause

    def get_cause(self):
        return self.cause


class PortNotOpenException(ChainableException):
    pass

class CommsErrorException(ChainableException):
    pass
