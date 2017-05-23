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
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ListProperty, BooleanProperty
from utils import *
from autosportlabs.racecapture.views.configuration.channels.channelsview import ChannelEditor
from autosportlabs.racecapture.data.channels import *


class ChannelNameSelectorView(BoxLayout):

    Builder.load_string("""
<ChannelNameSelectorView>:
    BoxLayout:
        orientation: 'horizontal'
        spacing: sp(5)
        FieldLabel:
            size_hint_x: 0.4
            text: 'Channel'
            halign: 'right'
            id: channel_label
        ChannelNameSpinner:
            size_hint_x: 0.45
            id: channel_name
            on_text: root.on_channel_selected(*args)
        BoxLayout:
            size_hint_x: 0.15
#            padding: (dp(2), dp(2))
            IconButton:
                color: ColorScheme.get_accent()        
                text: u'\uf013'
                on_release: root.on_customize(*args)    
    """)

    channel_type = NumericProperty(CHANNEL_TYPE_UNKNOWN)
    filter_list = ListProperty([])
    compact = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(ChannelNameSelectorView, self).__init__(**kwargs)
        self.channel_config = None
        self._runtime_channels = None
        self.register_event_type('on_channels_updated')
        self.register_event_type('on_channel')
        self.bind(channel_type=self.on_channel_type)

    def on_filter_list(self, instance, value):
        self.ids.channel_name.filterList = value

    def on_channels_updated(self, runtime_channels):
        self._runtime_channels = runtime_channels
        self.ids.channel_name.dispatch('on_channels_updated', runtime_channels)

    def on_channel_type(self, instance, value):
        self.ids.channel_name.channelType = value

    def on_compact(self, instance, value):
        if value:
            label = self.ids.channel_label
            label.parent.remove_widget(label)

    def setValue(self, value):
        self.channel_config = value
        self.set_channel_name(value.name)

    def set_channel_name(self, name):
        self.ids.channel_name.text = str(name)

    def on_channel_selected(self, instance, value):
        channel_meta = self._runtime_channels.findChannelMeta(value, None)
        if channel_meta is not None:
            self.channel_config.name = channel_meta.name
            self.channel_config.units = channel_meta.units
            self.channel_config.min = channel_meta.min
            self.channel_config.max = channel_meta.max
            self.channel_config.precision = channel_meta.precision
            self.dispatch('on_channel')

    def _dismiss_editor(self):
        self._popup.dismiss()

    def on_customize(self, *args):

        content = ChannelEditor(channel=self.channel_config)
        popup = Popup(title='Customize Channel',
                      content=content,
                      size_hint=(None, None), size=(dp(500), dp(220)))
        popup.bind(on_dismiss=self.on_edited)
        content.bind(on_channel_edited=lambda *args:popup.dismiss())
        popup.open()

    def on_edited(self, *args):
        self.set_channel_name(self.channel_config.name)
        self.dispatch('on_channel')

    def on_channel(self):
        pass

