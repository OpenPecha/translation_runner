import io
import json
import shutil
import zipfile
from pathlib import Path

import requests

from translation_runner.config import (
    DOWNLOAD_PECHA_DEV,
    DOWNLOAD_PECHA_PROD,
    GET_ANNOTATION_DEV,
    GET_ANNOTATION_PROD,
)


def download_pecha(pecha_id: str, output_path: Path, development: bool = True) -> Path:
    """
    Download a pecha from the OpenPecha API.
    """
    pecha_path = output_path / pecha_id
    if pecha_path.exists():
        shutil.rmtree(pecha_path)
    pecha_path.mkdir(parents=True, exist_ok=True)

    url = (
        f"{DOWNLOAD_PECHA_PROD}{pecha_id}"
        if not development
        else f"{DOWNLOAD_PECHA_DEV}{pecha_id}"
    )
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


def get_annotations(pecha_id: str, development: bool = True):
    """
    Get annotations from the OpenPecha API.
    """
    url = (
        f"{GET_ANNOTATION_DEV}{pecha_id}"
        if development
        else f"{GET_ANNOTATION_PROD}{pecha_id}"
    )

    headers = {"Accept": "application/json"}

    try:
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        raise Exception(f"Failed to get annotations for pecha '{pecha_id}': {e}") from e

    return response.json()


def write_json(data: dict, output_path: Path):
    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)


def read_json(output_path: Path) -> dict:
    with open(output_path) as f:
        return json.load(f)
