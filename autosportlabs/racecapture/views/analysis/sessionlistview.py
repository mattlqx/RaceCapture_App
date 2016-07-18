#
# Race Capture App
#
# Copyright (C) 2014-2016 Autosport Labs
#
# This file is part of the Race Capture App
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the GNU General Public License for more details. You should
# have received a copy of the GNU General Public License along with
# this code. If not, see <http://www.gnu.org/licenses/>.

import kivy
kivy.require('1.9.1')
import json
from kivy.app import Builder
from kivy.properties import ListProperty
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.metrics import sp
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.anchorlayout import AnchorLayout
from kivy.adapters.listadapter import ListAdapter
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from autosportlabs.racecapture.datastore import DatastoreException, Filter
from autosportlabs.racecapture.views.util.viewutils import format_laptime
from autosportlabs.racecapture.views.analysis.markerevent import SourceRef
from autosportlabs.widgets.scrollcontainer import ScrollContainer
from autosportlabs.racecapture.theme.color import ColorScheme
from autosportlabs.racecapture.views.analysis.sessioneditorview import SessionEditorView
from autosportlabs.racecapture.views.util.alertview import confirmPopup, alertPopup, editor_popup
from autosportlabs.racecapture.views.util.viewutils import format_laptime
from fieldlabel import FieldLabel

Builder.load_file('autosportlabs/racecapture/views/analysis/sessionlistview.kv')

class NoSessionsAlert(FieldLabel):
    pass

class LapItemButton(ToggleButton):
    background_color_normal = ColorScheme.get_dark_background()
    background_color_down = ColorScheme.get_primary()

    def __init__(self, session, lap, laptime, **kwargs):
        super(LapItemButton, self).__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = self.background_color_normal
        self.session = session
        self.lap = lap
        self.laptime = laptime

    def on_state(self, instance, value):
        self.background_color = self.background_color_down if value == 'down' else self.background_color_normal

class Session(BoxLayout):
    data_items = ListProperty()

    def __init__(self, session, accordion, **kwargs):
        super(Session, self).__init__(**kwargs)
        self.session = session
        self.register_event_type('on_remove_session')
        self.register_event_type('on_edit_session')
        self.accordion = accordion

    @property
    def item_count(self):
        return len(self.ids.lap_list.children)

    def append_lap(self, session, lap, laptime):
        text = '{} :: {}'.format(int(lap), format_laptime(laptime))
        lapitem = LapItemButton(session=session, text=text, lap=lap, laptime=laptime)
        self.ids.lap_list.add_widget(lapitem)
        return lapitem

    def get_all_laps(self):
        '''
        Get a list of laps for this session
        :returns an array of SourceRef objects
        :type array 
        '''
        lap_list = self.ids.lap_list
        lap_refs = []
        for child in lap_list.children:
            if type(child) is LapItemButton:
                lap_refs.append(SourceRef(child.lap, child.session))

        return lap_refs

    def append_label(self, message):
        self.ids.lap_list.add_widget(FieldLabel(text=message, halign='center'))

    def on_remove_session(self, value):
        pass

    def on_edit_session(self, value):
        pass

    def edit_session(self):
        self.dispatch('on_edit_session', self.session.session_id)

    def remove_session(self):
        self.dispatch('on_remove_session', self.accordion)


class SessionAccordionItem(AccordionItem):
    def __init__(self, **kwargs):
        self.session_widget = None
        super(SessionAccordionItem, self).__init__(**kwargs)
        self.register_event_type('on_collapsed')

    def on_collapsed(self, value):
        pass

    def on_collapse(self, instance, value):
        super(SessionAccordionItem, self).on_collapse(instance, value)
        self.dispatch('on_collapsed', value)


