""" hammock.views.db

    DB view for admin convenience

    NOTE: server.create('database-name') returns 401-unauthorized,
          but from futon with the same user, it works fine.  wtf?
"""

from flask import render_template# render_template_string

from couchdb.mapping import Document
from corkscrew import View
from corkscrew.blueprint import BluePrint
from report import report as report

from hammock._couch import get_db, Server, unpack_as_schema
from hammock.utils import memoized_property, use_local_template

class DBView(View):
    """ abstract view for helping with access to a particular couch database """
    database_name = None
    db_schema     = None
    related_views = []
    def __init__(self, *args, **kargs):
        super(DBView, self).__init__(*args, **kargs)
        assert self.db_schema,str(self)
        self.db_schema.view = self

    def _list(self):
        """ returns objects based on raw data from self.rows """
        out=[]
        for _id, _data in self.rows:
            doc = unpack_as_schema(_data, self.db_schema)
            if not getattr(doc, 'id'):
                doc.id = _id
            out.append(doc)
        return out

    def build_new_entry(self):
        """ not really quite generic enough.
            still it depends on 'stamp' as pk
        """
        entry = self.schema()   # as dictionary
        _id = entry['stamp']    # get new items key.
        self._db[_id] = entry   # save it..
        entry = self._db[_id]   # as document
        return entry

    def schema(self):
        """ returns a new, empty entry for the books database
            TODO: stop returning the dictionary asap and give back a Document instance
        """
        assert self.db_schema is not None, 'override db_schema first..'
        tmp = self.db_schema()
        if isinstance(tmp, Document):
            return tmp._data
        return tmp

    @memoized_property
    def _db(self):
        """ not sure yet whether caching this is safe.  we shall see """
        return self.server[self.database_name]

    @property
    def rows(self):
        if self['tag']:
            keys = self.filter_where_tag_is(self['tag'])
            queryset = (self._db[x] for x in keys)
            for row in queryset:
                yield row.id, dict(row)

        else:
            queryset = self._db.all()
            for row in queryset:
                yield row.id, row.value

    def rows_at(self, attr_name):
        """ """
        q = '''function(doc){emit(null, doc.%s);}''' % attr_name
        out = [ x.value for x in self._db.query(q) ]
        return out

    def _all_unique_tags(self):
        """ TODO: remove special case in Slash when coordinates
                  database supports "tags" instead of just "tag"
        """
        out = self.rows_at('tags')
        if out:
            out = reduce(lambda x,y: x+y, out)
            out = set(out)
        return out

    def get_entry(self, _id):
        """ """
        #try:
        return self._db[_id]
        #except ResourceNotFound,e:
        #    report('resource with key "{id}" not found',id=_id)
        #    raise

    @memoized_property
    def server(self): return Server()

    def _tag_filter_function(self, tag):
        """ TODO: dryer"""
        out = render_template('js/tag_query.js', tag=tag)
        print '-'*70, out, '-'*70
        return out
        #'''function(doc){if(doc.tag=='%s'){emit(null, doc);}}'''%tag

    def filter_where_tag_is(self, tag):
        """ NOTE: returns keys only! """
        q = self._tag_filter_function(tag)
        return [ x.id for x in self._db.query(q) ]
