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
from autosportlabs.widgets.separator import HSeparator, HSeparatorMinor
from fieldlabel import FieldLabel

class CameraMakeModelSpinner(MappedSpinner):
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
    HSeparatorMinor:
        text: 'Automatic SD Logging'
        halign: 'left'
        size_hint_y: 0.10

    BoxLayout:
        orientation: 'horizontal'
        FieldLabel:
            text: 'Enabled'
        Switch:
            id: enabled
"""

class AutologgingView(BaseConfigView):
    Builder.load_string(AUTOLOGGING_VIEW_KV)

    def __init__(self, **kwargs):
        super(AutologgingView, self).__init__(**kwargs)

CAMERACONTROL_VIEW_KV = """
<CameraControlView>:
    spacing: (dp(10))
    HSeparatorMinor:
        text: 'CameraControl'
        halign: 'left'
        size_hint_y: 0.10
            
    BoxLayout:
        orientation: 'horizontal'
        FieldLabel:
            text: 'Enabled'
        Switch:
            id: enabled

    BoxLayout:
        orientation: 'horizontal'
        FieldLabel:
            text: 'Camera'
        CameraMakeModelSpinner:
            id: makemodel
"""
class CameraControlView(BaseConfigView):
    Builder.load_string(CAMERACONTROL_VIEW_KV)

    def __init__(self, **kwargs):
        super(CameraControlView, self).__init__(**kwargs)

AUTOCONTROL_CONFIG_VIEW_KV = """
<AutoControlConfigView>:
    spacing: dp(10)
    orientation: 'vertical'

    HSeparator:
        text: 'Automatic Control'
        halign: 'left'
        size_hint_y: 0.10
        
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: 0.15
        FieldLabel:
            text: 'Channel'
        TextValueField:
            id: channel
            
    BoxLayout:
        size_hint_y: 0.15
        FieldLabel:
            text: 'Start Trigger'
        LtGtSpinner:
            id: ltgt_start
        TextValueField:
            id: threshold_start
        
    BoxLayout:
        size_hint_y: 0.15
        FieldLabel:
            text: 'Stop Trigger'
        LtGtSpinner:
            id: ltgt_stop
        TextValueField:
            id: threshold_stop
        
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
            row_default_height: dp(120)
            size_hint_y: None
            height: self.minimum_height
            AutologgingView:
            CameraControlView:
                        
            
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
            #do the loading thing
        finally:
            self.view_loaded = True


