""" /home/matt/code/hammock/lib/hammock/_couch.py
"""
from hammock.data import *
from hammock.util import report

def update_db(db, _id, dct):
    """  stupid.. have to delete and restore instead of update? """
    before = db[_id]
    before = dict(before.items())
    before.pop('_rev')
    before.update(dct)
    del db[_id]
    db[_id] = before
    report("updated {id} with new values for keys".format(id=_id), dct.keys())

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
