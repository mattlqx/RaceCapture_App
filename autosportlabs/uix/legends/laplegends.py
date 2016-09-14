import kivy
kivy.require('1.9.0')
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, ListProperty
from autosportlabs.uix.color.colorgradient import SimpleColorGradient, HeatColorGradient
from autosportlabs.uix.legends.colorlegends import GradientBox
from kivy.graphics import Color, Rectangle
from kivy.app import Builder

class GradientLapLegend(BoxLayout):
    '''
    A compound widget that presents a gradient color legend including session/lap and min/max values
    '''
    Builder.load_string('''
<GradientLapLegend>:
    orientation: 'horizontal'
    spacing: sp(5)
    FieldLabel:
        id: lap
        size_hint_x: 0.5
        halign: 'right'
        valign: 'middle'
        text: '{} :: {}'.format(root.session, root.lap)
    FieldLabel:
        id: min_value
        text: str(root.min_value)
        size_hint_x: 0.2
        halign: 'right'
        valign: 'middle'
        font_size: 0.5 * self.height
    GradientLegend:
        id: legend
        size_hint_x: 0.1
        height_pct: root.height_pct
        color: root.color
    FieldLabel:
        id: max_value
        text: str(root.max_value)
        size_hint_x: 0.2
        halign: 'left'
        valign: 'middle'
        font_size: 0.5 * self.height
''')
    color = ObjectProperty([1.0, 1.0, 1.0], allownone=True)
    min_value = NumericProperty(0.0)
    max_value = NumericProperty(100.0)
    session = StringProperty('')
    lap = StringProperty('')
    height_pct = NumericProperty(0.3)

class LapLegend(BoxLayout):
    '''
    A compound widget that presents a colored legend with session/lap information
    '''
    Builder.load_string('''
<LapLegend>:
    orientation: 'horizontal'
    spacing: sp(5)
    FieldLabel:
        id: lap
        size_hint_x: 0.7
        halign: 'right'
        valign: 'middle'
        text: '{} :: {}'.format(root.session, root.lap)
        color: root.color
    FieldLabel:
        id: laptime
        size_hint_x: 0.3
        halign: 'right'
        valign: 'middle'
        text: '{}'.format(root.lap_time)
    ''')
    color = ListProperty([1.0, 1.0, 1.0, 1.0])
    session = StringProperty('')
    lap = StringProperty('')
    lap_time = StringProperty('')
