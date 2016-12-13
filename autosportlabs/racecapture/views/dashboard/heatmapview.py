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
from Cython.Shadow import numeric
kivy.require('1.9.1')
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.app import Builder
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import NumericProperty, ListProperty, StringProperty, ObjectProperty
from autosportlabs.racecapture.views.dashboard.widgets.gauge import Gauge
from autosportlabs.racecapture.widgets.heat.heatgauge import TireHeatGauge, BrakeHeatGauge
from autosportlabs.racecapture.views.dashboard.dashboardscreen import DashboardScreen
from autosportlabs.uix.gauge.bargraphgauge import BarGraphGauge
from autosportlabs.uix.color.colorgradient import HeatColorGradient
from autosportlabs.racecapture.views.dashboard.widgets.imugauge import ImuGauge
from utils import kvFindClass

class TireCorner(BoxLayout):
    DEFAULT_TIRE_ZONES = 1
    DEFAULT_TIRE_MIN = 0
    DEFAULT_TIRE_MAX = 300
    zones = NumericProperty()
    minval = NumericProperty()
    maxval = NumericProperty()

    def __init__(self, **kwargs):
        super(TireCorner, self).__init__(**kwargs)
        self.tire_value_widgets = []
        self.heat_gradient = HeatColorGradient()

    def _init_view(self):
        self.tire_zones = TireCorner.DEFAULT_TIRE_ZONES
        self.minval = TireCorner.DEFAULT_TIRE_MIN
        self.maxval = TireCorner.DEFAULT_TIRE_MAX

    def on_minval(self, instance, value):
        for gauge in self.tire_value_widgets:
            gauge.minval = value

    def on_maxval(self, instance, value):
        for gauge in self.tire_value_widgets:
            gauge.maxval = value

    def on_zones(self, instance, value):
        self.ids.tire.zones = value
        self.ids.tire_values.clear_widgets()
        del(self.tire_value_widgets[:])
        for i in range(0, value):
            tire_values = self.ids.tire_values
            is_first_widget = self.children.index(tire_values) == 1
            orientation = 'right-left' if is_first_widget else 'left-right'
            gauge = BarGraphGauge(orientation=orientation)
            tire_values.add_widget(gauge)
            self.tire_value_widgets.append(gauge)
            gauge.minval = self.minval
            gauge.maxval = self.maxval

    def set_value(self, zone, value):
        value = min(self.maxval, value)
        value = max(self.minval, value)
        scaled = value / self.maxval
        self.ids.tire.set_value(zone, scaled)
        try:
            value_widget = self.tire_value_widgets[zone]
            value_widget.value = value
            value_widget.color = self.heat_gradient.get_color_value(scaled)
        except IndexError:
            pass

TIRE_CORNER_LEFT_KV = """
<TireCornerLeft>:
    spacing: dp(10)
    GridLayout:
        id: tire_values
        size_hint: (0.4, 0.5)
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}                        
        cols: 1                                    
    TireHeatGauge:
        id: tire
        size_hint: (0.6, 0.6)
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        direction: 'right-left'
"""
class TireCornerLeft(TireCorner):
    Builder.load_string(TIRE_CORNER_LEFT_KV)

TIRE_CORNER_RIGHT_KV = """
<TireCornerRight>:
    spacing: dp(10)
    TireHeatGauge:
        id: tire
        size_hint: (0.6, 0.6)
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        direction: 'left-right'
    GridLayout:
        id: tire_values
        size_hint: (0.4, 0.5)
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        cols: 1                        
"""
class TireCornerRight(TireCorner):
    Builder.load_string(TIRE_CORNER_RIGHT_KV)

