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

from kivy.uix.boxlayout import BoxLayout
from autosportlabs.widgets.scrollcontainer import ScrollContainer
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.settings import SettingsWithNoMenu
from kivy.app import Builder
from kivy.utils import platform
from utils import *
import os
import json

PREFERENCES_KV_FILE = 'autosportlabs/racecapture/views/preferences/preferences.kv'

class PreferencesView(Screen):
    settings = None
    content = None
    base_dir = None

    def __init__(self, settings, **kwargs):
        Builder.load_file(PREFERENCES_KV_FILE)
        super(PreferencesView, self).__init__(**kwargs)
        self.settings = settings
        self.base_dir = kwargs.get('base_dir')
        self.register_event_type('on_pref_change')

        self.settings_view = SettingsWithNoMenu()
        self.settings_view.bind(on_config_change=self._on_preferences_change)

        # So, Kivy's Settings object doesn't allow you to add multiple json panels at a time, only 1. If you add
        # multiple, the last one added 'wins'. So what we do is load the settings JSON ourselves and then merge it
        # with any platform-specific settings (if applicable). It's silly, but works.
        settings_json = json.loads(open(os.path.join(self.base_dir, 'resource', 'settings', 'settings.json')).read())

        if platform == 'android':
            android_settings_json = json.loads(open(os.path.join(self.base_dir, 'resource', 'settings', 'android_settings.json')).read())
            settings_json = settings_json + android_settings_json

        self.settings_view.add_json_panel('Preferences', self.settings.userPrefs.config, data=json.dumps(settings_json))

        self.content = kvFind(self, 'rcid', 'preferences')
        self.content.add_widget(self.settings_view)

    def on_pref_change(self, section, option, value):
        pass

    def _on_preferences_change(self, menu, config, section, key, value):
        self.dispatch('on_pref_change', section, key, value)

