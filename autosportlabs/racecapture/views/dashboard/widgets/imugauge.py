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
from kivy.uix.behaviors import ButtonBehavior
from kivy.app import Builder
from kivy.metrics import dp
from fieldlabel import FieldLabel
from utils import kvFind, kvquery
from kivy.properties import NumericProperty, ObjectProperty
from autosportlabs.uix.imu.imuview import ImuView
from autosportlabs.racecapture.views.dashboard.widgets.gauge import Gauge
from autosportlabs.uix.color.colorsequence import ColorSequence
from kivy.uix.settings import SettingsWithNoMenu


class ImuLabel(FieldLabel):
    Builder.load_string("""
<ImuLabel>:
    font_size: min(dp(20), max(1,self.height * 1.0))
    """)

IMU_GAUGE_KV = """
<ImuGauge>:
    AnchorLayout:
        ImuView:
            id: imu

    AnchorLayout:
        anchor_x: 'left'
        anchor_y: 'center'
        GridLayout:
            size_hint: (0.3, 0.5)
            spacing: (dp(10), dp(10))
            cols: 2
            ImuLabel:
                text: 'X'
                halign: 'right'
                size_hint_x: 0.3
            BarGraphGauge:
                id: accel_x
                size_hint_x: 0.7
            ImuLabel:
                text: 'Y'
                halign: 'right'
                size_hint_x: 0.3
            BarGraphGauge:
                id: accel_y
                size_hint_x: 0.7
            ImuLabel:
                text: 'Z'
                halign: 'right'
                size_hint_x: 0.3
            BarGraphGauge:
                id: accel_z
                size_hint_x: 0.7
    AnchorLayout:
        anchor_x: 'right'
        anchor_y: 'center'
        GridLayout:
            size_hint: (0.3, 0.5)
            spacing: (dp(10), dp(10))
            cols: 2
            BarGraphGauge:
                id: gyro_yaw
                orientation: 'right-left'
                size_hint_x: 0.5
            ImuLabel:
                text: 'Yaw'
                halign: 'left'
                size_hint_x: 0.5
            BarGraphGauge:
                id: gyro_pitch
                orientation: 'right-left'                
                size_hint_x: 0.5
            ImuLabel:
                text: 'Pitch'
                halign: 'left'
                size_hint_x: 0.5
            BarGraphGauge:
                id: gyro_roll
                orientation: 'right-left'                
                size_hint_x: 0.5
            ImuLabel:
                text: 'Roll'
                halign: 'left'
                size_hint_x: 0.5
"""

class ImuGauge(Gauge):
    Builder.load_string(IMU_GAUGE_KV)

    GYRO_SCALING = 0.5
    ACCEL_SCALING = 1.0
    ACCEL_X = "AccelX"
    ACCEL_Y = "AccelY"
    ACCEL_Z = "AccelZ"
    GYRO_YAW = "Yaw"
    GYRO_PITCH = "Pitch"
    GYRO_ROLL = "Roll"

    IMU_AMPLIFICATION = 2.0

    channel_metas = ObjectProperty(None)
    zoom = NumericProperty(1)

    def __init__(self, **kwargs):
        super(ImuGauge, self).__init__(**kwargs)
        self._color_sequence = ColorSequence()

    def on_zoom(self, instance, value):
        self.ids.imu.position_z /= value

    def on_channel_meta(self, channel_metas):
        self.channel_metas = channel_metas

    def on_data_bus(self, instance, value):
        self._update_channel_binding()

    def update_colors(self):
        view = self.valueView
        if view:
            view.color = self.normal_color

    def refresh_value(self, value):
        view = self.valueView
        if view:
            view.text = self.value_formatter(value)
            self.update_colors()

    def on_value(self, instance, value):
        self.refresh_value(value)

    def sensor_formatter(self, value):
        return "" if value is None else self.sensor_format.format(value)

    def on_channel(self, instance, value):
        self._update_gauge_meta()

    def _update_channel_binding(self):
        data_bus = self.data_bus
        if data_bus:
            data_bus.addChannelListener(self.ACCEL_X, self.set_accel_x)
            data_bus.addChannelListener(self.ACCEL_Y, self.set_accel_y)
            data_bus.addChannelListener(self.ACCEL_Z, self.set_accel_z)
            data_bus.addChannelListener(self.GYRO_YAW, self.set_gyro_yaw)
            data_bus.addChannelListener(self.GYRO_PITCH, self.set_gyro_pitch)
            data_bus.addChannelListener(self.GYRO_ROLL, self.set_gyro_roll)
            data_bus.addMetaListener(self.on_channel_meta)
            meta = data_bus.getMeta()
            if len(data_bus.getMeta()) > 0:
                self.on_channel_meta(meta)

    def set_accel_x(self, value):
        self.ids.imu.accel_x = value * ImuGauge.ACCEL_SCALING
        self.ids.accel_x.value = value

    def set_accel_y(self, value):
        self.ids.imu.accel_y = value * ImuGauge.ACCEL_SCALING
        self.ids.accel_y.value = value

    def set_accel_z(self, value):
        self.ids.imu.accel_z = value * ImuGauge.ACCEL_SCALING
        self.ids.accel_z.value = value

    def set_gyro_yaw(self, value):
        self.ids.imu.gyro_yaw = value * ImuGauge.GYRO_SCALING
        self.ids.gyro_yaw.value = value

    def set_gyro_pitch(self, value):
        self.ids.imu.gyro_pitch = value * ImuGauge.GYRO_SCALING
        self.ids.gyro_pitch.value = value

    def set_gyro_roll(self, value):
        self.ids.imu.gyro_roll = value * ImuGauge.GYRO_SCALING
        self.ids.gyro_roll.value = value

    def on_hide(self):
        self.ids.imu.cleanup_view()

    def on_show(self):
        self.ids.imu.init_view()

    def _update_imu_meta(self, channel_meta, gauge):
        if channel_meta is None:
            return
        gauge.minval = channel_meta.min / ImuGauge.IMU_AMPLIFICATION
        gauge.maxval = channel_meta.max / ImuGauge.IMU_AMPLIFICATION
        gauge.color = self._color_sequence.get_color(channel_meta.name)

    def on_channel_metas(self, instance, value):
        self._update_imu_meta(value.get('AccelX'), self.ids.accel_x)
        self._update_imu_meta(value.get('AccelY'), self.ids.accel_y)
        self._update_imu_meta(value.get('AccelZ'), self.ids.accel_z)
        self._update_imu_meta(value.get('Yaw'), self.ids.gyro_yaw)
        self._update_imu_meta(value.get('Pitch'), self.ids.gyro_pitch)
        self._update_imu_meta(value.get('Roll'), self.ids.gyro_roll)
