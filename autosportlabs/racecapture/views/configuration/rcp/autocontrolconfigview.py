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
from kivy.metrics import dp
from settingsview import SettingsSwitch, SettingsMappedSpinner
from mappedspinner import MappedSpinner
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.switch import Switch
from kivy.uix.button import Button
from kivy.properties import NumericProperty, ListProperty
from kivy.app import Builder
from utils import *
from settingsview import SettingsView
from autosportlabs.racecapture.views.configuration.baseconfigview import BaseConfigView
from autosportlabs.widgets.separator import HSeparator, HSeparatorMinor, HLineSeparator
from autosportlabs.racecapture.views.configuration.channels.channelsview import ChannelNameField
from fieldlabel import FieldLabel
from valuefield import FloatValueField

class CameraMakeModelSpinner(SettingsMappedSpinner):
    channel_id = NumericProperty(0)

    def __init__(self, **kwargs):
        super(CameraMakeModelSpinner, self).__init__(**kwargs)
        self.setValueMap({0: 'GoPro Hero 2/3', 1: 'GoPro Hero 4/5'}, 'GoPro Hero 2/3')

class LtGtSpinner(MappedSpinner):
    channel_id = NumericProperty(0)

    def __init__(self, **kwargs):
        super(LtGtSpinner, self).__init__(**kwargs)
        self.setValueMap({False: 'Less Than', True: 'Greater Than'}, 'Less Than')

AUTOLOGGING_VIEW_KV = """
<AutologgingView>:
    spacing: dp(15)
    HLineSeparator:
        size_hint_y: 0.01    
    SettingsView:
        id: enabled
        label_text: 'SD Logging'
        help_text: 'Enable SD logging control'
        size_hint_y: 0.15
"""

class AutologgingView(BaseConfigView):
    Builder.load_string(AUTOLOGGING_VIEW_KV)

    def __init__(self, **kwargs):
        super(AutologgingView, self).__init__(**kwargs)
        self.register_event_type('on_config_updated')
        settings = self.ids.enabled
        settings.bind(on_setting=self.on_enabled)
        settings.setControl(SettingsSwitch())

    def on_enabled(self, instance, value):
        print('enabled')

    def on_config_updated(self, cfg):
        pass


CAMERACONTROL_VIEW_KV = """
<CameraControlView>:
    spacing: dp(15)
    HLineSeparator:
        size_hint_y: 0.01
    SettingsView:
        id: enabled
        label_text: 'Camera Control'
        help_text: 'Enable Camera Control (Experimental)'
            
    SettingsView:
        id: makemodel
        label_text: 'Camera Type'
        help_text: 'Ensure WiFi is connected to the camera\\'s access point'
"""

class CameraControlView(BaseConfigView):
    Builder.load_string(CAMERACONTROL_VIEW_KV)

    def __init__(self, **kwargs):
        super(CameraControlView, self).__init__(**kwargs)
        settings = self.ids.enabled
        settings.bind(on_setting=self.on_enabled)
        settings.setControl(SettingsSwitch())

        camera_type = self.ids.makemodel
        camera_type.bind(on_setting=self.on_makemodel)
        camera_type.setControl(CameraMakeModelSpinner())

    def on_enabled(self, instance, value):
        print('enabled {}'.format(value))

    def on_makemodel(self, instance, value):
        print('on makemodel {}'.format(value))

AUTOCONTROL_CONFIG_VIEW_KV = """
<AutoControlConfigView>:
    spacing: dp(10)
    padding: (dp(10), dp(10))
    orientation: 'vertical'

    HSeparator:
        text: 'Automatic Control'
        halign: 'left'
        size_hint_y: 0.10
        
    BoxLayout:
        orientation: 'horizontal'
        spacing: dp(10)
        size_hint_y: None
        height: dp(30)
        FieldLabel:
            text: 'Channel'
            halign: 'right'
        BoxLayout:
            size_hint_x: None
            width: dp(100)
        ChannelNameField:
            id: channel
            size_hint_x: None
            width: dp(200)
            
    BoxLayout:
        spacing: dp(10)
        size_hint_y: None
        height: dp(30)
        FieldLabel:
            text: 'Start Trigger'
            halign: 'right'
        LtGtSpinner:
            id: ltgt_start
            size_hint_x: None
            width: dp(100)
        FloatValueField:
            size_hint_x: None
            width: dp(200)
            id: threshold_start
        
    BoxLayout:
        spacing: dp(10)
        size_hint_y: None
        height: dp(30)
        FieldLabel:
            text: 'Stop Trigger'
            halign: 'right'
        LtGtSpinner:
            id: ltgt_stop
            size_hint_x: None
            width: dp(100)
        FloatValueField:
            id: threshold_stop
            size_hint_x: None
            width: dp(200)
        
    ScrollContainer:
        do_scroll_x: False
        do_scroll_y: True
        size_hint_y: 1
        size_hint_x: 1
        GridLayout:
            cols: 1
            id: autocontrol_settings
            row_force_default: True
            padding: [0, dp(20)]
            spacing: [0, dp(10)]
            row_default_height: dp(150)
            size_hint_y: None
            height: self.minimum_height
                        
            
"""
class AutoControlConfigView(BaseConfigView):
    Builder.load_string(AUTOCONTROL_CONFIG_VIEW_KV)

    def __init__(self, **kwargs):
        super(AutoControlConfigView, self).__init__(**kwargs)
        self.view_loaded = False

        self.register_event_type('on_config_updated')

    def on_config_updated(self, cfg):
        try:
            self.view_loaded = False
            self._load_settings(cfg)
            # do the loading thing
        finally:
            self.view_loaded = True

    def _load_settings(self, cfg):
        self.ids.autocontrol_settings.add_widget(AutologgingView())
        self.ids.autocontrol_settings.add_widget(CameraControlView())

