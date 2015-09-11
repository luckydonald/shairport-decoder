function zoomImage() {
    $("imageoverlay").style.visibility = "visible";
    $("imageoverlay").style.display = "inline";
    infobuffer.coverEnabled = true;
    calculateImgSize();
}
function dezoomImage() {
    $("imageoverlay").style.visibility = "hidden";
    $("imageoverlay").style.display = "none";
    infobuffer.coverEnabled = false;
}

function screenSize(){
    var w = window,
        d = document,
        e = d.documentElement,
        g = d.getElementsByTagName('body')[0],
        x = w.innerWidth || e.clientWidth || g.clientWidth,
        y = w.innerHeight|| e.clientHeight|| g.clientHeight;
    return {width:x,height:y};
}
//using a fancy var block rulez!
function calculateImgSize(){
    var screen = screenSize();
    var overlayimage = $("overlayimage");
    overlayimage.style.maxWidth = (screen.width) + "px";
    overlayimage.style.maxHeight = (screen.height) + "px";
}