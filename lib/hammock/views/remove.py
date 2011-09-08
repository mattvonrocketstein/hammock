""" hammock.views.remove
"""

from corkscrew import SmartView

from hammock._couch import update_db
from .db import DBView

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
