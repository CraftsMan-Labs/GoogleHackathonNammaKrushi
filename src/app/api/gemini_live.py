"""
Gemini Live API endpoints for real-time agricultural assistance.
"""

import json
import logging
from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    HTTPException,
    Depends,
    Header,
)
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
from pydantic import BaseModel

from ..services.gemini_live_service import get_gemini_live_service
from ..services.gemini_streaming_service import get_gemini_streaming_service
from ..utils.auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/live", tags=["Gemini Live"])
security = HTTPBearer()


class ChatRequest(BaseModel):
    """Request model for chat messages."""

    message: str


class ChatStreamResponse(BaseModel):
    """Response model for streaming chat."""

    type: str
    content: str
    functions: Optional[list] = None


@router.post(
    "/chat/stream",
    summary="Stream Chat with AI Assistant",
    description="Stream real-time chat responses with JWT authentication and personalized farming advice",
)
async def stream_chat(
    request: ChatRequest, current_user: User = Depends(get_current_user)
):
    """
    Stream chat responses using Server-Sent Events (SSE) with JWT authentication.

    This endpoint:
    1. Requires JWT authentication via Authorization header
    2. Gets personalized farmer data based on the authenticated user
    3. Streams real-time AI responses using Server-Sent Events
    4. Saves chat history to the database
    5. Provides access to all agricultural tools and features

    **Authentication:**
    - Include JWT token in Authorization header: `Bearer YOUR_JWT_TOKEN`

    **Request Body:**
    ```json
    {
      "message": "What are the best crops for my land?"
    }
    ```

    **Response:**
    - Content-Type: text/event-stream
    - Real-time streaming responses
    - Personalized based on user's farming profile
    """
    try:
        logging.info(
            f"Starting streaming chat for user {current_user.id}: {request.message}"
        )

        # Get the streaming service
        service = get_gemini_streaming_service()

        # Get farmer data for personalization
        farmer_data = service.get_farmer_data(current_user.id)

        # Create the streaming response
        async def generate_stream():
            async for chunk in service.stream_chat_response(
                message=request.message, user=current_user, farmer_data=farmer_data
            ):
                yield chunk

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control",
            },
        )

    except Exception as e:
        logging.error(f"Streaming chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat streaming failed: {str(e)}")


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, token: str = None, user_id: int = None
):
    """
    WebSocket endpoint for Gemini Live text chat (DEPRECATED - Use /chat/stream instead).

    This endpoint is maintained for backward compatibility but the new HTTP streaming
    endpoint (/chat/stream) is recommended for better authentication and error handling.
    """
    logging.info("WebSocket connection requested (DEPRECATED - Use /chat/stream)")

    try:
        service = get_gemini_live_service()
        await service.handle_websocket_session(websocket, user_id)
    except WebSocketDisconnect:
        logging.info("WebSocket disconnected")
    except Exception as e:
        logging.error(f"WebSocket error: {str(e)}")
        try:
            await websocket.send_text(
                json.dumps({"type": "error", "content": f"Connection error: {str(e)}"})
            )
        except:
            pass


@router.get("/tools")
async def get_available_tools():
    """Get information about available tools."""
    service = get_gemini_live_service()
    return service.get_available_tools()


