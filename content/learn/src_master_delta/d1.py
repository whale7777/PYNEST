from glib import *

def _ev(exprs, pre=''):
    """식 목록을 실제로 실행해 결과 문자열 목록으로 돌려준다 (bucket·match 정답 검증용)"""
    out = run(pre + '\n' + '\n'.join(f'print(repr({e}))' for e in exprs))
    return out.split('\n')

# ============================================================ D1
_tf = ['all([])', 'any([])', 'all([0, 1])', 'any([0, 1])', 'all([[]])', 'any(["0"])', 'all(x > 5 for x in [1, 2] if x > 3)', 'any(x > 5 for x in [1, 2] if x > 3)']
_tfv = _ev(_tf)
assert set(_tfv) == {'True', 'False'}

_mp = ['max(d)', 'max(d.values())', 'max(d, key=d.get)', 'sorted(d, key=d.get)[1]', 'len(d)']
_mpv = [v.strip("'") for v in _ev(_mp, 'd = {"b": 9, "a": 30, "c": 5}')]
assert len(set(_mpv)) == len(_mpv), _mpv

_s1 = D('''
names = ["가", "나", "다"]
scores = [90, 85, 70]
for i, n in enumerate(names, start=1):
    line = str(i) + "." + n
    print(line, scores[i])
''')
assert errline(_s1) == 5 and err(_s1) == 'IndexError'

_s2 = D('''
scores = [70, 95, 80]
high = filter(lambda s: s >= 80, scores)
print(sorted(high))
count = len(high)
print(count)
''')
assert errline(_s2) == 4 and err(_s2) == 'TypeError'

assert err('print(int("129", 8))') == 'ValueError'
assert run('data = map(int, ["3", "9", "4"])\nprint("최댓값:", max(data))\nprint("합계:", sum(data))') == '최댓값: 9\n합계: 0'
assert run('data = list(map(int, ["3", "9", "4"]))\nprint("최댓값:", max(data))\nprint("합계:", sum(data))') == '최댓값: 9\n합계: 16'

