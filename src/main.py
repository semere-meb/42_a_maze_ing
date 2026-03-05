import os

import mlx


def put_pixel(data_addr, line_len, bpp, x, y, color):
    offset = (y * line_len) + (x * (bpp // 8))
    data_addr[offset]     = (color)       & 0xFF  # B
    data_addr[offset + 1] = (color >> 8)  & 0xFF  # G
    data_addr[offset + 2] = (color >> 16) & 0xFF  # R
    data_addr[offset + 3] = 0xFF                  # A


def put_box(data_addr, line_len, bpp, x, y, w, h, color):
    for yy in range(h):
        for xx in range(w):
            put_pixel(data_addr, line_len, bpp, x+xx, y+yy, color)


def on_keypress(keycode, param):
    if keycode == 65307:
        os._exit(0)


def on_close(param):
    exit(0)


def main():
    WIDTH = 800
    HEIGHT = 600

    m = mlx.Mlx()
    mlx_ptr = m.mlx_init()
    win_ptr = m.mlx_new_window(mlx_ptr, WIDTH, HEIGHT, "a-maze-ing")
    img_ptr = m.mlx_new_image(mlx_ptr, WIDTH, HEIGHT)

    data_addr, bpp, line_len, endian = m.mlx_get_data_addr(img_ptr)

    put_box(data_addr, line_len, bpp, 0, 0, 10, 40, 0xFF0000)
    put_box(data_addr, line_len, bpp, 200, 40, 10, 20, 0x0000FF)

    m.mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, 0, 0)

    m.mlx_key_hook(win_ptr, on_keypress, None)
    m.mlx_loop(mlx_ptr)

if __name__ == "__main__":
    main()
