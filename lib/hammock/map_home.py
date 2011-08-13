""" hammock.map_home
"""
import logging
log = logging.getLogger(__file__)

from flask import request, render_template

from hammock._math import box, calculate_center
from hammock.rendering import render_control, tag2iconf
from hammock._couch import coordinates, handle_dirty_entry
from hammock._couch import all_unique_tags, filter_where_tag_is, get_db
from hammock._flask import HammockView


class Slash(HammockView):
    """ """

    url = '/'

    @property
    def center_zoom(self):
        """ """
        if self['goto']:
            return 3
        return self['zoom'] or self.settings['hammock.default_zoom']

    @property
    def points(self):
        """ """
        db         = get_db()
        points     = []

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
            if self.authorized:
                # TODO: move render_control and <b> stuff into templates..
                label   += render_control(_id, lat, lon, tag)
            points.append([lat, lon, label, iconf])
        return points

    def main(self):
        """ the homepage:

            renders all geocoordinates in coordinate database,
            along with labels.
        """
        points = self.points
        if self['center']:
            # is this case still used?
            center_lat, center_lon = self['center'].split(',')
            minLat, minLng, maxLat, maxLng = None, None, None, None
        else:
            center_lat, center_lon = calculate_center(points)
            minLat, minLng, maxLat, maxLng = box(points)

        return render_template('index.html',
                               authenticated = self.authorized,
                               points        = points,
                               center_lat    = center_lat,
                               center_lon    = center_lon,
                               minLat        = minLat, minLng=minLng,
                               maxLat        = maxLat, maxLng=maxLng,
                               center_zoom   = self.center_zoom,
                               utags         = all_unique_tags(),
                               goto          = self['goto'],
                               API_KEY       = self.settings['google.maps_key'])
