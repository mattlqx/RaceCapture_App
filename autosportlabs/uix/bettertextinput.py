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

import kivy
kivy.require('1.9.1')
from valuefield import ValueField
import re


class BetterTextInput(ValueField):
    """
    A better text input for forms. Allows for limiting # of characters and using a regex to also limit characters
    entered.
    """

    def __init__(self, max_chars=200000, regex=None, **kwargs):
        super(BetterTextInput, self).__init__(**kwargs)
        self.max_chars = max_chars
        self.regex = regex

    def insert_text(self, substring, from_undo=False):
        if not from_undo and (len(self.text) + len(substring) > self.max_chars):
            return

        if self.regex:
            pattern = re.compile(self.regex)
            substring = re.sub(pattern, '', substring)

        super(BetterTextInput, self).insert_text(substring, from_undo=from_undo)
