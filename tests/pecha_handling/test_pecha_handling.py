from pathlib import Path
from unittest.mock import patch

from openpecha.pecha import Pecha

from translation_runner.pecha_handling import get_alignment


def test_get_alignment():
    DATA_DIR = Path(__file__).parent / "data"

    root_id = "IDDA32A00"
    commentary_id = "I92B4BA6C"

    root_pecha = Pecha.from_path(DATA_DIR / root_id)
    commentary_pecha = Pecha.from_path(DATA_DIR / commentary_id)

    with patch(
        "translation_runner.pecha_handling.get_commentary_alignment_id"
    ) as mock_get_commentary_alignment_id, patch(
        "translation_runner.pecha_handling.get_root_alignment_id"
    ) as mock_get_root_alignment_id:

        mock_get_commentary_alignment_id.return_value = "4249/alignment-8899"
        mock_get_root_alignment_id.return_value = "4885/alignment-298F"

        alignment = get_alignment(root_pecha, commentary_pecha)
        assert alignment == [
            {"root": "ཚིག་གྲུབ་དང་པོ།", "commentary": "འགྲེལ་བཤད་དང་པོ།"},
            {"root": "ཚིག་གྲུབ་གཉིས་པ།  ", "commentary": "འགྲེལ་བཤད་གཉིས་པ།"},
            {"root": "ཚིག་གྲུབ་གསུམ་པ།", "commentary": "འགྲེལ་བཤད་གསུམ་པ།"},
        ]
