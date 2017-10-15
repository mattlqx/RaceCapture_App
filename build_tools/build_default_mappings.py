#!/usr/bin/python
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

from autosportlabs.racecapture.presets.presetmanager import PresetManager
import json
import zipfile
import StringIO
import os
from autosportlabs.racecapture.presets.presetmanager import PresetManager

tm = PresetManager()

tracks = tm.download_all_presets()

mf = StringIO.StringIO()
with zipfile.ZipFile(mf, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
    for track_id, track in tracks.iteritems():
        track_json_string = json.dumps(track.to_dict(), sort_keys=True, indent=2, separators=(',', ': '))
        zf.writestr('{}.json'.format(track_id), track_json_string)

archive_path = os.path.join('defaults', 'default_mappings.zip')

with open(archive_path, 'wb') as f:
    f.write(mf.getvalue())
    
tm.refresh()
