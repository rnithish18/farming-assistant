from fastapi import FastAPI, UploadFile, File, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional
from groq import Groq
import base64
import os
import re
from dotenv import load_dotenv
import requests
import sqlite3

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

app = FastAPI(title="Farming AI Assistant - Multi-Channel Core")

def strip_think_tags(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


# --- PYDANTIC MODEL SCHEMAS ---

class ChatRequest(BaseModel):
    message: str
    lang: str = "en"
    username: str = "Anonymous"


class LogRequest(BaseModel):
    username: str
    feature_type: str
    query_details: str


# Upgraded schema to support flexible multi-channel profiles without 422 parsing structural exceptions
class ProfileRequest(BaseModel):
    username: str
    auth_type: str  # Supports: "guest", "phone", "email"
    phone_number: Optional[str] = None
    email: Optional[str] = None
    age: int
    gender: str


class OTPVerifyRequest(BaseModel):
    username: str
    otp: str


# --- SILENT HANDLERS FOR CLEAN TERMINAL LOGS ---

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@app.get("/.well-known/appspecific/com.chrome.devtools.json", include_in_schema=False)
def chrome_devtools_silent_handler():
    return Response(status_code=204)


# --- DATABASE LIFECYCLE MANAGEMENT ---

def init_db():
    conn = sqlite3.connect("farming_assistant.db")
    cursor = conn.cursor()
    
    # Activity logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            feature_type TEXT NOT NULL,
            query_details TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Farmer profiles verification table (Updated with multi-channel and tracking logic)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS farmer_profiles (
            username TEXT PRIMARY KEY,
            auth_type TEXT NOT NULL DEFAULT 'phone',
            phone_number TEXT,
            email TEXT,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            is_otp_verified INTEGER DEFAULT 0,
            mock_otp TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

# Initialize database tables on spin up
init_db()


# --- INTERCEPTOR LOGIC VERIFICATION SECURITY GUARDS ---

def is_profile_verified(username: str) -> bool:
    try:
        conn = sqlite3.connect("farming_assistant.db")
        cursor = conn.cursor()
        cursor.execute("SELECT is_otp_verified FROM farmer_profiles WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        if row and row[0] == 1:
            return True
    except Exception:
        pass
    return False


def save_verified_log(username: str, feature_type: str, details: str):
    if is_profile_verified(username):
        try:
            conn = sqlite3.connect("farming_assistant.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO activity_logs (username, feature_type, query_details) VALUES (?, ?, ?)",
                (username, feature_type, details)
            )
            conn.commit()
            conn.close()
            print(f"Log successfully recorded for verified user: {username}")
        except Exception as e:
            print(f"Logging error: {e}")
    else:
        print(f"Log blocked: User {username} has not verified their profile yet.")


# --- PROFILE REGISTRATION AND OTP ENDPOINTS ---

@app.post("/register-profile")
def register_profile(request: ProfileRequest):
    try:
        username_clean = request.username.strip()
        if not username_clean:
            return {"status": "error", "message": "Username parameter cannot be empty."}

        # Guest accounts skip the OTP verification state step entirely
        is_verified = 1 if request.auth_type == "guest" else 0
        
        # Branch sandbox security code values dynamically depending on requested access track
        if request.auth_type == "phone":
            simulated_otp = "1234"
        elif request.auth_type == "email":
            simulated_otp = "5678"
        else:
            simulated_otp = ""  # Guest account gets no verification token

        conn = sqlite3.connect("farming_assistant.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO farmer_profiles 
            (username, auth_type, phone_number, email, age, gender, is_otp_verified, mock_otp) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (username_clean, request.auth_type, request.phone_number, request.email, request.age, request.gender, is_verified, simulated_otp))
        conn.commit()
        conn.close()
        
        # Display explicit validation strings in local terminal window for developers
        if request.auth_type != "guest":
            print("\n" + "="*60)
            print(f"🔑 SECURITY SANDBOX VERIFICATION MONITOR")
            print(f"Target Identity User: {username_clean} via [{request.auth_type.upper()}]")
            print(f"PASSCODE VALUE TO SUBMIT FRONTEND: {simulated_otp}")
            print("="*60 + "\n")

        if request.auth_type == "guest":
            return {"status": "success", "message": f"Guest Profile Active! Welcome {username_clean}."}
        elif request.auth_type == "email":
            return {"status": "success", "message": "Profile initialized. Check sandbox console for email token entry.", "mock_otp": "5678"}
        else:
            return {"status": "success", "message": "Profile initialized. Check sandbox console for SMS OTP code.", "mock_otp": "1234"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/verify-otp")
def verify_otp(request: OTPVerifyRequest):
    try:
        username_clean = request.username.strip()
        conn = sqlite3.connect("farming_assistant.db")
        cursor = conn.cursor()
        cursor.execute("SELECT mock_otp FROM farmer_profiles WHERE username = ?", (username_clean,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return {"status": "error", "message": "Profile not detected. Please register account info first."}
            
        stored_otp = row[0]
        
        if request.otp == stored_otp:
            cursor.execute("UPDATE farmer_profiles SET is_otp_verified = 1 WHERE username = ?", (username_clean,))
            conn.commit()
            conn.close()
            return {"status": "success", "message": "Identity validation step approved successfully!"}
        else:
            conn.close()
            return {"status": "error", "message": "Invalid code token sequence entered. Re-check sandbox environment hint values."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# --- TELEMETRY TRACKING API ENDPOINTS ---

@app.post("/save-log")
def save_user_log(request: LogRequest):
    try:
        conn = sqlite3.connect("farming_assistant.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO activity_logs (username, feature_type, query_details) VALUES (?, ?, ?)",
            (request.username, request.feature_type, request.query_details)
        )
        conn.commit()
        conn.close()
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


# --- CORE ASSISTANT ROUTING MATCHES ---

@app.get("/", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
def read_root():
    return FileResponse("static/index.html")

# Static Multi-Page Module Router Layers
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
    save_verified_log(request.username, "AI Chatbot", f"Asked: {request.message[:40]}...")
    return {"reply": reply}


@app.post("/diagnose")
async def diagnose(file: UploadFile = File(...), lang: str = "en", username: str = "Nithish"):
    image_bytes = await file.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    if lang == "ta":
        prompt_text = (
            "நீங்கள் இந்திய விவசாயிகளுக்கு உதவும் ஒரு நிபுணர் வேளாண் உதவியாளர். "
            "இந்த பயிர் அல்லது தாவர இலையின் புகைப்படத்தை பார்த்து தமிழில் மட்டும் பதிலளிக்கவும். "
            "கண்டறியவும்: 1. நோய் அல்லது பூச்சி பிரச்சனை என்னவென்று 2. எவ்வளவு தீவிரமாக உள்ளது "
            "3. உள்ளூரில் கிடைக்கும் மலிவான முறைகளில் எளிய சிகிச்சை படிகள். "
            "எளிமையாகவும் தொழில்நுட்ப வார்த்தைகள் இல்லாமலும் எழுதவும்."
        )
    else:
        prompt_text = (
            "You are an expert agricultural assistant helping Indian farmers. "
            "Look at this photo of a crop or plant leaf and respond in English only. "
            "Identify: 1. The likely disease or pest problem if any 2. How serious it looks "
            "3. Simple practical treatment steps using affordable locally available methods. "
            "Keep it simple and avoid technical jargon."
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
    save_verified_log(username, "Crop Diagnosis", f"Uploaded plant health image: {file.filename}")
    return {"diagnosis": diagnosis}


@app.get("/weather")
def get_weather(city: str, lang: str = "en", username: str = "Nithish"):
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

    save_verified_log(username, "Live Weather", f"Checked weather parameters for {data['name']}")

    return {
        "city": data["name"],
        "temperature": temp,
        "feels_like": data["main"]["feels_like"],
        "humidity": humidity,
        "description": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"],
        "farming_tip": tip
    }


@app.get("/forecast")
def get_forecast(city: str, lang: str = "en", username: str = "Nithish"):
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
                advice = "லேசான மழை எதிர்பார்க்கப்படுகிறது — பயிர்களுக்கு நல்லது, நீர்பாசனம் நிறுத்தவும்."
            elif avg_temp > 38:
                advice = "மிகவும் சூடான நாள் — காலையிலோ மாலையிலோ பயிர்களுக்கு தண்ணீர் பாய்ச்சவும்."
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

    save_verified_log(username, "Weather Forecast", f"Looked up a 7-day outlook for {data['city']['name']}")
    return {"city": data["city"]["name"], "forecast": forecast}


@app.get("/market")
def get_market_prices(crop: str, state: str = "Tamil Nadu", lang: str = "en", username: str = "Nithish"):
    if lang == "ta":
        prompt = f"""நீங்கள் இந்தியாவிற்கான வேளாண் சந்தை விலை நிபுணர்.\n{state}, இந்தியாவில் {crop} பயிரின் தற்போதைய மொத்த சந்தை விலைகளை தமிழில் கொடுக்கவும்.\n\nஇந்த சரியான வடிவத்தில் பதில் கொடுக்கவும் (வேறு எந்த உரையும் வேண்டாம்):\nபயிர்: {crop}\nமாநிலம்: {state}\nகிலோ விலை: ரூ [X]/கிலோ\nகுவிண்டால் விலை: ரூ [X]/குவிண்டால்\nகுறைந்தபட்ச விலை: ரூ [X]/கிலோ\nஅதிகபட்ச விலை: ரூ [X]/கிலோ\nசிறந்த சந்தைகள்: [{state}வில் 2-3 சந்தை பெயர்கள்]\nவிலை போக்கு: [அதிகரிக்கிறது/குறக்கிறது/நிலையானது]\nவிவசாயி குறிப்பு: [இந்த பயிரை விற்பது பற்றிய ஒரு நடைமுறை குறிப்பு]\n\nயதார்த்தமான தற்போதைய இந்திய சந்தை விலைகளை பயன்படுத்தவும்."""
        system_msg = "நீங்கள் ஒரு இந்திய வேளாண் சந்தை விலை நிபுணர். எப்போதும் கோரிய சரியான வடிவத்தில் தமிழில் பதில் கொடுக்கவும்."
    else:
        prompt = f"""You are an agricultural market price expert for India.\nProvide current approximate wholesale market prices for {crop} in {state}, India.\n\nGive the response in this exact format (no extra text):\nCrop: {crop}\nState: {state}\nPrice per Kg: Rs [X]/kg\nPrice per Quintal: Rs [X]/quintal\nMin Price: Rs [X]/kg\nMax Price: Rs [X]/kg\nBest Markets: [2-3 market names in {state}]\nPrice Trend: [Rising/Falling/Stable]\nFarmer Tip: [one practical tip about selling this crop]\n\nUse realistic current Indian market prices. Keep it brief and practical."""
        system_msg = "You are an Indian agricultural market price expert. Always respond in the exact format requested. No extra explanation."

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ],
        max_tokens=512
    )
    
    prices = strip_think_tags(response.choices[0].message.content)
    save_verified_log(username, "Market Prices", f"Checked marketplace value for {crop} ({state})")
    return {"prices": prices}


@app.get("/soil")
def get_soil_tips(crop: str, season: str, soil_type: str, lang: str = "en", username: str = "Nithish"):
    if lang == "ta":
        prompt = f"""நீங்கள் இந்திய விவசாயிகளுக்கான நிபுணர் வேளாண் ஆலோசகர்.\nஇதற்கான நடைமுறை மண் தயாரிப்பு மற்றும் பயிர் வளர்ப்பு குறிப்புகளை தமிழில் கொடுக்கவும்:\nபயிர்: {crop}\nபருவம்: {season}\nமண் வகை: {soil_type}\n\nஇந்த வடிவத்தில் பதில் கொடுக்கவும்:\nபயிர்: {crop}\nபருவம்: {season}\nமண் வகை: {soil_type}\n\nமண் தயாரிப்பு:\n[மண்ணை தயாரிக்க 3-4 எளிய படிகள்]\n\nஉர குறிப்புகள்:\n[என்ன உரங்கள் பயன்படுத்த வேண்டும், ஒரு ஏக்கருக்கு எவ்வளவு, எளிய வார்த்தைகளில்]\n\nநீர்பாசன வழிகாட்டி:\n[எவ்வளவு அடிக்கடி தண்ணீர் கொடுக்க வேண்டும், எவ்வளவு]\n\nசிறந்த நடவு நேரம்:\n[இந்த பருவத்தில் நடவு செய்ய சரியான மாதங்கள்]\n\nஎதிர்பார்க்கப்படும் அறுவடை:\n[அறுவடைக்கு எத்தனை நாட்கள்/மாதங்கள்]\n\nவிவசாயி குறிப்பு:\n[இந்த பயிர் மற்றும் மண் சேர்க்கைக்கான ஒரு முக்கியமான குறிப்பு]"""
        system_msg = "நீங்கள் ஒரு நிபுணர் இந்திய வேளாண் ஆலோசகர். நடைமுறை, எளிய ஆலோசனை கொடுக்கவும். எப்போதும் கோரிய சரியான வடிவத்தில் தமிழில் பதில் கொடுக்கவும்."
    else:
        prompt = f"""You are an expert agricultural advisor for Indian farmers.\nGive practical soil preparation and crop growing tips for:\nCrop: {crop}\nSeason: {season}\nSoil Type: {soil_type}\n\nGive the response in this format:\nCrop: {crop}\nSeason: {season}\nSoil Type: {soil_type}\n\nSoil Preparation:\n[3-4 simple steps to prepare the soil]\n\nFertilizer Tips:\n[what fertilizers to use, how much per acre, in simple terms]\n\nWatering Guide:\n[how often to water, how much]\n\nBest Planting Time:\n[exact months to plant in this season]\n\nExpected Harvest:\n[how many days/months to harvest]\n\nFarmer Tip:\n[one important tip specific to this crop and soil combination]\n\nKeep everything simple and practical for a farmer with no technical background."""
        system_msg = "You are an expert Indian agricultural advisor. Give practical, simple advice. Always follow the exact format requested."

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024
    )
    
    tips = strip_think_tags(response.choices[0].message.content)
    save_verified_log(username, "Soil Advisory", f"Requested optimization guidelines for {crop} in {soil_type}")
    return {"tips": tips}


@app.get("/pest")
def get_pest_alerts(crop: str, state: str, season: str, lang: str = "en", username: str = "Nithish"):
    if lang == "ta":
        prompt = f"""நீங்கள் இந்திய விவசாயிகளுக்கான நிபுணர் பூச்சி மேலாண்மை ஆலோசகர்.\nஇதற்கான பூச்சி மற்றும் நோய் எச்சரிக்கைகளை தமிழில் கொடுக்கவும்:\nபயிர்: {crop}\nமாநிலம்/பகுதி: {state}\nபருவம்: {season}\n\nஇந்த வடிவத்தில் பதில் கொடுக்கவும்:\n\nபயிர்: {crop}\nபகுதி: {state}\nபருவம்: {season}\n\nஇந்த பருவத்தில் பொதுவான பூச்சிகள்:\n1. [பூச்சி பெயர்] — [எப்படி தெரியும், என்ன சேதம் செய்யும்]\n2. [பூச்சி பெயர்] — [எப்படி தெரியும், என்ன சேதம் செய்யும்]\n3. [பூச்சி பெயர்] — [எப்படி தெரியும், என்ன சேதம் செய்யும்]\n\nகவனிக்க வேண்டிய எச்சரிக்கை அறிகுறிகள்:\n[விவசாயி வயலில் கவனிக்க வேண்டிய 3 முன்கூட்டிய அறிகுறிகள்]\n\nஇயற்கை சிகிச்சை (மலிவான, உள்ளூர் முறைகள்):\n[உள்ளூரில் கிடைக்கும் பொருட்களை பயன்படுத்தி 2-3 மலிவான இயற்கை தீர்வுகள்]\n\nஇரசாயன சிகிச்சை (தீவிமாக இருந்தால்):\n[உள்ளூர் வேளாண் கடைகளில் கிடைக்கும் 1-2 பொதுவான பூச்சிக்கொல்லிகள், அளவுடன்]\n\nதடுப்பு குறிப்புகள்:\n[2-3 எளிய தடுப்பு நடவடிக்கைகள்]"""
        system_msg = "நீங்கள் ஒரு நிபுணர் இந்திய வேளாண் பூச்சி மேலாண்மை ஆலோசகர். நடைமுறை, பிராந்திய குறிப்பிட்ட ஆலோசனை கொடுக்கவும். எப்போதும் கோரிய சரியான வடிவத்தில் தமிழில் பதில் கொடுக்கவும்."
    else:
        prompt = f"""You are an expert pest management advisor for Indian farmers.\nGive pest and disease alerts for:\nCrop: {crop}\nState/Region: {state}\nSeason: {season}\n\nGive the response in this format:\n\nCrop: {crop}\nRegion: {state}\nSeason: {season}\n\nCommon Pests This Season:\n1. [Pest name] — [what it looks like, what damage it causes]\n2. [Pest name] — [what it looks like, what damage it causes]\n3. [Pest name] — [what it looks like, what damage it causes]\n\nWarning Signs to Watch:\n[3 early warning signs a farmer should look for in the field]\n\nOrganic Treatment (cheap, local methods):\n[2-3 affordable organic solutions using locally available materials]\n\nChemical Treatment (if severe):\n[1-2 common pesticides available at local agri shops, with dosage]\n\nPrevention Tips:\n[2-3 simple prevention steps]\n\nKeep everything simple, practical, and specific to {state} farmers."""
        system_msg = "You are an expert Indian agricultural pest management advisor. Give practical, region-specific advice. Follow the exact format requested."

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024
    )
    
    alerts = strip_think_tags(response.choices[0].message.content)
    save_verified_log(username, "Pest Advisory", f"Checked warnings for {crop} during {season}")
    return {"alerts": alerts}


@app.get("/schemes")
def get_schemes(state: str, category: str = "All", lang: str = "en", username: str = "Nithish"):
    if lang == "ta":
        prompt = f"""நீங்கள் இந்திய விவசாயிகளுக்கான ஒரு அரசு திட்ட நிபுணர்.\n{state} மாநிலத்தில் உள்ள விவசாயிகளுக்குக் கிடைக்கும் முக்கிய தற்போதைய அரசு திட்டங்கள் மற்றும் மானியங்களை தமிழில் பட்டியலிடவும்.\nவகைப்பாடு முன்னுரிமை: {category}\n\nஇந்த தெளிவான வடிவத்தில் பதில் கொடுக்கவும்:\nமாநிலம்: {state}\n\n1. [திட்டத்தின் பெயர்]\n- தகுதி: [யாரெல்லாம் விண்ணப்பிக்கலாம்]\n- நன்மைகள்: [எவ்வளவு உதவி அல்லது மானியம் கிடைக்கும்]\n- விண்ணப்பிக்கும் முறை: [எங்கு அல்லது எப்படி விண்ணப்பிக்க வேண்டும்]\n\n2. [திட்டத்தின் பெயர்]\n- தகுதி: [விவரங்கள்]\n- நன்மைகள்: [விவரங்கள்]\n- விண்ணப்பிக்கும் முறை: [விவரங்கள்]\n\nநடைமுறை, தற்போதைய உண்மையான அரசு திட்டங்களை (எ.கா. PM-KISAN, பயிர் காப்பீடு, சொட்டு நீர் பாசன மானியம்) பயன்படுத்தவும்."""
        system_msg = "நீங்கள் ஒரு அரசு திட்ட ஆலோசகர். எப்போதும் எளிய தமிழில், துүзியமான வடிவத்தில் மட்டும் பதிலளிக்கவும்."
    else:
        prompt = f"""You are an expert government schemes advisor for Indian farmers.\nList important current central and state government agricultural schemes or subsidies available in the state of {state}.\nCategory preference: {category}\n\nProvide the response in this structured format:\nState: {state}\n\n1. [Scheme Name]\n- Eligibility: [Who can apply]\n- Benefits: [Financial aid, loan or subsidy amounts]\n- How to Apply: [Where to apply or official procedure]\n\n2. [Scheme Name]\n- Eligibility: [Details]\n- Benefits: [Details]\n- How to Apply: [Details]\n\nUse authentic, existing Indian welfare initiatives (e.g., PM-KISAN, Fasal Bima Yojana, micro-irrigation subsidies). Keep it simple and clear."""
        system_msg = "You are an Indian government scheme advisor. Always respond in the exact format requested with no extra chat."

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024
    )
    
    schemes = strip_think_tags(response.choices[0].message.content)
    save_verified_log(username, "Govt Schemes", f"Searched programs inside {state} matching {category}")
    return {"schemes": schemes}

# Explicit mount initialization rule ordering matches production specifications
app.mount("/static", StaticFiles(directory="static"), name="static")