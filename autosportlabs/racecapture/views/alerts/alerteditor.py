import kivy
kivy.require('1.10.0')
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.switch import Switch
from fieldlabel import FieldLabel
from iconbutton import IconButton
from kivy.app import Builder
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from autosportlabs.racecapture.theme.color import ColorScheme
from autosportlabs.racecapture.views.util.alertview import confirmPopup
from autosportlabs.widgets.scrollcontainer import ScrollContainer

class AlertRuleSummaryView(BoxLayout):
    is_first = BooleanProperty(False)
    is_last = BooleanProperty(False)
    
    Builder.load_string("""
<ClickLabel@ButtonBehavior+FieldLabel>

<AlertRuleSummaryView>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(30)
    FieldLabel:
        id: range
        size_hint_x: 0.25
    ClickLabel:
        id: type
        size_hint_x: 0.25
        on_press: root.dispatch('on_select', root._alertrule)
    Switch:
        id: enabled
        size_hint_x: 0.2
        on_active: root.on_enable_disable()
    IconButton:
        size_hint_x: 0.1        
        text: u'\uf063'
        disabled: root.is_last
        on_release: root.dispatch('on_move_down', root._alertrule)    
    IconButton:
        size_hint_x: 0.1
        text: u'\uf062'
        disabled: root.is_first        
        on_release: root.dispatch('on_move_up', root._alertrule)
    IconButton:
        size_hint_x: 0.1        
        text: u'\uf014'
        on_release: root.dispatch('on_delete', root._alertrule)    
""")
    def __init__(self, alertrule, **kwargs):
        super(AlertRuleSummaryView, self).__init__(**kwargs)        
        self._alertrule = alertrule
        self.register_event_type('on_select')
        self.register_event_type('on_move_down')
        self.register_event_type('on_move_up')
        self.register_event_type('on_delete')
        self.register_event_type('on_modified')
        self._refresh_view()
        
    def _refresh_view(self):
        ar = self._alertrule
        self.ids.range.text = '{} - {}'.format(ar.low_threshold, ar.high_threshold)
        actions = ar.alert_actions
        actions_len = len(ar.alert_actions)
        action_title = actions[0].title if actions_len == 1 else '(Multiple Actions)' if actions_len > 1 else '(No Actions)'
        self.ids.type.text = action_title
        self.ids.enabled.active = ar.enabled is True
        
    def on_select(self, rule):
        pass
        
    def on_enable_disable(self):
        self._alertrule.enabled = self.ids.enabled.active
        self.dispatch('on_modified', self._alertrule)
    
    def on_modified(self, rule):
        pass
    
    def on_edit(self, rule):
        pass
    
    def on_delete(self, rule):
        pass
    
    def on_move_down(self, rule):
        pass
    
    def on_move_up(self, rule):
        pass
    
class AlertRuleList(Screen):
    alertrule_collection = ObjectProperty()
    Builder.load_string("""
<AlertRuleList>:
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
    
    def __init__(self, **kwargs):
        super(AlertRuleList, self).__init__(**kwargs)
        self.register_event_type('on_select')  
    
    def on_select(self, value):
        pass
    
    def on_alertrule_collection(self, instance, value):
        self._refresh_view()
        
    def _refresh_view(self):
        grid = self.ids.rules_grid
        rules = self.alertrule_collection
        
        grid.clear_widgets()
        is_first = True
        view = None
        for rule in rules.alert_rules:
            view = AlertRuleSummaryView(rule)
            view.bind(on_select=self._on_select_rule)
            view.bind(on_move_up=self._on_move_rule_up)
            view.bind(on_move_down=self._on_move_rule_down)
            view.bind(on_delete=self._on_delete_rule)
            view.bind(on_modified=self._on_modified_rule)
            view.is_first = is_first
            is_first = False
            grid.add_widget(view)
        if view is not None:
            view.is_last = True
    
    def _on_modified_rule(self, instance, value):
        print('rule modified {}'.format(value))
        
    def _on_select_rule(self, instance, value):
        self.dispatch('on_select', value)
        
    def _on_move_rule_up(self, instance, value):
        rules = self.alertrule_collection.alert_rules
        current_index = rules.index(value)
        if current_index == 0:
            return
        
        rules.insert(current_index - 1, rules.pop(current_index))
        self._refresh_view()
        
    def _on_move_rule_down(self, instance, value):
        rules = self.alertrule_collection.alert_rules
        current_index = rules.index(value)
        if current_index == len(rules) - 1:
            return
        
        rules.insert(current_index + 1, rules.pop(current_index))
        self._refresh_view()
        
    def _on_delete_rule(self, instance, value):
        
        popup = None
        def confirm_delete(instance, delete):
            if delete:
                rules = self.alertrule_collection.alert_rules
                rules.remove(value)
                self._refresh_view()
            popup.dismiss()

        popup = confirmPopup('Delete', 'Delete Group {}-{}?'.format(value.low_threshold, value.high_threshold), confirm_delete)        

class AlertActionList(Screen):
    alertrule_collection = ObjectProperty()
    Builder.load_string("""
<AlertActionList>:
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
            id: grid
            padding: [dp(5), dp(5)]                        
            spacing: [dp(0), dp(10)]
            size_hint_y: None
            height: max(self.minimum_height, scroller.height)
            cols: 1
    """)

    def __init__(self, **kwargs):
        super(AlertActionList, self).__init__(**kwargs)
        self.register_event_type('on_close')

    def on_close(self):
        pass
    
    def on_enter(self, *args):
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.dispatch('on_close'), 1.0)

class AlertRulesView(BoxLayout):
    Builder.load_string("""
<AlertRulesView>:
    ScreenManager:
        id: screen_manager
        AlertRuleList:
            name: "rule_list"
            id: rule_list
        AlertActionList:
            name: 'group_list'
            id: group_list
    """)
    
    def __init__(self, alertrule_collection, **kwargs):
        super(AlertRulesView, self).__init__(**kwargs)
        self.ids.screen_manager.transition = SlideTransition()
        self._alertrule_collection = alertrule_collection
        self.ids.rule_list.bind(on_select=self._on_rule_select)
        self.ids.rule_list.alertrule_collection = alertrule_collection
        
        self.ids.group_list.bind(on_close=self._on_close_group)
        
    def _on_rule_select(self, instance, value):
        sm = self.ids.screen_manager
        sm.transition.direction = 'up' 
        sm.current = 'group_list'
    
    def _on_close_group(self, instance):
        sm = self.ids.screen_manager
        sm.transition.direction = 'down' 
        sm.current = 'rule_list'
        

        
        
    