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
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.app import Builder
from kivy.uix.label import Label
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.screenmanager import Screen
from autosportlabs.widgets.separator import HSeparator, HSeparatorMinor
from autosportlabs.racecapture.views.util.alertview import alertPopup
from autosportlabs.racecapture.views.configuration.baseconfigview import BaseConfigView
from autosportlabs.racecapture.data.channels import ChannelMeta
from utils import *
from autosportlabs.racecapture.config.rcpconfig import *
from valuefield import FloatValueField, IntegerValueField, TextValueField
from autosportlabs.widgets.scrollcontainer import ScrollContainer


class ChannelNameField(TextValueField):

    def insert_text(self, s, from_undo=False):
        s = ''.join([char for char in s if char.isalnum() or char == ' '])
        return super(ChannelNameField, self).insert_text(s, from_undo=from_undo)


class ChannelLabel(Label):
    Builder.load_string("""
<ChannelLabel>:
    size_hint_y: None
    padding_x: -10
    height: max(dp(30), self.texture_size[1] + dp(5))
    text_size: self.width, None
    valign: 'middle'
    halign: 'left'
    font_size: sp(18)
    canvas.before:
        Color:
            rgba: .1, .1, .1, .9
        Rectangle:
            size: self.size
            pos: self.pos
    
    """)
    def __init__(self, **kwargs):
        super(ChannelLabel, self).__init__(**kwargs)

class ChannelView(BoxLayout):
    Builder.load_string("""
<ChannelView>:
    spacing: dp(10)
    height: dp(30)
    size_hint_y: None
    BoxLayout:
        orientation: 'horizontal'
        IconButton:
            size_hint_x: 0.05
            rcid: 'sysChan'
            text: ''
        ChannelLabel:
            size_hint_x: 0.7
            rcid: 'name'
            font_size: sp(25)
        IconButton:
            size_hint_x: 0.05
            rcid: 'edit'
            on_release: root.on_edit()
            text: '\357\201\204'
        IconButton:
            size_hint_x: 0.05
            rcid: 'delete'
            text: '\357\200\224'
            on_release: root.on_delete()            
    
    """)

    channel = None
    def __init__(self, **kwargs):
        super(ChannelView, self).__init__(**kwargs)
        self.channel = kwargs.get('channel', self.channel)
        self.register_event_type('on_delete_channel')
        self.register_event_type('on_modified')
        self.updateView()

    def on_modified(self):
        pass

    def updateView(self):
        kvFind(self, 'rcid', 'sysChan').text = '\357\200\243' if self.channel.systemChannel else ''
        deleteButton = kvFind(self, 'rcid', 'delete')
        deleteButton.disabled = self.channel.systemChannel
        deleteButton.text = '\357\200\224'
        kvFind(self, 'rcid', 'name').text = self.channel.name + ('' if self.channel.units == '' else ' (' + self.channel.units + ')')

    def on_edit(self):
        channel = self.channel
        popup = Popup(title='Edit System Channel' if channel.systemChannel else 'Edit Channel',
                      content=ChannelEditor(channel=channel),
                      size_hint=(None, None), size=(dp(500), dp(180)))
        popup.open()
        popup.bind(on_dismiss=self.on_edited)

    def on_delete(self):
        self.dispatch('on_delete_channel', self.channel)

    def on_delete_channel(self, *args):
        pass

    def on_edited(self, *args):
        self.updateView()
        self.dispatch('on_modified')