@router.get("/demo", response_class=HTMLResponse)
async def get_demo_page():
    """Live AI assistant demo page."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Namma Krushi AI - Live Assistant</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
                min-height: 100vh;
            }
            .container {
                max-width: 900px;
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
                font-size: 2.5em;
                font-weight: 300;
            }
            .header p {
                margin: 10px 0 0 0;
                opacity: 0.9;
                font-size: 1.1em;
            }
            .chat-container {
                height: 500px;
                overflow-y: auto;
                padding: 20px;
                border-bottom: 1px solid #eee;
                background: #fafafa;
            }
            .message {
                margin-bottom: 15px;
                padding: 12px 15px;
                border-radius: 18px;
                max-width: 80%;
                word-wrap: break-word;
                line-height: 1.4;
            }
            .user-message {
                background: #4CAF50;
                color: white;
                margin-left: auto;
                text-align: right;
            }
            .bot-message {
                background: white;
                border: 1px solid #ddd;
                margin-right: auto;
            }
            .system-message {
                background: #e3f2fd;
                border: 1px solid #bbdefb;
                margin-right: auto;
                font-style: italic;
                color: #1565c0;
                text-align: center;
                max-width: 100%;
            }
            .function-call {
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                margin-right: auto;
                font-style: italic;
                color: #856404;
                text-align: center;
                max-width: 100%;
            }
            .error-message {
                background: #f8d7da;
                border: 1px solid #f5c6cb;
                color: #721c24;
                margin-right: auto;
            }
            .input-container {
                padding: 20px;
                display: flex;
                gap: 10px;
                background: white;
            }
            .input-field {
                flex: 1;
                padding: 12px 15px;
                border: 2px solid #ddd;
                border-radius: 25px;
                font-size: 16px;
                outline: none;
                transition: border-color 0.3s;
            }
            .input-field:focus {
                border-color: #4CAF50;
            }
            .send-button {
                padding: 12px 20px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                transition: background 0.3s;
            }
            .send-button:hover {
                background: #45a049;
            }
            .send-button:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            .status {
                padding: 10px 20px;
                text-align: center;
                font-size: 14px;
                color: #666;
            }
            .connected {
                color: #4CAF50;
            }
            .disconnected {
                color: #f44336;
            }
            .examples {
                padding: 20px;
                background: #f8f9fa;
                border-top: 1px solid #eee;
            }
            .examples h3 {
                margin: 0 0 15px 0;
                color: #333;
            }
            .example-button {
                display: inline-block;
                margin: 5px;
                padding: 8px 12px;
                background: #e9ecef;
                border: 1px solid #ced4da;
                border-radius: 15px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s;
            }
            .example-button:hover {
                background: #4CAF50;
                color: white;
                border-color: #4CAF50;
            }
            .tools-info {
                padding: 15px 20px;
                background: #e8f5e8;
                border-top: 1px solid #c8e6c9;
                font-size: 14px;
                color: #2e7d32;
            }
            .auth-form input {
                box-sizing: border-box;
            }
            .auth-form input:focus {
                outline: none;
                border-color: #4CAF50;
                box-shadow: 0 0 5px rgba(76, 175, 80, 0.3);
            }
            .tab-button {
                transition: background-color 0.3s;
            }
            .tab-button:hover {
                opacity: 0.9;
            }
            .tab-button.active {
                font-weight: bold;
            }
            #userInfo {
                animation: slideIn 0.3s ease-in;
            }
            @keyframes slideIn {
                from { opacity: 0; transform: translateY(-10px); }
                to { opacity: 1; transform: translateY(0); }
            }
        </style>
    </head>
    <body>
        <div class="container">
                <div class="header">
                <h1>🌱 Namma Krushi AI</h1>
                <p>Text Chat AI Assistant for Karnataka Farmers</p>
            </div>            
            <div class="status" id="status">
                <span class="disconnected">Connecting...</span>
            </div>
            
            <div class="auth-section" id="authSection" style="padding: 20px; background: #f8f9fa; border-bottom: 1px solid #dee2e6;">
                <div class="auth-tabs" style="margin-bottom: 15px;">
                    <button id="loginTab" class="tab-button active" onclick="showLoginForm()" style="padding: 8px 16px; margin-right: 10px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">Login</button>
                    <button id="tokenTab" class="tab-button" onclick="showTokenForm()" style="padding: 8px 16px; background: #6c757d; color: white; border: none; border-radius: 4px; cursor: pointer;">Use Token</button>
                </div>
                
                <!-- Login Form -->
                <div id="loginForm" class="auth-form">
                    <h4 style="margin: 0 0 15px 0; color: #333;">🔐 Login for Personalized Experience</h4>
                    <div style="margin-bottom: 10px;">
                        <input type="email" id="emailInput" placeholder="Email address" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 10px;">
                        <input type="password" id="passwordInput" placeholder="Password" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 15px;">
                    </div>
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <button onclick="loginUser()" id="loginButton" style="padding: 10px 20px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">Login</button>
                        <button onclick="showRegisterForm()" style="padding: 10px 20px; background: #17a2b8; color: white; border: none; border-radius: 4px; cursor: pointer;">Register</button>
                        <span id="loginStatus" style="margin-left: 10px; font-size: 14px;"></span>
                    </div>
                    <div style="margin-top: 10px; font-size: 12px; color: #666;">
                        💡 Login to get personalized farming advice based on your crops, land, and activities
                    </div>
                </div>
                
                <!-- Token Form -->
                <div id="tokenForm" class="auth-form" style="display: none;">
                    <h4 style="margin: 0 0 15px 0; color: #333;">🔑 Use Existing JWT Token</h4>
                    <div style="margin-bottom: 15px;">
                        <input type="text" id="tokenInput" placeholder="Enter your JWT token for personalized experience" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px;">
                    </div>
                    <div style="display: flex; gap: 10px;">
                        <button onclick="setToken()" style="padding: 10px 20px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">Set Token</button>
                        <button onclick="clearToken()" style="padding: 10px 20px; background: #f44336; color: white; border: none; border-radius: 4px; cursor: pointer;">Clear Token</button>
                    </div>
                </div>
                
                <!-- Register Form -->
                <div id="registerForm" class="auth-form" style="display: none;">
                    <h4 style="margin: 0 0 15px 0; color: #333;">📝 Create New Account</h4>
                    <div style="margin-bottom: 10px;">
                        <input type="text" id="regNameInput" placeholder="Full Name" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 10px;">
                        <input type="email" id="regEmailInput" placeholder="Email address" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 10px;">
                        <input type="tel" id="regPhoneInput" placeholder="Phone number" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 10px;">
                        <input type="password" id="regPasswordInput" placeholder="Password" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 15px;">
                    </div>
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <button onclick="registerUser()" id="registerButton" style="padding: 10px 20px; background: #17a2b8; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">Register</button>
                        <button onclick="showLoginForm()" style="padding: 10px 20px; background: #6c757d; color: white; border: none; border-radius: 4px; cursor: pointer;">Back to Login</button>
                        <span id="registerStatus" style="margin-left: 10px; font-size: 14px;"></span>
                    </div>
                </div>
                
                <!-- Current User Info -->
                <div id="userInfo" style="display: none; margin-top: 15px; padding: 10px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 4px;">
                    <strong>✅ Logged in as:</strong> <span id="currentUser"></span>
                    <button onclick="logout()" style="margin-left: 10px; padding: 5px 10px; background: #dc3545; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 12px;">Logout</button>
                </div>
            </div>
            
            <div class="chat-container" id="chatContainer">
                <div class="message bot-message">
                    <strong>Namma Krushi AI:</strong> ನಮಸ್ಕಾರ! I'm your text-based AI farming assistant for Karnataka. I can help you with:
                    <br>• <strong>Crop Management:</strong> Track crops, stages, health scores
                    <br>• <strong>Daily Logs:</strong> Record farming activities and observations  
                    <br>• <strong>Sales Tracking:</strong> Monitor sales and calculate profits
                    <br>• <strong>Disease Diagnosis:</strong> Analyze crop images for diseases
                    <br>• <strong>Weather & Soil:</strong> Get weather forecasts and soil analysis
                    <br>• <strong>Government Schemes:</strong> Find subsidies and programs for farmers
                    <br>• <strong>Market Research:</strong> Search for prices and best practices
                    <br><br><strong>🔐 Login above for personalized advice</strong> based on your specific crops, land, and farming activities!
                    <br>Type your questions in English or Kannada! Try the examples below.
                </div>
            </div>
            
            <div class="input-container">
                <input type="text" id="messageInput" class="input-field" 
                       placeholder="Ask about crops, weather, sales, or farming advice... (English/Kannada)" 
                       disabled>
                <button id="sendButton" class="send-button" disabled>Send</button>
            </div>
            
            <div class="examples">
                <h3>Try these examples:</h3>
                <div class="example-button" data-example="What's the weather like in Bangalore today?">Weather in Bangalore</div>
                <div class="example-button" data-example="Get soil analysis for coordinates 12.9716, 77.5946">Soil Analysis Bangalore</div>
                <div class="example-button" data-example="How do I identify tomato blight disease?">Tomato Disease Help</div>
                <div class="example-button" data-example="Create a crop record for 2 acres of rice in Mysore">Add Rice Crop</div>
                <div class="example-button" data-example="Show me sales analytics for the last month">Sales Analytics</div>
                <div class="example-button" data-example="Record today's farming activities">Daily Log Entry</div>
                <div class="example-button" data-example="Best practices for ragi cultivation in Karnataka">Ragi Farming Tips</div>
                <div class="example-button" data-example="What government schemes are available for small farmers?">Government Schemes</div>
                <div class="example-button" data-example="ಟೊಮೇಟೊ ಬೆಳೆಗೆ ಯಾವ ಗೊಬ್ಬರ ಬಳಸಬೇಕು?">Tomato Fertilizer (Kannada)</div>
            </div>
            
            <div class="tools-info">
                <strong>Available Tools:</strong> Google Search, Exa AI Search, Government Scheme Search, Weather API, Soil Analysis, 
                Crop Disease Detection, Crop Management, Daily Logs, Sales Tracking, and more agricultural tools. 
                <br><strong>🔐 Authentication:</strong> Login for personalized responses based on your farmer profile, current crops, and farming history. 
                All chat history is automatically saved and linked to your account.
            </div>
        </div>

        <script>
            const chatContainer = document.getElementById('chatContainer');
            const messageInput = document.getElementById('messageInput');
            const sendButton = document.getElementById('sendButton');
            const status = document.getElementById('status');
            
            let isConnected = false;
            let currentEventSource = null;

            function connect() {
                const token = localStorage.getItem('auth_token');
                const userEmail = localStorage.getItem('user_email');
                
                if (token && userEmail) {
                    isConnected = true;
                    const statusText = `Connected as ${userEmail} - Personalized farming assistance ready!`;
                    status.innerHTML = `<span class="connected">${statusText}</span>`;
                    messageInput.disabled = false;
                    sendButton.disabled = false;
                    messageInput.focus();
                } else {
                    isConnected = false;
                    status.innerHTML = '<span class="disconnected">Please login for personalized assistance</span>';
                    messageInput.disabled = true;
                    sendButton.disabled = true;
                }
            }

            function addMessage(content, className, sender = null) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${className}`;
                
                if (className === 'user-message') {
                    messageDiv.innerHTML = `<strong>You:</strong> ${content}`;
                } else if (className === 'bot-message' && sender) {
                    messageDiv.innerHTML = `<strong>${sender}:</strong> ${content}`;
                } else {
                    messageDiv.innerHTML = content;
                }
                
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }

            async function sendMessage() {
                const message = messageInput.value.trim();
                const token = localStorage.getItem('auth_token');
                
                if (!message) return;
                
                if (!token) {
                    addMessage('Please login to send messages', 'error-message');
                    return;
                }
                
                // Disable input while processing
                messageInput.disabled = true;
                sendButton.disabled = true;
                sendButton.textContent = 'Sending...';
                
                // Add user message to chat
                addMessage(message, 'user-message');
                messageInput.value = '';
                
                try {
                    // Close any existing EventSource
                    if (currentEventSource) {
                        currentEventSource.close();
                    }
                    
                    // Send message via HTTP POST and stream response
                    const response = await fetch('/live/chat/stream', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`,
                            'Accept': 'text/event-stream',
                        },
                        body: JSON.stringify({
                            message: message
                        })
                    });
                    
                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.detail || 'Request failed');
                    }
                    
                    // Create EventSource for streaming response
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    
                    let currentBotMessage = '';
                    let botMessageElement = null;
                    
                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;
                        
                        const chunk = decoder.decode(value);
                        const lines = chunk.split('\n');
                        
                        for (const line of lines) {
                            if (line.startsWith('data: ')) {
                                try {
                                    const data = JSON.parse(line.slice(6));
                                    
                                    if (data.type === 'response') {
                                        // Accumulate bot response
                                        currentBotMessage += data.content;
                                        
                                        // Update or create bot message element
                                        if (!botMessageElement) {
                                            botMessageElement = document.createElement('div');
                                            botMessageElement.className = 'message bot-message';
                                            botMessageElement.innerHTML = '<strong>Namma Krushi AI:</strong> ';
                                            chatContainer.appendChild(botMessageElement);
                                        }
                                        
                                        // Update content with streaming text
                                        botMessageElement.innerHTML = `<strong>Namma Krushi AI:</strong> ${currentBotMessage}`;
                                        chatContainer.scrollTop = chatContainer.scrollHeight;
                                        
                                    } else if (data.type === 'function_call') {
                                        addMessage(data.message || `🔧 Using tools: ${data.functions.join(', ')}`, 'function-call');
                                    } else if (data.type === 'system') {
                                        addMessage(data.content, 'system-message');
                                    } else if (data.type === 'error') {
                                        addMessage(`Error: ${data.content}`, 'error-message');
                                    } else if (data.type === 'complete') {
                                        // Response completed
                                        console.log('Response completed');
                                    }
                                } catch (e) {
                                    console.error('Error parsing SSE data:', e);
                                }
                            }
                        }
                    }
                    
                } catch (error) {
                    console.error('Chat error:', error);
                    addMessage(`Error: ${error.message}`, 'error-message');
                    
                    // Check if it's an authentication error
                    if (error.message.includes('401') || error.message.includes('Unauthorized')) {
                        addMessage('Authentication failed. Please login again.', 'error-message');
                        logout();
                    }
                } finally {
                    // Re-enable input
                    messageInput.disabled = false;
                    sendButton.disabled = false;
                    sendButton.textContent = 'Send';
                    messageInput.focus();
                }
            }

            // Event listeners
            sendButton.addEventListener('click', sendMessage);
            
            messageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });

            // Example buttons
            document.querySelectorAll('.example-button').forEach(button => {
                button.addEventListener('click', function() {
                    const example = this.getAttribute('data-example');
                    messageInput.value = example;
                    if (isConnected) {
                        sendMessage();
                    }
                });
            });

            // Authentication functions
            async function loginUser() {
                const email = document.getElementById('emailInput').value.trim();
                const password = document.getElementById('passwordInput').value.trim();
                const loginButton = document.getElementById('loginButton');
                const loginStatus = document.getElementById('loginStatus');
                
                if (!email || !password) {
                    loginStatus.innerHTML = '<span style="color: #dc3545;">Please enter email and password</span>';
                    return;
                }
                
                loginButton.disabled = true;
                loginButton.textContent = 'Logging in...';
                loginStatus.innerHTML = '<span style="color: #6c757d;">Authenticating...</span>';
                
                try {
                    const response = await fetch('/auth/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            email: email,
                            password: password
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok && data.access_token) {
                        // Store token and user info
                        localStorage.setItem('auth_token', data.access_token);
                        localStorage.setItem('user_email', email);
                        
                        // Show success and hide auth section
                        loginStatus.innerHTML = '<span style="color: #28a745;">✅ Login successful!</span>';
                        showUserInfo(email);
                        
                        // Reconnect with token
                        connect();
                        
                        setTimeout(() => {
                            document.getElementById('authSection').style.display = 'none';
                        }, 1500);
                        
                    } else {
                        loginStatus.innerHTML = '<span style="color: #dc3545;">❌ ' + (data.detail || 'Login failed') + '</span>';
                    }
                } catch (error) {
                    console.error('Login error:', error);
                    loginStatus.innerHTML = '<span style="color: #dc3545;">❌ Network error. Please try again.</span>';
                } finally {
                    loginButton.disabled = false;
                    loginButton.textContent = 'Login';
                }
            }
            
            async function registerUser() {
                const name = document.getElementById('regNameInput').value.trim();
                const email = document.getElementById('regEmailInput').value.trim();
                const phone = document.getElementById('regPhoneInput').value.trim();
                const password = document.getElementById('regPasswordInput').value.trim();
                const registerButton = document.getElementById('registerButton');
                const registerStatus = document.getElementById('registerStatus');
                
                if (!name || !email || !password) {
                    registerStatus.innerHTML = '<span style="color: #dc3545;">Please fill all required fields</span>';
                    return;
                }
                
                registerButton.disabled = true;
                registerButton.textContent = 'Registering...';
                registerStatus.innerHTML = '<span style="color: #6c757d;">Creating account...</span>';
                
                try {
                    const response = await fetch('/auth/register', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            name: name,
                            email: email,
                            phone: phone,
                            password: password,
                            latitude: 12.9716, // Default to Bangalore coordinates
                            longitude: 77.5946
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        registerStatus.innerHTML = '<span style="color: #28a745;">✅ Registration successful!</span>';
                        
                        // Auto-login after registration
                        setTimeout(async () => {
                            document.getElementById('emailInput').value = email;
                            document.getElementById('passwordInput').value = password;
                            showLoginForm();
                            await loginUser();
                        }, 1500);
                        
                    } else {
                        registerStatus.innerHTML = '<span style="color: #dc3545;">❌ ' + (data.detail || 'Registration failed') + '</span>';
                    }
                } catch (error) {
                    console.error('Registration error:', error);
                    registerStatus.innerHTML = '<span style="color: #dc3545;">❌ Network error. Please try again.</span>';
                } finally {
                    registerButton.disabled = false;
                    registerButton.textContent = 'Register';
                }
            }
            
            function showLoginForm() {
                document.getElementById('loginForm').style.display = 'block';
                document.getElementById('tokenForm').style.display = 'none';
                document.getElementById('registerForm').style.display = 'none';
                document.getElementById('loginTab').classList.add('active');
                document.getElementById('tokenTab').classList.remove('active');
                document.getElementById('loginTab').style.background = '#4CAF50';
                document.getElementById('tokenTab').style.background = '#6c757d';
            }
            
            function showTokenForm() {
                document.getElementById('loginForm').style.display = 'none';
                document.getElementById('tokenForm').style.display = 'block';
                document.getElementById('registerForm').style.display = 'none';
                document.getElementById('loginTab').classList.remove('active');
                document.getElementById('tokenTab').classList.add('active');
                document.getElementById('loginTab').style.background = '#6c757d';
                document.getElementById('tokenTab').style.background = '#4CAF50';
            }
            
            function showRegisterForm() {
                document.getElementById('loginForm').style.display = 'none';
                document.getElementById('tokenForm').style.display = 'none';
                document.getElementById('registerForm').style.display = 'block';
            }
            
            function showUserInfo(email) {
                document.getElementById('currentUser').textContent = email;
                document.getElementById('userInfo').style.display = 'block';
            }
            
            function logout() {
                localStorage.removeItem('auth_token');
                localStorage.removeItem('user_email');
                document.getElementById('userInfo').style.display = 'none';
                document.getElementById('authSection').style.display = 'block';
                showLoginForm();
                
                // Clear form fields
                document.getElementById('emailInput').value = '';
                document.getElementById('passwordInput').value = '';
                document.getElementById('loginStatus').innerHTML = '';
                
                // Reconnect without token
                connect();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.get("/health")
async def health_check():
    """Health check for Gemini Live service."""
    try:
        service = get_gemini_live_service()
        tools_info = service.get_available_tools()
        return {
            "status": "healthy",
            "service": "Gemini Live Agricultural Assistant",
            "tools_available": tools_info["total_tools"],
            "model": service.model,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service unhealthy: {str(e)}")
