""" hammock.conf
"""
import os
import ConfigParser

from hammock.util import report

DEFAULT_SETTINGS = os.path.abspath(os.path.join(os.path.split(__file__)[0], "hammock.ini"))

class Settings(object):
    """ """

    from optparse import OptionParser
    parser = OptionParser()
    parser.set_conflict_handler("resolve")
    parser.add_option("--port",  dest="port",
                      default='', help="server listen port")
    parser.add_option("--shell", dest="shell",
                      default=False, help="hammock db shell",
                      action='store_true')
    parser.add_option("--config", dest='config',
                      default="./hammock.ini",
                      help="use config file")

    def __init__(self):
        """
            first load the default config so that overrides don't need
            to mention everything.  update default with the config
            specified by the command line optionparser, then
            update that with any other overrides delivered to the parser.
        """
        self.options, self.args = Settings.parser.parse_args()
        self._settings = self.load(file=DEFAULT_SETTINGS)
        self._settings.update(self.load(file=self.options.config))

        # a few command line options are allowed to override the .ini
        if self.options.port:
            self._settings.update({'hammock.port':self.options.port})

        self.shell = self.options.shell

        # TODO: move this to ConfigParser subclass.
        # allow pythonic comments in the .ini files,
        # and strip any trailing whitespace.
        for k,v in self._settings.items():
            self._settings[k]=v.strip()
            if '#' in v:
                self._settings[k]=v[:v.find('#')]
        report('finished parsing settings from',
               Global=DEFAULT_SETTINGS,
               Local=self.options.config)

    def __getitem__(self,k):
        """ proxy to settings dictionary """
        return self._settings[k]

    def load(self, file, config={}):
        """ returns a dictionary with key's of the form
            <section>.<option> and the values
        """
        if not os.path.exists(file):
            raise ValueError,'config file @{f} does not exist'.format(f=file)
        config = config.copy()
        cp = ConfigParser.ConfigParser()
        cp.read(file)
        for sec in cp.sections():
            name = sec.lower()
            for opt in cp.options(sec):
                config[name + "." + opt.lower()] = cp.get(sec, opt).strip()
        return config
