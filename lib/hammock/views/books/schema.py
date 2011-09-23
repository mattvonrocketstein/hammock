""" hammock.views.books.schema
"""

import datetime
from hammock._couch import Schema


class BookSchema(Schema):
    author = ''
    title  = ''
    tags   = []
    stamp  = lambda: str(datetime.datetime.utcnow())
    index  = 0
    _unpack = dict(tags=eval, index=int)
