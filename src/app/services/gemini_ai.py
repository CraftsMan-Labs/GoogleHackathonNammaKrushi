from __future__ import annotations

import os
import json
from typing import Optional, Dict, Any, List
import google.generativeai as genai
from ..models.user import User
from ..models.farm import Farm
from ..config.settings import settings

# Configure Gemini AI
genai.configure(api_key=settings.GEMINI_API_KEY)

class GeminiAIService:
    """Service for interacting with Google's Gemini AI."""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        
    def _build_context_prompt(
        self, 
        user: User, 
        farm: Optional[Farm] = None,
        message_type: str = "general"
    ) -> str:
        """Build context prompt for the AI based on user and farm data."""
        
        context = f"""You are Namma Krushi AI, an intelligent farming assistant specifically designed for Karnataka farmers. 
        
User Information:
- Name: {user.name}
- Location: {user.location}, {user.district}, Karnataka
- Phone: {user.phone}

"""
        
        if farm:
            context += f"""Farm Information:
- Farm Name: {farm.farm_name}
- Total Area: {farm.total_area_acres} acres
- Current Crop: {farm.current_crop} ({farm.crop_variety})
- Crop Stage: {farm.crop_stage}
- Soil Type: {farm.soil_type}
- Irrigation: {farm.irrigation_type}
- Water Source: {farm.water_source}
- Crop Health Score: {farm.crop_health_score}/100

"""

        context += f"""Instructions:
1. Respond in a mix of Kannada and English as appropriate for Karnataka farmers
2. Be practical, actionable, and specific to Karnataka's agricultural conditions
3. Consider the current season and local farming practices
4. Provide step-by-step guidance when needed
5. Be encouraging and supportive
6. If asked about diseases/pests, ask for photos if not provided
7. Include relevant government schemes when applicable
8. Keep responses concise but informative
9. Use simple language that farmers can understand
10. Include cost-effective solutions

Message Type: {message_type}

Respond as a knowledgeable, friendly farming expert who understands both traditional and modern farming practices in Karnataka.
"""
        
        return context
    
    def _build_farming_knowledge_prompt(self) -> str:
        """Build farming knowledge specific to Karnataka."""
        return """
Karnataka Farming Context:
- Major crops: Rice, Ragi, Maize, Cotton, Sugarcane, Coconut, Arecanut, Coffee, Cardamom
- Seasons: Kharif (June-Oct), Rabi (Nov-Feb), Summer (Mar-May)
- Common soil types: Red soil, Black soil, Laterite soil, Alluvial soil
- Major districts: Mysore, Mandya, Hassan, Tumkur, Kolar, Bangalore Rural
- Common pests: Bollworm, Stem borer, Aphids, Thrips
- Common diseases: Blast, Blight, Wilt, Rust
- Water sources: Bore wells, Canals, Tanks, Rivers (Cauvery, Krishna)
- Government schemes: PM-KISAN, PMFBY, Soil Health Card, PMKSY

Weather patterns:
- Monsoon: June-September (Southwest), October-December (Northeast)
- Summer: March-May (hot and dry)
- Winter: December-February (mild and dry)
"""

    async def generate_response(
        self,
        user_message: str,
        user: User,
        farm: Optional[Farm] = None,
        message_type: str = "general",
        language: str = "kn"
    ) -> Dict[str, Any]:
        """Generate AI response using Gemini."""
        
        try:
            # Build the complete prompt
            context_prompt = self._build_context_prompt(user, farm, message_type)
            farming_knowledge = self._build_farming_knowledge_prompt()
            
            full_prompt = f"""
{context_prompt}

{farming_knowledge}

User's Question: {user_message}

Please provide a helpful, practical response. If the user is asking in Kannada, respond primarily in Kannada with some English technical terms. If asking in English, respond in English with some Kannada phrases for familiarity.
"""
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            # Extract and clean the response
            ai_response = response.text.strip()
            
            # Determine confidence score based on response quality
            confidence_score = self._calculate_confidence_score(ai_response, message_type)
            
            # Determine if follow-up is needed
            follow_up_needed = self._needs_follow_up(user_message, ai_response)
            
            # Generate action items if applicable
            actions = self._extract_actions(ai_response, message_type)
            
            return {
                "response": ai_response,
                "confidence_score": confidence_score,
                "follow_up_needed": follow_up_needed,
                "actions_triggered": actions,
                "context_data": {
                    "message_type": message_type,
                    "farm_id": farm.id if farm else None,
                    "language": language,
                    "user_location": f"{user.location}, {user.district}"
                }
            }
            
        except Exception as e:
            # Fallback to a basic response if Gemini fails
            return self._generate_fallback_response(user_message, user, message_type)
    
    def _calculate_confidence_score(self, response: str, message_type: str) -> float:
        """Calculate confidence score based on response characteristics."""
        score = 0.7  # Base score
        
        # Increase score for longer, more detailed responses
        if len(response) > 200:
            score += 0.1
        if len(response) > 400:
            score += 0.1
            
        # Increase score for specific message types with technical content
        technical_keywords = [
            "fertilizer", "pesticide", "irrigation", "soil", "crop", "disease",
            "ಗೊಬ್ಬರ", "ಕೀಟನಾಶಕ", "ನೀರಾವರಿ", "ಮಣ್ಣು", "ಬೆಳೆ", "ರೋಗ"
        ]
        
        keyword_count = sum(1 for keyword in technical_keywords if keyword.lower() in response.lower())
        score += min(keyword_count * 0.02, 0.15)
        
        return min(score, 1.0)
    
    def _needs_follow_up(self, user_message: str, ai_response: str) -> bool:
        """Determine if the conversation needs follow-up."""
        follow_up_indicators = [
            "more information", "details", "photo", "image", "picture",
            "ಹೆಚ್ಚಿನ ಮಾಹಿತಿ", "ಚಿತ್ರ", "ಫೋಟೋ"
        ]
        
        return any(indicator in ai_response.lower() for indicator in follow_up_indicators)
    
    def _extract_actions(self, response: str, message_type: str) -> List[str]:
        """Extract actionable items from the response."""
        actions = []
        
        # Check for common action patterns
        if "weather" in message_type and ("check" in response.lower() or "forecast" in response.lower()):
            actions.append("check_weather")
            
        if "todo" in response.lower() or "reminder" in response.lower():
            actions.append("create_todo")
            
        if "scheme" in response.lower() or "subsidy" in response.lower():
            actions.append("check_schemes")
            
        return actions
    
    def _generate_fallback_response(
        self, 
        user_message: str, 
        user: User, 
        message_type: str
    ) -> Dict[str, Any]:
        """Generate a fallback response when Gemini API fails."""
        
        fallback_responses = {
            "weather": f"ನಮಸ್ಕಾರ {user.name}, ಹವಾಮಾನ ಮಾಹಿತಿಗಾಗಿ ದಯವಿಟ್ಟು ಸ್ಥಳೀಯ ಹವಾಮಾನ ವರದಿಯನ್ನು ಪರಿಶೀಲಿಸಿ. ನಾನು ಈಗ ತಾಂತ್ರಿಕ ಸಮಸ್ಯೆಯನ್ನು ಎದುರಿಸುತ್ತಿದ್ದೇನೆ.",
            "disease": f"ನಮಸ್ಕಾರ {user.name}, ಬೆಳೆಯ ಸಮಸ್ಯೆಗಳಿಗೆ ಸ್ಥಳೀಯ ಕೃಷಿ ಅಧಿಕಾರಿಯನ್ನು ಸಂಪರ್ಕಿಸಿ. ನಾನು ಈಗ ತಾಂತ್ರಿಕ ಸಮಸ್ಯೆಯನ್ನು ಎದುರಿಸುತ್ತಿದ್ದೇನೆ.",
            "market": f"ನಮಸ್ಕಾರ {user.name}, ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳಿಗಾಗಿ ಸ್ಥಳೀಯ ಮಂಡಿಯನ್ನು ಸಂಪರ್ಕಿಸಿ. ನಾನು ಈಗ ತಾಂತ್ರಿಕ ಸಮಸ್ಯೆಯನ್ನು ಎದುರಿಸುತ್ತಿದ್ದೇನೆ.",
            "general": f"ನಮಸ್ಕಾರ {user.name}, ಕ್ಷಮಿಸಿ, ನಾನು ಈಗ ತಾಂತ್ರಿಕ ಸಮಸ್ಯೆಯನ್ನು ಎದುರಿಸುತ್ತಿದ್ದೇನೆ. ದಯವಿಟ್ಟು ಸ್ವಲ್ಪ ಸಮಯದ ನಂತರ ಪ್ರಯತ್ನಿಸಿ."
        }
        
        response_text = fallback_responses.get(message_type, fallback_responses["general"])
        
        return {
            "response": response_text,
            "confidence_score": 0.3,
            "follow_up_needed": False,
            "actions_triggered": [],
            "context_data": {
                "message_type": message_type,
                "fallback": True,
                "language": "kn"
            }
        }

# Global instance
gemini_service = GeminiAIService()