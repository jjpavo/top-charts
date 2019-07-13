import axios from '../@bundled-es-modules/axios/axios.js';

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"

let cropperWrapper = {
  cropper: undefined,
  mode: undefined
};
// The current cropped image.
let croppedImage;
export let defaultImages = {};
let croppedImages = {};

window.addEventListener('beforeunload', function (e) {
  // e.preventDefault();
  // e.returnValue = "";
});

export function readFile(input, readerFunc, type) {
  if (input.files && input.files[0]) {
    var reader = new FileReader();
    if (type === "url") {
      reader.readAsDataURL(input.files[0]);
    } else if (type === "text") {
      reader.readAsText(input.files[0])
    } else {
      // TODO
    }
    reader.onload = function (event) {
      readerFunc(event);
    }
  } else {
    alert("Sorry - you're browser doesn't support the FileReader API");
  }
}

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

document.allowDrop = function (ev) {
  ev.preventDefault();
}

document.drag = function (ev) {
  ev.dataTransfer.setData("src", ev.target.src);
  ev.dataTransfer.setData("title", ev.target.alt);
  ev.dataTransfer.setData("id", ev.target.dataset.id);
  ev.dataTransfer.setData("relpath", ev.target.dataset.relpath);
}

document.drop = function (ev) {
  ev.preventDefault();
  const src = ev.dataTransfer.getData("src");
  const title = ev.dataTransfer.getData("title");
  const id = ev.dataTransfer.getData("id");
  const relpath = ev.dataTransfer.getData("relpath");

  // Whether you're dragging onto an empty div or an image.
  if (ev.target.nodeName == "IMG") {
    ev.target.src = src;
    ev.target.title = title;
    ev.target.alt = title;
    ev.target.dataset.id = id;
    ev.target.dataset.relpath = relpath;
  } else {
    let draggedImage = document.createElement('img');
    draggedImage.src = src;
    draggedImage.title = title;
    draggedImage.alt = title;
    draggedImage.dataset.id = id;
    draggedImage.dataset.relpath = relpath;
    draggedImage.draggable = false;
    ev.target.appendChild(draggedImage);
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const image = document.getElementById('image');

  const imageOptionsForm = document.getElementById('image-options');

  let croppedCanvas;
  croppedImage = document.getElementById("cropped-image");
  croppedImage.draggable = true;
  croppedImage.ondragstart = function (event) {
    document.drag(event);
  }

  const cropperModal = document.getElementById("cropper-modal");

  const openCropperButton = document.getElementById("open-cropper");

  const closeCropper = document.getElementsByClassName("close")[0];

  const cropButton = document.getElementById("crop");

  const tagInput = document.getElementById("tags");

  const aspect169Button = document.getElementById("16:9");
  const aspect43Button = document.getElementById("4:3");
  const aspect11Button = document.getElementById("1:1");
  const aspectFreeButton = document.getElementById("free-aspect-ratio");

  const imageSearchButton = document.getElementById("image-search-button");
  const imageSearchText = document.getElementById("image-search");
  const searchedImages = document.getElementById("searched-images");

  document.getElementById('image-upload').addEventListener("change", function () {
    // When an image is opened, read it as a base 64 string and open the cropper.
    readFile(this, readImage, "url");
  });

  // Open the cropper when the button is clicked
  openCropperButton.onclick = () => {
    openCropper();
  }

  cropButton.onclick = function () {
    croppedCanvas = cropperWrapper.cropper.getCroppedCanvas();
    croppedImage.src = croppedCanvas.toDataURL();

    const cropperData = cropperWrapper.cropper.getData();
    const cropData = [
      cropperData.x,
      cropperData.y,
      cropperData.x + cropperData.width,
      cropperData.y + cropperData.height
    ];

    if (cropperWrapper.mode === "uploaded") {
      const tags = tagInput.value.split(",");
      const imageOptions = serialize(imageOptionsForm);
      uploadImage(imageOptions, cropData, tags);
    } else {
      defaultImages[croppedImage.dataset.id] = {
        cropData: cropData,
        path: croppedImage.dataset.relpath,
      }
      console.log(defaultImages);
    }

    cropperModal.style.display = "none";
    cropperWrapper.cropper.destroy();
  }

  // Button to close the cropper.
  closeCropper.onclick = function () {
    cropperModal.style.display = "none";
    cropperWrapper.cropper.destroy();
  }

  // Close the cropper when the user clicks outside it.
  window.onclick = function (event) {
    if (event.target == cropperModal) {
      cropperModal.style.display = "none";
      cropperWrapper.cropper.destroy();
    }
  }

  aspect169Button.onclick = function (event) {
    if (!cropperWrapper.cropper) {
      return;
    }

    cropperWrapper.cropper.setAspectRatio(16 / 9);
  }

  aspect43Button.onclick = function (event) {
    if (!cropperWrapper.cropper) {
      return;
    }

    cropperWrapper.cropper.setAspectRatio(4 / 3);
  }

  aspect11Button.onclick = function (event) {
    if (!cropperWrapper.cropper) {
      return;
    }

    cropperWrapper.cropper.setAspectRatio(1);
  }

  aspectFreeButton.onclick = function (event) {
    if (!cropperWrapper.cropper) {
      return;
    }

    cropperWrapper.cropper.setAspectRatio(NaN);
  }

  imageSearchButton.onclick = function (event) {
    axios({
      method: 'get',
      url: 'image',
      params: {
        tags: imageSearchText.value
      }
    }).then(function (response) {
      while (searchedImages.firstChild) {
        searchedImages.removeChild(searchedImages.firstChild);
      }
      for (let key in response.data) {
        if (response.data.hasOwnProperty(key)) {
          let val = response.data[key];
          let searchedImage = document.createElement('img');
          searchedImage.src = val.path;
          searchedImage.title = val.title;
          searchedImage.alt = val.title;
          searchedImage.dataset.id = key;
          searchedImage.dataset.relpath = val.relpath;
          searchedImage.draggable = true;
          searchedImage.ondragstart = function (event) {
            document.drag(event);
          }
          searchedImage.ondblclick = function (event) {
            cropperWrapper.mode = "searched";
            image.src = searchedImage.src;
            croppedImage.title = searchedImage.title;
            croppedImage.alt = searchedImage.alt;
            croppedImage.dataset.id = searchedImage.dataset.id;
            croppedImage.dataset.relpath = searchedImage.dataset.relpath;
            openCropper();
          }
          searchedImages.appendChild(searchedImage);
        }
      };
    }).catch(function (error) {
      // TODO
      console.log(error);
    });
  }

  function readImage(event) {
    image.src = event.target.result;
    cropperWrapper.mode = "uploaded";
    openCropper();
  }

  function uploadImage(imageOptions, cropData, tags) {
    axios({
      method: 'post',
      url: 'image',
      data: {
        image: image.src.replace(/^data:image\/[a-z]+;base64,/, ""),
        title: imageOptions['image-title'],
        tags: tags
      }
    }).then(function (response) {
      croppedImage.dataset.path = response.headers.path;
      croppedImage.dataset.id = response.headers.id;
      // TODO Add title.

      defaultImages[response.headers.id] = {
        cropData: cropData,
        path: response.headers.path,
      }
      croppedImages[response.headers.id] = {
        image: croppedImage.src,
        index: undefined,
        group: undefined
      }
    }).catch(function (error) {
      // TODO
      console.log(error);
    });
  }


  function openCropper() {
    switch (cropperWrapper.mode) {
      case "uploaded":
        imageOptionsForm.style.display = "block";
        break;
      case "searched":
        imageOptionsForm.style.display = "none";
        break;
      default:
        return;
    }

    cropperWrapper.cropper = new Cropper(image, {
      dragMode: 'move',
      initialAspectRatio: 1,
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

  const containers = document.querySelectorAll('.draggable-container');

  const sortable = new Draggable.Sortable(containers, {
    draggable: ".draggable",
    plugins: [Draggable.Plugins.ResizeMirror]
  });
});