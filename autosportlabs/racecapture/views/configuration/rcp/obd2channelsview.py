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
from kivy.uix.boxlayout import BoxLayout
from kivy.app import Builder
from iconbutton import IconButton
from settingsview import SettingsSwitch
from autosportlabs.racecapture.views.configuration.baseconfigview import BaseConfigView
from autosportlabs.racecapture.views.configuration.rcp.canmappingview import CANChannelConfigView, CANChannelMappingTab, CANFilters
from autosportlabs.uix.layout.sections import SectionBoxLayout
from autosportlabs.racecapture.views.util.alertview import editor_popup, confirmPopup
from autosportlabs.racecapture.OBD2.obd2settings import OBD2Settings
from utils import *
from autosportlabs.racecapture.config.rcpconfig import *
from autosportlabs.racecapture.theme.color import ColorScheme
from autosportlabs.widgets.scrollcontainer import ScrollContainer
import copy

class PIDConfigTab(CANChannelMappingTab):
    PID_RANGES = (0, 256)
    SUPPORTED_MODES = {1:'01h', 9: '09h', 34:'22h'}
    DEFAULT_MODE = '01h'

    Builder.load_string("""
<PIDConfigTab>:
    text: 'OBDII PID'
    BoxLayout:
        AnchorLayout:
            BoxLayout:
                spacing: dp(10)
                orientation: 'vertical'
                SectionBoxLayout:
                    FieldLabel:
                        text: 'OBDII PID'
                        halign: 'right'
                    LargeMappedSpinner:
                        id: pid
                        on_text: root.on_pid(*args)
                
                SectionBoxLayout:
                    FieldLabel:
                        text: 'Mode'
                        halign: 'right'
                        id: mode
                    LargeMappedSpinner:
                        id: mode
                        on_text: root.on_mode(*args)
        
        SectionBoxLayout:
            orientation: 'horizontal'
            FieldLabel:
                size_hint_x: 0.7
                text: 'Passive Mode'
                halign: 'right'
            CheckBox:
                id: passive
                size_hint_x: 0.3                
                on_active: root.on_passive(*args)
    """)

    def __init__(self, **kwargs):
        super(PIDConfigTab, self).__init__(**kwargs)
        self._loaded = False

    def init_view(self, channel_cfg):
        self._loaded = False
        self.channel_cfg = channel_cfg

        pids = {}
        for i in range(PIDConfigTab.PID_RANGES[0], PIDConfigTab.PID_RANGES[1]):
            pids[i] = str(i)
        self.ids.pid.setValueMap(pids, str(PIDConfigTab.PID_RANGES[0]))

        self.ids.mode.setValueMap(PIDConfigTab.SUPPORTED_MODES, PIDConfigTab.DEFAULT_MODE)
        self.ids.mode.setFromValue(channel_cfg.mode)
        self.ids.pid.setFromValue(channel_cfg.pid)
        self.ids.passive.active = channel_cfg.passive
        self._loaded = True

    def on_pid(self, instance, value):
        if self._loaded:
            self.channel_cfg.pid = instance.getValueFromKey(value)

    def on_mode(self, instance, value):
        if self._loaded:
            self.channel_cfg.mode = instance.getValueFromKey(value)

    def on_passive(self, instance, value):
        if self._loaded:
            self.channel_cfg.passive = instance.active

class OBD2ChannelConfigView(CANChannelConfigView):
    def __init__(self, obd2_settings, **kwargs):
        self.obd2_settings = obd2_settings
        self.pid_config_tab = PIDConfigTab()
        super(OBD2ChannelConfigView, self).__init__(**kwargs)
        self.can_channel_customization_tab.set_channel_filter_list(obd2_settings.getChannelNames())
        self.can_channel_customization_tab.bind(on_channel=self.on_channel_selected)

    def on_channel_selected(self, instance, channel_cfg):
        obd2_preset = self.obd2_settings.obd2channelInfo.get(channel_cfg.name)
        if obd2_preset is None:
            return

        channel_cfg.__dict__.update(obd2_preset.__dict__)

        self.load_tabs()

    def init_tabs(self):
        self.ids.tabs.add_widget(self.can_channel_customization_tab)
        self.ids.tabs.add_widget(self.pid_config_tab)
        self.ids.tabs.add_widget(self.can_id_tab)
        self.ids.tabs.add_widget(self.can_value_map_tab)
        self.ids.tabs.add_widget(self.can_formula_tab)

    def load_tabs(self):
        super(OBD2ChannelConfigView, self).load_tabs()
        self.pid_config_tab.init_view(self.channel_cfg) 

class OBD2Channel(BoxLayout):
    channel = None
    obd2_settings = None
    max_sample_rate = 0
    channel_index = 0
    Builder.load_string("""
<OBD2Channel>:
    size_hint_y: None
    height: dp(30)
    orientation: 'horizontal'
    FieldLabel:
        size_hint_x: 0.5
        id: name
    FieldLabel:
        size_hint_x: 0.3
        id: sample_rate
    IconButton:
        size_hint_x: 0.1    
        text: u'\uf044'
        on_release: root.on_edit()        
    IconButton:
        size_hint_x: 0.1
        text: '\357\200\224'
        on_release: root.on_delete()
""")

    def __init__(self, obd2_settings, max_sample_rate, can_filters, channels, **kwargs):
        super(OBD2Channel, self).__init__(**kwargs)
        self.obd2_settings = obd2_settings
        self.max_sample_rate = max_sample_rate
        self.can_filters = can_filters
        self.channels = channels
        self.register_event_type('on_delete_obd2_channel')
        self.register_event_type('on_modified')
        self.register_event_type('on_edit_channel')

    def on_delete_obd2_channel(self, pid):
        pass

    def on_modified(self):
        pass

    def on_delete(self):
        self.dispatch('on_delete_obd2_channel', self.channel_index)

    def on_edit_channel(self, channel_index):
        pass

    def on_edit(self):
        self.dispatch('on_edit_channel', self.channel_index)

    def set_channel(self, channel_index, channel):
        self.channel_index = channel_index
        self.channel = channel
        self.refresh()

    def refresh(self):
        self.ids.name.text = self.channel.name
        self.ids.sample_rate.text = '{} Hz'.format(self.channel.sampleRate)
 
