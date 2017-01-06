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
from autosportlabs.racecapture.theme.color import ColorScheme
from kivy.base import Builder
from fieldlabel import FieldLabel
from utils import kvFindClass

class StatsFieldLabel(FieldLabel):
    alert_color = ObjectProperty(ColorScheme.get_shadow())
    Builder.load_string("""
<StatsFieldLabel>:
    canvas.before:
        Color:
            rgba: root.alert_color
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
            id: min_field
            alert_color: root.min_alert_color
        StatsFieldLabel:
            id: avg_field
            alert_color: root.avg_alert_color
        StatsFieldLabel:
            id: max_field
            alert_color: root.max_alert_color
""")
    source_ref = ObjectProperty()
    min_value = NumericProperty()
    avg_value = NumericProperty()
    max_value = NumericProperty()

    min_alert_color = ObjectProperty(ColorScheme.get_shadow())
    avg_alert_color = ObjectProperty(ColorScheme.get_shadow())
    max_alert_color = ObjectProperty(ColorScheme.get_shadow())

    def on_min_value(self, instance, value):
        self.ids.min_field.text = str(value)
        
    def on_avg_value(self, instance, value):
        self.ids.avg_field.text = str(value)
        
    def on_max_value(self, instance, value):
        self.ids.max_field.text = str(value)
        
class RangeTracker():
    min_value = None
    max_value = None
    min_widget = None
    max_widget = None
    
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
        self._update_alert_colors()
    
    def remove_widget(self, widget):
        super(ChannelStatsSlice, self).remove_widget(widget)
        self._update_alert_colors()
        
    def _update_alert_colors(self):
        min_values = {}
        avg_values = {}
        max_values = {}
        stats_children = list(kvFindClass(self, CurrentLapChannelStats))        
        for c in stats_children:
            min_values[c.min_value] = c
            avg_values[c.avg_value] = c
            max_values[c.max_value] = c
            
        sorted_min_values = sorted(min_values)
        sorted_avg_values = sorted(avg_values)
        sorted_max_values = sorted(max_values)
        
        for k in sorted_min_values:
            min_values[k].min_alert_color = ColorScheme.get_shadow()
        if len(sorted_min_values) > 1:
            try:
                min_min = sorted_min_values[0]
                min_values[min_min].min_alert_color = [0, 0.3, 0, 1]
            except IndexError:
                pass
                
            try:
                max_min = sorted_min_values[-1]
                min_values[max_min].min_alert_color = [0.3, 0, 0, 1]
            except IndexError:
                pass

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
            channel_stats = self._build_current_lap_channel_stats(source_ref, channel_slice.channel)
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

    def _build_current_lap_channel_stats(self, source_ref, channel):
        channel_stats = CurrentLapChannelStats()
        channel_stats.source_ref = source_ref
        session = source_ref.session
        lap = source_ref.lap
        min_value = self.datastore.get_channel_min(channel, laps=[lap], sessions=[session])
        channel_stats.min_value = min_value

        max_value = self.datastore.get_channel_max(channel, laps=[lap], sessions=[session])
        channel_stats.max_value = max_value

        avg_value = self.datastore.get_channel_average(channel, laps=[lap], sessions=[session])
        channel_stats.avg_value = avg_value
        return channel_stats

    def _add_channel_stats(self, channel):
        channel_slice = ChannelStatsSlice(channel=channel)
        header = LapChannelHeader()
        header.name = channel
        channel_slice.add_widget(header)
        lap_stats = list(kvFindClass(self.ids.grid, LapStatsItem))
        for item in lap_stats:
            channel_stats = self._build_current_lap_channel_stats(item.source_ref, channel)
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