class BrakeCorner(BoxLayout):
    DEFAULT_BRAKE_ZONES = 1
    DEFAULT_BRAKE_MIN = 0
    DEFAULT_BRAKE_MAX = 1000
    zones = NumericProperty()
    minval = NumericProperty()
    maxval = NumericProperty()
    bar_gauge_orientation = StringProperty()

    def __init__(self, **kwargs):
        super(BrakeCorner, self).__init__(**kwargs)
        self.brake_value_widgets = []
        self.heat_gradient = HeatColorGradient()


    def on_zones(self, instance, value):
        self.ids.brake.zones = value
        self.ids.brake_values_top.clear_widgets()
        self.ids.brake_values_bottom.clear_widgets()
        current_grid = self.ids.brake_values_top
        del(self.brake_value_widgets[:])
        for i in range(0, value):
            if i > 1:
                current_grid = self.ids.brake_values_bottom  # 2 values above, 2 below
            gauge = BarGraphGauge(orientation=self.bar_gauge_orientation)
            gauge.minval = self.minval
            gauge.maxval = self.maxval
            current_grid.add_widget(gauge)
            self.brake_value_widgets.append(gauge)

    def set_value(self, zone, value):
        value = min(self.maxval, value)
        value = max(self.minval, value)
        scaled = value / self.maxval
        self.ids.brake.set_value(zone, scaled)
        try:
            value_widget = self.brake_value_widgets[zone]
            value_widget.value = value
            value_widget.color = self.heat_gradient.get_color_value(scaled)
        except IndexError:
            pass

    def on_minval(self, instance, value):
        for gauge in self.brake_value_widgets:
            gauge.minval = value

    def on_maxval(self, instance, value):
        for gauge in self.brake_value_widgets:
            gauge.maxval = value


BRAKE_CORNER_LEFT_KV = """
<BrakeCornerLeft>:
    orientation: 'vertical'
    bar_gauge_orientation: 'right-left'
    GridLayout:
        id: brake_values_top
        size_hint: (0.5, 0.2)
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}                        
        cols: 1                                        
    BrakeHeatGauge:
        id: brake
        size_hint: (1.0, 0.6)
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
    GridLayout:
        id: brake_values_bottom
        size_hint: (0.5, 0.2)
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}                        
        cols: 1                                    
"""
class BrakeCornerLeft(BrakeCorner):
    Builder.load_string(BRAKE_CORNER_LEFT_KV)

BRAKE_CORNER_RIGHT_KV = """
<BrakeCornerRight>:
    orientation: 'vertical'
    bar_gauge_orientation: 'left-right'
    GridLayout:
        id: brake_values_top
        size_hint: (0.5, 0.2)
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}                        
        cols: 1                                        
    BrakeHeatGauge:
        id: brake
        size_hint: (1.0, 0.6)
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
    GridLayout:
        id: brake_values_bottom
        size_hint: (0.5, 0.2)
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}                        
        cols: 1                                    
        
"""
class BrakeCornerRight(BrakeCorner):
    Builder.load_string(BRAKE_CORNER_RIGHT_KV)

class HeatmapCorner(AnchorLayout):
    brake_zones = NumericProperty()
    tire_zones = NumericProperty()
    brake_range = ListProperty()
    tire_range = ListProperty()

    def __init__(self, **kwargs):
        super(HeatmapCorner, self).__init__(**kwargs)

    def on_brake_zones(self, instance, value):
        self.ids.brake.zones = value

    def on_tire_zones(self, instance, value):
        self.ids.tire.zones = value

    def on_tire_range(self, instance, value):
        self.ids.tire.minval = value[0]
        self.ids.tire.maxval = value[1]

    def on_brake_range(self, instance, value):
        self.ids.brake.minval = value[0]
        self.ids.brake.maxval = value[1]

    def set_brake_value(self, zone, value):
        self.ids.brake.set_value(zone, value)

    def set_tire_value(self, zone, value):
        self.ids.tire.set_value(zone, value)

HEATMAP_CORNER_LEFT_KV = """
<HeatmapCornerLeft>:
    BoxLayout:
        padding: (dp(10), dp(10))
        spacing: dp(10)
        TireCornerLeft:
            id: tire
            size_hint_x: 0.55
        BrakeCornerLeft:
            id: brake
            size_hint_x: 0.45
"""

