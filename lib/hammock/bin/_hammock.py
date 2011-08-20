#!/usr/bin/env python
""" hammock.bin._hammock:

    command line script
"""

from flask import Flask
from jinja2 import FileSystemLoader

from hammock.util import report
from hammock.auth import Login, Logout
from hammock.plumbing import before_request, after_request
from hammock.map_home import Slash
from hammock._couch import get_db, update_db, setup
from hammock import views
from hammock.reflect import namedAny
def go():
    from hammock.conf import settings
    app_name = settings['flask.app']
    app = Flask(app_name)
    app.secret_key = settings['flask.secret_key']

    if 'flask.template_path' in settings:
        app.jinja_loader = FileSystemLoader(settings['template_path'])

    if 'flask.before_request' in settings:
        before_request = settings['flask.before_request']
        before_request = namedAny(before_request)
        app.before_request(before_request)

    if 'flask.after_request' in settings:
        after_request = settings['flask.after_request']
        after_request = namedAny(after_request)
        app.after_request(after_request)

    [ v(app=app) for v in
      [Slash,
       Login,
       Logout,
       views.Remove,
       views.Set_Location,
       views.set_factory('label'),
       views.set_factory('tag')]
      ]

    @app.route("/favicon.ico")
    def favicon():
        return app.send_static_file("favicon.ico")

    return app

def entry():
    """ Main entry point """
    from hammock import conf
    settings = conf.Settings()
    conf.settings = settings

    if settings['user.shell']:
        from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
    else:
        app = go()
        app.run(host=settings['flask.host'],
                port=int(settings['flask.port']),
                debug=settings['flask.debug'])

if __name__=='__main__':
    entry()
