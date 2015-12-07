localStorage.clear();

var userdata = { 'logged_in': false };

//TODO remove this block when done everything
if(JSON.parse(localStorage.getItem("userdata")) != null){
	userdata = JSON.parse(localStorage.getItem("userdata"));
	
	$('#username').text(userdata['username']);
    $('#user-img').attr("src", "http://localhost:5000/static/uploads/" + userdata['image_url']);
}

// Here's my data model
var ViewModel = function() {
    
    var self = this;
    // USER VARS
    
    self.loggedIn = ko.observable(userdata['logged_in']);
    self.username = ko.observable(userdata['username']);
    console.log(userdata['username']);
    //---------------------------
    
    self.username = ko.observable();
    self.password = ko.observable();
    self.userdata = {}

    $("#login-form").on("submit", function(e){
        
        //e.preventDefault();
        
        self.userdata.username = self.username;
        self.userdata.password = self.password;
        var queryData = ko.toJSON(self.userdata);
        console.log(queryData);
        $.ajax({
            type: "POST",
            url: "http://localhost:5000/login/",
            dataType: 'json',
            contentType: 'json',
            data: queryData,


            success: function(result){
				console.log("hello");
                if (!result.userdata){
                    alert("Authentification failure. Please check credentials");
                }

                else{
                    alert("Success");
                    console.log(result);
                    console.log(result.userdata);
                    localStorage.setItem("userdata", JSON.stringify(result.userdata));
                     window.location.href = "/home";
                }
                
            },
            
            error: function(result){
                console.log(result);
                alert("Error");
            }
        });
    });
 
};

ko.applyBindings(new ViewModel()); // This makes Knockout get to work