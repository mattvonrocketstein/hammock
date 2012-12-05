""" hammock.views.administration
"""
from corkscrew import View
from corkscrew.blueprint import BluePrint

from hammock.utils import use_local_template
from hammock._couch import get_db

class CouchView(View):
    """
    1) a list of couch databases and detail views for each,
    2) a list of views complete with class-name, defining-module, url
    """
    url           = '/_'
    requires_auth = True
    blueprint     = BluePrint('couchview', __name__)

    @use_local_template
    def list_databases(self):
        """
        {# renders a list of all databases together with a link to their futon page #}
        <table>
          <tr><td>database name (click for detail)</td><td>link to futon</td></tr>
          {% for x in databases%}
          <tr>
            <td><a href="/_?db={{x}}"><b>{{x}}</b></a></td>
            <td><a href="{{couch_base}}{{x}}">(futon)</a></td>
          </tr>
          {%endfor%}
        </table>
        """
        couch_base = (self % 'couch.server') + '_utils/database.html?'
        return dict(couch_base=couch_base, databases=self.databases)

    @use_local_template
    def list_views(self):
        """
        {# renders a list of all views.. #}
        <table>
          <tr>
             <td>view</td>
             <td>url</td>
             <td>from module</td>
             <td>related views</td>
          </tr>
          <tr><td colspan=3> <hr/></td></tr>
          {% for v in views %}
          <tr>
            <td><b>{{v.__name__}}</b></td>
            <td><i>{{v.url}}</i></td>
            <td><small>{{v.__class__.__module__}}<small></td>
            <td>{%for x in v.__class__.related_views %}{{x.__name__}} | {%endfor%}</td>
            <td>{{v.parent_url}}</td>
          </tr>
          {%endfor%}
        </table>
        """
        return dict(views=self.settings._installed_views)

    @use_local_template
    def db_detail(self, db_name):
        """
        {# given a db, renders length, an example key value, and guesses at the schema #}
        <table>
        {% for x,y in stats%}
        <tr><td><b>{{x}}</b></td><td>{{y}}</td></tr>
        {%endfor%}
        </table>
        """
        db        = get_db(db_name)
        enum      = [x for x in db]
        length    = len(enum)
        key_style = [k for k in db[enum[0]].keys() if not k.startswith('_')] if length else []
        stats     = dict(length=length,
                         key = length and enum[0],
                         schema=key_style)
        return dict(stats=stats.items())

    @use_local_template
    def index(self):
        """
        <a href=/_?action=db> list databases</a><br/>
        <a href=/_?action=views> list views</a><br/>
        """
        return dict()
    def main(self):
        """ dispatch to either the list function or the detail function"""

        action  = self['action']
        if action=='views':
            return self.list_views()
        elif action=='db':
            db_name = self['db']
            if db_name:
                return self.db_detail(db_name)
            else:
                return self.list_databases()
        else:
            return self.index()


    @property
    def databases(self): return [ x for x in self.server ]