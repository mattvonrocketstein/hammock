""" hammock.views.books

    http://www.jamendo.com/en/album/27535
    http://blog.skitsanos.com/2009/11/jquerycouchjs-cheatsheet.html
    http://stackoverflow.com/questions/5982638/using-cherrypy-cherryd-to-launch-multiple-flask-instances
"""
from flask import jsonify
from flask import request, render_template
from jinja2 import Template

from report import report

from hammock._couch import document2namedt
from hammock._couch import unpack_as_schema
from hammock.utils import authorization_required
from hammock.views.mixins import Removable

from .abstract import BookAbstract

def nonprivate_editable(key, db_schema):
    return not key.startswith('_') and key not in db_schema._no_edit

class BookUpdate(BookAbstract):
    requires_auth = True
    methods       = ['GET']
    url           = '/books/update'
    returns_json  = True

    def main(self):
        updated = unpack_as_schema(request, self.db_schema)
        doc     = self._db[self['id']]
        doc.update(**updated)
        self._db[self['id']] = doc
        return dict(ok='true')

class Editable(object):
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
                               redirect_success=self.redirect_success,
                               id=_id,
                               obj=editable_parts)

class BookList(BookAbstract, Removable, Editable):
    update_url    = BookUpdate.url

    def _list(self):
        return [ document2namedt(obj) for k, obj in self.rows ]

    def list(self):
        """ TODO: use named tuples by default with self.rows? """
        booklist = self._list()
        tags     = self._all_unique_tags()
        return self.render_template(tags=tags,
                                    this_url=self.url,
                                    item_list=booklist)

    def main(self):
        if self['id']:
            return self.edit()
        if self['remove']:
            return self.remove()
        else:
            return self.list()

if __name__=='__main__':
    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
