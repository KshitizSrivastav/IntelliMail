from typing import Dict, List

class ToneController:
    """
    Manages different email tone configurations and provides tone-specific instructions
    """
    
    def __init__(self):
        self.tone_configs = {
            "formal": {
                "description": "Professional and respectful language with proper business etiquette",
                "keywords": ["please", "kindly", "respectfully", "sincerely", "regards"],
                "style_instructions": [
                    "Use formal greetings and closings",
                    "Avoid contractions",
                    "Use complete sentences",
                    "Maintain professional distance"
                ],
                "avoid": ["slang", "casual expressions", "emojis", "exclamation points"]
            },
            
            "friendly": {
                "description": "Warm and approachable while maintaining professionalism",
                "keywords": ["thanks", "appreciate", "happy to", "glad", "hope"],
                "style_instructions": [
                    "Use warm greetings",
                    "Include personal touches when appropriate",
                    "Use positive language",
                    "Be conversational but professional"
                ],
                "avoid": ["overly casual language", "excessive enthusiasm"]
            },
            
            "casual": {
                "description": "Relaxed and informal communication style",
                "keywords": ["hey", "thanks", "cool", "sure", "no problem"],
                "style_instructions": [
                    "Use informal greetings",
                    "Contractions are acceptable",
                    "Keep it conversational",
                    "Be direct and to the point"
                ],
                "avoid": ["formal business language", "overly complex sentences"]
            },
            
            "professional": {
                "description": "Balanced professional tone, neither too formal nor too casual",
                "keywords": ["thank you", "please", "best regards", "appreciate", "assist"],
                "style_instructions": [
                    "Use standard business language",
                    "Be clear and concise",
                    "Maintain respectful tone",
                    "Focus on solutions and actions"
                ],
                "avoid": ["overly formal language", "casual slang"]
            },
            
            "apologetic": {
                "description": "Express regret and take responsibility while offering solutions",
                "keywords": ["sorry", "apologize", "regret", "mistake", "make it right"],
                "style_instructions": [
                    "Acknowledge the issue clearly",
                    "Take responsibility without over-explaining",
                    "Offer concrete solutions",
                    "Express genuine regret"
                ],
                "avoid": ["making excuses", "shifting blame", "being defensive"]
            },
            
            "urgent": {
                "description": "Convey importance and time-sensitivity without being aggressive",
                "keywords": ["urgent", "immediate", "time-sensitive", "priority", "asap"],
                "style_instructions": [
                    "State urgency clearly at the beginning",
                    "Provide specific deadlines",
                    "Explain the impact of delays",
                    "Remain professional despite urgency"
                ],
                "avoid": ["ALL CAPS", "excessive exclamation points", "threatening language"]
            },
            
            "grateful": {
                "description": "Express appreciation and thankfulness prominently",
                "keywords": ["thank you", "grateful", "appreciate", "thankful", "valued"],
                "style_instructions": [
                    "Lead with gratitude",
                    "Be specific about what you're thankful for",
                    "Express the impact of their help",
                    "Reciprocate when possible"
                ],
                "avoid": ["taking credit", "minimal acknowledgment"]
            },
            
            "polite": {
                "description": "Extremely courteous and considerate language",
                "keywords": ["please", "would you mind", "if possible", "when convenient", "kindly"],
                "style_instructions": [
                    "Use please and thank you liberally",
                    "Frame requests as questions",
                    "Acknowledge their time and effort",
                    "Be gracious and considerate"
                ],
                "avoid": ["demanding language", "assuming availability", "being pushy"]
            }
        }
    
    def get_tone_config(self, tone: str) -> Dict:
        """
        Get configuration for a specific tone
        """
        return self.tone_configs.get(tone.lower(), self.tone_configs["professional"])
    
    def get_all_tones(self) -> Dict[str, str]:
        """
        Get all available tones with their descriptions
        """
        return {
            tone: config["description"] 
            for tone, config in self.tone_configs.items()
        }
    
    def get_tone_keywords(self, tone: str) -> List[str]:
        """
        Get keywords associated with a specific tone
        """
        config = self.get_tone_config(tone)
        return config.get("keywords", [])
    
    def get_tone_instructions(self, tone: str) -> List[str]:
        """
        Get style instructions for a specific tone
        """
        config = self.get_tone_config(tone)
        return config.get("style_instructions", [])
    
    def get_tone_avoid_list(self, tone: str) -> List[str]:
        """
        Get list of things to avoid for a specific tone
        """
        config = self.get_tone_config(tone)
        return config.get("avoid", [])
    
    def analyze_tone_match(self, text: str, target_tone: str) -> Dict:
        """
        Analyze how well a text matches a target tone
        """
        config = self.get_tone_config(target_tone)
        keywords = config.get("keywords", [])
        avoid_words = config.get("avoid", [])
        
        text_lower = text.lower()
        
        # Count keyword matches
        keyword_matches = sum(1 for keyword in keywords if keyword in text_lower)
        keyword_score = min(keyword_matches / len(keywords), 1.0) if keywords else 0.5
        
        # Count avoid word matches (negative scoring)
        avoid_matches = sum(1 for avoid_word in avoid_words if avoid_word in text_lower)
        avoid_penalty = min(avoid_matches / len(avoid_words), 0.5) if avoid_words else 0
        
        # Calculate overall score
        overall_score = max(0, keyword_score - avoid_penalty)
        
        return {
            "tone": target_tone,
            "score": round(overall_score, 2),
            "keyword_matches": keyword_matches,
            "avoid_violations": avoid_matches,
            "suggestions": self._generate_tone_suggestions(target_tone, keyword_matches, avoid_matches)
        }
    
    def _generate_tone_suggestions(self, tone: str, keyword_matches: int, avoid_violations: int) -> List[str]:
        """
        Generate suggestions for improving tone match
        """
        suggestions = []
        config = self.get_tone_config(tone)
        
        if keyword_matches == 0:
            suggestions.append(f"Consider using words like: {', '.join(config['keywords'][:3])}")
        
        if avoid_violations > 0:
            suggestions.append(f"Avoid using: {', '.join(config['avoid'][:2])}")
        
        if tone == "formal" and avoid_violations > 0:
            suggestions.append("Use more formal language and complete sentences")
        
        if tone == "friendly" and keyword_matches < 2:
            suggestions.append("Add warmer, more personal language")
        
        if tone == "urgent" and keyword_matches == 0:
            suggestions.append("Clearly state the urgency and timeline")
        
        return suggestions
    
    def suggest_tone_alternatives(self, current_tone: str) -> List[Dict]:
        """
        Suggest alternative tones based on the current tone
        """
        alternatives = []
        
        tone_relationships = {
            "formal": ["professional", "polite"],
            "friendly": ["casual", "grateful"],
            "casual": ["friendly", "professional"],
            "professional": ["formal", "polite"],
            "apologetic": ["polite", "professional"],
            "urgent": ["professional", "formal"],
            "grateful": ["friendly", "polite"],
            "polite": ["formal", "professional"]
        }
        
        related_tones = tone_relationships.get(current_tone, ["professional", "friendly"])
        
        for tone in related_tones:
            if tone != current_tone:
                config = self.get_tone_config(tone)
                alternatives.append({
                    "tone": tone,
                    "description": config["description"],
                    "reason": f"Similar to {current_tone} but with different emphasis"
                })
        
        return alternatives
