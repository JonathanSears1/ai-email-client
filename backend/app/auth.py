from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from requests_oauthlib import OAuth2Session
import os
import database
import crud
from auth_utils import create_access_token, get_current_user
from fastapi import Depends

router = APIRouter()

# Environment variables
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

# Scopes
SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events.owned",
    "openid"
]

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Step 1: Generate login URL
@router.get("/login")
def login():
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPES)
    authorization_url, state = oauth.authorization_url(
        'https://accounts.google.com/o/oauth2/auth',
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    return {"auth_url": authorization_url}

# Step 2: Handle callback
@router.get("/callback")
async def callback(request: Request):
    authorization_response = str(request.url)

    oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPES)
    token = oauth.fetch_token(
        'https://oauth2.googleapis.com/token',
        authorization_response=authorization_response,
        client_secret=CLIENT_SECRET
    )

    # Step 3: Get user profile info
    r = oauth.get('https://www.googleapis.com/oauth2/v1/userinfo')
    user_info = r.json()
    
    # Get database session
    db = next(get_db())
    try:
        user = crud.create_or_update_user(
            db=db,
            email=user_info.get("email"),
            name=user_info.get("name"),
            token=token
        )
        access_token = create_access_token(data={"sub": user.email})
        print(access_token)
        redirect_url = f"http://localhost:3000/auth/callback?token={access_token}"
        return RedirectResponse(redirect_url)
    finally:
        db.close()

@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": "This is a protected route", "user": current_user}