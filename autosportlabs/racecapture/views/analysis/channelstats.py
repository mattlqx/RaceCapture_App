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
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from autosportlabs.racecapture.views.analysis.analysispage import AnalysisPage
from autosportlabs.racecapture.views.util.viewutils import format_laptime
from kivy.base import Builder
from fieldlabel import FieldLabel
from utils import kvFindClass

class StatsFieldLabel(FieldLabel):
    Builder.load_string("""
<StatsFieldLabel>:
    canvas.before:
        Color:
            rgba: ColorScheme.get_shadow()
        Rectangle:
            pos: self.pos
            size: self.size
    
    """)

class LapStatsItem(BoxLayout):
    Builder.load_string("""
<LapStatsItem>:
#    size_hint_y: None
#    height: dp(30)
    FieldLabel:
        id: lap_session
        size_hint_x: 0.6
        text: root.lap_session
    FieldLabel:
        id: lap_number
        size_hint_x: 0.1
        text: root.lap_number
    FieldLabel:
        id: lap_time
        size_hint_x: 0.3
        text: root.lap_time    
""")
    lap_session = StringProperty()
    lap_time = StringProperty()
    lap_number = StringProperty()
    source_ref = ObjectProperty()


class LapChannelHeader(BoxLayout):
    Builder.load_string("""
<LapChannelHeader>:
    FieldLabel:
        text: root.name
        halign: 'center'
""")
    name = StringProperty()

class CurrentLapChannelStats(BoxLayout):
    Builder.load_string("""
<CurrentLapChannelStats>:
    BoxLayout:
        padding: (dp(3), dp(1), dp(3), dp(1))
        StatsFieldLabel:
            id: min
            text: root.min_value
        StatsFieldLabel:
            id: current
            text: root.current_value
        StatsFieldLabel:
            id: max
            text: root.max_value
""")
    source_ref = ObjectProperty()
    min_value = StringProperty()
    current_value = StringProperty()
    max_value = StringProperty()

class ChannelStatsSlice(BoxLayout):
    Builder.load_string("""
<ChannelStatsSlice>:
    orientation: 'vertical'
    size_hint_x: None
    width: dp(200)
   # size_hint_y: None
    #height: len(self.children) * dp(20) 
""")
    channel = StringProperty()

    def add_widget(self, widget, index=0):
        super(ChannelStatsSlice, self).add_widget(widget, index=index)

CHANNEL_STATS_KV = """
<ChannelStats>:
    BoxLayout:
        orientation: 'vertical'                
        ScrollContainer:
            id: scroll
            size_hint_y: 1.0
            do_scroll_x:False
            do_scroll_y:True
            GridLayout:
                cols: 2
                size_hint_y: None
                size_hint_x: 1.0
                height: self.minimum_height
                width: self.minimum_width
                GridLayout:
                    id: grid
                    #padding: (dp(10), dp(10))
                    #spacing: dp(10)
                    row_default_height: dp(30) #root.height * 0.3
                    size_hint_y: None
                    size_hint_x: 0.3
                    height: self.minimum_height
                    cols: 1
                    FieldLabel:
                        text: 'Selected Laps'
                    
                ScrollContainer:
                    id: scroll_stats
                    size_hint_x: 0.7
                    size_hint_y: 1.0
                    do_scroll_x: True
                    do_scroll_y: False
                    GridLayout:
                        id: grid_stats
                        #row_default_height: dp(30) #root.height * 0.3
                        row_default_width: root.width * 0.3
                        size_hint_y: 1.0
                        size_hint_x: None
                        width: self.minimum_width
                     #   padding: (dp(10), dp(10))
                      #  spacing: dp(10)
                        cols: 1
                        BoxLayout:
                            id: stats
                            orientation: 'horizontal'
                            size_hint_x: None
                            width: len(self.children) * dp(200) 

"""
class ChannelStats(AnalysisPage):
    Builder.load_string(CHANNEL_STATS_KV)

    def __init__(self, **kwargs):
        super(ChannelStats, self).__init__(**kwargs)
        self._channels = []

    def add_lap(self, source_ref):
        lap = LapStatsItem()
#        lap.lap_number = str(source_ref)
        # lap.lap_session = str('{} -- {}'.format(source_ref.lap, source_ref.session))
        lap_info = self.datastore.get_cached_lap_info(source_ref)
        lap.lap_time = format_laptime(lap_info.lap_time)
        self.ids.grid.add_widget(lap)

        session = self.datastore.get_session_by_id(source_ref.session)
        lap.lap_session = session.name
        lap.lap_number = str(source_ref.lap)
        lap.source_ref = source_ref

        self._add_lap_slices(source_ref)

    def _add_lap_slices(self, source_ref):
        for channel_slice in self.ids.stats.children:
            channel_stats = CurrentLapChannelStats()
            channel_stats.source_ref = source_ref
            channel_slice.add_widget(channel_stats)
        
    def remove_lap(self, source_ref):
        channel_slices = list(kvFindClass(self.ids.stats, CurrentLapChannelStats))
        for channel_slice in channel_slices:
            if channel_slice.source_ref == source_ref:
                channel_slice.parent.remove_widget(channel_slice)

        lap_stats = list(kvFindClass(self.ids.grid, LapStatsItem))
        for item in lap_stats:
            if item.source_ref == source_ref:
                item.parent.remove_widget(item)
                            
    def _add_channel_stats(self, channel):
        channel_slice = ChannelStatsSlice(channel=channel)
        header = LapChannelHeader()
        header.name = channel
        channel_slice.add_widget(header)
        lap_stats = list(kvFindClass(self.ids.grid, LapStatsItem))        
        for item in lap_stats:
            channel_stats = CurrentLapChannelStats()
            channel_stats.source_ref = item.source_ref
            channel_stats.min_value = str(0)
            channel_stats.max_value = str(1000)
            channel_stats.current_value = str(333)
            channel_slice.add_widget(channel_stats)
        self.ids.stats.add_widget(channel_slice)
        self._channels.append(channel)

    def _remove_channel_stats(self, channel):
        for c in self.ids.stats.children:
            if c.channel == channel:
                
                self.ids.stats.remove_widget(c)
                break
        self._channels.remove(channel)
        
    def set_selected_channels(self, channels):
        current = self._channels
        removed = [c for c in current if c not in channels]
        added = [c for c in channels if c not in current]

        for c in added:
            self._add_channel_stats(c)
            
        for c in removed:
            self._remove_channel_stats(c)
        