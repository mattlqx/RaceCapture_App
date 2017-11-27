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
from kivy.clock import Clock
from kivy.app import Builder
from kivy.uix.screenmanager import Screen
from autosportlabs.racecapture.views.setup.infoview import InfoView
from autosportlabs.uix.button.betterbutton import BetterToggleButton
from kivy.properties import ObjectProperty

SELECT_PRESET_VIEW_KV = """
<SelectPresetView>:
    #background_source: 'resource/setup/background_device.jpg'
    info_text: 'Select a preset'
    BoxLayout:
        orientation: 'vertical'
        padding: [0, dp(20)]
        spacing: [0, dp(10)]
        BoxLayout:
            size_hint_y: 0.10
        ScrollContainer:
            size_hint_y: 0.7
            do_scroll_x: False
            do_scroll_y: True
            size_hint_y: 1
            size_hint_x: 1
            GridLayout:
                id: presets
                spacing: [0, dp(10)]
                row_default_height: dp(130)
                size_hint_y: None
                height: self.minimum_height
                cols: 1
        BoxLayout:
            size_hint_y: 0.15
"""


class SelectPresetView(InfoView):
    """
    A setup screen that lets users select what device they have.
    """
    Builder.load_string(SELECT_PRESET_VIEW_KV)
    
    def __init__(self, **kwargs):
        super(SelectPresetView, self).__init__(**kwargs)
        self.ids.next.disabled = True
        self.ids.next.pulsing = False

    def on_setup_config(self, instance, value):
        self._update_ui()

    def _update_ui(self):
        self.ids.presets.clear_widgets()
        for k, v in self.preset_manager.get_presets_by_type('PC_MK1'):
            name = v.name
            notes = v.notes
            self.add_preset(k, name, notes)
        

    def add_preset(self, preset_id, name, notes):
        print('add presest {}'.format(preset_id))
    
    def _select_preset(self, preset):
        self.ids.next.disabled = False
        
                
