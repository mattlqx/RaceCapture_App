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
import os
import kivy
kivy.require('1.9.1')
from kivy.properties import StringProperty, ObjectProperty
from autosportlabs.racecapture.widgets.heat.wheelcorner import HeatmapCorner, HeatmapCornerLeft, HeatmapCornerRight
from autosportlabs.racecapture.views.dashboard.widgets.gauge import Gauge

class HeatmapCornerGauge(Gauge, HeatmapCorner):
    DEFAULT_TIRE_CHANNEL_PREFIX = 'TireTmp'
    DEFAULT_BRAKE_CHANNEL_PREFIX = 'BrakeTmp'
    corner_prefix = StringProperty('')
    tire_channel_prefix = StringProperty(DEFAULT_TIRE_CHANNEL_PREFIX)
    brake_channel_prefix = StringProperty(DEFAULT_BRAKE_CHANNEL_PREFIX)

    channel_metas = ObjectProperty()

    def on_data_bus(self, instance, value):
        self._update_channel_binding()

    def _update_channel_binding(self):
        data_bus = self.data_bus
        if data_bus is None:
            return

        for zone in range (0, self.tire_zones):
            channel = '{}{}{}'.format(self.tire_channel_prefix, self.corner_prefix, zone + 1)
            data_bus.addChannelListener(channel, lambda value, z=zone: self._set_tire_value(value, z))

        for zone in range (0, self.brake_zones):
            channel = '{}{}{}'.format(self.brake_channel_prefix, self.corner_prefix, zone + 1)
            data_bus.addChannelListener(channel, lambda value, z=zone: self._set_brake_value(value, z))

        data_bus.addMetaListener(self.on_channel_meta)
        meta = data_bus.getMeta()
        if len(data_bus.getMeta()) > 0:
            self.on_channel_meta(meta)

    def _set_tire_value(self, value, index):
        self.set_tire_value(index, value)

    def _set_brake_value(self, value, index):
        self.set_brake_value(index, value)

    def on_channel_meta(self, channel_metas):
        self.channel_metas = channel_metas

    def on_channel_metas(self, instance, value):
        pass

class HeatmapCornerLeftGauge(HeatmapCornerGauge, HeatmapCornerLeft):
    pass

class HeatmapCornerRightGauge(HeatmapCornerGauge, HeatmapCornerRight):
    pass
