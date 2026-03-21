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
    allow_headers=["*"],
    allow_methods=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

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
    
    target_lang = "Arabic (اللغة العربية الفصحى الفنية)" if ui_lang == "ar" else "Professional English"

    sys_msg = (
        f"You are AetherCode AI, an elite surgical debugger. "
        f"Fix only the bugs in the {lang} code. Keep style and comments identical. "
        f"Return ONLY valid JSON: {{'explanation': 'Detailed fix in {target_lang}', 'result': 'The corrected code'}}"
    )

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": f"Code:\n{code}\nGoal: {inquiry}\nError: {error_log}"}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=25)
        return json.loads(response.json()['choices'][0]['message']['content'])
    except Exception as e:
        return {"explanation": "Error", "result": str(e)}
