import logging
log = logging.getLogger(__file__)

import datetime
import urlparse
import traceback

from flask import request, jsonify

from hammock.auth import requires_authentication
from hammock.util import report
from hammock._couch import get_db, update_db



def remove():
    """ remove a loction ajax """
    if request.method=='POST':
        _id = request.form['id']
        del get_db()[_id]
        return jsonify(result='ok')

def set_location():
    """ sets a location ajax

        TODO: use set_factory to build this one too?
    """
    if request.method == 'POST':
        db = get_db()
        date_str = str(datetime.datetime.now())
        coords=request.form['coords'].replace('(','').replace(')','')
        data = dict(coords=coords, timestamp=date_str, tag='recent')
        db[date_str] = data
        return jsonify(result='ok')

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
