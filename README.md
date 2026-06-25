# 🌾 Farming AI Assistant

An AI-powered farming assistant built for Indian farmers to get instant help with crops, weather, market prices, and more — in English and Tamil.

🔗 **Live Demo:** https://farming-assistant-fxvg.onrender.com

---

## 📱 Features

| Feature | Description |
|--------|-------------|
| 💬 AI Chat | Ask farming questions in English or Tamil with voice input |
| 📸 Crop Diagnosis | Upload a plant photo to detect diseases instantly |
| ☀️ Live Weather | Real-time weather with farming tips for your city |
| 🌧️ Rain Forecast | 7-day rain prediction with irrigation advice |
| 📊 Market Prices | Wholesale crop prices in Rs/kg and Rs/quintal |
| 🌱 Soil Advisory | Soil prep and fertilizer tips by crop and season |
| 🐛 Pest Alerts | Region-specific pest warnings with organic and chemical fixes |
| 📋 Govt Schemes | Central and state farming subsidies and loan schemes |
| 🔐 Registration | Secure farmer login with real Email OTP verification |

---

## 🛠️ Tech Stack

**Backend**
- Python + FastAPI
- Groq API (LLaMA 3.3 70B for chat, LLaMA 4 Scout for image diagnosis)
- OpenWeatherMap API (weather + forecast)
- Gmail SMTP (Email OTP)
- SQLite (activity logs + farmer profiles)

**Frontend**
- HTML, CSS, JavaScript (no framework)
- Web Speech API (voice input)
- Mobile-friendly responsive design

**Deployment**
- Render (live hosting)
- GitHub (version control)

---

## 🚀 Getting Started Locally

### 1. Clone the repository
```bash
git clone https://github.com/rnithish18/farming-assistant.git
cd farming-assistant
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create .env file

GROQ_API_KEY=your_groq_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
GMAIL_ADDRESS=your_gmail@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password

### 5. Run the server
```bash
uvicorn main:app --reload
```

### 6. Open in browser

http://127.0.0.1:8000

---

## 🔑 API Keys Required

| Service | Purpose | Free? |
|---------|---------|-------|
| [Groq](https://console.groq.com) | AI chat and image diagnosis | ✅ Free |
| [OpenWeatherMap](https://openweathermap.org/api) | Weather and forecast | ✅ Free |
| [Gmail](https://myaccount.google.com/apppasswords) | Email OTP sending | ✅ Free |

---

## 📂 Project Structure

farming-assistant/

├── main.py              # FastAPI backend with all endpoints
├── requirements.txt     # Python dependencies
├── .env                 # API keys (not committed)
├── farming_assistant.db # SQLite database (auto-created)
└── static/
├── index.html       # Home dashboard
├── register.html    # Farmer registration + OTP
├── chat.html        # AI chat with Tamil + voice
├── diagnose.html    # Crop disease diagnosis
├── weather.html     # Live weather
├── forecast.html    # 7-day rain forecast
├── market.html      # Market prices
├── soil.html        # Soil advisory
├── pest.html        # Pest alerts
└── schemes.html     # Government schemes
---

## 📸 Screenshots

> Home dashboard with all 8 features, farmer registration with Email OTP, AI chat in Tamil, crop disease diagnosis, 7-day rain forecast with farming advice.

---

## 👨‍💻 Developer

**R Nithish**
- GitHub: [@rnithish18](https://github.com/rnithish18)
- Project built as a portfolio project for Indian agriculture

---

## 📄 License

MIT License — free to use and modify.
