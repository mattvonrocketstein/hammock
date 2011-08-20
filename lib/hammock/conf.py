""" hammock.conf
"""
from hammock.corkscrew import FlaskSettings

import os

class Settings(FlaskSettings):
    DEFAULT_SETTINGS = os.path.abspath(os.path.join(os.path.split(__file__)[0], "hammock.ini"))
    def __init__(self,*args, **kargs):
        #ugh hack
        super(Settings,self).__init__(*args, **kargs)
        from hammock.corkscrew.settings import settings
        from hammock import conf
        conf.settings = self
