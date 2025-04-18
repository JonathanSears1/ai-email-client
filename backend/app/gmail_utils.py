from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def create_message(sender, to, subject, body):
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject
    message['reply-to'] = sender
    message['Sender'] = sender
    message.attach(MIMEText(body, 'plain'))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}

def get_gmail_service(access_token, refresh_token, token_uri, client_id, client_secret, token_expiry):
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret,
        expiry=token_expiry
    )

    service = build('gmail', 'v1', credentials=creds)
    return service