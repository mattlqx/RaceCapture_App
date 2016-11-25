import kivy
kivy.require('1.9.0')
import os
from kivy.metrics import sp
from kivy.app import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.switch import Switch
from kivy.uix.spinner import SpinnerOption
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from iconbutton import IconButton
from settingsview import SettingsSwitch
from autosportlabs.racecapture.views.configuration.baseconfigview import BaseConfigView
from autosportlabs.racecapture.config.rcpconfig import *
from autosportlabs.uix.layout.sections import SectionBoxLayout
from autosportlabs.racecapture.views.util.alertview import confirmPopup, choicePopup, editor_popup
from autosportlabs.racecapture.resourcecache.resourcemanager import ResourceCache
from fieldlabel import FieldLabel
from utils import *
from valuefield import FloatValueField, IntegerValueField
from mappedspinner import MappedSpinner
import copy

class LargeSpinnerOption(SpinnerOption):
    Builder.load_string("""
<LargeSpinnerOption>:
    font_size: self.height * 0.5
""")

class LargeMappedSpinner(MappedSpinner):
    Builder.load_string("""
<LargeMappedSpinner>:
    font_size: self.height * 0.4
    option_cls: 'LargeSpinnerOption'
""")

class LargeFieldLabel(FieldLabel):
    Builder.load_string("""
<LargeFieldLabel>:
    font_size: self.height * 0.4
""")


class LargeIntegerValueField(IntegerValueField):
    Builder.load_string("""
<LargeIntegerValueField>:
    font_size: self.height * 0.5
""")

class LargeFloatValueField(FloatValueField):
    Builder.load_string("""
<LargeFloatValueField>:
    font_size: self.height * 0.5
""")

class SymbolFieldLabel(FieldLabel):
    Builder.load_string("""
<SymbolFieldLabel>:
    font_size: self.height * 0.6
    font_name: 'resource/fonts/Roboto-Bold.ttf'    
""")


