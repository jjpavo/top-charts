import axios from '../@bundled-es-modules/axios/axios.js';

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

function initGroups() {
  for (let group in chart.tile_count) {
    const groupWrapper = document.createElement("div");
    groupWrapper.className = "chart-group"
    groupWrapper.id = "chart-group-" + group;
    tilesDiv.appendChild(groupWrapper);

    const header = document.createElement("h2");
    header.className = "group-title";
    header.innerText = "Group Title";

    const inputHeader = document.createElement("input");
    inputHeader.type = "text";
    inputHeader.className = "group-title-input";
    inputHeader.style.display = "none";

    editableText(inputHeader, header);

    const tilesWrapper = document.createElement("div");
    tilesWrapper.className = "tiles-wrapper draggable-container grid";

    groupWrapper.appendChild(header);
    groupWrapper.appendChild(inputHeader);
    groupWrapper.appendChild(tilesWrapper);

    for (let i = chart.tile_count[group][1]; i > 0; i--) {
      for (let j = chart.tile_count[group][0]; j > 0; j--) {
        const tile = document.createElement("div");
        tile.className = "tile draggable";
        tile.ondrop = function (event) { document.drop(event) };
        tile.ondragover = function (event) { document.allowDrop(event) };
        tilesWrapper.appendChild(tile);
      }
    }
  }
}

function initChart() {
  initGroups();
}

function renderChart() {
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

initChart();