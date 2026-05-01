class Ship:
    """Класс корабля"""
    def __init__(self, size, start_coord, orientation):
        """Инициализация"""
        self.size = size
        self.start_row, self.start_col = start_coord
        self.orientation = orientation
        self.is_sunk = False
        self.coords = self._get_coords()

    def _get_coords(self):
        """Получить координаты всех занимаемых клеток корабля"""
        coords = []
        row, col = self.start_row, self.start_col

        for i in range(self.size):
            if self.orientation == "horizontal":
                coords.append((row, col + 1))
            else:
                coords.append((row + 1, col))

        return coords

    def is_alive(self):
        """Проверяет живучесть"""
        return not self.is_sunk

    def is_contain_coord(self, row, col):
        """Проверяет попадание"""
        return (row, col) in self.coords
