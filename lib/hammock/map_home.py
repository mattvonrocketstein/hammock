""" hammock.map_home
"""
import logging
log = logging.getLogger(__file__)

from flask import request, render_template, g

from hammock.data import settings
from hammock._math import box, calculate_center
from hammock.auth import authenticated
from hammock.rendering import render_control, tag2iconf
from hammock._couch import coordinates, handle_dirty_entry
from hammock._couch import all_unique_tags, filter_where_tag_is, get_db

import logging
log = logging.getLogger(__file__)

DEFAULT_ZOOM = settings['hammock.default_zoom']
MAPS_API_KEY = settings['google.maps_key']


def slash():
    """ the homepage:
        renders all geocoordinates in coordinate database,
        along with labels.
    """

    db         = get_db()
    points     = []
    authorized = authenticated(g)
    use_tag     = request.values.get('tag') or None
    if use_tag:
        ROOT = filter_where_tag_is(use_tag)
    else:
        ROOT = coordinates(db)

    for _id in ROOT:
        obj = db[_id]
        if 'coords' not in obj:
            handle_dirty_entry(_id)
            continue
        lat, lon = obj['coords'].split(',')
        label    = '<b>' + obj.get('label', 'label is empty') + '</b>'

        #only the first tag is used currently
        tag     = obj.get('tag', 'default')
        iconf   = tag2iconf(tag)
        if authorized:
            # TODO: move render_control and <b> stuff into templates..
            label   += render_control(_id, lat, lon, tag)
        points.append([lat,lon, label, iconf])

    center      = request.values.get('center')
    center_zoom = request.values.get('zoom') or DEFAULT_ZOOM

    if center:
        center_lat, center_lon = center.split(',')
        minLat, minLng, maxLat, maxLng = None, None, None, None
    else:
        center_lat, center_lon = calculate_center(points)
        minLat, minLng, maxLat, maxLng = box(points)

    goto = request.args.get('goto') or None
    if goto:
        center_zoom = 3
    try:
        return render_template('index.html',
                           authenticated=authenticated(g),
                           points=points,
                           center_lat=center_lat,
                           center_lon=center_lon,
                           minLat=minLat, minLng=minLng,
                           maxLat=maxLat, maxLng=maxLng,
                           center_zoom=center_zoom,
                           utags=all_unique_tags(),
                           goto = goto,
                           API_KEY=MAPS_API_KEY)
    except:
        print 'error rendering template'
