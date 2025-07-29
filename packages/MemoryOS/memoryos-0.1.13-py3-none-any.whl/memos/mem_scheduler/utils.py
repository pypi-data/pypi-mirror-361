import json

from pathlib import Path

import yaml


def extract_json_dict(text: str):
    text = text.strip()
    patterns_to_remove = ["json'''", "latex'''", "'''"]
    for pattern in patterns_to_remove:
        text = text.replace(pattern, "")
    res = json.loads(text)
    return res


def parse_yaml(yaml_file):
    yaml_path = Path(yaml_file)
    yaml_path = Path(yaml_file)
    if not yaml_path.is_file():
        raise FileNotFoundError(f"No such file: {yaml_file}")

    with yaml_path.open("r", encoding="utf-8") as fr:
        data = yaml.safe_load(fr)

    return data
