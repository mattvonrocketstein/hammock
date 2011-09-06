""" hammock.views.books
"""

from hammock._couch import document2namedt
from hammock.views.db import DBView, use_local_template


class BookList(DBView):
    """ partial replacement  for reader.zgct """

    url = '/books'
    database_name = 'books'

    @use_local_template
    def main(self):
        """
        <table>
        {%for book in booklist%}
        <tr><td>{{book.index}}. {{book.author}}: {{book.title}} <small>{{book.tags}}</small></td></tr>
        {%endfor%}
        </table>
        """
        return dict(booklist=[document2namedt(self._db[k]) for k in self._db])
