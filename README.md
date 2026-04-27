# 🩸 BloodNet — Blood Bank Emergency Connector (Backend)

A Flask backend that powers the BloodNet blood donor matching system with AI chat support.

---

## ⚙️ Environment Variables

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key from [console.anthropic.com](https://console.anthropic.com) |

---

## 🚀 Deploy to Railway (Recommended)

1. Push this folder to a GitHub repo
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub**
3. Select your repo → Go to **Variables** tab → Add `ANTHROPIC_API_KEY`
4. Railway auto-detects Python and deploys ✅

---

## 🚀 Deploy to Render

1. Push to GitHub → Go to [render.com](https://render.com) → **New Web Service**
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `gunicorn app:app`
4. Add `ANTHROPIC_API_KEY` under Environment → Deploy ✅

---

## 💻 Run Locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your_key_here"
python app.py
```

---

## 📤 Push to GitHub (First Time)

```bash
git init
git add .
git commit -m "Initial commit: BloodNet backend"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

---

## 🔗 Connect Frontend to Backend

Update API calls in your frontend to point to the deployed backend URL:

```js
const API_BASE = "https://your-app.up.railway.app";
```
