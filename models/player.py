from models.grid import Grid, ShotResult
import random
from models.grid import CellState


class Player:
    """Базовый класс игрока"""

    def __init__(self, name, grid_size=10):
        self.name = name
        self.grid = Grid(grid_size)
        self.opponent_grid = None  # Ссылка на сетку противника (для AI)

    def set_opponent_grid(self, opponent_grid):
        """Устанавливает ссылку на сетку противника"""
        self.opponent_grid = opponent_grid

    def make_shot(self, row, col):
        """
        Выполняет выстрел по координатам (row, col)
        Возвращает результат выстрела
        """
        if self.opponent_grid is None:
            raise ValueError("Opponent grid not set")
        return self.opponent_grid.receive_shot(row, col)

    def has_lost(self):
        """Проверяет, проиграл ли игрок"""
        return not self.grid.is_game_not_over()

    def place_ships_random(self, ships_config):
        """
        Автоматическая случайная расстановка кораблей
        ships_config: [{'size': 4, 'count': 1}, {'size': 3, 'count': 2}, ...]
        """
        orientations = ['horizontal', 'vertical']

        for ship_type in ships_config:
            for _ in range(ship_type['count']):
                placed = False
                attempts = 0
                max_attempts = 1000

                while not placed and attempts < max_attempts:
                    row = random.randint(0, self.grid.size - 1)
                    col = random.randint(0, self.grid.size - 1)
                    orientation = random.choice(orientations)

                    if self.grid.place_ship(row, col, ship_type['size'], orientation):
                        placed = True
                    attempts += 1

                if not placed:
                    # Если не удалось разместить за max_attempts, очищаем поле и пробуем заново
                    self._reset_grid()
                    self.place_ships_random(ships_config)
                    return

    def _reset_grid(self):
        """Сбрасывает сетку (используется при неудачной случайной расстановке)"""
        self.grid = Grid(self.grid.size)


class HumanPlayer(Player):
    """Класс игрока-человека"""

    def __init__(self, name, grid_size=10):
        super().__init__(name, grid_size)

    def make_shot(self, row, col):
        """Человек делает выстрел по указанным координатам"""
        return super().make_shot(row, col)


class AIPlayer(Player):
    """Класс компьютерного противника"""

    def __init__(self, name, grid_size=10, strategy="random"):
        super().__init__(name, grid_size)
        self.strategy = strategy
        self.last_hit = None  # Последнее попадание (для умной стратегии)
        self.hunting_mode = False  # Режим охоты (после попадания)
        self.hunt_targets = []  # Очередь потенциальных целей

    def _get_random_shot(self):
        """Случайный выстрел"""
        attempts = 0
        max_attempts = 100

        while attempts < max_attempts:
            row = random.randint(0, self.grid.size - 1)
            col = random.randint(0, self.grid.size - 1)

            # Проверяем, можно ли стрелять в эту клетку
            cell = self.opponent_grid._get_cell(row, col)
            if cell not in [None, 2, 3, 4]:  # Не HIT, MISS, DESTROY
                return row, col
            attempts += 1

        # Если все клетки обстреляны
        for i in range(self.grid.size):
            for j in range(self.grid.size):
                cell = self.opponent_grid._get_cell(i, j)
                if cell not in [None, 2, 3, 4]:
                    return i, j
        return 0, 0

    def _get_smart_shot(self):
        """Умная стратегия: после попадания ищет соседние клетки"""
        if self.hunting_mode and self.hunt_targets:
            # Стреляем по следующей цели из очереди
            return self.hunt_targets.pop(0)

        # Если не в режиме охоты - случайный выстрел
        return self._get_random_shot()

    def _update_hunting_mode(self, row, col, result):
        """Обновляет режим охоты на основе результата выстрела"""
        if result == ShotResult.HIT:
            # Попали, но не уничтожили - добавляем соседние клетки
            self.hunting_mode = True
            neighbors = [
                (row - 1, col), (row + 1, col),
                (row, col - 1), (row, col + 1)
            ]

            for n_row, n_col in neighbors:
                if self.opponent_grid._is_valid_coord(n_row, n_col):
                    cell = self.opponent_grid._get_cell(n_row, n_col)
                    # Если клетка не обстреляна
                    if cell not in [CellState.HIT, CellState.MISS, CellState.DESTROYED]:
                        if (n_row, n_col) not in self.hunt_targets:
                            self.hunt_targets.append((n_row, n_col))

            self.last_hit = (row, col)

        elif result == ShotResult.DESTROYED:
            # Уничтожили корабль - выходим из режима охоты
            self.hunting_mode = False
            self.hunt_targets.clear()
            self.last_hit = None

        elif result == ShotResult.MISS:
            # Промах - продолжаем охоту если есть цели
            pass

    def make_shot(self, row=None, col=None):
        """
        AI делает выстрел
        Если переданы координаты - использует их (для тестов)
        Иначе - выбирает по стратегии
        """
        if self.opponent_grid is None:
            raise ValueError("Opponent grid not set")

        if row is not None and col is not None:
            # Для тестов или отладки
            result = super().make_shot(row, col)
            self._update_hunting_mode(row, col, result)
            return result

        # Выбираем координаты на основе стратегии
        if self.strategy == "smart":
            target_row, target_col = self._get_smart_shot()
        else:
            target_row, target_col = self._get_random_shot()

        result = super().make_shot(target_row, target_col)
        self._update_hunting_mode(target_row, target_col, result)

        return result, target_row, target_col

    def reset_strategy(self):
        """Сбрасывает стратегию AI для новой игры"""
        self.last_hit = None
        self.hunting_mode = False
        self.hunt_targets = []