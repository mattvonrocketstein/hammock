""" hammock.views.ajax

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

class CouchView(View):
    """ shows list of couch databases and detail views for each """
    requires_auth = True
    url = '/_'
    blueprint  = BluePrint('couchview', __name__)
    @use_local_template
    def list_databases(self):
        """
        {# renders a list of all databases together with a link to their futon page #}
        <table>
          <tr><td>database name (click for detail)</td><td>link to futon</td></tr>
          {% for x in databases%}
          <tr>
            <td><a href="/_?db={{x}}"><b>{{x}}</b></a></td>
            <td><a href="{{couch_base}}{{x}}">(futon)</a></td>
          </tr>
          {%endfor%}
        </table>
        """
        couch_base = self % 'couch.server' + '_utils/database.html?'
        return dict(couch_base=couch_base, databases=self.databases)

    @use_local_template
    def list_views(self):
        """
        {# renders a list of all views.. #}
        <table>
          <tr><td>view</td><td>from module</td></tr>
          {% for v in views %}
          <tr>
            <td><b>{{v.__name__}}</b></td>
            <td>{{v.__class__.__module__}}</td>
          </tr>
          {%endfor%}
        </table>
        """
        return dict(views=self.settings._installed_views)

    @use_local_template
    def db_detail(self, db_name):
        """
        {# given a db, renders length, an example key value, and guesses at the schema #}
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

    @use_local_template
    def index(self):
        """
        <a href=/_?action=db> list databases</a><br/>
        <a href=/_?action=views> list views</a><br/>
        """
        return dict()
    def main(self):
        """ dispatch to either the list function or the detail function"""

        action  = self['action']
        if action=='views':
            return self.list_views()
        elif action=='db':
            db_name = self['db']
            if db_name:
                return self.db_detail(db_name)
            else:
                return self.list_databases()
        else:
            return self.index()


    @property
    def databases(self): return [ x for x in self.server ]


class ViewView(View):
    """ view for showing information abouts views
    """
    url = '/__'
    requires_auth = True
    def main(self):
        return "NIY"
