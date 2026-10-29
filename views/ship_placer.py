import tkinter as tk

from models.grid import CellState
from config import *


class ShipPlacer(tk.Frame):
    """
    Экран ручной расстановки кораблей для одного игрока.

    on_ready     — callback(), вызывается по кнопке «Готов» (все корабли расставлены)
    on_cancel    — callback(), вызывается по кнопке «Назад»
    """


    def __init__(self, parent, player, ships_config, on_ready, on_cancel=None, bg=BACKGROUND_COLOR):
        super().__init__(parent, bg=bg)
        self.player = player
        self.grid = player.grid
        self.ships_config = ships_config
        self.on_ready = on_ready
        self.on_cancel = on_cancel

        # Состояние расстановки
        self.remaining = {item["size"]: item["count"] for item in ships_config}
        self.initial_remaining = dict(self.remaining)
        self.selected_size = self._pick_default_size()
        self.orientation = "horizontal"
        self.delete_mode = False
        self.hover = None  # (row, col) под курсором или None

        self._build()
        self._update_panel()
        self._redraw()

    # ---------- построение UI ----------

    def _build(self):
        # Верхняя панель с именем игрока
        header = tk.Frame(self, bg=BACKGROUND_COLOR)
        header.pack(fill="x", pady=(10, 5))
        tk.Label(
            header,
            text=f"Расстановка кораблей: {self.player.name}",
            font=("Arial", 16, "bold"),
            bg=BACKGROUND_COLOR
        ).pack()

        # Основная зона: слева поле, справа панель управления
        body = tk.Frame(self, bg=BACKGROUND_COLOR)
        body.place(relx=0.5, rely=0.5, anchor="center")

        # Канва с полем
        self.canvas = tk.Canvas(
            body,
            width=self.grid.size * CELL_SIZE,
            height=self.grid.size * CELL_SIZE,
            bg=WATER_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack(side="left", padx=(0, 20))
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<Leave>", self._on_leave)
        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<Button-3>", self._on_right_click)

        # Правая панель
        side = tk.Frame(body, bg=BACKGROUND_COLOR)
        side.pack(side="left", fill="y")

        tk.Label(side, text="Корабли:", font=("Arial", 12, "bold"), bg=BACKGROUND_COLOR).pack(anchor="w")
        self.ships_frame = tk.Frame(side, bg=WHITE)
        self.ships_frame.pack(anchor="w", pady=(5, 15))

        # Кнопки управления
        tk.Button(
            side, text="Повернуть (ПКМ / Space)",
            command=self._rotate, width=24,
        ).pack(pady=3)
        self.delete_button = tk.Button(
            side, text="Удалить корабль",
            command=self._toggle_delete_mode, width=24,
        )
        self.delete_button.pack(pady=3)
        tk.Button(
            side, text="Очистить поле",
            command=self._clear, width=24,
        ).pack(pady=3)
        tk.Button(
            side, text="Случайно",
            command=self._random_place, width=24,
        ).pack(pady=3)

        self.ready_button = tk.Button(
            side, text="Готов",
            command=self._on_ready_clicked, width=24,
            state="disabled",
        )
        self.ready_button.pack(pady=(15, 3))
        tk.Button(
            side, text="Назад",
            command=self._on_cancel_clicked, width=24,
        ).pack(pady=3)

        # Биндим пробел на всё окно
        self.winfo_toplevel().bind("<space>", self._on_space)

    # ---------- работа со списком кораблей ----------

    def _pick_default_size(self):
        sizes = [item["size"] for item in self.ships_config if item["count"] > 0]
        return max(sizes) if sizes else None

    def _update_panel(self):
        # перерисовать элементы выбора корабля
        for widget in self.ships_frame.winfo_children():
            widget.destroy()

        for item in self.ships_config:
            size = item["size"]
            count = self.remaining.get(size, 0)
            total = item["count"]
            if total == 0:
                continue
            selected = (size == self.selected_size and count > 0)
            btn = tk.Button(
                self.ships_frame,
                text=f"{size}-палубный: {count}/{total}",
                width=20,
                command=lambda s=size: self._select_size(s),
                relief="sunken" if selected else "raised",
                bg=SELECTED_COLOR if selected else WHITE,
                state="normal" if count > 0 else "disabled",
            )
            btn.pack(anchor="w", pady=1)

        # Готов активна только когда всё расставлено
        all_placed = all(v == 0 for v in self.remaining.values())
        self.ready_button.config(state="normal" if all_placed else "disabled")

        # Подсветка кнопки удаления
        self.delete_button.config(
            relief="sunken" if self.delete_mode else "raised",
            bg=SELECTED_COLOR if self.delete_mode else WHITE,
        )

    def _select_size(self, size):
        if self.remaining.get(size, 0) > 0:
            self.selected_size = size
            self.delete_mode = False
            self._update_panel()
            self._redraw()

    # ---------- действия кнопок ----------

    def _rotate(self):
        self.orientation = "vertical" if self.orientation == "horizontal" else "horizontal"
        self._redraw()

    def _on_space(self, event):
        self._rotate()

    def _toggle_delete_mode(self):
        self.delete_mode = not self.delete_mode
        self._update_panel()
        self._redraw()

    def _clear(self):
        self.grid.cells = [
            [CellState.EMPTY for _ in range(self.grid.size)]
            for _ in range(self.grid.size)
        ]
        self.grid.ships.clear()
        self.grid.cell_to_ship.clear()
        self.grid.destroyed_count = 0
        self.remaining = dict(self.initial_remaining)
        self.selected_size = self._pick_default_size()
        self.delete_mode = False
        self.hover = None
        self._update_panel()
        self._redraw()

    def _random_place(self):
        self.player.place_ships_random(self.ships_config)
        for size in self.remaining:
            self.remaining[size] = 0
        self.delete_mode = False
        self.hover = None
        self._update_panel()
        self._redraw()

    def _on_ready_clicked(self):
        if all(v == 0 for v in self.remaining.values()):
            self._unbind_space()
            self.on_ready()

    def _on_cancel_clicked(self):
        self._unbind_space()
        if self.on_cancel:
            self.on_cancel()

    def _unbind_space(self):
        try:
            self.winfo_toplevel().unbind("<space>")
        except tk.TclError:
            pass

    # ---------- мышь по полю ----------

    def _event_to_cell(self, event):
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        if 0 <= row < self.grid.size and 0 <= col < self.grid.size:
            return row, col
        return None

    def _on_motion(self, event):
        cell = self._event_to_cell(event)
        if cell != self.hover:
            self.hover = cell
            self._redraw()

    def _on_leave(self, event):
        if self.hover is not None:
            self.hover = None
            self._redraw()

    def _on_right_click(self, event):
        self._rotate()

    def _on_left_click(self, event):
        cell = self._event_to_cell(event)
        if cell is None:
            return
        row, col = cell

        if self.delete_mode:
            self._try_remove_ship(row, col)
        else:
            self._try_place_ship(row, col)

    def _try_place_ship(self, row, col):
        if self.selected_size is None:
            return
        if self.remaining.get(self.selected_size, 0) <= 0:
            return
        if self.grid.place_ship(row, col, self.selected_size, self.orientation):
            self.remaining[self.selected_size] -= 1
            if self.remaining[self.selected_size] == 0:
                self.selected_size = self._pick_default_size()
            self._update_panel()
            self._redraw()

    def _try_remove_ship(self, row, col):
        ship = self.grid.cell_to_ship.get((row, col))
        if ship is None:
            return
        # Удаляем все клетки корабля
        for (r, c) in ship.get_coords():
            self.grid.cells[r][c] = CellState.EMPTY
            if (r, c) in self.grid.cell_to_ship:
                del self.grid.cell_to_ship[(r, c)]
        if ship in self.grid.ships:
            self.grid.ships.remove(ship)
        # Возвращаем размер в remaining
        size = ship.get_size()
        self.remaining[size] = self.remaining.get(size, 0) + 1
        self.selected_size = self._pick_default_size()
        self._update_panel()
        self._redraw()

    # ---------- отрисовка ----------

    def _redraw(self):
        self.canvas.delete("all")
        self._draw_grid_lines()
        self._draw_ships()
        self._draw_preview()

    def _draw_grid_lines(self):
        n = self.grid.size
        for i in range(n + 1):
            x = i * CELL_SIZE
            self.canvas.create_line(x, 0, x, n * CELL_SIZE, fill=GRID_LINE_COLOR)
            self.canvas.create_line(0, x, n * CELL_SIZE, x, fill=GRID_LINE_COLOR)

    def _draw_ships(self):
        for (row, col), ship in self.grid.cell_to_ship.items():
            if self.grid.cells[row][col] == CellState.SHIP:
                self._draw_filled_cell(row, col, SHIP_COLOR)

    def _draw_preview(self):
        if self.hover is None or self.delete_mode:
            return
        if self.selected_size is None:
            return
        if self.remaining.get(self.selected_size, 0) <= 0:
            return

        row, col = self.hover
        size = self.selected_size
        cells = self._preview_cells(row, col, size)
        if not cells:
            return

        can_place = self.grid._can_place_ship(row, col, size, self.orientation)
        color = PREVIEW_OK_COLOR if can_place else PREVIEW_BAD_COLOR

        for (r, c) in cells:
            self._draw_filled_cell(r, c, color, outline=HOVER_OK_OUTLINE if can_place else HOVER_BAD_OUTLINE)

    def _preview_cells(self, row, col, size):
        cells = []
        for i in range(size):
            if self.orientation == "horizontal":
                r, c = row, col + i
            else:
                r, c = row + i, col
            if not (0 <= r < self.grid.size and 0 <= c < self.grid.size):
                return []
            cells.append((r, c))
        return cells

    def _draw_filled_cell(self, row, col, color, outline=""):
        x0 = col * CELL_SIZE
        y0 = row * CELL_SIZE
        x1 = x0 + CELL_SIZE
        y1 = y0 + CELL_SIZE
        self.canvas.create_rectangle(
            x0 + 2, y0 + 2, x1 - 2, y1 - 2,
            fill=color, outline=outline,
        )