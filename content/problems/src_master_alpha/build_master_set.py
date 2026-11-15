import json, plib
plib.PROBS.clear()
import q1, q2
from collections import Counter
PROBS = plib.PROBS
topics = []
for p in PROBS:
    if p['topic'] not in topics: topics.append(p['topic'])
def prob(p): return {'difficulty': p['difficulty'], 'label': '', 'points': None, 'tags': [], 'source': 'The MASTER α', 'body': p['body'], 'check': '', 'tests': p['tests'], 'answers': []}
core, bank = [], []
for t in topics:
    ps = [p for p in PROBS if p['topic'] == t]; assert len(ps) == 6, (t, len(ps))
    core.append({'title': t, 'problems': [prob(p) for p in ps[:3]]})
    bank.append({'title': t, 'problems': [prob(p) for p in ps[3:]]})
desc = ("*주의* 꼭 마스터의 스킬을 완벽히 학습하고 오십시오. 다음 문제의 난이도는 어렵습니다.\n"
"마스터의 스킬을 배우고 꼭 이 문제를 푸십시오. 숙제만 보기 버튼을 눌러 가장 중요한 문제를 먼저 푸시고, 그 이후 나머지 문제를 풀어보는걸 권장드립니다.")
doc = {'format': 'pynest-problemset-v1', 'title': 'The MASTER [α]', 'short_name': 'MASTER α', 'folder': 'The MASTER', 'week': '', 'description': desc,
  'chapters': [{'title': '핵심 30', 'subtitle': '숙제 — 가장 먼저 푸는 문제', 'sections': core}, {'title': '도전 30', 'subtitle': '만점을 향해', 'sections': bank}], 'elite': []}
json.dump(doc, open('MASTER_alpha.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
allp = [q for ch in doc['chapters'] for s in ch['sections'] for q in s['problems']]
print(len(allp), Counter(q['difficulty'] for q in allp), sum(len(q['tests']) for q in allp), min(len(q['tests']) for q in allp))
json.dump({p['title']: p['sol'] for p in PROBS}, open('MASTER_alpha_solutions.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
