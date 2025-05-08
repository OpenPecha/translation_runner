import logging
import os
from typing import Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- Constants ---
SCOPES = ["https://www.googleapis.com/auth/documents"]
TOKEN_PATH = "token.json"
CREDENTIALS_PATH = "credentials.json"

logging.basicConfig(level=logging.INFO)


def get_credentials(
    token_path: str = TOKEN_PATH, credentials_path: str = CREDENTIALS_PATH
) -> Credentials:
    """
    Obtain Google API credentials, refreshing or requesting as needed.
    """
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    return creds


def build_numbered_list_document(
    service, title: str, texts: List[str]
) -> Dict[str, str]:
    """
    Create a Google Doc with the given title and texts, storing each text as a true numbered list item.
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
        "url": f"https://docs.google.com/document/d/{doc_id}/edit",
        "document_id": doc_id,
    }


def create_google_doc(title: str, texts: List[str]) -> Optional[Dict[str, str]]:
    """
    High-level API: create a Google Doc and return its title and URL.
    """
    try:
        creds = get_credentials()
        service = build("docs", "v1", credentials=creds)
        doc_links = {}
        try:
            result = build_numbered_list_document(service, title, texts)
            doc_links[result["title"]] = result["url"]
        except Exception as e:
            logging.error(f"Error creating Google Doc: {e}")
        return doc_links
    except HttpError as error:
        logging.error(f"Google Docs API error: {error}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    return None
