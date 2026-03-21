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
    error_log: str = Form(None),
    follow_up: str = Form(None)
):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    target_lang = "Arabic" if ui_lang == "ar" else "English"

    sys_msg = (
        f"You are AetherCode AI, elite surgical debugger. Fix {lang} code. "
        f"RULES: 1. Return ONLY a valid JSON object: {{'explanation': '...', 'result': '...'}}. "
        f"2. Explanation in {target_lang}. 3. Keep original comments and style. "
        f"4. Result must be ONLY the corrected code string."
    )

    messages = [{"role": "system", "content": sys_msg}, {"role": "user", "content": f"Code: {code}\nTask: {inquiry}\nError: {error_log}"}]
    if follow_up: messages.append({"role": "user", "content": f"Update request: {follow_up}"})

    try:
        response = requests.post(url, json={"model": "llama-3.3-70b-versatile", "messages": messages, "response_format": {"type": "json_object"}, "temperature": 0}, headers=headers, timeout=25)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return {"explanation": "خطأ في الاتصال بالسيرفر.", "result": str(e)}
