# PROBLEM STATEMENT

The Challenge: Rohan, a young farmer in a village in rural Karnataka, inspects his tomato crop. A strange pattern of yellow spots has appeared on the leaves of several plants. Is it a fungus? A pest? The wrong kind of fertilizer? The local agricultural office is miles away, and by the time he gets an answer, a significant portion of his crop could be lost. He also faces another challenge: when to sell. The price he gets for his produce at the local mandi can vary wildly from day to day. A day's delay could mean the difference between a profitable season and a loss. He has a smartphone, but the information he needs—expert pest diagnosis, real-time market prices, and guidance on government subsidies—is scattered, complex, and not available in his native Kannada. He doesn't need more data; he needs an ally, an expert in his pocket who understands his land and his language.
The Objective: Build "Project Kisan," an AI-powered personal assistant that acts as a personal agronomist, market analyst, and government scheme navigator for small-scale farmers. This agent should provide actionable intelligence to farmers, enabling them to protect their crops, maximize their income, and navigate complex agricultural systems. The agent should:
Diagnose Crop Diseases Instantly: Allow a farmer to take a photo of a diseased plant. The agent will use a multimodal Gemini model on Vertex AI to instantly analyze the image, identify the pest or disease, and provide clear, actionable advice on locally available and affordable remedies.
Deliver Real-Time Market Analysis: Enable a farmer to ask in their native language, "What is the price of tomatoes today?" The agent, built with Vertex AI Agent Builder, will fetch real-time data from public market APIs, use a Gemini model to analyze trends, and provide a simple, actionable summary to guide selling decisions.
Navigate Government Schemes: When a farmer asks about a specific need, like "subsidies for drip irrigation," the agent will use a Gemini model trained on government agricultural websites to explain relevant schemes in simple terms, list eligibility requirements, and provide direct links to application portals.
Enable Voice-First Interaction: Overcome literacy barriers by allowing farmers to interact entirely through voice. The agent will use Vertex AI Speech-to-Text and Text-to-Speech to understand queries in local dialects and respond with clear, easy-to-understand voice notes.
Tech Stack: Use of Google AI technologies is mandatory.
Special prize for using Firebase Studio and deploying the project.

1. Location data
   a. Geo data – Geo datasets and Geo Earth API from Google Earth API
   b. Climate data - Weather API
   c. Water Table data this google search API from gov website
   Outcomes:
   Crop recommendations – Good profits avoid poor harvest and great funding
2. Journal Farm Diaries – Voice all data via voice API schema
   a. Tool call to populate
   i. Crop Image data
   ii. Video data ??
   iii. Resutls outcomes disease
   iv. Pesticides used/ Fertiliser
   v. database
   vi. Soil health status
   vii. Farmer notes
   viii. Yield behaviour
   ix. Harvest notes
   x. Cost/sales
   b. Disease Dataset – public datasets – Cure (Optional if we have time) deep research citations
   Outcomes
3. Yeild Predication
4. Get help/Help in a better way
5. Farmers Personlised Prompt

6. Prediction of datascience (Yeild behavior trends across similar farmers) sales data prediction , consumption to sales to period. (Horticulture department)

7. Everything will be available as MCP

8. Farmers details

Simple Auth
Simple database
ECS
Metadata and SVG handling
User Profile/Preview

Potential to solve a problem

Overall Features
Farms
Current Farm
Crop type
Crop Stage
Health of the crop
Soil type
Insight
Check-ins - Daily check-ins
Scan the crops daily - First code → AI agents
Conversation -First code → AI agents
Questions??
Market
ONDC/ farmer sales/ Supply demand trends : First code → AI agents
Dashboard
Weather forecast
To-do Lists
Summaries and reports First code → AI agents
Information and QA: First code → AI agents
Gov Schemes : First code → AI agents
User-setup ??

Use sound indicators while using voice and the rest of the app

## MVP

Get the voice module with Gemini live api ready for communication and
Frontend usibility should be able to:
Farm section

Check in section
Assisstant usage
Dashboard

How we are pitching our product, what we are solving and how
Let’s highlight the ‘accessibility’’ aspect of our product as a primary stand out feature
[DRAFT]
Problem Overview

Is it even a problem?

