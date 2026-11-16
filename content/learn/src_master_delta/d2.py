from glib import *

def spotv(q, code, a, ex='', name=None, **kw):
    """예외가 나는 줄을 실제 실행으로 확인한 뒤 spot 문제를 만든다"""
    assert errline(code) == a, (errline(code), a)
    if name: assert err(code) == name, (err(code), name)
    return spot(q, code, a, ex, **kw)
def same(code, expect, stdin=''):
    o = run(code, nl(stdin)); assert o == expect, (o, expect)

# ============================================================ D4
_shared = D('''
nums = [1, 2, 3, 4, 5, 6]
it = iter(nums)
for a in it:
    if a == 2:
        break
for b in it:
    print(b, end=" ")
print()
for c in it:
    print("c", c)
print(next(it, "없음"), len(nums))
''')
_zip2 = D('''
names = ["가", "나", "다", "라", "마"]
it = iter(names)
pairs = list(zip(it, it))
print(pairs)
print(next(it, "남은 것 없음"))
''')
_order_cls = D('''
class Down:
    def __init__(self, n):
        self.n = n
    def __iter__(self):
        print("I", end=" ")
        return self
    def __next__(self):
        print("N", end=" ")
        if self.n == 0:
            raise StopIteration
        self.n -= 1
        return self.n + 1
d = Down(2)
for x in d:
    print(x, end=" ")
print()
for x in d:
    print(x, end=" ")
print("끝")
''')
_spot_next = D('''
class Seat:
    def __init__(self, rows):
        self.rows = rows
        self.i = 0
    def __iter__(self):
        return self
    def __next__(self):
        row = self.rows[self.i]
        self.i += 1
        return row + "열"
s = Seat(["A", "B"])
print(next(s))
print(next(s))
print(next(s))
''')
_spot_val = D('''
class Ages:
    def __init__(self, data):
        self.data = data
        self.i = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.i >= len(self.data):
            raise StopIteration
        v = self.data[self.i]
        self.i += 1
        if v < 0:
            raise ValueError("음수")
        return v
total = 0
for a in Ages([15, 16, -1, 17]):
    total += a
print(total)
''')
_val_out = D('''
class Ages:
    def __init__(self, data):
        self.data = data
        self.i = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.i >= len(self.data):
            raise StopIteration
        v = self.data[self.i]
        self.i += 1
        if v < 0:
            raise ValueError(f"{v} 는 음수")
        return v
it = Ages([15, -3, 16, -1, 17])
total = 0
while True:
    try:
        total += next(it)
    except ValueError as e:
        print("건너뜀:", e)
    except StopIteration:
        print("끝")
        break
print(total)
''')
same("it = iter([1, 2, 3])\nprint(iter(it) is it, iter([1, 2, 3]) is [1, 2, 3])", 'True False')
same("m = map(str, [1, 2])\nprint(iter(m) is m)\nr = range(3)\nprint(iter(r) is r)\ns = 'ab'\nprint(iter(s) is s)\nz = zip([1], [2])\nprint(iter(z) is z)\ne = enumerate([1])\nprint(iter(e) is e)\nd = {1: 2}\nprint(iter(d) is d)", 'True\nFalse\nFalse\nTrue\nTrue\nFalse')

