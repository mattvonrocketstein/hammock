""" hammock.data

    You can override this file by using "hammock --settings=<path>"
"""
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
    'hammock.default_zoom':6
    }

class Settings(object):
    """ """
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
settings = Settings().load()
if __name__=="__main__":
    print Settings().load("./hammock.ini", _ConfigDefault)
