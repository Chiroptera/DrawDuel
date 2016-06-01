from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import uuid
from random import choice
import logging

logger = logging.getLogger('simple_example')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('spam.log')
fh.setLevel(logging.INFO)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

canvasCount = 0
currentDrawing = list()
canvas = {0: currentDrawing}

current_client = 0
clients = list()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_uuid')
def get_uuid():
    return uuid.uuid4().get_hex()


@socketio.on('disconnect')
def disconnected():
    global current_client
    logger.debug('Client disconnected. Number of clients: {}'.format(len(clients)))
    clients.remove(request.sid)

    if current_client >= len(clients):
        current_client -= 1


@socketio.on('register')
def register_client():
    global current_client

    logger.debug('client registered: {}'.format(request.sid))

    clients.append(request.sid)

    logger.debug('Client registered. Number of clients: {}'.format(len(clients)))

    if len(clients) == 2:
        chosenClient = clients[current_client]
        socketio.emit('your_turn', room=chosenClient)


@socketio.on('im_done')
def change_client():
    global canvasCount, current_client

    logger.debug('client done: {}'.format(request.sid))

    current_client += 1
    if current_client >= len(clients):
        current_client = 0

    logger.debug('current client: {}'.format(current_client))
    logger.debug('clients len: {}'.format(len(clients)))
    nextClient = clients[current_client]
    socketio.emit('your_turn', room=nextClient)

    canvasCount += 1
    currentDrawing = list()
    canvas[canvasCount] = currentDrawing


@socketio.on('px2server')
def recv_pixels(msg):
    logger.debug('got pixel: {}'.format(msg))
    currentDrawing.append((msg['x'], msg['y'], msg.get('dragging', False)))

    otherClients = [c for c in clients if c != request.sid]
    for client in otherClients:
        socketio.emit('px2client', msg, room=client)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