Value Proposition
Providing farmers expert help on demand. We are building a proactive farm management hub that transforms a farmer's smartphone into an agronomist, market analyst, and government scheme navigator, all interacting in their native language!

Existing farm apps are often reactive information portals—a farmer asks, and they answer. Project Kisan is proactive. Instead of just providing data, it creates a "digital twin" of the farm to anticipate the farmer's needs, predict problems, and deliver personalized, actionable intelligence directly to them
Target Audience
Young farmers in rural Karnataka who grow crops
User Goals
Crop Protection from diseases
Maximize Income
Leverage appropriate Government Subsidies
Assumptions
Access to a Smartphone with moderate 3G/4G internet connectivity
Able to receive mobile notifications

Core Functionality
Voice-First Interface: Full interaction in native languages like Kannada, breaking literacy barriers.
Smart Farm Dashboard: A "digital twin" of your farm with real-time status and an AI-generated to-do list.
Proactive Health Monitoring: AI-powered predictive alerts for pests and diseases based on weather and crop cycle.
"Should I Sell Today?" Analysis: Nuanced market advice that analyzes price trends to suggest the most profitable time to sell.

Automated Scheme Discovery: Proactively identifies and simplifies relevant government subsidies for the farmer.
Smart Price Alerts: Set a target price for your crop and receive notifications when the market reaches it.

Functional Requirements
Non-Functional Requirements
Wireframes & User Flows

Perfect! Here's a robust yet simple database schema and feature plan for your 5-hour hackathon build:

## **Database Schema (SQLite)**

```sql
-- Users Table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    phone TEXT,
    location TEXT,
    latitude REAL,
    longitude REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Farms Table
CREATE TABLE farms (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    farm_name TEXT NOT NULL,
    crop_type TEXT NOT NULL,
    planting_date DATE,
    expected_harvest_date DATE,
    field_size_acres REAL,
    soil_type TEXT,
    irrigation_method TEXT,
    crop_stage TEXT, -- seedling, growing, flowering, harvesting
    health_status TEXT DEFAULT 'good', -- good, moderate, poor
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Daily Farm Logs
CREATE TABLE daily_logs (
    id INTEGER PRIMARY KEY,
    farm_id INTEGER REFERENCES farms(id),
    log_date DATE NOT NULL,
    activity_type TEXT, -- watering, fertilizing, pest_control, observation
    notes TEXT,
    weather_temp REAL,
    weather_humidity REAL,
    weather_rainfall REAL,
    weather_conditions TEXT,
    crop_health_notes TEXT,
    diseases_noted TEXT,
    image_path TEXT, -- for crop/disease photos
    video_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TODO Tasks
CREATE TABLE todo_tasks (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    farm_id INTEGER REFERENCES farms(id), -- NULL for general tasks
    task_title TEXT NOT NULL,
    task_description TEXT,
    priority TEXT DEFAULT 'medium', -- high, medium, low
    status TEXT DEFAULT 'pending', -- pending, completed, cancelled
    due_date DATE,
    is_system_generated BOOLEAN DEFAULT FALSE,
    weather_triggered BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sales Data
CREATE TABLE sales (
    id INTEGER PRIMARY KEY,
    farm_id INTEGER REFERENCES farms(id),
    sale_date DATE NOT NULL,
    crop_type TEXT,
    quantity_kg REAL,
    price_per_kg REAL,
    total_amount REAL,
    buyer_type TEXT, -- direct, market, middleman, export
    transportation_cost REAL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Weather History
CREATE TABLE weather_history (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    date DATE NOT NULL,
    temperature REAL,
    humidity REAL,
    rainfall REAL,
    conditions TEXT,
    alerts TEXT, -- JSON array of weather alerts
    recommended_actions TEXT, -- AI-generated suggestions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat History
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    message_type TEXT DEFAULT 'general', -- general, farm_specific, weather, sales
    farm_id INTEGER REFERENCES farms(id), -- if farm-specific query
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Government Schemes
CREATE TABLE government_schemes (
    id INTEGER PRIMARY KEY,
    scheme_name TEXT NOT NULL,
    description TEXT,
    eligibility_criteria TEXT,
    application_link TEXT,
    crop_types TEXT, -- JSON array
    location_applicable TEXT,
    deadline DATE,
    benefit_amount TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

-- Crop Recommendations
CREATE TABLE crop_recommendations (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    recommended_crop TEXT,
    current_crop TEXT,
    reason TEXT,
    expected_profit_increase REAL,
    seasonal_suitability TEXT,
    market_demand TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## **5-Hour Build Priority Features**

### **Hour 1: Core Setup**

- FastAPI setup with SQLite
- User registration/login endpoints
- Basic farm creation

### **Hour 2: Farm Management**

- Farm CRUD operations
- Daily log creation
- Image upload for crop issues

### **Hour 3: Smart Features**

- Weather API integration
- Auto-generate TODO tasks based on weather
- Basic sales tracking

### **Hour 4: AI Chat Integration**

- Chat endpoint with database access
- Simple query responses
- Weather-based recommendations

### **Hour 5: Dashboard & Demo Prep**

- Simple frontend/dashboard
- Historical data views
- Demo data seeding

## **Key API Endpoints Structure**

```python
# Authentication
POST /auth/register
POST /auth/login

