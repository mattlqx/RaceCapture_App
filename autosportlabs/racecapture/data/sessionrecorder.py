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

from datetime import datetime
from autosportlabs.racecapture.datastore import Session
from kivy.logger import Logger


class SessionRecorder(object):
    """
    Handles starting/stopping session recording and other related tasks
    """

    # Main app views that the SessionRecorder should start recording when displayed
    RECORDING_VIEWS = ['dash']

    def __init__(self, datastore, databus, rcpapi, track_manager=None, current_view=None):
        """
        Initializer.
        :param datastore: Datastore for saving data
        :param databus: Databus for listening for data
        :param rcpapi: RcpApi object for listening for connect/disconnect events
        :return:
        """
        self._datastore = datastore
        self._databus = databus
        self._rcapi = rcpapi
        self._channels = None
        self.recording = False
        self._current_session = None
        self._track_manager = track_manager
        self._meta = None
        self._rc_connected = False
        self._current_view = current_view

        self._rcapi.add_connect_listener(self._on_rc_connected)
        self._rcapi.add_disconnect_listener(self._on_rc_disconnected)
        self._databus.addMetaListener(self._on_meta)
        self._databus.addSampleListener(self._on_sample)

        metas = self._databus.getMeta()

        if metas:
            self._on_meta(metas)

        self._check_should_record()

    def start(self, session_name=None):
        """
        Starts recording a new session.
        :param session_name: Name of session
        :type session_name: String
        :return: None
        """
        Logger.info("SessionRecorder: starting new session")

        session_id = self._datastore.create_session(self._create_session_name())
        self._current_session = self._datastore.get_session_by_id(session_id)
        self.recording = True

    def stop(self):
        """
        Stops recording the current session, does any additional post-processing necessary
        :return: None
        """
        Logger.info("SessionRecorder: stopping session")
        self.recording = False
        self._current_session = None

    @property
    def _should_record(self):
        if self._current_view not in SessionRecorder.RECORDING_VIEWS:
            return False

        if not self._rc_connected:
            return False

        if not self._channels:
            return False

        return True

    def _check_should_record(self):
        if self._should_record and not self.recording:
            self.start()
        elif not self._should_record and self.recording:
            self.stop()

    def _create_session_name(self):
        """
        Creates a session name
        :return: String name
        """
        date = datetime.now()

        date_string = date.strftime("%x %X%p")

        return date_string

    def on_view_change(self, view_name):
        """
        View change listener, if the view being displayed is a view we want to record for, start recording.
        If not and we are currently recording, stop
        :param view_name:
        :return:
        """
        self._current_view = view_name
        self._check_should_record()

    def _save_sample(self, sample):
        pass

    def _on_meta(self, metas):
        """
        Event listener for new meta (channel) information
        :param metas:
        :return:
        """
        self._channels = metas
        self._check_should_record()

    def _on_sample(self, sample):
        """
        Sample listener for data from RC. Saves data to Datastore if a session is being recorded
        :param sample:
        :return:
        """
        if self.recording:
            self._save_sample(sample)

    def _on_rc_connected(self):
        """
        Event listener for when RC is connected
        :return:
        """
        self._rc_connected = True
        self._check_should_record()

    def _on_rc_disconnected(self):
        """
        Event listener for when RC is disconnected
        :return:
        """
        self._rc_connected = False
        self.stop()
