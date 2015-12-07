// --------------------------------------------------
//  UI/UX Functionality for UniVerse
//  DATE    August, 2015
//
//  AUTHOR  David Leger
//  URL     davidleger.me
//  EMAIL   davidleger95@me.com
//  
// --------------------------------------------------

$(document).ready(function(){
    
    // --------------------------------------------------
    //  Navbar Dropdown
    // --------------------------------------------------
    $(".nav-item").on('click', function(){
        $(this).toggleClass('active');
        $(this).siblings().removeClass('active');
    });
    
    // --------------------------------------------------
    //  Add Artist Member
    // --------------------------------------------------
    $("#new-member").keyup(function (e) {
        if (e.keyCode == 17) {
            var $member = $(this);

            var index = $member.parent().index() + 1;
            var value = $member.val();

            if(index < 10){
                icon = index;
            }else{
                icon = 'ellipsis'
            }

            $('<li><input name="artist-member-'+ index +
              '" id="artist-member-'+ index +
              '" type="text" class="icon-'+ icon +
              '" placeholder="Member '+ index +
              '" value="'+ value +'"></li>').insertBefore($member.parent());

            $member.val('');
        }
    });
    
    // --------------------------------------------------
    //  Add Song Composer
    // --------------------------------------------------
    $("#new-composer").keyup(function (e) {
        if (e.keyCode == 17) {
            var $composer = $(this);
            var index = $composer.parent().index() + 1;
            var value = $composer.val();

            if(index < 10){
                icon = index;
            }else{
                icon = 'ellipsis'
            }

            $('<li><input name="composer-'+ index +
              '" id="composer-'+ index +
              '" type="text" class="icon-'+ icon +
              '" placeholder="Composer '+ index +
              '" value="'+ value +'"></li>').insertBefore($composer.parent());

            $composer.val('');
        }
    });
});


// --------------------------------------------------
//  Filter Tracklist
// --------------------------------------------------
function filter(element) {
    var value = $(element).val();

    $(".tracklist > ul > li").each(function() {
        if ($(this).text().toLowerCase().search(value) > -1) {
            $(this).slideDown(200);
            $('.album-meta').show();
        }
        else {
            $(this).slideUp(200);
            $('.album-meta').hide();
        }
    });
}

// --------------------------------------------------
//  Image Upload Previews
// --------------------------------------------------
function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            $('#user-image-preview, #album-artwork-preview').attr('src', e.target.result);
        }

        reader.readAsDataURL(input.files[0]);
    }
}

$("#user-image, #album-artwork").change(function(){
    readURL(this);
});