#!/usr/bin/env python3

from typing import List
from collections import defaultdict, deque
import time
import random
import os


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


class Grid:
    adj: List[List["Cell"]]
    num_cells: int
    height: int
    width: int
    maze: bool
    adj_list: dict[List["Cell"]]

    def __init__(self, adj: List[List["Cell"]], height: int, width: int) -> None:
        self.adj = adj
        self.num_cells = height * width
        self.width = width
        self.height = height
        self.maze = False

    def generate_adj_list(self) -> dict[List["Cell"]]:
        adj_list = defaultdict(list)
        for row in self.adj:
            for c in row:
                if not c.n:
                    adj_list[c].append(self.adj[c.pos[0] - 1][c.pos[1]])
                if not c.e:
                    adj_list[c].append(self.adj[c.pos[0]][c.pos[1] + 1])
                if not c.s:
                    adj_list[c].append(self.adj[c.pos[0] + 1][c.pos[1]])
                if not c.w:
                    adj_list[c].append(self.adj[c.pos[0]][c.pos[1] - 1])
        self.adj_list = adj_list
        return adj_list

    class Cell:
        pos: tuple[int]
        n: bool
        e: bool
        s: bool
        w: bool
        fill: bool
        pattern: bool

        def __init__(
            self,
            m,
            mlx_ptr,
            win_ptr,
            pos: tuple[int],
            n: bool,
            e: bool,
            s: bool,
            w: bool,
            height: int,
            width: int,
        ) -> None:
            self.m = m
            self.mlx_ptr = mlx_ptr
            self.win_ptr = win_ptr

            self.height = height
            self.width = width
            self.pos = pos
            self.n = n
            self.e = e
            self.s = s
            self.w = w
            self.fill = False
            self.pattern = False
            self.path = False

        def render(self, data_addr, line_len, bpp) -> None:
            row, column = self.pos
            x = column * self.width
            y = row * self.height
            wall_size = self.width // 20
            if self.pattern:
                put_box(
                    data_addr, line_len, bpp, x, y, self.width, self.height, GREEN
                )  # inner
                return

            put_box(
                data_addr,
                line_len,
                bpp,
                x + wall_size,
                y + wall_size,
                self.width - 2 * wall_size,
                self.height - 2 * wall_size,
                BLACK if not self.path else WHITE,
            )  # inner

            self.w and put_box(
                data_addr, line_len, bpp, x, y, wall_size, self.height, RED
            )  # west
            
            not self.w and self.path and put_box(
                data_addr, line_len, bpp, x, y, wall_size, self.height, WHITE
            )  # west
            self.e and put_box(
                data_addr,
                line_len,
                bpp,
                x + self.width - wall_size,
                y,
                wall_size,
                self.height,
                RED,
            )  # east
            not self.e and self.path and put_box(
                data_addr,
                line_len,
                bpp,
                x + self.width - wall_size,
                y,
                wall_size,
                self.height,
                WHITE,
            )  # east

            self.n and put_box(
                data_addr, line_len, bpp, x, y, self.width, wall_size, RED
            )  # north
            not self.n and self.path and put_box(
                data_addr, line_len, bpp, x, y, self.width, wall_size, WHITE
            )  # north

            self.s and put_box(
                data_addr,
                line_len,
                bpp,
                x,
                y + self.height - wall_size,
                self.width,
                wall_size,
                RED,
            )  # south
            not self.s and self.path and put_box(
                data_addr,
                line_len,
                bpp,
                x,
                y + self.height - wall_size,
                self.width,
                wall_size,
                WHITE,
            )  # south

            def __hash__(self):
                return hash(self.pos)


def bfs(grid: Grid, entry: Grid.Cell, exit: Grid.Cell) -> List[Grid.Cell]:
    adj_list = grid.generate_adj_list()
    q = deque([entry])
    visited = set([entry])
    parent = {entry: None}

    while len(q):
        curr = q.popleft()

        if curr == exit:
            break
        for neighbor in adj_list[curr]:
            if neighbor not in parent.keys():
                parent[neighbor] = curr
                q.append(neighbor)
    path = []
    curr = exit
    while curr:
        curr.path = True
        path.append(curr)
        curr = parent[curr]
    path.reverse()
    return path


