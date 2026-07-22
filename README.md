# 🌾 AI-Powered Personal Farming Assistant

A bilingual (English/Tamil), voice-enabled web platform that gives Indian farmers instant, AI-driven agricultural advice — crop diagnosis, weather, market prices, irrigation planning, government schemes, financial tracking, and peer/AI community support — with no mandatory sign-up required.

Built as an independent student project by **Nithish**, B.E. Computer Science and Engineering, V.S.B Engineering College, Karur, Tamil Nadu.
live link:https://farming-assistant-fxvg.onrender.com/static/index.html
---

## ✨ Features

| # | Module | Description |
|---|--------|-------------|
| 1 | 💬 Conversational Chat | Open-ended farming questions, text or voice, English/Tamil |
| 2 | 📸 Crop Diagnosis | Vision-model analysis of an uploaded leaf photo for disease/pest ID |
| 3 | ☀️ Live Weather | Current conditions + farming recommendation |
| 4 | 🌧️ 7-Day Rain Forecast | Day-by-day irrigation/spraying guidance |
| 5 | 📊 Market Prices | LLM-estimated wholesale price ranges by crop and state |
| 6 | 🌱 Soil Advisory | Preparation, fertilizer, and watering guidance |
| 7 | 🐛 Pest Alerts | Region- and season-specific pest and treatment guidance |
| 8 | 📋 Government Schemes | State-wise subsidy and loan scheme listing |
| 9 | 📅 Crop Calendar | Month-by-month sowing-to-harvest timeline |
| 10 | 🧪 Fertilizer Calculator | NPK quantity estimate from land size, soil, growth stage |
| 11 | 🌾 Crop Recommendation | Ranked crop suggestions from soil, season, water availability |
| 12 | 📈 Yield Prediction | AI-estimated yield range with confidence caveat |
| 13 | 💧 Irrigation Scheduler | Watering frequency/quantity plan by crop stage, soil, method |
| 14 | 💰 Expense Tracker | Income/expense logging with running profit/loss |
| 15 | 🗨️ Community Q&A | Farmer-to-farmer Q&A with optional AI-generated answers |

### Account & Platform Features
- **Three access tiers** — registered (email + OTP verified), guest (username only), and no-account/anonymous
- **Voice input & spoken read-back** across nearly every module (Web Speech API)
- **Dark mode**, profile photo upload, and per-user activity history
- **CSV and bilingual PDF export** of activity history (Tamil-safe via HTML-to-image rendering)
- **Self-service account deletion**, password-confirmed for registered users, cascading across all stored data
- **Owner-oversight email alerts** on every registration, login, and account deletion
- **Community broadcast notifications** — every registered user is emailed when a new question is posted

---

## 🏗️ Architecture

Browser (HTML/CSS/JS, Web Speech API)
│  Fetch API
▼
FastAPI backend (Python)
├── Groq API  → LLaMA 3.3 70B (text) / LLaMA 4 Scout (vision)
├── OpenWeatherMap API → current + forecast weather
├── Brevo Email API (HTTPS) → OTP, owner alerts, community broadcasts
└── MongoDB Atlas → users, activity logs, expenses, community posts

Deployed on **Render** with continuous deployment from this GitHub repository — every push to `main` triggers an automatic rebuild.

---

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI, Pydantic, bcrypt, PyMongo
- **Frontend:** Vanilla HTML/CSS/JavaScript (no build step), Web Speech API, jsPDF, html2canvas
- **Database:** MongoDB Atlas
- **AI Inference:** Groq (LLaMA 3.3 70B Versatile, LLaMA 4 Scout 17B)
- **Weather Data:** OpenWeatherMap
- **Email:** Brevo Transactional Email API
- **Hosting:** Render (free tier, continuous deployment)

---

## ⚙️ Environment Variables

Create a `.env` file locally (never commit this) or set these in Render → Environment:

GROQ_API_KEY=_groq_api_key
OPENWEATHER_API_KEY=_openweathermap_api_key
MONGODB_URI=_mongodb_atlas_connection_string
BREVO_API_KEY=_brevo_api_key
SENDER_EMAIL=_verified_sender_email
OWNER_EMAIL=_email_for_admin_alerts

> **Note:** Email is sent via Brevo's HTTPS API, not SMTP. Most free-tier hosts (including Render) block outbound SMTP ports (25/465/587), so the app uses `https://api.brevo.com/v3/smtp/email` on port 443 instead.

---

## 🚀 Running Locally

```bash
git clone https://github.com/<your-username>/farming-assistant.git
cd farming-assistant

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

# create your .env file with the variables listed above

uvicorn main:app --reload
```

Visit `http://127.0.0.1:8000` in your browser.

---

## 📦 Deployment (Render)

1. Push this repository to GitHub.
2. On [Render](https://render.com), create a new **Web Service** and connect the repo.
3. Set the build command: `pip install -r requirements.txt`
4. Set the start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add all environment variables listed above under **Environment**.
6. Deploy — every future `git push origin main` auto-redeploys.

---

## 📁 Project Structure

├── main.py                  # FastAPI backend — all routes and logic
├── requirements.txt
├── static/
│   ├── index.html            # Dashboard
│   ├── login.html / register.html
│   ├── profile.html          # Account info, photo, password, delete account
│   ├── chat.html
│   ├── diagnose.html
│   ├── weather.html / forecast.html
│   ├── market.html
│   ├── soil.html / pest.html
│   ├── schemes.html
│   ├── calendar.html
│   ├── fertilizer.html
│   ├── expenses.html
│   ├── recommend.html
│   ├── yield.html
│   ├── irrigation.html
│   └── community.html
└── README.md

---

## 📄 Research Paper

A full academic write-up of the system design, architecture, evaluation, and limitations is included:
**`AI_Powered_Personal_Farming_Assistant_Paper.docx`**

---

## ⚠️ Limitations

- Advisory outputs (fertilizer, yield, irrigation, market prices) are general-purpose LLM estimates, not validated agronomic models.
- Crop diagnosis uses a general vision-language model, not a disease-specific classifier.
- Requires an active internet connection throughout.
- Community broadcast emails scale linearly with registered users per question — batching/digesting needed at larger scale.
- Account deletion is immediate and irreversible.
- Evaluation to date is qualitative and developer-conducted; no farmer field trial has been performed yet.

---

## 🙏 Acknowledgments

Built using freely accessible tiers of FastAPI, MongoDB Atlas, Groq, OpenWeatherMap, and Brevo — made possible as an independent student project.

---

## 👤 Author

**Nithish**
B.E. Computer Science and Engineering, 3rd Year
V.S.B Engineering College, Karur, Tamil Nadu, India

---

## 📜 License

This project is submitted as academic coursework. Contact the author before reuse or redistribution.
