import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lotc import *


def build(C):
    lesson09(C)
    lesson10(C)
    lesson11(C)
    lesson12(C)
    lesson13(C)


# =====================================================================
def lesson09(C):
    L = C.lesson('β-09 set: 중복 없는 주머니', 25,
'''- set 은 **중복이 없고 순서가 없는** 자료형. `set(리스트)` 로 중복 제거, 빈 set 은 `set()` (`{}` 는 딕셔너리!)
- `add` 추가 · `remove` 삭제(없으면 **KeyError**) · `discard` 삭제(없어도 조용히 넘어감)
- 합 `|`·`union` / 교 `&`·`intersection` / 차 `-`·`difference` / 대칭차 `^`·`symmetric_difference`
- 연산자는 **양쪽 모두 set** 이어야 하고, 메서드는 괄호 안에 리스트도 받아요.
- `x in set` 은 리스트보다 훨씬 빨라요 → "이미 나온 적 있나?" 검사에 딱!''')

    L.review('🔁 지난 시간 복습: 딕셔너리',
        [T('지난 두 레슨에서 딕셔너리로 **누적·빈도 세기**(`d[k] = d.get(k, 0) + 1`), **최댓값 찾기**(`max(d.values())`),\n'
           '**range 키·중첩 딕셔너리·list of dict** 를 다뤘어요. 오늘 배울 set 은 딕셔너리에서 **값을 뺀 키만의 주머니**라고 생각하면 쉬워요.'),
         REVEAL_RUN('`"banana"` 의 글자 빈도 딕셔너리는?',
                    'cnt = {}\nfor ch in "banana":\n    cnt[ch] = cnt.get(ch, 0) + 1\nprint(cnt)')])
    L.output('복습: 출력은?', '''\
votes = ["kim", "lee", "kim", "park", "kim", "lee"]
cnt = {}
for v in votes:
    cnt[v] = cnt.get(v, 0) + 1
best = max(cnt.values())
for name in cnt:
    if cnt[name] == best:
        print(name, best)''',
        '`get(v, 0) + 1` 로 표를 세면 kim 3, lee 2, park 1. 가장 큰 값 3 을 가진 키를 찾아요.\n\n```\n{out}\n```', review=True)
    L.output('복습: list of dict — 출력은?', '''\
books = [{"title": "A", "page": 120}, {"title": "B", "page": 300}, {"title": "C", "page": 90}]
total = 0
for b in books:
    total += b["page"]
print(total)
print(books[1]["title"])''',
        '리스트에서 딕셔너리를 하나씩 꺼내 `b["page"]` 로 값을 읽어요. `books[1]` 은 두 번째 딕셔너리예요.\n\n```\n{out}\n```', review=True)

    L.explain('set 은 중복 없는 주머니',
        [T('set 은 `{1, 2, 3}` 처럼 중괄호로 쓰지만 **키: 값** 이 없어요.\n'
           '같은 값을 여러 번 넣어도 **하나만** 남아요. 그래서 `set(리스트)` 는 **중복 제거**의 단골 도구예요.'),
         CODE('nums = [3, 1, 3, 2, 1, 3]\ns = set(nums)\nprint(len(nums), len(s))\nprint(sorted(s))', '중복 제거')],
        [T('set 은 **순서가 없어서** 인덱스로 꺼낼 수 없어요. 출력 순서도 넣은 순서와 다를 수 있어요.\n'
           '순서대로 보고 싶으면 `sorted(s)` 로 **정렬된 리스트**를 만들어요.'),
         CMP(side('가능', 'for 로 돌기, in 검사, len', 's = {5, 7, 9}\nfor x in sorted(s):\n    print(x)\nprint(7 in s)', 'good'),
             side('불가능', '인덱스 접근 → TypeError', 's = {5, 7, 9}\nprint(s[0])', 'bad', expect_error=True))],
        [T('빈 set 을 만들 때 조심하세요. `{}` 는 **빈 딕셔너리**예요.'),
         WARN('빈 set 은 반드시 `set()`. `s = {}` 다음에 `s.add(1)` 을 하면 **AttributeError** 가 나요(딕셔너리에는 add 가 없어요).')])

    L.output('출력은?', '''\
word = "mississippi"
s = set(word)
print(len(s))
print("".join(sorted(s)))''',
        '`set("mississippi")` 는 글자 하나하나를 넣으니 m, i, s, p 4종류만 남아요. 정렬하면 i, m, p, s.\n\n```\n{out}\n```')

    L.spot('실행하면 **오류**가 나는 줄은?', '''\
nums = [4, 4, 8, 2]
s = set(nums)
print(len(s))
print(s[0])
print(sorted(s))''', 4,
        'set 은 순서가 없어 `s[0]` 처럼 인덱스로 꺼낼 수 없어요 → `TypeError`. 하나씩 보려면 `for x in s:` 또는 `sorted(s)[0]`.',
        error_line=4)

    L.explain('add · remove · discard',
        [T('`add(x)` 는 x 를 넣어요. 이미 있으면 **아무 일도 안 일어나요**(중복이 안 생겨요).\n'
           '리스트의 `append` 와 비슷하지만, set 에는 순서가 없으니 "끝에 붙인다"는 개념이 없어요.'),
         CODE('s = {1, 2}\ns.add(3)\ns.add(2)\nprint(sorted(s))', 'add')],
        [T('지우는 방법은 두 가지. **없는 값을 지울 때** 반응이 달라요. (find/index 차이와 닮았죠?)'),
         CMP(side('remove(x)', '없으면 **KeyError** 로 멈춰요', 's = {1, 2, 3}\ns.remove(5)', 'bad', expect_error=True),
             side('discard(x)', '없어도 **조용히** 넘어가요', 's = {1, 2, 3}\ns.discard(5)\nprint(sorted(s))', 'good')),
         TIP('"있을 때만 지워라" 는 `discard` 한 줄, 또는 `if x in s: s.remove(x)`.')])

    L.match('set 메서드와 동작을 이어 보세요.',
        [['s.add(x)', 'x 넣기 (이미 있으면 그대로)'], ['s.remove(x)', 'x 지우기, 없으면 KeyError'],
         ['s.discard(x)', 'x 지우기, 없어도 오류 없음'], ['len(s)', '서로 다른 값의 개수'], ['set()', '빈 set 만들기']],
        '`remove` 와 `discard` 의 차이는 **없는 값을 지울 때**만 드러나요. 빈 set 은 `{}` 가 아니라 `set()`!')

    L.explain('합·교·차·대칭차 — 메서드 vs 연산자',
        [T('두 set 을 수학의 집합처럼 계산할 수 있어요. **같은 일을 하는 메서드와 연산자**가 짝으로 있어요.'),
         TABS(('합집합', '`a | b` = `a.union(b)` : 둘 중 하나라도 있는 것',
               'a = {1, 2, 3, 4}\nb = {3, 4, 5}\nprint(sorted(a | b))\nprint(sorted(a.union(b)))'),
              ('교집합', '`a & b` = `a.intersection(b)` : 둘 다 있는 것',
               'a = {1, 2, 3, 4}\nb = {3, 4, 5}\nprint(sorted(a & b))\nprint(sorted(a.intersection(b)))'),
              ('차집합', '`a - b` = `a.difference(b)` : a 에만 있는 것 (순서 바꾸면 결과도 바뀜!)',
               'a = {1, 2, 3, 4}\nb = {3, 4, 5}\nprint(sorted(a - b))\nprint(sorted(b - a))'),
              ('대칭차', '`a ^ b` = `a.symmetric_difference(b)` : 한쪽에만 있는 것',
               'a = {1, 2, 3, 4}\nb = {3, 4, 5}\nprint(sorted(a ^ b))\nprint(sorted(a.symmetric_difference(b)))'))],
        [T('결과는 같지만 **받아 주는 상대**가 달라요.\n'
           '메서드는 괄호 안에 **리스트·문자열 같은 다른 묶음**도 받아 주지만, 연산자는 **양쪽이 모두 set** 이어야 해요.'),
         CMP(side('메서드', '리스트도 OK', 'a = {1, 2}\nprint(sorted(a.union([2, 3])))', 'good'),
             side('연산자', 'set | list → TypeError', 'a = {1, 2}\nprint(a | [2, 3])', 'bad', expect_error=True)),
         EXAM('2024년에 같은 계산을 **메서드로 한 번, 연산자로 한 번** 쓰게 하는 문제가 나왔어요. 네 쌍을 짝으로 외워 두세요.')],
        [T('네 연산 모두 **새 set** 을 돌려줘요. a, b 원본은 그대로예요.'),
         FLIP(['|', 'union — 합집합'], ['&', 'intersection — 교집합'], ['-', 'difference — 차집합'],
              ['^', 'symmetric_difference — 대칭차집합'])])

    L.output('출력은?', '''\
math = {"kim", "lee", "park", "choi"}
sci = {"lee", "choi", "jung"}
print(sorted(math & sci))
print(sorted(sci - math))
print(len(math | sci))
print(len(math ^ sci))''',
        '교집합 = 두 반 모두 = lee, choi. `sci - math` = sci 에만 = jung. 합집합은 5명, 대칭차는 한쪽에만 있는 kim, park, jung 3명.\n\n```\n{out}\n```')

    L.fill('연산자로 쓴 코드를 **메서드**로 바꿔 쓰세요. (출력이 같아야 해요)', '''\
a = {2, 4, 6, 8}
b = {4, 8, 12}
print(sorted(a.___(b)))      # a | b
print(sorted(a.___(b)))      # a & b
print(sorted(a.___(b)))      # a - b''', [['union'], ['intersection'], ['difference']],
        '`|` → union, `&` → intersection, `-` → difference. 대칭차 `^` 는 symmetric_difference 예요.',
        expect='[2, 4, 6, 8, 12]\n[4, 8]\n[2, 6]')

    L.bucket('각 코드가 **오류 없이 실행되는지** 분류하세요. (a = {1, 2})', ['정상 실행', 'TypeError'],
        [['a | {3}', 1], ['a | [3]', 2], ['a.union([3])', 1], ['a & {1}', 1],
         ['a.intersection("12")', 1], ['a - [1]', 2], ['a.difference(range(2))', 1]],
        '연산자(`| & - ^`)는 **양쪽 모두 set** 일 때만 돼요. 메서드는 리스트·문자열·range 같은 묶음도 받아 줘요. (`"12"` 는 글자 "1","2" 라 숫자 1, 2 와 겹치지 않을 뿐, 오류는 아니에요)')

    L.explain('in 검사는 set 이 빠르다',
        [T('`x in 리스트` 는 앞에서부터 **하나씩 비교**해요. 10만 개면 최악 10만 번!\n'
           '`x in set` 은 값을 **해시**라는 번호표로 바꿔 그 자리만 바로 확인해요. 개수가 많아도 거의 한 번에 끝나요.'),
         CMP(side('리스트 in', '처음부터 끝까지 훑기 → 개수에 비례해 느려짐', 'nums = list(range(100000))\nprint(99999 in nums)', 'bad'),
             side('set in', '번호표 자리만 확인 → 거의 즉시', 'nums = set(range(100000))\nprint(99999 in nums)', 'good'))],
        [T('그래서 "**이미 나왔던 값인가?**" 를 반복해서 물어야 할 때는 set 에 담아 두는 게 정석이에요.\n'
           '빈 set 을 하나 만들고 → 새 값이면 add, 이미 있으면 "중복!" 으로 처리해요.'),
         KEY('`seen = set()` → `if x in seen: 중복` → `else: seen.add(x)`. 이 세 줄이 **중복 탐지 공식**이에요.')])

    L.choice('학생 5만 명의 제출 코드에서 **중복**을 찾을 때, 이미 본 코드를 담아 두기에 가장 알맞은 것은?',
        ['리스트에 append 하고 `in` 으로 검사', 'set 에 add 하고 `in` 으로 검사',
         '문자열에 이어 붙이고 `find` 로 검사', '매번 `sorted()` 로 정렬해서 검사'], 2,
        'set 의 `in` 은 개수가 많아도 거의 한 번에 확인해요. 리스트는 매번 처음부터 훑어서 5만 × 5만 번 가까이 비교할 수 있어요.')

    L.explain('중복 제출 탐지 — zip + enumerate(start=1) + set',
        [T('이름 리스트와 제출 리스트가 **따로** 있을 때 `zip` 으로 짝을 짓고,\n'
           '`enumerate(..., start=1)` 로 **1번부터** 번호를 붙여요. 여기에 set 공식을 얹으면 끝!'),
         TRACE('''\
names = ["Ann", "Bo", "Cy", "Di"]
codes = ["x7", "k2", "x7", "m9"]
seen = set()
for i, (name, code) in enumerate(zip(names, codes), start=1):
    if code in seen:
        print(i, name, "중복")
    else:
        seen.add(code)
print(len(seen))''', '중복 제출 찾기')],
        [T('`enumerate(zip(a, b))` 는 `(번호, (a값, b값))` 을 줘요. 그래서 `for i, (name, code) in ...` 처럼 **괄호로 한 번 더 풀어요**.'),
         WARN('`for i, name, code in enumerate(zip(...))` 처럼 괄호 없이 쓰면 **ValueError**(풀 개수가 안 맞음)예요.'),
         EXAM('2026년에 zip·enumerate(start=1)·set 으로 **중복 제출을 찾는** 출력 추론·빈칸 문제가 나왔어요.')])

    L.output('출력은?', '''\
ids = [105, 102, 105, 108, 102, 105]
seen = set()
dup = set()
for i, x in enumerate(ids, start=1):
    if x in seen:
        dup.add(x)
        print(i, end=" ")
    seen.add(x)
print()
print(sorted(dup), len(seen))''',
        '이미 본 값이 다시 나올 때(3·5·6번째) 번호를 찍어요. dup 은 set 이라 105 가 여러 번 들어가도 하나만. seen 에는 서로 다른 값 3개.\n\n```\n{out}\n```')

    L.order('두 리스트 `names`, `answers` 에서 **처음 나온 답안만** 남기고 중복 제출자 번호를 출력하는 코드를 순서대로 놓으세요.',
        ['names = ["A", "B", "C"]', 'answers = ["p", "q", "p"]', 'seen = set()',
         'for i, (n, a) in enumerate(zip(names, answers), start=1):',
         '    if a in seen:', '        print(i, n)', '    seen.add(a)'],
        '빈 set 을 **반복 전에** 만들고, 검사(`in`) 다음에 add 해요. add 를 먼저 하면 모든 답안이 "중복" 으로 보여요.',
        check=True, expect='3 C')

    L.practice('[기출유사] 과제 중복 제출 탐지',
'''온라인 과제 시스템에 학생들이 **제출 코드**를 냈어요. 같은 코드가 다시 나오면 **두 번째부터는 중복 제출**이에요.

**[조건]**
- 첫째 줄: 학생 이름들(공백 구분), 둘째 줄: 각 학생의 제출 코드(공백 구분, 개수는 같아요)
- `zip` 과 `enumerate(…, start=1)` 로 번호를 붙이고, 이미 나온 코드는 **set** 에 담아 검사하세요.
- 중복이면 `번호번 이름: 중복 제출` 을 출력해요.
- 중복이 하나도 없으면 `중복 없음` 을 출력해요.
- 마지막 줄에 `고유 제출: 개수개` 를 출력해요.

{ex}

{ex2}''',
'''names = input().split()
codes = input().split()
seen = set()
# 이어서 작성하세요
''',
'''names = input().split()
codes = input().split()
seen = set()      # 이미 나온 제출 코드
dup = 0           # 중복 개수
for i, (name, code) in enumerate(zip(names, codes), start=1):
    if code in seen:              # 이미 나온 코드 → 중복
        print(f"{i}번 {name}: 중복 제출")
        dup += 1
    else:
        seen.add(code)            # 처음 나온 코드는 기록
if dup == 0:
    print("중복 없음")
print(f"고유 제출: {len(seen)}개")''',
        ['Ann Bo Cy Di Ed\nq1 z9 q1 k3 z9', 'Mia Leo Zoe\na1 b2 c3'],
        ['Solo\nx', 'A B C D\nsame same same same', 'p q r s t u\n1 2 3 1 2 3'],
        ['`for i, (name, code) in enumerate(zip(names, codes), start=1):` 로 시작해요.',
         '`if code in seen:` 이면 중복 출력 + 개수 세기, 아니면 `seen.add(code)`.',
         '반복이 끝난 뒤 중복 개수가 0 이면 `중복 없음`, 마지막에 `len(seen)` 출력.'],
        '`seen` 은 "지금까지 본 코드" 주머니예요. 검사를 먼저 하고 나서 add 해야 첫 제출이 중복으로 잡히지 않아요. 고유 제출 수는 `len(set(codes))` 와 같아요.')

    L.practice('[기출유사] 두 동아리 명단 비교',
'''코딩 동아리 A 와 로봇 동아리 B 의 명단이 주어져요. 집합 연산으로 다음을 출력하세요.

**[조건]**
- 첫째 줄: A 명단, 둘째 줄: B 명단 (공백 구분, 한 명단 안에 같은 이름이 또 나올 수도 있어요)
- `둘 다: …` (교집합), `A만: …` (A - B), `B만: …` (B - A) — 이름은 `sorted` 로 정렬해 공백으로 이어요. 해당 학생이 없으면 `없음`.
- 마지막 줄: `전체: 인원명` (합집합 크기)

{ex}

{ex2}''',
'''A = set(input().split())
B = set(input().split())
# 이어서 작성하세요
''',
'''A = set(input().split())     # 중복 이름은 set 이 알아서 제거
B = set(input().split())

def show(s):                  # 정렬해서 잇고, 비었으면 "없음"
    if len(s) == 0:
        return "없음"
    return " ".join(sorted(s))

print("둘 다:", show(A & B))
print("A만:", show(A - B))
print("B만:", show(B - A))
print(f"전체: {len(A | B)}명")''',
        ['kim lee park choi\nlee jung choi han', 'yoon yoon seo\nseo'],
        ['a b c\na b c', 'x\ny', 'm n m n o\no p o p'],
        ['교집합 `A & B`, 차집합 `A - B`, `B - A`, 합집합 `A | B`.',
         '빈 set 일 때 `없음` 을 내는 작은 함수 `show(s)` 를 만들면 세 번 재사용할 수 있어요.',
         '`" ".join(sorted(s))` — set 은 순서가 없으니 꼭 정렬!'],
        '입력을 바로 `set()` 으로 바꾸면 같은 이름이 두 번 적혀 있어도 한 명으로 세요. 출력 순서가 매번 같도록 `sorted` 를 꼭 써요.')

    L.essay('`a = {1, 2}` 일 때 `a.union([3, 4])` 는 실행되지만 `a | [3, 4]` 는 오류가 나요. **두 코드의 차이와 오류 이유**, 그리고 연산자로 고치는 방법을 서술하세요.',
        'union 메서드는 괄호 안에 리스트 같은 반복 가능한 묶음을 받아 set 으로 처리해 주지만, `|` 연산자는 양쪽이 모두 set 일 때만 계산할 수 있다. 그래서 set 과 list 를 `|` 로 합치면 TypeError 가 난다. 연산자를 쓰려면 `a | set([3, 4])` 또는 `a | {3, 4}` 처럼 오른쪽도 set 으로 바꾼다.',
        ['union 은 리스트도 받는다', '연산자는 양쪽 모두 set 이어야 한다', 'TypeError 가 난다', 'set([3, 4]) 로 바꿔 고친다'])