D1 = lesson('1강. 출력 추론 심화 — 내장함수 손추적과 진수 변환', 45,
'- `enumerate(a, start=k)` 는 **번호만** k 부터 — 그 번호로 `a[i]` 를 읽으면 한 칸 밀린다\n- `divmod(a, b)` 는 `(몫, 나머지)` 튜플 — 누적 문제는 **바퀴마다 표**를 그린다\n- `all([])` 는 True, `any([])` 는 False — 컴프의 `if` 가 전부 걸러 내면 빈 것이 된다\n- `sorted` 는 **안정 정렬**: 기준이 같으면 원래 순서 그대로. `max(key=)` 는 동률이면 **먼저 나온 것**\n- `map`·`filter` 객체는 **한 번 쓰면 끝** — 두 번 쓰려면 `list()` 로 저장\n- `0b`·`0o`·`0x` 로 쓴 수는 그냥 정수, `bin`·`oct`·`hex` 결과는 **접두사 붙은 문자열**, `int(s, base)` 는 정수로 되돌리기',
review('🔁 L.O.T.C. [δ] 핵심 점검', [T('마스터의 스킬 [δ] 는 L.O.T.C. [δ] 를 끝낸 사람을 위한 코스예요. 아래 카드의 뒷면이 바로 떠오르지 않으면 L.O.T.C. 의 해당 강을 먼저 다시 보고 오세요.'), flip(['`divmod(17, 5)`', '`(3, 2)` — (몫, 나머지) 튜플'], ['`enumerate(a, start=1)` 이 주는 것', '(번호, 값) 쌍 — 번호가 1부터'], ['`map(f, a)` 의 결과를 눈으로 보려면', '`list()` 로 감싼다'], ['버블 정렬의 조기 종료 조건', '한 바퀴 동안 교환이 없으면 break'], ['이터레이터를 다 꺼낸 뒤 `next()`', 'StopIteration'], ['리스트 컴프 vs 제너레이터 표현식', '한꺼번에 저장 vs 필요할 때 하나씩 (메모리 적게)'], ['`bin(5)` 의 자료형', 'str — `"0b101"`'], ['`np.argsort(a)` 가 주는 것', '정렬했을 때의 **원래 위치(인덱스)**'])],
  [T('이번 코스는 열 강이에요. 개념을 처음부터 다시 설명하지 않고 **점수가 갈리는 지점**만 깊게 다뤄요.'), steps(['1~3강 — 손으로 푸는 문항', '출력 추론·진수 변환 / 내장함수 쓰기·안 쓰기 / 정렬 직접 구현'], ['4~7강 — 서술형이 붙는 문항', '이터레이터 / 제너레이터와 메모리 / 클로저 / 데코레이터'], ['8~9강 — 큰 배점 문항', '파일·예외·모듈 종합 / numpy'], ['10강 — 만점 모의고사', '100점 구성으로 실전 점검']), exam('2학기 2차는 4~6점짜리 출력 추론이 앞쪽에 여러 개 나와요. 여기서 시간을 아끼고 한 문제도 놓치지 않아야 뒤쪽 큰 문항에 시간을 쓸 수 있어요.')]),
outq('복습 — 출력 결과는?', D('''
words = ["kiwi", "fig", "banana"]
total = 0
for i, w in enumerate(words, 1):
    q, r = divmod(len(w), i)
    total += q * 10 + r
    print(i, q, r)
print(total)
'''), '바퀴마다 `i`, `len(w)`, `q`, `r` 을 표로 적으면 틀릴 일이 없어요. `enumerate(words, 1)` 의 1 은 `start=1` 과 같아요.', review=True),
explain('enumerate·divmod — 누적 문제는 표로',
  [T('`enumerate(a, start=k)` 에서 바뀌는 것은 **번호뿐**이에요. 값은 언제나 `a[0]` 부터 나와요. 그래서 start 를 준 번호로 다시 `a[i]` 를 읽으면 한 칸 뒤의 값을 읽게 되고, 마지막 바퀴에서는 IndexError 가 나요.'),
   cmp('번호와 값을 함께 받기', 'a = ["가", "나", "다"]\nfor i, x in enumerate(a, start=1):\n    print(i, x)', '번호로 다시 인덱싱', 'a = ["가", "나", "다"]\nfor i, x in enumerate(a, start=1):\n    print(i, a[i])', '1 가 / 2 나 / 3 다', '1 나 / 2 다 / 그다음 IndexError'),
   key('start 는 "몇 번부터 **부를지**"만 정해요. 리스트의 어디부터 **꺼낼지**는 바꾸지 않아요.')],
  [T('`divmod(a, b)` 는 `(a // b, a % b)` 예요. 시험은 이 결과를 **다음 바퀴로 넘기는** 누적 형태로 내요. 머리로 풀지 말고 변수마다 한 칸씩 표를 그리세요.'),
   trace(D('''
data = [17, 8, 25]
acc = 0
for i, x in enumerate(data, start=2):
    q, r = divmod(x + acc, i)
    acc = r
    print(i, q, r)
print(acc)
'''), '나머지 r 이 다음 바퀴의 acc 로 넘어가요'),
   tip('표의 열은 `i`, `x`, `x + acc`, `q`, `r` 다섯 개면 충분해요. **print 가 있는 줄에서 한 행**을 완성한다고 생각하세요.')],
  [T('음수가 섞이면 `//` 는 **작은 쪽(음의 무한대 쪽)으로** 내려요. 나머지는 나누는 수와 같은 부호가 돼요. `divmod` 도 똑같이 따라요.'),
   C(D('''
print(divmod(7, 2), divmod(-7, 2), divmod(7, -2))
q, r = divmod(-7, 2)
print(q * 2 + r)
'''), '몫 × 나누는 수 + 나머지 = 원래 수 는 항상 성립해요'),
   exam('`q, r = divmod(...)` 처럼 **두 변수로 풀어 받는 것**까지가 한 세트예요. `x = divmod(9, 4)` 로 받으면 x 는 튜플 `(2, 1)` 이고 `x[0]`, `x[1]` 로 꺼내요.')]),
outq('출력 결과는?', D('''
a = [5, 12, 7, 20]
s = 0
for i, x in enumerate(a, start=1):
    q, r = divmod(x, i)
    if r == 0:
        s += q
    else:
        s -= r
print(s)
print(list(enumerate("ab", 5)))
'''), '(i, x) = (1, 5), (2, 12), (3, 7), (4, 20) 순서로 나머지가 0 인지 확인해요. `enumerate("ab", 5)` 는 번호만 5 부터예요.'),
spot('**예외가 발생하는 줄**은?', _s1, 5, '`enumerate(names, start=1)` 이라 i 는 1, 2, 3 이에요. `scores[1]`, `scores[2]` 까지는 (한 칸 밀린 값이지만) 읽히고, `scores[3]` 에서 IndexError 가 나요. 줄은 5번이에요.'),
explain('all·any — 빈 것을 조심',
  [T('`all(…)` 은 "거짓이 **하나도 없나**?", `any(…)` 는 "참이 **하나라도 있나**?"를 물어요. 그래서 검사할 것이 하나도 없으면 `all` 은 True(거짓이 없으니까), `any` 는 False(참이 없으니까)예요.'),
   C(D('''
a = [3, 8, 12]
print(all(x > 2 for x in a), any(x > 10 for x in a))
print(all([]), any([]))
print(all(x > 100 for x in a if x > 50))
'''), '마지막 줄: 50 보다 큰 수가 없어 검사 대상이 0개 → True'),
   warn('컴프리헨션 뒤쪽의 `if` 는 **검사 대상을 고르는** 조건이에요. 그 조건에 맞는 값이 하나도 없으면 `all` 은 무조건 True 가 돼요. "전원 통과"를 물을 때 명단이 비었는지 따로 확인해야 하는 이유예요.')],
  [T('`all`·`any` 는 조건식이 아니라 **값 자체**를 넣어도 돼요. 그때는 각 값의 참·거짓을 봐요. 거짓으로 치는 값은 `0`, `0.0`, `""`, `[]`, `{}`, `None`, `False` 예요.'),
   flip(['`all([1, 2, 0])`', 'False — 0 은 거짓'], ['`any(["", "a"])`', 'True — "a" 는 참'], ['`any(["0"])`', 'True — 글자가 있는 문자열은 참 ("0" 도!)'], ['`all([[]])`', 'False — 원소 `[]` 가 거짓'], ['`all([])`', 'True — 원소가 없음']),
   exam('2023 유형: `all(컴프)` 한 줄의 출력을 묻는 4점 문항. **컴프가 만드는 값 목록을 먼저 적고**, 그 목록에 거짓이 있는지 보세요.')]),
outq('출력 결과는?', D('''
scores = {"민": 82, "솔": 95, "준": 58}
print(all(v >= 60 for v in scores.values()), any(v >= 90 for v in scores.values()))
print(all(v >= 60 for v in scores.values() if v > 70))
print(all(len(k) == 1 for k in scores), any(k == "하" for k in scores))
print(all([]), any([]), all([[]]), any(["0", 0]))
'''), '둘째 줄은 70 초과인 82, 95 만 검사해요. 딕셔너리를 그대로 돌면 **키**가 나와요.'),
bucket('실행 결과가 True 인 것과 False 인 것으로 나누세요.', ['True', 'False'], [(f'`{e}`', 1 if v == 'True' else 2) for e, v in zip(_tf, _tfv)], '빈 것이면 all 은 True, any 는 False 예요. `[[]]` 는 원소가 하나(빈 리스트) 있는 리스트이고 그 원소가 거짓이에요. `"0"` 은 글자가 있으니 참이에요.'),
explain('sorted(key=)·max(key=) — 튜플 키와 안정성',
  [T('`sorted(a, key=f)` 는 원소마다 `f(원소)` 를 계산해 **그 값으로 줄을 세우고**, 결과에는 원래 원소를 그대로 둬요. key 가 튜플을 돌려주면 **앞 칸부터** 비교하고, 같으면 다음 칸으로 넘어가요.'),
   C(D('''
words = ["pear", "fig", "apple", "kiwi", "plum", "yam"]
print(sorted(words, key=len))
print(sorted(words, key=lambda w: (-len(w), w)))
'''), '길이순 / 길이 내림차순 + 같으면 사전순'),
   key('`sorted` 는 **안정 정렬**이에요. key 값이 같은 원소끼리는 **원래 리스트에서의 순서**를 그대로 지켜요. 첫 줄에서 길이 3 인 fig, yam 과 길이 4 인 pear, kiwi, plum 이 입력 순서대로 나오는 이유예요.')],
  [T('`max(a, key=f)`, `min(a, key=f)` 는 key 값이 가장 큰(작은) **원소 하나**를 돌려줘요. 동률이면 **먼저 나온 것**이에요. 딕셔너리에 쓰면 키를 돌면서 비교해요.'),
   C(D('''
d = {"b": 9, "a": 30, "c": 5, "e": 30}
print(max(d), max(d.values()), max(d, key=d.get))
print(sorted(d, key=d.get), sorted(d.items(), key=lambda kv: -kv[1])[0])
'''), 'max(d) 는 "가장 큰 키", max(d, key=d.get) 은 "값이 가장 큰 키"'),
   warn('`max(d)` 와 `max(d, key=d.get)` 을 헷갈리면 바로 감점이에요. key 가 없으면 **키끼리**(글자면 사전순) 비교해요.')],
  [T('숫자는 `-x` 로 내림차순을 만들 수 있지만 문자열에는 `-` 를 붙일 수 없어요. 그럴 때는 `reverse=True` 를 쓰거나, 정렬을 **두 번**(덜 중요한 기준 먼저) 해요. 안정 정렬이라서 가능한 방법이에요.'),
   C(D('''
rows = [("민", 80), ("솔", 95), ("준", 80), ("하", 95)]
step1 = sorted(rows, key=lambda r: r[0], reverse=True)   # 이름 내림차순
step2 = sorted(step1, key=lambda r: -r[1])               # 점수 내림차순
print(step2)
'''), '점수가 같은 사람끼리는 step1 의 순서(이름 내림차순)가 유지돼요'),
   exam('2024 유형: `sorted(key=)`, `map(len, …)`, `max`, `pop`/`append` 가 한 코드에 섞인 10점 출력 추론. 한 줄 실행할 때마다 **리스트 전체를 다시 적으세요**.')]),
outq('출력 결과는?', D('''
team = [("ara", 3, 71), ("bo", 5, 64), ("chan", 3, 88), ("dua", 5, 64)]
print([t[0] for t in sorted(team, key=lambda t: t[1])])
print([t[0] for t in sorted(team, key=lambda t: (-t[1], -t[2], t[0]))])
print(max(team, key=lambda t: t[1])[0], min(team, key=lambda t: t[2])[0])
print(sorted(team, key=lambda t: len(t[0]))[-1][0])
'''), '첫 줄: 값이 3 인 ara, chan 과 5 인 bo, dua 가 각각 입력 순서를 지켜요(안정 정렬). 셋째 줄: 동률이면 먼저 나온 것이에요.'),
match('`d = {"b": 9, "a": 30, "c": 5}` 일 때 식과 결과를 이으세요.', [(f'`{e}`', v) for e, v in zip(_mp, _mpv)], 'key 가 없으면 키(글자)끼리 비교하고, `key=d.get` 이면 값으로 비교해 **키**를 돌려줘요.'),
explain('map·filter 는 한 번 쓰면 끝',
  [T('`map`, `filter` 는 리스트가 아니라 **값을 하나씩 흘려보내는 객체**(이터레이터)예요. 한 번 끝까지 흘려보내면 비어 버려요. `max` 로 한 번 쓰고 `sum` 으로 또 쓰면 두 번째는 빈 것을 더해요.'),
   C(D('''
nums = [4, 7, 10, 13]
m = map(lambda x: x * 2, nums)
print(max(m), sum(m))
f = filter(lambda x: x % 2 == 1, nums)
print(list(f), list(f))
sq = [x * x for x in nums]
print(max(sq), sum(sq))
'''), 'sum(m) 은 0, 두 번째 list(f) 는 []'),
   key('두 번 이상 쓸 거면 **`list()` 로 저장**해요. 리스트·튜플·문자열·`range` 는 몇 번을 써도 그대로예요.')],
  [T('"끝까지"가 아니라 **중간까지만** 쓰는 경우도 있어요. `in` 은 찾을 때까지만 꺼내고 멈추기 때문에, 그 뒤의 값은 남아 있어요.'),
   C(D('''
m = map(str, [1, 2, 3, 4])
print("2" in m)
print(list(m))
'''), '"1", "2" 까지 꺼내 쓰고 멈춤 → 남은 것은 "3", "4"'),
   warn('`len(map객체)`, `map객체[0]` 은 **TypeError** 예요. 길이도 모르고 칸 번호도 없는 "흐름"이기 때문이에요. `print(map객체)` 는 오류는 아니지만 `<map object at …>` 만 보여요.')],
  [T('`pop`·`append` 가 섞인 문제는 **두 리스트가 짝이 맞는지**를 봐요. 한쪽만 순서를 바꾸면 같은 인덱스가 더는 같은 사람을 가리키지 않아요.'),
   trace(D('''
names = ["dora", "al", "minho", "eve"]
lens = list(map(len, names))
names.append(names.pop(0))
lens.append(lens.pop())
k = lens.index(max(lens))
print(names)
print(lens, k, names[k])
'''), 'names 만 돌아가서 lens 와 짝이 어긋나요'),
   tip('`a.pop()` 은 **맨 뒤**, `a.pop(0)` 은 **맨 앞**을 꺼내요. `a.append(a.pop())` 는 아무 일도 없는 것과 같고, `a.append(a.pop(0))` 은 왼쪽으로 한 칸 돌리기예요.')]),
outq('출력 결과는?', D('''
titles = ["sun", "river", "sky", "mountain"]
lens = map(len, titles)
longest = max(lens)
rest = list(lens)
titles.append(titles.pop(1))
print(longest, rest, len(rest))
print(titles, sorted(titles, key=len)[1])
evens = filter(lambda n: n % 2 == 0, range(1, 9))
print(4 in evens, list(evens))
'''), '`max(lens)` 가 끝까지 꺼내 쓰므로 `rest` 는 빈 리스트예요. `4 in evens` 는 2, 4 까지만 꺼내고 멈춰요.'),
spot('**예외가 발생하는 줄**은?', _s2, 4, '`sorted(high)` 는 filter 객체를 받아 리스트를 만들어 주므로 정상이에요(이때 high 는 다 써 버려요). 4번 줄에서 filter 객체에 `len()` 을 써서 TypeError 가 나요. `high = list(filter(...))` 로 저장해 두면 해결돼요.'),
essay('아래 코드는 합계가 `16` 이 아니라 `0` 으로 출력돼요. **문제점**을 map 객체의 성질과 연결하여 서술하고, **수정 방법**을 쓰세요.\n\n```\ndata = map(int, ["3", "9", "4"])\nprint("최댓값:", max(data))\nprint("합계:", sum(data))\n```', 'map 객체는 값을 하나씩 꺼내 주는 이터레이터여서 한 번 끝까지 꺼내면 다시 처음으로 돌아가지 않는다. max(data) 가 세 값을 모두 꺼내 써 버렸기 때문에 sum(data) 는 남은 값이 없는 빈 객체를 더해 0 이 된다. data = list(map(int, ["3", "9", "4"])) 처럼 list 로 바꿔 저장하면 리스트는 여러 번 순회할 수 있으므로 합계가 16 으로 출력된다.', ['map 객체는 한 번만 순회할 수 있다(이터레이터)고 썼다', 'max 가 값을 모두 꺼내 써서 sum 에는 남은 값이 없다고 썼다', 'list() 로 바꿔 저장한다고 수정 방법을 썼다']),
explain('진수 변환 — 정수와 문자열을 구분',
  [T('`0b1010`, `0o17`, `0x1F` 는 **표기만 다른 정수**예요. 저장되는 순간 그냥 10, 15, 31 이고 `print` 하면 10진수로 나와요. 반대로 `bin`·`oct`·`hex` 의 결과는 접두사가 붙은 **문자열**이에요.'),
   C(D('''
a = 0b1010
b = 0o17
c = 0x1F
print(a, b, c, a + b + c)
print(bin(a), oct(b), hex(c))
print(bin(5) + bin(2), bin(5 + 2))
'''), '문자열끼리 + 는 이어 붙이기'),
   key('**정수 ↔ 문자열** 방향을 먼저 정하세요. `bin(n)` 은 정수 → 문자열, `int(s, 2)` 는 문자열 → 정수예요. `hex` 의 글자는 소문자(`0x1f`)로 나와요.')],
  [T('`int(s, base)` 는 s 를 base 진법으로 읽어요. 그 진법에 없는 숫자가 들어 있으면 **ValueError** 예요. 접두사가 붙은 문자열도 진법이 맞으면 읽어 줘요.'),
   C(D('''
print(int("1010", 2), int("17", 8), int("ff", 16), int("FF", 16))
print(int("0b11", 2), int("0x1f", 16))
print(bin(10)[2:], bin(10)[2:].count("1"), len(hex(255)))
'''), '접두사를 떼려면 [2:]'),
   warn('`int("12", 2)` 는 ValueError(2진수에 2 는 없음), `int("129", 8)` 도 ValueError(8진수에 9 는 없음)예요. `int(1010, 2)` 처럼 **정수를 넣으면 TypeError** 예요 — 첫 인자는 문자열이어야 해요.')],
  [T('"`bin` 을 쓰지 말고"라는 조건이 붙으면 직접 바꿔요. **진법으로 나눈 나머지**를 모으면 낮은 자리부터 나오므로, 새 글자를 **앞에** 붙여요. 10 이상인 나머지는 글자표에서 꺼내면 16진수까지 한 번에 돼요.'),
   C(D('''
def to_base(n, base):
    digits = "0123456789ABCDEF"
    if n == 0:
        return "0"
    out = ""
    while n > 0:
        n, r = divmod(n, base)
        out = digits[r] + out
    return out
print(to_base(10, 2), to_base(255, 16), to_base(64, 8), to_base(0, 2))
'''), 'n == 0 을 따로 처리하지 않으면 빈 문자열이 나와요'),
   exam('감점 1순위는 **n 이 0 일 때** 예요. while 문에 한 번도 들어가지 않아 빈 문자열이 돼요. 2순위는 나머지를 뒤에 붙여 **거꾸로** 출력하는 실수예요.')],
  [T('거꾸로(문자열 → 정수)는 왼쪽 글자부터 읽으면서 **지금까지의 값 × 진법 + 이번 자리**를 반복해요. 자리값을 따로 거듭제곱으로 구할 필요가 없어요.'),
   trace(D('''
s = "2F"
digits = "0123456789ABCDEF"
value = 0
for ch in s:
    value = value * 16 + digits.index(ch)
    print(ch, value)
'''), '2 → 2, F → 2 × 16 + 15'),
   tip('`digits.index(ch)` 는 글자 ch 가 글자표의 몇 번 칸인지 알려 줘요. `"F"` 는 15번 칸이에요. 소문자 입력은 먼저 `upper()` 로 바꿔요.')]),
outq('출력 결과는?', D('''
x = 0b110
y = 0x10
print(x * y, x + int("11", 2), oct(x + y))
print(bin(x)[2:] + hex(y)[2:], int(bin(x)[2:] + "1", 2))
print(type(bin(x)).__name__, type(0o10).__name__, hex(255).upper())
v = 0
for ch in "1101":
    v = v * 2 + int(ch)
print(v, bin(v) == "0b1101")
'''), 'x 는 6, y 는 16 이에요. `bin(x)[2:]` 는 문자열 "110" 이라 `+` 는 이어 붙이기예요. `upper()` 는 접두사의 x 도 대문자로 바꿔요.'),
fill('정수를 base 진법 문자열로 바꾸는 함수예요. 빈칸을 채우세요.', D('''
def to_base(n, base):
    digits = "0123456789ABCDEF"
    if n == 0:
        return "0"
    out = ""
    while n > 0:
        n, r = ___(n, base)
        out = ___ + out
    return out
print(to_base(255, 16), to_base(10, 2), to_base(64, 8))
'''), ['divmod', ['digits[r]']], '몫은 다음 바퀴의 n, 나머지는 이번 자리예요. 나머지를 글자로 바꿔 **앞에** 붙여요.', expect='FF 1010 100'),
order('16진수 문자열 `"2F"` 를 10진수로 바꿔 출력하는 코드예요. 순서대로 놓으세요.', ['value = 0', 'for ch in "2F":', '    d = "0123456789ABCDEF".index(ch)', '    value = value * 16 + d', 'print(value)'], '왼쪽 글자부터 "지금까지의 값 × 16 + 이번 자리"를 반복해요.'),
essay('`print(int("129", 8))` 을 실행하면 오류가 나요. **오류의 종류**와 **이유**를 쓰고, `int("129", 8)` 과 `int("0o17", 8)` 의 차이를 한 문장으로 설명하세요.', 'ValueError 가 발생한다. int(s, 8) 은 문자열 s 를 8진수로 해석하는데, 8진수는 0~7 의 숫자만 쓸 수 있으므로 9 가 들어 있는 "129" 는 8진수로 읽을 수 없기 때문이다. 반면 "0o17" 은 8진수 접두사 0o 뒤에 0~7 만 있으므로 정상적으로 15 가 된다.', ['ValueError 라고 썼다', '8진수는 0~7 만 쓸 수 있는데 9 가 있어서라고 이유를 썼다', '"0o17" 은 올바른 8진수 표기라 15 가 된다고 썼다']),
prac('[기출유사] 진수 변환표 — 내장함수와 직접 구현', '0 이상의 정수 `n` 과 진법 `b` 를 받아 변환표를 출력해요.\n\n입력: 첫 줄 `n` (0 이상), 둘째 줄 `b` (2~16)\n\n출력\n1. `2진: … / 8진: … / 16진: …` — **접두사 없이**. 16진수는 대문자\n2. `b진: …` — b 는 입력받은 수. 10 이상의 자리는 `A`~`F`\n3. `1의 개수: k` — 2진 표현에 들어 있는 1 의 개수\n\n[조건] ○ 1번 줄은 `bin`, `oct`, `hex` 를 **사용** ○ 2번 줄은 `bin`·`oct`·`hex`·`int(문자열, 진법)` 을 **쓰지 않고** 직접 구현한 함수로 ○ n 이 0 이면 `0`',
D('''
def to_base(n, base):
    digits = "0123456789ABCDEF"
    if n == 0:
        return "0"
    out = ""
    while n > 0:
        n, r = divmod(n, base)      # 몫은 다음 바퀴로, 나머지는 이번 자리
        out = digits[r] + out       # 낮은 자리부터 나오므로 앞에 붙인다
    return out
n = int(input())
b = int(input())
print(f"2진: {bin(n)[2:]} / 8진: {oct(n)[2:]} / 16진: {hex(n)[2:].upper()}")
print(f"{b}진: {to_base(n, b)}")
print(f"1의 개수: {bin(n).count('1')}")
'''), ['45\n3', '255\n16', '0\n2', '1\n7', '1000\n12', '4095\n5', '64\n8'],
  starter='def to_base(n, base):\n    digits = "0123456789ABCDEF"\n    # n 을 base 진법 문자열로 바꿔 return\n\nn = int(input())\nb = int(input())\n',
  hints=['`bin(n)` 은 `"0b…"` 문자열이에요. `[2:]` 로 접두사를 떼요. 16진수는 `.upper()`.', '직접 변환: `while n > 0:` 안에서 `n, r = divmod(n, base)`, `out = digits[r] + out`.', 'n 이 0 이면 while 에 들어가지 않으니 함수 맨 앞에서 `"0"` 을 return 해요.'],
  ex='접두사를 떼는 `[2:]`, 0 처리, 나머지를 앞에 붙이기 — 세 가지가 채점 포인트예요.'),
prac('[기출유사] 동아리 발표 순위표', '발표 기록을 정리해요.\n\n입력: 첫 줄 `n`, 이어서 n 줄에 `이름 점수 시간(초)`\n\n출력\n1. 순위표 n 줄: `k위 이름 점수점 시간초` — **점수 높은 순**, 같으면 **시간 짧은 순**, 그래도 같으면 **이름 사전순**\n2. `최장 발표: 이름` — 시간이 가장 긴 사람(같으면 **먼저 입력된** 사람)\n3. `전원 통과: True/False` — 모두 60점 이상인가\n4. `만점 있음: True/False` — 100점이 한 명이라도 있는가\n\n[조건] ○ 순위표는 `sorted(key=)` 와 `enumerate(start=1)` 사용 ○ 2번은 `max(key=)` ○ 3·4번은 `all`, `any`',
D('''
n = int(input())
rows = []
for _ in range(n):
    name, score, sec = input().split()
    rows.append((name, int(score), int(sec)))
ranked = sorted(rows, key=lambda r: (-r[1], r[2], r[0]))   # 튜플 키: 앞 칸부터 비교
for k, r in enumerate(ranked, start=1):
    print(f"{k}위 {r[0]} {r[1]}점 {r[2]}초")
print("최장 발표:", max(rows, key=lambda r: r[2])[0])      # 동률이면 먼저 나온 것
print("전원 통과:", all(r[1] >= 60 for r in rows))
print("만점 있음:", any(r[1] == 100 for r in rows))
'''), ['3\n하늘 85 120\n바다 92 150\n구름 85 100', '2\n가 100 60\n나 100 60', '4\n민 59 30\n솔 60 200\n준 75 200\n하 75 199', '1\n혼자 40 10', '5\n다 70 90\n가 70 90\n나 70 90\n라 100 300\n마 100 250', '3\n강 61 5\n산 60 5\n들 99 5'],
  hints=['입력을 `(이름, 점수, 시간)` 튜플로 리스트에 모아요.', '`key=lambda r: (-r[1], r[2], r[0])` — 점수만 부호를 뒤집어요.', '최장 발표는 **정렬 전 리스트**에 `max(rows, key=lambda r: r[2])` — 동률이면 먼저 입력된 사람이 나와요.'],
  ex='순위표는 정렬한 리스트, 최장 발표는 원래 리스트에서 구해야 "먼저 입력된 사람" 규칙이 맞아요.'),
prac('[심화] 진법 바꾸기 — a진수를 b진수로', '`a` 진법으로 쓰인 문자열 `s` 를 `b` 진법으로 바꿔요.\n\n입력: 첫 줄 `s` (숫자와 영문자, 소문자일 수 있음), 둘째 줄 `a b` (각각 2~16)\n\n출력\n- s 에 a 진법에서 쓸 수 없는 글자가 있으면 `변환 불가 (글자)` 한 줄만 — **처음 만난** 잘못된 글자를 대문자로\n- 아니면 첫 줄 `10진: 값`, 둘째 줄 `b진: 결과` (b 는 입력받은 수, 영문자는 대문자)\n\n[조건] ○ `int(문자열, 진법)`, `bin`, `oct`, `hex` 를 쓰지 않아요 ○ 문자열 → 정수는 "값 × 진법 + 자리", 정수 → 문자열은 나머지 모으기',
D('''
digits = "0123456789ABCDEF"
s = input().strip().upper()
a, b = map(int, input().split())
value = 0
bad = ""
for ch in s:
    d = digits.find(ch)             # 글자표에서의 위치 = 그 자리의 값
    if d == -1 or d >= a:           # 없는 글자이거나 a 진법에서 못 쓰는 숫자
        bad = ch
        break
    value = value * a + d
if bad:
    print(f"변환 불가 ({bad})")
else:
    print("10진:", value)
    n = value
    out = "0" if n == 0 else ""
    while n > 0:
        n, r = divmod(n, b)
        out = digits[r] + out
    print(f"{b}진: {out}")
'''), ['1011\n2 16', 'ff\n16 2', '129\n8 10', '0\n5 3', 'zz\n16 2', '777\n8 16', '1G\n16 8', 'abc\n13 7'],
  hints=['먼저 `upper()` 로 대문자로 바꾸고, 글자표 `"0123456789ABCDEF"` 에서 `find` 로 위치를 구해요.', '위치가 -1 이거나 `a` 이상이면 그 진법에서 쓸 수 없는 글자예요.', '`value = value * a + d` 를 끝까지 반복한 뒤, `divmod(n, b)` 로 다시 문자열을 만들어요. 값이 0 인 경우를 잊지 마세요.'],
  ex='읽기(× 진법 + 자리)와 쓰기(나머지를 앞에 붙이기)를 한 프로그램에서 모두 연습해요.'),
prac('[심화] 구간 기록 누적 — divmod 두 번', '달리기 구간 기록(초)이 한 줄에 공백으로 주어져요. 구간마다 기록과 누적 시간을 출력해요.\n\n입력: 한 줄에 구간 기록(초, 1 이상의 정수) 여러 개\n\n출력\n- 구간마다 `k구간 M분 SS초 (누적 H:MM:SS)` — 초는 두 자리, 누적의 분·초도 두 자리\n- 마지막 줄 `가장 느린 구간: k구간` — 기록이 가장 큰 구간(같으면 **앞 구간**)\n\n[조건] ○ `enumerate(start=1)` 과 `divmod` 를 사용 ○ `//`, `%` 연산자를 직접 쓰지 않아요',
D('''
laps = list(map(int, input().split()))
total = 0
slow_k = 1
for k, sec in enumerate(laps, start=1):
    total += sec
    m, s = divmod(sec, 60)
    tm, ts = divmod(total, 60)      # 누적 초 → 분, 초
    th, tm = divmod(tm, 60)         # 분 → 시간, 분
    print(f"{k}구간 {m}분 {s:02d}초 (누적 {th}:{tm:02d}:{ts:02d})")
    if sec > laps[slow_k - 1]:      # 더 클 때만 바꾸므로 동률이면 앞 구간
        slow_k = k
print(f"가장 느린 구간: {slow_k}구간")
'''), ['95 130 61', '3600', '59 60 59 60', '1800 1800 1 3599', '7 7 7', '725 1210 1210 300 45'],
  hints=['`m, s = divmod(sec, 60)` — 두 변수로 풀어 받아요.', '누적은 divmod 를 두 번: 초 → (분, 초), 분 → (시간, 분).', '번호 k 는 1부터라서 리스트에서 다시 읽으려면 `laps[k - 1]` 이에요.'],
  ex='start=1 로 받은 번호를 인덱스로 쓰려면 1 을 빼야 해요 — 1강의 첫 함정을 직접 코드로 확인하는 문제예요.'),
)

