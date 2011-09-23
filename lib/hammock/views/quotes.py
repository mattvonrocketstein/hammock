""" hammock.views.quotes
"""

from .books import BookList, BookUpdate
from .books.schema import BookSchema

class QuoteSchema(BookSchema):
    source   = ''
    format   = 'raw'
    content  = ''
    _render  = dict(content='<textarea style="font-size:7pt;font-family:comic sans ms" style="color:#003399" id=input_{{key}} rows=20 cols=90>{{value}}</textarea>')
    _no_edit = 'index stamp'.split()

class QuoteAbstract(object):
    url           = '/quotes'
    database_name = 'quotes'
    methods       = ['GET', 'POST']
    template      = 'quotes.html'
    edit_template = 'quotes_dialog_ajax.html'
    db_schema     = QuoteSchema
    update_url    = '/quotes/update'
    redirect_success = '/quotes'
    # TMP
    #def _all_unique_tags(self):
    #    return []

class QuoteList(QuoteAbstract,BookList):
    def _list(self):
        """ temporary until i figure out how to ask couch to do this """
        return [x for x in reversed(super(QuoteList,self)._list())]


class QuoteUpdate(QuoteAbstract, BookUpdate):
    url           = QuoteList.update_url

    #@authorization_required
    def main(self):
        return super(QuoteUpdate,self).main()