# =====================================================================
def lesson10(C):
    L = C.lesson('β-10 재귀 ①: 자기 자신을 부르는 함수', 25,
'''- 재귀 함수 = **기저 조건**(더 부르지 않고 바로 return) + **재귀 호출**(더 작은 문제로 자기 자신 호출)
- 팩토리얼 `n * fact(n - 1)`, 합 `n + total(n - 1)`, 문자 세기 `(첫 글자 검사) + count(s[1:])`
- 호출은 **스택**에 쌓였다가, 기저 조건에서부터 **거꾸로** 돌아오며 계산돼요.
- 기저 조건이 없거나 도달하지 못하면 → 약 1000번 쌓이다 **RecursionError**''')

    L.review('🔁 지난 시간 복습: set',
        [T('set 은 중복 없는 주머니. `add`/`remove`/`discard`, 그리고 합 `|`·교 `&`·차 `-`·대칭차 `^` 를 배웠어요.\n'
           '연산자는 **양쪽이 set** 이어야 하고, 메서드(union …)는 리스트도 받아요.'),
         REVEAL_RUN('`{1, 2, 3} ^ {2, 3, 4}` 의 결과는?', 'print(sorted({1, 2, 3} ^ {2, 3, 4}))')])
    L.output('복습: 출력은?', '''\
s = set()
for w in "to be or not to be".split():
    s.add(w)
s.discard("or")
s.discard("xyz")
print(len(s))
print(sorted(s))''',
        '단어 to, be, or, not 4종류 → or 를 지우면 3개. 없는 값 xyz 를 discard 해도 오류가 없어요.\n\n```\n{out}\n```', review=True)
    L.short('복습: `a = {1, 2, 3, 4}`, `b = {3, 4, 5}` 일 때 `a.difference(b)` 를 **연산자**로 쓰면? (공백 없이, 예: `a|b`)', 'a-b',
        '`difference` ↔ `-`. 차집합은 순서가 중요해서 `b-a` 는 `{5}` 로 결과가 달라요.', alts=['a - b'], review=True)

    L.explain('재귀란? — 기저 조건 + 재귀 호출',
        [T('**재귀 함수**는 함수 안에서 **자기 자신을 다시 부르는** 함수예요.\n'
           '큰 문제를 "조금 더 작은 같은 문제" 로 바꿔서 풀어요. 단, 언젠가는 **멈춰야** 하겠죠?'),
         STEPS(('① 기저 조건', '가장 작은 경우. 더 부르지 않고 바로 답을 return 해요. 예: `if n == 0: return`'),
               ('② 재귀 호출', '문제를 한 칸 줄여 자기 자신을 불러요. 예: `countdown(n - 1)`'),
               ('③ 결과 합치기', '돌아온 답에 지금 단계의 일을 더해요. 예: `n * fact(n - 1)`'))],
        [T('가장 단순한 재귀: 카운트다운. n 을 출력하고 n-1 로 다시 불러요. 0 이 되면 멈춰요.'),
         CODE('def countdown(n):\n    if n == 0:          # 기저 조건\n        print("발사!")\n        return\n    print(n)\n    countdown(n - 1)    # 재귀 호출\n\ncountdown(3)', '카운트다운')],
        [T('print 를 **재귀 호출 뒤로** 옮기면 어떻게 될까요? 먼저 끝까지 내려갔다가, **돌아오면서** 출력해요.'),
         REVEAL_RUN('print 를 아래로 옮긴 코드의 출력은?',
                    'def up(n):\n    if n == 0:\n        return\n    up(n - 1)\n    print(n)\n\nup(3)',
                    '`up(3)` → `up(2)` → `up(1)` → `up(0)` 이 끝나고 나서야 1, 2, 3 순서로 print 가 실행돼요.'),
         KEY('재귀 호출 **앞**의 일은 내려가며, **뒤**의 일은 올라오며 실행돼요.')])

    L.match('재귀 함수의 부분과 역할을 이어 보세요.',
        [['if n == 0: return 1', '기저 조건'], ['fact(n - 1)', '재귀 호출'],
         ['n * fact(n - 1)', '결과 합치기'], ['n - 1', '문제를 작게 만들기']],
        '기저 조건이 있어야 멈추고, `n - 1` 처럼 **기저 조건에 다가가는** 방향으로 불러야 해요.')

    L.output('출력은?', '''\
def show(n):
    if n > 3:
        return
    print("in", n)
    show(n + 1)
    print("out", n)

show(1)''',
        '`in` 은 내려가며 1, 2, 3. n=4 에서 멈춘 뒤 돌아오며 `out` 3, 2, 1 이에요.\n\n```\n{out}\n```')

    L.explain('팩토리얼과 합 — 값을 돌려주는 재귀',
        [T('`5! = 5 × 4!` 이고 `4! = 4 × 3!` … 처럼 팩토리얼은 **자기보다 작은 팩토리얼**로 정의돼요.\n'
           '기저 조건은 `1! = 1` (또는 `0! = 1`).'),
         CODE('def fact(n):\n    if n <= 1:\n        return 1\n    return n * fact(n - 1)\n\nprint(fact(5))', '팩토리얼')],
        [T('1 부터 n 까지 합도 똑같은 모양이에요. `total(n) = n + total(n - 1)`, 기저 조건은 `total(0) = 0`.'),
         TABS(('재귀', '', 'def total(n):\n    if n == 0:\n        return 0\n    return n + total(n - 1)\n\nprint(total(10))'),
              ('반복문', '', 's = 0\nfor i in range(1, 11):\n    s += i\nprint(s)')),
         TIP('재귀 함수는 **"작은 문제의 답이 이미 있다고 믿고"** 지금 단계만 써요. 이걸 "재귀적 믿음" 이라고 해요.')])

    L.fill('2 의 n 제곱을 재귀로 구하는 함수를 완성하세요.', '''\
def power2(n):
    if n == ___:
        return 1
    return ___ * power2(n - 1)

print(power2(5))''', [['0'], ['2']],
        '`2⁰ = 1` 이 기저 조건, `2ⁿ = 2 × 2ⁿ⁻¹` 이 재귀 호출이에요. 결과는 32.', expect='32')

    L.explain('호출 스택 — 쌓였다가 거꾸로 돌아온다',
        [T('함수를 부르면 컴퓨터는 "어디까지 했는지" 를 **스택(쌓인 접시)** 에 올려 둬요.\n'
           '`fact(3)` 은 `fact(2)` 를 부르느라 잠시 멈추고, `fact(2)` 는 `fact(1)` 을 부르느라 멈춰요.'),
         STEPS('fact(3) 호출 → 3 * fact(2) 를 계산하려고 대기',
               'fact(2) 호출 → 2 * fact(1) 을 계산하려고 대기',
               'fact(1) → 기저 조건! 1 을 return',
               'fact(2) 가 2 * 1 = 2 를 return',
               'fact(3) 이 3 * 2 = 6 을 return')],
        [T('따라가기로 직접 확인해 봐요. depth(깊이)를 함께 출력해서 쌓이는 모습을 볼 수 있어요.'),
         TRACE('''\
def fact(n):
    print("호출", n)
    if n <= 1:
        return 1
    r = n * fact(n - 1)
    print("반환", n, r)
    return r

print(fact(3))''', '팩토리얼 호출 스택'),
         EXAM('시험은 이런 "호출/반환 순서" 를 **표로 채우거나 출력 순서를 쓰게** 해요. 내려가는 줄과 올라오는 줄을 구분하세요.')])

    L.order('`fact(3)` 을 실행할 때 일어나는 일을 순서대로 놓으세요.',
        ['fact(3) 이 fact(2) 를 호출', 'fact(2) 가 fact(1) 을 호출', 'fact(1) 이 1 을 반환',
         'fact(2) 가 2 를 반환', 'fact(3) 이 6 을 반환'],
        '호출은 3 → 2 → 1 로 내려가고, 반환은 1 → 2 → 3 으로 **거꾸로** 올라와요.', mono=False)

    L.explain('재귀로 문자 개수 세기',
        [T('문자열도 재귀로 다룰 수 있어요. **첫 글자**만 보고, 나머지 `s[1:]` 는 재귀에게 맡겨요.\n'
           '빈 문자열이면 셀 게 없으니 0 이 기저 조건이에요.'),
         CODE('def count(s, ch):\n    if s == "":                 # 기저 조건\n        return 0\n    first = 1 if s[0] == ch else 0\n    return first + count(s[1:], ch)   # 나머지는 재귀에게\n\nprint(count("banana", "a"))', '문자 세기 재귀')],
        [T('`1 if 조건 else 0` 은 **조건 표현식**이에요. 조건이 참이면 1, 거짓이면 0.\n'
           '`if` 문으로 풀어 써도 똑같이 동작해요.'),
         CMP(side('조건 표현식', '한 줄', 'ch = "a"\nfirst = 1 if "apple"[0] == ch else 0\nprint(first)', 'good'),
             side('if 문', '여러 줄', 'ch = "a"\nif "apple"[0] == ch:\n    first = 1\nelse:\n    first = 0\nprint(first)', 'good')),
         EXAM('2023년에 **count() 없이 재귀로 문자 개수를 세는** 빈칸 문제가 나왔어요. 기저 조건(`s == ""`)과 `s[1:]` 이 빈칸 단골!')])

    L.fill('재귀로 문자열 속 **숫자 글자**의 개수를 세는 함수를 완성하세요.', '''\
def digits(s):
    if ___:
        return 0
    if s[0].isdigit():
        return 1 + digits(___)
    return digits(s[1:])

print(digits("A1b22c3"))''', [['s == ""', 'len(s) == 0', 'not s'], ['s[1:]']],
        '빈 문자열이 기저 조건, 나머지 `s[1:]` 로 한 글자씩 줄여 가요. 숫자 글자는 1, 2, 2, 3 → 4개.', expect='4')

    L.output('출력은?', '''\
def dsum(n):
    if n < 10:
        return n
    return n % 10 + dsum(n // 10)

print(dsum(4096))
print(dsum(7))''',
        '`n % 10` 은 일의 자리, `n // 10` 은 나머지 자릿수. 4096 → 6 + dsum(409) → 6 + 9 + dsum(40) → … = 4+0+9+6.\n\n```\n{out}\n```')

    L.explain('기저 조건이 없으면? — RecursionError',
        [T('기저 조건이 없거나, 있어도 **도달하지 못하면** 함수가 끝없이 자기 자신을 불러요.\n'
           '파이썬은 스택이 넘치지 않게 약 **1000번** 쌓이면 멈추고 `RecursionError` 를 내요.'),
         CODE('def bad(n):\n    print(n, end=" ")\n    bad(n - 1)     # 멈출 곳이 없어요\n\nbad(3)', '기저 조건이 없는 재귀', expect_error=True)],
        [T('기저 조건이 **있어도** 틀릴 수 있어요. 아래는 n 이 2 씩 줄어서 홀수일 때 0 을 건너뛰어요.'),
         CMP(side('도달 못 함', 'n=5 → 3 → 1 → -1 … 0 을 지나쳐 버림',
                  'def half(n):\n    if n == 0:\n        return 0\n    return n + half(n - 2)\n\nprint(half(5))', 'bad', expect_error=True),
             side('범위로 막기', '`n <= 0` 이면 홀수도 멈춰요',
                  'def half(n):\n    if n <= 0:\n        return 0\n    return n + half(n - 2)\n\nprint(half(5))', 'good')),
         WARN('기저 조건은 `==` 보다 `<=` 처럼 **범위**로 쓰는 게 안전할 때가 많아요.')])

    L.spot('`total(4)` 를 실행하면 끝나지 않고 **RecursionError** 가 나요. 원인이 되는 줄은?', '''\
def total(n):
    if n == 0:
        return 0
    return n + total(n)

print(total(4))''', 4,
        '재귀 호출에서 `total(n)` 처럼 **같은 크기**로 다시 부르니 기저 조건(n == 0)에 영원히 다가가지 못해요. `total(n - 1)` 로 고쳐야 해요.',
        error_line=4)

    L.ox('파이썬에서 재귀 호출은 기본 설정으로 약 1000단계까지 쌓을 수 있고, 그보다 깊어지면 RecursionError 가 난다.', True,
        '`sys.getrecursionlimit()` 의 기본값이 1000 이에요. 그래서 `count(s, ch)` 같은 재귀도 아주 긴 문자열에는 쓸 수 없어요.')

    L.practice('[기출유사] count() 없이 재귀로 글자 세기',
'''문자열과 찾을 글자 하나가 주어질 때, **재귀 함수**로 그 글자가 몇 번 나오는지 세어 출력하세요.

**[조건]**
- 첫째 줄: 문자열 (공백이 들어 있을 수 있어요), 둘째 줄: 찾을 글자 1개
- `def count(s, ch):` 재귀 함수를 만들어요. `count()` 메서드와 반복문은 쓰지 않아요. (자동 채점은 결과만 확인해요)
- 기저 조건은 빈 문자열, 재귀 호출은 `s[1:]`
- 출력 형식: `'글자': 개수개`

{ex}

{ex2}''',
'''def count(s, ch):
    # 기저 조건과 재귀 호출을 작성하세요
    return 0

s = input()
ch = input()
print(f"'{ch}': {count(s, ch)}개")''',
'''def count(s, ch):
    if s == "":                       # 기저 조건: 빈 문자열
        return 0
    first = 1 if s[0] == ch else 0    # 첫 글자만 검사
    return first + count(s[1:], ch)   # 나머지는 재귀에게

s = input()
ch = input()
print(f"'{ch}': {count(s, ch)}개")''',
        ['banana bread\na', 'Mississippi\ns'],
        ['xyz\nq', 'aaaaaaaaaa\na', '\nk', 'A a A a\nA'],
        ['기저 조건: `if s == "": return 0`',
         '첫 글자가 ch 면 1, 아니면 0 → `1 if s[0] == ch else 0`',
         '`return first + count(s[1:], ch)`'],
        '한 번 부를 때마다 문자열이 한 글자씩 짧아지므로 언젠가 빈 문자열(기저 조건)에 도달해요. 대소문자는 다른 글자로 세요.',
        starter_may_pass=False)

    L.practice('재귀 연습: 자릿수 합과 숫자 뒤집기',
'''양의 정수 N 이 주어져요. 두 재귀 함수를 만들어 출력하세요.

**[조건]**
- `dsum(n)`: 각 자릿수의 합을 **재귀로** 구해요. (`n % 10`, `n // 10` 활용)
- `rev(n)`: 숫자를 뒤집은 **문자열**을 재귀로 만들어요. 예: 1203 → `"3021"`
- 첫째 줄에 자릿수 합, 둘째 줄에 뒤집은 문자열을 출력해요.

{ex}

{ex2}''',
'''def dsum(n):
    pass

def rev(n):
    pass

n = int(input())
print(dsum(n))
print(rev(n))''',
'''def dsum(n):
    if n < 10:                       # 한 자리면 그대로
        return n
    return n % 10 + dsum(n // 10)    # 일의 자리 + 나머지 자릿수 합

def rev(n):
    if n < 10:                       # 한 자리면 그 글자 하나
        return str(n)
    return str(n % 10) + rev(n // 10)   # 일의 자리를 앞에 붙여요

n = int(input())
print(dsum(n))
print(rev(n))''',
        ['1203', '98765'], ['5', '1000', '123456789'],
        ['두 함수 모두 기저 조건은 `n < 10` (한 자리 수)이에요.',
         '`dsum`: `n % 10 + dsum(n // 10)`', '`rev`: `str(n % 10) + rev(n // 10)` — 문자열로 이어 붙여요.'],
        '`rev(1000)` 은 `"0001"` 처럼 앞의 0 이 남아요. 숫자가 아니라 **문자열**로 이어 붙였기 때문이에요.')

    L.essay('다음 함수 `def f(n): return n + f(n - 1)` 로 `f(5)` 를 실행하면 어떤 일이 일어나는지 **이유와 함께** 서술하고, 고치는 방법을 쓰세요.',
        '기저 조건이 없어서 f(5) → f(4) → … → f(0) → f(-1) … 처럼 끝없이 자기 자신을 호출한다. 호출이 스택에 계속 쌓이다가 최대 깊이(약 1000)를 넘으면 RecursionError 가 발생하며 프로그램이 멈춘다. `if n <= 0: return 0` 같은 기저 조건을 재귀 호출 앞에 넣어 고친다.',
        ['기저 조건이 없다', '끝없이 자기 자신을 호출한다(음수로 계속)', 'RecursionError 가 발생한다', 'if n <= 0: return 0 같은 기저 조건을 추가한다'])


