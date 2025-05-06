from pathlib import Path

from openpecha.pecha import Pecha

from translation_runner.utils import download_pecha


def get_pecha(pecha_id: str, output_path: Path) -> Pecha:
    pecha_path = download_pecha(pecha_id, output_path)
    return Pecha.from_path(pecha_path)
