from glib import *

# ============================================================ G8
G8 = lesson('8강. 연산자 오버로딩 — + 와 - 를 내 클래스에 가르치기', 45,
'- `a + b` 는 `a.__add__(b)`, `a - b` 는 `a.__sub__(b)`, `print(a)` 는 `a.__str__()`\n- 결과는 **새 객체를 만들어 return** — self 를 바꾸지 않는다\n- return 을 빠뜨리면 결과가 None → 다음 줄에서 AttributeError\n- 범위 규칙(0~255 등)은 **`__init__` 한곳**에서 지키면 모든 연산이 자동으로 지킨다\n- `==` 는 `__eq__`, `<` 는 `__lt__` — `sorted`, `max`, `min` 이 `__lt__` 를 쓴다\n- `a + b + c` 가 되려면 `__add__` 가 **같은 클래스의 객체**를 돌려줘야 한다',
review('🔁 7강 복습', [T('캡슐화와 is / == 를 확인해요.'), flip(['밖에서 `obj.__x` 를 읽으면', 'AttributeError'], ['밖에서 `obj.__x = 0` 을 대입하면', '오류 없이 새 속성이 생김 — 진짜 값은 그대로'], ['`__eq__` 가 없는 클래스의 `==`', 'is 처럼 "같은 객체인가"를 본다'], ['`b = a` 뒤 `b is a`', 'True — 복사가 아니라 별명'])]),
outq('복습 — 출력 결과는?', D('''
class Box:
    def __init__(self, n):
        self.__n = n
    def get(self):
        return self.__n
    def __eq__(self, other):
        return self.get() == other.get()
a = Box(3)
b = Box(3)
c = a
a.__n = 9
print(a == b, a is b, c is a, c.get(), len(vars(a)))
'''), review=True),
explain('연산자는 메서드 호출이다',
  [T('`3 + 4` 가 되는 이유는 int 클래스에 `__add__` 가 있기 때문이에요. 내 클래스에도 같은 이름의 메서드를 만들면 `+` 를 쓸 수 있어요. 이것이 **연산자 오버로딩**이에요(2024 4번 Vector2D 15점, 2025 3번 Color 12점).'),
   C(D('''
class Vector2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)
    def __str__(self):
        return f"({self.x}, {self.y})"
a = Vector2D(3, 4)
b = Vector2D(1, 2)
print(a + b)
print(a - b)
print(a + b + b)
print(a, b)
'''), 'a + b 는 a.__add__(b) — self 가 왼쪽, other 가 오른쪽'),
   key('`__add__` 는 **새 Vector2D 를 만들어 return** 해요. 그래서 a 와 b 는 그대로이고, 결과가 또 Vector2D 라서 `a + b + b` 처럼 이어 쓸 수 있어요.')],
  [T('시험에 나오는 짝은 몇 개 안 돼요.'),
   flip(['a + b', '__add__(self, other)'], ['a - b', '__sub__(self, other)'], ['a * b', '__mul__(self, other)'], ['a == b', '__eq__(self, other)'], ['a < b', '__lt__(self, other)'], ['print(a), str(a)', '__str__(self)'], ['len(a)', '__len__(self)']),
   C(D('''
class Vector2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __mul__(self, k):
        return Vector2D(self.x * k, self.y * k)
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __str__(self):
        return f"({self.x}, {self.y})"
a = Vector2D(1, 2)
print(a * 3)
print(a * 3 == Vector2D(3, 6), a == Vector2D(2, 1))
'''), 'other 가 꼭 같은 클래스일 필요는 없어요 (여기서는 숫자 k)'),
   tip('`a * 3` 은 되지만 `3 * a` 는 TypeError 예요. `3 * a` 는 **왼쪽인 int** 의 `__mul__` 을 먼저 부르는데, int 는 Vector2D 를 모르기 때문이에요.')],
  [T('감점되는 실수 세 가지를 미리 봐요.'),
   tabs(['① return 을 빠뜨림', '`__add__` 가 None 을 돌려줘서, 결과를 쓰는 **다음 줄**에서 AttributeError', 'def __add__(self, other):\n    Vector2D(self.x + other.x, self.y + other.y)   # return 없음'], ['② self 를 바꿈', '`c = a + b` 를 했는데 **a 가 변해요**. 덧셈은 원본을 바꾸면 안 돼요', 'def __add__(self, other):\n    self.x += other.x\n    self.y += other.y\n    return self'], ['③ 다른 자료형을 return', '튜플을 돌려주면 `a + b + c` 의 두 번째 `+` 가 깨져요 (튜플 + Vector2D)', 'def __add__(self, other):\n    return (self.x + other.x, self.y + other.y)'], ['④ __str__ 에서 print', '`__str__` 은 문자열을 **return**. print 하면 TypeError', 'def __str__(self):\n    print(f"({self.x}, {self.y})")']),
   key('체크리스트: **① 새 객체를 만든다 ② return 한다 ③ self·other 는 건드리지 않는다.**')]),
explain('규칙을 지키는 연산 — Color 와 비교 연산',
  [T('RGB 색은 각 값이 **0~255** 여야 해요. 더해서 255 를 넘으면 255, 빼서 음수가 되면 0 으로 만들라는 조건이 붙어요. 이 규칙을 **어디에** 쓰느냐가 설계예요.'),
   C(D('''
class Color:
    def __init__(self, r, g, b):
        self.r = max(0, min(255, r))
        self.g = max(0, min(255, g))
        self.b = max(0, min(255, b))
    def __add__(self, other):
        return Color(self.r + other.r, self.g + other.g, self.b + other.b)
    def __sub__(self, other):
        return Color(self.r - other.r, self.g - other.g, self.b - other.b)
    def __str__(self):
        return f"RGB({self.r}, {self.g}, {self.b})"
red = Color(200, 30, 30)
gray = Color(100, 100, 100)
print(red + gray)
print(red - gray)
'''), '규칙은 __init__ 에만. __add__ 와 __sub__ 는 넘치는 값을 그대로 넘겨요'),
   key('`max(0, min(255, v))` 는 "v 를 0~255 사이로 자르기"예요. 생성자에 한 번 써 두면 `+` 든 `-` 든 **결과가 생성자를 거치므로** 자동으로 규칙을 지켜요. 5강의 Time 클래스와 같은 생각이에요.')],
  [T('`__lt__`(less than, `<`)를 만들면 **정렬과 최대·최소**가 한꺼번에 돼요. `sorted`, `max`, `min` 이 내부에서 `<` 만 쓰기 때문이에요.'),
   C(D('''
class Player:
    def __init__(self, name, score):
        self.name = name
        self.score = score
    def __lt__(self, other):
        return self.score < other.score
    def __str__(self):
        return f"{self.name}:{self.score}"
ps = [Player("민", 70), Player("솔", 95), Player("율", 80)]
print(*[str(p) for p in sorted(ps)])
print(max(ps), min(ps))
print(ps[0] < ps[1], ps[1] < ps[2])
'''), 'sorted 에 key 를 주지 않아도 __lt__ 로 비교해요'),
   warn('`sum([v1, v2, v3])` 은 `__add__` 가 있어도 TypeError 예요. sum 은 `0 + v1` 부터 시작하는데 int 0 은 Vector2D 를 더할 줄 몰라요. `sum(vs, Vector2D(0, 0))` 처럼 **시작값**을 주거나 반복문으로 더해요.')]),
outq('[기출유사] 출력 결과는?', D('''
class V:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __add__(self, o):
        return V(self.x + o.x, self.y + o.y)
    def __sub__(self, o):
        return V(self.x - o.x, self.y - o.y)
    def __str__(self):
        return f"<{self.x},{self.y}>"
a, b, c = V(5, 1), V(2, 2), V(1, 4)
d = a + b - c
e = a - (b - c)
print(d, e, a)
'''), '`a + b - c` 는 왼쪽부터: (a + b) - c. 괄호가 있으면 괄호 먼저. a 는 바뀌지 않아요.'),
outq('[기출유사] 출력 결과는?', D('''
class Color:
    def __init__(self, r, g, b):
        self.rgb = [max(0, min(255, v)) for v in (r, g, b)]
    def __add__(self, o):
        return Color(*[x + y for x, y in zip(self.rgb, o.rgb)])
    def __sub__(self, o):
        return Color(*[x - y for x, y in zip(self.rgb, o.rgb)])
    def __str__(self):
        return "-".join(map(str, self.rgb))
a = Color(250, 100, 0)
b = Color(10, 200, 50)
print(a + b, a - b, a + b - b, a - b + b)
'''), '`a + b - b` 는 a 로 돌아오지 않아요. 한 번 255 로 잘린 값은 원래 값을 기억하지 못해요.'),
spot('[기출유사] **예외가 발생하는 줄**은?', D('''
class V:
    def __init__(self, x):
        self.x = x
    def __add__(self, other):
        V(self.x + other.x)
a = V(1) + V(2)
b = V(3)
print(a.x + b.x)
'''), 8, '5번 줄에 return 이 없어 `a` 는 None 이에요. 6번 줄의 덧셈 자체는 오류 없이 끝나고, `a.x` 를 읽는 8번 줄에서 AttributeError 가 나요.'),
fill('[기출유사] 두 점수 묶음을 과목별로 더하고, `국어 150 / 수학 170` 형식으로 출력해요.', D('''
class Score:
    def __init__(self, kor, math):
        self.kor, self.math = kor, math
    def ___(self, other):
        return ___(self.kor + other.kor, self.math + other.math)
    def __str__(self):
        return f"국어 {self.kor} / 수학 {self.math}"
print(Score(70, 90) + Score(80, 80))
'''), ['__add__', 'Score'], expect='국어 150 / 수학 170'),
outq('[기출유사] 출력 결과는?', D('''
class Card:
    def __init__(self, suit, n):
        self.suit, self.n = suit, n
    def __lt__(self, other):
        return self.n < other.n
    def __str__(self):
        return f"{self.suit}{self.n}"
cards = [Card("S", 7), Card("H", 3), Card("D", 9), Card("C", 3)]
print(*[str(c) for c in sorted(cards)], max(cards), min(cards))
'''), '숫자가 같은 H3 와 C3 는 **원래 순서**를 유지해요(안정 정렬). min 도 같은 값 중 **먼저 나온** H3 를 골라요.'),
outq('[기출유사] 출력 결과는?', D('''
class V:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __add__(self, o):
        return V(self.x + o.x, self.y + o.y)
    def __mul__(self, k):
        return V(self.x * k, self.y * k)
    def __eq__(self, o):
        return (self.x, self.y) == (o.x, o.y)
    def __str__(self):
        return f"({self.x}, {self.y})"
a = V(1, 2)
b = a * 3
c = a + a + a
print(b, b == c, b is c, a)
'''), '값은 같지만(`==`) 따로 만들어진 객체라 `is` 는 False.'),
outq('[심화] 출력 결과는?', D('''
class Bad:
    def __init__(self, x):
        self.x = x
    def __add__(self, o):
        self.x += o.x
        return self
a = Bad(1)
b = Bad(2)
c = a + b
d = a + b
print(a.x, c.x, d.x, c is a, c is d)
'''), '`__add__` 가 self 를 바꾸고 self 를 돌려줘서, a·c·d 가 **모두 같은 객체**예요. 덧셈을 두 번 했더니 a 가 5 가 됐어요.'),
ch('[심화] `V` 클래스에 `__mul__(self, k)` 만 정의했을 때 `V(1, 2) * 3` 은 되는데 `3 * V(1, 2)` 는 TypeError 가 나는 이유는?', ['곱셈은 교환 법칙이 성립하지 않아서', '`3 * v` 는 왼쪽 피연산자인 int 의 `__mul__` 을 먼저 부르는데, int 는 V 를 곱할 줄 몰라서', '`__mul__` 의 매개변수 이름이 k 여서', 'V 에 `__str__` 이 없어서'], 2, '연산자는 **왼쪽 객체의 메서드**를 불러요. 오른쪽에 있을 때도 동작하게 하려면 `__rmul__` 을 따로 만들어야 해요(시험 범위 밖, 이유만 알아 두세요).'),
match('연산과 호출되는 메서드를 이어 보세요.', [['a + b', 'a.__add__(b)'], ['a - b', 'a.__sub__(b)'], ['a == b', 'a.__eq__(b)'], ['a < b', 'a.__lt__(b)'], ['print(a)', 'a.__str__()'], ['len(a)', 'a.__len__()']]),
essay('[기출유사 · 서술 6점] 아래 `__add__` 로 `c = a + b` 를 실행한 뒤 `print(a.x)` 를 하면 처음 값과 달라져 있어요. **문제점**을 설명하고 `__add__` 를 바르게 고치세요.\n\n```\nclass V:\n    def __init__(self, x):\n        self.x = x\n    def __add__(self, other):\n        self.x += other.x\n        return self\n```', '__add__ 안에서 self.x 를 직접 바꾸고 self 를 반환하기 때문에, a + b 를 계산하면 왼쪽 피연산자인 a 자신이 변하고 c 는 a 와 같은 객체가 된다. 덧셈은 원래 값을 바꾸지 않고 새 결과를 만들어야 한다. return V(self.x + other.x) 처럼 새 객체를 만들어 반환하도록 고친다.', ['self(왼쪽 피연산자 a)가 바뀐다는 문제를 짚었다', 'c 와 a 가 같은 객체가 된다(또는 원본이 보존되지 않는다)고 썼다', '새 객체를 만들어야 한다고 썼다', 'return V(self.x + other.x) 로 고쳤다']),
ox('`__add__` 만 정의한 클래스의 객체 리스트 `vs` 에 대해 `sum(vs)` 는 모든 객체를 더한 결과를 돌려준다.', False, 'sum 은 `0 + vs[0]` 부터 계산해서 TypeError 예요. `sum(vs, V(0, 0))` 처럼 시작값을 줘야 해요.'),
prac('[기출유사 · 15점] Vector2D 계산', '`Vector2D` 클래스에 `__add__`, `__sub__`, `__mul__`(정수 k 배), `__eq__`, `__str__` 을 만들어요. 출력 형식은 `(x, y)`.\n\n입력: 첫 줄 `x1 y1` (벡터 a), 둘째 줄 `x2 y2` (벡터 b), 셋째 줄 정수 `k`\n\n출력(한 줄씩)\n1. `a + b`\n2. `a - b`\n3. `b - a`\n4. `a * k`\n5. `a + b * k - a` (연산 순서는 파이썬 그대로)\n6. `a == b` 의 결과 (`True` / `False`)\n7. `(a + b) - b == a` 의 결과\n8. `a` 와 `b` 를 공백으로 구분해 출력 (원본이 바뀌지 않았는지 확인)\n\n[조건] ○ 모든 연산은 **새 객체**를 return ○ 메인 코드에서 `.x`, `.y` 를 직접 꺼내 계산하지 말고 **연산자만** 사용',
D('''
class Vector2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)
    def __mul__(self, k):
        return Vector2D(self.x * k, self.y * k)
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __str__(self):
        return f"({self.x}, {self.y})"
x1, y1 = map(int, input().split())
x2, y2 = map(int, input().split())
k = int(input())
a = Vector2D(x1, y1)
b = Vector2D(x2, y2)
print(a + b)
print(a - b)
print(b - a)
print(a * k)
print(a + b * k - a)
print(a == b)
print((a + b) - b == a)
print(a, b)
'''), ['3 4\n1 2\n2', '0 0\n0 0\n5', '-1 7\n-1 7\n-1', '10 -3\n4 4\n0', '2 2\n5 -5\n3', '1 0\n0 1\n10'],
  starter=D('''
class Vector2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)
    # __sub__, __mul__, __eq__, __str__ 를 작성하세요

x1, y1 = map(int, input().split())
x2, y2 = map(int, input().split())
k = int(input())
a = Vector2D(x1, y1)
b = Vector2D(x2, y2)
print(a + b)
'''), hints=['`__mul__(self, k)` 의 k 는 숫자예요: `Vector2D(self.x * k, self.y * k)`', '`a + b * k - a` 는 `*` 가 먼저라 `(a + (b * k)) - a`', '`__eq__` 는 True/False 를 return: `self.x == other.x and self.y == other.y`'], ex='5번 줄의 결과는 항상 `b * k` 와 같아요. 연산자 우선순위는 **내 클래스에서도 그대로**예요 — `__mul__` 이 `__add__` 보다 먼저 불려요.'),
prac('[기출유사 · 12점] Color — 넘치지 않는 색', '`Color` 클래스를 만들어요. r, g, b 는 항상 **0~255** 를 유지해요(넘으면 255, 음수면 0).\n\n- `__add__`, `__sub__` : 성분별로 더하고 빼요\n- `__eq__` : 세 성분이 모두 같으면 True\n- `__str__` : `RGB(r, g, b)`\n\n입력: 첫 줄 색의 수 `n`, 이어서 n 줄에 `r g b` (범위 밖의 값이 들어올 수 있어요). 그다음 줄 `q`, 이어서 q 줄에 `i 연산 j` (i, j 는 1부터, 연산은 `+` `-` `==`).\n\n출력\n1. 등록된 색을 한 줄씩\n2. 질의마다 결과 (`+` `-` 는 색, `==` 는 `같은 색` / `다른 색`)\n3. 마지막 줄에 **모든 색을 1번부터 차례로 더한** 결과를 `전체 합: RGB(…)` 로\n\n[조건] ○ 범위 규칙은 **`__init__` 에만** 작성 ○ 전체 합은 `+` 연산자로 누적',
D('''
class Color:
    def __init__(self, r, g, b):
        self.r = max(0, min(255, r))
        self.g = max(0, min(255, g))
        self.b = max(0, min(255, b))
    def __add__(self, other):
        return Color(self.r + other.r, self.g + other.g, self.b + other.b)
    def __sub__(self, other):
        return Color(self.r - other.r, self.g - other.g, self.b - other.b)
    def __eq__(self, other):
        return (self.r, self.g, self.b) == (other.r, other.g, other.b)
    def __str__(self):
        return f"RGB({self.r}, {self.g}, {self.b})"
n = int(input())
colors = []
for _ in range(n):
    r, g, b = map(int, input().split())
    colors.append(Color(r, g, b))
for c in colors:
    print(c)
q = int(input())
for _ in range(q):
    i, op, j = input().split()
    x, y = colors[int(i) - 1], colors[int(j) - 1]
    if op == "+":
        print(x + y)
    elif op == "-":
        print(x - y)
    else:
        print("같은 색" if x == y else "다른 색")
total = colors[0]
for c in colors[1:]:
    total = total + c
print(f"전체 합: {total}")
'''), ['3\n200 30 30\n100 100 100\n300 -20 255\n4\n1 + 2\n1 - 2\n2 - 1\n3 == 3', '1\n0 0 0\n1\n1 == 1', '2\n255 255 255\n999 999 999\n3\n1 == 2\n1 + 2\n1 - 2', '3\n10 20 30\n10 20 30\n1 2 3\n3\n1 == 2\n1 - 3\n3 - 1', '4\n60 60 60\n70 70 70\n80 80 80\n90 90 90\n2\n4 - 1\n1 + 4'],
  starter=D('''
class Color:
    def __init__(self, r, g, b):
        # 0~255 로 잘라서 저장
        self.r = r
        self.g = g
        self.b = b
    # __add__, __sub__, __eq__, __str__ 를 작성하세요

n = int(input())
colors = []
for _ in range(n):
    r, g, b = map(int, input().split())
    colors.append(Color(r, g, b))
for c in colors:
    print(c)
'''), hints=['자르기: `max(0, min(255, r))`', '`__add__` 는 그냥 `Color(self.r + other.r, …)` — 넘치는 값은 생성자가 잘라 줘요.', '전체 합: `total = colors[0]` 에서 시작해 `total = total + c`'], ex='입력에서 `300 -20 255` 가 `RGB(255, 0, 255)` 로 등록되는 것도, 덧셈 결과가 255 에서 멈추는 것도 **같은 한 줄**(생성자) 덕분이에요. 규칙이 한곳에 있으면 빠뜨릴 수가 없어요.'),
prac('[심화 · 16점] 분수 클래스 Fraction', '분수를 다루는 `Fraction` 클래스를 만들어요.\n\n- `__init__(self, n, d)` : 분모가 0 이면 **ZeroDivisionError 를 raise**. 항상 **기약분수**로, **분모는 양수**로 정리해서 저장 (예: `2/-4` → `-1/2`)\n- `__add__`, `__sub__`, `__mul__` : 결과는 새 Fraction\n- `__eq__`, `__lt__` : 값으로 비교\n- `__str__` : `n/d`, 분모가 1 이면 `n` 만\n\n입력: 첫 줄 `k`, 이어서 k 줄에 `분자/분모` (정수).\n\n출력\n1. 분모가 0 인 줄은 `[N번] 잘못된 분수` 를 출력하고 제외해요 (N 은 입력 순서, 1부터)\n2. 올바른 분수가 하나도 없으면 `분수 없음` 을 출력하고 끝내요\n3. `정리: ` 뒤에 정리된 분수들을 입력 순서대로 공백 구분\n4. `합: ` / `곱: ` / `첫째 - 둘째: ` (분수가 1개뿐이면 이 줄은 생략)\n5. `정렬: ` 뒤에 오름차순으로 공백 구분\n6. `최대: ` 와 `최소: ` 를 각각 한 줄씩\n7. `서로 다른 값: N개`\n\n[조건] ○ 약분은 `math.gcd` 사용 ○ 정렬·최대·최소는 `sorted`, `max`, `min` 에 **key 없이** (`__lt__` 로) ○ 서로 다른 값의 개수는 `==` 로 비교해 세기',
D('''
import math
class Fraction:
    def __init__(self, n, d):
        if d == 0:
            raise ZeroDivisionError
        if d < 0:
            n, d = -n, -d
        g = math.gcd(n, d)
        self.n = n // g
        self.d = d // g
    def __add__(self, o):
        return Fraction(self.n * o.d + o.n * self.d, self.d * o.d)
    def __sub__(self, o):
        return Fraction(self.n * o.d - o.n * self.d, self.d * o.d)
    def __mul__(self, o):
        return Fraction(self.n * o.n, self.d * o.d)
    def __eq__(self, o):
        return self.n == o.n and self.d == o.d
    def __lt__(self, o):
        return self.n * o.d < o.n * self.d
    def __str__(self):
        return str(self.n) if self.d == 1 else f"{self.n}/{self.d}"
k = int(input())
fs = []
for i in range(1, k + 1):
    n, d = map(int, input().split("/"))
    try:
        fs.append(Fraction(n, d))
    except ZeroDivisionError:
        print(f"[{i}번] 잘못된 분수")
if not fs:
    print("분수 없음")
else:
    print("정리:", *fs)
    total = fs[0]
    prod = fs[0]
    for f in fs[1:]:
        total = total + f
        prod = prod * f
    print("합:", total)
    print("곱:", prod)
    if len(fs) >= 2:
        print("첫째 - 둘째:", fs[0] - fs[1])
    print("정렬:", *sorted(fs))
    print("최대:", max(fs))
    print("최소:", min(fs))
    uniq = []
    for f in fs:
        if f not in uniq:
            uniq.append(f)
    print(f"서로 다른 값: {len(uniq)}개")
'''), ['4\n1/2\n2/4\n3/-4\n5/0', '1\n6/3', '2\n1/0\n-2/0', '3\n1/3\n1/6\n1/2', '4\n-1/2\n2/-4\n-3/-6\n0/5', '3\n7/1\n-7/1\n14/2'],
  hints=['정리 순서: 분모가 음수면 분자·분모의 부호를 함께 바꾸고 → `g = math.gcd(n, d)` 로 나눠요. `math.gcd` 는 음수가 섞여도 양수를 돌려줘요.', '덧셈: `Fraction(self.n * o.d + o.n * self.d, self.d * o.d)` — 약분은 생성자가 해요.', '`__lt__`: 분모가 양수이므로 `self.n * o.d < o.n * self.d` (교차 곱)', '`print("정리:", *fs)` 처럼 객체를 print 에 넘기면 `__str__` 이 자동으로 불려요.'], ex='`f not in uniq` 는 `__eq__` 를, `sorted`·`max`·`min` 은 `__lt__` 를 불러요. 메서드 다섯 개를 만들었더니 파이썬의 **내장 기능들이 내 클래스를 이해**하게 됐어요. 그리고 기약분수 규칙은 이번에도 생성자 한곳에만 있어요.'),
)

