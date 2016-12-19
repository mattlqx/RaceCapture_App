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
from kivy.properties import StringProperty, NumericProperty
from autosportlabs.racecapture.views.analysis.analysispage import AnalysisPage
from kivy.base import Builder
from fieldlabel import FieldLabel

LAP_STATS_ITEM_KV = """
<LapStatsItem>:
    FieldLabel:
        id: lap_session
        text: root.lap_session
    FieldLabel:
        id: lap_time
        #text: root.lap_time
    FieldLabel:
        id: lap_number
        text: root.lap_number
"""

class LapStatsItem(BoxLayout):
    Builder.load_string(LAP_STATS_ITEM_KV)
    lap_session = StringProperty()
    lap_time = StringProperty()
    lap_number = StringProperty()

CHANNEL_STATS_KV = """
<ChannelStats>:
    ScrollContainer:
        id: scroll
        size_hint_y: 1.0
        do_scroll_x:False
        do_scroll_y:True
        GridLayout:
            id: grid
            padding: (dp(10), dp(10))
            spacing: dp(10)
            row_default_height: root.height * 0.3
            size_hint_y: None
            height: self.minimum_height
            cols: 1        
"""
class ChannelStats(AnalysisPage):
    Builder.load_string(CHANNEL_STATS_KV)
    
    def __init__(self, **kwargs):
        super(ChannelStats, self).__init__(**kwargs)
        self._laps = {}
        
    def add_lap(self, source_ref):
        print('add lap {}'.format(source_ref))
        lap = LapStatsItem()
#        lap.lap_number = str(source_ref)
        #lap.lap_session = str('{} -- {}'.format(source_ref.lap, source_ref.session))
        lap.lap_time = str('123')
        self.ids.grid.add_widget(lap)
        
        session = self.datastore.get_session_by_id(source_ref.session)
        lap.lap_session = session.name
        lap.lap_number = str(source_ref.lap)
        

    def remove_lap(self, source_ref):
        print('remove lap {}'.format(source_ref))

    
    