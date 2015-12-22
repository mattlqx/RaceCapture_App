from threading import Thread, Lock
import urllib2
import os
import errno
import shutil

class ResourceCache(object):
    
    READ_RETRIES = 3
    RETRY_DELAY = 1.0

    def __init__(self, user_dir, resource_url, resource_name, default_resource_dir, **kwargs):
        self.default_resource_dir = default_resource_dir
        self.on_progress = lambda self, value: value
        self.resource_user_dir = '.'
        self.set_resource_user_dir(os.path.join(user_dir, resource_name))
        self.update_lock = Lock()    

    def set_resource_user_dir(self, path):
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        self.resource_user_dir = path
        
    def load_defaults(self):
        resource_list = os.listdir(self.resource_user_dir)
        if len(resource_list) == 0:
            default_list = os.listdir(self.default_resource_dir)
            for default in default_list:
                shutil.copy(os.path.join(default, self.default_resource_dir), self.resource_user_dir)

