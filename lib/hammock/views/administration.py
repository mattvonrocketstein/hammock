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
        <center><table style="width:90%;">
          {% for x in databases%}
          <tr>
            <td><b>{{x}}</b></td>
            <td>
               <a href="/_?action=db&db={{x}}">view schema</a></td><td>
               <a href="{{couch_base}}{{x}}">browse database</a>
            </td>
          </tr>
          {%endfor%}
        </table></center>
        """
        #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        settings = self.settings['couch']
        couch_base = "http://{0}:{1}/{2}".format(
            settings['host'],
            settings['port'],
            '_utils/database.html?')
        return dict(couch_base=couch_base, databases=self.databases)

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
        <a href=/_?action=tro> show template search order</a><br/>
        <a href=/_?action=db> list databases</a><br/>
        <a href=/__views__> list views</a><br/>
        """
        return dict()

    @use_local_template
    def action_tro(self):
        """ <h2>app.jinja_loader.searchpath:</h2>
        {%for p in searchpath%}<p>{{p}}</p>{%endfor%} """
        return dict(searchpath=self.app.jinja_loader.searchpath)

    def main(self):
        """ dispatch to either the list function or the detail function"""

        def db_action():
            db_name = self['db']
            if db_name:
                return self.db_detail(db_name)
            else:
                return self.list_databases()

        action  = self['action']
        if action=='db':    return db_action()
        elif action=='tro': return self.action_tro()
        else:               return self.index()


    @property
    def databases(self):
        """ TODO: move this to the settings object itself """
        dbs = [ getattr(v, 'database_name', None) for v in self.settings._installed_views ]
        dbs = list(set([ x for x in dbs if x]))
        return dbs
