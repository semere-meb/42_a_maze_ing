from generator import Grid


def get_walls_as_int(cell: Grid.Cell) -> int:
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
    hex = "0123456789abcdef"
    idx = get_walls_as_int(cell)
    return hex[idx]


def construct_hex_string(grid: Grid) -> str:
    maze = ""
    for row in grid.adj:
        for cell in row:
            maze += get_hex(cell)
        maze += "\n"
    return maze + "\n"


def path_to_string(path: list[Grid.Cell]) -> str:
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
    entry: tuple, exit: tuple, grid: Grid, path: list[Grid.Cell], url: str
) -> bool:
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
