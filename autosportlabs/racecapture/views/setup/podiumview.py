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
from kivy.clock import Clock
from kivy.app import Builder
from kivy.uix.screenmanager import Screen
from autosportlabs.racecapture.views.setup.infoview import InfoView
import webbrowser
from utils import is_mobile_platform

PODIUM_SETUP_VIEW_KV = """
<PodiumSetupView>:
    background_source: 'resource/setup/background_podium.jpg'
    info_text: 'You can live-stream telemetry to Podium for realtime data to the pits, friends or race coaches around the world.\\nGo to [color=00BCD4][ref=podium]podium.live[/ref][/color] to get started!'
"""

class PodiumSetupView(InfoView):
    """
    Provides information on Dashboard features, and optionally configure specific options
    """
    Builder.load_string(PODIUM_SETUP_VIEW_KV)
    def __init__(self, **kwargs):
        super(PodiumSetupView, self).__init__(**kwargs)

    def on_info_ref(self, instance, value):
        print ('ref')
        if value == 'podium' and is_mobile_platform():
            webbrowser.open('http://podium.live')
