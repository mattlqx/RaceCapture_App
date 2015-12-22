from threading import Thread, Lock
import urllib2
import os
import glob
import errno
import shutil
import json
from kivy.logger import Logger

class ResourceCache(object):
    
    READ_RETRIES = 3
    RETRY_DELAY = 1.0

    def __init__(self, settings, resource_url, resource_name, default_resource_dir, **kwargs):
        self.resources = {}
        self.resource_image_paths = {}
        
        self._resource_name = resource_name        
        self._default_resource_dir = default_resource_dir
        self.on_progress = lambda self, value: value
        self._resource_user_dir = '.'
        self.set_resource_user_dir(os.path.join(settings.get_default_data_dir(), resource_name))
        self._update_lock = Lock()
        self._check_load_defaults()
        self._load_resources()    

    def set_resource_user_dir(self, path):
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        self._resource_user_dir = path
        
    def _check_load_defaults(self):
        resource_list = os.listdir(self._resource_user_dir)
        if len(resource_list) == 0:
            Logger.info('ResourceCache: loading defaults for {}'.format(self._resource_name))
            default_list = os.listdir(self._default_resource_dir)
            for default in default_list:
                Logger.info('ResourceCache: loading default {} resource: {}'.format(self._resource_name, default ))
                #TODO: this may not be possible on android if the os's cp is not available to the app
                shutil.copy(os.path.join(self._default_resource_dir, default), self._resource_user_dir)
                
    def _load_resources(self):
        resource_list = glob.glob(os.path.join(self._resource_user_dir, '*.json'))
        for resource in resource_list:
            resource_path = open(os.path.join(self._resource_user_dir, resource))
            try:
                resource_json = json.load(resource_path)
                key = resource_json.get('id', None)
                if key:
                    self.resources[key] = resource_json
                    self.resource_image_paths[key] = os.path.join(self._resource_user_dir, '{}.jpg'.format(key))
                else:
                    Logger.error('ResourceCache: Invalid resource file; missing ID: {}'.format(str(resource_json)))
            except Exception as e:
                Logger.error('Failed to load resource {} : {}', resource_path, str(e))
                
                        
