""" hammock/crud/update
"""

# TODO: not yet generic.. moved to robotninja.coords
#from .remove import Remove
#TODO: move to utilities
#from hammock.util import nomprivate_editable
from jinja2 import Template
from flask import render_template

from report import report

from hammock.utils import authorization_required

def nonprivate_editable(key, db_schema):
    """ """
    return not key.startswith('_') and key not in db_schema._no_edit


class Editable(object):
    """

    Mixin requires:

      edit_template::

      update_url::

      db_schema::

      redirect_success::
        where to redirect to on successful update.
        templates may choose not to use this.
    """

    @authorization_required
    def edit(self):
        widget_template = '<input id=input_{{key}} style="width:250px;" value="{{value}}" type=text>'

        # get or create a new entry id
        _id   = self['id']
        entry = self.build_new_entry() if _id=='new' else self.get_entry(_id)
        _id   = entry.id

        editable_parts = []

        items = [ [key, val] for key,val in entry.items() \
                  if nonprivate_editable(key,self.db_schema) ]
        for key, val in items:
            template = self.db_schema._render.get(key, widget_template)
            widget = Template(template).render(key=key, value=val)
            editable_parts.append([key, widget])

        return render_template(self.edit_template,
                               update_url=self.update_url,
                               id=_id,
                               obj=editable_parts)
