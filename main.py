from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import requests
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

app = FastAPI()

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def read_root():
    return FileResponse("static/index.html")


# Chat Assistant
@app.post("/chat")
def chat(request: ChatRequest):
    try:
        prompt = f"""
You are a helpful farming assistant for farmers in India.

Answer the following question simply and practically in English.

Question: {request.message}
"""

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return {
            "reply": completion.choices[0].message.content
        }

    except Exception as e:
        return {
            "reply": f"Error: {str(e)}"
        }


# Plant Diagnosis
@app.post("/diagnose")
async def diagnose(file: UploadFile = File(...)):
    try:
        filename = file.filename

        return {
            "reply": f"""
Plant image uploaded successfully.

File Name: {filename}

The image diagnosis model is currently unavailable on this deployment.

Future Enhancement:
• Detect plant disease
• Identify pests
• Suggest treatments
• Provide prevention methods

Image upload functionality is working correctly.
"""
        }

    except Exception as e:
        return {
            "reply": f"Diagnosis failed: {str(e)}"
        }


# Weather API
@app.get("/weather")
def get_weather(city: str):
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"

        params = {
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }

        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code != 200:
            return {
                "error": data.get("message", "Could not fetch weather")
            }

        return {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"]
        }

    except Exception as e:
        return {
            "error": str(e)
        }


# Available Models
@app.get("/models")
def get_models():
    try:
        models = client.models.list()
        return models
    except Exception as e:
        return {"error": str(e)}