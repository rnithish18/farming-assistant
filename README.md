# 🌾 Farming AI Assistant

An AI-powered farming assistant built for Indian farmers to get instant help with crops, weather, market prices, expenses, and more — in English and Tamil, with voice support throughout.

🔗 **Live Demo:** https://farming-assistant-fxvg.onrender.com

---

## 📱 Features

| Feature | Description |
|---------|-------------|
| 💬 AI Chat | Ask farming questions in English or Tamil with voice input |
| 📸 Crop Diagnosis | Upload a plant photo to detect diseases instantly |
| ☀️ Live Weather | Real-time weather with farming tips for your city |
| 🌧️ Rain Forecast | 7-day rain prediction with irrigation advice |
| 📊 Market Prices | Wholesale crop prices in Rs/kg and Rs/quintal |
| 🌱 Soil Advisory | Soil prep and fertilizer tips by crop and season |
| 🐛 Pest Alerts | Region-specific pest warnings with organic and chemical fixes |
| 📋 Govt Schemes | Central and state farming subsidies and loan schemes |
| 📅 Crop Calendar | Month-by-month planting and harvesting guide |
| 🧪 Fertilizer Calculator | Exact NPK fertilizer quantities for your land and crop |
| 💰 Expense Tracker | Log farming expenses and income, track profit/loss |
| 🌾 Crop Recommendation | AI-suggested best crops for your soil, season, and water |
| 📈 Yield Prediction | AI estimate of expected crop yield |
| 🔐 Authentication | Email OTP registration, login, forgot password, guest login, or use without an account |
| 👤 Profile | Photo upload, activity stats, password management |
| 🌙 Dark Mode | Toggleable dark theme across the dashboard |

Most advisory features support **English/Tamil toggle**, **voice input (mic)**, and **read-aloud (voice reader)** for accessibility.

---

## 🛠️ Tech Stack

**Backend**
- Python + FastAPI
- Groq API (LLaMA 3.3 70B for chat/advisory features, LLaMA 4 Scout for image diagnosis)
- OpenWeatherMap API (weather + forecast)
- Brevo SMTP (Email OTP delivery)
- MongoDB (users, activity logs, expenses)
- bcrypt (password hashing)

**Frontend**
- HTML, CSS, JavaScript (no framework)
- Web Speech API (voice input and text-to-speech)
- Mobile-friendly responsive design

**Deployment**
- Render (live hosting)
- GitHub (version control, auto-deploy on push)

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

GROQ_API_KEY=groq_api_key
OPENWEATHER_API_KEY=openweather_api_key
MONGODB_URI=mongodb_connection_string
BREVO_SMTP_LOGIN=brevo_smtp_login
BREVO_SMTP_KEY=brevo_smtp_key
SENDER_EMAIL=verified_sender_email

### 5. Run the server
```bash
uvicorn main:app --reload
```

### 6. Open in browser

http://127.0.0.1:8000/

---

## 🔑 API Keys / Services Required