# ============================================================ G9
G9 = lesson('9강. numpy — 반복문 없이 배열 전체를 계산하기', 45,
'- 리스트 `* 2` 는 **반복**, 배열 `* 2` 는 **원소마다 2배** — 배열의 연산은 원소별\n- `shape` 는 (행, 열), `size` 는 전체 개수, `ndim` 은 차원 수\n- `np.zeros(n)`, `np.ones(n)` 은 **실수** / `np.arange(a, b, c)` 는 range 처럼 / `reshape(행, 열)` 은 개수가 맞아야\n- `axis=0` → **열마다**(행 방향으로 합침), `axis=1` → **행마다**\n- 조건식 `a > 5` 는 True/False 배열 → `.sum()` 으로 **개수**, `a[a > 5]` 로 **골라내기**\n- 2차원 인덱싱 `a[행, 열]`, 한 열 전체 `a[:, 열]`',
review('🔁 8강 복습', [T('연산자 오버로딩의 체크리스트를 확인해요.'), rev('`a + b` 가 부르는 메서드와 인자는?', code='a.__add__(b)   # self = a, other = b'), rev('`__add__` 가 지켜야 할 세 가지는?', '① 새 객체를 만든다 ② return 한다 ③ self·other 를 바꾸지 않는다'), rev('0~255 규칙을 한곳에만 쓰려면 어디에?', '`__init__` (생성자)')]),
outq('복습 — 출력 결과는?', D('''
class N:
    def __init__(self, v):
        self.v = max(0, min(9, v))
    def __add__(self, o):
        return N(self.v + o.v)
    def __sub__(self, o):
        return N(self.v - o.v)
    def __lt__(self, o):
        return self.v < o.v
    def __str__(self):
        return str(self.v)
a, b = N(7), N(5)
print(a + b, b - a, a + b - a, max(a, b), b < a)
'''), review=True),
explain('배열은 리스트가 아니다',
  [T('numpy 는 2025학년도부터 시험에 들어온 **새 범위**예요(1차 7문항 중 2문항, 27점). 리스트처럼 보이지만 **연산의 뜻이 달라요**.'),
   C(D('''
import numpy as np
a = [1, 2, 3]
b = np.array([1, 2, 3])
print(a * 2)
print(b * 2)
print(a + a)
print(b + b)
print(b + 10, b ** 2, b > 1)
'''), '리스트의 + 와 * 는 "이어 붙이기", 배열은 "원소마다 계산"'),
   key('배열의 연산은 **같은 자리끼리**(원소별) 일어나요. 숫자 하나와 연산하면 그 숫자가 **모든 원소에** 적용돼요. 그래서 반복문이 필요 없어요.'),
   tip('출력 모양도 달라요. 리스트는 `[1, 2, 3]`(쉼표), 배열은 `[1 2 3]`(공백). 시험 답안을 쓸 때 구분해서 적으세요. 리스트로 바꾸려면 `b.tolist()`.')],
  [T('배열의 **모양**을 묻는 문제가 꼭 나와요.'),
   C(D('''
import numpy as np
m = np.array([[90, 80, 70], [60, 50, 40]])
print(m.shape, m.ndim, m.size, len(m))
print(m[0])
print(m[1, 2], m[0][1])
print(m[:, 1])
print(m[1, :2])
'''), 'shape 은 (행, 열) 튜플'),
   flip(['m.shape', '(행 수, 열 수) — 여기서는 (2, 3)'], ['m.size', '전체 원소 수 — 6'], ['m.ndim', '차원 수 — 2'], ['len(m)', '**행** 수 — 2'], ['m[1, 2]', '1행 2열 (0부터) — 40'], ['m[:, 1]', '모든 행의 1열 — [80 50]'])],
  [T('배열을 **만드는** 함수들이에요. 2025 7번(12점)이 `np.ones` 와 `np.arange().reshape` 였어요.'),
   C(D('''
import numpy as np
print(np.zeros(3))
print(np.ones((2, 3)))
print(np.ones(4, dtype=int) * 5)
print(np.arange(5), np.arange(2, 11, 3))
print(np.arange(1, 7).reshape(2, 3))
'''), 'zeros·ones 는 기본이 실수(0. 1.)'),
   warn('`reshape` 은 **원소 개수가 같아야** 해요. 6개짜리를 `reshape(4, 2)` 하면 ValueError. 그리고 `reshape` 은 **새 배열을 돌려줘요** — 원래 배열의 모양은 그대로예요.'),
   tabs(['np.zeros(n)', '0.0 이 n개 (실수)', 'np.zeros(3)        # [0. 0. 0.]'], ['np.ones((r, c))', '1.0 으로 채운 r행 c열 — 2차원은 **튜플**로', 'np.ones((2, 3))'], ['np.arange(a, b, s)', 'range(a, b, s) 의 배열판. b 는 포함 안 됨', 'np.arange(0, 10, 2) # [0 2 4 6 8]'], ['.reshape(r, c)', '같은 원소를 r행 c열로 다시 배치', 'np.arange(6).reshape(2, 3)'])]),
explain('통계 · axis · 조건',
  [T('합·평균·최대·최소는 메서드 한 번이에요. 2차원에서는 **`axis`** 로 방향을 정해요.'),
   C(D('''
import numpy as np
s = np.array([[90, 80, 70],
              [60, 100, 50]])
print(s.sum(), s.mean(), s.max(), s.min())
print(s.sum(axis=0))
print(s.sum(axis=1))
print(s.mean(axis=1), s.max(axis=0))
'''), '2명 × 3과목 점수표'),
   key('`axis=0` 은 **0번 축(행)을 따라 내려가며** 합쳐요 → 결과는 **열마다 하나**(과목별). `axis=1` 은 **1번 축(열)을 따라 옆으로** 합쳐요 → 결과는 **행마다 하나**(학생별). 헷갈리면 결과의 개수로 확인: (2, 3) 에서 axis=0 이면 3개, axis=1 이면 2개.')],
  [T('배열에 비교 연산을 하면 **True/False 배열**이 나와요. True 는 1 이라서 `sum` 이 곧 **개수**예요.'),
   C(D('''
import numpy as np
stock = np.ones(6, dtype=int) * 5
sold = np.arange(6)
left = stock - sold * 2
print(left)
print(left <= 0)
print((left <= 0).sum())
print(left[left > 0])
print(left[left > 0].sum())
'''), '재고 5개씩 6칸, 칸 번호 × 2 만큼 판매'),
   steps(['조건 개수', '`(a <= 0).sum()` — 괄호를 꼭! `a <= 0.sum()` 은 문법 오류'], ['조건 비율', '`(a > 0).mean()` — True 의 비율'], ['골라내기', '`a[a > 0]` — 조건이 True 인 원소만 모은 1차원 배열'], ['배열끼리 연산', '모양이 같으면 같은 자리끼리: `stock - sold`']),
   exam('"배열을 만들고 → 다른 배열을 빼고 → 합과 0 이하의 개수를 구하라" — 2025 7번의 흐름이 위 코드 그대로예요.')]),
outq('[기출유사] 출력 결과는?', D('''
import numpy as np
a = [1, 2, 3]
b = np.array(a)
print(a * 2, (b * 2).tolist(), len(a + a), (b + b).tolist(), (b * b).sum())
'''), '리스트 `a * 2` 는 길이가 6 이 되고, 배열 `b * 2` 는 값이 2배가 돼요. `b * b` 는 원소별 제곱.'),
outq('[기출유사] 출력 결과는?', D('''
import numpy as np
m = np.arange(12).reshape(3, 4)
print(m.shape, m.ndim, m.size, len(m), m[1, 2], m[2].tolist(), m[:, 0].tolist())
'''), '`np.arange(12)` 는 0~11. 3행 4열로 놓으면 1행은 `[4 5 6 7]` 이에요.'),
outq('[기출유사] 출력 결과는?', D('''
import numpy as np
s = np.array([[90, 80, 70], [60, 100, 50]])
print(s.sum(axis=0).tolist(), s.sum(axis=1).tolist(), s.max(), s.mean(axis=1).tolist(), s.mean())
'''), 'axis=0 은 과목별(3개), axis=1 은 학생별(2개).'),
outq('[기출유사] 출력 결과는?', D('''
import numpy as np
seat = np.ones((3, 4), dtype=int) * 6
used = np.arange(12).reshape(3, 4)
left = seat - used
print(left[0].tolist(), (left <= 0).sum(), left[left > 0].sum(), (left < 0).sum(axis=1).tolist())
'''), '`left` 는 6 - (0~11). 0 이하는 6~11 의 여섯 칸, 음수는 7~11 의 다섯 칸(1행에 1개, 2행에 4개).'),
sh('[기출유사] `np.arange(2, 20, 3)` 의 원소는 몇 개?', 6, '2, 5, 8, 11, 14, 17 — range(2, 20, 3) 과 같아요.'),
spot('[기출유사] **예외가 발생하는 줄**은?', D('''
import numpy as np
a = np.arange(10)
b = a.reshape(2, 5)
c = b * 2
d = a.reshape(3, 4)
print(d.shape)
'''), 5, '원소 10개를 3 × 4 = 12칸에 놓을 수 없어 ValueError. 3번 줄의 reshape 은 a 를 바꾸지 않으므로 a 는 여전히 10개짜리 1차원이에요.'),
ch('[기출유사] `np.ones((2, 3))` 에 대한 설명으로 옳은 것은?', ['shape 이 (3, 2) 이고 원소는 정수 1', 'shape 이 (2, 3) 이고 원소는 실수 1.0', '원소가 2 와 3 인 1차원 배열', '1 이 5개인 1차원 배열'], 2, '튜플 `(2, 3)` 은 2행 3열이라는 뜻이고, ones 의 기본 자료형은 실수예요. 정수로 만들려면 `dtype=int`.'),
match('`m = np.array([[1, 2, 3], [4, 5, 6]])` 일 때 표현과 결과를 이어 보세요.', [['m.shape', '(2, 3)'], ['m.sum()', '21'], ['m.sum(axis=0).tolist()', '[5, 7, 9]'], ['m.sum(axis=1).tolist()', '[6, 15]'], ['m[:, 1].tolist()', '[2, 5]'], ['m[1].tolist()', '[4, 5, 6]'], ['m.size', '6']]),
fill('[기출유사] 1~6 을 2행 3열로 놓고 **열별 평균**을 구해요.', D('''
import numpy as np
m = np.arange(1, 7).___(2, 3)
print(m.mean(axis=___).tolist())
'''), ['reshape', '0'], expect='[2.5, 3.5, 4.5]'),
outq('[심화] 출력 결과는?', D('''
import numpy as np
h = np.array([150, 162, 171, 158, 180])
tall = h >= 160
print(tall.tolist(), tall.sum(), tall.mean(), h[tall].mean(), h[~tall].tolist())
'''), '`tall.mean()` 은 True 의 비율(3/5). `~tall` 은 True 와 False 를 뒤집어요 — 160 미만인 사람만 남아요.'),
essay('[기출유사 · 서술 5점] `a = [1, 2, 3]` 과 `b = np.array([1, 2, 3])` 에 대해 `a * 2` 와 `b * 2` 의 **결과를 각각 쓰고**, 왜 다른지 설명하세요. 또 리스트 `a` 의 모든 원소를 2배로 만들려면 어떻게 써야 하는지 쓰세요.', 'a * 2 는 [1, 2, 3, 1, 2, 3] 이고 b * 2 는 [2 4 6] 이다. 리스트의 * 는 리스트를 그 횟수만큼 반복해 이어 붙이는 연산이고, numpy 배열의 * 는 각 원소에 대해 따로 계산하는 원소별 연산이기 때문이다. 리스트의 원소를 2배로 만들려면 [x * 2 for x in a] 처럼 컴프리헨션(또는 반복문)을 써야 한다.', ['a * 2 의 결과를 [1, 2, 3, 1, 2, 3] 으로 썼다', 'b * 2 의 결과를 [2 4 6] 으로 썼다', '리스트는 반복, 배열은 원소별 연산이라고 차이를 썼다', '컴프리헨션이나 반복문으로 리스트 원소를 2배 하는 방법을 썼다']),
ox('`a = np.arange(6)` 에서 `a.reshape(2, 3)` 을 실행하면 `a.shape` 이 `(2, 3)` 으로 바뀐다.', False, '`reshape` 은 새 배열을 **돌려줄** 뿐이에요. `a = a.reshape(2, 3)` 으로 다시 담아야 해요.'),
prac('[기출유사 · 15점] 성적 배열 분석', '첫 줄에 학생 수 `n` 과 과목 수 `m`, 이어서 n 줄에 학생별 m 과목 점수(정수)가 주어져요.\n\n출력(한 줄씩)\n1. `n행 m열`  ← 배열의 `shape` 에서 꺼낼 것\n2. `전체 평균: X.XX`\n3. `학생별 평균:` 뒤에 소수 첫째 자리까지 공백 구분\n4. `과목별 최고:` 뒤에 공백 구분\n5. `전체 평균 이상: K개` (전체 평균 이상인 **점수**의 개수)\n6. `만점자: K명` (모든 과목이 100 인 학생 수)\n\n[조건] ○ 점수는 2차원 numpy 배열로 만들 것 ○ 합·평균·최대를 구하는 **반복문 금지** (`axis` 사용) ○ 6번은 학생별 최솟값을 이용할 것',
D('''
import numpy as np
n, m = map(int, input().split())
s = np.array([list(map(int, input().split())) for _ in range(n)])
r, c = s.shape
print(f"{r}행 {c}열")
avg = s.mean()
print(f"전체 평균: {avg:.2f}")
print("학생별 평균:", " ".join(f"{x:.1f}" for x in s.mean(axis=1)))
print("과목별 최고:", " ".join(str(x) for x in s.max(axis=0)))
print(f"전체 평균 이상: {(s >= avg).sum()}개")
print(f"만점자: {(s.min(axis=1) == 100).sum()}명")
'''), ['2 3\n90 80 70\n60 100 50', '1 1\n100', '3 2\n100 100\n100 99\n100 100', '4 4\n10 20 30 40\n50 60 70 80\n90 100 0 5\n15 25 35 45', '2 5\n0 0 0 0 0\n0 0 0 0 0', '3 3\n77 88 99\n66 55 44\n100 100 100'],
  starter=D('''
import numpy as np
n, m = map(int, input().split())
s = np.array([list(map(int, input().split())) for _ in range(n)])
r, c = s.shape
print(f"{r}행 {c}열")
# 이어서 작성
'''), hints=['학생별 = 행마다 = `axis=1`, 과목별 = 열마다 = `axis=0`', '출력: `" ".join(f"{x:.1f}" for x in s.mean(axis=1))`', '개수: `(s >= avg).sum()` / 만점자: `(s.min(axis=1) == 100).sum()`'], ex='"한 학생의 **최솟값**이 100 이면 모든 과목이 100" — 조건을 통계로 바꾸는 생각이 numpy 문제의 핵심이에요. 반복문으로 한 명씩 검사하던 일을 한 줄로 해요.'),
prac('[기출유사 · 12점] 사물함 재고 차감', '`r` 행 `c` 열의 진열대에 물건이 칸마다 `k` 개씩 있어요. 칸 번호는 왼쪽 위부터 0, 1, 2, … 순서로 매기고, **칸 번호 × d 개**씩 팔렸어요.\n\n입력: 한 줄에 `r c k d` (정수)\n\n출력\n1. 남은 수량을 행마다 한 줄씩, 공백 구분 (음수도 그대로 출력)\n2. `재고 부족: N칸` (남은 수량이 0 이하인 칸 수)\n3. `남은 합계: S` (0 보다 큰 칸의 수량만 더한 값)\n4. `행별 부족: ` 뒤에 행마다 0 이하인 칸 수를 공백 구분\n\n[조건] ○ 처음 재고는 `np.ones((r, c), dtype=int) * k`, 판매량은 `np.arange(r * c).reshape(r, c) * d` 로 만들 것 ○ 2~4번에 반복문으로 세지 말 것',
D('''
import numpy as np
r, c, k, d = map(int, input().split())
stock = np.ones((r, c), dtype=int) * k
sold = np.arange(r * c).reshape(r, c) * d
left = stock - sold
for row in left:
    print(*row.tolist())
print(f"재고 부족: {(left <= 0).sum()}칸")
print(f"남은 합계: {left[left > 0].sum()}")
print("행별 부족:", *(left <= 0).sum(axis=1).tolist())
'''), ['2 3 5 2', '1 1 10 3', '3 4 6 1', '2 2 0 5', '3 3 20 3', '4 2 7 7'],
  starter=D('''
import numpy as np
r, c, k, d = map(int, input().split())
stock = np.ones((r, c), dtype=int) * k
sold = np.arange(r * c).reshape(r, c) * d
left = stock - sold
for row in left:
    print(*row.tolist())
# 이어서 작성
'''), hints=['부족한 칸 수: `(left <= 0).sum()`', '양수만 더하기: `left[left > 0].sum()`', '행별: `(left <= 0).sum(axis=1)` — 행마다 True 의 수'], ex='`np.ones` 에 `dtype=int` 를 빼면 `5.0 3.0 1.0` 처럼 실수로 출력돼요. 실제 시험의 출력 추론에서도 **`1.` 과 `1` 의 차이**를 물어요.'),
prac('[심화 · 14점] 기온 관측표', '`d` 일 동안 하루 4번(새벽·아침·낮·밤) 잰 기온이 주어져요.\n\n입력: 첫 줄 `d`, 이어서 d 줄에 정수 4개.\n\n출력\n1. `일교차:` 뒤에 날마다 (최고 - 최저) 를 공백 구분\n2. `일교차 최대: N일차` (같으면 가장 빠른 날)\n3. `시간대 평균:` 뒤에 새벽·아침·낮·밤 순서로 소수 첫째 자리까지 공백 구분\n4. `전체 평균 초과: K회` (전체 평균보다 **큰** 측정값의 수)\n5. `영하 없는 날: K일` (네 번 모두 0 이상인 날 수)\n6. `가장 추운 시간대: 이름` (시간대 평균이 가장 낮은 곳, 같으면 앞의 것)\n\n[조건] ○ 기온은 `(d, 4)` 모양의 numpy 배열 ○ 1·3·4·5번은 반복문으로 계산하지 말 것 (출력을 위한 join/반복은 괜찮아요)',
D('''
import numpy as np
d = int(input())
t = np.array([list(map(int, input().split())) for _ in range(d)])
gap = t.max(axis=1) - t.min(axis=1)
print("일교차:", *gap.tolist())
g = gap.tolist()
print(f"일교차 최대: {g.index(max(g)) + 1}일차")
part = t.mean(axis=0)
print("시간대 평균:", " ".join(f"{x:.1f}" for x in part))
print(f"전체 평균 초과: {(t > t.mean()).sum()}회")
print(f"영하 없는 날: {(t.min(axis=1) >= 0).sum()}일")
names = ["새벽", "아침", "낮", "밤"]
p = part.tolist()
print(f"가장 추운 시간대: {names[p.index(min(p))]}")
'''), ['3\n-2 1 8 3\n0 2 5 1\n-5 -1 9 2', '1\n10 10 10 10', '2\n-1 -2 -3 -4\n4 3 2 1', '4\n0 0 0 0\n-1 5 12 6\n3 7 15 9\n2 2 14 2', '2\n5 1 9 1\n1 5 1 9', '3\n-10 -3 2 -6\n-8 -1 4 -4\n-12 -5 0 -7'],
  hints=['일교차: `t.max(axis=1) - t.min(axis=1)` — 배열끼리 빼요.', '가장 큰 날: 리스트로 바꿔 `g.index(max(g)) + 1` (index 는 처음 것을 찾아요)', '영하 없는 날: `(t.min(axis=1) >= 0).sum()`'], ex='행 방향(날짜별)과 열 방향(시간대별)을 **한 문제에서 모두** 썼어요. "~별"이라는 말이 나오면 결과가 몇 개여야 하는지부터 세고 axis 를 정하세요: 날짜별이면 d 개 → `axis=1`, 시간대별이면 4개 → `axis=0`.'),
)
G9['libs'] = ['numpy']

