from fastapi import FastAPI, HTTPException, Request # Requestをインポート
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates # Jinja2Templatesをインポート
import httpx
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import random
import json # jsonモジュールを追加

import logging

from tools.weather import get_weather, WeatherResponse
from tools.search import search_web, SearchResponse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Example usage of logger
logger.info("Logging is set up.")


app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# テンプレートエンジンを初期化
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request): # requestを引数に追加
    return templates.TemplateResponse("index.html", {"request": request})

# tools_config.jsonのパス
TOOLS_CONFIG_PATH = "tools_config.json"

@app.get("/static/tools_config")
async def get_static_tools_config():
    try:
        with open(TOOLS_CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        return JSONResponse(content=config)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="tools_config.json not found")
    except Exception as e:
        logger.error(f"Error reading tools config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not read tools config: {str(e)}")

# 静的ファイルを提供
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load environment variables
load_dotenv(override=True)

# Get API key from environment variable
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
REALTIME_SESSION_URL = os.getenv("REALTIME_SESSION_URL")

# this is the openai url: https://api.openai.com/v1/realtime/sessions
logger.info(f"REALTIME_SESSION_URL: {REALTIME_SESSION_URL}")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
if not SERPER_API_KEY:
    raise ValueError("SERPER_API_KEY not found in environment variables")
if not REALTIME_SESSION_URL:
    raise ValueError("REALTIME_SESSION_URL not found in environment variables")

class SessionResponse(BaseModel):
    session_id: str
    token: str

class WeatherResponse(BaseModel):
    temperature: float
    humidity: float
    precipitation: float
    wind_speed: float
    unit_temperature: str = "celsius"
    unit_precipitation: str = "mm"
    unit_wind: str = "km/h"
    forecast_daily: list
    current_time: str
    latitude: float
    longitude: float
    location_name: str
    weather_code: int

class SearchResponse(BaseModel): # SearchResponseの定義が抜けていたので追加
    title: str
    snippet: str
    source: str
    image_url: str | None = None
    image_source: str | None = None

@app.get("/session")
async def get_session(voice: str = "echo"):
    try:
        # tools_config.jsonを読み込み、有効なツールのみを渡す
        with open(TOOLS_CONFIG_PATH, "r", encoding="utf-8") as f:
            tools_config = json.load(f)
        
        enabled_tools = []
        if tools_config.get("weather", {}).get("enabled"):
            enabled_tools.append({
                "type": "function",
                "name": "get_weather",
                "description": "Get current weather and 7-day forecast for any location on Earth. Includes temperature, humidity, precipitation, and wind speed.",
                "parameters": {
                    "type": "object",
                    "description": "The location to get the weather for in English",
                    "properties": {
                        "location": { 
                            "type": "string",
                            "description": "The city or location name to get weather for"
                        }
                    },
                    "required": ["location"]
                }
            })
        if tools_config.get("search", {}).get("enabled"):
            enabled_tools.append({
                "type": "function",
                "name": "search_web",
                "description": "Search the web for current information about any topic",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": { "type": "string" }
                    },
                    "required": ["query"]
                }
            })

        async with httpx.AsyncClient() as client:
            response = await client.post(
                REALTIME_SESSION_URL,
                headers={
                    'Authorization': f'Bearer {OPENAI_API_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    "model": "gpt-4o-realtime-preview",
                    "voice": voice,
                    "instructions": """
                    You are a helpful assistant that can answer questions and help with tasks.
                    You have access to real-time weather data and web search capabilities.
                    When asked about the weather, provide the current temperature and humidity. Provide more information when asked.
                    When asked about a forecast, provide it but say ranging from x to y degrees over the days.
                    Never answer in markdown format. Plain text only with no markdown.
                    """,
                    "tools": enabled_tools, # 有効なツールのみを渡す
                    "tool_choice": "auto"
                }
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e.response.status_code}")
        return JSONResponse(status_code=e.response.status_code, content={"error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "details": str(e)})

@app.get("/weather/{location}", response_model=WeatherResponse)
async def get_weather_endpoint(location: str):
    return await get_weather(location)

@app.get("/search/{query}", response_model=SearchResponse)
async def search_web_endpoint(query: str):
    return await search_web(query, SERPER_API_KEY)

# tools_config.jsonのパス
TOOLS_CONFIG_PATH = "tools_config.json"

@app.get("/tools_config")
async def get_tools_config():
    try:
        with open(TOOLS_CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        return JSONResponse(content=config)
    except FileNotFoundError:
        return JSONResponse(status_code=404, content={"error": "tools_config.json not found"})
    except Exception as e:
        logger.error(f"Error reading tools config: {str(e)}")
        return JSONResponse(status_code=500, content={"error": f"Could not read tools config: {str(e)}"})

@app.post("/update_tools_config")
async def update_tools_config(config: dict):
    try:
        with open(TOOLS_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        return {"message": "Tools configuration updated successfully"}
    except Exception as e:
        logger.error(f"Error updating tools config: {str(e)}")
        return JSONResponse(status_code=500, content={"error": f"Could not update tools config: {str(e)}"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
