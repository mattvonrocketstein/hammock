    if (GBrowserIsCompatible()) {

      function createMarker(point,html) {
        var marker = new GMarker(point);
        GEvent.addListener(marker, "click", function() {
          marker.openInfoWindowHtml(html);
        });

        // The new marker "mouseover" listener
        GEvent.addListener(marker,"mouseover", function() {
          marker.openInfoWindowHtml(html);
        });

        return marker;
      }

      var map = new GMap2(document.getElementById("map"));
      map.addControl(new GLargeMapControl());
      map.addControl(new GMapTypeControl());
      map.setCenter(new GLatLng(43.907787,-79.359741), 9);
      {% for lat,lon,label in points %}
      var marker = createMarker(new GLatLng({{lat}},{{lon}}),'{{label}}')
      map.addOverlay(marker);
      {%endfor%}
    }


    else {
      alert("Sorry, the Google Maps API is not compatible with this browser");
    }

    // This Javascript is based on code provided by the
    // Community Church Javascript Team
    // http://www.bisphamchurch.org.uk/
    // http://econym.org.uk/gmap/
