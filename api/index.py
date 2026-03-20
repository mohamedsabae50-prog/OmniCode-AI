from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@app.get("/api/index")
async def health():
    return {"message": "OmniCode AI is Active"}

@app.post("/api/index")
async def fix_code(code: str = Form(...), lang: str = Form(...), ui_lang: str = Form(...), inquiry: str = Form(None), error_log: str = Form(None)):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    sys_msg = f"You are OmniCode AI expert. Target: {lang}. UI Lang: {ui_lang}. Return ONLY JSON with 'explanation' and 'result'."
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": f"Code: {code}\nError: {error_log}\nGoal: {inquiry}"}
        ],
        "response_format": { "type": "json_object" }
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return {"explanation": "Error", "result": str(e)}
from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def read_index():
    # بنطلع بره فولدر api عشان نلاقي ملف index.html
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()
