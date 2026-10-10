import os, requests, time, re

API_KEY = os.environ.get("GROQ_API_KEY", "")
URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "qwen/qwen3.8-27b"

QUESTIONS = [
    {"id": 1, "type": "factual", "q": "What is the capital of Japan?"},
    {"id": 7, "type": "unverifiable", "q": "When was the University of Jijel founded?"},
    {"id": 6, "type": "unverifiable", "q": "What was the result of the 2023 Algiers mayoral election?"},
]

MAX_TOKENS = 800

def query(question):
    payload = {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "temperature": 0.7,
        "messages": [{"role": "user", "content": question}],
    }
    r = requests.post(URL,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json=payload, timeout=120)
    return r.json()

PATTERNS = {
    "self_questioning": r"\?",
    "hedging": r"\b(maybe|perhaps|possibly|might|may|likely|probably|could|uncertain)\b",
    "fact_checking": r"\b(check|verify|confirm|actually|wait|let me|recall)\b",
    "date_search": r"\b(19|20)\d{2}\b",
    "self_correction": r"\b(no,|wait,|actually,|but)\b",
    "refusal_consideration": r"\b(can't|cannot|shouldn't|refuse|not allowed|policy|safety)\b",
}

for q_obj in QUESTIONS:
    print(f"\n{'='*80}")
    print(f"Q{q_obj['id']} ({q_obj['type']}): {q_obj['q']}")
    print('='*80)
    
    r = query(q_obj["q"])
    
    if "choices" not in r:
        print("ERROR:", r)
        continue
    
    choice = r["choices"][0]
    content = choice["message"].get("content", "") or ""
    reasoning = choice["message"].get("reasoning", "") or ""
    finish = choice.get("finish_reason", "?")
    usage = r.get("usage", {})
    completion_tokens = usage.get("completion_tokens", 0)
    reasoning_tokens = usage.get("completion_tokens_details", {}).get("reasoning_tokens", 0)
    
    print(f"\n  finish_reason: {finish}")
    print(f"  completion_tokens: {completion_tokens}")
    print(f"  reasoning_tokens: {reasoning_tokens}")
    print(f"  reasoning_length: {len(reasoning)} chars")
    print(f"  content_length: {len(content)} chars")
    print(f"\n  --- CONTENT (full) ---")
    print(content[:1500])
    print(f"  --- END CONTENT ---")
    
    if reasoning:
        print(f"\n  --- REASONING (full) ---")
        print(reasoning)
        print(f"  --- END REASONING ---")
    
    print(f"\n  --- PATTERNS (in content) ---")
    for name, pattern in PATTERNS.items():
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            print(f"    {name}: {len(matches)} matches")
    
    time.sleep(6)
