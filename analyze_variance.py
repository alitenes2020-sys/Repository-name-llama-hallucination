import csv, re
from collections import Counter, defaultdict

# قراءة البيانات
rows = []
with open("study_v3.csv", "r", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        rows.append(row)

def normalize(text):
    """تطبيع النص للمقارنة"""
    t = text.strip().lower()
    t = re.sub(r'\*\*|\*|#|`', '', t)  # إزالة تنسيق markdown
    t = re.sub(r'\s+', ' ', t)
    # أخذ أول 100 حرف فقط
    return t[:100]

def extract_year(text):
    """استخراج سنة من النص"""
    m = re.search(r'\b(19|20)\d{2}\b', text)
    return m.group() if m else None

# تحليل حسب النموذج والسؤال
analysis = defaultdict(lambda: defaultdict(list))

for row in rows:
    model = row["model"]
    qid = row["question_id"]
    response = row["response"].strip()
    
    if row["error"]:
        continue  # تجاهل الأخطاء
    
    if not response:
        analysis[model][qid].append("__EMPTY__")
    else:
        analysis[model][qid].append(response)

# حساب الانحراف لكل سؤال
print("="*90)
print(f"{'Model':<25} {'Q#':<5} {'n':<4} {'unique':<8} {'variance':<10} {'most_common'}")
print("="*90)

for model in sorted(analysis.keys()):
    print(f"\n### {model}")
    total_var = 0
    count = 0
    for qid in sorted(analysis[model].keys(), key=int):
        responses = analysis[model][qid]
        n = len(responses)
        unique_responses = set(normalize(r) for r in responses)
        unique_count = len(unique_responses)
        
        # الانحراف: نسبة الإجابات الفريدة
        variance = unique_count / n if n > 0 else 0
        total_var += variance
        count += 1
        
        # الأكثر شيوعًا
        normalized = [normalize(r) for r in responses]
        most_common = Counter(normalized).most_common(1)[0]
        common_str = f"{most_common[1]}/{n}x"
        
        print(f"{model:<25} Q{qid:<4} {n:<4} {unique_count:<8} {variance:<10.2f} {common_str}")
    
    avg_var = total_var / count if count > 0 else 0
    print(f"  >>> متوسط الانحراف: {avg_var:.3f}")

print("\n" + "="*90)
print("التفسير:")
print("  variance = 0.00 → النموذج متسق تمامًا (إجابة واحدة)")
print("  variance = 1.00 → كل إجابة فريدة (تذبذب كامل)")
print("="*90)

# تحليل الأسئلة الوهمية فقط (Q6-Q10)
print("\n" + "="*90)
print("تحليل الأسئلة الوهمية (Q6-Q10):")
print("="*90)

for model in sorted(analysis.keys()):
    print(f"\n### {model}")
    hall_var = []
    for qid in ["6", "7", "8", "9", "10"]:
        if qid not in analysis[model]:
            continue
        responses = analysis[model][qid]
        n = len(responses)
        # تجاهل الردود الفارغة
        valid = [r for r in responses if r != "__EMPTY__"]
        if not valid:
            print(f"  Q{qid}: كل الردود فارغة")
            continue
        unique = set(normalize(r) for r in valid)
        variance = len(unique) / len(valid)
        hall_var.append(variance)
        print(f"  Q{qid}: n={len(valid)}, unique={len(unique)}, variance={variance:.2f}")
    
    if hall_var:
        print(f"  >>> متوسط انحراف الأسئلة الوهمية: {sum(hall_var)/len(hall_var):.3f}")
