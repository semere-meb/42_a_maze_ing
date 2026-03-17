"""mazegen — Reusable maze generation and solving library.

Provides the ``MazeGenerator`` class for creating perfect mazes using
Wilson's algorithm and finding shortest paths with BFS.  No graphical
dependencies — pure Python.

Quick start::

    from mazegen import MazeGenerator

    mg = MazeGenerator(width=20, height=15,
                       entry=(0, 0), exit=(14, 19), seed=42)
    mg.generate()
    path = mg.solve()

    for cell in path:
        print(cell.pos)
"""

from mazegen.generator import MazeGenerator, Grid, Cell

__all__ = ["MazeGenerator", "Grid", "Cell"]
