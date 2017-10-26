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

import os
import json
from autosportlabs.racecapture.config.rcpconfig import PidConfig

class OBD2Settings(object):
    obd2channelInfo = {}
    base_dir = None
    def __init__(self, base_dir=None, **kwargs):
        super(OBD2Settings, self).__init__(**kwargs)
        self.base_dir = base_dir
        self.loadOBD2Channels()
            
    def getChannelNames(self):
        return self.obd2channelInfo.keys()
    
    def loadOBD2Channels(self):
        obd2_json = open(os.path.join(self.base_dir, 'resource', 'settings', 'obd2_channels.json'))
        obd2channels = json.load(obd2_json)
        obd2channels = obd2channels['obd2Channels']
        for c in obd2channels:
            obd2channel = PidConfig()
            obd2channel.fromJson(c)
            self.obd2channelInfo[obd2channel.name] = obd2channel
