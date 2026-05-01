import pytest
from models.grid import Grid, CellState, ShotResult


class TestGridInit:
    def test_default_size(self):
        grid = Grid()
        assert grid.size == 10
        assert len(grid.cells) == 10
        assert len(grid.cells[0]) == 10

    def test_custom_size(self):
        grid = Grid(8)
        assert grid.size == 8
        assert len(grid.cells) == 8

    def test_all_cells_empty(self):
        grid = Grid()
        for row in range(10):
            for col in range(10):
                assert grid.cells[row][col] == CellState.EMPTY

    def test_empty_ships_list(self):
        grid = Grid()
        assert grid.ships == []
        assert grid.destroyed_count == 0
        assert grid.cell_to_ship == {}


class TestShipPlacement:
    def test_place_ship_horizontal_valid(self):
        grid = Grid()

        result = grid.place_ship(2, 2, 3, "horizontal")

        assert result is True
        assert len(grid.ships) == 1
        assert grid.cells[2][2] == CellState.SHIP
        assert grid.cells[2][3] == CellState.SHIP
        assert grid.cells[2][4] == CellState.SHIP

    def test_place_ship_vertical_valid(self):
        grid = Grid()

        result = grid.place_ship(3, 4, 2, "vertical")

        assert result is True
        assert grid.cells[3][4] == CellState.SHIP
        assert grid.cells[4][4] == CellState.SHIP
        assert grid.cells[5][4] == CellState.EMPTY

    def test_place_ship_out_of_bounds_horizontal(self):
        grid = Grid(10)

        result = grid.place_ship(5, 8, 3, "horizontal")

        assert result is False
        assert len(grid.ships) == 0

    def test_place_ship_out_of_bounds_vertical(self):
        grid = Grid(10)

        result = grid.place_ship(8, 5, 3, "vertical")

        assert result is False

    def test_place_ship_adjacent_ships(self):
        """Проверка правила несоприкасающихся кораблей"""
        grid = Grid()
        grid.place_ship(2, 2, 1, "horizontal")  # Корабль в (2,2)

        # Пытаемся поставить рядом
        result = grid.place_ship(2, 3, 1, "horizontal")  # Соседняя клетка

        assert result is False

    def test_place_ship_overlapping(self):
        grid = Grid()
        grid.place_ship(2, 2, 3, "horizontal")

        # Попытка поставить корабль поверх существующего
        result = grid.place_ship(2, 3, 2, "horizontal")

        assert result is False

    def test_cell_to_ship_mapping(self):
        grid = Grid()
        grid.place_ship(1, 1, 2, "horizontal")

        assert (1, 1) in grid.cell_to_ship
        assert (1, 2) in grid.cell_to_ship
        assert grid.cell_to_ship[(1, 1)] == grid.ships[0]


class TestShots:
    def test_shot_miss(self):
        grid = Grid()
        grid.place_ship(2, 2, 1, "horizontal")

        result = grid.receive_shot(5, 5)

        assert result == ShotResult.MISS
        assert grid.cells[5][5] == CellState.MISS

    def test_shot_hit(self):
        grid = Grid()
        grid.place_ship(2, 2, 3, "horizontal")

        result = grid.receive_shot(2, 3)

        assert result == ShotResult.HIT
        assert grid.cells[2][3] == CellState.HIT
        assert grid.ships[0]._hits_count == 1

    def test_shot_destroyed_one_deck(self):
        grid = Grid()
        grid.place_ship(3, 3, 1, "horizontal")

        result = grid.receive_shot(3, 3)

        assert result == ShotResult.DESTROYED
        assert grid.cells[3][3] == CellState.DESTROY
        assert grid.destroyed_count == 1
        assert grid.ships[0].get_is_sunk() is True

    def test_shot_destroyed_multi_deck(self):
        grid = Grid()
        grid.place_ship(2, 2, 2, "horizontal")

        grid.receive_shot(2, 2)  # первый хит
        result = grid.receive_shot(2, 3)  # второй хит

        assert result == ShotResult.DESTROYED
        assert grid.destroyed_count == 1

    def test_shot_already_shot(self):
        grid = Grid()
        grid.place_ship(2, 2, 1, "horizontal")
        grid.receive_shot(2, 2)

        result = grid.receive_shot(2, 2)

        assert result == ShotResult.ALREADY_SHOT

    def test_shot_invalid_coordinates(self):
        grid = Grid()

        result = grid.receive_shot(-1, 5)
        assert result == ShotResult.INVALID

        result = grid.receive_shot(10, 5)
        assert result == ShotResult.INVALID


class TestGameState:
    def test_is_game_not_over_true(self):
        grid = Grid()
        grid.place_ship(2, 2, 1, "horizontal")
        grid.place_ship(5, 5, 1, "horizontal")

        assert grid.is_game_not_over() is True

    def test_is_game_not_over_false(self):
        grid = Grid()
        grid.place_ship(2, 2, 1, "horizontal")
        grid.receive_shot(2, 2)

        assert grid.is_game_not_over() is False

    def test_destroyed_count_tracking(self):
        grid = Grid()
        grid.place_ship(1, 1, 2, "horizontal")
        grid.place_ship(5, 5, 1, "horizontal")

        grid.receive_shot(1, 1)  # попадание в 1-й корабль
        assert grid.destroyed_count == 0  # еще не уничтожен

        grid.receive_shot(1, 2)  # уничтожение 1-го корабля
        assert grid.destroyed_count == 1

        grid.receive_shot(5, 5)  # уничтожение 2-го корабля
        assert grid.destroyed_count == 2


class TestHelperMethods:
    def test_is_valid_coord(self):
        grid = Grid()
        assert grid._is_valid_coord(5, 5) is True
        assert grid._is_valid_coord(0, 0) is True
        assert grid._is_valid_coord(9, 9) is True
        assert grid._is_valid_coord(-1, 5) is False
        assert grid._is_valid_coord(10, 5) is False

    def test_is_empty(self):
        grid = Grid()
        assert grid._is_empty(0, 0) is True
        grid.cells[0][0] = CellState.SHIP
        assert grid._is_empty(0, 0) is False

class TestNotValidCoord:
    def test_get_cell(self):
        grid = Grid()
        assert grid._get_cell(-1, 0) is None

    def test_set_cell(self):
        grid = Grid()
        assert grid._set_cell(-1, 0, CellState.SHIP) is False

    def test_is_cell_free_for_ship(self):
        grid = Grid()
        assert grid._is_cell_free_for_ship(-1, 0) is False

    def test_can_place_ship(self):
        grid = Grid()
        assert grid._can_place_ship(-1, 0, 1, "horizontal") is False

