*This project has been created as part of the 42 curriculum by ryin & semebrah.*

# A-Maze-ing

A Python maze generator that creates random mazes using Wilson's algorithm, solves them with BFS, and provides an interactive graphical display via MiniLibX (MLX).

---

## Description

**A-Maze-ing** reads a configuration file, generates a random maze (optionally perfect), writes the result to a file using a hexadecimal wall-encoding format, and opens an interactive MLX window for visualization.

Key capabilities:

- Generate mazes of arbitrary size from a simple config file.
- Produce **perfect mazes** (exactly one path between any two cells) when the `PERFECT` flag is set.
- Embed a visible **"42" pattern** made of fully-closed cells in the centre of the maze (when dimensions allow).
- Solve the maze with BFS and export the shortest path as compass directions (`N`, `E`, `S`, `W`).
- Display the maze graphically with interactive controls for regeneration, colour cycling, and path toggling.

The generation logic is also packaged as a standalone, pip-installable library (`mazegen`) with no graphical dependencies, so it can be reused in other projects.

---

## Instructions

### Prerequisites

| Requirement | Notes |
|---|---|
| **Python** | >= 3.10 |
| **pipx** | Used to install `uv` |
| **uv** | Python package / venv manager (installed automatically by `make install`) |
| **MLX** | The local wheel `dist/mlx-2.2-py3-none-any.whl` must be present |

### Installation

```bash
make install
```

This creates a `.venv` virtual environment, installs `uv` via `pipx`, and syncs all dependencies (including the local MLX wheel).

### Running

```bash
make run
```

Or manually:

```bash
uv run ./a_maze_ing.py config.txt
```

Replace `config.txt` with any valid configuration file.

### Linting

```bash
make lint          # ruff + flake8 + mypy (recommended flags)
make lint-strict   # ruff + flake8 + mypy --strict
```

### Other Makefile targets

| Target | Description |
|---|---|
| `make run` | Install dependencies then run the program with `config.txt` |
| `make install` | Create venv and sync dependencies |
| `make clean` | Remove `__pycache__`, `.mypy_cache`, `.ruff_cache`, `.venv` |
| `make lint` | Run ruff, flake8, and mypy |
| `make lint-strict` | Same as `lint` with mypy `--strict` |
| `make format` | Auto-format source files with ruff |
| `make debug` | Run the program under `pdb` |
| `make reset-env` | Delete and recreate the virtual environment |
| `make re` | `clean` + `install` |

---

## Configuration File

The program takes a single argument: the path to a plain-text configuration file.

### Format

- One `KEY=VALUE` pair per line.
- Lines starting with `#` are comments and are ignored.
- Keys are case-insensitive.

### Mandatory keys

| Key | Type | Description | Example |
|---|---|---|---|
| `WIDTH` | integer | Number of columns (cells) | `WIDTH=20` |
| `HEIGHT` | integer | Number of rows (cells) | `HEIGHT=15` |
| `ENTRY` | x,y | Entry cell coordinates | `ENTRY=0,0` |
| `EXIT` | x,y | Exit cell coordinates | `EXIT=19,14` |
| `OUTPUT_FILE` | string | Path for the output maze file | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | boolean | Whether the maze must be perfect | `PERFECT=true` |

### Optional keys

| Key | Type | Description | Example |
|---|---|---|---|
| `SEED` | integer | RNG seed for reproducibility | `SEED=42` |

If `SEED` is omitted the default seed `42` is used.

### Default configuration file (`config.txt`)

```
WIDTH=6
HEIGHT=6
ENTRY=0,0
EXIT=5,5
OUTPUT_FILE=maze.txt
PERFECT=true
# SEED=10
```

---

## Maze Generation Algorithm

### Wilson's Algorithm (Loop-Erased Random Walk)

This project uses **Wilson's algorithm** to generate uniform spanning tree mazes.

#### How it works

