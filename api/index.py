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

# بوابة الصفحة الرئيسية
@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"<h1>AetherCode Error: index.html not found!</h1><p>{str(e)}</p>"

# بوابة معالجة الكود
@app.post("/api/index")
async def fix_code(
    code: str = Form(None), 
    lang: str = Form(...),  
    ui_lang: str = Form(...),  
    inquiry: str = Form(None),  
    error_log: str = Form(None)
):
    if not GROQ_API_KEY:
        return {"explanation": "Error", "result": "API Key is missing in Vercel settings!"}

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    lang_map = {
        "ar": "اللغة العربية الفصحى (No Franco)",
        "en": "Professional English",
        "de": "Fluent German"
    }
    
    sys_msg = (
        f"You are AetherCode AI. Expert in {lang}. "
        f"Output MUST be a valid JSON object with keys: 'explanation' and 'result'. "
        f"The 'explanation' MUST be in {lang_map.get(ui_lang, 'English')}. "
        "The 'result' must contain ONLY the corrected code."
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
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        # تحويل النص لـ JSON للتأكد من سلامته
        return json.loads(content)
    except Exception as e:
        return {"explanation": "خطأ فني في الاتصال بالذكاء الاصطناعي", "result": f"Detail: {str(e)}"}
