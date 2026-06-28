from fastapi import FastAPI, UploadFile, File, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional
from groq import Groq
import base64
import os
import re
import resend
import random
import time
import bcrypt
from dotenv import load_dotenv
import requests
from pymongo import MongoClient

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
resend.api_key = os.getenv("RESEND_API_KEY")

# MongoDB
mongo_client = MongoClient(os.getenv("MONGODB_URI"))
db = mongo_client["farming_assistant"]
users_col = db["users"]

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

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ResetPasswordRequest(BaseModel):
    email: str
    otp: str
    new_password: str

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)

@app.get("/.well-known/appspecific/com.chrome.devtools.json", include_in_schema=False)
def chrome_devtools():
    return Response(status_code=204)

def send_otp_email(email: str, name: str, otp: str, subject: str):
    try:
        resend.Emails.send({
            "from": "Farming Assistant <onboarding@resend.dev>",
            "to": email,
            "subject": subject,
            "html": f"""
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
        })
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


# --- AUTH ENDPOINTS ---

@app.post("/send-otp")
def send_otp(data: dict):
    email = data.get("email", "").strip()
    name = data.get("name", "").strip()
    if not email or "@" not in email:
        return {"success": False, "message": "Invalid email address"}
    otp = str(random.randint(100000, 999999))
    otp_store[email] = {"otp": otp, "time": time.time(), "name": name}
    success = send_otp_email(email, name, otp, f"{otp} is your Farming Assistant OTP")
    if success:
        return {"success": True, "message": "OTP sent successfully"}
    return {"success": False, "message": "Failed to send email"}


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


@app.post("/register")
def register(request: RegisterRequest):
    username = request.username.strip()
    email = request.email.strip()
    password = request.password.strip()

    if not username or not email or not password:
        return {"success": False, "message": "All fields are required."}
    if len(password) < 6:
        return {"success": False, "message": "Password must be at least 6 characters."}

    # Check if username already exists
    if users_col.find_one({"username": username}):
        return {"success": False, "message": "Username already taken. Please choose another."}

    # Check if email already exists
    if users_col.find_one({"email": email}):
        return {"success": False, "message": "Email already registered. Please login."}

    # Hash password
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    # Save to MongoDB
    users_col.insert_one({
        "username": username,
        "email": email,
        "password": hashed,
        "created_at": time.time()
    })

    return {"success": True, "message": f"Account created! Welcome {username}."}


@app.post("/login")
def login(request: LoginRequest):
    username = request.username.strip()
    password = request.password.strip()

    user = users_col.find_one({"username": username})
    if not user:
        return {"success": False, "message": "Username not found. Please register first."}

    if not bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        return {"success": False, "message": "Incorrect password. Please try again."}

    return {"success": True, "message": f"Welcome back, {username}!", "username": username}


@app.post("/forgot-password/send-otp")
def forgot_password_otp(data: dict):
    email = data.get("email", "").strip()
    if not email:
        return {"success": False, "message": "Please enter your email."}

    user = users_col.find_one({"email": email})
    if not user:
        return {"success": False, "message": "No account found with this email."}

    otp = str(random.randint(100000, 999999))
    otp_store[f"reset_{email}"] = {"otp": otp, "time": time.time(), "name": user["username"]}

    success = send_otp_email(
        email, user["username"], otp,
        f"{otp} - Reset your Farming Assistant password"
    )
    if success:
        return {"success": True, "message": "OTP sent to your email."}
    return {"success": False, "message": "Failed to send email."}


@app.post("/forgot-password/reset")
def reset_password(request: ResetPasswordRequest):
    email = request.email.strip()
    otp = request.otp.strip()
    new_password = request.new_password.strip()

    key = f"reset_{email}"
    if key not in otp_store:
        return {"success": False, "message": "No OTP found. Please request a new one."}

    stored = otp_store[key]
    if time.time() - stored["time"] > 600:
        del otp_store[key]
        return {"success": False, "message": "OTP expired. Please request a new one."}

    if stored["otp"] != otp:
        return {"success": False, "message": "Incorrect OTP. Please try again."}

    if len(new_password) < 6:
        return {"success": False, "message": "Password must be at least 6 characters."}

    hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
    users_col.update_one({"email": email}, {"$set": {"password": hashed}})
    del otp_store[key]

    return {"success": True, "message": "Password reset successfully! Please login."}


# --- LOGS ---

@app.post("/save-log")
def save_user_log(request: LogRequest):
    try:
        db["activity_logs"].insert_one({
            "username": request.username,
            "feature_type": request.feature_type,
            "query_details": request.query_details,
            "timestamp": time.time()
        })
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/get-logs")
def get_user_logs(username: str):
    try:
        logs = list(db["activity_logs"].find(
            {"username": username},
            {"_id": 0}
        ).sort("timestamp", -1).limit(10))
        return {"history": [{"feature": l["feature_type"], "query": l["query_details"], "time": l.get("timestamp", "")} for l in logs]}
    except Exception as e:
        return {"error": str(e)}


# --- PAGE ROUTES ---

@app.get("/", response_class=HTMLResponse)
def read_root():
    return FileResponse("static/index.html")

@app.get("/chat.html", response_class=HTMLResponse)
def serve_chat(): return FileResponse("static/chat.html")

@app.get("/diagnose.html", response_class=HTMLResponse)
def serve_diagnose(): return FileResponse("static/diagnose.html")

@app.get("/weather.html", response_class=HTMLResponse)
def serve_weather(): return FileResponse("static/weather.html")

@app.get("/forecast.html", response_class=HTMLResponse)
def serve_forecast(): return FileResponse("static/forecast.html")

@app.get("/market.html", response_class=HTMLResponse)
def serve_market(): return FileResponse("static/market.html")

@app.get("/soil.html", response_class=HTMLResponse)
def serve_soil(): return FileResponse("static/soil.html")

@app.get("/pest.html", response_class=HTMLResponse)
def serve_pest(): return FileResponse("static/pest.html")

@app.get("/schemes.html", response_class=HTMLResponse)
def serve_schemes(): return FileResponse("static/schemes.html")

@app.get("/login.html", response_class=HTMLResponse)
def serve_login(): return FileResponse("static/login.html")

@app.get("/register.html", response_class=HTMLResponse)
def serve_register(): return FileResponse("static/register.html")


# --- CHAT ---

@app.post("/chat")
def chat(request: ChatRequest):
    if request.lang == "ta":
        system_message = (
            "நீங்கள் இந்திய விவசாயிகளுக்கு உதவும் ஒரு பயனுள்ள வேளாண் உதவியாளர். "
            "கேள்விகளுக்கு தமிழில் மட்டும், எளிமையாகவும் நடைமுறையாகவும் பதிலளிக்கவும்."
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
    return {"reply": reply}


# --- DIAGNOSE ---

@app.post("/diagnose")
async def diagnose(file: UploadFile = File(...), lang: str = "en", username: str = "Anonymous"):
    image_bytes = await file.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    if lang == "ta":
        prompt_text = (
            "நீங்கள் இந்திய விவசாயிகளுக்கு உதவும் நிபுணர். "
            "இந்த பயிர் இலையை பார்த்து தமிழில் பதிலளிக்கவும்: "
            "1. நோய் அல்லது பூச்சி பிரச்சனை 2. தீவிரம் 3. எளிய சிகிச்சை படிகள்."
        )
    else:
        prompt_text = (
            "You are an expert agricultural assistant. Look at this crop photo and identify: "
            "1. Disease or pest problem 2. Severity 3. Simple treatment steps."
        )
    response = groq_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_text},
                {"type": "image_url", "image_url": {"url": f"data:{file.content_type};base64,{image_b64}"}}
            ]
        }],
        max_tokens=1024
    )
    return {"diagnosis": strip_think_tags(response.choices[0].message.content)}


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
        tip = "மிகவும் சூடான நாள்." if temp > 38 else "அதிக ஈரப்பதம்." if humidity > 80 else "நல்ல விவசாய சூழல்."
    else:
        tip = "Very hot — water crops early morning." if temp > 38 else "High humidity — watch for fungal diseases." if humidity > 80 else "Good farming conditions."
    return {
        "city": data["name"], "temperature": temp,
        "feels_like": data["main"]["feels_like"], "humidity": humidity,
        "description": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"], "farming_tip": tip
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
        if rain_mm > 10:
            advice = "Heavy rain — avoid spraying." if lang != "ta" else "கனமழை — தெளிக்க வேண்டாம்."
        elif rain_mm > 2:
            advice = "Light rain — hold irrigation." if lang != "ta" else "லேசான மழை — நீர்பாசனம் நிறுத்தவும்."
        elif avg_temp > 38:
            advice = "Very hot — water early morning." if lang != "ta" else "சூடான நாள் — காலையில் தண்ணீர் பாய்ச்சவும்."
        elif avg_humidity > 80:
            advice = "High humidity — watch for fungal diseases." if lang != "ta" else "அதிக ஈரப்பதம் — பூஞ்சை நோய் கவனிக்கவும்."
        else:
            advice = "Good farming conditions." if lang != "ta" else "நல்ல விவசாய சூழல்."
        forecast.append({
            "date": date, "avg_temp": avg_temp, "avg_humidity": avg_humidity,
            "description": most_common_desc, "rain_mm": rain_mm, "farming_advice": advice
        })
    return {"city": data["city"]["name"], "forecast": forecast}


# --- MARKET ---

@app.get("/market")
def get_market_prices(crop: str, state: str = "Tamil Nadu", lang: str = "en", username: str = "Anonymous"):
    if lang == "ta":
        prompt = f"{state}வில் {crop} பயிரின் தற்போதைய மொத்த சந்தை விலைகளை தமிழில் கொடுக்கவும். கிலோ விலை, குவிண்டால் விலை, சிறந்த சந்தைகள், விலை போக்கு, விவசாயி குறிப்பு என்று பதிலளிக்கவும்."
        system_msg = "தமிழில் மட்டும் பதில் கொடுக்கவும்."
    else:
        prompt = f"Provide current wholesale market prices for {crop} in {state}, India. Include: Price per Kg, Price per Quintal, Min/Max Price, Best Markets, Price Trend, Farmer Tip."
        system_msg = "You are an Indian agricultural market price expert."
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": prompt}],
        max_tokens=512
    )
    return {"prices": strip_think_tags(response.choices[0].message.content)}


# --- SOIL ---

@app.get("/soil")
def get_soil_tips(crop: str, season: str, soil_type: str, lang: str = "en", username: str = "Anonymous"):
    if lang == "ta":
        prompt = f"{crop} பயிர், {season} பருவம், {soil_type} மண் வகைக்கான மண் தயாரிப்பு, உர குறிப்புகள், நீர்பாசன வழிகாட்டி, நடவு நேரம், அறுவடை தகவல் தமிழில் கொடுக்கவும்."
        system_msg = "தமிழில் மட்டும் பதில் கொடுக்கவும்."
    else:
        prompt = f"Give practical soil and crop tips for Crop: {crop}, Season: {season}, Soil: {soil_type}. Cover: Soil Preparation, Fertilizer, Watering, Planting Time, Harvest."
        system_msg = "You are an expert Indian agricultural advisor."
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": prompt}],
        max_tokens=1024
    )
    return {"tips": strip_think_tags(response.choices[0].message.content)}


# --- PEST ---

@app.get("/pest")
def get_pest_alerts(crop: str, state: str, season: str, lang: str = "en", username: str = "Anonymous"):
    if lang == "ta":
        prompt = f"{crop} பயிர், {state} மாநிலம், {season} பருவத்தில் பொதுவான பூச்சிகள், எச்சரிக்கை அறிகுறிகள், இயற்கை மற்றும் இரசாயன சிகிச்சை, தடுப்பு குறிப்புகள் தமிழில் கொடுக்கவும்."
        system_msg = "தமிழில் மட்டும் பதில் கொடுக்கவும்."
    else:
        prompt = f"Give pest alerts for Crop: {crop}, State: {state}, Season: {season}. Cover: Common Pests, Warning Signs, Organic Treatment, Chemical Treatment, Prevention."
        system_msg = "You are an expert Indian pest management advisor."
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": prompt}],
        max_tokens=1024
    )
    return {"alerts": strip_think_tags(response.choices[0].message.content)}


# --- SCHEMES ---

@app.get("/schemes")
def get_schemes(state: str, category: str = "All", lang: str = "en", username: str = "Anonymous"):
    if lang == "ta":
        prompt = f"{state} மாநிலத்தில் விவசாயிகளுக்கு கிடைக்கும் அரசு திட்டங்களை தமிழில் பட்டியலிடவும். வகை: {category}."
        system_msg = "தமிழில் மட்டும் பதில் கொடுக்கவும்."
    else:
        prompt = f"List government agricultural schemes in {state}, India. Category: {category}. Include Eligibility, Benefits, How to Apply."
        system_msg = "You are an Indian government scheme advisor."
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": prompt}],
        max_tokens=1024
    )
    return {"schemes": strip_think_tags(response.choices[0].message.content)}


app.mount("/static", StaticFiles(directory="static"), name="static")