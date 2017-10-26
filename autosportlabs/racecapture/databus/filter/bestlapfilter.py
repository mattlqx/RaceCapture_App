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


class BestLapFilter(object):
    """Update BestLap if laptime is present and is faster than the current best"""
    BEST_LAPTIME_KEY = 'BestLap'
    LAPTIME_KEY = 'LapTime'
    best_laptime = 0
    best_laptime_meta = None
    def __init__(self, system_channels):
        self.best_laptime_meta = system_channels.findChannelMeta(BestLapFilter.BEST_LAPTIME_KEY)
        
    def get_channel_meta(self, channel_meta):
        metas = {}
        if channel_meta.get(self.LAPTIME_KEY):
            metas[BestLapFilter.BEST_LAPTIME_KEY] = self.best_laptime_meta
        return metas
    
    def reset(self):
        self.best_laptime = 0
         
    def filter(self, channel_data):
        laptime = channel_data.get(self.LAPTIME_KEY)
        if laptime is not None and laptime > 0:
            current_best_laptime = self.best_laptime
            if current_best_laptime == 0 or laptime < current_best_laptime: 
                current_best_laptime = laptime
                channel_data[self.BEST_LAPTIME_KEY] = current_best_laptime
                self.best_laptime = current_best_laptime
