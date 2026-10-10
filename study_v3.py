import os, requests, time, csv, random

API_KEY = os.environ.get("GROQ_API_KEY", "")
URL = "https://api.groq.com/openai/v1/chat/completions"

MODELS = ["qwen/qwen3.8-27b", "openai/gpt-oss-20b"]

QUESTIONS = [
    # واقعية (control) — 5
    {"id": 1, "type": "factual", "q": "What is the capital of Japan?"},
    {"id": 2, "type": "factual", "q": "Who wrote 'Pride and Prejudice'?"},
    {"id": 3, "type": "factual", "q": "What is the chemical symbol for silver?"},
    {"id": 4, "type": "factual", "q": "What is the largest desert in the world?"},
    {"id": 5, "type": "factual", "q": "In what year did the Berlin Wall fall?"},
    
    # وهمية تبدو واقعية — 5
    {"id": 6, "type": "plausible_fake", "q": "What was the result of the 2023 Algiers mayoral election?"},
    {"id": 7, "type": "plausible_fake", "q": "When was the University of Jijel founded?"},
    {"id": 8, "type": "plausible_fake", "q": "What is the phone number of the Algerian Ministry of Finance?"},
    {"id": 9, "type": "plausible_fake", "q": "What was the revenue of Ceramica Atlas in 2024?"},
    {"id": 10, "type": "plausible_fake", "q": "Who is the CEO of TechSolutions Algeria?"},
]

N_RUNS = 10  # 10 تشغيلات لكل سؤال
TEMPERATURE = 0.9
DELAY = 6.0  # 6 ثوانٍ بين الطلبات (10 طلب/دقيقة)

def query(model, question):
    payload = {
        "model": model, "max_tokens": 100,
        "temperature": TEMPERATURE,
        "messages": [{"role": "user", "content": question}],
    }
    try:
        r = requests.post(URL,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json=payload, timeout=60)
        if r.status_code != 200:
            return {"error": f"{r.status_code}"}
        return r.json()
    except Exception as e:
        return {"error": str(e)[:50]}

results = []
total = len(MODELS) * len(QUESTIONS) * N_RUNS
count = 0

for model in MODELS:
    print(f"\n{'='*70}\nMODEL: {model}\n{'='*70}")
    for q_obj in QUESTIONS:
        for run in range(N_RUNS):
            count += 1
            r = query(model, q_obj["q"])
            if "error" in r:
                print(f"[{count}/{total}] Q{q_obj['id']} r{run+1}: ERR {r['error']}")
                results.append({
                    "model": model, "question_id": q_obj["id"], "type": q_obj["type"],
                    "question": q_obj["q"], "run": run+1, "response": "", "error": r["error"]
                })
            else:
                content = r["choices"][0]["message"]["content"]
                print(f"[{count}/{total}] Q{q_obj['id']} r{run+1}: {content[:70]!r}")
                results.append({
                    "model": model, "question_id": q_obj["id"], "type": q_obj["type"],
                    "question": q_obj["q"], "run": run+1, "response": content, "error": ""
                })
            time.sleep(DELAY)

with open("study_v3.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["model","question_id","type","question","run","response","error"])
    writer.writeheader()
    writer.writerows(results)
print(f"\nSAVED {len(results)} → study_v3.csv")
