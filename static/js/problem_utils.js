var holds = [];
var polys = [];
var ratio;
var dragok = false;
var wasDragged = false;

var radius;
var holdDetectionActive = true;

function hexToRGBA(hex, alpha) {
  var r = parseInt(hex.slice(1, 3), 16),
    g = parseInt(hex.slice(3, 5), 16),
    b = parseInt(hex.slice(5, 7), 16);

  if (alpha) {
    return "rgba(" + r + ", " + g + ", " + b + ", " + alpha + ")";
  } else {
    return "rgb(" + r + ", " + g + ", " + b + ")";
  }
}

function fillCanvasWithGray(context, canvas) {
  // fill canvas with gray
  context.fillStyle = hexToRGBA("#9c9c9c", 0.65);
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = "#000000";
}


function draw(event) {
  var cnvs = document.getElementById("wall-canvas");
  var ctx = cnvs.getContext("2d");
  var holdColor = document.querySelector('input[name="hold_type"]:checked')
    .value;
  drawHold(
    ctx,
    event.offsetX,
    event.offsetY,
    radius * cnvs.width,
    holdColor,
    holds
  );
}

function drawHold(ctx, x, y, radius, color, holdArray, shouldPush = true) {
  // Test if click inside hold
  var hold_found = false;
  if (holdDetectionActive) {
    for (let index = 0; index < polys.length; index++) {
      var poly = {
        type: 'Polygon',
        coordinates: [polys[index]]
      }
      var inside = turf.booleanPointInPolygon.default([x, y], poly)
      if (inside == true) {
        drawPolygon(ctx, polys[index], color, 1);
        hold_found = true;
      }
    }
  }
  if (hold_found == false || holdDetectionActive == false) {
    // Draw circle
    ctx.globalCompositeOperation = "source-over";
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, 2 * Math.PI, false);
    ctx.lineWidth = 4;
    ctx.strokeStyle = color;
    ctx.stroke();
    ctx.globalCompositeOperation = 'destination-out';
    ctx.fill()
    ctx.globalCompositeOperation = "source-over";
  }
  // push to hold array
  if (shouldPush == true) {
    holdArray.push({
      x: x / ctx.width,
      y: y / ctx.height,
      color: color,
      radius: radius
    });
  }
}

// clear the canvas
function clear(cnvs, ctx) {
  ctx.clearRect(0, 0, cnvs.width, cnvs.height);
}

function drawPolygon(ctx, poly, color, ratio) {
  ctx.globalCompositeOperation = "source-over";
  ctx.lineWidth = 4;
  // ctx.fillStyle = hexToRGBA(color, 1);
  // ctx.strokeStyle = hexToRGBA(color, 1);
  if (poly.length <= 2) {
    return;
  }
  ctx.beginPath();
  ctx.moveTo(poly[0][0] * ratio, poly[0][1] * ratio);
  for (item = 2; item < poly.length - 1; item += 1) {
    ctx.lineTo(poly[item][0] * ratio, poly[item][1] * ratio);
  }
  ctx.lineTo(poly[item][0] * ratio, poly[item][1] * ratio);
  ctx.closePath();
  ctx.strokeStyle = color;
  ctx.stroke();
  ctx.globalCompositeOperation = 'destination-out';
  ctx.fill();
  ctx.globalCompositeOperation = "source-over";
}

// redraw the scene
function drawAll() {
  var cnvs = document.getElementById("wall-canvas");
  var ctx = cnvs.getContext("2d");
  clear(cnvs, ctx);
  if (holdDetectionActive) {
    fillCanvasWithGray(ctx, cnvs);
  }
  // redraw each rect in the holds array
  for (var i = 0; i < holds.length; i++) {
    var hold = holds[i];
    drawHold(ctx, hold.x * cnvs.width, hold.y * cnvs.height, hold.radius, hold.color, holds, shouldPush = false);
  }
}

