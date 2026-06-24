\# 🌾 AI-Powered Personal Farming Assistant



A mobile-friendly web app built for Indian farmers to get AI-powered farming help in English and Tamil.



\## 🔗 Live Demo

👉 \*\*https://farming-assistant-fxvg.onrender.com\*\*



> Hosted on Render — free tier, may take 30–60 seconds to wake up on first visit.



\## ✨ Features



| Feature | Description |

|---|---|

| 💬 Ask a Question | AI farming Q\&A in English \& Tamil with voice input |

| 📷 Plant Disease Diagnosis | Upload crop photo for instant disease detection |

| ☀️ Weather | Live weather data with farming tips |

| 🌧️ Rain Forecast | 7-day rain prediction with daily farming advice |

| 📊 Market Prices | Crop wholesale prices by state (Rs/kg \& Rs/quintal) |

| 🌱 Soil Tips | Soil prep \& fertilizer guide by crop, season, soil type |

| 🐛 Pest Alert | Region-specific pest warnings with organic \& chemical treatment |



\## 🛠️ Tech Stack



\- \*\*Backend:\*\* FastAPI (Python)

\- \*\*AI Models:\*\* Groq API (LLaMA 3.3 70B, Qwen Vision)

\- \*\*Weather:\*\* OpenWeatherMap API

\- \*\*Frontend:\*\* HTML, CSS, JavaScript (mobile-first)

\- \*\*Deployment:\*\* Render



\## 🚀 Run Locally



```bash

git clone https://github.com/rnithish18/farming-assistant

cd farming-assistant

python -m venv venv

venv\\Scripts\\activate

pip install -r requirements.txt

```



Create a `.env` file:

```

GROQ\_API\_KEY=your\_key\_here

OPENWEATHER\_API\_KEY=your\_key\_here

```



```bash

uvicorn main:app --reload

```



Open http://127.0.0.1:8000



\## ☁️ Deploy on Render



🌐 \*\*Live App:\*\* https://farming-assistant-fxvg.onrender.com



1\. Push your code to GitHub

2\. Go to https://render.com and click \*\*New → Web Service\*\*

3\. Connect your GitHub repo

4\. Set these settings:

&#x20;  - \*\*Build Command:\*\* `pip install -r requirements.txt`

&#x20;  - \*\*Start Command:\*\* `uvicorn main:app --host 0.0.0.0 --port $PORT`

&#x20;  - \*\*Environment:\*\* Python 3

5\. Add environment variables in Render dashboard:

&#x20;  - `GROQ\_API\_KEY` → your Groq API key

&#x20;  - `OPENWEATHER\_API\_KEY` → your OpenWeatherMap API key

6\. Click \*\*Deploy\*\* — your app will be live in 2-3 minutes



\## 📁 Project Structure

farming-assistant/

├── main.py              # FastAPI backend (all endpoints)

├── requirements.txt     # Python dependencies

├── .env                 # API keys (not uploaded to GitHub)

└── static/

├── index.html       # Home page (7 feature cards)

├── chat.html        # Ask a Question + Tamil + Voice

├── diagnose.html    # Plant disease diagnosis

├── weather.html     # Current weather

├── forecast.html    # 7-day rain forecast

├── market.html      # Crop market prices

├── soil.html        # Soil tips by season

└── pest.html        # Pest alerts by region

\## 👨‍💻 Built By



Nithish R — AI \& Full Stack Developer



