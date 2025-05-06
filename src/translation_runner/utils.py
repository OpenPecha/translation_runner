import io
import shutil
import zipfile
from pathlib import Path

import requests

API_BASE_URL = "https://api-aq25662yyq-uc.a.run.app/pecha/"


def download_pecha(pecha_id: str, output_path: Path) -> Path:
    """
    Download a pecha from the OpenPecha API.
    """
    pecha_path = output_path / pecha_id
    if pecha_path.exists():
        shutil.rmtree(pecha_path)
    pecha_path.mkdir(parents=True, exist_ok=True)

    url = f"{API_BASE_URL}{pecha_id}"
    headers = {"Accept": "application/zip"}

    try:
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        raise Exception(f"Failed to download pecha '{pecha_id}': {e}") from e

    try:
        with io.BytesIO(response.content) as zip_buffer:
            with zipfile.ZipFile(zip_buffer, "r") as zip_ref:
                zip_ref.extractall(pecha_path)
    except zipfile.BadZipFile as e:
        raise Exception(
            f"Downloaded file is not a valid zip archive for pecha '{pecha_id}'."
        ) from e

    return pecha_path
