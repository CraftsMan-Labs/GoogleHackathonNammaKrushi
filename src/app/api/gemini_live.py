"""
Gemini Live API endpoints for real-time agricultural assistance.
"""

import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, Any

from ..services.gemini_live_service import get_gemini_live_service

router = APIRouter(prefix="/live", tags=["Gemini Live"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user_id: int = None):
    """WebSocket endpoint for Gemini Live text chat with history tracking."""
    logging.info("WebSocket connection requested")

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
            
            <div class="chat-container" id="chatContainer">
                <div class="message bot-message">
                    <strong>Namma Krushi AI:</strong> ನಮಸ್ಕಾರ! I'm your text-based AI farming assistant for Karnataka. I can help you with:
                    <br>• <strong>Crop Management:</strong> Track crops, stages, health scores
                    <br>• <strong>Daily Logs:</strong> Record farming activities and observations  
                    <br>• <strong>Sales Tracking:</strong> Monitor sales and calculate profits
                    <br>• <strong>Disease Diagnosis:</strong> Analyze crop images for diseases
                    <br>• <strong>Weather & Soil:</strong> Get weather forecasts and soil analysis
                    <br>• <strong>Market Research:</strong> Search for prices and best practices
                    <br><br>Type your questions in English or Kannada! Try the examples below.
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
                <div class="example-button" data-example="ಟೊಮೇಟೊ ಬೆಳೆಗೆ ಯಾವ ಗೊಬ್ಬರ ಬಳಸಬೇಕು?">Tomato Fertilizer (Kannada)</div>
            </div>
            
            <div class="tools-info">
                <strong>Available Tools:</strong> Google Search, Weather API, Soil Analysis, Crop Disease Detection, 
                Crop Management, Daily Logs, Sales Tracking, and more agricultural tools. All chat history is automatically saved.
            </div>
        </div>

        <script>
            const chatContainer = document.getElementById('chatContainer');
            const messageInput = document.getElementById('messageInput');
            const sendButton = document.getElementById('sendButton');
            const status = document.getElementById('status');
            
            let ws = null;
            let isConnected = false;

            function connect() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/live/ws`;
                
                ws = new WebSocket(wsUrl);
                
                ws.onopen = function() {
                    isConnected = true;
                    status.innerHTML = '<span class="connected">Connected - Ready to help with farming!</span>';
                    messageInput.disabled = false;
                    sendButton.disabled = false;
                    messageInput.focus();
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    
                    if (data.type === 'response') {
                        addMessage(data.content, 'bot-message', 'Namma Krushi AI');
                    } else if (data.type === 'function_call') {
                        addMessage(data.message || `🔧 Using tools: ${data.functions.join(', ')}`, 'function-call');
                    } else if (data.type === 'system') {
                        addMessage(data.content, 'system-message');
                    } else if (data.type === 'error') {
                        addMessage(`Error: ${data.content}`, 'error-message');
                    }
                };
                
                ws.onclose = function() {
                    isConnected = false;
                    status.innerHTML = '<span class="disconnected">Disconnected - Reconnecting...</span>';
                    messageInput.disabled = true;
                    sendButton.disabled = true;
                    
                    // Reconnect after 3 seconds
                    setTimeout(connect, 3000);
                };
                
                ws.onerror = function(error) {
                    console.error('WebSocket error:', error);
                    addMessage('Connection error occurred', 'error-message');
                };
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

            function sendMessage() {
                const message = messageInput.value.trim();
                if (!message || !isConnected) return;
                
                addMessage(message, 'user-message');
                
                ws.send(JSON.stringify({
                    message: message
                }));
                
                messageInput.value = '';
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

            // Connect on page load
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
