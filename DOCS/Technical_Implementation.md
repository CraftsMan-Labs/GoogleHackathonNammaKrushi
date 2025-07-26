# Technical Implementation Guide - Namma Krushi

## Table of Contents
1. [Project Setup](#project-setup)
2. [Backend Architecture](#backend-architecture)
3. [Google AI Integration](#google-ai-integration)
4. [Voice Interface Implementation](#voice-interface-implementation)
5. [Database Implementation](#database-implementation)
6. [API Endpoints](#api-endpoints)
7. [Frontend Implementation](#frontend-implementation)
8. [Deployment Strategy](#deployment-strategy)
9. [Testing & Demo Data](#testing--demo-data)
10. [Performance Optimization](#performance-optimization)

---

## Project Setup

### Prerequisites
```bash
# Python 3.9+
python --version

# Node.js 16+ (for frontend)
node --version

# Google Cloud CLI
gcloud --version
```

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### requirements.txt (Minimal Setup)
```txt
# Core Framework
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
aiofiles==23.2.1
httpx==0.25.1

# Google AI (Minimal - Just Gemini)
google-generativeai==0.3.0

# Database
psycopg2-binary==2.9.9  # For PostgreSQL/Cloud SQL
cloud-sql-python-connector==1.5.0  # For Cloud SQL connection

# Voice (Using Web Speech API instead)
# Removed google-cloud-speech and texttospeech

# Utilities
python-dotenv==1.0.0
requests==2.31.0
pillow==10.1.0  # For image processing

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
```

### Project Structure
```
namma-krushi/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── farm.py
│   │   │   ├── todo.py
│   │   │   └── chat.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── farm.py
│   │   │   └── response.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── farms.py
│   │   │   ├── chat.py
│   │   │   ├── voice.py
│   │   │   └── market.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── gemini.py
│   │   │   ├── weather.py
│   │   │   ├── market.py
│   │   │   └── government.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       └── helpers.py
│   ├── tests/
│   ├── .env
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
├── docs/
└── docker-compose.yml
```

---

## Backend Architecture

### Core Configuration (config.py)
```python
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Namma Krushi"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./namma_krushi.db"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Google Cloud
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT")
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    # Gemini AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = "gemini-pro"
    GEMINI_VISION_MODEL: str = "gemini-pro-vision"
    
    # Firebase
    FIREBASE_CREDENTIALS: str = os.getenv("FIREBASE_CREDENTIALS")
    
    # External APIs
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY")
    WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5"
    
    # Voice Settings
    SPEECH_LANGUAGE_CODE: str = "kn-IN"  # Kannada
    VOICE_NAME: str = "kn-IN-Standard-A"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Database Setup (database.py)
```python
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Enable foreign keys for SQLite
if "sqlite" in settings.DATABASE_URL:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Enhanced Models (models/farm.py)
```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Farm(Base):
    __tablename__ = "farms"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    farm_name = Column(String, nullable=False)
    farm_code = Column(String, unique=True, index=True)  # Unique identifier
    
    # Location
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(Text)
    village = Column(String)
    district = Column(String)
    state = Column(String, default="Karnataka")
    
    # Farm Details
    total_area_acres = Column(Float)
    cultivable_area_acres = Column(Float)
    soil_type = Column(String)
    water_source = Column(String)
    irrigation_type = Column(String)
    
    # Current Crop
    current_crop = Column(String)
    crop_variety = Column(String)
    planting_date = Column(DateTime)
    expected_harvest_date = Column(DateTime)
    crop_stage = Column(String)  # seedling, vegetative, flowering, fruiting, harvesting
    crop_health_score = Column(Float, default=100.0)  # 0-100
    
    # Historical Data
    previous_crops = Column(JSON)  # List of previous crops
    average_yield = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="farms")
    daily_logs = relationship("DailyLog", back_populates="farm", cascade="all, delete-orphan")
    todos = relationship("TodoTask", back_populates="farm", cascade="all, delete-orphan")
    disease_reports = relationship("DiseaseReport", back_populates="farm", cascade="all, delete-orphan")
    weather_alerts = relationship("WeatherAlert", back_populates="farm", cascade="all, delete-orphan")
```

---

## Google AI Integration

### Gemini Service (services/gemini.py)
```python
import google.generativeai as genai
from typing import Dict, List, Optional
import base64
from PIL import Image
import io
from ..config import settings

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.text_model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.vision_model = genai.GenerativeModel(settings.GEMINI_VISION_MODEL)
        
    async def generate_response(self, prompt: str, context: Dict) -> str:
        """Generate contextual response using Gemini"""
        
        # Build enhanced prompt with context
        enhanced_prompt = self._build_contextual_prompt(prompt, context)
        
        try:
            response = self.text_model.generate_content(enhanced_prompt)
            return response.text
        except Exception as e:
            print(f"Gemini error: {e}")
            return "ಕ್ಷಮಿಸಿ, ತಾಂತ್ರಿಕ ದೋಷ ಉಂಟಾಗಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."
    
    async def analyze_crop_image(self, image_data: bytes, farm_context: Dict) -> Dict:
        """Analyze crop disease from image"""
        
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        prompt = f"""
        Analyze this crop image for diseases or pests.
        Farm context:
        - Crop: {farm_context.get('crop_type', 'Unknown')}
        - Stage: {farm_context.get('crop_stage', 'Unknown')}
        - Location: {farm_context.get('location', 'Karnataka')}
        
        Provide response in this format:
        1. Disease/Pest identified (in Kannada and English)
        2. Severity (Low/Medium/High)
        3. Immediate actions needed
        4. Organic remedies available locally
        5. Chemical treatments if necessary
        6. Prevention measures
        
        Respond in simple Kannada.
        """
        
        try:
            response = self.vision_model.generate_content([prompt, image])
            return self._parse_disease_response(response.text)
        except Exception as e:
            print(f"Vision analysis error: {e}")
            return {
                "error": True,
                "message": "ಚಿತ್ರ ವಿಶ್ಲೇಷಣೆಯಲ್ಲಿ ದೋಷ"
            }
    
    def _build_contextual_prompt(self, user_prompt: str, context: Dict) -> str:
        """Build prompt with farm context"""
        
        return f"""
        You are a helpful farming assistant responding in Kannada to a farmer.
        
        Farmer's Context:
        - Name: {context.get('user_name', 'ರೈತ')}
        - Location: {context.get('location', 'Karnataka')}
        - Current Crop: {context.get('current_crop', 'Not specified')}
        - Crop Stage: {context.get('crop_stage', 'Not specified')}
        - Weather: {context.get('weather', 'Normal')}
        - Recent Activities: {context.get('recent_activities', [])}
        
        Farmer's Question: {user_prompt}
        
        Instructions:
        1. Respond in simple Kannada
        2. Be specific and actionable
        3. Consider local context and practices
        4. If discussing remedies, mention locally available options
        5. Include cost estimates where relevant
        6. Keep response concise and practical
        """
    
    def _parse_disease_response(self, response_text: str) -> Dict:
        """Parse disease analysis response"""
        # Implementation to parse structured response
        return {
            "disease_name": "Extracted disease",
            "severity": "Medium",
            "immediate_actions": ["Action 1", "Action 2"],
            "remedies": {
                "organic": ["Neem spray", "Garlic solution"],
                "chemical": ["Fungicide XYZ"]
            },
            "prevention": ["Measure 1", "Measure 2"],
            "raw_response": response_text
        }

# Singleton instance
gemini_service = GeminiService()
```

### Voice Service (services/voice.py)
```python
from google.cloud import speech_v1
from google.cloud import texttospeech_v1
import io
import base64
from typing import Optional
from ..config import settings

class VoiceService:
    def __init__(self):
        self.speech_client = speech_v1.SpeechClient()
        self.tts_client = texttospeech_v1.TextToSpeechClient()
        
    async def speech_to_text(self, audio_data: bytes, language_code: str = None) -> str:
        """Convert speech to text"""
        
        language_code = language_code or settings.SPEECH_LANGUAGE_CODE
        
        audio = speech_v1.RecognitionAudio(content=audio_data)
        config = speech_v1.RecognitionConfig(
            encoding=speech_v1.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code=language_code,
            enable_automatic_punctuation=True,
            model="latest_long",
            use_enhanced=True,
        )
        
        try:
            response = self.speech_client.recognize(config=config, audio=audio)
            
            if response.results:
                return response.results[0].alternatives[0].transcript
            return ""
            
        except Exception as e:
            print(f"Speech recognition error: {e}")
            return ""
    
    async def text_to_speech(self, text: str, language_code: str = None) -> bytes:
        """Convert text to speech"""
        
        language_code = language_code or settings.SPEECH_LANGUAGE_CODE
        
        synthesis_input = texttospeech_v1.SynthesisInput(text=text)
        
        voice = texttospeech_v1.VoiceSelectionParams(
            language_code=language_code,
            name=settings.VOICE_NAME,
            ssml_gender=texttospeech_v1.SsmlVoiceGender.FEMALE
        )
        
        audio_config = texttospeech_v1.AudioConfig(
            audio_encoding=texttospeech_v1.AudioEncoding.MP3,
            speaking_rate=0.9,  # Slightly slower for clarity
            pitch=0.0
        )
        
        try:
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            return response.audio_content
            
        except Exception as e:
            print(f"Text-to-speech error: {e}")
            return b""

# Singleton instance
voice_service = VoiceService()
```

---

## Voice Interface Implementation

### Voice Chat API (api/voice.py)
```python
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
import json
from ..database import get_db
from ..services.voice import voice_service
from ..services.gemini import gemini_service
from ..models import User, Farm, ChatHistory
from ..utils.auth import get_current_user
from ..schemas.response import VoiceResponse

router = APIRouter(prefix="/api/voice", tags=["voice"])

@router.post("/chat", response_model=VoiceResponse)
async def voice_chat(
    audio_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Handle voice input and return voice response"""
    
    # 1. Convert speech to text
    audio_data = await audio_file.read()
    user_text = await voice_service.speech_to_text(audio_data)
    
    if not user_text:
        raise HTTPException(status_code=400, detail="Could not understand audio")
    
    # 2. Get user's farm context
    farm = db.query(Farm).filter(Farm.user_id == current_user.id).first()
    context = build_user_context(current_user, farm, db)
    
    # 3. Generate AI response
    ai_response = await gemini_service.generate_response(user_text, context)
    
    # 4. Convert response to speech
    audio_response = await voice_service.text_to_speech(ai_response)
    
    # 5. Save to chat history
    chat_entry = ChatHistory(
        user_id=current_user.id,
        farm_id=farm.id if farm else None,
        user_message=user_text,
        ai_response=ai_response,
        message_type="voice",
        metadata={
            "audio_duration": len(audio_data) / 1024,  # Approximate
            "language": "kn"
        }
    )
    db.add(chat_entry)
    db.commit()
    
    # 6. Check if any actions needed
    actions = extract_actions_from_response(ai_response, farm, db)
    
    return VoiceResponse(
        text_response=ai_response,
        audio_response=base64.b64encode(audio_response).decode(),
        user_message=user_text,
        actions=actions
    )

def build_user_context(user: User, farm: Farm, db: Session) -> Dict:
    """Build comprehensive context for AI"""
    
    context = {
        "user_name": user.name,
        "location": user.location,
        "language": "Kannada"
    }
    
    if farm:
        # Get latest weather
        weather = get_latest_weather(farm.latitude, farm.longitude)
        
        # Get recent activities
        recent_logs = db.query(DailyLog)\
            .filter(DailyLog.farm_id == farm.id)\
            .order_by(DailyLog.created_at.desc())\
            .limit(5).all()
        
        context.update({
            "current_crop": farm.current_crop,
            "crop_stage": farm.crop_stage,
            "planting_date": farm.planting_date.isoformat() if farm.planting_date else None,
            "days_since_planting": (datetime.now() - farm.planting_date).days if farm.planting_date else 0,
            "weather": weather,
            "recent_activities": [log.activity_type for log in recent_logs],
            "soil_type": farm.soil_type,
            "irrigation_type": farm.irrigation_type
        })
    
    return context

def extract_actions_from_response(response: str, farm: Farm, db: Session) -> List[Dict]:
    """Extract actionable items from AI response"""
    
    actions = []
    
    # Check for task-related keywords
    task_keywords = ["ಮಾಡಿ", "ಬೇಕು", "ಅವಶ್ಯಕ", "ಮುಖ್ಯ"]
    
    if any(keyword in response for keyword in task_keywords):
        # Use Gemini to extract tasks
        prompt = f"""
        From this farming advice, extract specific tasks:
        {response}
        
        Return as JSON array with: task_title, priority (high/medium/low), due_days
        """
        
        try:
            task_response = gemini_service.text_model.generate_content(prompt)
            tasks = json.loads(task_response.text)
            
            for task in tasks:
                actions.append({
                    "type": "create_task",
                    "data": task
                })
        except:
            pass
    
    return actions
```

### Real-time Voice Streaming
```python
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import json

@router.websocket("/stream")
async def voice_stream(
    websocket: WebSocket,
    db: Session = Depends(get_db)
):
    """Real-time voice streaming with live transcription"""
    
    await websocket.accept()
    
    # Initialize streaming session
    streaming_config = speech_v1.StreamingRecognitionConfig(
        config=speech_v1.RecognitionConfig(
            encoding=speech_v1.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code="kn-IN",
            enable_automatic_punctuation=True,
        ),
        interim_results=True,
    )
    
    audio_queue = asyncio.Queue()
    
    async def audio_processor():
        """Process audio chunks"""
        async for responses in speech_client.streaming_recognize(
            streaming_config, audio_generator()
        ):
            for response in responses:
                if response.results:
                    result = response.results[0]
                    if result.is_final:
                        await websocket.send_json({
                            "type": "final_transcript",
                            "text": result.alternatives[0].transcript
                        })
                    else:
                        await websocket.send_json({
                            "type": "interim_transcript",
                            "text": result.alternatives[0].transcript
                        })
    
    try:
        # Start audio processor
        processor_task = asyncio.create_task(audio_processor())
        
        while True:
            # Receive audio chunks
            data = await websocket.receive_bytes()
            await audio_queue.put(data)
            
    except WebSocketDisconnect:
        processor_task.cancel()
        await websocket.close()
```

---

## Database Implementation

### Advanced Models with Triggers
```python
# models/daily_log.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, event
from sqlalchemy.orm import relationship
from ..database import Base

class DailyLog(Base):
    __tablename__ = "daily_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    
    # Activity Details
    activity_type = Column(String)  # watering, fertilizing, spraying, harvesting
    activity_details = Column(JSON)
    
    # Voice Journal
    voice_note_url = Column(String)
    voice_transcript = Column(Text)
    
    # Observations
    crop_health_observation = Column(String)
    pest_spotted = Column(Boolean, default=False)
    disease_spotted = Column(Boolean, default=False)
    
    # Weather at time of log
    temperature = Column(Float)
    humidity = Column(Float)
    rainfall = Column(Float)
    weather_conditions = Column(String)
    
    # Images
    images = Column(JSON)  # List of image URLs
    
    # AI Analysis
    ai_insights = Column(Text)
    ai_recommendations = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    farm = relationship("Farm", back_populates="daily_logs")

# Trigger to update farm health score
@event.listens_for(DailyLog, 'after_insert')
def update_farm_health(mapper, connection, target):
    """Update farm health score based on daily logs"""
    if target.pest_spotted or target.disease_spotted:
        # Decrease health score
        connection.execute(
            f"UPDATE farms SET crop_health_score = crop_health_score - 10 WHERE id = {target.farm_id}"
        )
```

### Smart TODO Generation
```python
# services/todo_generator.py
from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from ..models import Farm, TodoTask, WeatherForecast

class SmartTodoGenerator:
    def __init__(self, db: Session):
        self.db = db
    
    async def generate_daily_todos(self, farm: Farm) -> List[TodoTask]:
        """Generate daily TODOs based on multiple factors"""
        
        todos = []
        
        # 1. Weather-based tasks
        weather_todos = await self._generate_weather_todos(farm)
        todos.extend(weather_todos)
        
        # 2. Crop stage-based tasks
        stage_todos = self._generate_crop_stage_todos(farm)
        todos.extend(stage_todos)
        
        # 3. Calendar-based tasks
        calendar_todos = self._generate_calendar_todos(farm)
        todos.extend(calendar_todos)
        
        # 4. Health-based tasks
        if farm.crop_health_score < 80:
            health_todos = self._generate_health_todos(farm)
            todos.extend(health_todos)
        
        return todos
    
    async def _generate_weather_todos(self, farm: Farm) -> List[TodoTask]:
        """Generate weather-based tasks"""
        
        todos = []
        forecast = await get_weather_forecast(farm.latitude, farm.longitude)
        
        # Heavy rain expected
        if forecast.get('rain_probability', 0) > 70:
            todos.append(TodoTask(
                user_id=farm.user_id,
                farm_id=farm.id,
                task_title="ಮಳೆಗೆ ಮುಂಚೆ ಕೊಯ್ಲು ಮಾಡಿ",
                task_description="ಭಾರೀ ಮಳೆ ನಿರೀಕ್ಷಿತ - ಮಾಗಿದ ಹಣ್ಣುಗಳನ್ನು ಕೊಯ್ಲು ಮಾಡಿ",
                priority="high",
                due_date=datetime.now().date(),
                is_system_generated=True,
                weather_triggered=True
            ))
            
            todos.append(TodoTask(
                user_id=farm.user_id,
                farm_id=farm.id,
                task_title="ಒಳಚರಂಡಿ ಪರಿಶೀಲಿಸಿ",
                task_description="ನೀರು ಹರಿಯಲು ಚರಂಡಿಗಳನ್ನು ಸ್ವಚ್ಛಗೊಳಿಸಿ",
                priority="medium",
                due_date=datetime.now().date(),
                is_system_generated=True,
                weather_triggered=True
            ))
        
        # High temperature expected
        if forecast.get('max_temp', 0) > 35:
            todos.append(TodoTask(
                user_id=farm.user_id,
                farm_id=farm.id,
                task_title="ಹೆಚ್ಚುವರಿ ನೀರಾವರಿ",
                task_description=f"ತಾಪಮಾನ {forecast['max_temp']}°C - ಸಂಜೆ ನೀರು ಹಾಕಿ",
                priority="high",
                due_date=datetime.now().date(),
                is_system_generated=True,
                weather_triggered=True
            ))
        
        return todos
    
    def _generate_crop_stage_todos(self, farm: Farm) -> List[TodoTask]:
        """Generate crop stage specific tasks"""
        
        todos = []
        days_since_planting = (datetime.now() - farm.planting_date).days if farm.planting_date else 0
        
        crop_schedules = {
            "tomato": {
                "fertilizer": [15, 30, 45, 60],
                "pruning": [25, 40],
                "staking": [20]
            },
            "brinjal": {
                "fertilizer": [20, 40, 60],
                "pruning": [30, 45]
            }
        }
        
        if farm.current_crop in crop_schedules:
            schedule = crop_schedules[farm.current_crop]
            
            # Check fertilizer schedule
            if days_since_planting in schedule.get("fertilizer", []):
                todos.append(TodoTask(
                    user_id=farm.user_id,
                    farm_id=farm.id,
                    task_title="ಗೊಬ್ಬರ ಹಾಕುವ ಸಮಯ",
                    task_description=f"{days_since_planting} ದಿನಗಳು - NPK ಗೊಬ್ಬರ ಹಾಕಿ",
                    priority="high",
                    due_date=datetime.now().date(),
                    is_system_generated=True
                ))
        
        return todos
```

---

## API Endpoints

### Complete API Documentation
```python
# api/farms.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/farms", tags=["farms"])

@router.post("/", response_model=FarmResponse)
async def create_farm(
    farm_data: FarmCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new farm with location validation"""
    
    # Validate location
    if not (-90 <= farm_data.latitude <= 90) or not (-180 <= farm_data.longitude <= 180):
        raise HTTPException(status_code=400, detail="Invalid coordinates")
    
    # Generate unique farm code
    farm_code = generate_farm_code(current_user.id, farm_data.farm_name)
    
    # Get location details from coordinates
    location_details = await get_location_details(farm_data.latitude, farm_data.longitude)
    
    farm = Farm(
        **farm_data.dict(),
        user_id=current_user.id,
        farm_code=farm_code,
        village=location_details.get("village"),
        district=location_details.get("district"),
        state=location_details.get("state", "Karnataka")
    )
    
    db.add(farm)
    db.commit()
    db.refresh(farm)
    
    # Generate initial tasks
    await generate_onboarding_tasks(farm, db)
    
    # Get initial weather data
    await fetch_and_store_weather(farm, db)
    
    return farm

@router.get("/{farm_id}/analytics")
async def get_farm_analytics(
    farm_id: int,
    days: int = Query(30, description="Number of days for analytics"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive farm analytics"""
    
    farm = verify_farm_ownership(farm_id, current_user.id, db)
    
    # Date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get daily logs
    logs = db.query(DailyLog).filter(
        DailyLog.farm_id == farm_id,
        DailyLog.created_at >= start_date
    ).all()
    
    # Get sales data
    sales = db.query(Sale).filter(
        Sale.farm_id == farm_id,
        Sale.sale_date >= start_date.date()
    ).all()
    
    # Calculate analytics
    analytics = {
        "summary": {
            "total_activities": len(logs),
            "health_score": farm.crop_health_score,
            "days_to_harvest": (farm.expected_harvest_date - datetime.now()).days if farm.expected_harvest_date else None,
            "total_sales": sum(sale.total_amount for sale in sales),
            "average_price": sum(sale.price_per_kg for sale in sales) / len(sales) if sales else 0
        },
        "activity_breakdown": {},
        "health_trend": [],
        "weather_impact": {},
        "sales_trend": [],
        "recommendations": []
    }
    
    # Activity breakdown
    activity_counts = {}
    for log in logs:
        activity_counts[log.activity_type] = activity_counts.get(log.activity_type, 0) + 1
    analytics["activity_breakdown"] = activity_counts
    
    # Generate AI recommendations
    recommendations = await generate_farm_recommendations(farm, analytics, db)
    analytics["recommendations"] = recommendations
    
    return analytics

@router.post("/{farm_id}/voice-note")
async def add_voice_note(
    farm_id: int,
    audio_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add voice note to daily log"""
    
    farm = verify_farm_ownership(farm_id, current_user.id, db)
    
    # Process voice
    audio_data = await audio_file.read()
    transcript = await voice_service.speech_to_text(audio_data)
    
    # Store audio file
    file_url = await store_audio_file(audio_data, farm_id)
    
    # Extract insights from transcript
    insights = await extract_insights_from_transcript(transcript, farm)
    
    # Create daily log
    log = DailyLog(
        farm_id=farm_id,
        voice_note_url=file_url,
        voice_transcript=transcript,
        ai_insights=insights.get("summary"),
        activity_type=insights.get("activity_type", "observation"),
        pest_spotted=insights.get("pest_mentioned", False),
        disease_spotted=insights.get("disease_mentioned", False)
    )
    
    db.add(log)
    
    # Create tasks if needed
    if insights.get("tasks"):
        for task in insights["tasks"]:
            todo = TodoTask(
                user_id=current_user.id,
                farm_id=farm_id,
                **task,
                is_system_generated=True
            )
            db.add(todo)
    
    db.commit()
    
    return {
        "message": "Voice note added successfully",
        "transcript": transcript,
        "insights": insights
    }
```

### Market Intelligence API
```python
# api/market.py
@router.get("/prices/current")
async def get_current_prices(
    crop: str = Query(..., description="Crop name"),
    location: Optional[str] = Query(None, description="Market location"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current market prices with AI analysis"""
    
    # Get user's location if not specified
    if not location:
        location = current_user.district or "Bangalore"
    
    # Fetch from multiple sources
    prices = await fetch_market_prices(crop, location)
    
    # Get historical data for comparison
    historical = await get_historical_prices(crop, location, days=30)
    
    # AI analysis
    analysis = await gemini_service.generate_response(
        f"Analyze market prices for {crop} in {location}. Current: {prices}, Historical: {historical}",
        {"role": "market_analyst"}
    )
    
    # Generate selling recommendation
    recommendation = await generate_selling_recommendation(
        crop, prices, historical, current_user.farms
    )
    
    return {
        "current_prices": prices,
        "trend": calculate_price_trend(historical),
        "ai_analysis": analysis,
        "recommendation": recommendation,
        "best_markets": identify_best_markets(prices),
        "price_forecast": await predict_prices(crop, location, days=7)
    }

@router.post("/price-alerts")
async def create_price_alert(
    alert: PriceAlertCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set price alerts for crops"""
    
    alert_obj = PriceAlert(
        user_id=current_user.id,
        crop_type=alert.crop_type,
        target_price=alert.target_price,
        alert_type=alert.alert_type,  # above, below
        market_location=alert.market_location,
        is_active=True
    )
    
    db.add(alert_obj)
    db.commit()
    
    return {"message": "Price alert created successfully", "alert_id": alert_obj.id}
```

---

## Frontend Implementation

### React Native Voice Interface
```javascript
// components/VoiceChat.js
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  Animated,
  StyleSheet
} from 'react-native';
import Voice from '@react-native-voice/voice';
import { Audio } from 'expo-av';

const VoiceChat = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [pulseAnim] = useState(new Animated.Value(1));

  useEffect(() => {
    Voice.onSpeechResults = onSpeechResults;
    Voice.onSpeechPartialResults = onSpeechPartialResults;
    
    return () => {
      Voice.destroy().then(Voice.removeAllListeners);
    };
  }, []);

  const startListening = async () => {
    try {
      await Voice.start('kn-IN'); // Kannada
      setIsListening(true);
      startPulseAnimation();
    } catch (e) {
      console.error(e);
    }
  };

  const stopListening = async () => {
    try {
      await Voice.stop();
      setIsListening(false);
      Animated.timing(pulseAnim).stop();
      
      // Send to backend
      const response = await sendVoiceToBackend(transcript);
      setResponse(response.text);
      
      // Play audio response
      await playAudioResponse(response.audio);
    } catch (e) {
      console.error(e);
    }
  };

  const startPulseAnimation = () => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.2,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    ).start();
  };

  const onSpeechResults = (e) => {
    setTranscript(e.value[0]);
  };

  const onSpeechPartialResults = (e) => {
    setTranscript(e.value[0]);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>ನಮ್ಮ ಕೃಷಿ ಸಹಾಯಕ</Text>
      
      <View style={styles.transcriptContainer}>
        <Text style={styles.transcriptLabel}>ನೀವು:</Text>
        <Text style={styles.transcript}>{transcript || 'ಮಾತನಾಡಲು ಕೆಳಗಿನ ಬಟನ್ ಒತ್ತಿ...'}</Text>
      </View>

      <TouchableOpacity
        onPress={isListening ? stopListening : startListening}
        style={styles.micButton}
      >
        <Animated.View
          style={[
            styles.micButtonInner,
            {
              transform: [{ scale: pulseAnim }],
              backgroundColor: isListening ? '#ff4444' : '#4CAF50',
            },
          ]}
        >
          <Text style={styles.micIcon}>{isListening ? '⏹' : '🎤'}</Text>
        </Animated.View>
      </TouchableOpacity>

      {response && (
        <View style={styles.responseContainer}>
          <Text style={styles.responseLabel}>ಸಹಾಯಕ:</Text>
          <Text style={styles.response}>{response}</Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 30,
    color: '#2e7d32',
  },
  transcriptContainer: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 10,
    marginBottom: 20,
    minHeight: 100,
  },
  transcriptLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  transcript: {
    fontSize: 18,
    color: '#333',
  },
  micButton: {
    alignSelf: 'center',
    marginVertical: 30,
  },
  micButtonInner: {
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 5,
  },
  micIcon: {
    fontSize: 40,
    color: 'white',
  },
  responseContainer: {
    backgroundColor: '#e8f5e9',
    padding: 15,
    borderRadius: 10,
    marginTop: 20,
  },
  responseLabel: {
    fontSize: 14,
    color: '#2e7d32',
    marginBottom: 5,
  },
  response: {
    fontSize: 18,
    color: '#1b5e20',
  },
});

export default VoiceChat;
```

### Farm Dashboard Component
```javascript
// components/FarmDashboard.js
import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  RefreshControl
} from 'react-native';
import { LineChart, ProgressChart } from 'react-native-chart-kit';

const FarmDashboard = ({ farmId }) => {
  const [farmData, setFarmData] = useState(null);
  const [todos, setTodos] = useState([]);
  const [weather, setWeather] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, [farmId]);

  const loadDashboardData = async () => {
    try {
      const [farmRes, todosRes, weatherRes] = await Promise.all([
        fetch(`/api/farms/${farmId}`),
        fetch(`/api/todos?farm_id=${farmId}`),
        fetch('/api/weather/current')
      ]);

      setFarmData(await farmRes.json());
      setTodos(await todosRes.json());
      setWeather(await weatherRes.json());
    } catch (error) {
      console.error('Error loading dashboard:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Weather Card */}
      <View style={styles.weatherCard}>
        <Text style={styles.cardTitle}>ಇಂದಿನ ಹವಾಮಾನ</Text>
        {weather && (
          <View style={styles.weatherInfo}>
            <Text style={styles.temperature}>{weather.temperature}°C</Text>
            <Text style={styles.weatherCondition}>{weather.condition}</Text>
            {weather.rain_probability > 50 && (
              <Text style={styles.rainAlert}>
                ⚠️ ಮಳೆಯ ಸಾಧ್ಯತೆ: {weather.rain_probability}%
              </Text>
            )}
          </View>
        )}
      </View>

      {/* Farm Health */}
      <View style={styles.healthCard}>
        <Text style={styles.cardTitle}>ಬೆಳೆ ಆರೋಗ್ಯ</Text>
        <ProgressChart
          data={{
            labels: ["ಆರೋಗ್ಯ"],
            data: [farmData?.crop_health_score / 100 || 0]
          }}
          width={300}
          height={200}
          strokeWidth={16}
          radius={32}
          chartConfig={{
            backgroundColor: '#ffffff',
            backgroundGradientFrom: '#ffffff',
            backgroundGradientTo: '#ffffff',
            color: (opacity = 1) => `rgba(76, 175, 80, ${opacity})`,
          }}
          hideLegend={false}
        />
      </View>

      {/* Today's Tasks */}
      <View style={styles.todosCard}>
        <Text style={styles.cardTitle}>ಇಂದಿನ ಕಾರ್ಯಗಳು</Text>
        {todos.filter(t => t.status === 'pending').map((todo) => (
          <TodoItem key={todo.id} todo={todo} onComplete={handleTodoComplete} />
        ))}
      </View>

      {/* Quick Actions */}
      <View style={styles.quickActions}>
        <QuickActionButton
          icon="📷"
          label="ರೋಗ ಪತ್ತೆ"
          onPress={() => navigation.navigate('DiseaseDetection')}
        />
        <QuickActionButton
          icon="💰"
          label="ಮಾರುಕಟ್ಟೆ ಬೆಲೆ"
          onPress={() => navigation.navigate('MarketPrices')}
        />
        <QuickActionButton
          icon="🎤"
          label="ಧ್ವನಿ ಟಿಪ್ಪಣಿ"
          onPress={() => navigation.navigate('VoiceNote')}
        />
        <QuickActionButton
          icon="📊"
          label="ವಿಶ್ಲೇಷಣೆ"
          onPress={() => navigation.navigate('Analytics')}
        />
      </View>
    </ScrollView>
  );
};
```

---

## Deployment Strategy

### Docker Configuration
```dockerfile
# Backend Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run migrations
RUN python -m alembic upgrade head

# Start server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/namma_krushi
      - GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/google-creds.json
    volumes:
      - ./credentials:/app/credentials
      - ./data:/app/data
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=namma_krushi
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Quick Deploy Script
```bash
#!/bin/bash
# deploy.sh

echo "🚀 Deploying Namma Krushi..."

# Load environment variables
export $(cat .env | xargs)

# Build and start services
docker-compose up -d --build

# Run migrations
docker-compose exec backend python -m alembic upgrade head

# Seed initial data
docker-compose exec backend python scripts/seed_data.py

# Health check
sleep 5
curl -f http://localhost:8000/health || exit 1

echo "✅ Deployment complete!"
echo "🌐 API: http://localhost:8000"
echo "📚 Docs: http://localhost:8000/docs"
```

---

## Testing & Demo Data

### Demo Data Seeder
```python
# scripts/seed_demo_data.py
import asyncio
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import *
from app.utils.auth import hash_password

async def seed_demo_data():
    db = SessionLocal()
    
    # Create demo user
    demo_user = User(
        name="ರಾಮು",
        email="demo@nammakrushi.com",
        password_hash=hash_password("demo123"),
        phone="+919876543210",
        location="ಮೈಸೂರು",
        district="Mysore",
        latitude=12.2958,
        longitude=76.6394
    )
    db.add(demo_user)
    db.commit()
    
    # Create demo farm
    demo_farm = Farm(
        user_id=demo_user.id,
        farm_name="ಹಸಿರು ತೋಟ",
        farm_code="DEMO001",
        latitude=12.2958,
        longitude=76.6394,
        total_area_acres=2.5,
        current_crop="ಟೊಮೇಟೊ",
        crop_variety="Hybrid-2021",
        planting_date=datetime.now() - timedelta(days=45),
        expected_harvest_date=datetime.now() + timedelta(days=30),
        crop_stage="flowering",
        soil_type="red_soil",
        irrigation_type="drip"
    )
    db.add(demo_farm)
    db.commit()
    
    # Add sample daily logs
    activities = ["watering", "fertilizing", "weeding", "spraying"]
    for i in range(30):
        log = DailyLog(
            farm_id=demo_farm.id,
            activity_type=activities[i % 4],
            notes=f"Day {i+1} activity",
            temperature=28 + (i % 5),
            humidity=65 + (i % 10),
            created_at=datetime.now() - timedelta(days=30-i)
        )
        db.add(log)
    
    # Add government schemes
    schemes = [
        {
            "scheme_name": "ಪ್ರಧಾನ ಮಂತ್ರಿ ಕಿಸಾನ್ ಸಮ್ಮಾನ್ ನಿಧಿ",
            "description": "ವಾರ್ಷಿಕ ₹6000 ನೇರ ಹಣ ವರ್ಗಾವಣೆ",
            "eligibility_criteria": "2 ಹೆಕ್ಟೇರ್‌ಗಿಂತ ಕಡಿಮೆ ಭೂಮಿ",
            "benefit_amount": "₹6000/year"
        },
        {
            "scheme_name": "ಕೃಷಿ ಸಿಂಚನ ಯೋಜನೆ",
            "description": "ಡ್ರಿಪ್ ನೀರಾವರಿಗೆ 90% ಸಬ್ಸಿಡಿ",
            "eligibility_criteria": "ಎಲ್ಲಾ ರೈತರು",
            "benefit_amount": "90% subsidy"
        }
    ]
    
    for scheme_data in schemes:
        scheme = GovernmentScheme(**scheme_data, is_active=True)
        db.add(scheme)
    
    db.commit()
    print("✅ Demo data seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_demo_data())
```

### API Testing
```python
# tests/test_voice_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_voice_chat():
    # Login first
    login_response = client.post("/auth/login", json={
        "email": "demo@nammakrushi.com",
        "password": "demo123"
    })
    token = login_response.json()["access_token"]
    
    # Test voice chat
    with open("tests/fixtures/kannada_audio.webm", "rb") as audio:
        response = client.post(
            "/api/voice/chat",
            files={"audio_file": audio},
            headers={"Authorization": f"Bearer {token}"}
        )
    
    assert response.status_code == 200
    assert "text_response" in response.json()
    assert "audio_response" in response.json()
```

---

## Performance Optimization

### Caching Strategy
```python
# utils/cache.py
import redis
import json
from functools import wraps
from typing import Optional

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def cache_result(expiration: int = 3600):
    """Cache function results in Redis"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            redis_client.setex(
                cache_key,
                expiration,
                json.dumps(result, default=str)
            )
            
            return result
        return wrapper
    return decorator

# Usage
@cache_result(expiration=1800)  # 30 minutes
async def get_weather_data(lat: float, lon: float):
    # Expensive weather API call
    pass
```

### Database Query Optimization
```python
# Optimized queries with eager loading
from sqlalchemy.orm import joinedload, selectinload

def get_farm_with_details(farm_id: int, db: Session):
    """Get farm with all related data in one query"""
    return db.query(Farm)\
        .options(
            joinedload(Farm.owner),
            selectinload(Farm.daily_logs),
            selectinload(Farm.todos).selectinload(TodoTask.user)
        )\
        .filter(Farm.id == farm_id)\
        .first()
```

### Background Tasks
```python
# Background task processing
from fastapi import BackgroundTasks

@router.post("/farms/{farm_id}/analyze")
async def analyze_farm(
    farm_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger farm analysis in background"""
    
    farm = verify_farm_ownership(farm_id, current_user.id, db)
    
    # Start analysis in background
    background_tasks.add_task(
        perform_deep_analysis,
        farm_id=farm_id,
        user_id=current_user.id
    )
    
    return {"message": "Analysis started", "status": "processing"}

async def perform_deep_analysis(farm_id: int, user_id: int):
    """Heavy analysis task"""
    db = SessionLocal()
    try:
        # Perform analysis
        results = await analyze_farm_data(farm_id)
        
        # Store results
        analysis = FarmAnalysis(
            farm_id=farm_id,
            results=results,
            completed_at=datetime.now()
        )
        db.add(analysis)
        db.commit()
        
        # Notify user
        await send_notification(user_id, "Analysis complete!")
    finally:
        db.close()
```

---

## Troubleshooting Guide

### Common Issues

1. **Voice Recognition Issues**
```python
# Add fallback for voice recognition
if not transcript:
    # Try with different language codes
    for lang in ["kn-IN", "en-IN", "hi-IN"]:
        transcript = await voice_service.speech_to_text(audio_data, lang)
        if transcript:
            break
```

2. **Database Connection Issues**
```python
# Add connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,  # Verify connections
    pool_recycle=3600    # Recycle connections after 1 hour
)
```

3. **Memory Optimization**
```python
# Stream large files
@router.get("/export/farm-data")
async def export_farm_data(farm_id: int):
    async def generate():
        # Stream data in chunks
        offset = 0
        while True:
            logs = db.query(DailyLog).filter(
                DailyLog.farm_id == farm_id
            ).offset(offset).limit(100).all()
            
            if not logs:
                break
                
            for log in logs:
                yield f"{log.to_csv()}\n"
            
            offset += 100
    
    return StreamingResponse(generate(), media_type="text/csv")
```

---

## Security Best Practices

### API Security
```python
# Rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/api/voice/chat")
@limiter.limit("10/minute")
async def voice_chat_limited(request: Request):
    pass

# Input validation
from pydantic import validator

class FarmCreate(BaseModel):
    farm_name: str
    latitude: float
    longitude: float
    
    @validator('farm_name')
    def validate_name(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Farm name must be 3-50 characters')
        return v
    
    @validator('latitude')
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Invalid latitude')
        return v
```

---

This comprehensive technical implementation guide provides everything needed to build Namma Krushi in a 5-hour hackathon, with clear code examples, configurations, and best practices for each component.