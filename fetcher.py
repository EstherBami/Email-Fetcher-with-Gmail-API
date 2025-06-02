import os
import base64
import re
import json
from datetime import datetime
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from collections import defaultdict

# Scopes for Gmail: read, send, and metadata access
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None
    token_file = 'token.json'

    # Load existing token if available
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    # If there are no valid creds, authenticate the user
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('email_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save token for future use
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    
    return creds

def decode_and_clean(data, is_html=False):
    try:
        decoded = base64.urlsafe_b64decode(data).decode('utf-8')
    except Exception:
        return ""

    if is_html:
        soup = BeautifulSoup(decoded, 'html.parser')
        text = soup.get_text()
    else:
        text = decoded

    text = re.sub(r'\s+', ' ', text)

    # Remove noise and common email footer patterns
    noise_patterns = [
        r'unsubscribe.*?(click here|manage preferences)?',
        r'view (entire message|online version)',
        r'follow us on.*',
        r'contact us.*',
        r'https?://\S+',
        r'\b(all rights reserved|copyright)\b',
    ]
    for pattern in noise_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    return text.strip()

def extract_body_from_payload(payload):
    """Extract cleaned body and a preview of the email content."""
    body_text = ""

    if 'parts' in payload:
        for part in payload['parts']:
            mime_type = part.get("mimeType")
            data = part['body'].get('data')
            if data:
                if mime_type == "text/plain":
                    body_text = decode_and_clean(data)
                    break
                elif mime_type == "text/html":
                    body_text = decode_and_clean(data, is_html=True)
                    break
    else:
        data = payload.get('body', {}).get('data')
        if data:
            is_html = payload.get('mimeType') == 'text/html'
            body_text = decode_and_clean(data, is_html=is_html)

    sentences = re.split(r'(?<=[.?!])\s+', body_text)
    preview = " ".join(sentences[:5]).strip()

    return body_text, preview

def fetch_emails():
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)

    results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=10).execute()
    messages = results.get('messages', [])

    threads = defaultdict(list)

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        payload = msg_data['payload']
        headers = payload.get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '(Unknown Sender)')
        timestamp_raw = int(msg_data.get('internalDate')) / 1000
        timestamp = datetime.fromtimestamp(timestamp_raw).strftime('%Y-%m-%d %H:%M')

        full_body, preview = extract_body_from_payload(payload)

        threads[msg_data['threadId']].append({
            'from': sender,
            'subject': subject,
            'timestamp': timestamp,
            'timestamp_raw': timestamp_raw,
            'preview': preview,
            'full_body': full_body
        })

    # Sort messages inside each thread by timestamp
    for thread_id in threads:
        threads[thread_id].sort(key=lambda x: x['timestamp_raw'])

    # Convert threads dict to list of threads
    email_threads = []
    for thread_id, messages in threads.items():
        email_threads.append({
            'threadId': thread_id,
            'subject': messages[0]['subject'],
            'messages': messages
        })

    return email_threads

if __name__ == '__main__':
    email_threads = fetch_emails()

    # Save the full threads to a JSON file
    with open('email_thread.json', 'w', encoding='utf-8') as f:
        json.dump(email_threads, f, ensure_ascii=False, indent=2)

    print("Saved email threads to email_threads.json")

    for idx, thread in enumerate(email_threads):
        print(f"\nEmail {idx + 1}: {thread['subject']}")
        for msg in thread['messages']:
            print(f"  ↳ {msg['timestamp']} | {msg['from']}")
            print(f"     Preview: {msg['preview'][:200]}...")
