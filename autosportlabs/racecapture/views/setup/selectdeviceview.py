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
from kivy.uix.screenmanager import Screen
from autosportlabs.racecapture.views.setup.infoview import InfoView
from autosportlabs.uix.button.betterbutton import BetterToggleButton

SELECT_DEVICE_VIEW_KV = """
<SelectDeviceView>:
    background_source: 'resource/setup/background_device_screen.jpg'
    info_text: 'Select your device'
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint_y: 0.2
        AnchorLayout:
            size_hint_y: 0.3
            Image:
                allow_stretch: True
                source: 'resource/setup/device_racecapture.png'     
            AnchorLayout:
                anchor_x: 'right'
                padding: (dp(10), dp(10))
                BetterToggleButton:
                    id: racecapture
                    group: 'device'
                    size_hint: (0.35, 0.5)
                    text: 'RaceCapture'
                    on_release: root.select_device('racecapture')
        AnchorLayout:
            size_hint_y: 0.3        
            Image:
                allow_stretch: True
                source: 'resource/setup/device_racecapturepro.png'             
            AnchorLayout:
                anchor_x: 'right'
                padding: (dp(10), dp(10))
                BetterToggleButton:
                    id: racecapturepro
                    group: 'device'
                    size_hint: (0.35, 0.5)
                    text: 'RaceCapture/Pro'
                    on_release: root.select_device('racecapturepro')
        BoxLayout:
            size_hint_y: 0.2
"""

class SelectDeviceView(InfoView):
    Builder.load_string(SELECT_DEVICE_VIEW_KV)
    def __init__(self, **kwargs):
        super(SelectDeviceView, self).__init__(**kwargs)
        self.ids.next.disabled = True
        self.ids.next.pulsing = False

    def select_device(self, device):
        self.ids.next.disabled = False
        #update our setup config with the selected device
        step = self.get_setup_step('device')
        step['device'] = device

    def on_setup_config(self, instance, value):
        self._update_ui()
        
    def _update_ui(self):
        #set the button that matches what's in the current config, if set
        if self.setup_config is not None:
            step = self.get_setup_step('device')
            current_device = step['device']
            current_device_button = self.ids.get(current_device)
            if current_device_button is not None:
                current_device_button.active = True
            
        