# ============================================================ D2
_top2_fix = D('''
def top2(a):
    first, second = max(a[0], a[1]), min(a[0], a[1])
    for x in a[2:]:
        if x > first:
            second = first
            first = x
        elif x > second:
            second = x
    return first + second
print(top2([3, 8, 5, 9]), top2([-4, -9, -7]), top2([5, 5, 3]))
''')
_top2_bug = D('''
def top2(a):
    first, second = max(a[0], a[1]), min(a[0], a[1])
    for x in a[2:]:
        if x > first:
            second = first
            first = x
        if x > second:
            second = x
    return first + second
print(top2([3, 8, 5, 9]), top2([-4, -9, -7]), top2([5, 5, 3]))
''')
assert run(_top2_fix) == '17 -11 10', run(_top2_fix)
assert run(_top2_bug) != run(_top2_fix), run(_top2_bug)
assert _top2_bug.split('\n')[6].strip() == 'if x > second:'

D2 = lesson('2강. 같은 문제 두 가지 풀이 — 내장함수 쓰기 / 안 쓰기', 50,
'- 시험은 같은 일을 **내장함수로 한 번, 직접 구현으로 한 번** 쓰게 한다 — [조건]의 금지 목록부터 읽기\n- 최댓값·두 번째 값의 **초기값은 0 이 아니라 리스트의 원소**로 (음수 입력 대비)\n- `set` 은 순서를 약속하지 않는다 — 순서 유지는 `if x not in result`, 정렬된 결과는 `sorted(set(a))`\n- 회문 변형은 **전처리(소문자·공백 제거) 먼저**, 그다음 양 끝 비교\n- 최빈값의 동률 규칙: `>` 는 먼저 나온 것, `>=` 는 나중에 나온 것\n- "오름차순인가"는 **이웃끼리** 비교 — 같은 값 허용이면 `<=`, 아니면 `<`',
review('🔁 1강 복습', [T('출력 추론의 함정을 다시 확인해요.'), flip(['`enumerate(a, start=1)` 의 번호로 `a[i]`', '한 칸 밀리고 마지막에 IndexError'], ['`all([])`, `any([])`', 'True, False'], ['`max(m)` 뒤의 `sum(m)` (m 은 map 객체)', '0 — 이미 다 꺼내 씀'], ['`sorted` 에서 key 가 같은 원소들', '원래 순서 유지 (안정 정렬)'], ['`bin(6)`', '문자열 `"0b110"`'], ['`int("12", 2)`', 'ValueError — 2진수에 2 는 없음'], ['문자열 → 정수 직접 변환', '값 = 값 × 진법 + 이번 자리'])]),
outq('복습 — 출력 결과는?', D('''
pairs = [("101", 2), ("1A", 16), ("17", 8)]
vals = map(lambda p: int(p[0], p[1]), pairs)
big = max(vals)
print(big, list(vals))
nums = [int(s, b) for s, b in pairs]
print(nums, bin(sum(nums)), all(n > 5 for n in nums if n < 5))
'''), '`max(vals)` 가 map 객체를 끝까지 꺼내 쓰므로 `list(vals)` 는 빈 리스트예요. 마지막 `all` 은 5 미만인 수가 없어 검사 대상이 없어요.', review=True),
explain('가장 큰 두 수 — 초기값이 점수를 가른다',
  [T('"가장 큰 두 수의 합"은 2023 기출에서 **sorted 를 쓰는 풀이**와 **쓰지 않는 풀이**를 모두 쓰게 했어요. 내장함수 풀이는 한 줄이지만, 직접 구현은 변수 두 개를 **어떤 값으로 시작하느냐**에서 점수가 갈려요.'),
   cmp('sorted 사용', 'a = [3, 8, 5, 9]\nprint(sum(sorted(a)[-2:]))', 'sorted 없이', 'a = [3, 8, 5, 9]\nfirst, second = max(a[0], a[1]), min(a[0], a[1])\nfor x in a[2:]:\n    if x > first:\n        second = first\n        first = x\n    elif x > second:\n        second = x\nprint(first + second)', '정렬 뒤 뒤에서 두 개', '한 번 훑으며 1등·2등을 갱신', tones=('good', 'good')),
   key('1등이 바뀔 때는 **옛 1등을 2등으로 내려보내는 것이 먼저**예요. `second = first` → `first = x` 순서가 바뀌면 둘 다 x 가 돼요.')],
  [T('가장 흔한 실수는 `first = second = 0` 으로 시작하는 거예요. 입력이 모두 음수면 어떤 값도 0 을 이기지 못해서 결과가 0 으로 남아요. 양수와 음수가 섞여도 2등이 0 으로 남을 수 있어요.'),
   C(D('''
def top2(a):
    first = second = 0
    for x in a:
        if x > first:
            second = first
            first = x
        elif x > second:
            second = x
    return first, second
print(top2([4, 9, 7]), top2([-4, -9, -7]), top2([-2, 6, -1]))
'''), '초기값 0 — 음수가 있으면 틀려요'),
   warn('초기값은 **리스트에 실제로 있는 값**으로 잡아요. 앞의 두 원소를 비교해 큰 쪽을 first, 작은 쪽을 second 로 두고 **세 번째 원소부터** 훑으면 돼요.')],
  [T('중복이 있을 때의 규칙도 문제에서 확인하세요. `[5, 5, 3]` 에서 `sorted(a)[-2:]` 는 `[5, 5]` 라서 합이 10 이에요. 직접 구현도 같은 답을 내려면 `elif x > second` 에서 **1등과 같은 값도 2등이 될 수 있어야** 해요.'),
   tabs(('같은 값도 2등 (sorted 와 같은 결과)', '`[5, 5, 3]` → 1등 5, 2등 5', 'if x > first:\n    second = first\n    first = x\nelif x > second:\n    second = x'), ('서로 다른 값만 (두 번째로 큰 "값")', '`[5, 5, 3]` → 1등 5, 2등 3. 조건에 `x != first` 를 더해요.', 'if x > first:\n    second = first\n    first = x\nelif x != first and x > second:\n    second = x')),
   exam('두 풀이의 **출력이 같아야** 만점이에요. 직접 구현을 쓴 뒤 `[5, 5, 3]`, `[-4, -9, -7]`, `[1, 2]` 세 가지를 머릿속으로 넣어 보세요.')]),
outq('출력 결과는?', D('''
def top2(a):
    first = second = a[0]
    for x in a[1:]:
        if x > first:
            second = first
            first = x
        elif x > second:
            second = x
    return first, second
print(top2([4, 9, 7]))
print(top2([9, 4, 7]))
print(top2([-3, -8, -5]))
print(sorted([9, 4, 7])[-2:], sorted([-3, -8, -5])[-2:])
'''), '`first = second = a[0]` 도 함정이에요. 첫 원소가 가장 크면 second 가 a[0] 에 머물러 아무도 이기지 못해요. 2등의 초기값은 "1등이 아닌 실제 원소"여야 해요.'),
spot('가장 큰 두 수의 합을 구하는 함수인데 `top2([3, 8, 5, 9])` 가 17 이 아닌 값을 돌려줘요. **잘못된 줄**은?', _top2_bug, 7, '7번 줄이 `elif` 가 아니라 `if` 예요. x 가 새 1등이 되면 4~6번 줄에서 2등이 옛 1등으로 바뀌는데, 곧바로 7번 줄이 또 참이 되어 2등까지 x 로 덮어써요. `elif x > second:` 로 고쳐야 해요.'),
essay('아래 함수는 리스트에서 가장 큰 두 수의 합을 구하려고 해요. `top2([-4, -9, -7])` 을 호출하면 `-11` 이 아니라 `0` 이 나와요. **문제점**을 쓰고 **수정 방법**을 서술하세요.\n\n```\ndef top2(a):\n    first = second = 0\n    for x in a:\n        if x > first:\n            second = first\n            first = x\n        elif x > second:\n            second = x\n    return first + second\n```', 'first 와 second 의 초기값을 0 으로 두었기 때문에, 리스트의 값이 모두 음수이면 x > first 와 x > second 가 한 번도 참이 되지 않아 두 변수가 0 으로 남는다. 초기값을 리스트에 실제로 있는 값으로 바꿔야 한다. 예를 들어 a[0] 과 a[1] 중 큰 값을 first, 작은 값을 second 로 두고 a[2:] 를 순회하면 음수만 있어도 -4 + -7 = -11 이 나온다.', ['초기값 0 이 원인이라고 썼다', '모두 음수이면 비교가 참이 되지 않아 0 으로 남는다고 설명했다', '리스트의 실제 원소(앞의 두 원소)로 초기화한다고 수정했다', '순회 시작 위치(세 번째 원소부터)를 맞게 썼다']),
explain('중복 제거 — set 은 순서를 약속하지 않아요',
  [T('`set(a)` 는 중복을 한 번에 없애 주지만 **원소의 순서를 보장하지 않아요**. 그래서 "처음 나온 순서대로"라는 조건이 있으면 set 만으로는 풀 수 없어요. "크기순"이면 `sorted(set(a))` 로 정렬까지 해야 해요.'),
   cmp('set 사용', 'a = [3, 1, 3, 2, 1]\nprint(sorted(set(a)))\nprint(len(set(a)))', 'set 없이', 'a = [3, 1, 3, 2, 1]\nres = []\nfor x in a:\n    if x not in res:\n        res.append(x)\nprint(res)\nprint(len(res))', '[1, 2, 3] / 3 — 정렬해서 출력', '[3, 1, 2] / 3 — 처음 나온 순서 유지', tones=('good', 'good')),
   warn('`print(set(a))` 나 `list(set(a))` 를 그대로 출력하는 답은 위험해요. 문자열 집합은 실행할 때마다 순서가 달라질 수 있어요. 출력하기 전에 **`sorted` 로 순서를 정하거나** 직접 구현으로 순서를 지키세요.')],
  [T('직접 구현의 핵심은 `if x not in res` 한 줄이에요. 여기서 조금만 바꾸면 변형 문제가 풀려요. **마지막에 나온 위치**를 기준으로 남기려면 뒤에서부터 훑고 결과를 다시 뒤집어요.'),
   C(D('''
a = [3, 1, 3, 2, 1, 3]
last = []
for x in a[::-1]:
    if x not in last:
        last.append(x)
print(last[::-1])
dup = []
for i in range(len(a)):
    if a[i] in a[:i] and a[i] not in dup:
        dup.append(a[i])
print(dup)
'''), '마지막 등장 기준으로 남기기 / 두 번 이상 나온 값만 모으기'),
   tip('`a[i] in a[:i]` 는 "**내 앞에** 나와 같은 값이 있었나?"예요. 중복 "제거"가 아니라 중복 "찾기"를 물을 때 써요.')]),
outq('출력 결과는?', D('''
tags = ["py", "ai", "py", "web", "ai", "py"]
first = []
count = {}
for t in tags:
    if t not in first:
        first.append(t)
    count[t] = count.get(t, 0) + 1
print(first, sorted(set(tags)))
print(len(tags) - len(first), [t for t in first if count[t] > 1])
print(sorted(first, key=len)[0], sorted(first, key=lambda t: -count[t])[-1])
'''), '`first` 는 처음 나온 순서, `sorted(set(tags))` 는 사전순이에요. 마지막 줄의 `sorted(first, key=len)` 은 안정 정렬이라 길이가 같은 "py", "ai" 가 first 에서의 순서를 지켜요.'),
order('입력 순서를 지키며 중복을 없애 출력하는 코드예요. 순서대로 놓으세요.', ['result = []', 'for x in [2, 5, 2, 7, 5]:', '    if x not in result:', '        result.append(x)', 'print(result)'], '빈 리스트 → 하나씩 꺼내 → 없을 때만 추가 → 출력.'),
explain('회문 — 뒤집기와 양 끝 비교',
  [T('회문 검사도 두 가지로 써요. 슬라이싱 `s == s[::-1]` 은 한 줄이고, 직접 구현은 **양 끝에서 안쪽으로** 좁혀 오며 비교해요. 다르면 바로 False 를 돌려주고, 끝까지 같으면 True 예요.'),
   cmp('뒤집어서 비교', 'def is_pal(s):\n    return s == s[::-1]', '양 끝 비교', 'def is_pal(s):\n    i, j = 0, len(s) - 1\n    while i < j:\n        if s[i] != s[j]:\n            return False\n        i += 1\n        j -= 1\n    return True', '새 문자열을 하나 더 만든다', '다른 곳을 찾으면 바로 끝낸다', tones=('good', 'good')),
   key('반복 조건은 `i < j` 예요. 글자 수가 홀수면 가운데 글자는 비교할 필요가 없고, 빈 문자열이나 한 글자는 반복 없이 True 가 돼요.')],
  [T('변형은 "대소문자와 공백을 무시하고"예요. 비교 코드를 고치지 말고 **먼저 문자열을 정리**하세요. 정리한 문자열에 원래 검사 함수를 그대로 쓰면 돼요.'),
   C(D('''
def clean(s):
    return s.lower().replace(" ", "")
for s in ["Was it a cat I saw", "No lemon no melon", "Step on no pet"]:
    t = clean(s)
    print(t == t[::-1], len(t))
'''), '전처리 → 검사'),
   exam('인덱스로 쓰는 다른 모양도 알아 두세요: `for i in range(len(s) // 2): if s[i] != s[len(s) - 1 - i]` 또는 `s[-1 - i]`. **`len(s) - i` 로 쓰면 IndexError** 예요(1 을 빼야 해요).')]),
fill('양 끝 비교로 회문을 검사해요. 빈칸을 채우세요.', D('''
def is_pal(s):
    i, j = 0, ___
    while i < j:
        if s[i] != s[j]:
            return ___
        i += 1
        j -= 1
    return True
print(is_pal("level"), is_pal("lever"), is_pal(""))
'''), [['len(s) - 1', 'len(s)-1'], 'False'], '마지막 칸의 번호는 `len(s) - 1` 이에요. 한 곳이라도 다르면 그 자리에서 False 를 돌려줘요.', expect='True False True'),
explain('최빈 문자 — 세기와 동률 규칙',
  [T('가장 많이 나온 글자는 "세기"와 "가장 큰 것 찾기" 두 단계예요. `count()` 가 금지되면 딕셔너리로 직접 세요. 그다음이 진짜 문제예요 — **횟수가 같은 글자가 여럿일 때 무엇을 출력하느냐**.'),
   C(D('''
s = "tomato motto"
cnt = {}
for ch in s:
    if ch != " ":
        cnt[ch] = cnt.get(ch, 0) + 1
print(cnt)
b1 = b2 = ""
m1 = m2 = 0
for k in cnt:
    if cnt[k] > m1:
        b1, m1 = k, cnt[k]
    if cnt[k] >= m2:
        b2, m2 = k, cnt[k]
print(b1, m1, b2, m2, max(cnt, key=cnt.get))
'''), 't 와 o 가 4번씩 — > 와 >= 의 결과가 달라요'),
   key('`>` 는 **더 클 때만** 바꾸므로 먼저 나온 글자가 남고, `>=` 는 같아도 바꾸므로 나중에 나온 글자가 남아요. `max(cnt, key=cnt.get)` 은 `>` 와 같은 결과(먼저 들어간 키)예요.')],
  [T('"동률이면 사전순으로 앞선 글자"라는 규칙이면 조건을 하나 더 붙여요. 횟수가 **더 크거나**, 횟수가 **같으면서 글자가 더 앞**이면 바꿔요.'),
   C(D('''
cnt = {"t": 4, "o": 4, "m": 2, "a": 1}
best, m = "", 0
for k in cnt:
    if cnt[k] > m or (cnt[k] == m and k < best):
        best, m = k, cnt[k]
print(best, m, sorted(cnt, key=lambda k: (-cnt[k], k))[0])
'''), '직접 구현과 sorted(key=) 풀이가 같은 답'),
   exam('딕셔너리는 **키를 넣은 순서**를 기억해요. 그래서 "먼저 나온 글자"는 `>` 로 한 번 훑으면 끝이에요. 문제의 동률 규칙에 밑줄부터 치세요.')]),
outq('출력 결과는?', D('''
s = "level meter"
cnt = {}
for ch in s.replace(" ", ""):
    cnt[ch] = cnt.get(ch, 0) + 1
a = b = ""
ma = mb = 0
for k in cnt:
    if cnt[k] > ma:
        a, ma = k, cnt[k]
    if cnt[k] >= mb:
        b, mb = k, cnt[k]
print(list(cnt.items())[:3])
print(a, ma, b, mb)
print([k for k in cnt if cnt[k] == 1], len(cnt))
'''), '먼저 글자별 횟수를 등장 순서대로 적어요. 가장 큰 횟수를 가진 글자가 하나뿐이면 `>` 와 `>=` 의 결과가 같아요.'),
match('내장함수 풀이와 같은 일을 하는 직접 구현을 이으세요.', [('`max(a)`', '`m = a[0]` 뒤 `if x > m: m = x`'), ('`set(a)` 로 중복 제거', '`if x not in res: res.append(x)`'), ('`s == s[::-1]`', '`s[i] != s[len(s) - 1 - i]` 이면 False'), ('`s.count(c)`', '`if ch == c: n += 1`'), ('`sum(a)`', '`total = 0` 뒤 `total += x`')], '[조건]에 금지된 함수가 보이면 오른쪽 모양을 바로 떠올릴 수 있어야 해요.'),
explain('제곱·정렬 네 가지와 "조건에 맞는 것만 모으기"',
  [T('2023 기출은 "제곱해서 정렬"을 **바꾸는 방법 2가지 × 정렬 방법 2가지**로 쓰게 했어요(12점). 바꾸기는 `map + lambda` 또는 컴프리헨션, 정렬은 `sorted` 또는 직접 정렬이에요.'),
   tabs(('map + sorted', '', 'a = [3, -4, 1]\nprint(sorted(map(lambda x: x * x, a)))'), ('컴프 + sorted', '', 'a = [3, -4, 1]\nprint(sorted([x * x for x in a]))'), ('map + 직접 정렬', 'map 결과는 list 로 바꿔야 인덱스를 쓸 수 있어요.', 'a = [3, -4, 1]\nb = list(map(lambda x: x * x, a))\nfor i in range(len(b) - 1):\n    for j in range(len(b) - 1 - i):\n        if b[j] > b[j + 1]:\n            b[j], b[j + 1] = b[j + 1], b[j]\nprint(b)'), ('컴프 + 직접 정렬', '', 'a = [3, -4, 1]\nb = [x * x for x in a]\nfor i in range(len(b) - 1):\n    for j in range(len(b) - 1 - i):\n        if b[j] > b[j + 1]:\n            b[j], b[j + 1] = b[j + 1], b[j]\nprint(b)')),
   warn('**제곱한 뒤 정렬**과 **정렬한 뒤 제곱**은 음수가 있으면 결과가 달라요. `[3, -4, 1]` → 앞은 `[1, 9, 16]`, 뒤는 `[16, 1, 9]`. 문제의 순서를 그대로 따르세요.')],
  [T('"주사위 5개가 오름차순으로 나온 경우만 모으기"(2023 유형)는 판정을 어떻게 쓰느냐가 전부예요. 이웃한 두 칸을 차례로 비교하면 돼요.'),
   tabs(('sorted 사용', '같은 값 허용(1 3 3 5 6 도 통과)', 'r = [1, 3, 3, 5, 6]\nprint(r == sorted(r))'), ('all 사용', '`<` 면 같은 값 불허, `<=` 면 허용', 'r = [1, 3, 3, 5, 6]\nprint(all(r[i] <= r[i + 1] for i in range(len(r) - 1)))\nprint(all(r[i] < r[i + 1] for i in range(len(r) - 1)))'), ('직접 구현', '깃발 변수 하나', 'r = [1, 3, 3, 5, 6]\nok = True\nfor i in range(len(r) - 1):\n    if r[i] > r[i + 1]:\n        ok = False\n        break\nprint(ok)')),
   key('이웃 비교의 범위는 `range(len(r) - 1)` 이에요. `r[i + 1]` 을 읽기 때문에 마지막 칸에서는 비교를 시작하면 안 돼요.')]),
outq('출력 결과는?', D('''
rolls = [[1, 3, 3, 5, 6], [2, 1, 4, 5, 6], [1, 2, 3, 4, 5], [6, 6, 6, 6, 6]]
up = [r for r in rolls if r == sorted(r)]
strict = [r for r in rolls if all(r[i] < r[i + 1] for i in range(len(r) - 1))]
print(len(up), len(strict), strict[0][-1])
print(sorted(map(lambda x: x * x, [3, -4, 1])), [x * x for x in sorted([3, -4, 1])])
print(sum(map(lambda r: r[0], up)), [sum(r) for r in rolls if r != sorted(r)])
'''), '`r == sorted(r)` 는 같은 값이 이어져도 참이에요. `<` 로 이웃을 비교하면 같은 값이 있는 줄은 탈락해요.'),
spot('[조건] `sorted`, `max`, `set` 을 **사용하지 않고** 작성해야 하는 답안이에요. 조건을 어긴 줄은?', D('''
a = list(map(int, input().split()))
res = []
for x in a:
    if x not in res:
        res.append(x)
big = res[0]
for x in res:
    big = max(big, x)
print(res, big)
'''), 8, '8번 줄의 `max(big, x)` 가 금지된 함수예요. `if x > big: big = x` 로 써야 해요. 결과가 맞아도 조건을 어기면 그 부분 점수는 0점이에요.'),
essay('리스트의 중복을 없애는 두 풀이 ㉮ `result = list(set(a))` 와 ㉯ `for x in a: if x not in result: result.append(x)` 의 **차이점**을 결과의 순서와 연결하여 서술하고, "처음 제출한 순서대로 명단을 출력"해야 할 때 어느 쪽을 써야 하는지 이유와 함께 쓰세요.', '㉮는 set 을 거치므로 코드가 짧지만 set 은 원소의 순서를 보장하지 않아 결과 리스트의 순서가 입력 순서와 달라질 수 있다. ㉯는 앞에서부터 하나씩 확인하며 결과에 없는 값만 추가하므로 처음 등장한 순서가 그대로 유지된다. 처음 제출한 순서대로 출력해야 한다면 순서가 유지되는 ㉯를 써야 한다. (㉮를 쓰려면 sorted 로 정렬 기준을 정해야 하는데, 그것은 제출 순서가 아니다.)', ['set 은 순서를 보장하지 않는다고 썼다', '㉯는 처음 등장한 순서가 유지된다고 썼다', '㉯를 선택하고 순서 유지를 이유로 들었다']),
prac('[기출유사] 최고 기록 두 개의 합 — 두 가지 방법', '기록이 한 줄에 공백으로 주어져요(2개 이상, **음수와 같은 값이 있을 수 있어요**). 가장 큰 두 수의 합을 두 가지 방법으로 구해요.\n\n출력\n1. `방법1: 합` — `sorted` 를 사용\n2. `방법2: 합` — 직접 구현\n3. `1등 x, 2등 y` — 방법2 에서 구한 두 값 (같은 값이 두 번 있으면 둘 다 그 값)\n\n[조건] ○ 방법2 는 `sorted`, `sort`, `max`, `min`, `sum` 을 쓰지 않고 **리스트를 한 번만 훑어서** 구해요',
D('''
a = list(map(int, input().split()))
print("방법1:", sum(sorted(a)[-2:]))
# 초기값은 실제 원소로: 앞의 두 값 중 큰 쪽이 1등
if a[0] >= a[1]:
    first, second = a[0], a[1]
else:
    first, second = a[1], a[0]
for x in a[2:]:
    if x > first:
        second = first          # 옛 1등을 2등으로 먼저 내린다
        first = x
    elif x > second:
        second = x
print("방법2:", first + second)
print(f"1등 {first}, 2등 {second}")
'''), ['3 8 5 9', '-4 -9 -7', '5 5 3', '1 2', '-2 6 -1', '10 9 8 7 6', '0 0 0 0', '-5 -5 -1 -9 -1'],
  starter='a = list(map(int, input().split()))\nprint("방법1:", sum(sorted(a)[-2:]))\nfirst = second = 0   # ← 이 초기값이면 음수 입력에서 틀려요. 고치세요.\n',
  hints=['초기값을 0 으로 두면 `-4 -9 -7` 에서 틀려요. 앞의 두 원소로 시작하세요.', '`for x in a[2:]:` — 세 번째 원소부터 훑어요.', '`if x > first: second = first; first = x` / `elif x > second: second = x`'],
  ex='음수만 있는 입력, 같은 값이 있는 입력, 원소가 딱 2개인 입력이 숨은 테스트예요.'),
prac('[기출유사] 과제 제출 명단 — 중복 제거 두 가지', '과제를 제출한 학생 이름이 제출 순서대로 한 줄에 공백으로 주어져요. 같은 학생이 여러 번 제출했을 수 있어요.\n\n출력\n1. `사전순: …` — 중복 없이 사전순 (`set` 과 `sorted` 사용)\n2. `제출순: …` — 중복 없이 **처음 제출한 순서**\n3. `재제출: 이름(횟수) …` — 2번 이상 제출한 학생을 처음 제출한 순서대로. 없으면 `재제출: 없음`\n4. `인원: n명`\n\n[조건] ○ 2·3번 줄은 `set`, `count` 를 쓰지 않고 직접 구현',
D('''
names = input().split()
print("사전순:", *sorted(set(names)))
order = []
cnt = {}
for n in names:
    if n not in order:              # 처음 본 이름만 추가 → 순서 유지
        order.append(n)
    cnt[n] = cnt.get(n, 0) + 1      # count() 대신 딕셔너리로 세기
print("제출순:", *order)
again = [f"{n}({cnt[n]})" for n in order if cnt[n] >= 2]
if again:
    print("재제출:", *again)
else:
    print("재제출: 없음")
print(f"인원: {len(order)}명")
'''), ['민수 지아 민수 하준 지아 민수', '가 나 다', '솔 솔 솔 솔', '하나', '준 민 준 민 솔 하 솔', '라 다 나 가 가 나 다 라'],
  hints=['1번 줄은 `sorted(set(names))` 를 `*` 로 풀어 출력해요.', '`if n not in order: order.append(n)` 과 `cnt[n] = cnt.get(n, 0) + 1` 을 같은 반복문에서 해요.', '재제출 명단은 `order` 를 돌면서 `cnt[n] >= 2` 인 이름만 `이름(횟수)` 로 만들어요.'],
  ex='같은 "중복 제거"라도 조건(사전순 / 제출순)에 따라 도구가 달라져요.'),
prac('[기출유사] 주사위 기록 — 오름차순만 모으기', '주사위 5개를 던진 기록이 여러 줄 주어져요. **왼쪽부터 값이 줄어들지 않는**(같은 값은 허용) 기록만 모아요.\n\n입력: 첫 줄 `n`, 이어서 n 줄에 주사위 눈 5개(공백 구분)\n\n출력\n- 조건에 맞는 기록을 입력 순서대로 `k번: 1 3 3 5 6 (합 18)` — k 는 입력에서 몇 번째 줄인지(1부터)\n- 마지막 줄 `모은 기록: m개`\n- 그중 **같은 값이 하나도 없는**(엄격한 오름차순) 기록의 수를 `엄격: s개` 로 한 줄 더\n\n[조건] ○ `sorted`, `sort`, `sum` 을 쓰지 않아요 ○ 이웃한 두 칸을 비교',
D('''
n = int(input())
m = s = 0
for k in range(1, n + 1):
    r = list(map(int, input().split()))
    ok = True           # 줄어들지 않는가
    strict = True       # 같은 값도 없는가
    total = 0
    for i in range(len(r)):
        total += r[i]
        if i < len(r) - 1:              # 마지막 칸은 비교를 시작하지 않는다
            if r[i] > r[i + 1]:
                ok = False
            if r[i] >= r[i + 1]:
                strict = False
    if ok:
        m += 1
        print(f"{k}번:", *r, f"(합 {total})")
        if strict:
            s += 1
print(f"모은 기록: {m}개")
print(f"엄격: {s}개")
'''), ['4\n1 3 3 5 6\n2 1 4 5 6\n1 2 3 4 5\n6 6 6 6 6', '2\n5 4 3 2 1\n1 2 3 4 3', '1\n2 3 4 5 6', '3\n1 1 1 1 2\n1 2 2 2 2\n3 3 3 3 3', '5\n6 5 6 5 6\n1 2 3 5 6\n1 1 2 3 4\n2 4 6 6 5\n1 3 4 5 6', '3\n1 2 3 4 5\n1 2 3 4 6\n1 2 3 5 6'],
  hints=['줄마다 깃발 `ok = True` 로 시작해 `r[i] > r[i + 1]` 을 만나면 False 로 바꿔요.', '비교 범위는 `range(len(r) - 1)` — 마지막 칸에서 `r[i + 1]` 을 읽으면 IndexError.', '엄격 판정은 `r[i] >= r[i + 1]` 을 만나면 탈락이에요. 합계는 직접 더해요.'],
  ex='`>` 와 `>=` 한 글자 차이가 "같은 값 허용 / 불허"를 가르는 문제예요.'),
prac('[심화] 최빈 글자 — 동률 규칙 세 가지', '한 줄의 영어 문장에서 가장 많이 나온 글자를 찾아요. **공백은 세지 않고 대소문자는 구분하지 않아요**(모두 소문자로).\n\n출력\n1. `먼저 나온 글자: x (n번)` — 최다 횟수인 글자 중 문장에서 가장 먼저 나온 것\n2. `나중에 나온 글자: y` — 최다 횟수인 글자 중 **처음 등장이 가장 늦은** 것\n3. `사전순 글자: z` — 최다 횟수인 글자 중 사전순으로 가장 앞선 것\n4. `동률: k개` — 최다 횟수를 가진 글자의 수\n\n[조건] ○ `count`, `max`, `min`, `sorted`, `sort` 를 쓰지 않아요 ○ 글자 세기는 딕셔너리로',
D('''
s = input().lower().replace(" ", "")
cnt = {}
for ch in s:
    cnt[ch] = cnt.get(ch, 0) + 1
first = last = alpha = ""
m = 0
for k in cnt:                       # 딕셔너리는 처음 등장한 순서대로 돈다
    if cnt[k] > m:                  # 새 최다 횟수 → 세 답을 모두 새로 시작
        m = cnt[k]
        first = last = alpha = k
        tie = 1
    elif cnt[k] == m:               # 동률
        tie += 1
        last = k                    # 나중에 등장한 글자로 갱신
        if k < alpha:               # 사전순으로 더 앞이면 갱신
            alpha = k
print(f"먼저 나온 글자: {first} ({m}번)")
print(f"나중에 나온 글자: {last}")
print(f"사전순 글자: {alpha}")
print(f"동률: {tie}개")
'''), ['Tomato Motto', 'banana', 'Zebra Apple', 'a', 'Hello World', 'cc bb aa dd', 'Mississippi River'],
  hints=['`input().lower().replace(" ", "")` 로 먼저 정리해요.', '딕셔너리를 돌 때 `>` 이면 새 최다(세 변수 모두 교체), `==` 이면 동률 처리예요.', '동률일 때: 개수 +1, "나중" 은 무조건 교체, "사전순" 은 `k < alpha` 일 때만 교체.'],
  ex='한 번의 순회로 세 가지 동률 규칙을 모두 처리해요. 새 최다 횟수를 만나면 동률 개수를 1 로 되돌리는 것을 잊지 마세요.'),
prac('[심화] 회문 검사기 — 뒤집기 금지', '문장 여러 개를 검사해요. **글자와 숫자만 남기고**(공백·문장부호 제거) 소문자로 바꾼 뒤 회문인지 판정해요.\n\n입력: 첫 줄 `n`, 이어서 n 줄에 문장\n\n출력: 문장마다 한 줄\n- 회문이면 `회문 (길이 L)` — L 은 정리한 뒤의 글자 수\n- 아니면 `아님 (k번째: x ≠ y)` — 앞에서부터 처음 어긋난 위치 k(1부터)와 그 자리의 앞쪽 글자 x, 짝이 되는 뒤쪽 글자 y\n\n[조건] ○ `[::-1]`, `reversed`, `reverse` 를 쓰지 않아요 ○ 글자·숫자 판정은 `isalnum()`',
D('''
def check(s):
    t = ""
    for ch in s:
        if ch.isalnum():            # 글자·숫자만 남긴다
            t += ch.lower()
    i, j = 0, len(t) - 1
    while i < j:
        if t[i] != t[j]:
            return f"아님 ({i + 1}번째: {t[i]} ≠ {t[j]})"
        i += 1
        j -= 1
    return f"회문 (길이 {len(t)})"
n = int(input())
for _ in range(n):
    print(check(input()))
'''), ['3\nWas it a cat I saw?\nNo lemon, no melon\nStep on no pet', '2\nlevel\nlever', '1\n!!', '3\nA\nab\nMadam, I\'m Adam', '2\n12321\n12 3 4 21', '2\n다시 합창합시다\n소주 만 병만 주소!'],
  hints=['먼저 `isalnum()` 인 글자만 모아 소문자 문자열 `t` 를 만들어요.', '`i, j = 0, len(t) - 1` 로 시작해 `while i < j:` 동안 비교해요.', '어긋나면 `i + 1` 번째(1부터 세기), `t[i]`, `t[j]` 를 담아 바로 return 해요.'],
  ex='전처리와 검사를 분리하면 변형 조건이 붙어도 검사 코드는 그대로예요. 정리한 결과가 빈 문자열이면 반복 없이 회문(길이 0)이 돼요.'),
)