| Service | Purpose | Free? |
|---------|---------|-------|
| [Groq](https://console.groq.com) | AI chat, diagnosis, and advisory features | ✅ Free |
| [OpenWeatherMap](https://openweathermap.org/api) | Weather and forecast | ✅ Free |
| [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) | Database (users, logs, expenses) | ✅ Free tier |
| [Brevo](https://www.brevo.com) | Email OTP delivery (SMTP) | ✅ Free (300 emails/day) |

---

## 📂 Project Structure

5. Expense Tracker — in terminal:
notepad static\expenses.html
Select all (Ctrl+A), delete, paste this:
html<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Expense Tracker - Farming Assistant</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background-color: #f4f9f4; color: #1a3d1a; padding-bottom: 40px; }
        header {
            background: linear-gradient(135deg, #2d5e2d, #1b441b);
            color: white; padding: 15px 20px;
            display: flex; align-items: center; gap: 15px;
        }
        header a { color: white; text-decoration: none; font-size: 1.5rem; }
        header h1 { font-size: 1.15rem; flex: 1; }
        .lang-toggle {
            display: flex; background: rgba(255,255,255,0.2);
            border-radius: 20px; overflow: hidden;
        }
        .lang-toggle button {
            background: none; border: none; color: white;
            padding: 6px 12px; font-size: 0.85rem; cursor: pointer;
        }
        .lang-toggle button.active {
            background: white; color: #2d5e2d; font-weight: bold;
        }
        .profile-bar {
            background: #e8f5e9; padding: 10px 20px; text-align: right;
            border-bottom: 1px solid #d0e2d0; font-size: 0.85rem; color: #1b441b;
        }
        .container { max-width: 550px; margin: 20px auto; padding: 0 20px; }

        .summary-grid {
            display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;
            margin-bottom: 20px;
        }
        .summary-card {
            background: white; border-radius: 10px; padding: 14px 10px;
            text-align: center; box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        }
        .summary-card .label { font-size: 0.75rem; color: #666; margin-bottom: 4px; }
        .summary-card .value { font-size: 1.1rem; font-weight: bold; }
        .income-color { color: #2d7d2d; }
        .expense-color { color: #c62828; }
        .profit-color { color: #2d5e2d; }
        .loss-color { color: #c62828; }

        .form-box {
            background: white; border-radius: 12px; padding: 18px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 20px;
        }
        .form-box h3 { color: #2d5e2d; margin-bottom: 12px; font-size: 1rem; }
        .type-toggle { display: flex; gap: 8px; margin-bottom: 12px; }
        .type-toggle button {
            flex: 1; padding: 10px; border: 2px solid #ccc; background: white;
            border-radius: 8px; font-weight: bold; cursor: pointer; color: #666;
        }
        .type-toggle button.active-expense { border-color: #c62828; background: #fde8e8; color: #c62828; }
        .type-toggle button.active-income { border-color: #2d7d2d; background: #e8f5e9; color: #2d7d2d; }

        label { display: block; font-weight: bold; margin-bottom: 4px; color: #333; font-size: 0.85rem; }
        input, select {
            width: 100%; padding: 10px; border: 1.5px solid #ccc;
            border-radius: 8px; font-size: 0.9rem; margin-bottom: 10px; font-family: inherit;
        }
        .input-row { display: flex; gap: 8px; align-items: center; }
        .input-row input { flex: 1; margin-bottom: 0; }
        .mic-btn {
            width: 40px; height: 40px; border-radius: 50%;
            background: #2d5e2d; color: white; border: none;
            font-size: 1.05rem; cursor: pointer; flex-shrink: 0; margin-bottom: 10px;
        }
        .mic-btn.recording { background: #cc0000; animation: pulse 1s infinite; }
        @keyframes pulse { 0%,100%{transform:scale(1);} 50%{transform:scale(1.1);} }
        .voice-status { text-align: center; color: #cc0000; font-size: 0.8rem; margin: -6px 0 10px; min-height: 16px; }

        .btn-row { display: flex; gap: 8px; }
        button.submit-btn {
            flex: 1; padding: 12px; background: #2d5e2d; color: white;
            border: none; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 0.95rem;
        }
        button.submit-btn:hover { background: #1b5e20; }
        button.speak-btn {
            width: 44px; background: #1b441b; color: white; border: none;
            border-radius: 8px; font-size: 1.1rem; cursor: pointer; flex-shrink: 0;
        }
        button.speak-btn.speaking { background: #cc0000; }

        .entry {
            background: white; border-radius: 10px; padding: 12px 14px;
            margin-bottom: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            display: flex; justify-content: space-between; align-items: center;
        }
        .entry-left { flex: 1; }
        .entry-category { font-weight: bold; font-size: 0.95rem; }
        .entry-note { font-size: 0.8rem; color: #778b77; margin-top: 2px; }
        .entry-date { font-size: 0.75rem; color: #aaa; margin-top: 2px; }
        .entry-amount { font-weight: bold; font-size: 1rem; margin-right: 10px; }
        .delete-btn {
            background: none; border: none; color: #c62828; font-size: 1.1rem;
            cursor: pointer; padding: 4px 8px;
        }
        .empty-msg { text-align: center; color: #999; padding: 20px; font-size: 0.9rem; }
        #status-msg { text-align: center; font-weight: bold; font-size: 0.85rem; margin-top: 8px; min-height: 18px; }
        footer {
            text-align: center; margin-top: 30px; padding: 14px;
            font-size: 0.8rem; color: #777;
        }
    </style>
</head>
<body>
    <header>
        <a href="/static/index.html">←</a>
        <h1 id="pageTitle">💰 Expense Tracker</h1>
        <div class="lang-toggle">
            <button id="btnEn" class="active" onclick="setLang('en')">EN</button>
            <button id="btnTa" onclick="setLang('ta')">தமிழ்</button>
        </div>
    </header>

    <div class="profile-bar">👤 Farmer Profile: <b id="farmerName">Guest</b></div>

    <div class="container">
        <div class="summary-grid">
            <div class="summary-card">
                <div class="label" id="lblIncome">Income</div>
                <div class="value income-color" id="totalIncome">₹0</div>
            </div>
            <div class="summary-card">
                <div class="label" id="lblExpenses">Expenses</div>
                <div class="value expense-color" id="totalExpense">₹0</div>
            </div>
            <div class="summary-card">
                <div class="label" id="lblNetProfit">Net Profit</div>
                <div class="value" id="netProfit">₹0</div>
            </div>
        </div>

        <div class="form-box">
            <h3 id="lblAddEntry">Add Entry</h3>
            <div class="type-toggle">
                <button id="btnExpense" class="active-expense" onclick="setType('expense')">➖ <span id="lblExpenseBtn">Expense</span></button>
                <button id="btnIncome" onclick="setType('income')">➕ <span id="lblIncomeBtn">Income</span></button>
            </div>

            <label id="lblCategory">Category:</label>
            <select id="category">
                <option>Seeds</option>
                <option>Fertilizer</option>
                <option>Pesticide</option>
                <option>Labor</option>
                <option>Irrigation</option>
                <option>Equipment</option>
                <option>Transport</option>
                <option>Crop Sale</option>
                <option>Other</option>
            </select>

            <label id="lblAmount">Amount (₹):</label>
            <input type="number" id="amount" placeholder="e.g. 1500" min="1">

            <label id="lblCrop">Crop (optional):</label>
            <input type="text" id="crop" placeholder="e.g. Rice">

            <label id="lblNote">Note (optional):</label>
            <div class="input-row">
                <input type="text" id="note" placeholder="e.g. Bought urea from local shop">
                <button class="mic-btn" id="micBtn" onclick="toggleVoice()">🎤</button>
            </div>
            <div class="voice-status" id="voiceStatus"></div>

            <div class="btn-row">
                <button class="submit-btn" onclick="addEntry()" id="lblAddBtn">Add Entry</button>
                <button class="speak-btn" onclick="toggleSpeak()" id="speakBtn" title="Read summary aloud">🔊</button>
            </div>
            <p id="status-msg"></p>
        </div>

        <h3 style="margin-bottom:10px;color:#2d5e2d;" id="lblRecent">Recent Entries</h3>
        <div id="entriesList"></div>
    </div>

    <footer>Developed by Nithish | Software Engineering Student</footer>

    <script>
        document.getElementById('farmerName').textContent = localStorage.getItem('farmer_username') || 'Guest';

        const username = localStorage.getItem('farmer_username') || 'Anonymous';
        let currentType = 'expense';
        let currentLang = 'en';
        let recognition = null;
        let isRecording = false;
        let synth = window.speechSynthesis;
        let isSpeaking = false;
        let lastEntriesData = null;

        const t = {
            en: {
                title: '💰 Expense Tracker', income: 'Income', expenses: 'Expenses', netProfit: 'Net Profit',
                addEntry: 'Add Entry', expenseBtn: 'Expense', incomeBtn: 'Income', category: 'Category:',
                amount: 'Amount (₹):', crop: 'Crop (optional):', note: 'Note (optional):',
                notePlaceholder: 'e.g. Bought urea from local shop', addBtn: 'Add Entry', recent: 'Recent Entries',
                voiceListening: '🔴 Listening... speak now', voiceDone: '✅ Got it!', empty: 'No entries yet. Add your first one above!'
            },
            ta: {
                title: '💰 செலவு கண்காணிப்பு', income: 'வருமானம்', expenses: 'செலவுகள்', netProfit: 'நிகர லாபம்',
                addEntry: 'உள்ளீடு சேர்க்கவும்', expenseBtn: 'செலவு', incomeBtn: 'வருமானம்', category: 'வகை:',
                amount: 'தொகை (₹):', crop: 'பயிர் (விருப்பம்):', note: 'குறிப்பு (விருப்பம்):',
                notePlaceholder: 'எ.கா. உள்ளூர் கடையில் இருந்து யூரியா வாங்கியது', addBtn: 'சேர்க்கவும்', recent: 'சமீபத்திய உள்ளீடுகள்',
                voiceListening: '🔴 கேட்கிறேன்... இப்போது பேசுங்கள்', voiceDone: '✅ கிடைத்தது!', empty: 'இன்னும் உள்ளீடுகள் இல்லை. மேலே முதலில் சேர்க்கவும்!'
            }
        };

        function setLang(lang) {
            currentLang = lang;
            document.getElementById('pageTitle').textContent = t[lang].title;
            document.getElementById('lblIncome').textContent = t[lang].income;
            document.getElementById('lblExpenses').textContent = t[lang].expenses;
            document.getElementById('lblNetProfit').textContent = t[lang].netProfit;
            document.getElementById('lblAddEntry').textContent = t[lang].addEntry;
            document.getElementById('lblExpenseBtn').textContent = t[lang].expenseBtn;
            document.getElementById('lblIncomeBtn').textContent = t[lang].incomeBtn;
            document.getElementById('lblCategory').textContent = t[lang].category;
            document.getElementById('lblAmount').textContent = t[lang].amount;
            document.getElementById('lblCrop').textContent = t[lang].crop;
            document.getElementById('lblNote').textContent = t[lang].note;
            document.getElementById('note').placeholder = t[lang].notePlaceholder;
            document.getElementById('lblAddBtn').textContent = t[lang].addBtn;
            document.getElementById('lblRecent').textContent = t[lang].recent;
            document.getElementById('btnEn').classList.toggle('active', lang === 'en');
            document.getElementById('btnTa').classList.toggle('active', lang === 'ta');
            localStorage.setItem('app_lang', lang);
            if (lastEntriesData) renderEntries(lastEntriesData);
        }

        const savedLang = localStorage.getItem('app_lang');
        if (savedLang) setLang(savedLang);

        function setType(type) {
            currentType = type;
            document.getElementById('btnExpense').classList.toggle('active-expense', type === 'expense');
            document.getElementById('btnIncome').classList.toggle('active-income', type === 'income');
        }

        function toggleVoice() {
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                alert('Voice input not supported. Please use Chrome.');
                return;
            }
            if (isRecording) { recognition.stop(); return; }
            const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SR();
            recognition.lang = currentLang === 'ta' ? 'ta-IN' : 'en-IN';
            recognition.interimResults = false;
            recognition.onstart = () => {
                isRecording = true;
                document.getElementById('micBtn').classList.add('recording');
                document.getElementById('micBtn').textContent = '⏹';
                document.getElementById('voiceStatus').textContent = t[currentLang].voiceListening;
            };
            recognition.onresult = (e) => {
                document.getElementById('note').value = e.results[0][0].transcript;
                document.getElementById('voiceStatus').textContent = t[currentLang].voiceDone;
            };
            recognition.onend = () => {
                isRecording = false;
                document.getElementById('micBtn').classList.remove('recording');
                document.getElementById('micBtn').textContent = '🎤';
            };
            recognition.onerror = () => {
                isRecording = false;
                document.getElementById('micBtn').classList.remove('recording');
                document.getElementById('micBtn').textContent = '🎤';
                document.getElementById('voiceStatus').textContent = '❌ Could not hear. Try again.';
            };
            recognition.start();
        }

        function toggleSpeak() {
            if (isSpeaking) {
                synth.cancel();
                isSpeaking = false;
                document.getElementById('speakBtn').classList.remove('speaking');
                document.getElementById('speakBtn').textContent = '🔊';
                return;
            }
            if (!lastEntriesData) { alert('No summary to read yet.'); return; }
            const summary = currentLang === 'ta'
                ? `மொத்த வருமானம் ரூபாய் ${lastEntriesData.total_income}. மொத்த செலவு ரூபாய் ${lastEntriesData.total_expense}. நிகர லாபம் ரூபாய் ${lastEntriesData.net_profit}.`
                : `Total income is rupees ${lastEntriesData.total_income}. Total expenses are rupees ${lastEntriesData.total_expense}. Net profit is rupees ${lastEntriesData.net_profit}.`;
            const utterance = new SpeechSynthesisUtterance(summary);
            utterance.lang = currentLang === 'ta' ? 'ta-IN' : 'en-IN';
            utterance.rate = 0.9;
            utterance.onstart = () => {
                isSpeaking = true;
                document.getElementById('speakBtn').classList.add('speaking');
                document.getElementById('speakBtn').textContent = '⏹';
            };
            utterance.onend = () => {
                isSpeaking = false;
                document.getElementById('speakBtn').classList.remove('speaking');
                document.getElementById('speakBtn').textContent = '🔊';
            };
            synth.speak(utterance);
        }

        function renderEntries(data) {
            document.getElementById('totalIncome').textContent = '₹' + data.total_income.toLocaleString('en-IN');
            document.getElementById('totalExpense').textContent = '₹' + data.total_expense.toLocaleString('en-IN');
            const netEl = document.getElementById('netProfit');
            netEl.textContent = '₹' + data.net_profit.toLocaleString('en-IN');
            netEl.className = 'value ' + (data.net_profit >= 0 ? 'profit-color' : 'loss-color');

            const list = document.getElementById('entriesList');
            if (data.entries.length === 0) {
                list.innerHTML = `<div class="empty-msg">${t[currentLang].empty}</div>`;
                return;
            }
            list.innerHTML = data.entries.map(e => `
                <div class="entry">
                    <div class="entry-left">
                        <div class="entry-category">${e.category}${e.crop ? ' — ' + e.crop : ''}</div>
                        ${e.note ? `<div class="entry-note">${e.note}</div>` : ''}
                        <div class="entry-date">${new Date(e.timestamp * 1000).toLocaleDateString('en-IN')}</div>
                    </div>
                    <div class="entry-amount ${e.type === 'income' ? 'income-color' : 'expense-color'}">
                        ${e.type === 'income' ? '+' : '-'}₹${e.amount.toLocaleString('en-IN')}
                    </div>
                    <button class="delete-btn" onclick="deleteEntry(${e.timestamp})">🗑️</button>
                </div>
            `).join('');
        }

        async function loadEntries() {
            try {
                const res = await fetch(`/get-expenses?username=${encodeURIComponent(username)}`);
                const data = await res.json();
                lastEntriesData = data;
                renderEntries(data);
            } catch (e) {
                document.getElementById('entriesList').innerHTML = '<div class="empty-msg">Could not load entries.</div>';
            }
        }

        async function addEntry() {
            const category = document.getElementById('category').value;
            const amount = document.getElementById('amount').value.trim();
            const crop = document.getElementById('crop').value.trim();
            const note = document.getElementById('note').value.trim();

            if (!amount || amount <= 0) { showMsg('Please enter a valid amount.', 'red'); return; }

            try {
                const res = await fetch('/add-expense', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, type: currentType, category, amount, crop, note })
                });
                const data = await res.json();
                if (data.success) {
                    showMsg('Entry added!', 'green');
                    document.getElementById('amount').value = '';
                    document.getElementById('crop').value = '';
                    document.getElementById('note').value = '';
                    loadEntries();
                } else {
                    showMsg(data.message, 'red');
                }
            } catch (e) {
                showMsg('Error: could not reach server.', 'red');
            }
        }

        async function deleteEntry(timestamp) {
            try {
                await fetch('/delete-expense', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, timestamp })
                });
                loadEntries();
            } catch (e) {}
        }

        function showMsg(text, color) {
            const msg = document.getElementById('status-msg');
            msg.textContent = text;
            msg.style.color = color === 'red' ? '#d32f2f' : '#2d5e2d';
            setTimeout(() => { msg.textContent = ''; }, 2500);
        }

        loadEntries();
    </script>
</body>
</html>
Save Ctrl+S, close Notepad.
All 5 done. Restart your server (uvicorn main:app --reload) and check each of the 5 pages loads correctly with the profile bar and footer showing. Send me a screenshot, then push:
git add .
git commit -m "Add farmer profile bar and footer to Crop Calendar, Fertilizer Calculator, Crop Recommendation, Yield Prediction, and Expense Tracker pages"
git push origin mainrecent activity log not work perfect it has all detail and clear history and download optionArchitected feature enhancements for activity logs functionalityArchitected feature enhancements for activity logs functionalityGood addition — let's add a Clear History button and a Download button (CSV export) to the Recent Activity Logs section on the dashboard. This only touches index.html and adds one small backend endpoint, nothing else.
Step 1 — Backend. In your terminal:
notepad main.py
Find:
python@app.get("/get-logs")
def get_user_logs(username: str):
Add this new endpoint right before it:
python@app.post("/clear-logs")
def clear_user_logs(data: dict):
    username = data.get("username", "").strip()
    if not username:
        return {"success": False, "message": "Missing username"}
    db["activity_logs"].delete_many({"username": username})
    return {"success": True, "message": "History cleared"}
Save Ctrl+S, close Notepad.
Step 2 — Frontend. In terminal:
notepad static\index.html
Find this:
html        <div class="history-section">
            <h3 style="margin-bottom: 12px;">🕒 Recent Activity Logs</h3>
            <div id="historyLogs" style="color: #666; font-size: 0.9rem;">Fetching logs...</div>
        </div>
Replace with:
html        <div class="history-section">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px;">
                <h3>🕒 Recent Activity Logs</h3>
                <div style="display:flex;gap:8px;">
                    <button onclick="downloadHistory()" style="padding:6px 12px;background:#2d5e2d;color:white;border:none;border-radius:6px;font-size:0.8rem;cursor:pointer;font-weight:bold;">⬇️ Download</button>
                    <button onclick="clearHistory()" style="padding:6px 12px;background:#c62828;color:white;border:none;border-radius:6px;font-size:0.8rem;cursor:pointer;font-weight:bold;">🗑️ Clear</button>
                </div>
            </div>
            <div id="historyLogs" style="color: #666; font-size: 0.9rem;">Fetching logs...</div>
        </div>
Now find:
javascript        async function loadHistory(name) {
            const container = document.getElementById("historyLogs");
            try {
                const response = await fetch(`/get-logs?username=${encodeURIComponent(name)}`);
                const data = await response.json();
                if (data.history && data.history.length > 0) {
                    container.innerHTML = data.history.map(item => `
                        <div class="history-item">
                            <div>
                                <span class="history-tag">${item.feature}</span>
                                <span>${item.query}</span>
                            </div>
                            <span style="color:#778b77;font-size:0.8rem;">${new Date(item.time * 1000).toLocaleString('en-IN')}</span>
                        </div>
                    `).join('');
                } else {
                    container.textContent = "No activity recorded yet.";
                }
            } catch (err) {
                container.textContent = "Could not fetch activity logs.";
            }
        }
Replace with:
javascript        let lastHistoryData = [];

        async function loadHistory(name) {
            const container = document.getElementById("historyLogs");
            try {
                const response = await fetch(`/get-logs?username=${encodeURIComponent(name)}`);
                const data = await response.json();
                lastHistoryData = data.history || [];
                if (lastHistoryData.length > 0) {
                    container.innerHTML = lastHistoryData.map(item => `
                        <div class="history-item">
                            <div>
                                <span class="history-tag">${item.feature}</span>
                                <span>${item.query}</span>
                            </div>
                            <span style="color:#778b77;font-size:0.8rem;">${new Date(item.time * 1000).toLocaleString('en-IN')}</span>
                        </div>
                    `).join('');
                } else {
                    container.textContent = "No activity recorded yet.";
                }
            } catch (err) {
                container.textContent = "Could not fetch activity logs.";
            }
        }

        function downloadHistory() {
            if (!lastHistoryData || lastHistoryData.length === 0) {
                alert("No activity to download yet.");
                return;
            }
            let csv = "Feature,Details,Date & Time\n";
            lastHistoryData.forEach(item => {
                const date = new Date(item.time * 1000).toLocaleString('en-IN');
                const safeQuery = String(item.query).replace(/"/g, '""');
                csv += `"${item.feature}","${safeQuery}","${date}"\n`;
            });
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `farming_activity_${savedUser}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }

        async function clearHistory() {
            if (!confirm("Clear all your activity history? This cannot be undone.")) return;
            try {
                const res = await fetch('/clear-logs', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: savedUser })
                });
                const data = await res.json();
                if (data.success) {
                    lastHistoryData = [];
                    document.getElementById('historyLogs').textContent = "No activity recorded yet.";
                } else {
                    alert("Could not clear history.");
                }
            } catch (e) {
                alert("Error: could not reach server.");
            }
        }
Save Ctrl+S, close Notepad.
Restart your server (uvicorn main:app --reload), refresh the dashboard, and test both the Download button (should save a CSV file) and Clear button (should ask for confirmation, then wipe the list). Send me a screenshot before we push.<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Farming AI Assistant - Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
         pastedgive me full code without change any working conditionInvestigated logging inconsistencies across application endpointsInvestigated logging inconsistencies across application endpointsHere's the complete index.html with the Download and Clear buttons added, everything else untouched:
In your terminal:
notepad static\index.html
Select all (Ctrl+A), delete, paste this:
html<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Farming AI Assistant - Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background-color: #f4f9f4; color: #1a3d1a;
            transition: background-color 0.3s, color 0.3s;
        }
        body.dark-mode { background-color: #121a12; color: #e0f0e0; }
        body.dark-mode .card { background: #1e2a1e; border-color: #2d3d2d; color: #e0f0e0; }
        body.dark-mode .card p { color: #a0b8a0; }
        body.dark-mode .profile-bar { background: #1a2a1a; border-color: #2d3d2d; }
        body.dark-mode .profile-bar span { color: #c8e6c9; }
        body.dark-mode .history-section { background: #1e2a1e; border-color: #2d3d2d; }
        body.dark-mode .history-item { border-color: #2d3d2d; }
        body.dark-mode .history-tag { background: #2d3d2d; color: #81c784; }
        .theme-toggle {
            background: none; border: 2px solid #2d5e2d; color: #2d5e2d;
            width: 34px; height: 34px; border-radius: 50%; cursor: pointer;
            font-size: 1rem; display: flex; align-items: center; justify-content: center;
        }
        body.dark-mode .theme-toggle { border-color: #81c784; color: #81c784; }
        header {
            background: linear-gradient(135deg, #2d5e2d, #1b441b);
            color: white; padding: 25px 20px; text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        header h1 { font-size: 1.8rem; margin-bottom: 5px; }
        header p { font-size: 0.95rem; opacity: 0.9; }
        .profile-bar {
            background: #e8f5e9; padding: 12px; text-align: center;
            border-bottom: 1px solid #d0e2d0;
            display: flex; justify-content: center; align-items: center; gap: 15px;
        }
        .profile-bar span { font-weight: 600; color: #1b441b; }
        .profile-link {
            color: #2d5e2d; font-weight: 600; text-decoration: none;
        }
        .logout-btn {
            padding: 6px 12px; background: #c62828; color: white;
            border: none; border-radius: 4px; cursor: pointer;
            font-weight: bold; font-size: 0.85rem;
        }
        .logout-btn:hover { background: #b71c1c; }
        .container { max-width: 800px; margin: 30px auto; padding: 0 20px; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
        }
        .card {
            background: white; border-radius: 16px; padding: 20px;
            text-align: center; text-decoration: none; color: #1a3d1a;
            box-shadow: 0 4px 10px rgba(0,0,0,0.04);
            border: 1px solid #e1ebe1;
            transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.3s, border-color 0.3s;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
        }
        .card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(45,94,45,0.12);
            border-color: #2d5e2d;
        }
        .card .icon { font-size: 2.5rem; margin-bottom: 12px; }
        .card h3 { font-size: 1.15rem; margin-bottom: 6px; font-weight: 600; }
        .card p { font-size: 0.85rem; color: #556b55; line-height: 1.4; }
        .history-section {
            background: white; padding: 20px; border-radius: 16px;
            margin-top: 30px; border: 1px solid #e1ebe1;
            box-shadow: 0 4px 10px rgba(0,0,0,0.04);
            transition: background 0.3s, border-color 0.3s;
        }
        .history-item {
            padding: 10px 0; border-bottom: 1px solid #eee;
            font-size: 0.9rem; display: flex;
            justify-content: space-between; align-items: center;
        }
        .history-item:last-child { border-bottom: none; }
        .history-tag {
            background: #e8f5e9; color: #2d5e2d;
            padding: 2px 6px; border-radius: 4px;
            font-weight: bold; font-size: 0.75rem;
            margin-right: 8px; text-transform: uppercase;
        }
        footer {
            text-align: center; margin-top: 40px;
            font-size: 0.85rem; color: #778b77; padding-bottom: 25px;
        }
    </style>
</head>
<body>
    <header>
        <h1 id="welcomeTitle">🌾 Farming AI Assistant</h1>
        <p>Your intelligent companion for smarter, high-yield farming</p>
    </header>

    <div class="profile-bar">
        <img id="headerPhoto" src="" alt="" style="width:32px;height:32px;border-radius:50%;object-fit:cover;border:2px solid #2d5e2d;display:none;vertical-align:middle;">
        <span id="activeUserLabel">Active Profile: Loading...</span>
        <a href="/static/profile.html" class="profile-link">👤 Profile</a>
        <button class="theme-toggle" onclick="toggleTheme()" id="themeBtn">🌙</button>
        <button class="logout-btn" onclick="logOutSession()">Logout</button>
    </div>

    <div class="container">
        <div class="grid">
            <a href="/static/chat.html" class="card">
                <div class="icon">💬</div>
                <h3>Ask a Question</h3>
                <p>Chat with AI assistant in English or தமிழ் via text or voice.</p>
            </a>
            <a href="/static/diagnose.html" class="card">
                <div class="icon">📸</div>
                <h3>Crop Diagnosis</h3>
                <p>Take or upload leaf photos to instantly find plant diseases.</p>
            </a>
            <a href="/static/weather.html" class="card">
                <div class="icon">☀️</div>
                <h3>Live Weather</h3>
                <p>Check temperature, humidity, and real-time smart farming tips.</p>
            </a>
            <a href="/static/forecast.html" class="card">
                <div class="icon">🌧️</div>
                <h3>Rain Forecast</h3>
                <p>Track a 7-day outlook to safely time sprays and irrigation.</p>
            </a>
            <a href="/static/market.html" class="card">
                <div class="icon">📊</div>
                <h3>Market Prices</h3>
                <p>See accurate market wholesale rates and selling trends.</p>
            </a>
            <a href="/static/soil.html" class="card">
                <div class="icon">🌱</div>
                <h3>Soil Advisory</h3>
                <p>Get custom land prep steps and fertilization guides.</p>
            </a>
            <a href="/static/pest.html" class="card">
                <div class="icon">🐛</div>
                <h3>Pest Alerts</h3>
                <p>Identify active risks and explore organic or chemical fixes.</p>
            </a>
            <a href="/static/schemes.html" class="card">
                <div class="icon">📋</div>
                <h3>Govt Schemes</h3>
                <p>Explore central/state farming benefits, loans, and subsidies.</p>
            </a>
            <a href="/static/calendar.html" class="card">
                <div class="icon">📅</div>
                <h3>Crop Calendar</h3>
                <p>Month-by-month planting and harvesting guide for your crop.</p>
            </a>
            <a href="/static/fertilizer.html" class="card">
                <div class="icon">🧪</div>
                <h3>Fertilizer Calculator</h3>
                <p>Get exact NPK fertilizer quantities for your land size and crop.</p>
           </a>
           <a href="/static/expenses.html" class="card">
               <div class="icon">💰</div>
               <h3>Expense Tracker</h3>
               <p>Log farming expenses and income to track your profit or loss.</p>
           </a>
           <a href="/static/recommend.html" class="card">
               <div class="icon">🌾</div>
               <h3>Crop Recommendation</h3>
               <p>Get AI-suggested best crops based on soil, season, and water.</p>
           </a>
           <a href="/static/yield.html" class="card">
               <div class="icon">📈</div>
               <h3>Yield Prediction</h3>
               <p>Get an AI estimate of your expected crop yield.</p>
           </a>
        </div>

        <div class="history-section">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px;">
                <h3>🕒 Recent Activity Logs</h3>
                <div style="display:flex;gap:8px;">
                    <button onclick="downloadHistory()" style="padding:6px 12px;background:#2d5e2d;color:white;border:none;border-radius:6px;font-size:0.8rem;cursor:pointer;font-weight:bold;">⬇️ Download</button>
                    <button onclick="clearHistory()" style="padding:6px 12px;background:#c62828;color:white;border:none;border-radius:6px;font-size:0.8rem;cursor:pointer;font-weight:bold;">🗑️ Clear</button>
                </div>
            </div>
            <div id="historyLogs" style="color: #666; font-size: 0.9rem;">Fetching logs...</div>
        </div>
    </div>

    <footer>
        <p>© 2026 Farming AI Assistant • Designed for Indian Agriculture</p>
        <p style="margin-top:5px;">Developed by Nithish | Software Engineering Student</p>
    </footer>

    <script>
        const savedUser = localStorage.getItem("farmer_username");
        if (!savedUser) {
            window.location.replace("/static/login.html");
        }

        if (localStorage.getItem('theme') === 'dark') {
            document.body.classList.add('dark-mode');
        }

        function toggleTheme() {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            document.getElementById('themeBtn').textContent = isDark ? '☀️' : '🌙';
        }

        document.addEventListener("DOMContentLoaded", () => {
            if (localStorage.getItem('theme') === 'dark') {
                document.getElementById('themeBtn').textContent = '☀️';
            }
            if (savedUser) {
                document.getElementById("welcomeTitle").textContent = `🌾 Welcome back, ${savedUser}!`;
                document.getElementById("activeUserLabel").textContent = `👤 Active Farmer: ${savedUser}`;
                loadHistory(savedUser);
                loadHeaderPhoto(savedUser);
            }
        });

        async function loadHeaderPhoto(name) {
            try {
                const res = await fetch(`/get-photo?username=${encodeURIComponent(name)}`);
                const data = await res.json();
                if (data.success && data.photo) {
                    const img = document.getElementById('headerPhoto');
                    img.src = data.photo;
                    img.style.display = 'inline-block';
                }
            } catch (e) {}
        }

        function logOutSession() {
            localStorage.removeItem("farmer_username");
            window.location.href = "/static/login.html";
        }

        let lastHistoryData = [];

        async function loadHistory(name) {
            const container = document.getElementById("historyLogs");
            try {
                const response = await fetch(`/get-logs?username=${encodeURIComponent(name)}`);
                const data = await response.json();
                lastHistoryData = data.history || [];
                if (lastHistoryData.length > 0) {
                    container.innerHTML = lastHistoryData.map(item => `
                        <div class="history-item">
                            <div>
                                <span class="history-tag">${item.feature}</span>
                                <span>${item.query}</span>
                            </div>
                            <span style="color:#778b77;font-size:0.8rem;">${new Date(item.time * 1000).toLocaleString('en-IN')}</span>
                        </div>
                    `).join('');
                } else {
                    container.textContent = "No activity recorded yet.";
                }
            } catch (err) {
                container.textContent = "Could not fetch activity logs.";
            }
        }

        function downloadHistory() {
            if (!lastHistoryData || lastHistoryData.length === 0) {
                alert("No activity to download yet.");
                return;
            }
            let csv = "Feature,Details,Date & Time\n";
            lastHistoryData.forEach(item => {
                const date = new Date(item.time * 1000).toLocaleString('en-IN');
                const safeQuery = String(item.query).replace(/"/g, '""');
                csv += `"${item.feature}","${safeQuery}","${date}"\n`;
            });
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `farming_activity_${savedUser}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }

        async function clearHistory() {
            if (!confirm("Clear all your activity history? This cannot be undone.")) return;
            try {
                const res = await fetch('/clear-logs', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: savedUser })
                });
                const data = await res.json();
                if (data.success) {
                    lastHistoryData = [];
                    document.getElementById('historyLogs').textContent = "No activity recorded yet.";
                } else {
                    alert("Could not clear history.");
                }
            } catch (e) {
                alert("Error: could not reach server.");
            }
        }
    </script>
</body>
</html>
Save Ctrl+S, close Notepad.
Don't forget the backend piece — make sure you also added the /clear-logs endpoint to main.py from my previous message (right before the /get-logs endpoint). If you haven't done that yet, let me know and I'll resend it.
Restart your server (uvicorn main:app --reload), refresh the dashboard, and test both Download and Clear. One thing worth noting separately: none of our new features (Fertilizer, Crop Calendar, Recommendation, Yield, Expenses) currently write to the activity log — only Chat and a couple of older endpoints do — so the history list may look sparse regardless. That's a separate fix if you want it; let me know after testing this one.from fastapi import FastAPI, UploadFile, File, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional
from groq import Groq
import base64
import os
import re
impopastedgive full main.py code and give comment to push it in the github and render and give me the complete readmein githubThought for 3sThought for 3sHere's the complete main.py with the /clear-logs endpoint added, everything else exactly as it was:Prepare working directoryPrepare working directoryIn your terminal:
notepad main.py
Select all (Ctrl+A), delete, paste this:
pythonfrom fastapi import FastAPI, UploadFile, File, Response, HTTPException
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
    return {"calendar": strip_think_tags(response.choices[0].message.content)}

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
    return {"result": strip_think_tags(response.choices[0].message.content)}

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
    return {"result": strip_think_tags(response.choices[0].message.content)}

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
    return {"result": strip_think_tags(response.choices[0].message.content)}

app.mount("/static", StaticFiles(directory="static"), name="static")
Save Ctrl+S, close Notepad.
Push commands:
git add .
git commit -m "Add clear-logs endpoint; download and clear history buttons on dashboard"
git push origin main
Now let's create the README.Opted for plain text format due to markdown constraintsOpted for plain text format due to markdown constraintsHere's your complete, updated README reflecting all current features. In your terminal:
notepad README.md
Select all (Ctrl+A), delete, paste this:
markdown# 🌾 Farming AI Assistant

An AI-powered farming assistant built for Indian farmers to get instant help with crops, weather, market prices, expenses, and more — in English and Tamil, with voice support throughout.

🔗 **Live Demo:** https://farming-assistant-fxvg.onrender.com

---

## 📱 Features

| Feature | Description |
|---------|-------------|
| 💬 AI Chat | Ask farming questions in English or Tamil with voice input |
| 📸 Crop Diagnosis | Upload a plant photo to detect diseases instantly |
| ☀️ Live Weather | Real-time weather with farming tips for your city |
| 🌧️ Rain Forecast | 7-day rain prediction with irrigation advice |
| 📊 Market Prices | Wholesale crop prices in Rs/kg and Rs/quintal |
| 🌱 Soil Advisory | Soil prep and fertilizer tips by crop and season |
| 🐛 Pest Alerts | Region-specific pest warnings with organic and chemical fixes |
| 📋 Govt Schemes | Central and state farming subsidies and loan schemes |
| 📅 Crop Calendar | Month-by-month planting and harvesting guide |
| 🧪 Fertilizer Calculator | Exact NPK fertilizer quantities for your land and crop |
| 💰 Expense Tracker | Log farming expenses and income, track profit/loss |
| 🌾 Crop Recommendation | AI-suggested best crops for your soil, season, and water |
| 📈 Yield Prediction | AI estimate of expected crop yield |
| 🔐 Authentication | Email OTP registration, login, forgot password, guest login, or use without an account |
| 👤 Profile | Photo upload, activity stats, password management |
| 🌙 Dark Mode | Toggleable dark theme across the dashboard |

Most advisory features support **English/Tamil toggle**, **voice input (mic)**, and **read-aloud (voice reader)** for accessibility.

---

## 🛠️ Tech Stack

**Backend**
- Python + FastAPI
- Groq API (LLaMA 3.3 70B for chat/advisory features, LLaMA 4 Scout for image diagnosis)
- OpenWeatherMap API (weather + forecast)
- Brevo SMTP (Email OTP delivery)
- MongoDB (users, activity logs, expenses)
- bcrypt (password hashing)

**Frontend**
- HTML, CSS, JavaScript (no framework)
- Web Speech API (voice input and text-to-speech)
- Mobile-friendly responsive design

**Deployment**
- Render (live hosting)
- GitHub (version control, auto-deploy on push)

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
MONGODB_URI=your_mongodb_connection_string
BREVO_SMTP_LOGIN=your_brevo_smtp_login
BREVO_SMTP_KEY=your_brevo_smtp_key
SENDER_EMAIL=your_verified_sender_email

### 5. Run the server
```bash
uvicorn main:app --reload
```

### 6. Open in browser
http://127.0.0.1:8000

---

## 🔑 API Keys / Services Required

| Service | Purpose | Free? |
|---------|---------|-------|
| [Groq](https://console.groq.com) | AI chat, diagnosis, and advisory features | ✅ Free |
| [OpenWeatherMap](https://openweathermap.org/api) | Weather and forecast | ✅ Free |
| [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) | Database (users, logs, expenses) | ✅ Free tier |
| [Brevo](https://www.brevo.com) | Email OTP delivery (SMTP) | ✅ Free (300 emails/day) |

---

## 📂 Project Structure


farming-assistant/
├── main.py                  # FastAPI backend with all endpoints
├── requirements.txt         # Python dependencies
├── .env                     # API keys and secrets (not committed)
├── farming_assistant.db     # Legacy SQLite file (unused, MongoDB is primary)
└── static/
├── index.html            # Home dashboard
├── login.html            # Login + forgot password
├── register.html         # Registration (Email OTP / Guest / No account)
├── profile.html          # Farmer profile, photo, password
├── chat.html              # AI chat with Tamil + voice
├── diagnose.html          # Crop disease diagnosis
├── weather.html           # Live weather
├── forecast.html          # 7-day rain forecast
├── market.html            # Market prices
├── soil.html               # Soil advisory
├── pest.html                # Pest alerts
├── schemes.html             # Government schemes
├── calendar.html            # Crop calendar
├── fertilizer.html          # Fertilizer calculator
├── expenses.html            # Expense tracker
├── recommend.html           # Crop recommendation
└── yield.html                # Yield prediction

---

## 🔐 Authentication Options

Farmers can access the app in three ways:
1. **Email OTP Registration** — full account with secure password (bcrypt-hashed) and email verification
2. **Guest Login** — lightweight account (name only, no password) with saved activity history
3. **Use Without Account** — instant access, no data saved

---

## 📸 Screenshots

> Home dashboard with all features, farmer registration with Email OTP, AI chat in Tamil, crop disease diagnosis, expense tracker with profit/loss summary, and 7-day rain forecast with farming advice.

---

## 👨‍💻 Developer

**R Nithish**
- GitHub: [@rnithish18](https://github.com/rnithish18)
- Project built as a portfolio project for Indian agriculture

---

## 📄 License

MIT License — free to use and modify.