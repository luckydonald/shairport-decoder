function endsWith(str, suffix) {
    return str.indexOf(suffix, str.length - suffix.length) !== -1;
}
function startsWith(str, prefix) {
    return str.indexOf(prefix) === 0;
}

function $(id){
    if(startsWith(id, "#")){
        id = id.substr(1);
    }
    if(startsWith(id, ".")){
        id = id.substr(1);
        return document.getElementsByClassName(id)
    }
    return document.getElementById(id);
}

//http://javascript.about.com/library/bldom08.htm
document.getElementsByClassName = function(cl) {
	var retnode = [];
	var myclass = new RegExp('\\b'+cl+'\\b');
	var elem = this.getElementsByTagName('*');
	for (var i = 0; i < elem.length; i++) {
		var classes = elem[i].className;
		if (myclass.test(classes)) retnode.push(elem[i]);
	}
	return retnode;
};
document.getElementsByTitle = function(cl) {
	var retnode = [];
	var myclass = new RegExp('\\b'+cl+'\\b');
	var elem = this.getElementsByTagName('*');
	for (var i = 0; i < elem.length; i++) {
		var classes = elem[i].title;
		if (myclass.test(classes)) retnode.push(elem[i]);
	}
	return retnode;
};

document.getElementsByTag = function(tagname,tagvalue) {
	var retnode = [];
	var myclass = new RegExp('\\b'+ tagvalue +'\\b');
	var elem = this.getElementsByTagName('*');
	for (var i = 0; i < elem.length; i++) {
		var classes = elem[i].getAttribute(tagname);
		if (myclass.test(classes))
			retnode.push(elem[i]);
	}
	return retnode;
};




// COLOR STUFF

// http://24ways.org/2010/calculating-color-contrast/
function getContrastYIQ(hexcolor) {
    if (hexcolor == null) {
        console.trace();
    }
    hexcolor = prepareColor(hexcolor);
    if (hexcolor == null) {
        console.trace();
    }
    var r = parseInt(hexcolor.substr(0, 2), 16);
    var g = parseInt(hexcolor.substr(2, 2), 16);
    var b = parseInt(hexcolor.substr(4, 2), 16);
    return getContrastYIQ_rgb(r, g, b);
}
function getContrastYIQ_rgb(r,g,b){
	return ((r*299)+(g*587)+(b*114))/1000;
}
function getContrastYIQ_bool(hexcolor) {
    return (getContrastYIQ(r, g, b) >= 128);
}
function getContrastYIQ_rgb_bool(r,g,b) {
    return (getContrastYIQ_rgb(r, g, b) >= 128);
}
function getContrastYIQ_BW(color){
	return (getContrastYIQ_bool(color) ? "#000000" : "#FFFFFF");
}
function getContrastYIQ_BW_rgb(r,g,b){
	return (getContrastYIQ_rgb_bool(r,g,b) ? "#000000" : "#FFFFFF");
}

function getMinAndMaxContrastYIQ(listOfColorTriples) {
    var color = listOfColorTriples[0];
    var min = getContrastYIQ_rgb(color.r, color.g, color.b), min_color = color,
        max = min,   max_color = min_color;
    for (var i = 1; i < listOfColorTriples.length; i++) {
        color       = listOfColorTriples[i];
        var contrastYIQ = getContrastYIQ_rgb(color.r, color.g, color.b);
        console.log(color, contrastYIQ, min, max);
        if (contrastYIQ > max) {
            max_color = color;
            max = contrastYIQ;
        }
        if (contrastYIQ < min) {
            min_color = color;
            min = contrastYIQ;
        }
    }
    return {min:min_color, max:max_color}
}