# Assuming you have a fresh couchdb, this will add
# the hammock user and initialize hammock's database
USER="hammock_coordinates"
PASSWD="whereintheworldiscarmensandiego"
HOST="http://127.0.0.1:5984"
curl -X PUT $HOST/database
curl -X PUT $HOST/_config/admins/$USER -d '"$PASSWD"'
HOST="http://$USER:$PASSWD@127.0.0.1:5984"
curl -X PUT $HOST/hammock_coordinates
