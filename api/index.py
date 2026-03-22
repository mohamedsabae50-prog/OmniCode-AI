import os
import requests
import json
import random
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# سحب المفاتيح من Vercel Environment Variables
RAW_KEYS = os.getenv("GROQ_API_KEYS", "")
API_KEYS = [k.strip() for k in RAW_KEYS.split(",") if k.strip()]

@app.get("/")
async def read_root():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
@app.post("/api/index")
async def fix_code(request: Request):
    try:
        data = await request.json()
        code = data.get("code", "")
        lang = data.get("lang", "Python")
        ui_lang = data.get("ui_lang", "ar")
        inquiry = data.get("inquiry", "Fix")
        error_log = data.get("error_log", "")
        follow_up = data.get("follow_up", "")
        
        target_lang = "Arabic" if ui_lang == "ar" else "English"
        sys_msg = (
            f"You are AetherCode Master Architect. Fix {lang} code. "
            f"Explanation in {target_lang}. "
            f"Return ONLY JSON: {{'explanation': '...', 'result': '...', 'complexity': '...'}}"
        )
        
        messages = [{"role": "system", "content": sys_msg}, {"role": "user", "content": f"Task: {inquiry}\nCode: {code}\nError: {error_log}"}]
        if follow_up: messages.append({"role": "user", "content": follow_up})

        if not API_KEYS:
            return JSONResponse(content={"explanation": "API Keys Missing in Vercel Settings", "result": "// Error"}, status_code=500)

        for key in random.sample(API_KEYS, len(API_KEYS)):
            try:
                r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json={"model": "llama-3.3-70b-versatile", "messages": messages, "response_format": {"type": "json_object"}, "temperature": 0.4},
                    timeout=20)
                return JSONResponse(content=json.loads(r.json()['choices'][0]['message']['content']))
            except: continue
            
        return JSONResponse(content={"explanation": "All API keys failed", "result": "// Error"}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"explanation": str(e), "result": "// Error"}, status_code=400)