class ChannelEditor(BoxLayout):
    Builder.load_string("""
<ChannelEditor>:
    orientation: 'vertical'
    GridLayout:
        size_hint_y: 0.75
        spacing: dp(20)
        cols: 2
        BoxLayout:
            spacing: dp(20)
            orientation: 'vertical'
            HSeparatorMinor:
                text: 'Channel'
            GridLayout:
                cols: 2
                spacing: dp(10)
                FieldLabel:
                    text: 'Name'
                ChannelNameField:
                    max_len: 11
                    rcid: 'name'
                    on_text: root.on_name(*args)
                FieldLabel:
                    text: 'Units'
                TextValueField:
                    max_len: 7
                    rcid: 'units'
                    on_text: root.on_units(*args)
        BoxLayout:
            spacing: dp(20)        
            orientation: 'vertical'
            HSeparatorMinor:
                text: 'Settings'
            GridLayout:
                cols: 2
                spacing: dp(10)
                FieldLabel:
                    text: 'Precision'
                IntegerValueField:
                    rcid: 'prec'
                    min_value: 0
                    max_value: 6
                    on_text: root.on_precision(*args)
                FieldLabel:
                    text: 'Min / max'
                BoxLayout:
                    orientation: 'horizontal'
                    FloatValueField:
                        rcid: 'min'
                        on_text: root.on_min(*args)
                    FloatValueField:
                        rcid: 'max'
                        on_text: root.on_max(*args)
    IconButton:
        size_hint_y: 0.25
        text: "\357\200\214"
        on_press: root.on_close()    
    """)

    channel = None
    def __init__(self, **kwargs):
        super(ChannelEditor, self).__init__(**kwargs)
        self.channel = kwargs.get('channel', None)
        self.register_event_type('on_channel_edited')
        self.init_view()

    def init_view(self):
        nameField = kvFind(self, 'rcid', 'name')
        unitsField = kvFind(self, 'rcid', 'units')
        precisionField = kvFind(self, 'rcid', 'prec')
        minField = kvFind(self, 'rcid', 'min')
        maxField = kvFind(self, 'rcid', 'max')

        nameField.set_next(unitsField)
        unitsField.set_next(precisionField)
        precisionField.set_next(minField)
        minField.set_next(maxField)
        maxField.set_next(nameField)

        if self.channel:
            channel = self.channel
            nameField.text = str(channel.name)
            try:
                nameField.disabled = channel.systemChannel
            except AttributeError:
                nameField.disabled = False
            unitsField.text = str(channel.units)
            precisionField.text = str(channel.precision)
            minField.text = str(channel.min)
            maxField.text = str(channel.max)

    def on_name(self, instance, value):
        value = value.strip()
        instance.text = value
        self.channel.name = value

    def on_units(self, instance, value):
        self.channel.units = value

    def on_precision(self, instance, value):
        self.channel.precision = int(value)

    def on_min(self, instance, value):
        max_range = self.channel.max
        min_range = float(value)
        if min_range > max_range:
            min_range = max_range
            instance.text = str(min_range)
        self.channel.min = float(min_range)

    def on_max(self, instance, value):
        min_range = self.channel.min
        max_range = float(value)
        if max_range < min_range:
            max_range = min_range
            instance.text = str(max_range)
        self.channel.max = float(max_range)


    def on_channel_edited(self, *args):
        pass

    def on_close(self):
        self.dispatch('on_channel_edited')

class ChannelsView(BaseConfigView):
    Builder.load_string("""
<ChannelsView>:
    BoxLayout:
        padding: (dp(10),dp(10))
        spacing: dp(20)
        orientation: 'vertical'
        HSeparator:
            text: 'System Channels'
            size_hint_y: 0.1
        BoxLayout:
            size_hint_y: 0.9
            padding: (dp(50), dp(10))
            spacing: dp(20)
            orientation: 'vertical'
            ScrollContainer:
                id: scrlChan
                size_hint_y: 0.7
                do_scroll_x:False
                do_scroll_y:True
                GridLayout:
                    rcid: 'channelsContainer'
                    padding: [dp(20), dp(20)]
                    spacing: [dp(10), dp(10)]
                    size_hint_y: None
                    height: max(self.minimum_height, scrlChan.height)
                    cols: 1
                
            BoxLayout:
                size_hint_y: 0.05
                IconButton:
                    text: '\357\201\247'
                    on_release: root.on_add_channel()
                    disabled: True
                    rcid: 'addChan'    
    """)

    channelsContainer = None
    channels = None
    def __init__(self, **kwargs):
        super(ChannelsView, self).__init__(**kwargs)
        self.register_event_type('on_config_updated')
        self.channelsContainer = kvFind(self, 'rcid', 'channelsContainer')

    def on_modified(self, *args):
        self.channels.stale = True
        super(ChannelsView, self).on_modified(args)

    def on_config_updated(self, rcpCfg):
        self.on_channels_updated(rcpCfg.channels)

    def on_channels_updated(self, runtime_channels):
        self.channelsContainer.clear_widgets()
        for channel in runtime_channels.items:
            channelView = ChannelView(channel=channel)
            channelView.bind(on_delete_channel=self.on_delete_channel)
            channelView.bind(on_modified=self.on_modified)
            self.channelsContainer.add_widget(channelView)
        self.channels = runtime_channels
        kvFind(self, 'rcid', 'addChan').disabled = False

    def on_delete_channel(self, instance, value):
        channelItems = self.channels.items
        for channel in channelItems:
            if value == channel:
                channelItems.remove(channel)
                break
        self.on_channels_updated(self.channels)
        self.channels.stale = True
        self.dispatch('on_modified')

    def on_add_channel(self):
        newChannel = ChannelMeta(name='Channel', units='', precision=0, min=0, max=100)
        self.channels.items.append(newChannel)
        channelView = ChannelView(channel=newChannel)
        channelView.bind(on_delete_channel=self.on_delete_channel)
        channelView.bind(on_modified=self.on_modified)
        self.channelsContainer.add_widget(channelView)
        channelView.on_edit()
        self.channels.stale = True
        self.dispatch('on_modified')

