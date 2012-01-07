""" hammock.plumbing
"""
from flask import g
from flask import session, request
from hammock.utils import report2 as report

registry = []

def before_request():
    """ Make sure we are connected to the database
        each request and look up the current user
        so that we know he's there.
    """
    g.user = None
    print request.url
    if request.values:
        #report(str(request.values))
        print request.values
    if 'user_id' in session:
        g.user = session['user_id']

def after_request(response):
    response.request = request
    for f in registry:
        response = f(response)
    return response

def register(f):
    registry.append(f)
