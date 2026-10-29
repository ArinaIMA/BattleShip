from models.player import HumanPlayer, AIPlayer, Player
from models.game import Game
from models.grid import ShotResult

class GameController:
    def __init__(self):
        self.is_running = True
        self.main_window = None
        self.is_with_ai = False
        self.is_waiting_for_turn_end = False
        self.is_waiting_for_ai = False

    def set_main_window(self, window):
        """Связываем контроллер с окном"""
        self.main_window = window

    def start_game_vs_human(self):
        self.is_with_ai = False
        p1 = HumanPlayer("Игрок 1")
        p2 = HumanPlayer("Игрок 2")
        ships_config = [
            {'size': 4, 'count': 1},
            {'size': 3, 'count': 2},
            {'size': 2, 'count': 3},
            {'size': 1, 'count': 4},
        ]
        self._start_game(p1, p2, ships_config)

    def start_game_vs_ai(self):
        self.is_with_ai = True
        p1 = HumanPlayer("Игрок 1")
        p2 = AIPlayer("Компьютер", strategy="smart")
        ships_config = [
            {'size': 4, 'count': 1},
            {'size': 3, 'count': 2},
            {'size': 2, 'count': 3},
            {'size': 1, 'count': 4},
        ]
        self._start_game(p1, p2, ships_config)

    def _start_game(self, p1, p2, ships_config):
        self.game = Game(p1, p2, ships_config)

        # Расстановка
        self._place_ships()

        # Переход к экрану игры
        if not self.is_with_ai:
            self.is_waiting_for_turn_end = True
            self.main_window.show_handoff_screen(
                next_player_name=self.game.current_player.name,
                on_ready=self._on_handoff_ready,
            )
            return

        self._refresh_game_screen()

    def _place_ships(self):
        self.game.place_ships_randomly()

    def _refresh_game_screen(self):
        if self.is_with_ai:
            self._show_game_screen(self.game.player1, self.game.player2)
        else:
            self._show_game_screen(self.game.current_player, self.game.opponent)

    def _show_game_screen(self, current, opponent):
        self.main_window.show_game_screen(
            own_name=current.name,
            own_grid=current.grid,  # тут видны СВОИ корабли
            enemy_name=opponent.name,
            enemy_grid=current.opponent_grid,  # тут корабли СКРЫТЫ
        )

    def on_cell_click(self, row, col):
        if self.is_waiting_for_turn_end or self.is_waiting_for_ai:
            return
        if self.game is None or self.game.is_over:
            return

        outcome = self.game.make_shot(row, col)
        if outcome is None:
            return
        if outcome["result"] in (ShotResult.ALREADY_SHOT, ShotResult.INVALID):
            return

        self.is_waiting_for_turn_end = True
        self._refresh_game_screen() # первый игрок видит результат выстрела
        self.main_window.root.after(300, lambda: self._finish_turn(outcome))

    def _finish_turn(self, outcome):
        """Вызывается через after — здесь уже безопасно менять ход и перерисовывать."""
        self.game.end_turn(outcome)

        if self.game.is_over:
            self.main_window.show_game_over(self.game.winner.name)
            self.is_waiting_for_turn_end = False
            return

        turn_switched = (outcome["result"] == ShotResult.MISS)

        if not self.is_with_ai and turn_switched:
            self.is_waiting_for_turn_end = True
            self.main_window.show_handoff_screen(
                next_player_name=self.game.current_player.name,
                on_ready=self._on_handoff_ready,
            )
            return

        self._refresh_game_screen()
        self.is_waiting_for_turn_end = False

        if self.is_with_ai and self.game.current_player.name == "Компьютер":
            self._ai_turn()

    def _on_handoff_ready(self):
        self._refresh_game_screen()
        self.is_waiting_for_turn_end = False

    def _ai_turn(self):
        if self.game is None or self.game.is_over:
            return

        # Небольшая задержка, чтобы игрок увидел, что произошло
        self.main_window.root.after(300, self._ai_make_one_shot)

    def _ai_make_one_shot(self):
        self.is_waiting_for_ai = True

        ai = self.game.current_player
        if type(ai) is not AIPlayer:
            self.is_waiting_for_ai = False
            return  # ход уже не у AI (например, промахнулся и передал ход)

        outcome = self.game.make_shot()
        self.game.end_turn(outcome)
        if self.game.is_over:
            self.main_window.show_game_over(self.game.winner.name)
            self.is_waiting_for_ai = False
            return

        self._refresh_game_screen()
        self.main_window.root.after(300, self._ai_make_one_shot)

    def on_exit(self):
        """Обработчик закрытия приложения"""
        print("Выход из игры")
        if self.main_window:
            self.main_window.close()  # Закрываем окно
        self.is_running = False

    def on_click(self, x, y):
        """Заглушка для обработки кликов (пока не используется)"""
        print(f"Клик по координатам: ({x}, {y})")

    def reset_game(self):
        """Полный сброс текущей партии."""
        self.game = None
        self.is_waiting_for_turn_end = False
        self.is_waiting_for_ai = False