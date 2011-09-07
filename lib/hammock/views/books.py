""" hammock.views.books

    http://www.jamendo.com/en/album/27535
    http://blog.skitsanos.com/2009/11/jquerycouchjs-cheatsheet.html
    http://stackoverflow.com/questions/5982638/using-cherrypy-cherryd-to-launch-multiple-flask-instances
"""

from hammock._couch import document2namedt
from hammock.views.db import DBView, use_local_template

from flask import render_template

class BookList(DBView):
    """ partial replacement  for reader.zgct """

    url           = '/books'
    database_name = 'books'
    methods       = ['GET', 'POST']

    def _all_unique_tags(self):
        q = '''function(doc){emit(null, doc.%s);}'''%'tags'
        out = reduce(lambda x,y: x+y,[x.value for x in self._db.query(q)])
        out = set(out)
        return out

    def main(self):
        if self['id']:
            _id = self['id']
            obj = [ x for x in self._db[_id].items() if not x[0].startswith('_') ]
            #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
            return render_template('books_dialog_ajax.html',
                                   id=_id, obj=obj)
        return render_template('books.html',
                               authenticated = self.authorized,
                               tags=self._all_unique_tags(),
                               booklist=[document2namedt(obj) for k,obj in self.rows])
from flask import request
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
        #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        self._db[self['id']] = doc
        return dict(ok='true')
        #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
