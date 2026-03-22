import os
import requests
import json
import random
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from dotenv import load_dotenv
from pathlib import Path

# 1. تحديد المسارات بشكل قاطع
BASE_DIR = Path(__file__).resolve().parent.parent
HTML_FILE = BASE_DIR / "index.html"

load_dotenv(BASE_DIR / ".env")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

RAW_KEYS = os.getenv("GROQ_API_KEYS", "")
API_KEYS = [k.strip() for k in RAW_KEYS.split(",") if k.strip()]

# ---------------------------------------------------------
# 🎯 السطر اللي هيشغل الموقع "عافية"
# ---------------------------------------------------------
@app.get("/")
async def serve_home():
    # طالما السيرفر شغال، هيرد عليك في الـ Terminal لما تفتح الصفحة
    print(f"🏠 Request received at root! Looking for: {HTML_FILE}")
    if HTML_FILE.exists():
        return FileResponse(str(HTML_FILE))
    return HTMLResponse(f"<h1>File Not Found</h1><p>Searching at: {HTML_FILE}</p>", status_code=404)

# ---------------------------------------------------------
# 🤖 معالج طلبات الذكاء الاصطناعي
# ---------------------------------------------------------
@app.post("/api/index")
async def fix_code(request: Request):
    try:
        data = await request.json()
        code = data.get("code", "")
        lang = data.get("lang", "Python")
        ui_lang = data.get("ui_lang", "ar")
        target_lang = "Arabic" if ui_lang == "ar" else "English"
        
        # تعليمات صارمة جداً باللغة المطلوبة
        sys_msg = (
            f"You are a professional {lang} developer. "
            f"STRICT RULE 1: Your 'explanation' MUST be in {target_lang} language only. "
            f"STRICT RULE 2: Your 'result' field MUST contain the COMPLETE FIXED CODE, not error messages. "
            f"STRICT RULE 3: Fix syntax, logic, and convert from other languages to {lang}. "
            f"Return ONLY JSON: {{'explanation': '...', 'result': '...', 'complexity': '...'}}"
        )

        if not API_KEYS: return JSONResponse(content={"explanation": "Keys missing", "result": "// Error"})

        for key in random.sample(API_KEYS, len(API_KEYS)):
            try:
                r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json={
                        "model": "llama-3.3-70b-versatile", 
                        "messages": [
                            {"role": "system", "content": sys_msg}, 
                            {"role": "user", "content": f"Fix this code and explain in {target_lang}:\n{code}"}
                        ], 
                        "response_format": {"type": "json_object"}, 
                        "temperature": 0.1 
                    }, timeout=15)
                return JSONResponse(content=json.loads(r.json()['choices'][0]['message']['content']))
            except: continue
        return JSONResponse(content={"explanation": "API Error"})
    except Exception as e:
        return JSONResponse(content={"explanation": str(e), "result": "// Error"})
