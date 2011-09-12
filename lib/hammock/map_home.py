""" hammock.map_home
"""
from collections import defaultdict

from jinja2 import Template

from report import report as report
from corkscrew import SmartView

from hammock.views.db import DBView
from hammock._math import box, calculate_center
from hammock._couch import handle_dirty_entry

is_legal_coordinate_entry = lambda obj: 'coords' in obj
obj2coords                = lambda obj: obj['coords'].split(',')
obj2label                 = lambda obj: obj.get('label', 'label is empty')
obj2primary_tag           = lambda obj: obj.get('tag', 'default') #only the first tag is used currently

tag2iconf = defaultdict(lambda *args:'blue',
                        {'default':'yellow',
                         'hiking':'green',
                         'outdoors':'green'})


class Slash(DBView):
    url      = '/'
    template = 'index.html'
    database_name = 'coordinates'

    def _all_unique_tags(self):
        """ TODO: this can go away after coordinates is using 'tags' instead of 'tag'
        """
        return self._db._all_unique_attr('tag')

    @property
    def smart_views(self):
        """ enumerate views that understand/generate their own javascript counterparts """
        from hammock import views
        out = [ x for x in views.__views__ if issubclass(x, SmartView) and x.__doc__ ]
        return out

    @property
    def control_js(self):
        """ collects docstrings from the smart views to render control javascript """
        out = []
        for view in self.smart_views:
            view_js = Template(view.__doc__)
            view_js = view_js.render(view_url=view.url)
            out.append(view_js)
        return '\n\n'.join(out)

    @property
    def center_zoom(self):
        """ decide on map zoom, depending on GET args and defaulting to settings"""
        if self['goto']:
            return self.settings['hammock.detail_zoom']
        return self['zoom'] or self.settings['hammock.default_zoom']

    @property
    def points(self):
        """ TODO: move render_control and <b> stuff into templates """
        points     = []
        for _id, obj in self.rows:
            if not is_legal_coordinate_entry(obj):
                handle_dirty_entry(_id)
            else:
                lat, lon = obj2coords(obj)
                label    = obj2label(obj)
                tag      = obj2primary_tag(obj)
                iconf    = tag2iconf[tag]
                control  = ''
                points.append([ _id, lat, lon,
                                label, tag, control,
                                iconf ])
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
            utags         = self._all_unique_tags(),
            control_js    = self.control_js,
            draw_trajectory = True if self['tag']=='recent' else False,
            goto          = self['goto'],
            API_KEY       = self.settings['google.maps_key'])