1. Start with every cell fully walled. Mark one cell (the entry) as part of the tree.
2. Pick a random cell that is not yet in the tree.
3. Perform a **random walk** from that cell. If the walk revisits a cell, erase the loop (remove the cycle from the path).
4. When the walk reaches a cell that is already in the tree, add the entire loop-erased path to the tree by carving open the walls along it.
5. Repeat steps 2-4 until every non-pattern cell belongs to the tree.

#### Why Wilson's algorithm?

- **Unbiased**: It produces a uniform spanning tree, meaning every possible perfect maze is equally likely to be generated. Many other algorithms (like recursive backtracker or Prim's) have subtle biases that favour certain maze topologies.
- **Elegant correctness**: The loop-erasure step guarantees the result is always a spanning tree (i.e. a perfect maze) without requiring any post-processing or validity checks.
- **Educational value**: It demonstrates a non-trivial application of random walks and graph theory, which aligns well with the goals of the project.

The tradeoff is that Wilson's can be slower on very large grids because early random walks may take many steps before hitting the tree. In practice the performance is more than adequate for the maze sizes used in this project.

### Perfect vs. non-perfect mazes

When `PERFECT=true`, the maze generated by Wilson's algorithm is used as-is — there is exactly one path between any two cells.

When `PERFECT=false`, one additional wall is removed after generation (`break_perfect`), creating a cycle and thus multiple possible paths.

### Pathfinding: BFS

The shortest path from entry to exit is found using **breadth-first search** on the adjacency graph implied by the open walls. BFS guarantees the shortest path in an unweighted graph.

---

## Output File Format

The output file uses one hexadecimal digit per cell, encoding walls as a 4-bit value:

| Bit | Direction |
|---|---|
| 0 (LSB) | North |
| 1 | East |
| 2 | South |
| 3 (MSB) | West |

A **closed** wall sets the bit to `1`; an **open** passage sets it to `0`.

Examples:
- `3` (binary `0011`) — North and East walls closed, South and West open.
- `A` (binary `1010`) — East and West walls closed, North and South open.

Cells are written row by row, one row per line. After an empty line, three additional lines follow:

1. Entry coordinates (`row,col`)
2. Exit coordinates (`row,col`)
3. Shortest path as compass directions (`N`, `E`, `S`, `W`)

---

## Visual Representation

The program opens an MLX window displaying the maze graphically. Walls, the entry/exit, the "42" pattern, and the solution path are all visible.

### Interactive controls

| Key | Action |
|---|---|
| **ESC** | Quit the program |
| **R** | Regenerate the maze with a new random seed |
| **C** | Cycle wall colours (Blue -> White -> Red) |
| **P** | Toggle solution path colour (Yellow / Black) |

---

## Reusable Module — `mazegen`

The maze generation logic is available as a standalone Python package with **no graphical dependencies**. It lives in the `mazegen/` directory and can be built into a pip-installable `.whl` or `.tar.gz`.

### Building the package

```bash
cd mazegen
pip install build
python -m build
```

This produces files like `mazegen-1.0.0-py3-none-any.whl` and `mazegen-1.0.0.tar.gz` in `mazegen/dist/`.

### Installing

```bash
pip install mazegen/dist/mazegen-1.0.0-py3-none-any.whl
```

### API overview

The package exposes three classes: `MazeGenerator`, `Grid`, and `Cell`.

#### Quick start

```python
from mazegen import MazeGenerator

mg = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit=(14, 19),
    seed=42,
)

grid = mg.generate()
path = mg.solve()

for cell in path:
    print(cell.pos)
```

#### `MazeGenerator` parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `width` | `int` | — | Number of columns |
| `height` | `int` | — | Number of rows |
| `entry` | `tuple[int, int]` | — | `(row, col)` of the entrance |
| `exit` | `tuple[int, int]` | — | `(row, col)` of the exit |
| `seed` | `int \| None` | `None` | RNG seed for reproducibility |
| `pattern` | `bool` | `True` | Embed the "42" pattern if dimensions allow |

#### Key methods

- **`generate() -> Grid`** — Generates the maze using Wilson's algorithm. Returns the `Grid` object.
- **`solve() -> list[Cell]`** — Finds the shortest path from entry to exit via BFS. Must be called after `generate()`.
- **`get_cell(row, col) -> Cell`** — Returns the `Cell` at the given position.

#### Inspecting cells

Each `Cell` has boolean wall attributes (`n`, `e`, `s`, `w`), a `pos` tuple, a `pattern` flag, and a `path` flag (set after solving):

```python
cell = mg.get_cell(3, 7)
print(cell.n, cell.e, cell.s, cell.w)  # True/False for each wall
print(cell.pos)                         # (3, 7)
print(cell.path)                        # True if on the solution path
```

---

## Project Structure

```
maze/
├── a_maze_ing.py        # Main entry point (CLI + MLX rendering)
├── generator.py         # Grid, Cell, Wilson's algorithm, BFS, MLX rendering helpers
├── parser.py            # Config file parsing and validation
├── utils.py             # Hex encoding and file output
├── config.txt           # Default configuration file
├── Makefile             # Build, run, lint, clean targets
├── pyproject.toml       # Project metadata and dependencies
├── uv.lock              # Locked dependency versions
├── mlx.pyi              # Type stubs for MLX
├── .gitignore
├── dist/                # Local MLX wheel
│   └── mlx-2.2-py3-none-any.whl
└── mazegen/             # Reusable library (pip-installable)
    ├── pyproject.toml
    └── src/
        └── mazegen/
            ├── __init__.py
            └── generator.py
```

---

## Team & Project Management

### Team members

| Member |
|---|
| **ryin** | Generation and path-finding alog
| **semebrah** | Visualization and rendering integration with MLX

### Planning and evolution

The project was planned in phases:

1. **Config parsing** — Read and validate the configuration file with clear error messages.
2. **Maze generation** — Implement Wilson's algorithm with "42" pattern support.
3. **Output serialization** — Hex encoding, path directions, file writing.
4. **MLX visualization** — Interactive window with colour cycling, path toggle, and regeneration.
5. **Reusable library** — Extract pure-algorithm code into the `mazegen` package.
6. **Documentation** — This README and in-code docstrings.

The plan largely held, though visualization and interactive controls required more iteration than expected (colour state management, re-rendering on regeneration).

### What worked well

- Wilson's algorithm produced visually satisfying and provably unbiased mazes from the start.
- Separating the pure algorithm (`mazegen`) from the rendering (`generator.py` + MLX) kept the code clean and made the library reusable without graphical dependencies.
- Using `uv` for dependency management made environment setup fast and reproducible.

### What could be improved

- The main `generator.py` mixes algorithm logic with MLX rendering concerns; a stricter separation would make testing easier.
- Adding automated tests (pytest) for the generation and solving logic would increase confidence during refactoring.

### Tools used

| Tool | Purpose |
|---|---|
| **Python 3.10** | Implementation language |
| **uv** | Virtual environment and dependency management |
| **MiniLibX (MLX)** | Graphical window rendering |
| **flake8** | PEP 8 linting |
| **mypy** | Static type checking |
| **ruff** | Fast linting and formatting |
| **Git** | Version control |

---

## Resources

- [Wilson's Algorithm — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm#Wilson's_algorithm)
- [Maze Generation Algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Think Labyrinth — Walter Pullen](http://www.astrolog.org/labyrnth/algrithm.htm) — Comprehensive survey of maze algorithms
- [Jamis Buck — Maze Generation](https://weblog.jamisbuck.org/2011/1/20/maze-generation-algorithm-recap) — Visual explanations of common algorithms
- [BFS Shortest Path — GeeksforGeeks](https://www.geeksforgeeks.org/shortest-path-unweighted-graph/)
- [Python `random` module documentation](https://docs.python.org/3/library/random.html)
- [MiniLibX documentation](https://harm-smits.github.io/42docs/libs/minilibx)

### AI usage

AI tools were used to assist research. All source code, algorithm implementation, and architectural decisions were made by the team.
