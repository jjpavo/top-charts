import axios from '../@bundled-es-modules/axios/axios.js';

import { defaultImages, readFile } from './scripts.js';

let chart = {
  username: "username",
  title_text: {
    text: "Top 20 Anime",
    size: 70,
    height_padding: 30,
    width_padding: 150,
    show: true,
    font: "arial",
    alignment: "center"
  },
  tile_name_text: {
    size: 24,
    height_padding: 5,
    width_padding: 5,
    show: true,
    font: "arial",
    alignment: "left"
  },
  tile_name_row_text: {
    size: 30,
    height_padding: 5,
    width_padding: 0,
    show: true,
    font: "arial",
    alignment: "left"
  },
  group_title_text: {
    text: [
      "Top 10",
      "Second-tier Classics"
    ],
    size: 62,
    height_padding: 50,
    width_padding: 150,
    show: true,
    font: "arial",
    alignment: "left"
  },
  tile_row_text: {
    size: 55,
    height_padding: 0,
    width_padding: 15,
    show: true,
    font: "arial",
    alignment: "left"
  },
  gap_size: 5,
  chart_width_padding: 50,
  chart_height_padding: 10,
  background_color: "#292929",
  group_count: 2,
  tile_count: [
    [
      5,
      2
    ],
    [
      10,
      1
    ]
  ],
  tile_sizes: [
    [
      360,
      360
    ],
    [
      180,
      180
    ]
  ],
  images: [
  ]
}

// For resaving a chart.
let chartID;

const chartDiv = document.getElementById("chart");

// const containers = document.querySelectorAll('.draggable-container');

const renderButton = document.getElementById("render");
const saveButton = document.getElementById("save");
const downloadButton = document.getElementById("download-config");
const uploadChartConfig = document.getElementById("upload-config");

// Using a button to open the chart manually rather than it just open automatically
// since most people block popups nowadays.
const openChartButton = document.getElementById("open-chart");
const openChartLink = document.getElementById("open-chart-link");

const tilesDiv = document.getElementById("tiles");


renderButton.onclick = function () {
  renderChart();
}

saveButton.onclick = function () {
  saveChart();
}

downloadButton.onclick = function () {
  downloadChartConfig();
}

uploadChartConfig.addEventListener("change", function () {
  readFile(this, readChartConfig, "text");
});

openChartLink.onclick = function () {
  openChartButton.style.display = "none";
}

function editableText(inputElement, textElement, type) {
  inputElement.addEventListener("keydown", function (event) {
    if (event.repeat) { return } //debounce
    if (event.keyCode === 13) {
      // Show label with user entry and hide text input box.

      textElement.style.display = "block";

      if (event.target.value === "") {
        textElement.innerText = "\"empty\"";
      } else {
        textElement.innerText = event.target.value;
      }

      event.target.style.display = "none";

      if (type === "group") {
        const group = event.target.parentElement.dataset.groupIndex;
        chart['group_title_text']['text'][Number(group)] = event.target.value;
      } else if (type === "title") {
        chart['title_text']['text'] = event.target.value;
      }
    }
  });

  textElement.addEventListener("click", function (event) {
    // Show label with user entry and hide text input box.
    inputElement.style.display = "block";
    inputElement.value = event.target.innerText;
    event.target.style.display = "none";
  });
}

function loadTitle() {
  const header = document.getElementById("chart-title");
  header.innerText = chart.title_text.text;

  const inputHeader = document.getElementById("title-input");

  editableText(inputHeader, header, "title");
}

