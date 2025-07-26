# Gemini Live API Implementation - Namma Krushi

## Overview
Ultra-simplified architecture using:
- **Gemini Live API** for real-time voice conversations
- **SQLite** local database (no cloud database needed)
- **Single API key** setup (just Gemini)
- **Direct deployment** to any server/VM

---

## Minimal Requirements

### Only ONE API Key Needed!
```bash
# Get from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your-gemini-api-key
```

### Simplified requirements.txt
```txt
# Core
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Gemini Live API
google-generativeai==0.3.2

# Database (SQLite - built-in!)
# No additional packages needed

# Image processing
pillow==10.1.0

# Utilities
python-dotenv==1.0.0
aiofiles==23.2.1
websockets==12.0
```

---

## Gemini Live API Integration

### Core Live Service (services/gemini_live.py)
```python
import google.generativeai as genai
from typing import Dict, AsyncGenerator, Optional
import asyncio
import json
import sqlite3
from datetime import datetime
from ..config import settings

class GeminiLiveService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Initialize Gemini Live model
        self.model = genai.GenerativeModel(
            model_name='gemini-pro',
            generation_config={
                'temperature': 0.7,
                'top_p': 0.8,
                'top_k': 40,
                'max_output_tokens': 2048,
            }
        )
        
        # System prompt for farming context
        self.system_prompt = """
        You are a Kannada-speaking farming assistant helping Indian farmers.
        Always respond in simple Kannada.
        Provide practical, actionable advice.
        Consider local farming practices and conditions.
        Be concise and clear.
        """
        
    async def start_live_session(self, user_id: int, farm_id: int) -> Dict:
        """Start a live conversation session"""
        
        # Get user context from SQLite
        context = await self.get_user_context(user_id, farm_id)
        
        # Create conversation with context
        chat = self.model.start_chat(history=[
            {
                "role": "user",
                "parts": [f"System: {self.system_prompt}\nContext: {json.dumps(context, ensure_ascii=False)}"]
            },
            {
                "role": "model", 
                "parts": ["ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ ಕೃಷಿ ಸಹಾಯಕ. ನಿಮ್ಮ ಬೆಳೆಯ ಬಗ್ಗೆ ಏನಾದರೂ ಸಹಾಯ ಬೇಕೇ?"]
            }
        ])
        
        return {
            "session_id": f"session_{user_id}_{datetime.now().timestamp()}",
            "chat": chat,
            "context": context
        }
    
    async def stream_response(
        self, 
        chat, 
        user_input: str,
        session_id: str
    ) -> AsyncGenerator[str, None]:
        """Stream response from Gemini"""
        
        try:
            # Send message and get streaming response
            response = await chat.send_message_async(
                user_input,
                stream=True
            )
            
            full_response = ""
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
                    full_response += chunk.text
            
            # Save to conversation history
            await self.save_conversation(session_id, user_input, full_response)
            
            # Extract and execute any actions
            await self.process_actions(full_response, session_id)
            
        except Exception as e:
            yield f"ಕ್ಷಮಿಸಿ, ದೋಷ: {str(e)}"
    
    async def get_user_context(self, user_id: int, farm_id: int) -> Dict:
        """Get context from SQLite database"""
        
        conn = sqlite3.connect('namma_krushi.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get user info
        user = cursor.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        
        # Get farm info
        farm = cursor.execute(
            "SELECT * FROM farms WHERE id = ?", (farm_id,)
        ).fetchone()
        
        # Get recent activities
        activities = cursor.execute(
            """SELECT * FROM daily_logs 
               WHERE farm_id = ? 
               ORDER BY created_at DESC 
               LIMIT 5""", 
            (farm_id,)
        ).fetchall()
        
        # Get pending todos
        todos = cursor.execute(
            """SELECT * FROM todo_tasks 
               WHERE user_id = ? AND status = 'pending'
               ORDER BY due_date ASC 
               LIMIT 5""", 
            (user_id,)
        ).fetchall()
        
        conn.close()
        
        return {
            "user_name": dict(user)["name"] if user else "ರೈತ",
            "location": dict(user)["location"] if user else "Karnataka",
            "farm": dict(farm) if farm else {},
            "recent_activities": [dict(a) for a in activities],
            "pending_tasks": [dict(t) for t in todos],
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            "season": self.get_current_season()
        }
    
    async def save_conversation(self, session_id: str, user_input: str, response: str):
        """Save conversation to SQLite"""
        
        conn = sqlite3.connect('namma_krushi.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO chat_history (session_id, user_message, ai_response, created_at)
            VALUES (?, ?, ?, ?)
        """, (session_id, user_input, response, datetime.now()))
        
        conn.commit()
        conn.close()
    
    async def process_actions(self, response: str, session_id: str):
        """Extract and execute actions from response"""
        
        # Use Gemini to extract actions
        action_prompt = f"""
        From this response, extract any farming tasks or actions mentioned:
        {response}
        
        Return as JSON array with: task, priority, due_days
        If no tasks, return empty array.
        """
        
        try:
            action_response = self.model.generate_content(action_prompt)
            actions = json.loads(action_response.text)
            
            if actions:
                conn = sqlite3.connect('namma_krushi.db')
                cursor = conn.cursor()
                
                for action in actions:
                    cursor.execute("""
                        INSERT INTO todo_tasks 
                        (user_id, task_title, priority, due_date, is_system_generated)
                        VALUES (?, ?, ?, date('now', '+' || ? || ' days'), 1)
                    """, (
                        self.get_user_from_session(session_id),
                        action['task'],
                        action['priority'],
                        action.get('due_days', 1)
                    ))
                
                conn.commit()
                conn.close()
        except:
            pass  # Silently fail action extraction
    
    def get_current_season(self):
        """Get current agricultural season"""
        month = datetime.now().month
        if month in [6, 7, 8, 9]:
            return "ಖರೀಫ್ (Kharif)"
        elif month in [10, 11, 12, 1]:
            return "ರಬಿ (Rabi)"
        else:
            return "ಜಾಯಿದ್ (Zaid)"

# Singleton instance
gemini_live = GeminiLiveService()
```

