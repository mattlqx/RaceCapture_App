import kivy
kivy.require('1.10.0')
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.switch import Switch
from fieldlabel import FieldLabel
from iconbutton import IconButton
from kivy.app import Builder

from autosportlabs.widgets.scrollcontainer import ScrollContainer

class AlertRuleSummaryView(BoxLayout):
    Builder.load_string("""
<AlertRuleSummaryView>:
    orientation: 'horizontal'
    size_hint_y: 'None'
    height: dp(30)
    FieldLabel:
        id: range
        size_hint_x: 0.2
    FieldLabel:
        id: type
        size_hint_x: 0.4
    Switch:
        id: enabled
        size_hint_x: 0.2
        on_active: root.on_enable_disable()
    IconButton:
        size_hint_x: 0.1        
        text: u'\uf044'
        on_release: root.on_edit()
    IconButton:
        size_hint_x: 0.1        
        text: u'\uf014'
        on_release: root.on_delete()    
""")
    def __init__(self, alertrule, **kwargs):
        super(AlertRuleSummaryView, self).__init__(**kwargs)        
        self._alertrule = alertrule
        self._refresh_view()
        
    def _refresh_view(self):
        ar = self._alertrule
        self.ids.range.text = '{} - {}'.format(ar.low_threshold, ar.high_threshold)
        self.ids.type.text = ar.alert_action.title
        self.ids.enabled.active = ar.enabled is True
        
    def on_enable_disable(self):
        self._alertrule.enabled = self.ids.enabled.active
    
    def on_edit(self):
        pass
    
    def on_delete(self):
        pass

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
    
    def __init__(self, alertrule_collection, **kwargs):
        super(AlertRulesView, self).__init__(**kwargs)
        self._alertrule_collection = alertrule_collection
        self._refresh_view()
        
    def _refresh_view(self):
        grid = self.ids.rules_grid
        rules = self._alertrule_collection
        
        grid.clear_widgets()
        for rule in rules.alert_rules:
            view = AlertRuleSummaryView(rule)
            grid.add_widget(view)
    
    