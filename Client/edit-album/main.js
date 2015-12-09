$(document).ready(function(){
        // Here's my data model

         var userdata = { 'logged_in': false };

        if(JSON.parse(localStorage.getItem("userdata"))){
            userdata = JSON.parse(localStorage.getItem("userdata"));

            $('#username').text(userdata['username']);
            $('#user-img').attr("src", "http://localhost:5000/static/uploads/" + userdata['image_url']);
            
            
        }

// Here's my data model
var ViewModel = function() {
    if(userdata.logged_in == false){
        window.location.href = "/login";
    }else{
    
    var queryParameters = getUrlVars();
    var artist = queryParameters.artist;
    var album = queryParameters.album;
    var song = queryParameters.song;
    var url = "http://localhost:5000/album/" + album;
    
    var self = this;
    
    self.loggedIn = ko.observable(userdata['logged_in']);
    self.artwork = ko.observable();
    self.title = ko.observable();
    self.genre = ko.observable();
    self.year = ko.observable();
    self.name = ko.observable();
    self.album_id = ko.observable();
    self.artist_id = ko.observable();
    
    $.ajax({
        type: "GET",
        url: url,
        dataType: 'json',
        success: function(result){
            console.log(result.album.title);
            self.artwork(result.album.artwork);
            self.title(result.album.title);
            self.genre(result.album.genre);
            self.year(result.album.year_released);
            self.album_id(result.album.album_id);
            self.artist_id(result.album.artist_id);
            self.name(result.album.name);
        },
        
        error: function(result){
            console.log(result);
            alert("Error");
        }
    });
    
    $("#save-album").on("submit", function(e){
        
        var queryData = $.extend({}, userdata, self);
        
        var jsonData = queryData;
         var data = $("#save-album").serializeArray();
        for(i = 0; i<data.length; i++){
               jsonData[data[i].name] = data[i].value;
         };
        //queryData = JSON.stringify(queryData);
        console.log(ko.toJSON(jsonData));
        
        console.log(queryData);
        var resource = "http://localhost:5000/" + self.artist_id() + "/" + self.album_id() + "/";
        $.ajax({
            type: "POST",
            url: resource,
            dataType: 'json',
            contentType: 'application/json; charset=utf-8',
            data: ko.toJSON(jsonData),


            success: function(result){
				console.log("hello");
                if (result.error){
                    alert("Error: " + result.message);
                }

                else{
                    alert("Success: " + result.message);
                     window.location.href = "/artist/?artist=" + self.artist_id() + "#album" + self.album_id();
                    console.log(result)
                }
                
            },
            
            error: function(result){
                console.log(result);
                alert("Error!");
            }
        });
    });
    }
};

ko.applyBindings(new ViewModel()); // This makes Knockout get to work

});

// Converts newline chars to <br /> tags
function nl2br (str, is_xhtml) {   
    var breakTag = (is_xhtml || typeof is_xhtml === 'undefined') ? '<br />' : '<br>';    
    return (str + '').replace(/([^>\r\n]?)(\r\n|\n\r|\r|\n)/g, '$1'+ breakTag +'$2');
}

function getUrlVars()
{
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++)
    {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    return vars;
}