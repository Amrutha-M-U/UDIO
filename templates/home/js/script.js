 function downLoad(){

                   jQuery(".layer1_class").delay(1000).fadeOut("slow");
                   document.getElementById("layer2").style.visibility="visible";
                          
        
}


window.onscroll = function() {myFunction()};

function myFunction() {
    if (document.body.scrollTop > 50 || document.documentElement.scrollTop > 50) {
         $("header").removeClass("header-nav");
         $("header").addClass("header-navScroll");
    } else {
         $("header").removeClass("header-navScroll");
         $("header").addClass("header-nav");
    }

    if (document.body.scrollTop > 699 || document.documentElement.scrollTop > 699) {
         $("header").removeClass("header-navScroll");
         $("header").addClass("header-navScrollLogin");
    } else if (document.body.scrollTop > 50 || document.documentElement.scrollTop > 50){
         $("header").removeClass("header-navScrollLogin");
         $("header").addClass("header-navScroll");
    }
}

 var hashTagActive = "";
    $(".scroll").click(function (event) {
        if(hashTagActive != this.hash) { //this will prevent if the user click several times the same link to freeze the scroll.
            event.preventDefault();
            //calculate destination place
            var dest = 0;
            if ($(this.hash).offset().top > $(document).height() - $(window).height()) {
                dest = $(document).height() - $(window).height();
            } else {
                dest = $(this.hash).offset().top;
            }
            //go to destination
            $('html,body').animate({
                scrollTop: dest
            }, 2000, 'swing');
            hashTagActive = this.hash;
        }
    });