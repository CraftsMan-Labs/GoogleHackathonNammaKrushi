import asyncio
import logging
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from google import genai
from google.genai import types
import requests
from typing import Dict, Any, Union
import os
from dotenv import load_dotenv
from PIL import Image
import io
import base64
from pydantic import BaseModel

load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Agricultural Assistant API", version="1.0.0")

# Initialize GenAI client
client = genai.Client()
model = "gemini-live-2.5-flash-preview"


# Pydantic models for API requests
class SearchRequest(BaseModel):
    query: str


class WeatherRequest(BaseModel):
    city: str


class CoordinatesRequest(BaseModel):
    lat: float
    lon: float


class CropAnalysisRequest(BaseModel):
    image_base64: str
    farmer_query: str
    include_visual_search: bool = True


# Agricultural function implementations
async def google_search(query: str) -> dict:
    """Performs a Google search and returns a list of results."""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": os.getenv("GOOGLE_SEARCH_API_KEY"),
        "cx": os.getenv("GOOGLE_SEARCH_CSE_ID"),
        "num": 10,
    }

    try:
        logging.info(f"Performing Google search with params: {params}")
        response = requests.get(url, params=params)
        response.raise_for_status()

        results = response.json().get("items", [])
        search_results = [
            {
                "title": item.get("title"),
                "snippet": item.get("snippet"),
                "link": item.get("link"),
            }
            for item in results
        ]

        if search_results:
            formatted_results = "\n".join(
                f"{i + 1}. {item['title']}\n{item['snippet']}\n{item['link']}"
                for i, item in enumerate(search_results)
            )
            return {"status": "success", "results": formatted_results}
        else:
            return {"status": "success", "results": "No results found."}

    except Exception as e:
        return {"status": "error", "error_message": f"Google search failed: {str(e)}"}


async def analyze_crop_image_and_search(
    image_input: str, farmer_query: str, include_visual_search: bool = True
) -> Dict[str, Any]:
    """Analyzes a diseased crop image using Google Vision API and performs a web search."""

    try:
        # Assume image_input is base64 encoded string
        image_base64 = image_input.replace("data:image/jpeg;base64,", "").replace(
            "data:image/png;base64,", ""
        )
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to process image: {str(e)}",
        }

    # Analyze image with Google Vision API
    vision_analysis = {}
    try:
        vision_api_key = os.getenv("GOOGLE_VISION_API_KEY")
        vision_url = "https://vision.googleapis.com/v1/images:annotate"

        vision_request = {
            "requests": [
                {
                    "image": {"content": image_base64},
                    "features": [
                        {"type": "LABEL_DETECTION", "maxResults": 10},
                        {"type": "WEB_DETECTION", "maxResults": 5},
                        {"type": "OBJECT_LOCALIZATION", "maxResults": 5},
                        {"type": "IMAGE_PROPERTIES", "maxResults": 5},
                    ],
                }
            ]
        }

        response = requests.post(
            f"{vision_url}?key={vision_api_key}", json=vision_request
        )
        response.raise_for_status()
        vision_data = response.json()

        if "responses" in vision_data and vision_data["responses"]:
            response = vision_data["responses"][0]

            labels = []
            if "labelAnnotations" in response:
                labels = [
                    label["description"] for label in response["labelAnnotations"][:5]
                ]

            web_entities = []
            if "webDetection" in response and "webEntities" in response["webDetection"]:
                web_entities = [
                    entity.get("description", "")
                    for entity in response["webDetection"]["webEntities"]
                    if entity.get("description")
                ][:3]

            vision_analysis = {
                "labels": labels,
                "web_entities": web_entities,
            }

    except Exception as e:
        logging.error(f"Vision API error: {str(e)}")
        vision_analysis = {"error": f"Vision API failed: {str(e)}"}

    # Enhanced search
    search_terms = []
    if vision_analysis.get("web_entities"):
        search_terms.extend(vision_analysis["web_entities"][:2])

    crop_disease_keywords = [
        "plant",
        "leaf",
        "disease",
        "fungus",
        "pest",
        "crop",
        "blight",
        "wilt",
        "spot",
    ]
    if vision_analysis.get("labels"):
        relevant_labels = [
            label
            for label in vision_analysis["labels"]
            if any(keyword in label.lower() for keyword in crop_disease_keywords)
        ]
        search_terms.extend(relevant_labels[:2])

    search_terms.append(farmer_query)
    enhanced_query = (
        " ".join(search_terms) if search_terms[:-1] else f"crop disease {farmer_query}"
    )

    # Perform search
    search_results = await google_search(enhanced_query)

    return {
        "status": "success",
        "farmer_query": farmer_query,
        "image_analysis": vision_analysis,
        "search_results": search_results,
        "enhanced_query": enhanced_query,
    }


