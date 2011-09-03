""" hammock.views

    don't use settings in here! they aren't ready yet
"""
import datetime
import urlparse
import traceback

from flask import request

from corkscrew import SmartView,View
from corkscrew.auth import Login, Logout
from report import report as report

from hammock.map_home import Slash
from hammock._couch import get_db, update_db

from .remove import Remove
from .ajax import set_factory


class SetLocation(View):
    """ sets a location ajax

        TODO: use set_factory to build this one too?
    """
    methods       = ['POST']
    url           =  '/set'
    returns_json  = True
    requires_auth = True

    def main(self):
        db = get_db()
        date_str     = str(datetime.datetime.now())
        coords       = request.form['coords'].replace('(','').replace(')','')
        data         = dict(coords=coords, timestamp=date_str, tag='recent')
        db[date_str] = data
        return dict(result='ok')

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

from corkscrew.views import Favicon

__views__= [ Favicon,
             Slash,
             Login, Logout,
             Remove, SetLocation,
             SetLabel, SetTag ]