function loadGroups() {
  while (tilesDiv.firstChild) {
    tilesDiv.removeChild(tilesDiv.firstChild);
  }

  let gapSize = chart["gap_size"];

  let tileSize;
  let tileXCount;
  let tileYCount;
  for (let group in chart.tile_count) {
    const groupWrapper = document.createElement("div");
    groupWrapper.className = "chart-group"
    groupWrapper.id = "chart-group-" + group;
    groupWrapper.dataset.groupIndex = group;

    tilesDiv.appendChild(groupWrapper);

    const header = document.createElement("h2");

    header.className = "group-title";
    header.innerText = chart['group_title_text']['text'][Number(group)];

    const inputHeader = document.createElement("input");
    inputHeader.type = "text";
    inputHeader.className = "group-title-input";
    inputHeader.style.display = "none";

    editableText(inputHeader, header, "group");

    tileSize = chart["tile_sizes"][group];
    tileXCount = chart.tile_count[group][0];
    tileYCount = chart.tile_count[group][1];

    const tilesWrapper = document.createElement("div");
    tilesWrapper.className = "tiles-wrapper draggable-container grid";
    tilesWrapper.style.gridGap = gapSize + "px";
    tilesWrapper.style.width = (tileSize[0] * tileXCount) + (gapSize * tileXCount) + "px";
    tilesWrapper.style.height = (tileSize[1] * tileYCount) + (gapSize * tileYCount) + "px";
    tilesWrapper.style.gridTemplateColumns = "repeat(" + chart.tile_count[group][0] + ", 1fr";
    tilesWrapper.style.gridTemplateRows = "repeat(" + chart.tile_count[group][1] + ", 1fr";

    groupWrapper.appendChild(header);
    groupWrapper.appendChild(inputHeader);
    groupWrapper.appendChild(tilesWrapper);


    for (let i = tileYCount; i > 0; i--) {
      for (let j = tileXCount; j > 0; j--) {
        const tile = document.createElement("div");
        tile.className = "tile draggable";
        // tile.style.width = tileSize[0] + "px";
        // tile.style.height = tileSize[1] + "px";

        tile.ondrop = function (event) { document.drop(event) };
        tile.ondragover = function (event) { document.allowDrop(event) };

        tilesWrapper.appendChild(tile);
        // tile.style.width = "";
        // tile.style.height = "";

      }
    }
  }
}

function loadChart() {
  loadTitle();
  loadGroups();
  // TODO Load images, if present in loaded chart.
}

function renderChart() {
  gatherImages();
  axios({
    method: 'post',
    url: 'chart',
    data: chart,
    responseType: 'blob'
  }).then(function (response) {
    let url = URL.createObjectURL(response.data);
    openChartLink.href = url;
    openChartButton.style.display = "inline";
  }).catch(function (error) {
    // TODO
    console.log(error);
  });

  return false;
}

function saveChart() {
  // TODO resave chart
  gatherImages();
  axios({
    method: 'post',
    url: 'config',
    data: {
      chart: chart,
      // TODO WIP
      name: chart["title_text"]["text"],
      username: null
    }
  }).then(function (response) {
    chartID = response.headers.id;
  }).catch(function (error) {
    // TODO
    console.log(error);
  });
}

function downloadChartConfig() {
  let chartJSON = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(chart));
  let downloadNode = document.createElement('a');
  downloadNode.setAttribute("href", chartJSON);
  downloadNode.setAttribute("download", chart["title_text"]["text"] + ".json");
  document.body.appendChild(downloadNode);
  downloadNode.click();
  downloadNode.remove();
}

function readChartConfig(event) {
  chart = JSON.parse(event.target.result);
  // TODO Smarter way of loading chart, so that it's not always loaded wholly from scratch.
  loadChart();
  loadImages();
}

function loadImages() {
  if (typeof chart.images !== 'undefined' && chart.images.length > 0) {
    for (let group in chart.images) {
      let groupDiv = document.getElementById("chart-group-" + group);
      let tilesWrapper = groupDiv.getElementsByClassName("tiles-wrapper")[0];
      let tileSize = chart.tile_sizes[group];
      for (let image in chart.images[group]) {
        axios({
          method: 'get',
          url: 'image',
          params: {
            path: chart.images[group][image].path,
            "crop": chart.images[group][image].crop,
            "tile_size": tileSize
          }
        }).then(function (response) {
          let tile = tilesWrapper.childNodes[image]
          let tileImage = document.createElement('img');
          let id = Object.keys(response.data)[0]
          tileImage.src = "data:image/jpg;base64," + response.data[id].path;
          tileImage.title = response.data[id].title;
          tileImage.alt = response.data[id].title;
          tileImage.dataset.id = id;
          tileImage.dataset.relpath = response.data[id].relpath;
          tile.appendChild(tileImage);
          // console.log(response);
        }).catch(function (error) {
          console.log(error);
          console.log(error.response.data.message);
        });
        // return;
      }
    }
  }
}

function gatherImages() {
  const tileGroups = document.getElementsByClassName("tiles-wrapper");
  let group;
  let image;
  // TODO Optimize so we don't need to repush all images into a new list!
  chart["images"] = [];
  for (let i = 0, len = tileGroups.length; i < len; i++) {
    group = tileGroups[i].childNodes;
    chart["images"].push([]);
    for (let j = 0, groupLen = group.length; j < groupLen; j++) {
      image = group[j].firstChild
      chart["images"][i].push({
        path: image.dataset.relpath,
        id: image.dataset.id,
        // Using alt because title is inconsistent? It's sometimes empty.
        title: image.dataset.alt,
        crop: defaultImages[image.dataset.id]["cropData"]
      });
    }
  }
}

loadChart();