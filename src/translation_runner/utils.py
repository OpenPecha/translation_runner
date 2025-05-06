import io
import shutil
import zipfile
from pathlib import Path

import requests


def download_pecha(pecha_id: str, output_path: Path) -> Path:
    """
    Download a pecha from OpenPecha API.
    """
    pecha_path = output_path / pecha_id
    if pecha_path.exists():
        shutil.rmtree(pecha_path)
    pecha_path.mkdir(parents=True, exist_ok=True)

    url = f"https://api-aq25662yyq-uc.a.run.app/pecha/{pecha_id}"

    headers = {"accept": "application/zip"}
    response = requests.get(url, headers=headers, stream=True)

    if response.status_code == 200:
        with io.BytesIO(response.content) as zip_buffer:
            with zipfile.ZipFile(zip_buffer, "r") as zip_ref:
                zip_ref.extractall(pecha_path)

        return pecha_path
    else:
        raise Exception(
            f"Failed to download pecha. Status code: {response.status_code}"
        )
