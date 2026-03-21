import os
import requests
import json
import random
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv

# تحميل ملف .env لو موجود محلياً
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 فكرة سحب المفاتيح الثلاثة بأمان 🔥
# بنسحب نص واحد فيه كل المفاتيح مفصولة بفاصلة
RAW_KEYS = os.getenv("GROQ_API_KEYS", "")
# بنقطع النص ونشيل أي مسافات زيادة ونحطهم في قائمة
API_KEYS = [k.strip() for k in RAW_KEYS.split(",") if k.strip()]

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("index.html", "r", encoding="utf-8") as f: return f.read()

@app.post("/api/index")
async def fix_code(request: Request):
    try:
        data = await request.json()
        code, lang = data.get("code", ""), data.get("lang", "Python")
        ui_lang, inquiry = data.get("ui_lang", "ar"), data.get("inquiry", "Fix")
        error_log, follow_up = data.get("error_log", ""), data.get("follow_up", "")
        
        target_lang = "Arabic" if ui_lang == "ar" else "English"
        sys_msg = (
            f"You are AetherCode Master Architect. Fix {lang} code. "
            f"Explanation in {target_lang}. "
            f"Return ONLY JSON object: {{'explanation': '...', 'result': '...', 'complexity': '...'}}"
        )
        
        messages = [{"role": "system", "content": sys_msg}, {"role": "user", "content": f"Task: {inquiry}\nCode: {code}"}]
        if follow_up: messages.append({"role": "user", "content": follow_up})

        # لو مفيش مفاتيح خالص يطلع Error
        if not API_KEYS:
            return JSONResponse(content={"explanation": "No API Keys found", "result": "// Error"}, status_code=500)

        # بنختار مفتاح عشوائي من التلاتة عشان نوزع الحمل
        for key in random.sample(API_KEYS, len(API_KEYS)):
            try:
                r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json={"model": "llama-3.3-70b-versatile", "messages": messages, "response_format": {"type": "json_object"}, "temperature": 0.4},
                    timeout=20)
                
                content = json.loads(r.json()['choices'][0]['message']['content'])
                return JSONResponse(content=content)
            except: continue # لو مفتاح فشل يجرب اللي بعده
            
        return JSONResponse(content={"explanation": "All keys failed", "result": "// Error"}, status_code=500)

    except Exception as e:
        return JSONResponse(content={"explanation": str(e), "result": "// Error"}, status_code=400)
