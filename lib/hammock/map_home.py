""" hammock.map_home
"""
import logging
log = logging.getLogger(__file__)
from collections import defaultdict
from jinja2 import Template
from flask import request, render_template

from corkscrew import View

from hammock._math import box, calculate_center
from hammock._couch import coordinates, handle_dirty_entry
from hammock._couch import all_unique_tags, filter_where_tag_is, get_db

is_legal_coordinate_entry = lambda obj: 'coords' in obj
obj2coords                = lambda obj: obj['coords'].split(',')
obj2label                 = lambda obj: obj.get('label', 'label is empty')
obj2primary_tag           = lambda obj: obj.get('tag', 'default') #only the first tag is used currently

tag2iconf = defaultdict(lambda *args:'blue',
                        {'default':'yellow',
                         'hiking':'green',
                         'outdoors':'green'})

class Slash(View):
    url      = '/'
    template = 'index.html'

    @property
    def smart_views(self):
        """ views that understand/generate their own javascript counterparts """
        from hammock import views
        get = lambda name: getattr(views, name)
        return [ get(name) for name in dir(views)
                if get(name)!=views.SmartView and
                 isinstance(get(name), views.SmartView)]

    @property
    def control_js(self):
        out = []
        for view in self.smart_views:
            view_js = Template(view.__doc__)
            view_js = view_js.render(view_url=view.url)
            out.append(view_js)
        return '\n\n'.join(out)

    @property
    def center_zoom(self):
        """ """
        if self['goto']:
            return self.settings['hammock.detail_zoom']
        return self['zoom'] or self.settings['hammock.default_zoom']

    @property
    def points(self):
        """ TODO: move render_control and <b> stuff into templates """
        db         = get_db()
        points     = []

        if self['tag']: ROOT = filter_where_tag_is(self['tag'])
        else:           ROOT = coordinates(db)

        for _id in ROOT:
            obj = db[_id]
            if not is_legal_coordinate_entry(obj):
                handle_dirty_entry(_id)
            else:
                lat, lon = obj2coords(obj)
                label    = obj2label(obj)
                tag      = obj2primary_tag(obj)
                iconf    = tag2iconf[tag]
                control = ''
                points.append([_id, lat, lon, label, tag, control, iconf])
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
        return self.render_template(
                               authenticated = self.authorized,
                               points        = points,
                               center_lat    = center_lat,
                               center_lon    = center_lon,
                               minLat        = minLat, minLng=minLng,
                               maxLat        = maxLat, maxLng=maxLng,
                               center_zoom   = self.center_zoom,
                               utags         = all_unique_tags(),
                               control_js    = self.control_js,
                               goto          = self['goto'],
                               API_KEY       = self.settings['google.maps_key'])
