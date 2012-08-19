""" hammock.views.ajax

    Factory for ajax attribute-setters
"""
import urlparse
import traceback
from flask import request

from corkscrew import View
from report import report as report

from hammock._couch import update_db
from .db import DBView
from corkscrew.blueprint import BluePrint

class Setter(DBView):
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

            val = request.args.get(this_attr)
            # 'or' needed because we don't want to set
            # it as None if the ajax screws up
            val = val or str(val)
            report("in inner set with", [val])
            update_db(db, _id, {this_attr:val}, self.schema)
            return dict(result='ok')

        except Exception, e:
            # tornado ate my exception?
            traceback.print_exc(e)


def set_factory(database_name, attr, schema=None):
    """ """
    assert schema is not None, database_name
    name  = 'set_' + attr
    bases = (Setter,)
    dct   = dict(url  = '/set_' + attr,
                 attr = attr,
                 blueprint = BluePrint(database_name+'__'+name),
                 schema=schema,
                 db_schema=schema, #HACK
                 database_name=database_name)
    return type(name, bases, dct)
