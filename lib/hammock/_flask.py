""" hammock._flask

    Extensions for flask
"""

from flask import request, g

class FlaskView(object):
    """ """
    def asdf__new__(kls, *args, **kargs):
        """ """
        if args or kargs:
            raise NotImplemented
        instance = object.__new__(kls)
        instance.__name__ = kls.__name__.lower()
        return instance

    def __init__(self,app=None):
        """ """
        self.__name__=self.__class__.__name__.lower()
        if app is not None:
            if self.url:
                app.add_url_rule(self.url, self.__name__, self)
            else:
                raise NotImplemented

    def __call__(self):
        """ """
        return self.main()

    def __getitem__(self, k):
        return request.values.get(k, None)

class HammockView(FlaskView):
    @property
    def settings(self):
        """ cache this """
        from hammock.conf import settings
        return settings

    @property
    def authorized(self):
        """ """
        from hammock.auth import authenticated
        return authenticated(g)
