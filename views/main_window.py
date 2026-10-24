import tkinter as tk
from config import WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, BACKGROUND_COLOR
from views.board_view import BoardView


class MainWindow:
    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()

        # Настройка окна
        self.root.title(WINDOW_TITLE) # название окна
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}") # размеры окна
        self.root.configure(bg=BACKGROUND_COLOR) # цвет фона

        # Содержимое текущего окна
        self.content_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        self.content_frame.pack(fill="both", expand=True)

        # Создание интерфейса
        self.start_menu_widgets()

    def start_menu_widgets(self):
        self.clear_content()

        # Контейнер по центру экрана
        center = tk.Frame(self.content_frame, bg=BACKGROUND_COLOR)
        center.place(relx=0.5, rely=0.5, anchor="center")

        # Заголовок - надпись
        title_label = tk.Label(
            center,
            text="Морской бой",
            font=("Arial", 24, "bold"),
            bg=BACKGROUND_COLOR
        )
        title_label.pack(pady=20)

        # Кнопка начала игры
        start_button = tk.Button(
            center,
            text="Новая игра",
            command=self._choose_enemy,
            font=("Arial", 12),
            width=20
        )
        start_button.pack(pady=10)

        # Кнопка выхода
        exit_button = tk.Button(
            center,
            text="Выход",
            command=self.controller.on_exit,
            font=("Arial", 12),
            width=20
        )
        exit_button.pack(pady=10)

        # Метка информации
        self.info_label = tk.Label(
            center,
            text="Добро пожаловать в игру!",
            font=("Arial", 14),
            bg=BACKGROUND_COLOR
        )
        self.info_label.pack(pady=20)

    def _choose_enemy(self):
        self.clear_content()

        # Контейнер по центру экрана
        center = tk.Frame(self.content_frame, bg=BACKGROUND_COLOR)
        center.place(relx=0.5, rely=0.5, anchor="center")

        # Заголовок - надпись
        title_label = tk.Label(
            center,
            text="Выберите противника",
            font=("Arial", 24, "bold"),
            bg=BACKGROUND_COLOR
        )
        title_label.pack(pady=20)

        # Горизонтальный контейнер для двух кнопок
        buttons_row = tk.Frame(center, bg=BACKGROUND_COLOR)
        buttons_row.pack(pady=30)

        # Кнопка Игрок против Игрока
        human_button = tk.Button(
            buttons_row,
            text="Human",
            command=self.controller.start_game_vs_human,
            font=("Arial", 12),
            width=20
        )
        human_button.pack(side="left", padx=10)

        # Кнопка Игрок против Компьютера
        ai_button = tk.Button(
            buttons_row,
            text="Компьютер",
            command=self.controller.start_game_vs_ai,
            font=("Arial", 12),
            width=20
        )
        ai_button.pack(side="left", padx=10)

        # Кнопка выхода
        exit_button = tk.Button(
            center,
            text="Назад",
            command=self.start_menu_widgets,
            font=("Arial", 12),
            width=20,
            bg="lightgray",
            fg="black",
            activebackground="gray"
        )
        exit_button.pack(pady=20)

    def show_game_screen(self, own_name, own_grid, enemy_name, enemy_grid):
        self.clear_content()

        # Заголовок с именами
        title = tk.Label(
            self.content_frame,
            text=f"{own_name}  vs  {enemy_name}",
            font=("Arial", 16, "bold"),
            bg=BACKGROUND_COLOR
        )
        title.pack(pady=10)

        # Контейнер с двумя полями
        boards = tk.Frame(
            self.content_frame,
            bg=BACKGROUND_COLOR
        )
        boards.pack(expand=True)

        # Своё поле (корабли видны, клик не нужен)
        self.own_board = BoardView(
            boards, own_grid,
            mode="own",
            on_cell_click=None,
            bg=BACKGROUND_COLOR
        )
        self.own_board.pack(side="left", padx=20)

        # Поле противника (корабли скрыты, клик = выстрел)
        self.enemy_board = BoardView(
            boards, enemy_grid,
            mode="enemy",
            on_cell_click=self.controller.on_cell_click,
            bg=BACKGROUND_COLOR,
        )
        self.enemy_board.pack(side="left", padx=20)

    def show_handoff_screen(self, next_player_name, on_ready):
        """
        Экран «передайте устройство».
        on_ready — callback, вызывается по кнопке «Готов».
        """
        self.clear_content()

        center = tk.Frame(
            self.content_frame,
            bg=BACKGROUND_COLOR)
        center.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(center, text="Передайте устройство",
                 font=("Arial", 20, "bold"), bg=BACKGROUND_COLOR).pack(pady=20)
        tk.Label(center, text=f"Ходит: {next_player_name}",
                 font=("Arial", 16), bg=BACKGROUND_COLOR).pack(pady=10)
        tk.Button(center, text="Готов",
                  command=on_ready,
                  font=("Arial", 12), width=20).pack(pady=20)

    def show_game_over(self, winner_name):
        """Экран победы. winner_name — имя победителя."""
        self.clear_content()

        # Контейнер по центру
        center = tk.Frame(self.content_frame, bg=BACKGROUND_COLOR)
        center.place(relx=0.5, rely=0.5, anchor="center")

        # Заголовок
        title_label = tk.Label(
            center,
            text="Игра окончена",
            font=("Arial", 24, "bold"),
            bg=BACKGROUND_COLOR
        )
        title_label.pack(pady=20)

        # Имя победителя
        winner_label = tk.Label(
            center,
            text=f"Победил: {winner_name}",
            font=("Arial", 18, "bold"),
            fg="#2a7a2a",  # зелёный, чтобы выделялось
            bg=BACKGROUND_COLOR
        )
        winner_label.pack(pady=10)

        # Кнопка «Новая игра» — перезапуск с тем же режимом
        new_game_button = tk.Button(
            center,
            text="Новая игра",
            command=self._restart_game,
            font=("Arial", 12),
            width=20
        )
        new_game_button.pack(pady=10)

        # Кнопка «В меню»
        menu_button = tk.Button(
            center,
            text="В меню",
            command=self._back_to_menu,
            font=("Arial", 12),
            width=20
        )
        menu_button.pack(pady=10)

    def _restart_game(self):
        """Перезапуск с тем же режимом (человек/AI)."""
        if self.controller.is_with_ai:
            self.controller.start_game_vs_ai()
        else:
            self.controller.start_game_vs_human()

    def _back_to_menu(self):
        """Возврат в меню + сброс игры в контроллере."""
        self.controller.reset_game()
        self.start_menu_widgets()

    def clear_content(self):
        """Очищает текущий фрейм"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def update_info(self, message):
        """Обновление текста в информационной метке"""
        self.info_label.config(text=message)

    def run(self):
        """Запуск основного цикла приложения"""
        self.root.mainloop()

    def close(self):
        """Закрытие окна"""
        self.root.quit()