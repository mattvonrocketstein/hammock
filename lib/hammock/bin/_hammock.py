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
    app.run()


if __name__=='__main__':
    entry()
