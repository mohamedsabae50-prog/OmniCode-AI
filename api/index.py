@app.post("/api/index")
async def fix_code(request: Request):
    try:
        data = await request.json()
        code = data.get("code", "")
        lang = data.get("lang", "Python")
        ui_lang = data.get("ui_lang", "ar")
        inquiry = data.get("inquiry", "")
        follow_up = data.get("follow_up", "")
        
        target_lang = "Arabic" if ui_lang == "ar" else "English"
        
        # 🎯 السحر هنا: بنغير شخصية الذكاء الاصطناعي بناءً على زرار "تحديث"
        if follow_up.strip():
            sys_role = f"You are an Expert {lang} Developer. You MUST add, remove, or modify the code exactly as the user requests."
            user_prompt = f"USER UPDATE REQUEST: {follow_up}\n\nCURRENT CODE:\n{code}\n\nRewrite the code to completely fulfill the user's update request."
        else:
            sys_role = f"You are a Strict {lang} Compiler. You MUST fix errors, convert syntax to {lang}, and optimize."
            user_prompt = f"INQUIRY: {inquiry}\n\nCODE TO FIX:\n{code}\n\nFix the code."

        # أوامر صارمة لضمان النتيجة
        sys_msg = (
            f"{sys_role} "
            f"RULE 1: 'explanation' MUST be in {target_lang}. "
            f"RULE 2: 'result' MUST contain ONLY the pure valid {lang} code. NO markdown formatting. NO backticks. "
            f"Return ONLY JSON: {{\"explanation\": \"...\", \"result\": \"...\", \"complexity\": \"O(...)\"}}"
        )

        if not API_KEYS: return JSONResponse(content={"explanation": "API Keys missing", "result": "// Error", "complexity": "N/A"})

        for key in random.sample(API_KEYS, len(API_KEYS)):
            try:
                r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json={
                        "model": "llama-3.3-70b-versatile", 
                        "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": user_prompt}], 
                        "response_format": {"type": "json_object"}, "temperature": 0.2
                    }, timeout=15)
                return JSONResponse(content=json.loads(r.json()['choices'][0]['message']['content']))
            except: continue
        return JSONResponse(content={"explanation": "فشلت المفاتيح", "result": "// Error", "complexity": "N/A"})
    except Exception as e: return JSONResponse(content={"explanation": str(e), "result": "// Error", "complexity": "N/A"})
