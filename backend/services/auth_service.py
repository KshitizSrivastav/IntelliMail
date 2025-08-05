from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict

security = HTTPBearer()

# In-memory storage for demo purposes
# In production, use a proper database and JWT tokens
user_sessions = {}

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """
    Dependency to get current authenticated user from token
    """
    try:
        token = credentials.credentials
        
        # In this demo, we'll import the user_tokens from auth.py
        # In production, you'd validate JWT tokens or query a database
        from routes.auth import user_tokens
        
        # Find user by access token
        for email, data in user_tokens.items():
            if data.get('access_token') == token:
                # Add the access token to user info for services
                user_info = data['user_info'].copy()
                user_info['access_token'] = token
                return user_info
        
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

def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict]:
    """
    Optional user dependency for endpoints that work with or without authentication
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None

def require_admin_user(current_user: Dict = Depends(get_current_user)) -> Dict:
    """
    Dependency that requires admin privileges
    """
    # In a real application, you'd check user roles/permissions
    if not current_user.get('is_admin', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return current_user

def validate_email_access(email_id: str, current_user: Dict = Depends(get_current_user)) -> bool:
    """
    Validate that the current user has access to a specific email
    """
    # In a real application, you'd verify that the email belongs to the user
    # For now, we'll assume all authenticated users can access their own emails
    return True

class AuthService:
    """
    Service class for handling authentication-related operations
    """
    
    @staticmethod
    def create_session(user_info: Dict, access_token: str) -> str:
        """
        Create a user session and return session ID
        """
        session_id = f"session_{user_info['email']}_{len(user_sessions)}"
        user_sessions[session_id] = {
            "user_info": user_info,
            "access_token": access_token,
            "created_at": "2025-01-01T00:00:00Z"  # In real app, use current timestamp
        }
        return session_id
    
    @staticmethod
    def get_session(session_id: str) -> Optional[Dict]:
        """
        Get session data by session ID
        """
        return user_sessions.get(session_id)
    
    @staticmethod
    def invalidate_session(session_id: str) -> bool:
        """
        Invalidate a user session
        """
        if session_id in user_sessions:
            del user_sessions[session_id]
            return True
        return False
    
    @staticmethod
    def refresh_session(session_id: str, new_access_token: str) -> bool:
        """
        Refresh session with new access token
        """
        if session_id in user_sessions:
            user_sessions[session_id]['access_token'] = new_access_token
            return True
        return False
