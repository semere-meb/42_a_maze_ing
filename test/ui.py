import os
import mlx

def on_keypress(keycode, param):
    if keycode == 65307:  # ESC
        os._exit(0)

def on_close(param):
    os._exit(0)

WIDTH = 800
HEIGHT = 600

m = mlx.Mlx()
mlx_ptr = m.mlx_init()
win_ptr = m.mlx_new_window(mlx_ptr, WIDTH, HEIGHT, "a-maze-ing")

m.mlx_key_hook(win_ptr, on_keypress, None)
m.mlx_hook(win_ptr, 17, 0, on_close, None)

m.mlx_loop(mlx_ptr)
