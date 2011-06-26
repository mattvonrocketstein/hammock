""" hammock/plumbing
"""
from flask import render_template, abort, g, flash
from flask import Flask, request, session, url_for, redirect

def before_request():
    """ Make sure we are connected to the database
        each request and look up the current user
        so that we know he's there.
    """
    g.user = None
    if 'user_id' in session:
        g.user = 'superuser'

def after_request(response):
    """ nothing to do here so far. """
    return response
