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
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

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
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    lang_map = {"ar": "Arabic (اللغة العربية الفصحى الفنية)", "en": "Professional English"}
    target_lang = lang_map.get(ui_lang, "English")

    # برومبت "الجراح الصارم": ممنوع لمس الكومنتات أو الاستايل أو أسماء المتغيرات الغريبة
    sys_msg = (
        f"You are AetherCode AI, a Zero-Waste Surgical Debugger. "
        f"Your ONLY job is to fix the error in the user's {lang} code. "
        f"STRICT RULES:\n"
        f"1. DO NOT remove, translate, or modify ANY existing comments, even if they are in another language.\n"
        f"2. DO NOT change variable names or refactor logic that is already working.\n"
        f"3. KEEP the original indentation and coding style 100% identical.\n"
        f"4. ONLY fix the specific line/part causing the bug.\n"
        f"5. Explanation MUST be in {target_lang}.\n"
        f"6. Return ONLY valid JSON: {{'explanation': '...', 'result': '...'}}."
    )

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": f"Code:\n{code}\n\nTerminal Error: {error_log}\nInquiry: {inquiry}"}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.1
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=25)
        return json.loads(response.json()['choices'][0]['message']['content'])
    except Exception as e:
        return {"explanation": "Server Error", "result": str(e)}

@app.post("/api/feedback")
async def save_feedback(rating: str = Form(...), comment: str = Form(None), code_context: str = Form(None)):
    if DISCORD_WEBHOOK_URL:
        data = {"content": f"📢 **New Aether Feedback!**\n**Status:** {rating.upper()}\n**User Comment:** {comment}"}
        requests.post(DISCORD_WEBHOOK_URL, json=data)
    return {"message": "تم الإرسال! شكراً لمساهمتك في تطوير AetherCode."}
