import os

import mlx

WHITE = 0xFFFFFF
BLACK = 0x000000
RED = 0xFF0000
GREEN = 0x00FF00
BLUE = 0x0000FF


def put_pixel(data_addr, line_len, bpp, x, y, color):
    offset = (y * line_len) + (x * (bpp // 8))
    data_addr[offset] = (color) & 0xFF  # B
    data_addr[offset + 1] = (color >> 8) & 0xFF  # G
    data_addr[offset + 2] = (color >> 16) & 0xFF  # R
    data_addr[offset + 3] = 0xFF  # A


def put_box(data_addr, line_len, bpp, x, y, w, h, color):
    for yy in range(h):
        for xx in range(w):
            put_pixel(data_addr, line_len, bpp, x + xx, y + yy, color)


def on_keypress(keycode, param):
    if keycode == 65307:
        os._exit(0)


def on_close(param):
    exit(0)

class Config:
    width: int
    height: int
    entry: list
    exit: list
    output_file: str
    perfect: bool

    fill_color: int
    border_color: int

    def __init__(self, width: int, height: int, entry: list, exit: list, output_file: str, perfect: bool) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.output_file = output_file
        self.perfect = perfect
        

class Cell:
    width: int
    height: int
    north: bool
    east: bool
    south: bool
    west: bool

    def __init__(self, m, mlx_ptr, win_ptr, width, height, row, column) -> None:
        self.m = m
        self.mlx_ptr = mlx_ptr
        self.win_ptr = win_ptr

        self.width = width
        self.height = height

        self.row = row
        self.column = column

        self.fill = True
        self.west = True
        self.east = True
        self.north = True
        self.south = True


    def render(self, data_addr, line_len, bpp) -> None:
        x = self.row * self.height
        y = self.column * self.width
        wall_size = self.width//20

        self.fill and put_box(data_addr, line_len, bpp, x+wall_size, y+wall_size, self.width-2*wall_size, self.height-2*wall_size, BLACK) # inner

        self.west and put_box(data_addr, line_len, bpp, x, y, wall_size, self.height, BLUE) # west
        self.east and put_box(data_addr, line_len, bpp, x+self.width-wall_size, y, wall_size, self.height, BLUE) # east

        self.north and put_box(data_addr, line_len, bpp, x, y, self.width, wall_size, BLUE) # north
        self.south and put_box(data_addr, line_len, bpp, x, y+self.height-wall_size, self.width, wall_size, BLUE) # south


def main():
    WIDTH = 800
    HEIGHT = 800

    config = Config(16, 16, [0, 0], [0, 0], "output.txt", True)
    config.cell_width = WIDTH//config.width
    config.cell_height = HEIGHT//config.height
    config.fill_color = BLACK
    config.border_color = BLUE
    config.path_color = RED
    config.patter_color = GREEN

    m = mlx.Mlx()
    mlx_ptr = m.mlx_init()
    win_ptr = m.mlx_new_window(mlx_ptr, WIDTH, HEIGHT, "a-maze-ing")

    img_ptr = m.mlx_new_image(mlx_ptr, WIDTH, HEIGHT)
    data_addr, bpp, line_len, endian = m.mlx_get_data_addr(img_ptr)

    cells = []
    for row in range(config.height):
        curr_row = []
        for column in range(config.width):
            cell = Cell(m, mlx_ptr, win_ptr, config.cell_width, config.cell_height, row, column)
            cell.render(data_addr, line_len, bpp)
            curr_row.append(cell)
        cells.append(curr_row)

    m.mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, 0, 0)
    m.mlx_key_hook(win_ptr, on_keypress, None)
    m.mlx_loop(mlx_ptr)


if __name__ == "__main__":
    main()
