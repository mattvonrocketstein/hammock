"""
"""
import urlparse
import traceback
from flask import request

from corkscrew import SmartView
from report import report as report

from hammock._couch import get_db, update_db


class Setter(SmartView):
    """
    """
    requires_auth = True
    returns_json  = True
    def main(self):
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
            return dict(result='ok')
        except Exception, e:
            traceback.print_exc(e)

def set_factory(attr):
    """ """
    MySetter=type('set_' + attr,
                  (Setter,),
                  dict(url  = '/set_' + attr,
                       attr = attr)
                  )
    report("built setter {S} @ {U}", S=MySetter, U=MySetter.url)
    return MySetter
