from enum import Enum, auto
from models.ship import Ship

class CellState(Enum):
    """Состояние каждой клетки на поле"""
    EMPTY = 0
    SHIP = 1
    HIT = 2
    MISS = 3
    DESTROY = 4

class ShotResult(Enum):
    """Состояние после выстрела"""
    MISS = auto()
    HIT = auto()
    DESTROYED = auto()
    INVALID = auto()
    ALREADY_SHOT = auto()

class Grid:
    """Игровое поле, по умолчанию сетка 10х10"""
    def __init__(self, size=10):
        self.size = size
        self.cells = [[CellState.EMPTY for _ in range(size)] for _ in range(size)]
        self.ships = []
        self.destroyed_count = 0
        self.cell_to_ship = {}

    def _is_valid_coord(self, row, col):
        """Проверяет валидность координат для обращения к массиву"""
        return 0 <= row < self.size and 0 <= col < self.size

    def _get_cell(self, row, col):
        """Возвращает состояние клетки по координатам"""
        if self._is_valid_coord(row, col):
            return self.cells[row][col]
        return None

    def _set_cell(self, row, col, cell):
        """Устанавливает состояние клетки по координатам"""
        if self._is_valid_coord(row, col):
            self.cells[row][col] = cell
            return True
        return False

    def _is_empty(self, row, col):
        """Проверяет пуста ли клетка"""
        return self.cells[row][col] == CellState.EMPTY

    def _is_cell_free_for_ship(self, row, col):
        """
        Проверяет квадрат 3х3 на то, что
        можно ли поставить туда корабль?
        (не будет ли пересечений с
        другими кораблями?)
        """
        if not self._is_valid_coord(row, col):
            return False

        if not self._is_empty(row, col):
            return False

        for d_row in [-1, 0, 1]:
            for d_col in [-1, 0, 1]:
                n_row, n_col = row + d_row, col + d_col
                if self._is_valid_coord(n_row, n_col):
                    if self.cells[n_row][n_col] == CellState.SHIP:
                        return False

        return True

    def _can_place_ship(self, row, col, size, orientation):
        """Проверяет можно ли разместить корабль в указанной позиции"""
        # Проверка границ
        if not self._is_valid_coord(row, col):
            return False
        if orientation == 'horizontal':
            if col + size > self.size:
                return False
        else:
            if row + size > self.size:
                return False

        # Проверка, что все клетки корабля пустые + соседние
        for i in range(size):
            if orientation == 'horizontal':
                if not self._is_cell_free_for_ship(row, col + i):
                    return False
            else:
                if not self._is_cell_free_for_ship(row + i, col):
                    return False

        return True

    def __mark_destroyed_ship(self, coords):
        """Пометить клетки корабля, как уничтоженные"""
        for coord in coords:
            self._set_cell(coord[0], coord[1], CellState.DESTROY)

    def __is_ship_destroyed(self, row, col):
        """Обрабатывает попадание"""
        ship = self.cell_to_ship[(row, col)]
        if ship.is_sunk():
            self.__mark_destroyed_ship(ship.get_coords())
        return ship.is_sunk()

    def place_ship(self, row, col, size, orientation):
        """Размещает корабль, если возможно"""
        if not self._can_place_ship(row, col, size, orientation):
            return False

        ship = Ship(size, (row, col), orientation)
        for i in range(size):
            if orientation == 'horizontal':
                self._set_cell(row, col + i, CellState.SHIP)
                self.cell_to_ship[(row, col + i)] = ship
            else:
                self._set_cell(row + i, col, CellState.SHIP)
                self.cell_to_ship[(row + i, col)] = ship

        self.ships.append(ship)

        return True

    def receive_shot(self, row, col):
        """
        Обрабатывает выстрел
        Возвращает значение из ShotResult
        """
        if not self._is_valid_coord(row, col):
            return ShotResult.INVALID

        current = self._get_cell(row, col)

        if current == CellState.EMPTY:
            self._set_cell(row, col, CellState.MISS)
            return ShotResult.MISS
        elif current == CellState.SHIP:
            self._set_cell(row, col, CellState.HIT)
            ship = self.cell_to_ship[(row, col)]
            ship.add_hit()
            if self.__is_ship_destroyed(row, col):
                self.destroyed_count += 1
                return ShotResult.DESTROYED
            return ShotResult.HIT

        return ShotResult.ALREADY_SHOT

    def is_game_not_over(self):
        """Проверяет на конец игры"""
        return self.destroyed_count < len(self.ships)
