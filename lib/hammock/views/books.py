""" hammock.views.books

    http://www.jamendo.com/en/album/27535
    http://blog.skitsanos.com/2009/11/jquerycouchjs-cheatsheet.html
    http://stackoverflow.com/questions/5982638/using-cherrypy-cherryd-to-launch-multiple-flask-instances
"""
import datetime

from flask import request, render_template, redirect
from couchdb.client import ResourceNotFound

from report import report

from hammock._couch import document2namedt
from hammock._couch import Schema
from hammock.views.db import DBView, use_local_template


class BookSchema(Schema):
    author = ''
    title  = ''
    tags   = []
    stamp  = lambda: str(datetime.datetime.utcnow())
    index  = 0

class QuoteSchema(BookSchema):
    source = ''
    format = 'raw'

class BookList(DBView):
    """ partial replacement  for reader.zgct """

    url           = '/books'
    database_name = 'books'
    methods       = ['GET', 'POST']
    template      = 'books.html'
    edit_template = 'books_dialog_ajax.html'
    db_schema     = BookSchema

    def schema(self):
        """ returns a new, empty entry for the books database """
        schema = super(BookList,self).schema()
        schema.update(index=len(list(self.rows)))
        return schema

    def build_new_entry(self):
        """ almost ready to be promoted to DBView """
        entry = self.schema()   # as dictionary
        _id = entry['stamp']    # get new items key.
        self._db[_id] = entry   # save it..
        entry = self._db[_id]   # as document
        return entry

    def edit(self):
        """ TODO: make decorator for the self.authorized bit """
        if not self.authorized:
            return redirect(self.url)
        _id   = self['id']
        entry = self.build_new_entry() if _id=='new' else self.get_entry(_id)
        obj   = [ x for x in entry.items() if not x[0].startswith('_') ]
        return render_template(self.edit_template, id=_id, obj=obj)

    def list(self):
        """ TODO: use named tuples by default with self.rows? """
        booklist = [ document2namedt(obj) for k, obj in self.rows ]
        tags     = self._all_unique_tags()
        return self.render_template(tags=tags, booklist=booklist)

    def main(self):
        return self.edit() if self['id'] else self.list()

class BookUpdate(BookList):
    requires_auth = True
    methods       = ['GET']
    url           = '/books/update'
    returns_json  = True

    def main(self):
        doc    = self._db[self['id']]
        index  = self['index']
        author = self['author']
        title  = self['title']
        tags   = eval(self['tags'])
        doc.update(tags=tags, title=title, index=int(index), author=author)
        self._db[self['id']] = doc # actually necessary after .update()?
        return dict(ok='true')


if __name__=='__main__':
    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
