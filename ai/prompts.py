"""
AI Prompt Templates for IntelliMail
"""

class EmailPrompts:
    """
    Collection of prompt templates for email-related AI operations
    """
    
    @staticmethod
    def summarize_email_prompt(email_content: str, max_length: int = 150) -> str:
        """
        Generate prompt for email summarization
        """
        return f"""
        You are an expert email assistant. Summarize the following email content clearly and professionally.
        
        Requirements:
        - Maximum length: {max_length} words
        - Extract 3-5 key points
        - Focus on actionable items and important information
        - Maintain professional tone
        - Identify the main purpose of the email
        
        Email Content:
        {email_content}
        
        Format your response as JSON:
        {{
            "summary": "Brief, clear summary of the email",
            "key_points": ["point1", "point2", "point3"],
            "main_purpose": "primary purpose of the email",
            "action_required": "yes/no - whether action is required from recipient"
        }}
        """
    
    @staticmethod
    def summarize_thread_prompt(thread_content: str, email_count: int, max_length: int = 200) -> str:
        """
        Generate prompt for email thread summarization
        """
        return f"""
        You are an expert email assistant. Summarize this email thread containing {email_count} emails.
        
        Requirements:
        - Maximum length: {max_length} words
        - Show conversation progression and key decisions
        - Extract main topics and action items
        - Identify key participants and their roles
        - Highlight any conflicts or agreements
        
        Thread Content:
        {thread_content}
        
        Format your response as JSON:
        {{
            "summary": "Comprehensive summary of the entire thread",
            "key_points": ["point1", "point2", "point3", "point4"],
            "participants": ["participant1", "participant2"],
            "decisions_made": ["decision1", "decision2"],
            "action_items": ["action1", "action2"],
            "thread_outcome": "current status or outcome"
        }}
        """
    
    @staticmethod
    def generate_reply_prompt(original_email: str, tone: str, length: str, 
                            context: str = None, custom_instructions: str = None) -> str:
        """
        Generate prompt for email reply generation
        """
        length_instructions = {
            "short": "Keep the response brief and to the point (50-100 words)",
            "medium": "Provide a balanced response (100-200 words)",
            "long": "Provide a detailed and comprehensive response (200-300 words)"
        }
        
        context_section = f"\n\nAdditional Context:\n{context}" if context else ""
        custom_section = f"\n\nCustom Instructions:\n{custom_instructions}" if custom_instructions else ""
        
        return f"""
        You are an intelligent email assistant. Generate a professional email reply to the following email.
        
        Instructions:
        - Write in a {tone} tone
        - {length_instructions[length]}
        - Address all main points from the original email
        - Be helpful and provide clear value
        - Use appropriate greetings and professional closings
        - Sound natural and human-like
        - Do not include a subject line in your response
        {context_section}
        {custom_section}
        
        Original Email:
        {original_email}
        
        Generate a thoughtful, well-structured reply that addresses the sender's needs and maintains a {tone} tone throughout.
        """
    
    @staticmethod
    def refine_reply_prompt(original_reply: str, target_tone: str, instructions: str = None) -> str:
        """
        Generate prompt for refining email replies
        """
        instruction_section = f"\n\nAdditional Instructions:\n{instructions}" if instructions else ""
        
        return f"""
        You are an email editing specialist. Refine the following email reply to match a {target_tone} tone.
        
        Requirements:
        - Maintain the core message and main points
        - Adjust language, style, and approach to match {target_tone} tone
        - Keep the same level of professionalism
        - Preserve any important details or information
        - Ensure the response flows naturally
        {instruction_section}
        
        Original Reply:
        {original_reply}
        
        Provide the refined version that better matches the {target_tone} tone while preserving the essential message.
        """
    
    @staticmethod
    def analyze_tone_prompt(text: str) -> str:
        """
        Generate prompt for tone analysis
        """
        return f"""
        You are a communication expert specializing in tone analysis. Analyze the tone of the following text.
        
        Text to analyze:
        {text}
        
        Provide a detailed analysis including:
        - Primary tone identification
        - Confidence level in your assessment
        - Secondary tones present
        - Professional/personal classification
        - Emotional undertones
        - Suggestions for improvement
        
        Format your response as JSON:
        {{
            "primary_tone": "main tone (e.g., formal, friendly, urgent, professional)",
            "confidence": 0.85,
            "secondary_tones": ["tone1", "tone2"],
            "tone_scores": {{
                "formal": 0.8,
                "friendly": 0.3,
                "professional": 0.9,
                "casual": 0.1,
                "urgent": 0.2,
                "polite": 0.7
            }},
            "classification": "professional/personal",
            "emotional_undertones": ["positive", "neutral", "concerned"],
            "suggestions": ["suggestion1", "suggestion2"]
        }}
        """
    
    @staticmethod
    def extract_action_items_prompt(email_content: str) -> str:
        """
        Generate prompt for extracting action items
        """
        return f"""
        You are a task management expert. Extract clear, actionable items from the following email content.
        
        Focus on:
        - Specific tasks that require follow-up
        - Deadlines and time-sensitive items
        - Requests for information or action
        - Meeting or appointment scheduling
        - Document or deliverable requirements
        
        Email Content:
        {email_content}
        
        Format your response as JSON:
        {{
            "action_items": [
                {{
                    "task": "Clear description of the task",
                    "priority": "high/medium/low",
                    "deadline": "deadline if mentioned",
                    "assigned_to": "person responsible if clear",
                    "type": "task/meeting/deliverable/information_request"
                }}
            ],
            "follow_up_required": true/false,
            "next_steps": ["step1", "step2"]
        }}
        """
    
    @staticmethod
    def categorize_email_prompt(email_content: str) -> str:
        """
        Generate prompt for email categorization
        """
        return f"""
        You are an email organization expert. Categorize the following email into appropriate categories.
        
        Available categories:
        - Important: Critical business matters, urgent requests
        - Meetings: Meeting invitations, scheduling, calendar items
        - Projects: Project updates, deliverables, collaboration
        - FYI: Informational emails, updates, newsletters
        - Personal: Personal communications, non-work related
        - Marketing: Promotional emails, advertisements, sales
        - Support: Technical support, customer service, help requests
        - Finance: Invoices, payments, financial matters
        - HR: Human resources, policies, benefits
        - Spam: Unwanted or suspicious emails
        
        Email Content:
        {email_content}
        
        Format your response as JSON:
        {{
            "primary_category": "main category",
            "secondary_categories": ["category1", "category2"],
            "confidence": 0.85,
            "reasoning": "brief explanation for categorization",
            "tags": ["tag1", "tag2", "tag3"],
            "priority_level": "high/medium/low"
        }}
        """
    
    @staticmethod
    def suggest_subject_prompt(email_content: str, is_reply: bool = False) -> str:
        """
        Generate prompt for suggesting email subjects
        """
        reply_context = "This is a reply email. " if is_reply else "This is a new email. "
        
        return f"""
        You are an email communication specialist. Suggest an appropriate subject line for the following email content.
        
        {reply_context}Generate a subject line that:
        - Clearly summarizes the main topic
        - Is concise but informative (5-8 words ideal)
        - Uses appropriate professional language
        - Helps the recipient understand the email's purpose
        - Follows email best practices
        
        Email Content:
        {email_content}
        
        Format your response as JSON:
        {{
            "suggested_subject": "primary suggestion",
            "alternatives": ["alternative1", "alternative2", "alternative3"],
            "reasoning": "explanation for the suggestion"
        }}
        """
    
    @staticmethod
    def smart_compose_prompt(context: str, purpose: str, recipient_info: str = None) -> str:
        """
        Generate prompt for smart email composition
        """
        recipient_section = f"\n\nRecipient Information:\n{recipient_info}" if recipient_info else ""
        
        return f"""
        You are an expert email composer. Create a professional email based on the following requirements.
        
        Context: {context}
        Purpose: {purpose}
        {recipient_section}
        
        Requirements:
        - Write a complete, professional email
        - Include appropriate subject line
        - Use professional greeting and closing
        - Structure the content logically
        - Be clear, concise, and actionable
        - Maintain professional tone throughout
        
        Generate a well-structured email that effectively communicates the intended message.
        """

