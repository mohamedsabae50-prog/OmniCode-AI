from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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

# 1. بوابة الصفحة الرئيسية (تفتح التصميم)
@app.get("/", response_class=HTMLResponse)
async def read_root():
    # بنطلع بره فولدر api عشان نلاقي ملف index.html
    # لو الملف في الرئيسية، المسار "index.html" صح
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "<h1>AetherCode: index.html not found!</h1>"

# 2. بوابة التأكد من الحالة
@app.get("/api/index")
async def health():
    return {"message": "AetherCode AI is Active"}

# 3. بوابة معالجة الكود
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
    
    lang_map = {
        "ar": "PURE ARABIC (اللغة العربية). Strictly NO Franco.",
        "en": "Professional English.",
        "de": "Fluent German (Deutsch).",
        "es": "Fluent Spanish (Español)."
    }
    explanation_instruction = lang_map.get(ui_lang, "Professional English.")

    sys_msg = (
        f"You are AetherCode AI, a universal expert in ALL programming languages. "
        f"Target Language: {lang}. "
        f"Strictly: Explanation must be in {explanation_instruction}. "
        "If no code input is provided, write the code from scratch based ONLY on the Goal/Inquiry. "
        "Return ONLY a JSON object with: 'explanation' and 'result'."
    )
    
    code_content = code if code else ""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": f"Code: {code_content}\nError: {error_log}\nGoal: {inquiry}"}
        ],
        "response_format": { "type": "json_object" }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return {"explanation": "Error", "result": str(e)}
