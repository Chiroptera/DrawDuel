from flask import render_template, request, session, flash, redirect, url_for
from flask_socketio import SocketIO, emit

import uuid

from app import app, logger

from .game_manage import User, BattleRoom

socketio = SocketIO(app, logger=logger)

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
    newBR = BattleRoom()
    battle_rooms[newBR.uuid] = newBR
    logger.debug('created battleroom: {}'.format(newBR.uuid))
    return redirect('/battle_room/{}'.format(newBR.uuid))


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
        # return redirect(url_for('index'))

    curr_battleroom = battle_rooms.get(battle_id)
    if not curr_battleroom:
        logger.debug('battleroom doesn\'t exist , redirecting to main page')
        return redirect(url_for('index'))

    # users[user] = battle_id
    logger.debug('added user {} to battleroom {}'.format(curr_user.uuid,
                                                         curr_battleroom.uuid))

    if curr_battleroom.add_user(curr_user.uuid):
        return render_template('canvas_room.html', canvas_width=800,
                                                   canvas_height=500)

    return redirect(url_for('index'))


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


def server_message(recipient, msg):
    socketio.emit('server message', {'msg': str(msg)},
                  room=recipient)


@socketio.on('register')
def register_client(message):
    logger.debug('user registered; user: {}  sid: {}'.format(session['uuid'], request.sid))

    curr_user = load_user()
    if not curr_user:
        logger.debug('user not tracked yet, redirecting to main page')
        socketio.emit('expired', room=request.sid)
        return

    curr_battleroom = battle_rooms.get(message['battleroom'])
    if not curr_battleroom:
        logger.debug('battleroom doesn\'t exist , redirecting to main page')
        socketio.emit('expired', room=request.sid)
        return

    if not curr_battleroom.register(curr_user.uuid, request.sid):
        logger.debug('user not in battleroom')
        socketio.emit('expired', room=request.sid)
        return

    curr_user.register(curr_battleroom.uuid, request.sid)

    # send all pixels in canvas to registered client
    # for turn, points in curr_battleroom.canvas.items():
    #     for point in points:
    #         msg = {'x': point[0], 'y': point[1], 'dragging': point[2]}
    #         socketio.emit('px2client', msg, room=request.sid)

    logger.debug('battle room type: {}'.format(type(curr_battleroom)))
    for point in curr_battleroom:
        socketio.emit('px2client', point.make_message(), room=request.sid)

    if curr_battleroom.ready():
        logger.debug('battleroom ready, current player: {}'.format(curr_battleroom.current_player))
        try:
            socketio.emit('your_turn', room=curr_battleroom.get_curr_player_ws())
        except:
            logger.debug('\n\n\nyour turn failed; current_player: {}\n\n\n'.format(curr_battleroom.current_player))

    else:
        server_message(request.sid, 'Waiting for players...')


@socketio.on('im_done')
def change_client(message):
    curr_user = load_user()
    if not curr_user:
        logger.debug('user not tracked yet, redirecting to main page')
        socketio.emit('expired', room=request.sid)
        return

    curr_battleroom = battle_rooms.get(message['battleroom'])
    if not curr_battleroom:
        logger.debug('battleroom doesn\'t exist , redirecting to main page')
        socketio.emit('expired', room=request.sid)
        return

    logger.debug('player done: user: {}   sid: {}'.format(curr_user.uuid,
                                                          request.sid))

    curr_battleroom.turn_end()
    socketio.emit('your_turn', room=curr_battleroom.get_curr_player_ws())


def find_battleroom_of_ws(ws):
    for br in battle_rooms.values():
        if ws in br.all_ws():
            return br


@socketio.on('px2server')
def recv_pixels(msg):
    logger.debug('got pixel: {}'.format(msg))

    BR = find_battleroom_of_ws(request.sid)
    # BR.add_point((msg['x'], msg['y'], msg.get('dragging', False), msg['color'],
    #               msg['line_width']))
    BR.add_message_point(msg)

    for ws in BR.all_ws():
        if ws != request.sid:
            socketio.emit('px2client', msg, room=ws)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
