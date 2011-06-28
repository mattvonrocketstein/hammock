#!/usr/bin/env python
""" hammock.bin._hammock:

    command line script
"""

from optparse import OptionParser

def parser():
    """ builds the parser object """
    class Parser(OptionParser):
        def error(self, msg):
            pass
    parser = Parser()

def PARSER():
    p               = parser()
    return p.parse_args()
    #handle_main_argument(*PARSER())

def entry():
    """ Main entry point """
    from hammock import app
    #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
    #app.run()#def run(self, host='127.0.0.1', port=5000, **options):
    app.run(host='0',port=5000)

if __name__=='__main__':
    entry()
