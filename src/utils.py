"""Conversion and serialization helpers for maze output."""

from generator import Grid


def get_walls_as_int(cell: Grid.Cell) -> int:
    """Convert a cell wall state into the 4-bit integer encoding.

    Args:
        cell: Cell whose wall booleans are encoded.

    Returns:
        Integer value with bits mapped to N/E/S/W walls.
    """
    # north (LSB) 0
    # east bit 1
    # south bit 2
    # west bit 3
    output = 0

    if cell.n:
        output += 1
    if cell.e:
        output += 2
    if cell.s:
        output += 4
    if cell.w:
        output += 8

    return output


def get_hex(cell: Grid.Cell) -> str:
    """Convert a cell wall state into a hexadecimal digit.

    Args:
        cell: Cell whose wall booleans are encoded.

    Returns:
        A single lowercase hexadecimal character.
    """
    hex = "0123456789abcdef"
    idx = get_walls_as_int(cell)
    return hex[idx]


def construct_hex_string(grid: Grid) -> str:
    """Serialize all maze cells into the hexadecimal row format.

    Args:
        grid: Maze grid to serialize.

    Returns:
        Full maze body including row newlines and trailing empty line.
    """
    maze = ""
    for row in grid.adj:
        for cell in row:
            maze += get_hex(cell)
        maze += "\n"
    return maze + "\n"


def path_to_string(path: list[Grid.Cell]) -> str:
    """Encode a cell path into compass directions.

    Args:
        path: Ordered list of cells from start to destination.

    Returns:
        A direction string using N, E, S, and W followed by newline.
    """
    output = ""
    i = 1
    while i < len(path):
        prev = path[i - 1].pos
        curr = path[i].pos
        if curr[0] - prev[0] == 1:
            output += "S"
        elif curr[0] - prev[0] == -1:
            output += "N"
        elif curr[1] - prev[1] == 1:
            output += "E"
        elif curr[1] - prev[1] == -1:
            output += "W"
        else:
            output += " WRONG "
        i += 1
    return output + "\n"


def write_to_file(
    entry: tuple[int, int],
    exit: tuple[int, int],
    grid: Grid,
    path: list[Grid.Cell],
    url: str,
) -> bool:
    """Write maze layout, endpoints, and shortest path to disk.

    Args:
        entry: Entry coordinate as (row, column).
        exit: Exit coordinate as (row, column).
        grid: Generated maze grid.
        path: Shortest path from entry to exit.
        url: Destination output file path.

    Returns:
        True if writing succeeded, else False.
    """
    output = construct_hex_string(grid)
    output += f"{entry[0]},{entry[1]}\n{exit[0]},{exit[1]}\n"
    output += path_to_string(path)

    try:
        with open(url, "w") as f:
            f.write(output)
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        f.close()
