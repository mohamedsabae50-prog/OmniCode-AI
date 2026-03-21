from fastapi import FastAPI, Form, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import requests, os, json

app = FastAPI(title="AetherCode AI Master API")

# السماح بجميع الاتصالات لضمان عدم حدوث بلوك
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DEVELOPER_KEYS = {"admin": "ae-master-777", "tester": "ae-test-123"}
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        with open("index.html", "r", encoding="utf-8") as f: return f.read()
    except: return "<h1>AetherCode AI is active.</h1>"

# --- المسار الأساسي الوحيد للموقع (تأكد من مطابقة الـ Form Data) ---
@app.post("/api/index")
async def site_fix(
    code: str = Form(""), 
    lang: str = Form("Python"), 
    ui_lang: str = Form("ar"),
    inquiry: str = Form("Fix code"), 
    error_log: str = Form(""), 
    follow_up: str = Form("")
):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    target = "Arabic" if ui_lang == "ar" else "English"
    
    sys_msg = (
        f"You are AetherCode AI Master. Expert Debugger. "
        f"Return ONLY JSON: {{'explanation': '...', 'result': '...', 'complexity': 'Time: O(?), Space: O(?)'}}. "
        f"Explanation in {target}. Result must be clean executable {lang} code."
    )
    
    messages = [{"role": "system", "content": sys_msg}, {"role": "user", "content": f"Task: {inquiry}\nCode: {code}\nError: {error_log}"}]
    if follow_up: messages.append({"role": "user", "content": f"Instruction: {follow_up}"})

    try:
        response = requests.post(url, json={"model": "llama-3.3-70b-versatile", "messages": messages, "response_format": {"type": "json_object"}}, headers=headers, timeout=25)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return {"explanation": "خطأ في الاتصال بالسيرفر.", "result": f"// Error: {str(e)}", "complexity": "N/A"}
