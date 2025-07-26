"""
Streaming Authentication API

Provides streaming registration with real-time soil analysis.
"""

import asyncio
import json
import logging
from typing import Annotated, AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..models.user import User
from ..models.soil_analysis import SoilAnalysis
from ..schemas.user import UserCreate
from ..schemas.soil_analysis import RegistrationProgress, RegistrationComplete
from ..services.soil_analysis_service import SoilAnalysisService
from ..utils.auth import get_password_hash

router = APIRouter(prefix="/auth", tags=["streaming-authentication"])


async def registration_stream(
    user_data: UserCreate, db: Session
) -> AsyncGenerator[str, None]:
    """
    Stream registration progress with soil analysis.

    Args:
        user_data (UserCreate): User registration data
        db (Session): Database session

    Yields:
        str: JSON-encoded progress updates
    """
    try:
        # Step 1: Validate user data
        yield (
            json.dumps(
                {
                    "step": "validation",
                    "message": "Validating registration data...",
                    "progress": 10,
                }
            )
            + "\n"
        )

        await asyncio.sleep(0.5)  # Simulate processing time

        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            yield (
                json.dumps(
                    {
                        "step": "error",
                        "message": "Email already registered",
                        "progress": 0,
                    }
                )
                + "\n"
            )
            return

        # Step 2: Create user account
        yield (
            json.dumps(
                {
                    "step": "user_creation",
                    "message": "Creating your account...",
                    "progress": 25,
                }
            )
            + "\n"
        )

        await asyncio.sleep(0.5)

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=hashed_password,
            phone=user_data.phone,
            latitude=user_data.latitude,
            longitude=user_data.longitude,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Step 3: Start soil analysis (if coordinates provided)
        soil_analysis = None
        if user_data.latitude and user_data.longitude:
            yield (
                json.dumps(
                    {
                        "step": "soil_analysis_start",
                        "message": "Analyzing soil data for your location...",
                        "progress": 40,
                    }
                )
                + "\n"
            )

            await asyncio.sleep(1.0)

            # Initialize soil analysis service
            soil_service = SoilAnalysisService(db)

            # Step 4: Fetch soil data
            yield (
                json.dumps(
                    {
                        "step": "soil_data_fetch",
                        "message": "Fetching soil properties from global database...",
                        "progress": 55,
                    }
                )
                + "\n"
            )

            await asyncio.sleep(1.5)

            # Step 5: Process soil analysis
            yield (
                json.dumps(
                    {
                        "step": "soil_analysis_process",
                        "message": "Processing soil composition and nutrients...",
                        "progress": 70,
                    }
                )
                + "\n"
            )

            # Perform soil analysis
            soil_analysis = await soil_service.analyze_and_store_soil_data(
                user_id=db_user.id,
                latitude=user_data.latitude,
                longitude=user_data.longitude,
                location_name=f"Farm location for {user_data.name}",
            )

            await asyncio.sleep(1.0)

            # Step 6: Generate recommendations
            yield (
                json.dumps(
                    {
                        "step": "recommendations",
                        "message": "Generating personalized crop recommendations...",
                        "progress": 85,
                    }
                )
                + "\n"
            )

            await asyncio.sleep(1.0)

        # Step 7: Complete registration
        yield (
            json.dumps(
                {
                    "step": "completion",
                    "message": "Finalizing your agricultural profile...",
                    "progress": 95,
                }
            )
            + "\n"
        )

        await asyncio.sleep(0.5)

        # Step 8: Send final response
        completion_data = {
            "step": "complete",
            "message": "Registration completed successfully!",
            "progress": 100,
            "data": {
                "user_id": db_user.id,
                "name": db_user.name,
                "email": db_user.email,
                "soil_analysis": None,
                "recommendations": None,
                "suitable_crops": None,
            },
        }

        if soil_analysis:
            completion_data["data"]["soil_analysis"] = {
                "id": soil_analysis.id,
                "ph_value": soil_analysis.ph_value,
                "ph_description": soil_analysis.ph_description,
                "organic_carbon": soil_analysis.organic_carbon,
                "soil_texture": soil_analysis.soil_texture,
                "soil_quality_score": soil_analysis.soil_quality_score,
                "analysis_status": soil_analysis.analysis_status,
            }
            completion_data["data"]["recommendations"] = soil_analysis.recommendations
            completion_data["data"]["suitable_crops"] = soil_analysis.suitable_crops

        yield json.dumps(completion_data) + "\n"

    except Exception as e:
        logging.error(f"Registration stream error: {str(e)}")
        yield (
            json.dumps(
                {
                    "step": "error",
                    "message": f"Registration failed: {str(e)}",
                    "progress": 0,
                }
            )
            + "\n"
        )


