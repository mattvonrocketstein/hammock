""" hammock.conf
"""
import os

from peak.util.imports import lazyModule

from corkscrew import Settings as _Settings

couch = lazyModule('hammock._couch')

class Settings(_Settings):
    default_file  = 'hammock.ini'
    extra_options = ( ('--backup',),
                      dict(dest='backup_database',
                           default='',
                           handler='doomwagon',
                           ))

    def __init__(self,*args, **kargs):
        # ugh hack
        super(Settings,self).__init__(*args, **kargs)
        from corkscrew.settings import settings
        from hammock import conf
        conf.settings = self

    def shell_namespace(self):
        dct = super(Settings,self).shell_namespace()
        dct.update(db=couch.Server())
        return dct
