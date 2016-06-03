// http://www.williammalone.com/articles/create-html5-canvas-javascript-drawing-app/#demo-simple

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

/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 
                                GAME
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
var maxPx = 50;  // maximum pixels that the player can draw per turn
var countPx = 0;  // keep track of number of pixels drawn in current turn
var myTurn = false;

var clickX = new Array();
var clickY = new Array();
var clickDrag = new Array();
var paint;

var color = "#df4b26";
var line_join = "round";
var line_width = 5;

// receive points from server
socket.on('px2client', function(data){
    console.log(data);
    addClickServer(data.x, data.y, data.dragging)
    redraw();
});

socket.on('your_turn', function(){
    console.log('it\'s your turn now');
    $('#chat').append('<br>' + $('<div/>').text('It\'s your turn now.').html());
    myTurn = true;
    countPx = 0;
});

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


// draw points received from server
function addClickServer(x, y, dragging)
{
  clickX.push(x);
  clickY.push(y);
  clickDrag.push(dragging);
}


// draw points received locally
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
  // Clears the canvas
  context.clearRect(0, 0, context.canvas.width, context.canvas.height);

  context.strokeStyle = color;
  context.lineJoin = line_join;
  context.lineWidth = line_width;

  for(var i=0; i < clickX.length; i++) {
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