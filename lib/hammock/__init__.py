# -*- coding: utf-8 -*-
"""
"""

import datetime
import urlparse
import traceback

from flask import Flask, request, jsonify

from hammock.util import report
from hammock.data import settings
from hammock.auth import requires_authentication
from hammock._couch import get_db, update_db, setup

## Begin database setup
couch     = setup()

## Begin flask setup
app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = settings['flask.secret_key']

## Begin flask plumbing
from hammock.plumbing import before_request, after_request
before_request = app.before_request(before_request)
after_request  = app.after_request(after_request)

## Begin flask views
from hammock.map_home import slash
from hammock.auth import login,logout
login          = app.route('/login', methods=['GET', 'POST'])(login)
logout         = app.route('/logout')(logout)
slash          = app.route('/')(slash)

@requires_authentication
@app.route('/remove',methods=['POST'])
def remove():
    """ remove a loction ajax """
    if request.method=='POST':
        _id = request.form['id']
        del get_db()[_id]
        return jsonify(result='ok')

@requires_authentication
@app.route('/set', methods=['GET', 'POST'])
def set_location():
    """ sets a location ajax

        TODO: use set_factory to build this one too?
    """
    if request.method == 'POST':
        db = get_db()
        date_str = str(datetime.datetime.now())
        coords=request.form['coords'].replace('(','').replace(')','')
        data = dict(coords=coords, timestamp=date_str, tag='default')
        db[date_str] = data
        return jsonify(result='ok')

def set_factory(attr):
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

set_label = set_factory('label')
set_tag   = set_factory('tag')
