from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from groq import Groq
import base64
import os
from dotenv import load_dotenv
import requests

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
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
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful farming assistant for farmers in India. Answer questions simply and practically in English only. Avoid technical jargon."},
            {"role": "user", "content": request.message}
        ],
        max_tokens=1024
    )
    return {"reply": response.choices[0].message.content}

@app.post("/diagnose")
async def diagnose(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    response = groq_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{file.content_type};base64,{image_b64}"}
                    },
                    {
                        "type": "text",
                        "text": "You are an expert agricultural assistant helping Indian farmers. Look at this photo of a crop or plant leaf and respond in English only. Identify: 1. The likely disease or pest problem if any 2. How serious it looks 3. Simple practical treatment steps using affordable locally available methods. Keep it simple and avoid technical jargon."
                    }
                ]
            }
        ],
        max_tokens=1024
    )
    return {"diagnosis": response.choices[0].message.content}

@app.get("/weather")
def get_weather(city: str):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"}
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