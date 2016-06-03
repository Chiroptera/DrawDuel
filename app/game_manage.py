from random import randint


class BattleRoom:
    def __init__(self, uuid, **kwargs):
        self.players = kwargs.get('players', {})
        self.uuid = uuid  # this is a string

        self.canvas = {}
        self.n_players = len(self.players)
        self.turn = 0

    def add_user(self, player):
        self.players[player] = False
        self.n_players = 1

    def remove_user(self, player):
        if player in self.players:
            del self.players[player]
            self.n_players -= 1

    def register(self, player, ws):
        if player in self.players:
            self.players[player] = ws

    def turn_end(self, user):
        self.current_player += 1
        if self.current_player >= self.n_players:
            self.current_player = 0

        self.turn += 1

    def ready(self):
        if self.n_players >= 2:
            self.current_player = randint(0, self.n_players - 1)
            return True
        return False

    def get_curr_player(self):
        ws = self.players[self.current_player]
        if ws:
            return ws
        else:
            raise Exception('Player not registered yet.')

    def add_point(self, point):
        self.canvas[self.turn].append(point)


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