class OBD2ChannelsView(BaseConfigView):
    DEFAULT_OBD2_SAMPLE_RATE = 1
    obd2_cfg = None
    max_sample_rate = 0
    obd2_grid = None
    obd2_settings = None
    Builder.load_string("""
<OBD2ChannelsView>:
    spacing: dp(20)
    orientation: 'vertical'
    SettingsView:
        id: obd2enable
        label_text: 'OBDII channels'
        help_text: ''
        size_hint_y: 0.15
    BoxLayout:
        size_hint_y: 0.85
        orientation: 'vertical'        
        HSeparator:
            text: 'OBDII Channels'
        BoxLayout:
            orientation: 'horizontal'
            padding: [dp(5), dp(0)]
            size_hint_y: 0.1
            FieldLabel:
                text: 'Channel'
                size_hint_x: 0.5                
            FieldLabel:
                text: 'Rate'
                size_hint_x: 0.3
            BoxLayout:
                size_hint_x: 0.2
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
                        padding: [dp(5), dp(5)]
                        spacing: [dp(0), dp(10)]
                        size_hint_y: None
                        height: max(self.minimum_height, scrlobd2.height)
                        cols: 1
                FieldLabel:
                    halign: 'center'
                    id: list_msg
                    text: ''                                    
            AnchorLayout:
                anchor_y: 'bottom'
                IconButton:
                    size_hint: (None, None)
                    height: root.height * .12
                    text: u'\uf055'
                    color: ColorScheme.get_accent()
                    on_release: root.on_add_obd2_channel()
                    disabled: True
                    id: addpid
""")

    def __init__(self, **kwargs):
        super(OBD2ChannelsView, self).__init__(**kwargs)
        self.register_event_type('on_config_updated')
        self.obd2_grid = self.ids.obd2grid
        obd2_enable = self.ids.obd2enable
        obd2_enable.bind(on_setting=self.on_obd2_enabled)
        obd2_enable.setControl(SettingsSwitch())
        base_dir = kwargs.get('base_dir')

        self.obd2_settings = OBD2Settings(base_dir=base_dir)
        self.can_filters = CANFilters(base_dir)

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
        self.max_sample_rate = max_sample_rate
        self.obd2_cfg = obd2_cfg
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
            pid_config = obd2_cfg.pids[i]
            self.add_obd2_channel(i, pid_config, max_sample_rate)

        self.update_view_enabled()
        self._refresh_channel_list_notice(obd2_cfg)

    def _delete_obdii_channel(self, channel_index):
        del self.obd2_cfg.pids[channel_index]
        self.reload_obd2_channel_grid(self.obd2_cfg, self.max_sample_rate)
        self.dispatch('on_modified')

    def on_delete_obd2_channel(self, instance, channel_index):
        popup = None
        def _on_answer(instance, answer):
            if answer:
                self._delete_obdii_channel(channel_index)
            popup.dismiss()
        popup = confirmPopup('Confirm', 'Delete OBDII Channel?', _on_answer)


    def _replace_config(self, to_cfg, from_cfg):
        to_cfg.__dict__.update(from_cfg.__dict__)

    def _on_edit_channel(self, instance, channel_index):
        self._edit_channel(channel_index, False)

    def _edit_channel(self, channel_index, is_new):
        channel = self.obd2_cfg.pids[channel_index]
        working_channel_cfg = copy.deepcopy(channel)
        content = OBD2ChannelConfigView(self.obd2_settings)
        content.init_config(channel_index, working_channel_cfg, self.can_filters, self.max_sample_rate, self.channels)

        def _on_answer(instance, answer):
            if answer:
                self._replace_config(channel, working_channel_cfg)
                self.dispatch('on_modified')
                self.reload_obd2_channel_grid(self.obd2_cfg, self.max_sample_rate)
            popup.dismiss()

        title = 'Add OBDII channel' if is_new else 'Edit OBDII channel'
        popup = editor_popup(title, content, _on_answer, size=(dp(500), dp(300)))

    def add_obd2_channel(self, index, pid_config, max_sample_rate):
        channel = OBD2Channel(obd2_settings=self.obd2_settings, max_sample_rate=max_sample_rate, can_filters=self.can_filters, channels=self.channels)
        channel.bind(on_delete_obd2_channel=self.on_delete_obd2_channel)
        channel.bind(on_edit_channel=self._on_edit_channel)
        channel.set_channel(index, pid_config)
        channel.bind(on_modified=self.on_modified)
        self.obd2_grid.add_widget(channel)

    def on_add_obd2_channel(self):
        if (self.obd2_cfg):
            pid_config = PidConfig()
            pid_config.sampleRate = self.DEFAULT_OBD2_SAMPLE_RATE
            self.obd2_cfg.pids.append(pid_config)
            channel_index = len(self.obd2_cfg.pids) - 1
            self.add_obd2_channel(channel_index, pid_config, self.max_sample_rate)
            self.update_view_enabled()
            self.dispatch('on_modified')
            self._edit_channel(channel_index, True)

    def _refresh_channel_list_notice(self, obd2_cfg):
        channel_count = len(obd2_cfg.pids)
        self.ids.list_msg.text = 'Press (+) to add an OBDII channel' if channel_count == 0 else ''