async def get_weather_by_location(city: str) -> dict:
    """Retrieves the current weather report for a specified city using OpenWeatherMap API."""
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        return {
            "status": "error",
            "error_message": "OpenWeather API key not configured",
        }

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        weather_info = {
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "city": data["name"],
            "country": data["sys"]["country"],
        }

        return {
            "status": "success",
            "weather_data": weather_info,
            "report": f"Weather in {data['name']}, {data['sys']['country']}: {data['weather'][0]['description']}, {data['main']['temp']}°C, Humidity: {data['main']['humidity']}%",
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Weather API request failed: {str(e)}",
        }


async def get_weather_by_coordinates(lat: float, lon: float) -> dict:
    """Retrieves current weather data for specified coordinates."""
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        return {
            "status": "error",
            "error_message": "OpenWeather API key not configured",
        }

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        return {"status": "success", "weather_data": data}
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Weather API request failed: {str(e)}",
        }


import json
import requests


async def get_soilgrids_data(lat: float, lon: float) -> dict:
    """Fetches soil property data for the given coordinates using the SoilGrids v2.0 REST API."""
    properties = [
        "bdod",
        "cec",
        "cfvo",
        "clay",
        "nitrogen",
        "ocd",
        "ocs",
        "phh2o",
        "sand",
        "silt",
        "soc",
        "wv0010",
        "wv0033",
        "wv1500",
    ]
    depths = [
        "0-5cm",
        "0-30cm",
        "5-15cm",
        "15-30cm",
        "30-60cm",
        "60-100cm",
        "100-200cm",
    ]
    values = ["Q0.05", "Q0.5", "Q0.95", "mean", "uncertainty"]

    try:
        url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}"
        for prop in properties:
            url += f"&property={prop}"
        for depth in depths:
            url += f"&depth={depth}"
        for value in values:
            url += f"&value={value}"

        response = requests.get(
            url, timeout=200, headers={"accept": "application/json"}
        )
        response.raise_for_status()

        soil_data = response.json()
        processed_data = {}

        # Updated processing logic to match the actual API response structure
        if "properties" in soil_data and "layers" in soil_data["properties"]:
            for layer in soil_data["properties"]["layers"]:
                prop_name = layer.get("name")
                if prop_name:
                    processed_data[prop_name] = {}
                    # Add unit information
                    if "unit_measure" in layer:
                        processed_data[prop_name]["unit_measure"] = layer[
                            "unit_measure"
                        ]

                    # Process depths
                    for depth_info in layer.get("depths", []):
                        depth_label = depth_info.get("label", "unknown")
                        depth_values = depth_info.get("values", {})
                        processed_data[prop_name][depth_label] = depth_values

        return {"status": "success", "data": json.dumps(processed_data)}

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to fetch SoilGrids data: {str(e)}",
        }


# Function declarations for GenAI
function_declarations = [
    {
        "name": "google_search",
        "description": "Performs a Google search and returns relevant results",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query string"}
            },
            "required": ["query"],
        },
    },
    {
        "name": "analyze_crop_image_and_search",
        "description": "Analyzes a crop disease image and performs enhanced search",
        "parameters": {
            "type": "object",
            "properties": {
                "image_input": {
                    "type": "string",
                    "description": "Base64 encoded image data",
                },
                "farmer_query": {
                    "type": "string",
                    "description": "Farmer's description or question about the crop disease",
                },
                "include_visual_search": {
                    "type": "boolean",
                    "description": "Whether to include visual search",
                    "default": True,
                },
            },
            "required": ["image_input", "farmer_query"],
        },
    },
    {
        "name": "get_weather_by_location",
        "description": "Gets current weather for a specified city",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name for weather information",
                }
            },
            "required": ["city"],
        },
    },
    {
        "name": "get_weather_by_coordinates",
        "description": "Gets current weather for specified coordinates",
        "parameters": {
            "type": "object",
            "properties": {
                "lat": {"type": "number", "description": "Latitude coordinate"},
                "lon": {"type": "number", "description": "Longitude coordinate"},
            },
            "required": ["lat", "lon"],
        },
    },
    {
        "name": "get_soilgrids_data",
        "description": "Fetches comprehensive soil property data for given coordinates",
        "parameters": {
            "type": "object",
            "properties": {
                "lat": {"type": "number", "description": "Latitude coordinate"},
                "lon": {"type": "number", "description": "Longitude coordinate"},
            },
            "required": ["lat", "lon"],
        },
    },
]

