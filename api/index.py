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

RAW_KEYS = os.getenv("GROQ_API_KEYS", "")
API_KEYS = [k.strip() for k in RAW_KEYS.split(",") if k.strip()]

@app.get("/")
async def read_root():
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_path, "index.html")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except:
        return HTMLResponse(content="<h1>AetherCode AI</h1><p>Frontend Not Found.</p>")

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
        
        # الأوامر الصارمة جداً (الجزء الجذري)
        sys_msg = (
            f"ACT AS A {lang} COMPILER. "
            f"1. YOU ARE FORBIDDEN FROM CHANGING THE LANGUAGE TO C OR ANY OTHER LANGUAGE. "
            f"2. YOUR ONLY OUTPUT LANGUAGE MUST BE {lang}. "
            f"3. IF YOU SEE SYNTAX FROM ANOTHER LANGUAGE, CONVERT IT TO {lang} IMMEDIATELY. "
            f"4. DO NOT ADD HEADERS, MAIN FUNCTIONS, OR BOILERPLATE. "
            f"5. RETURN ONLY THE FIXED SNIPPET IN THE 'result' FIELD. "
            f"6. Explanation in {target_lang}."
        )
        
        user_content = f"STRICT MODE: {lang}\nREQUEST: {follow_up}\nCODE:\n{code}" if follow_up else f"STRICT MODE: {lang}\nTASK: {inquiry}\nCODE:\n{code}"

        messages = [{"role": "system", "content": sys_msg}, {"role": "user", "content": user_content}]

        if not API_KEYS:
            return JSONResponse(content={"explanation": "Missing API Keys", "result": "// Error"}, status_code=500)

        for key in random.sample(API_KEYS, len(API_KEYS)):
            try:
                r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json={"model": "llama-3.3-70b-versatile", "messages": messages, "response_format": {"type": "json_object"}, "temperature": 0.1},
                    timeout=20)
                return JSONResponse(content=json.loads(r.json()['choices'][0]['message']['content']))
            except: continue
            
        return JSONResponse(content={"explanation": "All keys failed", "result": "// Error"}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"explanation": str(e), "result": "// Error"}, status_code=400)
