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
        return "<h1>AetherCode AI: index.html not found!</h1>"

@app.post("/api/index")
async def fix_code(
    code: str = Form(None), 
    lang: str = Form(...),  
    ui_lang: str = Form(...),  
    inquiry: str = Form(None),  
    error_log: str = Form(None)
):
    if not GROQ_API_KEY:
        return {"explanation": "Error", "result": "API Key Missing!"}

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    # خريطة لضمان كتابة الشرح باللغة الصحيحة
    lang_names = {
        "ar": "Arabic (اللغة العربية)",
        "en": "English",
        "de": "German (Deutsch)"
    }
    target_lang = lang_names.get(ui_lang, "English")

    sys_msg = (
        f"You are AetherCode AI, an expert in {lang}. "
        f"You must return ONLY a JSON object: {{'explanation': '...', 'result': '...'}}. "
        f"CRITICAL: The 'explanation' field MUST be written in {target_lang}. "
        f"The 'result' field must contain ONLY the corrected code."
    )

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": f"Task:{inquiry}\nCode:{code}\nError:{error_log}"}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return json.dumps({"explanation": "Error", "result": str(e)})
