import os
import requests
import json
import random
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

RAW_KEYS = os.getenv("GROQ_API_KEYS", "")
API_KEYS = [k.strip() for k in RAW_KEYS.split(",") if k.strip()]

@app.post("/api/index")
async def fix_code(request: Request):
    try:
        data = await request.json()
        raw_code = data.get("code", "")
        lang = data.get("lang", "Python")
        
        # تنظيف الكود من أي علامات زايدة عشان الـ AI ما يتلخبطش
        code = raw_code.replace(f"[STRICT {lang} MODE]", "").strip()
        
        ui_lang = data.get("ui_lang", "ar")
        inquiry = data.get("inquiry", "")
        follow_up = data.get("follow_up", "")
        
        target_lang = "Arabic" if ui_lang == "ar" else "English"
        
        # 🔥 الحل الجذري: فصل تام لبرمجة الذكاء الاصطناعي 🔥
        if follow_up and follow_up.strip() != "":
            # 1. حالة التحديث: هنا بنجبره يكتب كود جديد وينفذ طلبك
            sys_msg = (
                f"You are a Senior {lang} Developer. "
                f"The user wants to ADD A NEW FEATURE or MODIFY the code. "
                f"STRICT RULES:\n"
                f"1. You MUST apply this exact request: '{follow_up}'\n"
                f"2. Do NOT just validate the code. You MUST completely rewrite it to include the new logic.\n"
                f"3. Explain what you added in {target_lang}.\n"
                f"4. OUTPUT ONLY JSON format: {{\"explanation\": \"...\", \"result\": \"NEW FULL CODE HERE\", \"complexity\": \"...\"}}"
            )
            user_content = f"Update the code to do this: {follow_up}\n\nCode:\n{code}"
            ai_temp = 0.3 # حرارة أعلى عشان يسمح له بالإبداع وكتابة كود جديد
        else:
            # 2. حالة التحليل الأولية: هنا بيشتغل كـ Compiler بيصلح الأخطاء بس
            sys_msg = (
                f"You are a Strict {lang} Compiler. "
                f"STRICT RULES:\n"
                f"1. Fix any syntax or logic errors.\n"
                f"2. Explain fixes in {target_lang}.\n"
                f"3. OUTPUT ONLY JSON format: {{\"explanation\": \"...\", \"result\": \"FIXED CODE HERE\", \"complexity\": \"...\"}}"
            )
            user_content = f"Task: {inquiry}\n\nCode:\n{code}"
            ai_temp = 0.1

        if not API_KEYS: 
            return JSONResponse(content={"explanation": "API Keys missing", "result": "// Error", "complexity": "N/A"})

        for key in random.sample(API_KEYS, len(API_KEYS)):
            try:
                r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json={
                        "model": "llama-3.3-70b-versatile", 
                        "messages": [
                            {"role": "system", "content": sys_msg}, 
                            {"role": "user", "content": user_content}
                        ], 
                        "response_format": {"type": "json_object"}, 
                        "temperature": ai_temp
                    }, timeout=15)
                
                resp_json = r.json()
                ai_reply = json.loads(resp_json['choices'][0]['message']['content'])
                return JSONResponse(content=ai_reply)
            except Exception as inner_e: 
                continue
                
        return JSONResponse(content={"explanation": "All API Keys failed", "result": "// Error", "complexity": "N/A"})
    except Exception as e: 
        return JSONResponse(content={"explanation": str(e), "result": "// Server Error", "complexity": "N/A"})