### WebSocket API for Live Chat
```python
# api/live_chat.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict
import json
import asyncio
from ..services.gemini_live import gemini_live
from ..database import get_db
from ..utils.auth import get_current_user_ws

router = APIRouter()

# Store active sessions
active_sessions: Dict[str, Dict] = {}

@router.websocket("/ws/chat/{user_id}/{farm_id}")
async def websocket_chat(
    websocket: WebSocket,
    user_id: int,
    farm_id: int
):
    await websocket.accept()
    
    try:
        # Start Gemini Live session
        session_data = await gemini_live.start_live_session(user_id, farm_id)
        session_id = session_data["session_id"]
        chat = session_data["chat"]
        
        # Store session
        active_sessions[session_id] = session_data
        
        # Send initial greeting
        await websocket.send_json({
            "type": "greeting",
            "message": "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ ಕೃಷಿ ಸಹಾಯಕ. ಏನು ಸಹಾಯ ಬೇಕು?",
            "session_id": session_id
        })
        
        # Handle messages
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            if data["type"] == "voice":
                # Voice data as base64
                user_input = data["transcript"]
            else:
                # Text input
                user_input = data["message"]
            
            # Send typing indicator
            await websocket.send_json({
                "type": "typing",
                "status": True
            })
            
            # Stream response from Gemini
            response_text = ""
            async for chunk in gemini_live.stream_response(chat, user_input, session_id):
                response_text += chunk
                
                # Send chunks to client
                await websocket.send_json({
                    "type": "response_chunk",
                    "chunk": chunk
                })
            
            # Send complete response
            await websocket.send_json({
                "type": "response_complete",
                "message": response_text,
                "timestamp": datetime.now().isoformat()
            })
            
    except WebSocketDisconnect:
        # Clean up session
        if session_id in active_sessions:
            del active_sessions[session_id]
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"ದೋಷ: {str(e)}"
        })
        await websocket.close()
```

