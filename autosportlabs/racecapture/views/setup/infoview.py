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
from kivy.properties import StringProperty

INFO_VIEW_KV = """    
<InfoView>:
    AnchorLayout:
        Image:
            allow_stretch: True
            source: root.background_source
        AnchorLayout:
            anchor_y: 'top'
            FieldLabel:
                text: root.info_text
        AnchorLayout:
            anchor_x: 'right'
            anchor_y: 'bottom'
            padding: (dp(10), dp(10))            
            Button:
                text: 'Next'
                size_hint: (0.25, 0.2)
"""
        
class InfoView(Screen):
    background_source = StringProperty()
    info_text = StringProperty()
    Builder.load_string(INFO_VIEW_KV)
    def __init__(self, **kwargs):
        super(InfoView, self).__init__(**kwargs)
