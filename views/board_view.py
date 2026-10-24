import tkinter as tk

from models.grid import CellState


class BoardView(tk.Frame):
    """
    Отрисовка одного игрового поля.
    mode: 'own'   — видны корабли (своё поле)
          'enemy' — корабли скрыты, видны только результаты выстрелов
    """

    CELL_SIZE = 40

    def __init__(self, parent, grid, mode="own", on_cell_click=None, bg="#ffffff"):
        super().__init__(parent, bg=bg)
        self.grid = grid
        self.mode = mode
        self.on_cell_click = on_cell_click   # callback(row, col) или None
        self._build()

    def _build(self):
        self.canvas = tk.Canvas(
            self,
            width=self.grid.size * self.CELL_SIZE,
            height=self.grid.size * self.CELL_SIZE,
            bg="#d0e8ff",          # цвет «воды»
            highlightthickness=0,
        )
        self.canvas.pack()
        self._draw_grid()
        self._draw_state()
        if self.on_cell_click:
            self.canvas.bind("<Button-1>", self._on_click)

    def _draw_grid(self):
        n = self.grid.size
        for i in range(n + 1):
            x = i * self.CELL_SIZE
            self.canvas.create_line(x, 0, x, n * self.CELL_SIZE, fill="#555")
            self.canvas.create_line(0, x, n * self.CELL_SIZE, x, fill="#555")

    def _draw_state(self):
        """Рисует корабли (если mode='own') и результаты выстрелов."""
        n = self.grid.size
        for row in range(n):
            for col in range(n):
                cell = self.grid._get_cell(row, col)
                if cell is None:
                    continue
                self._draw_cell(row, col, cell)

    def _draw_cell(self, row, col, cell_state):
        x0 = col * self.CELL_SIZE
        y0 = row * self.CELL_SIZE
        x1 = x0 + self.CELL_SIZE
        y1 = y0 + self.CELL_SIZE

        # Здесь маппинг CellState -> цвет. Подставьте свои значения.
        # Пример (зависит от вашего grid.py):
        #   SHIP (корабль)      -> тёмно-серый, только в mode='own'
        #   MISS (промах)       -> белый кружок
        #   HIT (попадание)     -> красный
        #   DESTROYED (убит)    -> тёмно-красный
        if cell_state == CellState.SHIP:
            if self.mode == "own":
                self.canvas.create_rectangle(x0+2, y0+2, x1-2, y1-2, fill="#444")
            # в mode='enemy' корабль не рисуем — враг не должен его видеть
        elif cell_state == CellState.MISS:
            cx, cy = (x0+x1)/2, (y0+y1)/2
            r = self.CELL_SIZE * 0.15
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="#888", outline="")
        elif cell_state == CellState.HIT:
            self.canvas.create_rectangle(x0+2, y0+2, x1-2, y1-2, fill="#ff5555")
        elif cell_state == CellState.DESTROYED:
            self.canvas.create_rectangle(x0+2, y0+2, x1-2, y1-2, fill="#aa0000")

    def _on_click(self, event):
        col = event.x // self.CELL_SIZE
        row = event.y // self.CELL_SIZE
        if 0 <= row < self.grid.size and 0 <= col < self.grid.size:
            self.on_cell_click(row, col)

    def refresh(self):
        """Перерисовать состояние (после выстрела)."""
        self.canvas.delete("all")
        self._draw_grid()
        self._draw_state()