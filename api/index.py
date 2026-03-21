from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import requests, os, json

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        with open("index.html", "r", encoding="utf-8") as f: return f.read()
    except: return "<h1>AetherCode AI is active.</h1>"

@app.post("/api/index")
async def site_fix(
    code: str = Form(""), lang: str = Form("python"), ui_lang: str = Form("ar"),
    inquiry: str = Form(""), error_log: str = Form(""), follow_up: str = Form("")
):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    target = "Arabic" if ui_lang == "ar" else "English"
    
    sys_msg = (
        f"You are AetherCode AI Master. Expert Debugger. "
        f"Return ONLY a valid JSON object: {{'explanation': '...', 'result': '...', 'complexity': 'Time: O(?), Space: O(?)'}}. "
        f"Explanation MUST be in {target}. Result MUST be clean executable {lang} code."
    )
    
    messages = [{"role": "system", "content": sys_msg}, {"role": "user", "content": f"Task: {inquiry}\nCode: {code}\nTerminal: {error_log}"}]
    if follow_up: messages.append({"role": "user", "content": f"Update: {follow_up}"})

    try:
        response = requests.post(url, json={"model": "llama-3.3-70b-versatile", "messages": messages, "response_format": {"type": "json_object"}}, headers=headers, timeout=25)
        # ضمان إرسال رد JSON نظيف للمتصفح
        return json.loads(response.json()['choices'][0]['message']['content'])
    except Exception as e:
        return {"explanation": "Server Error", "result": f"// Error: {str(e)}", "complexity": "N/A"}
