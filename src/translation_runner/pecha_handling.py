from pathlib import Path

from openpecha.alignment.commentary_transfer import CommentaryAlignmentTransfer
from openpecha.pecha import Pecha

from translation_runner.config import OUTPUT_PATH
from translation_runner.utils import download_pecha, get_annotations


def get_pecha(pecha_id: str, output_path: Path) -> Pecha:
    pecha_path = download_pecha(pecha_id, output_path)
    return Pecha.from_path(pecha_path)


def get_root_alignment_id(commentary_pecha: Pecha, alignment_id: str) -> str:
    """
    Return the root alignment id related to the commentary alignment id
    """
    anns = list(get_annotations(commentary_pecha.id).values())
    for ann_model in anns:
        if ann_model["path"] == alignment_id:
            if ann_model["aligned_to"]:
                return ann_model["aligned_to"]["alignment_id"]

            raise ValueError(
                f"Commentary alignment id {alignment_id} is not aligned to any root alignment id"
            )

    raise ValueError(f"Commentary alignment id {alignment_id} not found")


def get_commentary_alignment_id(commentary_pecha: Pecha) -> str:
    """
    Return the first alignment annotation layer from the Commentary Pecha
    """
    alignment_layer_path = next(commentary_pecha.layer_path.rglob("alignment*.json"))
    alignment_id = alignment_layer_path.relative_to(
        commentary_pecha.layer_path
    ).as_posix()
    return alignment_id


def get_alignment(root_id: str, commentary_id: str, output_path: Path = OUTPUT_PATH):
    root_pecha = get_pecha(root_id, output_path)
    commentary_pecha = get_pecha(commentary_id, output_path)

    commentary_alignment_id = get_commentary_alignment_id(commentary_pecha)
    root_alignment_id = get_root_alignment_id(commentary_pecha, commentary_alignment_id)
    return CommentaryAlignmentTransfer().get_serialized_commentary(
        root_pecha, root_alignment_id, commentary_pecha, commentary_alignment_id
    )
