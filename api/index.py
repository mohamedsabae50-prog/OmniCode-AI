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
        code, lang = data.get("code", ""), data.get("lang", "Python")
        ui_lang, inquiry = data.get("ui_lang", "ar"), data.get("inquiry", "Fix")
        follow_up = data.get("follow_up", "")
        
        target_lang = "Arabic" if ui_lang == "ar" else "English"
       sys_msg = (
            f"You are AetherCode Master Architect. "
            f"1. Analyze the code carefully and find the MOST logical fix. "
            f"2. Ensure the code in 'result' is 100% syntactically correct and professional. "
            f"3. Explanation in {target_lang} should be concise and accurate. "
            f"4. Do NOT give multiple versions, give the BEST one. "
            f"Return ONLY JSON: {{'explanation': '...', 'result': '...', 'complexity': '...'}}"
        )
        
        user_content = f"USER REQUEST: {follow_up}\n\nApply to this code:\n{code}" if follow_up else f"Task: {inquiry}\nCode:\n{code}"

        messages = [{"role": "system", "content": sys_msg}, {"role": "user", "content": user_content}]

        if not API_KEYS:
            return JSONResponse(content={"explanation": "Missing API Keys", "result": "// Error"}, status_code=500)

        for key in random.sample(API_KEYS, len(API_KEYS)):
            try:
                r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json={"model": "llama-3.3-70b-versatile", "messages": messages, "response_format": {"type": "json_object"}, "temperature": 0.2},
                    timeout=20)
                return JSONResponse(content=json.loads(r.json()['choices'][0]['message']['content']))
            except: continue
            
        return JSONResponse(content={"explanation": "All keys failed", "result": "// Error"}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"explanation": str(e), "result": "// Error"}, status_code=400)
