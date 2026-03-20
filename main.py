from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import requests
import json
import logging

# إعداد السجل (Logger) باسم المشروع الجديد
logging.basicConfig(filename='omnicode.log', level=logging.INFO, format='%(asctime)s - %(message)s')

app = FastAPI()

# مفتاح Groq الخاص بك (محرك الذكاء الاصطناعي)
import os
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/fix-code")
async def fix_code(
    code: str = Form(...), 
    lang: str = Form(...), 
    ui_lang: str = Form(...), 
    inquiry: str = Form(None),
    error_log: str = Form(None)
):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    # خريطة لغات الشرح الصارمة
    lang_map = {
        "ar": "PURE ARABIC (اللغة العربية). Strictly NO Franco.",
        "en": "Professional English.",
        "de": "Fluent German (Deutsch).",
        "es": "Fluent Spanish (Español)."
    }
    explanation_instruction = lang_map.get(ui_lang, "Professional English.")

    # تحديث اسم المساعد الذكي في الـ Prompt
    sys_msg = (
        f"You are OmniCode AI, a world-class expert in ALL programming languages. "
        f"Target Programming Language: {lang}. "
        f"If the logic is in another language, translate it perfectly to {lang}. "
        f"CRITICAL: Explanation must be in {explanation_instruction} "
        "Return ONLY a JSON object with: 'explanation' (detailed analysis) and 'result' (the clean, fixed code block)."
    )

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": f"Code Input:\n{code}\nTarget Language: {lang}\nError/Terminal Log: {error_log}\nInquiry: {inquiry}"}
        ],
        "response_format": { "type": "json_object" }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return json.dumps({"explanation": "Server Error", "result": str(e)})

@app.post("/submit-feedback")
async def submit_feedback(status: str = Form(...)):
    logging.info(f"USER FEEDBACK: {status}")
    return {"status": "success"}