def lesson11(C):
    L = C.lesson('β-11 재귀 ②: 점화식·호출 횟수·반복문 변환', 30,
'''- **점화식**: "마지막 칸을 어떻게 채우나?" 로 경우를 나누면 `f(n) = f(n-1) + f(n-2)` 같은 식이 나와요.
- 호출 횟수는 함수 첫 줄에서 `global count` + `count += 1` 로 세요.
- `f(n-1)` 을 **두 번** 부르는 재귀는 호출 수가 약 2배씩 불어나요(1, 3, 7, 15 …).
- 재귀 → 반복문: 작은 값부터 차례로 쌓아 올려요(`a, b = b, a + b`, `s = s + str(i) + s`).''')

    L.review('🔁 지난 시간 복습: 재귀 ①',
        [T('재귀 = **기저 조건 + 재귀 호출**. 호출은 스택에 쌓였다가 기저 조건에서부터 **거꾸로** 돌아오며 계산돼요.\n'
           '기저 조건이 없거나 도달하지 못하면 RecursionError 였죠.'),
         REVEAL_RUN('`fact(4)` 는 몇일까요?', 'def fact(n):\n    if n <= 1:\n        return 1\n    return n * fact(n - 1)\n\nprint(fact(4))')])
    L.output('복습: 출력은?', '''\
def f(s):
    if len(s) <= 1:
        return s
    return f(s[1:]) + s[0]

print(f("abcd"))''',
        '`f("abcd") = f("bcd") + "a" = (f("cd") + "b") + "a" = …` 결국 문자열이 뒤집혀요.\n\n```\n{out}\n```', review=True)
    L.spot('복습: `count_down(5)` 를 실행하면 RecursionError 가 나요. **고쳐야 할 줄**은?', '''\
def count_down(n):
    if n == 0:
        return
    print(n)
    count_down(n - 2)

count_down(5)''', 2,
        'n 이 5 → 3 → 1 → -1 … 로 2씩 줄어 0 을 **건너뛰어요**. 기저 조건을 `if n <= 0:` 으로 바꿔야 해요.', review=True)

    L.explain('점화식 ① 타일 채우기',
        [T('폭 2, 길이 n 인 길을 **2×1 타일**(세로로 1칸 차지)과 **2×2 타일**(2칸 차지)로 빈틈없이 덮는 방법의 수를 세 볼게요.\n'
           '전부 그려 보면 힘들어요. 대신 **맨 끝을 어떻게 덮었나** 로 경우를 나눠요.'),
         STEPS(('끝이 2×1 타일', '나머지는 길이 n-1 → 방법 f(n-1) 가지'),
               ('끝이 2×2 타일', '나머지는 길이 n-2 → 방법 f(n-2) 가지'),
               ('합치기', 'f(n) = f(n-1) + f(n-2)'),
               ('기저 조건', 'f(1) = 1 (세로 하나), f(2) = 2 (세로 둘 또는 2×2 하나)'))],
        [T('점화식을 그대로 코드로 옮기면 재귀 함수가 돼요. **기저 조건 두 개**를 잊지 마세요.'),
         CODE('def tile(n):\n    if n == 1:\n        return 1\n    if n == 2:\n        return 2\n    return tile(n - 1) + tile(n - 2)\n\nfor n in range(1, 7):\n    print(n, tile(n))', '타일 채우기'),
         TIP('결과가 1, 2, 3, 5, 8, 13 … **피보나치 수열** 모양이에요. "끝을 두 가지로 나누는" 문제는 대부분 이 모양이에요.')])

    L.fill('타일 채우기 재귀 함수의 빈칸을 채우세요.', '''\
def tile(n):
    if n <= 2:
        return ___
    return tile(___) + tile(n - 2)

print(tile(7))''', [['n'], ['n - 1', 'n-1']],
        'f(1)=1, f(2)=2 이니 기저 조건은 `return n` 한 줄로 쓸 수 있어요. tile(7) = 21.', expect='21')

    L.explain('점화식 ② 구슬 배열',
        [T('흰 구슬(W)과 검은 구슬(B)을 n 개 한 줄로 놓는데, **검은 구슬이 연속으로 붙으면 안 돼요.**\n'
           '이번에도 **마지막 구슬**로 나눠요.'),
         STEPS(('마지막이 W', '앞의 n-1 개는 규칙만 지키면 아무거나 → f(n-1)'),
               ('마지막이 B', '바로 앞은 반드시 W. 그 앞 n-2 개는 아무거나 → f(n-2)'),
               ('점화식', 'f(n) = f(n-1) + f(n-2)'),
               ('기저 조건', 'f(1) = 2 (W, B), f(2) = 3 (WW, WB, BW)'))],
        [T('점화식 모양은 타일과 같지만 **기저 값이 달라서** 결과가 달라요. 시험에서는 기저 조건 빈칸이 자주 나와요.'),
         REVEAL_RUN('n = 1 ~ 5 일 때 구슬 배열 수는?',
                    'def bead(n):\n    if n == 1:\n        return 2\n    if n == 2:\n        return 3\n    return bead(n - 1) + bead(n - 2)\n\nfor n in range(1, 6):\n    print(n, bead(n))'),
         EXAM('2024년에 구슬 배열 점화식을 **재귀 빈칸**으로 채우고 **n=5 결과**를 쓰는 문제가 나왔어요. 직접 표를 그려 확인하는 습관!')])

    L.short('흰·검 구슬 배열(검은 구슬 연속 금지)에서 n = 6 일 때 방법의 수는?', '21',
        'f(1)=2, f(2)=3, f(3)=5, f(4)=8, f(5)=13, f(6)=13+8=21.',
        check_code='def b(n):\n    if n == 1:\n        return 2\n    if n == 2:\n        return 3\n    return b(n - 1) + b(n - 2)\nprint(b(6))')

    L.explain('호출 횟수 세기 — global count',
        [T('재귀 함수가 **몇 번 불렸는지** 세려면 함수 밖에 `count = 0` 을 두고, 함수 첫 줄에서 1 씩 더해요.\n'
           '함수 안에서 바깥 변수를 **바꾸려면** `global` 선언이 필요해요(β-05 에서 배웠죠).'),
         CODE('count = 0\n\ndef tile(n):\n    global count\n    count += 1          # 불릴 때마다 1\n    if n <= 2:\n        return n\n    return tile(n - 1) + tile(n - 2)\n\nprint(tile(5), count)', '호출 횟수')],
        [T('tile(5) 는 tile(4) 와 tile(3) 을, tile(4) 는 또 tile(3) 과 tile(2) 를 불러요. **같은 값을 여러 번** 계산하죠.\n'
           '호출 나무를 그려 세면 이렇게 돼요.'),
         CODE('''\
#                tile(5)
#           /              \\
#       tile(4)          tile(3)
#       /     \\          /     \\
#   tile(3)  tile(2)  tile(2)  tile(1)
#   /     \\
# tile(2) tile(1)
print("동그라미 개수 = 9")''', '호출 나무', run_=False),
         WARN('`global count` 를 빼면 `count += 1` 에서 **UnboundLocalError** 가 나요. 함수 안에서 대입하는 순간 지역 변수로 보기 때문이에요.')])

    L.output('출력은?', '''\
count = 0

def tile(n):
    global count
    count += 1
    if n <= 2:
        return n
    return tile(n - 1) + tile(n - 2)

tile(6)
print(count)
count = 0
tile(7)
print(count)''',
        '호출 수 c(n) = 1 + c(n-1) + c(n-2), c(1)=c(2)=1 → c(3)=3, c(4)=5, c(5)=9, c(6)=15, c(7)=25. n 이 하나 늘 때마다 약 1.6배씩 불어나요.\n\n```\n{out}\n```')

    L.spot('호출 횟수를 세려 했는데 **오류**가 나요. 문제가 되는 줄은? (오류는 그 줄에서 나요)', '''\
calls = 0

def fact(n):
    calls += 1
    if n <= 1:
        return 1
    return n * fact(n - 1)

print(fact(4), calls)''', 4,
        '함수 안에서 `calls += 1` 처럼 **대입**하면 파이썬은 calls 를 지역 변수로 봐요. 아직 값이 없는데 더하려 해서 `UnboundLocalError`. 함수 첫 줄에 `global calls` 를 넣어야 해요.',
        error_line=4)

    L.explain('출력 추론: f(n-1) 을 두 번 부르는 재귀',
        [T('문자열을 돌려주는 재귀는 **작은 값부터 표로 채우면** 쉽게 풀려요.\n'
           '아래 함수는 가운데에 `str(n)` 을 두고 **양쪽에** f(n-1) 을 붙여요.'),
         TRACE('''\
def f(n):
    if n == 0:
        return ""
    return f(n - 1) + str(n) + f(n - 1)

print(f(1))
print(f(2))
print(f(3))''', '양쪽에 붙이기')],
        [T('표로 정리하면 이래요. 앞 줄의 결과를 **양쪽에 복사**하고 가운데에 n 을 넣어요.'),
         STEPS('f(0) = "" (기저 조건)', 'f(1) = "" + "1" + "" = "1"', 'f(2) = "1" + "2" + "1" = "121"',
               'f(3) = "121" + "3" + "121" = "1213121"'),
         KEY('길이는 1, 3, 7, 15 … = 2ⁿ - 1. 호출 횟수도 f(0) 까지 세면 1, 3, 7, 15, 31 … (2배 + 1 씩)')],
        [T('모양을 살짝 바꾼 변형도 같은 방법으로 풀어요. **표 채우기**가 정답이에요.'),
         TABS(('양 끝에 n', '`str(n) + f(n-1) + str(n)`',
               'def g(n):\n    if n == 0:\n        return ""\n    return str(n) + g(n - 1) + str(n)\n\nprint(g(3))'),
              ('앞뒤가 다름', '`f(n-1) + str(n) + f(n-2)`',
               'def h(n):\n    if n <= 0:\n        return ""\n    return h(n - 1) + str(n) + h(n - 2)\n\nprint(h(4))')),
         EXAM('2026년에 이런 재귀의 **출력·호출 횟수·반복문 변환**을 한 문항에서 연달아 물었어요.')])

    L.output('출력은?', '''\
def f(n):
    if n == 0:
        return "-"
    return f(n - 1) + str(n) + f(n - 1)

print(f(2))
print(len(f(4)))''',
        '이번엔 기저 값이 `"-"` 예요. f(1) = "-1-", f(2) = "-1-2-1-". 길이는 L(n) = 2·L(n-1) + 1, L(0)=1 → 3, 7, 15, 31.\n\n```\n{out}\n```')

    L.output('호출 횟수는? (f(0) 호출도 셉니다)', '''\
count = 0

def f(n):
    global count
    count += 1
    if n == 0:
        return ""
    return f(n - 1) + str(n) + f(n - 1)

f(4)
print(count)''',
        '한 번 부를 때마다 f(n-1) 을 **두 번** 불러요. c(0)=1, c(n) = 1 + 2·c(n-1) → 1, 3, 7, 15, 31.\n\n```\n{out}\n```')

    L.explain('재귀를 반복문으로 바꾸기',
        [T('재귀는 위에서 아래로(큰 n → 작은 n) 내려가지만, 반복문은 **아래에서 위로** 쌓아 올려요.\n'
           '"작은 값의 답으로 다음 답을 만든다" 는 점화식을 그대로 for 로 돌리면 돼요.'),
         CMP(side('재귀', 'f(n-1) 을 두 번 계산', 'def f(n):\n    if n == 0:\n        return ""\n    return f(n - 1) + str(n) + f(n - 1)\n\nprint(f(3))', 'good'),
             side('반복문', '이전 결과 s 를 재사용', 'n = 3\ns = ""\nfor i in range(1, n + 1):\n    s = s + str(i) + s\nprint(s)', 'good'))],
        [T('피보나치형(타일·구슬)은 **변수 두 개**만 들고 가면 돼요. `a` = f(i-2), `b` = f(i-1).'),
         TRACE('''\
n = 6
a, b = 1, 2          # tile(1), tile(2)
for i in range(3, n + 1):
    a, b = b, a + b  # 한 칸씩 밀기
print(b)''', '타일 채우기 반복문'),
         THINK('재귀 tile(35) 는 호출이 1800만 번이 넘어 몇 초가 걸리지만, 반복문은 33번만 돌아요. **같은 값을 다시 계산하지 않기** 때문이에요.')])

    L.fill('구슬 배열 수(f(1)=2, f(2)=3)를 **반복문**으로 구하세요.', '''\
n = 7
a, b = 2, 3
for i in range(3, n + 1):
    a, b = ___, ___
print(b)''', [['b'], ['a + b', 'a+b', 'b + a']],
        '한 칸씩 밀면서 새 값 = 앞의 두 값의 합. f(7) = 34.', expect='34')

    L.order('재귀 `f(n) = f(n-1) + str(n) + f(n-1)` (f(0)="") 을 반복문으로 바꾼 코드를 순서대로 놓으세요. (n=3 → 1213121)',
        ['n = 3', 's = ""', 'for i in range(1, n + 1):', '    s = s + str(i) + s', 'print(s)'],
        '`s` 가 f(i-1) 역할이에요. 기저 조건 f(0) = "" 이 `s = ""` 초기값이 돼요.',
        check=True, expect='1213121')

    L.practice('[기출유사] 타일 채우기 + 호출 횟수',
'''폭 2, 길이 N 인 길을 2×1 타일과 2×2 타일로 채우는 방법의 수를 **재귀 함수**로 구하고, 그 함수가 **몇 번 호출되었는지**도 출력하세요.

**[조건]**
- 입력: 정수 N (1 ≤ N ≤ 20)
- `def tile(n):` 재귀 함수. tile(1) = 1, tile(2) = 2, tile(n) = tile(n-1) + tile(n-2)
- 전역 변수 `count` 로 호출 횟수를 세요. (`global` 사용)
- 출력: `방법: 값` / `호출: 값번`

{ex}

{ex2}''',
'''count = 0

def tile(n):
    # 호출 횟수를 세고, 점화식대로 return 하세요
    pass

n = int(input())
''',
'''count = 0

def tile(n):
    global count          # 바깥 count 를 바꾸겠다고 선언
    count += 1            # 불릴 때마다 1 증가
    if n <= 2:            # 기저 조건: tile(1)=1, tile(2)=2
        return n
    return tile(n - 1) + tile(n - 2)

n = int(input())
ways = tile(n)
print(f"방법: {ways}")
print(f"호출: {count}번")''',
        ['5', '10'], ['1', '2', '20'],
        ['함수 첫 줄에 `global count`, 다음 줄에 `count += 1`.',
         '기저 조건은 `if n <= 2: return n` 한 줄로 쓸 수 있어요.',
         'tile(n) 을 **먼저** 호출해 결과를 변수에 담은 뒤 count 를 출력해야 해요.'],
        'print 안에서 `tile(n)` 과 `count` 를 같이 쓰면 순서에 따라 count 가 0 으로 찍힐 수 있어요. 먼저 계산하고 나서 출력하세요. 호출 수가 n=20 에서 1만 번이 넘는 것도 확인해 보세요.')

    L.practice('[기출유사] 구슬 배열 — 반복문으로 바꾸기',
'''흰 구슬과 검은 구슬 N 개를 한 줄로 놓을 때, **검은 구슬이 연속으로 붙지 않는** 배열의 수를 구하세요.
재귀로 풀면 N 이 크면 너무 오래 걸리니 **반복문**으로 바꿔서 풀어요.

**[조건]**
- 입력: 정수 N (1 ≤ N ≤ 80)
- f(1) = 2, f(2) = 3, f(n) = f(n-1) + f(n-2)
- 재귀를 쓰지 말고 `for` 반복문과 변수 두 개로 계산해요.
- 출력: `N개: 값가지`

{ex}

{ex2}''',
'''n = int(input())
# 반복문으로 f(n) 을 구하세요
''',
'''n = int(input())
if n == 1:
    ans = 2
else:
    a, b = 2, 3                 # f(1), f(2)
    for i in range(3, n + 1):
        a, b = b, a + b         # 한 칸씩 밀기
    ans = b
print(f"{n}개: {ans}가지")''',
        ['3', '5'], ['1', '2', '80'],
        ['`a, b = 2, 3` 으로 f(1), f(2) 를 담고 시작해요.',
         '`for i in range(3, n + 1): a, b = b, a + b`',
         'n == 1 이면 반복문이 돌지 않아 b(=3) 가 남으니 따로 처리해요.'],
        '반복문은 n-2 번만 더하면 끝나요. 재귀로 f(80) 을 구하면 호출이 수조 번이라 끝나지 않아요. n=1 같은 **경계값**은 따로 처리하는 습관을 들여요.')

    L.essay('타일 채우기 재귀 `tile(n) = tile(n-1) + tile(n-2)` 는 n 이 30 만 넘어도 매우 느려져요. **그 이유**와, 반복문으로 바꾸면 빨라지는 이유를 서술하세요.',
        '재귀 tile 은 한 번 호출될 때마다 두 번씩 다시 호출하고, tile(n-2) 처럼 같은 값을 여러 번 반복해서 계산한다. 그래서 호출 횟수가 n 이 1 늘 때마다 약 1.6 배씩 늘어나 n=30 이면 백만 번이 넘는다. 반복문은 작은 값부터 차례로 계산하며 이전 두 값만 변수에 저장해 다시 쓰므로 n 번 정도만 계산하면 된다.',
        ['한 번에 두 번씩 호출한다', '같은 값을 중복 계산한다', '호출 횟수가 기하급수적으로 늘어난다', '반복문은 이전 값을 저장해 재사용한다'])


