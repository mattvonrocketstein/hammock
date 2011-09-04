""" hammock.views.remove
"""

from corkscrew import SmartView
from hammock._couch import get_db, update_db

class Remove(SmartView):
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

    def main(self):
        del get_db()[self['id']]
        return dict(result='ok')
