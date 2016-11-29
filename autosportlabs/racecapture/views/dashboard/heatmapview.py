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
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.app import Builder
from kivy.clock import Clock
from autosportlabs.racecapture.views.dashboard.widgets.gauge import Gauge
from autosportlabs.racecapture.widgets.heat.heatgauge import TireHeatGauge, BrakeHeatGauge
from autosportlabs.racecapture.views.dashboard.dashboardscreen import DashboardScreen

HEATMAP_VIEW_KV = """
<HeatmapView>:
    BoxLayout:
        orientation: 'horizontal'
        BoxLayout:
            size_hint_x: 0.5
            orientation: 'vertical'
            spacing: dp(10)        
            BoxLayout:
                spacing: dp(10)
                orientation: 'horizontal'
                BoxLayout:
                    padding: (dp(10), dp(10))
                    spacing: dp(10)                
                    TireHeatGauge:
                        id: wheel_fl
                        size_hint: (0.4, 0.6)
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                        direction: 'right-left'
                    BrakeHeatGauge:
                        id: brake_fl
                        size_hint: (0.6, 0.6)
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                BoxLayout:
                    padding: (dp(10), dp(10))
                    spacing: dp(10)
                    BrakeHeatGauge:
                        id: brake_fr
                        size_hint: (0.6, 0.6)
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                    TireHeatGauge:
                        id: wheel_fr
                        size_hint: (0.4, 0.6)
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                        direction: 'left-right'
            BoxLayout:
                spacing: dp(10)        
                orientation: 'horizontal'
                BoxLayout:
                    padding: (dp(10), dp(10))
                    spacing: dp(10)
                    TireHeatGauge:
                        id: wheel_rl
                        size_hint: (0.4, 0.6)
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                        direction: 'right-left'
                    BrakeHeatGauge:
                        id: brake_rl
                        size_hint: (0.6, 0.6)
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                BoxLayout:
                    padding: (dp(10), dp(10))
                    spacing: dp(10)
                    BrakeHeatGauge:
                        id: brake_rr
                        size_hint: (0.6, 0.6)
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                    TireHeatGauge:
                        id: wheel_rr
                        size_hint: (0.4, 0.6)
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                        direction: 'left-right'

        BoxLayout:
            size_hint_x: 0.5


"""

class HeatmapView(DashboardScreen):
    Builder.load_string(HEATMAP_VIEW_KV)

    def __init__(self, databus, settings, **kwargs):
        super(HeatmapView, self).__init__(**kwargs)
        self._initialized = False
        self.register_event_type('on_tracks_updated')
        self._databus = databus
        self._settings = settings
        self.update_values(self.ids.wheel_fl)
        self.update_values(self.ids.wheel_fr)
        self.update_values(self.ids.wheel_rl)
        self.update_values(self.ids.wheel_rr)
        self.update_values(self.ids.brake_fl)
        self.update_values(self.ids.brake_fr)
        self.update_values(self.ids.brake_rl)
        self.update_values(self.ids.brake_rr)
    def update_values(self, widget):
        for x in range(0,8):
            widget.set_value(x, float(x) / 10.0)
        
    def init_view(self):
        data_bus = self._databus
        settings = self._settings
        self._initialized = True

    def on_tracks_updated(self, trackmanager):
        pass

    def on_enter(self):
        if not self._initialized:
            self.init_view()