# ============================================================ G10
G10 = lesson('10강. 만점 모의고사 — 2학기 1차 고사 실전', 60,
'- 시간 배분: 소형 문항(출력 추론·서술) 20분 → 중형 15분 → 대형 20분 → 검토 5분\n- 클래스 출력 추론: **MRO 를 한 줄로 적고** super() 마다 오른쪽으로 한 칸\n- 서술형 3요소: **이름**(어떤 오류) + **이유**(왜) + **해결**(어떻게)\n- 파일 문제: 모드 · `\\n` · strip — 세 가지만 점검\n- 예외 문제: "어느 줄이 **먼저** 실패하는가"\n- numpy: "~별"의 개수로 axis 를 정한다',
review('🔁 마스터의 스킬 [γ] 총정리', [T('아홉 강의 핵심을 한 장씩 확인해요.'), flip(['1강 — finally 와 return', 'return 값이 정해진 뒤 finally 실행, 그다음 함수 종료'], ['2강 — "w" 모드', '여는 순간 기존 내용이 지워짐'], ['3강 — try 의 위치', '반복문 안(줄 단위)에 둬야 나머지 줄을 계속 처리'], ['4강 — import 될 때의 __name__', '모듈 이름 ("__main__" 이 아님)'], ['5강 — self.count += 1', '클래스 변수는 그대로, 인스턴스에 새 변수'], ['6강 — super()', '실제 객체의 MRO 에서 다음 클래스'], ['7강 — 밖에서 obj.__x = 0', '오류 없이 새 속성, 진짜 값은 그대로'], ['8강 — __add__ 의 세 가지', '새 객체 · return · 원본 불변'], ['9강 — axis=0', '열마다 하나 (행 방향으로 합침)'])]),
explain('모의고사 안내',
  [T('실제 1차 고사와 같은 구성이에요. 확인 문제 8개는 소형 문항, 실습 4개는 중·대형 문항이에요. **50분** 타이머를 켜고 풀어 보세요.'),
   steps(['소형 문항 (46점)', '출력 추론 4 · 서술 2 · 오류 줄 찾기 1 · 선택 1'], ['중형 문항 (26점)', '실습 9번(12점), 10번(14점)'], ['대형 문항 (28점)', '실습 11번(14점), 12번(14점)']),
   exam('틀린 문제는 🔁 오답 복습으로 다시 풀고 해당 강의 설명을 다시 읽으세요. 이어서 **The MASTER [γ]** 문제로 몸에 익히면 준비가 끝나요.')]),
outq('[모의 1 · 6점] 출력 결과는?', D('''
class Device:
    def __init__(self, name):
        self.name = name
        print("D", end=" ")
    def info(self):
        return f"{self.name}:{self.power()}"
    def power(self):
        return 0
class Phone(Device):
    def __init__(self, name, battery):
        print("P1", end=" ")
        super().__init__(name)
        self.battery = battery
        print("P2", end=" ")
    def power(self):
        return self.battery
class Tablet(Phone):
    def power(self):
        return super().power() * 2
t = Tablet("탭", 40)
print()
print(t.info(), Phone("폰", 30).info())
''')),
outq('[모의 2 · 8점] 출력 결과는?', D('''
class Person:
    def __init__(self, name):
        self.name = name
    def role(self):
        return "P"
class Student(Person):
    def role(self):
        return "S" + super().role()
class Worker(Person):
    def role(self):
        return "W" + super().role()
class Intern(Student, Worker):
    def __eq__(self, other):
        return self.name == other.name
a = Intern("민")
b = Intern("민")
c = a
print(a == b, a is b, a is c, id(a) == id(c))
print(a.role(), Student("솔").role())
print([k.__name__ for k in Intern.mro()][:4])
''')),
essay('[모의 3 · 6점] 아래 코드의 마지막 줄에서 발생하는 **오류의 이름과 이유**를 쓰고, 포인트를 올바르게 출력하도록 고치는 방법을 서술하세요.\n\n```\nclass Card:\n    def __init__(self):\n        self.__point = 100\n    def use(self, n):\n        self.__point -= n\nc = Card()\nc.use(30)\nprint(c.__point)\n```', 'AttributeError 가 발생한다. __point 는 밑줄 두 개로 시작하는 private 속성이어서 클래스 외부에서는 그 이름으로 접근할 수 없기 때문이다(내부적으로 _Card__point 로 이름이 바뀐다). 클래스 안에 def get_point(self): return self.__point 와 같은 getter 메서드를 추가하고, print(c.get_point()) 로 출력한다.', ['AttributeError 라고 썼다', 'private 속성이라 클래스 밖에서 접근할 수 없다고 이유를 썼다', 'getter 메서드를 정의했다', 'getter 를 호출해 출력하도록 고쳤다']),
essay('[모의 4 · 5점] `util.py` 의 맨 아래에 `print(double(5))` 라는 테스트 코드가 있어요. `main.py` 에서 `import util` 을 하면 원하지 않는 `10` 이 출력돼요. **이유**를 쓰고, `util.py` 를 직접 실행할 때만 테스트가 돌도록 고치는 코드를 쓰세요.', 'import 를 하면 그 모듈 파일의 코드가 위에서 아래로 모두 실행되므로, 함수 정의 아래에 있는 print(double(5)) 도 함께 실행되어 10 이 출력된다. 테스트 코드를 if __name__ == "__main__": 아래로 옮기면 된다. 파일을 직접 실행하면 __name__ 이 "__main__" 이라 테스트가 실행되고, import 될 때는 __name__ 이 "util" 이라 실행되지 않는다.', ['import 하면 모듈의 코드가 전부 실행된다고 이유를 썼다', 'if __name__ == "__main__": 를 정확히 썼다', '직접 실행하면 __name__ 이 "__main__" 이라고 썼다', 'import 될 때는 __name__ 이 모듈 이름이라 실행되지 않는다고 썼다']),
outq('[모의 5 · 6점] 출력 결과는?', D('''
def pick(d, keys):
    out = []
    for k in keys:
        try:
            v = d[k]
            out.append(10 // v)
        except KeyError:
            out.append("K")
        except ZeroDivisionError:
            out.append("Z")
        else:
            out.append("+")
        finally:
            out.append("|")
    return out
print(*pick({"a": 2, "b": 0, "c": 5}, ["a", "x", "b"]))
''')),
spot('[모의 6 · 5점] `log.txt` 는 처음에 없는 파일이에요. **예외가 발생하는 줄**은?', D('''
with open("log.txt", "a") as f:
    f.write("start\\n")
with open("log.txt") as f:
    lines = f.readlines()
count = len(lines)
with open("log.txt", "w") as f:
    f.write("count=" + count)
print("done")
'''), 7, '`"a"` 모드는 없는 파일을 만들어 주므로 1번 줄은 정상이에요. 7번 줄에서 문자열과 정수를 `+` 해서 TypeError — `str(count)` 로 바꿔야 해요.'),
outq('[모의 7 · 6점] 출력 결과는?', D('''
import numpy as np
m = np.arange(1, 9).reshape(2, 4)
n = np.ones((2, 4), dtype=int) * 4
d = m - n
print(d.tolist())
print(d.sum(axis=0).tolist(), d.sum(axis=1).tolist(), (d > 0).sum(), d[d < 0].sum())
''')),
ch('[모의 8 · 4점] 클래스 변수 `count = 0` 을 가진 `Robot` 클래스에서, **만들어진 로봇의 총 개수**를 세려고 해요. `__init__` 에 넣을 코드로 옳은 것은?', ['`count += 1`', '`self.count += 1`', '`Robot.count += 1`', '`self.count = 1`'], 3, '①은 지역 변수 count 를 찾다가 UnboundLocalError, ②는 인스턴스마다 자기 count 가 1 이 될 뿐이에요. 클래스 변수는 **클래스 이름으로** 고쳐요.'),
prac('[모의 9 · 12점] 영상 길이 Duration', '영상 길이를 나타내는 `Duration` 클래스를 만들어요.\n\n- `__init__(self, m, s)` : 분, 초. 초가 60 이상이면 분으로 올리고, **전체가 음수면 0분 0초**로 저장\n- `__add__`, `__sub__` : 결과는 새 Duration (뺄셈 결과가 음수면 0분 0초)\n- `__eq__`, `__lt__` : 길이로 비교\n- `__str__` : `M:SS` (초는 두 자리)\n\n입력: 첫 줄 `n`, 이어서 n 줄에 `분 초` (0 이상의 정수, 초는 60 이상일 수 있어요)\n\n출력\n1. 정리된 길이를 입력 순서대로 공백 구분\n2. `전체: ` 모든 영상을 더한 길이\n3. `가장 긴 영상: ` / `가장 짧은 영상: ` (각각 한 줄)\n4. `첫 영상 빼고: ` 전체에서 첫 영상을 뺀 길이\n5. `첫 영상 - 전체: ` 첫 영상에서 전체를 뺀 길이\n6. `첫 영상과 같은 길이: K개` (첫 영상 자신은 제외)\n\n[조건] ○ 초 단위로 바꿔 정리하는 코드는 **`__init__` 에만** ○ 최대·최소는 `max`, `min` 에 key 없이',
D('''
class Duration:
    def __init__(self, m, s):
        total = max(0, m * 60 + s)
        self.m = total // 60
        self.s = total % 60
    def sec(self):
        return self.m * 60 + self.s
    def __add__(self, o):
        return Duration(0, self.sec() + o.sec())
    def __sub__(self, o):
        return Duration(0, self.sec() - o.sec())
    def __eq__(self, o):
        return self.sec() == o.sec()
    def __lt__(self, o):
        return self.sec() < o.sec()
    def __str__(self):
        return f"{self.m}:{self.s:02d}"
n = int(input())
vs = []
for _ in range(n):
    m, s = map(int, input().split())
    vs.append(Duration(m, s))
print(*vs)
total = vs[0]
for v in vs[1:]:
    total = total + v
print("전체:", total)
print("가장 긴 영상:", max(vs))
print("가장 짧은 영상:", min(vs))
print("첫 영상 빼고:", total - vs[0])
print("첫 영상 - 전체:", vs[0] - total)
print(f"첫 영상과 같은 길이: {sum(1 for v in vs[1:] if v == vs[0])}개")
'''), ['3\n3 45\n2 90\n0 30', '1\n0 0', '4\n1 0\n0 60\n0 59\n1 0', '2\n10 5\n0 605', '3\n0 125\n2 5\n1 65', '2\n59 59\n0 1'],
  hints=['`total = max(0, m * 60 + s)` 뒤 `// 60`, `% 60` — 모든 정리가 이 세 줄에 있어요.', '`__add__` 는 `Duration(0, 두 길이의 초 합)` 을 return 하면 생성자가 정리해 줘요.', '`f"{self.m}:{self.s:02d}"`']),
prac('[모의 10 · 14점] 도서 대출 기록 분석', '도서관의 책 목록과 대출 기록을 처리해요.\n\n입력: 첫 줄 `b`, 이어서 b 줄에 `책코드 제목` (제목은 공백 없음). 다음 줄 `k`, 이어서 k 줄에 기록 `학생,책코드,일수`.\n\n1. 책 목록을 `books.txt`, 기록을 `loan.csv` 에 저장한 뒤 **파일을 읽어** 처리해요.\n2. 기록 한 줄마다 이 순서로 검사해요. 쉼표로 나눈 조각이 3개가 아님 → `형식` / 없는 책코드 → `코드` / 일수가 정수가 아니거나 1 미만 → `일수`\n3. 정상 기록으로 **책별 대출 횟수**와 **학생별 총 대출 일수**를 구해요.\n4. `report.txt` 에 저장: 한 번 이상 대출된 책을 `제목 N회` (횟수 내림차순, 같으면 제목 사전순) → 이어서 `최다 대출 학생: 이름 (D일)` (같으면 이름 사전순으로 앞선 학생). 정상 기록이 없으면 `대출 없음` 한 줄만.\n\n출력: 오류 기록을 `N번 기록: 이유` 로 순서대로 → `report.txt` 의 내용 그대로.\n\n[조건] ○ 없는 책코드는 **KeyError**, 형식·일수는 **ValueError** 를 각각의 except 로 처리 ○ 기록은 줄 단위로 try',
D('''
b = int(input())
with open("books.txt", "w", encoding="utf-8") as f:
    for _ in range(b):
        f.write(input() + "\\n")
k = int(input())
with open("loan.csv", "w", encoding="utf-8") as f:
    for _ in range(k):
        f.write(input() + "\\n")
title = {}
with open("books.txt", encoding="utf-8") as f:
    for line in f:
        code, name = line.split()
        title[code] = name
cnt = {}
days = {}
with open("loan.csv", encoding="utf-8") as f:
    for no, line in enumerate(f, 1):
        parts = line.strip().split(",")
        try:
            if len(parts) != 3:
                raise ValueError("형식")
            who, code, d = parts
            name = title[code]
            try:
                d = int(d)
            except ValueError:
                raise ValueError("일수")
            if d < 1:
                raise ValueError("일수")
            cnt[name] = cnt.get(name, 0) + 1
            days[who] = days.get(who, 0) + d
        except KeyError:
            print(f"{no}번 기록: 코드")
        except ValueError as e:
            print(f"{no}번 기록: {e}")
with open("report.txt", "w", encoding="utf-8") as f:
    if not cnt:
        f.write("대출 없음\\n")
    else:
        for name in sorted(cnt, key=lambda x: (-cnt[x], x)):
            f.write(f"{name} {cnt[name]}회\\n")
        top = sorted(days, key=lambda x: (-days[x], x))[0]
        f.write(f"최다 대출 학생: {top} ({days[top]}일)\\n")
with open("report.txt", encoding="utf-8") as f:
    print(f.read().strip())
'''), ['3\nB1 파이썬\nB2 알고리즘\nB3 자료구조\n6\n민,B1,7\n솔,B9,3\n율,B1,삼일\n민,B2,3\n솔,B1\n솔,B2,10', '1\nX 책\n2\n가,Y,1\n가,X,0', '2\nA 나무\nB 가지\n4\n민,A,5\n솔,B,5\n율,B,1\n민,B,1', '1\nQ 수학의정석\n3\nk,Q,2\nk,Q,2\nm,Q,4', '2\nP1 a\nP2 b\n3\n,,\nx,P1,1.5\ny,P2,1,1'],
  hints=['검사 순서가 코드의 순서예요: 조각 수 → `title[code]` (KeyError) → `int(d)` → 범위', '`int()` 의 ValueError 는 안쪽 try 로 잡아 `raise ValueError("일수")` 로 바꿔요.', '정렬 key: `(-횟수, 제목)`, `(-일수, 이름)`']),
prac('[모의 11 · 14점] 회원과 VIP 회원', '쇼핑몰 회원 클래스를 만들어요.\n\n`Member`\n- `__init__(self, name)` : 이름(공개), 포인트(**private**, 0)\n- `get_point(self)` : getter\n- `rate(self)` : 적립률 → `1` (퍼센트)\n- `buy(self, price)` : `price * self.rate() // 100` 포인트를 적립하고 적립된 포인트를 return\n- `use(self, n)` : n 이 1 이상이고 가진 포인트 이하이면 차감하고 True, 아니면 False\n- `__str__(self)` : `이름 [일반] N점`\n\n`VipMember(Member)`\n- `__init__(self, name, level)` : level 은 1~3\n- `rate(self)` : `1 + level * 2`\n- `__str__(self)` : 부모의 결과에서 `[일반]` 을 `[VIP레벨]` 로 바꾼 문자열 (예: `솔 [VIP2] 150점`)\n\n입력: 첫 줄 `n`, 이어서 n 줄에 `일반 이름` 또는 `VIP 이름 레벨`. 그다음 명령들: `구매 이름 금액` → `P점 적립` / `사용 이름 포인트` → `사용 완료` 또는 `포인트 부족` / `조회 이름` → print(회원) / `종료`. 없는 이름이면 `없는 회원`.\n\n마지막에 `VIP 회원 수: K명` 과 `총 포인트: T점` 을 한 줄씩 출력해요.\n\n[조건] ○ `buy` 는 Member 에만 작성 (VipMember 에서 다시 만들지 않음) ○ 포인트는 밑줄 두 개 ○ VIP 수는 **isinstance** 로',
D('''
class Member:
    def __init__(self, name):
        self.name = name
        self.__point = 0
    def get_point(self):
        return self.__point
    def rate(self):
        return 1
    def buy(self, price):
        p = price * self.rate() // 100
        self.__point += p
        return p
    def use(self, n):
        if 1 <= n <= self.__point:
            self.__point -= n
            return True
        return False
    def __str__(self):
        return f"{self.name} [일반] {self.__point}점"
class VipMember(Member):
    def __init__(self, name, level):
        super().__init__(name)
        self.level = level
    def rate(self):
        return 1 + self.level * 2
    def __str__(self):
        return super().__str__().replace("[일반]", f"[VIP{self.level}]")
n = int(input())
members = {}
for _ in range(n):
    p = input().split()
    if p[0] == "VIP":
        members[p[1]] = VipMember(p[1], int(p[2]))
    else:
        members[p[1]] = Member(p[1])
while True:
    cmd = input().split()
    if cmd[0] == "종료":
        break
    try:
        m = members[cmd[1]]
    except KeyError:
        print("없는 회원")
        continue
    if cmd[0] == "구매":
        print(f"{m.buy(int(cmd[2]))}점 적립")
    elif cmd[0] == "사용":
        print("사용 완료" if m.use(int(cmd[2])) else "포인트 부족")
    elif cmd[0] == "조회":
        print(m)
print(f"VIP 회원 수: {sum(isinstance(m, VipMember) for m in members.values())}명")
print(f"총 포인트: {sum(m.get_point() for m in members.values())}점")
'''), ['2\n일반 민\nVIP 솔 2\n구매 민 10000\n구매 솔 10000\n사용 민 200\n사용 솔 200\n조회 민\n조회 솔\n조회 율\n종료', '1\n일반 가\n사용 가 0\n구매 가 99\n조회 가\n종료', '3\nVIP a 1\nVIP b 3\n일반 c\n구매 a 5000\n구매 b 5000\n구매 c 5000\n사용 b 350\n사용 b 1\n조회 b\n종료', '1\nVIP z 3\n구매 z 1234\n구매 z 1\n사용 z 86\n조회 z\n구매 y 1\n종료', '2\n일반 p\n일반 q\n종료'],
  hints=['`buy` 안에서 `self.rate()` 를 부르면, VIP 객체일 때는 **VipMember 의 rate** 가 실행돼요. 그래서 buy 를 다시 만들 필요가 없어요.', 'VipMember 안에서는 `self.__point` 를 쓸 수 없어요(이름이 `_VipMember__point` 로 바뀜). `super().__str__()` 의 결과를 가공하세요.', '`super().__str__().replace("[일반]", f"[VIP{self.level}]")`']),
prac('[모의 12 · 14점] 영화관 좌석 판매', '`r` 행 `c` 열의 좌석 가격표와 판매 여부가 주어져요.\n\n입력: 첫 줄 `r c`. 이어서 r 줄에 좌석 가격(정수 c 개), 그다음 r 줄에 판매 여부(0 또는 1, c 개).\n\n출력\n1. `매출: S원` (팔린 좌석의 가격 합)\n2. `판매율: X.X%` (팔린 좌석 수 / 전체 좌석 수 × 100, 소수 첫째 자리)\n3. `행별 매출:` 뒤에 공백 구분\n4. `열별 빈 좌석:` 뒤에 공백 구분\n5. `매진된 행: K개` (그 행의 모든 좌석이 팔린 행)\n6. `남은 좌석 최고가: P원` — 빈 좌석 중 가장 비싼 가격. 빈 좌석이 없으면 `전석 매진`\n\n[조건] ○ 가격과 판매 여부는 각각 `(r, c)` 모양의 numpy 배열 ○ 매출은 **두 배열의 곱**으로 구할 것 ○ 1~5번에 계산용 반복문 금지',
D('''
import numpy as np
r, c = map(int, input().split())
price = np.array([list(map(int, input().split())) for _ in range(r)])
sold = np.array([list(map(int, input().split())) for _ in range(r)])
income = price * sold
print(f"매출: {income.sum()}원")
print(f"판매율: {sold.mean() * 100:.1f}%")
print("행별 매출:", *income.sum(axis=1).tolist())
print("열별 빈 좌석:", *(sold == 0).sum(axis=0).tolist())
print(f"매진된 행: {(sold.min(axis=1) == 1).sum()}개")
empty = price[sold == 0]
if empty.size == 0:
    print("전석 매진")
else:
    print(f"남은 좌석 최고가: {empty.max()}원")
'''), ['2 3\n9000 12000 9000\n8000 10000 8000\n1 1 0\n1 1 1', '1 1\n5000\n0', '2 2\n100 200\n300 400\n1 1\n1 1', '3 4\n1 2 3 4\n5 6 7 8\n9 10 11 12\n0 0 0 0\n1 0 1 0\n1 1 1 1', '3 2\n7000 7000\n8000 8000\n9000 9000\n1 0\n0 1\n0 0', '2 5\n10 20 30 40 50\n50 40 30 20 10\n1 1 1 0 0\n0 0 1 1 1'],
  hints=['`income = price * sold` — 안 팔린 좌석은 가격 × 0 = 0 이 돼요.', '판매율: 0/1 배열의 평균이 곧 비율 → `sold.mean() * 100`', '빈 좌석 가격: `price[sold == 0]` — 비어 있으면 `.size == 0`'], ex='**마스터의 스킬 [γ] 를 끝냈어요.** 예외·파일·모듈·클래스·numpy — 2학기 1차의 모든 범위를 "왜 그렇게 되는지"까지 다뤘어요. 이제 The MASTER [γ] 문제로 몸에 익히세요. 예비 마스터 여러분을 응원합니다!'),
)
G10['libs'] = ['numpy']
