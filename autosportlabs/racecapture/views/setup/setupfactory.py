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
from autosportlabs.racecapture.views.setup.introview import IntroView

__all__ = 'setup_factory'


def setup_factory(key):
    # Connection type can be overridden by user or for testing purposes
    if key == 'intro':
        return IntroView()
    elif key == 'device':
        return None
    elif key == 'connection':
        return None
    elif key == 'finish':
        return None
