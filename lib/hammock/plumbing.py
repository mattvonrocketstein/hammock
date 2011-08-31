""" hammock.plumbing
"""
from flask import g
from flask import session

def before_request():
    """ Make sure we are connected to the database
        each request and look up the current user
        so that we know he's there.
    """
    g.user = None
    if 'user_id' in session:
        g.user = session['user_id']

def after_request(response): return response
