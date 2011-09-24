var tag='{{tag}}';

function inArray(needle, haystack) {
    for(var i = 0; i < haystack.length; i++) {
        if(haystack[i] == needle) return true;
    }
    return false;
}

function(doc) {
    if(doc.tag && inArray(tag, doc.tag.split(" "))) {
        emit(doc.tag,doc);
    }
    else{
        if(doc.tags.length && inArray(tag,doc.tags)) {
            emit(doc.tags, doc);
        }}

}