# ============================================================ D3
_bub_bug = D('''
a = [2, 3, 1, 4]
n = len(a)
for i in range(n - 1):
    for j in range(n - 1 - i):
        swapped = False
        if a[j] > a[j + 1]:
            a[j], a[j + 1] = a[j + 1], a[j]
            swapped = True
    if not swapped:
        break
print(a)
''')
_bl = _bub_bug.split('\n')
assert _bl[4].strip() == 'swapped = False'
_bub_fix = '\n'.join(_bl[:3] + ['    swapped = False'] + [_bl[3]] + _bl[5:])
assert run(_bub_bug) != '[1, 2, 3, 4]' and run(_bub_fix) == '[1, 2, 3, 4]', (run(_bub_bug), run(_bub_fix))

_cnt = D('''
def bubble(a, early):
    a = a[:]
    n = len(a)
    comp = 0
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            comp += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if early and not swapped:
            break
    return comp
print(bubble([1, 2, 3, 4, 5, 6], False), bubble([1, 2, 3, 4, 5, 6], True), bubble([6, 5, 4, 3, 2, 1], True))
''')
assert run(_cnt) == '15 5 15', run(_cnt)

_idx_bug = D('''
a = [5, 2, 9, 1]
n = len(a)
for i in range(n - 1):
    for j in range(n - i):
        if a[j] > a[j + 1]:
            a[j], a[j + 1] = a[j + 1], a[j]
print(a)
''')
assert errline(_idx_bug) == 5 and err(_idx_bug) == 'IndexError'

