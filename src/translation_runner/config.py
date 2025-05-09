import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def get_logger(name):
    return logging.getLogger(name)


def _mkdir(path):
    if path.is_dir():
        return path
    path.mkdir(exist_ok=True, parents=True)
    return path


OUTPUT_PATH = _mkdir(Path.home() / "translation_runner")


PRODUCTION_URL = "https://api-aq25662yyq-uc.a.run.app"
DEVELOPMENT_URL = "https://api-l25bgmwqoa-uc.a.run.app"

DOWNLOAD_PECHA_PROD = f"{PRODUCTION_URL}/pecha/"
DOWNLOAD_PECHA_DEV = f"{DEVELOPMENT_URL}/pecha/"

GET_ANNOTATION_PROD = f"{PRODUCTION_URL}/annotation/"
GET_ANNOTATION_DEV = f"{DEVELOPMENT_URL}/annotation/"

CREATE_PECHA_PROD = f"{PRODUCTION_URL}/post_pecha/"
CREATE_PECHA_DEV = f"{DEVELOPMENT_URL}/post_pecha/"
