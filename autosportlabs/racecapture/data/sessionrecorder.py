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

from threading import Thread
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.event import EventDispatcher
from autosportlabs.util.timeutil import format_date
from autosportlabs.racecapture.config.rcpconfig import GpsSample
from autosportlabs.racecapture.geo.geopoint import GeoPoint
from autosportlabs.util.threadutil import safe_thread_exit
import copy
import Queue
from Queue import Empty


class SessionRecorder(EventDispatcher) :
    """
    Handles starting/stopping session recording and other related tasks
    """

    # Main app views that the SessionRecorder should start recording when displayed
    RECORDING_VIEWS = ['dash']

    def __init__(self, datastore, databus, rcpapi, settings, track_manager=None, status_pump=None, stop_delay=60):
        """
        Initializer.
        :param datastore: Datastore for saving data
        :param databus: Databus for listening for data
        :param rcpapi: RcpApi object for listening for connect/disconnect events
        :return:
        """
        self._sample_queue = Queue.Queue()
        self._recorder_thread = None
        
        self._datastore = datastore
        self._databus = databus
        self._rcapi = rcpapi
        self._settings = settings
        self._channels = None
        self.recording = False
        self._current_session_id = None
        self._track_manager = track_manager
        self._meta = None
        self._rc_connected = False
        self._current_view = None
        status_pump.add_listener(self.status_updated)
        self._stop_delay = stop_delay
        self._stop_timer = Clock.create_trigger(self._actual_stop, self._stop_delay)

        self._rcapi.add_connect_listener(self._on_rc_connected)
        self._rcapi.add_disconnect_listener(self._on_rc_disconnected)
        self._databus.addMetaListener(self._on_meta)
        self._databus.addSampleListener(self._on_sample)
        self._gps_sample = GpsSample()
        metas = self._databus.getMeta()
        if metas:
            self._on_meta(metas)

        self._check_should_record()

        self.register_event_type('on_recording')

    def status_updated(self, status):
        try:
            status = status['status']['GPS']
            quality = status['qual']
            latitude = status['lat']
            longitude = status['lon']
            self._gps_sample.gps_qual = quality
            self._gps_sample.latitude = latitude
            self._gps_sample.longitude = longitude
        except KeyError:
            pass

    def on_recording(self, recording):
        pass

    def start(self, session_name=None):
        """
        Starts recording a new session.
        :param session_name: Name of session
        :type session_name: String
        :return: None
        """
        if self._stop_timer.is_triggered:
            Logger.info("SessionRecorder: cancelling stop timer")
            self._stop_timer.cancel()

        if not self.recording:
            Logger.info("SessionRecorder: starting new session")
            self._current_session_id = self._datastore.init_session(self._create_session_name(), self._channels)
            self.dispatch('on_recording', True)
            self.recording = True
            
            t = Thread(target=self._session_recorder_worker)
            t.start()
            self._recorder_thread = t
            

    def stop(self, stop_now=False):
        """
        Sets a timer that will stop the current session after a period of time.  If start is called
        before the timer fires then it will be canceled instead.
        :param stop_now True if you want it to stop immediately
        :type stop_now bool 
        :return: None
        """
        if (self.recording and not self._stop_timer.is_triggered) or stop_now:
            if self._stop_delay > 0 and not stop_now:
                Logger.info("SessionRecorder: scheduling session stop")
                self._stop_timer()
            else:
                self._stop_timer.cancel()
                self._actual_stop(0)

    def _actual_stop(self, dt):
        """
        Stops recording the current session, does any additional post-processing necessary
        :return: None
        """        
        if self.recording:
            Logger.info("SessionRecorder: stopping session")
            self.recording = False
            if self._recorder_thread is not None:
                self._recorder_thread.join()
            self._recorder_thread = None
            
            self._current_session_id = None            
            self.dispatch('on_recording', False)

    @property
    def _should_record(self):

        if self._settings.userPrefs.get_pref('preferences', 'record_session') == '0':
            return False

        if self._current_view not in SessionRecorder.RECORDING_VIEWS:
            return False

        if not self._rc_connected:
            return False

        if not self._channels:
            return False

        return True

    def _check_should_record(self):
        if self._should_record:
            self.start()
        elif not self._should_record:
            self.stop()

    def _create_session_name(self):
        """
        Creates a session name attempting to use the nearby venue name first, 
        then falling to a date stamp
        :return: String name
        """
        nearby_venues = self._track_manager.find_nearby_tracks(GeoPoint.fromPoint(self._gps_sample.latitude, self._gps_sample.longitude))
        session_names = [c.name for c in self._datastore.get_sessions()]

        # use the venue name if found nearby, otherwise use a date
        prefix = None if len(nearby_venues) == 0 else nearby_venues[0].name
        if prefix is None:
            prefix = format_date()

        # now find a unique name
        index = 1
        while True:
            session_name = '{} - {}'.format(prefix, index)
            if session_name not in session_names:
                return session_name
            index += 1

    def on_view_change(self, view_name):
        """
        View change listener, if the view being displayed is a view we want to record for, start recording.
        If not and we are currently recording, stop
        :param view_name:
        :return:
        """
        self._current_view = view_name
        self._check_should_record()

    def _session_recorder_worker(self):
        Logger.info('SessionRecorder: session recorder worker starting')
        try:
            #reset our sample data dict
            sample_data = {}
            index = 0
            qsize = 0
            sample_queue = self._sample_queue
            while self.recording or qsize > 0: #will drain the queue before exiting thread
                try:
                    sample = sample_queue.get(True, 0.5)
                    # Merging previous sample with new data to desparsify the data
                    sample_data.update(sample)
                    self._datastore.insert_sample(sample_data, self._current_session_id)
                    qsize = sample_queue.qsize()
                    if index % 100 == 0 and qsize > 0:
                        Logger.info('SessionRecorder: queue backlog: {}'.format(qsize))
                    index +=1
                except Empty:
                    pass
        except Exception as e:
            Logger.error('SessionRecorder: Exception in session recorder worker ' + str(e))
        finally:
            safe_thread_exit()
            
        Logger.info('SessionRecorder: session recorder worker ending')            
            
    def _channel_metas_same(self, metas):
        # determine if the provided channel metas have the same channel names as the current
        current_metas = self._channels
        if current_metas is None:
            return False
        return sorted(current_metas.keys()) == sorted(metas.keys())

    def _on_meta(self, metas):
        """
        Event listener for new meta (channel) information
        :param metas:
        :return:
        """
        if not self._channel_metas_same(metas):
            Logger.info("SessionRecorder: ChannelMeta changed - stop recording")
            self.stop(stop_now=True)
        self._channels = copy.deepcopy(dict(metas))
        self._check_should_record()

    def _on_sample(self, sample):
        """
        Sample listener for data from RC. Saves data to Datastore if a session is being recorded
        :param sample:
        :return:
        """
        if not self.recording:
            return
        
        self._sample_queue.put(copy.deepcopy(sample))
            

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
        self._actual_stop(0)
