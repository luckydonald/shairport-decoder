var infobuffer = {coverEnabled:false, coverHash:"NOPE.AVI"};
var colorThief = new ColorThief();




/*
  START IMAGE RESIZE
 */
if(typeof window.orientation === 'undefined') {
    /* use media query technique, fix for mobile firefox */
    var test = window.matchMedia("(orientation: portrait)");
    test.addListener(function(m) {
        if(m.matches) {
            // Changed to portrait
            calculateImgSize();
        }else {
            // Changed to landscape
            calculateImgSize();
        }
    });
} else {
    /*use orientationchange event handler*/
    window.addEventListener('orientationchange', calculateImgSize);
}
window.onresize=function() {
    calculateImgSize();
};
/* END IMAGE RESIZE */