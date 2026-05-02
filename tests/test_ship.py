import pytest
from models.ship import Ship


class TestShip:
    def test_init_horizontal(self):
        """Создание горизонтального корабля"""
        ship = Ship(3, (2, 2), "horizontal")

        assert ship._size == 3
        assert ship._start_row == 2
        assert ship._start_col == 2
        assert ship._orientation == "horizontal"
        assert ship._hits_count == 0
        assert len(ship._coords) == 3

    def test_init_vertical(self):
        """Создание вертикального корабля"""
        ship = Ship(4, (5, 0), "vertical")

        assert ship._orientation == "vertical"
        assert len(ship._coords) == 4

    def test_get_coords_horizontal(self):
        """Координаты горизонтального корабля"""
        ship = Ship(3, (1, 1), "horizontal")
        expected = [(1, 1), (1, 2), (1, 3)]

        assert ship.get_coords() == expected

    def test_get_coords_vertical(self):
        """Координаты вертикального корабля"""
        ship = Ship(2, (3, 4), "vertical")
        expected = [(3, 4), (4, 4)]

        assert ship.get_coords() == expected

    def test_is_contain_coord_true(self):
        """Проверка наличия координаты в корабле"""
        ship = Ship(3, (1, 1), "horizontal")

        assert ship.is_contain_coord(1, 2) is True
        assert ship.is_contain_coord(1, 3) is True

    def test_is_contain_coord_false(self):
        """Проверка отсутствия координаты"""
        ship = Ship(3, (1, 1), "horizontal")

        assert ship.is_contain_coord(1, 4) is False
        assert ship.is_contain_coord(0, 1) is False

    def test_get_is_sunk_false(self):
        """Корабль не уничтожен"""
        ship = Ship(3, (0, 0), "horizontal")

        assert ship.is_sunk() is False

    def test_get_is_sunk_true(self):
        """Корабль уничтожен после достаточного количества попаданий"""
        ship = Ship(3, (0, 0), "horizontal")

        ship.add_hit()
        ship.add_hit()
        ship.add_hit()

        assert ship.is_sunk() is True

    def test_add_hit_increments(self):
        """Проверка увеличения счетчика попаданий"""
        ship = Ship(2, (0, 0), "horizontal")

        ship.add_hit()
        assert ship._hits_count == 1

        ship.add_hit()
        assert ship._hits_count == 2

    def test_add_hit_after_sunk(self):
        """Добавление попаданий после уничтожения"""
        ship = Ship(1, (0, 0), "horizontal")

        ship.add_hit()
        assert ship.is_sunk() is True

        ship.add_hit()  # Лишнее попадание
        assert ship._hits_count == 2
        assert ship.is_sunk() is True