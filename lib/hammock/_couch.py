""" /home/matt/code/hammock/lib/hammock/_couch.py
"""
from hammock.data import *
from hammock.util import report

def get_db():
    return setup()['coordinates']

def update_db(db, _id, dct):
    """  stupid.. have to delete and restore instead of update? """
    print 'updating db',[db,_id,dct]
    doc = db[_id]
    print 'before',doc.items()
    for x in dct:
        doc[x]=dct[x]
    #before = dict(before.items())
    #before.pop('_rev')
    #before.update(dct)
    #del db[_id]
    db[doc.id] = doc
    print 'after', doc
    report('updated "{id}" with new values for keys'.format(id=_id), dct.keys())

def setup():
    """ couch-specific stuff """
    import couchdb
    global couch
    couch = couchdb.Server(SERVER)
    couch.resource.credentials = CREDENTIALS
    return couch

def coordinates(db):
    return filter(lambda x: not x.startswith('_'), db)

def handle_dirty_entry(_id):
    """ page at / may call this handler on malformed database entries. """
    report('dirty entry in coordinates database.. removing it',[_id])
    db = couch['coordinates']
    del db[_id]

def all_unique_tags():
    return all_unique_attr('tag')

def all_unique_attr(attrname):
    q = '''function(doc){emit(null, doc.%s);}'''%attrname
    return set([x.value for x in get_db().query(q)])

def filter_where_tag_is(tag):
    q = '''function(doc){if(doc.tag=='%s'){emit(null, doc);}}'''%tag
    return [x.id for x in get_db().query(q)]
