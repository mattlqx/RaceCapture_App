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
from plyer import gps
from kivy.clock import mainthread
from kivy.logger import Logger
from autosportlabs.racecapture.config.rcpconfig import GpsConfig
from autosportlabs.racecapture.geo.geopoint import GeoPoint
from kivy.event import EventDispatcher

class GeoProvider(EventDispatcher):
    INTERNAL_GPS_MIN_DISTANCE = 0
    INTERNAL_GPS_MIN_TIME = 1000

    def __init__(self, rc_api, databus, **kwargs):
        super(GeoProvider, self).__init__(**kwargs)
        self._internal_gps_supported = False
        self._internal_gps_active = False
        self._init_internal_gps()
        self._databus = databus
        self._rc_api = rc_api
        databus.addSampleListener(self._on_sample)
        self.register_event_type('on_location')
        self._init_internal_gps()

    def on_location(self, point):
        pass

    @property
    def location_source_internal(self):
        """
        Indicates if location data is currently provided by an internal source
        :return True if source is internal
        """
        return self._internal_gps_active

    @property
    def rc_connection_active(self):
        """
        Indicates if the RaceCapture connection is currently active
        """
        return self._rc_api.connected

    def _on_sample(self, sample):
        gps_quality = sample.get('GPSQual')
        latitude = sample.get('Latitude')
        longitude = sample.get('Longitude')

        if self._rc_api.connected and gps_quality >= GpsConfig.GPS_QUALITY_2D:
            self._update_current_location(GeoPoint.fromPoint(latitude, longitude))
            if self._internal_gps_active:
                self._stop_internal_gps()
        else:
            if self._internal_gps_supported and not self._internal_gps_active:
                self._start_internal_gps()

    def _update_current_location(self, point):
        self.dispatch('on_location', point)

    @mainthread
    def _on_internal_gps_location(self, **kwargs):
        print('internal gps location: ' + str(kwargs))
        latitude = kwargs.get('lat')
        longitude = lwargs.get('lon')
        self._update_current_location(GeoPoint.fromPoint(latitude, longitude))

    @mainthread
    def _on_internal_gps_status(self, **kwargs):
        print('internal gps status: ' + str(kwargs))

    def shutdown(self):
        self._stop_internal_gps()
        self._databus.remove_sample_listener(self._on_sample)

    def _init_internal_gps(self):
        self._internal_gps_supported = False
        return
        try:
            gps.configure(on_location=self._on_internal_gps_location, on_status=self._on_internal_gps_status)
            self._internal_gps_supported = True
            Logger.info('GeoProvider: internal GPS configured')
        except NotImplementedError:
            self._internal_gps_supported = False
            Logger.info('GeoProvider: Internal GPS is not implemented for your platform')

    def _start_internal_gps(self):
        return
        Logger.info('GeoProvider: starting internal GPS')
        gps.start()
        self._internal_gps_active = True

    def _stop_internal_gps(self):
        Logger.info('GeoProvider: stopping internal GPS')
        gps.stop()
        self._internal_gps_active = False
