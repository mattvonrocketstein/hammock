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
    app.config.from_object('hammock')#__name__)
    app.secret_key = settings['flask.secret_key']

    # HACK.. looking at template_folder arg passed to app()
    #import os
    #from jinja2 import FileSystemLoader
    #ROOT = os.path.join(os.path.split(__file__)[0],'..')
    #template_path = os.path.join(ROOT,'templates')
    #app.jinja_loader = FileSystemLoader(template_path)
    #app.static_folder =os.path.join(ROOT,'static')

    ## Begin flask plumbing
    views.before_request = app.before_request(before_request)
    views.after_request  = app.after_request(after_request)

    ## Begin flask views
    ## begin using these instead.. app.add_url_rule('/', 'index', index)
    views.login          = app.route('/login', methods=['GET', 'POST'])(login)
    views.logout         = app.route('/logout')(logout)
    views.slash          = app.route('/')(slash)
    views.remove = requires_authentication(app.route('/remove',methods=['POST'])(views.remove))
    views.set_location = requires_authentication(app.route('/set', methods=['GET', 'POST'])(views.set_location))
    views.set_label = set_factory('label', app)
    views.set_tag   = set_factory('tag', app)
    return app

    #@requires_authentication
    #@app.route('/remove',methods=['POST'])
    #@requires_authentication
    #@app.route('/set', methods=['GET', 'POST'])

def set_factory(attr,app):
        """ """
        def setter():
            """ ajax -- sets an setter.attribute for a location
                flask does something weird so that this closure doesn't
                work the way it ought to.  hence we have to calculate 'attr'
                based on request path :(
            """
            try:
                this_attr = urlparse.urlsplit(request.url).path.split('_')[-1]

                db    = get_db()
                _id   = request.args.get('id')
                report("in inner set for attribute {A} on id {I} with value {V}".format(I=_id,
                                                                                        A=this_attr,
                                                                                        V=request.form.keys()))

                label = request.args.get(this_attr)
                # 'or' needed because we don't want to set
                # it as None if the ajax screws up
                label = label or str(label)
                report("in inner set with", [label])
                update_db(db, _id, {this_attr:label})
                return jsonify(result='ok')
            except Exception, e:
                traceback.print_exc(e)
        url    = '/set_' + attr
        setter = requires_authentication(setter)
        setter = app.route(url)(setter)
        setter.attr = attr
        print " * built setter", [attr,url]
        return requires_authentication(setter)

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
