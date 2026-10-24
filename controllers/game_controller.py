from models.player import HumanPlayer, AIPlayer
from models.game import Game

class GameController:
    def __init__(self):
        self.is_running = True
        self.main_window = None
        self.is_with_ai = False

    def set_main_window(self, window):
        """Связываем контроллер с окном"""
        self.main_window = window

    def start_game_vs_human(self):
        self.is_with_ai = False
        self._start_game()

    def start_game_vs_ai(self):
        self.is_with_ai = True
        self._start_game()

    def _start_game(self):
        p1 = HumanPlayer("Игрок 1")
        p2 = HumanPlayer("Игрок 2") if not self.is_with_ai else AIPlayer("Компьютер", strategy="smart")

        ships_config = [
            {'size': 4, 'count': 1},
            {'size': 3, 'count': 2},
            {'size': 2, 'count': 3},
            {'size': 1, 'count': 4},
        ]
        self.game = Game(p1, p2, ships_config)

        # Расстановка
        self._place_ships()

        # Переход к экрану игры
        self._refresh_game_screen()

    def _place_ships(self):
        self.game.place_ships_randomly()

    def _refresh_game_screen(self):
        current = self.game.current_player
        opponent = self.game.player2 if current is self.game.player1 else self.game.player1
        self.main_window.show_game_screen(
            own_name=current.name,
            own_grid=current.grid,  # тут видны СВОИ корабли
            enemy_name=opponent.name,
            enemy_grid=current.opponent_grid,  # тут корабли СКРЫТЫ
            is_my_turn=True,
        )

    def on_cell_click(self):
        pass

    def on_exit(self):
        """Обработчик закрытия приложения"""
        print("Выход из игры")
        if self.main_window:
            self.main_window.close()  # Закрываем окно
        self.is_running = False

    def on_click(self, x, y):
        """Заглушка для обработки кликов (пока не используется)"""
        print(f"Клик по координатам: ({x}, {y})")