tools = [{"function_declarations": function_declarations}]
config = {
    "response_modalities": ["TEXT"],
    "tools": tools,
    "system_instruction": """You are an expert agricultural assistant with access to Google Search, Weather, and Soil Data APIs. 
    You can help farmers with:
    - Crop disease identification and treatment recommendations
    - Weather information for farming decisions
    - Soil property analysis for crop planning
    - General agricultural research and advice
    
    When users provide images of crops, analyze them for diseases and provide actionable recommendations.
    Always provide practical, evidence-based advice. Be concise but thorough in your responses.""",
}


async def handle_function_call(function_call):
    """Handle function calls and return responses"""
    function_name = function_call.name
    args = function_call.args

    try:
        if function_name == "google_search":
            result = await google_search(args.get("query", ""))
        elif function_name == "analyze_crop_image_and_search":
            result = await analyze_crop_image_and_search(
                args.get("image_input", ""),
                args.get("farmer_query", ""),
                args.get("include_visual_search", True),
            )
        elif function_name == "get_weather_by_location":
            result = await get_weather_by_location(args.get("city", ""))
        elif function_name == "get_weather_by_coordinates":
            result = await get_weather_by_coordinates(
                args.get("lat", 0), args.get("lon", 0)
            )
        elif function_name == "get_soilgrids_data":
            result = await get_soilgrids_data(args.get("lat", 0), args.get("lon", 0))
        else:
            result = {
                "status": "error",
                "error_message": f"Unknown function: {function_name}",
            }

        return types.FunctionResponse(
            id=function_call.id, name=function_call.name, response=result
        )
    except Exception as e:
        return types.FunctionResponse(
            id=function_call.id,
            name=function_call.name,
            response={"status": "error", "error_message": str(e)},
        )


