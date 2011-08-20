if (GBrowserIsCompatible()) {
    function go(a,b,c){
        map.setCenter(new GLatLng(a, b), c);
    }

    function getAddress(latlng, result_holder) {
        geocoder = new GClientGeocoder();
        marker = new GMarker(latlng, {draggable: true});
        if (latlng) {
            geocoder.getLocations(latlng, function(addresses) {
                    if(addresses.Status.code != 200) {
                        alert("reverse geocoder failed to find an address for " + latlng.toUrlValue());
                    }
                    else {
                        address = addresses.Placemark[0];
                        $('#'+result_holder).val(address.address);
                    }
                });
        }
    }

    function showAddress(address) {
        geocoder = new GClientGeocoder();
        if (geocoder) {
            geocoder.getLatLng(address,
                               function(point) {
                                   if (!point) {
                                       alert(address + " not found");
                                   }
                                   else {
                                       map.setCenter(point, 15);
                                       var marker = new GMarker(point, {draggable: true});
                                       //todo: make a helper for setting marker icon
                                       iconf='/static/markers/red_MarkerA.png';
                                       marker.setImage(iconf);
                                       marker.getIcon().image = iconf;
                                       map.addOverlay(marker);
                                       GEvent.addListener(marker, "dragend", function() {
                                               marker.openInfoWindowHtml(marker.getLatLng().toUrlValue(6));
                                           });
                                       GEvent.addListener(marker, "click", function() {
                                               marker.openInfoWindowHtml(marker.getLatLng().toUrlValue(6));
                                           });
                                       GEvent.trigger(marker, "click");
                                   }
                               } );
        }
    }

    function createMarker(point, html, iconf) {
        //alert(main_tag);
        var marker = new GMarker(point);
        GEvent.addListener(marker, "click", function() {
                zoomInHere();
                //marker.openInfoWindowHtml(html);
            });

        // The new marker "mouseover" listener
        GEvent.addListener(marker,"mouseover", function() {
                marker.openInfoWindowHtml(html);
            });

        marker.setImage(iconf);
        marker.getIcon().image = iconf;
        return marker;
    }

    //generic functions
    function efunc(request, status, error) {
        alert("Ajax error: "+request.responseText);
    }

    var map = new GMap2(document.getElementById("map"));
    map.addControl(new GLargeMapControl());
    map.addControl(new GMapTypeControl());
    go({{center_lat}}, {{center_lon}}, {{center_zoom}});

    POINTS = [ {% for lat, lon, label, iconf in points %}
    { lat : {{lat}},
      lon : {{lon}},
      label : '{{label}}',
      iconf : '{{iconf}}'}{%if not loop.last%},{%endif%}
    {% endfor %} ];

    $.each( POINTS,
            function( index_num, b ) {
                //alert( a+'::'+b.label );
                map.addOverlay(createMarker(new GLatLng(b.lat,b.lon),
                                            b.label,
                                            b.iconf));
                } );
    // === Global variable that can be used by the context handling functions ==
    var clickedPixel;

    // === create the context menu div ===
    var contextmenu = document.createElement("div");
    contextmenu.style.visibility="hidden";
    contextmenu.style.background="#ffffff";
    contextmenu.style.border="1px solid #8888FF";

    contextmenu.innerHTML = '<a href="javascript:zoomIn()"><div class="context">&nbsp;&nbsp;Zoom in&nbsp;&nbsp;<\/div><\/a>'
        + '<a href="javascript:zoomOut()"><div class="context">&nbsp;&nbsp;Zoom out&nbsp;&nbsp;<\/div><\/a>'
        + '<a href="javascript:zoomInHere()"><div class="context">&nbsp;&nbsp;Zoom in here&nbsp;&nbsp;<\/div><\/a>'
        + '<a href="javascript:zoomOutHere()"><div class="context">&nbsp;&nbsp;Zoom out here&nbsp;&nbsp;<\/div><\/a>'
        + '<a href="javascript:centreMapHere()"><div class="context">&nbsp;&nbsp;Centre map here&nbsp;&nbsp;<\/div><\/a>';
    map.getContainer().appendChild(contextmenu);

    // === listen for singlerightclick ===
    GEvent.addListener(map,"singlerightclick",function(pixel,tile) {
            // store the "pixel" info in case we need it later
            // adjust the context menu location if near an egde
            // create a GControlPosition
            // apply it to the context menu, and make the context menu visible
            clickedPixel = pixel;
            var x=pixel.x;
            var y=pixel.y;
            if (x > map.getSize().width - 120) { x = map.getSize().width - 120 }
            if (y > map.getSize().height - 100) { y = map.getSize().height - 100 }
            var pos = new GControlPosition(G_ANCHOR_TOP_LEFT, new GSize(x,y));
            pos.apply(contextmenu);
            contextmenu.style.visibility = "visible";
            $('#cmlab').text(map.fromContainerPixelToLatLng(clickedPixel)+'');
        });
    function hide_context_menu(){contextmenu.style.visibility="hidden";}

    function zoomIn() {
        map.zoomIn();
        hide_context_menu();
    }
    function zoomOut() {
        map.zoomOut();
        hide_context_menu();
    }
    function zoomInHere() {
        var point = map.fromContainerPixelToLatLng(clickedPixel);
        map.zoomIn(point,true);
        hide_context_menu();
    }
    function zoomOutHere() {
        var point = map.fromContainerPixelToLatLng(clickedPixel)
            // There is no map.zoomOut() equivalent
            map.setCenter(point, map.getZoom()-1);
        // hide the context menu now that it has been used
        hide_context_menu();
    }
    function centreMapHere() {
        var point = map.fromContainerPixelToLatLng(clickedPixel);
        map.setCenter(point);
        hide_context_menu();
    }

    {% if minLat %}
    var minLat={{minLat}};
    var minLng={{minLng}};
    var maxLat={{maxLat}};
    var maxLng={{maxLng}};

    botLeft = new GLatLng({{minLat}}, {{minLng}});
    topRight = new GLatLng({{maxLat}}, {{maxLng}});

    bounds = new GLatLngBounds(botLeft, topRight);
    //map.setCenter(new GLatLng((({{maxLat}} + {{minLat}}) / 2.0),(({{maxLng}} + {{minLng}}) / 2.0)),map.getBoundsZoomLevel(bounds));
    map.setCenter(new GLatLng(-2,85.7),1)
        {%endif%}

    // === If the user clicks on the map, close the context menu ===
    GEvent.addListener(map, "click", function() { hide_context_menu(); });

}


