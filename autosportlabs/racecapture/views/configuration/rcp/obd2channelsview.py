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
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.switch import Switch
from kivy.app import Builder
from iconbutton import IconButton
from settingsview import SettingsSwitch
from autosportlabs.racecapture.views.configuration.baseconfigview import BaseConfigView
from autosportlabs.racecapture.views.configuration.rcp.canchannelsview import CANChannelView
from autosportlabs.uix.layout.sections import SectionBoxLayout
from autosportlabs.racecapture.views.util.alertview import editor_popup
from autosportlabs.racecapture.OBD2.obd2settings import OBD2Settings
from utils import *
from autosportlabs.racecapture.config.rcpconfig import *
from autosportlabs.racecapture.theme.color import ColorScheme
from autosportlabs.widgets.scrollcontainer import ScrollContainer
import copy

OBD2_CHANNEL_CONFIG_VIEW_KV="""
<OBD2ChannelConfigView>
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(5)
        BoxLayout:
            size_hint_y: 0.2
            spacing: dp(5)
            orientation: 'horizontal'
            SectionBoxLayout:
                size_hint_x: 0.2
                FieldLabel:
                    text: 'PID'
                    halign: 'right'
            BoxLayout:
                size_hint_x: 0.8
                spacing: dp(5)
                SectionBoxLayout:
                    orientation: 'horizontal'
                    size_hint_x: 0.6
                    IntegerValueField:
                        id: pid
                SectionBoxLayout:
                    size_hint_x: 0.4
                    FieldLabel:
                        size_hint_x: 0.6
                        text: 'Mode'
                        halign: 'right'
                    IntegerValueField:
                        id: mode
                        size_hint_x: 0.4
            
        HLineSeparator:
                            
        CANChannelConfigView:
            id: can_channel_config
            size_hint_y: 0.8
"""

class OBD2ChannelConfigView(BoxLayout):
    Builder.load_string(OBD2_CHANNEL_CONFIG_VIEW_KV)
    
    def __init__(self, **kwargs):
        super(OBD2ChannelConfigView, self).__init__(**kwargs)

OBD2_CHANNEL_KV="""
<OBD2Channel>:
    spacing: dp(10)
    size_hint_y: None
    height: dp(30)
    orientation: 'horizontal'
    ChannelNameSelectorView:
        size_hint_x: 0.5
        id: chan_id
    SampleRateSpinner:
        size_hint_x: 0.3
        id: sr
    IconButton:
        size_hint_x: 0.1    
        text: u'\uf044'
        on_release: root.on_customize()        
    IconButton:
        size_hint_x: 0.1
        text: '\357\200\224'
        on_release: root.on_delete()
"""

class OBD2Channel(BoxLayout):
    channel = None
    obd2_settings = None
    max_sample_rate = 0
    pidIndex = 0
    Builder.load_string(OBD2_CHANNEL_KV)
    
    def __init__(self, obd2_settings, max_sample_rate, **kwargs):
        super(OBD2Channel, self).__init__(**kwargs)
        self.obd2_settings = obd2_settings
        self.max_sample_rate = max_sample_rate
        self.register_event_type('on_delete_pid')
        self.register_event_type('on_modified')

    def on_channel(self, instance):
        if self.channel:
            # copy in the extended PID and CAN mapping
            obd2_channel = self.obd2_settings.obd2channelInfo.get(self.channel.name)
            self.channel.pid = obd2_channel.pid
            self.channel.mode = obd2_channel.mode
            self.channel.mapping = copy.deepcopy(obd2_channel.mapping)
            self.channel.stale = True
            self.dispatch('on_modified')

    def on_modified(self):
        pass

    def on_sample_rate(self, instance, value):
        if self.channel:
            self.channel.sampleRate = instance.getValueFromKey(value)
            self.dispatch('on_modified')

    def on_delete_pid(self, pid):
        pass

    def on_delete(self):
        self.dispatch('on_delete_pid', self.pidIndex)

    def on_customize(self):
        content = OBD2ChannelConfigView()

        def _on_answer(instance, answer):
            if answer:
                self.dispatch('on_modified')
            popup.dismiss()
        
        popup = editor_popup('Customize OBDII mapping', content, _on_answer, size_hint=(0.7, 0.7))
        
        # TODO remove channels, no longer needed
        # remove PID index
    def set_channel(self, pidIndex, channel, channels):
        self.channel = channel
        sample_rate_spinner = self.ids.sr
        sample_rate_spinner.set_max_rate(self.max_sample_rate)
        sample_rate_spinner.setFromValue(channel.sampleRate)
        sample_rate_spinner.bind(text=self.on_sample_rate)
        
        channel_editor = self.ids.chan_id
        channel_editor.filter_list = self.obd2_settings.getChannelNames()
        channel_editor.on_channels_updated(channels)
        channel_editor.setValue(channel)
        channel_editor.bind(on_channel=self.on_channel)