# WebSocket endpoint for live streaming
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        async with client.aio.live.connect(model=model, config=config) as session:
            while True:
                # Receive message from client
                try:
                    data = await websocket.receive_text()
                    message_data = json.loads(data)
                    user_message = message_data.get("message", "")

                    if not user_message:
                        continue

                    # Send user message to GenAI
                    await session.send_client_content(
                        turns={"parts": [{"text": user_message}]}
                    )

                    # Process responses and stream back to client
                    async for chunk in session.receive():
                        if chunk.server_content:
                            if chunk.text is not None:
                                await websocket.send_text(
                                    json.dumps(
                                        {"type": "response", "content": chunk.text}
                                    )
                                )

                        elif chunk.tool_call:
                            # Notify client that functions are being called
                            function_names = [
                                fc.name for fc in chunk.tool_call.function_calls
                            ]
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "function_call",
                                        "functions": function_names,
                                    }
                                )
                            )

                            function_responses = []
                            for fc in chunk.tool_call.function_calls:
                                function_response = await handle_function_call(fc)
                                function_responses.append(function_response)

                            await session.send_tool_response(
                                function_responses=function_responses
                            )

                except WebSocketDisconnect:
                    break
                except json.JSONDecodeError:
                    await websocket.send_text(
                        json.dumps({"type": "error", "content": "Invalid JSON format"})
                    )
                except Exception as e:
                    await websocket.send_text(
                        json.dumps({"type": "error", "content": str(e)})
                    )

    except Exception as e:
        logging.error(f"WebSocket error: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass


# REST API endpoints
@app.post("/api/search")
async def search_endpoint(request: SearchRequest):
    """Google search endpoint"""
    result = await google_search(request.query)
    return result


@app.post("/api/weather/city")
async def weather_city_endpoint(request: WeatherRequest):
    """Weather by city endpoint"""
    result = await get_weather_by_location(request.city)
    return result


@app.post("/api/weather/coordinates")
async def weather_coordinates_endpoint(request: CoordinatesRequest):
    """Weather by coordinates endpoint"""
    result = await get_weather_by_coordinates(request.lat, request.lon)
    return result


@app.post("/api/soil")
async def soil_endpoint(request: CoordinatesRequest):
    """Soil data endpoint"""
    result = await get_soilgrids_data(request.lat, request.lon)
    return result


@app.post("/api/crop-analysis")
async def crop_analysis_endpoint(request: CropAnalysisRequest):
    """Crop analysis endpoint"""
    result = await analyze_crop_image_and_search(
        request.image_base64, request.farmer_query, request.include_visual_search
    )
    return result


# HTML Demo Page
@app.get("/", response_class=HTMLResponse)
async def get_demo_page():
    """Live API demo page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Agricultural Assistant - Text Chat Demo</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                max-width: 800px;
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
                height: 400px;
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
            }
            .user-message {
                background: #007bff;
                color: white;
                margin-left: auto;
                text-align: right;
            }
            .bot-message {
                background: white;
                border: 1px solid #ddd;
                margin-right: auto;
            }
            .function-call {
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                margin-right: auto;
                font-style: italic;
                color: #856404;
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
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌱 Agricultural Assistant</h1>
                <p>Text Chat AI assistant for farming, weather, soil analysis, and crop diseases</p>
            </div>
            
            <div class="status" id="status">
                <span class="disconnected">Connecting...</span>
            </div>
            
            <div class="chat-container" id="chatContainer">
                <div class="message bot-message">
                    <strong>Agricultural Assistant:</strong> Hello! I'm your text-based AI farming assistant. I can help you with:
                    <br>• Crop disease identification and treatment
                    <br>• Weather information for farming decisions  
                    <br>• Soil analysis for any location
                    <br>• Agricultural research and advice
                    <br><br>Type your questions or use the examples below!
                </div>
            </div>
            
            <div class="input-container">
                <input type="text" id="messageInput" class="input-field" 
                       placeholder="Ask about crops, weather, soil, or farming advice..." 
                       disabled>
                <button id="sendButton" class="send-button" disabled>Send</button>
            </div>
            
            <div class="examples">
                <h3>Try these examples:</h3>
                <div class="example-button" data-example="What's the weather like in Iowa today?">Weather in Iowa</div>
                <div class="example-button" data-example="Get soil analysis for coordinates 40.7128, -74.0060">Soil Analysis NYC</div>
                <div class="example-button" data-example="How do I identify tomato blight?">Tomato Blight</div>
                <div class="example-button" data-example="Best practices for corn planting in spring">Corn Planting Tips</div>
                <div class="example-button" data-example="Search for organic pesticide alternatives">Organic Pesticides</div>
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
                const wsUrl = `${protocol}//${window.location.host}/ws`;
                
                ws = new WebSocket(wsUrl);
                
                ws.onopen = function() {
                    isConnected = true;
                    status.innerHTML = '<span class="connected">Connected - Ready to chat!</span>';
                    messageInput.disabled = false;
                    sendButton.disabled = false;
                    messageInput.focus();
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    
                    if (data.type === 'response') {
                        addMessage(data.content, 'bot-message');
                    } else if (data.type === 'function_call') {
                        addMessage(`🔧 Calling functions: ${data.functions.join(', ')}`, 'function-call');
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

            function addMessage(content, className) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${className}`;
                
                if (className === 'user-message') {
                    messageDiv.innerHTML = `<strong>You:</strong> ${content}`;
                } else if (className === 'bot-message') {
                    messageDiv.innerHTML = `<strong>Assistant:</strong> ${content}`;
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


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Agricultural Assistant API is running"}


if __name__ == "__main__":
    import uvicorn

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Run the server
    uvicorn.run(
        "gemini_live_app:app",  # Replace "main" with your actual filename
        host="0.0.0.0",
        port=8000,
        reload=True,
        ws_ping_interval=20,
        ws_ping_timeout=20,
    )
