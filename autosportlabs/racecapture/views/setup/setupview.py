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
from kivy.app import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
import os
import json

SETUP_VIEW_KV = """
<SetupView>:
    BoxLayout:
        orientation: 'horizontal'
        GridLayout:
            id: steps
            cols: 1
            size_hint_x: 0.25
        ScreenManager:
            id: screen_manager
            size_hint_x: 0.75
"""

class SetupView(Screen):
    kv_loaded = False
    def __init__(self, databus, base_dir, **kwargs):
        super(SetupView, self).__init__(**kwargs)
        self._base_dir = base_dir
        self._databus = databus
        if not SetupView.kv_loaded:
            Builder.load_string(SETUP_VIEW_KV)
            SetupView.kv_loaded = True
            
    def on_parent(self, instance, value):
        self._init_view()
        
    def _init_view(self):
        json_data = open(os.path.join(self._base_dir, 'resource', 'setup', 'setup.json'))
        setup = json.load(json_data)
        steps = setup['steps']
        for step in steps:
            print('{}'.format(step))
        
            

