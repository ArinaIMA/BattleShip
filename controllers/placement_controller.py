from models.player import HumanPlayer, AIPlayer
from views.ship_placer import ShipPlacer


class PlacementController:
    """
    Расстановка кораблей для обоих игроков.

    Сценарий:
      - создаём игроков с пустыми сетками;
      - Игрок 1 расставляет вручную (кл. ShipPlacer);
      - если режим с AI — AI расставляется случайно, второй ShipPlacer не нужен;
      - иначе: экран передачи, после которого Игрок 2 может расставлять корабли;
      - по завершении вызывается on_complete(player1, player2),
        и GameController создаёт Game.
    """

    def __init__(self, main_window, game_controller):
        self.main_window = main_window
        self.game_controller = game_controller

        self.ships_config = None
        self.is_with_ai = False
        self.on_complete = None

        self.player1 = None
        self.player2 = None

    # ---------- точка входа ----------

    def start(self, ships_config, is_with_ai, on_complete):
        """
        on_complete  — callback(player1, player2), вызывается после расстановки обоих
        """
        self.ships_config = ships_config
        self.is_with_ai = is_with_ai
        self.on_complete = on_complete

        self.player1 = HumanPlayer("Игрок 1")
        if is_with_ai:
            self.player2 = AIPlayer("Компьютер", strategy="smart")
            # AI расставляется случайно сразу
            self.player2.place_ships_random(ships_config)
        else:
            self.player2 = HumanPlayer("Игрок 2")

        self._show_placer_for(self.player1)

    # ---------- экраны ----------

    def _show_placer_for(self, player):
        self.main_window.clear_content()

        placer = ShipPlacer(
            self.main_window.content_frame,
            player=player,
            ships_config=self.ships_config,
            on_ready=lambda: self._on_player_ready(player),
            on_cancel=self._on_cancel,
            bg=self.main_window.content_frame.cget("bg"),
        )
        placer.pack(expand=True, fill="both")

    def _on_player_ready(self, player):
        """Игрок закончил ручную расстановку"""
        if player is self.player1 and not self.is_with_ai:
            # Между двумя людьми — экран «Передайте устройство»
            self.main_window.show_handoff_screen(
                next_player_name=self.player2.name,
                on_ready=self._on_handoff_ready,
            )
            return

        # Либо это Игрок 2, либо режим с AI — расстановка закончена
        self._finish()

    def _on_handoff_ready(self):
        """Нажали «Готов» на экране передачи устройства — начинаем расстановку Игрока 2"""
        self._show_placer_for(self.player2)

    def _finish(self):
        """Оба игрока расставились — передаём управление в GameController"""
        if self.on_complete:
            self.on_complete(self.player1, self.player2)

    # ---------- отмена ----------

    def _on_cancel(self):
        """Кнопка «Назад» на экране расстановки — возврат в меню и сброс партии"""
        self.game_controller.reset_game()
        self.main_window.start_menu_widgets()