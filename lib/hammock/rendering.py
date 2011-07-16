""" hammock.rendering
"""

from hammock.data import CONTROL_T

def render_control(_id, lat, lon, tag):
    """ escaping stuff is obnoxious:
        the \x27 is javascript for single-quote
    """
    control = ''
    js = "do_label(\\x27"+_id+"\\x27,{lat},{lon});".format(lat=lat,lon=lon)
    control += CONTROL_T.format(link='''<a href="javascript:{js}">{label}</a>'''.format(js=js, label='adjust label for this point'))
    js = "do_tag(\\x27"+_id+"\\x27,\\x27"+tag+"\\x27);".format(tag=tag)
    control += CONTROL_T.format(link='''<a href="javascript:{js}">{label}</a>'''.format(js=js, label='adjust tag for this point'))
    js = "do_remove(\\x27"+_id+"\\x27);"
    control += CONTROL_T.format(link='''<a href="javascript:{js}">{label}</a>'''.format(js=js,label='remove this point'))
    return control

def getmarker(color):
    return "/static/markers/{color}_Marker.png".format(color=color)

def tag2iconf(tag):
    """ convert tag to icon file """
    if tag=='default':                 iconf = getmarker('yellow')
    elif tag in ['hiking','outdoors']: iconf = getmarker('green')
    else:                              iconf = getmarker('blue');
    return iconf
