from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
import requests

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.post("/chat")
def chat(request: ChatRequest):
    prompt = f"""You are a helpful farming assistant for farmers in India.
Answer the following question simply and practically in English only.
A farmer with no technical background should easily understand your answer.
Question: {request.message}"""
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt
    )
    return {"reply": response.text}

@app.post("/diagnose")
async def diagnose(file: UploadFile = File(...)):
    image_bytes = await file.read()
    prompt = """You are an expert agricultural assistant helping Indian farmers.
Look at this photo of a crop or plant leaf and respond in English only. Identify:
1. The likely disease or pest problem (if any)
2. How serious it looks
3. Simple, practical treatment steps using affordable or locally available methods
Keep the explanation simple and practical, avoiding technical jargon."""
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=file.content_type),
            prompt
        ]
    )
    return {"diagnosis": response.text}

@app.get("/weather")
def get_weather(city: str):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }
    response = requests.get(url, params=params)
    data = response.json()
    if response.status_code != 200:
        return {"error": data.get("message", "Could not fetch weather")}
    return {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"]
    }