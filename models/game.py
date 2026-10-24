from models.player import HumanPlayer, AIPlayer
from models.grid import ShotResult


class Game:
    """Модель одной партии. Правила, состояние, победа."""

    def __init__(self, player1, player2, ships_config):
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.ships_config = ships_config
        self.is_over = False
        self.winner = None

        # Связываем сетки: каждый игрок «видит» поле противника
        player1.set_opponent_grid(player2.grid)
        player2.set_opponent_grid(player1.grid)

    def place_ships_randomly(self):
        """Расставляет корабли обоим игрокам"""
        self.player1.place_ships_random(self.ships_config)
        self.player2.place_ships_random(self.ships_config)

    def make_shot(self, row, col):
        return self.current_player.make_shot(row, col)


