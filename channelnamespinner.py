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
from kivy.uix.spinner import Spinner

class ChannelNameSpinner(Spinner):
    channelType = None
    filterList = None
    def __init__(self, **kwargs):
        super(ChannelNameSpinner, self).__init__(**kwargs)
        self.register_event_type('on_channels_updated')
        self.values = []
     
    def on_channels_updated(self, runtime_channels):
        channel_names = runtime_channels.channel_names
        filtered_channel_names = channel_names
        if self.filterList != None:
            filtered_channel_names = []
            filter_list = self.filterList
            for channel in channel_names:
                if channel in filter_list:
                    filtered_channel_names.append(channel)
                    
        self.values = filtered_channel_names
