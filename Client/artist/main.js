$(document).ready(function(){

        // Check if user is logged in
        var userdata = { 'logged_in': false };
        if(JSON.parse(localStorage.getItem("userdata"))){
            userdata = JSON.parse(localStorage.getItem("userdata"));

            $('#username').text(userdata['username']);
            $('#user-img').attr("src", "http://localhost:5000/static/uploads/" + userdata['image_url']);
        }


    var ViewModel = function() {
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
        
        var queryParameters = getUrlVars();
        var artist = queryParameters.artist;
        var url = "http://localhost:5000/" + artist;
        //alert(queryParameters);

        var self = this;
        
        self.loggedIn = ko.observable(userdata['logged_in']);
        //self.data = ko.observableArray();
        self.artistid = ko.observable();
        self.name = ko.observable();
        self.bio = ko.observable();
        self.genre = ko.observable();
        self.year = ko.observable();
        self.members = ko.observableArray();
        self.albums = ko.observableArray();
        //self.tracks;

        $.ajax({
            type: "GET",
            url: url,
            dataType: 'json',
            success: function(result){
                
                self.artistid(result.artist.artist_id);
                self.name(result.artist.name);
                self.bio(nl2br(result.artist.biography));
                self.genre(result.artist.genre);
                self.year(result.artist.year_formed);
                self.members(result.artist.members);
                self.albums(result.artist.albums);
                
                // builds tracklist for each album dynamically
                var i = 0;
                while(result.artist.albums[i]){
                    
                    var tracks = result.artist.albums[i].tracklist;
                    var j = 0;
                    while(tracks[j]){
                        var html = 
                            '<li class="track"><a href="/song/?artist=' + self.artistid() + '&album='+ result.artist.albums[i].album_id +'&song=' + tracks[j].track_id + '">' +
                                tracks[j].track_no + '. ' + tracks[j].title + '</a>' +
                            '</li>';
                        
                        $('.tracklist [album_id= "' + result.artist.albums[i].album_id + '"]').append(html);
                        j++;
                    }
                    i++;
                }
                
            },
            error: function(result){
                console.log(result);
                //alert("Error");
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