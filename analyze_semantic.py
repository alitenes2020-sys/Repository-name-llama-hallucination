import csv, re
from collections import Counter, defaultdict

rows = []
with open("study_v3.csv", "r", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        rows.append(row)

# الإجابات "الذهبية" لكل سؤال
GOLD = {
    "1": ["tokyo", "طوكيو"],
    "2": ["jane austen", "أوستن"],
    "3": ["ag", "الفضة"],
    "4": ["antarctic", "antarctica", "القطبية", "أنتاركتيكا"],
    "5": ["1989"],
}

def extract_core(response, qid):
    """استخراج الإجابة الجوهرية"""
    if not response.strip():
        return "__EMPTY__"
    
    text = response.lower()
    
    # للأسئلة الواقعية: ابحث عن الإجابة الذهبية
    if qid in GOLD:
        for ans in GOLD[qid]:
            if ans.lower() in text:
                return ans.lower()
        return "__UNKNOWN__"
    
    # للأسئلة الوهمية: صنّف
    refusal_keywords = ["no ", "not ", "cannot", "can't", "don't have",
                        "don't know", "no publicly", "does not exist",
                        "never", "fictional", "not possible", "impossible",
                        "no widely", "not a widely", "no recognized"]
    
    if any(k in text for k in refusal_keywords):
        return "__REFUSAL__"
    
    # استخرج السنة (للأسئلة التاريخية)
    year = re.search(r'\b(19|20)\d{2}\b', text)
    if year:
        return f"__YEAR_{year.group()}__"
    
    # أرقام هواتف
    phone = re.search(r'\+?\d{2,3}[\s\-]?\d{2,3}[\s\-]?\d{2,3}', text)
    if phone:
        return f"__PHONE_{phone.group()}__"
    
    return "__OTHER__"

# تحليل
analysis = defaultdict(lambda: defaultdict(list))
for row in rows:
    if row["error"]:
        continue
    model = row["model"]
    qid = row["question_id"]
    response = row["response"]
    core = extract_core(response, qid)
    analysis[model][qid].append(core)

print("="*100)
print(f"{'Model':<25} {'Q#':<5} {'n':<4} {'unique':<8} {'variance':<10} {'breakdown'}")
print("="*100)

for model in sorted(analysis.keys()):
    print(f"\n### {model}")
    total_var = 0
    count = 0
    for qid in sorted(analysis[model].keys(), key=int):
        cores = analysis[model][qid]
        n = len(cores)
        unique = set(cores)
        variance = len(unique) / n if n > 0 else 0
        total_var += variance
        count += 1
        
        breakdown = Counter(cores).most_common(3)
        breakdown_str = ", ".join(f"{k}={v}" for k, v in breakdown)
        
        print(f"{model:<25} Q{qid:<4} {n:<4} {len(unique):<8} {variance:<10.2f} {breakdown_str[:60]}")
    
    avg = total_var / count if count else 0
    print(f"  >>> متوسط الانحراف الدلالي: {avg:.3f}")

print("\n" + "="*100)
print("تحليل الأسئلة الوهمية (Q6-Q10):")
print("="*100)

for model in sorted(analysis.keys()):
    print(f"\n### {model}")
    hall_var = []
    for qid in ["6","7","8","9","10"]:
        if qid not in analysis[model]:
            continue
        cores = [c for c in analysis[model][qid] if c != "__EMPTY__"]
        if not cores:
            print(f"  Q{qid}: all empty")
            continue
        unique = set(cores)
        variance = len(unique) / len(cores)
        hall_var.append(variance)
        breakdown = Counter(cores).most_common(3)
        breakdown_str = ", ".join(f"{k}={v}" for k, v in breakdown)
        print(f"  Q{qid}: n={len(cores)}, unique={len(unique)}, var={variance:.2f} | {breakdown_str[:70]}")
    
    if hall_var:
        print(f"  >>> متوسط انحراف الوهمية: {sum(hall_var)/len(hall_var):.3f}")