CAN_CHANNEL_CONFIG_VIEW_KV = """
<CANChannelConfigView>:
    spacing: dp(10)
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint_y: 0.9
            spacing: dp(10)
            orientation: 'vertical'
            
            BoxLayout:
                orientation: 'horizontal'
                spacing: dp(5)
                SectionBoxLayout:
                    size_hint_x: 0.15
                    FieldLabel:
                        halign: 'right'
                        text: 'CAN ID'
                BoxLayout:
                    spacing: dp(5)
                    size_hint_x: 0.85
                    orientation: 'horizontal'
                    SectionBoxLayout:
                        size_hint_x: 0.6
                        LargeIntegerValueField:
                            id: can_id
                            size_hint_x: 0.3
                            on_text: root.on_can_id(*args)
                    SectionBoxLayout:
                        size_hint_x: 0.4
                        FieldLabel:
                            size_hint_x: 0.6
                            text: 'CAN Bus'
                            halign: 'right'
                        LargeMappedSpinner:
                            size_hint_x: 0.4
                            id: can_bus_channel
                            on_text: root.on_can_bus_channel(*args)
    
            HLineSeparator:
                        
            BoxLayout:
                orientation: 'horizontal'
                spacing: dp(5)
                SectionBoxLayout:
                    size_hint_x: 0.15
                    orientation: 'horizontal'
                    FieldLabel:
                        halign: 'right'
                        text: 'Offset'
                        size_hint_x: 0.1

                BoxLayout:
                    size_hint_x: 0.85
                    orientation: 'horizontal'
                    spacing: dp(5)
                    SectionBoxLayout:
                        size_hint_x: 0.6
                        LargeMappedSpinner:
                            id: offset
                            size_hint_x: 0.1
                            on_text: root.on_bit_offset(*args)
                        FieldLabel:
                            halign: 'right'
                            text: 'Length'
                            size_hint_x: 0.1
                        LargeMappedSpinner:
                            id: length
                            size_hint_x: 0.1
                            on_text: root.on_bit_length(*args)
                    SectionBoxLayout:
                        size_hint_x: 0.4                    
                        BoxLayout:
                            orientation: 'vertical'
                            size_hint_x: 0.3
                            spacing: dp(5)
                            BoxLayout:
                                spacing: dp(5)
                                orientation: 'horizontal'
                                FieldLabel:
                                    text: 'Bit Mode'
                                    halign: 'right'
                                CheckBox:
                                    id: bitmode
                                    on_active: root.on_bit_mode(*args)
                            BoxLayout:
                                spacing: dp(5)
                                orientation: 'horizontal'
                                FieldLabel:
                                    text: 'Endian'
                                    halign: 'right'
                                MappedSpinner:
                                    id: endian
                                    on_text: root.on_endian(*args)

            HLineSeparator
                    
            BoxLayout:
                orientation: 'horizontal'
                spacing: dp(5)

                SectionBoxLayout:
                    size_hint_x: 0.15
                    spacing: dp(5)
                    orientation: 'horizontal'
                    FieldLabel:
                        halign: 'right'
                        text: 'Formula'
                        size_hint_x: 0.1
                
                SectionBoxLayout:
                    padding: (0, dp(10))
                    orientation: 'horizontal'
                    size_hint_x: 0.85
                    LargeFieldLabel:
                        size_hint_x: 0.1
                        halign: 'right'
                        text: 'Raw'
                    SymbolFieldLabel:
                        size_hint_x: 0.1
                        halign: 'center'
                        text: u' \u00D7 '
                    LargeFloatValueField:
                        id: multiplier
                        size_hint_x: 0.2
                        on_text: root.on_multiplier(*args)
                    SymbolFieldLabel:
                        halign: 'center'
                        text: u' \u00F7 '
                        size_hint_x: 0.1
                    LargeFloatValueField:
                        id: divider
                        size_hint_x: 0.2
                        on_text: root.on_divider(*args)
                    SymbolFieldLabel:
                        text: ' + '
                        halign: 'center'
                        size_hint_x: 0.1
                    LargeFloatValueField:
                        id: adder
                        size_hint_x: 0.2
                        on_text: root.on_adder(*args)
                
#            BoxLayout:
#                orientation: 'horizontal'
#                spacing: dp(5)
#                FieldLabel:
#                    halign: 'right'
#                    size_hint_x: 0.3
#                    text: 'Conversion Filter'
#                MappedSpinner:
#                    id: filters     
#                    size_hint_x: 0.7
#                    on_text: root.on_filter(*args)
"""

