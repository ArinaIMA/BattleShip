import pytest

from controllers.game_controller import GameController
from views.main_window import MainWindow
from models.game import Game
from models.player import Player, AIPlayer
from models.ship import Ship

class TestAi:
    def test_smart_vs_silly(self):
        gc = GameController()
        app = MainWindow(gc)  # класс, отвечающий за отрисовку
        gc.set_main_window(app)

        p1 = AIPlayer("Умник", strategy="smart")
        p2 = AIPlayer("Глупыш", strategy="silly")

        gc._start_game(p1, p2)

        while not gc.game.is_over:
            outcome = gc.game.make_shot()
            gc.game.end_turn(outcome)

        assert gc.game.winner == p1



