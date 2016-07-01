// http://www.williammalone.com/articles/create-html5-canvas-javascript-drawing-app/#demo-simple
//touch events rom:
// https://software.intel.com/en-us/xdk/article/touch-drawing-app-using-html5-canvas

/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
                                GAME
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
var maxPx = 50;  // maximum pixels that the player can draw per turn
var countPx = 0;  // keep track of number of pixels drawn in current turn
var myTurn = false;

var clickX = new Array();
var clickY = new Array();
var clickDrag = new Array();
var clickColor = new Array();
var clickLineWidth = new Array()
var paint;



var bgcolor = "#ffffff"
var color = "#000000";
var line_join = "round";
var line_width = 5;

function setDrawColor(fcolor) {
  color = '#' + fcolor;
  console.log('changed color to ' + color);
}


// we use the document.ready so that no code is executed before the page is loaded
$(document).ready(function(){

var battleroom = location.pathname.match(/([^\/]*)\/*$/)[1];
console.log('battleroom: ' + battleroom);


/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
                                MANAGE
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
console.log('connecting to websocket in: ' + document.domain + ':' + location.port);
var socket = io('http://' + document.domain + ':' + location.port);

socket.on('connect', function(){
    console.log('connected. registering...');
    $('#chat').append('<br>' + $('<div/>').text('Connected. Registering...').html());
    socket.emit('register', {battleroom: battleroom});
});

socket.on('server message', function(data){
  $('#chat').append('<br> <font color="red">' + $('</font><div/>').text(data.msg).html());
});

socket.on('disconnect', function(){
  console.log('disconnected.');
  $('#chat').append('<br>' + $('<div/>').text('Disconnected...').html());
});

socket.on('expired', function(){
  console.log('battleroom expired. reloading page...');
  location.reload();
});

/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
                                GAME
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */


// receive points from server
socket.on('px2client', function(data){
    console.log(data);
    addClickServer(data.x, data.y, data.c, data.lw, data.d)
    redraw();
});

socket.on('your_turn', function(){
    console.log('it\'s your turn now');
    $('#chat').append('<br>' + $('<div/>').text('It\'s your turn now.').html());
    myTurn = true;
    countPx = 0;
});

context = document.getElementById('drawCanvas').getContext("2d");

/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
                                MOUSE FUNCTIONS
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

$('#drawCanvas').mousedown(function(e){
  if (!myTurn){
    return;
  }

  var mouseX = e.pageX - this.offsetLeft;
  var mouseY = e.pageY - this.offsetTop;

  paint = true;
  addClick(mouseX, mouseY);
  redraw();
});

$('#drawCanvas').mousemove(function(e){
  if (!myTurn){
    return;
  }

  if(paint){
    addClick(e.pageX - this.offsetLeft, e.pageY - this.offsetTop, true);
    redraw();
  }
});

$('#drawCanvas').mouseup(function(e){
  paint = false;
});

$('#drawCanvas').mouseleave(function(e){
  paint = false;
});

/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
                                TOUCH FUNCTIONS
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
// $('#drawCanvas').touchstart(function(e){
//   var mouseX = e.originalEvent.touches[0].pageX - this.offsetLeft;
//   var mouseY = e.originalEvent.touches[0].pageY - this.offsetTop;

//   paint = true;
//   addClick(mouseX, mouseY);
//   redraw();
// });

// $('#drawCanvas').touchmove(function(e){
//   if(paint){
//     var mouseX = e.originalEvent.touches[0].pageX - this.offsetLeft;
//     var mouseY = e.originalEvent.touches[0].pageY - this.offsetTop;
//     addClick(mouseX, mouseY, true);
//     redraw();
//   }
// });

// $('#drawCanvas').touchend(function(e){
//   paint = false;
// });

// $('#drawCanvas').touchleave(function(e){
//   paint = false;
// });

/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
                                DRAWING FUNCTIONS
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

// draw points received from server
function addClickServer(x, y, c, lw, dragging)
{
  clickX.push(x);
  clickY.push(y);
  clickDrag.push(dragging);
  clickColor.push(c);
  clickLineWidth.push(lw);
}

/*
   Given a starting point p1 and a destination point p2, this function will
   return a third point p3 that lies between p1 and p2 but whose distance from
   p1 is approximetaly t.
           p3 = 1 + e * (p2 - p1)
           e = t / dist(p1, p2)
*/
function closest_point(p1, p2, t) {
  var v = {x: p2.x - p1.x, y: p2.y - p1.y};
  var d = Math.sqrt(Math.pow((p2.x - p1.x), 2) + Math.pow((p2.y - p1.y), 2));
  var e = 1.0;
  if (d > t) e = t / d;
  var p3 = {x: Math.ceil( p1.x + e * v.x ), y: Math.ceil( p1.y + e * v.y ), len: Math.ceil( e * d )};
  console.log(p1);
  console.log(p2);
  console.log(d);
  console.log(p3);
  return p3;
}

// draw points received locally
function addClick(x, y, dragging)
{
  if (!myTurn){
    return;
  }

  if (dragging) {
    var lx = clickX[clickX.length - 1];
    var ly = clickY[clickY.length - 1];
    var cp = closest_point({x:lx, y:ly}, {x:x, y:y}, countPx);
    console.log(cp);
    x = cp.x;
    y = cp.y;
    countPx += cp.len - 1;
  }

  countPx += 1;

  clickX.push(x);
  clickY.push(y);
  clickDrag.push(dragging);
  clickColor.push(color);
  clickLineWidth.push(line_width);
  socket.emit('px2server', { x: x, y: y, d: dragging, c: color, lw: line_width});

  if (countPx >= maxPx){
    socket.emit('im_done', {battleroom: battleroom});
    myTurn = false;
  }
}


function redraw(){
  // Clears the canvas
  context.clearRect(0, 0, context.canvas.width, context.canvas.height);
  context.lineJoin = line_join;

  for(var i=0; i < clickX.length; i++) {
    context.strokeStyle = clickColor[i];
    context.lineWidth = clickLineWidth[i];

    context.beginPath();
    if(clickDrag[i] && i){
      context.moveTo(clickX[i-1], clickY[i-1]);
    } else {
       context.moveTo(clickX[i]-1, clickY[i]);
    }
     context.lineTo(clickX[i], clickY[i]);
     context.closePath();
     context.stroke();
  }
}

});
