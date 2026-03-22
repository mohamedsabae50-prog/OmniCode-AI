import os, requests, json, random
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# سحب المفاتيح وتأمينها
RAW_KEYS = os.getenv("GROQ_API_KEYS", "")
API_KEYS = [k.strip() for k in RAW_KEYS.split(",") if k.strip()]

@app.get("/")
async def read_root():
    # البحث عن ملف HTML في كل المسارات الممكنة لـ Vercel
    paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "index.html"),
        os.path.join(os.getcwd(), "index.html"),
        "/var/task/index.html"
    ]
    for p in paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Site Online</h1><p>Frontend file not located. Check paths.</p>")

@app.post("/api/index")
async def fix_code(request: Request):
    try:
        data = await request.json()
        code, lang = data.get("code", ""), data.get("lang", "Python")
        ui_lang, inquiry = data.get("ui_lang", "ar"), data.get("inquiry", "Fix")
        follow_up = data.get("follow_up", "")
        
        target_lang = "Arabic" if ui_lang == "ar" else "English"
        
        # الأوامر الصارمة جداً
        sys_msg = (
            f"ACT AS A {lang} COMPILER. "
            f"1. FORBIDDEN to use C/C++ unless selected. 2. Output MUST be {lang}. "
            f"3. Return ONLY JSON: {{'explanation': '...', 'result': '...', 'complexity': '...'}} "
            f"4. Explanation in {target_lang}."
        )
        
        user_content = f"STRICT MODE: {lang}\nREQUEST: {follow_up}\nCODE:\n{code}" if follow_up else f"TASK: {inquiry}\nCODE:\n{code}"

        if not API_KEYS:
            return JSONResponse(content={"explanation": "خطأ: مفاتيح الـ API غير موجودة في Vercel Settings", "result": "// Error"}, status_code=200)

        for key in random.sample(API_KEYS, len(API_KEYS)):
            try:
                r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json={
                        "model": "llama-3.3-70b-versatile", 
                        "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": user_content}], 
                        "response_format": {"type": "json_object"}, 
                        "temperature": 0.1
                    }, timeout=15)
                return JSONResponse(content=json.loads(r.json()['choices'][0]['message']['content']))
            except: continue
            
        return JSONResponse(content={"explanation": "فشلت جميع المحاولات، تأكد من صحة المفاتيح", "result": "// API Error"}, status_code=200)
    except Exception as e:
        # بدل ما يرمي 500، هيرجع لنا رسالة الخطأ في صندوق الشرح عشان نفهمها
        return JSONResponse(content={"explanation": f"System Error: {str(e)}", "result": "// Logic Error"}, status_code=200)
