// Here's my data model
var ViewModel = function() {
    
    var artist = 1;
    
    var self = this;

    //self.data = ko.observableArray();
    self.name = ko.observable();
    self.bio = ko.observable();
    self.genre = ko.observable();
    self.year = ko.observable();
    self.members = ko.observableArray();
    
    $.ajax({
        type: "GET",
        url: "localhost/1.json",
        dataType: 'json',
        success: function(result){
            console.log(result.artist.biography);
            self.name(result.artist.name);
            self.bio(result.artist.biography);
            self.genre(result.artist.genre);
            self.year(result.artist.year_formed);
            self.members(result.artist.members);
        },
        error: function(result){
            console.log(result);
            alert("Error");
        }
    });
 
};

ko.applyBindings(new ViewModel()); // This makes Knockout get to work