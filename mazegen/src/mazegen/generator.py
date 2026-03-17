"""Pure-algorithm maze generation module (no rendering dependencies).

Contains the Cell, Grid, and MazeGenerator classes along with Wilson's
algorithm and BFS pathfinding.
"""

from __future__ import annotations

from typing import List
from collections import defaultdict, deque
import random


class Cell:
    """Single cell in a maze grid.

    Attributes:
        pos: ``(row, col)`` position in the grid.
        n: North wall present.
        e: East wall present.
        s: South wall present.
        w: West wall present.
        pattern: Whether this cell is part of the "42" pattern.
        path: Whether this cell lies on the solved path.
    """

    def __init__(
        self,
        pos: tuple[int, int],
        n: bool = True,
        e: bool = True,
        s: bool = True,
        w: bool = True,
    ) -> None:
        """Initialise a cell.

        Args:
            pos: ``(row, col)`` position within the grid.
            n: North wall present (default ``True``).
            e: East wall present (default ``True``).
            s: South wall present (default ``True``).
            w: West wall present (default ``True``).
        """
        self.pos = pos
        self.n = n
        self.e = e
        self.s = s
        self.w = w
        self.pattern: bool = False
        self.path: bool = False

    def __hash__(self) -> int:
        return hash(self.pos)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Cell):
            return NotImplemented
        return self.pos == other.pos

    def __repr__(self) -> str:
        return (
            f"Cell(pos={self.pos}, "
            f"walls=NESW({self.n},{self.e},{self.s},{self.w}))"
        )


class Grid:
    """Two-dimensional grid of ``Cell`` objects representing a maze.

    Attributes:
        adj: 2-D list of cells indexed ``[row][col]``.
        num_cells: Total number of cells (height * width).
        height: Number of rows.
        width: Number of columns.
        maze: ``True`` once Wilson's algorithm has been applied.
    """

    def __init__(
        self, adj: List[List[Cell]], height: int, width: int
    ) -> None:
        """Initialise the grid.

        Args:
            adj: Pre-built 2-D list of Cell objects.
            height: Number of rows in the grid.
            width: Number of columns in the grid.
        """
        self.adj = adj
        self.num_cells = height * width
        self.width = width
        self.height = height
        self.maze: bool = False

    def generate_adj_list(self) -> dict[Cell, List[Cell]]:
        """Build an adjacency list from the current wall state.

        A neighbour is reachable when the wall between the two cells is
        open.

        Returns:
            Dictionary mapping each Cell to a list of reachable neighbours.
        """
        adj_list: dict[Cell, List[Cell]] = defaultdict(list)
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
        return adj_list


# ---------------------------------------------------------------------------
# Internal helpers (prefixed with _)
# ---------------------------------------------------------------------------

