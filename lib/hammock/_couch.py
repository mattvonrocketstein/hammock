""" hammock._couch

    couchdb specific helpers.

    lots of this is pretty dumb, still need to figure out geocouch
"""

import couchdb
from peak.util.imports import lazyModule
from report import report as report

conf = lazyModule('hammock.conf')

def get_db():
    try:
        return setup()[conf.settings['hammock.coordinates_db_name']]
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

def setup():
    """ couch-specific stuff for hammock

        currently, this function is called several times and recreating
        the server object repeatedly because i'm not sure whether it
        handles reconnections, etc.
    """
    couch = couchdb.Server(conf.settings['couch.server'])
    couch.resource.credentials = ( conf.settings['couch.username'],
                                   conf.settings['couch.password'] )
    return couch

def coordinates(db):
    return (x for x in db.query('''function(doc){ emit(doc._id,doc);} '''))
    #return filter(lambda x: not x.startswith('_'), db)

def handle_dirty_entry(_id):
    """ page at / may call this handler on malformed database entries. """
    report('dirty entry in coordinates database.. removing it (faked)',[_id])
    db = get_db() #setup()[conf.settings['hammock.coordinates_db_name']]
    #del db[_id]

def all_unique_tags():
    """ """
    return all_unique_attr('tag')

def all_unique_attr(attrname):
    q = '''function(doc){emit(null, doc.%s);}'''%attrname
    return set([x.value for x in get_db().query(q)])

def filter_where_tag_is(tag):
    q = '''function(doc){if(doc.tag=='%s'){emit(null, doc);}}'''%tag
    return [x.id for x in get_db().query(q)]
