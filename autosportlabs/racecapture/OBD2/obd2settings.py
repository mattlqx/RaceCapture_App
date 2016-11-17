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

import os
import json

class OBD2Settings(object):
    obd2channelInfo = {}
    base_dir = None
    def __init__(self, base_dir=None, **kwargs):
        super(OBD2Settings, self).__init__(**kwargs)
        self.base_dir = base_dir
        self.loadOBD2Channels()
        
        
    def getPidForChannelName(self, name):
        pid = 0
        obd2Channel = self.obd2channelInfo.get(name)
        if obd2Channel:
            pid = int(obd2Channel['pid'])
        return pid
    
    def getChannelNames(self):
        return self.obd2channelInfo.keys()
    
    def loadOBD2Channels(self):
        try:
            obd2_json = open(os.path.join(self.base_dir, 'resource', 'settings', 'obd2_channels.json'))
            obd2channels = json.load(obd2_json)
            obd2channels = obd2channels['obd2Channels']
            
            for name in obd2channels:
                self.obd2channelInfo[name] = obd2channels[name]
        except Exception as detail:
            print('Error loading obd2 channel info ' + str(detail))
