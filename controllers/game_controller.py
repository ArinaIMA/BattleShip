class GameController:
    def __init__(self):
        self.is_running = True
        self.main_window = None

    def set_main_window(self, window):
        """Связываем контроллер с окном"""
        self.main_window = window

    def on_exit(self):
        """Обработчик закрытия приложения"""
        print("Выход из игры")
        if self.main_window:
            self.main_window.close()  # Закрываем окно
        self.is_running = False

    def on_click(self, x, y):
        """Заглушка для обработки кликов (пока не используется)"""
        print(f"Клик по координатам: ({x}, {y})")