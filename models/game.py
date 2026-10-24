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

    def make_shot(self, row=None, col=None):
        if self.is_over:
            return None

        shooter = self.current_player
        target = self.opponent

        if isinstance(shooter, AIPlayer):
            result, row, col = shooter.make_shot()
        else:
            result = shooter.make_shot(row, col)

        return {
            "result": result,
            "shooter": shooter,
            "target": target,
            "row": row,
            "col": col,
        }

    def end_turn(self, outcome):
        """Фиксирует последствия выстрела: смена хода, победа."""
        result = outcome["result"]
        if result in (ShotResult.ALREADY_SHOT, ShotResult.INVALID):
            return
        target = outcome["target"]

        if target.has_lost():
            self.is_over = True
            self.winner = outcome["shooter"]
            return

        # Ход переходит только при промахе
        if result == ShotResult.MISS:
            self.switch_turn()

    def switch_turn(self):
        self.current_player = (
            self.player2 if self.current_player is self.player1 else self.player1
        )

    @property
    def opponent(self):
        return self.player2 if self.current_player is self.player1 else self.player1