from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import json
import os
import random
from functools import wraps

app = Flask(__name__)
app.secret_key = 'dark_hunter_secret_key_2025'

# ------------------- بيانات العملات الحصرية -------------------
COINS = {
    "السطران": {"price": 367.98, "change": "+5.24", "volume": "2.41M", "icon": "🐉"},
    "العقرب": {"price": 51.73, "change": "-2.15", "volume": "1.17M", "icon": "🦂"},
    "الدلو": {"price": 1000.00, "change": "+18.47", "volume": "5.89M", "icon": "💧"}
}

# ------------------- إدارة المستخدمين -------------------
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    else:
        default_users = {
            "admin@example.com": {
                "password": "admin123",
                "wallet": {"السطران": 12.45, "العقرب": 35.80, "الدلو": 1.25, "usdt": 8750.50}
            }
        }
        save_users(default_users)
        return default_users

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

users_db = load_users()

# ------------------- الأسعار الحية (تقلبات ذكية) -------------------
def get_live_prices():
    updated = {}
    for coin, data in COINS.items():
        volatility = random.uniform(-0.02, 0.02)
        new_price = round(data["price"] * (1 + volatility), 2)
        change_val = round(((new_price - data["price"]) / data["price"]) * 100, 2)
        updated[coin] = {
            "price": new_price,
            "change": f"{'+' if change_val >= 0 else ''}{change_val}",
            "volume": data["volume"],
            "icon": data["icon"]
        }
    return updated

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ------------------- Routes -------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email in users_db and users_db[email]['password'] == password:
            session['email'] = email
            return redirect(url_for('index'))
        else:
            return render_template_string(LOGIN_TEMPLATE, error="Invalid email or password / البريد أو كلمة المرور غير صحيحة")
    return render_template_string(LOGIN_TEMPLATE, error=None)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if not email or not password:
            return render_template_string(REGISTER_TEMPLATE, error="All fields required / جميع الحقول مطلوبة")
        if email in users_db:
            return render_template_string(REGISTER_TEMPLATE, error="Email already registered / البريد مسجل بالفعل")
        users_db[email] = {
            "password": password,
            "wallet": {"السطران": 0.0, "العقرب": 0.0, "الدلو": 0.0, "usdt": 1000.0}
        }
        save_users(users_db)
        session['email'] = email
        return redirect(url_for('index'))
    return render_template_string(REGISTER_TEMPLATE, error=None)

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    email = session['email']
    wallet = users_db[email]['wallet']
    return render_template_string(MAIN_TEMPLATE, email=email, wallet=wallet, coins=COINS)

@app.route('/api/market_data')
def market_data():
    return jsonify(get_live_prices())

@app.route('/api/wallet')
@login_required
def get_wallet():
    email = session['email']
    return jsonify(users_db[email]['wallet'])

@app.route('/api/trade', methods=['POST'])
@login_required
def trade():
    data = request.get_json()
    coin = data.get('coin')
    action = data.get('action')
    amount = float(data.get('amount', 0))
    email = session['email']
    wallet = users_db[email]['wallet']

    if coin not in COINS:
        return jsonify({"success": False, "message": "Invalid coin"})

    price = COINS[coin]["price"]
    total_cost = amount * price

    if action == 'buy':
        if wallet['usdt'] >= total_cost:
            wallet['usdt'] -= total_cost
            wallet[coin] = wallet.get(coin, 0) + amount
            users_db[email]['wallet'] = wallet
            save_users(users_db)
            return jsonify({"success": True, "message": f"Bought {amount} {coin}", "wallet": wallet})
        else:
            return jsonify({"success": False, "message": "Insufficient USDT balance"})
    elif action == 'sell':
        if wallet.get(coin, 0) >= amount:
            wallet[coin] -= amount
            wallet['usdt'] += total_cost
            users_db[email]['wallet'] = wallet
            save_users(users_db)
            return jsonify({"success": True, "message": f"Sold {amount} {coin}", "wallet": wallet})
        else:
            return jsonify({"success": False, "message": f"Insufficient {coin} balance"})
    else:
        return jsonify({"success": False, "message": "Unknown action"})

