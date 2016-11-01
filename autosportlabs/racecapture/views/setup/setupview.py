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
from kivy.clock import Clock
from kivy.app import Builder
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from fieldlabel import FieldLabel
from autosportlabs.racecapture.views.setup.setupfactory import setup_factory
from autosportlabs.racecapture.views.util.alertview import confirmPopup
import os
import json

SETUP_VIEW_KV = """
<SetupItem>:
    canvas.before:
        Color:
            rgba: ColorScheme.get_dark_background_translucent()
        Rectangle:
            pos: self.pos
            size: self.size    
    orientation: 'horizontal'
    CheckBox:
        id: complete
        size_hint_x: 0.25
        disabled: True
        background_checkbox_disabled_down: self.background_checkbox_down
        background_checkbox_disabled_normal: self.background_checkbox_normal
        active: root.complete
    FieldLabel:
        id: title
        size_hint_x: 0.75
        text: root.title
        font_size: self.height * 0.4
    
<SetupView>:
    BoxLayout:
        orientation: 'horizontal'
        GridLayout:
            id: steps
            cols: 1
            size_hint_x: 0.25
            row_default_height: self.height * 0.1
            row_force_default: True
            padding: (dp(5), dp(5), dp(2.5), dp(5))
            spacing: dp(5)
        BoxLayout:
            padding: (dp(2.5), dp(5), dp(5), dp(5))
            size_hint_x: 0.75     
            AnchorLayout:       
                ScreenManager:
                    id: screen_manager
                AnchorLayout:
                    anchor_x: 'left'
                    anchor_y: 'bottom'
                    padding: (dp(10), dp(10))
                    LabelIconButton:
                        id: next
                        title: 'Skip'
                        icon_size: self.height * 0.5
                        title_font_size: self.height * 0.6
                        icon: u'\uf052'
                        size_hint: (0.2, 0.15)                
                        on_release: self.tile_color=ColorScheme.get_dark_accent(); root.on_skip()
                        on_press: self.tile_color=ColorScheme.get_medium_accent()
"""

class SetupItem(BoxLayout):
    title = StringProperty('')
    complete = BooleanProperty(False)
    def __init__(self, **kwargs):
        super(SetupItem, self).__init__(**kwargs)

class SetupView(Screen):
    kv_loaded = False
    Builder.load_string(SETUP_VIEW_KV)
    def __init__(self, settings, databus, base_dir, **kwargs):
        super(SetupView, self).__init__(**kwargs)
        self._settings = settings
        self._base_dir = base_dir
        self._databus = databus
        self._setup_config = None
        self._init_setup_config()

        if not SetupView.kv_loaded:
            SetupView.kv_loaded = True

    def on_enter(self):
        Clock.schedule_once(self.init_view)

    @property
    def should_show_setup(self):
        """
        Returns True if this setup view should be activated
        """
        setup_enabled = self._settings.userPrefs.get_pref_bool('setup', 'setup_enabled')
        next_view = self._select_next_view()
        return setup_enabled and next_view is not None

    def _skip_request(self):
        def confirm_skip(instance, skip):
            self._skip(skip)
            popup.dismiss()
        popup = confirmPopup('Skip', 'Continue setup next time?', confirm_skip)

    def _skip(self, continue_next_time):
        self._settings.userPrefs.set_pref('setup', 'setup_enabled', continue_next_time)

    def on_skip(self):
        self._skip_request()

    def _init_setup_config(self):
        json_data = open(os.path.join(self._base_dir, 'resource', 'setup', 'setup.json'))
        setup_config = json.load(json_data)
        self._setup_config = setup_config

    def init_view(self, *args):
        steps = self._setup_config['steps']
        for step in steps:
            content = SetupItem(title=step['title'], complete=step['complete'])
            self.ids.steps.add_widget(content)

        screen = self._select_next_view()
        if screen is not None:
            self.ids.screen_manager.switch_to(screen)
        else:
            self._setup_complete()

    def _select_next_view(self):
        setup_config = self._setup_config
        steps = setup_config['steps']
        for step in steps:
            if step['complete'] == False:
                return self._select_view(step)
        return None

    def _select_view(self, step):
        screen = setup_factory(step['key'])
        return screen

    def _setup_complete(self):
        pass
