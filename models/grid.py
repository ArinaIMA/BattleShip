from enum import Enum
from ship import Ship

class CellState(Enum):
    """Состояние каждой клетки на поле"""
    EMPTY = 0
    SHIP = 1
    HIT = 2
    MISS = 3
    DESTROY = 4

class Grid:
    """Игровое поле, по умолчанию сетка 10х10"""
    def __init__(self, size=10):
        self.size = size
        self.cells = [[CellState.EMPTY for _ in range(size)] for _ in range(size)]
        self.ships = []
        self.destroyed_count = 0

    def _is_valid_coord(self, x, y):
        """Проверяе валидность координат для обращения к массиву"""
        return 0 <= x < self.size and 0 <= y < self.size

    def _get_cell(self, x, y):
        """Возвращает состояние клетки по координатам"""
        if self._is_valid_coord(x, y):
            return self.cells[x][y]
        return None

    def _set_cell(self, x, y, cell):
        """Устанавливает состояние клетки по координатам"""
        if self._is_valid_coord(x, y):
            self.cells[x][y] = cell
            return True
        return False

    def _is_empty(self, x, y):
        """Проверяет пуста ли клетка"""
        return self.cells[x][y] == CellState.EMPTY

    def _is_cell_free_for_ship(self, x, y):
        if not self._is_valid_coord(x, y):
            return False

        if not self._is_empty(x, y):
            return False

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if self._is_valid_coord(nx, ny):
                    if self.cells[nx][ny] == CellState.SHIP:
                        return False

        return True

    def _can_place_ship(self, x, y, size, orientation):
        """Проверяет можно ли разместить корабль в указанной позиции"""
        # Проверка границ
        if not self._is_valid_coord(x, y):
            return False
        if orientation == 'horizontal':
            if x + size > self.size:
                return False
        else:
            if y + size > self.size:
                return False

        # Проверка, что все клетки корабля пустые + соседние
        for i in range(size):
            if orientation == 'horizontal':
                if not self._is_cell_free_for_ship(x + i, y):
                    return False
            else:
                if not self._is_cell_free_for_ship(x, y + i):
                    return False

        return True

    def _mark_destroyed_ship(self, coords):
        for coord in coords:
            self._set_cell(coord[0], coord[1], CellState.DESTROY)

    def _is_ship_destroyed(self, x, y):
        for ship in self.ships:
            if ship.is_contain_coord(x, y):
                ship.add_hit()
                if ship.get_is_sunk():
                    self._mark_destroyed_ship(ship.get_coords())
                return ship.get_is_sunk()

        return False

    def place_ship(self, x, y, size, orientation):
        """Размещает корабль, если возможно"""
        if not self._can_place_ship(x, y, size, orientation):
            return False

        for i in range(size):
            if orientation == 'horizontal':
                self._set_cell(x + i, y, CellState.SHIP)
            else:
                self._set_cell(x, y + i, CellState.SHIP)

        self.ships.append(Ship(size, (x, y), orientation))

        return True

    def receive_shot(self, x, y):
        """
        Обрабатывает выстрел
        Возвращает значение из
        ["hit", "miss", "invalid", "destroyed", "already_shot"]
        """
        if not self._is_valid_coord(x, y):
            return "invalid"

        current = self._get_cell(x, y)

        if current == CellState.EMPTY:
            return "miss"
        elif current == CellState.SHIP:
            self._set_cell(x, y, CellState.HIT)
            if self._is_ship_destroyed(x, y):
                self.destroyed_count += 1
                return "destroyed"
            return "hit"

        return "already_shot"

    def has_any_ship(self):
        return self.destroyed_count < len(self.ships)
