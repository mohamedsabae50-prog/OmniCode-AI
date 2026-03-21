from fastapi import FastAPI, Form, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import requests, os, json

app = FastAPI(
    title="AetherCode AI Developer API",
    description="محرك التصحيح الجراحي المخصص للمطورين",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 نظام إدارة مفاتيح المطورين (يمكنك إضافة مفاتيح هنا)
DEVELOPER_KEYS = {
    "mohamed_master": "ae-master-777",
    "alpha_tester": "ae-test-123"
}

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

async def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key not in DEVELOPER_KEYS.values():
        raise HTTPException(status_code=401, detail="Invalid API Key. Access Denied.")
    return x_api_key

@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "<h1>AetherCode AI is Running. index.html not found.</h1>"

# --- 1. مسار المطورين (Developer API Endpoint) ---
@app.post("/api/v1/fix")
async def developer_api_fix(
    code: str, 
    lang: str, 
    inquiry: str = "Fix this code", 
    key: str = Depends(verify_api_key)
):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    sys_msg = (
        f"You are AetherCode AI Engine. Surgical Debugger. "
        f"Return ONLY valid JSON: {{'explanation': '...', 'result': '...', 'complexity': '...'}}. "
        f"Result must be clean {lang} code."
    )
    
    messages = [{"role": "system", "content": sys_msg}, {"role": "user", "content": f"Task: {inquiry}\nCode: {code}"}]
    
    try:
        response = requests.post(url, json={"model": "llama-3.3-70b-versatile", "messages": messages, "response_format": {"type": "json_object"}}, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except:
        return {"error": "Aether Engine connection failed."}

# --- 2. مسار الموقع الأساسي (UI Endpoint) ---
@app.post("/api/index")
async def site_fix(
    code: str = Form(None), lang: str = Form(...), ui_lang: str = Form(...),
    inquiry: str = Form(None), error_log: str = Form(None), follow_up: str = Form(None)
):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    target_lang = "Arabic" if ui_lang == "ar" else "English"

    sys_msg = (
        f"You are AetherCode AI Master. Surgical Debugger. "
        f"RULES: 1. Return ONLY JSON: {{'explanation': '...', 'result': '...', 'complexity': 'Time: O(?), Space: O(?)'}}. "
        f"2. Explanation in {target_lang}. 3. Result MUST be clean executable {lang} code."
    )

    messages = [{"role": "system", "content": sys_msg}, {"role": "user", "content": f"Task: {inquiry}\nCode: {code}\nError: {error_log}"}]
    if follow_up: messages.append({"role": "user", "content": f"Update: {follow_up}"})

    try:
        response = requests.post(url, json={"model": "llama-3.3-70b-versatile", "messages": messages, "response_format": {"type": "json_object"}, "temperature": 0.1}, headers=headers, timeout=25)
        return response.json()['choices'][0]['message']['content']
    except:
        return {"explanation": "خطأ في الاتصال بالسيرفر.", "result": "// API Error", "complexity": "N/A"}
