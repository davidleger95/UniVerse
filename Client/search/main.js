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
        var query = queryParameters.search;
        var url = "http://localhost:5000/search/" + query;

        var self = this;
        
        self.loggedIn = ko.observable(userdata['logged_in']);
        
        self.query = ko.observable(query);
        self.songs = ko.observableArray();
        self.albums = ko.observableArray();
        self.artists = ko.observableArray();

        $.ajax({
            type: "GET",
            url: url,
            dataType: 'json',
            success: function(result){
                
                self.songs(result.tracks);
                self.albums(result.albums);
                console.log(self.albums())
                self.artists(result.artists);
                
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