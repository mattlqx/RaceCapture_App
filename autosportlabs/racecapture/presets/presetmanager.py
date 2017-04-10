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

import uuid
from datetime import datetime
import json
import time
import copy
import errno
import string
from threading import Thread, Lock
import urllib2
import os
import traceback
from StringIO import StringIO
import gzip
import zipfile
from autosportlabs.util.timeutil import time_to_epoch, epoch_to_time
from kivy.logger import Logger


class Preset(object):
    """Object to represent a preset item
    """
    def __init__(self):
        pass

class PresetManager(object):
    """Manages fetching and updating Presets 
    """
    RCP_PRESET_URL = 'https://podium.live/api/v1/venues'
    READ_RETRIES = 3
    RETRY_DELAY = 1.0
    PRESET_DOWNLOAD_TIMEOUT = 30

    def __init__(self, **kwargs):
        self.on_progress = lambda self, value: value
        self.presets_user_dir = '.'
        self.presets_user_subdir = '/presets'
        self.set_presets_user_dir(kwargs.get('user_dir', self.presets_user_dir) + self.presets_user_subdir)
        self.base_dir = kwargs.get('base_dir')

        self.update_lock = Lock()
        self.presets = {}

    def set_presets_user_dir(self, path):
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        self.presets_user_dir = path

    def init(self, progress_cb, success_cb, fail_cb):
        self.load_presets(progress_cb, success_cb, fail_cb)

    def load_json(self, uri):
        """Semi-generic method for fetching JSON data
        """
        retries = 0
        while retries < self.READ_RETRIES:
            try:
                opener = urllib2.build_opener()
                opener.addheaders = [('Accept', 'application/json'), ('Accept-encoding', 'gzip')]
                response = opener.open(uri, timeout=PresetManager.PRESET_DOWNLOAD_TIMEOUT)
                data = response.read()
                if response.info().get('Content-Encoding') == 'gzip':
                    string_buffer = StringIO(data)
                    data = gzip.GzipFile(fileobj=string_buffer).read()
                j = json.loads(data)
                return j
            except Exception as detail:
                Logger.warning('PresetManager: Failed to read: from {} : {}'.format(uri, traceback.format_exc()))
                if retries < self.READ_RETRIES:
                    Logger.warning('PresetManager: retrying in ' + str(self.RETRY_DELAY) + ' seconds...')
                    retries += 1
                    time.sleep(self.RETRY_DELAY)
        raise Exception('Error reading json doc from: ' + uri)

    def download_all_presets(self):
        """Downloads all presets, then turns them into Preset objects
        """
        presets = {}
        venues = self.fetch_preset_list(True)

        for venue in venues:
                preset = Preset()
                preset.from_dict(venue)
                presets[preset.preset_id] = preset

        return presets

    def fetch_preset_list(self, full_response=False):
        """Fetches all venues from RCL's API and returns them as an array of dicts. RCL's API normally returns minimal
        object information when listing multiple objects. The 'full_response' arg tells this function to expand
        all objects to contain all their data. This allows us to quickly get basic information about tracks or pull
        down everything if we have no tracks locally.
        """

        total_venues = None
        next_uri = self.RCP_PRESET_URL + "?start=0&per_page=100"

        if full_response:
            next_uri += '&expand=1'

        venues_list = []

        while next_uri:
            Logger.info('PresetManager: Fetching venue data: {}'.format(next_uri))
            response = self.load_json(next_uri)
            try:
                if total_venues is None:
                    total_venues = int(response.get('total', None))
                    if total_venues is None:
                        raise MissingKeyException('Venue list JSON: could not get total venue count')

                venues = response.get('venues', None)

                if venues is None:
                    raise MissingKeyException('Venue list JSON: could not get venue list')

                venues_list += venues
                next_uri = response.get('nextURI')

            except MissingKeyException as detail:
                Logger.error('PresetManager: Malformed venue JSON from url ' + next_uri + '; json =  ' + str(response) +
                             ' ' + str(detail))

        Logger.info('PresetManager: fetched list of ' + str(len(venues_list)) + ' tracks')

        if not total_venues == len(venues_list):
            Logger.warning('PresetManager: track list count does not reflect downloaded track list size ' + str(total_venues) + '/' + str(len(venues_list)))

        return venues_list

    def download_preset(self, preset_id):
        preset_url = self.RCP_PRESET_URL + '/' + preset_id
        response = self.load_json(preset_url)
        preset = Preset()
        try:
            preset_json = response.get('preset')
            preset.from_dict(preset_json)
            return copy.deepcopy(preset)
        except Warning:
            return None

    def add_preset(self, preset):
        """ Add the specified preset
        :param preset the preset to add
        :type preset TrackMap
        """
        self.save_preset(preset)
        self.presets[preset.preset_id] = preset

    def save_preset(self, preset):
        path = os.path.join(self.presets_user_dir, preset.preset_id + '.json')
        track_json_string = json.dumps(preset.to_dict(), sort_keys=True, indent=2, separators=(',', ': '))
        with open(path, 'w') as text_file:
            text_file.write(track_json_string)

    def load_current_tracks_worker(self, success_cb, fail_cb, progress_cb=None):
        """Method for loading local tracks files in a separate thread
        """
        try:
            self.update_lock.acquire()
            self.load_presets(progress_cb)
            success_cb()
        except Exception as detail:
            Logger.exception('')
            fail_cb(detail)
        finally:
            self.update_lock.release()

    def check_load_default_presets(self):
        preset_file_names = os.listdir(self.presets_user_dir)
        if (len(preset_file_names) == 0):
            Logger.info("PresetManager: No presets found; loading defaults")
            try:
                with zipfile.ZipFile(os.path.join(self.base_dir, 'defaults', 'default_presets.zip'), 'r') as z:
                    z.extractall(self.presets_user_dir)
            except Exception as e:
                Logger.error("PresetManager: Could not load default presets: {}".format(e))

    def load_presets(self, progress_cb=None, success_cb=None, fail_cb=None):
        """Loads tracks from local files. If called with success and fail callbacks it sets up a separate thread
        """
        if success_cb and fail_cb:
            t = Thread(target=self.load_current_tracks_worker, args=(success_cb, fail_cb, progress_cb))
            t.daemon = True
            t.start()
        else:
            preset_file_names = os.listdir(self.presets_user_dir)
            self.presets.clear()
            track_count = len(preset_file_names)
            count = 0

            for trackPath in preset_file_names:
                try:
                    json_data = open(os.path.join(self.presets_user_dir, trackPath))
                    preset_dict = json.load(json_data)
                    resave = False

                    # Backwards compatible-check for old format of preset files
                    if 'venue' in preset_dict:
                        preset_dict = preset_dict.get('venue')
                        resave = True

                    if preset_dict is not None:
                        preset = Preset()
                        preset.from_dict(preset_dict)
                        if resave:
                            self.save_preset(preset)

                        self.presets[preset.preset_id] = preset
                        count += 1
                        if progress_cb:
                            progress_cb(count=preset.count, total=track_count, message=preset.name)
                except Exception as detail:
                    Logger.warning('PresetManager: failed to read preset file ' + trackPath + ';\n' + str(detail))

    def update_all_presets_worker(self, success_cb, fail_cb, progress_cb=None):
        """Method for updating all tracks in a separate thread
        """
        try:
            self.update_lock.acquire()
            self.refresh(progress_cb)
            success_cb()
        except Exception as detail:
            Logger.exception('')
            fail_cb(detail)
        finally:
            self.update_lock.release()

    def refresh(self, progress_cb=None, success_cb=None, fail_cb=None):
        """Refreshes all presets. If success and fail callbacks are provided, sets up a new thread.
        If no presets are saved locally, it will fetch all preset data from RCL and save it.
        If there are tracks saved locally, it will fetch a minimal amount of data from RCL and only download
        all data for a track if the track has been updated
        """
        progress_cb(message="Fetching list of Presets...")
        if success_cb and fail_cb:
            t = Thread(target=self.update_all_presets_worker, args=(success_cb, fail_cb, progress_cb))
            t.daemon = True
            t.start()
        else:
            if len(self.presets) == 0:
                Logger.info("PresetManager: No presets found locally, fetching all presets")
                preset_list = self.download_all_presets()
                count = 0
                total = len(preset_list)

                for preset_id, track in preset_list.iteritems():
                    count += 1
                    if progress_cb:
                        progress_cb(count=count, total=total, message=track.name)
                    self.save_preset(track)
                    self.presets[preset_id] = track
            else:
                Logger.info("PresetManager: refreshing presets")
                venues = self.fetch_preset_list()

                preset_count = len(venues)
                count = 0

                for venue in venues:
                    update = False
                    count += 1
                    venue_id = venue.get('id')

                    if self.presets.get(venue_id) is None:
                        Logger.info('PresetManager: new track detected ' + venue_id)
                        update = True
                    elif not self.presets[venue_id].updated == venue['updated']:
                        Logger.info('PresetManager: existing preset changed ' + venue_id)
                        update = True

                    if update:
                        updated_preset = self.download_preset(venue_id)
                        if updated_preset is not None:
                            self.save_preset(updated_preset)
                            self.presets[venue_id] = updated_preset
                            if progress_cb:
                                progress_cb(count=count, total=preset_count, message=updated_preset.name)
                    else:
                        progress_cb(count=count, total=preset_count)


class MissingKeyException(Exception):
    """Exception for if a key is missing from a dict
    """
    pass
