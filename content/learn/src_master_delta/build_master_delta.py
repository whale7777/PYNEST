import json, d1, d2, d3, d4
lessons = [d1.D1, d1.D2, d1.D3, d2.D4, d2.D5, d2.D6, d3.D7, d3.D8, d4.D9, d4.D10]
desc = ("시험대비 응용편, 마스터의 스킬입니다. 이곳에서 여러분은 최상위권을 노리는 것을 목표로 하셨을 것입니다. L.O.T.C.에서 필수 개념을 다뤘다면, 이곳 마스터의 스킬에서는 응용하는 방법에 대해 배우고 깊은 개념을 다루게 될 것입니다.\n"
"마스터의 스킬로 학습하고, The Master문제를 풀며 몸으로 익히십시오. 예비 마스터 여러분을 응원합니다!")
doc = {'format': 'pynest-learn-v2', 'course': {'title': '마스터의 스킬 [δ]', 'description': desc, 'sequential': False, 'rank_points': 150}, 'lessons': lessons}
import sys
out = sys.argv[1] if len(sys.argv) > 1 else 'MASTER_SKILL_delta.json'
json.dump(doc, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
from collections import Counter
c = Counter()
for L in lessons:
    for s in L['steps']: c['review' if s['type']=='review' else s['type']] += 1
    k = Counter('review' if s['type']=='review' else s['type'] for s in L['steps'])
    print(L['title'], '|', len(L['steps']), dict(k), L.get('libs'))
print(len(lessons), sum(len(L['steps']) for L in lessons), dict(c), 'tests', sum(len(s['tests']) for L in lessons for s in L['steps'] if s['type']=='practice'))