D4 = lesson('4강. 이터레이터 심화 — for 문이 몰래 하는 일', 45,
'- for 문 = `iter()` **한 번** → `next()` 반복 → **StopIteration** 이 나면 조용히 끝\n- **이터러블**(리스트·문자열·range)은 iter 할 때마다 새 이터레이터, **이터레이터**는 `iter(it) is it` — 한 번 쓰면 끝\n- `map`·`filter`·`zip`·`enumerate` 의 결과도 이터레이터라서 **두 번째 for 는 빈손**\n- `__next__` 는 ① 끝 검사 → `raise StopIteration` ② 상태 갱신 ③ 값 return\n- for 문이 받아 주는 예외는 **StopIteration 하나뿐** — `raise ValueError` 는 try/except 로 직접 받아야 한다\n- 검사에서 raise 하기 **전에** 위치를 먼저 옮겨야 다음 next 가 다음 값으로 넘어간다',
review('🔁 3강 복습', [T('직접 구현하는 정렬의 핵심 네 가지를 확인해요.'), flip(['선택 정렬의 한 바퀴', '남은 칸에서 가장 작은 값의 **위치**를 찾아 맨 앞과 교환 — 교환은 바퀴당 최대 1번'], ['버블 정렬 안쪽 반복의 범위', '`range(n - 1 - i)` — 뒤쪽 i 칸은 이미 자리가 정해졌으니 제외'], ['`swapped` 가 False 인 채로 한 바퀴가 끝나면', '교환이 한 번도 없었다 = 이미 정렬됨 → `break`'], ['오름차순 → 내림차순', '비교 부등호 방향 하나만 바꾼다'])]),
outq('복습 — 출력 결과는?', D('''
a = [2, 1, 3, 5, 4]
n = len(a)
passes = 0
for i in range(n - 1):
    swapped = False
    passes += 1
    for j in range(n - 1 - i):
        if a[j] > a[j + 1]:
            a[j], a[j + 1] = a[j + 1], a[j]
            swapped = True
    if not swapped:
        break
print(a, passes)
'''), '1바퀴에서 (2,1), (5,4) 가 교환돼 정렬이 끝나요. 2바퀴는 교환이 없어서 `swapped` 가 False → break. 그래서 바퀴 수는 2예요.', review=True),
explain('iter 와 next — 약속(프로토콜) 정확히 알기',
  [T('L.O.T.C. 에서 `iter()` 와 `next()` 를 배웠어요. 응용편에서는 "**누가 언제 무엇을 부르는가**"를 한 줄도 틀리지 않게 따라가는 연습을 해요. 2024·2025년 모두 이 순서를 묻는 문제가 10점 이상으로 나왔어요.'),
   C(D('''
it = iter([10, 20, 30])
print(next(it))
print(next(it))
print(next(it))
print(next(it, "끝"))
print(next(it, "끝"))
'''), 'next(it, 기본값) — 다 꺼냈으면 오류 대신 기본값'),
   key('`next(it)` 는 다 꺼낸 뒤에 부르면 **StopIteration** 예외가 나요. `next(it, 기본값)` 처럼 두 번째 인자를 주면 예외 대신 그 값을 돌려줘요. 한 번 끝난 이터레이터는 몇 번을 불러도 계속 끝난 상태예요.')],
  [T('for 문은 사실 아래 오른쪽 코드를 줄여 쓴 것이에요. 시험에서 "for 문을 쓰지 않고 같은 결과를 내라" 또는 "for 문이 내부에서 하는 일을 서술하라"로 나와요.'),
   cmp('for 문', 'for x in data:\n    print(x)', 'for 문이 실제로 하는 일', 'it = iter(data)\nwhile True:\n    try:\n        x = next(it)\n    except StopIteration:\n        break\n    print(x)', 'iter 는 시작할 때 딱 한 번', 'next 는 값의 개수 + 1 번 (마지막은 StopIteration)', tones=('good', 'good')),
   exam('값이 3개면 `next` 는 **4번** 불려요. 네 번째 호출에서 StopIteration 이 나고, for 문이 그것을 받아 **오류 없이** 반복을 끝내요. "next 호출 횟수"를 묻는 문제에서 1 을 빼먹지 마세요.')],
  [T('서술형 답안은 이 세 단계를 순서대로 쓰면 돼요.'),
   steps(['① iter', 'for 문이 시작될 때 대상에 `iter()` (= `__iter__`) 를 **한 번** 호출해 이터레이터를 얻는다.'], ['② next 반복', '반복할 때마다 그 이터레이터에 `next()` (= `__next__`) 를 호출해 받은 값을 변수에 넣고 본문을 실행한다.'], ['③ StopIteration', '더 줄 값이 없으면 `__next__` 가 StopIteration 을 발생시키고, for 문은 이를 받아 반복을 종료한다.'])]),
outq('출력 결과는?', D('''
it = iter("PY")
a = next(it)
b = next(it, "?")
c = next(it, "?")
d = next(it, "!")
print(a + b + c + d)
'''), '문자열 "PY" 는 값이 2개예요. 세 번째부터는 다 꺼낸 상태라서 그때 준 기본값이 그대로 나와요.'),
order('`for x in data: print(x)` 와 **똑같이 동작하도록** 줄을 순서대로 놓으세요.', ['data = [3, 6, 9]', 'it = iter(data)', 'while True:', '    try:', '        x = next(it)', '    except StopIteration:', '        break', '    print(x)'], '`iter` 는 반복문 **밖에서 한 번**, `next` 는 try 안에서, StopIteration 을 받으면 break 예요.'),
essay('`for ch in "ABC": print(ch)` 가 실행될 때 파이썬이 내부에서 하는 일을 **호출 순서대로** 서술하고, `__next__` 가 모두 몇 번 호출되는지 쓰세요.', '먼저 for 문이 문자열 "ABC" 에 iter() 를 한 번 호출해(__iter__) 이터레이터를 얻는다. 그다음 반복할 때마다 이터레이터에 next() 를 호출해(__next__) 받은 값을 ch 에 넣고 본문을 실행한다. "A", "B", "C" 를 차례로 받은 뒤 네 번째 호출에서 더 줄 값이 없어 StopIteration 예외가 발생하고, for 문이 이 예외를 받아 오류 없이 반복을 끝낸다. 따라서 __next__ 는 모두 4번 호출된다.', ['iter(__iter__)가 처음에 한 번 호출된다고 썼다', '반복마다 next(__next__)가 호출된다고 썼다', 'StopIteration 이 발생하면 for 문이 반복을 끝낸다고 썼다', '__next__ 호출 횟수를 4번이라고 썼다']),
explain('이터러블 vs 이터레이터 — 한 번 쓰면 끝',
  [T('**이터러블**은 "for 로 돌 수 있는 것", **이터레이터**는 "next 로 하나씩 꺼내는 것"이에요. 리스트는 이터러블이지만 이터레이터는 아니에요. 둘을 가르는 가장 확실한 시험은 `iter(x) is x` 예요.'),
   C(D('''
nums = [1, 2, 3]
it = iter(nums)
print(iter(nums) is nums)
print(iter(it) is it)
print(list(it), list(it))
print(list(nums), list(nums))
'''), '이터레이터는 iter 를 해도 자기 자신'),
   key('리스트에 `iter()` 를 하면 **매번 새 이터레이터**가 나와서 몇 번이든 다시 돌 수 있어요. 이터레이터에 `iter()` 를 하면 **자기 자신**이 나와요. 그래서 한 번 다 꺼낸 이터레이터는 다시 돌려도 아무것도 안 나와요.')],
  [T('함정은 "리스트처럼 보이지만 이터레이터인 것들"이에요. `map`·`filter`·`zip`·`enumerate` 의 결과는 모두 이터레이터예요. (`range` 는 이터레이터가 **아니라** 다시 쓸 수 있는 이터러블이에요.)'),
   C(D('''
sq = map(lambda x: x * x, [1, 2, 3])
print(sum(sq))
print(sum(sq))
r = range(1, 4)
print(sum(r), sum(r))
pairs = zip("ab", [1, 2])
print(list(pairs), list(pairs))
'''), '두 번째로 쓰면 빈손'),
   warn('`sum(sq)` 를 한 번 하면 map 이터레이터가 **소진**돼요. 두 번째 `sum(sq)` 는 꺼낼 것이 없어서 0 이에요. 오류가 나지 않고 **조용히 빈 결과**가 나오기 때문에 출력 추론에서 가장 잘 틀려요. 여러 번 쓰려면 `list(map(...))` 로 리스트에 담아 두세요.')],
  [T('이터레이터 **하나를 여러 곳에서 같이 쓰면** 꺼낸 위치도 같이 움직여요. 앞의 for 가 break 로 나오면, 다음 for 는 처음이 아니라 **멈춘 다음 칸부터** 이어 가요.'),
   C(_shared, '세 개의 for 가 이터레이터 하나를 나눠 써요'),
   tip('첫 for 는 1, 2 를 꺼내고 멈췄어요. 둘째 for 가 3~6 을 모두 꺼내고, 셋째 for 는 꺼낼 것이 없어서 본문을 한 번도 실행하지 않아요. 원본 리스트 `nums` 는 그대로예요 — 소진되는 것은 **이터레이터**이지 리스트가 아니에요.')],
  [T('이 성질을 일부러 쓰는 기법도 있어요. `zip(it, it)` 은 **같은 이터레이터**에서 번갈아 꺼내므로 두 개씩 짝을 지어요.'),
   C(_zip2, '같은 이터레이터를 두 번 넣은 zip'),
   rev('"마" 는 어디로 갔을까요?', 'zip 은 세 번째 짝을 만들려고 첫 번째 자리의 값으로 "마" 를 **이미 꺼낸 뒤**, 두 번째 자리에서 StopIteration 을 만나 멈춰요. 꺼낸 "마" 는 버려지고 이터레이터는 비어 있어요. 그래서 마지막 줄은 기본값이 출력돼요.')]),
outq('출력 결과는?', D('''
words = ["sun", "moon", "star"]
lens = map(len, words)
big = [n for n in lens if n > 3]
total = sum(lens)
print(big, total, len(words))
'''), '리스트 컴프리헨션이 `lens` 를 끝까지 돌면서 소진했어요. 그 뒤의 `sum(lens)` 는 꺼낼 것이 없어서 0 이에요.'),
bucket('`iter(x) is x` 가 **True 인 것(이터레이터)** 과 False 인 것(다시 쓸 수 있는 이터러블)으로 나누세요.', ['이터레이터 (한 번 쓰면 끝)', '이터러블 (다시 쓸 수 있음)'], [['`[1, 2, 3]`', 2], ['`map(str, [1, 2])`', 1], ['`range(3)`', 2], ['`"ab"`', 2], ['`zip([1], [2])`', 1], ['`enumerate([1])`', 1], ['`iter([1, 2])`', 1], ['`{1: 2}`', 2]], 'map·zip·enumerate·filter 의 결과와 `iter()` 의 결과는 이터레이터예요. 리스트·문자열·range·딕셔너리는 iter 할 때마다 새 이터레이터를 주는 이터러블이에요.'),
outq('출력 결과는?', D('''
data = [5, 8, 2, 9, 4, 7]
it = iter(data)
first = next(it)
for x in it:
    if x > 8:
        break
rest = list(it)
print(first, x, rest, list(it))
'''), '`next` 로 5 를 꺼내고, for 는 8, 2, 9 까지 꺼낸 뒤 9 에서 break. 남은 4, 7 을 `list(it)` 가 가져가고, 그다음 `list(it)` 는 빈 리스트예요.'),
essay('아래 코드에서 **두 번째 for 문이 아무것도 출력하지 않는 이유**를 서술하고, 두 번 모두 출력되도록 고치는 방법을 쓰세요.\n\n```\nscores = map(int, ["70", "85", "90"])\nfor s in scores:\n    print(s)\nfor s in scores:\n    print(s + 5)\n```', 'map 의 결과는 리스트가 아니라 이터레이터이다. 이터레이터는 값을 한 번씩만 꺼낼 수 있고 iter() 를 호출해도 자기 자신을 돌려주므로, 첫 번째 for 문이 끝까지 돌면서 모두 소진된다. 두 번째 for 문이 next() 를 호출하면 바로 StopIteration 이 발생해 본문이 한 번도 실행되지 않는다. scores = list(map(int, [...])) 처럼 리스트로 바꿔 저장하면, 리스트는 for 문마다 새 이터레이터를 만들어 주므로 두 번 모두 출력된다.', ['map 의 결과가 이터레이터라고 썼다', '첫 번째 for 문에서 모두 소진되었다(한 번만 꺼낼 수 있다)고 썼다', '두 번째 for 에서는 바로 StopIteration 이 나서 본문이 실행되지 않는다고 썼다', 'list() 로 감싸 리스트로 저장하는 수정 방법을 썼다']),
explain('이터레이터 클래스 — __iter__ 와 __next__',
  [T('내 클래스를 for 문에 넣으려면 두 메서드를 만들어요. `__iter__` 는 이터레이터를 돌려주고(보통 `return self`), `__next__` 는 다음 값을 돌려주거나 끝났으면 `raise StopIteration` 을 해요. 호출 순서를 눈으로 보려고 print 를 넣어 봤어요.'),
   C(_order_cls, 'I = __iter__ 호출, N = __next__ 호출'),
   key('첫 for: I 한 번 → N 세 번(값 2, 1, 그리고 StopIteration). 둘째 for: I 한 번 → N 한 번(바로 StopIteration). `__iter__` 가 `self` 를 돌려주므로 **같은 객체가 그대로 이어져서**, n 이 이미 0 인 채로 다시 시작해요.')],
  [T('`__next__` 안의 줄 순서가 채점 포인트예요. **끝 검사 → 상태 갱신 → 값 반환** 순서를 지키세요.'),
   cmp('끝 검사가 먼저', 'def __next__(self):\n    if self.cur > self.end:\n        raise StopIteration\n    v = self.cur\n    self.cur += 1\n    return v', '끝 검사가 없으면', 'def __next__(self):\n    v = self.cur\n    self.cur += 1\n    return v', 'end 를 넘으면 for 가 멈춰요', 'StopIteration 이 영원히 안 나와서 for 문이 **무한 반복**'),
   warn('`return StopIteration` 이라고 쓰면 안 돼요. 그러면 예외가 아니라 **StopIteration 이라는 값**이 반환되어 for 문이 끝나지 않아요. 반드시 `raise` 예요. 또 `return v` 뒤에 `self.cur += 1` 을 쓰면 실행되지 않아요 — 갱신은 return **앞**에.')],
  [T('"두 번째 for 에서도 처음부터 다시 돌게 하려면?"이라는 수정 문제가 나올 수 있어요. 시작 위치를 `__iter__` 에서 다시 정해 주면 돼요.'),
   tabs(('한 번만 쓸 수 있음', '`__iter__` 가 아무것도 초기화하지 않아요. 한 번 끝나면 `cur` 가 끝에 머물러 있어요.', 'class Up:\n    def __init__(self, end):\n        self.end = end\n        self.cur = 1\n    def __iter__(self):\n        return self\n    def __next__(self):\n        if self.cur > self.end:\n            raise StopIteration\n        self.cur += 1\n        return self.cur - 1\nu = Up(3)\nprint(list(u), list(u))'),
        ('다시 쓸 수 있음', '`__iter__` 에서 `cur` 를 1 로 되돌려요. for 문은 시작할 때마다 `__iter__` 를 부르니까 매번 처음부터 돌아요.', 'class Up:\n    def __init__(self, end):\n        self.end = end\n        self.cur = 1\n    def __iter__(self):\n        self.cur = 1\n        return self\n    def __next__(self):\n        if self.cur > self.end:\n            raise StopIteration\n        self.cur += 1\n        return self.cur - 1\nu = Up(3)\nprint(list(u), list(u))'))]),
outq('출력 결과는? (I, N 은 호출될 때 찍히는 글자예요)', D('''
class Step:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __iter__(self):
        print("I", end="")
        return self
    def __next__(self):
        print("N", end="")
        if self.a > self.b:
            raise StopIteration
        self.a += 2
        return self.a - 2
s = Step(1, 5)
total = 0
for v in s:
    total += v
print()
print(total, s.a, next(s, -1))
'''), '값은 1, 3, 5 세 개라서 N 은 4번 찍혀요(마지막은 StopIteration). 끝난 뒤 a 는 7 이고, 마지막 줄의 `next(s, -1)` 이 N 을 한 번 더 찍은 다음 기본값 -1 을 돌려줘요. print 의 인자가 먼저 모두 계산되므로 N 이 숫자들보다 앞에 찍혀요.'),
fill('1부터 n 까지 **홀수만** 차례로 주는 이터레이터 클래스예요. 빈칸을 채우세요.', D('''
class Odd:
    def __init__(self, n):
        self.n = n
        self.cur = 1
    def ___(self):
        return self
    def ___(self):
        if self.cur > self.n:
            ___ StopIteration
        v = self.cur
        self.cur += ___
        return v
print(list(Odd(8)))
'''), ['__iter__', '__next__', 'raise', '2'], '`__iter__` 는 self 반환, `__next__` 는 끝 검사 후 `raise StopIteration`. 홀수만 주려면 2씩 늘려요.', expect='[1, 3, 5, 7]'),
spotv('`Seat` 는 끝 검사를 빠뜨린 이터레이터예요. **예외가 발생하는 줄**은?', _spot_next, 8, '세 번째 `next(s)` 에서 `self.i` 가 2 가 되어 `self.rows[2]` 가 **IndexError** 를 내요. for 문은 StopIteration 만 받아 주므로, for 에 넣어도 IndexError 로 프로그램이 멈춰요. 8번 줄 앞에 `if self.i >= len(self.rows): raise StopIteration` 이 필요해요.', name='IndexError'),
explain('값을 검사하는 이터레이터 — raise ValueError',
  [T('2025년에는 `__next__` 안에서 값을 **검사**해서 잘못된 값이면 `raise ValueError` 를 하는 이터레이터가 나왔어요. 핵심은 "for 문이 대신 받아 주는 예외는 **StopIteration 하나뿐**"이라는 점이에요. 다른 예외는 for 문 밖으로 그대로 튀어나와요.'),
   C(D('''
class Ages:
    def __init__(self, data):
        self.data = data
        self.i = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.i >= len(self.data):
            raise StopIteration
        v = self.data[self.i]
        self.i += 1
        if v < 0:
            raise ValueError(f"{v} 는 음수")
        return v
total = 0
try:
    for a in Ages([15, 16, -1, 17]):
        total += a
except ValueError as e:
    print("중단:", e)
print(total)
'''), 'try 가 for 문 전체를 감싸면 — 오류에서 반복이 끝나요'),
   key('`-1` 에서 ValueError 가 나면 for 문 전체가 중단되고 except 로 가요. 그래서 17 은 더해지지 않고 합계는 31 이에요. try 를 **어디에 두느냐**에 따라 "중단"과 "건너뛰고 계속"이 갈려요.')],
  [T('잘못된 값만 **건너뛰고 계속** 하려면 for 문을 쓸 수 없어요(for 는 예외가 나면 끝). `while True` 안에서 `next()` 를 직접 부르고 그 한 줄을 try 로 감싸요.'),
   C(_val_out, 'next 를 직접 부르면 — 건너뛰고 계속'),
   warn('`self.i += 1` 이 **raise 보다 앞**에 있는 것이 중요해요. 순서가 반대면 위치가 그대로라서, 다음 `next()` 가 같은 `-3` 을 또 만나 ValueError 가 끝없이 반복돼요.')],
  [T('정리하면 `__next__` 안에서 나갈 수 있는 길은 세 가지예요.'),
   flip(['`return 값`', 'for 문의 변수에 값이 들어가고 본문 실행'], ['`raise StopIteration`', 'for 문이 받아서 **조용히** 반복 종료'], ['`raise ValueError(...)`', 'for 문이 받지 않음 → try/except 가 없으면 프로그램이 오류로 멈춤'], ['`except ValueError as e` 의 `e`', 'raise 할 때 괄호 안에 넣은 메시지 — `print(e)` 로 출력'])]),
spotv('이 프로그램은 오류 메시지를 내며 멈춰요. **예외가 발생한(raise 된) 줄**은?', _spot_val, 13, '세 번째 값 -1 에서 13번 줄의 `raise ValueError` 가 실행돼요. for 문은 StopIteration 만 받아 주기 때문에 ValueError 는 그대로 밖으로 나가 프로그램이 멈추고, 마지막 `print(total)` 은 실행되지 않아요.', name='ValueError'),
outq('출력 결과는?', D('''
class Even:
    def __init__(self, data):
        self.data = data
        self.i = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.i == len(self.data):
            raise StopIteration
        v = self.data[self.i]
        self.i += 1
        if v % 2 == 1:
            raise ValueError("홀수")
        return v
it = Even([2, 4, 5, 6, 8])
got = []
try:
    for v in it:
        got.append(v)
except ValueError as e:
    got.append(str(e))
for v in it:
    got.append(v * 10)
print(got, next(it, "끝"))
'''), '첫 for 는 2, 4 를 넣고 5 에서 ValueError 로 중단돼요. 그때 `i` 는 이미 3 이라서, 같은 이터레이터로 도는 둘째 for 는 6, 8 부터 이어 가요.'),
essay('이터레이터에서 **StopIteration 예외의 역할**을 서술하고, `__next__` 안에서 `raise StopIteration` 대신 `raise ValueError("끝")` 을 쓰면 for 문에서 어떤 일이 생기는지 쓰세요.', 'StopIteration 은 이터레이터가 "더 이상 줄 값이 없다"는 것을 알리는 신호이다. for 문은 next() 를 반복 호출하다가 StopIteration 이 발생하면 이를 내부에서 처리해 오류 없이 반복을 끝낸다. for 문이 대신 처리해 주는 예외는 StopIteration 뿐이므로, ValueError 를 발생시키면 for 문이 받지 못하고 예외가 밖으로 전달되어, try/except 로 감싸지 않았다면 프로그램이 ValueError 오류로 중단된다.', ['StopIteration 이 "더 줄 값이 없음"을 알리는 신호라고 썼다', 'for 문이 StopIteration 을 받아 오류 없이 반복을 끝낸다고 썼다', 'ValueError 는 for 문이 처리하지 않는다고 썼다', 'try/except 가 없으면 프로그램이 오류로 중단된다고 썼다']),
prac('[기출유사] 사물함 번호 이터레이터', '새 학기 사물함 번호표를 만드는 이터레이터 클래스 `LockerIterator` 를 작성해요.\n\n- `__init__(self, zone, start, count)` : 구역 글자, 시작 번호, 개수. **count 가 1 미만이면** `raise ValueError("개수는 1 이상이어야 합니다")`\n- `__iter__` : 자기 자신을 반환\n- `__next__` : `구역-번호` 를 반환(번호는 **두 자리**, 예: `B-07`). count 개를 모두 주었으면 StopIteration\n\n입력: 한 줄에 `구역 시작번호 개수`\n\n출력\n1. 번호표를 한 줄에 하나씩\n2. `발급 N개`\n3. 같은 이터레이터로 한 번 더 for 문을 돌려 나온 개수를 `다시 돌리면 M개` 로 출력\n\n개수가 1 미만이면 `오류: 개수는 1 이상이어야 합니다` 한 줄만 출력해요.\n\n[조건] ○ 번호표는 **for 문**으로 꺼내요 ○ 오류 메시지는 `except ValueError as e` 의 `e` 를 출력',
D('''
class LockerIterator:
    def __init__(self, zone, start, count):
        if count < 1:
            raise ValueError("개수는 1 이상이어야 합니다")
        self.zone = zone
        self.cur = start
        self.left = count
    def __iter__(self):
        return self
    def __next__(self):
        if self.left == 0:
            raise StopIteration
        v = f"{self.zone}-{self.cur:02d}"
        self.cur += 1
        self.left -= 1
        return v
zone, start, count = input().split()
try:
    it = LockerIterator(zone, int(start), int(count))
    n = 0
    for tag in it:
        print(tag)
        n += 1
    print(f"발급 {n}개")
    m = 0
    for tag in it:
        m += 1
    print(f"다시 돌리면 {m}개")
except ValueError as e:
    print("오류:", e)
'''), ['B 7 4', 'A 1 0', 'C 98 3', 'K 10 1', 'Z 5 -2', 'M 1 6'],
  starter=D('''
class LockerIterator:
    def __init__(self, zone, start, count):
        # count 검사 후 저장
        pass
    # __iter__, __next__ 를 작성하세요

zone, start, count = input().split()
'''),
  hints=['`__init__` 의 첫 줄에서 `if count < 1: raise ValueError("...")`. 객체를 만드는 줄이 try 안에 있어야 받아 낼 수 있어요.', '`__next__` : 남은 개수가 0 이면 `raise StopIteration`, 아니면 값을 만들고 번호 +1, 남은 개수 -1.', '두 자리 번호는 `f"{self.zone}-{self.cur:02d}"`. 같은 이터레이터는 이미 소진돼서 두 번째 for 는 0개예요.'],
  ex='`__iter__` 가 self 를 반환하므로 두 번째 for 문은 이미 끝난 이터레이터를 다시 받아요. 그래서 항상 0개예요.'),
prac('[기출유사] for 없이 next 로 — 2인 1조 짝짓기', '이름이 공백으로 구분되어 한 줄로 주어져요. **앞에서부터 두 명씩** 짝을 지어 출력해요.\n\n출력\n- 한 줄에 한 조씩 `1조: 이름-이름`\n- 마지막에 한 명이 남으면 `K조: 이름-(혼자)`\n- 마지막 줄에 `총 K조`\n\n[조건] ○ **for 문을 쓰지 않아요** ○ `iter()` 로 이터레이터를 **하나만** 만들고 `while True` 안에서 `next()` 로 꺼내요 ○ 첫 번째 사람은 `try / except StopIteration` 으로, 두 번째 사람은 `next(it, 기본값)` 으로 꺼내요',
D('''
names = input().split()
it = iter(names)
k = 0
while True:
    try:
        a = next(it)
    except StopIteration:
        break
    b = next(it, "(혼자)")
    k += 1
    print(f"{k}조: {a}-{b}")
print(f"총 {k}조")
'''), ['민서 지호 하윤 도윤 서아', '가람 나래', '솔', '하나 두리 세찌 네찌 다섯 여섯', '봄 여름 가을', '일 이 삼 사 오 육 칠'],
  starter=D('''
names = input().split()
it = iter(names)
k = 0
while True:
    # next 로 두 명씩 꺼내세요
    break
print(f"총 {k}조")
'''),
  hints=['첫 사람은 `try: a = next(it)` / `except StopIteration: break` — 더 꺼낼 사람이 없으면 반복 종료.', '둘째 사람은 `b = next(it, "(혼자)")` — 없으면 기본값이 들어와요.', '`k += 1` 뒤에 `print(f"{k}조: {a}-{b}")`.'],
  ex='이터레이터 하나에서 `next` 를 두 번 부르면 자연스럽게 두 명씩 묶여요. for 문이 숨겨서 해 주던 일을 직접 쓴 것이에요.'),
prac('[심화] 점수 검사 이터레이터 — 건너뛰고 계속', '채점 기록이 공백으로 구분되어 한 줄로 주어져요. 숫자가 아닌 것, 범위를 벗어난 것이 섞여 있어요. 이터레이터 클래스 `ScoreIterator` 를 만들어 **잘못된 기록은 건너뛰고** 평균을 구해요.\n\n`__next__` 의 규칙 (이 순서로)\n1. 모두 꺼냈으면 StopIteration\n2. 현재 항목을 꺼내고 **위치를 한 칸 옮겨요**\n3. 정수로 바꿀 수 없으면 `raise ValueError("항목: 숫자 아님")`\n4. 0~100 을 벗어나면 `raise ValueError("항목: 범위 오류")`\n5. 정상이면 정수를 반환\n\n출력\n- 잘못된 기록마다 `건너뜀 - 항목: 이유`\n- `유효 N개, 평균 A` (평균은 소수 첫째 자리까지). 유효한 점수가 없으면 `유효한 점수 없음`\n\n[조건] ○ `while True` 안에서 `next()` 를 호출하고 **ValueError 와 StopIteration 을 각각의 except** 로 처리 ○ 메시지는 `e` 를 그대로 출력',
D('''
class ScoreIterator:
    def __init__(self, items):
        self.items = items
        self.i = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.i >= len(self.items):
            raise StopIteration
        s = self.items[self.i]
        self.i += 1
        try:
            v = int(s)
        except ValueError:
            raise ValueError(f"{s}: 숫자 아님")
        if v < 0 or v > 100:
            raise ValueError(f"{s}: 범위 오류")
        return v
it = ScoreIterator(input().split())
total = 0
n = 0
while True:
    try:
        v = next(it)
    except ValueError as e:
        print("건너뜀 -", e)
    except StopIteration:
        break
    else:
        total += v
        n += 1
if n == 0:
    print("유효한 점수 없음")
else:
    print(f"유효 {n}개, 평균 {total / n:.1f}")
'''), ['80 구십 95 120 70', 'abc -5 101', '100 0 50', '77', '3.5 60 x 61 -1 62', '100 100 1000 백 99'],
  starter=D('''
class ScoreIterator:
    def __init__(self, items):
        self.items = items
        self.i = 0
    def __iter__(self):
        return self
    def __next__(self):
        pass  # 규칙 1~5 를 순서대로

it = ScoreIterator(input().split())
'''),
  hints=['위치를 옮기는 `self.i += 1` 은 **검사보다 앞**에 둬요. 그래야 오류가 난 뒤의 next 가 다음 항목으로 가요.', '`int(s)` 를 try 로 감싸고 `except ValueError: raise ValueError(f"{s}: 숫자 아님")` 으로 메시지를 바꿔 다시 던져요.', '메인: `try: v = next(it)` / `except ValueError as e: print("건너뜀 -", e)` / `except StopIteration: break` / `else:` 에서 누적.'],
  ex='for 문은 ValueError 가 나는 순간 끝나 버려요. "건너뛰고 계속"은 next 를 직접 부르고 그 한 줄을 try 로 감싸야 가능해요. `"3.5"` 는 `int()` 로 바꿀 수 없어서 "숫자 아님"이에요.'),
)

