from fastapi import FastAPI, Form
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

@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "<h1>AetherCode AI: index.html not found!</h1>"

@app.post("/api/index")
async def fix_code(
    code: str = Form(None), 
    lang: str = Form(...),  
    ui_lang: str = Form(...),  
    inquiry: str = Form(None),  
    error_log: str = Form(None)
):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    lang_map = {"ar": "Arabic (اللغة العربية الفصحى الفنية)", "en": "Professional English"}
    target_lang = lang_map.get(ui_lang, "English")

    sys_msg = (
        f"You are AetherCode AI, a surgical code debugger. "
        f"Your task: Fix the user's {lang} code based on their inquiry/error. "
        f"CRITICAL: Change ONLY the problematic parts. Keep user's variables, style, and comments identical. "
        f"Return ONLY valid JSON: {{'explanation': 'Detailed fix info in {target_lang}', 'result': 'The corrected code'}}"
    )

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": f"Lang: {lang}\nCode: {code}\nInquiry: {inquiry}\nError: {error_log}"}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        return json.loads(response.json()['choices'][0]['message']['content'])
    except Exception as e:
        return {"explanation": "Error in AI Response", "result": str(e)}

@app.post("/api/feedback")
async def save_feedback(rating: str = Form(...), comment: str = Form(None), code_context: str = Form(None)):
    if DISCORD_WEBHOOK_URL:
        data = {"content": f"🚀 **New AetherFeedback!**\n**Rating:** {rating}\n**Comment:** {comment}\n**Snippet:** `{code_context[:100]}...`"}
        requests.post(DISCORD_WEBHOOK_URL, json=data)
    return {"message": "تم استلام ملاحظاتك بنجاح! شكراً لك."}
