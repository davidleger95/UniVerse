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
    
    var queryParameters = getUrlVars();
    var artist = queryParameters.artist;
    var album = queryParameters.album;
    var song = queryParameters.song;
    var url = "http://localhost:5000/" + artist + "/" + album + "/" + song;
    
    var self = this;
    
    self.loggedIn = ko.observable(userdata['logged_in']);
    //self.data = ko.observableArray();
    self.curr_title = ko.observable();
    self.album_id = ko.observable();
    self.lyrics = ko.observable();
    self.medialink = ko.observable();
    self.year = ko.observable();
    self.curr_track_id = ko.observable();
    self.curr_track_no= ko.observable();
    self.artwork = ko.observable();
    self.album_title = ko.observable();
    self.artist_id = ko.observable();
    self.name = ko.observable();
    self.genre = ko.observable();
    self.tracklist = ko.observableArray();
    
    $.ajax({
        type: "GET",
        url: url,
        dataType: 'json',
        success: function(result){
            console.log(result.track.title);
            self.curr_title(result.track.title);
            self.lyrics(nl2br(result.track.lyrics));
            var media = result.track.media_link;
            if(result.track.media_link){
                media = result.track.media_link.split("=")[1];
            }
            self.medialink(media);
            self.year(result.track.album[0].year_released);
            self.curr_track_id(result.track.track_id);
            self.curr_track_no(result.track.track_no);
            self.album_id(result.track.album_id);
            self.artwork(result.track.album[0].artwork);
            self.album_title(result.track.album[0]['a.title']);
            self.artist_id(result.track.album[0].artist_id);
            self.name(result.track.album[0].name);
            self.genre(result.track.album[0].genre);
            self.tracklist(result.track.album);
        },
        
        error: function(result){
            console.log(result);
            alert("Error");
        }
    });
 
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