# =====================================================================
def lesson12(C):
    L = C.lesson('β-12 이진 탐색: 반씩 버리며 찾기', 30,
'''- 이진 탐색은 **정렬된** 리스트에서만 써요. 가운데 `mid = (left + right) // 2` 와 비교해 **절반을 버려요**.
- 찾는 값이 더 크면 `left = mid + 1`, 더 작으면 `right = mid - 1`. 반복 조건은 `while left <= right`.
- 비교 횟수는 약 log₂N: 1000개 → 약 10번, 100만 개 → 약 20번.
- **파라메트릭 서치**: "조건을 만족하는 최대 높이" 를 이진 탐색으로 찾아요(답 후보를 반씩 버림).
- `left = mid` 처럼 mid 를 버리지 않으면 범위가 줄지 않아 **무한 루프**!''')

    L.review('🔁 지난 시간 복습: 재귀 ②',
        [T('점화식 `f(n) = f(n-1) + f(n-2)`, `global count` 로 호출 횟수 세기, f(n-1) 을 두 번 부르는 재귀의 출력, 그리고 반복문 변환을 배웠어요.'),
         REVEAL_RUN('`s = s + str(i) + s` 를 i = 1, 2, 3 으로 돌리면?', 's = ""\nfor i in range(1, 4):\n    s = s + str(i) + s\nprint(s)')])
    L.output('복습: 출력은?', '''\
def f(n):
    if n <= 1:
        return "*"
    return f(n - 1) + "+" + f(n - 2)

print(f(3))''',
        'f(0) = f(1) = "*". f(2) = "*" + "+" + "*" = "*+*". f(3) = f(2) + "+" + f(1) = "*+*+*".\n\n```\n{out}\n```', review=True)
    L.short('복습: 타일 채우기(f(1)=1, f(2)=2, f(n)=f(n-1)+f(n-2))에서 f(6) 은?', '13',
        '1, 2, 3, 5, 8, 13.', review=True,
        check_code='a, b = 1, 2\nfor i in range(3, 7):\n    a, b = b, a + b\nprint(b)')

    L.explain('업다운 게임과 이진 탐색',
        [T('1 ~ 100 중 숫자 맞히기 게임에서 "50!" → "업!" → "75!" … 처럼 **가운데를 부르면** 매번 후보가 절반으로 줄어요.\n'
           '이게 **이진 탐색**이에요. 앞에서부터 하나씩 보는 **순차 탐색**과 비교해 볼게요.'),
         CMP(side('순차 탐색', '처음부터 하나씩. 정렬 필요 없음. 최악 N 번', 'nums = [3, 8, 15, 21, 30, 42]\nfor i in range(len(nums)):\n    if nums[i] == 30:\n        print("찾음", i)', 'good'),
             side('이진 탐색', '가운데와 비교해 절반 버리기. **정렬 필수**. 최악 약 log₂N 번', 'nums = [3, 8, 15, 21, 30, 42]\nprint("가운데부터 본다:", nums[len(nums) // 2])', 'good'))],
        [T('왜 정렬이 꼭 필요할까요? "가운데보다 크면 **오른쪽에만** 있다" 는 판단은 **오름차순**일 때만 맞거든요.\n'
           '정렬되지 않은 리스트에 쓰면 있는 값도 "없다" 고 답할 수 있어요.'),
         WARN('시험에 "다음 리스트에 이진 탐색을 쓸 수 있는가?" 가 나오면 **정렬 여부**부터 확인!')])

    L.ox('이진 탐색은 리스트가 정렬되어 있지 않아도 항상 올바르게 값을 찾는다.', False,
        '가운데 값과 비교해 한쪽을 버리는 판단은 **정렬되어 있을 때만** 옳아요. 정렬 안 된 리스트면 먼저 `sort()` 해야 해요.')

    L.explain('left · right · mid 갱신',
        [T('`left`, `right` 는 **아직 후보인 구간**의 양 끝 인덱스예요. `mid` 는 그 가운데.\n'
           '가운데 값을 확인했으니 **mid 자체는 후보에서 빼고** 반쪽을 버려요.'),
         STEPS(('nums[mid] == target', '찾았다! mid 를 돌려줘요.'),
               ('nums[mid] < target', '답은 오른쪽 → `left = mid + 1`'),
               ('nums[mid] > target', '답은 왼쪽 → `right = mid - 1`'),
               ('left > right', '후보가 하나도 없음 → 없다(-1)'))],
        [T('따라가기로 left, right, mid 가 어떻게 움직이는지 봐요.'),
         TRACE('''\
nums = [2, 5, 9, 14, 20, 27, 33, 41]
target = 27
left, right = 0, len(nums) - 1
found = -1
while left <= right:
    mid = (left + right) // 2
    if nums[mid] == target:
        found = mid
        break
    elif nums[mid] < target:
        left = mid + 1
    else:
        right = mid - 1
print(found)''', '이진 탐색 따라가기'),
         KEY('`while left <= right` — `<=` 인 이유: left == right 일 때도 **후보가 한 칸 남아 있으니** 확인해야 해요.')])

    L.fill('이진 탐색 함수를 완성하세요.', '''\
def bsearch(nums, target):
    left, right = 0, len(nums) - 1
    while left ___ right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = ___
        else:
            right = ___
    return -1

print(bsearch([1, 4, 7, 10, 13, 16], 13), bsearch([1, 4, 7, 10, 13, 16], 5))''',
        [['<='], ['mid + 1', 'mid+1'], ['mid - 1', 'mid-1']],
        '`<=` 로 한 칸 남을 때까지 보고, mid 를 뺀 반쪽으로 좁혀요. 13 은 인덱스 4, 5 는 없어서 -1.', expect='4 -1')

    L.output('while 이 **몇 번** 도는지 세는 코드예요. 출력은?', '''\
nums = list(range(0, 100, 3))   # 0, 3, 6, ..., 99
target = 51
left, right = 0, len(nums) - 1
step = 0
while left <= right:
    step += 1
    mid = (left + right) // 2
    if nums[mid] == target:
        break
    elif nums[mid] < target:
        left = mid + 1
    else:
        right = mid - 1
print(mid, step)''',
        '34개 중에서 찾는데도 몇 번 만에 끝나요. 손으로 left/right/mid 표를 그려 확인해 보세요.\n\n```\n{out}\n```')

    L.explain('반복 횟수 감각 — log₂N',
        [T('한 번 비교할 때마다 후보가 **절반**이 돼요. 1024 → 512 → 256 → … → 1 까지 10번 나누면 끝!\n'
           '그래서 비교 횟수는 대략 **log₂N** 이에요. N 이 2배가 돼도 비교는 **1번**만 늘어요.'),
         REVEAL_RUN('N 을 1 이 될 때까지 반씩 나누는 횟수는?',
                    'for n in [8, 1000, 1000000, 1000000000]:\n    k = 0\n    m = n\n    while m > 1:\n        m //= 2\n        k += 1\n    print(n, "→", k, "번")')],
        [T('순차 탐색과 비교하면 차이가 엄청나요.'),
         FLIP(['N = 1,000', '순차: 최악 1,000번 / 이진: 약 10번'],
              ['N = 1,000,000', '순차: 최악 100만 번 / 이진: 약 20번'],
              ['N 이 2배', '순차: 2배 / 이진: +1번'])])

    L.short('정렬된 데이터 2048 개를 이진 탐색할 때, 후보를 반씩 줄여 **1개가 될 때까지** 몇 번 나누나요? (숫자만)', '11',
        '2048 = 2¹¹ 이니 11 번. 그 한 칸까지 확인하면 비교는 최대 12 번이에요.',
        check_code='m, k = 2048, 0\nwhile m > 1:\n    m //= 2\n    k += 1\nprint(k)')

    L.match('상황과 알맞은 갱신을 이어 보세요. (오름차순 리스트에서 target 찾기)',
        [['nums[mid] < target', 'left = mid + 1'], ['nums[mid] > target', 'right = mid - 1'],
         ['nums[mid] == target', 'mid 반환'], ['left > right', '-1 반환 (없음)']],
        '가운데가 **작으면 오른쪽**, **크면 왼쪽**으로. 구간이 뒤집히면(left > right) 후보가 없어요.')

    L.explain('파라메트릭 서치 — "가능한 최대값" 찾기',
        [T('이진 탐색은 리스트 안의 값만 찾는 게 아니에요. **답 후보(높이·길이)** 자체를 반씩 줄일 수도 있어요.\n'
           '예: 잔디 높이들이 있고 깎는 기계 높이를 H 로 맞추면 H 보다 높은 부분만 잘려요. **잘린 양이 M 이상**이 되는 **가장 높은 H** 는?'),
         CODE('grass = [19, 15, 10, 17]\nfor H in [10, 13, 15, 16]:\n    cut = 0\n    for g in grass:\n        if g > H:\n            cut += g - H\n    print(H, cut)', 'H 에 따른 잘린 양')],
        [T('H 를 올리면 잘린 양은 **줄어들기만** 해요. 그래서 "M 이상인가?" 가 어느 지점까지 O, 그 뒤로 X 예요.\n'
           '이 경계를 이진 탐색으로 찾아요. **O 면 답을 기록하고 더 높이**(left = mid + 1), **X 면 낮추기**(right = mid - 1).'),
         TRACE('''\
grass = [19, 15, 10, 17]
M = 7
left, right = 0, max(grass)
ans = 0
while left <= right:
    mid = (left + right) // 2
    cut = 0
    for g in grass:
        if g > mid:
            cut += g - mid
    if cut >= M:
        ans = mid
        left = mid + 1
    else:
        right = mid - 1
print(ans)''', '최대 높이 찾기'),
         EXAM('2026년에 이런 **떡 자르기형** 이진 탐색 코드를 주고, 잘못 쓴 갱신 줄의 문제점을 서술하게 했어요.')])

    L.fill('"잘린 양 ≥ M" 을 만족하는 **최대 높이**를 찾는 코드의 빈칸을 채우세요.', '''\
grass = [20, 15, 10, 17]
M = 7
left, right = 0, max(grass)
ans = 0
while left <= right:
    mid = (left + right) // 2
    cut = 0
    for g in grass:
        if g > mid:
            cut += g - mid
    if cut >= M:
        ans = ___
        left = ___
    else:
        right = mid - 1
print(ans)''', [['mid'], ['mid + 1', 'mid+1']],
        '조건을 만족하면 **일단 답으로 기록**하고 더 높은 쪽을 시도해요. 답은 15 (잘린 양 5+0+0+2=7).', expect='15')

    L.explain('left = mid 로 쓰면 왜 무한 루프일까?',
        [T('갱신을 `left = mid` 로 쓰면 mid 가 **다시 후보에 남아요**.\n'
           'left 와 right 가 **딱 1 차이**일 때 `mid = (left + right) // 2` 는 left 와 같아지니, left 가 **그대로** 예요. 구간이 영영 줄지 않아요!'),
         CODE('''\
left, right = 0, 8
step = 0
while left < right:
    step += 1
    if step > 8:
        print("무한 루프!")
        break
    mid = (left + right) // 2
    print(left, right, mid)
    if mid * mid <= 50:
        left = mid          # mid 를 버리지 않음
    else:
        right = mid - 1''', 'left = mid 의 함정 (8번에서 강제로 멈춤)')],
        [T('고치는 방법은 두 가지예요. 핵심은 **매 반복마다 구간이 반드시 줄어들게** 만드는 거예요.'),
         CMP(side('방법 1', '`ans = mid` 로 기록하고 `left = mid + 1`, 조건은 `left <= right`',
                  'left, right, ans = 0, 8, 0\nwhile left <= right:\n    mid = (left + right) // 2\n    if mid * mid <= 50:\n        ans = mid\n        left = mid + 1\n    else:\n        right = mid - 1\nprint(ans)', 'good'),
             side('방법 2', 'mid 를 올림으로: `mid = (left + right + 1) // 2`',
                  'left, right = 0, 8\nwhile left < right:\n    mid = (left + right + 1) // 2\n    if mid * mid <= 50:\n        left = mid\n    else:\n        right = mid - 1\nprint(left)', 'good')),
         KEY('서술형 답의 세 요소: ① left 와 right 가 1 차이일 때 ② mid 가 left 와 같아져 ③ left 가 변하지 않으므로 구간이 줄지 않아 무한 반복.')])

    L.spot('다음 코드는 n 이 특정 값일 때 **끝나지 않아요**. 문제가 되는 줄은?', '''\
n = 30
left, right = 0, n
while left < right:
    mid = (left + right) // 2
    if mid * mid <= n:
        left = mid
    else:
        right = mid - 1
print(left)''', 6,
        'left 와 right 가 1 차이(예: 5, 6)일 때 mid = 5 = left, 5×5 ≤ 30 이면 `left = mid` 가 left 를 그대로 둬서 무한 루프예요. `mid = (left + right + 1) // 2` 로 올림하거나 ans 기록 + `left = mid + 1` 방식으로 바꿔요.')

    L.bucket('각 상황이 이진 탐색으로 풀기 **알맞은지** 분류하세요.', ['알맞음', '알맞지 않음'],
        [['정렬된 학번 목록에서 학번 찾기', 1], ['뒤섞인 카드 더미에서 특정 카드 찾기', 2],
         ['잘린 양 ≥ M 인 최대 높이 찾기', 1], ['x*x ≤ N 인 가장 큰 정수 x 찾기', 1],
         ['정렬 안 된 점수 리스트의 최댓값 찾기', 2]],
        '"정렬되어 있다" 또는 "어느 지점을 기준으로 O/X 가 한 번만 바뀐다" 가 이진 탐색의 조건이에요. 뒤섞인 데이터는 순차 탐색이나 max() 를 써요.')

    L.practice('[기출유사] 잔디 깎기 — 최대 높이 찾기',
'''운동장 잔디 N 줄의 높이가 주어져요. 기계 높이를 H 로 맞추면 H 보다 높은 잔디는 H 높이로 깎이고, 깎여 나온 양은 `(잔디 높이 - H)` 의 합이에요.
깎인 양이 **M 이상**이 되도록 하는 **가장 높은 H** 를 출력하세요.

**[조건]**
- 첫째 줄: N M, 둘째 줄: 잔디 높이 N 개 (깎인 양이 M 이상이 되는 H 는 항상 있어요)
- 이진 탐색으로 H 를 찾아요. `left = 0`, `right = 가장 높은 잔디`
- 조건을 만족하면 `ans = mid` 로 기록하고 `left = mid + 1`, 아니면 `right = mid - 1`

{ex}

{ex2}''',
'''n, m = map(int, input().split())
grass = list(map(int, input().split()))
left, right = 0, max(grass)
ans = 0
# 이진 탐색을 작성하세요
print(ans)''',
'''n, m = map(int, input().split())
grass = list(map(int, input().split()))
left, right = 0, max(grass)
ans = 0
while left <= right:
    mid = (left + right) // 2
    cut = 0
    for g in grass:            # 높이 mid 로 깎았을 때 나온 양
        if g > mid:
            cut += g - mid
    if cut >= m:               # 충분하면 답 기록하고 더 높이
        ans = mid
        left = mid + 1
    else:                      # 부족하면 낮추기
        right = mid - 1
print(ans)''',
        ['4 7\n20 15 10 17', '5 20\n4 42 40 26 46'],
        ['3 6\n2 2 2', '1 1\n1000000', '4 3\n10 10 10 10', '3 60\n20 20 20'],
        ['while 안에서 mid 높이로 깎았을 때의 양 `cut` 을 for 로 구해요.',
         '`if cut >= m:` 이면 `ans = mid; left = mid + 1`, 아니면 `right = mid - 1`.',
         '`left = mid` 로 쓰면 무한 루프! 반드시 `mid + 1`.'],
        'H 를 올릴수록 깎인 양은 줄어들기만 하니 O…O X…X 경계를 이진 탐색으로 찾을 수 있어요. 높이가 100만이어도 약 20번만 돌면 끝나요.')

    L.practice('이진 탐색 비교 횟수 세기',
'''오름차순으로 정렬된 정수들과 찾을 값이 주어져요. 이진 탐색으로 찾고, **while 을 몇 번 돌았는지** 함께 출력하세요.

**[조건]**
- 첫째 줄: 정렬된 정수들(공백 구분), 둘째 줄: 찾을 값
- 찾으면 `위치: 인덱스`, 없으면 `없음`
- 둘째 줄에 `비교: 횟수번` (while 한 바퀴 = 1번)

{ex}

{ex2}''',
'''nums = list(map(int, input().split()))
target = int(input())
# 이어서 작성하세요
''',
'''nums = list(map(int, input().split()))
target = int(input())
left, right = 0, len(nums) - 1
found = -1
step = 0
while left <= right:
    step += 1                       # 한 바퀴 = 비교 1번
    mid = (left + right) // 2
    if nums[mid] == target:
        found = mid
        break
    elif nums[mid] < target:
        left = mid + 1
    else:
        right = mid - 1
if found == -1:
    print("없음")
else:
    print(f"위치: {found}")
print(f"비교: {step}번")''',
        ['2 5 9 14 20 27 33 41\n27', '1 3 5 7 9\n4'],
        ['7\n7', '7\n3', '1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16\n16', '10 20 30\n10'],
        ['기본 이진 탐색에 `step += 1` 만 while 첫 줄에 넣어요.',
         '찾으면 `found = mid` 후 `break`.', '없을 때도 비교 횟수는 출력해요.'],
        '16개짜리에서 맨 끝 값을 찾아도 5번이면 끝나요. 이진 탐색의 비교 횟수는 약 log₂N + 1 을 넘지 않아요.')

    L.essay('파라메트릭 서치에서 `while left < right:` 안의 갱신을 `if 조건: left = mid` / `else: right = mid - 1` (mid = (left + right) // 2) 로 쓰면 프로그램이 끝나지 않을 수 있어요. **언제, 왜** 그런지 서술하고 고치는 방법을 쓰세요.',
        'left 와 right 가 1 차이일 때 mid = (left + right) // 2 는 내림 때문에 left 와 같아진다. 이때 조건을 만족하면 left = mid 가 실행되어 left 가 그대로이고, 구간이 줄어들지 않아 같은 반복이 무한히 계속된다. mid 를 (left + right + 1) // 2 로 올림하거나, ans = mid 로 답을 기록한 뒤 left = mid + 1 로 바꾸고 조건을 left <= right 로 해서 매번 구간이 줄게 고친다.',
        ['left 와 right 가 1 차이일 때', 'mid 가 left 와 같아진다(내림)', 'left 가 변하지 않아 구간이 줄지 않는다 → 무한 루프', 'ans 기록 + left = mid + 1 또는 올림 mid 로 고친다'])


