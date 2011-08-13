""" hammock._flask

    Extensions for flask
"""

from flask import request, jsonify, g

class FlaskView(object):
    """ """
    returns_json = False
    methods      = ('GET',)

    def __init__(self,app=None):
        """ """
        self.__name__=self.__class__.__name__.lower()
        if app is not None:
            if self.url:
                app.add_url_rule(self.url, self.__name__, self,
                                 methods=self.methods)

    def __call__(self):
        """ """
        result = self.main()
        if self.returns_json:
            result = jsonify(**result)
        return result

    def __getitem__(self, k):
        return request.values.get(k, None)

    @property
    def user(self):
        return g.user

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
