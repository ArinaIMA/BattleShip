class Ship:
    """Класс корабля"""
    def __init__(self, size, start_coord, orientation):
        """Инициализация"""
        self.size = size
        self.start_row, self.start_col = start_coord
        self.orientation = orientation
        self.hits_count = 0
        self.coords = self.get_coords()

    @property
    def get_coords(self):
        """Получить координаты всех занимаемых клеток корабля"""
        coords = []
        row, col = self.start_row, self.start_col

        for i in range(self.size):
            if self.orientation == "horizontal":
                coords.append((row, col + i))
            else:
                coords.append((row + i, col))

        return coords

    @property
    def get_is_sunk(self):
        return self.hits_count >= self.size

    def is_contain_coord(self, row, col):
        """Проверяет попадание"""
        return (row, col) in self.coords

    def add_hit(self):
        self.hits_count += 1