class HeatmapCornerLeft(HeatmapCorner):
    Builder.load_string(HEATMAP_CORNER_LEFT_KV)

HEATMAP_CORNER_RIGHT_KV = """
<HeatmapCornerRight>:
    BoxLayout:
        padding: (dp(10), dp(10))
        spacing: dp(10)
        BrakeCornerRight:
            id: brake
            size_hint_x: 0.45
        TireCornerRight:
            id: tire
            size_hint_x: 0.55
"""
class HeatmapCornerRight(HeatmapCorner):
    Builder.load_string(HEATMAP_CORNER_RIGHT_KV)

class HeatmapCornerGauge(Gauge, HeatmapCorner):
    corner_prefix = StringProperty('')
    tire_channel_prefix = StringProperty("TireTmp")
    brake_channel_prefix = StringProperty("BrakeTmp")

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



HEATMAP_VIEW_KV = """
<HeatmapView>:
    BoxLayout:
        orientation: 'horizontal'
        BoxLayout:
            size_hint_x: 0.6
            orientation: 'vertical'
            spacing: dp(10)        
            BoxLayout:
                spacing: dp(10)
                orientation: 'horizontal'
                HeatmapCornerLeftGauge:
                    id: corner_fl
                    corner_prefix: 'FL'
                HeatmapCornerRightGauge:
                    id: corner_fr
                    corner_prefix: 'FR'
            BoxLayout:
                spacing: dp(10)        
                orientation: 'horizontal'
                HeatmapCornerLeftGauge:
                    id: corner_rl
                    corner_prefix: 'RL'
                HeatmapCornerRightGauge:
                    id: corner_rr
                    corner_prefix: 'RR'
        AnchorLayout:
            size_hint_x: 0.4
            BoxLayout:
                orientation: 'vertical'
                                
                AnchorLayout:
                    size_hint_y: 0.6
                    FieldLabel:
                        id: track_name
                        size_hint_y: 0.1
                        halign: 'center'
                        text: 'Waiting for track'
                    AnchorLayout:
                        anchor_y: 'top'
                        padding: (dp(10), dp(10))
                        RaceTrackView:
                            id: track
                            size_hint: (1.0, 1.0)
                ImuGauge:
                    id: imu
                    size_hint_y: 0.4
                    zoom: 0.5

"""

class HeatmapView(DashboardScreen):
    Builder.load_string(HEATMAP_VIEW_KV)

    def __init__(self, databus, settings, track_manager, status_pump, **kwargs):
        super(HeatmapView, self).__init__(**kwargs)
        self._initialized = False
        self.register_event_type('on_tracks_updated')
        self._databus = databus
        self._settings = settings
        self._track_manager = track_manager
        status_pump.add_listener(self._update_track_status)
        self._current_track_id = None

    def init_view(self):
        data_bus = self._databus
        settings = self._settings

        gauges = list(kvFindClass(self, Gauge))

        for gauge in gauges:
            gauge.settings = settings
            gauge.data_bus = data_bus
        self._initialized = True

    def on_tracks_updated(self, trackmanager):
        pass

    def on_enter(self):
        if not self._initialized:
            self.init_view()
        super(HeatmapView, self).on_enter()

    def _update_track_status(self, status_data):
        try:
            track_status = status_data['status']['track']
            track_id = track_status['trackId']
            if track_id == 0:
                self._set_state_message('Waiting for track')
            elif self._current_track_id != track_id:
                track = self._track_manager.find_track_by_short_id(track_status['trackId'])
                self.ids.track.initMap(track)
                self._current_track_id = track_id
                self._set_state_message('')
        except Exception as e:
            Logger.warn("HeatmapView: Could not retrieve track detection status " + str(e))

    def _set_state_message(self, msg):
        self.ids.track_name.text = msg

