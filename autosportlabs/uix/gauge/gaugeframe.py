import kivy
kivy.require('1.10.0')
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.app import Builder
from kivy.core.image import Image as CoreImage

GAUGE_FRAME_KV = """
<GaugeFrame>:
    orientation: 'vertical'
    FieldLabel:
        canvas.before:
            Color:
                rgba: ColorScheme.get_dark_background()
            Rectangle:
                pos: self.pos
                size: self.size
                texture: root.header.texture
  
        size_hint_y: None
        height: dp(25)
        id: title
        font_size: self.height * 0.8
        text: '{}{}'.format(root.title, '' if root.units is None else ' ({})'.format(root.units))
        halign: 'right'
        padding: (5,5)

#    AnchorLayout:
#        canvas.before:
#            Color:
#                rgba: ColorScheme.get_dark_background()
#            Rectangle:
#                pos: self.pos
#                size: self.size
#        #padding: (1,1)
#        
#        AnchorLayout:
#            canvas.before:
#                Color:
#                    rgba: ColorScheme.get_background()
#                Rectangle:
#                    pos: self.pos
#                    size: self.size          
#            padding: [2,2]
#            anchor_x: 'center'
#            anchor_y: 'center'
#            AnchorLayout:
#                id: raw_gauge_container
"""
class GaugeFrame(BoxLayout):
    Builder.load_string(GAUGE_FRAME_KV)
    minval = NumericProperty(0)
    maxval = NumericProperty(100)
    value = NumericProperty(0, allownone=True)
    value_type = NumericProperty()
    precision = NumericProperty(0, allownone=True)
    title = StringProperty()
    color_sequence = ObjectProperty()
    units = StringProperty(None, allownone=True)
    header = CoreImage('resource/gauge/header.png')
    raw_gauge = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super(GaugeFrame, self).__init__(**kwargs)

    def add_widget(self, widget, *args):
        super(GaugeFrame, self).add_widget(widget, 0)
        children = len(self.children)

        if children < 2:
            return

        if children > 2:
            raise Exception('GaugeFrame only allows one widget')

        self.raw_gauge = widget
        try:
            from kivy.clock import Clock
            widget.bind(channel=self._on_title)
            widget.bind(title=self._on_title)
        except AttributeError:
            Logger.warn('No title attribute on {}'.format(widget))

    def _on_title(self, instance, value):
        self.title = value

    def on_color_sequence(self, instance, color_sequence):
        self.raw_gauge.color = color_sequence.get_color(self.title)

    def on_value_type(self, instance, value_type):
        self.raw_gauge.value_type = value_type

    def on_precision(self, instance, precision):
        self.raw_gauge.precision = precision

    def on_minval(self, instance, minval):
        self.raw_gauge.minval = minval

    def on_maxval(self, instance, maxval):
        self.raw_gauge.maxval = maxval

    def on_value(self, instance, value):
        self.raw_gauge.value = value

