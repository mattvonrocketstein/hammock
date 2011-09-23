""" hammock.views.mixins
"""

from flask import jsonify
from hammock.utils import authorization_required

class Removable(object):
    """ mixin for item deletion """

    @authorization_required
    def remove(self):
        _id   = self['remove']
        report("Removing {id} from {db}", id=_id, db=self.database_name)
        del self._db[_id]
        return jsonify(dict(ok='true'))
