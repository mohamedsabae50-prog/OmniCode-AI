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
    
    sys_msg = (
        f"You are AetherCode AI, expert in {lang}. "
        f"Return ONLY valid JSON: {{'explanation': 'brief in {ui_lang}', 'result': 'pure code'}}. "
        "No markdown backticks."
    )

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": f"Goal:{inquiry}\nCode:{code}\nError:{error_log}"}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        raw_content = response.json()['choices'][0]['message']['content']
        return json.loads(raw_content)
    except Exception as e:
        return {"explanation": "Server Error", "result": str(e)}
