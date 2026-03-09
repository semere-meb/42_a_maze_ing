import os

import mlx
import generator as gen

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

    def __init__(
        self,
        width: int,
        height: int,
        entry: list,
        exit: list,
        output_file: str,
        perfect: bool,
    ) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.output_file = output_file
        self.perfect = perfect


def main():
    WIDTH = 800
    HEIGHT = 800

    config = Config(25, 25, [0, 0], [0, 0], "output.txt", True)
    config.cell_width = WIDTH // config.width
    config.cell_height = HEIGHT // config.height
    config.fill_color = BLACK
    config.border_color = BLUE
    config.path_color = RED
    config.patter_color = GREEN
    config.menu_color = GREEN

    m = mlx.Mlx()
    mlx_ptr = m.mlx_init()
    win_ptr = m.mlx_new_window(mlx_ptr, WIDTH + 20, HEIGHT + 130, "a-maze-ing")

    img_ptr = m.mlx_new_image(mlx_ptr, WIDTH, HEIGHT)
    data_addr, bpp, line_len, endian = m.mlx_get_data_addr(img_ptr)

    ps = gen.get_pattern_set(config.height, config.width)
    grid = gen.generate_grid(
        config.height,
        config.width,
        m,
        mlx_ptr,
        win_ptr,
        config.cell_height,
        config.cell_width,
        ps,
    )
    gen.wilson_generate(grid, (0, 0), config.height, config.width, ps)

    cells = grid.adj

    for row in cells:
        for cell in row:
            cell.render(data_addr, line_len, bpp)

    m.mlx_string_put(mlx_ptr, win_ptr, 10, HEIGHT + 10 + 10, GREEN, "MENU")
    m.mlx_string_put(mlx_ptr, win_ptr, 10, HEIGHT + 10 + 30, GREEN, "1. Regenerate")
    m.mlx_string_put(mlx_ptr, win_ptr, 10, HEIGHT + 10 + 50, GREEN, "2. Show path")
    m.mlx_string_put(mlx_ptr, win_ptr, 10, HEIGHT + 10 + 70, GREEN, "3. Change color")
    m.mlx_string_put(mlx_ptr, win_ptr, 10, HEIGHT + 10 + 90, GREEN, "ESC. Quit")

    m.mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, 10, 10)

    m.mlx_key_hook(win_ptr, on_keypress, None)
    m.mlx_loop(mlx_ptr)


if __name__ == "__main__":
    main()
