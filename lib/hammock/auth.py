""" hammock/auth
"""
from werkzeug import check_password_hash, generate_password_hash

from flask import render_template, g, flash
from flask import request, session, redirect

from hammock.util import report
from corkscrew import View

def auth_redirect(self):
    _next = request.referrer
    if not _next or self.url in _next:
        _next = '/?tag=recent'
    return redirect(_next)

class Logout(View):
    """Logs the user out."""
    url     = '/logout'
    methods = ["GET"]

    def main(self):
        flash('You were logged out')
        session.pop('user_id', None)
        return auth_redirect(self)

class Login(View):
    """ Logs the user in.

        TODO: send them back where they came from, and not to /
    """
    url      = '/login'
    methods  = methods = ["GET", "POST"]
    template = 'login.html'

    def main(self):
        """
            TODO: add back hashing after everything else is working
            TODO: convert to dispatch view
        """
        if self.authorized:
            report('already authorized', self.user)
            return auth_redirect(self)

        if request.method == 'POST':
            users = self.settings%'users'
            user = self['username']
            if user not in users:
                return self.render_template(error='Invalid username')
            if not check_password_hash(users[user],self['password']):
                return self.render_template(error='Invalid password')
            else:
                flash('You were logged in')
                session['user_id'] = user
                return auth_redirect(self)
        return render_template(self.template)
