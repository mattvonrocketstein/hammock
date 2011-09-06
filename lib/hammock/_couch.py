""" hammock._couch

    couchdb specific helpers.

    lots of this is pretty dumb, still need to figure out geocouch
"""

import couchdb
from peak.util.imports import lazyModule
from report import report as report

conf = lazyModule('hammock.conf')

def get_db(db_name=None):
    db_name = db_name or conf.settings['hammock.coordinates_db_name']
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

def handle_dirty_entry(_id, db_name=None):
    """ page at / may call this handler on malformed database entries. """
    report('dirty entry in coordinates database.. removing it (faked)',[_id])
    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
    db = get_db(db_name) #setup()[conf.settings['hammock.coordinates_db_name']]
    #del db[_id]

def all_unique_tags(db_name=None):
    """ """
    return all_unique_attr('tag',db_name)

def all_unique_attr(attrname, db_name):
    q = '''function(doc){emit(null, doc.%s);}'''%attrname
    return set([x.value for x in get_db(db_name).query(q)])

from collections import namedtuple
def document2namedt(doc):
    """ """
    doc=dict(doc.items())
    doc.pop('_rev')
    _id=doc.pop('_id')
    doc['id']=_id
    dnt = namedtuple('DynamicNamedTuple',' '.join(doc.keys()))
    return dnt(**doc)