@router.post("/register-stream")
async def register_user_stream(
    user_data: UserCreate, db: Annotated[Session, Depends(get_db)]
):
    """
    Stream user registration with real-time soil analysis.

    This endpoint provides a streaming response that shows registration progress
    including soil analysis for the user's location coordinates.

    Args:
        user_data (UserCreate): User registration data
        db (Session): Database session

    Returns:
        StreamingResponse: Server-sent events with registration progress
    """
    return StreamingResponse(
        registration_stream(user_data, db),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/plain; charset=utf-8",
        },
    )


@router.get("/registration-demo", response_class=StreamingResponse)
async def registration_demo():
    """
    Demo endpoint showing the registration streaming interface.

    Returns:
        StreamingResponse: HTML demo page
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Namma Krushi - Smart Registration</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #4CAF50, #45a049);
                color: white;
                padding: 30px;
                text-align: center;
            }
            .header h1 {
                margin: 0;
                font-size: 2.2em;
                font-weight: 300;
            }
            .header p {
                margin: 10px 0 0 0;
                opacity: 0.9;
            }
            .form-container {
                padding: 30px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            .form-group label {
                display: block;
                margin-bottom: 5px;
                font-weight: 500;
                color: #333;
            }
            .form-group input {
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 16px;
                transition: border-color 0.3s;
            }
            .form-group input:focus {
                outline: none;
                border-color: #4CAF50;
            }
            .form-row {
                display: flex;
                gap: 15px;
            }
            .form-row .form-group {
                flex: 1;
            }
            .register-btn {
                width: 100%;
                padding: 15px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 500;
                cursor: pointer;
                transition: background 0.3s;
            }
            .register-btn:hover {
                background: #45a049;
            }
            .register-btn:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            .progress-container {
                margin-top: 20px;
                display: none;
            }
            .progress-bar {
                width: 100%;
                height: 8px;
                background: #f0f0f0;
                border-radius: 4px;
                overflow: hidden;
                margin-bottom: 15px;
            }
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #4CAF50, #45a049);
                width: 0%;
                transition: width 0.3s ease;
            }
            .progress-message {
                text-align: center;
                color: #666;
                font-size: 14px;
                margin-bottom: 10px;
            }
            .progress-step {
                padding: 10px;
                margin: 5px 0;
                border-radius: 5px;
                font-size: 14px;
            }
            .step-validation { background: #e3f2fd; }
            .step-user_creation { background: #f3e5f5; }
            .step-soil_analysis_start { background: #fff3e0; }
            .step-soil_data_fetch { background: #e8f5e8; }
            .step-soil_analysis_process { background: #fff8e1; }
            .step-recommendations { background: #e1f5fe; }
            .step-completion { background: #f1f8e9; }
            .step-complete { background: #c8e6c9; font-weight: bold; }
            .step-error { background: #ffebee; color: #c62828; }
            .results-container {
                margin-top: 20px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
                display: none;
            }
            .soil-info {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin-top: 15px;
            }
            .soil-metric {
                background: white;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
            }
            .soil-metric .value {
                font-size: 1.5em;
                font-weight: bold;
                color: #4CAF50;
            }
            .soil-metric .label {
                font-size: 0.9em;
                color: #666;
                margin-top: 5px;
            }
            .crops-list {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-top: 10px;
            }
            .crop-tag {
                background: #4CAF50;
                color: white;
                padding: 5px 10px;
                border-radius: 15px;
                font-size: 12px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌱 Namma Krushi</h1>
                <p>Smart Agricultural Registration with Soil Analysis</p>
            </div>
            
            <div class="form-container">
                <form id="registrationForm">
                    <div class="form-group">
                        <label for="name">Full Name</label>
                        <input type="text" id="name" name="name" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="email">Email Address</label>
                        <input type="email" id="email" name="email" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="phone">Phone Number (Optional)</label>
                        <input type="tel" id="phone" name="phone">
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="latitude">Latitude</label>
                            <input type="number" id="latitude" name="latitude" step="any" placeholder="12.9716">
                        </div>
                        <div class="form-group">
                            <label for="longitude">Longitude</label>
                            <input type="number" id="longitude" name="longitude" step="any" placeholder="77.5946">
                        </div>
                    </div>
                    
                    <button type="submit" class="register-btn" id="registerBtn">
                        Register & Analyze Soil
                    </button>
                </form>
                
                <div class="progress-container" id="progressContainer">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                    <div class="progress-message" id="progressMessage">Starting registration...</div>
                    <div id="progressSteps"></div>
                </div>
                
                <div class="results-container" id="resultsContainer">
                    <h3>🎉 Registration Complete!</h3>
                    <div id="userInfo"></div>
                    <div id="soilResults"></div>
                </div>
            </div>
        </div>

        <script>
            document.getElementById('registrationForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const userData = {
                    name: formData.get('name'),
                    email: formData.get('email'),
                    password: formData.get('password'),
                    phone: formData.get('phone') || null,
                    latitude: formData.get('latitude') ? parseFloat(formData.get('latitude')) : null,
                    longitude: formData.get('longitude') ? parseFloat(formData.get('longitude')) : null
                };
                
                // Show progress container
                document.getElementById('progressContainer').style.display = 'block';
                document.getElementById('registerBtn').disabled = true;
                document.getElementById('registerBtn').textContent = 'Processing...';
                
                try {
                    const response = await fetch('/auth/register-stream', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(userData)
                    });
                    
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    
                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;
                        
                        const chunk = decoder.decode(value);
                        const lines = chunk.split('\\n').filter(line => line.trim());
                        
                        for (const line of lines) {
                            try {
                                const data = JSON.parse(line);
                                updateProgress(data);
                            } catch (e) {
                                console.error('Error parsing JSON:', e);
                            }
                        }
                    }
                } catch (error) {
                    console.error('Registration error:', error);
                    updateProgress({
                        step: 'error',
                        message: 'Registration failed. Please try again.',
                        progress: 0
                    });
                }
            });
            
            function updateProgress(data) {
                const progressFill = document.getElementById('progressFill');
                const progressMessage = document.getElementById('progressMessage');
                const progressSteps = document.getElementById('progressSteps');
                
                // Update progress bar
                progressFill.style.width = data.progress + '%';
                progressMessage.textContent = data.message;
                
                // Add step to history
                const stepDiv = document.createElement('div');
                stepDiv.className = `progress-step step-${data.step}`;
                stepDiv.textContent = data.message;
                progressSteps.appendChild(stepDiv);
                
                // Handle completion
                if (data.step === 'complete' && data.data) {
                    showResults(data.data);
                } else if (data.step === 'error') {
                    document.getElementById('registerBtn').disabled = false;
                    document.getElementById('registerBtn').textContent = 'Register & Analyze Soil';
                }
            }
            
            function showResults(data) {
                const resultsContainer = document.getElementById('resultsContainer');
                const userInfo = document.getElementById('userInfo');
                const soilResults = document.getElementById('soilResults');
                
                // Show user info
                userInfo.innerHTML = `
                    <p><strong>Welcome, ${data.name}!</strong></p>
                    <p>Email: ${data.email}</p>
                `;
                
                // Show soil analysis results
                if (data.soil_analysis) {
                    const soil = data.soil_analysis;
                    soilResults.innerHTML = `
                        <h4>🌱 Soil Analysis Results</h4>
                        <div class="soil-info">
                            <div class="soil-metric">
                                <div class="value">${soil.ph_value ? soil.ph_value.toFixed(1) : 'N/A'}</div>
                                <div class="label">pH Level (${soil.ph_description || 'Unknown'})</div>
                            </div>
                            <div class="soil-metric">
                                <div class="value">${soil.soil_quality_score ? soil.soil_quality_score.toFixed(0) : 'N/A'}</div>
                                <div class="label">Quality Score</div>
                            </div>
                            <div class="soil-metric">
                                <div class="value">${soil.organic_carbon ? soil.organic_carbon.toFixed(1) : 'N/A'}</div>
                                <div class="label">Organic Carbon (g/kg)</div>
                            </div>
                            <div class="soil-metric">
                                <div class="value">${soil.soil_texture || 'Unknown'}</div>
                                <div class="label">Soil Texture</div>
                            </div>
                        </div>
                        
                        ${data.suitable_crops ? `
                            <h4>🌾 Recommended Crops</h4>
                            <div class="crops-list">
                                ${data.suitable_crops.map(crop => `<span class="crop-tag">${crop}</span>`).join('')}
                            </div>
                        ` : ''}
                        
                        ${data.recommendations ? `
                            <h4>💡 Recommendations</h4>
                            <p>${data.recommendations}</p>
                        ` : ''}
                    `;
                } else {
                    soilResults.innerHTML = '<p>Soil analysis not available (coordinates not provided)</p>';
                }
                
                resultsContainer.style.display = 'block';
                document.getElementById('registerBtn').textContent = 'Registration Complete';
            }
            
            // Auto-fill coordinates if geolocation is available
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    document.getElementById('latitude').value = position.coords.latitude.toFixed(6);
                    document.getElementById('longitude').value = position.coords.longitude.toFixed(6);
                });
            }
        </script>
    </body>
    </html>
    """

    return StreamingResponse(iter([html_content]), media_type="text/html")
