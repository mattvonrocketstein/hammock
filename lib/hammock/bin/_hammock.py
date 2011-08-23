#!/usr/bin/env python
""" hammock.bin._hammock:
     invokes hammock server from the command line.

     Usage:

"""

def entry(settings=None):
    """ Main entry point """
    from hammock import conf
    settings = conf.Settings()
    settings.run()

if __name__=='__main__':
    entry()
