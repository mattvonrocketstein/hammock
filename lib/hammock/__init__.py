# -*- coding: utf-8 -*-
"""
"""

import datetime
from flask import render_template, abort, g, flash
from flask import Flask, request, session, url_for, redirect

from werkzeug import check_password_hash, generate_password_hash

from hammock._math import box, calculate_center
from hammock.data import *

## Begin flask setup
app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

## Begin flask plumbing

def before_request():
    """ Make sure we are connected to the database
        each request and look up the current user
        so that we know he's there.
    """
    g.user = None
    if 'user_id' in session:
        print 'logged in'
        g.user='superuser'

def after_request(response):
    """ nothing to do here so far. """
    return response

before_request = app.before_request(before_request)
after_request = app.after_request(after_request)

@app.route('/')
def slash():
    """ the homepage:
        renders all geocoordinates in coordinate database,
        along with labels.
    """
    db = couch['coordinates']
    points=[]
    for _id in coordinates(db):
        obj = db[_id]
        if 'coords' not in obj:
            print 'dirty entry in coordinates database.. removing it'
            #del db[_id]
            continue
        print '-'*10,_id, obj['coords']
        lat, lon = obj['coords'].split(',')
        label = obj.get('label', 'label is empty')
        if g.user:
            js = "$.post('/remove',{id:'" + _id + "'});window.location='/';"
            js = "do_remove(\\x27"+_id+"\\x27);"#.replace("'",'\\x27')
            #js = """alert('"""+_id+"""');""".replace("'",r'\\x27')
            control  = '''<br/><span><a href="javascript:{js}">remove this point</a></span>'''
            control  = control.format(js=js)
            label   += control
        points.append([lat,lon,label])
    center_lat,center_lon = calculate_center(points)
    minLat, minLng, maxLat, maxLng = box(points)
    return render_template('index.html',
                           points=points,
                           center_lat=center_lat,
                           center_lon=center_lon,
                           minLat=minLat, minLng=minLng,
                           maxLat=maxLat, maxLng=maxLng,
                           center_zoom=center_zoom)



@app.route('/remove',methods=['POST'])
def remove():
    if not g.user:
        return redirect('/login')
    if request.method=='POST':
        print 'removing',request.form['id']
        del couch['coordinates'][request.form['id']]
        return redirect('/')

@app.route('/set', methods=['GET', 'POST'])
def set_location():
    """ sets a location """
    if not g.user:
        return redirect('/login')
    if request.method == 'POST':
        db = couch['coordinates']
        date_str = str(datetime.datetime.now())
        data = {'coords':request.form['coords'].replace('(','').replace(')',''),
                'tag':date_str,
                }
        db[date_str] = data
        # this is ignored since it's posted with ajax..
        return redirect('/')
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

@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect('/')

## Begin couch-specific stuff
def setup():
    import couchdb
    global couch
    couch = couchdb.Server(SERVER)
    couch.resource.credentials = CREDENTIALS

def coordinates(db):
    return filter(lambda x: not x.startswith('_design'), db)

setup()

if __name__=='__main__':
    # hook for to clean up the database by hand
    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
