#!/usr/bin/env python
""" hammock.bin._hammock:

    command line script
"""
import logging
log = logging.getLogger(__file__)

import datetime
import urlparse
import traceback
from optparse import OptionParser
from hammock.auth import requires_authentication
parser = OptionParser()

parser.set_conflict_handler("resolve")
parser.add_option("--port",  dest="port",
                  default='5000', help="server listen port")
parser.add_option("--shell", dest="shell",
                  default=False, help="hammock db shell",
                  action='store_true')

def go():

    from flask import Flask, request, jsonify

    from hammock.util import report
    from hammock.data import settings
    from hammock._couch import get_db, update_db, setup
    from hammock import views
    from hammock.map_home import slash
    from hammock.auth import login,logout
    from hammock.plumbing import before_request, after_request

    ## Begin database setup
    couch     = setup()

    ## Begin flask setup
    app = Flask('hammock')
    app.config.from_object('hammock')
    app.secret_key = settings['flask.secret_key']

    views.before_request = app.before_request(before_request)
    views.after_request  = app.after_request(after_request)

    ## Begin flask views
    ## begin using these instead.. app.add_url_rule('/', 'index', index)
    views.login          = app.route('/login', methods=['GET', 'POST'])(login)
    views.logout         = app.route('/logout')(logout)
    views.slash          = app.route('/')(slash)
    views.remove = requires_authentication(app.route('/remove',methods=['POST'])(views.remove))
    views.set_location = requires_authentication(app.route('/set', methods=['GET', 'POST'])(views.set_location))
    views.set_label = views.set_factory('label', app)
    views.set_tag   = views.set_factory('tag', app)
    return app

def entry():
    """ Main entry point """
    from hammock import data
    settings = data.Settings(parser)
    data.settings = settings

    if settings.shell:
        from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
    else:
        app = go()
        app.run(host=settings['hammock.host'],
                port=int(settings['hammock.port']),
                debug=settings['flask.debug'])

if __name__=='__main__':
    entry()
