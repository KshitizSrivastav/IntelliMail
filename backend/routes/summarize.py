from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

from services.gpt_handler import GPTService
from services.gmail_client import GmailService
from services.auth_service import get_current_user

router = APIRouter()

class SummarizeRequest(BaseModel):
    thread_id: Optional[str] = None
    email_id: Optional[str] = None
    email_content: Optional[str] = None
    max_length: Optional[int] = 150

class SummarizeResponse(BaseModel):
    summary: str
    key_points: List[str]
    original_length: int
    summary_length: int
    compression_ratio: float

@router.post("/", response_model=SummarizeResponse)
async def summarize_email(
    request: SummarizeRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Summarize an email or email thread using AI
    """
    try:
        content_to_summarize = ""
        
        # Get content based on the request type
        if request.email_content:
            content_to_summarize = request.email_content
        elif request.email_id:
            gmail_service = GmailService(current_user['access_token'])
            email_detail = gmail_service.get_email_detail(request.email_id)
            content_to_summarize = f"Subject: {email_detail.get('subject', '')}\n\nFrom: {email_detail.get('sender', '')}\n\n{email_detail.get('body', '')}"
        elif request.thread_id:
            gmail_service = GmailService(current_user['access_token'])
            thread_emails = gmail_service.get_thread_emails(request.thread_id)
            
            # Combine all emails in the thread
            thread_content = []
            for email in thread_emails:
                email_text = f"From: {email.get('sender', '')}\nDate: {email.get('date', '')}\nSubject: {email.get('subject', '')}\n\n{email.get('body', '')}\n\n---\n\n"
                thread_content.append(email_text)
            
            content_to_summarize = "".join(thread_content)
        else:
            raise HTTPException(status_code=400, detail="Must provide either email_content, email_id, or thread_id")
        
        if not content_to_summarize.strip():
            raise HTTPException(status_code=400, detail="No content to summarize")
        
        # Generate summary using GPT
        gpt_service = GPTService()
        summary_result = await gpt_service.summarize_email(
            content=content_to_summarize,
            max_length=request.max_length
        )
        
        original_length = len(content_to_summarize)
        summary_length = len(summary_result['summary'])
        compression_ratio = round((1 - summary_length / original_length) * 100, 2) if original_length > 0 else 0
        
        return SummarizeResponse(
            summary=summary_result['summary'],
            key_points=summary_result['key_points'],
            original_length=original_length,
            summary_length=summary_length,
            compression_ratio=compression_ratio
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to summarize email: {str(e)}")

@router.post("/thread/{thread_id}", response_model=SummarizeResponse)
async def summarize_thread(
    thread_id: str,
    max_length: Optional[int] = 200,
    current_user: dict = Depends(get_current_user)
):
    """
    Summarize an entire email thread
    """
    try:
        gmail_service = GmailService(current_user['access_token'])
        thread_emails = gmail_service.get_thread_emails(thread_id)
        
        if not thread_emails:
            raise HTTPException(status_code=404, detail="Thread not found or empty")
        
        # Combine all emails in the thread with proper formatting
        thread_content = []
        for i, email in enumerate(thread_emails, 1):
            email_text = f"Email {i}:\nFrom: {email.get('sender', '')}\nDate: {email.get('date', '')}\nSubject: {email.get('subject', '')}\n\n{email.get('body', '')}\n\n{'='*50}\n\n"
            thread_content.append(email_text)
        
        full_thread = "".join(thread_content)
        
        # Generate summary using GPT
        gpt_service = GPTService()
        summary_result = await gpt_service.summarize_email_thread(
            thread_content=full_thread,
            email_count=len(thread_emails),
            max_length=max_length
        )
        
        original_length = len(full_thread)
        summary_length = len(summary_result['summary'])
        compression_ratio = round((1 - summary_length / original_length) * 100, 2) if original_length > 0 else 0
        
        return SummarizeResponse(
            summary=summary_result['summary'],
            key_points=summary_result['key_points'],
            original_length=original_length,
            summary_length=summary_length,
            compression_ratio=compression_ratio
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to summarize thread: {str(e)}")

@router.post("/bulk")
async def summarize_multiple_emails(
    email_ids: List[str],
    current_user: dict = Depends(get_current_user)
):
    """
    Summarize multiple emails at once
    """
    try:
        gmail_service = GmailService(current_user['access_token'])
        gpt_service = GPTService()
        
        summaries = []
        
        for email_id in email_ids:
            try:
                email_detail = gmail_service.get_email_detail(email_id)
                content = f"Subject: {email_detail.get('subject', '')}\n\nFrom: {email_detail.get('sender', '')}\n\n{email_detail.get('body', '')}"
                
                summary_result = await gpt_service.summarize_email(content=content, max_length=100)
                
                summaries.append({
                    "email_id": email_id,
                    "subject": email_detail.get('subject', ''),
                    "sender": email_detail.get('sender', ''),
                    "summary": summary_result['summary'],
                    "key_points": summary_result['key_points']
                })
            except Exception as e:
                summaries.append({
                    "email_id": email_id,
                    "error": f"Failed to summarize: {str(e)}"
                })
        
        return {
            "summaries": summaries,
            "total_processed": len(email_ids),
            "successful": len([s for s in summaries if 'error' not in s]),
            "failed": len([s for s in summaries if 'error' in s])
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process bulk summarization: {str(e)}")
