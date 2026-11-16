import json, g1, g2, g3
lessons = [g1.G1, g1.G2, g1.G3, g2.G4, g2.G5, g2.G6, g2.G7, g3.G8, g3.G9, g3.G10]
desc = ("시험대비 응용편, 마스터의 스킬입니다. 이곳에서 여러분은 최상위권을 노리는 것을 목표로 하셨을 것입니다. L.O.T.C.에서 필수 개념을 다뤘다면, 이곳 마스터의 스킬에서는 응용하는 방법에 대해 배우고 깊은 개념을 다루게 될 것입니다.\n"
"마스터의 스킬로 학습하고, The Master문제를 풀며 몸으로 익히십시오. 예비 마스터 여러분을 응원합니다!")
doc = {'format': 'pynest-learn-v2', 'course': {'title': '마스터의 스킬 [γ]', 'description': desc, 'sequential': False, 'rank_points': 150}, 'lessons': lessons}
json.dump(doc, open('MASTER_SKILL_gamma.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
from collections import Counter
c = Counter()
for L in lessons:
    for s in L['steps']: c['review' if s['type']=='review' else s['type']] += 1
print(len(lessons), sum(len(L['steps']) for L in lessons), dict(c))
