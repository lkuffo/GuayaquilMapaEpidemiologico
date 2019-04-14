$(document).ready(function(){
   $(".hm-institution-box").click(function(){
       var id = $(this).attr('id').split("-").pop();
       window.location.href = "/healthmap/" + id
   })

});