### Frontend WebSocket Client
```javascript
// services/GeminiLiveChat.js
class GeminiLiveChat {
  constructor(userId, farmId) {
    this.userId = userId;
    this.farmId = farmId;
    this.ws = null;
    this.sessionId = null;
    this.onMessage = null;
    this.onTyping = null;
  }

  connect() {
    const wsUrl = `ws://localhost:8000/ws/chat/${this.userId}/${this.farmId}`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('Connected to Gemini Live');
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch(data.type) {
        case 'greeting':
          this.sessionId = data.session_id;
          if (this.onMessage) {
            this.onMessage(data.message, 'assistant');
          }
          break;
          
        case 'typing':
          if (this.onTyping) {
            this.onTyping(data.status);
          }
          break;
          
        case 'response_chunk':
          // Handle streaming response
          if (this.onChunk) {
            this.onChunk(data.chunk);
          }
          break;
          
        case 'response_complete':
          if (this.onMessage) {
            this.onMessage(data.message, 'assistant');
          }
          if (this.onTyping) {
            this.onTyping(false);
          }
          break;
          
        case 'error':
          console.error('Chat error:', data.message);
          break;
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('Disconnected from Gemini Live');
      // Attempt reconnection after 3 seconds
      setTimeout(() => this.connect(), 3000);
    };
  }

  sendMessage(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'text',
        message: message
      }));
    }
  }

  sendVoice(transcript) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'voice',
        transcript: transcript
      }));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

// React Component using Gemini Live
import React, { useState, useEffect, useRef } from 'react';

const LiveChatComponent = ({ userId, farmId }) => {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [currentResponse, setCurrentResponse] = useState('');
  const chatRef = useRef(null);

  useEffect(() => {
    // Initialize Gemini Live Chat
    const chat = new GeminiLiveChat(userId, farmId);
    
    chat.onMessage = (message, sender) => {
      setMessages(prev => [...prev, { text: message, sender, timestamp: new Date() }]);
      setCurrentResponse('');
    };
    
    chat.onTyping = (status) => {
      setIsTyping(status);
    };
    
    chat.onChunk = (chunk) => {
      setCurrentResponse(prev => prev + chunk);
    };
    
    chat.connect();
    chatRef.current = chat;

    return () => {
      chat.disconnect();
    };
  }, [userId, farmId]);

  const handleSendMessage = (message) => {
    // Add user message to UI
    setMessages(prev => [...prev, { text: message, sender: 'user', timestamp: new Date() }]);
    
    // Send to Gemini Live
    chatRef.current.sendMessage(message);
  };

  const handleVoiceInput = async () => {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'kn-IN';
    
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      handleSendMessage(transcript);
    };
    
    recognition.start();
  };

  return (
    <div className="live-chat-container">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.sender}`}>
            <span className="text">{msg.text}</span>
            <span className="time">{msg.timestamp.toLocaleTimeString()}</span>
          </div>
        ))}
        
        {currentResponse && (
          <div className="message assistant streaming">
            <span className="text">{currentResponse}</span>
            <span className="cursor">▊</span>
          </div>
        )}
        
        {isTyping && !currentResponse && (
          <div className="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        )}
      </div>
      
      <div className="input-area">
        <button onClick={handleVoiceInput} className="voice-btn">
          🎤 ಮಾತನಾಡಿ
        </button>
        <input
          type="text"
          placeholder="ಇಲ್ಲಿ ಟೈಪ್ ಮಾಡಿ..."
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              handleSendMessage(e.target.value);
              e.target.value = '';
            }
          }}
        />
      </div>
    </div>
  );
};
```

---

## SQLite Database Setup

### database.py (SQLite)
```python
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# SQLite database file
DATABASE_URL = "sqlite:///./namma_krushi.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Enable foreign keys for SQLite
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

# Initialize database
def init_db():
    Base.metadata.create_all(bind=engine)
```

### Simplified Models
```python
# models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    location = Column(String)
    created_at = Column(DateTime, default=func.now())

class Farm(Base):
    __tablename__ = "farms"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    farm_name = Column(String, nullable=False)
    crop_type = Column(String)
    area_acres = Column(Float)
    created_at = Column(DateTime, default=func.now())

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    user_message = Column(Text)
    ai_response = Column(Text)
    created_at = Column(DateTime, default=func.now())

class TodoTask(Base):
    __tablename__ = "todo_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    task_title = Column(String, nullable=False)
    priority = Column(String, default="medium")
    status = Column(String, default="pending")
    due_date = Column(DateTime)
    is_system_generated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

class DailyLog(Base):
    __tablename__ = "daily_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, nullable=False)
    activity = Column(String)
    notes = Column(Text)
    weather = Column(String)
    created_at = Column(DateTime, default=func.now())
```

---

## Simplified Configuration

