from pathlib import Path

from openpecha.pecha import Pecha

from translation_runner.config import OUTPUT_PATH
from translation_runner.utils import download_pecha


def get_pecha(pecha_id: str, output_path: Path) -> Pecha:
    pecha_path = download_pecha(pecha_id, output_path)
    return Pecha.from_path(pecha_path)


def get_alignment(root_id: str, commentary_id: str, output_path: Path = OUTPUT_PATH):
    root_pecha = get_pecha(root_id, output_path)
    commentary_pecha = get_pecha(commentary_id, output_path)

    pass
