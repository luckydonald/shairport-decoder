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
    return document.getElementById(id);
}
