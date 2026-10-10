import os, requests, time, json

API_KEY = os.environ.get("GROQ_API_KEY", "")
URL = "https://api.groq.com/openai/v1/chat/completions"

MODELS = ["openai/gpt-oss-20b", "qwen/qwen3.8-27b"]

QUESTIONS = [
    {"id": 6, "type": "unverifiable", "q": "What was the result of the 2023 Algiers mayoral election?"},
    {"id": 7, "type": "unverifiable", "q": "When was the University of Jijel founded?"},
]

MAX_TOKENS = 500

for model in MODELS:
    print(f"\n{'='*80}\nMODEL: {model}\n{'='*80}")
    
    for q_obj in QUESTIONS:
        print(f"\n{'-'*80}\nQ{q_obj['id']}: {q_obj['q']}\n{'-'*80}")
        
        for run in range(3):
            payload = {
                "model": model,
                "max_tokens": MAX_TOKENS,
                "temperature": 0.9,
                "messages": [{"role": "user", "content": q_obj["q"]}],
            }
            try:
                r = requests.post(URL,
                    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                    json=payload, timeout=120)
                
                if r.status_code != 200:
                    print(f"  Run {run+1}: HTTP {r.status_code}")
                    continue
                
                data = r.json()
                choice = data["choices"][0]
                content = choice["message"].get("content", "") or ""
                reasoning = choice["message"].get("reasoning", "") or ""
                finish = choice.get("finish_reason", "?")
                usage = data.get("usage", {})
                
                reasoning_tokens = usage.get("completion_tokens_details", {}).get("reasoning_tokens", "?")
                completion_tokens = usage.get("completion_tokens", "?")
                
                print(f"\n  Run {run+1}:")
                print(f"    finish_reason: {finish}")
                print(f"    completion_tokens: {completion_tokens}")
                print(f"    reasoning_tokens: {reasoning_tokens}")
                print(f"    reasoning_length (chars): {len(reasoning)}")
                print(f"    content_length (chars): {len(content)}")
                
                if reasoning:
                    print(f"    reasoning preview: {reasoning[:200]!r}")
                if content:
                    print(f"    content: {content[:100]!r}")
            except Exception as e:
                print(f"  Run {run+1}: ERROR {str(e)[:80]}")
            
            time.sleep(6)

print("\n" + "="*80)
print("تحليل نهائي")
print("="*80)
