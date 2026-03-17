#!/usr/bin/env python3

"""Configuration parsing and validation for maze generation."""

from typing import Optional, Any
import sys


class Config:
    """Typed container for maze runtime configuration values."""

    width: int
    height: int
    entry: tuple
    exit: tuple
    output_file: str
    perfect: bool

    fill_color: int
    border_color: int

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple,
        exit: tuple,
        output_file: str,
        perfect: bool,
        seed: Optional[int] = None,
    ) -> None:
        """Build a configuration object from validated values.

        Args:
            width: Number of maze columns.
            height: Number of maze rows.
            entry: Entry cell coordinates as (row, column).
            exit: Exit cell coordinates as (row, column).
            output_file: Path where the output maze file is written.
            perfect: Whether the maze should keep perfect-maze constraints.
            seed: Optional random seed for reproducible generation.

        Returns:
            None.
        """
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.output_file = output_file
        self.perfect = perfect
        self.seed = seed if seed else 42


def parse_config(url_path: str) -> dict[str, str]:
    """Parse a key-value configuration file into a dictionary.

    Args:
        url_path: Path to the configuration file.

    Returns:
        A dictionary containing lowercase keys and stripped string values.
    """
    config = {}
    try:
        with open(url_path, "r") as f:
            for line in f:
                key, val = [m.strip() for m in line.lower().split("=")]
                config[key] = val
        return config
    except Exception as e:
        print(e)
        sys.exit()


def validate_config(config: dict[str, str]) -> dict[str, Any] | None:
    """Validate and convert raw config values into runtime types.

    Args:
        config: Raw key-value map produced by parsing the config file.

    Returns:
        A dictionary of validated and converted values, or None.
    """
    keys = ["width", "height", "entry", "exit",
            "output_file", "perfect", "seed"]
    validated: dict[str, Any] = {}
    try:
        for k in keys:
            val = config.get(k)
            if val is None:
                if k == "seed":
                    continue
                raise KeyError(f"Mandatory config {k} missing")
            if k == "width" or k == "height":
                validated[k] = int(val)
            if k == "entry" or k == "exit":
                sep = val.find(",")
                coord = (int(val[sep + 1:]), int(val[:sep]))  # TRY
                validated[k] = coord
                if (
                    coord[0] >= validated["height"]
                    or coord[0] < 0
                    or coord[1] >= validated["width"]
                    or coord[1] < 0
                ):
                    raise ValueError(f"CONFIG ERROR: {k} is outside of bounds")
            if k == "output_file":
                validated[k] = val
            if k == "perfect":
                validated[k] = True if val.lower() == "true" else False
            if k == "seed":
                validated[k] = int(val)
        return validated
    except Exception as e:
        print(e)
        sys.exit()


def get_config(url: str) -> Config:
    """Load, validate, and instantiate the project Config object.

    Args:
        url: Path to the configuration file.

    Returns:
        A fully initialized Config instance.
    """
    first = parse_config(url)
    config = validate_config(first)
    if config is None:
        sys.exit()
    return Config(
        config["width"],
        config["height"],
        config["entry"],
        config["exit"],
        config["output_file"],
        config["perfect"],
        config.get("seed"),
    )


def parse() -> None:
    """Utility entry point to print parsed and validated config values.

    Returns:
        None.
    """
    config = parse_config("../config.txt")
    for k, v in config.items():
        print(f"{k}={v}")
    val_config = validate_config(config)
    if val_config is None:
        return
    for k, v in val_config.items():
        print(f"{k}={v} --- {type(k)} -> {type(v)}")
    return


if __name__ == "__main__":
    parse()
