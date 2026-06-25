from fastapi import FastAPI, UploadFile, File, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional
from groq import Groq
import base64
import os
import re
import random
import time
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
import requests
import sqlite3

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL = "farming.assistant.india@gmail.com"
otp_store = {}

app = FastAPI(title="Farming AI Assistant")

def strip_think_tags(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

class ChatRequest(BaseModel):
    message: str
    lang: str = "en"
    username: str = "Anonymous"

class LogRequest(BaseModel):
    username: str
    feature_type: str
    query_details: str

class ProfileRequest(BaseModel):
    username: str
    auth_type: str
    phone_number: Optional[str] = None
    email: Optional[str] = None
    age: int
    gender: str

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)

@app.get("/.well-known/appspecific/com.chrome.devtools.json", include_in_schema=False)
def chrome_devtools_silent_handler():
    return Response(status_code=204)

def init_db():
    conn = sqlite3.connect("farming_assistant.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            feature_type TEXT NOT NULL,
            query_details TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS farmer_profiles (
            username TEXT PRIMARY KEY,
            auth_type TEXT NOT NULL DEFAULT 'guest',
            phone_number TEXT,
            email TEXT,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            is_otp_verified INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

def save_log(username: str, feature_type: str, details: str):
    try:
        conn = sqlite3.connect("farming_assistant.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO activity_logs (username, feature_type, query_details) VALUES (?, ?, ?)",
            (username, feature_type, details)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Logging error: {e}")

# --- OTP ENDPOINTS ---

@app.post("/send-otp")
def send_otp(data: dict):
    email = data.get("email", "").strip()
    name = data.get("name", "").strip()
    if not email or "@" not in email:
        return {"success": False, "message": "Invalid email address"}
    otp = str(random.randint(100000, 999999))
    otp_store[email] = {"otp": otp, "time": time.time(), "name": name}
    try:
        html_content = f"""
        <div style="font-family:Arial,sans-serif;max-width:400px;margin:auto;
                    background:#f0f7f0;border-radius:12px;padding:30px;text-align:center">
            <h2 style="color:#2d5e2d">🌾 Farming Assistant</h2>
            <p style="color:#333">Hello <b>{name}</b>! Your verification code is:</p>
            <div style="font-size:2.5rem;font-weight:bold;color:#2d5e2d;
                        background:white;border-radius:8px;padding:20px;margin:20px 0;
                        letter-spacing:8px">{otp}</div>
            <p style="color:#666;font-size:0.9rem">This code expires in 10 minutes.</p>
            <p style="color:#999;font-size:0.8rem">Do not share this code with anyone.</p>
        </div>
        """
        message = Mail(
            from_email=SENDER_EMAIL,
            to_emails=email,
            subject=f"{otp} is your Farming Assistant OTP",
            html_content=html_content
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        return {"success": True, "message": "OTP sent successfully"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.post("/verify-otp")
def verify_otp(data: dict):
    email = data.get("email", "").strip()
    otp = data.get("otp", "").strip()
    if not email or email not in otp_store:
        return {"success": False, "message": "No OTP found. Please request a new one."}
    stored = otp_store[email]
    if time.time() - stored["time"] > 600:
        del otp_store[email]
        return {"success": False, "message": "OTP expired. Please request a new one."}
    if stored["otp"] != otp:
        return {"success": False, "message": "Incorrect OTP. Please try again."}
    name = stored["name"]
    del otp_store[email]
    return {"success": True, "message": "Verified successfully", "name": name}

# --- REGISTER ---

@app.post("/register-profile")
def register_profile(request: ProfileRequest):
    try:
        username_clean = request.username.strip()
        if not username_clean:
            return {"status": "error", "message": "Username cannot be empty."}
        is_verified = 1 if request.auth_type == "guest" else 0
        conn = sqlite3.connect("farming_assistant.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO farmer_profiles
            (username, auth_type, phone_number, email, age, gender, is_otp_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (username_clean, request.auth_type, request.phone_number,
              request.email, request.age, request.gender, is_verified))
        conn.commit()
        conn.close()
        return {"status": "success", "message": f"Welcome {username_clean}!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- LOGS ---

@app.post("/save-log")
def save_user_log(request: LogRequest):
    try:
        save_log(request.username, request.feature_type, request.query_details)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/get-logs")
def get_user_logs(username: str):
    try:
        conn = sqlite3.connect("farming_assistant.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT feature_type, query_details, timestamp FROM activity_logs WHERE username = ? ORDER BY timestamp DESC LIMIT 10",
            (username,)
        )
        rows = cursor.fetchall()
        conn.close()
        history = [{"feature": r[0], "query": r[1], "time": r[2]} for r in rows]
        return {"history": history}
    except Exception as e:
        return {"error": str(e)}

# --- PAGE ROUTES ---

@app.get("/", response_class=HTMLResponse)
def read_root():
    return FileResponse("static/index.html")

@app.get("/chat.html", response_class=HTMLResponse)
def serve_chat_page(): return FileResponse("static/chat.html")

@app.get("/diagnose.html", response_class=HTMLResponse)
def serve_diagnose_page(): return FileResponse("static/diagnose.html")

@app.get("/weather.html", response_class=HTMLResponse)
def serve_weather_page(): return FileResponse("static/weather.html")

@app.get("/forecast.html", response_class=HTMLResponse)
def serve_forecast_page(): return FileResponse("static/forecast.html")

@app.get("/market.html", response_class=HTMLResponse)
def serve_market_page(): return FileResponse("static/market.html")

@app.get("/soil.html", response_class=HTMLResponse)
def serve_soil_page(): return FileResponse("static/soil.html")

@app.get("/pest.html", response_class=HTMLResponse)
def serve_pest_page(): return FileResponse("static/pest.html")

@app.get("/schemes.html", response_class=HTMLResponse)
def serve_schemes_page(): return FileResponse("static/schemes.html")

# --- CHAT ---

@app.post("/chat")
def chat(request: ChatRequest):
    if request.lang == "ta":
        system_message = (
            "நீங்கள் இந்திய விவசாயிகளுக்கு உதவும் ஒரு பயனுள்ள வேளாண் உதவியாளர். "
            "கேள்விகளுக்கு தமிழில் மட்டும், எளிமையாகவும் நடைமுறையாகவும் பதிலளிக்கவும். "
            "தொழில்நுட்ப வார்த்தைகளை தவிர்க்கவும்."
        )
    else:
        system_message = (
            "You are a helpful farming assistant for farmers in India. "
            "Answer questions simply and practically in English only. Avoid technical jargon."
        )
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": request.message}
        ],
        max_tokens=1024
    )
    reply = strip_think_tags(response.choices[0].message.content)
    save_log(request.username, "AI Chatbot", f"Asked: {request.message[:40]}...")
    return {"reply": reply}

# --- DIAGNOSE ---

@app.post("/diagnose")
async def diagnose(file: UploadFile = File(...), lang: str = "en", username: str = "Anonymous"):
    image_bytes = await file.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    if lang == "ta":
        prompt_text = (
            "நீங்கள் இந்திய விவசாயிகளுக்கு உதவும் ஒரு நிபுணர் வேளாண் உதவியாளர். "
            "இந்த பயிர் அல்லது தாவர இலையின் புகைப்படத்தை பார்த்து தமிழில் மட்டும் பதிலளிக்கவும். "
            "கண்டறியவும்: 1. நோய் அல்லது பூச்சி பிரச்சனை 2. எவ்வளவு தீவிரம் "
            "3. உள்ளூரில் கிடைக்கும் மலிவான முறைகளில் எளிய சிகிச்சை படிகள்."
        )
    else:
        prompt_text = (
            "You are an expert agricultural assistant helping Indian farmers. "
            "Look at this photo of a crop or plant leaf and respond in English only. "
            "Identify: 1. The likely disease or pest problem 2. How serious it looks "
            "3. Simple practical treatment steps using affordable locally available methods."
        )
    response = groq_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": f"data:{file.content_type};base64,{image_b64}"}}
                ]
            }
        ],
        max_tokens=1024
    )
    diagnosis = strip_think_tags(response.choices[0].message.content)
    save_log(username, "Crop Diagnosis", f"Uploaded image: {file.filename}")
    return {"diagnosis": diagnosis}

# --- WEATHER ---

@app.get("/weather")
def get_weather(city: str, lang: str = "en", username: str = "Anonymous"):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"}
    response = requests.get(url, params=params)
    data = response.json()
    if response.status_code != 200:
        return {"error": data.get("message", "Could not fetch weather")}
    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    if lang == "ta":
        if temp > 38:
            tip = "மிகவும் சூடான நாள் — காலையிலோ மாலையிலோ பயிர்களுக்கு தண்ணீர் பாய்ச்சவும்."
        elif humidity > 80:
            tip = "அதிக ஈரப்பதம் — இலைகளில் பூஞ்சை நோய்களை கவனிக்கவும்."
        else:
            tip = "நல்ல விவசாய சூழல் — வயல் வேலைகளுக்கு ஏற்றது."
    else:
        if temp > 38:
            tip = "Very hot day — water crops early morning or evening."
        elif humidity > 80:
            tip = "High humidity — watch for fungal diseases on leaves."
        else:
            tip = "Good farming conditions — suitable for field work."
    save_log(username, "Live Weather", f"Checked weather for {data['name']}")
    return {
        "city": data["name"],
        "temperature": temp,
        "feels_like": data["main"]["feels_like"],
        "humidity": humidity,
        "description": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"],
        "farming_tip": tip
    }

# --- FORECAST ---

@app.get("/forecast")
def get_forecast(city: str, lang: str = "en", username: str = "Anonymous"):
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
        if lang == "ta":
            if rain_mm > 10:
                advice = "கனமழை எதிர்பார்க்கப்படுகிறது — பூச்சிக்கொல்லி அல்லது உரம் தெளிக்க வேண்டாம்."
            elif rain_mm > 2:
                advice = "லேசான மழை எதிர்பார்க்கப்படுகிறது — பயிர்களுக்கு நல்லது."
            elif avg_temp > 38:
                advice = "மிகவும் சூடான நாள் — காலையிலோ மாலையிலோ தண்ணீர் பாய்ச்சவும்."
            elif avg_humidity > 80:
                advice = "அதிக ஈரப்பதம் — இலைகளில் பூஞ்சை நோய்களை கவனிக்கவும்."
            else:
                advice = "நல்ல விவசாய சூழல் — வயல் வேலைகளுக்கு ஏற்றது."
        else:
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
    save_log(username, "Weather Forecast", f"7-day forecast for {data['city']['name']}")
    return {"city": data["city"]["name"], "forecast": forecast}

# --- MARKET ---

@app.get("/market")
def get_market_prices(crop: str, state: str = "Tamil Nadu", lang: str = "en", username: str = "Anonymous"):
    if lang == "ta":
        prompt = f"""நீங்கள் இந்தியாவிற்கான வேளாண் சந்தை விலை நிபுணர்.
{state}, இந்தியாவில் {crop} பயிரின் தற்போதைய மொத்த சந்தை விலைகளை தமிழில் கொடுக்கவும்.

இந்த சரியான வடிவத்தில் பதில் கொடுக்கவும்:
பயிர்: {crop}
மாநிலம்: {state}
கிலோ விலை: ரூ [X]/கிலோ
குவிண்டால் விலை: ரூ [X]/குவிண்டால்
குறைந்தபட்ச விலை: ரூ [X]/கிலோ
அதிகபட்ச விலை: ரூ [X]/கிலோ
சிறந்த சந்தைகள்: [2-3 சந்தை பெயர்கள்]
விலை போக்கு: [அதிகரிக்கிறது/குறைகிறது/நிலையானது]
விவசாயி குறிப்பு: [ஒரு நடைமுறை குறிப்பு]"""
        system_msg = "நீங்கள் ஒரு இந்திய வேளாண் சந்தை விலை நிபுணர். தமிழில் மட்டும் பதில் கொடுக்கவும்."
    else:
        prompt = f"""You are an agricultural market price expert for India.
Provide current approximate wholesale market prices for {crop} in {state}, India.

Give the response in this exact format:
Crop: {crop}
State: {state}
Price per Kg: Rs [X]/kg
Price per Quintal: Rs [X]/quintal
Min Price: Rs [X]/kg
Max Price: Rs [X]/kg
Best Markets: [2-3 market names in {state}]
Price Trend: [Rising/Falling/Stable]
Farmer Tip: [one practical tip about selling this crop]"""
        system_msg = "You are an Indian agricultural market price expert. Always respond in the exact format requested."
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ],
        max_tokens=512
    )
    prices = strip_think_tags(response.choices[0].message.content)
    save_log(username, "Market Prices", f"Checked price for {crop} in {state}")
    return {"prices": prices}

