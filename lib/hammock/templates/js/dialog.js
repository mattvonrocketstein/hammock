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
    return keypress_event;
}

function open_bind_focus(name, _id){
    $('#'+name+'_dialog').dialog('open');
    $('#'+name+'_input ').bind('keypress', keypress_event_factory(name, _id));
    $('#'+name+'_input ').focus();
}

$(document).ready(function() {
        $(".dialog").dialog({ autoOpen: false});
    });