class CANChannelConfigView(BoxLayout):

    Builder.load_string(CAN_CHANNEL_CONFIG_VIEW_KV)

    def __init__(self, **kwargs):
        super(CANChannelConfigView, self).__init__(**kwargs)
        self._loaded = False

    def init_config(self, index, can_channel_cfg, can_filters):
        self.channel_index = index
        self.can_channel_cfg = can_channel_cfg
        self.can_filters = can_filters
        self.init_view()
        self._loaded = True

    def on_bit_mode(self, instance, value):
        if self._loaded:
            self.can_channel_cfg.mapping.bit_mode = self.ids.bitmode.active
            self.update_mapping_spinners()

    def on_sample_rate(self, instance, value):
        if self._loaded:
            self.can_channel_cfg.sampleRate = instance.getValueFromKey(value)

    def on_can_bus_channel(self, instance, value):
        if self._loaded:
            self.can_channel_cfg.mapping.can_channel = instance.getValueFromKey(value)

    def on_can_id(self, instance, value):
        if self._loaded:
            self.can_channel_cfg.mapping.can_id = int(value)

    def on_bit_offset(self, instance, value):
        if self._loaded:
            self.can_channel_cfg.mapping.bit_offset = instance.getValueFromKey(value)

    def on_bit_length(self, instance, value):
        if self._loaded:
            self.can_channel_cfg.mapping.bit_length = instance.getValueFromKey(value)

    def on_endian(self, instance, value):
        if self._loaded:
            self.can_channel_cfg.mapping.endian = instance.getValueFromKey(value)

    def on_multiplier(self, instance, value):
        if self._loaded:
            self.can_channel_cfg.mapping.multiplier = float(value)

    def on_divider(self, instance, value):
        if self._loaded:
            self.can_channel_cfg.mapping.divider = float(value)

    def on_adder(self, instance, value):
        if self._loaded:
            self.can_channel_cfg.mapping.adder = float(value)

    def on_filter(self, instance, value):
        if self._loaded:
            self.can_channel_cfg.mapping.conversion_filter_id = instance.getValueFromKey(value)

    def init_view(self):
        self.ids.can_bus_channel.setValueMap({0: '1', 1: '2'}, '1')

        self.ids.endian.setValueMap({0: 'Big (MSB)', 1: 'Little (LSB)'}, 'Big (MSB)')

        # Disable for the initial release
        # self.ids.filters.setValueMap(self.can_filters.filters, self.can_filters.default_value)

        self.update_mapping_spinners()
        self.load_values()

    def load_values(self):

        # CAN Channel
        self.ids.can_bus_channel.setFromValue(self.can_channel_cfg.mapping.can_channel)

        # CAN ID
        self.ids.can_id.text = str(self.can_channel_cfg.mapping.can_id)

        # CAN offset
        self.ids.offset.setFromValue(self.can_channel_cfg.mapping.bit_offset)

        # CAN length
        self.ids.length.setFromValue(self.can_channel_cfg.mapping.bit_length)

        # Bit Mode
        self.ids.bitmode.active = self.can_channel_cfg.mapping.bit_mode

        # Endian
        self.ids.endian.setFromValue(self.can_channel_cfg.mapping.endian)

        # Multiplier
        self.ids.multiplier.text = str(self.can_channel_cfg.mapping.multiplier)

        # Divider
        self.ids.divider.text = str(self.can_channel_cfg.mapping.divider)

        # Adder
        self.ids.adder.text = str(self.can_channel_cfg.mapping.adder)

        # Conversion Filter ID
        # Disable for initial release
        # self.ids.filters.setFromValue(self.can_channel_cfg.mapping.conversion_filter_id)

    def update_mapping_spinners(self):
        bit_mode = self.can_channel_cfg.mapping.bit_mode
        self.set_mapping_choices(bit_mode)

    def set_mapping_choices(self, bit_mode):
        choices = 63 if bit_mode else 7
        self.ids.offset.setValueMap(self.create_bit_choices(0, choices), '0')
        self.ids.length.setValueMap(self.create_bit_choices(1, 1 + choices), '1')

    def create_bit_choices(self, starting, max_choices):
        bit_choices = {}
        for i in range(starting, max_choices + 1):
            bit_choices[i] = str(i)
        return bit_choices

class CANFilters(object):
    filters = None
    default_value = None
    def __init__(self, base_dir, **kwargs):
        super(CANFilters, self).__init__(**kwargs)
        self.load_CAN_filters(base_dir)


    def load_CAN_filters(self, base_dir):
        if self.filters != None:
            return
        try:
            self.filters = {}
            can_filters_json = open(os.path.join(base_dir, 'resource', 'settings', 'can_channel_filters.json'))
            can_filters = json.load(can_filters_json)['can_channel_filters']
            for k in sorted(can_filters.iterkeys()):
                if not self.default_value:
                    self.default_value = k
                self.filters[int(k)] = can_filters[k]
        except Exception as detail:
            raise Exception('Error loading CAN filters: ' + str(detail))

