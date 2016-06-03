from flask import Flask, render_template, request, session, flash, redirect,\
                  url_for
from flask_socketio import SocketIO, emit

import uuid
import logging

from game_manage import User, BattleRoom
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                     LOGGING SETUP
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('app.log')
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

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                           APP SETUP
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.logger.addHandler(ch)
app.logger.addHandler(fh)
# FlaskSession.Session(app)
# FlaskSession.init_app(app)
socketio = SocketIO(app, logger=logger)


canvasCount = 0
currentDrawing = list()
canvas = {0: currentDrawing}

users = dict()
battle_rooms = dict()
waiting_rooms = list()


@app.route('/')
def index():
    track_user()
    return render_template('frontpage.html')


@app.route('/create_battleroom')
def create_battleroom():
    # add user to battle id
    track_user()
    new_room_uuid = uuid.uuid4().hex
    battle_rooms[new_room_uuid] = BattleRoom(new_room_uuid)
    logger.debug('created battleroom: {}'.format(new_room_uuid))
    return redirect('/battle_room/{}'.format(new_room_uuid))


@app.route('/test')
def test():
    return redirect(url_for('index'))


@app.route('/find_opponent')
def find_opponent():
    logger.debug('find oponent not implemented yet')
    return redirect(url_for('index'))


@app.route('/battle_room/<battle_id>')
def battle_room(battle_id):
    curr_user = track_user()

    if not curr_user:
        logger.debug('user not tracked yet, redirecting to main page')
        return redirect(url_for('index'))

    curr_battleroom = battle_rooms.get(battle_id)
    print('curr battlerrom: ', curr_battleroom)
    if not curr_battleroom:
        logger.debug('battleroom doesn\'t exist , redirecting to main page')
        return redirect(url_for('index'))

    # users[user] = battle_id
    curr_battleroom.add_user(curr_user)

    return render_template('canvas_room.html')


@app.route('/set_username')
def set_username():
    track_user()
    session['username'] = request.form['username']
    users[session['uuid']].username = request.form['username']


def load_user():
    if 'uuid' not in session:
        return None
    return users.get(session['uuid'], None)


def track_user():
    user_uuid = session.get('uuid')
    if not user_uuid:
        user_uuid = uuid.uuid4().hex
        session['uuid'] = user_uuid

    user = users.get(user_uuid)
    if not user:
        user = User(user_uuid)
        users[user_uuid] = user

    logger.debug('user being tracked: {}'.format(user.uuid))

    return user

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                      CANVAS WEBSOCKET
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


@socketio.on('disconnect')
def disconnected():
    logger.debug('User websocket disconnected. User uuid: {}'.format(session['uuid']))
    # clients.remove(request.sid)


@socketio.on('register')
def register_client(message):

    logger.debug('user registered; user: {}  sid: {}'.format(session['uuid'], request.sid))

    curr_user = load_user()
    if not curr_user:
        logger.debug('user not tracked yet, redirecting to main page')
        return redirect(url_for('index'))

    curr_battleroom = battle_rooms.get(message['battleroom'])
    if not curr_battleroom:
        logger.debug('battleroom doesn\'t exist , redirecting to main page')
        return redirect(url_for('index'))

    curr_user.register(curr_battleroom.uuid, request.sid)
    curr_battleroom.register(curr_user.uuid, request.sid)

    if curr_battleroom.ready():
        socketio.emit('your_turn', room=curr_battleroom.get_curr_player())
    else:
        socketio.emit('server message', {'msg': u'Waiting for another player...'},
                      room=request.sid)


@socketio.on('im_done')
def change_client(msg):
    curr_user = load_user()
    if not curr_user:
        logger.debug('user not tracked yet, redirecting to main page')
        return redirect(url_for('index'))

    curr_battleroom = battle_rooms.get(msg['battleroom'])
    if not curr_battleroom:
        logger.debug('battleroom doesn\'t exist , redirecting to main page')
        return redirect(url_for('index'))

    logger.debug('client done: {}'.format(request.sid))

    curr_battleroom

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
