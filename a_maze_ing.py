#!/usr/bin/env python3

"""Entry point for maze generation and interactive rendering."""
from typing import Any

import os
import sys
import mlx
import generator as gen
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


def reseed(param):
    config = param['config']
    mlx_ptr = param['mlx_ptr']
    win_ptr = param['win_ptr']
    data_addr = param['data_addr']
    line_len = param['line_len']
    bpp = param['bpp']
    win_ptr = param['win_ptr']
    m = param['m']
    entry = config.entry
    exit = config.exit
    grid = param['grid']
    random.seed(random.randint(1, 1000))

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
    gen.wilson_generate(grid, config.entry, config.height, config.width, ps)

    if not config.perfect:
        gen.break_perfect(grid.adj, ps, config.height)

    cells = grid.adj

    path = gen.bfs(grid, cells[entry[0]][entry[1]], cells[exit[0]][exit[1]])
    write_to_file(entry, exit, grid, path, config.output_file)
    for row in cells:
        for cell in row:
            cell.render(data_addr, line_len, bpp,
                        cell.colors[cell.wall_color_ix],
                        cell.path_colors[cell.path_color_ix],
                        )


def on_keypress(keycode: int, param: dict[str, Any]) -> None:
    """Handle keyboard events for the rendering window.

    Args:
        keycode: Numeric key code received from the window system.
        _: Unused callback payload required by the hook signature.

    Returns:
        None.
    """
    m = param['m']
    win_ptr = param['win_ptr']
    mlx_ptr = param['mlx_ptr']
    img_ptr = param['img_ptr']
    data_addr = param['data_addr']
    line_len = param['line_len']
    bpp = param['bpp']

    if keycode == 65307:    # ESC
        os._exit(0)

    if keycode == 114:    # R
        # print("rerender with a new seed")
        for y in range(HEIGHT):
            for x in range(WIDTH):
                gen.put_pixel(data_addr, line_len, bpp,  x, y, 0x000000)
        reseed(param)

    elif keycode == 99:    # C
        for row in param['grid'].adj:
            for cell in row:
                cell.wall_color_ix = (cell.wall_color_ix + 1) % 3
                cell.render(
                            param['data_addr'],
                            param['line_len'],
                            param['bpp'],
                            cell.colors[cell.wall_color_ix],
                            cell.path_colors[cell.path_color_ix],
                            )

    elif keycode == 112:    # P
        for cell in param['path']:
            cell.path_color_ix = (cell.path_color_ix + 1) % 2
            cell.render(
                        param['data_addr'],
                        param['line_len'],
                        param['bpp'],
                        cell.colors[cell.wall_color_ix],
                        cell.path_colors[cell.path_color_ix],
                        )

    m.mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, 10, 10)


def main() -> None:
    """Run the full maze generation workflow from CLI config.

    Reads configuration, generates and optionally alters the maze, writes the
    serialized output file, and launches an MLX window to render the result.

    Returns:
        None.
    """
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
            cell.render(data_addr, line_len, bpp,
                        cell.colors[cell.wall_color_ix],
                        cell.path_colors[cell.path_color_ix],
                        )
    m.mlx_string_put(mlx_ptr, win_ptr, 10, HEIGHT + 20, GREEN, "MENU")
    # m.mlx_string_put(mlx_ptr, win_ptr, 10, HEIGHT + 40, GREEN, f"SEED: {seed}")
    m.mlx_string_put(mlx_ptr, win_ptr, 10, HEIGHT + 60, GREEN, "ESC. Quit")
    m.mlx_string_put(mlx_ptr, win_ptr, 10, HEIGHT + 80, GREEN,
                     "C. Change wall colors")
    m.mlx_string_put(mlx_ptr, win_ptr, 10, HEIGHT + 100, GREEN,
                     "P. Toggle path color")

    m.mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, 10, 10)

    m.mlx_key_hook(win_ptr, on_keypress, {
                       "m": m,
                       "mlx_ptr": mlx_ptr,
                       "win_ptr": win_ptr,
                       "img_ptr": img_ptr,
                       "grid": grid,
                       "data_addr": data_addr,
                       "line_len": line_len,
                       "bpp": bpp,
                       'path': path,
                       'config': config
                   })
    m.mlx_loop(mlx_ptr)


if __name__ == "__main__":
    main()
