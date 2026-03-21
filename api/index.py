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
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "<h1>AetherCode AI: index.html not found!</h1>"

@app.post("/api/index")
async def fix_code(
    code: str = Form(None), 
    lang: str = Form(...),  
    ui_lang: str = Form(...),  
    inquiry: str = Form(None),  
    error_log: str = Form(None),
    follow_up: str = Form(None)
):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    target_lang = "Arabic" if ui_lang == "ar" else "English"

    sys_msg = (
        f"You are AetherCode AI Master. Expert Software Engineer. "
        f"RULES: 1. Return ONLY valid JSON: {{'explanation': '...', 'result': '...', 'complexity': 'Time: O(?), Space: O(?)'}}. "
        f"2. Explanation MUST be in {target_lang}. 3. 'result' field MUST be the clean fixed {lang} code ONLY. "
        f"4. If 'follow_up' is provided, treat it as a human instruction to modify the code."
    )

    messages = [{"role": "system", "content": sys_msg}, {"role": "user", "content": f"Task: {inquiry}\nCode: {code}\nTerminal: {error_log}"}]
    if follow_up: messages.append({"role": "user", "content": f"Instruction: {follow_up}"})

    try:
        response = requests.post(url, json={"model": "llama-3.3-70b-versatile", "messages": messages, "response_format": {"type": "json_object"}}, headers=headers, timeout=25)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return {"explanation": "Connection Error", "result": f"// Error: {str(e)}", "complexity": "N/A"}