CAN_CHANNEL_VIEW_KV = """
<CANChannelView>:
    spacing: dp(10)
    size_hint_y: None
    height: dp(30)
    orientation: 'horizontal'
    ChannelNameSelectorView:
        id: chan_id
        size_hint_x: 0.19
        compact: True
    SampleRateSpinner:
        id: sr
        size_hint_x: 0.15
        on_text: root.on_sample_rate(*args)
    FieldLabel:
        id: can_id
        size_hint_x: 0.16
    FieldLabel:
        id: can_offset_len
        size_hint_x: 0.2
    FieldLabel:
        size_hint_x: 0.25
        id: can_formula
    IconButton:
        size_hint_x: 0.05        
        text: u'\uf044'
        on_release: root.on_customize()
    IconButton:
        size_hint_x: 0.05        
        text: u'\uf014'
        on_release: root.on_delete()
"""

class CANChannelView(BoxLayout):
    Builder.load_string(CAN_CHANNEL_VIEW_KV)
    channels = None
    can_channel_cfg = None
    max_sample_rate = 0
    channel_index = 0

    def __init__(self, channel_index, can_channel_cfg, max_sample_rate, channels, **kwargs):
        super(CANChannelView, self).__init__(**kwargs)
        self.channel_index = channel_index
        self.can_channel_cfg = can_channel_cfg
        self.max_sample_rate = max_sample_rate
        self.channels = channels
        self.register_event_type('on_delete_channel')
        self.register_event_type('on_customize_channel')
        self.register_event_type('on_modified')
        self.set_channel()

    def on_modified(self):
        pass

    def on_sample_rate(self, instance, value):
        self.can_channel_cfg.sampleRate = instance.getValueFromKey(value)
        self.dispatch('on_modified')

    def on_delete_channel(self, channel_index):
        pass

    def on_customize_channel(self, channel_index):
        pass

    def on_delete(self):
        self.dispatch('on_delete_channel', self.channel_index)

    def on_customize(self):
        self.dispatch('on_customize_channel', self.channel_index)

    def set_channel(self):
        channel_editor = self.ids.chan_id
        channel_editor.on_channels_updated(self.channels)
        channel_editor.setValue(self.can_channel_cfg)

        sample_rate_spinner = self.ids.sr
        sample_rate_spinner.set_max_rate(self.max_sample_rate)
        sample_rate_spinner.setFromValue(self.can_channel_cfg.sampleRate)

        can_mapping = self.can_channel_cfg.mapping
        self.ids.can_id.text = '{}'.format(can_mapping.can_id)
        self.ids.can_offset_len.text = u'{} ( {} )'.format(can_mapping.bit_offset, can_mapping.bit_length)
        sign = '-' if can_mapping.adder < 0 else '+'
        self.ids.can_formula.text = u'\u00D7 {} {} {}'.format(can_mapping.multiplier, sign, abs(can_mapping.adder))
        self.ids.can_offset_len.text = u'{}({})'.format(can_mapping.bit_offset, can_mapping.bit_length)
        sign = '-' if can_mapping.adder < 0 else '+'
        self.ids.can_formula.text = u'\u00D7 {} {} {}'.format(can_mapping.multiplier, sign, abs(can_mapping.adder))

class CANPresetResourceCache(ResourceCache):
    preset_url = "http://podium.live/api/v1/can_presets"
    preset_name = 'can_presets'

    def __init__(self, settings, base_dir, **kwargs):
        default_preset_dir = os.path.join(base_dir, 'resource', self.preset_name)
        super(CANPresetResourceCache, self).__init__(settings, self.preset_url, self.preset_name, default_preset_dir, **kwargs)

