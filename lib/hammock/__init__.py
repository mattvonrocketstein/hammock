# -*- coding: utf-8 -*-
"""
"""
from __future__ import with_statement
import time
from contextlib import closing
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash
from werkzeug import check_password_hash, generate_password_hash

DEBUG = True
SECRET_KEY = 'development key'

app = Flask(__name__)
app.config.from_object(__name__)
#app.config.from_envvar('MINITWIT_SETTINGS', silent=True)

def init_db():
    """Creates the database tables."""
    return

def get_user_id(username):
    """Convenience method to look up the id for a username."""
    rv = g.db.execute('select user_id from user where username = ?',
                       [username]).fetchone()
    return rv[0] if rv else None

@app.before_request
def before_request():
    """Make sure we are connected to the database each request and look
    up the current user so that we know he's there.
    """
    #g.db = connect_db()
    g.user = None
    if 'user_id' in session:
        print 'logged in'
        #g.user = query_db('select * from user where user_id = ?',
        #                  [session['user_id']], one=True)


@app.after_request
def after_request(response):
    """Closes the database again at the end of the request."""
    #g.db.close()
    return response


@app.route('/')
def slash():
    """Shows a users timeline or if no user is logged in it will
    redirect to the public timeline.  This timeline shows the user's
    messages as well as all the messages of followed users.
    """
    #if not g.user:
    #    return redirect(url_for('public_timeline'))
    go()
    return render_template('index.html', points=[43.91892,-78.89231])

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        user = query_db('''select * from user where
            username = ?''', [request.form['username']], one=True)
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user['pw_hash'],
                                     request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['user_id'] = user['user_id']
            return redirect(url_for('timeline'))
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or \
                 '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif get_user_id(request.form['username']) is not None:
            error = 'The username is already taken'
        else:
            g.db.execute('''insert into user (
                username, email, pw_hash) values (?, ?, ?)''',
                [request.form['username'], request.form['email'],
                 generate_password_hash(request.form['password'])])
            g.db.commit()
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)


@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('/'))


def go():
    import couchdb
    couch = couchdb.Server('http://dojo.robotninja.org:5984/')
    couch.resource.credentials = ('matt', 'lemmein')
    db = couch['coordinates']
    for item in db:
        if not item.startswith('_design'): #skip design-docs
            print item, db[item]
            if not db[item]:
                del db[item]
if __name__ == '__main__':
    pass#app.run()
