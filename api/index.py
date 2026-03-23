@app.post("/api/index")
async def fix_code(request: Request):
    try:
        data = await request.json()
        code = data.get("code", "")
        lang = data.get("lang", "Python")
        ui_lang = data.get("ui_lang", "ar")
        inquiry = data.get("inquiry", "Fix this code")
        follow_up = data.get("follow_up", "")
        
        target_lang = "Arabic" if ui_lang == "ar" else "English"
        
        # 🎯 السر هنا: بنحدد للذكاء الاصطناعي هل ده كود جديد ولا تعديل بناءً على طلبك
        if follow_up.strip():
            action_prompt = f"MODIFY the code based on this specific user request: '{follow_up}'"
        else:
            action_prompt = f"FIX and OPTIMIZE this code based on: '{inquiry}'"

        # أوامر صارمة لمنع الأخطاء في عرض الكود
        sys_msg = (
            f"You are a Senior {lang} Developer. "
            f"RULE 1: 'explanation' MUST be written in {target_lang}. "
            f"RULE 2: 'result' MUST contain ONLY the pure valid {lang} code. NO markdown formatting, NO backticks (```), NO extra text. "
            f"Return ONLY a valid JSON object exactly like this: {{\"explanation\": \"...\", \"result\": \"...\", \"complexity\": \"O(...)\"}}"
        )

        if not API_KEYS: 
            return JSONResponse(content={"explanation": "تأكد من وضع مفاتيح API", "result": "// Missing Keys", "complexity": "N/A"})

        for key in random.sample(API_KEYS, len(API_KEYS)):
            try:
                r = requests.post("[https://api.groq.com/openai/v1/chat/completions](https://api.groq.com/openai/v1/chat/completions)",
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json={
                        "model": "llama-3.3-70b-versatile", 
                        "messages": [
                            {"role": "system", "content": sys_msg}, 
                            {"role": "user", "content": f"{action_prompt}\n\nCODE:\n{code}"}
                        ], 
                        "response_format": {"type": "json_object"}, 
                        "temperature": 0.2 # حرارة مناسبة عشان يكون مبدع في التعديل بس دقيق في الكود
                    }, timeout=15)
                
                response_data = r.json()
                ai_content = json.loads(response_data['choices'][0]['message']['content'])
                return JSONResponse(content=ai_content)
            except: 
                continue # لو المفتاح ده فشل، جرب اللي بعده
                
        return JSONResponse(content={"explanation": "فشلت جميع محاولات الاتصال بالخادم", "result": "// Connection Error", "complexity": "N/A"})
    except Exception as e:
        return JSONResponse(content={"explanation": f"حدث خطأ في النظام: {str(e)}", "result": "// System Error", "complexity": "N/A"})
