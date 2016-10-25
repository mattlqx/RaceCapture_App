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
        id: check
        value: root.check
        size_hint_x: 0.25
        disabled: True
        background_checkbox_disabled_down: self.background_checkbox_down
        background_checkbox_disabled_normal: self.background_checkbox_normal
        active: True
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
            ScreenManager:
                canvas.before:
                    Color:
                        rgba: ColorScheme.get_dark_background_translucent()
                    Rectangle:
                        pos: self.pos
                        size: self.size    
                id: screen_manager
"""

class SetupItem(BoxLayout):
    title = StringProperty('')
    check = BooleanProperty(False)
    def __init__(self, **kwargs):
        super(SetupItem, self).__init__(**kwargs)
        
class SetupView(Screen):
    kv_loaded = False
    Builder.load_string(SETUP_VIEW_KV)
    def __init__(self, databus, base_dir, **kwargs):
        super(SetupView, self).__init__(**kwargs)
        self._base_dir = base_dir
        self._databus = databus
        if not SetupView.kv_loaded:
            SetupView.kv_loaded = True
            
    def on_parent(self, instance, value):
        Clock.schedule_once(self._init_view)
        
    def _init_view(self, *args):
        json_data = open(os.path.join(self._base_dir, 'resource', 'setup', 'setup.json'))
        setup = json.load(json_data)
        steps = setup['steps']
        for step in steps:
            content = SetupItem(title=step['title'])
            self.ids.steps.add_widget(content)
        
            

