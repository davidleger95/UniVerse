$(document).ready(function(){
    // Here's my data model
    
     var userdata = { 'logged_in': false };
    
    if(JSON.parse(localStorage.getItem("userdata"))){
        userdata = JSON.parse(localStorage.getItem("userdata"));

        $('#username').text(userdata['username']);
        $('#user-img').attr("src", "http://localhost:5000/static/uploads/" + userdata['image_url']);
        $('#user-image-preview').attr("src", "http://localhost:5000/static/uploads/" + userdata['image_url']);
    }
    
    var ViewModel = function() {

        var self = this;
        // USER VARS

        self.loggedIn = ko.observable(userdata['logged_in']);
        //---------------------------

        self.username = ko.observable(userdata['username']);
        self.email = ko.observable(userdata['email']);
        self.confirmPassword = ko.observable();
        self.password = ko.observable();
        self.userdata = {}

        $("#save-settings").on("submit", function(e){
            
            self.userdata.username = self.username;
            self.userdata.email = self.email;
            self.userdata.password = self.password;
            self.userdata.confirmPassword = self.confirmPassword;
            
            var queryData = ko.toJSON(self.userdata);
            console.log(queryData);
            if(JSON.parse(queryData).password != JSON.parse(queryData).confirmPassword){
                alert("Passwords do not match!");
                return false;
            }
            /*
            $.ajax({
                type: "PUT",
                url: "http://localhost:5000/users/",
                dataType: 'json',
                contentType: 'json',
                data: queryData,

                success: function(result){
                    console.log(result);
                    if (result.userdata == false){
                        alert(result.error);
                        alert("false");
                    }

                    else{
                        alert(result.message);
                        alert("true");
                        window.location.href = "/home";
                    }

                },

                error: function(result){
                    console.log(result);
                    alert("Error");
                }
            });*/
        });

    };

    ko.applyBindings(new ViewModel()); // This makes Knockout get to work
    
});