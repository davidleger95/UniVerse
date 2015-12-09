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
    
    
    var self = this;
    
    self.loggedIn = ko.observable(userdata['logged_in']);
   
 
};

ko.applyBindings(new ViewModel()); // This makes Knockout get to work

});