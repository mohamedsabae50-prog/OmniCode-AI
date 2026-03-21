from fastapi import FastAPI, Form, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import requests, os, json

app = FastAPI(title="AetherCode AI API", version="5.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# مفاتيح المطورين (تقدر تطلبها من صفحة الـ API Docs مستقبلاً)
DEVELOPER_KEYS = {"admin": "ae-master-777", "tester": "ae-test-123"}
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

async def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key not in DEVELOPER_KEYS.values():
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        with open("index.html", "r", encoding="utf-8") as f: return f.read()
    except: return "<h1>AetherCode AI is active. index.html missing.</h1>"

# مسار المطورين (JSON)
@app.post("/api/v1/fix")
async def dev_fix(code: str, lang: str, inquiry: str = "Fix code", key: str = Depends(verify_api_key)):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    sys_msg = f"Fix {lang} code. Return ONLY JSON: {{'explanation': '...', 'result': '...', 'complexity': '...'}}"
    messages = [{"role": "system", "content": sys_msg}, {"role": "user", "content": f"Task: {inquiry}\nCode: {code}"}]
    try:
        response = requests.post(url, json={"model": "llama-3.3-70b-versatile", "messages": messages, "response_format": {"type": "json_object"}}, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except: return {"error": "API Error"}

# مسار الموقع (Form Data) - ده اللي بيحل الـ Connection Error
@app.post("/api/index")
async def site_fix(
    code: str = Form(None), 
    lang: str = Form(...), 
    ui_lang: str = Form(...),
    inquiry: str = Form(None), 
    error_log: str = Form(None), 
    follow_up: str = Form(None)
):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    target = "Arabic" if ui_lang == "ar" else "English"
    sys_msg = (
        f"You are AetherCode AI Master. Surgical Debugger. "
        f"Return ONLY JSON: {{'explanation': '...', 'result': '...', 'complexity': 'Time: O(?), Space: O(?)'}}. "
        f"Explanation in {target}. Result must be clean executable code."
    )
    # تجميع السياق
    content = f"Task: {inquiry}\nCode: {code}\nError: {error_log}"
    messages = [{"role": "system", "content": sys_msg}, {"role": "user", "content": content}]
    if follow_up: messages.append({"role": "user", "content": f"Instruction: {follow_up}"})

    try:
        response = requests.post(url, json={"model": "llama-3.3-70b-versatile", "messages": messages, "response_format": {"type": "json_object"}}, headers=headers, timeout=25)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return {"explanation": "Server Error", "result": f"// Error: {str(e)}", "complexity": "N/A"}
