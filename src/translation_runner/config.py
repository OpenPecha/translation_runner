from pathlib import Path


def _mkdir(path):
    if path.is_dir():
        return path
    path.mkdir(exist_ok=True, parents=True)
    return path


API_BASE_URL = "https://api-aq25662yyq-uc.a.run.app/pecha/"
OUTPUT_PATH = _mkdir(Path.home() / "translation_runner")