@app.route('/api/ai_insight')
def ai_insight():
    prices = get_live_prices()
    insights = []
    for coin, data in prices.items():
        change_val = float(data["change"])
        if change_val > 5:
            insights.append(f"🚀 {coin} is rising strongly, buy signal.")
        elif change_val < -2:
            insights.append(f"⚠️ {coin} under selling pressure, watch support.")
        else:
            insights.append(f"📊 {coin} is stable, sideways movement expected.")
    special = "💧 Al-Dalu (الدلو) surged +1000 units in last 24h! Exceptional AI-driven move."
    return jsonify({"insights": insights, "special": special})

# ------------------- قوالب HTML (ثنائية اللغة) -------------------
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dark Hunter - Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Tahoma, sans-serif; }
        body { background: linear-gradient(145deg, #0a0c12 0%, #0f111a 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; }
        .login-card { background: rgba(16,20,30,0.9); backdrop-filter: blur(12px); border-radius: 2rem; padding: 2rem; width: 380px; border: 1px solid rgba(240,185,11,0.3); box-shadow: 0 20px 35px rgba(0,0,0,0.5); text-align: center; }
        .login-card h1 { background: linear-gradient(135deg, #fff, #f0b90b); background-clip: text; -webkit-background-clip: text; color: transparent; margin-bottom: 1.5rem; font-size: 2rem; }
        .input-group { margin-bottom: 1.2rem; text-align: left; }
        .input-group input { width: 100%; padding: 0.8rem; background: #0f111a; border: 1px solid #2c2f42; border-radius: 1rem; color: white; font-size: 1rem; }
        button { background: #f0b90b; color: #0a0c12; border: none; padding: 0.7rem; width: 100%; border-radius: 1.5rem; font-weight: bold; font-size: 1rem; cursor: pointer; transition: 0.2s; }
        button:hover { filter: brightness(0.95); }
        .error { color: #ff5e7e; margin-top: 0.5rem; }
        .footer { margin-top: 1rem; font-size: 0.75rem; }
        .footer a { color: #f0b90b; text-decoration: none; }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>
    <div class="login-card">
        <h1><i class="fas fa-skull"></i> Dark Hunter</h1>
        <form method="POST">
            <div class="input-group">
                <input type="email" name="email" placeholder="Email" required>
            </div>
            <div class="input-group">
                <input type="password" name="password" placeholder="Password" required>
            </div>
            <button type="submit">Login</button>
            {% if error %}
                <div class="error">{{ error }}</div>
            {% endif %}
        </form>
        <div class="footer">No account? <a href="/register">Create one</a></div>
        <div class="footer">Demo: admin@example.com / admin123</div>
    </div>
</body>
</html>
"""

REGISTER_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dark Hunter - Register</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Tahoma, sans-serif; }
        body { background: linear-gradient(145deg, #0a0c12 0%, #0f111a 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; }
        .register-card { background: rgba(16,20,30,0.9); backdrop-filter: blur(12px); border-radius: 2rem; padding: 2rem; width: 380px; border: 1px solid rgba(240,185,11,0.3); box-shadow: 0 20px 35px rgba(0,0,0,0.5); text-align: center; }
        .register-card h1 { background: linear-gradient(135deg, #fff, #f0b90b); background-clip: text; -webkit-background-clip: text; color: transparent; margin-bottom: 1.5rem; font-size: 2rem; }
        .input-group { margin-bottom: 1.2rem; text-align: left; }
        .input-group input { width: 100%; padding: 0.8rem; background: #0f111a; border: 1px solid #2c2f42; border-radius: 1rem; color: white; font-size: 1rem; }
        button { background: #f0b90b; color: #0a0c12; border: none; padding: 0.7rem; width: 100%; border-radius: 1.5rem; font-weight: bold; font-size: 1rem; cursor: pointer; }
        .error { color: #ff5e7e; margin-top: 0.5rem; }
        .footer { margin-top: 1rem; }
        .footer a { color: #f0b90b; text-decoration: none; }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>
    <div class="register-card">
        <h1><i class="fas fa-user-plus"></i> Create Account</h1>
        <form method="POST">
            <div class="input-group">
                <input type="email" name="email" placeholder="Email" required>
            </div>
            <div class="input-group">
                <input type="password" name="password" placeholder="Password" required>
            </div>
            <button type="submit">Register</button>
            {% if error %}
                <div class="error">{{ error }}</div>
            {% endif %}
        </form>
        <div class="footer">Already have an account? <a href="/login">Login</a></div>
    </div>
</body>
</html>
"""

MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>Dark Hunter | Trading Platform</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', 'Poppins', sans-serif; }
        body { background: linear-gradient(145deg, #0a0c12 0%, #0f111a 100%); color: #eef2ff; padding: 1.5rem; min-height: 100vh; }
        /* تكبير الحاوية الرئيسية */
        .app-container { max-width: 1500px; margin: 0 auto; background: rgba(10, 14, 23, 0.7); backdrop-filter: blur(3px); border-radius: 2rem; padding: 1.5rem 2rem; box-shadow: 0 25px 45px rgba(0,0,0,0.5); }
        /* شريط الإعلانات */
        .ads-bar { background: linear-gradient(90deg, #1e1b2a, #261c2c); border-radius: 1rem; padding: 0.7rem 1rem; margin-bottom: 1.8rem; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; border: 1px solid rgba(240,185,11,0.4); font-size: 0.85rem; }
        .ads-text i { color: #f0b90b; margin-left: 0.5rem; }
        /* تكبير اسم المنصة */
        .logo-area h1 { font-size: 2.2rem; background: linear-gradient(135deg, #fff, #f0b90b); background-clip: text; -webkit-background-clip: text; color: transparent; }
        .logo-area p { font-size: 0.8rem; opacity: 0.8; }
        .section-title { font-size: 1.3rem; font-weight: 600; margin-bottom: 1.2rem; display: flex; align-items: center; gap: 0.5rem; border-right: 4px solid #f0b90b; padding-right: 0.8rem; }
        /* تكبير البطاقات والخطوط */
        .price-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.2rem; margin-bottom: 2rem; }
        .coin-card { background: rgba(20, 24, 36, 0.8); border-radius: 1.3rem; padding: 1.2rem; }
        .coin-price { font-size: 1.9rem; font-weight: 700; }
        .grid-2col { display: grid; grid-template-columns: 1fr 1fr; gap: 1.8rem; margin-bottom: 2rem; }
        @media (max-width: 900px) { .grid-2col { grid-template-columns: 1fr; } }
        .card { background: rgba(16, 20, 30, 0.85); border-radius: 1.5rem; padding: 1.4rem; }
        /* تكبير الشارت */
        .chart-container canvas { max-height: 320px; width: 100%; height: auto; }
        .exchange-table th, .exchange-table td { padding: 0.8rem 0.4rem; font-size: 0.9rem; }
        .btn-sm { background: #2a2e42; padding: 0.4rem 0.9rem; font-size: 0.8rem; }
        .wallet-item { font-size: 1rem; margin: 0.7rem 0; }
        .trade-form select, .trade-form input, .trade-form button { padding: 0.6rem 1rem; font-size: 0.9rem; }
        .ai-insight { font-size: 0.9rem; }
        .footer-note { margin-top: 2rem; font-size: 0.75rem; }
        /* أزرار اللغة */
        .lang-switch { display: flex; gap: 0.5rem; margin-right: 1rem; }
        .lang-btn { background: #2a2e42; border: none; color: white; padding: 0.3rem 0.7rem; border-radius: 20px; cursor: pointer; font-size: 0.7rem; }
        .lang-btn.active { background: #f0b90b; color: #0a0c12; }
        .header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; margin-bottom: 1.8rem; }
    </style>
</head>
<body>
<div class="app-container">
    <!-- شريط الإعلانات (خاص بالمنصة والعملات) -->
    <div class="ads-bar">
        <div class="ads-text"><i class="fas fa-bullhorn"></i> 🔥 Dark Hunter Exclusive: Trade Al-Satran, Al-Aqrab, Al-Dalu with 0% fees for first week! | AI predictions active</div>
        <div><i class="fas fa-gem"></i> Limited offer: Deposit bonus 10%</div>
    </div>

    <div class="header">
        <div class="logo-area">
            <h1><i class="fas fa-skull"></i> Dark Hunter</h1>
            <p>Advanced AI Trading | Exclusive Coins</p>
        </div>
        <div style="display: flex; align-items: center;">
            <div class="lang-switch">
                <button class="lang-btn active" data-lang="en">EN</button>
                <button class="lang-btn" data-lang="ar">AR</button>
            </div>
            <div class="ai-badge" style="background: rgba(240,185,11,0.15); padding: 0.4rem 1rem; border-radius: 40px; margin-left: 1rem;"><i class="fas fa-microchip"></i> AI v3.0</div>
            <a href="/logout" class="logout-btn" style="background: #2a2e42; padding: 0.4rem 1rem; border-radius: 40px; color: white; text-decoration: none; margin-right: 1rem;"><i class="fas fa-sign-out-alt"></i> Logout</a>
        </div>
    </div>

    <div class="price-cards" id="priceCardsContainer"></div>

    <div class="grid-2col">
        <div class="card">
            <div class="section-title"><i class="fas fa-chart-line"></i> <span data-en="Advanced Chart | Real-time" data-ar="الشارت المتقدم | لحظي">Advanced Chart | Real-time</span></div>
            <div class="chart-buttons" id="chartCoinSelector" style="margin-bottom: 1rem;">
                <button data-coin="السطران" class="btn-sm active-chart-btn">Al-Satran (SRT)</button>
                <button data-coin="العقرب" class="btn-sm">Al-Aqrab (AQR)</button>
                <button data-coin="الدلو" class="btn-sm">Al-Dalu (DLO)</button>
            </div>
            <div class="chart-container"><canvas id="priceChart" width="800" height="350" style="width:100%; height:auto; max-height:350px"></canvas></div>
            <div class="ai-insight" id="aiChartInsight"><i class="fas fa-robot"></i> AI: Analyzing price patterns...</div>
        </div>
        <div class="card">
            <div class="section-title"><i class="fas fa-globe"></i> <span data-en="Global Exchange | Dark Hunter Coins" data-ar="بورصة عالمية | عملات Dark Hunter">Global Exchange | Dark Hunter Coins</span></div>
            <div style="overflow-x: auto;">
                <table class="exchange-table">
                    <thead><tr><th>Pair</th><th>Price (USDT)</th><th>24h Change</th><th>Volume</th></tr></thead>
                    <tbody id="exchangeTbody"></tbody>
                </table>
            </div>
            <div class="ai-insight" style="margin-top: 1rem;" id="exchangeAIInsight"><i class="fas fa-brain"></i> <strong>AI Insight:</strong> Only platform-exclusive coins traded here.</div>
        </div>
    </div>

    <div class="grid-2col">
        <div class="card">
            <div class="section-title"><i class="fas fa-wallet"></i> <span data-en="Digital Wallets | Your Balance" data-ar="محافظ رقمية | رصيدك">Digital Wallets | Your Balance</span></div>
            <div id="walletList"></div>
            <div class="flex-between" style="display: flex; justify-content: space-between; margin-top: 1rem;"><span>💎 Total Portfolio (USDT):</span><strong id="totalPortfolioVal">0.00</strong></div>
        </div>
        <div class="card">
            <div class="section-title"><i class="fas fa-exchange-alt"></i> <span data-en="Instant Buy/Sell" data-ar="شراء / بيع فوري">Instant Buy/Sell</span></div>
            <div class="trade-form">
                <select id="tradeCoinSelect">
                    <option value="السطران">Al-Satran (SRT)</option>
                    <option value="العقرب">Al-Aqrab (AQR)</option>
                    <option value="الدلو">Al-Dalu (DLO)</option>
                </select>
                <input type="number" id="tradeAmount" placeholder="Amount" value="1" step="0.01">
                <button id="buyBtnAction"><i class="fas fa-cart-plus"></i> Buy</button>
                <button id="sellBtnAction"><i class="fas fa-arrow-down"></i> Sell</button>
            </div>
            <div style="margin-top: 0.8rem; background:#00000033; padding:0.5rem; border-radius:1rem;"><i class="fas fa-coins"></i> USDT Balance: <strong id="usdtBalanceDisplay">0.00</strong></div>
            <div id="tradeFeedback" style="margin-top:0.7rem; font-size:0.8rem;"></div>
        </div>
    </div>

    <div style="background: linear-gradient(90deg, #1f1b2e, #11131f); border-radius: 1.2rem; padding: 0.8rem 1.2rem; margin: 1rem 0; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;">
        <div><i class="fas fa-water" style="color:#4aa0ff;"></i> <strong>🚀 Al-Dalu (الدلو) Surge: +1000 units in 24h!</strong> AI-driven breakout.</div>
        <div><i class="fas fa-chart-line"></i> Forecast: Continued bullish momentum</div>
    </div>
    <div class="footer-note">
        <i class="fas fa-copyright"></i> 2025 Dark Hunter Platform. All rights reserved. Developed by atyaa9911@gmail.com
    </div>
</div>

<script>
    // Multi-language support
    let currentLang = 'en';
    function setLanguage(lang) {
        currentLang = lang;
        document.querySelectorAll('[data-en]').forEach(el => {
            if (lang === 'en') el.innerText = el.getAttribute('data-en');
            else el.innerText = el.getAttribute('data-ar');
        });
        document.querySelectorAll('.lang-btn').forEach(btn => {
            if (btn.getAttribute('data-lang') === lang) btn.classList.add('active');
            else btn.classList.remove('active');
        });
    }
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', () => setLanguage(btn.getAttribute('data-lang')));
    });

    let chartInstance = null;
    let currentChartCoin = 'السطران';
    let currentPrices = {};

    async function fetchMarketData() {
        const res = await fetch('/api/market_data');
        return await res.json();
    }
    async function fetchWallet() {
        const res = await fetch('/api/wallet');
        return await res.json();
    }
    async function updatePriceCards() {
        const market = await fetchMarketData();
        currentPrices = market;
        const container = document.getElementById('priceCardsContainer');
        container.innerHTML = '';
        for (const [coin, info] of Object.entries(market)) {
            let displayName = coin === 'السطران' ? 'Al-Satran' : (coin === 'العقرب' ? 'Al-Aqrab' : 'Al-Dalu');
            container.innerHTML += `
                <div class="coin-card">
                    <div><span>${info.icon} ${displayName}</span> <small>24h</small></div>
                    <div class="coin-price">${info.price} USDT</div>
                    <div class="${info.change.startsWith('+') ? 'positive' : 'negative'}">${info.change}%</div>
                </div>
            `;
        }
        return market;
    }
    async function updateExchangeTable(market) {
        const tbody = document.getElementById('exchangeTbody');
        tbody.innerHTML = '';
        for (const [coin, info] of Object.entries(market)) {
            let displayName = coin === 'السطران' ? 'Al-Satran' : (coin === 'العقرب' ? 'Al-Aqrab' : 'Al-Dalu');
            tbody.innerHTML += `<tr><td><strong>${info.icon} ${displayName}/USDT</strong></td><td style="direction:ltr">${info.price}</td><td class="${info.change.startsWith('+') ? 'positive' : 'negative'}">${info.change}%</td><td>${info.volume}</td></tr>`;
        }
    }
    function generateHistoricalData(coinName, days = 14) {
        const basePrice = currentPrices[coinName] ? currentPrices[coinName].price : (coinName === 'السطران' ? 367.98 : (coinName === 'العقرب' ? 51.73 : 1000));
        let data = [], labels = [];
        for (let i = days; i >= 0; i--) {
            let randomFactor = 1 + (Math.random() - 0.5) * 0.03;
            let price = basePrice * (0.92 + (i/days)*0.16) * randomFactor;
            if (coinName === 'الدلو') price = basePrice * (0.88 + (i/days)*0.24) * randomFactor;
            if (coinName === 'العقرب') price = basePrice * (0.95 + (i/days)*0.05) * randomFactor;
            data.push(price);
            let d = new Date(); d.setDate(d.getDate() - i);
            labels.push(`${d.getMonth()+1}/${d.getDate()}`);
        }
        return { labels, prices: data };
    }
    function renderChart(coinName) {
        const ctx = document.getElementById('priceChart').getContext('2d');
        if (chartInstance) chartInstance.destroy();
        const { labels, prices } = generateHistoricalData(coinName, 14);
        chartInstance = new Chart(ctx, {
            type: 'line',
            data: { labels, datasets: [{ label: `${coinName} (USDT)`, data: prices, borderColor: '#f0b90b', backgroundColor: 'rgba(240,185,11,0.05)', borderWidth: 2.5, pointRadius: 2, tension: 0.3, fill: true }] },
            options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { labels: { color: '#ddd' } } }, scales: { y: { grid: { color: '#2a2e42' }, ticks: { color: '#ccc' } }, x: { ticks: { color: '#aaa' } } } }
        });
        let insightMsg = '';
        if (coinName === 'السطران') insightMsg = '🧠 AI: Bullish engulfing pattern on daily chart, moderate positive momentum.';
        else if (coinName === 'العقرب') insightMsg = '🦂 AI: Oversold possible, watch support at 49.80.';
        else insightMsg = '💧 AI: Strong demand surge +1000 units, sharp upward breakout.';
        document.getElementById('aiChartInsight').innerHTML = `<i class="fas fa-robot"></i> 🤖 ${insightMsg}`;
    }
    async function updateWalletUI() {
        const wallet = await fetchWallet();
        const walletDiv = document.getElementById('walletList');
        let html = '';
        let total = wallet.usdt;
        const coinsList = ['السطران', 'العقرب', 'الدلو'];
        for (let coin of coinsList) {
            let balance = wallet[coin] || 0;
            let price = currentPrices[coin] ? currentPrices[coin].price : (coin === 'السطران' ? 367.98 : (coin === 'العقرب' ? 51.73 : 1000));
            let valueInUSDT = balance * price;
            total += valueInUSDT;
            let displayName = coin === 'السطران' ? 'Al-Satran' : (coin === 'العقرب' ? 'Al-Aqrab' : 'Al-Dalu');
            html += `<div class="wallet-item"><span><i class="fas fa-coins"></i> ${displayName}</span><span>${balance.toFixed(4)} units</span><span>≈ ${valueInUSDT.toFixed(2)} USDT</span></div>`;
        }
        html += `<div class="wallet-item"><span>USDT</span><span>${wallet.usdt.toFixed(2)}</span><span>--</span></div>`;
        walletDiv.innerHTML = html;
        document.getElementById('totalPortfolioVal').innerText = total.toFixed(2);
        document.getElementById('usdtBalanceDisplay').innerText = wallet.usdt.toFixed(2);
    }
    async function executeTrade(action) {
        const coin = document.getElementById('tradeCoinSelect').value;
        const amount = parseFloat(document.getElementById('tradeAmount').value);
        if (isNaN(amount) || amount <= 0) {
            showTradeFeedback('Please enter a valid amount.', false);
            return;
        }
        const res = await fetch('/api/trade', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ coin, action, amount })
        });
        const result = await res.json();
        if (result.success) {
            showTradeFeedback(`✅ ${result.message}`, true);
            await updateWalletUI();
            const market = await updatePriceCards();
            await updateExchangeTable(market);
            renderChart(currentChartCoin);
        } else {
            showTradeFeedback(`❌ ${result.message}`, false);
        }
    }
    function showTradeFeedback(msg, isSuccess) {
        const div = document.getElementById('tradeFeedback');
        div.innerHTML = `<i class="fas fa-${isSuccess ? 'check-circle' : 'exclamation-triangle'}"></i> ${msg}`;
        div.style.color = isSuccess ? '#b0ffb0' : '#ffb7b7';
        setTimeout(() => { if (div.innerHTML.includes(msg)) div.innerHTML = ''; }, 3500);
    }
    async function refreshAll() {
        const market = await updatePriceCards();
        await updateExchangeTable(market);
        renderChart(currentChartCoin);
        await updateWalletUI();
        const aiRes = await fetch('/api/ai_insight');
        const aiData = await aiRes.json();
        document.getElementById('exchangeAIInsight').innerHTML = `<i class="fas fa-brain"></i> <strong>AI Insight:</strong> ${aiData.insights.join(' · ')}<br>✨ ${aiData.special}`;
    }
    document.getElementById('buyBtnAction').onclick = () => executeTrade('buy');
    document.getElementById('sellBtnAction').onclick = () => executeTrade('sell');
    document.querySelectorAll('#chartCoinSelector .btn-sm').forEach(btn => {
        btn.onclick = () => {
            currentChartCoin = btn.getAttribute('data-coin');
            document.querySelectorAll('#chartCoinSelector .btn-sm').forEach(b => b.classList.remove('active-chart-btn'));
            btn.classList.add('active-chart-btn');
            renderChart(currentChartCoin);
        };
    });
    window.onload = async () => {
        await refreshAll();
        setInterval(refreshAll, 7000);
        setLanguage('en');
    };
</script>
<style>
    .positive { color: #00e6b2; }
    .negative { color: #ff5e7e; }
    .active-chart-btn { background: #f0b90b !important; color: #0a0c12 !important; }
    .btn-sm, .lang-btn { transition: 0.2s; }
    .btn-sm:hover, .lang-btn:hover { background: #f0b90b; color: #0a0c12; }
</style>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
