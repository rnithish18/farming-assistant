from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import requests
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
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

    completion = client.chat.completions.create(
        model="llama-3.3-70b-specdec",
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    return {"reply": completion.choices[0].message.content}

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