def lesson13(C):
    L = C.lesson('β-13 합병 정렬 + 메뉴형 CRUD 맛보기', 35,
'''- `merge(a, b)`: 두 **정렬된** 리스트의 앞쪽끼리 비교해 작은 것부터 담고, 남은 쪽은 `a[i:]`, `b[j:]` 로 통째로 붙여요.
- `merge_sort(arr)`: 길이 1 이하면 그대로(기저 조건) → 반으로 나눠 각각 정렬(재귀) → merge 로 합치기
- 내림차순은 merge 의 비교 한 줄 `a[i] <= b[j]` 를 `a[i] >= b[j]` 로 바꾸면 끝!
- 메뉴 프로그램 = **기능별 함수** + `{이름: 잔액}` 딕셔너리 + `while True` 메뉴 + 예외 상황 메시지(없는 이름·잔액 부족·잘못된 메뉴)''')

    L.review('🔁 지난 시간 복습: 이진 탐색',
        [T('이진 탐색은 **정렬된** 리스트에서 가운데와 비교해 절반을 버려요. `left = mid + 1`, `right = mid - 1` 로 mid 를 꼭 빼야 무한 루프가 안 생겨요.\n'
           '파라메트릭 서치는 "조건을 만족하는 최대값" 을 같은 방법으로 찾았어요.'),
         REVEAL_RUN('후보 100만 개를 반씩 줄이면 몇 번 만에 1개가 될까요?',
                    'm, k = 1000000, 0\nwhile m > 1:\n    m //= 2\n    k += 1\nprint(k)')])
    L.output('복습: 출력은?', '''\
nums = [3, 6, 9, 12, 15, 18, 21]
left, right = 0, len(nums) - 1
while left <= right:
    mid = (left + right) // 2
    print(nums[mid], end=" ")
    if nums[mid] == 6:
        break
    elif nums[mid] < 6:
        left = mid + 1
    else:
        right = mid - 1''',
        '가운데 12 → 왼쪽 반의 가운데 6 에서 찾아요. 들른 값만 출력돼요.\n\n```\n{out}\n```', review=True)
    L.ox('복습: 파라메트릭 서치에서 조건을 만족할 때 `left = mid` 로 쓰면, left 와 right 가 1 차이일 때 무한 루프가 생길 수 있다.', True,
        'mid = (left + right) // 2 가 left 와 같아져 left 가 그대로이기 때문이에요. `ans = mid; left = mid + 1` 로 고쳐요.', review=True)

    L.explain('merge — 정렬된 두 줄 합치기',
        [T('키 순서로 선 **두 줄**을 한 줄로 합친다고 생각해 봐요. 각 줄의 **맨 앞 사람끼리만** 비교해 더 작은 사람을 새 줄에 보내면 돼요.\n'
           '두 줄이 이미 정렬되어 있으니 맨 앞이 각 줄에서 가장 작거든요.'),
         STEPS('i, j 를 각 줄의 맨 앞(0)에 둔다',
               'a[i] 와 b[j] 중 작은 쪽을 result 에 넣고, 그쪽 인덱스만 1 증가',
               '한 줄이 다 떨어질 때까지 반복 (`while i < len(a) and j < len(b)`)',
               '남은 줄은 이미 정렬돼 있으니 `a[i:]`, `b[j:]` 를 통째로 붙이기')],
        [T('따라가기로 i, j, result 가 어떻게 변하는지 봐요.'),
         TRACE('''\
def merge(a, b):
    result = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i])
            i += 1
        else:
            result.append(b[j])
            j += 1
    result += a[i:]
    result += b[j:]
    return result

print(merge([2, 5, 8], [1, 3, 9, 10]))''', 'merge 따라가기'),
         WARN('남은 원소 붙이기(`result += a[i:]`, `b[j:]`)를 빼먹으면 **값이 사라져요**. 시험 빈칸 단골!')])

    L.fill('merge 함수의 빈칸을 채우세요.', '''\
def merge(a, b):
    result = []
    i = j = 0
    while i < len(a) ___ j < len(b):
        if a[i] <= b[j]:
            result.append(a[i])
            i += 1
        else:
            result.append(___)
            j += 1
    result += a[___:]
    result += b[j:]
    return result

print(merge([1, 4, 6], [2, 3, 7, 8]))''', [['and'], ['b[j]'], ['i']],
        '두 줄 **모두** 남아 있을 때만 비교하니 `and`. else 쪽은 b 의 앞사람 `b[j]`. 끝나면 a 의 남은 부분 `a[i:]`.',
        expect='[1, 2, 3, 4, 6, 7, 8]')

    L.output('남은 원소 붙이기를 **빼먹은** merge 예요. 출력은?', '''\
def merge(a, b):
    result = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i])
            i += 1
        else:
            result.append(b[j])
            j += 1
    return result

print(merge([1, 5, 9], [2, 3]))''',
        'b 가 먼저 다 떨어지는 순간 while 이 끝나요. a 에 남은 5, 9 가 사라져요.\n\n```\n{out}\n```')

    L.explain('merge_sort — 쪼개고, 정렬하고, 합치기',
        [T('합병 정렬은 재귀예요. **길이가 1 이하면 이미 정렬된 것**(기저 조건)!\n'
           '그보다 길면 반으로 나눠 **각각 merge_sort 로 정렬**하고(재귀 호출), merge 로 합쳐요.'),
         CODE('''\
def merge(a, b):
    result = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i]); i += 1
        else:
            result.append(b[j]); j += 1
    return result + a[i:] + b[j:]

def merge_sort(arr):
    if len(arr) <= 1:              # 기저 조건
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])   # 왼쪽 반 정렬
    right = merge_sort(arr[mid:])  # 오른쪽 반 정렬
    return merge(left, right)      # 합치기

print(merge_sort([38, 27, 43, 3, 9, 82, 10]))''', '합병 정렬')],
        [T('`[5, 2, 4, 1]` 이 어떻게 쪼개지고 합쳐지는지 단계별로 봐요.'),
         STEPS(('쪼개기 1', '[5, 2, 4, 1] → [5, 2] | [4, 1]'),
               ('쪼개기 2', '[5, 2] → [5] | [2],  [4, 1] → [4] | [1]  (길이 1 = 기저 조건)'),
               ('합치기 1', 'merge([5], [2]) = [2, 5],  merge([4], [1]) = [1, 4]'),
               ('합치기 2', 'merge([2, 5], [1, 4]) = [1, 2, 4, 5]')),
         KEY('쪼개는 건 재귀 호출이 **내려가며**, 합치는 건 **돌아오며** 일어나요. β-10 의 호출 스택과 같은 원리!')],
        [T('merge_sort 안에 print 를 넣으면 **어떤 순서로 합쳐지는지** 볼 수 있어요. 시험 출력 추론은 이런 모양이에요.'),
         REVEAL_RUN('merge 결과를 찍어 보면?', '''\
def merge(a, b):
    r, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            r.append(a[i]); i += 1
        else:
            r.append(b[j]); j += 1
    return r + a[i:] + b[j:]

def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    m = merge(merge_sort(arr[:mid]), merge_sort(arr[mid:]))
    print(m)
    return m

merge_sort([6, 3, 8, 1, 5])'''),
         EXAM('2026년에 merge 빈칸 + 정렬 결과 출력 + "**내림차순으로 바꾸려면 몇 번 줄을 고치나**" 가 한 문항으로 나왔어요.')])

    L.order('merge_sort 함수의 줄을 순서대로 놓으세요.',
        ['def merge_sort(arr):', '    if len(arr) <= 1:', '        return arr', '    mid = len(arr) // 2',
         '    left = merge_sort(arr[:mid])', '    right = merge_sort(arr[mid:])', '    return merge(left, right)'],
        '기저 조건 → 가운데 구하기 → 왼쪽·오른쪽 재귀 정렬 → 합치기. 기저 조건이 재귀 호출보다 **앞**에 와야 해요.')

    L.output('출력은?', '''\
count = 0

def merge(a, b):
    r, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            r.append(a[i]); i += 1
        else:
            r.append(b[j]); j += 1
    return r + a[i:] + b[j:]

def merge_sort(arr):
    global count
    count += 1
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    return merge(merge_sort(arr[:mid]), merge_sort(arr[mid:]))

print(merge_sort([7, 2, 9, 4]))
print(count)''',
        '길이 4 → 2, 2 → 1, 1, 1, 1 로 쪼개지니 merge_sort 호출은 1 + 2 + 4 = 7번이에요.\n\n```\n{out}\n```')

    L.spot('이 합병 정렬을 **내림차순**으로 바꾸려면 몇 번 줄을 고쳐야 할까요? (한 줄만 고칩니다)', '''\
def merge(a, b):
    result = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i])
            i += 1
        else:
            result.append(b[j])
            j += 1
    return result + a[i:] + b[j:]

def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    return merge(merge_sort(arr[:mid]), merge_sort(arr[mid:]))''', 5,
        '어느 쪽을 먼저 담을지 정하는 비교는 5번 줄 하나예요. `a[i] >= b[j]` 로 바꾸면 **큰 것부터** 담아 내림차순이 돼요. 14번 줄의 `<= 1` 은 기저 조건이라 건드리면 안 돼요.')

    L.explain('메뉴형 프로그램 — 함수 + 딕셔너리 + while',
        [T('큰 문항의 단골은 **은행·도서 관리** 메뉴 프로그램이에요. 뼈대는 늘 같아요.\n'
           '데이터는 `{이름: 잔액}` 딕셔너리 하나, 기능은 **함수 하나씩**, 메뉴는 `while True` 로 돌다가 종료 번호에서 break.'),
         STEPS(('데이터', '`bank = {}` — 키: 이름, 값: 잔액'),
               ('기능 함수', 'open_account · deposit · withdraw · show_all … 딕셔너리를 인자로 받아요'),
               ('메뉴 반복', '`while True:` → `menu = input()` → if/elif 로 함수 호출'),
               ('예외 처리', '없는 이름 · 중복 개설 · 잔액 부족 · 잘못된 메뉴 → **메시지 출력**'))],
        [T('짧은 예시로 흐름을 봐요. 입력은 줄마다 메뉴 번호, 그다음 줄에 필요한 값이 와요.'),
         CODE('''\
def open_account(bank, name):
    if name in bank:
        print("이미 있는 계좌입니다")
    else:
        bank[name] = 0
        print(name, "계좌 개설")

def deposit(bank, name, money):
    if name not in bank:
        print("없는 계좌입니다")
        return
    bank[name] += money
    print(name, "잔액:", bank[name])

bank = {}
while True:
    menu = input()
    if menu == "1":
        open_account(bank, input())
    elif menu == "2":
        deposit(bank, input(), int(input()))
    elif menu == "0":
        break
    else:
        print("잘못된 메뉴입니다")''', '미니 은행', stdin='1\nkim\n1\nkim\n2\nkim\n500\n2\nlee\n100\n7\n0\n'),
         TIP('딕셔너리는 **가변**이라 함수 안에서 `bank[name] = 0` 처럼 바꾸면 바깥의 bank 도 바뀌어요. global 이 필요 없어요.')],
        [T('평균 같은 **통계**를 낼 땐 계좌가 **하나도 없는 경우**를 먼저 막아야 해요. 0 으로 나누면 ZeroDivisionError!'),
         CMP(side('위험', '빈 딕셔너리면 오류', 'bank = {}\nprint(sum(bank.values()) / len(bank))', 'bad', expect_error=True),
             side('안전', '먼저 비었는지 검사', 'bank = {}\nif len(bank) == 0:\n    print("계좌가 없습니다")\nelse:\n    print(round(sum(bank.values()) / len(bank), 1))', 'good')),
         EXAM('2024·2025년에 **은행 함수 여러 개 + {이름: 잔액}**, 계좌 중복 처리, 거래 기록(list of dict), 빈 경우 통계가 큰 문항으로 나왔어요.')])

    L.output('위 미니 은행 코드에 다음을 입력했을 때 출력은? (입력: `1, kim, 1, kim, 2, kim, 500, 2, lee, 100, 7, 0` 을 한 줄씩)', '''\
def open_account(bank, name):
    if name in bank:
        print("이미 있는 계좌입니다")
    else:
        bank[name] = 0
        print(name, "계좌 개설")

def deposit(bank, name, money):
    if name not in bank:
        print("없는 계좌입니다")
        return
    bank[name] += money
    print(name, "잔액:", bank[name])

bank = {}
while True:
    menu = input()
    if menu == "1":
        open_account(bank, input())
    elif menu == "2":
        deposit(bank, input(), int(input()))
    elif menu == "0":
        break
    else:
        print("잘못된 메뉴입니다")''',
        '두 번째 개설은 중복, lee 는 없는 계좌, 7 은 잘못된 메뉴, 0 에서 종료.\n\n```\n{out}\n```',
        stdin='1\nkim\n1\nkim\n2\nkim\n500\n2\nlee\n100\n7\n0\n')

    L.fill('출금 함수를 완성하세요. 없는 계좌, 잔액 부족을 처리해야 해요.', '''\
def withdraw(bank, name, money):
    if name ___ bank:
        print("없는 계좌입니다")
    elif bank[name] ___ money:
        print("잔액이 부족합니다")
    else:
        bank[name] ___ money
        print(name, "잔액:", bank[name])

bank = {"kim": 1000}
withdraw(bank, "kim", 300)
withdraw(bank, "kim", 900)
withdraw(bank, "lee", 10)''', [['not in'], ['<'], ['-=']],
        '없는 계좌는 `not in`, 잔액이 출금액보다 **작으면** 부족, 정상이면 `-=` 로 빼요.',
        expect='kim 잔액: 700\n잔액이 부족합니다\n없는 계좌입니다')

    L.bucket('메뉴 프로그램에서 각 상황을 처리하는 **도구**로 분류하세요.', ['딕셔너리 검사(in / not in)', '값 비교(<, <=)', 'else 분기'],
        [['이미 있는 이름으로 개설', 1], ['없는 이름으로 입금', 1], ['잔액보다 큰 금액 출금', 2],
         ['0 이하 금액 입금', 2], ['메뉴에 없는 번호 입력', 3]],
        '이름 문제는 키 검사(`in`), 금액 문제는 크기 비교, 메뉴 번호가 어느 if/elif 에도 안 맞으면 마지막 else 에서 "잘못된 메뉴" 를 출력해요.')

    L.practice('[기출유사] 합병 정렬로 성적 순위 매기기',
'''학생 점수들을 **합병 정렬로 내림차순** 정렬해서 출력하세요.

**[조건]**
- 입력: 점수들(공백 구분, 1개 이상)
- `merge(a, b)` 와 `merge_sort(arr)` 를 직접 만들어요. `sort()`, `sorted()` 는 쓰지 않아요. (자동 채점은 결과만 확인해요)
- 첫째 줄: 내림차순으로 정렬한 점수 (공백 구분)
- 둘째 줄: `1등: 점수`

{ex}

{ex2}''',
'''def merge(a, b):
    result = []
    i = j = 0
    # 큰 것부터 담도록 작성하세요
    return result

def merge_sort(arr):
    # 기저 조건 → 반으로 나누기 → 합치기
    return arr

scores = list(map(int, input().split()))
''',
'''def merge(a, b):
    result = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] >= b[j]:          # 내림차순: 큰 것부터
            result.append(a[i])
            i += 1
        else:
            result.append(b[j])
            j += 1
    result += a[i:]               # 남은 원소 붙이기
    result += b[j:]
    return result

def merge_sort(arr):
    if len(arr) <= 1:             # 기저 조건
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

scores = list(map(int, input().split()))
ranked = merge_sort(scores)
print(" ".join(map(str, ranked)))
print(f"1등: {ranked[0]}")''',
        ['72 95 88 61 95 80', '40 100'],
        ['77', '5 4 3 2 1', '1 2 3 4 5 6 7 8 9 10 11'],
        ['merge 는 `a[i] >= b[j]` 일 때 a 쪽을 먼저 담으면 내림차순이에요.',
         'while 이 끝나면 `result += a[i:]`, `result += b[j:]` 를 잊지 마세요.',
         'merge_sort: `if len(arr) <= 1: return arr` → mid 로 나눠 재귀 → merge.'],
        '오름차순과 내림차순의 차이는 merge 의 비교 한 줄뿐이에요. 점수를 출력할 때는 `map(str, …)` 으로 글자로 바꿔 join 해요.')

    L.practice('[기출유사] 메뉴형 은행 프로그램',
'''함수 여러 개와 `{이름: 잔액}` 딕셔너리로 은행 프로그램을 만드세요. 입력은 **한 줄에 하나씩** 들어와요: 먼저 메뉴 번호, 이어서 그 메뉴에 필요한 값들.

**[메뉴]**
- `1` 개설: 다음 줄 이름. 이미 있으면 `이미 있는 계좌입니다`, 아니면 잔액 0 으로 만들고 `이름 계좌 개설`
- `2` 입금: 다음 두 줄 이름, 금액. 없는 이름이면 `없는 계좌입니다`, 금액이 0 이하면 `금액이 올바르지 않습니다`, 정상이면 `이름 잔액: 값`
- `3` 출금: 다음 두 줄 이름, 금액. 없는 이름 → `없는 계좌입니다`, 잔액보다 크면 `잔액이 부족합니다`, 정상이면 `이름 잔액: 값`
- `4` 통계: 계좌가 없으면 `계좌가 없습니다`, 있으면 `계좌 개수개, 총액 값, 평균 값` (평균은 `round(…, 1)`)
- `0` 종료: `종료합니다` 출력 후 끝
- 그 밖의 번호: `잘못된 메뉴입니다`

**[조건]**
- 개설·입금·출금·통계를 각각 **함수**로 만들어요. (예: `open_account(bank, name)`)
- 입력 검사(없는 이름, 금액)는 각 함수 안에서 처리해요.

{ex}

{ex2}''',
'''def open_account(bank, name):
    pass

def deposit(bank, name, money):
    pass

def withdraw(bank, name, money):
    pass

def stats(bank):
    pass

bank = {}
while True:
    menu = input()
    if menu == "0":
        print("종료합니다")
        break
    # 나머지 메뉴를 작성하세요
''',
'''def open_account(bank, name):
    if name in bank:                       # 중복 개설
        print("이미 있는 계좌입니다")
    else:
        bank[name] = 0
        print(f"{name} 계좌 개설")

def deposit(bank, name, money):
    if name not in bank:
        print("없는 계좌입니다")
    elif money <= 0:                       # 0 이하 금액
        print("금액이 올바르지 않습니다")
    else:
        bank[name] += money
        print(f"{name} 잔액: {bank[name]}")

def withdraw(bank, name, money):
    if name not in bank:
        print("없는 계좌입니다")
    elif money > bank[name]:               # 잔액 부족
        print("잔액이 부족합니다")
    else:
        bank[name] -= money
        print(f"{name} 잔액: {bank[name]}")

def stats(bank):
    if len(bank) == 0:                     # 빈 경우 먼저 (0 으로 나누기 방지)
        print("계좌가 없습니다")
        return
    total = sum(bank.values())
    avg = round(total / len(bank), 1)
    print(f"계좌 {len(bank)}개, 총액 {total}, 평균 {avg}")

bank = {}                                  # {이름: 잔액}
while True:
    menu = input()
    if menu == "1":
        open_account(bank, input())
    elif menu == "2":
        name = input()
        money = int(input())
        deposit(bank, name, money)
    elif menu == "3":
        name = input()
        money = int(input())
        withdraw(bank, name, money)
    elif menu == "4":
        stats(bank)
    elif menu == "0":
        print("종료합니다")
        break
    else:
        print("잘못된 메뉴입니다")''',
        ['1\nkim\n1\nlee\n2\nkim\n5000\n3\nkim\n2000\n3\nlee\n100\n4\n0',
         '4\n1\npark\n1\npark\n2\nchoi\n300\n9\n0'],
        ['0', '1\na\n2\na\n0\n2\na\n-5\n3\na\n1\n4\n0',
         '1\nx\n1\ny\n1\nz\n2\nx\n100\n2\ny\n250\n3\ny\n250\n4\n5\n0',
         '1\nm\n2\nm\n999\n3\nm\n999\n3\nm\n1\n4\n0'],
        ['메뉴 번호는 문자열로 비교해요: `if menu == "1":`. 금액은 `int(input())`.',
         '각 함수는 **먼저 예외 상황**(없는 이름, 잘못된 금액)을 if 로 걸러 내고, 마지막 else 에서 정상 처리해요.',
         '통계는 `if len(bank) == 0:` 을 먼저! 평균은 `round(sum(bank.values()) / len(bank), 1)`.'],
        '함수마다 "예외 먼저, 정상은 마지막" 순서로 쓰면 읽기 쉽고 실수가 줄어요. 딕셔너리는 함수 안에서 바꿔도 바깥에 그대로 반영돼요. 통계에서 빈 딕셔너리를 먼저 막지 않으면 ZeroDivisionError 가 나요.')

    L.essay('합병 정렬 `merge_sort(arr)` 에서 기저 조건 `if len(arr) <= 1: return arr` 이 **왜 필요한지**, 그리고 이 조건이 "길이 1 이하" 인 **이유**를 서술하세요.',
        '기저 조건이 없으면 리스트를 계속 반으로 나누는 재귀 호출이 끝나지 않아(빈 리스트를 또 나눔) RecursionError 가 난다. 원소가 0개 또는 1개인 리스트는 비교할 것이 없어 그 자체로 이미 정렬된 상태이므로, 더 나누지 않고 그대로 돌려주면 된다. 그 결과를 merge 로 합쳐 올라가며 전체가 정렬된다.',
        ['기저 조건이 없으면 재귀가 끝나지 않는다(RecursionError)', '원소 0~1개는 이미 정렬된 상태다', '더 나누지 않고 그대로 반환한다', '반환된 결과를 merge 로 합친다'])
