#!/usr/bin/env python3

from typing import List
import random

class Grid:
    adj: List[List["Cell"]]
    num_cells: int
    height: int
    width: int

    def __init__(self, adj: List[List["Cell"]], height: int, width: int) -> None:
        self.adj = adj
        self.num_cells = height * width
        self.width = width
        self.height = height

    def display(self) -> None:
        """
        Renders the maze using Unicode box-drawing characters.
        Assumptions:
          - self.adj is a height x width 2D list of Cell
          - cell.n/e/s/w == True means "there IS a wall" on that side.
        """
        H, W = self.height, self.width

        # 2H+1 by 2W+1 canvas of box-drawing junctions/lines/spaces
        rows = 2 * H + 1
        cols = 2 * W + 1
        canvas = [[" " for _ in range(cols)] for __ in range(rows)]

        # Helpers to place line glyphs; we build edges first, then compute junctions.
        def hline(r: int, c0: int, c1: int) -> None:
            for c in range(c0, c1 + 1):
                canvas[r][c] = "─"

        def vline(c: int, r0: int, r1: int) -> None:
            for r in range(r0, r1 + 1):
                canvas[r][c] = "│"

        # Draw border + internal walls.
        for r in range(H):
            for c in range(W):
                cell = self.adj[r][c]
                cr = 2 * r + 1
                cc = 2 * c + 1

                # Top wall
                if cell.n:
                    hline(cr - 1, cc, cc + 1)
                # Bottom wall
                if cell.s:
                    hline(cr + 1, cc, cc + 1)
                # Left wall
                if cell.w:
                    vline(cc - 1, cr, cr + 1)
                # Right wall
                if cell.e:
                    vline(cc + 1, cr, cr + 1)

        # Ensure outer border is closed if your cells don't already encode it.
        # (Safe even if already drawn.)
        hline(0, 0, cols - 1)
        hline(rows - 1, 0, cols - 1)
        vline(0, 0, rows - 1)
        vline(cols - 1, 0, rows - 1)

        # Convert line crossings into proper junction glyphs.
        # For each intersection point (even-even indices), decide which directions connect.
        def is_h(r: int, c: int) -> bool:
            return 0 <= r < rows and 0 <= c < cols and canvas[r][c] == "─"

        def is_v(r: int, c: int) -> bool:
            return 0 <= r < rows and 0 <= c < cols and canvas[r][c] == "│"

        junction_map = {
            (True,  True,  True,  True):  "┼",  # U D L R
            (True,  True,  True,  False): "┤",
            (True,  True,  False, True):  "├",
            (True,  False, True,  True):  "┴",
            (False, True,  True,  True):  "┬",
            (True,  True,  False, False): "│",
            (False, False, True,  True):  "─",
            (True,  False, True,  False): "┘",
            (True,  False, False, True):  "└",
            (False, True,  True,  False): "┐",
            (False, True,  False, True):  "┌",
            (True,  False, False, False): "│",
            (False, True,  False, False): "│",
            (False, False, True,  False): "─",
            (False, False, False, True):  "─",
            (False, False, False, False): " ",
        }

        for r in range(0, rows, 2):
            for c in range(0, cols, 2):
                up = is_v(r - 1, c)
                down = is_v(r + 1, c)
                left = is_h(r, c - 1)
                right = is_h(r, c + 1)

                # Also treat directly adjacent line glyphs (some walls are drawn on odd coords)
                # so corners don't get missed.
                if not left and c - 1 >= 0 and canvas[r][c - 1] == "─":
                    left = True
                if not right and c + 1 < cols and canvas[r][c + 1] == "─":
                    right = True
                if not up and r - 1 >= 0 and canvas[r - 1][c] == "│":
                    up = True
                if not down and r + 1 < rows and canvas[r + 1][c] == "│":
                    down = True

                canvas[r][c] = junction_map[(up, down, left, right)]

        print("\n".join("".join(row) for row in canvas))   

    class Cell:
        pos: tuple[int]
        n: bool
        e: bool
        s: bool
        w: bool

        def __init__(self, pos: tuple[int], n: bool, e: bool, s: bool, w: bool) -> None:
            self.pos = pos
            self.n = n
            self.e = e
            self.s = s
            self.w = w

           

def generate_grid(height: int, width: int) -> Grid:
    out = []
    for i in range(height):
        sub = []
        for j in range(width):
            sub.append(Grid.Cell((i,j), True, True, True, True))
        out.append(sub)
    return Grid(out, height, width)

def wilson_generate(grid: Grid, root: tuple, height: int, width: int) -> None:
    in_tree = {}
    for cell in [c for row in grid.adj for c in row]:
        in_tree[cell.pos] = False

    in_tree[root] = True    

    while any(v is False for v in in_tree.values()):
        start = random.choice([k for k, v in in_tree.items() if not v])        
        path = loop_erased_random_walk(start, in_tree, grid)

        for i in range(len(path) - 1):
            a = path[i]
            b = path[i + 1]

            remove_wall(a, b, grid)
            in_tree[a] = True

        in_tree[path[-1]] = True

def remove_wall(a: tuple[int], b: tuple[int], grid: Grid) -> None:
    r, c = a[0] - b[0], a[1] - b[1]
    cell_a = grid.adj[a[0]][a[1]] # instance of Cell object
    cell_b = grid.adj[b[0]][b[1]]
    if r < 0:
        cell_a.s ,cell_b.n = False, False
    if r > 0:
        cell_a.n, cell_b.s = False, False
    if c < 0:
        cell_a.e, cell_b.w = False, False
    if c > 0:
        cell_a.w, cell_b.e = False, False
        

def rand_neighbor(cell: tuple[int], grid: Grid) -> tuple[int]:
    r, c = cell
    neighbors = []

    if r - 1 >= 0:
        neighbors.append((r - 1, c))
    if c - 1 >= 0:
        neighbors.append((r, c - 1))
    if r + 1 < grid.height:
        neighbors.append((r + 1, c))
    if c + 1 < grid.width:
        neighbors.append((r, c + 1))

    return random.choice(neighbors)
    

def loop_erased_random_walk(start: tuple[int], in_tree: dict, grid: Grid) -> List[tuple[int]]:
    current = start
    path = []
    visited_idx = {}

    while in_tree[current] == False:
        if current in visited_idx.keys():
            loop_start_idx = visited_idx[current]

            path = path[:loop_start_idx + 1]

            visited_idx = {}
            for i in range(len(path)):
                visited_idx[path[i]] = i
        else:
            visited_idx[current] = len(path)
            path.append(current)
        next = rand_neighbor(current, grid)    
        current = next

    path.append(current)
    print("LERW RAN")
    return path

def main():
    grid = generate_grid(15,45)
    for sub in grid.adj:
        for cell in sub:
            print(cell.pos, (cell.n, cell.e, cell.s, cell.w), sep='->')
        print("")

    wilson_generate(grid, (0,0), 15, 45)
    for sub in grid.adj:
        for cell in sub:
            print(cell.pos, (cell.n, cell.e, cell.s, cell.w), sep='->')
        print("")

    grid.display()

if __name__ == "__main__":
    main()
