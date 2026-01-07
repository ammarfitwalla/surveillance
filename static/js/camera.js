/*========================================================*/
/*====  image upload js code                    ==========*/
/*========================================================*/


/*function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            $('#imagePreview').css('background-image', 'url('+e.target.result +')');
            $('#imagePreview').hide();
            $('#imagePreview').fadeIn(650);
        }
        reader.readAsDataURL(input.files[0]);
    }
}
jQuery(document).ready(function($) {
        jQuery("#imageUpload").change(function() {
            readURL(this);
        });*/


//===============================================
//  on click add active class on menu   //
//===============================================
/*  jQuery('ul li a').click(function(){
    jQuery('li a').removeClass("active");
    jQuery(this).addClass("active");
})*/
/*});*/

//============================================================================
// on click select camera options//
//================================================================================

function checkCamera() {
  if (document.getElementById('webcam').checked) {
    document.getElementById('showIP').style.display = 'none';
    document.getElementById('showVideo').style.display = 'none';
  } else if (document.getElementById('ipcam').checked) {
    document.getElementById('showIP').style.display = 'block';
    document.getElementById('showVideo').style.display = 'none';
  } else if (document.getElementById('video').checked) {
    document.getElementById('showVideo').style.display = 'block';
    document.getElementById('showIP').style.display = 'none';
  }
}

function showCameraSelect() {
  if (document.getElementById('camera_form').style.display = 'none') {
    document.getElementById('camera_form').style.display = 'block';
  } else {
    document.getElementById('camera_form').style.display = 'none';
  }


}

function showProgress() {
  document.getElementById('progress').style.display = 'block';
  document.getElementById('trainButton').style.display = 'none';
  document.getElementById('addUser').disabled = true;
}

//============================================================================
// image upload js code   //
//================================================================================
$(document).ready(function () {
  if (window.File && window.FileList && window.FileReader) {
    $("#files").on("change", function (e) {
      var files = e.target.files,
        filesLength = files.length;
      for (var i = 0; i < filesLength; i++) {
        var f = files[i]
        var fileReader = new FileReader();
        fileReader.onload = (function (e) {
          var file = e.target;
          $("<div class=\"img-thumb-wrapper pb-4\">" +
            "<img class=\"img-thumb\" src=\"" + e.target.result + "\" title=\"" + file.name + "\"/>" +
            "<br/><span class=\"remove\">Remove</span>" +
            "</div>").insertAfter("#files");
          $(".remove").click(function () {
            $(this).parent(".img-thumb-wrapper").remove();
          });

        });
        fileReader.readAsDataURL(f);
      }
      console.log(files);
    });
  } else {
    alert("Your browser doesn't support to File API")
  }
});

$(document).ready(function () {
  if (window.File && window.FileList && window.FileReader) {
    $("#videoFiles").on("change", function (e) {
      var files = e.target.files,
        filesLength = files.length;
      for (var i = 0; i < filesLength; i++) {
        var f = files[i]
        var fileReader = new FileReader();
        fileReader.onload = (function (e) {
          var file = e.target;
          // $("<div class=\"img-thumb-wrapper pb-4\">" +
          //   "<img class=\"img-thumb\" src=\"" + e.target.result + "\" title=\"" + file.name + "\"/>" +
          //   "<br/><span class=\"remove\">Remove</span>" +
          //   "</div>").insertAfter("#files");
          // $(".remove").click(function () {
          //   $(this).parent(".img-thumb-wrapper").remove();
          // });

        });
        fileReader.readAsDataURL(f);
      }
      console.log(files);
    });
  } else {
    alert("Your browser doesn't support to File API")
  }
});