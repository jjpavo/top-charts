let cropper;
let croppedImage;

document.addEventListener("DOMContentLoaded", function () {
  let defaultImages = {};
  let croppedImages = {};

  let image = document.getElementById('image');

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
    croppedCanvas = cropper.getCroppedCanvas();
    croppedImage.src = croppedCanvas.toDataURL();
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