""" hammock.views.books

    http://www.jamendo.com/en/album/27535
    http://blog.skitsanos.com/2009/11/jquerycouchjs-cheatsheet.html
    http://stackoverflow.com/questions/5982638/using-cherrypy-cherryd-to-launch-multiple-flask-instances
"""
import datetime

from flask import request, render_template
from couchdb.client import ResourceNotFound

from hammock._couch import document2namedt
from hammock.views.db import DBView, use_local_template
from report import report

class BookList(DBView):
    """ partial replacement  for reader.zgct """

    url           = '/books'
    database_name = 'books'
    methods       = ['GET', 'POST']

    def _all_unique_tags(self):
        """ TODO: remove when coordinates-db supports "tags" instead of just "tag"
        """
        q = '''function(doc){emit(null, doc.%s);}'''%'tags'
        out = reduce(lambda x,y: x+y,[x.value for x in self._db.query(q)])
        out = set(out)
        return out

    @property
    def schema(self):
        """ returns a new, empty entry for the books database """
        return dict(author='',
                    tags=[],
                    title='',
                    index=len(list(self.rows)),
                    stamp=str(datetime.datetime.utcnow()))

    def edit(self):
        _id = self['id']
        if _id=='new':
            entry = self.schema     # as dictionary
            _id = entry['stamp']    # get new items key.
            self._db[_id] = entry   # save it..
            entry = self._db[_id]   # as document
        else:
            try:
                entry = self._db[_id]
            except ResourceNotFound,e:
                report('resource with key "{id}" not found',id=_id)
                raise

        obj = [ x for x in entry.items() if not x[0].startswith('_') ]
        return render_template('books_dialog_ajax.html',
                               id=_id, obj=obj)

    def list(self):
        return render_template('books.html',
                               authenticated = self.authorized,
                               tags=self._all_unique_tags(),
                               booklist=[document2namedt(obj) for k,obj in self.rows])

    def main(self):
        #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        return self.edit() if self['id'] else self.list()

class BookUpdate(BookList):
    requires_auth = True
    methods       = ['GET']
    url           = '/books/update'
    returns_json  = True

    def main(self):
        doc = self._db[self['id']]
        index = self['index']
        author = self['author']
        title = self['title']
        tags = eval(self['tags'])
        doc.update(tags=tags, title=title, index=int(index), author=author)
        self._db[self['id']] = doc
        return dict(ok='true')


if __name__=='__main__':
    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
