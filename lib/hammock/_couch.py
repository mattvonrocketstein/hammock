""" hammock._couch

    couchdb specific helpers.

    lots of this is pretty dumb, still need to figure out geocouch
"""

import couchdb
from couchdb.client import ResourceNotFound
from peak.util.imports import lazyModule
from report import report as report

conf = lazyModule('hammock.conf')

class Database(couchdb.client.Database):
    """ """
    def _all_unique_attr(self, attrname):
        q = '''function(doc){emit(null, doc.%s);}'''%attrname
        return set([x.value for x in self.query(q)])

    def all(self):
        """ return iterator for all rows """
        query = '''function(doc){ emit(doc._id,doc);} '''
        return (x for x in self.query(query))


class Server(couchdb.Server):
    """ """
    def __init__(self):
        super(Server,self).__init__(conf.settings['couch.server'])
        self.resource.credentials = ( conf.settings['couch.username'],
                                      conf.settings['couch.password'] )
        self.resource.http.add_credentials(*self.resource.credentials)

    def __getitem__(self, name):
        from couchdb.client import validate_dbname, uri
        db = Database(uri(self.resource.uri, name), validate_dbname(name),
                      http=self.resource.http)
        db.resource.head() # actually make a request to the database
        return db


def get_db(db_name):
    db_name = db_name
    try:
        return setup()[db_name]
    except:
        report("\n\n------- Could not retrieve couch handle! ------- ")
        raise

def update_db(db, _id, dct):
    """  stupid.. have to delete and restore instead of update? """
    report('updating db',[db, _id, dct])
    doc = db[_id]
    report('before',doc.items())
    for x in dct:
        doc[x] = dct[x]

    # TODO: use db.update(doc) ?
    db[doc.id] = doc

    report('after', doc)
    report('updated "{id}" with new values for keys'.format(id=_id), dct.keys())

setup=Server

def handle_dirty_entry(_id, db_name=None):
    """ page at / may call this handler on malformed database entries. """
    report('dirty entry in coordinates database.. removing it (faked)',[_id])
    #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
    db = get_db(db_name)
    #del db[_id]

from collections import namedtuple
def document2namedt(doc):
    """ """
    doc = dict(doc.items())
    doc.pop('_rev')
    _id = doc.pop('_id')
    doc['id'] = _id
    dnt = namedtuple('DynamicNamedTuple',' '.join(doc.keys()))
    return dnt(**doc)

from hammock.utils import AllStaticMethods
class Schema(object):
    """ _unpack:

         metadata that defines helper functions that take
         request-variables to values suitable for storage
         in the database.  for example, integers will come
         of requests as simple strings by default, to fix
         that use something like this the following

           >>> myschema._unpack['my_int_var'] = int
    """
    __metaclass__ = AllStaticMethods
    _unpack  = {}
    _render  = {}
    _no_edit = []

def unpack_as_schema(req, schema):
    s = resolve_schema(schema).keys()
    q = dict(req.values.items())
    p = {}
    for x in q.keys():
        if x in s:
            p[x]=q[x]

    for special in schema._unpack:
        if special in p:
            p[special] = schema._unpack[special](p[special])

    return p

def resolve_schema(schema):
    schema=schema()
    out = [[x,getattr(schema,x)] for x in filter(lambda x: not x.startswith('_'), dir(schema))]
    out = dict(out)
    for x in out:
        if callable(out[x]):
            out[x]=out[x]()
    return out



class PersistentObject(object):
    """
    >>> APC = PersistentObject(db_name='pickles', property_name='airport_codes')

    """
    def __init__(self,db_name, property_name):
        self.db_name = db_name
        self.property_name = property_name

    @property
    def database(self):
        return Server()[self.db_name]

    @property
    def doc(self):
        pickles = self.database
        try:
            apcs    = pickles[self.property_name]
        except ResourceNotFound,e:
            apcs = dict(value=None)
            pickles[self.property_name] = apcs
            apcs    = pickles[self.property_name]
        return apcs

    def get(self):
        """ """
        return self.doc['value']

    def set(self,lst):
        doc = self.doc
        doc.update(value=lst)
        self.database[doc.id]=doc

    handle = property(get, set)
