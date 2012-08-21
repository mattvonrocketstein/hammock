""" hammock._couch

    couchdb specific helpers.

    lots of this is pretty dumb, still need to figure out geocouch
"""
import base64
from collections import namedtuple

import demjson
import couchdb
from peak.util.imports import lazyModule

from hammock.utils import AllStaticMethods
from report import report as report
from couchdb.mapping import ListField, TextField, DateTimeField
from couchdb.mapping import Document

conf = lazyModule('hammock.conf')

class DatabaseMixin(object): #couchdb.client.Database):
    """ """
    def _all_unique_attr(self, attrname):
        q = '''function(doc){emit(null, doc.%s);}'''%attrname
        out = []
        for x in self.query(q):
            tmp=x.value
            if tmp not in out: out.append(tmp)
        return out

    def all(self):
        """ return iterator for all rows """
        query = '''function(doc){ emit(doc._id,doc);} '''
        return (x for x in self.query(query))


class Server(couchdb.Server):
    """ """
    def __init__(self):
        super(Server,self).__init__(conf.settings['couch.server'])
        self.resource.credentials = ( conf.settings['couch.username'],
                                      base64.b64decode(conf.settings['couch.password']) )

    def __getitem__(self, name):
        """ just brutal """
        result = super(Server,self).__getitem__(name)
        result.__class__ = type('DynamicDatabase', (DatabaseMixin,result.__class__), {})
        return result

def get_db(db_name):
    db_name = db_name
    return setup()[db_name]

def update_db(db, _id, dct, schema=None):
    """  stupid.. have to delete and restore instead of update? """

    if not schema:
        report('SCHEMA NOT PROVIDED!!!!!!!')
        report('updating db',[db, _id, dct])
        doc = db[_id]
        report('before',doc.items())

        for x in dct:
            doc[x] = dct[x]

        # TODO: use db.update(doc) ?
        #db[doc.id] = doc

        report('after', doc)
        report('updated "{id}" with new values for keys'.format(id=_id), dct.keys())
    else:
        doc = schema.load(db, _id)
        for x in dct:
            val = dct[x]
            fieldtype = getattr(schema, x).__class__
            if fieldtype==ListField:
                val = demjson.decode(val)
            elif fieldtype==TextField:
                pass
            else:
                raise Exception, 'NIY:'+str(fieldtype)
            setattr(doc, x, val)
        doc.store(db)
setup=Server

def handle_dirty_entry(_id, db_name=None):
    """ page at / may call this handler on malformed database entries. """
    report('dirty entry in coordinates database.. removing it (faked)', [_id])
    db = get_db(db_name)
    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
    #del db[_id]

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
    _unpack       = {}
    _render       = {}
    _no_edit      = []

    @classmethod
    def _resolve(kls):
        return resolve_schema(kls)

def unpack_as_schema(q, schema):
    """ unpack a request/dict into a dictionary according to this schema

        TODO: verification for multiple choice?
    """
    # because it might be a request
    q = q if isinstance(q,dict) else dict(q.values.items())
    assert issubclass(schema, Document), 'old style schema?'
    for var in q:
        field = getattr(schema, var, None)
        if field==None:
            # might be interval value e.g. '_rev', etc
            continue
        if isinstance(field, ListField) and not isinstance(q[var], list):
            q[var] = demjson.decode(q[var])
        if isinstance(field, DateTimeField):
            q[var] = getattr(schema, var)._to_python( q[var] )
    return schema(**q)

def resolve_schema(schema):
    """ resolves a schema to the implied default value
        TODO: deprecate this
    """
    schema = schema()
    if isinstance(schema, Document):
        return schema

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
        #try:
        apcs    = pickles[self.property_name]
        #except ResourceNotFound,e:
        #    apcs = dict(value=None)
        #    pickles[self.property_name] = apcs
        #    apcs    = pickles[self.property_name]
        return apcs

    def get(self):
        """ """
        return self.doc['value']

    def set(self,lst):
        doc = self.doc
        doc.update(value=lst)
        self.database[doc.id]=doc

    handle = property(get, set)
