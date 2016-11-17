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
from kivy.uix.spinner import Spinner
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.app import Builder
from utils import *
from autosportlabs.racecapture.views.configuration.baseconfigview import BaseMultiChannelConfigView, BaseChannelView
from autosportlabs.racecapture.config.rcpconfig import *
from mappedspinner import MappedSpinner
from kivy.metrics import sp

GPIO_CHANNELS_VIEW_KV = 'autosportlabs/racecapture/views/configuration/rcp/gpiochannelsview.kv'


class GPIOChannelsView(BaseMultiChannelConfigView):
    Builder.load_file(GPIO_CHANNELS_VIEW_KV)

    def __init__(self, **kwargs):
        super(GPIOChannelsView, self).__init__(**kwargs)
        self.channel_title = 'Digital Input/Output '
        self.accordion_item_height = sp(120)

    def channel_builder(self, index, max_sample_rate):
        editor = GPIOChannel(id = 'gpio' + str(index), channels=self.channels)
        editor.bind(on_modified = self.on_modified)
        if self.config:
            editor.on_config_updated(self.config.channels[index], max_sample_rate)
        return editor
    
    def get_specific_config(self, rcp_cfg):
        return rcp_cfg.gpioConfig
    
class GPIOModeSpinner(MappedSpinner):
    def __init__(self, **kwargs):
        super(GPIOModeSpinner, self).__init__(**kwargs)
        self.setValueMap({0:'Input', 1:'Output'}, 'Input')
        
class GPIOChannel(BaseChannelView):
    def __init__(self, **kwargs):
        super(GPIOChannel, self).__init__(**kwargs)
                    
    def on_mode(self, instance, value):
        if self.channelConfig:
            self.channelConfig.mode = instance.getValueFromKey(value)
            self.channelConfig.stale = True
            self.dispatch('on_modified', self.channelConfig)
            
    def on_config_updated(self, channelConfig, max_sample_rate):
        self.ids.sr.setValue(channelConfig.sampleRate, max_sample_rate)

        self.ids.chan_id.setValue(channelConfig)
        self.ids.mode.setFromValue(channelConfig.mode)
        self.channelConfig = channelConfig
