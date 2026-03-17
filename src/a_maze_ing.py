#!/usr/bin/env python3

import os
import sys
import mlx
import generator as gen
from typing import Any
from utils import write_to_file
from parser import get_config
import random

# Colors
WHITE = 0xFFFFFF
BLACK = 0x000000
RED = 0xFF0000
GREEN = 0x00FF00
BLUE = 0x0000FF

# Window size
WIDTH = 800
HEIGHT = 800


def on_keypress(keycode: int, _: Any) -> None:
    if keycode == 65307:
        os._exit(0)


# def on_close(_: Any) -> None:
#     exit(0)


def main() -> None:
    print(sys.argv[0])
    if len(sys.argv) != 2:
        print("BOOM")
        return
    config = get_config(sys.argv[1])
    if config is None:
        print("ERROR: Error while parsing config file")
        return
    config.cell_width = WIDTH // config.width
    config.cell_height = HEIGHT // config.height
    config.fill_color = BLACK
    config.border_color = BLUE
    config.path_color = RED
    config.patter_color = GREEN
    config.menu_color = GREEN
    entry = config.entry
    exit = config.exit
    seed = config.seed
    random.seed(seed)
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
    gen.wilson_generate(grid, entry, config.height, config.width, ps)

    if not config.perfect:
        gen.break_perfect(grid.adj, ps, config.height)

    cells = grid.adj

    path = gen.bfs(grid, cells[entry[0]][entry[1]], cells[exit[0]][exit[1]])
    write_to_file(entry, exit, grid, path, config.output_file)
    for row in cells:
        for cell in row:
            cell.render(data_addr, line_len, bpp)
    m.mlx_string_put(mlx_ptr, win_ptr, 10, HEIGHT + 20, GREEN, "MENU")
    m.mlx_string_put(mlx_ptr, win_ptr, 10, HEIGHT + 40, GREEN, f"SEED: {seed}")
    m.mlx_string_put(mlx_ptr, win_ptr, 10, HEIGHT + 60, GREEN, "ESC. Quit")

    m.mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, 10, 10)

    m.mlx_key_hook(win_ptr, on_keypress, None)
    m.mlx_loop(mlx_ptr)


if __name__ == "__main__":
    main()
