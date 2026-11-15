import json, l1, l2, l3, l4
lessons = [l1.L1, l1.L2, l1.L3, l2.L4, l2.L5, l2.L6, l2.L7, l3.L8, l3.L9, l3.L10, l4.L11]
desc = ("L.O.T.C. : Logic of Test Completion (시험 완성의 논리)\n"
"정보 시험의 완전 분석과 설명을 담았습니다.\n"
"α단계에서는 (1학년 1학기 1차고사 범위: 변수·자료형·입출력과 오류 판단, 몫·나머지와 시간 환산, 조건문, for·while 반복과 break·continue, 중첩 반복 패턴, 문자열 슬라이싱·메서드·ASCII, 리스트, 버블 정렬, 딕셔너리, random·time, 실수 오차)의 내용을 담았습니다. 개념은 L.O.T.C., 실전은 ACE 문제집을 풀어 공부해주세요!")
doc = {'format': 'pynest-learn-v2', 'course': {'title': 'L.O.T.C. [α]', 'description': desc, 'sequential': False, 'rank_points': 150}, 'lessons': lessons}
json.dump(doc, open('LOTC_alpha.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
from collections import Counter
c = Counter(); 
for L in lessons:
    for s in L['steps']: c[s['type'] + (':' + s['kind'] if s.get('kind') else '')] += 1
print(sum(len(L['steps']) for L in lessons), dict(c))