CAN_CHANNELS_VIEW_KV = """
<CANChannelsView>:
    spacing: dp(20)
    orientation: 'vertical'
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: 0.20
        SettingsView:
            size_hint_y: 0.6
            id: can_channels_enable
            label_text: 'CAN channels'
            help_text: 'Enable CAN data mappings'
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: 0.4        
            BoxLayout:
                size_hint_x: 0.8
            LabelIconButton:
                size_hint_x: 0.2
                id: load_preset
                title: 'Presets'
                icon_size: self.height * 0.7
                title_font_size: self.height * 0.5
                icon: u'\uf150'
                on_press: root.load_preset_view()
        
    BoxLayout:
        size_hint_y: 0.70
        orientation: 'vertical'        
        HSeparator:
            text: 'CAN Channels'
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: 0.1
            FieldLabel:
                text: 'Channel'
                size_hint_x: 0.18
            FieldLabel:
                text: 'Sample Rate'
                size_hint_x: 0.15
                
            FieldLabel:
                text: 'ID'
                size_hint_x: 0.17
            FieldLabel:
                text: 'Offset(Length)'
                size_hint_x: 0.2
            FieldLabel:
                text: 'Formula'
                size_hint_x: 0.25
            FieldLabel:
                text: ''
                size_hint_x: 0.1
            
        AnchorLayout:                
            AnchorLayout:
                ScrollView:
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
                        id: can_grid
                        spacing: [dp(10), dp(10)]
                        size_hint_y: None
                        height: max(self.minimum_height, scroller.height)
                        cols: 1
                FieldLabel:
                    halign: 'center'
                    id: list_msg
                    text: ''
                        
            AnchorLayout:
                anchor_y: 'bottom'
                IconButton:
                    size_hint: (None, None)
                    height: root.height * .12
                    text: u'\uf055'
                    color: ColorScheme.get_accent()
                    on_release: root.on_add_can_channel()
                    disabled: True
                    id: add_can_channel
"""
class CANChannelsView(BaseConfigView):
    DEFAULT_CAN_SAMPLE_RATE = 1
    can_channels_cfg = None
    max_sample_rate = 0
    can_grid = None
    can_channels_settings = None
    can_filters = None
    _popup = None
    Builder.load_string(CAN_CHANNELS_VIEW_KV)

    def __init__(self, **kwargs):
        super(CANChannelsView, self).__init__(**kwargs)
        self.register_event_type('on_config_updated')
        self.can_grid = self.ids.can_grid
        self._base_dir = kwargs.get('base_dir')
        self.max_can_channels = 0
        can_channels_enable = self.ids.can_channels_enable
        can_channels_enable.bind(on_setting=self.on_can_channels_enabled)
        can_channels_enable.setControl(SettingsSwitch())
        self.update_view_enabled()
        self.can_filters = CANFilters(self._base_dir)
        self._resource_cache = None

    def get_resource_cache(self):
        if self._resource_cache is None:
            self._resource_cache = CANPresetResourceCache(self.settings, self._base_dir)
        return self._resource_cache

    def on_modified(self, *args):
        if self.can_channels_cfg:
            self.can_channels_cfg.stale = True
            self.dispatch('on_config_modified', *args)

    def on_can_channels_enabled(self, instance, value):
        if self.can_channels_cfg:
            self.can_channels_cfg.enabled = value
            self.dispatch('on_modified')

    def on_config_updated(self, rc_cfg):
        can_channels_cfg = rc_cfg.can_channels
        max_sample_rate = rc_cfg.capabilities.sample_rates.sensor
        max_can_channels = rc_cfg.capabilities.channels.can_channel
        self.ids.can_channels_enable.setValue(can_channels_cfg.enabled)

        self.reload_can_channel_grid(can_channels_cfg, max_sample_rate)
        self.can_channels_cfg = can_channels_cfg
        self.max_sample_rate = max_sample_rate
        self.max_can_channels = max_can_channels
        self.update_view_enabled()

    def update_view_enabled(self):
        add_disabled = True
        if self.can_channels_cfg:
            if len(self.can_channels_cfg.channels) < self.max_can_channels:
                add_disabled = False

        self.ids.add_can_channel.disabled = add_disabled

    def _refresh_can_channel_notice(self):
        cfg = self.can_channels_cfg
        if cfg is not None:
            channel_count = len(cfg.channels)
            self.ids.list_msg.text = 'No channels defined. Press (+) to map a CAN channel' if channel_count == 0 else ''

    def reload_can_channel_grid(self, can_channels_cfg, max_sample_rate):
        self.can_grid.clear_widgets()
        channel_count = len(can_channels_cfg.channels)
        for i in range(channel_count):
            can_channel_cfg = can_channels_cfg.channels[i]
            self.append_can_channel(i, can_channel_cfg, max_sample_rate)
        self.update_view_enabled()
        self._refresh_can_channel_notice()

    def append_can_channel(self, index, can_channel_cfg, max_sample_rate):
        channel_view = CANChannelView(index, can_channel_cfg, max_sample_rate, self.channels)
        channel_view.bind(on_delete_channel=self.on_delete_channel)
        channel_view.bind(on_customize_channel=self.on_customize_channel)
        channel_view.bind(on_modified=self.on_modified)
        self.can_grid.add_widget(channel_view)

    def on_add_can_channel(self):
        if (self.can_channels_cfg):
            can_channel = CANChannel()
            can_channel.sampleRate = self.DEFAULT_CAN_SAMPLE_RATE
            new_channel_index = self.add_can_channel(can_channel)
            self._customize_channel(new_channel_index)

    def add_can_channel(self, can_channel):
        self.can_channels_cfg.channels.append(can_channel)
        new_channel_index = len(self.can_channels_cfg.channels) - 1
        self.append_can_channel(new_channel_index, can_channel, self.max_sample_rate)
        self.update_view_enabled()
        self.dispatch('on_modified')
        return new_channel_index

    def _delete_all_channels(self):
        del self.can_channels_cfg.channels[:]
        self.reload_can_channel_grid(self.can_channels_cfg, self.max_sample_rate)
        self.dispatch('on_modified')

    def _delete_can_channel(self, channel_index):
        del self.can_channels_cfg.channels[channel_index]
        self.reload_can_channel_grid(self.can_channels_cfg, self.max_sample_rate)
        self.dispatch('on_modified')

    def on_delete_channel(self, instance, channel_index):
        popup = None
        def _on_answer(instance, answer):
            if answer:
                self._delete_can_channel(channel_index)
            popup.dismiss()
        popup = confirmPopup('Confirm', 'Delete CAN Channel?', _on_answer)

    def _replace_config(self, to_cfg, from_cfg):
        to_cfg.__dict__.update(from_cfg.__dict__)

    def popup_dismissed(self, *args):
        self.reload_can_channel_grid(self.can_channels_cfg, self.max_sample_rate)

    def _customize_channel(self, channel_index):
        content = CANChannelConfigView()
        working_channel_cfg = copy.deepcopy(self.can_channels_cfg.channels[channel_index])
        content.init_config(channel_index, working_channel_cfg, self.can_filters)

        def _on_answer(instance, answer):
            if answer:
                self._replace_config(self.can_channels_cfg.channels[content.channel_index], working_channel_cfg)
                self.dispatch('on_modified')

            self.reload_can_channel_grid(self.can_channels_cfg, self.max_sample_rate)
            popup.dismiss()

        popup = editor_popup('Customize CAN mapping', content, _on_answer, size_hint=(0.7, 0.7))

    def on_customize_channel(self, instance, channel_index):
        self._customize_channel(channel_index)

    def on_preset_selected(self, instance, preset_id):
        popup = None
        def _on_answer(instance, answer):
            if answer == True:
                self._delete_all_channels()
            self._import_preset(preset_id)
            popup.dismiss()

        if len(self.can_channels_cfg.channels) > 0:
            popup = choicePopup('Confirm', 'Overwrite or append existing channels?', 'Overwrite', 'Append', _on_answer)
        else:
            self._import_preset(preset_id)

    def _import_preset(self, preset_id):
        resource_cache = self.get_resource_cache()
        preset = resource_cache.resources.get(preset_id)
        if preset:
            for channel_json in preset['channels']:
                new_channel = CANChannel()
                new_channel.from_json_dict(channel_json)
                self.add_can_channel(new_channel)
        self._refresh_can_channel_notice()

    def load_preset_view(self):
        content = PresetBrowserView(self.get_resource_cache())
        content.bind(on_preset_selected=self.on_preset_selected)
        content.bind(on_preset_close=lambda *args:popup.dismiss())
        popup = Popup(title='Import a preset configuration', content=content, size_hint=(0.5, 0.75))
        popup.bind(on_dismiss=self.popup_dismissed)
        popup.open()

