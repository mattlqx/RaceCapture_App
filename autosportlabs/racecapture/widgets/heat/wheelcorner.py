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
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import NumericProperty, StringProperty, ListProperty
from autosportlabs.uix.gauge.bargraphgauge import BarGraphGauge
from autosportlabs.uix.color.colorgradient import HeatColorGradient
from autosportlabs.racecapture.widgets.heat.heatgauge import TireHeatGauge, BrakeHeatGauge
from kivy.app import Builder

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
