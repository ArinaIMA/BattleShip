class Ship:
    """Класс корабля"""
    def __init__(self, size, start_coord, orientation):
        """Инициализация"""
        self._size = size # размер - 1, ..., 4
        self._start_row, self._start_col = start_coord # стартовая ячейка поля - верхняя левая
        self._orientation = orientation # вниз или вправо
        self._hits_count = 0 # счетчик попаданий
        self._coords = [] # координаты всех ячеек, принадлежащих кораблю
        self.__set_coords()

    def __set_coords(self):
        """Установить координаты всех занимаемых клеток корабля"""
        row, col = self._start_row, self._start_col

        for i in range(self._size):
            if self._orientation == "horizontal": # по направлению корабля добавляем новые координаты
                self._coords.append((row, col + i))
            else:
                self._coords.append((row + i, col))

    def get_coords(self):
        """Вернуть координаты всех клеток корабля"""
        return self._coords

    def is_sunk(self):
        """Проверка: потанул ли корабль?"""
        return self._hits_count >= self._size

    def is_contain_coord(self, row, col):
        """Проверяет попадание"""
        return (row, col) in self._coords

    def add_hit(self):
        """Отметить попадание в корабль"""
        self._hits_count += 1