axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"

let cropper;
// The current cropped image.
let croppedImage;
let defaultImages = {};
let croppedImages = {};

window.addEventListener('beforeunload', function (e) {
  // e.preventDefault();
  // e.returnValue = "";
});

/*!
 * Serialize all form data into an object
 * (c) 2018 Chris Ferdinandi, MIT License, https://gomakethings.com
 * 
 * Modified to return JSON object.
 * 
 * @param  {Node}   form The form to serialize
 * @return {Object}      The serialized form data
 */
let serialize = function (form) {

  // Setup our serialized data
  var serialized = {};

  // Loop through each field in the form
  for (var i = 0; i < form.elements.length; i++) {

    var field = form.elements[i];

    // Don't serialize fields without a name, submits, buttons, file and reset inputs, and disabled fields
    if (!field.name || field.disabled || field.type === 'file' || field.type === 'reset' || field.type === 'submit' || field.type === 'button') continue;

    // If a multi-select, get all selections
    if (field.type === 'select-multiple') {
      for (var n = 0; n < field.options.length; n++) {
        if (!field.options[n].selected) continue;
        serialized[field.name] = field.options[n].value;
      }
    }

    // Convert field data to a query string
    else if ((field.type !== 'checkbox' && field.type !== 'radio') || field.checked) {
      serialized[field.name] = field.value;
    }
  }

  return serialized;

};

document.addEventListener("DOMContentLoaded", function () {
  const image = document.getElementById('image');

  const imageOptionsForm = document.getElementById('image-options');

  let croppedCanvas;
  croppedImage = document.getElementById("cropped-image");

  const cropperModal = document.getElementById("cropper-modal");

  const openCropperButton = document.getElementById("open-cropper");

  const closeCropper = document.getElementsByClassName("close")[0];

  const cropButton = document.getElementById("crop");

  document.getElementById('image-upload').addEventListener("change", function () {
    // When an image is opened, read it as a base 64 string and open the cropper.
    readFile(this);
  });

  // Open the cropper when the button is clicked
  openCropperButton.onclick = () => {
    openCropper();
  }

  cropButton.onclick = function () {
    let imageOptions = serialize(imageOptionsForm);
    croppedCanvas = cropper.getCroppedCanvas();
    croppedImage.src = croppedCanvas.toDataURL();
    var cropData = cropper.getData();
    // crop: [
    //   cropData.x,
    //   cropData.y,
    //   cropData.x + cropData.width,
    //   cropData.y + cropData.height
    // ],
    axios({
      method: 'post',
      url: 'image',
      data: {
        image: image.src,
        title: imageOptions['image-title']
      }
    }).then(function (response) {
      console.log(response);
    }).catch(function (error) {
      // TODO
      console.log(error);
    });

    cropperModal.style.display = "none";
    cropper.destroy();
  }

  // Button to close the cropper.
  closeCropper.onclick = function () {
    cropperModal.style.display = "none";
    cropper.destroy();
  }

  // Close the cropper when the user clicks outside it.
  window.onclick = function (event) {
    if (event.target == cropperModal) {
      cropperModal.style.display = "none";
      cropper.destroy();
    }
  }

  function readFile(input) {
    if (input.files && input.files[0]) {
      var reader = new FileReader();
      reader.readAsDataURL(input.files[0]);
      reader.onload = function (e) {
        image.src = e.target.result;
        openCropper();
      }
    } else {
      alert("Sorry - you're browser doesn't support the FileReader API");
    }
  }


  function openCropper() {
    cropper = new Cropper(image, {
      dragMode: 'move',
      initialAspectRatio: 16 / 9,
      autoCropArea: 0.65,
      restore: false,
      guides: true,
      center: false,
      highlight: false,
      cropBoxMovable: true,
      cropBoxResizable: true,
      toggleDragModeOnDblclick: false
    });
    cropperModal.style.display = "block";
  }
});