#!/usr/bin/env python
""" hammock.bin._hammock:

    command line script
"""
import logging
log = logging.getLogger(__file__)

import datetime
import urlparse
import traceback
from flask import Flask, request, jsonify

from hammock.util import report
from hammock.auth import Login, Logout
from hammock.plumbing import before_request, after_request

def go():
    from hammock.conf import settings
    from hammock._couch import get_db, update_db, setup
    from hammock import views
    from hammock.map_home import Slash

    ## Begin database setup
    couch     = setup()

    ## Begin flask setup
    app = Flask('hammock')
    app.config.from_object('hammock')
    app.secret_key = settings['flask.secret_key']

    views.before_request = app.before_request(before_request)
    views.after_request  = app.after_request(after_request)
    [ v(app=app) for v in
      [Slash,
       Login,
       Logout,
       views.Remove,
       views.Set_Location,
       views.set_factory('label'),
       views.set_factory('tag')]
      ]
    return app

def entry():
    """ Main entry point """
    from hammock import conf
    settings = conf.Settings()
    conf.settings = settings

    if settings.shell:
        from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
    else:
        app = go()
        app.run(host=settings['hammock.host'],
                port=int(settings['hammock.port']),
                debug=settings['flask.debug'])

if __name__=='__main__':
    entry()