# ============================================================ D5
_flow = D('''
def gen():
    print("A", end=" ")
    yield 1
    print("B", end=" ")
    yield 2
    print("C", end=" ")
g = gen()
print("시작", end=" ")
print(next(g), end=" ")
print(next(g), end=" ")
print(next(g, "끝"))
''')
_lazy = D('''
def sq(x):
    print("계산", x, end=" / ")
    return x * x
lst = [sq(x) for x in range(3)]
print("리스트 완성")
gen = (sq(x) for x in range(3))
print("제너레이터 완성")
print(next(gen))
print(next(gen))
''')
_len_err = D('''
nums = [3, 1, 4, 1, 5]
big = (n for n in nums if n > 2)
total = sum(big)
print(total)
count = len(big)
print(count)
''')
_idx_err = D('''
names = ["kim", "lee", "park"]
upper = (n.upper() for n in names)
first = next(upper)
print(first)
second = upper[0]
print(second)
''')
assert err(_idx_err) == 'TypeError'
same("import sys\nn = 100000\nprint(sys.getsizeof([x for x in range(n)]) > sys.getsizeof((x for x in range(n))))\nprint(sys.getsizeof((x for x in range(10))) == sys.getsizeof((x for x in range(n))))", 'True\nTrue')

D5 = lesson('5강. 제너레이터 심화 — yield 와 메모리', 50,
'- 제너레이터 함수는 **호출해도 실행되지 않는다** — `next()` 를 할 때마다 다음 `yield` 까지 실행하고 멈춘다\n- 함수가 끝나거나 `return` 을 만나면 StopIteration → for 문 종료\n- 이터레이터 클래스 = 제너레이터 함수 = 제너레이터 표현식: 같은 일을 점점 짧게\n- 리스트 컴프 `[ ]` 는 **모든 값을 한꺼번에 만들어 저장**, 제너레이터 표현식 `( )` 는 **필요할 때 하나씩** 만든다 → 메모리 절약\n- 제너레이터는 `len()`·인덱싱·슬라이싱 불가, **한 번 쓰면 끝**\n- 무한 제너레이터는 `while True` + `yield`, 받는 쪽에서 `break` 로 끊는다',
review('🔁 4강 복습', [T('이터레이터의 약속을 다시 확인해요. 제너레이터는 이 약속을 **자동으로 만들어 주는 도구**예요.'), flip(['for 문이 처음에 한 번 부르는 것', '`iter()` → `__iter__`'], ['값이 3개일 때 `__next__` 호출 횟수', '4번 — 마지막은 StopIteration'], ['`iter(it) is it` 가 True 이면', '이터레이터 — 한 번 쓰면 끝'], ['for 문이 대신 받아 주는 예외', 'StopIteration **하나뿐**'])]),
outq('복습 — 출력 결과는?', D('''
class Twice:
    def __init__(self, data):
        self.data = data
        self.i = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.i >= len(self.data):
            raise StopIteration
        self.i += 1
        return self.data[self.i - 1] * 2
t = Twice([1, 2, 3])
a = next(t)
b = [x for x in t]
c = [x for x in t]
print(a, b, c)
'''), '`next` 가 첫 값을 꺼내고, 첫 번째 컴프리헨션이 나머지를 모두 꺼내요. 같은 이터레이터라서 두 번째 컴프리헨션은 빈 리스트예요.', review=True),
explain('yield — 멈췄다가 이어 가는 함수',
  [T('함수 안에 `yield` 가 **하나라도** 있으면 그 함수는 제너레이터 함수예요. 가장 많이 틀리는 사실: 제너레이터 함수를 **호출해도 본문은 한 줄도 실행되지 않아요.** 제너레이터 객체가 만들어질 뿐이에요.'),
   C(_flow, '"시작" 이 "A" 보다 먼저 찍혀요'),
   key('`g = gen()` 에서는 아무것도 출력되지 않아요. 첫 `next(g)` 가 처음부터 `yield 1` 까지 실행하고(A 출력) **멈춰요.** 두 번째 `next(g)` 는 멈춘 자리 **다음 줄부터** `yield 2` 까지(B 출력). 세 번째는 C 를 출력하고 함수가 끝나서 StopIteration → 기본값 "끝".')],
  [T('출력 추론은 "next 한 번 = 다음 yield 까지"를 기계적으로 따라가면 돼요.'),
   steps(['g = gen()', '제너레이터 객체만 생김. 본문 실행 **없음**.'], ['첫 번째 next(g)', '함수 처음 ~ 첫 `yield` 까지 실행. yield 옆의 값을 돌려주고 그 자리에서 멈춤.'], ['그다음 next(g)', '멈춘 `yield` **다음 줄**부터 다음 `yield` 까지. 지역 변수는 그대로 남아 있음.'], ['함수 끝 또는 return', 'StopIteration 발생 → for 문이면 조용히 종료, `next(g, 기본값)` 이면 기본값.']),
   warn('`yield` **뒤에 있는 코드**는 그 값을 받은 순간이 아니라 **다음 next 때** 실행돼요. for 문으로 돌리면 "본문 실행 → 다음 next → yield 뒤 코드" 순서로 섞여서 출력돼요.')],
  [T('제너레이터 함수 안의 `return` 은 "값을 돌려준다"가 아니라 "**여기서 끝낸다**"는 뜻이에요. return 을 만나면 그 아래 yield 는 실행되지 않고 StopIteration 이 나요.'),
   C(D('''
def until_zero(data):
    for x in data:
        if x == 0:
            return
        yield x
    print("0 없이 끝")
print(list(until_zero([3, 5, 0, 7])))
print(list(until_zero([3, 5])))
'''), 'return 을 만나면 제너레이터가 끝나요'),
   tip('제너레이터도 이터레이터예요. `iter(g) is g` 가 True 이고, 한 번 다 쓰면 다시 쓸 수 없어요. 다시 쓰려면 제너레이터 **함수를 다시 호출**해 새 객체를 만들어요.')]),
outq('출력 결과는?', D('''
def steps():
    print("준비")
    yield "하나"
    print("진행")
    yield "둘"
    print("마무리")
for s in steps():
    print("받음:", s)
print("끝")
'''), '"받음: 하나" 를 출력한 뒤 for 문이 다음 값을 달라고 할 때 비로소 "진행" 이 찍혀요. "마무리" 는 세 번째 next 에서 찍히고, 함수가 끝나 StopIteration → for 종료.'),
outq('출력 결과는?', D('''
def counter(n):
    i = 0
    while i < n:
        yield i
        i += 2
g = counter(7)
h = counter(7)
print(next(g), next(g), next(h))
print(list(g), list(h), list(g))
'''), '`g` 와 `h` 는 서로 다른 제너레이터 객체라서 각자 자기 `i` 를 가져요. g 는 0, 2 를 꺼낸 뒤 4, 6 이 남고, h 는 0 을 꺼낸 뒤 2, 4, 6 이 남아요. 마지막 `list(g)` 는 이미 소진되어 빈 리스트예요.'),
order('1부터 시작해 **합이 limit 를 넘기 전까지**의 누적 합을 차례로 주는 제너레이터와 그 사용 코드예요. 순서대로 놓으세요.', ['def running(limit):', '    total = 0', '    n = 1', '    while total + n <= limit:', '        total += n', '        yield total', '        n += 1', 'print(list(running(12)))'], '`yield total` 로 값을 내보낸 뒤, 다음 next 때 `n += 1` 부터 이어 가요. 결과는 [1, 3, 6, 10] 이에요.'),
explain('세 가지 모양 — 클래스 ↔ 제너레이터 함수 ↔ 제너레이터 표현식',
  [T('2025년 시험은 **이터레이터 클래스를 제너레이터로 바꿔 쓰는** 문제를 냈어요. 같은 일을 세 가지로 쓸 수 있어야 해요. "start 부터 end 까지의 수를 제곱해서 하나씩 준다"를 세 모양으로 봐요.'),
   tabs(('① 이터레이터 클래스', '상태(`cur`)를 직접 저장하고, 끝 검사와 `raise StopIteration` 도 직접 써요.', 'class Squares:\n    def __init__(self, start, end):\n        self.cur = start\n        self.end = end\n    def __iter__(self):\n        return self\n    def __next__(self):\n        if self.cur > self.end:\n            raise StopIteration\n        v = self.cur ** 2\n        self.cur += 1\n        return v\nprint(list(Squares(1, 4)))'),
        ('② 제너레이터 함수', '`return v` 자리에 `yield`. 상태는 지역 변수가 기억하고, 함수가 끝나면 StopIteration 이 **자동**으로 나요.', 'def squares(start, end):\n    cur = start\n    while cur <= end:\n        yield cur ** 2\n        cur += 1\nprint(list(squares(1, 4)))'),
        ('③ 제너레이터 표현식', '리스트 컴프리헨션의 `[ ]` 를 `( )` 로. 한 줄로 끝나요.', 'g = (x ** 2 for x in range(1, 5))\nprint(list(g))')),
   key('클래스의 `__init__` → 함수의 매개변수·지역 변수, `__next__` 의 끝 검사 → `while` 조건, `return 값` → `yield 값`, `raise StopIteration` → 쓰지 않음(함수가 끝나면 자동).')],
  [T('검사해서 `raise ValueError` 를 하는 이터레이터도 제너레이터 함수로 옮길 수 있어요. 다만 차이가 하나 있어요.'),
   C(D('''
def ages(data):
    for v in data:
        if v < 0:
            raise ValueError(f"{v} 는 음수")
        yield v
g = ages([15, -3, 16])
print(next(g))
try:
    print(next(g))
except ValueError as e:
    print("오류:", e)
print(next(g, "이미 끝남"))
'''), '제너레이터 안에서 예외가 나면 그 제너레이터는 끝나요'),
   warn('이터레이터 **클래스**는 예외를 낸 뒤에도 `next` 를 다시 부르면 다음 값으로 이어 갈 수 있었어요(4강). **제너레이터**는 안에서 예외가 밖으로 나가는 순간 끝나 버려서, 그 뒤의 next 는 StopIteration 이에요. "건너뛰고 계속"을 원하면 제너레이터 안에서 `continue` 로 걸러야 해요.')],
  [T('표현식으로 바꿀 때는 괄호만 바꾸면 돼요. 함수의 인자로 **단독으로** 넣을 때는 괄호를 한 겹 생략할 수 있어요.'),
   cmp('리스트를 만들어 넘김', 'total = sum([x * x for x in data])', '제너레이터 표현식을 넘김', 'total = sum(x * x for x in data)', '제곱 리스트 전체가 메모리에 만들어진 뒤 합산', '제곱을 하나 만들 때마다 바로 더하고 버림', tones=('bad', 'good'))]),
fill('아래 이터레이터 클래스와 **같은 값**을 주는 제너레이터 함수예요. 빈칸을 채우세요.\n\n```\nclass Evens:\n    def __init__(self, n):\n        self.cur = 2\n        self.n = n\n    def __iter__(self):\n        return self\n    def __next__(self):\n        if self.cur > self.n:\n            raise StopIteration\n        v = self.cur\n        self.cur += 2\n        return v\n```', D('''
def evens(n):
    cur = ___
    while cur ___ n:
        ___ cur
        cur += 2
print(list(evens(9)))
'''), ['2', '<=', 'yield'], '끝 검사 `cur > n` 이면 종료 → 계속하는 조건은 그 반대인 `cur <= n`. `return v` 자리가 `yield cur` 예요.', expect='[2, 4, 6, 8]'),
ch('`def squares(n):` 안에서 `for i in range(n): yield i * i` 를 하는 제너레이터 함수와 **같은 값을 주는 제너레이터 표현식**은? (n = 5)', ['`[i * i for i in range(5)]`', '`(i * i for i in range(5))`', '`{i * i for i in range(5)}`', '`yield (i * i for i in range(5))`'], 2, '①은 리스트 컴프리헨션(값을 한꺼번에 만듦), ③은 집합 컴프리헨션이에요. 제너레이터 표현식은 **소괄호**예요. ④의 yield 는 함수 밖에서 쓸 수 없어요.'),
match('이터레이터 클래스의 각 부분이 제너레이터 함수에서는 무엇이 되는지 이으세요.', [['`self.cur = start` (상태 저장)', '지역 변수 `cur = start`'], ['`return v` (값 주기)', '`yield v`'], ['`raise StopIteration`', '함수가 끝나면 자동 발생'], ['`__iter__` 의 `return self`', '쓸 필요 없음 (자동 제공)']], '제너레이터는 `__iter__`·`__next__`·StopIteration 을 파이썬이 대신 만들어 줘요.'),
explain('리스트 컴프 vs 제너레이터 표현식 — 지연 평가와 메모리',
  [T('2024년 서술형(8점): "리스트 컴프리헨션과 제너레이터 표현식의 **메모리 사용 차이**를 서술하라." 답의 핵심은 **"한꺼번에 저장" 대 "필요할 때 하나씩"** 이에요. 먼저 눈으로 확인해요.'),
   C(_lazy, '리스트는 만드는 순간 전부 계산, 제너레이터는 next 때 계산'),
   key('리스트 컴프리헨션은 그 줄이 실행되는 순간 `sq` 를 3번 모두 불러 결과를 저장해요. 제너레이터 표현식은 그 줄에서 **한 번도 계산하지 않고**, `next` 를 부를 때마다 하나씩 계산해요. 이것을 **지연 평가**(lazy evaluation)라고 해요.')],
  [T('그래서 메모리가 달라요. 리스트는 원소 개수만큼 커지지만, 제너레이터는 "지금 어디까지 했는지"만 기억하면 되므로 원소가 10개든 100만 개든 **크기가 같아요.**'),
   C(D('''
import sys
n = 100000
lst = [x * x for x in range(n)]
gen = (x * x for x in range(n))
small = (x * x for x in range(10))
print(sys.getsizeof(lst) > sys.getsizeof(gen))
print(sys.getsizeof(gen) == sys.getsizeof(small))
print(sum(lst) == sum(gen))
'''), '크기는 다르고, 합은 같아요'),
   exam('서술 답안 틀: "리스트 컴프리헨션은 **모든 원소를 미리 만들어 메모리에 저장**하므로 원소 수에 비례해 메모리를 쓴다. 제너레이터 표현식은 값을 저장하지 않고 **요청(next)될 때마다 하나씩 만들어** 내보내므로 원소 수와 관계없이 메모리를 적게 쓴다." — 두 문장에 **저장 / 하나씩 / 메모리** 세 낱말이 들어가면 돼요.')],
  [T('대신 제너레이터는 "저장하지 않기 때문에" 못 하는 일이 있어요. 표현식으로 바꿔 쓰라는 문제에서 **바꾸면 안 되는 코드**를 가려내야 해요.'),
   flip(['`len(gen)`', 'TypeError — 다 만들어 보기 전에는 개수를 모른다'], ['`gen[0]`, `gen[1:3]`', 'TypeError — 저장된 칸이 없어 인덱싱·슬라이싱 불가'], ['두 번 돌기', '두 번째는 빈손 — 한 번 쓰면 끝'], ['`print(gen)`', '값이 아니라 `<generator object ...>` 가 출력된다'], ['`x in gen`', '되지만 찾을 때까지 **꺼내 버린다** — 그 뒤엔 남은 것만 있다'], ['`sum`, `max`, `min`, `sorted`, `list`, for', '모두 가능 — 하나씩 꺼내 쓰는 도구들']),
   tip('바꿔도 되는 경우: 결과를 **한 번만 차례로** 쓸 때(합계, 최댓값, 파일에 한 줄씩 쓰기, for 로 한 번 돌기). 바꾸면 안 되는 경우: 개수를 세거나, 인덱스로 꺼내거나, 여러 번 쓸 때.')],
  [T('`__name__` 과 함께 나온 2024년 형태처럼, 큰 데이터를 다루는 코드에서 이 차이가 실제로 중요해져요.'),
   cmp('리스트 컴프리헨션', 'squares = [x * x for x in range(10**7)]\nprint(sum(squares))', '제너레이터 표현식', 'squares = (x * x for x in range(10**7))\nprint(sum(squares))', '1000만 개의 제곱을 전부 메모리에 올린 뒤 더해요', '제곱을 하나 만들 때마다 더하고 버려요 — 결과는 같아요', tones=('bad', 'good'))]),
outq('출력 결과는?', D('''
def tag(x):
    print(x, end="")
    return x * 10
a = [tag(x) for x in "12"]
print("|", end="")
b = (tag(x) for x in "34")
print("|", end="")
c = list(b)
print("|")
print(a, c)
'''), '리스트 컴프는 만드는 줄에서 바로 `tag` 를 불러 "12" 가 찍혀요. 제너레이터 표현식 줄에서는 아무것도 안 찍히고, `list(b)` 를 할 때 "34" 가 찍혀요. 문자열 * 10 은 10번 반복이에요.'),
outq('출력 결과는?', D('''
nums = [4, 7, 1, 8]
gen = (n * 2 for n in nums)
print(max(gen))
print(sum(gen))
print(16 in (n * 2 for n in nums), sum(n * 2 for n in nums))
'''), '`max(gen)` 이 끝까지 꺼내서 gen 은 소진돼요. 그래서 `sum(gen)` 은 0. 셋째 줄은 **새 제너레이터**를 만들었으므로 정상이에요.'),
spotv('리스트 컴프리헨션을 제너레이터 표현식으로 바꿨더니 오류가 나요. **예외가 발생하는 줄**은?', _len_err, 5, '제너레이터는 값을 저장하지 않아서 `len()` 을 쓸 수 없어요(TypeError). 개수가 필요하면 리스트 컴프리헨션을 그대로 쓰거나 `sum(1 for n in nums if n > 2)` 로 세요.', name='TypeError'),
bucket('`data = (x for x in range(5))` 로 만든 **제너레이터**에 대해, 오류 없이 되는 것과 TypeError 가 나는 것으로 나누세요.', ['가능', 'TypeError'], [['`sum(data)`', 1], ['`len(data)`', 2], ['`data[0]`', 2], ['`list(data)`', 1], ['`next(data)`', 1], ['`data[1:3]`', 2], ['`sorted(data)`', 1], ['`for x in data:`', 1]], '하나씩 꺼내 쓰는 것은 모두 가능해요. 개수(len)와 위치(인덱싱·슬라이싱)는 저장된 칸이 있어야 해서 불가능해요.'),
essay('아래 두 코드의 결과는 같아요. **(가)와 (나)의 차이를 메모리 사용과 연결하여** 서술하세요.\n\n```\n(가) total = sum([len(line) for line in lines])\n(나) total = sum(len(line) for line in lines)\n```', '(가)는 리스트 컴프리헨션으로, 모든 줄의 길이를 먼저 전부 계산해 리스트로 메모리에 저장한 뒤 sum 이 더한다. 따라서 줄 수에 비례해 메모리를 사용한다. (나)는 제너레이터 표현식으로, 값을 미리 만들어 저장하지 않고 sum 이 값을 요청할 때마다 하나씩 계산해 넘겨주고 버린다(지연 평가). 따라서 줄 수가 아무리 많아도 메모리를 거의 일정하게 적게 사용한다. 데이터가 클수록 (나)가 메모리 면에서 유리하다.', ['(가)는 모든 값을 미리 만들어 리스트로 저장한다고 썼다', '(나)는 필요할 때 하나씩 만든다(지연 평가)고 썼다', '(가)는 원소 수에 비례해 메모리를 쓰고 (나)는 적게 쓴다고 비교했다', '(가)가 리스트 컴프리헨션, (나)가 제너레이터 표현식임을 밝혔다']),
essay('아래 코드의 `[ ]` 를 `( )` 로 바꿔 제너레이터 표현식으로 만들면 **정상 동작하는 줄과 문제가 생기는 줄**이 있어요. 각각 무엇인지, 이유와 함께 서술하세요.\n\n```\n1  evens = [n for n in nums if n % 2 == 0]\n2  print(sum(evens))\n3  print(len(evens))\n4  print(evens[0])\n```', '2번 줄의 sum 은 값을 하나씩 꺼내 더하므로 제너레이터로 바꿔도 정상 동작한다. 3번 줄은 문제가 생긴다. 제너레이터는 값을 저장하지 않아 개수를 알 수 없으므로 len() 에서 TypeError 가 발생한다. 4번 줄도 저장된 칸이 없어 인덱싱을 할 수 없으므로 TypeError 가 발생한다. 또한 제너레이터는 한 번 쓰면 소진되므로, 2번 줄에서 sum 으로 모두 꺼낸 뒤에는 더 꺼낼 값이 남아 있지 않다. 개수·인덱스가 필요하거나 여러 번 사용할 때는 리스트를 써야 한다.', ['sum 은 정상 동작한다고 썼다', 'len 에서 오류(TypeError)가 난다고 이유와 함께 썼다', '인덱싱에서 오류(TypeError)가 난다고 이유와 함께 썼다', '한 번 쓰면 소진된다는 점을 썼다']),
explain('무한 제너레이터와 any · sum',
  [T('"필요할 때 하나씩"이기 때문에 제너레이터는 **끝이 없는 수열**도 만들 수 있어요. `while True` 안에 `yield` 를 두고, **받는 쪽**이 필요한 만큼만 꺼낸 뒤 `break` 해요. 리스트로는 불가능한 일이에요.'),
   C(D('''
def multiples(k):
    n = k
    while True:
        yield n
        n += k
for m in multiples(7):
    if m > 30:
        break
    print(m, end=" ")
print()
g = multiples(5)
print([next(g) for _ in range(4)], next(g))
'''), '무한 제너레이터 — 멈추는 책임은 받는 쪽에'),
   warn('무한 제너레이터에 `list()`·`sum()`·`max()` 를 쓰면 영원히 끝나지 않아요. 반드시 `break` 가 있는 for 문이나, 횟수가 정해진 `next()` 로 꺼내요.')],
  [T('`any()` 와 `all()` 은 답이 정해지는 순간 **더 꺼내지 않고 멈춰요.** 제너레이터와 함께 쓰면 "어디까지 꺼냈는지"가 출력 추론 포인트가 돼요.'),
   C(D('''
nums = [3, 8, 5, 12, 7]
g = (n for n in nums)
print(any(n > 6 for n in nums))
print(any(n > 6 for n in g))
print(list(g))
h = (n for n in nums)
print(all(n < 6 for n in h), list(h))
'''), 'any 는 처음 True 를 만나면, all 은 처음 False 를 만나면 멈춰요'),
   rev('왜 `list(g)` 가 [5, 12, 7] 일까요?', '`any` 가 g 에서 3 (False), 8 (True) 까지 꺼내고 멈췄어요. 꺼낸 값은 돌아오지 않으니 g 에는 5, 12, 7 만 남아요. `all` 도 3 (True), 8 (False) 까지 꺼내고 멈춰서 같은 값이 남아요.')]),
outq('출력 결과는?', D('''
def naturals():
    n = 1
    while True:
        yield n
        n += 1
g = naturals()
picked = []
for n in g:
    if n % 3 == 0:
        picked.append(n)
    if len(picked) == 3:
        break
print(picked, next(g), next(g))
'''), '3, 6, 9 를 모으고 9 에서 break 해요. 제너레이터는 9 다음에서 멈춰 있으므로 이어지는 next 는 10, 11 이에요.'),
prac('[기출유사] 번호표 제너레이터 — 금지 숫자 건너뛰기', '은행 번호표는 1번부터 차례로 나오는데, 어떤 숫자 `d` 가 **들어 있는** 번호는 건너뛰어요(예: d 가 4 이면 4, 14, 24, 40~49 … 를 건너뜀).\n\n끝없이 번호를 주는 제너레이터 함수 `tickets(d)` 를 만들고, 앞에서부터 `n` 개를 뽑아요.\n\n입력: 한 줄에 `n d` (1 ≤ n ≤ 200, d 는 0~9)\n\n출력\n1. 뽑은 번호 n 개를 공백으로 구분해 한 줄에\n2. `마지막 번호: L`\n3. `건너뛴 번호: S개` (1 부터 L 사이에서 건너뛴 개수)\n4. `다음 번호: X` (같은 제너레이터에서 하나 더 꺼낸 값)\n\n[조건] ○ `tickets` 는 `while True` 와 `yield` 를 쓰는 **무한 제너레이터** ○ 번호는 `next()` 또는 break 가 있는 for 문으로 꺼내요',
D('''
def tickets(d):
    n = 1
    while True:
        if str(d) not in str(n):
            yield n
        n += 1
n, d = map(int, input().split())
g = tickets(d)
got = [next(g) for _ in range(n)]
print(*got)
last = got[-1]
print(f"마지막 번호: {last}")
print(f"건너뛴 번호: {last - n}개")
print(f"다음 번호: {next(g)}")
'''), ['10 4', '5 1', '1 1', '20 3', '12 0', '40 9', '3 7'],
  starter=D('''
def tickets(d):
    n = 1
    # while True 안에서, d 가 들어 있지 않은 번호만 yield 하세요

n, d = map(int, input().split())
g = tickets(d)
'''),
  hints=['"d 가 들어 있다"는 문자열로 검사해요: `str(d) in str(n)`.', '`got = [next(g) for _ in range(n)]` 으로 n 개만 꺼내요. 무한 제너레이터에 `list(g)` 는 금물!', '건너뛴 개수 = 마지막 번호 - n. 다음 번호는 **같은 g** 에 `next(g)` 를 한 번 더.'],
  ex='제너레이터는 멈춘 자리를 기억하므로, n 개를 뽑은 뒤 `next(g)` 를 한 번 더 하면 자연스럽게 다음 번호가 나와요.'),
prac('[기출유사] 콜라츠 수열 — 클래스를 제너레이터로', '아래 이터레이터 클래스는 콜라츠 수열(짝수면 2 로 나누고, 홀수면 3 을 곱해 1 을 더하기를 1 이 될 때까지 반복)을 만들어요. 이것과 **같은 값을 주는 제너레이터 함수** `collatz(n)` 으로 바꿔 쓰세요.\n\n```\nclass Collatz:\n    def __init__(self, n):\n        self.n = n\n        self.done = False\n    def __iter__(self):\n        return self\n    def __next__(self):\n        if self.done:\n            raise StopIteration\n        v = self.n\n        if v == 1:\n            self.done = True\n        elif v % 2 == 0:\n            self.n = v // 2\n        else:\n            self.n = 3 * v + 1\n        return v\n```\n\n입력: 양의 정수 n (1 ≤ n ≤ 1000)\n\n출력\n1. 수열을 공백으로 구분해 한 줄에 (n 부터 1 까지)\n2. `길이: K`\n3. `최댓값: M`\n4. `짝수 개수: E`\n\n[조건] ○ 클래스를 쓰지 않고 `yield` 를 쓰는 제너레이터 함수로 ○ 길이는 `len()` 없이 **제너레이터 표현식과 sum** 으로, 최댓값은 `max(collatz(n))` 으로 구해요(리스트를 만들지 않아요)',
D('''
def collatz(n):
    while n != 1:
        yield n
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
    yield 1
n = int(input())
print(*collatz(n))
print(f"길이: {sum(1 for _ in collatz(n))}")
print(f"최댓값: {max(collatz(n))}")
print(f"짝수 개수: {sum(1 for v in collatz(n) if v % 2 == 0)}")
'''), ['6', '1', '27', '8', '7', '97', '1000'],
  starter=D('''
def collatz(n):
    pass  # yield 로 n 부터 1 까지

n = int(input())
'''),
  hints=['`while n != 1:` 안에서 `yield n` 을 먼저 하고 n 을 바꿔요. 반복이 끝난 뒤 `yield 1` 을 한 번 더.', '제너레이터는 한 번 쓰면 끝이라서, 줄마다 `collatz(n)` 을 **새로 호출**해요.', '개수 세기: `sum(1 for _ in collatz(n))`. 짝수만: 뒤에 `if v % 2 == 0`.'],
  ex='클래스의 `self.n`·`self.done` 이 지역 변수와 while 조건으로 바뀌고, `raise StopIteration` 은 사라졌어요. 제너레이터는 `len()` 이 안 되므로 `sum(1 for ...)` 으로 세요.'),
prac('[심화] 연속 구간 제너레이터', '문자열에서 **같은 글자가 연속으로 이어진 구간**을 `(글자, 길이)` 로 하나씩 주는 제너레이터 함수 `runs(s)` 를 만들어요. 예: `"aaabccdd"` → `("a", 3)`, `("b", 1)`, `("c", 2)`, `("d", 2)`.\n\n입력: 공백 없는 문자열 한 줄 (길이 1 이상)\n\n출력\n1. 압축 결과: 구간마다 `글자길이` 를 공백으로 구분 (예: `a3 b1 c2 d2`)\n2. `구간 수: K`\n3. `가장 긴 구간: 글자 x 길이` (길이가 같으면 **먼저 나온** 구간)\n4. `길이 2 이상인 첫 구간: 글자` — 없으면 `길이 2 이상인 첫 구간: 없음`\n\n[조건] ○ `runs` 는 리스트를 만들어 반환하지 않고 **yield** 로 하나씩 ○ 4번은 제너레이터 표현식과 `next(…, 기본값)` 으로 구해요',
D('''
def runs(s):
    cur = s[0]
    n = 1
    for ch in s[1:]:
        if ch == cur:
            n += 1
        else:
            yield (cur, n)
            cur = ch
            n = 1
    yield (cur, n)
s = input()
print(*(f"{c}{n}" for c, n in runs(s)))
print(f"구간 수: {sum(1 for _ in runs(s))}")
best = None
for c, n in runs(s):
    if best is None or n > best[1]:
        best = (c, n)
print(f"가장 긴 구간: {best[0]} x {best[1]}")
first = next((c for c, n in runs(s) if n >= 2), "없음")
print(f"길이 2 이상인 첫 구간: {first}")
'''), ['aaabccdd', 'abc', 'zzzz', 'aabbbaabbb', 'x', '1100011110', 'abccbaa'],
  starter=D('''
def runs(s):
    cur = s[0]
    n = 1
    # 글자가 바뀔 때마다 (cur, n) 을 yield

s = input()
'''),
  hints=['글자가 바뀌는 순간 `yield (cur, n)` 을 하고 `cur`, `n` 을 새로 시작해요. **반복이 끝난 뒤 마지막 구간**도 yield 해야 해요.', '가장 긴 구간은 for 로 돌며 `n > best[1]` 일 때만 바꿔요(같으면 먼저 나온 것 유지).', '`next((c for c, n in runs(s) if n >= 2), "없음")` — 제너레이터 표현식을 next 의 인자로 넣을 때는 괄호가 필요해요.'],
  ex='`next(제너레이터 표현식, 기본값)` 은 조건에 맞는 **첫 번째** 값만 계산하고 멈춰요. 뒤쪽 구간은 만들지도 않아요 — 지연 평가의 이점이에요.'),
)

