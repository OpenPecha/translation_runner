import io
import os
from pathlib import Path
from typing import Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from translation_runner.config import get_logger

# --- Constants ---
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive",
]
TOKEN_PATH = "token.json"
CREDENTIALS_PATH = "credentials.json"

logger = get_logger(__name__)


def get_credentials(
    token_path: str = TOKEN_PATH, credentials_path: str = CREDENTIALS_PATH
) -> Credentials:
    """
    Obtain Google API credentials, refreshing or requesting as needed.
    """
    try:
        creds = None
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open(token_path, "w") as token:
                token.write(creds.to_json())
        return creds
    except FileNotFoundError as e:
        logger.error(f"Failed to obtain Google API credentials: {e}")
        raise FileNotFoundError(f"Failed to obtain Google API credentials: {e}")


def build_numbered_list_document(
    service, title: str, texts: List[str]
) -> Dict[str, str]:
    """
    Create a Google Doc with storing each text as a true numbered list item.
    """
    doc = service.documents().create(body={"title": title}).execute()
    doc_id = doc.get("documentId")

    # Insert all texts as separate paragraphs
    requests = []
    insert_index = 1
    for text in texts:
        paragraph = text + "\n"
        requests.append(
            {"insertText": {"location": {"index": insert_index}, "text": paragraph}}
        )
        insert_index += len(paragraph)

    # Apply numbered list style using createParagraphBullets
    if texts:
        requests.append(
            {
                "createParagraphBullets": {
                    "range": {"startIndex": 1, "endIndex": insert_index},
                    "bulletPreset": "NUMBERED_DECIMAL_ALPHA_ROMAN",
                }
            }
        )

    service.documents().batchUpdate(
        documentId=doc_id, body={"requests": requests}
    ).execute()
    return {
        "title": title,
        "url": f"https://docs.google.com/document/d/{doc_id}",
        "document_id": doc_id,
    }


def create_google_doc(title: str, texts: List[str]) -> Optional[Dict[str, str]]:
    """
    High-level API: create a Google Doc and return its title and URL.
    """
    try:
        creds = get_credentials()
        service = build("docs", "v1", credentials=creds)
        try:
            res = build_numbered_list_document(service, title, texts)
        except Exception as e:
            logger.error(f"Error creating Google Doc: {e}")
        return res
    except HttpError as error:
        logger.error(f"Google Docs API error: {error}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    return None


def download_doc(doc_id: str, output_path: str | Path):
    """
    Download a Google Doc as a .docx file and save it to disk.

    Args:
        doc_id (str): The ID of the Google Document to download.
        output_path (Path |str): File path to save the downloaded document.
    """
    try:
        creds = get_credentials()
        service = build("drive", "v3", credentials=creds)

        request = service.files().export(
            fileId=doc_id,
            mimeType="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                logger.info(f"Download progress: {int(status.progress() * 100)}%")

        fh.seek(0)
        output_path = output_path or f"{doc_id}.docx"
        with open(output_path, "wb") as f:
            f.write(fh.read())

        logger.info(f"Document saved to: {output_path}")
        return output_path

    except HttpError as error:
        logger.error(f"Failed to download document: {error}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    doc_id = "1QMZHP3BWVHIBGkbAXf2pbiWYe0mpbuZB1EaU0Uf6uHE"
    output_path = Path("test.docx")
    download_doc(doc_id, output_path)
