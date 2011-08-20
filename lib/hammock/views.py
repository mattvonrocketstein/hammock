""" hammock.views

    don't use settings in here! they aren't ready yet
"""
import datetime
import urlparse
import traceback

from flask import request

from hammock.util import report
from hammock._couch import get_db, update_db

from hammock.corkscrew import HammockView

class Remove(HammockView):
    """
    function do_remove(_id){
            $.ajax({
                    type: "get",
                    data : {id:_id},
                    url: '{{view_url}}',
                    success: function (data,text){alert('removed successfully');},
                    error: efunc
                    });
    }
    """
    methods       = ['GET']
    url           = '/remove'
    returns_json  = True
    requires_auth = True

    def main(self):
        del get_db()[self['id']]
        return dict(result='ok')

class Set_Location(HammockView):
    """ sets a location ajax

        TODO: use set_factory to build this one too?
    """
    methods       = ['POST']
    url           =  '/set'
    returns_json  = True
    requires_auth = True
    def main(self):
        db = get_db()
        date_str     = str(datetime.datetime.now())
        coords       = request.form['coords'].replace('(','').replace(')','')
        data         = dict(coords=coords, timestamp=date_str, tag='recent')
        db[date_str] = data
        return dict(result='ok')

class Setter(HammockView):
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

from hammock.map_home import Slash
from hammock.auth import Login, Logout
__views__= [ Slash,
             Login,
             Logout,
             Remove,
             Set_Location,
             set_factory('label'),
             set_factory('tag')
             ]
