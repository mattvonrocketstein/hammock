#!/usr/bin/env python
""" hammock.bin._hammock:

    command line script
"""

def entry(settings=None):
    """ Main entry point """
    if not settings:
        from hammock import conf
        settings = conf.Settings()
        conf.settings = settings

    if settings['user.shell']:
        from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
    else:
        app = settings.app
        app.run(host=settings['flask.host'],
                port=int(settings['flask.port']),
                debug=settings['flask.debug'])

if __name__=='__main__':
    entry()
