#
# Race Capture App
#
# Copyright (C) 2014-2017 Autosport Labs
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

from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.app import Builder
from autosportlabs.widgets.filebrowser import FileBrowser
from utils import kvFind

Builder.load_file('autosportlabs/racecapture/views/file/loaddialogview.kv')

class LoadDialog(FloatLayout):
    def __init__(self, **kwargs):
        super(LoadDialog, self).__init__(**kwargs)
        ok = kwargs.get('ok', None)
        cancel = kwargs.get('cancel', None)
        user_path = kwargs.get('user_path', '.')
            
        browser = kvFind(self, 'rcid', 'browser')
        browser.path = user_path
        browser.filters = kwargs.get('filters', ['*'])        
        if ok: browser.bind(on_success = ok)
        if cancel: browser.bind(on_canceled = cancel)
            
            