# --- SOIL ---

@app.get("/soil")
def get_soil_tips(crop: str, season: str, soil_type: str, lang: str = "en", username: str = "Anonymous"):
    if lang == "ta":
        prompt = f"""நீங்கள் இந்திய விவசாயிகளுக்கான நிபுணர் வேளாண் ஆலோசகர்.
பயிர்: {crop}, பருவம்: {season}, மண் வகை: {soil_type} இதற்கான குறிப்புகளை தமிழில் கொடுக்கவும்.

மண் தயாரிப்பு, உர குறிப்புகள், நீர்பாசன வழிகாட்டி, சிறந்த நடவு நேரம், எதிர்பார்க்கப்படும் அறுவடை, விவசாயி குறிப்பு என்று பதிலளிக்கவும்."""
        system_msg = "நீங்கள் ஒரு நிபுணர் இந்திய வேளாண் ஆலோசகர். தமிழில் மட்டும் பதில் கொடுக்கவும்."
    else:
        prompt = f"""You are an expert agricultural advisor for Indian farmers.
Give practical soil and crop tips for:
Crop: {crop}, Season: {season}, Soil Type: {soil_type}

Cover: Soil Preparation, Fertilizer Tips, Watering Guide, Best Planting Time, Expected Harvest, Farmer Tip."""
        system_msg = "You are an expert Indian agricultural advisor. Give practical simple advice."
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024
    )
    tips = strip_think_tags(response.choices[0].message.content)
    save_log(username, "Soil Advisory", f"Tips for {crop} in {soil_type}")
    return {"tips": tips}

