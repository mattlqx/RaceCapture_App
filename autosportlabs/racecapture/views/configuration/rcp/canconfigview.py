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

import kivy
kivy.require('1.10.0')
from kivy.metrics import dp
from settingsview import SettingsSwitch
from mappedspinner import MappedSpinner
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.switch import Switch
from kivy.uix.button import Button
from kivy.properties import NumericProperty, ListProperty
from kivy.app import Builder
from utils import *
from settingsview import SettingsView
from autosportlabs.racecapture.views.configuration.baseconfigview import BaseConfigView
from fieldlabel import FieldLabel

class CANBaudRateSpinner(MappedSpinner):
    channel_id = NumericProperty(0)

    def __init__(self, **kwargs):
        super(CANBaudRateSpinner, self).__init__(**kwargs)
        self.setValueMap({50000: '50K Baud', 100000: '100K Baud', 125000: '125K Baud', 250000:'250K Baud', 500000:'500K Baud', 1000000:'1M Baud'}, '500000')

class CANTerminationSwitch(Switch):
    channel_id = NumericProperty(0)

CAN_CONFIG_VIEW_KV = """
<CANConfigView>:
    spacing: dp(20)
    orientation: 'vertical'
    #row_default_height: dp(40)
    id: cansettings
    HSeparator:
        text: 'CAN bus Configuration'
        halign: 'left'
        size_hint_y: 0.10
        
    SettingsView:
        id: can_enabled
        label_text: 'CAN bus'
        help_text: 'CAN interface for OBDII and custom CAN channels'
        size_hint_y: 0.27
        
    HLineSeparator:
        size_hint_y: 0.01
        
    GridLayout:
        size_hint_y: 0.05
        cols: 3
        FieldLabel:
            halign: 'center'
            text: 'Channel'
        FieldLabel:
            halign: 'center'
            text: 'Baud Rate'
        FieldLabel:
            halign: 'center'
            id: can_term_header
            text: 'Termination'
            
        
    ScrollContainer:
        size_hint_y: 0.57
        do_scroll_x: False
        do_scroll_y: True
        size_hint_y: 1
        size_hint_x: 1
        GridLayout:
            cols: 3
            id: can_settings
            row_force_default: True
            padding: [0, dp(20)]
            spacing: [0, dp(10)]
            row_default_height: dp(50)
            size_hint_y: None
            height: self.minimum_height
            
"""
class CANConfigView(BaseConfigView):
    Builder.load_string(CAN_CONFIG_VIEW_KV)

    def __init__(self, **kwargs):
        super(CANConfigView, self).__init__(**kwargs)
        self.can_config = None
        self.view_loaded = False

        self.register_event_type('on_config_updated')
        btEnable = self.ids.can_enabled
        btEnable.bind(on_setting=self.on_can_enabled)
        btEnable.setControl(SettingsSwitch())

    def on_can_enabled(self, instance, value):
        if self.view_loaded:
            self.can_config.enabled = value
            self.can_config.stale = True
            self.dispatch('on_modified')

    def on_can_baud(self, instance, value):
        if self.view_loaded:
            channel_id = instance.channel_id
            self.can_config.baudRate[channel_id] = instance.getValueFromKey(value)
            self.can_config.stale = True
            self.dispatch('on_modified')

    def on_can_termination(self, instance, value):
        if self.view_loaded:
            channel_id = instance.channel_id
            self.can_config.termination_enabled[channel_id] = 1 if value == True else 0
            self.can_config.stale = True
            self.dispatch('on_modified')


    def on_config_updated(self, cfg):
        try:
            self.view_loaded = False
            can_config = cfg.canConfig
            self.ids.can_enabled.setValue(can_config.enabled)
            self._update_can_settings(cfg)
            self.can_config = can_config
            self.ids.can_term_header.text = 'Termination' if cfg.capabilities.has_can_term else ''
        finally:
            self.view_loaded = True

    def _update_can_settings(self, cfg):
        self.can_config = cfg.canConfig
        capabilities = cfg.capabilities
        can_settings = self.ids.can_settings
        can_settings.clear_widgets()
        can_channel_count = capabilities.channels.can

        for i in range(0, can_channel_count):
            can_settings.add_widget(FieldLabel(text=str(i + 1), halign='center'))

            baud_rate = CANBaudRateSpinner()
            baud_rate.channel_id = i
            baud_rate.bind(text=self.on_can_baud)
            baud_rate.setFromValue(self.can_config.baudRate[i])
            can_settings.add_widget(baud_rate)

            if capabilities.has_can_term:
                termination = CANTerminationSwitch()
                termination.channel_id = i
                termination.active = self.can_config.termination_enabled[i]
                termination.bind(active=self.on_can_termination)
                can_settings.add_widget(termination)
            else:
                can_settings.add_widget(BoxLayout())