# Farms
GET /farms/ # User's farms
POST /farms/ # Create farm
PUT /farms/{farm_id}
GET /farms/{farm_id}/logs # Daily logs

# Daily Operations
POST /farms/{farm_id}/logs # Add daily log
GET /todos/ # User's todos
POST /todos/ # Create todo
PUT /todos/{todo_id}/complete

# Sales
POST /farms/{farm_id}/sales
GET /farms/{farm_id}/sales # Sales history

# Chat & AI
POST /chat # Send message, get AI response with DB context
GET /chat/history

# Weather & Recommendations
GET /weather/current
GET /recommendations/crops
GET /schemes/applicable # Government schemes for user's location
```

## **Chat System Database Integration**

The AI chat will have read access to all tables and write access to:

- `todo_tasks` (create weather-based tasks)
- `crop_recommendations` (suggest alternative crops)
- `chat_history` (store conversations)

## **Demo Value Propositions**

1. **"Your farm in your pocket"** - Complete farm digitization
2. **"Never miss the perfect selling time"** - Weather + market timing
3. **"Government money waiting for you"** - Scheme recommendations
4. **"Talk to your farm data"** - AI chat with historical insights

Want me to start creating the FastAPI code structure or would you like to refine any part of this schema first?

Perfect! Here's the SQLAlchemy model structure for your FastAPI application:Now here's the database setup and Pydantic schemas:And here's the FastAPI routes structure to get you started:## **Quick Setup Instructions**

### **Required Dependencies**

```bash
pip install fastapi uvicorn sqlalchemy bcrypt pyjwt python-multipart requests
```

### **File Structure**

```
farm_app/
├── main.py          # Your FastAPI routes
├── models.py        # SQLAlchemy models
├── schemas.py       # Pydantic schemas
├── database.py      # Database config
└── farm_management.db  # SQLite database (auto-created)
```

### **5-Hour Implementation Priority**

**Hour 1: Core Setup**

- Copy the models, schemas, and database files
- Implement basic auth (register/login)
- Test with `uvicorn main:app --reload`

**Hour 2: Farm & Daily Logs**

- Implement farm CRUD operations
- Add daily log creation
- Test farm creation and logging

**Hour 3: TODOs & Weather**

- Implement TODO CRUD
- Add basic weather API integration
- Create weather-based TODO generation

**Hour 4: Sales & Basic AI Chat**

- Add sales tracking
- Implement simple chat endpoint
- Create context-building functions

**Hour 5: Government Schemes & Demo**

- Seed government schemes data
- Add crop recommendations
- Create demo data and test scenarios

### **Key Features Ready to Demo**

1. **Complete Farm Digitization** - All farm data in one place
2. **Smart TODO Generation** - Weather-based task creation
3. **Sales Tracking** - Revenue monitoring and forecasting
4. **AI Chat Assistant** - Context-aware responses using farm data
5. **Government Scheme Discovery** - Location and crop-based recommendations

### **Demo Script Ideas**

1. "Register farmer → Create farm → Log daily activity"
2. "Weather changes → System creates TODO → Farmer completes task"
3. "Record sales → Ask AI for profit analysis → Get recommendations"
4. "Chat: 'What government schemes apply to my tomato farm?'"

The structure is designed to be modular - you can implement features incrementally and still have a working demo at each stage. Focus on the core user flow first, then add intelligence layers!

Need help implementing any specific functions or want me to create sample data seeding scripts?

from sqlalchemy import Boolean, Column, Integer, String, Text, REAL, DateTime, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, date

Base = declarative_base()

class User(Base):
**tablename** = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    phone = Column(String)
    location = Column(String)
    latitude = Column(REAL)
    longitude = Column(REAL)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    farms = relationship("Farm", back_populates="owner")
    todos = relationship("TodoTask", back_populates="user")
    weather_history = relationship("WeatherHistory", back_populates="user")
    chat_history = relationship("ChatHistory", back_populates="user")

class Farm(Base):
**tablename** = "farms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    farm_name = Column(String, nullable=False)
    crop_type = Column(String, nullable=False)
    planting_date = Column(Date)
    expected_harvest_date = Column(Date)
    field_size_acres = Column(REAL)
    soil_type = Column(String)
    irrigation_method = Column(String)
    crop_stage = Column(String, default="seedling")  # seedling, growing, flowering, harvesting
    health_status = Column(String, default="good")  # good, moderate, poor
    created_at = Column(DateTime, default=func.now())

    # Relationships
    owner = relationship("User", back_populates="farms")
    daily_logs = relationship("DailyLog", back_populates="farm")
    todos = relationship("TodoTask", back_populates="farm")
    sales = relationship("Sale", back_populates="farm")

class DailyLog(Base):
**tablename** = "daily_logs"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    log_date = Column(Date, nullable=False, default=date.today)
    activity_type = Column(String)  # watering, fertilizing, pest_control, observation
    notes = Column(Text)
    weather_temp = Column(REAL)
    weather_humidity = Column(REAL)
    weather_rainfall = Column(REAL)
    weather_conditions = Column(String)
    crop_health_notes = Column(Text)
    diseases_noted = Column(Text)
    image_path = Column(String)  # for crop/disease photos
    video_path = Column(String)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    farm = relationship("Farm", back_populates="daily_logs")

class TodoTask(Base):
**tablename** = "todo_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=True)  # NULL for general tasks
    task_title = Column(String, nullable=False)
    task_description = Column(Text)
    priority = Column(String, default="medium")  # high, medium, low
    status = Column(String, default="pending")  # pending, completed, cancelled
    due_date = Column(Date)
    is_system_generated = Column(Boolean, default=False)
    weather_triggered = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="todos")
    farm = relationship("Farm", back_populates="todos")

class Sale(Base):
**tablename** = "sales"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    sale_date = Column(Date, nullable=False, default=date.today)
    crop_type = Column(String)
    quantity_kg = Column(REAL)
    price_per_kg = Column(REAL)
    total_amount = Column(REAL)
    buyer_type = Column(String)  # direct, market, middleman, export
    transportation_cost = Column(REAL)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    farm = relationship("Farm", back_populates="sales")

class WeatherHistory(Base):
**tablename** = "weather_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False, default=date.today)
    temperature = Column(REAL)
    humidity = Column(REAL)
    rainfall = Column(REAL)
    conditions = Column(String)
    alerts = Column(Text)  # JSON array of weather alerts
    recommended_actions = Column(Text)  # AI-generated suggestions
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="weather_history")

class ChatHistory(Base):
**tablename** = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    message_type = Column(String, default="general")  # general, farm_specific, weather, sales
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="chat_history")

# database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./farm_management.db"

engine = create_engine(
SQLALCHEMY_DATABASE_URL,
connect_args={"check_same_thread": False} # Only for SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables

Base.metadata.create_all(bind=engine)

# Dependency

def get_db():
db = SessionLocal()
try:
yield db
finally:
db.close()

# schemas.py - Pydantic models for API

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

# User Schemas

class UserCreate(BaseModel):
name: str
email: EmailStr
password: str
phone: Optional[str] = None
location: Optional[str] = None
latitude: Optional[float] = None
longitude: Optional[float] = None

class UserResponse(BaseModel):
id: int
name: str
email: str
phone: Optional[str]
location: Optional[str]
created_at: datetime

    class Config:
        from_attributes = True

# Farm Schemas

class FarmCreate(BaseModel):
farm_name: str
crop_type: str
planting_date: Optional[date] = None
expected_harvest_date: Optional[date] = None
field_size_acres: Optional[float] = None
soil_type: Optional[str] = None
irrigation_method: Optional[str] = None
crop_stage: str = "seedling"

class FarmResponse(BaseModel):
id: int
farm_name: str
crop_type: str
planting_date: Optional[date]
expected_harvest_date: Optional[date]
field_size_acres: Optional[float]
soil_type: Optional[str]
irrigation_method: Optional[str]
crop_stage: str
health_status: str
created_at: datetime

    class Config:
        from_attributes = True

# Daily Log Schemas

class DailyLogCreate(BaseModel):
log_date: date = date.today()
activity_type: Optional[str] = None
notes: Optional[str] = None
weather_temp: Optional[float] = None
weather_humidity: Optional[float] = None
weather_rainfall: Optional[float] = None
weather_conditions: Optional[str] = None
crop_health_notes: Optional[str] = None
diseases_noted: Optional[str] = None
image_path: Optional[str] = None
video_path: Optional[str] = None

class DailyLogResponse(BaseModel):
id: int
farm_id: int
log_date: date
activity_type: Optional[str]
notes: Optional[str]
weather_temp: Optional[float]
weather_humidity: Optional[float]
weather_rainfall: Optional[float]
weather_conditions: Optional[str]
crop_health_notes: Optional[str]
diseases_noted: Optional[str]
image_path: Optional[str]
video_path: Optional[str]
created_at: datetime

    class Config:
        from_attributes = True

# TODO Schemas

class TodoCreate(BaseModel):
task_title: str
task_description: Optional[str] = None
priority: str = "medium"
due_date: Optional[date] = None
farm_id: Optional[int] = None

class TodoResponse(BaseModel):
id: int
task_title: str
task_description: Optional[str]
priority: str
status: str
due_date: Optional[date]
farm_id: Optional[int]
is_system_generated: bool
weather_triggered: bool
completed_at: Optional[datetime]
created_at: datetime

    class Config:
        from_attributes = True

# Sales Schemas

class SaleCreate(BaseModel):
sale_date: date = date.today()
crop_type: Optional[str] = None
quantity_kg: Optional[float] = None
price_per_kg: Optional[float] = None
total_amount: Optional[float] = None
buyer_type: Optional[str] = None
transportation_cost: Optional[float] = None
notes: Optional[str] = None

class SaleResponse(BaseModel):
id: int
farm_id: int
sale_date: date
crop_type: Optional[str]
quantity_kg: Optional[float]
price_per_kg: Optional[float]
total_amount: Optional[float]
buyer_type: Optional[str]
transportation_cost: Optional[float]
notes: Optional[str]
created_at: datetime

    class Config:
        from_attributes = True

# Chat Schemas

class ChatMessage(BaseModel):
message: str
farm_id: Optional[int] = None

class ChatResponse(BaseModel):
id: int
message: str
response: str
message_type: str
farm_id: Optional[int]
created_at: datetime

    class Config:
        from_attributes = True

# Weather Schemas

class WeatherResponse(BaseModel):
id: int
date: date
temperature: Optional[float]
humidity: Optional[float]
rainfall: Optional[float]
conditions: Optional[str]
alerts: Optional[str]
recommended_actions: Optional[str]
created_at: datetime

    class Config:
        from_attributes = True

# Government Scheme Schemas

class GovernmentSchemeResponse(BaseModel):
id: int
scheme_name: str
description: Optional[str]
eligibility_criteria: Optional[str]
application_link: Optional[str]
crop_types: Optional[str]
location_applicable: Optional[str]
deadline: Optional[date]
benefit_amount: Optional[str]
is_active: bool

    class Config:
        from_attributes = True

# Authentication Schemas

class Token(BaseModel):
access_token: str
token_type: str

class TokenData(BaseModel):
email: Optional[str] = None

class UserLogin(BaseModel):
email: EmailStr
password: str

# main.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import bcrypt
import jwt
from datetime import datetime, timedelta
import requests
import json

from database import get_db
from models import _
from schemas import _

app = FastAPI(title="Farm Management API", version="1.0.0")
security = HTTPBearer()

# JWT Configuration

SECRET_KEY = "your-secret-key-here" # Change this in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Helper Functions

def hash_password(password: str) -> str:
return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict):
to_encode = data.copy()
expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
to_encode.update({"exp": expire})
return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
try:
payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
email: str = payload.get("sub")
if email is None:
raise HTTPException(status_code=401, detail="Invalid authentication")
except jwt.PyJWTError:
raise HTTPException(status_code=401, detail="Invalid authentication")

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Authentication Routes

@app.post("/auth/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)): # Check if user exists
if db.query(User).filter(User.email == user.email).first():
raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    hashed_password = hash_password(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password,
        phone=user.phone,
        location=user.location,
        latitude=user.latitude,
        longitude=user.longitude
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/auth/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
user = db.query(User).filter(User.email == user_credentials.email).first()

    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# Farm Routes

@app.get("/farms/", response_model=List[FarmResponse])
def get_farms(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
return db.query(Farm).filter(Farm.user_id == current_user.id).all()

@app.post("/farms/", response_model=FarmResponse)
def create_farm(farm: FarmCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
db_farm = Farm(\*\*farm.dict(), user_id=current_user.id)
db.add(db_farm)
db.commit()
db.refresh(db_farm)

    # Generate initial TODO tasks for new farm
    generate_initial_todos(db_farm, db)

    return db_farm

@app.get("/farms/{farm_id}", response_model=FarmResponse)
def get_farm(farm_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == current_user.id).first()
if not farm:
raise HTTPException(status_code=404, detail="Farm not found")
return farm

# Daily Logs Routes

@app.get("/farms/{farm_id}/logs", response_model=List[DailyLogResponse])
def get_daily_logs(farm_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)): # Verify farm ownership
farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == current_user.id).first()
if not farm:
raise HTTPException(status_code=404, detail="Farm not found")

    return db.query(DailyLog).filter(DailyLog.farm_id == farm_id).order_by(DailyLog.log_date.desc()).all()

@app.post("/farms/{farm_id}/logs", response_model=DailyLogResponse)
def create_daily_log(farm_id: int, log: DailyLogCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)): # Verify farm ownership
farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == current_user.id).first()
if not farm:
raise HTTPException(status_code=404, detail="Farm not found")

    db_log = DailyLog(**log.dict(), farm_id=farm_id)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

# TODO Routes

@app.get("/todos/", response_model=List[TodoResponse])
def get_todos(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
return db.query(TodoTask).filter(TodoTask.user_id == current_user.id).order_by(TodoTask.due_date).all()

@app.post("/todos/", response_model=TodoResponse)
def create_todo(todo: TodoCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
db_todo = TodoTask(\*\*todo.dict(), user_id=current_user.id)
db.add(db_todo)
db.commit()
db.refresh(db_todo)
return db_todo

@app.put("/todos/{todo_id}/complete", response_model=TodoResponse)
def complete_todo(todo_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
todo = db.query(TodoTask).filter(TodoTask.id == todo_id, TodoTask.user_id == current_user.id).first()
if not todo:
raise HTTPException(status_code=404, detail="TODO not found")

    todo.status = "completed"
    todo.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(todo)
    return todo

# Sales Routes

@app.get("/farms/{farm_id}/sales", response_model=List[SaleResponse])
def get_sales(farm_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)): # Verify farm ownership
farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == current_user.id).first()
if not farm:
raise HTTPException(status_code=404, detail="Farm not found")

    return db.query(Sale).filter(Sale.farm_id == farm_id).order_by(Sale.sale_date.desc()).all()

@app.post("/farms/{farm_id}/sales", response_model=SaleResponse)
def create_sale(farm_id: int, sale: SaleCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)): # Verify farm ownership
farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == current_user.id).first()
if not farm:
raise HTTPException(status_code=404, detail="Farm not found")

    db_sale = Sale(**sale.dict(), farm_id=farm_id)
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale

# Weather Routes

@app.get("/weather/current")
def get_current_weather(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
if not current_user.latitude or not current_user.longitude:
raise HTTPException(status_code=400, detail="User location not available")

    # Google Weather API call (you'll need to implement this)
    weather_data = fetch_weather_data(current_user.latitude, current_user.longitude)

    # Store in database
    db_weather = WeatherHistory(
        user_id=current_user.id,
        temperature=weather_data.get('temperature'),
        humidity=weather_data.get('humidity'),
        rainfall=weather_data.get('rainfall'),
        conditions=weather_data.get('conditions'),
        recommended_actions=generate_weather_recommendations(weather_data)
    )
    db.add(db_weather)
    db.commit()

    # Generate weather-based TODO tasks
    create_weather_todos(current_user, weather_data, db)

    return weather_data

# Chat Routes

@app.post("/chat", response_model=ChatResponse)
def chat_with_ai(chat: ChatMessage, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)): # Get relevant data for context
context = build_chat_context(current_user, chat.farm_id, db)

    # Generate AI response (you'll implement this)
    ai_response = generate_ai_response(chat.message, context)

    # Store chat history
    db_chat = ChatHistory(
        user_id=current_user.id,
        message=chat.message,
        response=ai_response,
        farm_id=chat.farm_id,
        message_type=determine_message_type(chat.message)
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)

    return db_chat

@app.get("/chat/history", response_model=List[ChatResponse])
def get_chat_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
return db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).order_by(ChatHistory.created_at.desc()).limit(50).all()

# Government Schemes Routes

@app.get("/schemes/applicable", response_model=List[GovernmentSchemeResponse])
def get_applicable_schemes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)): # Get user's crops
user_crops = db.query(Farm.crop_type).filter(Farm.user_id == current_user.id).distinct().all()
crop_types = [crop[0] for crop in user_crops]

    # Find applicable schemes (simplified logic for hackathon)
    schemes = db.query(GovernmentScheme).filter(
        GovernmentScheme.is_active == True,
        GovernmentScheme.location_applicable.contains(current_user.location or "")
    ).all()

    return schemes

# Helper Functions (you'll implement these)

def generate_initial_todos(farm: Farm, db: Session):
"""Generate initial TODO tasks for a new farm"""
pass

def fetch_weather_data(lat: float, lon: float):
"""Fetch weather data from Google Weather API"""
pass

def generate_weather_recommendations(weather_data: dict):
"""Generate recommendations based on weather"""
pass

def create_weather_todos(user: User, weather_data: dict, db: Session):
"""Create weather-based TODO tasks"""
pass

def build_chat_context(user: User, farm_id: Optional[int], db: Session):
"""Build context for AI chat"""
pass

def generate_ai_response(message: str, context: dict):
"""Generate AI response using context"""
pass

def determine_message_type(message: str):
"""Determine the type of chat message"""
return "general"

if **name** == "**main**":
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)

# Enhanced TodoTask model with recurring support

from sqlalchemy import Boolean, Column, Integer, String, Text, REAL, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship

class TodoTask(Base):
**tablename** = "todo_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=True)
    task_title = Column(String, nullable=False)
    task_description = Column(Text)
    priority = Column(String, default="medium")
    status = Column(String, default="pending")
    due_date = Column(Date)
    is_system_generated = Column(Boolean, default=False)
    weather_triggered = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())

    # NEW: Recurring fields
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String)  # 'daily', 'weekly', 'monthly', 'seasonal'
    recurrence_interval = Column(Integer, default=1)  # every X days/weeks/months
    parent_todo_id = Column(Integer, ForeignKey("todo_tasks.id"), nullable=True)  # Links to original template
    next_due_date = Column(Date)  # When to create next instance
    is_template = Column(Boolean, default=False)  # Original recurring template

    # Relationships
    user = relationship("User", back_populates="todos")
    farm = relationship("Farm", back_populates="todos")
    recurring_instances = relationship("TodoTask", cascade="all, delete-orphan")

# Enhanced Pydantic schemas

class TodoCreate(BaseModel):
task_title: str
task_description: Optional[str] = None
priority: str = "medium"
due_date: Optional[date] = None
farm_id: Optional[int] = None

    # NEW: Recurring fields
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None  # 'daily', 'weekly', 'monthly'
    recurrence_interval: int = 1

class TodoResponse(BaseModel):
id: int
task_title: str
task_description: Optional[str]
priority: str
status: str
due_date: Optional[date]
farm_id: Optional[int]
is_system_generated: bool
weather_triggered: bool
completed_at: Optional[datetime]
created_at: datetime

    # NEW: Recurring fields
    is_recurring: bool
    recurrence_pattern: Optional[str]
    recurrence_interval: int
    is_template: bool
    next_due_date: Optional[date]

    class Config:
        from_attributes = True

# Enhanced TODO creation with recurring support

@app.post("/todos/", response_model=TodoResponse)
def create_todo(todo: TodoCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)): # Create the main TODO
db_todo = TodoTask(\*\*todo.dict(), user_id=current_user.id)

    if todo.is_recurring:
        db_todo.is_template = True
        db_todo.next_due_date = calculate_next_due_date(todo.due_date, todo.recurrence_pattern, todo.recurrence_interval)

    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)

    # If recurring, create first instance
    if todo.is_recurring:
        create_recurring_instance(db_todo, db)

    return db_todo

# Helper functions for recurring TODOs

def calculate_next_due_date(current_date: date, pattern: str, interval: int) -> date:
"""Calculate when the next recurring task should be created"""
if not current_date:
current_date = date.today()

    if pattern == "daily":
        return current_date + timedelta(days=interval)
    elif pattern == "weekly":
        return current_date + timedelta(weeks=interval)
    elif pattern == "monthly":
        # Simple monthly calculation
        next_month = current_date.month + interval
        year = current_date.year + (next_month - 1) // 12
        month = ((next_month - 1) % 12) + 1
        return date(year, month, min(current_date.day, 28))  # Avoid month-end issues
    else:
        return current_date + timedelta(days=1)

def create_recurring_instance(template: TodoTask, db: Session):
"""Create a new instance of a recurring task"""
instance = TodoTask(
user_id=template.user_id,
farm_id=template.farm_id,
task_title=template.task_title,
task_description=template.task_description,
priority=template.priority,
due_date=template.due_date,
is_system_generated=True,
parent_todo_id=template.id,
is_recurring=False, # Instances are not recurring themselves
is_template=False
)
db.add(instance)
db.commit()

# Background job to create recurring tasks (run this daily)

def create_pending_recurring_todos(db: Session):
"""Create new instances of recurring TODOs that are due"""
today = date.today()

    # Find all recurring templates that need new instances
    recurring_templates = db.query(TodoTask).filter(
        TodoTask.is_template == True,
        TodoTask.is_recurring == True,
        TodoTask.next_due_date <= today
    ).all()

    for template in recurring_templates:
        # Create new instance
        create_recurring_instance(template, db)

        # Update next due date
        template.next_due_date = calculate_next_due_date(
            template.next_due_date,
            template.recurrence_pattern,
            template.recurrence_interval
        )

    db.commit()

# Endpoint to trigger recurring TODO creation (for demo)

@app.post("/todos/generate-recurring")
def generate_recurring_todos(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
"""Manually trigger creation of pending recurring TODOs"""
create_pending_recurring_todos(db)
return {"message": "Recurring TODOs generated successfully"}

# Get pending TODOs with recurring status

@app.get("/todos/active", response_model=List[TodoResponse])
def get_active_todos(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
"""Get only active TODO instances (not templates)"""
return db.query(TodoTask).filter(
TodoTask.user_id == current_user.id,
TodoTask.status == "pending",
TodoTask.is_template == False # Only get instances, not templates
).order_by(TodoTask.due_date).all()

# Complete recurring TODO and create next instance if needed

@app.put("/todos/{todo_id}/complete", response_model=TodoResponse)
def complete_todo(todo_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
todo = db.query(TodoTask).filter(TodoTask.id == todo_id, TodoTask.user_id == current_user.id).first()
if not todo:
raise HTTPException(status_code=404, detail="TODO not found")

    todo.status = "completed"
    todo.completed_at = datetime.utcnow()

    # If this was from a recurring template, check if we need to create next instance
    if todo.parent_todo_id:
        template = db.query(TodoTask).filter(TodoTask.id == todo.parent_todo_id).first()
        if template and template.is_recurring:
            # Update template's next due date
            template.next_due_date = calculate_next_due_date(
                todo.due_date,
                template.recurrence_pattern,
                template.recurrence_interval
            )

    db.commit()
    db.refresh(todo)
    return todo

REMEBER THIS IS A HACKTHON AND IT SHOULD BE BUILT WITHIN 5 HOURS AND YOU ARE WITH WORLDS FASTEST SOFTWARE DEVELOPER
