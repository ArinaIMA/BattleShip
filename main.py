from controllers.game_controller import GameController
from views.main_window import MainWindow


def main():
    # Создание контроллера - отвечает за ход игры
    controller = GameController()

    # Создание окна с передачей контроллера
    app = MainWindow(controller) # класс, отвечающий за отрисовку
    controller.set_main_window(app)

    # Запуск приложения
    app.run()


if __name__ == "__main__":
    main()