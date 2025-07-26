# crop_disease_agent.py
# Working A2A Crop Disease Diagnosis Agent using Official SDK

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Official A2A SDK imports - CORRECTED
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from a2a.types import AgentCard, AgentSkill, AgentCapabilities
import uvicorn


@dataclass
class DiagnosisResult:
    disease_name: str
    confidence: float
    symptoms_matched: List[str]
    treatment: List[str]
    timeline: str


class CropDiseaseKnowledgeBase:
    """Simple but effective crop disease database"""
    
    def __init__(self):
        self.diseases = {
            "late_blight": {
                "name": "Late Blight",
                "symptoms": ["dark spots", "white mold", "brown lesions", "leaf decay"],
                "crops": ["tomato", "potato"],
                "treatment": [
                    "Apply copper-based fungicide immediately",
                    "Remove infected plant material",
                    "Improve air circulation",
                    "Avoid overhead watering"
                ],
                "timeline": "7-14 days for improvement"
            },
            "powdery_mildew": {
                "name": "Powdery Mildew", 
                "symptoms": ["white powder", "yellowing", "stunted growth"],
                "crops": ["grape", "wheat", "rose"],
                "treatment": [
                    "Apply sulfur-based fungicide",
                    "Use milk spray (1:10 ratio with water)",
                    "Increase plant spacing",
                    "Prune for better airflow"
                ],
                "timeline": "5-10 days for improvement"
            },
            "bacterial_wilt": {
                "name": "Bacterial Wilt",
                "symptoms": ["wilting", "yellowing", "vascular browning"],
                "crops": ["tomato", "potato", "eggplant"],
                "treatment": [
                    "Remove infected plants immediately",
                    "Apply copper compounds to healthy plants",
                    "Improve soil drainage",
                    "Rotate crops next season"
                ],
                "timeline": "14-21 days for improvement"
            },
            "nitrogen_deficiency": {
                "name": "Nitrogen Deficiency",
                "symptoms": ["yellowing leaves", "stunted growth", "poor yield"],
                "crops": ["all"],
                "treatment": [
                    "Apply nitrogen-rich fertilizer",
                    "Use fish emulsion or blood meal",
                    "Apply compost",
                    "Monitor soil pH"
                ],
                "timeline": "7-14 days for improvement"
            }
        }
    
    def diagnose(self, symptoms: List[str], crop: str = "") -> DiagnosisResult:
        """Diagnose disease based on symptoms"""
        best_match = None
        best_score = 0
        
        for disease_id, disease_data in self.diseases.items():
            # Check if crop matches
            if crop and disease_data["crops"] != ["all"] and crop.lower() not in disease_data["crops"]:
                continue
                
            # Calculate symptom match score
            matched_symptoms = []
            for symptom in symptoms:
                for disease_symptom in disease_data["symptoms"]:
                    if disease_symptom.lower() in symptom.lower():
                        matched_symptoms.append(symptom)
                        break
            
            score = len(matched_symptoms) / len(disease_data["symptoms"]) if disease_data["symptoms"] else 0
            
            if score > best_score:
                best_score = score
                best_match = disease_data
                best_match["matched_symptoms"] = matched_symptoms
        
        if best_match and best_score > 0.3:  # Minimum confidence threshold
            return DiagnosisResult(
                disease_name=best_match["name"],
                confidence=best_score,
                symptoms_matched=best_match["matched_symptoms"],
                treatment=best_match["treatment"],
                timeline=best_match["timeline"]
            )
        else:
            return DiagnosisResult(
                disease_name="Unknown Condition",
                confidence=0.2,
                symptoms_matched=[],
                treatment=["Consult local agricultural extension office", "Consider lab analysis"],
                timeline="Pending proper diagnosis"
            )


