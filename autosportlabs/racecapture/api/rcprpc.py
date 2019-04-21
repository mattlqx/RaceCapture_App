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

class RaceCaptureRPC(object):
    def __init__(self, app):
        self.app = app

    def list_active_channels(self):
        return [c.name for name, c in self.app.settings.runtimeChannels.get_active_channels().items()]

    def get_active_channels(self):
        return [c.toJson() for name, c in self.app.settings.runtimeChannels.get_active_channels().items()]

    def get_channel_meta(self, channel):
        return self.app.settings.runtimeChannels.findChannelMeta(channel).toJson()

    def get_channel_value(self, channel):
        return self.app.settings.runtimeChannels.data_bus.getData(channel)

    def get_channel_values(self):
        return self.app.settings.runtimeChannels.data_bus.channel_data