class TonePrompts:
    """
    Tone-specific prompt modifiers and templates
    """
    
    TONE_MODIFIERS = {
        "formal": {
            "prefix": "Use formal business language with proper etiquette. ",
            "style": "Avoid contractions, use complete sentences, maintain professional distance. ",
            "closing": "Use formal closings like 'Sincerely' or 'Best regards'."
        },
        "friendly": {
            "prefix": "Use warm and approachable language while maintaining professionalism. ",
            "style": "Include personal touches, use positive language, be conversational. ",
            "closing": "Use warm closings like 'Best wishes' or 'Warm regards'."
        },
        "casual": {
            "prefix": "Use relaxed and informal communication style. ",
            "style": "Contractions are fine, keep it conversational and direct. ",
            "closing": "Use casual closings like 'Thanks' or 'Cheers'."
        },
        "urgent": {
            "prefix": "Convey importance and time-sensitivity clearly. ",
            "style": "State urgency early, provide specific deadlines, explain impact. ",
            "closing": "Emphasize the timeline in your closing."
        },
        "apologetic": {
            "prefix": "Express genuine regret and take responsibility. ",
            "style": "Acknowledge the issue, avoid excuses, offer concrete solutions. ",
            "closing": "Reaffirm your commitment to making things right."
        }
    }
    
    @staticmethod
    def get_tone_instruction(tone: str) -> str:
        """
        Get tone-specific instruction for prompts
        """
        modifier = TonePrompts.TONE_MODIFIERS.get(tone.lower(), TonePrompts.TONE_MODIFIERS["formal"])
        return modifier["prefix"] + modifier["style"] + modifier["closing"]
