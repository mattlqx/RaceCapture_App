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
from kivy.logger import Logger
from utils import is_mobile_platform, is_android
from kivy.clock import mainthread, Clock
from kivy.logger import Logger
from autosportlabs.racecapture.config.rcpconfig import GpsConfig
from autosportlabs.racecapture.geo.geopoint import GeoPoint
from kivy.event import EventDispatcher
if is_mobile_platform():
    from plyer import gps
    if is_android():
        from jnius import autoclass


class GeoProvider(EventDispatcher):
    """
    Provides a unified source of GPS data- 
    either from RaceCapture or an internal phone GPS sensor.
    """
    GPS_SOURCE_NONE = 0
    GPS_SOURCE_RACECAPTURE = 1
    GPS_SOURCE_INTERNAL = 2
    INTERNAL_GPS_UPDATE_INTERVAL_SEC = 0.5

    def __init__(self, rc_api, databus, **kwargs):
        super(GeoProvider, self).__init__(**kwargs)
        self._internal_gps_conn = None
        self._databus = databus
        self._rc_api = rc_api

        self._internal_gps_active = False
        self._rc_gps_quality = GpsConfig.GPS_QUALITY_NO_FIX
        self._last_internal_location_time = 0
        self._current_gps_source = GeoProvider.GPS_SOURCE_NONE

        databus.addSampleListener(self._on_sample)
        self.register_event_type('on_location')
        self.register_event_type('on_internal_gps_available')
        self.register_event_type('on_gps_source')
        if is_android():  # only support android for now
            self._start_internal_gps()

    def on_location(self, point):
        pass

    def on_internal_gps_available(self, available):
        pass

    def on_gps_source(self, source):
        pass

    @property
    def location_source_internal(self):
        """
        Indicates if location data is currently provided by an internal source
        :return True if source is internal
        """
        return self._internal_gps_active and self._should_use_internal_source

    @property
    def rc_connection_active(self):
        """
        Indicates if the RaceCapture connection is currently active
        """
        return self._rc_api.connected

    @property
    def _should_use_internal_source(self):
        return not self._rc_api.connected or self._rc_gps_quality < GpsConfig.GPS_QUALITY_2D

    def _on_sample(self, sample):
        gps_quality = sample.get('GPSQual')
        latitude = sample.get('Latitude')
        longitude = sample.get('Longitude')

        if self._rc_api.connected and gps_quality >= GpsConfig.GPS_QUALITY_2D:
            self._update_current_location(GeoPoint.fromPoint(latitude, longitude), GeoProvider.GPS_SOURCE_RACECAPTURE)

        self._rc_gps_quality = gps_quality

    def _update_current_location(self, point, gps_source):
        self.dispatch('on_location', point)
        if gps_source != self._current_gps_source:
            # If we've switched between RaceCapture and internal device GPS
            # or vice-versa, send an event
            self.dispatch('on_gps_source', gps_source)
            self._current_gps_source = gps_source

    def shutdown(self):
        """
        Shutdown / cleanup GeoProvider
        """
        self._stop_internal_gps()
        self._databus.remove_sample_listener(self._on_sample)
        Clock.unschedule(self._check_internal_gps_update)

    def _start_internal_gps(self):
        started = False
        gps_conn = autoclass('com.autosportlabs.racecapture.GpsConnection')
        self._internal_gps_conn = gps_conn.createInstance();
        configured = self._internal_gps_conn.configure()
        if configured:
            started = self._internal_gps_conn.start()
        Logger.info('GeoProvider: internal GPS started: {}'.format(started))
        self.dispatch('on_internal_gps_available', started)
        if started:
            Clock.schedule_interval(self._check_internal_gps_update, GeoProvider.INTERNAL_GPS_UPDATE_INTERVAL_SEC)

    def _check_internal_gps_update(self, *args):
        location = self._internal_gps_conn.getCurrentLocation()
        if not location:
            return
        location_time = location.getTime()
        if location_time != self._last_internal_location_time:
            self._internal_gps_active = True
            if self._should_use_internal_source:
                point = GeoPoint.fromPoint(location.getLatitude(), location.getLongitude())
                self._update_current_location(point, GeoProvider.GPS_SOURCE_INTERNAL)
            self._last_internal_location_time = location_time

    def _stop_internal_gps(self):
        Logger.info('GeoProvider: stopping internal GPS')
        if self._internal_gps_conn is not None:
            self._internal_gps_conn.stop()
        self._internal_gps_active = False