PRESET_ITEM_VIEW_KV = """
<PresetItemView>:
    canvas.before:
        Color:
            rgba: 0.01, 0.01, 0.01, 1
        Rectangle:
            pos: self.pos
            size: self.size             

    orientation: 'vertical'
    size_hint_y: None
    height: dp(200)
    padding: (dp(20), dp(0))
    spacing: dp(10)
    FieldLabel:
        id: title
        size_hint_y: 0.1
    BoxLayout:
        spacing: dp(10)
        size_hint_y: 0.85
        orientation: 'horizontal'
        AnchorLayout:
            size_hint_x: 0.75
            Image:
                id: image
            AnchorLayout:
                anchor_y: 'bottom'
                BoxLayout:
                    canvas.before:
                        Color:
                            rgba: 0, 0, 0, 0.7
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    size_hint_y: 0.3
                    FieldLabel:
                        halign: 'left'
                        id: notes

        AnchorLayout:
            size_hint_x: 0.25
            anchor_x: 'center'
            anchor_y: 'center'
            LabelIconButton:
                size_hint_x: 1
                size_hint_y: 0.3
                id: load_preset
                title: 'Select'
                icon_size: self.height * 0.7
                title_font_size: self.height * 0.5
                icon: u'\uf046'
                on_press: root.select_preset()
"""
class PresetItemView(BoxLayout):
    Builder.load_string(PRESET_ITEM_VIEW_KV)

    def __init__(self, preset_id, name, notes, image_path, **kwargs):
        super(PresetItemView, self).__init__(**kwargs)
        self.preset_id = preset_id
        self.ids.title.text = name
        self.ids.notes.text = notes
        self.ids.image.source = image_path
        self.register_event_type('on_preset_selected')

    def select_preset(self):
        self.dispatch('on_preset_selected', self.preset_id)

    def on_preset_selected(self, preset_id):
        pass

