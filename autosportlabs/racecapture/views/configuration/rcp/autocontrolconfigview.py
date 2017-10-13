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
from kivy.properties import NumericProperty, ListProperty, ObjectProperty
from kivy.app import Builder
from utils import *
from settingsview import SettingsView
from autosportlabs.racecapture.views.configuration.baseconfigview import BaseConfigView
from autosportlabs.widgets.separator import HSeparator, HSeparatorMinor, HLineSeparator
from autosportlabs.racecapture.views.configuration.channels.channelnameselectorview import ChannelNameSelectorView
from autosportlabs.racecapture.config.rcpconfig import BaseChannel
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

SD_CONTROL_VIEW_KV = """
<SDLoggingControlView>:
    spacing: dp(15)
    HLineSeparator:
        size_hint_y: 0.01    
    SettingsView:
        id: enabled
        label_text: 'SD Logging'
        help_text: 'Enable SD logging control'
        size_hint_y: 0.15
"""

class SDLoggingControlView(BaseConfigView):
    Builder.load_string(SD_CONTROL_VIEW_KV)
    config = ObjectProperty()

    def __init__(self, **kwargs):
        super(SDLoggingControlView, self).__init__(**kwargs)
        self.view_loaded = False
        self.register_event_type('on_modified')
        settings = self.ids.enabled
        settings.bind(on_setting=self.on_setting_enabled)
        settings.setControl(SettingsSwitch())

    def on_setting_enabled(self, instance, value):
        if not self.view_loaded:
            return
        self.config.enabled = value
        self.config.stale = True
        self.dispatch('on_modified')

    def update_config(self, cfg):
        self.view_loaded = False
        self.config = cfg
        self.ids.enabled.setValue(cfg.enabled)
        self.view_loaded = True

    def on_modified(self):
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
    config = ObjectProperty()

    def __init__(self, **kwargs):
        super(CameraControlView, self).__init__(**kwargs)
        self.view_loaded = False
        self.register_event_type('on_modified')

        settings = self.ids.enabled
        settings.bind(on_setting=self.on_setting_enabled)
        settings.setControl(SettingsSwitch())

        camera_type = self.ids.makemodel
        camera_type.bind(on_setting=self._on_setting_makemodel)
        camera_type.setControl(CameraMakeModelSpinner())

    def on_setting_enabled(self, instance, value):
        if not self.view_loaded:
            return
        self.config.enabled = value
        self.config.stale = True
        self.dispatch('on_modified')

    def _on_setting_makemodel(self, instance, value):
        if not self.view_loaded:
            return
        self.config.make_model = value
        self.config.stale = True
        self.dispatch('on_modified')

    def update_config(self, cfg):
        self.view_loaded = False
        self.config = cfg
        self.ids.enabled.setValue(cfg.enabled)
        self.ids.makemodel.setValue(cfg.make_model)
        self.view_loaded = True

    def on_modified(self):
        pass


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
        BoxLayout:
        ChannelNameSelectorView:
            id: channel
            on_channel: root._on_channel_name(*args)
            full_editor: False
            size_hint_x: None
            width: dp(300)
            
    BoxLayout:
        spacing: dp(5)
        size_hint_y: None
        height: dp(30)
        FieldLabel:
            text: 'Start Trigger'
            halign: 'right'
        LtGtSpinner:
            id: start_greater_than
            size_hint_x: None
            width: dp(100)
            on_value: root._on_value_changed('start_greater_than', *args) 
        FloatValueField:
            size_hint_x: None
            width: dp(65)
            id: start_threshold
            on_text: root._on_value_changed('start_threshold', *args)
        FieldLabel:
            text: 'after'
            size_hint_x: None
            width: dp(50)
            halign: 'center'
        IntegerValueField:
            size_hint_x: None
            width: dp(50)
            id: start_time
            on_text: root._on_value_changed('start_time', *args)
        FieldLabel:
            text: 'sec.'
            size_hint_x: None
            width: dp(45)
            halign: 'center'
        
    BoxLayout:
        spacing: dp(5)
        size_hint_y: None
        height: dp(30)
        FieldLabel:
            text: 'Stop Trigger'
            halign: 'right'
        LtGtSpinner:
            id: stop_greater_than
            size_hint_x: None
            width: dp(100)
            on_value: root._on_value_changed('stop_greater_than', *args)
        FloatValueField:
            size_hint_x: None
            width: dp(65)
            id: stop_threshold
            on_text: root._on_value_changed('stop_threshold', *args)
        FieldLabel:
            text: 'after'
            size_hint_x: None
            width: dp(50)
            halign: 'center'
        IntegerValueField:
            size_hint_x: None
            width: dp(50)
            id: stop_time
            on_text: root._on_value_changed('stop_time', *args)
        FieldLabel:
            text: 'sec.'
            size_hint_x: None
            width: dp(45)
            halign: 'center'
        
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
    channels = ObjectProperty()

    def __init__(self, **kwargs):
        super(AutoControlConfigView, self).__init__(**kwargs)
        self.register_event_type('on_config_updated')
        self.view_loaded = False
        self.sd_logging_control_view = None
        self.camera_control_view = None
        self.config = None
        self.auto_configs = []

    def on_config_updated(self, cfg):
        try:
            self.view_loaded = False
            self._load_view(cfg)
        finally:
            self.view_loaded = True


    def _update_auto_control_view(self, has_auto_control_type, config, view_type, container):
        view = None
        for c in container.children:
            if isinstance(c, view_type):
                view = c
                break

        if has_auto_control_type:
            if not view:
                view = view_type()
                view.bind(on_modified=self._on_autocontrol_modified)
                container.add_widget(view)
            view.update_config(config)
            self.auto_configs.append(config)
        else:
            if view:
                container.remove_widget(view)

    def _load_view(self, cfg):
        self.config = cfg
        self.ids.channel.on_channels_updated(self.channels)
        has_sd_logging = cfg.capabilities.has_sd_logging
        has_camera_control = cfg.capabilities.has_camera_control

        self.auto_configs = []
        container = self.ids.autocontrol_settings
        self._update_auto_control_view(has_sd_logging, cfg.sd_logging_control_config, SDLoggingControlView, container)
        self._update_auto_control_view(has_camera_control, cfg.camera_control_config, CameraControlView, container)

        primary_config = None
        primary_config = cfg.sd_logging_control_config if has_sd_logging else primary_config
        primary_config = cfg.camera_control_config if has_camera_control else primary_config

        if primary_config:
            channel = BaseChannel()
            channel.name = primary_config.channel
            self.ids.channel.setValue(channel)

            self.ids.start_threshold.text = str(primary_config.start_threshold)
            self.ids.start_greater_than.setFromValue(primary_config.start_greater_than)
            self.ids.start_time.text = str(primary_config.start_time)

            self.ids.stop_threshold.text = str(primary_config.stop_threshold)
            self.ids.stop_greater_than.setFromValue(primary_config.stop_greater_than)
            self.ids.stop_time.text = str(primary_config.stop_time)

    def _on_channel_name(self, instance, value):
        self._on_value_changed('channel', instance, value.name)

    def _on_value_changed(self, attr, instance, value):
        for cfg in self.auto_configs:
            setattr(cfg, attr, value)
            cfg.stale = True
        if self.view_loaded:
            self.dispatch('on_modified')

    def _on_autocontrol_modified(self, instance):
        self.dispatch('on_modified')