class SessionListView(AnchorLayout):
    ITEM_HEIGHT = sp(40)
    SESSION_TITLE_HEIGHT = sp(45)

    def __init__(self, **kwargs):
        super(SessionListView, self).__init__(**kwargs)
        self.register_event_type('on_lap_selection')
        accordion = Accordion(orientation='vertical', size_hint=(1.0, None))
        sv = ScrollContainer(size_hint=(1.0, 1.0), do_scroll_x=False)
        self.selected_laps = {}
        self.current_laps = {}
        sv.add_widget(accordion)
        self._accordion = accordion
        self.add_widget(sv)
        self.sessions = []
        self.datastore = None
        self.settings = None
        self._save_timeout = None
        self._session_accordion_items = []

    def init_view(self):
        if self.settings and self.datastore:
            selection_settings_json = self.settings.userPrefs.get_pref('analysis_preferences', 'selected_sessions_laps',
                                                                       {"sessions": {}})
            selection_settings = json.loads(selection_settings_json)
            delete_sessions = []

            # Load sessions first, then select the session
            for session_id_str, session_info in selection_settings["sessions"].iteritems():
                session = self.datastore.get_session_by_id(int(session_id_str))
                if session:
                    self.append_session(session)
                else:
                    # If the session doesn't exist anymore, remove it from settings
                    delete_sessions.append(session_id_str)

            if len(delete_sessions) > 0:
                for session_id in delete_sessions:
                    selection_settings["sessions"].pop(session_id)

                # Resave loaded sessions and laps
                self._save_event()

            for session_id_str, session_info in selection_settings["sessions"].iteritems():
                session_id = int(session_id_str)

                laps = session_info["selected_laps"]

                for lap in laps:
                    self.select_lap(session_id, lap, True)

        else:
            Logger.error("SessionListView: init_view failed, missing settings or datastore object")

    def _save_settings(self):
        selection_settings = {"sessions": {}}

        for session in self.sessions:
            selection_settings["sessions"][str(session.session_id)] = {"selected_laps": []}

        for key, source_ref in self.selected_laps.iteritems():
            selection_settings["sessions"][str(source_ref.session)]["selected_laps"].append(source_ref.lap)

        selection_json = json.dumps(selection_settings)

        self.settings.userPrefs.set_pref('analysis_preferences', 'selected_sessions_laps', selection_json)
        Logger.info("SessionListView: saved selection: {}".format(selection_json))

    @property
    def selected_count(self):
        return len(self.selected_laps.values())

    def on_session_collapsed(self, instance, value):
        if value == False:
            session_count = len(self._accordion.children)
            # minimum space needed in case there are no laps in the session, plus the session toolbar
            item_count = max(instance.session_widget.item_count, 1) + 1
            session_items_height = (item_count * self.ITEM_HEIGHT)
            session_titles_height = (session_count * self.SESSION_TITLE_HEIGHT)
            accordion_height = session_items_height + session_titles_height
            self._accordion.height = accordion_height

    def append_session(self, session):
        self.sessions.append(session)
        item = SessionAccordionItem(title=session.name)
        session_view = Session(session, item)

        item.session_widget = session_view
        item.bind(on_collapsed=self.on_session_collapsed)

        session_view.bind(on_remove_session=self.remove_session)
        session_view.bind(on_edit_session=self.edit_session)
        self._session_accordion_items.append(item)
        item.add_widget(session_view)

        self._accordion.add_widget(item)

        laps = self.datastore.get_laps(session.session_id)

        if len(laps) == 0:
            session_view.append_label('No Laps')
        else:
            for lap in laps:
                self.append_lap(session_view, lap.lap, lap.lap_time)

        self._save_event()

        return session_view

    def session_deleted(self, session):
        """
        Handles when a session is deleted outside the scope of this view
        :param session: Session db object
        """
        for session_accordion in self._session_accordion_items:
            if session_accordion.session_widget.session.session_id == session.session_id:
                self.remove_session(session_accordion.session_widget, session_accordion)
                self._session_accordion_items.remove(session_accordion)
                break

    def edit_session(self, instance, session_id):
        def _on_answer(instance, answer):
            if answer:
                session_name = session_editor.session_name
                if not session_name or len(session_name) == 0:
                    alertPopup('Error', 'A session name must be specified')
                    return
                session.name = session_editor.session_name
                session.notes = session_editor.session_notes
                self.datastore.update_session(session)
            popup.dismiss()

        session = self.datastore.get_session_by_id(session_id, self.sessions)
        session_editor = SessionEditorView()
        session_editor.session_name = session.name
        session_editor.session_notes = session.notes
        popup = editor_popup('Edit Session', session_editor, _on_answer)

    def remove_session(self, instance, accordion):
        self.sessions.remove(instance.session)
        self._save_event()
        self.deselect_laps(instance.get_all_laps())
        self._accordion.remove_widget(accordion)

    def append_lap(self, session_view, lap, laptime):
        lapitem = session_view.append_lap(session_view.session.session_id, lap, laptime)
        source_key = str(SourceRef(lap, session_view.session.session_id))
        if self.selected_laps.get(source_key):
            lapitem.state = 'down'
        lapitem.bind(on_press=self.lap_selection)
        self.current_laps[source_key] = lapitem

    def on_lap_selection(self, *args):
        pass

    def _save_event(self):
        if self._save_timeout:
            self._save_timeout.cancel()

        self._save_timeout = Clock.schedule_once(lambda dt: self._save_settings(), 1)

    def lap_selection(self, instance):
        source_ref = SourceRef(instance.lap, instance.session)
        source_key = str(source_ref)
        selected = instance.state == 'down'
        if selected:
            self.selected_laps[source_key] = instance
        else:
            self.selected_laps.pop(source_key, None)
        Clock.schedule_once(lambda dt: self._notify_lap_selected(source_ref, selected))
        self._save_event()

    def _notify_lap_selected(self, source_ref, selected):
        '''
        Deselect all laps specified in the list of source refs
        :param source_ref the source reference for the lap
        :type SourceRef
        :param selected true if the lap is selected
        :type Boolean 
        '''
        self.dispatch('on_lap_selection', source_ref, selected)

    def clear_sessions(self):
        self.current_laps = {}
        self._accordion.clear_widgets()

    def select_lap(self, session_id, lap_id, selected):
        source_ref = SourceRef(lap_id, session_id)
        source_key = str(source_ref)
        lap_instance = self.current_laps.get(str(source_ref))
        if lap_instance:
            lap_instance.state = 'down' if selected else 'normal'
            self._notify_lap_selected(source_ref, True)

            # Save our state
            if selected:
                self.selected_laps[source_key] = source_ref
            else:
                self.selected_laps.pop(source_key, None)

            self._save_event()

    def deselect_other_laps(self, session):
        '''
        Deselect all laps except from the session specified
        :param session id
        :type session integer
        '''
        source_refs = []
        for instance in self.selected_laps.itervalues():
            if instance.session != session:
                source_refs.append(SourceRef(instance.lap, instance.session))
        self.deselect_laps(source_refs)
        self._save_event()

    def deselect_laps(self, source_refs):
        '''
        Deselect all laps specified in the list of source refs
        :param source_refs the list of source_refs
        :type source_refs array 
        '''
        for source_ref in source_refs:
            source_key = str(source_ref)
            instance = self.selected_laps.get(source_key)
            if instance:
                instance.state = 'normal'
                self.selected_laps.pop(source_key, None)
                self._notify_lap_selected(source_ref, False)