OBD2_CHANNELS_VIEW_KV = """
<OBD2ChannelsView>:
    spacing: dp(20)
    orientation: 'vertical'
    SettingsView:
        id: obd2enable
        label_text: 'OBDII channels'
        help_text: 'Specify one or more OBDII Channels to enable'
        size_hint_y: 0.20
    BoxLayout:
        size_hint_y: 0.70
        #spacing: dp(5)
        orientation: 'vertical'        
        HSeparator:
            text: 'OBDII Channels'
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: 0.15
            spacing: dp(5)
            HSeparatorMinor:
                text: 'Channel'
                size_hint_x: 0.3            
            HSeparatorMinor:
                text: 'Logging Rate'
                size_hint_x: 0.3
        AnchorLayout:                
            AnchorLayout:
                ScrollContainer:
                    canvas.before:
                        Color:
                            rgba: 0.05, 0.05, 0.05, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size                
                    id: scrlobd2
                    size_hint_y: 0.95
                    do_scroll_x:False
                    do_scroll_y:True
                    GridLayout:
                        id: obd2grid
                        padding: [dp(20), dp(20)]
                        spacing: [dp(10), dp(10)]
                        size_hint_y: None
                        height: max(self.minimum_height, scrlobd2.height)
                        cols: 1
            AnchorLayout:
                anchor_y: 'bottom'
                IconButton:
                    size_hint: (None, None)
                    height: root.height * .12
                    text: u'\uf055'
                    color: ColorScheme.get_accent()
                    on_release: root.on_add_obd2_channel()
                    disabled: True
                    id: addpid"""

class OBD2ChannelsView(BaseConfigView):
    DEFAULT_OBD2_SAMPLE_RATE = 1
    obd2_cfg = None
    max_sample_rate = 0
    obd2_grid = None
    obd2_settings = None
    base_dir = None
    Builder.load_string(OBD2_CHANNELS_VIEW_KV)

    def __init__(self, **kwargs):
        super(OBD2ChannelsView, self).__init__(**kwargs)
        self.register_event_type('on_config_updated')
        self.obd2_grid = self.ids.obd2grid
        obd2_enable = self.ids.obd2enable
        obd2_enable.bind(on_setting=self.on_obd2_enabled)
        obd2_enable.setControl(SettingsSwitch())
        self.base_dir = kwargs.get('base_dir')

        self.obd2_settings = OBD2Settings(base_dir=self.base_dir)

        self.update_view_enabled()

    def on_modified(self, *args):
        if self.obd2_cfg:
            self.obd2_cfg.stale = True
            self.dispatch('on_config_modified', *args)

    def on_obd2_enabled(self, instance, value):
        if self.obd2_cfg:
            self.obd2_cfg.enabled = value
            self.dispatch('on_modified')

    def on_config_updated(self, rc_cfg):
        obd2_cfg = rc_cfg.obd2Config
        max_sample_rate = rc_cfg.capabilities.sample_rates.sensor
        self.ids.obd2enable.setValue(obd2_cfg.enabled)

        self.obd2_grid.clear_widgets()
        self.reload_obd2_channel_grid(obd2_cfg, max_sample_rate)
        self.obd2_cfg = obd2_cfg
        self.max_sample_rate = max_sample_rate
        self.update_view_enabled()

    def update_view_enabled(self):
        add_disabled = True
        if self.obd2_cfg:
            if len(self.obd2_cfg.pids) < OBD2_CONFIG_MAX_PIDS:
                add_disabled = False

        self.ids.addpid.disabled = add_disabled

    def reload_obd2_channel_grid(self, obd2_cfg, max_sample_rate):
        self.obd2_grid.clear_widgets()

        for i in range(len(obd2_cfg.pids)):
            pidConfig = obd2_cfg.pids[i]
            self.add_obd2_channel(i, pidConfig, max_sample_rate)

        self.update_view_enabled()

    def on_delete_pid(self, instance, pidIndex):
        del self.obd2_cfg.pids[pidIndex]
        self.reload_obd2_channel_grid(self.obd2_cfg, self.max_sample_rate)
        self.dispatch('on_modified')

    def add_obd2_channel(self, index, pidConfig, max_sample_rate):
        channel = OBD2Channel(obd2_settings=self.obd2_settings, max_sample_rate=max_sample_rate)
        channel.bind(on_delete_pid=self.on_delete_pid)
        channel.set_channel(index, pidConfig, self.channels)
        channel.bind(on_modified=self.on_modified)
        self.obd2_grid.add_widget(channel)

    def on_add_obd2_channel(self):
        if (self.obd2_cfg):
            pidConfig = PidConfig()
            pidConfig.sampleRate = self.DEFAULT_OBD2_SAMPLE_RATE
            self.obd2_cfg.pids.append(pidConfig)
            self.add_obd2_channel(len(self.obd2_cfg.pids) - 1, pidConfig, self.max_sample_rate)
            self.update_view_enabled()
            self.dispatch('on_modified')
