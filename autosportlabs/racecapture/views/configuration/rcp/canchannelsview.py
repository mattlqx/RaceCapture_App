import kivy
kivy.require('1.10.0')
import os
from kivy.metrics import dp
from kivy.app import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import SpinnerOption
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import StringProperty, NumericProperty
from garden_androidtabs import AndroidTabsBase, AndroidTabs
from iconbutton import IconButton
from settingsview import SettingsSwitch
from autosportlabs.racecapture.views.configuration.rcp.canmappingview import CANChannelConfigView
from autosportlabs.racecapture.data.unitsconversion import UnitsConversionFilters
from autosportlabs.racecapture.views.configuration.baseconfigview import BaseConfigView
from autosportlabs.racecapture.config.rcpconfig import *
from autosportlabs.uix.layout.sections import SectionBoxLayout
from autosportlabs.racecapture.views.util.alertview import confirmPopup, choicePopup, editor_popup
from autosportlabs.racecapture.resourcecache.resourcemanager import ResourceCache
from autosportlabs.widgets.scrollcontainer import ScrollContainer
from fieldlabel import FieldLabel
from utils import *
from valuefield import FloatValueField, IntegerValueField
from mappedspinner import MappedSpinner
import copy

class CANChannelView(BoxLayout):
    Builder.load_string("""
<CANChannelView>:
    size_hint_y: None
    height: dp(30)
    orientation: 'horizontal'
    FieldLabel:
        id: name
        size_hint_x: 0.18
    FieldLabel:
        id: sample_rate
        size_hint_x: 0.10
    FieldLabel:
        id: can_id
        size_hint_x: 0.14
    FieldLabel:
        id: can_offset_len
        size_hint_x: 0.15
    FieldLabel:
        size_hint_x: 0.30
        id: can_formula
    IconButton:
        size_hint_x: 0.09        
        text: u'\uf044'
        on_release: root.on_edit()
    IconButton:
        size_hint_x: 0.09        
        text: u'\uf014'
        on_release: root.on_delete()
""")

    def __init__(self, channel_index, channel_cfg, channels, **kwargs):
        super(CANChannelView, self).__init__(**kwargs)
        self.channel_index = channel_index
        self.channel_cfg = channel_cfg
        self.channels = channels
        self.register_event_type('on_delete_channel')
        self.register_event_type('on_edit_channel')
        self.register_event_type('on_modified')
        self._loaded = False
        self.set_channel()

    def on_modified(self):
        pass

    def on_delete_channel(self, channel_index):
        pass

    def on_edit_channel(self, channel_index):
        pass

    def on_delete(self):
        self.dispatch('on_delete_channel', self.channel_index)

    def on_edit(self):
        self.dispatch('on_edit_channel', self.channel_index)

    def set_channel(self):
        self.ids.name.text = self.channel_cfg.name

        self.ids.sample_rate.text = '{}Hz'.format(self.channel_cfg.sampleRate)

        can_mapping = self.channel_cfg.mapping
        self.ids.can_id.text = '{}'.format(can_mapping.can_id)

        self.ids.can_offset_len.text = u'{}({})'.format(can_mapping.offset, can_mapping.length)

        sign = '-' if can_mapping.adder < 0 else '+'
        self.ids.can_formula.text = u'\u00D7 {} \u00F7 {} {} {}'.format(can_mapping.multiplier, can_mapping.divider, sign, abs(can_mapping.adder))
        self._loaded = True

class CANPresetResourceCache(ResourceCache):
    preset_url = "https://podium.live/api/v1/mappings"
    preset_name = 'can_presets'

    def __init__(self, settings, base_dir, **kwargs):
        default_preset_dir = os.path.join(base_dir, 'resource', self.preset_name)
        super(CANPresetResourceCache, self).__init__(settings, self.preset_url, self.preset_name, default_preset_dir, **kwargs)

