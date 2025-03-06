import os
import pickle
import gspread
import pandas as pd
from google.cloud import bigquery
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from oauth2client.service_account import ServiceAccountCredentials

# Define OAuth 2.0 scope for Google Drive and Google Sheets
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

# BigQuery details
BQ_PROJECT_ID = 'drive-audit-369310'
BQ_DATASET = 'drive_audit'
BQ_TABLE = 'drive_audit_data'

def authenticate():
    """Authenticate using OAuth for Google Drive API."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def write_to_bigquery(data):
    """Write data to BigQuery."""
    client = bigquery.Client(project=BQ_PROJECT_ID)

    table_id = f"{BQ_PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}"

    # Convert data to Pandas DataFrame
    df = pd.DataFrame(data, columns=["file_name", "webView_link", "owner_email", "permission_type"])

    # Define BigQuery job config
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND  # Append new rows
    )

    # Load DataFrame into BigQuery
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()  # Wait for the job to complete
    print(f"Data successfully written to BigQuery table {table_id}")

def get_public_and_external_files():
    """Fetch public and externally shared files from Google Drive."""
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    # Define the query to find public files or files shared outside @tatvic.com
    domain = "tatvic.com"
    query = f"(visibility = 'anyoneWithLink') or (not '{domain}' in owners)"

    results = service.files().list(q=query, fields="files(id, name, webViewLink, owners(emailAddress), permissions)").execute()
    files = results.get('files', [])

    if not files:
        print("No public or externally shared files found.")
        return

    data = []
    for file in files:
        name = file.get('name', 'Unknown')
        link = file.get('webViewLink', 'No Link')
        owner_email = file['owners'][0]['emailAddress'] if 'owners' in file else "Unknown"

        permission = 'Outside Domain' if domain not in owner_email else 'Anyone with Link'
        data.append([name, link, owner_email, permission])
        print(f"Name: {name}, Link: {link}, Owner: {owner_email}, Permission: {permission}")

    # Write data to BigQuery
    write_to_bigquery(data)

# Run the function
get_public_and_external_files()
