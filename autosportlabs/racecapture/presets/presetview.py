import kivy
kivy.require('1.9.1')
import os
from kivy.metrics import dp
from kivy.app import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import SpinnerOption
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from iconbutton import IconButton
from autosportlabs.widgets.scrollcontainer import ScrollContainer

#    def load_preset_view(self):
#        content = PresetBrowserView(self.preset_manager, 'can')
#        content.bind(on_preset_selected=self.on_preset_selected)
#        content.bind(on_preset_close=lambda *args:popup.dismiss())
#        popup = Popup(title='Import a preset configuration', content=content, size_hint=(0.5, 0.75))
#        popup.bind(on_dismiss=self.popup_dismissed)
#        popup.open()

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
            size_hint_x: None
            width: dp(120)
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
        self.ids.title.text = '' if not name else name
        self.ids.notes.text = '' if not notes else notes
        self.ids.image.source = image_path
        self.register_event_type('on_preset_selected')

    def select_preset(self):
        self.dispatch('on_preset_selected', self.preset_id)

    def on_preset_selected(self, preset_id):
        pass

class PresetBrowserView(BoxLayout):
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

    def __init__(self, preset_manager, preset_type, **kwargs):
        super(PresetBrowserView, self).__init__(**kwargs)
        self.register_event_type('on_preset_close')
        self.register_event_type('on_preset_selected')
        self.preset_manager = preset_manager
        self.preset_type = preset_type
        self.init_view()

    def on_preset_close(self):
        pass

    def on_preset_selected(self, preset_id):
        pass

    def init_view(self):
        self.refresh_view()

    def refresh_view(self):
        for k, v in self.preset_manager.get_presets_by_type(self.preset_type):
            name = v.name
            notes = v.notes
            self.add_preset(k, name, notes)

    def add_preset(self, preset_id, name, notes):
        preset = self.preset_manager.get_preset_by_id(preset_id)
        if preset:
            image_path = preset.image_url
            preset_view = PresetItemView(preset_id, name, notes, preset.local_image_path)
            preset_view.bind(on_preset_selected=self.preset_selected)
            self.ids.preset_grid.add_widget(preset_view)

    def preset_selected(self, instance, preset_id):
        self.dispatch('on_preset_selected', preset_id)
        self.dispatch('on_preset_close')

    def on_close(self, *args):
        self.dispatch('on_preset_close')
