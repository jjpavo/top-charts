import axios from '../@bundled-es-modules/axios/axios.js';

import defaultImages from './scripts.js';

const chart = {
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

const chartDiv = document.getElementById("chart");

const renderButton = document.getElementById("render");

// Using a button to open the chart manually rather than it just open automatically
// since most people block popups nowadays.
const openChartButton = document.getElementById("open-chart");
const openChartLink = document.getElementById("open-chart-link");

const tilesDiv = document.getElementById("tiles");

renderButton.onclick = function () {
  renderChart()
}

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

function initTitle() {
  const header = document.getElementById("chart-title");
  header.innerText = chart.title_text.text;

  const inputHeader = document.getElementById("title-input");

  editableText(inputHeader, header, "title");
}

function initGroups() {
  let tileSize;
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

    const tilesWrapper = document.createElement("div");
    tilesWrapper.className = "tiles-wrapper draggable-container grid";

    groupWrapper.appendChild(header);
    groupWrapper.appendChild(inputHeader);
    groupWrapper.appendChild(tilesWrapper);

    tileSize = chart["tile_sizes"][group];
    tilesWrapper.style.gridTemplateColumns = "repeat(" + chart.tile_count[group][0] + ", " + tileSize[0] + "px";

    for (let i = chart.tile_count[group][1]; i > 0; i--) {
      for (let j = chart.tile_count[group][0]; j > 0; j--) {
        const tile = document.createElement("div");
        tile.className = "tile draggable";
        tile.style.width = tileSize[0] + "px";
        tile.style.height = tileSize[1] + "px";

        tile.ondrop = function (event) { document.drop(event) };
        tile.ondragover = function (event) { document.allowDrop(event) };

        tilesWrapper.appendChild(tile);
      }
    }
  }
}

function initChart() {
  initTitle();
  initGroups();
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

initChart();