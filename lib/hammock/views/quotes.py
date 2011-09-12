from .books import BookSchema, BookList, BookUpdate

class QuoteSchema(BookSchema):
    source   = ''
    format   = 'raw'
    content  = ''
    _render  = dict(content='<textarea style="font-size:7pt;font-family:comic sans ms" style="color:#003399" id=input_{{x}} rows=20 cols=90>{{y}}</textarea>')
    #_no_edit = 'index stamp'.split()
    _no_edit = 'stamp'.split()

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
    def _all_unique_tags(self):
        return []

class QuoteList(QuoteAbstract,BookList):
    def _list(self):
        """ temporary until i figure out how to ask couch to do this """
        return [x for x in reversed(super(QuoteList,self)._list())]


class QuoteUpdate(QuoteAbstract, BookUpdate):
    url           = QuoteList.update_url

    #@authorization_required
    def main(self):
        #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        return super(QuoteUpdate,self).main()