def get_pattern_set(height: int, width: int) -> set[tuple]:
    pattern = set()
    if height < 9 or width < 7:
        return pattern
    top_left = (height // 2 - 2, width // 2 - 2)
    # four
    pattern.add(top_left)
    pattern.add((top_left[0] + 1, top_left[1]))
    pattern.add((top_left[0] + 2, top_left[1]))
    pattern.add((top_left[0] + 2, top_left[1] + 1))
    pattern.add((top_left[0] + 2, top_left[1] + 2))
    pattern.add((top_left[0] + 3, top_left[1] + 2))
    pattern.add((top_left[0] + 4, top_left[1] + 2))

    # two
    pattern.add((top_left[0], top_left[1] + 4))
    pattern.add((top_left[0], top_left[1] + 5))
    pattern.add((top_left[0], top_left[1] + 6))
    pattern.add((top_left[0] + 1, top_left[1] + 6))
    pattern.add((top_left[0] + 2, top_left[1] + 6))
    pattern.add((top_left[0] + 2, top_left[1] + 5))
    pattern.add((top_left[0] + 2, top_left[1] + 4))
    pattern.add((top_left[0] + 3, top_left[1] + 4))
    pattern.add((top_left[0] + 4, top_left[1] + 4))
    pattern.add((top_left[0] + 4, top_left[1] + 5))
    pattern.add((top_left[0] + 4, top_left[1] + 6))
    return pattern


def generate_grid(
    height: int,
    width: int,
    m,
    mlx_ptr,
    win_ptr,
    cell_height: int,
    cell_width: int,
    ps: set,
) -> Grid:
    out = []
    pattern_set = ps
    # pattern_set = {}
    for i in range(height):
        sub = []
        for j in range(width):
            cell = Grid.Cell(
                m,
                mlx_ptr,
                win_ptr,
                (i, j),
                True,
                True,
                True,
                True,
                cell_height,
                cell_width,
            )
            if (i, j) in pattern_set:
                cell.pattern = True
            sub.append(cell)
        out.append(sub)
    return Grid(out, height, width)


def wilson_generate(
    grid: Grid, root: tuple, height: int, width: int, pattern_set: set
) -> None:
    in_tree = {}
    forbidden = pattern_set
    for cell in [c for row in grid.adj for c in row]:
        if cell.pattern:
            continue
        in_tree[cell.pos] = False

    in_tree[root] = True

    while any(v is False for v in in_tree.values()):
        start = random.choice([k for k, v in in_tree.items() if not v])
        path = loop_erased_random_walk(start, in_tree, grid, pattern_set)

        for i in range(len(path) - 1):
            a = path[i]
            b = path[i + 1]

            remove_wall(a, b, grid)
            in_tree[a] = True

        in_tree[path[-1]] = True
    grid.maze = True


def remove_wall(a: tuple[int], b: tuple[int], grid: Grid) -> None:
    r, c = a[0] - b[0], a[1] - b[1]
    cell_a = grid.adj[a[0]][a[1]]  # instance of Cell object
    cell_b = grid.adj[b[0]][b[1]]
    if r < 0:
        cell_a.s, cell_b.n = False, False
    if r > 0:
        cell_a.n, cell_b.s = False, False
    if c < 0:
        cell_a.e, cell_b.w = False, False
    if c > 0:
        cell_a.w, cell_b.e = False, False


def rand_neighbor(cell: tuple[int], grid: Grid, forbidden: dict) -> tuple[int]:
    r, c = cell
    neighbors = []

    if r - 1 >= 0 and (r - 1, c) not in forbidden:
        neighbors.append((r - 1, c))
    if c - 1 >= 0 and (r, c - 1) not in forbidden:
        neighbors.append((r, c - 1))
    if r + 1 < grid.height and (r + 1, c) not in forbidden:
        neighbors.append((r + 1, c))
    if c + 1 < grid.width and (r, c + 1) not in forbidden:
        neighbors.append((r, c + 1))
    return random.choice(neighbors)


def loop_erased_random_walk(
    start: tuple[int], in_tree: dict, grid: Grid, pattern_set: set
) -> List[tuple[int]]:
    current = start
    path = []
    visited_idx = {}

    while in_tree[current] == False:
        if current in visited_idx.keys():
            loop_start_idx = visited_idx[current]

            path = path[: loop_start_idx + 1]

            visited_idx = {}
            for i in range(len(path)):
                visited_idx[path[i]] = i
        else:
            visited_idx[current] = len(path)
            path.append(current)

        next = rand_neighbor(current, grid, pattern_set)
        current = next

    path.append(current)
    return path


def main():
    grid = generate_grid(5, 15)

    wilson_generate(grid, (0, 0), 5, 15)
    for sub in grid.adj:
        for cell in sub:
            print(cell.pos, (cell.n, cell.e, cell.s, cell.w), sep="->")
        print("")

    grid.display()

    adj_list = grid.generate_adj_list()
    path = bfs(grid, grid.adj[0][0], grid.adj[4][4])
    print("AFTER BFS")
    for i in path:
        print(i.pos, end=" ")
    print("")


if __name__ == "__main__":
    main()