# ============================================================ D6
_ube = D('''
def make_counter():
    count = 0
    def inc():
        count += 1
        return count
    return inc
c = make_counter()
print(c())
''')
_late = D('''
fs = []
for i in range(3):
    fs.append(lambda x: x + i)
print(fs[0](10), fs[1](10), fs[2](10))
gs = []
for i in range(3):
    gs.append(lambda x, i=i: x + i)
print(gs[0](10), gs[1](10), gs[2](10))
''')
_avg = D('''
def make_averager():
    total = 0
    count = 0
    def add(x):
        nonlocal total, count
        total += x
        count += 1
        return total / count
    return add
avg = make_averager()
print(avg(80))
print(avg(90))
print(avg(100))
''')
_spot_nl = D('''
def make_bank(balance):
    log = []
    def deposit(x):
        log.append(x)
        balance = balance + x
        return balance
    return deposit
d = make_bank(100)
print(d(50))
''')
same(D('''
def outer():
    x = 1
    def a():
        return x + 1
    def b():
        nums.append(x)
        return len(nums)
    nums = []
    return a, b
a, b = outer()
print(a(), b(), b())
'''), '2 1 2')

D6 = lesson('6강. 클로저 — 함수가 기억하는 변수', 50,
'- 함수 안에서 함수를 만들어 **괄호 없이** return 하면 "함수를 돌려주는 함수"가 된다\n- **클로저** = 바깥 함수의 변수(자유 변수)를 기억하는 안쪽 함수. 바깥 함수의 호출이 끝나도 그 변수는 살아 있다\n- 바깥 함수를 **호출할 때마다** 새 변수 묶음이 생긴다 → 클로저마다 독립된 상태\n- 바깥 변수에 **대입**(`=`, `+=`)하려면 `nonlocal` 선언. 없으면 지역 변수로 취급되어 **UnboundLocalError**\n- 읽기만 하거나 리스트에 `append` 하는 것은 대입이 아니라서 nonlocal 이 필요 없다\n- 클로저는 값이 아니라 **변수 자체**를 기억한다 — 반복문에서 만든 lambda 는 모두 마지막 값을 본다',
review('🔁 5강 복습', [T('제너레이터의 핵심을 확인해요. 오늘 배울 클로저도 "함수가 **상태를 기억한다**"는 점에서 닮았어요.'), flip(['제너레이터 함수를 호출하면', '본문은 실행되지 않고 제너레이터 객체만 만들어진다'], ['`next(g)` 한 번', '다음 `yield` 까지 실행하고 멈춘다'], ['리스트 컴프 vs 제너레이터 표현식의 메모리', '전부 만들어 저장 vs 필요할 때 하나씩'], ['제너레이터에 `len()`', 'TypeError'])]),
outq('복습 — 출력 결과는?', D('''
def gen(n):
    print("start", end=" ")
    for i in range(n):
        yield i * i
    print("end", end=" ")
g = gen(3)
print("made", end=" ")
a = next(g)
b = sum(g)
print(a, b, sum(g))
'''), '호출만으로는 "start" 가 찍히지 않아요. 첫 next 에서 "start" 가 찍히고 0 을 받아요. `sum(g)` 가 1 + 4 를 더하고 끝까지 가서 "end" 가 찍혀요. 마지막 `sum(g)` 는 소진되어 0 이에요.', review=True),
explain('함수 안의 함수, 함수를 돌려주는 함수',
  [T('클로저는 L.O.T.C. 에서 다루지 않은 **새 개념**이라 처음부터 차근차근 갈게요. 출발점은 "파이썬에서 **함수도 값**이다"예요. 숫자처럼 변수에 담고, 인자로 넘기고, return 할 수 있어요.'),
   C(D('''
def hello():
    return "안녕"
f = hello
print(f())
print(f is hello)
def twice(func):
    return func() + func()
print(twice(hello))
'''), 'hello 는 함수 자체, hello() 는 호출한 결과'),
   key('`hello` 는 **함수 그 자체**이고 `hello()` 는 **함수를 실행한 결과**예요. 괄호 하나가 뜻을 완전히 바꿔요. 6강·7강의 출력 추론은 대부분 이 구분에서 갈려요.')],
  [T('함수 안에서 또 함수를 만들 수 있어요(**중첩 함수**). 그리고 그 안쪽 함수를 return 하면 "함수를 만들어 돌려주는 함수"가 돼요.'),
   cmp('함수를 돌려줌', 'def outer():\n    def inner():\n        return "inner 실행"\n    return inner\nf = outer()\nprint(f())', '실행 결과를 돌려줌', 'def outer():\n    def inner():\n        return "inner 실행"\n    return inner()\nf = outer()\nprint(f)', 'f 는 함수 → `f()` 로 불러야 실행돼요', 'f 는 문자열 "inner 실행" — 이 f 에 `f()` 를 하면 TypeError', tones=('good', 'bad')),
   warn('`return inner` 와 `return inner()` 를 구분하세요. 클로저를 만들 때는 **괄호 없이** 함수를 돌려줘요.')],
  [T('이제 핵심이에요. 안쪽 함수가 **바깥 함수의 변수**를 쓰면 어떻게 될까요?'),
   C(D('''
def make_multiplier(k):
    def mul(x):
        return x * k
    return mul
double = make_multiplier(2)
triple = make_multiplier(3)
print(double(5), triple(5))
print(double(7), triple(7))
'''), 'make_multiplier 는 이미 끝났는데 k 를 기억하고 있어요'),
   key('`make_multiplier(2)` 의 실행은 return 과 함께 끝났어요. 보통이라면 지역 변수 `k` 도 사라져야 해요. 하지만 안쪽 함수 `mul` 이 `k` 를 쓰고 있어서 **k 는 사라지지 않고 mul 과 함께 살아남아요.** 이렇게 바깥 함수의 변수를 기억하는 안쪽 함수를 **클로저**(closure)라고 해요.')],
  [T('용어를 정리해요. 서술형에서 이 낱말들을 쓰면 답안이 또렷해져요.'),
   flip(['중첩 함수', '함수 안에 정의한 함수'], ['자유 변수', '안쪽 함수가 쓰지만 **자기 것이 아닌**(바깥 함수의) 변수 — 위의 `k`'], ['클로저', '자유 변수를 기억한 채로 반환된 안쪽 함수'], ['클로저의 3조건', '① 중첩 함수 ② 안쪽이 바깥 변수를 사용 ③ 바깥이 안쪽 함수를 **반환**']),
   tip('`double` 과 `triple` 은 같은 코드(`mul`)로 만들어졌지만 **서로 다른 k** 를 기억해요. `make_multiplier` 를 호출할 때마다 새 `k` 가 만들어지기 때문이에요.')]),
outq('출력 결과는?', D('''
def make_tag(mark):
    def tag(text):
        return mark + text + mark
    return tag
star = make_tag("*")
bar = make_tag("|")
print(star("a"), bar("b"), star(bar("c")))
print(make_tag("#")("d"))
'''), '`star` 는 "*" 를, `bar` 는 "|" 를 기억해요. `make_tag("#")("d")` 는 만들자마자 바로 호출한 것이에요.'),
ch('아래 코드의 실행 결과로 옳은 것은?\n\n```\ndef outer():\n    msg = "hi"\n    def inner():\n        return msg.upper()\n    return inner()\nf = outer()\nprint(f())\n```', ['`HI` 가 출력된다', '`hi` 가 출력된다', 'TypeError — 문자열은 호출할 수 없다', 'NameError — msg 를 찾을 수 없다'], 3, '`return inner()` 는 함수가 아니라 **호출 결과인 문자열 "HI"** 를 돌려줘요. 그래서 `f` 는 문자열이고 `f()` 에서 TypeError 가 나요. `return inner` 로 고쳐야 `HI` 가 출력돼요.'),
match('용어와 설명을 이으세요.', [['중첩 함수', '다른 함수의 안에서 정의된 함수'], ['자유 변수', '안쪽 함수가 사용하는 바깥 함수의 변수'], ['클로저', '바깥 함수의 변수를 기억한 채 반환된 함수'], ['`return inner`', '함수 자체를 돌려준다'], ['`return inner()`', '함수를 실행한 결과를 돌려준다']], '괄호가 있으면 "실행 결과", 없으면 "함수 자체"예요.'),
explain('클로저마다 독립된 상태, 그리고 nonlocal',
  [T('클로저의 진짜 쓸모는 **값을 바꿔 가며 기억**하는 데 있어요. 호출 횟수를 세는 카운터를 만들어 봐요. 그런데 그냥 쓰면 오류가 나요.'),
   CX(_ube, '실행하면 UnboundLocalError'),
   warn('`count += 1` 은 `count = count + 1` 이에요. 함수 안에 **대입문이 있으면** 파이썬은 그 변수를 **그 함수의 지역 변수**로 정해요. 그래서 `inc` 안의 `count` 는 바깥의 count 와 다른 지역 변수가 되고, 값을 넣기도 전에 `count + 1` 을 읽으려다 **UnboundLocalError** 가 나요.')],
  [T('"이 변수는 내 것이 아니라 **바깥 함수의 변수**다"라고 알려 주는 선언이 `nonlocal` 이에요.'),
   C(D('''
def make_counter():
    count = 0
    def inc():
        nonlocal count
        count += 1
        return count
    return inc
a = make_counter()
b = make_counter()
print(a(), a(), a())
print(b())
print(a())
'''), 'nonlocal 로 해결 — a 와 b 는 서로 다른 count'),
   key('`make_counter()` 를 **부를 때마다 새 count** 가 만들어져요. 그래서 `a` 가 3까지 세어도 `b` 는 1부터 시작해요. 전역 변수 하나로 만든 카운터는 이렇게 여러 개를 따로 굴릴 수 없어요.')],
  [T('nonlocal 이 **언제 필요하고 언제 필요 없는지**가 시험의 갈림길이에요. 기준은 하나: 바깥 변수에 **대입**(`=`, `+=`, `-=` …)을 하는가.'),
   tabs(('읽기만 → 불필요', '바깥 변수의 값을 읽어 쓰기만 하면 선언이 필요 없어요.', 'def make_adder(n):\n    def add(x):\n        return x + n\n    return add\nprint(make_adder(10)(5))'),
        ('append → 불필요', '`nums.append(x)` 는 리스트 **안을 고치는 것**이지 `nums` 라는 변수에 대입하는 것이 아니에요.', 'def make_log():\n    nums = []\n    def add(x):\n        nums.append(x)\n        return nums\n    return add\nlog = make_log()\nlog(1)\nprint(log(2))'),
        ('대입 → 필요', '`total += x`, `nums = nums + [x]` 처럼 변수 자체에 새 값을 넣으면 nonlocal 이 있어야 해요.', 'def make_sum():\n    total = 0\n    def add(x):\n        nonlocal total\n        total += x\n        return total\n    return add\ns = make_sum()\ns(5)\nprint(s(7))')),
   exam('서술형 "이 코드에서 오류가 나는 이유와 수정 방법"의 답: **오류 이름**(UnboundLocalError) + **이유**(함수 안에서 대입하면 지역 변수로 취급되어, 값이 정해지기 전에 읽게 된다) + **수정**(대입하는 함수 안의 첫 줄에 `nonlocal 변수`).')],
  [T('`global` 과 헷갈리지 마세요. 가리키는 곳이 달라요.'),
   flip(['`nonlocal x`', '**바로 바깥 함수**의 변수 x 를 쓰겠다'], ['`global x`', '함수 밖 **맨 바깥(전역)** 의 변수 x 를 쓰겠다'], ['바깥 함수에 x 가 없는데 `nonlocal x`', 'SyntaxError — 감싸는 함수에 그 변수가 있어야 한다'], ['선언 위치', '대입하는 **안쪽 함수의 맨 위**(사용하기 전)'])]),
spotv('잔액을 기억하는 입금 함수를 만들려고 했어요. **예외가 발생하는 줄**은?', _spot_nl, 5, '4번 줄의 `log.append(x)` 는 대입이 아니라서 정상이에요. 5번 줄은 `balance` 에 대입하므로 `balance` 가 `deposit` 의 지역 변수로 취급되고, 오른쪽의 `balance + x` 를 계산할 때 아직 값이 없어 **UnboundLocalError** 가 나요. `deposit` 의 첫 줄에 `nonlocal balance` 를 넣어야 해요.', name='UnboundLocalError'),
outq('출력 결과는?', D('''
def make_stepper(step):
    pos = 0
    def move():
        nonlocal pos
        pos += step
        return pos
    return move
a = make_stepper(2)
b = make_stepper(5)
a()
a()
b()
c = a
print(a(), b(), c(), a is c)
'''), '`a` 는 2, 4 까지 간 뒤 세 번째 호출에서 6. `b` 는 5 다음 10. `c = a` 는 **같은 클로저의 별명**이라서 `c()` 는 a 의 pos 를 이어서 8 로 만들어요.'),
bucket('안쪽 함수에서 바깥 함수의 변수 `total`(정수), `items`(리스트)를 아래처럼 쓸 때, `nonlocal` 선언이 **필요한 것**과 필요 없는 것으로 나누세요.', ['nonlocal 필요', '필요 없음'], [['`total += x`', 1], ['`return total * 2`', 2], ['`items.append(x)`', 2], ['`items = items + [x]`', 1], ['`total = 0`', 1], ['`print(len(items))`', 2], ['`items[0] = x`', 2], ['`total -= 1`', 1]], '변수 이름 자체에 `=`·`+=`·`-=` 로 새 값을 넣으면 필요해요. `append`, `items[0] = x` 는 리스트의 **내용**을 고치는 것이라 필요 없어요. (`total = 0` 을 nonlocal 없이 쓰면 오류는 안 나지만, 바깥 total 은 그대로이고 새 지역 변수가 생겨요.)'),
fill('호출할 때마다 **지금까지의 최댓값**을 돌려주는 클로저예요. 빈칸을 채우세요.', D('''
def make_max():
    best = None
    def check(x):
        ___ best
        if best is None or x > best:
            best = x
        ___ best
    return ___
m = make_max()
m(4)
m(9)
print(m(6))
'''), ['nonlocal', 'return', 'check'], '`best = x` 로 대입하므로 nonlocal 이 필요해요. 바깥 함수는 안쪽 함수를 **괄호 없이** 돌려줘요.', expect='9'),
essay('아래 코드를 실행하면 오류가 발생해요. **오류의 종류와 이유**를 서술하고, 방문 횟수가 1, 2, 3 … 으로 출력되도록 **수정 방법**을 쓰세요.\n\n```\ndef make_visit():\n    n = 0\n    def visit():\n        n += 1\n        return n\n    return visit\nv = make_visit()\nprint(v())\nprint(v())\n```', 'UnboundLocalError 가 발생한다. visit 함수 안에 n += 1 이라는 대입문이 있으므로, 파이썬은 n 을 visit 의 지역 변수로 취급한다. 그런데 n += 1 은 n = n + 1 이어서 지역 변수 n 에 값이 들어가기 전에 n 을 읽으려 하기 때문에 오류가 난다. visit 함수의 첫 줄에 nonlocal n 을 선언하면 n 이 바깥 함수 make_visit 의 변수를 가리키게 되어, 호출할 때마다 1, 2, 3 으로 누적된다.', ['UnboundLocalError 라고 썼다', '함수 안에서 대입하면 지역 변수로 취급된다고 썼다', '값이 정해지기 전에 읽으려 해서 오류가 난다고 썼다', 'visit 안에 nonlocal n 을 선언한다고 썼다']),
explain('누적 평균 — 시험 유형과 마지막 함정',
  [T('2023년에는 "값을 넣을 때마다 **지금까지의 평균**을 돌려주는 클로저"가 10점으로 나왔어요. 두 가지 방법이 있고, 어느 쪽을 요구하는지는 [조건]이 정해요.'),
   tabs(('① 리스트를 기억', '값을 모두 리스트에 모아 두고 매번 `sum / len`. append 는 대입이 아니라서 **nonlocal 이 필요 없어요.**', 'def make_averager():\n    nums = []\n    def add(x):\n        nums.append(x)\n        return sum(nums) / len(nums)\n    return add\navg = make_averager()\nprint(avg(80))\nprint(avg(90))\nprint(avg(100))'),
        ('② 합계와 개수를 기억', '숫자 두 개만 기억해요. `+=` 로 대입하므로 **nonlocal 이 필요**해요. 값이 아무리 많아도 메모리를 더 쓰지 않아요.', _avg)),
   exam('[조건]에 "리스트를 사용하지 않는다"가 있으면 ②, "nonlocal 을 사용하지 않는다"가 있으면 ①이에요. `nonlocal total, count` 처럼 쉼표로 여러 개를 한 줄에 선언할 수 있어요.')],
  [T('클로저는 "메서드가 하나뿐인 작은 클래스"와 같은 일을 해요. 서술형에서 둘을 비교하라고 할 수 있어요.'),
   cmp('클로저', 'def make_counter():\n    count = 0\n    def inc():\n        nonlocal count\n        count += 1\n        return count\n    return inc\nc = make_counter()\nprint(c(), c())', '클래스', 'class Counter:\n    def __init__(self):\n        self.count = 0\n    def inc(self):\n        self.count += 1\n        return self.count\nc = Counter()\nprint(c.inc(), c.inc())', '상태는 자유 변수에 — 밖에서 `count` 에 직접 접근할 수 없어요', '상태는 인스턴스 변수에 — `c.count` 로 밖에서 읽고 고칠 수 있어요', tones=('good', 'good')),
   tip('공통점: 만들 때마다 **독립된 상태**가 생겨요(`make_counter()` 를 두 번 = `Counter()` 를 두 번). 차이점: 클로저의 변수는 밖에서 건드릴 방법이 없어 저절로 숨겨져요.')],
  [T('마지막 함정이에요. 클로저는 변수의 **값을 복사해 두는 것이 아니라 변수 자체를 기억**해요. 그래서 나중에 그 변수가 바뀌면 바뀐 값을 봐요.'),
   C(_late, '반복문에서 만든 lambda 세 개'),
   rev('왜 첫 줄이 12 12 12 일까요?', '세 lambda 는 모두 **같은 변수 i** 를 기억해요. lambda 가 실제로 호출되는 시점에는 반복이 끝나 i 가 2 이므로 셋 다 `x + 2` 예요. 둘째 줄처럼 `i=i` 기본값 인자를 쓰면, lambda 를 **만드는 순간의 값**이 각자의 매개변수에 저장되어 10 11 12 가 돼요.')]),
outq('출력 결과는?', D('''
def make_averager():
    total = 0
    count = 0
    def add(x):
        nonlocal total, count
        total += x
        count += 1
        return total / count
    return add
a = make_averager()
b = make_averager()
a(10)
a(20)
b(100)
print(a(60), b(50), a(30))
'''), 'a: (10+20+60)/3 = 30.0, 이어서 (…+30)/4 = 30.0. b 는 a 와 독립이라 (100+50)/2 = 75.0 이에요. 나눗셈 `/` 의 결과는 항상 실수예요.'),
outq('출력 결과는?', D('''
def make_funcs():
    funcs = []
    for n in [1, 2, 3]:
        def f(x):
            return x * n
        funcs.append(f)
    return funcs
a, b, c = make_funcs()
print(a(10), b(10), c(10))
'''), '세 함수는 모두 같은 변수 `n` 을 기억하고, 호출 시점의 n 은 반복이 끝난 뒤의 값 3 이에요. 그래서 모두 30 이에요.'),
order('호출할 때마다 **받은 값들의 누적 합**을 돌려주는 클로저와 그 사용 코드예요. 순서대로 놓으세요.', ['def make_sum():', '    total = 0', '    def add(x):', '        nonlocal total', '        total += x', '        return total', '    return add', 's = make_sum()', 's(3)', 'print(s(4))'], '`nonlocal` 선언은 대입보다 앞, 안쪽 함수의 맨 위예요. `return add` 는 바깥 함수의 들여쓰기 깊이에 있어야 해요.'),
essay('아래 코드에서 `add5` 가 **무엇을 기억하고 있는지**, 그리고 `make_adder(5)` 의 실행이 끝났는데도 `add5(10)` 이 15 를 출력할 수 있는 이유를 **클로저**라는 낱말을 사용해 서술하세요.\n\n```\ndef make_adder(n):\n    def add(x):\n        return x + n\n    return add\nadd5 = make_adder(5)\nprint(add5(10))\n```', 'make_adder 는 안쪽 함수 add 를 반환하고, add 는 바깥 함수의 변수 n 을 사용한다. 이렇게 바깥 함수의 변수(자유 변수)를 기억한 채 반환된 안쪽 함수를 클로저라고 한다. add5 는 클로저로서 n = 5 인 변수를 함께 기억하고 있다. 보통 함수의 지역 변수는 호출이 끝나면 사라지지만, 클로저가 그 변수를 참조하고 있는 동안에는 사라지지 않고 유지되므로, make_adder(5) 가 끝난 뒤에도 add5(10) 은 10 + 5 = 15 를 계산할 수 있다.', ['add5 가 바깥 함수의 변수 n(값 5)을 기억한다고 썼다', '바깥 변수를 기억한 채 반환된 안쪽 함수가 클로저라고 썼다', '클로저가 참조하는 변수는 바깥 함수가 끝나도 사라지지 않는다고 썼다', '10 + 5 = 15 가 되는 과정을 썼다']),
prac('[기출유사] 누적 평균 기록기', '모의고사 점수를 한 번 볼 때마다 **지금까지의 평균과 최고점**을 알려 주는 기록기를 클로저로 만들어요.\n\n`make_recorder()` 는 안쪽 함수 `record(score)` 를 반환해요. `record` 는 점수를 받아 `(지금까지의 평균, 지금까지의 최고점)` 을 반환해요.\n\n입력: 첫 줄 `n`, 다음 줄에 점수 n 개(공백 구분, 정수)\n\n출력: 점수를 하나 넣을 때마다 `K회: 평균 A / 최고 B` (평균은 소수 첫째 자리까지). 마지막 줄에는 **새 기록기**를 만들어 마지막 점수 하나만 넣은 결과를 `새 기록기: 평균 A / 최고 B` 로 출력해요.\n\n[조건] ○ 전역 변수·클래스·**리스트를 쓰지 않아요** ○ 합계·횟수·최고점을 바깥 함수의 변수로 두고 `nonlocal` 을 사용',
D('''
def make_recorder():
    total = 0
    count = 0
    best = 0
    def record(score):
        nonlocal total, count, best
        total += score
        count += 1
        if count == 1 or score > best:
            best = score
        return total / count, best
    return record
n = int(input())
scores = map(int, input().split())
rec = make_recorder()
k = 0
for s in scores:
    k += 1
    avg, best = rec(s)
    print(f"{k}회: 평균 {avg:.1f} / 최고 {best}")
avg, best = make_recorder()(s)
print(f"새 기록기: 평균 {avg:.1f} / 최고 {best}")
'''), ['4\n80 90 85 70', '1\n100', '3\n0 0 1', '5\n55 65 75 85 95', '3\n90 60 30', '6\n71 72 73 99 10 10'],
  starter=D('''
def make_recorder():
    total = 0
    count = 0
    best = 0
    def record(score):
        pass  # nonlocal 선언 후 누적
    return record

n = int(input())
'''),
  hints=['`record` 의 첫 줄: `nonlocal total, count, best`.', '`return total / count, best` 처럼 쉼표로 두 값을 돌려주고 `avg, best = rec(s)` 로 받아요.', '새 기록기는 `make_recorder()` 를 **다시 호출**해요. 이전 기록기의 합계와 무관하게 0 부터 시작해요.'],
  ex='`make_recorder()` 를 부를 때마다 새 `total`·`count`·`best` 가 생겨요. 그래서 새 기록기의 평균은 마지막 점수 그 자체예요.'),
prac('[기출유사] 저금통 여러 개 — 독립된 상태', '저금통마다 잔액을 따로 기억해야 해요. `make_bank(name)` 은 그 저금통의 처리 함수 `deal(amount)` 를 반환해요.\n\n- amount 가 양수면 입금, 음수면 출금\n- 출금액이 잔액보다 크면 **거절**하고 잔액은 그대로\n- `deal` 은 결과 문자열을 반환: 성공 `이름: 잔액 B원`, 거절 `이름: 잔액 부족 (B원)`\n\n입력: 첫 줄에 저금통 이름들(공백 구분). 다음 줄 `q`, 이어서 q 줄에 `이름 금액`. 없는 이름이면 `이름: 없는 저금통` 을 출력해요.\n\n출력: 명령마다 결과 한 줄.\n\n[조건] ○ 잔액은 **클로저**가 기억(전역 변수·클래스 금지) ○ 딕셔너리에는 `{이름: 클로저 함수}` 만 저장하고 잔액 숫자는 저장하지 않아요',
D('''
def make_bank(name):
    balance = 0
    def deal(amount):
        nonlocal balance
        if balance + amount < 0:
            return f"{name}: 잔액 부족 ({balance}원)"
        balance += amount
        return f"{name}: 잔액 {balance}원"
    return deal
banks = {}
for name in input().split():
    banks[name] = make_bank(name)
q = int(input())
for _ in range(q):
    name, amount = input().split()
    if name in banks:
        print(banks[name](int(amount)))
    else:
        print(f"{name}: 없는 저금통")
'''), ['여행 간식\n5\n여행 5000\n간식 1000\n여행 -2000\n간식 -1500\n여행 300', '돼지\n3\n돼지 -100\n돼지 100\n돼지 -100', 'a b c\n4\na 10\nd 10\nb 20\na 5', '용돈\n1\n용돈 0', 'x y\n6\nx 100\ny 100\nx -50\nx -50\nx -1\ny -100', '책 폰\n5\n폰 700\n책 -1\n폰 -700\n폰 -1\n게임 5'],
  starter=D('''
def make_bank(name):
    balance = 0
    def deal(amount):
        pass
    return deal

banks = {}
'''),
  hints=['`banks[name] = make_bank(name)` — 이름마다 클로저를 하나씩 만들어 딕셔너리에 담아요.', '`deal` 안: `nonlocal balance`, `balance + amount < 0` 이면 거절 문자열을 return.', '호출은 `banks[name](int(amount))` — 딕셔너리에서 꺼낸 **함수를 바로 호출**해요.'],
  ex='`name` 은 읽기만 하므로 nonlocal 이 필요 없고, `balance` 는 대입하므로 필요해요. 저금통마다 `make_bank` 를 따로 불렀으니 잔액도 따로예요.'),
prac('[심화] 쿠폰 발급기 공장', '가게마다 쿠폰 규칙이 달라요. `make_coupon(rate, limit)` 은 할인 함수 `use(price)` 를 반환해요.\n\n- `rate` : 할인율(%) / `limit` : 이 쿠폰을 쓸 수 있는 **최대 횟수**\n- `use(price)` 는 남은 횟수가 있으면 `price` 에서 rate% 를 할인한 금액(원 미만 버림)을 반환하고 사용 횟수를 1 늘려요. 횟수를 다 썼으면 `price` 를 그대로 반환해요.\n\n입력: 첫 줄 `rate limit`, 둘째 줄에 가격들(공백 구분)\n\n출력\n1. 가격마다 `가격원 → 결제 P원 (할인)` 또는 `가격원 → 결제 P원 (정가)`\n2. `총 결제: T원`\n3. `아낀 금액: S원`\n\n[조건] ○ 사용 횟수는 클로저가 기억(`nonlocal`) ○ 할인 여부는 **`use` 가 돌려준 값과 원래 가격을 비교**해 판단 (단, 할인 금액이 0원이면 `(정가)` 로 표시)',
D('''
def make_coupon(rate, limit):
    used = 0
    def use(price):
        nonlocal used
        if used >= limit:
            return price
        used += 1
        return price - price * rate // 100
    return use
rate, limit = map(int, input().split())
use = make_coupon(rate, limit)
total = 0
saved = 0
for p in map(int, input().split()):
    pay = use(p)
    kind = "할인" if pay < p else "정가"
    print(f"{p}원 → 결제 {pay}원 ({kind})")
    total += pay
    saved += p - pay
print(f"총 결제: {total}원")
print(f"아낀 금액: {saved}원")
'''), ['10 2\n5000 3000 8000', '25 5\n1000 1999', '50 0\n4000 4000', '15 1\n990', '30 3\n100 250 3 7000 7000', '1 2\n50 12345 100'],
  starter=D('''
def make_coupon(rate, limit):
    used = 0
    def use(price):
        pass
    return use

rate, limit = map(int, input().split())
'''),
  hints=['`use` 안: `nonlocal used` → `if used >= limit: return price` → `used += 1` → 할인 금액 return.', '원 미만 버림: `price - price * rate // 100`.', '`rate`, `limit` 는 읽기만 하므로 nonlocal 에 넣지 않아도 돼요. 대입하는 것은 `used` 뿐이에요.'],
  ex='할인액이 0원(예: 50원의 1%)이어도 **사용 횟수는 줄어요.** 횟수를 세는 것은 클로저 안의 `used` 이고, 바깥 코드는 그 값을 볼 수 없어요.'),
prac('[심화] 호출 횟수를 세는 포장 함수', '함수를 **인자로 받아**, 그 함수가 몇 번 불렸는지 세어 주는 포장 함수를 만들어요. (다음 강 데코레이터의 준비 운동이에요.)\n\n`make_counted(func)` 는 함수 두 개를 튜플로 반환해요.\n- `call(x)` : `func(x)` 의 결과를 그대로 반환하면서 호출 횟수를 1 늘려요\n- `get_count()` : 지금까지의 호출 횟수를 반환해요\n\n아래 두 함수를 각각 포장해서 써요.\n\n```\ndef square(x):\n    return x * x\ndef half(x):\n    return x // 2\n```\n\n입력: 첫 줄 `q`, 이어서 q 줄에 `명령 정수`. 명령은 `sq`(square) 또는 `hf`(half).\n\n출력: 명령마다 결과를 한 줄씩. 마지막에 `square 호출 A번, half 호출 B번`, 그리고 **결과의 총합** `합계: T`.\n\n[조건] ○ 횟수는 클로저가 기억(전역 변수 금지) ○ `square`, `half` 의 본문은 고치지 않아요',
D('''
def make_counted(func):
    count = 0
    def call(x):
        nonlocal count
        count += 1
        return func(x)
    def get_count():
        return count
    return call, get_count
def square(x):
    return x * x
def half(x):
    return x // 2
sq, sq_count = make_counted(square)
hf, hf_count = make_counted(half)
total = 0
for _ in range(int(input())):
    cmd, x = input().split()
    r = sq(int(x)) if cmd == "sq" else hf(int(x))
    print(r)
    total += r
print(f"square 호출 {sq_count()}번, half 호출 {hf_count()}번")
print(f"합계: {total}")
'''), ['4\nsq 3\nhf 9\nsq 5\nsq 1', '1\nhf 7', '3\nsq 0\nsq 10\nsq 2', '5\nhf 100\nhf 50\nsq 4\nhf 1\nhf 0', '2\nsq 12\nhf 12', '6\nsq 1\nhf 2\nsq 3\nhf 4\nsq 5\nhf 6'],
  starter=D('''
def make_counted(func):
    count = 0
    # call, get_count 를 만들어 return call, get_count

def square(x):
    return x * x
def half(x):
    return x // 2
'''),
  hints=['안쪽 함수 두 개가 **같은 count** 를 함께 기억해요. `call` 은 대입하므로 `nonlocal count`, `get_count` 는 읽기만 하므로 선언이 필요 없어요.', '`return call, get_count` 로 두 함수를 돌려주고 `sq, sq_count = make_counted(square)` 로 받아요.', '`call` 안에서는 `return func(x)` — 받은 함수 `func` 도 클로저가 기억하는 자유 변수예요.'],
  ex='`make_counted` 를 두 번 불렀으므로 square 용 count 와 half 용 count 는 서로 달라요. "함수를 받아 → 감싼 새 함수를 돌려준다"는 이 구조가 바로 다음 강의 데코레이터예요.'),
)
