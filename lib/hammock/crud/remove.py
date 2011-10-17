""" hammock.views.remove
"""

from flask import jsonify

from corkscrew import SmartView

from hammock._couch import update_db
from hammock.views.db import DBView
from hammock.utils import authorization_required

from report import report

class Removable(object):
    """ mixin for item deletion """

    @authorization_required
    def remove(self):
        _id   = self['remove']
        report("Removing {id} from {db}", id=_id, db=self.database_name)
        del self._db[_id]
        return jsonify(dict(ok='true'))