PRESET_BROWSER_VIEW_KV = """
<PresetBrowserView>:
    orientation: 'vertical'
    spacing: dp(10)
    ScrollView:
        size_hint_y: 0.85
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
            id: preset_grid
            spacing: [dp(10), dp(10)]
            size_hint_y: None
            height: max(self.minimum_height, scroller.height)
            cols: 1
    IconButton:
        size_hint_y: 0.15
        text: u'\uf00d'
        on_press: root.on_close()
"""

class PresetBrowserView(BoxLayout):
    presets = None
    Builder.load_string(PRESET_BROWSER_VIEW_KV)

    def __init__(self, resource_cache, **kwargs):
        super(PresetBrowserView, self).__init__(**kwargs)
        self.register_event_type('on_preset_close')
        self.register_event_type('on_preset_selected')
        self.resource_cache = resource_cache
        self.init_view()

    def on_preset_close(self):
        pass

    def on_preset_selected(self, preset_id):
        pass

    def init_view(self):
        self.refresh_view()

    def refresh_view(self):
        for k, v in self.resource_cache.resources.iteritems():
            name = v.get('name', '')
            notes = v.get('notes', '')
            self.add_preset(k, name, notes)

    def add_preset(self, preset_id, name, notes):
        image_path = self.resource_cache.resource_image_paths.get(preset_id)
        preset_view = PresetItemView(preset_id, name, notes, image_path)
        preset_view.bind(on_preset_selected=self.preset_selected)
        self.ids.preset_grid.add_widget(preset_view)

    def preset_selected(self, instance, preset_id):
        self.dispatch('on_preset_selected', preset_id)
        self.dispatch('on_preset_close')

    def on_close(self, *args):
        self.dispatch('on_preset_close')
