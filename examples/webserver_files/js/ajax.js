/* FUNCTIONS BLOCK START */

function loadJSON(url, callback){
    var http_request = new XMLHttpRequest();
    try{
       // Opera 8.0+, Firefox, Chrome, Safari
       http_request = new XMLHttpRequest();
    }catch (e){
       // Internet Explorer Browsers
       try{
          http_request = new ActiveXObject("Msxml2.XMLHTTP");

       }catch (e) {

          try{
             http_request = new ActiveXObject("Microsoft.XMLHTTP");
          }catch (e){
             // Something went wrong
             alert("Ajax failed to init.\nI just don't know what went wrong...");
             return false;
          }

       }
    }

    http_request.onreadystatechange = function(){
       if (http_request.readyState == 4){
          // Javascript function JSON.parse to parse JSON data
          var jsonObj = JSON.parse(http_request.responseText);

          // jsonObj variable now contains the data structure and can
          // be accessed as jsonObj.name and jsonObj.country.
          callback(jsonObj)
       }
    };

    http_request.open("GET", url, true);
    http_request.send();
 }