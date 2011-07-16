# -*- coding: utf-8 -*-
"""
    TODO: use this stuff:

"""

import datetime
import urlparse
import traceback

from flask import Flask, request, redirect, jsonify
from werkzeug import check_password_hash, generate_password_hash

from hammock.util import report
from hammock.data import SECRET_KEY
from hammock.auth import requires_authentication
from hammock._couch import get_db, update_db, setup


## Begin database setup
couch     = setup()

## Begin flask setup
app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = SECRET_KEY

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
            #this_attr = request.url.split('?')[0].split('/')[-1]
            this_attr = urlparse.urlsplit(request.url).path.split('_')[-1]

            db    = get_db()
            _id   = request.args.get('id')
            report("in inner set for attribute {A} on id {I} with value {V}".format(I=_id,
                                                                                    A=this_attr,
                                                                                    V=request.form.keys()))
            #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
            label = request.args.get(this_attr)
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


if __name__=='__main__':
    # hook for to clean up the database by hand
    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
