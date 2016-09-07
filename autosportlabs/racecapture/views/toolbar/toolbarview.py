import kivy
kivy.require('1.9.1')
from utils import *
from kivy.properties import ObjectProperty, NumericProperty, ListProperty, StringProperty
from kivy.uix.stacklayout import StackLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.progressbar import ProgressBar
from kivy.app import Builder
from kivy.clock import Clock
from iconbutton import IconButton
from kivy.logger import Logger
from fieldlabel import FieldLabel
from autosportlabs.racecapture.theme.color import ColorScheme

TOOLBAR_VIEW_KV = '''
<ProgressFieldLabel>:
    RelativeLayout:
        StencilView:
            size_hint: (None, 1.0)
            id: stencil
            width: 0
            canvas.after:
                Color:
                    rgba: root.color
                Rectangle:
                    pos: self.pos
                    size: self.size
    FieldLabel:
        id: value
        halign: 'center'
        color: root.text_color
        font_size: self.height * 0.6

<ToolbarItem>:
    canvas.before:
        Color:
            rgba: ColorScheme.get_dark_background()
        Rectangle:
            pos: self.pos
            size: self.size

<ToolbarView>:
    orientation: 'horizontal'
    spacing: sp(2)
    ToolbarItem:
        padding: self.height * 0.5, 0
        size_hint_x: 0.10
        orientation: 'horizontal'
        IconButton:
            id: menu
            text: '\357\203\211'
            on_release: root.mainMenu()
            size_hint_x: None
            width: self.height * 1
            font_size: self.height
        Button:
            background_color: [0.0, 0.0, 0.0, 0.0]
            background_down: ''
            text: '    '
            font_name: "resource/fonts/ASL_light.ttf"
            size_hint_x: 0.0
            width: self.height * 2.4
            font_size: self.height * 0.7
            on_release: root.mainMenu()
            
    ToolbarItem:
        orientation: 'horizontal'
        padding: self.height * 0.4, 0
        size_hint_x: 0.50
        FieldLabel:
            halign: 'center'
            text: ''
            id: state
            font_size: self.height * 0.7

    ToolbarItem:
        orientation: 'horizontal'
        padding: self.height * 0.4, 0
        size_hint_x: 0.3
        ProgressFieldLabel:
            text: ''
            id: prog_status
        
    ToolbarItem:
        orientation: 'horizontal'
        size_hint_x: 0.1
        IconButton:
            id: gps_status
            text: u'\uf041'
            font_size: self.height * 0.8
            color: [0.3, 0.3, 0.3, 0.2]
        IconButton:
            id: tele_status
            text: '\357\203\256'
            color: [0.3, 0.3, 0.3, 0.2]        
            font_size: self.height * 0.8
        IconButton:
            id: data_rx_status
            text: '\357\202\223'
            color: [0.0, 0.8, 1.0, 0.2]
            font_size: self.height * 0.8
            
            

'''
class ToolbarItem(BoxLayout):
    pass

class ProgressFieldLabel(AnchorLayout):
    minval = NumericProperty(0)
    maxval = NumericProperty(100)
    value = NumericProperty(0)
    color = ColorScheme.get_accent()
    text_color = ColorScheme.get_light_primary_text()
    text = StringProperty('')

    def __init__(self, **kwargs):
        super(ProgressFieldLabel, self).__init__(**kwargs)

    def on_minval(self, instance, value):
        self._refresh_value()

    def on_maxval(self, instance, value):
        self._refresh_value()

    def on_value(self, instance, value):
        self._refresh_value()

    def on_text(self, instance, value):
        self.ids.value.text = str(value)

    def _refresh_value(self):
        stencil = self.ids.stencil
        value = self.value
        minval = self.minval
        maxval = self.maxval
        pct = ((value - minval) / (maxval - minval))
        width = self.width * pct
        stencil.width = width

