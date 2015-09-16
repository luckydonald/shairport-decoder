var server = "";//"/shairport-decode/examples/webserver_files/test_json"; //last one is the PyCharm debug server url. Else (default) set it to ""
var cover_json_url = server+"/cover.img.json";
var color_json_url = server+"/cover.color.json";
var meta_json_url = server+"/meta.json";
var cover_url = server+"/cover"; //+".png"
var lol = {cover:false, meta:false, color:false}; //debug: prints only once after site loaded.

var refresh_timeout = null;
window.onload = function() {
    refresh_timeout = window.setTimeout("refreshInfos()", 1000);
};

function refreshInfos(){
    loadJSON( meta_json_url, set_meta);
    loadJSON(cover_json_url, set_cover);
    refresh_timeout = window.setTimeout("refreshInfos()", 1000);
}

colorThief = new ColorThief();
function set_cover(jsonObj) {
    if(jsonObj.checksum == null) {
        return
    }
    if (!lol.cover) {
        console.log(jsonObj);
        lol.cover = true;
    }
    if(jsonObj.checksum != infobuffer.coverHash) {
        //var temp_cover_url = cover_url + jsonObj.extension + "#" + new Date().getTime();
        var temp_cover_url = "data:image/png;base64," + jsonObj.base64;


        $("#coverimage").src = temp_cover_url;
        $("#overlayimage").src = temp_cover_url;
        infobuffer.coverHash = jsonObj.checksum;
        loadJSON(color_json_url, set_color);
    }

}

function set_color(jsonObj) {
    if (!lol.color) {
        console.log(jsonObj);
        lol.color = true;
    }
    /*var palette = colorThief.getPalette($("coverimage"), colorCount=2, quality=100),
        background = palette[0],
        forderground = palette[1];
    */
    var foorp = getMinAndMaxContrastYIQ(jsonObj.colors);
    var background = [jsonObj.colors[0].r,jsonObj.colors[0].g,jsonObj.colors[0].b];
    var forderground = [jsonObj.colors[1].r,jsonObj.colors[1].g,jsonObj.colors[1].b];
    document.body.style.backgroundColor = "rgb(" + background[0]   + ","+background[1]   + "," + background[2]   + ")";
    document.body.style.color =           "rgb(" + forderground[0] + ","+forderground[1] + "," + forderground[2] + ")";

    var fields = $(".field");
    for (var i = 0; i < fields.length; i++) {
        var field = fields[i];
        field.style.borderColor =           "rgb(" + forderground[0] + ","+forderground[1] + "," + forderground[2] + ")";
    }
    //.style.color =           "rgb(" + forderground[0] + ","+forderground[1] + "," + forderground[2] + ")"
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