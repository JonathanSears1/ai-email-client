from langchain.tools import Tool
import datetime
from googleapiclient.discovery import build
from sqlalchemy.orm import Session
from database import User  # adjust import as needed
from gmail_utils import get_gmail_service
import os
import getpass
import os
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.llm import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
import base64

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

class SummaryAgent:
    def __init__(self, user: User, db: Session, llm="gpt-4o-mini", provider="openai"):
        self.user = user
        self.db = db
        self.service = get_gmail_service(
            access_token=user.access_token,
            refresh_token=user.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            token_expiry=user.token_expiry
        )
        self.llm = init_chat_model(llm, model_provider=provider)

    def fetch_emails(self):
        """Fetches emails since the user's last summary run."""
        query = "label:inbox"
        now = datetime.datetime.now(datetime.timezone.utc)

        if self.user.last_summary_run:
            # Ensure last_summary_run is timezone aware before subtraction
            last_run = self.user.last_summary_run
            if last_run.tzinfo is None:
                last_run = last_run.replace(tzinfo=datetime.timezone.utc)
            delta = now - last_run
            days = max(1, delta.days)
            query += f" newer_than:{days}d"
        else:
            # Default to last 1 day if no previous run
            query += " newer_than:1d"

        results = self.service.users().messages().list(userId='me', q=query).execute()
        messages = results.get("messages", [])

        emails = []
        for msg in messages:
            full = self.service.users().messages().get(userId='me', id=msg["id"], format="full").execute()
            emails.append(full)

        return emails

    def update_last_summary_run(self):
        """Call this after the summary is generated."""
        self.user.last_summary_run = datetime.datetime.now(datetime.timezone.utc)
        print(f"Last summary run updated to {self.user.last_summary_run}")
        self.db.commit()

    def summarize_emails(self):
        """Summarize the fetched emails."""
        emails = self.fetch_emails()
        
        # Convert Gmail messages to LangChain Documents
        documents = []
        for email in emails:
            payload = email.get('payload', {})
            headers = payload.get('headers', [])
            
            # Extract relevant email information
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
            
            # Get the email body
            body = ''
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        body = part['body'].get('data', '')
                        if body:
                            body = base64.urlsafe_b64decode(body).decode('utf-8')
                            break
            
            # Create a formatted string with email content
            content = f"From: {from_email}\nSubject: {subject}\nDate: {date}\n\n{body}"
            
            # Create LangChain Document
            doc = Document(
                page_content=content,
                metadata={
                    'subject': subject,
                    'from': from_email,
                    'date': date
                }
            )
            documents.append(doc)
        
        prompt = ChatPromptTemplate.from_messages(
            [("system", '''
              You are an AI email assistant. Summarize the following emails clearly and concisely.
              \nOnly include:\n
              - Important meeting invites\n
              - Work/project updates\n
              - Personal communication if relevant\n
              Ignore:
              - Promotions, newsletters, receipts, and spam
              \n
              \n
              {context}
              ''')])
        
        # Instantiate chain
        chain = create_stuff_documents_chain(self.llm, prompt)
        # Invoke chain with documents
        result = chain.invoke({"context": documents})
        # After summarizing, update the last summary run time
        self.update_last_summary_run()
        return result