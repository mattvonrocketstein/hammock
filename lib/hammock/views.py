from flask import Flask, request, jsonify
def remove():
    """ remove a loction ajax """
    if request.method=='POST':
        _id = request.form['id']
        del get_db()[_id]
        return jsonify(result='ok')
def set_location():
    """ sets a location ajax

        TODO: use set_factory to build this one too?
    """
    if request.method == 'POST':
        db = get_db()
        date_str = str(datetime.datetime.now())
        coords=request.form['coords'].replace('(','').replace(')','')
        data = dict(coords=coords, timestamp=date_str, tag='default')
        db[date_str] = data
        return jsonify(result='ok')
