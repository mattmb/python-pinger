import os
import glob
from lib.plugins import PluginMount
import logging

class Handler(object):
    __metaclass__ = PluginMount
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    def send(self, message, details):
        self.log.info(message)
        self.log.info(details)

modules = glob.glob(os.path.dirname(__file__)+"/*.py")
__all__ = [ os.path.basename(f)[:-3] for f in modules]
print __all__
from handlers import *
