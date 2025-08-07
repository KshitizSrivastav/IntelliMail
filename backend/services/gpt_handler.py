import openai
from typing import Dict, List, Optional
import json
import asyncio
import logging

from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

class GPTService:
    def __init__(self):
        try:
            if not OPENAI_API_KEY:
                logger.warning("⚠️  OpenAI API key not provided")
                self.client = None
            else:
                self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
                logger.info("✅ OpenAI client initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI client: {e}")
            self.client = None
    
    async def summarize_email(self, content: str, max_length: int = 150) -> Dict:
        """
        Summarize email content using GPT-4
        """
        if not self.client:
            return {
                "summary": "OpenAI service not available",
                "key_points": ["OpenAI API key not configured"]
            }
            
        try:
            prompt = f"""
            You are an expert email assistant. Summarize the following email content in a clear, concise manner.
            
            Requirements:
            - Maximum length: {max_length} words
            - Extract 3-5 key points
            - Maintain professional tone
            - Focus on actionable items and important information
            
            Email Content:
            {content}
            
            Provide the response in JSON format:
            {{
                "summary": "Brief summary of the email",
                "key_points": ["point1", "point2", "point3"]
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful email summarization assistant. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "summary": response.choices[0].message.content[:max_length],
                "key_points": ["Summary generation completed", "Please review the content"]
            }
        except Exception as e:
            raise Exception(f"Failed to summarize email: {str(e)}")
    
    async def summarize_email_thread(self, thread_content: str, email_count: int, max_length: int = 200) -> Dict:
        """
        Summarize an entire email thread
        """
        try:
            prompt = f"""
            You are an expert email assistant. Summarize this email thread containing {email_count} emails.
            
            Requirements:
            - Maximum length: {max_length} words
            - Show conversation flow and key decisions
            - Extract main topics and action items
            - Identify key participants and their roles
            
            Thread Content:
            {thread_content}
            
            Provide the response in JSON format:
            {{
                "summary": "Brief summary of the entire thread",
                "key_points": ["point1", "point2", "point3", "point4", "point5"]
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful email thread summarization assistant. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except json.JSONDecodeError:
            return {
                "summary": response.choices[0].message.content[:max_length],
                "key_points": ["Thread summary generated", "Multiple emails processed"]
            }
        except Exception as e:
            raise Exception(f"Failed to summarize email thread: {str(e)}")
    
    async def generate_reply(self, original_email: str, tone: str, length: str, 
                           context: Optional[str] = None, custom_instructions: Optional[str] = None,
                           tone_config: Optional[Dict] = None) -> Dict:
        """
        Generate an email reply using GPT-4
        """
        try:
            # Length mapping
            length_instructions = {
                "short": "Keep the response brief and to the point (50-100 words)",
                "medium": "Provide a balanced response (100-200 words)",
                "long": "Provide a detailed and comprehensive response (200-300 words)"
            }
            
            # Build tone instruction
            tone_instruction = f"Write in a {tone} tone"
            if tone_config:
                tone_instruction += f". {tone_config.get('description', '')}"
                if 'keywords' in tone_config:
                    tone_instruction += f" Use appropriate language such as: {', '.join(tone_config['keywords'][:3])}"
            
            context_text = f"\n\nAdditional Context: {context}" if context else ""
            custom_text = f"\n\nCustom Instructions: {custom_instructions}" if custom_instructions else ""
            
            prompt = f"""
            You are an intelligent email assistant. Generate a professional email reply to the following email.
            
            Instructions:
            - {tone_instruction}
            - {length_instructions[length]}
            - Address the main points from the original email
            - Be helpful and provide value
            - Include appropriate greetings and closings
            {context_text}
            {custom_text}
            
            Original Email:
            {original_email}
            
            Generate a reply that sounds natural and human-like. Do not include a subject line.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"You are a helpful email writing assistant. Write professional emails in a {tone} tone."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.4
            )
            
            reply_content = response.choices[0].message.content.strip()
            
            return {
                "reply": reply_content,
                "confidence_score": 0.85,  # Could be calculated based on various factors
                "word_count": len(reply_content.split())
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate reply: {str(e)}")
    
    async def refine_reply(self, original_reply: str, target_tone: str, 
                          tone_config: Optional[Dict] = None, instructions: Optional[str] = None) -> Dict:
        """
        Refine an existing reply with different tone or instructions
        """
        try:
            tone_instruction = f"Rewrite this email in a {target_tone} tone"
            if tone_config:
                tone_instruction += f". {tone_config.get('description', '')}"
            
            instruction_text = f"\n\nAdditional Instructions: {instructions}" if instructions else ""
            
            prompt = f"""
            {tone_instruction}
            
            Keep the core message and main points, but adjust the language, style, and approach to match the requested tone.
            {instruction_text}
            
            Original Reply:
            {original_reply}
            
            Provide the refined version:
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"You are a helpful email editing assistant. Refine emails to match specific tones while maintaining the core message."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.3
            )
            
            refined_content = response.choices[0].message.content.strip()
            
            return {
                "reply": refined_content,
                "changes_summary": [f"Adjusted tone to {target_tone}", "Refined language and style"]
            }
            
        except Exception as e:
            raise Exception(f"Failed to refine reply: {str(e)}")
    
    async def analyze_tone(self, text: str) -> Dict:
        """
        Analyze the tone of given text
        """
        try:
            prompt = f"""
            Analyze the tone of the following text. Identify the primary tone and provide confidence scores.
            
            Text to analyze:
            {text}
            
            Provide the response in JSON format:
            {{
                "primary_tone": "dominant tone (e.g., formal, friendly, urgent)",
                "confidence": 0.85,
                "tone_scores": {{
                    "formal": 0.8,
                    "friendly": 0.2,
                    "professional": 0.9,
                    "casual": 0.1,
                    "urgent": 0.1
                }},
                "suggestions": ["suggestion1", "suggestion2"]
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a tone analysis expert. Analyze text tone and provide detailed insights in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except json.JSONDecodeError:
            return {
                "primary_tone": "neutral",
                "confidence": 0.5,
                "tone_scores": {"neutral": 0.5},
                "suggestions": ["Unable to analyze tone accurately"]
            }
        except Exception as e:
            raise Exception(f"Failed to analyze tone: {str(e)}")
    
    async def extract_action_items(self, email_content: str) -> List[str]:
        """
        Extract action items from email content
        """
        try:
            prompt = f"""
            Extract action items and tasks from the following email content.
            Focus on specific, actionable tasks that require follow-up.
            
            Email Content:
            {email_content}
            
            List action items as a JSON array:
            ["action1", "action2", "action3"]
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an action item extraction specialist. Extract clear, actionable tasks from email content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.2
            )
            
            action_items = json.loads(response.choices[0].message.content)
            return action_items if isinstance(action_items, list) else []
            
        except (json.JSONDecodeError, Exception):
            return ["Unable to extract action items"]
