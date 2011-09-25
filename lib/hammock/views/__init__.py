""" hammock.views

    don't use settings in here! they aren't ready yet
"""
import datetime

from flask import request

from corkscrew import View
from corkscrew.auth import Login, Logout
from corkscrew.views import Favicon

from report import report as report

from hammock.crud.remove import Remove

from hammock.views.db import CouchView
from hammock.views.ajax import set_factory

# TODO: move
from hammock.views.set_location import SetLocation

Login._template = """
{% extends "layout.html" %}
{% block title %}Sign In{% endblock %}
{% block body %}
  <h2>Sign In</h2>
  {% if error %}<div class=error><strong>Error:</strong> {{ error }}</div>{% endif %}
  <form action="" method=post>
    <dl>
      <dt>Username:
      <dd><input type=text name=username size=30 value="{{ request.form.username }}">
      <dt>Password:
      <dd><input type=password name=password size=30>
    </dl>
    <div class=actions><input type=submit value="Sign In"></div>
  </form>
{% endblock %}
"""

SetLabel = set_factory('label')
SetTag   = set_factory('tag')

from robotninja.books import BookList, BookUpdate
from robotninja.quotes import QuoteList, QuoteUpdate
from robotninja.coords.map_home import Slash

__views__= [
    # corkscrew standard views
    Favicon, Login, Logout,

    # hammock core
    Slash,
    Remove, SetLocation,
    SetLabel, SetTag,

    # trac replacements
    BookList, BookUpdate,
    QuoteList, QuoteUpdate,

    # couch views
    CouchView,
    ]
