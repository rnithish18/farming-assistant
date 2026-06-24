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
    system_message: str = "You are a helpful farming assistant for farmers in India. Answer questions simply and practically in English only. Avoid technical jargon."

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.post("/chat")
def chat(request: ChatRequest):
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": request.system_message},
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
        model="qwen/qwen3.6-27b",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "You are an expert agricultural assistant helping Indian farmers. Look at this photo of a crop or plant leaf and respond in English only. Identify: 1. The likely disease or pest problem if any 2. How serious it looks 3. Simple practical treatment steps using affordable locally available methods. Keep it simple and avoid technical jargon."
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{file.content_type};base64,{image_b64}"}
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

@app.get("/forecast")
def get_forecast(city: str):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric", "cnt": 40}
    response = requests.get(url, params=params)
    data = response.json()
    if response.status_code != 200:
        return {"error": data.get("message", "Could not fetch forecast")}
    days = {}
    for item in data["list"]:
        date = item["dt_txt"].split(" ")[0]
        if date not in days:
            days[date] = {"temps": [], "descriptions": [], "rain": 0, "humidity": []}
        days[date]["temps"].append(item["main"]["temp"])
        days[date]["descriptions"].append(item["weather"][0]["description"])
        days[date]["humidity"].append(item["main"]["humidity"])
        if "rain" in item:
            days[date]["rain"] += item["rain"].get("3h", 0)
    forecast = []
    for date, info in list(days.items())[:7]:
        avg_temp = round(sum(info["temps"]) / len(info["temps"]), 1)
        avg_humidity = round(sum(info["humidity"]) / len(info["humidity"]))
        most_common_desc = max(set(info["descriptions"]), key=info["descriptions"].count)
        rain_mm = round(info["rain"], 1)
        if rain_mm > 10:
            advice = "Heavy rain expected — avoid spraying pesticides or fertilizers."
        elif rain_mm > 2:
            advice = "Light rain expected — good for crops, hold off on irrigation."
        elif avg_temp > 38:
            advice = "Very hot day — water crops early morning or evening."
        elif avg_humidity > 80:
            advice = "High humidity — watch for fungal diseases on leaves."
        else:
            advice = "Good farming conditions — suitable for field work."
        forecast.append({
            "date": date,
            "avg_temp": avg_temp,
            "avg_humidity": avg_humidity,
            "description": most_common_desc,
            "rain_mm": rain_mm,
            "farming_advice": advice
        })
    return {"city": data["city"]["name"], "forecast": forecast}

@app.get("/market")
def get_market_prices(crop: str, state: str = "Tamil Nadu"):
    prompt = f"""You are an agricultural market price expert for India.
Provide current approximate wholesale market prices for {crop} in {state}, India.

Give the response in this exact format (no extra text):
Crop: {crop}
State: {state}
Price per Kg: Rs [X]/kg
Price per Quintal: Rs [X]/quintal
Min Price: Rs [X]/kg
Max Price: Rs [X]/kg
Best Markets: [2-3 market names in {state}]
Price Trend: [Rising/Falling/Stable]
Farmer Tip: [one practical tip about selling this crop]

Use realistic current Indian market prices. Keep it brief and practical."""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an Indian agricultural market price expert. Always respond in the exact format requested. No extra explanation."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=512
    )
    return {"prices": response.choices[0].message.content}

@app.get("/soil")
def get_soil_tips(crop: str, season: str, soil_type: str):
    prompt = f"""You are an expert agricultural advisor for Indian farmers.
Give practical soil preparation and crop growing tips for:
Crop: {crop}
Season: {season}
Soil Type: {soil_type}

Give the response in this format:
Crop: {crop}
Season: {season}
Soil Type: {soil_type}

Soil Preparation:
[3-4 simple steps to prepare the soil]

Fertilizer Tips:
[what fertilizers to use, how much per acre, in simple terms]

Watering Guide:
[how often to water, how much]

Best Planting Time:
[exact months to plant in this season]

Expected Harvest:
[how many days/months to harvest]

Farmer Tip:
[one important tip specific to this crop and soil combination]

Keep everything simple and practical for a farmer with no technical background."""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an expert Indian agricultural advisor. Give practical, simple advice. Always follow the exact format requested."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024
    )
    return {"tips": response.choices[0].message.content}

@app.get("/pest")
def get_pest_alerts(crop: str, state: str, season: str):
    prompt = f"""You are an expert pest management advisor for Indian farmers.
Give pest and disease alerts for:
Crop: {crop}
State/Region: {state}
Season: {season}

Give the response in this format:

Crop: {crop}
Region: {state}
Season: {season}

Common Pests This Season:
1. [Pest name] — [what it looks like, what damage it causes]
2. [Pest name] — [what it looks like, what damage it causes]
3. [Pest name] — [what it looks like, what damage it causes]

Warning Signs to Watch:
[3 early warning signs a farmer should look for in the field]

Organic Treatment (cheap, local methods):
[2-3 affordable organic solutions using locally available materials]

Chemical Treatment (if severe):
[1-2 common pesticides available at local agri shops, with dosage]

Prevention Tips:
[2-3 simple prevention steps]

Keep everything simple, practical, and specific to {state} farmers."""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an expert Indian agricultural pest management advisor. Give practical, region-specific advice. Follow the exact format requested."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024
    )
    return {"alerts": response.choices[0].message.content}