// handle mousedown events
function myDown(e) {

  // tell the browser we're handling this mouse event
  e.preventDefault();
  e.stopPropagation();

  // get the current mouse position
  var mx = parseInt(e.offsetX);
  var my = parseInt(e.offsetY);

  var cnvs = document.getElementById("wall-canvas");
  const ctx = cnvs.getContext("2d");

  // test each hold polygon/marker to see if mouse is inside
  dragok = false;
  for (var i = 0; i < holds.length; i++) {
    var h = holds[i];
    for (let index = 0; index < polys.length; index++) {
      var poly = {
        type: 'Polygon',
        coordinates: [polys[index]]
      }
      var hold_inside = turf.booleanPointInPolygon.default([h.x * cnvs.width, h.y * cnvs.height], poly)
      var mouse_inside = turf.booleanPointInPolygon.default([mx, my], poly)
      if (hold_inside == true && mouse_inside == true) {
        dragok = true;
        h.isDragging = true;
      }
    }
    if (dragok == false) {
      if (((mx - h.x * cnvs.width) ** 2 + (my - h.y * cnvs.height) ** 2) < h.radius ** 2) {
        // if yes, set that hold marker isDragging=true
        dragok = true;
        h.isDragging = true;
      }
    }
  }
}

// handle mouseup events
function myUp(e) {

  // tell the browser we're handling this mouse event
  e.preventDefault();
  e.stopPropagation();

  // clear all the dragging flags
  for (var i = 0; i < holds.length; i++) {
    holds[i].isDragging = false;
  }
  // If we are not dragging anything
  if (!dragok) {
    // If the clicked element doesn't have the right selector, bail
    if (
      !(
        e.target.matches("#wall-image") ||
        e.target.matches("#wall-canvas")
      )
    ) return;
    // Don't follow the link
    // event.preventDefault();
    draw(e);
  }
  // Clear global drag flag
  dragok = false;
  return;
}

// handle mouse moves
function myMove(e) {
  // if we're dragging anything...
  if (dragok) {

    // tell the browser we're handling this mouse event
    e.preventDefault();
    e.stopPropagation();

    // get the current mouse position
    var mx = parseInt(e.offsetX);
    var my = parseInt(e.offsetY);

    // calculate the distance the mouse has moved
    // since the last mousemove
    var cnvs = document.getElementById("wall-canvas");
    const ctx = cnvs.getContext("2d");

    // move each hold marker that isDragging 
    // to the mouse position
    for (var i = 0; i < holds.length; i++) {
      var hold = holds[i];
      if (hold.isDragging) {
        hold.x = mx / cnvs.width;
        hold.y = my / cnvs.height;
      }
    }

    // redraw the scene with the new hold marker positions
    drawAll();

  }
}

function undoMove() {
  holds.pop(); // Remove last selected hold
  // Clear canvas
  var cnvs = document.getElementById("wall-canvas");
  const ctx = cnvs.getContext("2d");
  clear(cnvs, ctx);
  // fill again canvas with gray
  if (holdDetectionActive) {
    fillCanvasWithGray(ctx, cnvs);
  }
  // redraw holds
  var newHolds = [];
  holds.forEach((hold) =>
    drawHold(
      ctx,
      hold.x * cnvs.width,
      hold.y * cnvs.height,
      radius * cnvs.width,
      hold.color,
      newHolds
    )
  );
  holds = newHolds;
}

function setHolds() {
  // Avoid storing unnecessary data
  for (var i = 0; i < holds.length; i++) {
    delete holds[i].radius;
    delete holds[i].isDragging;
  }
  document.getElementById("holds-array").value = JSON.stringify(holds);
}

function validateForm() {
  if (holds.length === 0) {
    alert("Boulder cannot be empty");
    return false;
  }
  return true;
}

