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
kivy.require('1.9.1')
from kivy.app import Builder
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
import re
from autosportlabs.racecapture.views.configuration.baseconfigview import BaseConfigView
from autosportlabs.racecapture.views.configuration.rcp.telemetry.backgroundstreamingview import BackgroundStreamingView
from autosportlabs.widgets.separator import HLineSeparator
from settingsview import SettingsView, SettingsTextField, SettingsSwitch
from valuefield import ValueField
from utils import *

TELEMETRY_CONFIG_VIEW_KV = 'autosportlabs/racecapture/views/configuration/rcp/telemetry/telemetryconfigview.kv'


class TelemetryConfigView(BaseConfigView):
    connectivityConfig = None
    Builder.load_file(TELEMETRY_CONFIG_VIEW_KV)

    def __init__(self, capabilities, **kwargs):
        super(TelemetryConfigView, self).__init__(**kwargs)
        self.register_event_type('on_config_updated')
    
        deviceId = kvFind(self, 'rcid', 'deviceId')
        deviceId.bind(on_setting=self.on_device_id)
        deviceId.setControl(SettingsTextField())

        self._bg_stream_view = None
        self.capabilities = capabilities

        self._render()

    def _render(self):
        if self.capabilities.has_cellular:
            separator = HLineSeparator()
            self.ids.content.add_widget(separator)

            bg_stream_view = BackgroundStreamingView()
            self.ids.content.add_widget(bg_stream_view)
            bg_stream_view.bind(on_modified=self._on_bg_stream_modified)
            self._bg_stream_view = bg_stream_view

    def _on_bg_stream_modified(self, *args):
        self.dispatch('on_config_modified')

    def on_device_id(self, instance, value):
        if self.connectivityConfig and value != self.connectivityConfig.telemetryConfig.deviceId:
            value = strip_whitespace(value)
            if len(value) > 0 and not self.validate_device_id(value):
                instance.set_error('Only numbers / letters allowed')
            else:
                #instance.setValue(value)
                self.connectivityConfig.telemetryConfig.deviceId = value
                self.connectivityConfig.stale = True
                self.dispatch('on_modified')
                instance.clear_error()

    def on_config_updated(self, rcpCfg):
        connectivityConfig = rcpCfg.connectivityConfig
        kvFind(self, 'rcid', 'deviceId').setValue(connectivityConfig.telemetryConfig.deviceId)
        self.connectivityConfig = connectivityConfig

        if self._bg_stream_view:
            self._bg_stream_view.on_config_updated(rcpCfg)

    def validate_device_id(self, device_id):
        return device_id.isalnum()
