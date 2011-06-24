# -*- coding: utf-8 -*-
"""
"""

import time
from contextlib import closing
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash
from werkzeug import check_password_hash, generate_password_hash

DEBUG       = True
SERVER      = 'http://dojo.robotninja.org:5984/'
CREDENTIALS = ('matt', 'lemmein')

center_zoom=6

app = Flask(__name__)
app.config.from_object(__name__)

@app.before_request
def before_request():
    """Make sure we are connected to the database each request and look
    up the current user so that we know he's there.
    """
    #g.db = connect_db()
    g.user = None
    if 'user_id' in session:
        print 'logged in'
        g.user='superuser'

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
    db = couch['coordinates']
    def coordinates():
        return filter(lambda x: not x.startswith('_design'), db)
    points=[]
    for _id in coordinates():
        obj = db[_id]
        if 'coords' not in obj:
            print 'dirty entry in coordinates database.. removing it'
            #del db[_id]
            continue
        print '-'*10,_id, obj['coords']
        lat, lon = obj['coords'].split(',')
        label = obj.get('label', 'label is empty')
        points.append([lat,lon,label])

    return render_template('index.html', points=points,
                           center_lat='43.907787',
                           center_lon='-79.359741',
                           center_zoom=center_zoom)
@app.route('/set', methods=['GET', 'POST'])
def set_location():
    """ sets a location """
    if not g.user:
        return redirect('/login')
    return render_template('set.html',
                           center_lat='43.907787',
                           center_lon='-79.359741',
                           center_zoom=center_zoom
                           )


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['user_id']=None
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
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

@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect('/')

def list_db(item, db):
    if not item.startswith('_design'): #skip design-docs
        print item, db[item]

def setup():
    import couchdb
    global couch
    couch = couchdb.Server(SERVER)
    couch.resource.credentials = CREDENTIALS

setup()
db = couch['coordinates']
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__=='__main__':
    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
