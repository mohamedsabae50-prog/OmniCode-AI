from fastapi import FastAPI, Form, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import requests, os

app = FastAPI(title="AetherCode Developer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 قائمة المفاتيح المسموح لها (ممكن تنقلها لقاعدة بيانات مستقبلاً)
VALID_KEYS = {
    "mohamed_hamdy_dev": "ae-77-master-key",
    "guest_user": "ae-guest-123"
}

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# دالة للتحقق من الهوية
async def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key not in VALID_KEYS.values():
        raise HTTPException(status_code=401, detail="Invalid API Key. Get your key from AetherCode.")
    return x_api_key

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("index.html", "r", encoding="utf-8") as f: return f.read()

# --- مسار الـ API الجديد للمطورين ---
@app.post("/api/v1/fix")
async def developer_api_fix(
    code: str, 
    lang: str, 
    inquiry: str = "Fix this code", 
    key: str = Depends(verify_api_key)
):
    """
    أهلاً بك في AetherCode API. 
    هذا المسار مخصص للمطورين لاستخدام محرك التصحيح في تطبيقاتهم الخاصة.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    sys_msg = f"You are AetherCode AI Engine. Fix {lang} code. Return ONLY JSON: {{'explanation': '...', 'result': '...'}}"
    messages = [{"role": "system", "content": sys_msg}, {"role": "user", "content": f"Task: {inquiry}\nCode: {code}"}]

    try:
        response = requests.post(url, json={"model": "llama-3.3-70b-versatile", "messages": messages, "response_format": {"type": "json_object"}}, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except:
        return {"error": "Aether Engine is busy."}

# المسار الأصلي للموقع (شغال زي ما هو)
@app.post("/api/index")
async def site_fix(code: str = Form(None), lang: str = Form(...), ui_lang: str = Form(...), inquiry: str = Form(None)):
    # الكود اللي عندك في index.py بيفضل زي ما هو عشان الموقع ميتأثرش
    pass
