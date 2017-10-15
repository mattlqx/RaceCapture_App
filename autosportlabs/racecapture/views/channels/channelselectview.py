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
from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
kivy.require('1.9.1')
from iconbutton import IconButton
from kivy.app import Builder
from kivy.metrics import dp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListView, ListItemButton
from utils import kvFind
from kivy.adapters.listadapter import ListAdapter
from kivy.properties import ListProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.logger import Logger
from autosportlabs.racecapture.theme.color import ColorScheme

class SelectableChannelLabel(RecycleDataViewBehavior, Label):
    Builder.load_string("""
<SelectableChannelLabel>:
    # Draw a background to indicate selection
    canvas.before:
        Color:
            rgba: ColorScheme.get_primary() if self.selected else ColorScheme.get_dark_background_translucent()
        Rectangle:
            pos: self.pos
            size: self.size
    font_name: 'resource/fonts/ASL_light.ttf'
    font_size: self.height * 0.5    
    """)

    index = NumericProperty(None, allownone=True)
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableChannelLabel, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableChannelLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            rv.selected_channel = rv.data[index]['text']

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''

class ChannelSelectDialog(FloatLayout):
    Builder.load_string("""
<ChannelSelectDialog>:
    BoxLayout:
        size: root.size
        pos: root.pos
        orientation: 'vertical'
        ChannelSelectView:
            id: sv
        IconButton:
            size_hint_y: 0.2
            text: "\357\200\214"
            on_press: root.on_close()
    """)

    selected_channel = StringProperty(None, allownone=True)

    def __init__(self, settings, channel, **kwargs):
        super(ChannelSelectDialog, self).__init__(**kwargs)
        self.register_event_type('on_channel_selected')
        self.register_event_type('on_channel_cancel')

        self.selected_channel = channel
        sv = self.ids.sv

        sv.selected_channel = channel

        available_channels = list(settings.runtimeChannels.get_active_channels().iterkeys())
        available_channels.sort()

        sv.available_channels = available_channels
        sv.bind(on_channel_selected=self.on_select)

    def on_select(self, instance, value):
        self.selected_channel = value

    def on_cancel(self):
        self.dispatch('on_channel_cancel', self.selected_channel)

    def on_close(self):
        self.dispatch('on_channel_selected', self.selected_channel)

    def on_channel_selected(self, selected_channel):
        pass

    def on_channel_cancel(self):
        pass

class ChannelSelectView(RecycleView):
    Builder.load_string("""
<ChannelSelectView>:
    viewclass: 'SelectableChannelLabel'
    scroll_type: ['bars', 'content']
    scroll_wheel_distance: dp(114)
    bar_width: dp(20)
       
    SelectableRecycleBoxLayout:
        default_size: None, dp(56)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        multiselect: False
        touch_multiselect: True    
    """)
    available_channels = ListProperty()
    selected_channel = StringProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super(ChannelSelectView, self).__init__(**kwargs)
        self.register_event_type('on_channel_selected')

    def on_available_channels(self, instance, value):
        channel = self.selected_channel
        data = []
        selected_index = None
        index = 0
        for c in value:
            data.append({'text': c})
            if c == channel:
                selected_index = index
            index += 1

        self.data = data

        if selected_index:
            self.layout_manager.selected_nodes = [selected_index]

    def on_selected_channel(self, instance, value):
        self.dispatch('on_channel_selected', value)

    def on_channel_selected(self, selected_channel):
        pass




