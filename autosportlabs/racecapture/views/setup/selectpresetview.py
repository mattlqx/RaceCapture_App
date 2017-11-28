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
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.app import Builder
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from fieldlabel import FieldLabel
from kivy.uix.screenmanager import Screen
from autosportlabs.racecapture.views.setup.infoview import InfoView
from autosportlabs.uix.button.betterbutton import BetterToggleButton
from kivy.properties import ObjectProperty, StringProperty
from autosportlabs.racecapture.presets.presetview import PresetItemView
from autosportlabs.racecapture.views.util.alertview import okPopup

class SelectPresetView(InfoView):
    """
    A setup screen that lets users select what device they have.
    """
    Builder.load_string("""
<SelectPresetView>:
    background_source: 'resource/setup/background_blank.png'
    info_text: 'Select a preset'
    BoxLayout:
        orientation: 'vertical'
        padding: [0, dp(20)]
        spacing: [0, dp(10)]
        BoxLayout:
            size_hint_y: 0.10
        ScrollContainer:
            size_hint_y: 0.7
            do_scroll_x: False
            do_scroll_y: True
            size_hint_y: 1
            size_hint_x: 1
            GridLayout:
                id: presets
                spacing: [0, dp(10)]
                row_default_height: dp(130)
                size_hint_y: None
                height: self.minimum_height
                cols: 1
        BoxLayout:
            size_hint_y: 0.15    
    """)

    def __init__(self, **kwargs):
        super(SelectPresetView, self).__init__(**kwargs)
        self.ids.next.disabled = True
        self.ids.next.pulsing = False

    def on_setup_config(self, instance, value):
        self._update_ui()

    def _update_ui(self):
        self.ids.presets.clear_widgets()
        for k, v in self.preset_manager.get_presets_by_type('PC_MK1'):
            name = v.name
            notes = v.notes
            self.add_preset(k, v)

    def add_preset(self, key, preset):
        view = PresetItemView(preset_id=preset.mapping_id,
                                                   name=preset.name,
                                                   notes=preset.notes,
                                                   image_path=preset.local_image_path)
        view.bind(on_preset_selected=self._preset_selected)
        self.ids.presets.add_widget(view)

    def _preset_selected(self, instance, preset_id):
        def write_win(details):
            msg.text = 'Success: {}'.format(preset.name)
            Clock.schedule_once(lambda dt: progress_view.dismiss(), 2.0)
            self.ids.next.disabled = False

        def write_fail(details):
            progress_view.dismiss()
            okPopup('Oops!',
                         'We had a problem applying the preset. Check the device connection and try again.\n\nError:\n\n{}'.format(details),
                         lambda *args: None)
        progress_view = ModalView(size_hint=(None, None), size=(600, 200))
        msg = FieldLabel(halign='center', text='Applying Preset...')

        progress_view.add_widget(msg)
        progress_view.open()
        preset = self.preset_manager.get_preset_by_id(preset_id)
        self.rc_config.fromJson(preset.mapping)
        self.rc_config.stale = True
        self.rc_api.writeRcpCfg(self.rc_config, write_win, write_fail)

    def _select_preset(self, preset):
        self.ids.next.disabled = False


