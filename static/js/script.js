 function downLoad(){
                   jQuery(".layer1_class").delay(1000).fadeOut("slow");
                   document.getElementById("layer2").style.visibility="visible";
};


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

 