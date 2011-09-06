""" hammock.views.books

    http://www.jamendo.com/en/album/27535
    http://blog.skitsanos.com/2009/11/jquerycouchjs-cheatsheet.html
    http://stackoverflow.com/questions/5982638/using-cherrypy-cherryd-to-launch-multiple-flask-instances
"""

from hammock._couch import document2namedt
from hammock.views.db import DBView, use_local_template


class BookList(DBView):
    """ partial replacement  for reader.zgct """

    url = '/books'
    database_name = 'books'

    def _all_unique_tags(self):
        q = '''function(doc){emit(null, doc.%s);}'''%'tags'
        out = reduce(lambda x,y: x+y,[x.value for x in self._db.query(q)])
        out=set(out)
        return out

    @use_local_template
    def main(self):
        """
        tags: {%for t in tags%}
        <a href="/books?tag={{t}}">{{t}}</a> |
        {%endfor%}
        <hr/>
        <table>
        {%for book in booklist%}
        <tr><td>{{book.index}}. {{book.author}}: {{book.title}} <small>{{book.tags}}</small></td></tr>
        {%endfor%}
        </table>
        """
        return dict(tags=self._all_unique_tags(),
                    booklist=[document2namedt(obj) for k,obj in self.rows])

hrm = """
        <script src="/static/jquery.couch.js"></script>
        <script>
        // run this before anything else with $.couch
        $.couch.urlPrefix = "http://dojo.robotninja.org:5984/";
        $.couch.login({
        url: '/_session',
        name: 'matt',
        password: 'lemmein',
        success: function() {
        alert('Ready!');
        }
        });
        </script>
"""
