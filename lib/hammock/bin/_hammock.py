#!/usr/bin/env python
""" hammock.bin._hammock:

    command line script
"""
import logging
log = logging.getLogger(__file__)

from optparse import OptionParser
parser = OptionParser()
parser.set_conflict_handler("resolve")
parser.add_option("-u", "--user",    dest="user",   default='',     help="couchdb user",)
parser.add_option("-p","--password", dest="passwd", default='',     help="couchdb password")
parser.add_option("-h", "--host",    dest="host",   default='',     help="couchdb host")
parser.add_option("--port",          dest="port",   default='5000', help="server listen port")
parser.add_option("--shell",         dest="shell",  default=False,  help="db shell",
                  action='store_true')

def entry():
    """ Main entry point """
    from hammock.data import Settings
    from hammock import app
    options, args = parser.parse_args()
    #Settings.load(
    if options.shell:
        from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
    else:
        app.run(host='0', port=int(options.port), debug=True)

if __name__=='__main__':
    entry()
