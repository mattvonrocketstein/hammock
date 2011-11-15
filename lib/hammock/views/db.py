""" hammock.views.ajax

    DB view for admin convenience

    NOTE: server.create('database-name') returns 401-unauthorized,
          but from futon with the same user, it works fine.  wtf?
"""

from flask import render_template_string, render_template

#from couchdb.client import ResourceNotFound

from corkscrew import View

from report import report as report

from hammock._couch import get_db, Server
from hammock._couch import document2namedt
from hammock.utils import memoized_property, use_local_template

class DBView(View):
    """ abstract view for helping with access to a particular couch database """
    database_name = None
    db_schema     = None

    def _list(self):
        """ similar to self.rows, except it returns named tuples """
        return [ document2namedt(obj) for k, obj in self.rows ]

    def get_url(self, hash):
        "eg http://dojo.robotninja.org:5984/psa/cbe4af06308e90adc707559b85e27a52/wtf%20is%20velapene%20screen.mp3"

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
        """ returns a new, empty entry for the books database """
        assert self.db_schema is not None,'override db_schema first..'
        from hammock._couch import resolve_schema
        return resolve_schema(self.db_schema)

    @memoized_property
    def _db(self):
        """ not sure yet whether caching this is safe.  we shall see """
        return self.server[self.database_name]

    @property
    def rows(self):
        db         = self._db
        if self['tag']:
            keys = self.filter_where_tag_is(self['tag'])
            queryset = (self._db[x] for x in keys)
            for row in queryset:
                yield row.id, dict(row)

        else:
            queryset = self._db.all()
            for row in queryset:
                yield row.id, row.value

    def _all_unique_tags(self):
        """ TODO: remove special case in Slash when coordinates
                  database supports "tags" instead of just "tag"
        """
        q = '''function(doc){emit(null, doc.%s);}'''%'tags'
        out = [x.value for x in self._db.query(q)]
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
        out = render_template('js/tag_query.js', tag=tag)
        print '-'*70
        print out
        print '-'*70
        return out

        #'''function(doc){if(doc.tag=='%s'){emit(null, doc);}}'''%tag

    def filter_where_tag_is(self, tag):
        """ NOTE: returns keys only! """
        q = self._tag_filter_function(tag)
        return [ x.id for x in self._db.query(q) ]

class CouchView(DBView):
    """ shows list of couch databases and detail views for each """
    requires_auth = True
    url = '/_'

    @use_local_template
    def list_databases(self):
        """
        {% for x in databases%}
        <a href="/_?db={{x}}"><b>{{x}}</b></a> <br/>
        {%endfor%}
        """
        return dict(databases=self.databases)

    @use_local_template
    def db_detail(self, db_name):
        """
        <table>
        {% for x,y in stats%}
        <tr><td><b>{{x}}</b></td><td>{{y}}</td></tr>
        {%endfor%}
        </table>
        """
        db        = get_db(db_name)
        enum      = [x for x in db]
        length    = len(enum)
        key_style = [k for k in db[enum[0]].keys() if not k.startswith('_')] if length else []
        stats     = dict(length=length,
                         key = length and enum[0],
                         schema=key_style)
        return dict(stats=stats.items())

    def main(self):
        """ dispatch to either the list function or the detail function"""
        db_name = self['db']
        return self.db_detail(db_name) if db_name else self.list_databases()

    @property
    def databases(self): return [ x for x in self.server ]

class ViewView(View):
    """ view for showing information abouts views
    """
    url = '/__'
    requires_auth = True
    def main(self):
        return "NIY"
