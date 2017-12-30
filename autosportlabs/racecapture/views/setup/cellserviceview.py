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
from __builtin__ import True
kivy.require('1.10.0')
from kivy.clock import Clock
from kivy.app import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.modalview import ModalView
from autosportlabs.racecapture.views.setup.infoview import InfoView
import webbrowser
from utils import is_mobile_platform
from fieldlabel import FieldLabel
from valuefield import ValueField
from settingsview import SettingsSwitch, SettingsMappedSpinner
import json
import os

class CellServiceView(InfoView):
    """
    A setup screen that lets them set up their cellular carrier
    """
    Builder.load_string("""
<CellServiceView>:
    background_source: 'resource/setup/background_podium.jpg'
    info_text: 'Select your cellular Service'
    BoxLayout:
        orientation: 'vertical'
        padding: (0, dp(20))
        spacing: (0, dp(10))

        SettingsView:
            id: cell_enable
            label_text: 'Cellular Module'
            help_text: 'Enable if the Real-time telemetry module is installed'
        SettingsView:
            id: cell_provider
            label_text: 'Cellular Provider'
            help_text: 'Select the cellular provider, or specify custom APN settings'
        Label:
            text: 'Custom Cellular Settings'
            text_size: self.size
            halign: 'center'
            font_size: dp(26)
        GridLayout:
            cols: 2
            size_hint_y: 0.2
            spacing: (dp(30), dp(5))
            FieldLabel:
                text: 'APN Host'
                halign: 'right'
            ValueField:
                id: apn_host
                disabled: True
                on_text: root.on_apn_host(*args)
        GridLayout:
            cols: 2
            size_hint_y: 0.2            
            spacing: (dp(30), dp(5))
            FieldLabel:
                halign: 'right'
                text: 'APN User Name'
            ValueField:
                id: apn_user
                size_hint_y: 1
                disabled: True
                on_text: root.on_apn_user(*args)
        GridLayout:
            cols: 2
            size_hint_y: 0.2            
            spacing: (dp(30), dp(5))
            FieldLabel:
                halign: 'right'
                text: 'APN Password'
            ValueField:
                id: apn_pass
                disabled: True
                size_hint_y: 1
                on_text: root.on_apn_pass(*args)
    """)
    def __init__(self, **kwargs):
        super(CellServiceView, self).__init__(**kwargs)
        
        cell_enable = self.ids.cell_enable
        cell_enable.setControl(SettingsSwitch(active=self.rc_config.connectivityConfig.cellConfig.cell_enabled))
        cell_enable.control.bind(active=self.on_cell_change)

        cell_provider = self.ids.cell_provider
        cell_provider.bind(on_setting=self.on_cell_provider)
        apnSpinner = SettingsMappedSpinner()
        
        self.loadApnSettingsSpinner(apnSpinner)
        self.apnSpinner = apnSpinner
        cell_provider.setControl(apnSpinner)

    def get_apn_setting_by_name(self, name):
        providers = self.cellProviderInfo['cellProviders']
        for apn_name in providers:
            if apn_name == name:
                return providers[apn_name]
        return None
        
    def on_cell_change(self, instance, value):
        self.rc_config.connectivityConfig.stale = True
        self.connectivityConfig.cellConfig.cellEnabled = value

    def on_cell_provider(self, instance, value):
        apnSetting = self.get_apn_setting_by_name(value)
        knownProvider = False
        if apnSetting:
            self.apnHostField.text = apnSetting['apn_host']
            self.apnUserField.text = apnSetting['apn_user']
            self.apnPassField.text = apnSetting['apn_pass']
            knownProvider = True

        self.update_controls_state()
        self.setCustomApnFieldsDisabled(knownProvider)
        
    def loadApnSettingsSpinner(self, spinner):
        try:
            json_data = open(os.path.join(self.base_dir, 'resource', 'settings', 'cell_providers.json'))
            cellProviderInfo = json.load(json_data)
            apnMap = {}
            apnMap['custom'] = self.customApnLabel

            for name in cellProviderInfo['cellProviders']:
                apnMap[name] = name

            spinner.setValueMap(apnMap, self.customApnLabel)
            self.cellProviderInfo = cellProviderInfo
        except Exception as detail:
            print('Error loading cell providers ' + str(detail))
        

    def on_setup_config(self, instance, value):
        self.ids.next.disabled = False
        self.ids.next.pulsing = False


    def select_next(self):
        self.ids.next.disabled = True
        def do_next():
            super(CellServiceView, self).select_next()

        cfg = self.rc_config.connectivityConfig
        cfg.stale = True

        self.write_rcp_config('Updating Configuration ... ', do_next)


