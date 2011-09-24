""" hammock.views.books

    http://www.jamendo.com/en/album/27535
    http://blog.skitsanos.com/2009/11/jquerycouchjs-cheatsheet.html
    http://stackoverflow.com/questions/5982638/using-cherrypy-cherryd-to-launch-multiple-flask-instances
"""
from flask import request

from hammock._couch import document2namedt
from hammock._couch import unpack_as_schema
from hammock.utils import authorization_required
from hammock.views.mixins import Removable, Editable

from .abstract import BookAbstract

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

class BookList(BookAbstract, Removable, Editable):
    update_url    = BookUpdate.url

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
