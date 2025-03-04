# import os
# import pickle
# from googleapiclient.discovery import build
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request

# # Define OAuth 2.0 scope for Google Drive
# SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

# # Authenticate using OAuth 2.0
# def authenticate():
#     creds = None
#     if os.path.exists('token.pickle'):
#         with open('token.pickle', 'rb') as token:
#             creds = pickle.load(token)

#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
#             creds = flow.run_local_server(port=0)

#         with open('token.pickle', 'wb') as token:
#             pickle.dump(creds, token)

#     return creds

# # Function to list files with public access
# def get_public_files():
#     creds = authenticate()
#     service = build('drive', 'v3', credentials=creds)
    
#     query = "visibility = 'anyoneWithLink'"
#     results = service.files().list(q=query, fields="files(id, name, webViewLink)").execute()
#     files = results.get('files', [])

#     if not files:
#         print("No publicly accessible files found.")
#     else:
#         print("Publicly Accessible Files:")
#         for file in files:
#             print(f"Name: {file['name']}, Link: {file['webViewLink']}")

# # Run the function
# get_public_files()


import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Define OAuth 2.0 scope for Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

# Authenticate using OAuth 2.0
def authenticate():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('drive_audit_cred.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

# Function to list public files and files shared outside @tatvic.com
def get_public_and_external_files():
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    
    # Define the query to find public files or files shared outside @tatvic.com
    domain = "tatvic.com"
    query = f"(visibility = 'anyoneWithLink') or (not '{domain}' in owners)"

    results = service.files().list(q=query, fields="files(id, name, webViewLink, owners(emailAddress))").execute()
    files = results.get('files', [])

    if not files:
        print("No public or externally shared files found.")
    else:
        print("Publicly Accessible or Externally Shared Files:")
        for file in files:
            owner_email = file['owners'][0]['emailAddress'] if 'owners' in file else "Unknown"
            print(f"Name: {file['name']}, Link: {file['webViewLink']}, Owner: {owner_email}")

# Run the function
get_public_and_external_files()
