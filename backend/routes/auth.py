from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
import os
import datetime
from jose import jwt
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI, GMAIL_SCOPES, JWT_SECRET_KEY

router = APIRouter()
security = HTTPBearer()

class LoginRequest(BaseModel):
    auth_code: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    user_info: dict

# Store for demo purposes - in production, use a proper database
user_tokens = {}

@router.get("/google/url")
async def get_google_auth_url():
    """
    Get Google OAuth2 authorization URL
    """
    try:
        # Create the OAuth2 flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [GOOGLE_REDIRECT_URI]
                }
            },
            scopes=GMAIL_SCOPES
        )
        flow.redirect_uri = GOOGLE_REDIRECT_URI
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        return {
            "authorization_url": authorization_url,
            "state": state
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate auth URL: {str(e)}")

@router.post("/google/callback", response_model=TokenResponse)
async def google_auth_callback(login_request: LoginRequest):
    """
    Handle Google OAuth2 callback and exchange code for tokens
    """
    try:
        # Create the OAuth2 flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [GOOGLE_REDIRECT_URI]
                }
            },
            scopes=GMAIL_SCOPES
        )
        flow.redirect_uri = GOOGLE_REDIRECT_URI
        
        # Exchange authorization code for access token
        flow.fetch_token(code=login_request.auth_code)
        
        credentials = flow.credentials
        
        # Get user info
        service = build('gmail', 'v1', credentials=credentials)
        profile = service.users().getProfile(userId='me').execute()
        
        # Get user's email address
        people_service = build('people', 'v1', credentials=credentials)
        person = people_service.people().get(
            resourceName='people/me',
            personFields='emailAddresses,names'
        ).execute()
        
        email = profile.get('emailAddress', '')
        name = ''
        if 'names' in person and person['names']:
            name = person['names'][0].get('displayName', '')
        
        user_info = {
            "email": email,
            "name": name,
            "id": profile.get('historyId', email)
        }
        
        # Store tokens (in production, use a proper database)
        user_tokens[email] = {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "user_info": user_info,
            "credentials": credentials
        }
        
        return TokenResponse(
            access_token=credentials.token,
            refresh_token=credentials.refresh_token,
            user_info=user_info
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

@router.get("/callback")
async def google_auth_callback_get(code: str, state: str = None):
    """
    Handle Google OAuth2 callback (GET request from Google)
    """
    try:
        # Create the OAuth2 flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [GOOGLE_REDIRECT_URI]
                }
            },
            scopes=GMAIL_SCOPES
        )
        flow.redirect_uri = GOOGLE_REDIRECT_URI
        
        # Exchange authorization code for access token
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        
        # Get user info
        service = build('gmail', 'v1', credentials=credentials)
        profile = service.users().getProfile(userId='me').execute()
        
        # Get user's email address from People API
        try:
            people_service = build('people', 'v1', credentials=credentials)
            person = people_service.people().get(
                resourceName='people/me',
                personFields='emailAddresses,names'
            ).execute()
            
            email = profile.get('emailAddress', '')
            name = ''
            if 'names' in person and person['names']:
                name = person['names'][0].get('displayName', '')
        except Exception:
            # Fallback if People API fails
            email = profile.get('emailAddress', '')
            name = email.split('@')[0] if email else 'User'
        
        user_info = {
            "email": email,
            "name": name,
            "id": profile.get('historyId', email)
        }
        
        # Store tokens (in production, use a proper database)
        user_tokens[email] = {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "user_info": user_info,
            "credentials": credentials
        }
        
        # Create JWT token for the frontend
        jwt_payload = {
            "email": email,
            "name": name,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        jwt_token = jwt.encode(jwt_payload, JWT_SECRET_KEY, algorithm="HS256")
        
        # Redirect to frontend with tokens
        frontend_url = f"http://localhost:3000/auth/callback?token={jwt_token}&access_token={credentials.token}"
        
        # Return HTML that redirects to frontend
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>IntelliMail - Authentication Success</title>
            <script>
                window.location.href = "{frontend_url}";
            </script>
        </head>
        <body>
            <p>Authentication successful! Redirecting...</p>
            <p>If you are not redirected automatically, <a href="{frontend_url}">click here</a>.</p>
        </body>
        </html>
        """
        
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=html_content)
    
    except Exception as e:
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>IntelliMail - Authentication Error</title>
        </head>
        <body>
            <h1>Authentication Error</h1>
            <p>Error: {str(e)}</p>
            <p><a href="http://localhost:3000">Return to IntelliMail</a></p>
        </body>
        </html>
        """
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=error_html, status_code=400)

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """
    Refresh an expired access token
    """
    try:
        # Find user by refresh token
        user_data = None
        for email, data in user_tokens.items():
            if data.get('refresh_token') == refresh_token:
                user_data = data
                break
        
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        credentials = user_data['credentials']
        credentials.refresh(Request())
        
        # Update stored token
        user_data['access_token'] = credentials.token
        
        return {
            "access_token": credentials.token,
            "token_type": "bearer"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Token refresh failed: {str(e)}")

@router.post("/logout")
async def logout(current_user: dict = Depends(lambda: get_current_user)):
    """
    Logout user and invalidate tokens
    """
    try:
        email = current_user.get('email')
        if email and email in user_tokens:
            del user_tokens[email]
        
        return {"message": "Logged out successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(lambda: get_current_user)):
    """
    Get current user information
    """
    return {
        "user": current_user,
        "authenticated": True
    }

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to get current authenticated user
    """
    try:
        token = credentials.credentials
        
        # Find user by access token
        for email, data in user_tokens.items():
            if data.get('access_token') == token:
                return data['user_info']
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
