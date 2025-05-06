from pathlib import Path

from openpecha.alignment.commentary_transfer import CommentaryAlignmentTransfer
from openpecha.pecha import Pecha

from translation_runner.config import OUTPUT_PATH
from translation_runner.utils import download_pecha


def get_pecha(pecha_id: str, output_path: Path) -> Pecha:
    pecha_path = download_pecha(pecha_id, output_path)
    return Pecha.from_path(pecha_path)


def get_commentary_alignment_id(pecha: Pecha) -> str:
    """
    Return the first alignment annotation layer from the Commentary Pecha
    """
    alignment_layer_path = next(pecha.layer_path.rglob("alignment*.json"))
    alignment_id = alignment_layer_path.relative_to(pecha.layer_path).name
    return alignment_id


def get_alignment(root_id: str, commentary_id: str, output_path: Path = OUTPUT_PATH):
    root_pecha = get_pecha(root_id, output_path)
    commentary_pecha = get_pecha(commentary_id, output_path)

    commentary_alignment_id = get_commentary_alignment_id(commentary_pecha)
    return CommentaryAlignmentTransfer().get_serialized_commentary(
        root_pecha, commentary_pecha, commentary_alignment_id
    )
