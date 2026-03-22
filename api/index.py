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

# سحب المفاتيح
RAW_KEYS = os.getenv("GROQ_API_KEYS", "")
API_KEYS = [k.strip() for k in RAW_KEYS.split(",") if k.strip()]

@app.get("/")
async def read_root():
    # كود تحديد مسار ملف الـ HTML بدقة
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_path, "index.html")
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Site is Up</h1><p>Frontend file missing.</p>")

@app.post("/api/index")
async def fix_code(request: Request):
    try:
        data = await request.json()
        code = data.get("code", "")
        lang = data.get("lang", "Python")
        ui_lang = data.get("ui_lang", "ar")
        inquiry = data.get("inquiry", "Fix")
        follow_up = data.get("follow_up", "")
        
        target_lang = "Arabic" if ui_lang == "ar" else "English"
        
        # أوامر صارمة جداً لمنع التغيير للغة C
        sys_msg = (
            f"STRICT {lang} EXPERT. "
            f"1. ONLY use {lang} syntax. NO C/C++ boilerplate. "
            f"2. Convert any foreign syntax to {lang}. "
            f"3. Explanation in {target_lang}. "
            f"Return ONLY JSON: {{'explanation': '...', 'result': '...', 'complexity': '...'}}"
        )
        
        user_content = f"STRICT MODE: {lang}\nREQUEST: {follow_up}\nCODE:\n{code}" if follow_up else f"TASK: {inquiry}\nCODE:\n{code}"

        if not API_KEYS:
            return JSONResponse(content={"explanation": "Missing API Keys", "result": "// Error"}, status_code=500)

        for key in random.sample(API_KEYS, len(API_KEYS)):
            try:
                r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json={
                        "model": "llama-3.3-70b-versatile", 
                        "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": user_content}], 
                        "response_format": {"type": "json_object"}, 
                        "temperature": 0.1
                    }, timeout=20)
                return JSONResponse(content=json.loads(r.json()['choices'][0]['message']['content']))
            except: continue
            
        return JSONResponse(content={"explanation": "All keys failed", "result": "// Error"}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"explanation": str(e), "result": "// Error"}, status_code=400)
