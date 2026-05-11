import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from langchain_core.tools import tool

# This points to the secret key you downloaded earlier
if os.path.exists("service_account.json"):
    CREDENTIALS_FILE = "service_account.json"
else:
    CREDENTIALS_FILE = os.path.join("credentials", "service_account.json")

def get_drive_service():
    """Authenticates using the service account and returns the Drive API service."""
    # We only need read-only access for searching
    scopes = ['https://www.googleapis.com/auth/drive.readonly']
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=scopes)
    service = build('drive', 'v3', credentials=creds)
    return service

@tool
def search_google_drive(query: str) -> str:
    """
    Searches Google Drive for files using a specific query string.
    The query should be a valid Google Drive API 'q' parameter string.
    Example: name contains 'report' and mimeType = 'application/pdf'
    """
    print(f"\n[DEBUG] LLM GENERATED QUERY: {query}\n")
    try:
        service = get_drive_service()
        
        # This is the core files.list method required by the assignment
        results = service.files().list(
            q=query,
            spaces='drive',
            fields="nextPageToken, files(id, name, mimeType, webViewLink, createdTime)",
            pageSize=10
        ).execute()
        
        items = results.get('files', [])
        
        if not items:
            return "No files found matching that exact query."
        
        # Format the results into a clean string so the LLM can read and summarize it easily
        response = "Found the following files:\n"
        for item in items:
            response += f"- Name: {item['name']} | Type: {item['mimeType']} | Link: {item.get('webViewLink', 'N/A')}\n"
        
        return response
        
    except Exception as e:
        return f"An error occurred while searching Drive: {str(e)}"