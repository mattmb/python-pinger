import os
import glob
from lib.plugins import PluginMount
import logging

class Handler(object):
    __metaclass__ = PluginMount
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    def send(self, url, message, details=None):
        self.log.info(message)
        self.log.info(details)

    def down_alert(self, url, message, details):
        self.send(self, url, message, details)

    def up_alert(self, url, message):
        self.send(self, url, message)

modules = glob.glob(os.path.dirname(__file__)+"/*.py")
__all__ = [ os.path.basename(f)[:-3] for f in modules]
print __all__
from handlers import *
