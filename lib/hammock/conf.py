""" hammock.conf
"""
import os

from corkscrew import Settings as _Settings


class Settings(_Settings):
    DEFAULT_SETTINGS = os.path.abspath(os.path.join(os.path.split(__file__)[0], "hammock.ini"))
    default_file = 'hammock.ini'
    def __init__(self,*args, **kargs):
        #ugh hack
        super(Settings,self).__init__(*args, **kargs)
        from corkscrew.settings import settings
        from hammock import conf
        conf.settings = self
