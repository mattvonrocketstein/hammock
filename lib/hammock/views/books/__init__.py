""" hammock.views.books

    http://www.jamendo.com/en/album/27535
    http://blog.skitsanos.com/2009/11/jquerycouchjs-cheatsheet.html
    http://stackoverflow.com/questions/5982638/using-cherrypy-cherryd-to-launch-multiple-flask-instances
"""
from flask import jsonify
from jinja2 import Template
from flask import request, render_template, redirect
from couchdb.client import ResourceNotFound

from report import report

from hammock._couch import document2namedt
from hammock._couch import unpack_as_schema
from hammock.utils import authorization_required
from hammock.views.db import DBView, use_local_template

from .schema import BookSchema


class BookAbstract(DBView):
    """ partial replacement  for reader.zgct """

    url           = '/books'
    database_name = 'books'
    methods       = ['GET', 'POST']
    template      = 'books.html'
    edit_template = 'books_dialog_ajax.html'
    db_schema     = BookSchema
    redirect_success = '/books'

    def schema(self):
        """ returns a new, empty entry for the books database """
        schema = super(BookAbstract, self).schema()
        #schema = DBView.schema(self)
        schema.update(index=len(list(self.rows)))
        return schema

    def build_new_entry(self):
        """ almost ready to be promoted to DBView """
        entry = self.schema()   # as dictionary
        _id = entry['stamp']    # get new items key.
        self._db[_id] = entry   # save it..
        entry = self._db[_id]   # as document
        return entry

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


class BookList(BookAbstract):
    update_url    = BookUpdate.url

    @authorization_required
    def remove(self):
        _id   = self['remove']
        report("Removing {id} from {db}", id=_id, db=self.database_name)
        del self._db[_id]
        return jsonify(dict(ok='true'))

    @authorization_required
    def edit(self):
        """ TODO: make decorator for the self.authorized bit """
        defaultTemplate = '<input id=input_{{x}} style="width:250px;" value="{{y}}" type=text>'

        _id   = self['id']
        entry = self.build_new_entry() if _id=='new' else self.get_entry(_id)
        _id   = entry.id
        test  = lambda x: not x.startswith('_') and x not in self.db_schema._no_edit

        obj = []
        for key,val in entry.items():
            if not test(key): continue
            else:
                template = self.db_schema._render.get(key, defaultTemplate)
                val = Template(template).render(x=key, y=val)
                obj.append([key, val])

        return render_template(self.edit_template,
                               update_url=self.update_url,
                               redirect_success=self.redirect_success,
                               id=_id,
                               obj=obj)
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
