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
from autosportlabs.racecapture.datastore import DataStore, Filter, timing
from autosportlabs.racecapture.geo.geopoint import GeoPoint
from kivy.logger import Logger
from kivy.clock import Clock

class ChannelStats(object):
    def __init__(self, **kwargs):
        self.values = kwargs.get('values')
        self.min = kwargs.get('min')
        self.max = kwargs.get('max')
        self.avg = kwargs.get('avg')

class ChannelData(object):
    values = None
    channel = None
    min = 0
    max = 0
    source = None

    def __init__(self, **kwargs):
        self.values = kwargs.get('values', None)
        self.channel = kwargs.get('channel', None)
        self.min = kwargs.get('min', 0)
        self.max = kwargs.get('max', 0)
        self.source = kwargs.get('source', None)

class CachingAnalysisDatastore(DataStore):

    def __init__(self, **kwargs):
        super(CachingAnalysisDatastore, self).__init__(**kwargs)
        self._channel_data_cache = {}
        self._session_location_cache = {}
        self._session_info_cache = {}

    @property
    def session_info_cache(self):
        """
        Provides a cached representation of the list of sessions and laps.
        @return dict of Session objects
        """
        session_info = self._session_info_cache

        # Populate our cache if necessary
        if len(session_info.keys()) == 0:
            self._refresh_session_data()
        return session_info

    @timing
    def _query_channel_data(self, source_ref, channels, combined_channel_data):
        Logger.info('CachingAnalysisDatastore: querying {} {}'.format(source_ref, channels))
        lap = source_ref.lap
        session = source_ref.session
        f = Filter().eq('CurrentLap', lap)
        dataset = self.query(sessions=[session], channels=channels, data_filter=f)
        records = dataset.fetch_records()

        for index in range(len(channels)):
            channel = channels[index]
            values = []
            for record in records:
                # pluck out just the channel value
                values.append(record[1 + index])

            channel_meta = self.get_channel(channel)
            channel_data = ChannelData(values=values, channel=channel, min=channel_meta.min, max=channel_meta.max, source=source_ref)
            combined_channel_data[channel] = channel_data

    def _get_channel_data(self, source_ref, channels, callback):
        '''
        Retrieve cached or query channel data as appropriate.
        '''
        source_key = str(source_ref)
        channel_data = self._channel_data_cache.get(str(source_key))
        if not channel_data:
            channel_data = {}
            self._channel_data_cache[source_key] = channel_data

        channels_to_query = []
        for channel in channels:
            channel_d = channel_data.get(channel)
            if not channel_d:
                channels_to_query.append(channel)

        if len(channels_to_query) > 0:
            channel_d = self._query_channel_data(source_ref, channels_to_query, channel_data)

        Clock.schedule_once(lambda dt: callback(channel_data))

    @timing
    def import_datalog(self, path, name, notes='', progress_cb=None):
        session_id = super(CachingAnalysisDatastore, self).import_datalog(path, name, notes, progress_cb)
        self._refresh_session_data()
        return session_id

    def delete_session(self, session_id):
        super(CachingAnalysisDatastore, self).delete_session(session_id)
        self._refresh_session_data()

    @timing
    def _refresh_session_data(self):
        self._session_info_cache.clear()
        sessions = self.get_sessions()
        for session in sessions:
            session_id = session.session_id
            laps_dict = self.get_laps(session_id)
            self._session_info_cache[session_id] = laps_dict

    def get_cached_lap_info(self, source_ref):
        """
        Retrieves cached information for a specific lap
        :param source_ref the session / lap reference
        :type source_ref SourceRef
        :return a Lap object representing the lap information if found; None if not found
        """
        lap = None
        session = self.session_info_cache.get(source_ref.session)
        if session is not None:
            lap = session.get(source_ref.lap)
        return lap

    def get_cached_session_laps(self, session_id):
        """
        Returns an ordered Dictionary of Lap objects for the specified session
        :param session_id the session to get
        :type session_id int
        :return an OrderedDict of Lap objects for the specified session. Key is lap id
        """
        laps = self.session_info_cache.get(session_id)
        if laps is None:  # if it's not in the cache it could be because the cache is stale
            self._refresh_session_data()
            laps = self.session_info_cache.get(session_id)
        return laps

    def delete_session(self, session_id):
        """
        Deletes the specified session. 
        Removes the session from the local cache as needed.
        :param session_id The session to delete
        :type session_id int
        """
        super(CachingAnalysisDatastore, self).delete_session(session_id)
        self.session_info_cache.pop(session_id, None)

    def get_channel_data(self, source_ref, channels, callback):
        '''
        Retrieve channel data for the specified source (session / lap combo).
        Data is returned with the specified callback function.
        '''
        self._get_channel_data(source_ref, channels, callback)

    def get_location_data(self, source_ref, callback=None):
        '''
        Retrieve location data for the specified source (session / lap combo). 
        If immediately available, return it, otherwise use the callback for a later return after querying.
        '''
        cached = self._session_location_cache.get(str(source_ref))
        if callback:
            if cached:
                callback(cached)
            else:
                self._get_location_data(source_ref, callback)
        return cached

    def _get_location_data(self, source_ref, callback):
        '''
        Retrieve cached or query Location data as appropriate.
        '''
        session = source_ref.session
        lap = source_ref.lap
        f = Filter().neq('Latitude', 0).and_().neq('Longitude', 0).eq("CurrentLap", lap)
        dataset = self.query(sessions=[session],
                                        channels=["Latitude", "Longitude"],
                                        data_filter=f)
        records = dataset.fetch_records()
        cache = []
        for r in records:
            lat = r[1]
            lon = r[2]
            cache.append(GeoPoint.fromPoint(lat, lon))
        self._session_location_cache[str(source_ref)] = cache

        Clock.schedule_once(lambda dt: callback(cache))


