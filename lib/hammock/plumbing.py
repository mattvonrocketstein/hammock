""" hammock.plumbing
"""
from flask import g
from flask import session, request
from hammock.utils import report2 as report

def before_request():
    """ Make sure we are connected to the database
        each request and look up the current user
        so that we know he's there.
    """
    g.user = None
    report(request.url)
    if request.values:
        report(request.values)
    if 'user_id' in session:
        g.user = session['user_id']

def after_request(response):
    return response
