import json, p1, p2, p3
from plib import PROBS
from collections import Counter
topics = []
for p in PROBS:
    if p['topic'] not in topics: topics.append(p['topic'])
def prob(p): return {'difficulty': p['difficulty'], 'label': '', 'points': None, 'tags': [], 'source': 'A.C.E. α', 'body': p['body'], 'check': '', 'tests': p['tests'], 'answers': []}
core, bank = [], []
for t in topics:
    ps = [p for p in PROBS if p['topic'] == t]; assert len(ps) == 10, (t, len(ps))
    core.append({'title': t, 'problems': [prob(p) for p in ps[:3]]})
    bank.append({'title': t, 'problems': [prob(p) for p in ps[3:]]})
desc = ("A.C.E. : Archive of Core Examinations (핵심 기출 아카이브)\n"
"α단계(1학년 1학기 1차고사 범위: 연산·조건·반복·문자열·리스트·버블 정렬·딕셔너리)의 실전 문제집입니다. 핵심 30문제는 숙제로 따로 묶여 있어요. 개념은 L.O.T.C. [α] 로 먼저 학습하세요!")
doc = {'format': 'pynest-problemset-v1', 'title': 'A.C.E. [α]', 'short_name': 'ACE α', 'folder': 'A.C.E.', 'week': '', 'description': desc,
  'chapters': [{'title': '핵심 30', 'subtitle': '숙제 — 가장 먼저 푸는 문제', 'sections': core}, {'title': '문제 은행 70', 'subtitle': '유형 넓히기', 'sections': bank}], 'elite': []}
json.dump(doc, open('ACE_alpha.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
allp = [q for ch in doc['chapters'] for s in ch['sections'] for q in s['problems']]
print(len(allp), Counter(q['difficulty'] for q in allp), Counter(q['difficulty'] for s in core for q in s['problems']), sum(len(q['tests']) for q in allp))
json.dump({p['title']: p['sol'] for p in PROBS}, open('ACE_alpha_solutions.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
