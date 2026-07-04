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
import bcrypt
from dotenv import load_dotenv
import requests
from pymongo import MongoClient
from bson import ObjectId

# --- SMTP EMAIL IMPORTS ---
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Brevo SMTP credentials (from environment variables)
BREVO_SMTP_LOGIN = os.getenv("BREVO_SMTP_LOGIN")
BREVO_SMTP_KEY = os.getenv("BREVO_SMTP_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

# MongoDB Connection
mongo_client = MongoClient(os.getenv("MONGODB_URI"))
db = mongo_client["farming_assistant"]
users_col = db["users"]

otp_store = {}

app = FastAPI(title="Farming AI Assistant")

def strip_think_tags(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

def log_activity(username: str, feature_type: str, search_summary: str, result_text: str = ""):
    """Save an activity log entry showing what was searched and a preview of what was returned."""
    try:
        if not username or username == "Anonymous":
            return
        preview = result_text.strip().replace("\n", " ")
        if len(preview) > 150:
            preview = preview[:150] + "..."
        details = search_summary
        if preview:
            details = f"{search_summary} → {preview}"
        db["activity_logs"].insert_one({
            "username": username,
            "feature_type": feature_type,
            "query_details": details,
            "timestamp": time.time()
        })
    except Exception as e:
        print(f"Activity log error: {e}")

# --- PYDANTIC SCHEMAS ---
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


# --- BREVO SMTP EMAIL SENDING ---
def send_otp_email(email: str, name: str, otp: str, subject: str):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Farming Assistant <{SENDER_EMAIL}>"
        msg["To"] = email

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
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP("smtp-relay.brevo.com", 587) as server:
            server.starttls()
            server.login(BREVO_SMTP_LOGIN, BREVO_SMTP_KEY)
            server.sendmail(SENDER_EMAIL, email, msg.as_string())
        return True
    except Exception as e:
        print(f"Brevo SMTP email delivery error: {e}")
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
    return {"success": False, "message": "Failed to send email. Please try again."}


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


# --- GUEST LOGIN ---

@app.post("/guest-login")
def guest_login(data: dict):
    username = data.get("username", "").strip()
    if not username:
        return {"success": False, "message": "Please enter a name."}
    if len(username) < 2:
        return {"success": False, "message": "Name must be at least 2 characters."}

    existing = users_col.find_one({"username": username})
    if existing and not existing.get("is_guest"):
        return {"success": False, "message": "That name is taken by a registered account. Please choose another."}

    if not existing:
        users_col.insert_one({
            "username": username,
            "email": None,
            "password": None,
            "is_guest": True,
            "created_at": time.time()
        })

    return {"success": True, "message": f"Welcome, {username}!", "username": username}


@app.post("/register")
def register(request: RegisterRequest):
    username = request.username.strip()
    email = request.email.strip()
    password = request.password.strip()

    if not username or not email or not password:
        return {"success": False, "message": "All fields are required."}
    if len(password) < 6:
        return {"success": False, "message": "Password must be at least 6 characters."}

    if users_col.find_one({"username": username}):
        return {"success": False, "message": "Username already taken. Please choose another."}

    if users_col.find_one({"email": email}):
        return {"success": False, "message": "Email already registered. Please login."}

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    users_col.insert_one({
        "username": username,
        "email": email,
        "password": hashed,
        "is_guest": False,
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

    if user.get("is_guest"):
        return {"success": False, "message": "This is a guest account with no password. Use Guest Login instead."}

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


# --- PROFILE PHOTO ---

@app.post("/upload-photo")
def upload_photo(data: dict):
    username = data.get("username", "").strip()
    photo = data.get("photo", "")
    if not username or not photo:
        return {"success": False, "message": "Missing data"}
    if len(photo) > 1400000:
        return {"success": False, "message": "Image too large"}
    users_col.update_one({"username": username}, {"$set": {"photo": photo}})
    return {"success": True, "message": "Photo updated"}


@app.get("/get-photo")
def get_photo(username: str):
    user = users_col.find_one({"username": username})
    if user and user.get("photo"):
        return {"success": True, "photo": user["photo"]}
    return {"success": False, "photo": None}


# --- PROFILE ---

@app.get("/profile")
def get_profile(username: str):
    user = users_col.find_one({"username": username})
    if not user:
        return {"success": False, "message": "User not found"}

    total = db["activity_logs"].count_documents({"username": username})

    pipeline = [
        {"$match": {"username": username}},
        {"$group": {"_id": "$feature_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]
    result = list(db["activity_logs"].aggregate(pipeline))
    most_used = result[0]["_id"] if result else "None yet"

    created_at = user.get("created_at", time.time())
    member_since = time.strftime("%d %b %Y", time.localtime(created_at))

    return {
        "success": True,
        "email": user.get("email") or "Guest account (no email)",
        "total_activities": total,
        "most_used_feature": most_used,
        "member_since": member_since,
        "is_guest": user.get("is_guest", False)
    }


@app.post("/change-password")
def change_password(data: dict):
    username = data.get("username", "").strip()
    current_password = data.get("current_password", "").strip()
    new_password = data.get("new_password", "").strip()

    user = users_col.find_one({"username": username})
    if not user:
        return {"success": False, "message": "User not found"}

    if user.get("is_guest"):
        return {"success": False, "message": "Guest accounts don't have passwords."}

    if not bcrypt.checkpw(current_password.encode("utf-8"), user["password"]):
        return {"success": False, "message": "Current password is incorrect"}

    if len(new_password) < 6:
        return {"success": False, "message": "New password must be at least 6 characters"}

    hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
    users_col.update_one({"username": username}, {"$set": {"password": hashed}})

    return {"success": True, "message": "Password updated successfully"}


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


@app.post("/clear-logs")
def clear_user_logs(data: dict):
    username = data.get("username", "").strip()
    if not username:
        return {"success": False, "message": "Missing username"}
    db["activity_logs"].delete_many({"username": username})
    return {"success": True, "message": "History cleared"}


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

@app.get("/profile.html", response_class=HTMLResponse)
def serve_profile(): return FileResponse("static/profile.html")

@app.get("/calendar.html", response_class=HTMLResponse)
def serve_calendar(): return FileResponse("static/calendar.html")

@app.get("/fertilizer.html", response_class=HTMLResponse)
def serve_fertilizer(): return FileResponse("static/fertilizer.html")

@app.get("/expenses.html", response_class=HTMLResponse)
def serve_expenses(): return FileResponse("static/expenses.html")

@app.get("/recommend.html", response_class=HTMLResponse)
def serve_recommend(): return FileResponse("static/recommend.html")

@app.get("/yield.html", response_class=HTMLResponse)
def serve_yield(): return FileResponse("static/yield.html")

@app.get("/community.html", response_class=HTMLResponse)
def serve_community(): return FileResponse("static/community.html")

@app.get("/irrigation.html", response_class=HTMLResponse)
def serve_irrigation(): return FileResponse("static/irrigation.html")

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
    log_activity(request.username, "AI Chat", f"Asked: {request.message[:60]}", reply)
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
    diagnosis = strip_think_tags(response.choices[0].message.content)
    log_activity(username, "Crop Diagnosis", f"Uploaded photo: {file.filename}", diagnosis)
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
        tip = "மிகவும் சூடான நாள்." if temp > 38 else "அதிக ஈரப்பதம்." if humidity > 80 else "நல்ல விவசாய சூழல்."
    else:
        tip = "Very hot — water crops early morning." if temp > 38 else "High humidity — watch for fungal diseases." if humidity > 80 else "Good farming conditions."
    log_activity(username, "Live Weather", f"City: {data['name']}", f"{temp}°C, {data['weather'][0]['description']}, {tip}")
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
    log_activity(username, "Rain Forecast", f"City: {data['city']['name']}", f"7-day outlook, first day: {forecast[0]['description']}, {forecast[0]['rain_mm']}mm rain")
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
    prices = strip_think_tags(response.choices[0].message.content)
    log_activity(username, "Market Prices", f"Crop: {crop}, State: {state}", prices)
    return {"prices": prices}


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
    tips = strip_think_tags(response.choices[0].message.content)
    log_activity(username, "Soil Advisory", f"Crop: {crop}, Season: {season}, Soil: {soil_type}", tips)
    return {"tips": tips}


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
    alerts = strip_think_tags(response.choices[0].message.content)
    log_activity(username, "Pest Alerts", f"Crop: {crop}, State: {state}, Season: {season}", alerts)
    return {"alerts": alerts}


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
    schemes = strip_think_tags(response.choices[0].message.content)
    log_activity(username, "Govt Schemes", f"State: {state}, Category: {category}", schemes)
    return {"schemes": schemes}


# --- CROP CALENDAR ---

@app.get("/crop-calendar")
def get_crop_calendar(crop: str, state: str = "Tamil Nadu", lang: str = "en", username: str = "Anonymous"):
    if lang == "ta":
        prompt = f"{state}வில் {crop} பயிருக்கான மாதவாரியான பயிர் காலண்டரை தமிழில் கொடுக்கவும். நடவு மாதங்கள், வளர்ச்சி நிலைகள், அறுவடை மாதங்கள், ஒவ்வொரு கட்டத்திலும் கவனிக்க வேண்டிய முக்கிய பணிகள் என்று பட்டியலிடவும்."
        system_msg = "தமிழில் மட்டும் பதில் கொடுக்கவும்."
    else:
        prompt = f"Give a month-by-month crop calendar for {crop} in {state}, India. Include: Best Sowing Months, Growth Stages with approximate duration, Harvesting Months, Key Tasks for each stage (land prep, sowing, weeding, fertilizing, harvesting)."
        system_msg = "You are an expert Indian agricultural crop calendar advisor."
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": prompt}],
        max_tokens=1024
    )
    calendar = strip_think_tags(response.choices[0].message.content)
    log_activity(username, "Crop Calendar", f"Crop: {crop}, State: {state}", calendar)
    return {"calendar": calendar}

@app.get("/fertilizer-calculator")
def get_fertilizer_calculator(crop: str, land_size: float, land_unit: str = "acre", soil_type: str = "Loamy", growth_stage: str = "Sowing / Land Preparation", lang: str = "en", username: str = "Anonymous"):
    if lang == "ta":
        prompt = f"""{crop} பயிருக்கு {land_size} {land_unit} நிலப்பரப்பில், {soil_type} மண் வகையில், {growth_stage} கட்டத்தில் தேவையான உரத்தின் அளவை தமிழில் கணக்கிட்டுக் கொடுக்கவும்.

இந்த வடிவத்தில் பதில் கொடுக்கவும்:
நைட்ரஜன் (N): [அளவு] கிலோ
பாஸ்பரஸ் (P): [அளவு] கிலோ
பொட்டாசியம் (K): [அளவு] கிலோ
பரிந்துரைக்கப்படும் உரங்கள்: [குறிப்பிட்ட உர பெயர்கள் மற்றும் அளவுகள்]
பயன்படுத்தும் முறை: [எப்படி, எப்போது பயன்படுத்த வேண்டும்]
விவசாயி குறிப்பு: [ஒரு நடைமுறை குறிப்பு]"""
        system_msg = "நீங்கள் ஒரு இந்திய வேளாண் உர நிபுணர். துல்லியமான எண்களுடன் தமிழில் மட்டும் பதில் கொடுக்கவும்."
    else:
        prompt = f"""Calculate the fertilizer requirement for {crop} grown on {land_size} {land_unit} of land, with {soil_type} soil, currently at the {growth_stage} stage.

Give the response in this exact format:
Nitrogen (N): [amount] kg
Phosphorus (P): [amount] kg
Potassium (K): [amount] kg
Recommended Fertilizers: [specific fertilizer names and quantities, e.g. Urea, DAP, MOP]
Application Method: [how and when to apply]
Farmer Tip: [one practical tip]"""
        system_msg = "You are an Indian agricultural fertilizer expert. Give precise, practical calculations based on standard Indian crop fertilizer recommendations."
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": prompt}],
        max_tokens=1024
    )
    result = strip_think_tags(response.choices[0].message.content)
    log_activity(username, "Fertilizer Calculator", f"Crop: {crop}, {land_size} {land_unit}, Soil: {soil_type}", result)
    return {"result": result}

@app.post("/add-expense")
def add_expense(data: dict):
    username = data.get("username", "").strip()
    entry_type = data.get("type", "").strip()  # "expense" or "income"
    category = data.get("category", "").strip()
    amount = data.get("amount")
    note = data.get("note", "").strip()
    crop = data.get("crop", "").strip()

    if not username or not entry_type or not category or amount is None:
        return {"success": False, "message": "Missing required fields."}
    try:
        amount = float(amount)
    except:
        return {"success": False, "message": "Invalid amount."}
    if amount <= 0:
        return {"success": False, "message": "Amount must be greater than 0."}

    db["expenses"].insert_one({
        "username": username,
        "type": entry_type,
        "category": category,
        "amount": amount,
        "note": note,
        "crop": crop,
        "timestamp": time.time()
    })
    return {"success": True, "message": "Entry added"}


@app.get("/get-expenses")
def get_expenses(username: str):
    entries = list(db["expenses"].find(
        {"username": username}, {"_id": 0}
    ).sort("timestamp", -1))

    total_income = sum(e["amount"] for e in entries if e["type"] == "income")
    total_expense = sum(e["amount"] for e in entries if e["type"] == "expense")

    return {
        "entries": entries,
        "total_income": total_income,
        "total_expense": total_expense,
        "net_profit": total_income - total_expense
    }


@app.post("/delete-expense")
def delete_expense(data: dict):
    username = data.get("username", "").strip()
    timestamp = data.get("timestamp")
    if not username or timestamp is None:
        return {"success": False, "message": "Missing data"}
    db["expenses"].delete_one({"username": username, "timestamp": timestamp})
    return {"success": True, "message": "Entry deleted"}

@app.get("/crop-recommendation")
def get_crop_recommendation(soil_type: str, season: str, state: str = "Tamil Nadu", water_availability: str = "Medium", lang: str = "en", username: str = "Anonymous"):
    if lang == "ta":
        prompt = f"""{state}வில், {soil_type} மண் வகையில், {season} பருவத்தில், {water_availability} நீர் கிடைக்கும் நிலையில் சிறந்த 3-4 பயிர்களை பரிந்துரைக்கவும். தமிழில் பதிலளிக்கவும்.

இந்த வடிவத்தில் பதில் கொடுக்கவும்:
பரிந்துரைக்கப்படும் பயிர்கள்: [பயிர் பெயர்கள் பட்டியல்]

ஒவ்வொரு பயிருக்கும்:
- ஏன் இது பொருத்தமானது
- எதிர்பார்க்கப்படும் வருமானம் (உயர்/நடுத்தர/குறைவு)
- வளர்ச்சி காலம்

சிறந்த தேர்வு: [ஒரு பயிரை முதன்மையாக பரிந்துரைக்கவும் மற்றும் ஏன்]"""
        system_msg = "தமிழில் மட்டும் பதில் கொடுக்கவும்."
    else:
        prompt = f"""Recommend the best 3-4 crops to grow in {state}, India with {soil_type} soil, during {season} season, with {water_availability} water availability.

Give the response in this exact format:
Recommended Crops: [list of crop names]

For each crop:
- Why it's suitable
- Expected profitability (High/Medium/Low)
- Growth duration

Top Pick: [recommend one crop as the best choice and why]"""
        system_msg = "You are an expert Indian agricultural crop advisor helping farmers choose the most profitable and suitable crops for their conditions."
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": prompt}],
        max_tokens=1024
    )
    result = strip_think_tags(response.choices[0].message.content)
    log_activity(username, "Crop Recommendation", f"Soil: {soil_type}, Season: {season}, State: {state}", result)
    return {"result": result}

@app.get("/yield-prediction")
def get_yield_prediction(crop: str, land_size: float, land_unit: str = "acre", soil_type: str = "Loamy", irrigation: str = "Rain-fed", lang: str = "en", username: str = "Anonymous"):
    if lang == "ta":
        prompt = f"""{crop} பயிருக்கு {land_size} {land_unit} நிலப்பரப்பில், {soil_type} மண் வகையில், {irrigation} நீர்ப்பாசன முறையில் எதிர்பார்க்கப்படும் மகசூலை தமிழில் மதிப்பிடவும்.

இந்த வடிவத்தில் பதில் கொடுக்கவும்:
மதிப்பிடப்பட்ட மகசூல்: [அளவு வரம்பு] (எ.கா. குவிண்டால் அல்லது டன்)
சராசரி மகசூல் ஒப்பீடு: [இந்த பகுதியின் சராசரியுடன் ஒப்பிடுக]
மகசூலை பாதிக்கும் காரணிகள்: [முக்கிய காரணிகள் பட்டியல்]
மகசூலை மேம்படுத்த குறிப்புகள்: [2-3 நடைமுறை குறிப்புகள்]
கணிப்பு நம்பகத்தன்மை: [குறிப்பு - இது ஒரு பொதுவான மதிப்பீடு, சரியான புள்ளிவிவரம் அல்ல]"""
        system_msg = "தமிழில் மட்டும் பதில் கொடுக்கவும். இது ஒரு பொதுவான AI மதிப்பீடு என்பதை தெளிவுபடுத்தவும், துல்லியமான அறிவியல் கணிப்பு அல்ல."
    else:
        prompt = f"""Estimate the expected yield for {crop} grown on {land_size} {land_unit} of land, with {soil_type} soil, using {irrigation} irrigation.

Give the response in this exact format:
Estimated Yield: [range] (e.g. in quintals or tonnes)
Comparison to Regional Average: [how it compares]
Factors Affecting Yield: [list key factors]
Tips to Improve Yield: [2-3 practical tips]
Prediction Confidence: [note that this is a general AI estimate, not a precise scientific forecast]"""
        system_msg = "You are an agricultural yield estimation assistant. Give a general, practical estimate based on typical Indian farming conditions. Always clarify this is an approximate AI estimate, not a precise scientific prediction."
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": prompt}],
        max_tokens=1024
    )
    result = strip_think_tags(response.choices[0].message.content)
    log_activity(username, "Yield Prediction", f"Crop: {crop}, {land_size} {land_unit}, {irrigation}", result)
    return {"result": result}


# --- IRRIGATION SCHEDULER ---

@app.get("/irrigation-schedule")
def get_irrigation_schedule(crop: str, soil_type: str = "Loamy", growth_stage: str = "Sowing / Land Preparation", season: str = "Kharif (Monsoon)", irrigation_method: str = "Rain-fed", lang: str = "en", username: str = "Anonymous"):
    if lang == "ta":
        prompt = f"""{crop} பயிருக்கு, {soil_type} மண் வகையில், {growth_stage} கட்டத்தில், {season} பருவத்தில், {irrigation_method} முறையில் தேவையான நீர்ப்பாசன அட்டவணையை தமிழில் கொடுக்கவும்.

இந்த வடிவத்தில் பதில் கொடுக்கவும்:
நீர்ப்பாசன அதிர்வெண்: [எத்தனை நாட்களுக்கு ஒருமுறை]
ஒவ்வொரு முறையும் தேவையான நீர் அளவு: [மிமீ அல்லது லிட்டரில்]
சிறந்த நேரம்: [காலை/மாலை போன்றவை]
கவனிக்க வேண்டியவை: [மண் ஈரப்பதம் சரிபார்ப்பு, வானிலை மாற்றங்கள் போன்றவை]
விவசாயி குறிப்பு: [ஒரு நடைமுறை குறிப்பு]"""
        system_msg = "நீங்கள் ஒரு இந்திய வேளாண் நீர்ப்பாசன நிபுணர். நடைமுறை அட்டவணையுடன் தமிழில் மட்டும் பதில் கொடுக்கவும்."
    else:
        prompt = f"""Create a practical irrigation schedule for {crop}, grown in {soil_type} soil, currently at the {growth_stage} stage, during {season} season, using {irrigation_method} irrigation.

Give the response in this exact format:
Irrigation Frequency: [how often, e.g. every X days]
Water Amount per Session: [in mm or liters]
Best Time of Day: [e.g. early morning / evening]
Things to Watch: [soil moisture checks, weather changes to adjust for]
Farmer Tip: [one practical tip]"""
        system_msg = "You are an Indian agricultural irrigation expert. Give a practical, easy-to-follow watering schedule based on typical Indian farming conditions."
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": prompt}],
        max_tokens=1024
    )
    result = strip_think_tags(response.choices[0].message.content)
    log_activity(username, "Irrigation Scheduler", f"Crop: {crop}, Soil: {soil_type}, Stage: {growth_stage}", result)
    return {"result": result}


# --- COMMUNITY Q&A ---

@app.post("/community/ask")
def post_question(data: dict):
    username = data.get("username", "Anonymous").strip()
    question = data.get("question", "").strip()
    lang = data.get("lang", "en")
    if not question:
        return {"success": False, "message": "Please enter a question."}
    doc = {
        "username": username,
        "question": question,
        "lang": lang,
        "timestamp": time.time(),
        "answers": []
    }
    result = db["community"].insert_one(doc)
    log_activity(username, "Community Q&A", f"Asked: {question[:60]}")
    return {"success": True, "message": "Question posted", "id": str(result.inserted_id)}


@app.get("/community/questions")
def get_questions(limit: int = 30):
    posts = list(db["community"].find().sort("timestamp", -1).limit(limit))
    for p in posts:
        p["id"] = str(p["_id"])
        del p["_id"]
    return {"questions": posts}


@app.post("/community/answer")
def post_answer(data: dict):
    question_id = data.get("question_id", "").strip()
    username = data.get("username", "Anonymous").strip()
    answer = data.get("answer", "").strip()
    if not question_id or not answer:
        return {"success": False, "message": "Missing data"}
    db["community"].update_one(
        {"_id": ObjectId(question_id)},
        {"$push": {"answers": {"username": username, "answer": answer, "timestamp": time.time()}}}
    )
    return {"success": True, "message": "Answer posted"}


@app.post("/community/ai-answer")
def get_ai_answer(data: dict):
    question_id = data.get("question_id", "").strip()
    question_text = data.get("question", "").strip()
    lang = data.get("lang", "en")
    if not question_text:
        return {"success": False, "message": "Missing question"}
    if lang == "ta":
        system_msg = "நீங்கள் இந்திய விவசாயிகளுக்கு உதவும் ஒரு பயனுள்ள வேளாண் உதவியாளர். தமிழில் மட்டும், சுருக்கமாகவும் நடைமுறையாகவும் பதிலளிக்கவும்."
    else:
        system_msg = "You are a helpful farming assistant for Indian farmers. Answer briefly and practically in English only."
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": question_text}],
        max_tokens=512
    )
    answer = strip_think_tags(response.choices[0].message.content)
    if question_id:
        db["community"].update_one(
            {"_id": ObjectId(question_id)},
            {"$push": {"answers": {"username": "🤖 AI Assistant", "answer": answer, "timestamp": time.time()}}}
        )
    return {"success": True, "answer": answer}


@app.post("/community/delete")
def delete_question(data: dict):
    question_id = data.get("question_id", "").strip()
    username = data.get("username", "").strip()
    if not question_id:
        return {"success": False, "message": "Missing data"}
    post = db["community"].find_one({"_id": ObjectId(question_id)})
    if not post:
        return {"success": False, "message": "Not found"}
    if post.get("username") != username:
        return {"success": False, "message": "You can only delete your own question"}
    db["community"].delete_one({"_id": ObjectId(question_id)})
    return {"success": True, "message": "Deleted"}


app.mount("/static", StaticFiles(directory="static"), name="static")