from random import randint
import uuid


class BattleRoom:
    def __init__(self, **kwargs):

        self.uuid = uuid.uuid4().hex  # this is a string

        self.canvas = {0: []}
        self.turn = 0

        self.players = []
        self.n_players = 0

        self.players_ws = {}

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
        if len(self.players_ws) == 2:
            self.current_player = randint(0, len(self.players_ws) - 1)
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
