def box(points):
    points = [ [p[0], p[1]] for p in points] # drop label
    points = [ map(float, [p[0], p[1]]) for p in points] # make numeric
    lats = [p[0] for p in points]
    lons = [p[1] for p in points]
    return min(lats), min(lons), max(lats), max(lons)

def calculate_center(points):
    points = [ [p[0], p[1]] for p in points] # drop label
    points = [ map(float, [p[0], p[1]]) for p in points] # make numeric
    lats = [p[0] for p in points]
    lons = [p[1] for p in points]
    lat = max(lats) + min(lats)/2.0
    lon = max(lons) + min(lons)/2.0
    return lat,lon
