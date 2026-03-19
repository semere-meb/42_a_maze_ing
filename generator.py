"""Maze data structures, generation, traversal, and rendering helpers."""

from typing import List, Any
from collections import defaultdict, deque
import random
import mlx


WHITE = 0xFFFFFF
BLACK = 0x000000
RED = 0xFF0000
GREEN = 0x00FF00
BLUE = 0x0000FF


def put_pixel(
    data_addr: memoryview,
    line_len: int,
    bpp: int,
    x: int,
    y: int,
    color: int,
) -> None:
    """Write a single RGBA pixel in the MLX image buffer.

    Args:
        data_addr: Raw writable image buffer.
        line_len: Number of bytes per image row.
        bpp: Bits per pixel.
        x: Horizontal pixel coordinate.
        y: Vertical pixel coordinate.
        color: RGB color as an integer.

    Returns:
        None.
    """
    offset = (y * line_len) + (x * (bpp // 8))
    data_addr[offset] = (color) & 0xFF  # B
    data_addr[offset + 1] = (color >> 8) & 0xFF  # G
    data_addr[offset + 2] = (color >> 16) & 0xFF  # R
    data_addr[offset + 3] = 0xFF  # A


def put_box(
    data_addr: memoryview,
    line_len: int,
    bpp: int,
    x: int,
    y: int,
    w: int,
    h: int,
    color: int,
) -> None:
    """Draw a filled rectangle into the MLX image buffer.

    Args:
        data_addr: Raw writable image buffer.
        line_len: Number of bytes per image row.
        bpp: Bits per pixel.
        x: Rectangle left coordinate.
        y: Rectangle top coordinate.
        w: Rectangle width in pixels.
        h: Rectangle height in pixels.
        color: RGB color as an integer.

    Returns:
        None.
    """
    for yy in range(h):
        for xx in range(w):
            put_pixel(data_addr, line_len, bpp, x + xx, y + yy, color)


def break_perfect(
    grid: List[List["Grid.Cell"]],
    ps: set[tuple[int, int]],
    height: int
) -> None:
    """Open one additional wall to break perfect-maze uniqueness.

    Args:
        grid: Matrix of maze cells.
        ps: Coordinates reserved for the closed "42" pattern.
        height: Maze height in number of rows.

    Returns:
        None.
    """
    for row in grid:
        for cell in row:
            h, w = cell.pos
            if cell.s and (h + 1, w) not in ps and h < height - 1:
                cell.s = False
                cell_below = grid[h + 1][w]
                cell_below.n = False
                return


class Grid:
    """Grid wrapper storing maze cells and derived adjacency relations."""

    adj: List[List["Cell"]]
    num_cells: int
    height: int
    width: int
    maze: bool
    adj_list: dict["Cell", List["Cell"]]

    def __init__(self, adj: List[List["Cell"]], height: int, width: int):
        """Initialize grid metadata and cell matrix.

        Args:
            adj: Two-dimensional matrix of Cell instances.
            height: Grid height in cells.
            width: Grid width in cells.
        """
        self.adj = adj
        self.num_cells = height * width
        self.width = width
        self.height = height
        self.maze = False

    def generate_adj_list(self) -> dict["Cell", List["Cell"]]:
        """Build adjacency list from currently open walls between cells.

        Returns:
            A mapping from each cell to neighboring reachable cells.
        """
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
        """Single maze cell with walls and rendering state."""

        pos: tuple[int, int]
        n: bool
        e: bool
        s: bool
        w: bool
        fill: bool
        pattern: bool

        def __init__(
            self,
            m: mlx.Mlx,
            mlx_ptr: memoryview,
            win_ptr: memoryview,
            pos: tuple[int, int],
            n: bool,
            e: bool,
            s: bool,
            w: bool,
            height: int,
            width: int,
        ) -> None:
            """Create a maze cell with initial wall and display values.

            Args:
                m: MLX instance.
                mlx_ptr: MLX context pointer.
                win_ptr: MLX window pointer.
                pos: Cell position as (row, column).
                n: Whether north wall is closed.
                e: Whether east wall is closed.
                s: Whether south wall is closed.
                w: Whether west wall is closed.
                height: Cell pixel height.
                width: Cell pixel width.

            Returns:
                None.
            """
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
            self.colors = [BLUE, WHITE, RED]
            self.path_colors = [0xffff00ff, BLACK]
            self.wall_color_ix = 0
            self.path_color_ix = 0

        def render(self,
                   data_addr: memoryview,
                   ll: int,
                   bpp: int,
                   wall_color: int,
                   path_color: int) -> None:
            """Render this cell and its walls into the image buffer.

            Args:
                data_addr: Raw writable image buffer.
                ll: Number of bytes per image row.
                bpp: Bits per pixel.

            Returns:
                None.
            """
            row, column = self.pos
            x = column * self.width
            y = row * self.height
            wall_size = self.width // 10
            if self.pattern:
                put_box(
                    data_addr,
                    ll,
                    bpp,
                    x,
                    y,
                    self.width,
                    self.height,
                    GREEN,
                )  # inner
                return

            if not self.path:    # non-path fill
                put_box(
                    data_addr,
                    ll,
                    bpp,
                    x + wall_size,
                    y + wall_size,
                    self.width - 2 * wall_size,
                    self.height - 2 * wall_size,
                    BLACK,
                )

            if self.path:    # path fill
                put_box(
                    data_addr,
                    ll,
                    bpp,
                    x + wall_size,
                    y + wall_size,
                    self.width - 2 * wall_size,
                    self.height - 2 * wall_size,
                    self.path_colors[self.path_color_ix],
                )

            if self.w:      # west wall
                put_box(
                    data_addr,
                    ll,
                    bpp,
                    x,
                    y,
                    wall_size,
                    self.height,
                    self.colors[self.wall_color_ix],
                )
            if self.e:      # east wall
                put_box(
                    data_addr,
                    ll,
                    bpp,
                    x + self.width - wall_size,
                    y,
                    wall_size,
                    self.height,
                    self.colors[self.wall_color_ix],
                )

            if self.n:      # north wall
                put_box(
                    data_addr,
                    ll,
                    bpp,
                    x,
                    y,
                    self.width,
                    wall_size,
                    self.colors[self.wall_color_ix],
                )
            if self.s:      # south wall
                put_box(
                    data_addr,
                    ll,
                    bpp,
                    x,
                    y + self.height - wall_size,
                    self.width,
                    wall_size,
                    self.colors[self.wall_color_ix],
                )

            def __hash__(self: "Grid.Cell") -> int:
                return hash(self.pos)


def bfs(grid: Grid, entry: Grid.Cell, exit: Grid.Cell) -> List[Grid.Cell]:
    """Compute and mark a shortest path from entry to exit.

    Args:
        grid: Grid containing the maze cells.
        entry: Starting cell.
        exit: Destination cell.

    Returns:
        The path as an ordered list of cells from entry to exit.
    """
    adj_list = grid.generate_adj_list()
    q = deque([entry])
    parent: dict[Grid.Cell, Any] = {entry: None}

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


def get_pattern_set(height: int, width: int) -> set[tuple[int, int]]:
    """Generate coordinates used to draw the closed-cell "42" pattern.

    Args:
        height: Maze height in cells.
        width: Maze width in cells.

    Returns:
        A set of (row, column) coordinates for the pattern.
    """
    pattern: set[tuple[int, int]] = set()
    if height < 6 or width < 8:
        print("Maze too small to draw the 42 pattern")
        return pattern
    top_left = ((height - 5) // 2, (width - 7) // 2)
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
    m: mlx.Mlx,
    mlx_ptr: memoryview,
    win_ptr: memoryview,
    cell_height: int,
    cell_width: int,
    ps: set[tuple[int, int]],
) -> Grid:
    """Build an all-walls-closed grid and mark pattern cells.

    Args:
        height: Maze height in cells.
        width: Maze width in cells.
        m: MLX instance.
        mlx_ptr: MLX context pointer.
        win_ptr: MLX window pointer.
        cell_height: Cell pixel height.
        cell_width: Cell pixel width.
        ps: Coordinates reserved for the closed "42" pattern.

    Returns:
        A Grid initialized with fresh Cell objects.
    """
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


def clear_grid(
    grid: Grid,
) -> None:
    """Build an all-walls-closed grid and mark pattern cells.

    Args:
        height: Maze height in cells.
        width: Maze width in cells.
        m: MLX instance.
        mlx_ptr: MLX context pointer.
        win_ptr: MLX window pointer.
        cell_height: Cell pixel height.
        cell_width: Cell pixel width.
        ps: Coordinates reserved for the closed "42" pattern.

    Returns:
        A Grid initialized with fresh Cell objects.
    """
    for row in grid.adj:
        for cell in row:
            cell.n, cell.e, cell.s, cell.w = True, True, True, True
            cell.path = False


def wilson_generate(
    grid: Grid,
    root: tuple[int, int],
    height: int,
    width: int,
    pattern_set: set[tuple[int, int]],
) -> None:
    """Generate a maze using Wilson's algorithm with loop erasure.

    Args:
        grid: Grid to mutate into a generated maze.
        root: Coordinate of the initial tree node.
        height: Maze height in cells.
        width: Maze width in cells.
        pattern_set: Coordinates reserved for the closed "42" pattern.

    Returns:
        None.
    """
    in_tree: dict[tuple[int, int], bool] = {}
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


def remove_wall(a: tuple[int, int], b: tuple[int, int], grid: Grid) -> None:
    """Open the shared wall between two orthogonally adjacent cells.

    Args:
        a: First cell coordinate.
        b: Second cell coordinate.
        grid: Grid containing both cells.

    Returns:
        None.
    """
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


def rand_neighbor(
    cell: tuple[int, int],
    grid: Grid,
    f: set[tuple[int, int]]
) -> tuple[int, int]:
    """Select a random valid neighbor not in the forbidden set.

    Args:
        cell: Source coordinate.
        grid: Grid boundaries provider.
        f: Set of coordinates to exclude from candidates.

    Returns:
        A randomly chosen neighboring coordinate.
    """
    r, c = cell
    neighbors: list[tuple[int, int]] = []

    if r - 1 >= 0 and (r - 1, c) not in f:
        neighbors.append((r - 1, c))
    if c - 1 >= 0 and (r, c - 1) not in f:
        neighbors.append((r, c - 1))
    if r + 1 < grid.height and (r + 1, c) not in f:
        neighbors.append((r + 1, c))
    if c + 1 < grid.width and (r, c + 1) not in f:
        neighbors.append((r, c + 1))
    return random.choice(neighbors)


def loop_erased_random_walk(
    start: tuple[int, int],
    in_tree: dict[tuple[int, int], bool],
    grid: Grid,
    pattern_set: set[tuple[int, int]],
) -> List[tuple[int, int]]:
    """Run a loop-erased random walk until reaching the current tree.

    Args:
        start: Starting coordinate for the walk.
        in_tree: Membership map of coordinates already in the maze tree.
        grid: Grid used to evaluate neighbor bounds.
        pattern_set: Coordinates reserved for the closed "42" pattern.

    Returns:
        Ordered list of coordinates describing the loop-erased walk.
    """
    current = start
    path: List[tuple[int, int]] = []
    visited_idx: dict[tuple[int, int], int] = {}

    while not in_tree[current]:
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
