from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import requests
import base64
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

# 1. TEXT CHAT ENDPOINT
@app.post("/chat")
def chat(request: ChatRequest):
    prompt = f"""You are a helpful farming assistant for farmers in India.
Answer the following question simply and practically in English only.
A farmer with no technical background should easily understand your answer.
Question: {request.message}"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    return {"reply": completion.choices[0].message.content}

# 2. IMAGE DIAGNOSIS ENDPOINT (PRODUCTION VISION MODEL FIXED)
@app.post("/diagnose")
async def diagnose(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        base64_image = base64.b64encode(contents).decode("utf-8")

        prompt = """You are an expert plant pathologist and agronomy assistant. 
        Analyze this plant image. Identify the plant, identify any visible diseases or pests, 
        and give clear, simple, practical treatment solutions in English for a regular farmer."""

        completion = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{file.content_type};base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
        )
        return {"reply": completion.choices[0].message.content}
    except Exception as e:
        return {"reply": f"Diagnosis failed: {str(e)}"}

# 3. WEATHER ENDPOINT
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