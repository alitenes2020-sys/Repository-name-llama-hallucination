import csv, json
from collections import Counter, defaultdict

rows = []
with open("study_v3.csv", "r", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        rows.append(row)

# 1. عدّ الردود الفارغة حسب النموذج
print("="*80)
print("1. الردود الفارغة حسب النموذج")
print("="*80)

empty_by_model = defaultdict(lambda: {"empty": 0, "total": 0, "error": 0})
for row in rows:
    model = row["model"]
    empty_by_model[model]["total"] += 1
    if row["error"]:
        empty_by_model[model]["error"] += 1
    elif not row["response"].strip():
        empty_by_model[model]["empty"] += 1

for model in sorted(empty_by_model.keys()):
    d = empty_by_model[model]
    pct = (d["empty"] / d["total"]) * 100
    print(f"{model}:")
    print(f"  إجمالي: {d['total']}")
    print(f"  فارغة: {d['empty']} ({pct:.1f}%)")
    print(f"  أخطاء: {d['error']}")

# 2. الردود الفارغة حسب نوع السؤال
print("\n" + "="*80)
print("2. الردود الفارغة حسب نوع السؤال")
print("="*80)

empty_by_type = defaultdict(lambda: defaultdict(int))
for row in rows:
    if row["error"]:
        continue
    model = row["model"]
    qid = int(row["question_id"])
    # تصنيف السؤال: واقعي (1-5) أو وهمي (6-10)
    q_type = "factual" if qid <= 5 else "unverifiable"
    if not row["response"].strip():
        empty_by_type[model][q_type] += 1

for model in sorted(empty_by_type.keys()):
    print(f"\n{model}:")
    for t in ["factual", "unverifiable"]:
        print(f"  {t}: {empty_by_type[model][t]} فارغة")

# 3. الردود الفارغة حسب رقم السؤال
print("\n" + "="*80)
print("3. الردود الفارغة حسب السؤال")
print("="*80)

empty_by_q = defaultdict(lambda: defaultdict(int))
for row in rows:
    if row["error"]:
        continue
    model = row["model"]
    qid = row["question_id"]
    if not row["response"].strip():
        empty_by_q[model][qid] += 1

for model in sorted(empty_by_q.keys()):
    print(f"\n{model}:")
    for qid in sorted(empty_by_q[model].keys(), key=int):
        print(f"  Q{qid}: {empty_by_q[model][qid]} فارغة")

# 4. مقارنة Q6-Q8 (الأسئلة الأكثر حساسية)
print("\n" + "="*80)
print("4. تحليل Q6-Q8 (الأسئلة الأكثر حساسية)")
print("="*80)

for qid in ["6", "7", "8"]:
    print(f"\nQ{qid}:")
    for row in rows:
        if row["question_id"] == qid:
            model = row["model"]
            resp = row["response"].strip()
            if not resp:
                resp = "[EMPTY]"
            print(f"  {model}: {resp[:80]!r}")
