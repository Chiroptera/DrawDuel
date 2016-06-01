// http://www.williammalone.com/articles/create-html5-canvas-javascript-drawing-app/#demo-simple


var paint = false;
var maxPx = 50;
var countPx = 0;
var myTurn = false;

console.log('connecting to websocket in: ' + document.domain + ':' + location.port)

var socket = io('http://' + document.domain + ':' + location.port);
socket.on('connect', function(){
    console.log('registering...');
    socket.emit('register');
});
socket.on('event', function(data){});

socket.on('px2client', function(data){
    console.log(data);
    addClickServer(data.x, data.y, data.dragging)
    redraw();
});

socket.on('your_turn', function(){
    console.log('it\'s your turn now');
    myTurn = true;
    countPx = 0;
});

socket.on('disconnect', function(){});

context = document.getElementById('drawCanvas').getContext("2d");

$('#drawCanvas').mousedown(function(e){
  var mouseX = e.pageX - this.offsetLeft;
  var mouseY = e.pageY - this.offsetTop;

  paint = true;
  addClick(e.pageX - this.offsetLeft, e.pageY - this.offsetTop);
  redraw();
});

$('#drawCanvas').mousemove(function(e){
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

var clickX = new Array();
var clickY = new Array();
var clickDrag = new Array();
var paint;

function addClickServer(x, y, dragging)
{
  clickX.push(x);
  clickY.push(y);
  clickDrag.push(dragging);
}

function addClick(x, y, dragging)
{
  countPx += 1;
  if (!myTurn){
    return;
  }

  clickX.push(x);
  clickY.push(y);
  clickDrag.push(dragging);
  socket.emit('px2server', { x: x, y: y, dragging: dragging});

  if (countPx >= maxPx){
    socket.emit('im_done');
    myTurn = false;
  }
}

function redraw(){
  context.clearRect(0, 0, context.canvas.width, context.canvas.height); // Clears the canvas

  context.strokeStyle = "#df4b26";
  context.lineJoin = "round";
  context.lineWidth = 5 ;

  for(var i=0; i < clickX.length; i++) {
    context.beginPath();
    if(clickDrag[i] && i){
      context.moveTo(clickX[i-1], clickY[i-1]);
     }else{
       context.moveTo(clickX[i]-1, clickY[i]);
     }
     context.lineTo(clickX[i], clickY[i]);
     context.closePath();
     context.stroke();
  }
}