### config.py
```python
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Namma Krushi"
    VERSION: str = "1.0.0"
    
    # Only ONE API key needed!
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")
    
    # Database (SQLite - no config needed!)
    DATABASE_URL: str = "sqlite:///./namma_krushi.db"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### .env file
```bash
# Only ONE key needed!
GEMINI_API_KEY=your-gemini-api-key
SECRET_KEY=your-secret-key
```

---

## Main Application

### main.py
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from .database import init_db
from .api import auth, farms, live_chat
from .config import settings

# Create app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-powered farming assistant with Gemini Live"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(farms.router, prefix="/api/farms", tags=["farms"])
app.include_router(live_chat.router, tags=["live-chat"])

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "gemini": "connected" if settings.GEMINI_API_KEY else "not configured",
        "database": "sqlite"
    }

# Serve static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Docker Deployment (Super Simple!)

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Create data directory for SQLite
RUN mkdir -p /app/data

# Volume for persistent SQLite data
VOLUME ["/app/data"]

# Environment
ENV DATABASE_URL=sqlite:////app/data/namma_krushi.db

# Port
EXPOSE 8000

# Run
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    volumes:
      - ./data:/app/data  # Persist SQLite database
      - ./uploads:/app/uploads  # Persist uploaded images
    restart: unless-stopped
```

---

## Quick Start (5 Minutes!)

```bash
# 1. Clone and setup
git clone <your-repo>
cd namma-krushi

# 2. Add your Gemini API key
echo "GEMINI_API_KEY=your-key-here" > .env

# 3. Run with Docker
docker-compose up -d

# 4. Access app
open http://localhost:8000

# That's it! 🎉
```

---

## Deploy Anywhere!

### Option 1: Any Linux VPS
```bash
# SSH to your server
ssh user@your-server

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone and run
git clone <your-repo>
cd namma-krushi
echo "GEMINI_API_KEY=your-key" > .env
docker-compose up -d
```

### Option 2: GCP Compute Engine (Free Tier)
```bash
# Create instance
gcloud compute instances create namma-krushi \
  --machine-type=e2-micro \
  --zone=us-central1-a \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud

# SSH and deploy
gcloud compute ssh namma-krushi
# Then follow Linux VPS steps above
```

### Option 3: Local Development
```bash
# Without Docker
pip install -r requirements.txt
export GEMINI_API_KEY=your-key
python -m uvicorn app.main:app --reload
```

---

## Cost Analysis

### Total Monthly Cost: $0 - $5
- **Gemini API**: Free tier (60 requests/minute)
- **Database**: SQLite (free, local file)
- **Server**: 
  - Local: $0
  - GCP e2-micro: Free tier eligible
  - Any VPS: ~$5/month

### No Cloud Services Needed!
- ❌ No Cloud SQL
- ❌ No Cloud Storage
- ❌ No Cloud Speech API
- ✅ Just Gemini API key!

---

## Demo Features

### 1. Live Voice Chat
```javascript
// Farmer speaks in Kannada
"ನನ್ನ ಟೊಮೇಟೊ ಎಲೆಗಳು ಹಳದಿ ಆಗುತ್ತಿವೆ"

// Gemini Live responds instantly
"ಹಳದಿ ಎಲೆಗಳು ಸಾರಜನಕದ ಕೊರತೆಯ ಲಕ್ಷಣ. 
ತಕ್ಷಣ ಯೂರಿಯಾ 50 ಗ್ರಾಂ/ಲೀಟರ್ ನೀರಿನಲ್ಲಿ ಕರಗಿಸಿ ಸಿಂಪಡಿಸಿ..."
```

### 2. Image Analysis
```python
# Upload crop photo
# Gemini analyzes and responds
"ಈ ಚಿತ್ರದಲ್ಲಿ ಎಲೆ ಕುಳಿ ರೋಗ ಕಾಣುತ್ತಿದೆ..."
```

### 3. Smart TODOs
```python
# Gemini automatically creates tasks
"ನಾಳೆ ಮಳೆ ಬರಬಹುದು, ಇಂದೇ ಕೊಯ್ಲು ಮಾಡಿ"
# → Creates TODO with high priority
```

---

## Advantages of This Approach

1. **Ultra Simple**: One API key, one database file
2. **No Cloud Lock-in**: Deploy anywhere
3. **Cost Effective**: Nearly free to run
4. **Fast Development**: No complex setup
5. **Offline Capable**: SQLite works offline
6. **Easy Backup**: Just copy the .db file

This is perfect for a 5-hour hackathon build!