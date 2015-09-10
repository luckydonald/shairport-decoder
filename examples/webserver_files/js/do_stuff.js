var server = "";//"/shairport-decode/examples/webserver_files/test_json"; //last one is the PyCharm debug server url. Else (default) set it to ""
var cover_url = server+"/cover.json";
var meta_url = server+"/meta.json";
var lol = {cover:false, meta:false}; //debug prints only once on side load.

var refresh_timeout = null;
window.onload = function() {
    refresh_timeout = window.setTimeout("refreshInfos()", 1000);
};

function refreshInfos(){
    loadJSON(meta_url, set_meta);
    loadJSON(cover_url, set_cover);

    refresh_timeout = window.setTimeout("refreshInfos()", 1000);
}

function set_cover(jsonObj) {
        if (!lol.cover) {
        console.log(jsonObj);
        lol.cover = true;
    }

}

function set_meta(jsonObj) {
    $("name").innerHTML = jsonObj.itemname;
    $("album").innerHTML = jsonObj.songartist;
    $("artist").innerHTML = jsonObj.songalbum;
    if (!lol.meta) {
        console.log(jsonObj);
        lol.meta = true;
    }
}