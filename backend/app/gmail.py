from fastapi import Depends, APIRouter, HTTPException, Body
from sqlalchemy.orm import Session
from auth_utils import get_current_user
from database import SessionLocal
from crud import get_user_by_email
from gmail_utils import get_gmail_service, create_message
from agent import SummaryAgent
import os
import base64

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/inbox")
async def read_inbox(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # Step 1: Get user from DB
    user = get_user_by_email(db, current_user["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Step 2: Build Gmail service
    service = get_gmail_service(
        access_token=user.access_token,
        refresh_token=user.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        token_expiry=user.token_expiry
    )

    # Step 3: List messages
    results = service.users().messages().list(userId='me', maxResults=25).execute()
    messages = results.get('messages', [])

    # Step 4: Fetch message details
    detailed_messages = []
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        payload = msg.get('payload', {})
        headers = payload.get('headers', [])

        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
        sender = next((header['value'] for header in headers if header['name'] == 'From'), None)

        detailed_messages.append({
            'id': message['id'],
            'subject': subject,
            'from': sender
        })

    return {"messages": detailed_messages}


@router.post("/send")
async def send_email(
    to: str = Body(...),
    subject: str = Body(...),
    body: str = Body(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, current_user["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    service = get_gmail_service(
        access_token=user.access_token,
        refresh_token=user.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        token_expiry=user.token_expiry
    )

    message = create_message(sender=user.email, to=to, subject=subject, body=body)
    
    
    try:
        sent = service.users().messages().send(userId='me', body=message).execute()
        return {"status": "success", "message_id": sent['id']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/drafts")
async def list_drafts(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, current_user["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    service = get_gmail_service(
        access_token=user.access_token,
        refresh_token=user.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        token_expiry=user.token_expiry
    )

    try:
        # Step 1: List draft metadata
        drafts_list = service.users().drafts().list(userId='me', maxResults=10).execute()
        draft_items = drafts_list.get('drafts', [])

        # Step 2: Get full draft message data for each one
        detailed_drafts = []
        for draft in draft_items:
            draft_id = draft['id']
            full_draft = service.users().drafts().get(userId='me', id=draft_id, format='full').execute()
            payload = full_draft['message'].get('payload', {})
            headers = payload.get('headers', [])

            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), None)
            to = next((h['value'] for h in headers if h['name'] == 'To'), None)

            # Extract plain text body if available
            body_data = None
            parts = payload.get('parts', [])
            for part in parts:
                if part.get('mimeType') == 'text/plain':
                    body_data = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break

            detailed_drafts.append({
                "draft_id": draft_id,
                "to": to,
                "subject": subject,
                "body": body_data
            })

        return {"drafts": detailed_drafts}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/draft")
async def save_draft(
    to: str = Body(...),
    subject: str = Body(...),
    body: str = Body(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, current_user["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    service = get_gmail_service(
        access_token=user.access_token,
        refresh_token=user.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        token_expiry=user.token_expiry
    )

    try:
        # Build the MIME message
        message = create_message(user.email,to, subject, body)
        draft = {
            'message': message
        }

        # Save the draft
        created_draft = service.users().drafts().create(userId='me', body=draft).execute()
        return {
            "status": "success",
            "draft_id": created_draft['id']
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/summary")
def generate_summary(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = get_user_by_email(db, current_user["sub"])
    agent = SummaryAgent(user, db)
    # Do scoring + summarization logic here...
    summary = agent.summarize_emails()

    return {"summary": summary}