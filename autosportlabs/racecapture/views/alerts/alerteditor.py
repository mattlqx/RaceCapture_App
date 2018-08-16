import kivy
kivy.require('1.10.0')
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from fieldlabel import FieldLabel
from iconbutton import IconButton
from autosportlabs.widgets.scrollcontainer import ScrollContainer

class AlertRuleSummaryView(BoxLayout):
    # value range
    # type
    # enabled
    # edit
    # delete
    Builder.load_string("""
<AlertRuleSummaryView>:
    orientation: 'horizontal'
    size_hint_y: 'None'
    height: dp(30)
    FieldLabel:
        id: range
        size_hint: 0.2
    FieldLabel:
        id: type
        size_hint: 0.4
    ToggleButton:
        id: enabled
        size_hint:0.2
    IconButton:
        size_hint_x: 0.1        
        text: u'\uf044'
        on_release: root.on_edit()
    IconButton:
        size_hint_x: 0.1        
        text: u'\uf014'
        on_release: root.on_delete()    
""")

class AlertRulesView(BoxLayout):
    Builder.load_string("""
<AlertRulesView>:
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
            id: rules_grid
            padding: [dp(5), dp(5)]                        
            spacing: [dp(0), dp(10)]
            size_hint_y: None
            height: max(self.minimum_height, scroller.height)
            cols: 1
    """)
