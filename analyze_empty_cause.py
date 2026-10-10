import os, requests, json, time

API_KEY = os.environ.get("GROQ_API_KEY", "")
URL = "https://api.groq.com/openai/v1/chat/completions"

# الأسئلة التي أنتجت ردودًا فارغة
QUESTIONS = [
    "What was the result of the 2023 Algiers mayoral election?",
    "When was the University of Jijel founded?",
    "What is the phone number of the Algerian Ministry of Finance?",
    "What was the revenue of Ceramica Atlas in 2024?",
    "Who is the CEO of TechSolutions Algeria?",
]

print("="*80)
print("تحليل سبب الردود الفارغة — GPT-OSS 20B")
print("="*80)

for i, q in enumerate(QUESTIONS, 1):
    print(f"\n{'─'*80}")
    print(f"Q{i}: {q}")
    print('─'*80)
    
    # 3 محاولات بنفس السؤال
    for run in range(3):
        payload = {
            "model": "openai/gpt-oss-20b",
            "max_tokens": 300,  # زيادة max_tokens
            "temperature": 0.7,
            "messages": [{"role": "user", "content": q}],
        }
        try:
            r = requests.post(URL,
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                json=payload, timeout=60)
            
            data = r.json()
            
            if r.status_code != 200:
                print(f"  Run {run+1}: HTTP {r.status_code} — {r.text[:100]}")
                continue
            
            choice = data["choices"][0]
            content = choice["message"].get("content", "")
            finish = choice.get("finish_reason", "?")
            usage = data.get("usage", {})
            
            print(f"  Run {run+1}:")
            print(f"    content: {content[:100]!r}")
            print(f"    content_length: {len(content)}")
            print(f"    finish_reason: {finish}")
            print(f"    completion_tokens: {usage.get('completion_tokens', '?')}")
            print(f"    reasoning: {choice['message'].get('reasoning', 'None')[:100] if choice['message'].get('reasoning') else 'None'}")
        except Exception as e:
            print(f"  Run {run+1}: ERROR {str(e)[:80]}")
        
        time.sleep(4)

print("\n" + "="*80)
print("تحليل: هل الرد الفارغ يتغير مع max_tokens؟")
print("="*80)

# نفس السؤال بـ max_tokens مختلفة
test_q = "When was the University of Jijel founded?"

for max_tok in [50, 100, 300, 500]:
    payload = {
        "model": "openai/gpt-oss-20b",
        "max_tokens": max_tok,
        "temperature": 0.7,
        "messages": [{"role": "user", "content": test_q}],
    }
    r = requests.post(URL,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json=payload, timeout=60)
    data = r.json()
    if r.status_code == 200:
        content = data["choices"][0]["message"].get("content", "")
        finish = data["choices"][0].get("finish_reason", "?")
        print(f"  max_tokens={max_tok}: len={len(content)}, finish={finish}, content={content[:60]!r}")
    time.sleep(4)

print("\n" + "="*80)
print("تحليل: هل system prompt يغير السلوك؟")
print("="*80)

# جرّب system prompt مختلف
test_q = "When was the University of Jijel founded?"

SYSTEM_PROMPTS = [
    None,
    "You are a helpful assistant. Always provide an answer.",
    "If you don't know the answer, say 'I don't know' clearly.",
    "Answer every question with a specific fact. Do not refuse.",
]

for sp in SYSTEM_PROMPTS:
    messages = []
    if sp:
        messages.append({"role": "system", "content": sp})
    messages.append({"role": "user", "content": test_q})
    
    payload = {
        "model": "openai/gpt-oss-20b",
        "max_tokens": 300,
        "temperature": 0.7,
        "messages": messages,
    }
    r = requests.post(URL,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json=payload, timeout=60)
    data = r.json()
    if r.status_code == 200:
        content = data["choices"][0]["message"].get("content", "")
        print(f"  SP={sp[:40] if sp else 'None'}...")
        print(f"    → {content[:100]!r}")
    time.sleep(4)