def _get_pattern_set(height: int, width: int) -> set[tuple[int, int]]:
    """Compute cell positions that form the "42" pattern.

    Returns an empty set when the grid is too small (height < 9 or
    width < 7).

    Args:
        height: Number of rows.
        width: Number of columns.

    Returns:
        Set of ``(row, col)`` tuples belonging to the pattern.
    """
    pattern: set[tuple[int, int]] = set()
    if height < 9 or width < 7:
        return pattern
    top_left = ((height - 5) // 2, (width - 7) // 2)
    # "4"
    pattern.add(top_left)
    pattern.add((top_left[0] + 1, top_left[1]))
    pattern.add((top_left[0] + 2, top_left[1]))
    pattern.add((top_left[0] + 2, top_left[1] + 1))
    pattern.add((top_left[0] + 2, top_left[1] + 2))
    pattern.add((top_left[0] + 3, top_left[1] + 2))
    pattern.add((top_left[0] + 4, top_left[1] + 2))
    # "2"
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


def _generate_grid(
    height: int, width: int, pattern_set: set[tuple[int, int]]
) -> Grid:
    """Create a grid with all walls closed.

    Args:
        height: Number of rows.
        width: Number of columns.
        pattern_set: Positions belonging to the "42" pattern.

    Returns:
        Fully initialised Grid.
    """
    out: List[List[Cell]] = []
    for i in range(height):
        sub: List[Cell] = []
        for j in range(width):
            cell = Cell((i, j))
            if (i, j) in pattern_set:
                cell.pattern = True
            sub.append(cell)
        out.append(sub)
    return Grid(out, height, width)


def _remove_wall(
    a: tuple[int, int], b: tuple[int, int], grid: Grid
) -> None:
    """Remove the shared wall between two adjacent cells.

    Args:
        a: ``(row, col)`` of the first cell.
        b: ``(row, col)`` of the second cell.
        grid: Grid containing both cells.
    """
    r, c = a[0] - b[0], a[1] - b[1]
    cell_a = grid.adj[a[0]][a[1]]
    cell_b = grid.adj[b[0]][b[1]]
    if r < 0:
        cell_a.s, cell_b.n = False, False
    if r > 0:
        cell_a.n, cell_b.s = False, False
    if c < 0:
        cell_a.e, cell_b.w = False, False
    if c > 0:
        cell_a.w, cell_b.e = False, False


def _rand_neighbor(
    cell: tuple[int, int],
    grid: Grid,
    forbidden: set[tuple[int, int]],
) -> tuple[int, int]:
    """Return a random cardinal neighbour not in *forbidden*.

    Args:
        cell: ``(row, col)`` of the current cell.
        grid: Grid (used for boundary checks).
        forbidden: Positions to exclude (pattern cells).

    Returns:
        ``(row, col)`` of a randomly chosen valid neighbour.
    """
    r, c = cell
    neighbors: list[tuple[int, int]] = []
    if r - 1 >= 0 and (r - 1, c) not in forbidden:
        neighbors.append((r - 1, c))
    if c - 1 >= 0 and (r, c - 1) not in forbidden:
        neighbors.append((r, c - 1))
    if r + 1 < grid.height and (r + 1, c) not in forbidden:
        neighbors.append((r + 1, c))
    if c + 1 < grid.width and (r, c + 1) not in forbidden:
        neighbors.append((r, c + 1))
    return random.choice(neighbors)


def _loop_erased_random_walk(
    start: tuple[int, int],
    in_tree: dict[tuple[int, int], bool],
    grid: Grid,
    pattern_set: set[tuple[int, int]],
) -> List[tuple[int, int]]:
    """Perform a loop-erased random walk until a tree cell is reached.

    Args:
        start: Walk origin.
        in_tree: Maps positions to tree membership.
        grid: The maze grid.
        pattern_set: Forbidden positions to avoid.

    Returns:
        Self-avoiding path ending at a cell already in the tree.
    """
    current = start
    path: list[tuple[int, int]] = []
    visited_idx: dict[tuple[int, int], int] = {}

    while in_tree[current] is False:
        if current in visited_idx:
            loop_start_idx = visited_idx[current]
            path = path[: loop_start_idx + 1]
            visited_idx = {}
            for i in range(len(path)):
                visited_idx[path[i]] = i
        else:
            visited_idx[current] = len(path)
            path.append(current)

        next_cell = _rand_neighbor(current, grid, pattern_set)
        current = next_cell

    path.append(current)
    return path


def _wilson_generate(
    grid: Grid,
    root: tuple[int, int],
    pattern_set: set[tuple[int, int]],
) -> None:
    """Carve a perfect maze using Wilson's algorithm.

    Args:
        grid: Grid whose walls will be carved.
        root: Initial tree cell (typically the entry).
        pattern_set: Pattern cell positions to exclude.
    """
    in_tree: dict[tuple[int, int], bool] = {}
    for cell in [c for row in grid.adj for c in row]:
        if cell.pattern:
            continue
        in_tree[cell.pos] = False

    in_tree[root] = True

    while any(v is False for v in in_tree.values()):
        start = random.choice(
            [k for k, v in in_tree.items() if not v]
        )
        path = _loop_erased_random_walk(
            start, in_tree, grid, pattern_set
        )
        for i in range(len(path) - 1):
            _remove_wall(path[i], path[i + 1], grid)
            in_tree[path[i]] = True
        in_tree[path[-1]] = True

    grid.maze = True


def _bfs(grid: Grid, entry: Cell, exit_cell: Cell) -> List[Cell]:
    """Find the shortest path via breadth-first search.

    Cells on the path have their ``path`` attribute set to ``True``.

    Args:
        grid: The maze grid.
        entry: Starting cell.
        exit_cell: Target cell.

    Returns:
        Ordered list of cells from *entry* to *exit_cell*.
    """
    adj_list = grid.generate_adj_list()
    q: deque[Cell] = deque([entry])
    parent: dict[Cell, Cell | None] = {entry: None}

    while len(q):
        curr = q.popleft()
        if curr == exit_cell:
            break
        for neighbor in adj_list[curr]:
            if neighbor not in parent:
                parent[neighbor] = curr
                q.append(neighbor)

    path: list[Cell] = []
    curr = exit_cell
    while curr:
        curr.path = True
        path.append(curr)
        curr = parent[curr]  # type: ignore[assignment]
    path.reverse()
    return path


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class MazeGenerator:
    """High-level facade for maze generation and solving.

    Wraps grid construction, Wilson's algorithm, and BFS into a single
    class with no rendering dependencies.

    Attributes:
        width: Number of columns.
        height: Number of rows.
        entry: ``(row, col)`` of the maze entrance.
        exit: ``(row, col)`` of the maze exit.
        seed: Optional RNG seed for reproducibility.
        pattern: Whether to embed the "42" pattern.
        grid: The generated ``Grid`` (available after ``generate()``).
        solution: Solved path (available after ``solve()``).

    Example::

        from mazegen import MazeGenerator

        mg = MazeGenerator(width=20, height=15,
                           entry=(0, 0), exit=(14, 19), seed=42)
        grid = mg.generate()
        path  = mg.solve()

        # Inspect a cell
        cell = mg.get_cell(3, 7)
        print(cell.n, cell.e, cell.s, cell.w)

        # Iterate the solution
        for cell in path:
            print(cell.pos)
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit: tuple[int, int],
        seed: int | None = None,
        pattern: bool = True,
    ) -> None:
        """Initialise the generator.

        Args:
            width: Number of columns in the maze.
            height: Number of rows in the maze.
            entry: ``(row, col)`` of the entrance.
            exit: ``(row, col)`` of the exit.
            seed: Optional random seed for reproducible mazes.
            pattern: If ``True``, embed the "42" pattern (when
                dimensions allow).
        """
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.seed = seed
        self.pattern = pattern
        self.grid: Grid | None = None
        self.solution: List[Cell] | None = None

    def generate(self) -> Grid:
        """Generate the maze using Wilson's algorithm.

        Seeds the RNG if a seed was provided, builds the grid, and carves
        passages.

        Returns:
            The generated ``Grid``.

        Raises:
            ValueError: If entry or exit are out of bounds.
        """
        if self.seed is not None:
            random.seed(self.seed)

        if not (0 <= self.entry[0] < self.height
                and 0 <= self.entry[1] < self.width):
            raise ValueError(
                f"Entry {self.entry} is outside grid bounds "
                f"({self.height}x{self.width})"
            )
        if not (0 <= self.exit[0] < self.height
                and 0 <= self.exit[1] < self.width):
            raise ValueError(
                f"Exit {self.exit} is outside grid bounds "
                f"({self.height}x{self.width})"
            )

        ps = (
            _get_pattern_set(self.height, self.width)
            if self.pattern
            else set()
        )
        self.grid = _generate_grid(self.height, self.width, ps)
        _wilson_generate(self.grid, self.entry, ps)
        return self.grid

    def solve(self) -> List[Cell]:
        """Find the shortest path from entry to exit using BFS.

        Returns:
            Ordered list of ``Cell`` objects from entry to exit.

        Raises:
            RuntimeError: If ``generate()`` has not been called yet.
        """
        if self.grid is None:
            raise RuntimeError(
                "Maze not generated yet. Call generate() first."
            )
        entry_cell = self.grid.adj[self.entry[0]][self.entry[1]]
        exit_cell = self.grid.adj[self.exit[0]][self.exit[1]]
        self.solution = _bfs(self.grid, entry_cell, exit_cell)
        return self.solution

    def get_cell(self, row: int, col: int) -> Cell:
        """Return the ``Cell`` at the given position.

        Args:
            row: Row index.
            col: Column index.

        Returns:
            The ``Cell`` object at ``(row, col)``.

        Raises:
            RuntimeError: If ``generate()`` has not been called yet.
        """
        if self.grid is None:
            raise RuntimeError(
                "Maze not generated yet. Call generate() first."
            )
        return self.grid.adj[row][col]
