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

import json
import os

class UnitsConversionFilters(object):
    """
    Provides mappings for converting common units of measurment
    """
    filters = None
    filter_labels = None
    default_key = None
    def __init__(self, base_dir, **kwargs):
        super(UnitsConversionFilters, self).__init__(**kwargs)
        self.load_CAN_filters(base_dir)

    def load_CAN_filters(self, base_dir):
        if UnitsConversionFilters.filters is not None:
            return
        try:
            UnitsConversionFilters.filters = {}
            UnitsConversionFilters.filter_labels = {}
            filters_json = open(os.path.join(base_dir, 'resource', 'settings', 'units_conversion_filters.json'))
            can_filters = json.load(filters_json)['filters']
            for k in sorted(can_filters.iterkeys()):
                if UnitsConversionFilters.default_key is None:
                    UnitsConversionFilters.default_key = k
                f = can_filters[k]
                convert_from = f['from']
                convert_to = f['to']
                label = 'No Conversion' if not (convert_from and convert_to) else '{} -> {}'.format(convert_from, convert_to)
                filter_key = int(k)
                UnitsConversionFilters.filters[filter_key] = f
                UnitsConversionFilters.filter_labels[filter_key] = label

        except Exception as detail:
            raise Exception('Error loading units conversion filters: ' + str(detail))

    def get_filter(self, filter_id):
        f = UnitsConversionFilters.filters.get(filter_id)
        return (f['from'], f['to']) if f else (None, None)

    def get_filter_label(self, filter_id):
        return UnitsConversionFilters.filter_labels.get(filter_id)
