import os, requests, time, json, csv, re

API_KEY = os.environ.get("GROQ_API_KEY", "")
URL = "https://api.groq.com/openai/v1/chat/completions"

if not API_KEY:
    print("ERROR: GROQ_API_KEY not set.")
    exit()

MODELS = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-20b",
]

QUESTIONS = [
    # فئة A: واقعية (لها إجابة معروفة)
    {"id": 1, "type": "factual", "q": "What is the capital of France?"},
    {"id": 2, "type": "factual", "q": "Who wrote the play Hamlet?"},
    {"id": 3, "type": "factual", "q": "What is the boiling point of water in Celsius at sea level?"},
    {"id": 4, "type": "factual", "q": "In what year did World War II end?"},
    {"id": 5, "type": "factual", "q": "Who painted the Mona Lisa?"},
    {"id": 6, "type": "factual", "q": "What is the chemical symbol for gold?"},
    {"id": 7, "type": "factual", "q": "How many continents are there on Earth?"},
    {"id": 8, "type": "factual", "q": "What is the largest ocean on Earth?"},
    {"id": 9, "type": "factual", "q": "Who was the first person to walk on the Moon?"},
    {"id": 10, "type": "factual", "q": "What is the speed of light in a vacuum (in km/s)?"},
    # فئة B: غامضة (لا إجابة معروفة)
    {"id": 11, "type": "obscure", "q": "What was the exact revenue of Company Atlas in Algeria in 2023?"},
    {"id": 12, "type": "obscure", "q": "Who was the 47th president of the United States?"},
    {"id": 13, "type": "obscure", "q": "What is the phone number of the mayor of Tizi Ouzou?"},
    {"id": 14, "type": "obscure", "q": "What did I eat for breakfast on January 1, 2000?"},
    {"id": 15, "type": "obscure", "q": "How many grains of sand are on Jijel beach in Algeria?"},
    {"id": 16, "type": "obscure", "q": "What is the exact number of cats in Paris right now?"},
    {"id": 17, "type": "obscure", "q": "Who is the current CEO of a company called Nexara Systems?"},
    {"id": 18, "type": "obscure", "q": "What is the Wi-Fi password of the Algiers airport?"},
    {"id": 19, "type": "obscure", "q": "What is the middle name of my neighbor?"},
    {"id": 20, "type": "obscure", "q": "How many steps did I take yesterday?"},
]

N_RUNS = 3
TEMPERATURE = 0.7

def query(model, question):
    payload = {
        "model": model,
        "max_tokens": 150,
        "temperature": TEMPERATURE,
        "messages": [{"role": "user", "content": question}],
    }
    try:
        r = requests.post(
            URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )
        if r.status_code != 200:
            return {"error": f"HTTP {r.status_code}: {r.text[:150]}"}
        return r.json()
    except Exception as e:
        return {"error": str(e)}

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
                print(f"[{count}/{total}] Q{q_obj['id']} r{run+1}: ERROR {r['error'][:60]}")
                results.append({
                    "model": model, "question_id": q_obj["id"],
                    "type": q_obj["type"], "question": q_obj["q"],
                    "run": run + 1, "response": "", "error": r["error"],
                })
                continue
            content = r["choices"][0]["message"]["content"]
            print(f"[{count}/{total}] Q{q_obj['id']} r{run+1}: {content[:70]!r}")
            results.append({
                "model": model, "question_id": q_obj["id"],
                "type": q_obj["type"], "question": q_obj["q"],
                "run": run + 1, "response": content, "error": "",
            })
            time.sleep(1.5)  # احترام rate limit

with open("study_results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["model","question_id","type","question","run","response","error"])
    writer.writeheader()
    writer.writerows(results)

print(f"\n{'='*70}\nSAVED {len(results)} responses → study_results.csv\n{'='*70}")
