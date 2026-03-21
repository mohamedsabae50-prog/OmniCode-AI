from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import requests, os, json

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@app.post("/api/index")
async def site_fix(
    code: str = Form(""), lang: str = Form("python"), ui_lang: str = Form("ar"),
    inquiry: str = Form(""), error_log: str = Form(""), follow_up: str = Form("")
):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    target = "Arabic" if ui_lang == "ar" else "English"
    
    # تحسين الـ Prompt لضمان دقة الكود المصلح
    sys_msg = (
        f"You are a strict code repair engine. "
        f"1. Fix the provided {lang} code based ONLY on the user intent and error. "
        f"2. DO NOT change variable names or logic unless they are part of the error. "
        f"3. Return ONLY a JSON object: {{'explanation': '...', 'result': '...', 'complexity': '...'}}. "
        f"4. Explanation must be in {target}."
    )
    
    messages = [{"role": "system", "content": sys_msg}, {"role": "user", "content": f"Code to fix: {code}\nError: {error_log}\nIntent: {inquiry}"}]
    if follow_up: messages.append({"role": "user", "content": f"Additional Instruction: {follow_up}"})

    try:
        response = requests.post(url, json={"model": "llama-3.3-70b-versatile", "messages": messages, "response_format": {"type": "json_object"}}, headers=headers, timeout=25)
        return json.loads(response.json()['choices'][0]['message']['content'])
    except:
        return {"explanation": "Error", "result": "// Fail", "complexity": "N/A"}
