""" hammock/auth
"""
from flask import render_template, g, flash
from flask import request, session, redirect
from hammock.util import report

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

def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect('/')

def login():
    """ Logs the user in.
        TODO: add back hashing after everything else is working
    """
    if g.user:
        print g,g.user
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
    return render_template('login.html', error=error)
