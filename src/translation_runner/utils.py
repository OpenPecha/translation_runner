import json
from pathlib import Path


def write_json(
    data: dict,
    output_fn: str | Path,
) -> Path:
    output_fn = Path(output_fn)
    output_fn.parent.mkdir(exist_ok=True, parents=True)
    with output_fn.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return output_fn


def read_json(output_path: Path) -> dict:
    with open(output_path, encoding="utf-8") as f:
        return json.load(f)
