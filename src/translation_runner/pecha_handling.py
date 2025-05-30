from pathlib import Path

from openpecha.alignment.commentary_transfer import parse_root_mapping
from openpecha.pecha import Pecha, get_anns
from stam import AnnotationStore

from translation_runner.openpecha_api import download_pecha, get_annotations


def get_pecha(pecha_id: str, output_path: Path) -> Pecha:
    """
    Download and load Pecha.
    """
    pecha_path = download_pecha(pecha_id, output_path)
    return Pecha.from_path(pecha_path)


def get_pecha_anns(pecha: Pecha, annotation_path: str) -> dict:
    """
    Read all annotations from a given annotation layer.
    """
    layer_path = pecha.layer_path / f"{annotation_path}.json"
    return get_anns(AnnotationStore(file=str(layer_path)))


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
    layer_path = next(commentary_pecha.layer_path.rglob("alignment*.json"))
    alignment_id = layer_path.relative_to(commentary_pecha.layer_path).as_posix()
    return alignment_id


def get_alignment(root_pecha: Pecha, commentary_pecha: Pecha):
    commentary_alignment_id = get_commentary_alignment_id(commentary_pecha)
    root_alignment_id = get_root_alignment_id(commentary_pecha, commentary_alignment_id)

    root_anns = get_pecha_anns(root_pecha, root_alignment_id)
    commentary_anns = get_pecha_anns(commentary_pecha, commentary_alignment_id)

    alignment = []
    for commentary_ann in commentary_anns:
        commentary_text = commentary_ann["text"]
        root_idx = parse_root_mapping(commentary_ann["root_idx_mapping"])[0]

        root_text = root_anns[root_idx - 1]["text"]
        alignment.append({"root": root_text, "commentary": commentary_text})
    return alignment
