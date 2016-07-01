from random import randint
import uuid
import time


class DrawPoint:
    def __init__(self, **kwargs):
        '''
        x,y : cartesian coordinates of the point
        d   : dragging
        c   : color
        lw  : line width'''
        msg = kwargs.get('message')
        if msg:
            self.parse_message_point(msg)
        else:
            self.x = kwargs.get('x')
            self.y = kwargs.get('y')
            self.d = kwargs.get('dragging')
            self.c = kwargs.get('color')
            self.lw = kwargs.get('lw')

        if not self.x or not self.y or not self.d or not self.c or not self.lw:
            raise ValueError("all parameters of a point must be provided")

    def parse_message_point(self, msg):
        self.x = msg['x']
        self.y = msg['y']
        self.d = msg.get('d', False)
        self.c = msg['c']
        self.lw = msg['lw']

    def make_message(self):
        return {'x': self.x, 'y': self.y, 'd': self.d,
                'c': self.c, 'lw': self.lw}



class BattleRoom:
    def __init__(self, **kwargs):

        self.uuid = uuid.uuid4().hex  # this is a string

        self.canvas = {0: []}
        self.turn = 0

        self.players = []
        self.n_players = 0

        self.players_ws = {}

        self.started = False

        self.last_visited = time.time()

    def is_full(self):
        if self.n_players == 2:
            return True
        return False

    def all_ws(self):
        return self.players_ws.values()

    def add_user(self, user):

        if user in self.players:
            return True

        if self.n_players < 2:
            self.players_ws[user] = False
            self.players.append(user)
            self.n_players += 1
            return True

        return False

    def remove_user(self, player):
        if player in self.players:
            del self.players[player]
            self.players.remove(player)
            self.n_players -= 1
            return True
        return False

    def register(self, player, ws):
        if player in self.players:
            self.last_visited = time.time()
            self.players_ws[player] = ws
            return True
        return False

    def turn_end(self):
        self.current_player += 1
        if self.current_player >= self.n_players:
            self.current_player = 0

        self.turn += 1
        self.canvas[self.turn] = []

    def ready(self):
        if self.started:
            return True
        if len(self.players_ws) == 2:
            self.current_player = randint(0, len(self.players_ws) - 1)
            self.started = True
            return True
        return False

    def get_curr_player_ws(self):
        ws = self.players_ws[self.players[self.current_player]]
        if ws:
            return ws
        else:
            raise Exception('Player not registered yet.')

    def add_point(self, point):
        self.canvas[self.turn].append(point)

    def add_message_point(self, msg):
        point = DrawPoint(message=msg)
        self.canvas[self.turn].append(point)

    def __iter__(self):
        self._turn = iter(self.canvas.values())
        self._point = iter(next(self._turn))
        return self

    def __next__(self):
        while True:
            try:
                result = next(self._point)
            except StopIteration:
                self._point = iter(next(self._turn))
                continue
            return result



        # if self._point >= len(self.canvas[self._turn]):
        #     self._turn += 1
        #     self._point = 0
        #
        # if self._turn > max(self.canvas):
        #     raise StopIteration
        #
        # print(self._point, len(self.canvas[self._turn]))
        # result = self.canvas[self._turn][self._point]
        # self._point += 1
        # return result



class User:
    def __init__(self, uuid, **kwargs):
        self.username = kwargs.get('username', None)
        self.battlerooms = {}
        self.uuid = uuid

    def join_battleroom(self, battleroom):
        self.battlerooms[battleroom] = None

    def register(self, br, websocket):
        if br in self.battlerooms:
            self.battlerooms[br] = websocket
