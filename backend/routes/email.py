from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import json

from services.gmail_client import GmailService
from services.auth_service import get_current_user

router = APIRouter()

class EmailResponse(BaseModel):
    id: str
    subject: str
    sender: str
    date: str
    snippet: str
    thread_id: str
    is_read: bool

class EmailDetail(BaseModel):
    id: str
    subject: str
    sender: str
    recipient: str
    date: str
    body: str
    thread_id: str
    is_read: bool

@router.get("/", response_model=List[EmailResponse])
async def get_emails(
    max_results: int = 10,
    query: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Fetch emails from user's Gmail inbox
    """
    try:
        gmail_service = GmailService(current_user['access_token'])
        emails = gmail_service.get_emails(max_results=max_results, query=query)
        
        email_responses = []
        for email in emails:
            email_responses.append(EmailResponse(
                id=email['id'],
                subject=email.get('subject', 'No Subject'),
                sender=email.get('sender', 'Unknown'),
                date=email.get('date', ''),
                snippet=email.get('snippet', ''),
                thread_id=email.get('thread_id', ''),
                is_read=email.get('is_read', False)
            ))
        
        return email_responses
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch emails: {str(e)}")

@router.get("/{email_id}", response_model=EmailDetail)
async def get_email_detail(
    email_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed view of a specific email
    """
    try:
        gmail_service = GmailService(current_user['access_token'])
        email_detail = gmail_service.get_email_detail(email_id)
        
        return EmailDetail(
            id=email_detail['id'],
            subject=email_detail.get('subject', 'No Subject'),
            sender=email_detail.get('sender', 'Unknown'),
            recipient=email_detail.get('recipient', 'Unknown'),
            date=email_detail.get('date', ''),
            body=email_detail.get('body', ''),
            thread_id=email_detail.get('thread_id', ''),
            is_read=email_detail.get('is_read', False)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch email detail: {str(e)}")

@router.get("/thread/{thread_id}")
async def get_email_thread(
    thread_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all emails in a thread
    """
    try:
        gmail_service = GmailService(current_user['access_token'])
        thread_emails = gmail_service.get_thread_emails(thread_id)
        
        return {
            "thread_id": thread_id,
            "emails": thread_emails,
            "message_count": len(thread_emails)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch email thread: {str(e)}")

@router.post("/send")
async def send_email(
    email_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Send an email through Gmail API
    """
    try:
        gmail_service = GmailService(current_user['access_token'])
        
        # Validate required fields
        required_fields = ['to', 'subject', 'body']
        for field in required_fields:
            if field not in email_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        result = gmail_service.send_email(
            to=email_data['to'],
            subject=email_data['subject'],
            body=email_data['body'],
            reply_to_id=email_data.get('reply_to_id')
        )
        
        return {
            "success": True,
            "message_id": result['id'],
            "message": "Email sent successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

@router.put("/{email_id}/mark-read")
async def mark_email_read(
    email_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark an email as read
    """
    try:
        gmail_service = GmailService(current_user['access_token'])
        gmail_service.mark_as_read(email_id)
        
        return {
            "success": True,
            "message": "Email marked as read"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark email as read: {str(e)}")
