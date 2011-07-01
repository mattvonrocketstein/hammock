# -*- coding: utf-8 -*-
"""
"""

import datetime
from flask import render_template, abort, g, flash
from flask import Flask, request, session, url_for, redirect

from werkzeug import check_password_hash, generate_password_hash

from hammock._math import box, calculate_center
from hammock.data import *
from hammock.util import *
from hammock.auth import *
from hammock.plumbing import *
from hammock._couch import update_db, setup, coordinates, handle_dirty_entry

## Begin flask setup
app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = SECRET_KEY

def render_control(_id, lat, lon):
    """ escaping stuff is obnoxious:
        the \x27 is javascript for single-quote
    """
    control = ''
    js = "do_label(\\x27"+_id+"\\x27,{lat},{lon});".format(lat=lat,lon=lon)
    control += CONTROL_T.format(link='''<a href="javascript:{js}">adjust label for this point</a>'''.format(js=js))
    js = "do_tag(\\x27"+_id+"\\x27);"
    control += CONTROL_T.format(link='''<a href="javascript:{js}">adjust tag for this point</a>'''.format(js=js))
    js = "do_remove(\\x27"+_id+"\\x27);"
    control += CONTROL_T.format(link='''<a href="javascript:{js}">remove this point</a>'''.format(js=js))
    return control

def tag2iconf(tag):
    if tag=='default':
        iconf = "/static/markers/yellow_MarkerC.png";
    else:
        iconf = "/static/markers/blue_MarkerC.png";
    return iconf

@app.route('/')
def slash():
    """ the homepage:
        renders all geocoordinates in coordinate database,
        along with labels.
    """
    db     = couch['coordinates']
    points = []
    authorized = authenticated(g)
    for _id in coordinates(db):

        obj = db[_id]
        if 'coords' not in obj:
            handle_dirty_entry(_id)
            continue
        lat, lon = obj['coords'].split(',')
        label    = '<b>' + obj.get('label', 'label is empty') + '</b>'

        #only the first tag is used currently
        tag     = obj.get('tag', 'default')

        """
        >>> map_fun = '''function(doc) {
        ...     emit([doc.type, doc.name], doc.name);
        ... }'''
        >>> results = db.query(map_fun)
        """
        # query by..
        #z=[x for x in \
        #   db.query("""function(doc){if(doc.tag=="default"){emit(null,doc);}}""")
        #   ]
        iconf   = tag2iconf(tag)
        if authorized:
            label   += render_control(_id,lat,lon)
        points.append([lat,lon, label, iconf])
    center_lat,center_lon = calculate_center(points)
    minLat, minLng, maxLat, maxLng = box(points)
    return render_template('index.html',
                           authenticated=authenticated(g),
                           points=points,
                           center_lat=center_lat,
                           center_lon=center_lon,
                           minLat=minLat, minLng=minLng,
                           maxLat=maxLat, maxLng=maxLng,
                           center_zoom=center_zoom,
                           API_KEY=MAPS_API_KEY)

@requires_authentication
@app.route('/remove',methods=['POST'])
def remove():
    """ remove a loction ajax """
    if request.method=='POST':
        _id = request.form['id']
        print 'removing', _id
        del couch['coordinates'][_id]
        return redirect('/')

@requires_authentication
@app.route('/set', methods=['GET', 'POST'])
def set_location():
    """ sets a location ajax """
    if request.method == 'POST':
        db = couch['coordinates']
        date_str = str(datetime.datetime.now())
        coords=request.form['coords'].replace('(','').replace(')','')
        data = dict(coords=coords, timestamp=date_str, tag='default')
        db[date_str] = data
        return redirect('/')

def set_factory(attr):
    """ """
    def setter():
        """ ajax -- sets an setter.attribute for a location
            flask does something weird so that this closure doesn't
            work the way it ought to.  hence we have to calculate 'attr'
            based on request path :(
        """
        this_attr = request.url.split('/')[-1].split('_')[-1]
        if request.method == 'POST':
            db    = couch['coordinates']
            _id   = request.form['id']
            report("in inner set with", [_id, this_attr, request.form.keys()])
            label = request.form[this_attr]
            report("in inner set with", [label])
            update_db(db, _id, {this_attr:label})
            return redirect('/')
    url    = '/set_' + attr
    setter = requires_authentication(setter)
    setter = app.route(url, methods=['POST'])(setter)
    setter.attr = attr
    print " * built setter", [attr,url]
    return requires_authentication(setter)

set_label = set_factory('label')
set_tag   = set_factory('tag')
couch     = setup()

before_request = app.before_request(before_request)
after_request  = app.after_request(after_request)
login          = app.route('/login', methods=['GET', 'POST'])(login)
logout         = app.route('/logout')(logout)

x = """
function(doc) {
        if(doc.label=="default"){emit(null,doc);}
        }
"""
if __name__=='__main__':
    # hook for to clean up the database by hand
    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
