""" hammock.views.ajax

    Factory for ajax attribute-setters
"""
import urlparse
import traceback
from flask import request

from corkscrew import SmartView
from report import report as report

from hammock._couch import update_db
from .db import DBView

class Setter(SmartView, DBView):
    """
    """
    requires_auth = True
    returns_json  = True

    def main(self):
        """ ajax -- sets an attribute for a location

            flask does something weird so that this closure doesn't
            work the way it ought to.  hence we have to calculate 'attr'
            based on request path :(
        """
        try:
            this_attr = urlparse.urlsplit(request.url).path.split('_')[-1]

            db    = self._db
            _id   = request.args.get('id')
            msg = "in inner set for attribute {A} on id {I} with value {V}"
            report(msg.format(I=_id,
                              A=this_attr,
                              V=request.form.keys()))

            label = request.args.get(this_attr)
            # 'or' needed because we don't want to set
            # it as None if the ajax screws up
            label = label or str(label)
            report("in inner set with", [label])
            update_db(db, _id, {this_attr:label})
            return dict(result='ok')
        except Exception, e:
            traceback.print_exc(e)

def set_factory(database_name, attr):
    """ """
    name  = 'set_' + attr
    bases = (Setter,)
    dct   = dict(url  = '/set_' + attr,
                 attr = attr,
                 database_name=database_name)
    return type(name, bases, dct)