class ToolbarView(BoxLayout):
    status_pump = ObjectProperty(None)
    track_manager = ObjectProperty(None)

    TOOLBAR_DATA_RX_DURATION = 0.1
    PROGRESS_COMPLETE_LINGER_DURATION = 7.0
    ACTIVITY_MESSAGE_LINGER_DURATION = 7.5
    STATUS_LINGER_DURATION = 2.0

    TELEMETRY_IDLE = 0
    TELEMETRY_ACTIVE = 1
    TELEMETRY_CONNECTING = 2
    TELEMETRY_ERROR = 3

    telemetry_color = {TELEMETRY_IDLE:[0.0, 1.0, 0.0, 0.2],
                       TELEMETRY_ACTIVE:[0.0, 1.0, 0.0, 1.0],
                       TELEMETRY_CONNECTING:[1.0, 1.0, 0.0, 1.0],
                       TELEMETRY_ERROR:[1.0, 0.0, 0.0, 1.0]
                       }

    DATA_NO_RX = 0
    DATA_RX = 1
    data_rx_color = {DATA_NO_RX:[0.0, 0.8, 1.0, 0.2],
                     DATA_RX:[0.0, 0.8, 1.0, 1.0]}


    GPS_NO_DATA = 0
    GPS_NO_LOCK = 1
    GPS_MARGINAL = 2
    GPS_HIGH_QUALITY = 3
    gps_color = { GPS_NO_DATA: [0.3, 0.3, 0.3, 0.2],
                 GPS_NO_LOCK: [1.0, 0.0, 0.0, 1.0],
                 GPS_MARGINAL: [1.0, 1.0, 0.0, 1.0],
                 GPS_HIGH_QUALITY: [0.0, 1.0, 0.0, 1.0]}

    normal_status_color = ColorScheme.get_light_primary_text()
    alert_status_color = ColorScheme.get_alert()

    Builder.load_string(TOOLBAR_VIEW_KV)

    def __init__(self, **kwargs):
        super(ToolbarView, self).__init__(**kwargs)
        self.current_status = ''
        self.register_event_type('on_main_menu')
        self.register_event_type('on_progress')
        self.register_event_type('on_data_rx')
        self.register_event_type('on_tele_status')
        self.register_event_type('on_status')
        self.register_event_type('on_activity')
        self._data_rx_decay = Clock.create_trigger(self.on_data_rx_decay, ToolbarView.TOOLBAR_DATA_RX_DURATION)
        self._activity_decay = Clock.create_trigger(self.on_activity_decay, ToolbarView.ACTIVITY_MESSAGE_LINGER_DURATION)
        self._progress_decay = Clock.create_trigger(self.on_progress_decay, ToolbarView.PROGRESS_COMPLETE_LINGER_DURATION)
        self._gps_decay = Clock.create_trigger(self._on_gps_decay, ToolbarView.STATUS_LINGER_DURATION)

    def on_status_pump(self, instance, value):
        value.add_listener(self.on_rc_status_updated)

    def on_rc_status_updated(self, status_data):
        self._update_track_status(status_data)
        self._update_gps_status(status_data)

    def on_activity(self, msg):
        self._set_activity_message(msg)
        self._activity_decay()

    def set_state_message(self, msg):
        self.ids.state.text = msg

    def _set_activity_message(self, msg):
        prog_status = self.ids.prog_status
        prog_status.text = msg

    def on_status(self, msg, isAlert):
        status_label = self.ids.prog_status
        status_label.text = msg
        self.current_status = msg
        if isAlert == True:
            status_label.text_color = self.alert_status_color
        else:
            status_label.text_color = self.normal_status_color

    def update_progress(self, value):
        self.ids.prog_status.value = value
        if value == 100:
            self._progress_decay()

    def on_progress(self, value):
        self.update_progress(value)

    def on_main_menu(self, instance, *args):
        pass

    def mainMenu(self):
        self.dispatch('on_main_menu', None)

    def on_progress_decay(self, dt):
        self.update_progress(0)
        self.ids.prog_status.text = self.current_status

    def on_activity_decay(self, dt):
        self._set_activity_message(self.current_status)

    def on_data_rx_decay(self, dt):
        self.ids.data_rx_status.color = ToolbarView.data_rx_color[int(False)]

    def on_data_rx(self, value):
        self._data_rx_decay.cancel()
        self.ids.data_rx_status.color = ToolbarView.data_rx_color[int(value)]
        self._data_rx_decay()

    def on_tele_status(self, status):
        try:
            self.ids.tele_status.color = self.telemetry_color[status]
        except:
            Logger.error("ToolbarView: Invalid telemetry status: " + str(status))

    def _on_gps_decay(self, dt):
        self.ids.gps_status.color = ToolbarView.gps_color[ToolbarView.GPS_NO_DATA]

    def _update_gps_status(self, status_data):
        self._gps_decay.cancel()
        gps_status = status_data['status']['GPS']
        gps_quality_code = gps_status['qual']
        gps_quality = ToolbarView.GPS_NO_DATA
        if gps_quality_code == 0:
            gps_quality = ToolbarView.GPS_NO_LOCK
        elif gps_quality_code == 1:
            gps_quality = ToolbarView.GPS_MARGINAL
        elif gps_quality_code >= 2:
            gps_quality = ToolbarView.GPS_HIGH_QUALITY

        gps_color = ToolbarView.gps_color[gps_quality]
        self.ids.gps_status.color = gps_color
        self._gps_decay()

    def _update_track_status(self, status_data):
        try:
            track_status = status_data['status']['track']
            detection_status = track_status['status']
            if detection_status == 0:
                track_status_msg = 'Searching for Track'
            elif detection_status == 1 and status_data['status']['track']['trackId'] == 0:
                track_status_msg = 'User defined Track'
            else:
                if track_status['trackId'] != 0:
                    track = self.track_manager.find_track_by_short_id(track_status['trackId'])
                    if track is None:
                        track_status_msg = '(Unknown Track)'
                    else:
                        track_status_msg = track.name
                        configuration_name = track.configuration
                        if configuration_name and len(configuration_name):
                            track_status_msg += ' (' + configuration_name + ')'
                else:
                    track_status_msg = 'No track detected'
            self.set_state_message(track_status_msg)
        except Exception as e:
            Logger.warn("ToolbarView: Could not retrieve track detection status " + str(e))

