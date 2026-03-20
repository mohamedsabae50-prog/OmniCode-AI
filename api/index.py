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

@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "<h1>AetherCode: index.html not found!</h1>"

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
    
    lang_map = {
        "ar": "اللغة العربية الفصحى حصراً (No Franco)",
        "en": "Professional English",
        "de": "Fluent German"
    }
    
    sys_msg = (
        f"You are AetherCode AI. Expert in {lang}. "
        f"Output MUST be in JSON format with keys: 'explanation' and 'result'. "
        f"The 'explanation' MUST be in {lang_map.get(ui_lang, 'English')}. "
        "Keep the 'result' as pure code."
    )

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": f"Code: {code}\nError: {error_log}\nInquiry: {inquiry}"}
        ],
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        # نرجع الرد كـ JSON مباشر للمتصفح
        content = response_data['choices'][0]['message']['content']
        return json.loads(content)
    except Exception as e:
        return {"explanation": "حدث خطأ في السيرفر", "result": str(e)}
