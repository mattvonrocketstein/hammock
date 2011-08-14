""" hammock/auth
"""
from werkzeug import check_password_hash, generate_password_hash

from flask import render_template, g, flash
from flask import request, session, redirect

from hammock.util import report
from hammock._flask import HammockView

def authenticated(g): return True if g.user else False

def requires_authentication(fxn):
    def new_fxn(*args, **kargs):
        if not g.user:
            report('view requires authentication..redirecting to login',[fxn,g.user])
            return redirect('/login')
        else:
            result = fxn(*args, **kargs)
            return result
    return new_fxn

class Logout(HammockView):
    """Logs the user out."""
    url     = '/logout'
    methods = ["GET"]

    def main(self):
        flash('You were logged out')
        session.pop('user_id', None)
        return redirect('/')

class Login(HammockView):
    """ Logs the user in """
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
            return redirect('/')
        error = None
        if request.method == 'POST':
            user = dict(user_id='superuser',pw_hash='test')
            if user is None:
                error = 'Invalid username'
            elif not user['pw_hash']==request.form['password']:
            #elif not check_password_hash(user['pw_hash'],
            #                             request.form['password']):
                error = 'Invalid password'
            else:
                flash('You were logged in')
                session['user_id'] = user['user_id']
                return redirect('/')
        return render_template(self.template, error=error)
