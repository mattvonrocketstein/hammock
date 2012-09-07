""" hammock.views

    don't use settings in here! they aren't ready yet
"""
import datetime

from flask import request

from corkscrew import View
from corkscrew.auth import Login, Logout
from corkscrew.views import Favicon

from report import report as report

from hammock.views.administration import CouchView

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
      <input type=hidden name=next value="{{request.values.next}}">
    </dl>
    <div class=actions><input type=submit value="Sign In"></div>
  </form>
{% endblock %}
"""

__views__= [
    # corkscrew standard views
    Favicon, Login, Logout,

    # couch views
    CouchView,
    ]
