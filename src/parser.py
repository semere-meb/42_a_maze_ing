#!/usr/bin/env python3

class Config:
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
    ) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.output_file = output_file
        self.perfect = perfect

def parse_config(url_path: str) -> dict:
    config = {}
    try:
        with open(url_path, "r") as f:
            for line in f:
                sep = line.find("=")
                key = line[:sep].lower().strip()
                val = line[sep + 1 :].strip()
                config[key] = val
        print(f"config is of {type(config)}")
        f.close()
        return config
    except Exception as e:
        print(e)
        return None


def validate_config(config: dict) -> dict | None:
    keys = ["width", "height", "entry", "exit", "output_file", "perfect"]
    validated = {}
    try:
        for k in keys:
            val = config.get(k)
            if val is None:
                raise KeyError(f"Mandatory config {k} not specified in config file")
            if k == "width" or k == "height":
                validated[k] = int(val)                
            if k == "entry" or k == "exit":
                sep = val.find(",")
                coord = (int(val[:sep]), int(val[sep + 1 :]))
                validated[k] = coord
                if coord[0] >= validated["height"] or coord[0] < 0 or coord[1] >= validated["width"] or coord[0] < 0:
                    raise ValueError(f"CONFIG ERROR: {k} is outside of bounds")
            if k == "output_file":
                validated[k] = val
            if k == "perfect":
                validated[k] = bool(val)
        return validated
    except Exception as e:
        print(e)
    return None

def get_config(url: str) -> Config:
    first = parse_config(url)
    config = validate_config(first)
    if config is None:
        return None
    return Config(
        config['width'],
        config['height'],
        config['entry'],
        config['exit'],
        config['output_file'],
        config['perfect']
    )


def parse() -> None:
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
