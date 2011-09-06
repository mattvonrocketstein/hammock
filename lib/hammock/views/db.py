""" hammock.views.ajax

    DB view for admin convenience

    NOTE: server.create('database-name') returns 401-unauthorized,
          but from futon with the same user, it works fine.  wtf?
"""

from corkscrew import View

from report import report as report

from hammock._couch import get_db, setup, filter_where_tag_is


from flask import render_template_string

def use_local_template(func):
    def fxn(*args, **kargs):
        context = func(*args, **kargs)
        template = '{%extends "layout.html" %}{%block body%}<center>' + \
                   func.__doc__ + '</center>{%endblock%}'
        return render_template_string(template, **context)
    return fxn
class memoized_property(object):
    """
    A read-only @property that is only evaluated once.

    From: http://www.reddit.com/r/Python/comments/ejp25/cached_property_decorator_that_is_memory_friendly/
    """
    def __init__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return self
        obj.__dict__[self.__name__] = result = self.fget(obj)
        return result

class DBView(View):
    """ abstract view for helping with access to a particular couch database """
    database_name = None

    @memoized_property
    def _db(self):
        """ not sure yet whether caching this is safe.  we shall see """
        return get_db(self.database_name)

    @property
    def _all_rows(self):
        print "getting all rows"
        query = '''function(doc){ emit(doc._id,doc);} '''
        return (x for x in self._db.query(query))

    @property
    def rows(self):
        db         = get_db(self.database_name)
        if self['tag']:
            keys = filter_where_tag_is(self['tag'], self.database_name)
            queryset = (db[x] for x in keys)
            for row in queryset:
                yield row.id, dict(row)

        else:
            queryset = self._all_rows
            for row in queryset:
                yield row.id, row.value

    @memoized_property
    def server(self): return setup()

    @property
    def databases(self): return [ x for x in self.server ]

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
