from pathlib import Path

from translation_runner.config import OUTPUT_PATH
from translation_runner.pecha_handling import get_alignment, get_pecha


def get_commentary_translation(
    root_id: str, commentary_id: str, output_path: Path = OUTPUT_PATH
):
    root_pecha = get_pecha(root_id, output_path)
    commentary_pecha = get_pecha(commentary_id, output_path)

    alignment = get_alignment(root_pecha, commentary_pecha)
    return alignment