class CANChannelsView(BaseConfigView):
    DEFAULT_CAN_SAMPLE_RATE = 1
    can_channels_cfg = None
    max_sample_rate = 0
    can_grid = None
    can_channels_settings = None
    can_filters = None
    _popup = None
    Builder.load_string("""
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
            help_text: ''
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: 0.4        
            BoxLayout:
                size_hint_x: 0.8
#            LabelIconButton:
#                size_hint_x: 0.2
#                id: load_preset
#                title: 'Presets'
#                icon_size: self.height * 0.7
#                title_font_size: self.height * 0.5
#                icon: u'\uf150'
#                on_press: root.load_preset_view()
        
    BoxLayout:
        size_hint_y: 0.70
        orientation: 'vertical'        
        HSeparator:
            text: 'CAN Channels'
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: 0.1
            padding: [dp(5), dp(0)]            
            FieldLabel:
                text: 'Channel'
                halign: 'left'
                size_hint_x: 0.18
            FieldLabel:
                text: 'Rate'
                halign: 'left'
                size_hint_x: 0.10
                
            FieldLabel:
                text: 'CAN ID'
                size_hint_x: 0.14
            FieldLabel:
                text: 'Offset(Len)'
                size_hint_x: 0.15
            FieldLabel:
                text: 'Formula'
                size_hint_x: 0.30
            FieldLabel:
                text: ''
                size_hint_x: 0.18
            
        AnchorLayout:                
            AnchorLayout:
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
                        id: can_grid
                        padding: [dp(5), dp(5)]                        
                        spacing: [dp(0), dp(10)]
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
""")

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
        self.can_filters = UnitsConversionFilters(self._base_dir)
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
        self.reload_can_channel_grid(can_channels_cfg)
        self.max_sample_rate = max_sample_rate
        self.max_can_channels = max_can_channels
        self.can_channels_cfg = can_channels_cfg
        self.update_view_enabled()

    def update_view_enabled(self):
        add_disabled = True
        if self.can_channels_cfg:
            if len(self.can_channels_cfg.channels) < self.max_can_channels:
                add_disabled = False

        self.ids.add_can_channel.disabled = add_disabled

    def _refresh_channel_list_notice(self, cfg):
        channel_count = len(cfg.channels)
        self.ids.list_msg.text = 'Press (+) to map a CAN channel' if channel_count == 0 else ''

    def reload_can_channel_grid(self, can_channels_cfg):
        self.can_grid.clear_widgets()
        channel_count = len(can_channels_cfg.channels)
        for i in range(channel_count):
            channel_cfg = can_channels_cfg.channels[i]
            self.append_can_channel(i, channel_cfg)
        self.update_view_enabled()
        self._refresh_channel_list_notice(can_channels_cfg)

    def append_can_channel(self, index, channel_cfg):
        channel_view = CANChannelView(index, channel_cfg, self.channels)
        channel_view.bind(on_delete_channel=self.on_delete_channel)
        channel_view.bind(on_edit_channel=self.on_edit_channel)
        channel_view.bind(on_modified=self.on_modified)
        self.can_grid.add_widget(channel_view)

    def on_add_can_channel(self):
        if not self.can_channels_cfg:
            return

        can_channel = CANChannel()
        can_channel.sampleRate = self.DEFAULT_CAN_SAMPLE_RATE

        content = CANChannelConfigView()
        content.init_config(can_channel, self.can_filters, self.max_sample_rate, self.channels)

        popup = None
        def _on_answer(instance, answer):
            if answer:
                self.add_can_channel(can_channel)
                self.dispatch('on_modified')
                self.reload_can_channel_grid(self.can_channels_cfg)
            popup.dismiss()

        popup = editor_popup('Add CAN Channel Mapping', content, _on_answer, size=(dp(500), dp(300)))

    def add_can_channel(self, can_channel):
        self.can_channels_cfg.channels.append(can_channel)
        new_channel_index = len(self.can_channels_cfg.channels) - 1
        self.append_can_channel(new_channel_index, can_channel)
        self.update_view_enabled()
        self.dispatch('on_modified')
        return new_channel_index

    def _delete_all_channels(self):
        del self.can_channels_cfg.channels[:]
        self.reload_can_channel_grid(self.can_channels_cfg)
        self.dispatch('on_modified')

    def _delete_can_channel(self, channel_index):
        del self.can_channels_cfg.channels[channel_index]
        self.reload_can_channel_grid(self.can_channels_cfg)
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
        self.reload_can_channel_grid(self.can_channels_cfg)

    def _edit_channel(self, channel_index):
        content = CANChannelConfigView()
        working_channel_cfg = copy.deepcopy(self.can_channels_cfg.channels[channel_index])
        content.init_config(working_channel_cfg, self.can_filters, self.max_sample_rate, self.channels)

        def _on_answer(instance, answer):
            if answer:
                self._replace_config(self.can_channels_cfg.channels[channel_index], working_channel_cfg)
                self.dispatch('on_modified')

            self.reload_can_channel_grid(self.can_channels_cfg)
            popup.dismiss()

        popup = editor_popup('Edit CAN Channel Mapping', content, _on_answer, size=(dp(500), dp(300)))

    def on_edit_channel(self, instance, channel_index):
        self._edit_channel(channel_index)

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

    def load_preset_view(self):
        content = PresetBrowserView(self.get_resource_cache())
        content.bind(on_preset_selected=self.on_preset_selected)
        content.bind(on_preset_close=lambda *args:popup.dismiss())
        popup = Popup(title='Import a preset configuration', content=content, size_hint=(0.5, 0.75))
        popup.bind(on_dismiss=self.popup_dismissed)
        popup.open()

class PresetItemView(BoxLayout):
    Builder.load_string("""
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
""")

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

class PresetBrowserView(BoxLayout):
    presets = None
    Builder.load_string("""
<PresetBrowserView>:
    orientation: 'vertical'
    spacing: dp(10)
    ScrollContainer:
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
""")

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
