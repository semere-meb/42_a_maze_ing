import os

import mlx

red = 0xFF0000
green = 0x00FF00
blue = 0x0000FF


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


class Cell:
    width: int
    height: int
    fill_color: int
    west: int
    south: int
    east: int
    north: int

    def __init__(self, m, mlx_ptr, win_ptr, width, height, row, column) -> None:
        self.m = m
        self.mlx_ptr = mlx_ptr
        self.win_ptr = win_ptr

        self.row = row
        self.column = column

        self.width = width
        self.height = height
        self.fill_color = blue
        self.west = red
        self.west = red
        self.west = red
        self.west = red
        self.render()

    def render(self) -> None:
        self.img_ptr = self.m.mlx_new_image(self.mlx_ptr, 800, 800)
        data_addr, bpp, line_len, endian = self.m.mlx_get_data_addr(self.img_ptr)

        # inner
        put_box( data_addr, line_len, bpp, 200 * self.row + 0, self.column * 200 + 0, 200, 200, red, )

        # west
        put_box( data_addr, line_len, bpp, 200 * self.row + 0, self.column * 200 + 0, 0 + 20, 200, blue, )

        # east
        put_box( data_addr, line_len, bpp, 200 * self.row + 200 - 20, self.column * 200 + 0, 0 + 20, 200, blue, )

        # north
        put_box( data_addr, line_len, bpp, 200 * self.row + 0 + 20, self.column * 200 + 0, 200 - 2 * 20, 0 + 20, blue, )

        # wouth
        put_box( data_addr, line_len, bpp, 200 * self.row + 20, self.column * 200 + 200 - 20, 200 - 2 * 20, 0 + 20, blue, )

        self.m.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr, self.img_ptr, 0, 0)


def main():
    WIDTH = 800
    HEIGHT = 800

    m = mlx.Mlx()
    mlx_ptr = m.mlx_init()
    win_ptr = m.mlx_new_window(mlx_ptr, WIDTH, HEIGHT, "a-maze-ing")

    cells = []
    for row in range(4):
        curr_row = []
        for column in range(4):
            curr_row.append(Cell(m, mlx_ptr, win_ptr, 200, 200, row, column))
        cells.append(row)

    m.mlx_key_hook(win_ptr, on_keypress, None)
    m.mlx_loop(mlx_ptr)


if __name__ == "__main__":
    main()