D3 = lesson('3강. 정렬 직접 구현 — 선택·버블·조기 종료', 50,
'- **선택 정렬**: 남은 칸에서 가장 작은 값의 **위치**를 기억 → 바퀴 끝에 교환 **한 번**. 비교는 항상 n(n-1)/2 번\n- **버블 정렬**: 이웃끼리 비교·교환. i 번째 바퀴가 끝나면 뒤쪽 i+1 칸이 확정 → 안쪽 범위는 `n - 1 - i`\n- **swapped**: 한 바퀴 동안 교환이 있었는지 기억하는 깃발. 바깥 반복 **안, 안쪽 반복 밖**에서 False 로 초기화\n- 교환이 없던 바퀴 = 이미 정렬됨 → `break` (조기 종료). 없으면 정렬된 입력에도 끝까지 비교한다\n- 내림차순은 **비교 부등호 한 곳**만 뒤집는다\n- 여러 기준은 `(점수, 시간)` 을 차례로 비교. 버블의 `>` 는 안정, `>=` 는 불안정, 선택 정렬은 불안정',
review('🔁 2강 복습', [T('"쓰기 / 안 쓰기" 쌍의 핵심을 다시 확인해요.'), flip(['최댓값 변수의 초기값', '0 이 아니라 리스트의 실제 원소'], ['1등이 바뀔 때 먼저 할 일', '`second = first` (옛 1등을 2등으로)'], ['입력 순서를 지키는 중복 제거', '`if x not in res: res.append(x)`'], ['양 끝 비교의 반복 조건', '`while i < j`'], ['동률일 때 먼저 나온 것을 남기려면', '`>` 로 비교 (`>=` 는 나중 것)'], ['"오름차순인가" 이웃 비교의 범위', '`range(len(r) - 1)`'])]),
outq('복습 — 출력 결과는?', D('''
a = [4, -2, 7, 7, -5]
first, second = max(a[0], a[1]), min(a[0], a[1])
for x in a[2:]:
    if x > first:
        first, second = x, first
    elif x > second:
        second = x
uniq = []
for x in a:
    if x not in uniq:
        uniq.append(x)
print(first, second, uniq)
print(all(uniq[i] < uniq[i + 1] for i in range(len(uniq) - 1)), sorted(set(a))[1])
'''), '`first, second = x, first` 는 오른쪽을 먼저 계산하므로 옛 1등이 안전하게 2등이 돼요. 두 번째 7 은 `elif x > second` 에서 2등이 돼요.', review=True),
explain('선택 정렬 — 위치를 기억하고 교환은 한 번',
  [T('선택 정렬은 "남은 칸 중 **가장 작은 값이 어디 있는지**"를 찾아 맨 앞 칸과 바꿔요. 안쪽 반복이 하는 일은 교환이 아니라 **위치 기억**이에요. 교환은 안쪽 반복이 끝난 뒤 한 번만 해요.'),
   trace(D('''
a = [29, 10, 14, 37, 13]
n = len(a)
for i in range(n - 1):
    m = i
    for j in range(i + 1, n):
        if a[j] < a[m]:
            m = j
    a[i], a[m] = a[m], a[i]
    print(i, m, a)
'''), 'm = 지금까지 본 것 중 가장 작은 값의 위치'),
   key('비교는 `a[j] < a[i]` 가 아니라 **`a[j] < a[m]`** 이에요. i 번 칸이 아니라 "지금까지의 최솟값"과 비교해야 해요. 교환 줄의 들여쓰기는 **바깥 for 와 같은 깊이 + 한 칸**(안쪽 for 밖)이에요.')],
  [T('선택 정렬의 **비교 횟수는 입력과 상관없이** 정해져 있어요. 바퀴마다 n-1, n-2, …, 1 번이라 합이 n(n-1)/2 예요. 이미 정렬된 리스트를 넣어도 똑같이 비교해요. 교환은 바퀴당 최대 한 번이에요.'),
   C(D('''
def selection(a):
    a = a[:]
    n = len(a)
    comp = swap = 0
    for i in range(n - 1):
        m = i
        for j in range(i + 1, n):
            comp += 1
            if a[j] < a[m]:
                m = j
        if m != i:
            a[i], a[m] = a[m], a[i]
            swap += 1
    return a, comp, swap
print(selection([29, 10, 14, 37, 13]))
print(selection([1, 2, 3, 4, 5]))
print(selection([5, 4, 3, 2, 1]))
'''), '비교는 늘 10번, 교환 횟수만 달라져요'),
   exam('"실제로 자리가 바뀐 횟수"를 물으면 `if m != i:` 일 때만 세요. 조건 없이 세면 제자리 교환까지 세어서 항상 n-1 이 돼요.')],
  [T('내림차순으로 바꾸려면 **비교 부등호 한 곳**만 뒤집어요. "가장 큰 값의 위치"를 찾게 되는 거예요. 변수 이름(m)이나 교환 줄은 그대로예요.'),
   cmp('오름차순', 'if a[j] < a[m]:\n    m = j', '내림차순', 'if a[j] > a[m]:\n    m = j', '가장 작은 값의 위치', '가장 큰 값의 위치', tones=('good', 'good')),
   tip('2026 1학기 합병 정렬 문항처럼 "**내림차순으로 고치려면 몇 번 줄을 어떻게 바꾸는가**"를 줄 번호로 물을 수 있어요. 비교가 일어나는 줄이 어디인지 표시해 두세요.')]),
outq('출력 결과는? (내림차순 선택 정렬)', D('''
a = [3, 9, 4, 9, 1]
n = len(a)
for i in range(n - 1):
    m = i
    for j in range(i + 1, n):
        if a[j] > a[m]:
            m = j
    if m != i:
        a[i], a[m] = a[m], a[i]
        print(i, m, a)
print(a)
'''), '`>` 는 더 클 때만 위치를 바꾸므로 9 가 두 개면 **앞쪽 9** 의 위치가 남아요. 위치가 같으면(`m == i`) 교환도 출력도 없어요.'),
order('오름차순 선택 정렬 코드예요. 순서대로 놓으세요.', ['a = [3, 1, 2]', 'for i in range(len(a) - 1):', '    m = i', '    for j in range(i + 1, len(a)):', '        if a[j] < a[m]:', '            m = j', '    a[i], a[m] = a[m], a[i]', 'print(a)'], '`m = i` 로 시작 → 뒤쪽을 훑으며 더 작은 값의 위치로 갱신 → 안쪽 반복이 끝난 뒤 교환 한 번.'),
explain('버블 정렬 — n-1-i 와 swapped',
  [T('버블 정렬은 **이웃한 두 칸**을 비교해 순서가 틀리면 바로 바꿔요. 한 바퀴를 돌면 가장 큰 값이 맨 뒤까지 밀려가서 **자리가 확정**돼요. 그래서 다음 바퀴는 확정된 칸을 빼고 돌아도 돼요.'),
   trace(D('''
a = [5, 1, 4, 2]
n = len(a)
for i in range(n - 1):
    for j in range(n - 1 - i):
        if a[j] > a[j + 1]:
            a[j], a[j + 1] = a[j + 1], a[j]
    print(i, a)
'''), 'i 번째 바퀴 뒤에는 뒤쪽 i+1 칸이 확정'),
   key('안쪽 범위 `range(n - 1 - i)` 의 뜻: `-1` 은 `a[j + 1]` 을 읽기 때문에, `-i` 는 **이미 확정된 뒤쪽 i 칸을 다시 비교하지 않으려고**예요. `range(n - 1)` 로 써도 결과는 같지만 쓸데없는 비교를 해요.')],
  [T('리스트가 중간에 이미 정렬됐다면 남은 바퀴는 낭비예요. **한 바퀴 동안 교환이 한 번도 없었다**면 모든 이웃이 올바른 순서라는 뜻이므로 거기서 끝내요. 그 사실을 기억하는 변수가 `swapped` 예요.'),
   C(D('''
a = [3, 1, 2, 4, 5]
n = len(a)
comp = swap = 0
for i in range(n - 1):
    swapped = False
    for j in range(n - 1 - i):
        comp += 1
        if a[j] > a[j + 1]:
            a[j], a[j + 1] = a[j + 1], a[j]
            swap += 1
            swapped = True
    print(i, a, swapped)
    if not swapped:
        break
print(comp, swap)
'''), '교환이 없던 바퀴에서 break'),
   warn('`swapped = False` 의 위치가 감점 포인트예요. **바깥 for 안, 안쪽 for 밖**(바퀴가 시작될 때마다)에 둬요. 바깥 for 밖에 두면 한 번 True 가 된 뒤 영영 True 라서 조기 종료가 안 되고, 안쪽 for 안에 두면 마지막 비교 결과만 남아 **정렬이 덜 된 채 끝날 수 있어요**.')],
  [T('횟수를 정리해요. n 개를 정렬할 때 조기 종료가 없으면 비교는 항상 n(n-1)/2 번이에요. 조기 종료가 있으면 **이미 정렬된 입력은 한 바퀴(n-1 번 비교)** 로 끝나요. 거꾸로 정렬된 입력은 조기 종료가 있어도 줄어들지 않아요.'),
   tabs(('n = 6, 조기 종료 없음', '5 + 4 + 3 + 2 + 1 = **15번** (입력과 무관)'), ('n = 6, 이미 정렬됨, 조기 종료 있음', '첫 바퀴 5번 비교, 교환 0 → break. **5번**'), ('n = 6, 역순, 조기 종료 있음', '매 바퀴 교환이 일어나 끝까지. **15번**')),
   exam('2026 1학기 기출 서술형 유형: "**swapped 변수의 역할**을 쓰시오". 답의 뼈대는 ① 한 바퀴 동안 교환이 있었는지 기록 ② 교환이 없었다면 이미 정렬된 것 ③ 그래서 반복을 일찍 끝내 불필요한 비교를 줄임 — 세 문장이에요.')]),
outq('출력 결과는?', D('''
a = [2, 1, 3, 5, 4]
n = len(a)
comp = swap = 0
for i in range(n - 1):
    swapped = False
    for j in range(n - 1 - i):
        comp += 1
        if a[j] > a[j + 1]:
            a[j], a[j + 1] = a[j + 1], a[j]
            swap += 1
            swapped = True
    if not swapped:
        break
print(a, i, comp, swap)
'''), '첫 바퀴(비교 4번)에서 교환 2번, 둘째 바퀴(비교 3번)에서 교환이 없어 break — 그때의 i 는 1 이에요.'),
sh('6개의 수 `[1, 2, 3, 4, 5, 6]` 을 **swapped 조기 종료가 있는** 버블 정렬(오름차순, 안쪽 범위 `n - 1 - i`)로 정렬하면 비교는 모두 몇 번 일어날까요? (숫자만)', 5, '이미 정렬돼 있어 첫 바퀴의 5번 비교에서 교환이 한 번도 없고, 바로 break 해요. 조기 종료가 없다면 5 + 4 + 3 + 2 + 1 = 15번이에요.', alts=['5번']),
spot('오름차순 버블 정렬인데 `[2, 3, 1, 4]` 를 넣으면 `[2, 1, 3, 4]` 가 출력돼요. **잘못된 줄**은?', _bub_bug, 5, '`swapped = False` 가 안쪽 반복 안에 있어서 비교할 때마다 깃발이 꺼져요. 첫 바퀴의 **마지막 비교**(3 과 4)에서 교환이 없었다는 이유로 정렬이 끝난 줄 알고 break 해요. 5번 줄을 안쪽 for 위(바깥 for 바로 아래)로 옮겨야 해요.'),
spot('아래 버블 정렬은 실행하면 **예외**가 발생해요. 예외가 발생하는 줄은?', _idx_bug, 5, '안쪽 범위가 `n - i` 라서 첫 바퀴에 j 가 3 까지 가요. 5번 줄에서 `a[j + 1]` = `a[4]` 를 읽다가 IndexError 가 나요. 원인은 4번 줄의 범위이고, `range(n - 1 - i)` 로 고쳐야 해요.'),
essay('버블 정렬 코드에서 `swapped` 변수의 **역할**을 쓰고, 이 변수와 `if not swapped: break` 가 **없을 때의 문제점**을 "이미 정렬된 리스트"의 경우와 연결하여 서술하세요.', 'swapped 는 한 바퀴(안쪽 반복 한 번) 동안 교환이 한 번이라도 일어났는지를 기록하는 변수이다. 바퀴를 시작할 때 False 로 두고 교환할 때 True 로 바꾼다. 한 바퀴가 끝났는데 swapped 가 False 이면 모든 이웃한 값이 올바른 순서라는 뜻이므로 이미 정렬이 끝난 것이고, break 로 반복을 일찍 끝낸다. 이 변수가 없으면 리스트가 이미 정렬되어 있어도 남은 바퀴를 모두 돌며 n(n-1)/2 번의 비교를 하게 되어 불필요한 연산이 생긴다. (조기 종료가 있으면 정렬된 리스트는 한 바퀴, n-1 번의 비교로 끝난다.)', ['한 바퀴 동안 교환이 있었는지 기록한다고 썼다', '교환이 없으면 이미 정렬된 것이라고 썼다', 'break 로 반복을 일찍 끝낸다(조기 종료)고 썼다', '없으면 정렬된 리스트에도 끝까지 비교해 불필요한 연산이 생긴다고 썼다']),
essay('버블 정렬(오름차순)의 안쪽 반복을 `for j in range(n - 1):` 대신 `for j in range(n - 1 - i):` 로 써도 **올바르게 정렬되는 이유**를 "한 바퀴가 끝날 때마다 일어나는 일"과 연결하여 서술하세요.', '오름차순 버블 정렬은 한 바퀴를 돌 때마다 그 바퀴에서 비교한 범위의 가장 큰 값이 이웃 교환을 거쳐 범위의 맨 뒤로 이동한다. 따라서 i 번째 바퀴(0부터)가 시작될 때는 뒤쪽 i 개의 칸에 이미 가장 큰 값들이 순서대로 자리를 잡아 확정되어 있다. 확정된 칸은 다시 비교해도 교환이 일어나지 않으므로 비교 범위에서 제외해도 결과가 같고, 그만큼 비교 횟수가 줄어든다.', ['한 바퀴마다 가장 큰 값이 맨 뒤로 이동해 확정된다고 썼다', 'i 번째 바퀴에서는 뒤쪽 i 칸이 이미 정렬(확정)되어 있다고 썼다', '확정된 칸은 비교해도 교환이 없으므로 제외해도 된다고 썼다']),
explain('나눠서 정렬하기 · 여러 기준 · 안정성',
  [T('2024 기출(18점)은 **짝수는 선택 정렬, 홀수는 버블 정렬**로 따로 정렬하게 했어요. 한 리스트 안에서 억지로 하지 말고 **먼저 둘로 나눈 뒤** 각각 정렬하면 지금까지의 코드를 그대로 쓸 수 있어요.'),
   C(D('''
data = [7, 4, 9, 2, 8, 1, 6]
even = [x for x in data if x % 2 == 0]
odd = [x for x in data if x % 2 == 1]
for i in range(len(even) - 1):              # 선택 정렬 (오름차순)
    m = i
    for j in range(i + 1, len(even)):
        if even[j] < even[m]:
            m = j
    even[i], even[m] = even[m], even[i]
for i in range(len(odd) - 1):               # 버블 정렬 (내림차순)
    swapped = False
    for j in range(len(odd) - 1 - i):
        if odd[j] < odd[j + 1]:
            odd[j], odd[j + 1] = odd[j + 1], odd[j]
            swapped = True
    if not swapped:
        break
print(even, odd)
'''), '나누기 → 각각 정렬'),
   tip('원소가 0개나 1개인 리스트는 `range(len(a) - 1)` 이 비어서 반복에 들어가지 않아요. 따로 검사하지 않아도 오류가 없어요.')],
  [T('`[이름, 점수]` 같은 **리스트의 리스트**를 정렬할 때는 비교하는 칸만 바꾸면 돼요. 교환은 **줄 전체**를 바꿔요. 기준이 둘이면 "첫 기준이 다르면 그것으로, 같으면 둘째 기준으로"를 조건식으로 써요.'),
   C(D('''
rows = [["민", 80, 31], ["솔", 95, 40], ["준", 80, 27], ["하", 95, 40]]
n = len(rows)
for i in range(n - 1):
    for j in range(n - 1 - i):
        x, y = rows[j], rows[j + 1]
        # 점수 내림차순, 같으면 시간 오름차순
        if x[1] < y[1] or (x[1] == y[1] and x[2] > y[2]):
            rows[j], rows[j + 1] = y, x
print([r[0] for r in rows])
'''), '"바꿔야 하는 경우"를 조건식으로'),
   key('조건식은 "**x 가 y 보다 뒤에 와야 하는가**"를 써요. 튜플 비교로 줄일 수도 있어요: `(-x[1], x[2]) > (-y[1], y[2])` 이면 교환.')],
  [T('**안정 정렬**은 기준 값이 같은 원소들의 원래 순서를 지키는 정렬이에요. 버블 정렬은 **이웃끼리만** 바꾸므로 `>` 로 비교하면 같은 값은 서로 넘어가지 않아 안정이에요. `>=` 로 쓰면 같은 값끼리도 바꿔서 순서가 뒤집혀요. 선택 정렬은 멀리 있는 칸과 바꾸기 때문에 같은 값의 순서가 바뀔 수 있어요.'),
   C(D('''
rows = [["가", 2], ["나", 2], ["다", 1]]
b = list(rows)
for i in range(len(b) - 1):
    for j in range(len(b) - 1 - i):
        if b[j][1] > b[j + 1][1]:
            b[j], b[j + 1] = b[j + 1], b[j]
s = list(rows)
for i in range(len(s) - 1):
    m = i
    for j in range(i + 1, len(s)):
        if s[j][1] < s[m][1]:
            m = j
    s[i], s[m] = s[m], s[i]
print([r[0] for r in b], [r[0] for r in s])
'''), '버블은 가 → 나 순서 유지, 선택은 뒤집힘'),
   exam('"점수가 같으면 **입력 순서대로**"라는 조건이 있으면 버블 정렬 + `>`(또는 `<`) 로 쓰세요. `>=` 를 쓰거나 선택 정렬을 쓰면 숨은 테스트에서 틀려요.')]),
outq('출력 결과는?', D('''
rows = [["a", 3], ["b", 1], ["c", 3], ["d", 2]]
n = len(rows)
for i in range(n - 1):
    swapped = False
    for j in range(n - 1 - i):
        if rows[j][1] < rows[j + 1][1]:
            rows[j], rows[j + 1] = rows[j + 1], rows[j]
            swapped = True
    print(i, "".join(r[0] for r in rows), swapped)
    if not swapped:
        break
'''), '점수 내림차순 버블 정렬이에요. `<` 로 비교하므로 점수가 3 으로 같은 a 와 c 는 서로 넘어가지 않아요(안정).'),
ch('오름차순 버블 정렬의 비교 줄 `if a[j][1] > a[j + 1][1]:` 을 아래처럼 바꿨을 때, **기준 값이 같은 원소들의 입력 순서가 뒤집힐 수 있는** 것은?', ['`if a[j][1] > a[j + 1][1]:` 그대로 둔다', '`if a[j + 1][1] < a[j][1]:`', '`if a[j][1] >= a[j + 1][1]:`', '`if not a[j][1] <= a[j + 1][1]:`'], 3, '①②④는 모두 "앞이 더 클 때만 교환"으로 같은 뜻이에요. ③만 값이 같을 때도 교환해서 같은 값끼리 순서가 바뀌어요(불안정).'),
fill('`[이름, 점수]` 목록을 **점수 내림차순, 같으면 이름 사전순**으로 버블 정렬해요. 빈칸을 채우세요.', D('''
rows = [["다", 70], ["가", 90], ["나", 70], ["라", 90]]
n = len(rows)
for i in range(n - 1):
    for j in range(___):
        x, y = rows[j], rows[j + 1]
        if x[1] < y[1] or (x[1] ___ y[1] and x[0] > y[0]):
            rows[j], rows[j + 1] = y, x
print([r[0] for r in rows])
'''), [['n - 1 - i', 'n-1-i', 'n - i - 1', 'n-i-1'], '=='], '점수가 작은 쪽이 뒤로, 점수가 **같을 때만** 이름을 비교해 사전순으로 뒤인 쪽이 뒤로 가요.', expect="['가', '라', '나', '다']"),
prac('[기출유사] 학급문고 번호 정리 — 짝수는 선택, 홀수는 버블', '책 번호가 한 줄에 공백으로 주어져요. 짝수 번호와 홀수 번호를 나눠 각각 정렬해요.\n\n출력\n1. `짝수: …` — **선택 정렬**로 오름차순. 없으면 `짝수: 없음`\n2. `홀수: …` — **버블 정렬**로 내림차순(swapped 조기 종료 포함). 없으면 `홀수: 없음`\n3. `비교 횟수: 선택 c1번, 버블 c2번`\n\n[조건] ○ `sorted`, `sort`, `min`, `max` 를 쓰지 않아요 ○ 버블 정렬의 안쪽 범위는 정렬이 끝난 뒤쪽을 제외 ○ 한 바퀴 동안 교환이 없으면 종료',
D('''
data = list(map(int, input().split()))
even = [x for x in data if x % 2 == 0]
odd = [x for x in data if x % 2 != 0]
c1 = c2 = 0
# 선택 정렬 (오름차순): 가장 작은 값의 위치를 찾아 한 번 교환
for i in range(len(even) - 1):
    m = i
    for j in range(i + 1, len(even)):
        c1 += 1
        if even[j] < even[m]:
            m = j
    even[i], even[m] = even[m], even[i]
# 버블 정렬 (내림차순): 정렬된 뒤쪽 제외 + 조기 종료
for i in range(len(odd) - 1):
    swapped = False
    for j in range(len(odd) - 1 - i):
        c2 += 1
        if odd[j] < odd[j + 1]:
            odd[j], odd[j + 1] = odd[j + 1], odd[j]
            swapped = True
    if not swapped:
        break
if even:
    print("짝수:", *even)
else:
    print("짝수: 없음")
if odd:
    print("홀수:", *odd)
else:
    print("홀수: 없음")
print(f"비교 횟수: 선택 {c1}번, 버블 {c2}번")
'''), ['7 4 9 2 8 1 6', '9 7 5 3 1', '2 4 6 8', '5', '1 3 5 7 9 10 8', '12 3 12 3 7 0 -4 -3', '6 1'],
  hints=['먼저 컴프리헨션으로 `even`, `odd` 두 리스트로 나눠요.', '선택 정렬: `m = i` → `if even[j] < even[m]: m = j` → 안쪽 반복이 끝난 뒤 교환. 비교할 때마다 `c1 += 1`.', '버블 내림차순: `if odd[j] < odd[j + 1]` 일 때 교환, 바퀴 끝에 `if not swapped: break`.'],
  ex='홀수가 이미 내림차순(예: 9 7 5 3 1)이면 버블 비교는 한 바퀴(4번)로 끝나요. 선택 정렬은 입력과 상관없이 k(k-1)/2 번이에요.'),
prac('[기출유사] 버블 정렬 중계 — 바퀴마다 출력', '정수들이 한 줄에 공백으로 주어져요. 오름차순 버블 정렬을 하면서 **바퀴가 끝날 때마다** 리스트를 출력해요.\n\n출력\n- 바퀴마다 `k바퀴: …` (k 는 1부터, 값은 공백 구분)\n- 교환이 없던 바퀴도 출력한 뒤 정렬을 끝내요\n- 마지막 줄 `총 k바퀴, 비교 c번, 교환 s번`\n- 수가 1개면 바퀴 없이 `총 0바퀴, 비교 0번, 교환 0번` 만\n\n[조건] ○ `sorted`, `sort` 금지 ○ 안쪽 범위에서 정렬된 부분 제외 ○ swapped 로 조기 종료',
D('''
a = list(map(int, input().split()))
n = len(a)
rounds = comp = swap = 0
for i in range(n - 1):
    swapped = False                 # 바퀴를 시작할 때마다 깃발을 내린다
    for j in range(n - 1 - i):      # 뒤쪽 i 칸은 이미 확정
        comp += 1
        if a[j] > a[j + 1]:
            a[j], a[j + 1] = a[j + 1], a[j]
            swap += 1
            swapped = True
    rounds += 1
    print(f"{rounds}바퀴:", *a)
    if not swapped:                 # 교환이 없었다 = 이미 정렬됨
        break
print(f"총 {rounds}바퀴, 비교 {comp}번, 교환 {swap}번")
'''), ['3 1 2 4 5', '1 2 3 4', '4 3 2 1', '7', '2 1', '5 1 4 2 8 8 3', '1 3 2 4 6 5'],
  hints=['바깥 for 바로 아래에서 `swapped = False`.', '안쪽은 `range(n - 1 - i)`, 비교할 때마다 `comp += 1`, 교환할 때마다 `swap += 1` 과 `swapped = True`.', '바퀴 출력 **뒤에** `if not swapped: break` — 교환이 없던 바퀴도 출력해야 해요.'],
  ex='이미 정렬된 입력은 1바퀴만 출력하고 끝나요. 역순 입력은 n-1 바퀴를 모두 돌아요.'),
prac('[심화] 기록 순위표 — 여러 기준 직접 정렬', '대회 기록을 정렬해 순위표를 만들어요.\n\n입력: 첫 줄 `n`, 이어서 n 줄에 `이름 점수 시간`\n\n정렬 기준: ① **점수 높은 순** ② 점수가 같으면 **시간 짧은 순** ③ 둘 다 같으면 **입력된 순서 그대로**\n\n출력: `k위 이름 점수 시간` 을 n 줄 (k 는 1부터 차례대로)\n\n[조건] ○ `sorted`, `sort`, `lambda` 를 쓰지 않아요 ○ 직접 구현한 정렬로 ○ ③번 기준 때문에 **같은 기록끼리 순서가 바뀌지 않는** 정렬이어야 해요',
D('''
n = int(input())
rows = []
for _ in range(n):
    name, score, t = input().split()
    rows.append([name, int(score), int(t)])
# 버블 정렬: 이웃끼리만 바꾸고, "확실히 뒤에 와야 할 때만" 바꾸므로 안정
for i in range(n - 1):
    swapped = False
    for j in range(n - 1 - i):
        x, y = rows[j], rows[j + 1]
        if x[1] < y[1] or (x[1] == y[1] and x[2] > y[2]):
            rows[j], rows[j + 1] = y, x
            swapped = True
    if not swapped:
        break
for k in range(n):
    print(f"{k + 1}위", *rows[k])
'''), ['4\n민 80 31\n솔 95 40\n준 80 27\n하 95 40', '3\n가 70 10\n나 70 10\n다 70 10', '1\n혼자 50 5', '5\n다 60 9\n가 90 30\n나 60 9\n라 90 25\n마 60 8', '4\nd 1 1\nc 2 2\nb 3 3\na 4 4', '6\n가 50 20\n나 50 20\n다 80 20\n라 50 19\n마 80 20\n바 50 20'],
  hints=['`[이름, 점수, 시간]` 리스트로 모으고 버블 정렬을 써요(선택 정렬은 같은 기록의 순서가 바뀔 수 있어요).', '교환 조건: `x[1] < y[1] or (x[1] == y[1] and x[2] > y[2])`.', '둘 다 같을 때는 조건이 거짓이라 교환하지 않아요 — 그래서 입력 순서가 지켜져요.'],
  ex='조건식에 `<=`, `>=` 를 쓰면 완전히 같은 기록끼리도 교환되어 ③번 기준이 깨져요.'),
prac('[심화] 선택 정렬 교환 일지', '정수들이 한 줄에 공백으로 주어져요. **내림차순 선택 정렬**을 하면서 실제로 자리가 바뀐 교환만 기록해요.\n\n출력\n- 교환이 일어날 때마다 `i↔m: …` — i, m 은 바뀐 두 칸의 인덱스(0부터, i < m), 뒤에는 교환 직후의 리스트(공백 구분)\n- 마지막 줄 `교환 s번 / 비교 c번`\n\n[조건] ○ `sorted`, `sort`, `max`, `min`, `index` 금지 ○ 가장 큰 값이 여러 개면 **가장 앞의 것**을 고르세요 ○ 고른 위치가 제자리(m == i)면 교환하지 않아요',
D('''
a = list(map(int, input().split()))
n = len(a)
swap = comp = 0
for i in range(n - 1):
    m = i
    for j in range(i + 1, n):
        comp += 1
        if a[j] > a[m]:             # 더 클 때만 갱신 → 같은 값이면 앞의 것이 남는다
            m = j
    if m != i:                      # 제자리면 교환하지 않는다
        a[i], a[m] = a[m], a[i]
        swap += 1
        print(f"{i}↔{m}:", *a)
print(f"교환 {swap}번 / 비교 {comp}번")
'''), ['3 9 4 9 1', '5 4 3 2 1', '1 2 3 4 5', '8', '2 2 2', '4 7 1 7 9 3', '-1 -5 0 -5'],
  hints=['`m = i` 로 시작해 `a[j] > a[m]` 일 때만 `m = j`.', '안쪽 반복이 끝난 뒤 `if m != i:` 일 때만 교환하고 출력해요.', '비교 횟수는 안쪽 반복에서 매번 +1 — 입력과 상관없이 n(n-1)/2 가 나와요.'],
  ex='이미 내림차순인 입력은 교환 0번이지만 비교는 그대로 n(n-1)/2 번이에요 — 선택 정렬에는 조기 종료가 없다는 것을 숫자로 확인해요.'),
)
