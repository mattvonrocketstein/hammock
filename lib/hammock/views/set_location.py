""" hammock.views.set_location
"""

import datetime
from flask import request

from .db import DBView

class SetLocation(DBView):
    """ sets a location ajax

        TODO: use set_factory to build this one too?
    """
    methods       = ['POST']
    url           =  '/set'
    returns_json  = True
    requires_auth = True
    database_name = 'coordinates'

    def main(self):
        db           = self._db
        date_str     = str(datetime.datetime.utcnow())
        coords       = request.form['coords'].replace('(','').replace(')','')
        data         = dict(coords=coords, timestamp=date_str, tag='recent')
        db[date_str] = data
        return dict(result='ok')
