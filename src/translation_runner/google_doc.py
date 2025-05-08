import os
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/documents"]


def get_credentials():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def create_doc_from_file(service, title: str, texts: list[str]):
    # Read file content as plain text
    content = "\n".join(texts)

    # Create new doc with filename as title
    doc_title = title
    doc = service.documents().create(body={"title": doc_title}).execute()
    doc_id = doc.get("documentId")

    # Create requests for document formatting
    requests = [
        {"insertText": {"location": {"index": 1}, "text": content}},
        {
            "updateParagraphStyle": {
                "range": {"startIndex": 1, "endIndex": len(content) + 1},
                "paragraphStyle": {
                    "namedStyleType": "NORMAL_TEXT",
                    "spaceAbove": {"magnitude": 0, "unit": "PT"},
                    "spaceBelow": {"magnitude": 0, "unit": "PT"},
                    "lineSpacing": 115,
                },
                "fields": "namedStyleType,spaceAbove,spaceBelow,lineSpacing",
            }
        },
    ]

    # Apply the formatting
    service.documents().batchUpdate(
        documentId=doc_id, body={"requests": requests}
    ).execute()

    return {
        "title": doc_title,
        "url": f"https://docs.google.com/document/d/{doc_id}/edit",  # noqa
    }


def main(title: str, texts: list[str]) -> Optional[dict]:
    try:
        creds = get_credentials()
        service = build("docs", "v1", credentials=creds)

        # Load existing doc links
        doc_links = {}

        try:
            result = create_doc_from_file(service, title, texts)
            doc_links[result["title"]] = result["url"]
        except Exception as e:
            print(f"Error creating google doc... : {e}")  # noqa

        return doc_links

    except HttpError as error:
        print(f"An error occurred with the Google Docs API: {error}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return None
