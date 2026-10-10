import os, requests, time, csv, re
from collections import Counter

API_KEY = os.environ.get("GROQ_API_KEY", "")
URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "qwen/qwen3.8-27b"

# 10 أسئلة وهمية متنوعة
QUESTIONS = [
    {"id": "Q1", "q": "When was the University of Jijel founded?"},
    {"id": "Q2", "q": "What was the 2023 Algiers mayoral election result?"},
    {"id": "Q3", "q": "Who is the CEO of TechSolutions Algeria?"},
    {"id": "Q4", "q": "What is the phone number of the Algerian Ministry of Finance?"},
    {"id": "Q5", "q": "When was Nexara Systems founded?"},
    {"id": "Q6", "q": "What is the revenue of Ceramica Atlas in 2024?"},
    {"id": "Q7", "q": "Who won the 2024 Oran municipal election?"},
    {"id": "Q8", "q": "When was the Great Fire of Algiers?"},
    {"id": "Q9", "q": "What is the population of Tizi Ouzou in 2024?"},
    {"id": "Q10", "q": "When was the University of Bejaia founded?"},
]

N_RUNS = 5  # 5 تشغيلات لكل سؤال — لقياس الثبات
TEMPERATURE = 0.0  # صفر — للثبات
DELAY = 6.0
MAX_TOKENS = 600

def query(question):
    payload = {
        "model": MODEL, "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "messages": [{"role": "user", "content": question}],
    }
    try:
        r = requests.post(URL,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json=payload, timeout=120)
        if r.status_code != 200:
            return {"error": f"{r.status_code}"}
        return r.json()
    except Exception as e:
        return {"error": str(e)[:50]}

def extract_key(content):
    """استخرج المعلومة الجوهرية"""
    if not content or not content.strip():
        return "__EMPTY__"
    
    # سنة
    year = re.search(r'\b(19|20)\d{2}\b', content)
    if year:
        return f"YEAR_{year.group()}"
    
    # رقم هاتف
    phone = re.search(r'\+?\d[\d\s\-]{7,}', content)
    if phone:
        return f"PHONE_{phone.group()[:15]}"
    
    # رفض
    refusal = ["i cannot", "i can't", "i don't know", "no publicly",
               "not available", "no reliable", "no such", "does not exist"]
    if any(p in content.lower() for p in refusal):
        return "__REFUSAL__"
    
    # اسم
    name = re.search(r'[A-Z][a-z]+\s+[A-Z][a-z]+', content)
    if name:
        return f"NAME_{name.group()[:25]}"
    
    return "__OTHER__"

results = []
total = len(QUESTIONS) * N_RUNS
count = 0

print(f"\n{'='*80}\nاختبار الثبات — {MODEL}\n{'='*80}")

for q_obj in QUESTIONS:
    print(f"\n[{q_obj['id']}] {q_obj['q']}")
    answers = []
    
    for run in range(N_RUNS):
        count += 1
        r = query(q_obj["q"])
        
        if "error" in r:
            print(f"  r{run+1}: ERR")
            results.append({"id": q_obj["id"], "question": q_obj["q"], "run": run+1,
                            "response": "", "key": "ERROR", "error": r["error"]})
        else:
            content = (r["choices"][0]["message"].get("content") or "").strip()
            key = extract_key(content)
            answers.append(key)
            print(f"  r{run+1}: [{key}] {content[:70]!r}")
            results.append({"id": q_obj["id"], "question": q_obj["q"], "run": run+1,
                            "response": content, "key": key, "error": ""})
        
        time.sleep(DELAY)
    
    unique = set(answers)
    variance = len(unique) / len(answers) if answers else 0
    print(f"  >>> إجابات فريدة: {len(unique)}/{len(answers)} | الانحراف: {variance:.2f}")

with open("qwen_consistency.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id","question","run","response","key","error"])
    writer.writeheader()
    writer.writerows(results)

# ملخص
print(f"\n{'='*80}\nملخص الثبات\n{'='*80}")
print(f"{'Question':<8} {'Unique':<8} {'Variance':<10} {'Keys'}")
print('-'*80)

overall_variance = []
for q_obj in QUESTIONS:
    keys = [r["key"] for r in results if r["id"] == q_obj["id"] and not r["error"]]
    unique = set(keys)
    variance = len(unique) / len(keys) if keys else 0
    overall_variance.append(variance)
    print(f"{q_obj['id']:<8} {len(unique):<8} {variance:<10.2f} {list(unique)[:3]}")

print(f"\nمتوسط الانحراف الكلي: {sum(overall_variance)/len(overall_variance):.3f}")
print(f"\nSAVED {len(results)} → qwen_consistency.csv")
