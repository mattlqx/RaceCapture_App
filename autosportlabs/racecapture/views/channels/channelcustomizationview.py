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
from iconbutton import IconButton
from kivy.app import Builder
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from autosportlabs.uix.textwidget import TextWidget
from kivy.uix.slider import Slider
from utils import kvFind
from autosportlabs.racecapture.views.color.colorpickerview import ColorBlock
from autosportlabs.racecapture.settings.prefs import Range
from autosportlabs.racecapture.views.color.colorpickerview import ColorPickerView
from valuefield import FloatValueField
from fieldlabel import FieldLabel


class RangeLabel(FieldLabel):
    Builder.load_string("""
<RangeLabel>:
    font_size: sp(20)    
    """)
    pass

class ChannelCustomizationView(FloatLayout):

    Builder.load_string("""   
<ChannelCustomizationView>:
    BoxLayout:
        size: root.size
        pos: root.pos
        orientation: 'vertical'
        spacing: dp(10)
        ScrollContainer:
            canvas.before:
                Color:
                    rgba: 0.05, 0.05, 0.05, 1
                Rectangle:
                    pos: self.pos
                    size: self.size                
            id: scroller
            size_hint_y: 0.95
            do_scroll_x:False
            do_scroll_y:True
            GridLayout:
                id: scroll_grid
                padding: [dp(5), dp(5)]                        
                spacing: [dp(0), dp(20)]
                size_hint_y: None
                height: max(self.minimum_height, scroller.height)
                cols: 1
                row_default_height: dp(120)
                BoxLayout:
                    size_hint_y: 0.4
                    orientation: 'horizontal'
                    spacing: dp(20)
                    RangeLabel:
                        size_hint_x: 0.15
                        text: 'Warn'
                        halign: 'right'
                    GridLayout:
                        size_hint_x: 0.75
                        cols: 2
                        orientation: 'vertical'
                        RangeLabel:
                            size_hint_x: 0.10
                            text: 'Low'
                            halign: 'right'
                        Slider:
                            size_hint_x: 0.90
                            id: warnLowSlider
                            on_value: root.on_warnLow(*args)
                        RangeLabel:
                            size_hint_x: 0.10
                            text: 'High'
                            halign: 'right'
                        Slider:
                            size_hint_x: 0.90
                            id: warnHighSlider
                            on_value: root.on_warnHigh(*args)
                        Widget:
                            size_hint_x: 0.25
                        BoxLayout:
                            size_hint_x: 0.75
                            size_hint_y: None
                            height: dp(40)
                            orientation: 'horizontal'
                            FloatValueField:
                                id: warnLowValue
                                on_text: root.on_warn_low_field(*args)
                            RangeLabel:
                                halign: 'center'
                                text: '-'
                            FloatValueField:
                                id: warnHighValue
                                on_text: root.on_warn_high_field(*args)
                    ColorBlock:
                        id: selectedWarnColor
                        size_hint_x: 0.15
                        on_press: root.on_warn_color()
                        
                BoxLayout:
                    size_hint_y: 0.4
                    orientation: 'horizontal'
                    spacing: dp(20)
                    RangeLabel:
                        size_hint_x: 0.15
                        text: 'Alert'
                        halign: 'right'
                    GridLayout:
                        size_hint_x: 0.75
                        cols: 2
                        orientation: 'vertical'
                        RangeLabel:
                            size_hint_x: 0.10
                            text: 'Low'
                            halign: 'right'
                        Slider:
                            size_hint_x: 0.90
                            id: alertLowSlider
                            on_value: root.on_alertLow(*args)
                        RangeLabel:
                            size_hint_x: 0.10
                            text: 'High'
                            halign: 'right'
                        Slider:
                            size_hint_x: 0.90
                            id: alertHighSlider
                            on_value: root.on_alertHigh(*args)
        
                        Widget:
                            size_hint_x: 0.25
                        BoxLayout:
                            size_hint_x: 0.75
                            size_hint_y: None
                            height: dp(40)
                            orientation: 'horizontal'
                            FloatValueField:
                                halign: 'right'
                                id: alertLowValue
                                on_text: root.on_alert_low_field(*args)
                            RangeLabel:
                                halign: 'center'
                                text: '-'
                            FloatValueField:
                                input_type: 'number'
                                input_filter: 'int'
                                halign: 'left'
                                id: alertHighValue
                                on_text: root.on_alert_high_field(*args)
                    ColorBlock:
                        id: selectedAlertColor
                        padding: (dp(20), dp(20))
                        size_hint_x: 0.15
                        on_press: root.on_alert_color()
                        
                    
        IconButton:
            size_hint_y: 0.2
            text: "\357\200\214"
            on_press: root.on_close()    
    """)

    _popup = None
    def __init__(self, **kwargs):
        self.settings = None
        self.channel = None
        self.channelMeta = None
        self.warnRange = Range()
        self.alertRange = Range()
        self._syncing = False

        super(ChannelCustomizationView, self).__init__(**kwargs)
        self.register_event_type('on_channel_customization_close')

        self.settings = kwargs.get('settings')
        self.channel = kwargs.get('channel')
        self.channelMeta = self.settings.runtimeChannels.findChannelMeta(self.channel)
        self.init_view()


    def getWarnPrefsKey(self, channel):
        return '{}.warn'.format(self.channel)

    def getAlertPrefsKey(self, channel):
        return '{}.alert'.format(self.channel)

    def on_close(self):
        self.settings.userPrefs.set_range_alert(self.getWarnPrefsKey(self.channel), self.warnRange)
        self.settings.userPrefs.set_range_alert(self.getAlertPrefsKey(self.channel), self.alertRange)
        self.dispatch('on_channel_customization_close', self.warnRange, self.alertRange)

    def on_channel_customization_close(self, instance, *args):
        pass

    def setupSlider(self, slider, channelMeta, initialValue):
        min = channelMeta.min
        max = channelMeta.max

        slider.value = initialValue if initialValue != None else min
        slider.min = min
        slider.max = max
        slider.step = (max - min) / 100

    def sanitize_range(self, channel_range, channel_meta):
        channel_range.min = channel_meta.min if channel_range.min < channel_meta.min else channel_range.min
        channel_range.max = channel_meta.max if channel_range.max > channel_meta.max else channel_range.max

    def init_view(self):
        channel = self.channel
        channelMeta = self.channelMeta
        if channel and channelMeta:

            warnRange = self.settings.userPrefs.get_range_alert(self.getWarnPrefsKey(channel),
                    Range(min=channelMeta.max, max=channelMeta.max, color=Range.DEFAULT_WARN_COLOR))
            alertRange = self.settings.userPrefs.get_range_alert(self.getAlertPrefsKey(channel),
                    Range(min=channelMeta.max, max=channelMeta.max, color=Range.DEFAULT_ALERT_COLOR))

            self.sanitize_range(warnRange, channelMeta)
            self.sanitize_range(alertRange, channelMeta)

            self.setupSlider(self.ids.warnLowSlider, channelMeta, warnRange.min)
            self.setupSlider(self.ids.warnHighSlider, channelMeta, warnRange.max)

            self.setupSlider(self.ids.alertLowSlider, channelMeta, alertRange.min)
            self.setupSlider(self.ids.alertHighSlider, channelMeta, alertRange.max)

            self.ids.selectedWarnColor.color = warnRange.color
            self.ids.selectedAlertColor.color = alertRange.color

            self.alertRange = alertRange
            self.warnRange = warnRange

    def _synchLabels(self, gaugeRange, lowSlider, highSlider, lowLabel, highLabel):
        min_range = gaugeRange.min if gaugeRange.min != None else self.channelMeta.min
        lowLabel.text = str(int(min_range) if self.channelMeta.precision == 0 else float(min_range))
        lowSlider.value = min_range

        max_range = gaugeRange.max if gaugeRange.max != None else self.channelMeta.max
        highLabel.text = str(int(max_range) if self.channelMeta.precision == 0 else float(max_range))
        highSlider.value = max_range

    def _updateHighRange(self, gaugeRange, lowSlider, highSlider, lowLabel, highLabel, value):
        gaugeRange.max = value
        if gaugeRange.min == None: gaugeRange.min = self.channelMeta.min
        if value < gaugeRange.min:
            gaugeRange.min = value
        self._synchLabels(gaugeRange, lowSlider, highSlider, lowLabel, highLabel)

    def _updateLowRange(self, gaugeRange, lowSlider, highSlider, lowLabel, highLabel, value):
        gaugeRange.min = value
        if gaugeRange.max == None: gaugeRange.max = self.channelMeta.min
        if value > gaugeRange.max:
            gaugeRange.max = value
        self._synchLabels(gaugeRange, lowSlider, highSlider, lowLabel, highLabel)

    def on_alertHigh(self, instance, value):
        self._updateHighRange(self.alertRange, self.ids.alertLowSlider, self.ids.alertHighSlider, self.ids.alertLowValue, self.ids.alertHighValue, value)

    def on_alertLow(self, instance, value):
        self._updateLowRange(self.alertRange, self.ids.alertLowSlider, self.ids.alertHighSlider, self.ids.alertLowValue, self.ids.alertHighValue, value)

    def on_warnHigh(self, instance, value):
        self._updateHighRange(self.warnRange, self.ids.warnLowSlider, self.ids.warnHighSlider, self.ids.warnLowValue, self.ids.warnHighValue, value)

    def on_warnLow(self, instance, value):
        self._updateLowRange(self.warnRange, self.ids.warnLowSlider, self.ids.warnHighSlider, self.ids.warnLowValue, self.ids.warnHighValue, value)

    def _sync_slider(self, field_instance, slider_instance, value):
        if self._syncing:
            return
        self._syncing = True
        try:
            value = max(self.channelMeta.min, min(self.channelMeta.max, int(value) if self.channelMeta.precision == 0 else float(value)))
            field_instance.text = str(value)
            slider_instance.value = value
        except ValueError:
            pass
        self._syncing = False

    def on_alert_high_field(self, instance, value):
        self._sync_slider(instance, self.ids.alertHighSlider, value)

    def on_alert_low_field(self, instance, value):
        self._sync_slider(instance, self.ids.alertLowSlider, value)

    def on_warn_high_field(self, instance, value):
        self._sync_slider(instance, self.ids.warnHighSlider, value)

    def on_warn_low_field(self, instance, value):
        self._sync_slider(instance, self.ids.warnLowSlider, value)

    def popup_dismissed(self, *args):
        self._popup = None

    def dismiss_popup(self, *args):
        if self._popup:
            self._popup.dismiss()
            self._popup = None

    def warnColorSelected(self, instance, value):
        self.warnRange.color = value
        self.ids.selectedWarnColor.color = value
        self.dismiss_popup()

    def alertColorSelected(self, instance, value):
        self.alertRange.color = value
        self.ids.selectedAlertColor.color = value
        self.dismiss_popup()

    def show_color_select_popup(self, title, content):
        popup = Popup(title="Warning Color", content=content, size_hint=(0.4, 0.6))
        popup.bind(on_dismiss=self.popup_dismissed)
        popup.open()
        self._popup = popup

    def on_warn_color(self):
        content = ColorPickerView(color=self.warnRange.color)
        content.bind(on_color_selected=self.warnColorSelected)
        content.bind(on_color_cancel=self.dismiss_popup)
        self.show_color_select_popup('Warning Color', content)

    def on_alert_color(self):
        content = ColorPickerView(color=self.alertRange.color)
        content.bind(on_color_selected=self.alertColorSelected)
        content.bind(on_color_cancel=self.dismiss_popup)
        self.show_color_select_popup('Alert Color', content)
