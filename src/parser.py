#!/usr/bin/env python3

def parse_config(url_path: str) -> dict:
    config = {}
    try:
        with open(url_path, "r") as f:
            for line in f:
                sep = line.find("=")
                key = line[:sep].lower().strip()
                val = line[sep + 1:].strip()
                config[key] = val
        print(f"config is of {type(config)}")
        return config
    except Exception as e:
        print(e)
    finally:
        f.close()
    return

def validate_config(config: dict) -> dict | None:
    keys = [
        "width",
        "height",
        "entry",
        "exit",
        "output_file",
        "perfect"
    ]
    validated = {}
    try:
        for k in keys:
            val = config.get(k)
            if val is None:
                raise KeyError(f"Mandatory config {k} not specified in config file")
            if k == "width" or k == "height":
                validated[k] = int(val)
            if k == "entry" or k == "exit":
                sep = val.find(',')
                coord = (int(val[:sep]), int(val[sep+1:]))
                validated[k] = coord
            if k == "output_file":
                validated[k] = val
            if k == "perfect":
                validated[k] = bool(val)
            print("Returning validated")
        return validated
    except Exception as e:
        print(e)
    return None

def parse() -> None:
    config = parse_config("config.txt")
    for k, v in config.items():
        print(f"{k}={v}")
    val_config = validate_config(config)
    for k, v in val_config.items():
        print(f"{k}={v} --- {type(k)} -> {type(v)}")
    return


if __name__ == "__main__":
    parse()