class CropDiseaseAgent:
    """Main crop disease analysis agent"""
    
    def __init__(self):
        self.knowledge_base = CropDiseaseKnowledgeBase()
    
    async def diagnose(self, user_input: str) -> str:
        """Analyze user input and provide diagnosis"""
        try:
            # Simple parsing - extract symptoms and crop type
            symptoms = self._extract_symptoms(user_input)
            crop = self._extract_crop(user_input)
            
            # Get diagnosis
            diagnosis = self.knowledge_base.diagnose(symptoms, crop)
            
            # Format response
            return self._format_response(diagnosis, user_input)
            
        except Exception as e:
            logging.error(f"Error in diagnosis: {e}")
            return f"Error analyzing your crop issue: {str(e)}. Please describe your crop symptoms in detail."
    
    def _extract_symptoms(self, text: str) -> List[str]:
        """Extract symptoms from user text"""
        symptoms = []
        text_lower = text.lower()
        
        # Look for common symptom keywords
        symptom_keywords = [
            "dark spots", "white mold", "yellowing", "wilting", "brown lesions",
            "white powder", "stunted growth", "leaf decay", "spots", "mold",
            "yellow", "wilt", "brown", "decay", "powder"
        ]
        
        for keyword in symptom_keywords:
            if keyword in text_lower:
                symptoms.append(keyword)
        
        # If no specific symptoms found, add the whole description
        if not symptoms:
            symptoms.append(text_lower)
            
        return symptoms
    
    def _extract_crop(self, text: str) -> str:
        """Extract crop type from user text"""
        text_lower = text.lower()
        crops = ["tomato", "potato", "corn", "wheat", "grape", "eggplant", "rose"]
        
        for crop in crops:
            if crop in text_lower:
                return crop
        return ""
    
    def _format_response(self, diagnosis: DiagnosisResult, original_query: str) -> str:
        """Format the diagnosis into a comprehensive response"""
        
        confidence_percent = f"{diagnosis.confidence:.0%}"
        
        response = f"""
🌱 CROP DISEASE DIAGNOSIS REPORT
=====================================

📊 DIAGNOSIS SUMMARY
Disease Identified: {diagnosis.disease_name}
Confidence Level: {confidence_percent}

🔍 ANALYSIS
Your Query: {original_query}

Symptoms Matched: {', '.join(diagnosis.symptoms_matched) if diagnosis.symptoms_matched else 'General symptoms observed'}

💊 TREATMENT PLAN
"""
        
        for i, treatment in enumerate(diagnosis.treatment, 1):
            response += f"{i}. {treatment}\n"
        
        response += f"""
⏱️ EXPECTED TIMELINE
{diagnosis.timeline}

✅ MONITORING & VALIDATION
- Take photos before treatment for comparison
- Monitor daily for symptom changes
- Document treatment applications
- Reassess after recommended timeline
- Contact extension office if no improvement

🛡️ PREVENTION MEASURES
- Maintain proper plant spacing
- Ensure good air circulation
- Water at soil level, not on leaves
- Regular crop rotation
- Monitor weather conditions

📞 NEXT STEPS
1. Begin treatment immediately if confidence is high
2. Isolate affected plants if possible
3. Monitor closely for changes
4. Seek professional help if symptoms worsen

---
Confidence: {confidence_percent} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
*For severe cases or uncertain diagnosis, consult your local agricultural extension office*
"""
        return response


class CropDiseaseAgentExecutor(AgentExecutor):
    """A2A Agent Executor - handles the protocol interface"""
    
    def __init__(self):
        super().__init__()
        self.agent = CropDiseaseAgent()
    
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Handle incoming requests"""
        try:
            # Get user input from the context
            user_input = context.get_user_input() or ""
            
            if not user_input:
                response = "Please describe your crop disease symptoms, including the type of crop and what you're observing."
            else:
                # Run the diagnosis
                response = await self.agent.diagnose(user_input)
            
            # Send response back through event queue
            event_queue.enqueue_event(new_agent_text_message(response))
            
        except Exception as e:
            logging.error(f"Error in agent executor: {e}")
            error_response = f"I encountered an error: {str(e)}. Please try again with a description of your crop symptoms."
            event_queue.enqueue_event(new_agent_text_message(error_response))
    
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Handle cancellation requests"""
        event_queue.enqueue_event(new_agent_text_message("Crop diagnosis task cancelled."))


def create_agent_card() -> AgentCard:
    """Create the agent card that describes this agent's capabilities"""
    
    # Define what this agent can do
    skills = [
        AgentSkill(
            id="crop_disease_diagnosis",
            name="Crop Disease Diagnosis", 
            description="Diagnose plant diseases from symptom descriptions and provide treatment recommendations",
            tags=["agriculture", "plant pathology", "disease diagnosis", "farming"],
            examples=[
                "My tomato plants have dark spots on the leaves",
                "White powder appearing on grape leaves", 
                "Corn plants turning yellow and wilting",
                "Potato plants showing brown lesions"
            ]
        ),
        AgentSkill(
            id="treatment_planning",
            name="Treatment Planning",
            description="Provide detailed treatment plans for identified crop diseases",
            tags=["treatment", "agriculture", "pest management"],
            examples=[
                "How to treat late blight in tomatoes",
                "Organic solutions for powdery mildew"
            ]
        ),
        AgentSkill(
            id="prevention_advice", 
            name="Prevention & Monitoring",
            description="Advice on preventing crop diseases and monitoring plant health",
            tags=["prevention", "monitoring", "crop management"],
            examples=[
                "How to prevent fungal diseases",
                "Best practices for crop monitoring"
            ]
        )
    ]
    
    return AgentCard(
        name="Crop Disease Diagnosis Agent",
        description="AI-powered agricultural assistant specializing in crop disease identification and treatment recommendations",
        version="1.0.0",
        url="http://localhost:8000/",
        defaultInputModes=["text/plain"],
        defaultOutputModes=["text/plain", "text/markdown"],
        capabilities=AgentCapabilities(
            streaming=True,
            stateTransitionHistory=False,
            pushNotifications=False
        ),
        skills=skills
    )


def main():
    """Start the A2A agent server"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🌱 Starting Crop Disease Diagnosis A2A Agent...")
    
    # Create the agent card
    agent_card = create_agent_card()
    
    # Create the request handler
    request_handler = DefaultRequestHandler(
        agent_executor=CropDiseaseAgentExecutor(),
        task_store=InMemoryTaskStore()
    )
    
    # Create the A2A application
    app_builder = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )
    
    print("✅ Agent configured successfully")
    print("📍 Agent URL: http://localhost:8000")
    print("🔍 Agent Card: http://localhost:8000/.well-known/agent.json")
    print("🚀 Starting server...")
    
    # Start the server
    uvicorn.run(
        app_builder.build(),
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()