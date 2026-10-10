import os, requests, time, csv

API_KEY = os.environ.get("GROQ_API_KEY", "")
URL = "https://api.groq.com/openai/v1/chat/completions"

MODEL = "qwen/qwen3.8-27b"

# نفس أسئلة GPT-OSS v4 (للمقارنة المباشرة)
QUESTIONS = [
    {"id": 1, "type": "factual", "q": "What is the capital of Japan?"},
    {"id": 2, "type": "factual", "q": "Who wrote 'Pride and Prejudice'?"},
    {"id": 6, "type": "unverifiable", "q": "What was the result of the 2023 Algiers mayoral election?"},
    {"id": 7, "type": "unverifiable", "q": "When was the University of Jijel founded?"},
    {"id": 8, "type": "unverifiable", "q": "What is the phone number of the Algerian Ministry of Finance?"},
]

N_RUNS = 5
TEMPERATURE = 0.9
DELAY = 6.0
MAX_TOKENS = 500

def query(model, question):
    payload = {
        "model": model, "max_tokens": MAX_TOKENS,
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

results = []
total = len(QUESTIONS) * N_RUNS
count = 0

print(f"\n{'='*70}\nMODEL: {MODEL} (max_tokens={MAX_TOKENS})\n{'='*70}")

for q_obj in QUESTIONS:
    for run in range(N_RUNS):
        count += 1
        r = query(MODEL, q_obj["q"])
        if "error" in r:
            print(f"[{count}/{total}] Q{q_obj['id']} r{run+1}: ERR")
            results.append({
                "model": MODEL, "question_id": q_obj["id"], "type": q_obj["type"],
                "question": q_obj["q"], "run": run+1, "response": "", "error": r["error"]
            })
        else:
            choice = r["choices"][0]
            content = choice["message"].get("content", "")
            finish = choice.get("finish_reason", "?")
            print(f"[{count}/{total}] Q{q_obj['id']} r{run+1}: [{finish}] {content[:90]!r}")
            results.append({
                "model": MODEL, "question_id": q_obj["id"], "type": q_obj["type"],
                "question": q_obj["q"], "run": run+1, "response": content, "error": ""
            })
        time.sleep(DELAY)

with open("qwen_v4.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["model","question_id","type","question","run","response","error"])
    writer.writeheader()
    writer.writerows(results)
print(f"\nSAVED {len(results)} → qwen_v4.csv")
