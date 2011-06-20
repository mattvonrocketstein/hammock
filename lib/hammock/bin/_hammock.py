#!/usr/bin/env python
""" hammock.bin.hammock:  the command line script
"""

def fpath2namespace(fpath):
    """ """
    namespace  = fpath.namebase
    if namespace == '__init__':
        namespace = fpath.dirname().namebase
    return namespace

def parser():
    """ builds the parser object """
    class Parser(OptionParser):
        def error(self, msg):
            pass
    parser = Parser()

    return parser

def announce_discovery(fpath, plugin_obj):
    """ placeholder """
    # print "\tfound plugin",fpath,plugin_obj, plugin_obj.__class__.__bases__
    pass

def plugin_search_results():
    """ NOTE: currently the search-path only includes kinbaku's root module """
    plugins         = []
    fileself        = path(__file__).abspath()
    container       = fileself.dirname().dirname().abspath()
    container_all   = [ x.abspath() for x in container.files() if x.abspath()!=fileself and x.namebase!='__init__']
    container_files = [ x for x in container_all if x.ext == '.py']
    module_dir      = lambda x: any([y.name=='__init__.py' for y in x.files()])
    module_roots    = [ x + path('/__init__.py') for x in container.dirs() if module_dir(x) ]

    file_options    = container_files + module_roots
    for fpath in file_options:
        reality    = globals()
        shadow     = copy.copy(globals())
        namespace  = fpath2namespace(fpath)
        shadow.update(dict(__name__=namespace))
        execfile(fpath, shadow)
        difference = list(set(shadow.keys())-set(reality.keys()))
        if "plugin" in difference:
            plugin_obj = shadow['plugin']
            plugins.append([fpath, plugin_obj])
            announce_discovery(fpath, plugin_obj)
    return plugins

def PARSER():
    p               = parser()
    return p.parse_args()

def entry():
    """ Main entry point
        NOTE: takes no arguments without defaults.. """
    from hammock import zoo
    app.run()


if __name__=='__main__':
    entry()
