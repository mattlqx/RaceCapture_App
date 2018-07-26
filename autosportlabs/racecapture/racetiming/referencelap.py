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

from sortedcontainers import SortedDict

class ReferenceLap(object):

    """Object to represent a reference lap
    """
    def __init__(self, reference_data_list):
        # channel values indexed by distance
        self.lap_data_by_distance = SortedDict()
        self.load_sample_data(reference_data_list)

    def load_sample_data(self, reference_data_list):
        self.lap_data_by_distance.clear()
        ld = self.lap_data_by_distance
        for d in reference_data_list:
            distance = d[0]
            value = d[1]
            ld[distance] = value

    def get_sample_at_distance(self, distance):
        # Find the closest key in the sorted data
        if distance is None:
            return None

        ld = self.lap_data_by_distance
        index = ld.bisect(distance)

        key = None
        key_before = None
        key_after = None
        try:
            key = ld.iloc[index]
        except IndexError:
            pass

        try:
            key_before = ld.iloc[index - 1]
        except IndexError:
            pass

        try:
            key_after = ld.iloc[index + 1]
        except IndexError:
            pass

        if key_before is not None:
            key = key_before if key is None or abs(distance - key_before) < abs(distance - key) else key

        if key_after is not None:
            key = key_after if key is None or abs(distance - key_after) < abs(distance - key) else key

        return None if key is None else ld.get(key)
