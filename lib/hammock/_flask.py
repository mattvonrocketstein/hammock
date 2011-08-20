""" hammock._flask

    Extensions for flask
"""


import os
import ConfigParser

from flask import request, jsonify, g, redirect
from flask import render_template

from hammock.util import report
from hammock.util import report

class FlaskSettings(object):
    """ combination option parser / settings parser for flask
        that reads the .ini format.
    """

    @classmethod
    def get_parser(self):
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
        return parser

    def __contains__(self,other):
        """ dictionary compatability """
        return other in self._settings

    def __getitem__(self,k):
        """ dictionary compatability """
        return self._settings[k]


    def __init__(self):
        """
            first load the default config so that overrides don't need
            to mention everything.  update default with the config
            specified by the command line optionparser, then
            update that with any other overrides delivered to the parser.
        """
        self.options, self.args = self.get_parser().parse_args()
        self._settings = self.load(file=self.DEFAULT_SETTINGS)
        self._settings.update(self.load(file=self.options.config))

        # a few command line options are allowed to override the .ini
        if self.options.port:
            self._settings.update({'flask.port':self.options.port})

        # build a special section for things the user wants,
        # ie, things that have been passed into the option
        # parser but are not useful in the .ini
        self._settings.update({'user.shell' : self.options.shell and 'true' or ''})

        # TODO: move this to ConfigParser subclass.
        # allow pythonic comments in the .ini files,
        # and strip any trailing whitespace.
        for k,v in self._settings.items():
            self._settings[k]=v.strip()
            if '#' in v:
                self._settings[k]=v[:v.find('#')]
        report('finished parsing settings from',
               Global=self.DEFAULT_SETTINGS,
               Local=self.options.config)


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

class FlaskView(object):
    """ encapsulates a few of the flask semantics into one object """

    returns_json  = False
    methods       = ('GET',)
    requires_auth = False

    def __init__(self,app=None):
        """ """
        self.__name__=self.__class__.__name__.lower()
        if app is not None:
            if self.url:
                app.add_url_rule(self.url, self.__name__, self,
                                 methods=self.methods)

    def __call__(self):
        """ """
        if self.requires_auth and not self.authorized:
            report('view requires authentication..redirecting to login',[self, g.user])
            return redirect('/login')
        result = self.main()
        if self.returns_json:
            result = jsonify(**result)
        return result

    def __getitem__(self, k):
        return request.values.get(k, None)

    @property
    def user(self):
        return g.user

    @property
    def authorized(self):
        """ """
        return True if g.user else False

    def render_template(self, **kargs):
        return render_template(self.template, **kargs)

class HammockView(FlaskView):

    def render_template(self, **kargs):
     kargs.update(authenticated = self.authorized)
     return super(HammockView,self).render_template(**kargs)

    @property
    def settings(self):
        """ cache this """
        from hammock.conf import settings
        return settings



def namedAny(name):
    """
    Retrieve a Python object by its fully qualified name from the global Python
    module namespace.  The first part of the name, that describes a module,
    will be discovered and imported.  Each subsequent part of the name is
    treated as the name of an attribute of the object specified by all of the
    name which came before it.  For example, the fully-qualified name of this
    object is 'twisted.python.reflect.namedAny'.

    @type name: L{str}
    @param name: The name of the object to return.

    @raise InvalidName: If the name is an empty string, starts or ends with
        a '.', or is otherwise syntactically incorrect.

    @raise ModuleNotFound: If the name is syntactically correct but the
        module it specifies cannot be imported because it does not appear to
        exist.

    @raise ObjectNotFound: If the name is syntactically correct, includes at
        least one '.', but the module it specifies cannot be imported because
        it does not appear to exist.

    @raise AttributeError: If an attribute of an object along the way cannot be
        accessed, or a module along the way is not found.

    @return: the Python object identified by 'name'.
    """
    if not name:
        raise ValueError('Empty module name')

    names = name.split('.')

    # if the name starts or ends with a '.' or contains '..', the __import__
    # will raise an 'Empty module name' error. This will provide a better error
    # message.
    if '' in names:
        raise InvalidName(
            "name must be a string giving a '.'-separated list of Python "
            "identifiers, not %r" % (name,))

    topLevelPackage = None
    moduleNames = names[:]
    while not topLevelPackage:
        if moduleNames:
            trialname = '.'.join(moduleNames)
            try:
                topLevelPackage = _importAndCheckStack(trialname)
            except _NoModuleFound:
                moduleNames.pop()
        else:
            if len(names) == 1:
                raise ValueError("No module named %r" % (name,))
            else:
                raise ValueError('%r does not name an object' % (name,))

    obj = topLevelPackage
    for n in names[1:]:
        obj = getattr(obj, n)

    return obj
