""" hammock.views.books

    http://blog.skitsanos.com/2009/11/jquerycouchjs-cheatsheet.html
    http://stackoverflow.com/questions/5982638/using-cherrypy-cherryd-to-launch-multiple-flask-instances
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
        return dict(booklist=[document2namedt(obj) for k,obj in self.rows])
tagger = lambda tag: """
function(doc){
function inside(needle,haystack) {
        for(var i = 0; i < this.length; i++) {
            if(this[i] === needle) {
                return i;
            }
        }
        return -1;
    };

if(doc.tag=='"""+tag+"""' or inside('"""+tag+"""',doc.tags)){emit(null, doc);}
}"""