# --- PEST ---

@app.get("/pest")
def get_pest_alerts(crop: str, state: str, season: str, lang: str = "en", username: str = "Anonymous"):
    if lang == "ta":
        prompt = f"""நீங்கள் இந்திய விவசாயிகளுக்கான நிபுணர் பூச்சி மேலாண்மை ஆலோசகர்.
பயிர்: {crop}, மாநிலம்: {state}, பருவம்: {season} இதற்கான பூச்சி எச்சரிக்கைகளை தமிழில் கொடுக்கவும்.

பொதுவான பூச்சிகள், எச்சரிக்கை அறிகுறிகள், இயற்கை சிகிச்சை, இரசாயன சிகிச்சை, தடுப்பு குறிப்புகள் என்று பதிலளிக்கவும்."""
        system_msg = "நீங்கள் ஒரு நிபுணர் இந்திய பூச்சி மேலாண்மை ஆலோசகர். தமிழில் மட்டும் பதில் கொடுக்கவும்."
    else:
        prompt = f"""You are an expert pest management advisor for Indian farmers.
Give pest alerts for Crop: {crop}, State: {state}, Season: {season}.

Cover: Common Pests, Warning Signs, Organic Treatment, Chemical Treatment, Prevention Tips."""
        system_msg = "You are an expert Indian pest management advisor. Give practical region-specific advice."
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024
    )
    alerts = strip_think_tags(response.choices[0].message.content)
    save_log(username, "Pest Advisory", f"Pest alert for {crop} in {state}")
    return {"alerts": alerts}

# --- SCHEMES ---

@app.get("/schemes")
def get_schemes(state: str, category: str = "All", lang: str = "en", username: str = "Anonymous"):
    if lang == "ta":
        prompt = f"""{state} மாநிலத்தில் விவசாயிகளுக்கு கிடைக்கும் முக்கிய அரசு திட்டங்களை தமிழில் பட்டியலிடவும்.
வகை: {category}. தகுதி, நன்மைகள், விண்ணப்பிக்கும் முறை என்று விளக்கவும்."""
        system_msg = "நீங்கள் ஒரு அரசு திட்ட ஆலோசகர். தமிழில் மட்டும் பதில் கொடுக்கவும்."
    else:
        prompt = f"""List important government agricultural schemes available in {state}, India.
Category: {category}. For each scheme include: Eligibility, Benefits, How to Apply."""
        system_msg = "You are an Indian government scheme advisor. Give accurate practical information."
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024
    )
    schemes = strip_think_tags(response.choices[0].message.content)
    save_log(username, "Govt Schemes", f"Schemes in {state} - {category}")
    return {"schemes": schemes}

app.mount("/static", StaticFiles(directory="static"), name="static")