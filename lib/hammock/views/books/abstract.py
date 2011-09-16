""" hammock.views.books.abstract
"""
from hammock.views.db import DBView, use_local_template
from .schema import BookSchema

class BookAbstract(DBView):
    """ partial replacement  for reader.zgct """

    url              = '/books'
    database_name    = 'books'
    methods          = ['GET', 'POST']
    template         = 'books.html'
    edit_template    = 'books_dialog_ajax.html'
    db_schema        = BookSchema
    redirect_success = '/books'

    def schema(self):
        """ returns a new, empty entry for the books database """
        schema = super(BookAbstract, self).schema()
        schema.update(index=len(list(self.rows)))
        return schema

    def build_new_entry(self):
        """ almost ready to be promoted to DBView """
        entry = self.schema()   # as dictionary
        _id = entry['stamp']    # get new items key.
        self._db[_id] = entry   # save it..
        entry = self._db[_id]   # as document
        return entry
