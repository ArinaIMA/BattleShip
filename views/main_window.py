import tkinter as tk
from config import WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, BACKGROUND_COLOR


class MainWindow:
    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()

        # Настройка окна
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg=BACKGROUND_COLOR)

        # Создание интерфейса
        self._create_widgets()

    def _create_widgets(self):
        # Заголовок
        title_label = tk.Label(
            self.root,
            text="Морской бой",
            font=("Arial", 24, "bold"),
            bg=BACKGROUND_COLOR
        )
        title_label.pack(pady=20)

        # Кнопка выхода
        exit_button = tk.Button(
            self.root,
            text="Выход",
            command=self.controller.on_exit,
            font=("Arial", 12),
            width=20
        )
        exit_button.pack(pady=10)

        # Метка информации (пока заглушка)
        self.info_label = tk.Label(
            self.root,
            text="Добро пожаловать в игру!",
            font=("Arial", 14),
            bg=BACKGROUND_COLOR
        )
        self.info_label.pack(pady=20)

    def update_info(self, message):
        """Обновление текста в информационной метке"""
        self.info_label.config(text=message)

    def run(self):
        """Запуск основного цикла приложения"""
        self.root.mainloop()

    def close(self):
        """Закрытие окна"""
        self.root.quit()