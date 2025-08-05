from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Literal
from enum import Enum

from services.gpt_handler import GPTService
from services.gmail_client import GmailService
from services.tone_control import ToneController
from services.auth_service import get_current_user

router = APIRouter()

class ToneType(str, Enum):
    FORMAL = "formal"
    FRIENDLY = "friendly"
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    APOLOGETIC = "apologetic"
    URGENT = "urgent"
    GRATEFUL = "grateful"
    POLITE = "polite"

class ReplyRequest(BaseModel):
    email_id: Optional[str] = None
    email_content: Optional[str] = None
    context: Optional[str] = None
    tone: ToneType = ToneType.PROFESSIONAL
    length: Literal["short", "medium", "long"] = "medium"
    include_signature: bool = True
    custom_instructions: Optional[str] = None

class ReplyResponse(BaseModel):
    generated_reply: str
    tone_used: str
    confidence_score: float
    suggested_subject: Optional[str] = None
    alternative_replies: Optional[List[str]] = None

@router.post("/generate", response_model=ReplyResponse)
async def generate_reply(
    request: ReplyRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate an AI-powered email reply
    """
    try:
        content_to_reply = ""
        original_subject = ""
        sender_name = ""
        
        # Get email content if email_id is provided
        if request.email_id:
            gmail_service = GmailService(current_user['access_token'])
            email_detail = gmail_service.get_email_detail(request.email_id)
            content_to_reply = email_detail.get('body', '')
            original_subject = email_detail.get('subject', '')
            sender_name = email_detail.get('sender', '')
        elif request.email_content:
            content_to_reply = request.email_content
        else:
            raise HTTPException(status_code=400, detail="Must provide either email_id or email_content")
        
        if not content_to_reply.strip():
            raise HTTPException(status_code=400, detail="No content to reply to")
        
        # Generate reply using GPT with tone control
        gpt_service = GPTService()
        tone_controller = ToneController()
        
        # Get tone-specific prompt modifications
        tone_config = tone_controller.get_tone_config(request.tone.value)
        
        reply_result = await gpt_service.generate_reply(
            original_email=content_to_reply,
            tone=request.tone.value,
            length=request.length,
            context=request.context,
            custom_instructions=request.custom_instructions,
            tone_config=tone_config
        )
        
        # Generate suggested subject line
        suggested_subject = None
        if original_subject:
            if not original_subject.lower().startswith('re:'):
                suggested_subject = f"Re: {original_subject}"
            else:
                suggested_subject = original_subject
        
        # Generate alternative replies with different tones
        alternative_replies = []
        if request.tone != ToneType.FORMAL:
            try:
                formal_reply = await gpt_service.generate_reply(
                    original_email=content_to_reply,
                    tone="formal",
                    length=request.length,
                    context=request.context,
                    tone_config=tone_controller.get_tone_config("formal")
                )
                alternative_replies.append(formal_reply['reply'])
            except:
                pass
        
        if request.tone != ToneType.FRIENDLY:
            try:
                friendly_reply = await gpt_service.generate_reply(
                    original_email=content_to_reply,
                    tone="friendly",
                    length=request.length,
                    context=request.context,
                    tone_config=tone_controller.get_tone_config("friendly")
                )
                alternative_replies.append(friendly_reply['reply'])
            except:
                pass
        
        return ReplyResponse(
            generated_reply=reply_result['reply'],
            tone_used=request.tone.value,
            confidence_score=reply_result.get('confidence_score', 0.85),
            suggested_subject=suggested_subject,
            alternative_replies=alternative_replies[:2] if alternative_replies else None
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate reply: {str(e)}")

@router.post("/refine")
async def refine_reply(
    reply_text: str,
    target_tone: ToneType,
    refinement_instructions: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Refine an existing reply with different tone or instructions
    """
    try:
        gpt_service = GPTService()
        tone_controller = ToneController()
        
        tone_config = tone_controller.get_tone_config(target_tone.value)
        
        refined_reply = await gpt_service.refine_reply(
            original_reply=reply_text,
            target_tone=target_tone.value,
            tone_config=tone_config,
            instructions=refinement_instructions
        )
        
        return {
            "refined_reply": refined_reply['reply'],
            "original_tone": "unknown",
            "new_tone": target_tone.value,
            "changes_made": refined_reply.get('changes_summary', [])
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refine reply: {str(e)}")

@router.post("/analyze-tone")
async def analyze_tone(
    text: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze the tone of a given text
    """
    try:
        gpt_service = GPTService()
        
        tone_analysis = await gpt_service.analyze_tone(text)
        
        return {
            "detected_tone": tone_analysis.get('primary_tone', 'neutral'),
            "confidence": tone_analysis.get('confidence', 0.0),
            "tone_breakdown": tone_analysis.get('tone_scores', {}),
            "suggestions": tone_analysis.get('suggestions', [])
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze tone: {str(e)}")

@router.get("/tones")
async def get_available_tones():
    """
    Get list of available tones with descriptions
    """
    tone_controller = ToneController()
    return {
        "available_tones": tone_controller.get_all_tones(),
        "default_tone": "professional"
    }

@router.post("/template")
async def create_reply_template(
    template_name: str,
    template_content: str,
    tone: ToneType,
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a reusable reply template
    """
    try:
        # In a real application, you'd save this to a database
        # For now, we'll return a success response
        
        template_data = {
            "name": template_name,
            "content": template_content,
            "tone": tone.value,
            "category": category,
            "created_by": current_user.get('email', 'unknown'),
            "created_at": "2025-01-01T00:00:00Z"  # In real app, use current timestamp
        }
        
        return {
            "success": True,
            "template": template_data,
            "message": "Template created successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")
