import kivy
kivy.require('1.10.0')
from kivy.app import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from fieldlabel import FieldLabel
from kivy.properties import ObjectProperty
from autosportlabs.racecapture.alerts.alertactions import *
from autosportlabs.racecapture.views.color.colorpickerview import ColorPickerView
from autosportlabs.racecapture.views.color.colorpickerview import ColorBlock
from autosportlabs.uix.textwidget import FieldInput
import re

class BaseAlertActionEditorView(BoxLayout):
    alertaction = ObjectProperty()

    @classmethod
    def new_instance(cls, action):
        return cls(alertaction=action)

class ColorAlertActionEditorView(BaseAlertActionEditorView):
    Builder.load_string("""
<ColorAlertActionEditorView>:
    BoxLayout:
        size_hint_x: 0.8
    
        AnchorLayout:
            ColorBlock:
                size_hint: (0.5, 0.5)
                id: selected_color
        
    ColorWheel:
        id: color_wheel
        on_color: root._select_color(*args)
    """)

    def __init__(self, **kwargs):
        super(ColorAlertActionEditorView, self).__init__(**kwargs)
        c = self.alertaction.color_rgb
        self.ids.selected_color.color = [c[0], c[1], c[2], 1.0]

    def _select_color(self, instance, color):
        self.ids.selected_color.color = color
        self.alertaction.color_rgb = [color[0], color[1], color[2], 1.0]

class PopupAlertActionEditorView(BaseAlertActionEditorView):
    Builder.load_string("""
<PopupAlertActionEditorView>:
    BoxLayout:
        size_hint_x: 0.8
        orientation: 'vertical'
        spacing: dp(10)
        Widget:
        BoxLayout:
            spacing: dp(10)
            size_hint_y: None
            height: dp(40)
            FieldLabel:
                text: 'Message'
                halign: 'right'
            FieldInput:
                id: popup_message
                on_text: root._on_popup_message(*args)

        BoxLayout:
            spacing: dp(10)
            size_hint_y: None
            height: dp(40)
            FieldLabel:
                text: 'Shape'
                halign: 'right'
            Spinner:
                values: ['None', 'Triangle', 'Octagon']
                id: popup_shape
                on_text: root._on_popup_shape(*args)
                
        BoxLayout:
            spacing: dp(10)
            size_hint_y: None
            height: dp(40)
            FieldLabel:
                text: 'Color'
                halign: 'right'
            AnchorLayout:
                ColorBlock:
                    id: popup_color
                    on_press: root._on_select_color(*args)
        Widget:
                        
    FieldLabel:
        text: 'Preview here'
        halign: 'center'
    """)

    shape_map = {None:'None', 'triangle':'Triangle', 'octagon':'Octagon'}

    def __init__(self, **kwargs):
        super(PopupAlertActionEditorView, self).__init__(**kwargs)
        self._refresh_view()

    def _refresh_view(self):
        alertaction = self.alertaction
        self.ids.popup_message.text = alertaction.message
        self.ids.popup_shape.text = PopupAlertActionEditorView.shape_map.get(alertaction.shape, 'None')
        c = alertaction.color_rgb
        self.ids.popup_color.color = [c[0], c[1], c[2], 1.0]

    def _on_popup_message(self, instance, value):
        # filter the message
        value = value.strip()
        self.ids.popup_message.text = value
        self.alertaction.message = value

    def _on_popup_shape(self, instance, value):
        map = PopupAlertActionEditorView.shape_map
        self.alertaction.shape = map.keys()[map.values().index(value)]

    def _on_select_color(self, instance):
        def color_selected(instance, c):
            self.alertaction.color_rgb = [c[0], c[1], c[2], 1.0]
            self.ids.popup_color.color = [c[0], c[1], c[2], 1.0]
            popup.dismiss()

        c = self.alertaction.color_rgb
        content = ColorPickerView(color=[c[0], c[1], c[2], 1.0])
        content.bind(on_color_selected=color_selected)
        popup = Popup(title="Select Color", content=content, size_hint=(0.4, 0.6))
        popup.open()

class LedAlertActionEditorView(BaseAlertActionEditorView):
    Builder.load_string("""
<LedAlertActionEditorView>:
    FieldLabel:
        text: 'LED'
    """)

class ShiftLightAlertActionEditorView(BaseAlertActionEditorView):
    Builder.load_string("""
<ShiftLightAlertActionEditorView>:
    FieldLabel:
        text: 'shift light'
    """)

class AlertActionEditorFactory(object):

    factory = {
                ColorAlertAction.__name__:ColorAlertActionEditorView.new_instance,
                PopupAlertAction.__name__:PopupAlertActionEditorView.new_instance,
                LedAlertAction.__name__:LedAlertActionEditorView.new_instance,
                ShiftLightAlertAction.__name__:ShiftLightAlertActionEditorView.new_instance
              }

    @staticmethod
    def create_editor(action):
        return AlertActionEditorFactory.factory[action.__class__.__name__](action)
