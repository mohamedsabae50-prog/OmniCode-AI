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
# لو عايز تشغل الفيدباك على ديسكورد، حط اللينك هنا، لو مش عايز سيبها فاضية
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
    
    lang_names = {"ar": "Arabic (العربية)", "en": "English", "de": "German"}
    target_lang = lang_names.get(ui_lang, "English")

    # برومبت "الجراح": يركز فقط على المشكلة ويحافظ على هيكل الكود الأصلي
    sys_msg = (
        f"You are AetherCode AI. Expert in {lang}. "
        f"CRITICAL: Fix only the parts related to the error or inquiry. "
        f"STRICTLY preserve the user's original coding style, variable names, and comments. "
        f"Do not refactor the entire code if not necessary. "
        f"Return JSON: {{'explanation': 'Detailed explanation in {target_lang}', 'result': 'The full code with surgical fixes'}}"
    )

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": f"Task: {inquiry}\nCode: {code}\nError Log: {error_log}"}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        return json.loads(response.json()['choices'][0]['message']['content'])
    except Exception as e:
        return {"explanation": "Error", "result": str(e)}

# بوابة الفيدباك الجديدة
@app.post("/api/feedback")
async def save_feedback(
    rating: str = Form(...), 
    comment: str = Form(None),
    code_context: str = Form(None)
):
    # هنا ممكن تسيف في Database، أو تبعت لنفسك على Discord (أسهل حل ليك حالياً)
    if DISCORD_WEBHOOK_URL:
        data = {
            "content": f"🌟 **New Feedback from AetherCode!**\n**Rating:** {rating}\n**Comment:** {comment}\n**Context:** {code_context[:200]}..."
        }
        requests.post(DISCORD_WEBHOOK_URL, json=data)
    
    return {"status": "success", "message": "شكراً لتقييمك يا هندسة!"}
