""" hammock.data

    You can override this file by using "hammock --settings=<path>"
"""
import logging
log = logging.getLogger(__file__)

import os
import ConfigParser
import string

CONTROL_T   = "<br/><span class=control_class>{link}</span>"

_ConfigDefault = {
    # DEBUG
    'flask.debug'  : True,
    # SERVER
    'couch.server'      : 'http://dojo.robotninja.org:5984/',
    # CREDENTIALS was tuple
    'couch.username' : 'matt',
    'couch.password' : 'lemmein',
    # SECRET_KEY
    'flask.secret_key':'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT',
    # MAPS_API_KEY
    'google.maps_key':'ABQIAAAAGGWUIcktQOU5Q76O6cV_BhRFeVNa246MatoBH1bx3V0-W8LG9hTZAWkoAFU1qTLCQuQOI0mPSlWsXQ',
    # DEFAULT_ZOOM
    'hammock.default_zoom':6,
    'hammock.port':5000,
    'hammock.host':'0',
    }

class Settings(object):
    """ """

    def __init__(self,parser):
        self.options, self.args = parser.parse_args()
        self._settings = self.load()

        # a few command line options are allowed to override the .ini
        if self.options.port:
            self._settings.update({'hammock.port':self.options.port})

        self.shell=self.options.shell

    def __getitem__(self,k):
        return self._settings[k]

    def load(self, file=None, config={}):
        """ returns a dictionary with key's of the form
            <section>.<option> and the values
        """
        if file is None:
            return _ConfigDefault
        if not os.path.exists(file): raise Exception,'dood'
        config = config.copy()
        cp = ConfigParser.ConfigParser()
        cp.read(file)
        for sec in cp.sections():
            name = string.lower(sec)
            for opt in cp.options(sec):
                config[name + "." + string.lower(opt)] = string.strip(cp.get(sec, opt))
        return config

if __name__=="__main__":
    print Settings().load("./hammock.ini", _ConfigDefault)
