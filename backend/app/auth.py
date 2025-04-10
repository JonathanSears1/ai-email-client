from fastapi import APIRouter, Request
from requests_oauthlib import OAuth2Session
import os

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

# Step 1: Generate login URL
@router.get("/auth/login")
def login():
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPES)
    authorization_url, state = oauth.authorization_url(
        'https://accounts.google.com/o/oauth2/auth',
        access_type="offline",
        prompt="consent"
    )
    return {"auth_url": authorization_url}

# Step 2: Handle callback
@router.get("/auth/callback")
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

    return {
        "email": user_info.get("email"),
        "access_token": token.get("access_token"),
        "refresh_token": token.get("refresh_token"),
        "expires_in": token.get("expires_in"),
        "id_token": token.get("id_token")
    }