function downloadProblem(boulder_name, image_wall) {
  // create canvas, load image, add holds, and set to download
  var downloadCanvas = document.createElement('canvas');
  var img_ref = document.getElementById('wall-image')

  document.getElementById('wrapper').insertBefore(downloadCanvas, img_ref);

  downloadCanvas.id = "download-canvas";
  downloadCanvas.style.position = "absolute";
  downloadCanvas.style.left = img_ref.offsetLeft + "px";
  downloadCanvas.style.top = img_ref.offsetTop + "px";
  downloadCanvas.width = img_ref.offsetWidth;
  downloadCanvas.height = img_ref.offsetHeight;

  dcctx = downloadCanvas.getContext('2d');

  // load image on canvas
  var img_to_download = new Image();
  img_to_download.onload = function () {
    //draw background image
    clear(downloadCanvas, dcctx);
    dcctx.drawImage(img_to_download, 0, 0, downloadCanvas.width, downloadCanvas.height);
    // redraw each rect in the holds array
    for (var i = 0; i < holds.length; i++) {
      var hold = holds[i];
      // Draw circle
      dcctx.beginPath();
      dcctx.arc(hold.x * downloadCanvas.width, hold.y * downloadCanvas.height, hold.radius, 0, 2 * Math.PI, false);
      dcctx.lineWidth = 3;
      dcctx.strokeStyle = hold.color;
      dcctx.stroke();

    }

    var link = document.createElement('a');
    link.id = "download-a";
    link.download = boulder_name + ".png";
    link.href = document.getElementById('download-canvas').toDataURL()
    link.click();
    $("#download-canvas").remove();
    $("#download-a").remove();
  };

  img_to_download.src = image_wall;
}

function addHoldDetectionCallback(holdDetectionSwitchId) {
  // Add hold detection change callback
  var checkbox = document.getElementById(holdDetectionSwitchId);

  checkbox.addEventListener('change', (event) => {
    holdDetectionActive = event.currentTarget.checked;
    drawAll();
  });
}


function setCanvasAndPolygons(holdRadius, holdData, imageId, canvasId) {
  radius = holdRadius;
  var img = document.getElementById(imageId);
  var cnvs = document.getElementById(canvasId);

  cnvs.style.position = "absolute";
  cnvs.style.left = img.offsetLeft + "px";
  cnvs.style.top = img.offsetTop + "px";
  cnvs.width = img.offsetWidth;
  cnvs.height = img.offsetHeight;

  var ctx = cnvs.getContext("2d");
  ctx.width = cnvs.width;
  ctx.height = cnvs.height;
  if (holdDetectionActive) {
    fillCanvasWithGray(ctx, cnvs);
  }

  var wall_hold_data = holdData;
  var parsed_data = JSON.parse(wall_hold_data);
  polys = parsed_data.holds;
  ratio = img.offsetWidth / img.naturalWidth;
  for (let index = 0; index < polys.length; index++) {
    // Adjust ratio
    for (let i = 0; i < polys[index].length; i++) {
      polys[index][i][0] *= ratio;
      polys[index][i][1] *= ratio;
    }
  }
};

function boulderCreateInit(holdDetectionSwitchId, imageId, canvasId, holdRadius, holdData) {
  addHoldDetectionCallback(holdDetectionSwitchId);
  setCanvasAndPolygons(holdRadius, holdData, imageId, canvasId);

  var cnvs = document.getElementById(canvasId);

  // listen for mouse events
  cnvs.onmousedown = myDown;
  cnvs.onmouseup = myUp;
  cnvs.onmousemove = myMove;
};

function boulderLoadInit(holdDetectionSwitchId, imageId, canvasId, holdRadius, holdData) {
  addHoldDetectionCallback(holdDetectionSwitchId);
  setCanvasAndPolygons(holdRadius, holdData, imageId, canvasId);

  var cnvs = document.getElementById(canvasId);

  for (var i = 0; i < holds.length; i++) {
    holds[i].radius = radius * cnvs.width;
  }

  drawAll();
};

window.holds = holds;
window.polys = polys;
window.ratio = ratio;
window.dragok = dragok;
window.wasDragged = wasDragged;
window.radius = radius;
window.holdDetectionActive = holdDetectionActive;
window.boulderCreateInit = boulderCreateInit;
window.boulderLoadInit = boulderLoadInit;
window.hexToRGBA = hexToRGBA;
window.draw = draw;
window.fillCanvasWithGray = fillCanvasWithGray;
window.drawHold = drawHold;
window.clear = clear;
window.drawPolygon = drawPolygon;
window.drawAll = drawAll;
window.myDown = myDown;
window.myUp = myUp;
window.myMove = myMove;
window.undoMove = undoMove;
window.setHolds = setHolds;
window.validateForm = validateForm;
window.downloadProblem = downloadProblem;
