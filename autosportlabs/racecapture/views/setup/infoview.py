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
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty

INFO_VIEW_KV = """    
<InfoView>:
    AnchorLayout:
        Image:
            allow_stretch: True
            source: root.background_source
        AnchorLayout:
            anchor_y: 'top'
            AnchorLayout:
                size_hint_y: 0.4
                padding: (dp(10), dp(10))
                FieldLabel:
                    on_ref_press: root.on_info_ref(*args)
                    markup: True
                    text_size: self.size
                    font_size: self.height * 0.15
                    text: root.info_text
                    shorten: False
                    valign: 'top'
        AnchorLayout:
            anchor_x: 'right'
            anchor_y: 'bottom'
            padding: (dp(10), dp(10))            
            LabelIconButton:
                id: next
                title: root.next_text
                icon_size: self.height * 0.5
                title_font_size: self.height * 0.6
                icon: root.next_icon
                size_hint: (0.22, 0.1)                
                on_release: root._on_next()
                
"""


class InfoView(Screen):
    """
    A base class for setup screens. 
    """
    setup_config = ObjectProperty()
    next_text = StringProperty('Next')
    next_icon = StringProperty(u'\uf0a9')
    background_source = StringProperty()
    info_text = StringProperty()
    is_last = BooleanProperty(False)
    rc_api = ObjectProperty()
    settings = ObjectProperty()

    Builder.load_string(INFO_VIEW_KV)

    def __init__(self, **kwargs):
        super(InfoView, self).__init__(**kwargs)
        self.register_event_type('on_next')

    def on_info_ref(self, instance, value):
        pass

    def on_pre_enter(self, *args):
        self.ids.next.pulsing = True

    def on_leave(self, *args):
        self.ids.next.pulsing = False

    def on_next(self):
        pass

    def on_is_last(self, instance, value):
        self.next_text = 'Done' if value else 'Next'
        self.next_icon = u'\uf00c' if value else u'\uf0a9'

    def _on_next(self):
        self.dispatch('on_next')

    def get_setup_step(self, key):
        if self.setup_config is not None:
            for step in self.setup_config['steps']:
                if step['key'] == key:
                    return step
        return None
