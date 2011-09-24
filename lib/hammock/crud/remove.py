""" hammock.views.remove
"""

from corkscrew import SmartView

from hammock._couch import update_db
from hammock.views.db import DBView
from hammock.utils import authorization_required

class Remove(SmartView, DBView):
    """
    function do_remove(_id){
       $.ajax({ type: "get",
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
    database_name = 'coordinates'

    def main(self):
        del self._db[self['id']]
        return dict(result='ok')

class Removable(object):
    """ mixin for item deletion """

    @authorization_required
    def remove(self):
        _id   = self['remove']
        report("Removing {id} from {db}", id=_id, db=self.database_name)
        del self._db[_id]
        return jsonify(dict(ok='true'))
