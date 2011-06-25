# -*- coding: utf-8 -*-
"""
"""

import datetime
from flask import render_template, abort, g, flash
from flask import Flask, request, session, url_for, redirect

from werkzeug import check_password_hash, generate_password_hash

from hammock._math import box, calculate_center
from hammock.data import *
from hammock.auth import *
from hammock.plumbing import *

## Begin flask setup
app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = SECRET_KEY

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
            js = "do_remove(\\x27"+_id+"\\x27);"
            control  = CONTROL_T.format(link='''<a href="javascript:{js}">remove this point</a>'''.format(js=js))
            js = "do_label(\\x27"+_id+"\\x27);"
            control += CONTROL_T.format(link='''<a href="javascript:{js}">adjust label for this point</a>'''.format(js=js))
            js = "do_label(\\x27"+_id+"\\x27);"
            control += CONTROL_T.format(link='''<a href="javascript:{js}">adjust tag for this point</a>'''.format(js=js))
            label   += control
        points.append([lat,lon,label])
    center_lat,center_lon = calculate_center(points)
    minLat, minLng, maxLat, maxLng = box(points)
    return render_template('index.html',
                           authenticated=authenticated(g),
                           points=points,
                           center_lat=center_lat,
                           center_lon=center_lon,
                           minLat=minLat, minLng=minLng,
                           maxLat=maxLat, maxLng=maxLng,
                           center_zoom=center_zoom)

@app.route('/remove',methods=['POST'])
def remove():
    """ remove a loction ajax """
    if not g.user:
        return redirect('/login')
    if request.method=='POST':
        _id = request.form['id']
        print 'removing', _id
        del couch['coordinates'][_id]
        return redirect('/')

@app.route('/set', methods=['GET', 'POST'])
def set_location():
    """ sets a location ajax """
    if not g.user:
        return redirect('/login')
    if request.method == 'POST':
        db = couch['coordinates']
        date_str = str(datetime.datetime.now())
        coords=request.form['coords'].replace('(','').replace(')','')
        data = dict(coords=coords,
                    tag=date_str)
        db[date_str] = data
        return redirect('/')

@app.route('/set_label',methods=['POST'])
def set_label():
    """ ajax -- sets a label for a location """
    if not g.user:
        return redirect('/login')
    if request.method == 'POST':
        db = couch['coordinates']
        _id = request.form['id']
        label = request.form['label']
        before = db[request.form['id']]
        before = dict(before.items())
        before.pop('_rev')
        before['label']=label
        # stupid.. have to delete and restore instead of update?
        del db[_id]
        db[_id] = before
        report('updated label for ',[_id,label])
        return redirect('/')


def setup():
    """ couch-specific stuff """
    import couchdb
    global couch
    couch = couchdb.Server(SERVER)
    couch.resource.credentials = CREDENTIALS

def coordinates(db):
    return filter(lambda x: not x.startswith('_design'), db)

def report(msg, vars):
    print msg,vars

setup()

before_request = app.before_request(before_request)
after_request  = app.after_request(after_request)
login          = app.route('/login', methods=['GET', 'POST'])(login)
logout         = app.route('/logout')(logout)

if __name__=='__main__':
    # hook for to clean up the database by hand
    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
