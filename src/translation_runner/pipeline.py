from pathlib import Path

from claude_translator import translate_commentaries

from translation_runner.config import OUTPUT_PATH
from translation_runner.pecha_handling import get_alignment, get_pecha


def get_commentary_translation(
    root_id: str,
    commentary_id: str,
    target_language: str = "English",
    output_path: Path = OUTPUT_PATH,
) -> dict:
    root_pecha = get_pecha(root_id, output_path)
    commentary_pecha = get_pecha(commentary_id, output_path)

    alignment = get_alignment(root_pecha, commentary_pecha)

    commentary_translation = translate_commentaries(
        commentary_root_pairs=alignment,
        target_language=target_language,
        num_threads=10,
        use_cache=True,
    )

    return commentary_translation
