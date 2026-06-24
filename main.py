from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from groq import Groq
import base64
import os
import re
from dotenv import load_dotenv
import requests

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


def strip_think_tags(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


class ChatRequest(BaseModel):
    message: str
    lang: str = "en"


@app.get("/")
def read_root():
    return FileResponse("static/index.html")


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
    return {"reply": strip_think_tags(response.choices[0].message.content)}


@app.post("/diagnose")
async def diagnose(file: UploadFile = File(...), lang: str = "en"):
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
    return {"diagnosis": strip_think_tags(response.choices[0].message.content)}


@app.get("/weather")
def get_weather(city: str, lang: str = "en"):
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
def get_forecast(city: str, lang: str = "en"):
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

    return {"city": data["city"]["name"], "forecast": forecast}


@app.get("/market")
def get_market_prices(crop: str, state: str = "Tamil Nadu", lang: str = "en"):
    if lang == "ta":
        prompt = f"""நீங்கள் இந்தியாவிற்கான வேளாண் சந்தை விலை நிபுணர்.
{state}, இந்தியாவில் {crop} பயிரின் தற்போதைய மொத்த சந்தை விலைகளை தமிழில் கொடுக்கவும்.

இந்த சரியான வடிவத்தில் பதில் கொடுக்கவும் (வேறு எந்த உரையும் வேண்டாம்):
பயிர்: {crop}
மாநிலம்: {state}
கிலோ விலை: ரூ [X]/கிலோ
குவிண்டால் விலை: ரூ [X]/குவிண்டால்
குறைந்தபட்ச விலை: ரூ [X]/கிலோ
அதிகபட்ச விலை: ரூ [X]/கிலோ
சிறந்த சந்தைகள்: [{state}வில் 2-3 சந்தை பெயர்கள்]
விலை போக்கு: [அதிகரிக்கிறது/குறைகிறது/நிலையானது]
விவசாயி குறிப்பு: [இந்த பயிரை விற்பது பற்றிய ஒரு நடைமுறை குறிப்பு]

யதார்த்தமான தற்போதைய இந்திய சந்தை விலைகளை பயன்படுத்தவும்."""
        system_msg = "நீங்கள் ஒரு இந்திய வேளாண் சந்தை விலை நிபுணர். எப்போதும் கோரிய சரியான வடிவத்தில் தமிழில் பதில் கொடுக்கவும்."
    else:
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
        system_msg = "You are an Indian agricultural market price expert. Always respond in the exact format requested. No extra explanation."

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ],
        max_tokens=512
    )
    return {"prices": strip_think_tags(response.choices[0].message.content)}


@app.get("/soil")
def get_soil_tips(crop: str, season: str, soil_type: str, lang: str = "en"):
    if lang == "ta":
        prompt = f"""நீங்கள் இந்திய விவசாயிகளுக்கான நிபுணர் வேளாண் ஆலோசகர்.
இதற்கான நடைமுறை மண் தயாரிப்பு மற்றும் பயிர் வளர்ப்பு குறிப்புகளை தமிழில் கொடுக்கவும்:
பயிர்: {crop}
பருவம்: {season}
மண் வகை: {soil_type}

இந்த வடிவத்தில் பதில் கொடுக்கவும்:
பயிர்: {crop}
பருவம்: {season}
மண் வகை: {soil_type}

மண் தயாரிப்பு:
[மண்ணை தயாரிக்க 3-4 எளிய படிகள்]

உர குறிப்புகள்:
[என்ன உரங்கள் பயன்படுத்த வேண்டும், ஒரு ஏக்கருக்கு எவ்வளவு, எளிய வார்த்தைகளில்]

நீர்பாசன வழிகாட்டி:
[எவ்வளவு அடிக்கடி தண்ணீர் கொடுக்க வேண்டும், எவ்வளவு]

சிறந்த நடவு நேரம்:
[இந்த பருவத்தில் நடவு செய்ய சரியான மாதங்கள்]

எதிர்பார்க்கப்படும் அறுவடை:
[அறுவடைக்கு எத்தனை நாட்கள்/மாதங்கள்]

விவசாயி குறிப்பு:
[இந்த பயிர் மற்றும் மண் சேர்க்கைக்கான ஒரு முக்கியமான குறிப்பு]"""
        system_msg = "நீங்கள் ஒரு நிபுணர் இந்திய வேளாண் ஆலோசகர். நடைமுறை, எளிய ஆலோசனை கொடுக்கவும். எப்போதும் கோரிய சரியான வடிவத்தில் தமிழில் பதில் கொடுக்கவும்."
    else:
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
        system_msg = "You are an expert Indian agricultural advisor. Give practical, simple advice. Always follow the exact format requested."

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024
    )
    return {"tips": strip_think_tags(response.choices[0].message.content)}


@app.get("/pest")
def get_pest_alerts(crop: str, state: str, season: str, lang: str = "en"):
    if lang == "ta":
        prompt = f"""நீங்கள் இந்திய விவசாயிகளுக்கான நிபுணர் பூச்சி மேலாண்மை ஆலோசகர்.
இதற்கான பூச்சி மற்றும் நோய் எச்சரிக்கைகளை தமிழில் கொடுக்கவும்:
பயிர்: {crop}
மாநிலம்/பகுதி: {state}
பருவம்: {season}

இந்த வடிவத்தில் பதில் கொடுக்கவும்:

பயிர்: {crop}
பகுதி: {state}
பருவம்: {season}

இந்த பருவத்தில் பொதுவான பூச்சிகள்:
1. [பூச்சி பெயர்] — [எப்படி தெரியும், என்ன சேதம் செய்யும்]
2. [பூச்சி பெயர்] — [எப்படி தெரியும், என்ன சேதம் செய்யும்]
3. [பூச்சி பெயர்] — [எப்படி தெரியும், என்ன சேதம் செய்யும்]

கவனிக்க வேண்டிய எச்சரிக்கை அறிகுறிகள்:
[விவசாயி வயலில் கவனிக்க வேண்டிய 3 முன்கூட்டிய அறிகுறிகள்]

இயற்கை சிகிச்சை (மலிவான, உள்ளூர் முறைகள்):
[உள்ளூரில் கிடைக்கும் பொருட்களை பயன்படுத்தி 2-3 மலிவான இயற்கை தீர்வுகள்]

இரசாயன சிகிச்சை (தீவிரமாக இருந்தால்):
[உள்ளூர் வேளாண் கடைகளில் கிடைக்கும் 1-2 பொதுவான பூச்சிக்கொல்லிகள், அளவுடன்]

தடுப்பு குறிப்புகள்:
[2-3 எளிய தடுப்பு நடவடிக்கைகள்]"""
        system_msg = "நீங்கள் ஒரு நிபுணர் இந்திய வேளாண் பூச்சி மேலாண்மை ஆலோசகர். நடைமுறை, பிராந்திய குறிப்பிட்ட ஆலோசனை கொடுக்கவும். எப்போதும் கோரிய சரியான வடிவத்தில் தமிழில் பதில் கொடுக்கவும்."
    else:
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
        system_msg = "You are an expert Indian agricultural pest management advisor. Give practical, region-specific advice. Follow the exact format requested."

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024
    )
    return {"alerts": strip_think_tags(response.choices[0].message.content)}