else {
    alert("Sorry, the Google Maps API is not compatible with this browser");
}



{%if authenticated%}
function sfunc_factory(name){
    function sfunc(data, text) {
        $(name).dialog('close');
        alert('finished ok');
        //document.location='/';
    }
    return sfunc;
}
function keypress_event_factory(name, _id){
    function keypress_event(e){

        if(e.which == 13){
            var data = {id:_id};
            data[name] = $('#'+name+'_input').val();
            $.ajax({
                    type: "get",
                    data:data,
                    url: "/set_"+name,
                    success: sfunc_factory('#'+name+'_dialog'),
                    error: efunc
                    });
        }
    }
    return keypress_event
        }
function open_bind_focus(name,_id){
    $('#'+name+'_dialog').dialog('open');
    $('#'+name+'_input ').bind('keypress', keypress_event_factory(name, _id));
    $('#'+name+'_input ').focus();
}

{{control_js}}

function do_label(_id, lat, lon){
    $('#label_current_id').html(_id);
    $('#label_id').html(_id);
    $('#label_coords').html(lat+', '+lon);
    open_bind_focus('label', _id);
}

function do_tag(_id, tag){
    $('#tag_current_id').html(_id);
    $('#tag_current').html(tag);
    open_bind_focus('tag', _id);
}

function setLocation() {
    var point = map.fromContainerPixelToLatLng(clickedPixel);
    $.ajax({
            type: "post",
                data:{coords:''+point},
                url: "/set",
                success: function sfunc(data, text) {alert('added ok');},
                error: efunc
                });
    //{coords:''+point} );
    hide_context_menu();
    //window.location='/';
}
contextmenu.innerHTML = '<a href="javascript:setLocation()"><div class="context">&nbsp;&nbsp;Set as new location&nbsp;&nbsp;<\/div><\/a>'+contextmenu.innerHTML;

$(document).ready(function() {
        $(".dialog").dialog({ autoOpen: false });
    });

{%endif%}





$(document).ready(function() {
        contextmenu.innerHTML = '<span id=cmlab><small>testing</small><\/span><br\/><br\/>'+contextmenu.innerHTML;
        $('#address_search').bind('focus', function(e){$('#address_search').val('');})
            $('#address_search').bind('keypress',
                                      function(e){
                                          if(e.which == 13){showAddress($('#address_search').val());}
                                      });
        {%if goto%} {# support for ie ?goto=kansas #}
        showAddress('{{goto}}');
        {%endif%}
    });