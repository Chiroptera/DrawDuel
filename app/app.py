from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

from random import choice

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

canvasCount = 0
currentDrawing = list()
canvas = {0: currentDrawing}
clients = list()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('disconnect')
def disconnected():
    print('client disconnected: ', request.sid)
    clients.remove(request.sid)

@socketio.on('register')
def register_client():
    clients.append(request.sid)

    print('client registered: ', request.sid)
    if len(clients) > 1:
        print('first client chosen: ', request.sid)
        chosenClient = choice(clients)
        socketio.emit('your_turn', room=chosenClient)

@socketio.on('im_done')
def change_client():
    global canvasCount
    otherClient = choice([c for c in clients if c != request.sid])
    socketio.emit('your_turn', room=otherClient)

    canvasCount += 1
    currentDrawing = list()
    canvas[canvasCount] = currentDrawing

    print('client done: ', request.sid)

@socketio.on('px2server')
def recv_pixels(msg):
    print('got pixel: ', msg)
    currentDrawing.append((msg['x'], msg['y'], msg.get('dragging', False)))

    # print('gonna choose from: ', clients)
    otherClients = [c for c in clients if c != request.sid]
    for client in otherClients:
        socketio.emit('px2client', msg, room=client)

if __name__ == '__main__':
    socketio.run(app)
