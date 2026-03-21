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
        return "<h1>AetherCode: index.html missing!</h1>"

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
        f"You are AetherCode AI. Surgical Precision Mode. "
        f"Fix {lang}. Keep ALL comments and original structure. "
        f"ONLY return a JSON object with 'explanation' (in {target_lang}) and 'result' (the clean code string). "
        f"DO NOT include any text outside the JSON."
    )

    messages = [{"role": "system", "content": sys_msg}, {"role": "user", "content": f"Code: {code}\nTask: {inquiry}\nError: {error_log}"}]
    if follow_up: messages.append({"role": "user", "content": f"Follow-up: {follow_up}"})

    try:
        response = requests.post(url, json={"model": "llama-3.3-70b-versatile", "messages": messages, "response_format": {"type": "json_object"}}, headers=headers, timeout=25)
        return json.loads(response.json()['choices'][0]['message']['content'])
    except:
        return {"explanation": "Server Error", "result": "Error fixing code."}
