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
    except Exception as e:
        return f"<h1>Error reading index.html: {str(e)}</h1>"

@app.post("/api/index")
async def fix_code(
    code: str = Form(None), 
    lang: str = Form(...),  
    ui_lang: str = Form(...),  
    inquiry: str = Form(None),  
    error_log: str = Form(None),
    follow_up: str = Form(None) # Request 3: حقل التعديلات الإضافية
):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    lang_map = {"ar": "Arabic (العربية الفصحى الفنية)", "en": "Professional English"}
    target_lang = lang_map.get(ui_lang, "English")

    sys_msg = (
        f"You are AetherCode AI, an elite software engineer from AASTMT, Alexandria. "
        f"You fix only broken code. CRITICAL RULES:\n"
        f"1. Keep user's exact indentation, variable names, AND ALL comments (even Franco-Arabic).\n"
        f"2. Fix only the problematic part of the {lang} code/markup.\n"
        f"3. Return full, clean code without markdown backticks.\n"
        f"4. Explanation must be Technically Deep and purely in {target_lang}.\n"
        f"5. If follow-up edits are provided, adjust the PREVIOUS fix based on them.\n"
        f"6. Result must be valid JSON: {{'explanation': '...', 'result': '...'}}"
    )

    # هيكلة الرسائل لتدعيم الذاكرة التفاعلية
    messages = [
        {"role": "system", "content": sys_msg},
        {"role": "user", "content": f"Lang: {lang}\nInquiry: {inquiry}\nTerminal: {error_log}\nCode:\n{code}"}
    ]

    # لو فيه تعديلات إضافية، الـ AI هيعتبرها تكملة للطلب
    if follow_up:
        messages.append({"role": "user", "content": f"📝 Follow-up Edits Requested: {follow_up}"})

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "response_format": {"type": "json_object"},
        "temperature": 0.1, # Strictness Level: High
        "max_tokens": 1024
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=25)
        response.raise_for_status()
        return json.loads(response.json()['choices'][0]['message']['content'])
    except Exception as e:
        return {"explanation": "خطأ فني في الرد الجراحي أو التعديل.", "result": str(e)}

@app.post("/api/feedback")
async def save_feedback(rating: str = Form(...), comment: str = Form(None), code_context: str = Form(None)):
    if DISCORD_WEBHOOK_URL:
        data = {"content": f"🎯 **Feedback Received!** [{rating.upper()}]\nComment: {comment}\nSnippet (first 100): `{code_context[:100]}...`"}
        requests.post(DISCORD_WEBHOOK_URL, json=data)
    return {"message": "تم استلام ملاحظاتك بنجاح! شكراً لك."}
