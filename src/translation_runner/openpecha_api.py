import io
import json
import shutil
import zipfile
from pathlib import Path

import requests

from translation_runner.config import (
    CREATE_PECHA_DEV,
    CREATE_PECHA_PROD,
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


def create_pecha(docx_file: str | Path, metadata: dict, development: bool = True):
    """
    Create a new pecha in the OpenPecha API with docx file and metadata.
    """
    url = CREATE_PECHA_DEV if development else CREATE_PECHA_PROD

    if isinstance(docx_file, str):
        docx_file = Path(docx_file)

    try:
        with open(docx_file, "rb") as f:
            files = {
                "text": (
                    docx_file.name,
                    f,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            }
            data = {"metadata": json.dumps(metadata), "annotation_id": ""}

            response = requests.post(url, files=files, data=data, timeout=60)
            response.raise_for_status()
            return response.json()

    except requests.HTTPError as e:
        print("Server returned error response:")
        print(response.text)
        raise Exception(f"Failed to create pecha: {e}") from e
    except requests.RequestException as e:
        raise Exception(f"Failed to create pecha: {e}") from e


if __name__ == "__main__":
    docx_file = Path("test.docx")
    metadata = {
        "language": "bo",
        "author": {"bo": "commentary alignment"},
        "title": {"bo": "commentary alignment", "en": "commentary alignment"},
        "long_title": {"bo": "commentary alignment"},
        "source_url": None,
        "source": "commentary alignment",
        "commentary_of": "I00BBCC2A",
        "document_id": "d1",
    }
    res = create_pecha(docx_file, metadata)
    print(res)
