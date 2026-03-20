from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
import os

# 1. إنشاء المحرك أولاً
app = FastAPI()

# 2. إعداد الصلاحيات (CORS) مباشرة بعد إنشاء app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. الحصول على المفتاح السري
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@app.get("/")
async def health_check():
    return {"status": "OmniCode AI is Running"}

@app.post("/api/index") # المسار اللي الـ HTML بيكلمه
async def fix_code(
    code: str = Form(...), 
    lang: str = Form(...), 
    ui_lang: str = Form(...), 
    inquiry: str = Form(None),
    error_log: str = Form(None)
):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    lang_map = {
        "ar": "PURE ARABIC (اللغة العربية). Strictly NO Franco.",
        "en": "Professional English.",
        "de": "Fluent German (Deutsch).",
        "es": "Fluent Spanish (Español)."
    }
    explanation_instruction = lang_map.get(ui_lang, "Professional English.")

    sys_msg = (
        f"You are OmniCode AI, a world-class expert in ALL programming languages. "
        f"Target Programming Language: {lang}. "
        f"Explanation must be in {explanation_instruction} "
        "Return ONLY a JSON object with: 'explanation' and 'result'."
    )

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": f"Code Input:\n{code}\nTarget Language: {lang}\nError: {error_log}\nInquiry: {inquiry}"}
        ],
        "response_format": { "type": "json_object" }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return {"explanation": "Server Error", "result": str(e)}

@app.post("/api/feedback")
async def submit_feedback(status: str = Form(...)):
    return {"status": "success", "feedback": status}
