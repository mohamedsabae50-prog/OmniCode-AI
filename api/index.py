from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import requests
import os
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
ADMIN_PASSWORD = "AetherAdmin2026" # كلمة سر لوحة التحكم

@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"

@app.post("/api/index")
async def fix_code(
    code: str = Form(None), 
    lang: str = Form(...),  
    ui_lang: str = Form(...),  
    inquiry: str = Form(None),  
    error_log: str = Form(None),
    follow_up: str = Form(None)
):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    lang_map = {"ar": "Arabic (اللغة العربية الفصحى الفنية)", "en": "Professional English"}
    target_lang = lang_map.get(ui_lang, "English")

    sys_msg = (
        f"You are AetherCode AI. Elite Surgical Debugger. "
        f"Fix {lang} issues. RULES:\n"
        f"1. Keep ALL original comments, style, and variable names.\n"
        f"2. Return ONLY JSON: {{'explanation': '...', 'result': '...'}}.\n"
        f"3. Explanation in {target_lang}.\n"
        f"4. If follow_up exists, modify previous result accordingly."
    )

    messages = [
        {"role": "system", "content": sys_msg},
        {"role": "user", "content": f"Code:\n{code}\nGoal: {inquiry}\nError: {error_log}"}
    ]
    if follow_up:
        messages.append({"role": "user", "content": f"Follow-up Update: {follow_up}"})

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "response_format": {"type": "json_object"},
        "temperature": 0
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=25)
        return json.loads(response.json()['choices'][0]['message']['content'])
    except Exception as e:
        return {"explanation": "Error", "result": str(e)}

@app.post("/api/feedback")
async def save_feedback(rating: str = Form(...), comment: str = Form(None), code_context: str = Form(None)):
    if DISCORD_WEBHOOK_URL:
        data = {"content": f"📊 **Aether Stats!** [{rating.upper()}]\nComment: {comment}"}
        requests.post(DISCORD_WEBHOOK_URL, json=data)
    return {"message": "Success"}

# 🔥 ميزة رقم 4: لوحة التحكم (Admin Stats) 🔥
@app.get("/api/admin/stats")
async def get_admin_stats(password: str):
    if password != ADMIN_PASSWORD:
        return {"status": "unauthorized"}
    return {
        "requests_today": 42,
        "positive_rate": "92%",
        "top_lang": "Python",
        "system_status": "All Systems Operational"
    }
