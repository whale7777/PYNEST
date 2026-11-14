import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lotc import *

C = Course('δ', '1학년 2학기 2차고사 범위: 내장함수 직접 구현(max·sum·set·count)과 회문·최빈 문자, '
           'lambda·map·filter·컴프리헨션, sorted(key)·max(key)·all·any, enumerate·divmod·진수 변환, '
           '선택정렬·버블정렬 직접 구현(조기 종료), 이터레이터(__iter__·__next__·StopIteration), '
           '제너레이터(yield·제너레이터 표현식·메모리 차이), 모듈 분리와 __name__, 파일 모드·경로·인코딩·누적, '
           '예외 처리 종합(try·except·else·raise), numpy 심화 기초(where·행/열 슬라이싱·boolean indexing·sort·argsort)')

# =====================================================================
L = C.lesson('δ-01 시작하기: 2학기 2차 시험 지도 + γ 실력 점검', 20,
'''- 2학기 2차는 **"내장함수 쓰기/안 쓰기"·이터레이터·제너레이터·파일·예외·numpy** 가 중심이에요.
- 2025년엔 numpy 만 5문항(약 50점)! 출력 추론으로 대비해요.
- γ 내용(try/except, with open, 클래스, numpy 기초)은 2차에서 **도구**로 계속 써요.
- 이 코스는 개념 → 확인 문제 → 기출유사 실습 순서. 다 끝나면 **A.C.E. [δ]** 로 실전!''')

L.explain('이번 시험은 이렇게 나와요',
    [T('1학년 2학기 **2차고사(기말)** 는 8~13문항, 100점이에요.\n'
       '문항은 크게 다섯 모양으로 나와요.'),
     STEPS(('A 출력 추론 (4~10점)', 'sorted(key=)·all·enumerate·divmod·numpy 슬라이싱 코드의 출력을 손으로 적어요.'),
           ('B 같은 일 두 가지로 (6~12점)', '"sorted 를 써서 / 쓰지 않고", "set 을 써서 / 쓰지 않고" 처럼 **쌍**으로 작성해요.'),
           ('C 직접 구현 (13~18점)', '선택정렬·버블정렬, 이터레이터 클래스(__iter__/__next__)를 직접 써요.'),
           ('D 파일 + 예외 프로그램 (12~14점)', '환율 계산기·노래자랑 점수처럼 파일을 읽고 쓰며 try/except 로 오류를 처리해요.'),
           ('E 서술형', '"리스트 컴프리헨션과 제너레이터 표현식의 메모리 차이", "왜 오류인가" 를 써요.'))],
    [T('3년 동안 나온 소재를 먼저 기억해 두세요.\n'
       '이 코스의 예제도 이 소재들을 **구조를 바꿔서** 다뤄요.'),
     FLIP(['내장함수 사용/미사용 쌍', '가장 큰 두 수 합·중복 제거·제곱 정렬 (2023)'],
          ['sorted(key=)·max(key=)·all/any', '3년 연속 — 출력 추론과 딕셔너리'],
          ['정렬 직접 구현', '선택정렬 + 버블정렬 조기 종료 (2024, 18점)'],
          ['이터레이터', '__iter__·__next__·StopIteration (2024·2025)'],
          ['제너레이터', '제너레이터 표현식 변환, 메모리 차이 서술'],
          ['파일·예외', '모드 r/w/a, 인코딩, FileNotFoundError, 환율 계산기'],
          ['numpy', '2025년 5문항 — where·슬라이싱·boolean·sort·argsort'])],
    [T('공부 순서는 이렇게 추천해요.\n\n'
       '1. 레슨 하나를 끝까지(복습 → 개념 → 확인 → 실습).\n'
       '2. 틀린 문제는 🔁 오답 복습에서 다시.\n'
       '3. 모든 레슨이 끝나면 **A.C.E. [δ]** 문제집으로 실전 연습.'),
     EXAM('"sorted() 를 사용하지 않고" 같은 [조건]은 **채점 기준**이에요. 자동 채점은 결과만 보지만, 시험에선 조건을 어기면 감점돼요.')])

L.choice('2025년 2학기 2차에서 **가장 많은 문항**이 나온 영역은?',
    ['재귀 함수', 'numpy 배열(where·슬라이싱·정렬)', '거북이 그래픽', '변수 이름 규칙'], 2,
    '2025년엔 numpy 문항이 5개(약 50점)였어요. 사이트에선 numpy 가 실행되지 않으니 **출력 추론 문제**로 손에 익혀요.')

L.explain('γ 점검 ① 예외 처리',
    [T('`try` 안에서 오류가 나면 **바로** 맞는 `except` 로 뛰어가요.\n'
       '오류가 **없을 때만** `else` 가 실행되고, `raise` 는 일부러 오류를 일으켜요.'),
     CODE('''for s in ["12", "abc"]:
    try:
        n = int(s)
    except ValueError:
        print(s, "→ 숫자가 아니에요")
    else:
        print(s, "→", n * 2)''', 'try / except / else')],
    [T('`raise ValueError("메시지")` 로 직접 만든 오류도 `except ValueError as e:` 로 잡을 수 있어요.\n'
       '`e` 를 출력하면 넣어 둔 메시지가 나와요.'),
     CODE('''def check_age(n):
    if n < 0:
        raise ValueError("나이는 음수일 수 없어요")
    return n

try:
    check_age(-3)
except ValueError as e:
    print("오류:", e)''', 'raise 와 as e')])

L.output('출력 결과를 그대로 쓰세요.', '''\
data = ["5", "x", "0"]
for s in data:
    try:
        print(10 // int(s))
    except ValueError:
        print("V")
    except ZeroDivisionError:
        print("Z")
    else:
        print("ok")''',
    '"5" 는 정상 → 2 출력 후 else 의 ok. "x" 는 int() 에서 ValueError → V. "0" 은 나눗셈에서 ZeroDivisionError → Z.\n\n```\n{out}\n```')

L.explain('γ 점검 ② 파일과 with',
    [T('`with open(파일, 모드, encoding=...) as f:` 는 블록이 끝나면 **파일을 자동으로 닫아요**.\n'
       '모드 `w` 는 새로 쓰기, `r` 는 읽기예요. 한 줄씩 읽을 땐 `for line in f:` 와 `strip()`!'),
     CODE('''with open("memo.txt", "w", encoding="utf-8") as f:
    f.write("사과,3\\n")
    f.write("배,5\\n")

with open("memo.txt", "r", encoding="utf-8") as f:
    for line in f:
        name, cnt = line.strip().split(",")
        print(name, int(cnt) * 2)''', '쓰고 다시 읽기'),
     TIP('`write()` 는 줄바꿈을 자동으로 넣지 않아요. `"\\n"` 을 직접 붙여야 해요.')])

L.fill('파일 `score.txt` 의 각 줄(정수 하나)을 모두 더해 출력하세요.', '''\
with open("score.txt", "w") as f:
    f.write("70\\n85\\n90\\n")
total = 0
with open("score.txt", "___") as f:
    for line in f:
        total += int(line.___())
print(total)''', [['r'], ['strip']],
    '읽을 땐 모드 `r`. 줄 끝의 `\\n` 은 `strip()` 으로 지워요(사실 `int()` 는 줄바꿈을 무시하지만 습관처럼 쓰는 게 안전해요). 합은 245.',
    expect='245')

L.explain('γ 점검 ③ 클래스·상속·연산자 오버로딩',
    [T('`class 자식(부모):` 로 상속하고, `super().__init__(...)` 으로 부모의 초기화를 불러요.\n'
       '`__add__` 를 정의하면 `+` 연산자를, `__str__` 을 정의하면 `print()` 모양을 정할 수 있어요.'),
     CODE('''class Money:
    def __init__(self, won):
        self.won = won
    def __add__(self, other):
        return Money(self.won + other.won)
    def __str__(self):
        return f"{self.won}원"

class Coin(Money):
    def __init__(self, cnt):
        super().__init__(cnt * 500)

print(Money(1000) + Coin(3))''', '상속 + __add__ + __str__')],
    [T('이름 앞에 `__` 를 붙인 속성(`self.__pw`)은 **밖에서 바로 읽을 수 없게** 숨겨져요(캡슐화).\n'
       '그래서 값을 확인·변경하는 **메서드**를 따로 만들어요.'),
     KEY('2차의 이터레이터 클래스도 결국 `__iter__`·`__next__` 라는 **특별한 메서드**를 정의하는 거예요. `__add__` 와 같은 원리!')])

L.output('출력은?', '''\
class Animal:
    def __init__(self, name):
        self.name = name
    def sound(self):
        return "..."
    def show(self):
        print(self.name, self.sound())

class Dog(Animal):
    def sound(self):
        return "멍"

Animal("고양이").show()
Dog("바둑이").show()''',
    '`Dog` 는 `sound` 만 **재정의(오버라이딩)** 했어요. `show` 는 부모 것을 쓰지만, 안에서 부르는 `self.sound()` 는 Dog 의 것이에요.\n\n```\n{out}\n```')

L.spot('실행하면 **오류**가 나는 줄은?', '''\
class Account:
    def __init__(self, pw):
        self.__pw = pw
    def check(self, pw):
        return self.__pw == pw

a = Account("1234")
print(a.check("1234"))
print(a.__pw)''', 9,
    '`__pw` 처럼 밑줄 두 개로 시작하는 속성은 클래스 밖에서 그 이름으로 접근할 수 없어 `AttributeError` 가 나요. 그래서 `check()` 같은 메서드로만 확인해요.',
    error_line=9)

L.explain('γ 점검 ④ __name__ 과 numpy 기초',
    [T('파일을 **직접 실행**하면 그 파일의 `__name__` 은 `"__main__"` 이에요.\n'
       '다른 파일에서 `import` 되면 `__name__` 은 **모듈 이름**(파일 이름)이 돼요. 자세한 건 δ-09 에서!'),
     CODE('print(__name__)', '직접 실행하면?')],
    [T('numpy 배열은 `np.array(리스트)` 로 만들고, `shape`(모양)·`mean()`(평균)·`reshape(행, 열)` 을 썼어요.\n'
       '이 사이트에선 numpy 가 **실행되지 않아요**. 코드를 읽고 결과를 예측하는 연습을 해요.'),
     CODE('''import numpy as np
a = np.array([1, 2, 3, 4, 5, 6])
b = a.reshape(2, 3)
print(b)
print(b.shape)
print(b.mean())''', 'numpy 기초 (읽기 전용)', run_=False),
     WARN('`reshape(2, 3)` 은 원소 수가 2×3=6 일 때만 돼요. 원소가 5개면 `ValueError`!')])

L.output('numpy 코드의 출력을 예측하세요. (사이트에선 실행되지 않으니 손으로!)', '''\
import numpy as np
a = np.array([2, 4, 6, 8]).reshape(2, 2)
print(a.shape)
print(a.sum())
print(a * 10)''',
    '`reshape(2, 2)` → 2행 2열. 배열에 숫자를 곱하면 **모든 칸**에 곱해져요.\n\n```\n{out}\n```')

L.match('γ 에서 배운 도구와 쓰임을 이어 보세요.',
    [['else (try 문)', '오류가 없을 때만 실행'], ['raise', '오류를 일부러 일으키기'],
     ['with open(...)', '블록이 끝나면 파일 자동 닫기'], ['super().__init__()', '부모 클래스 초기화 호출'],
     ['__add__', '+ 연산자 동작 정하기'], ['reshape', '배열 모양 바꾸기']],
    '2차 시험에서도 이 여섯 개는 그대로 도구로 써요. 특히 `raise`·`else` 는 환율 계산기 문제, `__xxx__` 메서드는 이터레이터 문제에 나와요.')

L.practice('[기출유사] 공부시간 기록 정리',
'''일주일 동안 공부시간(분)을 한 줄에 하나씩 입력받아요. 첫 줄에 기록 개수 N 이 주어지고, 이어서 N 줄이 주어져요.
그런데 가끔 숫자가 아닌 값(예: `쉼`, `1h`)이 섞여 있어요.

**[조건]**
- 각 값을 `int()` 로 바꾸고, 실패하면 `try/except ValueError` 로 **건너뛰어요**.
- 바꾸기에 성공한 값은 `else` 블록에서 합계에 더해요.
- 첫째 줄: `합계: ○분`, 둘째 줄: `무시: ○개`

{ex}

{ex2}''',
'''n = int(input())
total = 0
skip = 0
for _ in range(n):
    s = input()
    # try / except / else 로 처리하세요
print("합계:", str(total) + "분")
print("무시:", str(skip) + "개")''',
'''n = int(input())
total = 0
skip = 0
for _ in range(n):
    s = input()
    try:
        m = int(s)            # 숫자로 바꾸기 시도
    except ValueError:
        skip += 1             # 실패하면 무시 개수 +1
    else:
        total += m            # 성공했을 때만 더하기
print("합계:", str(total) + "분")
print("무시:", str(skip) + "개")''',
    ['4\n60\n쉼\n90\n45', '3\n1h\n30\n30'], ['1\n0', '2\nx\ny', '5\n10\n20\n30\n40\n50'],
    ['`try:` 안에는 **오류가 날 수 있는 한 줄** `m = int(s)` 만 넣어요.',
     '`except ValueError:` 에서 `skip += 1`.',
     '`else:` 에서 `total += m`. else 는 오류가 없을 때만 실행돼요.'],
    '`else` 를 쓰면 "변환에 성공한 경우에만 할 일" 을 try 블록과 분리할 수 있어요. try 블록을 짧게 두면 어떤 줄의 오류를 잡는지 분명해져요.')

L.essay('try 문에서 `else` 블록은 언제 실행되는지 쓰고, `total += m` 을 try 블록 안이 아니라 else 블록에 두면 좋은 이유를 서술하세요.',
    'else 블록은 try 블록에서 예외가 하나도 발생하지 않았을 때만 실행된다. 변환 성공 후의 처리를 else 에 두면 try 블록에는 오류가 날 수 있는 코드(int 변환)만 남게 되어, except 가 어떤 줄의 오류를 처리하는지 분명해지고 다른 줄의 오류를 실수로 잡지 않는다.',
    ['예외가 없을 때만 실행된다', 'try 에는 오류가 날 수 있는 코드만 둔다', '다른 오류를 실수로 잡지 않는다'])

# =====================================================================
L = C.lesson('δ-02 내장함수 없이 만들기: 두 수 합·중복 제거·회문·최빈 문자', 30,
'''- 시험은 같은 일을 **내장함수로 한 번, 직접 구현으로 한 번** 쓰게 해요.
- 가장 큰 두 수: `sorted(a)[-2:]` ↔ `first`·`second` 변수로 한 번 훑기.
- 중복 제거: `set` 은 **순서가 사라짐** ↔ `if x not in result` 로 직접.
- 회문: `s == s[::-1]` ↔ 양 끝에서 좁혀 오며 비교.
- 최빈 문자: 딕셔너리로 세고 **가장 큰 값**을 직접 찾기.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간에는 2차 시험의 모양과 γ 핵심(try/except/else, with open, 클래스, numpy 기초)을 점검했어요.'),
     REVEAL_RUN('`int("3.5")` 를 실행하면 무슨 오류가 날까요? (except 로 잡은 결과)',
                'try:\n    int("3.5")\nexcept ValueError as e:\n    print("ValueError:", e)')])
L.ox('복습: try 문의 `else` 블록은 예외가 발생했을 때 실행된다.', False,
     '반대예요. `else` 는 예외가 **없을 때만** 실행돼요. 예외가 나면 `except` 가 실행돼요.', review=True)

L.explain('가장 큰 두 수의 합 — 쓰기 vs 안 쓰기',
    [T('내장함수를 쓰면 한 줄이에요. 정렬한 뒤 **뒤에서 두 개**를 잘라 더해요.\n'
       '`sorted()` 는 **새 리스트**를 돌려주니 원본은 그대로예요.'),
     CODE('a = [7, 3, 9, 1, 8]\ntop2 = sorted(a)[-2:]\nprint(top2, sum(top2))', 'sorted 사용')],
    [T('`sorted` 를 못 쓰면 **한 번 훑으면서** 1등(`first`)과 2등(`second`)을 기억해요.\n'
       '새 값이 1등보다 크면 → 1등이 2등으로 밀리고 새 값이 1등.\n'
       '1등보다는 작지만 2등보다 크면 → 2등만 바꿔요.'),
     TRACE('''a = [7, 3, 9, 1, 8]
first = second = -10**9
for x in a:
    if x > first:
        second = first
        first = x
    elif x > second:
        second = x
print(first, second, first + second)''', '1등·2등 따라가기')],
    [WARN('처음 값을 `0` 으로 두면 **음수만 있는 입력**에서 틀려요. 아주 작은 수(`-10**9`)나 `a[0]` 으로 시작하세요.'),
     TIP('`second = first` 를 `first = x` **보다 먼저** 써야 해요. 순서를 바꾸면 옛 1등 값이 사라져요.')])

L.output('출력은?', '''\
a = [5, 5, 2]
print(sorted(a)[-2:])
print(sum(sorted(a, reverse=True)[:2]))''',
    '같은 값 5 가 두 개면 둘 다 가장 큰 두 수예요. `reverse=True` 로 내림차순 정렬하면 앞에서 두 개를 자르면 돼요.\n\n```\n{out}\n```')

L.spot('`sorted` 없이 가장 큰 두 수를 찾는 코드인데 **결과가 틀려요**. 잘못된 줄은?', '''\
a = [4, 9, 6]
first = second = -10**9
for x in a:
    if x > first:
        first = x
        second = first
    elif x > second:
        second = x
print(first, second)''', 6,
    '`first = x` 를 먼저 하면 옛 1등 값이 사라지고 `second` 에도 새 값이 들어가요. 그래서 `9 9` 가 나와요. 5·6행의 순서를 바꿔 `second = first` 를 먼저 써야 `9 6` 이 돼요.')

L.explain('중복 제거 — set vs 직접',
    [T('`set` 은 중복을 허락하지 않아서 `set(리스트)` 한 번이면 중복이 사라져요.\n'
       '하지만 set 에는 **순서가 없어서** 처음 나온 순서가 보장되지 않아요.'),
     CMP(side('set 사용', '짧지만 순서가 보장되지 않아요 → 필요하면 sorted', 'a = [3, 1, 3, 2, 1]\nprint(sorted(set(a)))', 'good'),
         side('직접 구현', '처음 나온 순서 그대로 남아요', 'a = [3, 1, 3, 2, 1]\nresult = []\nfor x in a:\n    if x not in result:\n        result.append(x)\nprint(result)', 'good'))],
    [T('직접 구현의 핵심은 `if x not in result:` 예요. **이미 담은 것인지** 확인하고 처음 본 값만 넣어요.\n'
       '`len(a) != len(set(a))` 이면 "중복이 있다" 는 뜻이라, 중복 검사에도 자주 써요.'),
     EXAM('"set 을 사용한 방법과 사용하지 않은 방법 두 가지로 작성하시오" 가 2023년에 나왔어요. 두 방법 다 손에 익혀 두세요.')])

L.fill('set 을 쓰지 않고 중복을 제거해 **처음 나온 순서대로** 출력하세요.', '''\
words = ["cat", "dog", "cat", "owl", "dog"]
result = []
for w in words:
    if w ___ result:
        result.___(w)
print(result)''', [['not in'], ['append']],
    '`not in` 으로 아직 없는 단어인지 확인하고, 없으면 `append` 로 넣어요.', expect="['cat', 'dog', 'owl']")

L.explain('회문 — 뒤집기 vs 양 끝 비교',
    [T('**회문**은 거꾸로 읽어도 같은 말이에요. 슬라이싱 `s[::-1]` 로 뒤집어 비교하면 끝!'),
     SLC('s', 'RACECAR', None, None, -1)],
    [T('슬라이싱을 쓰지 말라면 **양 끝에서 안쪽으로** 좁혀 오며 비교해요.\n'
       '왼쪽 `i`, 오른쪽 `j` 가 만날 때까지 `s[i] == s[j]` 인지 확인하고, 하나라도 다르면 회문이 아니에요.'),
     TRACE('''s = "level"
i, j = 0, len(s) - 1
ok = True
while i < j:
    if s[i] != s[j]:
        ok = False
        break
    i += 1
    j -= 1
print(ok)''', '양 끝 비교 따라가기'),
     TIP('`for k in range(len(s) // 2):` 로 `s[k]` 와 `s[-1 - k]` 를 비교해도 같아요.')])

L.output('출력은?', '''\
for w in ["noon", "abca", "x"]:
    same = True
    for k in range(len(w) // 2):
        if w[k] != w[-1 - k]:
            same = False
    print(w, same)''',
    '"noon" 은 n=n, o=o 로 회문. "abca" 는 b≠c 라 False. 한 글자 "x" 는 비교할 쌍이 없어서 True 그대로예요.\n\n```\n{out}\n```')

L.explain('최빈 문자 — 세고, 가장 큰 것 찾기',
    [T('먼저 **딕셔너리로 개수**를 세요. `d[ch] = d.get(ch, 0) + 1` 이 단골 한 줄이에요.\n'
       '그다음 가장 많이 나온 글자를 찾아요.'),
     CODE('''s = "banana"
d = {}
for ch in s:
    d[ch] = d.get(ch, 0) + 1
print(d)
print(max(d, key=d.get))''', '세기 + max(key=)')],
    [T('`max(d, key=d.get)` 를 못 쓰면 **최댓값 찾기**를 직접 해요.\n'
       '`best` 에 지금까지 1등 글자를 두고, 더 큰 개수를 만나면 바꿔요.\n'
       '`>` 를 쓰면 동률일 때 **먼저 나온 글자**가 남아요.'),
     CODE('''s = "banana"
d = {}
for ch in s:
    d[ch] = d.get(ch, 0) + 1
best = ""
for ch in d:
    if best == "" or d[ch] > d[best]:
        best = ch
print(best, d[best])''', 'max 없이'),
     KEY('딕셔너리는 **넣은 순서**를 기억해요(파이썬 3.7+). 그래서 `for ch in d` 는 처음 나온 글자부터 돌아요.')])

L.order('문자열 `s` 에서 **가장 많이 나온 글자**를 출력하는 코드를 순서대로 놓으세요.',
    ['s = "abracadabra"', 'd = {}', 'for ch in s:', '    d[ch] = d.get(ch, 0) + 1', 'best = max(d, key=d.get)', 'print(best, d[best])'],
    '세기(딕셔너리 누적) → 가장 큰 값 찾기(max key) → 출력. a 가 5번으로 가장 많아요.',
    check=True, expect='a 5')

L.bucket('각 방법이 **내장함수 사용**인지 **직접 구현**인지 분류하세요.', ['내장함수 사용', '직접 구현'],
    [['sorted(a)[-2:]', 1], ['first·second 변수로 한 번 훑기', 2], ['list(set(a))', 1],
     ['if x not in result: result.append(x)', 2], ['s == s[::-1]', 1], ['while i < j: s[i] 와 s[j] 비교', 2],
     ['max(d, key=d.get)', 1], ['best 를 두고 d[ch] > d[best] 비교', 2]],
    '슬라이싱 `[::-1]` 도 "직접 뒤집지 않고 기능을 쓴" 쪽이에요. 시험이 "슬라이싱을 쓰지 않고" 라고 하면 양 끝 비교로 바꿔요.')

L.practice('[기출유사] 가장 큰 두 수의 합 (sorted·max 금지)',
'''한 줄에 정수들이 공백으로 주어져요. 가장 큰 수와 두 번째로 큰 수를 찾아 출력하세요.

**[조건]**
- `sorted()`, `sort()`, `max()` 를 사용하지 않아요. (자동 채점은 결과만 보지만, 시험이라면 감점이에요)
- 같은 값이 여러 개면 둘 다 셀 수 있어요. (예: `5 5 1` → 가장 큰 두 수는 5, 5)
- 정수는 2개 이상이고 **음수**도 나올 수 있어요.
- 첫째 줄: `1등: ○, 2등: ○`, 둘째 줄: `합: ○`

{ex}

{ex2}''',
'''a = list(map(int, input().split()))
first = second = -10**9
# 한 번 훑으며 1등, 2등을 찾으세요
''',
'''a = list(map(int, input().split()))
first = second = -10**9          # 아주 작은 수로 시작 (음수 입력 대비)
for x in a:
    if x > first:                # 새 1등
        second = first           # 옛 1등은 2등으로
        first = x
    elif x > second:             # 1등은 아니지만 2등보다 큼
        second = x
print(f"1등: {first}, 2등: {second}")
print(f"합: {first + second}")''',
    ['7 3 9 1 8', '4 10 10 2'], ['-5 -2 -9', '1 2', '6 6 6 6', '3 1 2 100 50'],
    ['`x > first` 이면 1등이 바뀌어요. 이때 옛 1등은 2등이 돼요.',
     '`elif x > second:` 로 2등만 바꾸는 경우를 따로 처리해요.',
     '같은 값 10 이 두 번 나오면, 두 번째 10 은 `x > first` 가 거짓이고 `x > second` 가 참이라 2등이 돼요.'],
    '처음 값을 0 으로 두면 `-5 -2 -9` 에서 0 이 1등이 돼 버려요. 그래서 `-10**9` 같은 아주 작은 수로 시작해요.')

L.practice('[기출유사] 타자 연습 — 가장 많이 친 글자',
'''타자 연습에서 친 문장이 한 줄 주어져요. **공백을 뺀** 글자 중 가장 많이 나온 글자와 횟수를 출력하세요.

**[조건]**
- 딕셔너리로 글자 수를 세요.
- `max()` 와 `count()` 를 사용하지 않고 직접 최댓값을 찾아요.
- 횟수가 같으면 문장에서 **먼저 나온 글자**를 출력해요.
- 출력 형식: `글자 횟수`

{ex}

{ex2}''',
'''s = input()
d = {}
# 공백을 빼고 글자를 세세요
''',
'''s = input()
d = {}
for ch in s:
    if ch == " ":                 # 공백은 세지 않기
        continue
    d[ch] = d.get(ch, 0) + 1      # 글자별 개수 누적
best = ""
for ch in d:                      # 넣은 순서 = 처음 나온 순서
    if best == "" or d[ch] > d[best]:   # > 이므로 동률이면 먼저 나온 글자 유지
        best = ch
print(best, d[best])''',
    ['hello world', 'aabb cc'], ['z', 'a b c', 'mississippi river', '  xx yy x'],
    ['`if ch == " ": continue` 로 공백을 건너뛰어요.',
     '`d[ch] = d.get(ch, 0) + 1` 로 세요.',
     '`>=` 가 아니라 `>` 를 써야 동률일 때 먼저 나온 글자가 남아요.'],
    '딕셔너리는 넣은 순서를 기억하니까 `for ch in d` 는 문장에서 처음 나온 순서대로 돌아요. 그래서 `>` 비교만으로 "먼저 나온 글자 우선" 이 지켜져요.')

L.essay('`list(set([3, 1, 3, 2]))` 로 중복을 제거하는 방법의 **문제점**을 쓰고, set 을 쓰지 않고 처음 나온 순서를 지키며 중복을 제거하는 방법을 서술하세요.',
    'set 은 순서가 없는 자료형이라 set 으로 바꾸면 원래 리스트에서 값이 나온 순서가 보장되지 않는다. 빈 리스트 result 를 만들고 원래 리스트를 앞에서부터 보며 `if x not in result:` 일 때만 append 하면, 처음 나온 순서대로 중복 없이 남는다.',
    ['set 은 순서가 없다', '원래 순서가 보장되지 않는다', '빈 리스트에 not in 으로 확인 후 append'])

# =====================================================================
L = C.lesson('δ-03 lambda·map·filter·컴프리헨션 — 같은 일 네 가지로', 30,
'''- `lambda x: x * x` 는 **이름 없는 한 줄 함수**예요.
- `map(함수, 리스트)` 는 모두 바꾸기, `filter(함수, 리스트)` 는 참인 것만 남기기.
- map·filter 결과는 **list() 로 감싸야** 내용이 보여요.
- 컴프리헨션 `[x*x for x in a if 조건]` 은 map + filter 를 한 줄로!
- 시험: "제곱 → 정렬" 을 map+lambda / 컴프 / sorted / 직접 정렬로 각각 쓰기.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간에는 내장함수를 쓴 방법과 직접 구현한 방법을 짝지어 연습했어요(두 수 합, 중복 제거, 회문, 최빈 문자).'),
     REVEAL_RUN('`d = {"a": 3, "b": 5, "c": 5}` 에서 `max(d, key=d.get)` 은?',
                'd = {"a": 3, "b": 5, "c": 5}\nprint(max(d, key=d.get))',
                '동률이면 **먼저 나온 키**가 답이에요.')])
L.output('복습: 출력은?', 'a = [2, 7, 2, 5, 7]\nr = []\nfor x in a:\n    if x not in r:\n        r.append(x)\nprint(r, len(a) - len(r))',
    '처음 나온 순서대로 2, 7, 5 만 남고, 빠진 중복은 2개예요. → {out}', review=True)

L.explain('lambda — 이름 없는 한 줄 함수',
    [T('`lambda 매개변수: 결과식` 은 `def` 로 쓰는 짧은 함수를 **한 줄로** 쓴 거예요.\n'
       '`return` 을 쓰지 않아도 `:` 뒤의 식이 바로 결과예요.'),
     CMP(side('def', '', 'def sq(x):\n    return x * x\nprint(sq(4))', 'good'),
         side('lambda', '', 'sq = lambda x: x * x\nprint(sq(4))', 'good'))],
    [T('lambda 는 보통 **다른 함수에 넘겨 줄 때** 써요. `map`, `filter`, `sorted(key=)` 가 대표적이에요.\n'
       '매개변수가 두 개면 `lambda a, b: a + b` 처럼 써요.'),
     TIP('lambda 안에는 **식 하나**만 들어가요. `if` 문, `for` 문을 여러 줄로 쓸 수 없어요. (`x if 조건 else y` 같은 식은 가능)')])

L.output('출력은?', '''\
f = lambda x, y: x * 10 + y
g = lambda n: "짝" if n % 2 == 0 else "홀"
print(f(3, 4))
print(g(f(1, 2)))''',
    '`f(3, 4)` = 34. `f(1, 2)` = 12 는 짝수라 `g` 는 "짝".\n\n```\n{out}\n```')

L.explain('map 과 filter',
    [T('`map(함수, 리스트)` 는 리스트의 **모든 값에 함수를 적용**해요.\n'
       '`filter(함수, 리스트)` 는 함수 결과가 **참인 값만** 남겨요.'),
     CODE('''a = [1, 2, 3, 4, 5]
print(list(map(lambda x: x * x, a)))
print(list(filter(lambda x: x % 2 == 1, a)))''', 'map · filter')],
    [T('map·filter 는 결과를 **한꺼번에 만들지 않고** 필요할 때 하나씩 꺼내는 물건(이터레이터)을 돌려줘요.\n'
       '그래서 그냥 출력하면 내용이 아니라 `<map object ...>` 가 보여요.'),
     CMP(side('그냥 출력', '내용이 안 보여요', 'print(map(str, [1, 2]))', 'bad'),
         side('list() 로 감싸기', '', 'print(list(map(str, [1, 2])))', 'good')),
     KEY('map 이 돌려주는 것은 **이터레이터**예요. δ-07 에서 배울 `next()` 로 하나씩 꺼낼 수도 있어요.')])

L.spot('실행하면 **오류**가 나는 줄은?', '''\
nums = [3, 6, 9]
half = map(lambda x: x // 3, nums)
print(sum(nums))
print(half[0])''', 4,
    'map 결과는 리스트가 아니라서 `half[0]` 처럼 **인덱스로 꺼낼 수 없어요** → `TypeError: \'map\' object is not subscriptable`. `list(half)[0]` 으로 바꿔야 해요.',
    error_line=4)

L.explain('제곱의 합 — 네 가지 방법',
    [T('"1~N 중 홀수의 제곱의 합" 을 네 가지로 써 볼게요. 결과는 모두 같아요.\n'
       '시험은 이 중 **두세 가지를 골라 쓰게** 해요.'),
     TABS(('for 문', '가장 기본. 누적 변수 total.', 'n = 5\ntotal = 0\nfor x in range(1, n + 1):\n    if x % 2 == 1:\n        total += x * x\nprint(total)'),
          ('컴프리헨션', '조건은 뒤에 `if`.', 'n = 5\nprint(sum([x * x for x in range(1, n + 1) if x % 2 == 1]))'),
          ('map + filter', '안쪽이 먼저: filter 로 고르고 map 으로 제곱.', 'n = 5\nodd = filter(lambda x: x % 2 == 1, range(1, n + 1))\nprint(sum(map(lambda x: x * x, odd)))'),
          ('def + map', 'lambda 대신 이름 있는 함수를 넘겨도 돼요.', 'def sq(x):\n    return x * x\nn = 5\nprint(sum(map(sq, range(1, n + 1, 2))))'))],
    [T('컴프리헨션의 모양을 외워 두세요.\n\n'
       '`[ 바꿀식  for 변수 in 범위  if 조건 ]`\n\n'
       '= `map(바꿀식)` + `filter(조건)` 을 한 번에 한 것이에요.'),
     WARN('`if` 를 앞에 쓰려면 **else 가 꼭 있어야** 해요: `[x if x > 0 else 0 for x in a]` (바꾸기). 뒤의 `if` 는 고르기예요.')])

L.fill('map 과 filter 로 **3의 배수의 제곱의 합**을 구하세요.', '''\
a = [1, 3, 4, 6, 9]
b = ___(lambda x: x % 3 == 0, a)
c = ___(lambda x: x ** 2, b)
print(sum(c))''', [['filter'], ['map']],
    '고르는 건 `filter`, 바꾸는 건 `map`. 3, 6, 9 의 제곱 9 + 36 + 81 = 126.', expect='126')

L.explain('제곱해서 정렬하기 — 정렬도 네 가지',
    [T('2023년엔 "각 수를 제곱해 오름차순 정렬" 을 **map+lambda / 컴프리헨션 × sorted / 직접 정렬** 로 쓰게 했어요.'),
     TABS(('map + sorted', '', 'a = [-3, 1, -2, 4]\nprint(sorted(map(lambda x: x * x, a)))'),
          ('컴프 + sort()', 'sort() 는 원본을 바꾸고 None 반환.', 'a = [-3, 1, -2, 4]\nb = [x * x for x in a]\nb.sort()\nprint(b)'),
          ('컴프 + 직접 정렬', '정렬 직접 구현은 δ-06 에서 자세히!', 'a = [-3, 1, -2, 4]\nb = [x * x for x in a]\nfor i in range(len(b) - 1):\n    for j in range(len(b) - 1 - i):\n        if b[j] > b[j + 1]:\n            b[j], b[j + 1] = b[j + 1], b[j]\nprint(b)'))],
    [T('`sorted()` 는 리스트뿐 아니라 **map 결과 같은 이터레이터도** 받아서 **리스트**로 돌려줘요.\n'
       '그래서 `sorted(map(...))` 은 `list()` 로 감쌀 필요가 없어요.'),
     THINK('`sorted(a, key=lambda x: x * x)` 는 무엇이 다를까요? → 정렬 **기준**만 제곱이고, 결과에는 **원래 값**이 남아요. 다음 레슨에서!')])

L.match('코드와 결과를 이어 보세요. (`a = [3, -1, 2]`)',
    [['list(map(lambda x: x * 2, a))', '[6, -2, 4]'], ['list(filter(lambda x: x > 0, a))', '[3, 2]'],
     ['sorted(map(lambda x: x * x, a))', '[1, 4, 9]'], ['[x for x in a if x < 3]', '[-1, 2]'],
     ['sum(x * x for x in a)', '14']],
    'map 은 개수가 그대로, filter 는 개수가 줄어들 수 있어요. 컴프리헨션의 뒤 if 는 filter 와 같아요.')

L.output('출력은?', '''\
words = ["sky", "a", "tree", "go"]
lens = list(map(len, words))
long = [w.upper() for w in words if len(w) >= 3]
print(lens)
print(long)
print(sum(lens) - len(long))''',
    '`map(len, words)` 은 단어마다 len 을 적용해요. 길이 3 이상은 sky·tree 두 개.\n\n```\n{out}\n```')

L.practice('[기출유사] 홀수 제곱 합 — map·filter 버전',
'''한 줄에 정수들이 공백으로 주어져요. **홀수만** 골라 제곱한 값들을 출력하고, 그 합을 출력하세요.

**[조건]**
- `filter` 와 `lambda` 로 홀수를 고르고, `map` 과 `lambda` 로 제곱하세요.
- 첫째 줄: 제곱한 값들을 공백으로 구분해 출력 (홀수가 없으면 `없음`)
- 둘째 줄: `합: ○`
- 음수 홀수(예: -3)도 홀수예요. (`-3 % 2` 는 1)

{ex}

{ex2}''',
'''a = list(map(int, input().split()))
# filter → map 순서로 처리하세요
''',
'''a = list(map(int, input().split()))
odd = filter(lambda x: x % 2 == 1, a)     # 홀수만 고르기
sq = list(map(lambda x: x * x, odd))       # 제곱하기 (리스트로 저장)
if sq:                                     # 빈 리스트는 거짓
    print(" ".join(map(str, sq)))          # 숫자 → 글자로 바꿔 join
else:
    print("없음")
print("합:", sum(sq))''',
    ['1 2 3 4 5', '-3 8 7'], ['2 4 6', '9', '-1 -2 -3 0 11'],
    ['`filter(lambda x: x % 2 == 1, a)` 로 홀수만.',
     'map 결과를 두 번(출력·합) 쓰려면 `list()` 로 저장해 두세요. 이터레이터는 한 번 쓰면 비어요.',
     '`" ".join(map(str, sq))` 로 숫자를 글자로 바꿔 이어요. 빈 리스트는 `if sq:` 에서 거짓이에요.'],
    '파이썬에서 `-3 % 2` 는 1 이라 음수 홀수도 `x % 2 == 1` 로 걸러져요. map 결과를 list 로 저장하지 않으면 join 에서 다 써 버려 sum 이 0 이 돼요.')

L.practice('[기출유사] 제곱 정렬 — 컴프리헨션 + 직접 정렬',
'''한 줄에 정수들이 주어져요. 각 수를 제곱한 뒤 **내림차순**으로 정렬해 출력하세요.

**[조건]**
- 제곱은 **리스트 컴프리헨션**으로 만들어요.
- 정렬은 `sorted()`·`sort()` 없이 **버블정렬로 직접** 해요. (자동 채점은 결과만 봐요)
- 정렬 결과를 공백으로 구분해 한 줄로 출력해요.

{ex}

{ex2}''',
'''a = list(map(int, input().split()))
b = []   # 컴프리헨션으로 바꾸세요
# 버블정렬(내림차순)
print(" ".join(map(str, b)))''',
'''a = list(map(int, input().split()))
b = [x * x for x in a]                      # 제곱 리스트
n = len(b)
for i in range(n - 1):
    for j in range(n - 1 - i):
        if b[j] < b[j + 1]:                 # 내림차순: 뒤가 더 크면 교환
            b[j], b[j + 1] = b[j + 1], b[j]
print(" ".join(map(str, b)))''',
    ['3 -5 1 2', '-1 1 0'], ['7', '-4 -3 -2 -1', '10 -10 5 0 3'],
    ['`b = [x * x for x in a]`',
     '버블정렬: 바깥 `for i in range(n - 1)`, 안쪽 `for j in range(n - 1 - i)`.',
     '내림차순이니 `b[j] < b[j + 1]` 일 때 교환해요.'],
    '음수도 제곱하면 양수가 되니 -5 의 제곱 25 가 가장 커요. 부등호 방향만 바꾸면 오름차순/내림차순이 바뀌어요.')

L.essay('`print(map(lambda x: x + 1, [1, 2]))` 를 실행하면 `[2, 3]` 이 아니라 `<map object at ...>` 같은 결과가 나와요. 그 **이유**와 고치는 방법을 서술하세요.',
    'map 은 결과를 리스트로 한꺼번에 만들지 않고, 필요할 때 값을 하나씩 만들어 주는 map 객체(이터레이터)를 돌려준다. print 는 그 객체 자체를 출력하므로 내용이 보이지 않는다. `list(map(...))` 처럼 list() 로 감싸 값을 모두 꺼내면 [2, 3] 이 출력된다.',
    ['map 은 리스트가 아니라 map 객체(이터레이터)를 돌려준다', '값을 필요할 때 하나씩 만든다', 'list() 로 감싸면 내용이 보인다'])

# =====================================================================
L = C.lesson('δ-04 sorted(key=)·max(key=)·all·any — 기준을 정하는 법', 30,
'''- `sorted(a, key=함수)` 는 **함수 결과를 기준**으로 정렬하고, 결과엔 **원래 값**이 남아요.
- `key=lambda x: (-x[1], x[0])` → 1번 칸 내림차순, 같으면 0번 칸 오름차순.
- `max(d, key=d.get)` → 값이 가장 큰 **키**.
- `all(조건 for …)` 은 모두 참?, `any(…)` 는 하나라도 참? (빈 것: all=True, any=False)
- 딕셔너리 + `sum(컴프)` 로 합계 한 줄.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간에는 lambda·map·filter·컴프리헨션으로 같은 일을 여러 방법으로 썼어요.'),
     REVEAL_RUN('`[x * 2 for x in range(5) if x % 2 == 0]` 의 결과는?', 'print([x * 2 for x in range(5) if x % 2 == 0])')])
L.fill('복습: map 으로 문자열 리스트를 정수 리스트로 바꾸세요.', 'a = ["4", "10", "7"]\nb = list(___(int, a))\nprint(sum(b))', [['map']],
    '`map(int, a)` 는 각 글자에 int 를 적용해요. 4 + 10 + 7 = 21.', expect='21', review=True)

L.explain('sorted(key=) — 정렬 기준 바꾸기',
    [T('`key=` 에는 **값 하나를 받아 기준을 돌려주는 함수**를 넣어요.\n'
       '정렬은 그 기준으로 하지만, 결과 리스트에는 **원래 값**이 들어 있어요.'),
     CODE('''words = ["banana", "kiwi", "apple", "fig"]
print(sorted(words))
print(sorted(words, key=len))
print(sorted(words, key=len, reverse=True))''', 'key=len')],
    [T('튜플(또는 리스트) 목록은 `lambda` 로 **몇 번 칸을 기준**으로 할지 정해요.\n'
       '기준이 같으면 원래 순서가 유지돼요(안정 정렬).'),
     CODE('''songs = [("지민", 88), ("하준", 95), ("서연", 88)]
print(sorted(songs, key=lambda x: x[1]))
print(sorted(songs, key=lambda x: x[1], reverse=True))''', 'key=lambda x: x[1]')],
    [T('기준이 **두 개**면 튜플로 돌려줘요. 숫자를 **내림차순**으로 하고 싶으면 앞에 `-` 를 붙여요.\n'
       '`key=lambda x: (-x[1], x[0])` → 점수 높은 순, 같으면 이름 가나다순.'),
     CODE('''songs = [("지민", 88), ("하준", 95), ("서연", 88)]
print(sorted(songs, key=lambda x: (-x[1], x[0])))''', '두 기준'),
     EXAM('2024년엔 `sorted(key=)`·`map(len, …)`·`max`·`pop`·`append` 가 섞인 **출력 추론**(10점)이 나왔어요.')])

L.output('출력은?', '''\
a = ["ccc", "a", "bb", "dd"]
b = sorted(a, key=len)
c = list(map(len, b))
b.append(b.pop(0) * 2)
print(b)
print(c, max(c))''',
    'key=len 으로 a(1) → bb(2) → dd(2) → ccc(3). bb 와 dd 는 길이가 같아 원래 순서대로예요. `pop(0)` 은 "a" 를 꺼내고 `"a" * 2` = "aa" 를 맨 뒤에 붙여요.\n\n```\n{out}\n```')

L.choice('`nums = [-7, 3, -2, 5]` 일 때 `sorted(nums, key=abs)` 의 결과는?',
    ['[-7, -2, 3, 5]', '[-2, 3, 5, -7]', '[2, 3, 5, 7]', '[5, 3, -2, -7]'], 2,
    '기준은 절댓값(2, 3, 5, 7)이지만 결과엔 **원래 값**이 남아요 → `[-2, 3, 5, -7]`. `[2, 3, 5, 7]` 은 값을 바꾼 map 의 결과와 헷갈린 거예요.')

L.explain('max(key=) · min(key=)',
    [T('`max` 와 `min` 도 `key=` 를 받아요. **기준이 가장 큰 원래 값**을 돌려줘요.\n'
       '딕셔너리에 그냥 `max(d)` 를 쓰면 **키끼리** 비교해요. 값 기준은 `key=d.get`!'),
     CMP(side('max(d)', '키(글자)끼리 비교 — 가나다순 마지막', 'd = {"콜라": 3, "사이다": 9, "주스": 5}\nprint(max(d))', 'bad'),
         side('max(d, key=d.get)', '값 기준 — 재고가 가장 많은 음료', 'd = {"콜라": 3, "사이다": 9, "주스": 5}\nprint(max(d, key=d.get))', 'good'))],
    [T('리스트 안의 튜플이면 `key=lambda x: x[1]` 처럼 칸을 골라요.\n'
       '`d.items()` 는 `(키, 값)` 튜플들이니 같은 방법을 써요.'),
     CODE('''d = {"콜라": 3, "사이다": 9, "주스": 5}
name, cnt = max(d.items(), key=lambda x: x[1])
print(name, cnt)
print(min(d.items(), key=lambda x: x[1]))''', 'items() + key')])

L.output('출력은?', '''\
scores = {"민수": 72, "지아": 91, "도윤": 85}
print(max(scores))
print(max(scores, key=scores.get))
print(min(scores.values()))''',
    '`max(scores)` 는 **키(이름)** 를 가나다순으로 비교해 "지아". 값 기준 최대도 우연히 "지아"(91). `min(values())` 는 값만 비교해 72.\n\n```\n{out}\n```')

L.explain('all · any — 모두? 하나라도?',
    [T('`all(목록)` 은 **모두 참**이면 True, `any(목록)` 는 **하나라도 참**이면 True 예요.\n'
       '보통 괄호 안에 **조건 컴프리헨션**을 넣어요.'),
     CODE('''stock = [3, 0, 5]
print(all(x > 0 for x in stock))
print(any(x == 0 for x in stock))
print(all([]), any([]))''', 'all / any')],
    [T('빈 목록이면 `all` 은 True(반례가 없으니까), `any` 는 False(참인 게 없으니까)예요.\n'
       '`all` 은 False 를 **하나 찾는 순간** 멈추고, `any` 는 True 를 하나 찾는 순간 멈춰요.'),
     TIP('`all(x > 0 for x in a)` 처럼 괄호 안에 바로 `for` 를 쓰면 대괄호가 없어도 돼요. 이건 **제너레이터 표현식**이에요(δ-08).')])

L.bucket('결과가 True 인지 False 인지 분류하세요. (`a = [2, 4, 7]`)', ['True', 'False'],
    [['all(x % 2 == 0 for x in a)', 2], ['any(x % 2 == 1 for x in a)', 1], ['all(x > 1 for x in a)', 1],
     ['any(x > 10 for x in a)', 2], ['all([])', 1], ['any([])', 2], ['all([1, 0, 3])', 2]],
    '`all([1, 0, 3])` 은 0 이 거짓이라 False 예요. 빈 리스트는 all 만 True!')

L.explain('딕셔너리 + 컴프리헨션 합계',
    [T('매점 음료 딕셔너리가 `{"이름": [가격, 재고]}` 모양이라고 해 볼게요.\n'
       '전체 재고, 재고 금액 합, 품절 여부를 **한 줄씩** 구할 수 있어요.'),
     CODE('''drinks = {"콜라": [1500, 4], "사이다": [1400, 0], "주스": [2000, 2]}
print(sum(v[1] for v in drinks.values()))
print(sum(p * c for p, c in drinks.values()))
print(any(c == 0 for p, c in drinks.values()))
print(max(drinks, key=lambda k: drinks[k][0]))''', '음료 딕셔너리')],
    [T('`for p, c in drinks.values()` 는 `[가격, 재고]` 를 **두 변수에 풀어서** 받아요.\n'
       '`max(drinks, key=lambda k: drinks[k][0])` 는 키(이름)를 돌면서 **가격**을 기준으로 비교해요.'),
     KEY('2024년 음료 문제(15점)는 sum(컴프)·all/any·max(key=) 를 한 번에 물었어요. 세 도구를 같이 연습하세요.')])

L.fill('재고(값)가 가장 적은 음료 이름과, 모든 음료 재고가 3개 이상인지를 출력하세요.', '''\
stock = {"콜라": 5, "우유": 2, "녹차": 7}
print(min(stock, key=stock.___))
print(___(v >= 3 for v in stock.values()))''', [['get'], ['all']],
    '`min(stock, key=stock.get)` 는 값이 가장 작은 **키**. 모두 3 이상인지는 `all` — 우유가 2 라 False.', expect='우유\nFalse')

L.practice('[기출유사] 매점 음료 재고 보고서',
'''첫 줄에 음료 수 N, 이어서 N 줄에 `이름 가격 재고` 가 주어져요. 딕셔너리 `{이름: [가격, 재고]}` 에 담고 보고서를 출력하세요.

**[조건]**
- 1줄: `총 재고: ○개` — `sum` + 제너레이터/컴프리헨션
- 2줄: `가장 비싼 음료: ○○` — `max(key=lambda …)` (가격이 같으면 먼저 입력된 음료)
- 3줄: 모든 음료의 재고가 있으면 `전부 있음`, 아니면 `품절 있음` — `all` 사용
- 4줄: 재고 많은 순(같으면 이름 가나다순)으로 이름을 공백으로 구분해 출력 — `sorted(key=lambda …)`

{ex}

{ex2}''',
'''n = int(input())
drinks = {}
for _ in range(n):
    name, price, cnt = input().split()
    drinks[name] = [int(price), int(cnt)]
# 보고서 4줄을 출력하세요
''',
'''n = int(input())
drinks = {}
for _ in range(n):
    name, price, cnt = input().split()
    drinks[name] = [int(price), int(cnt)]
print(f"총 재고: {sum(v[1] for v in drinks.values())}개")
print("가장 비싼 음료:", max(drinks, key=lambda k: drinks[k][0]))   # 가격 기준
if all(v[1] > 0 for v in drinks.values()):                          # 모두 재고 있음?
    print("전부 있음")
else:
    print("품절 있음")
order = sorted(drinks, key=lambda k: (-drinks[k][1], k))            # 재고 내림차순, 이름 오름차순
print(" ".join(order))''',
    ['3\n콜라 1500 4\n사이다 1400 0\n주스 2000 2', '2\n우유 1200 5\n두유 1200 5'],
    ['1\n물 800 0', '4\nd 100 1\nc 300 1\nb 300 9\na 200 1', '3\n초코 1800 10\n딸기 1800 3\n바나나 1700 3'],
    ['`sum(v[1] for v in drinks.values())` 로 재고만 더해요.',
     '`max(drinks, key=lambda k: drinks[k][0])` 는 이름을 돌면서 가격을 비교해요. 동률이면 먼저 나온 키가 남아요.',
     '`sorted(drinks, key=lambda k: (-drinks[k][1], k))` — 재고에 `-` 를 붙이면 내림차순이 돼요.'],
    '딕셔너리를 `sorted` 하면 **키 목록**이 정렬돼 나와요. 튜플 기준 `(-재고, 이름)` 하나로 "재고 내림차순, 같으면 이름 오름차순" 을 한 번에 처리해요.')

L.essay('딕셔너리 `d = {"콜라": 3, "사이다": 9}` 에서 `max(d)` 와 `max(d, key=d.get)` 의 결과가 **다른 이유**를 서술하세요.',
    'max(d) 는 딕셔너리를 돌 때 키만 나오므로 키(문자열)끼리 비교해 사전순으로 가장 뒤인 "콜라" 를 돌려준다. max(d, key=d.get) 는 각 키를 d.get 에 넣은 값(재고)을 기준으로 비교하므로 값이 가장 큰 키 "사이다" 를 돌려준다. 두 경우 모두 결과는 키이다.',
    ['max(d) 는 키끼리 비교한다', 'key=d.get 은 값을 기준으로 비교한다', '결과는 둘 다 키이다'])

# =====================================================================
L = C.lesson('δ-05 출력 추론 도구: enumerate·divmod·진수 변환', 25,
'''- `enumerate(a, start=1)` → `(번호, 값)` 쌍을 차례로 줘요.
- `divmod(a, b)` → `(a // b, a % b)` 튜플. `q, r = divmod(...)` 로 풀어 받기.
- `0b`(2진)·`0o`(8진)·`0x`(16진) 로 쓴 수는 **그냥 정수**예요.
- `bin`·`oct`·`hex` 는 **접두사 붙은 문자열**, `int("글자", 진법)` 은 정수로 되돌리기.
- 직접 2진 변환: `divmod(n, 2)` 로 나머지를 모아 **거꾸로**.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간에는 `sorted(key=)`·`max(key=)`·`all`·`any` 로 기준을 정해 고르고 정렬했어요.'),
     REVEAL_RUN('`sorted(["bb", "a", "ccc"], key=len, reverse=True)` 의 결과는?', 'print(sorted(["bb", "a", "ccc"], key=len, reverse=True))')])
L.output('복습: 출력은?', 'a = [4, 0, 7]\nprint(any(x == 0 for x in a), all(a))',
    '0 이 하나 있으니 any 는 True. `all(a)` 는 0 이 거짓이라 False. → {out}', review=True)

L.explain('enumerate — 번호 붙여 돌기',
    [T('`for i, x in enumerate(a):` 는 **번호(인덱스)와 값**을 같이 받아요.\n'
       '`start=1` 을 주면 번호가 1부터 시작해요. 값은 그대로예요.'),
     CODE('''menu = ["김밥", "라면", "만두"]
for i, m in enumerate(menu, start=1):
    print(i, m)
print(list(enumerate("ab")))''', 'enumerate')],
    [T('출력 추론에서는 번호 `i` 를 **계산에 쓰는** 코드가 자주 나와요.\n'
       '표를 그려서 `i`, `x`, 누적 변수를 한 줄씩 적으면 실수가 줄어요.'),
     TRACE('''a = [3, 5, 2]
total = 0
for i, x in enumerate(a):
    total += i * x
    print(i, x, total)''', 'i * x 누적')])

L.output('출력은?', '''\
s = "PYTHON"
for i, ch in enumerate(s, 1):
    if i % 2 == 0:
        print(i, ch)''',
    '`enumerate(s, 1)` 이라 번호는 1부터. 짝수 번호 2, 4, 6 의 글자 Y, H, N 이 출력돼요.\n\n```\n{out}\n```')

L.explain('divmod — 몫과 나머지를 한 번에',
    [T('`divmod(a, b)` 는 `(a // b, a % b)` 를 **튜플 하나**로 돌려줘요.\n'
       '`q, r = divmod(a, b)` 처럼 두 변수에 풀어 받는 게 보통이에요.'),
     CODE('''print(divmod(17, 5))
sec = 3725
m, s = divmod(sec, 60)
h, m = divmod(m, 60)
print(h, "시간", m, "분", s, "초")''', '초 → 시·분·초')],
    [T('2023년엔 **enumerate + divmod + 누적**을 섞은 출력 추론이 나왔어요.\n'
       '괄호 안부터 계산하고, 튜플을 어느 변수가 받는지 하나씩 적어 보세요.'),
     REVEAL_RUN('이 코드의 출력은?', '''acc = 0
for i, n in enumerate([7, 10, 13], 1):
    q, r = divmod(n, i + 1)
    acc += q - r
    print(i, q, r, acc)''')])

L.match('식과 결과를 이어 보세요.',
    [['divmod(20, 6)', '(3, 2)'], ['divmod(9, 10)', '(0, 9)'], ['list(enumerate("hi"))', "[(0, 'h'), (1, 'i')]"],
     ['list(enumerate([5], 3))', '[(3, 5)]'], ['divmod(-7, 2)', '(-4, 1)']],
    '`divmod(-7, 2)` 는 `-7 // 2 = -4`, `-7 % 2 = 1`. 파이썬의 `//` 는 **더 작은 쪽으로** 내림해요.')

L.explain('진수 변환 — 0b·0o·0x 와 bin·oct·hex',
    [T('코드에 `0b1010` 이라고 쓰면 2진수, `0o17` 은 8진수, `0xff` 는 16진수예요.\n'
       '이렇게 쓴 값은 모두 **그냥 정수**라서 출력하면 10진수로 보여요.'),
     CODE('print(0b1010, 0o17, 0xff)\nprint(0b11 + 0x10)', '접두사 표기는 정수')],
    [T('반대로 정수를 다른 진수 **글자**로 바꾸려면 `bin`·`oct`·`hex` 를 써요. 결과는 **접두사가 붙은 문자열**!\n'
       '글자를 다시 정수로 바꿀 땐 `int(글자, 진법)` 이에요.'),
     TABS(('정수 → 글자', '', 'n = 26\nprint(bin(n), oct(n), hex(n))\nprint(type(bin(n)))'),
          ('글자 → 정수', '', 'print(int("11010", 2))\nprint(int("32", 8))\nprint(int("1a", 16))\nprint(int("0x1a", 16))'),
          ('접두사 떼기', '', 'n = 26\nprint(bin(n)[2:])\nprint(format(n, "b"), format(n, "x"))')),
     WARN('`int("12", 2)` 는 **ValueError** 예요. 2진수에는 0 과 1 만 있으니까요. `bin(n) + 1` 도 문자열 + 정수라 TypeError!')])

L.bucket('결과의 **자료형**을 분류하세요.', ['정수(int)', '문자열(str)'],
    [['0b101', 1], ['bin(5)', 2], ['int("101", 2)', 1], ['hex(255)', 2], ['0x1f + 1', 1], ['bin(5)[2:]', 2], ['oct(8)', 2]],
    '`0b101` 처럼 **코드에 직접 쓴 수**는 정수, `bin`·`oct`·`hex` 의 **결과**는 문자열이에요.')

L.explain('직접 2진수로 바꾸기',
    [T('`bin()` 을 못 쓰면 **2로 나눈 나머지**를 모아요. 나머지는 낮은 자리부터 나오니까 **거꾸로** 붙여요.\n'
       '`divmod(n, 2)` 를 쓰면 몫과 나머지를 한 번에 얻어요.'),
     TRACE('''n = 13
bits = ""
while n > 0:
    n, r = divmod(n, 2)
    bits = str(r) + bits
print(bits)''', '13 → 1101'),
     TIP('`bits = str(r) + bits` 처럼 **앞에 붙이면** 따로 뒤집을 필요가 없어요. `n = 0` 이면 반복이 안 도니 `"0"` 을 따로 처리해야 해요.')])

L.fill('8진수 글자로 직접 바꾸세요. (`oct` 사용 금지)', '''\
n = 100
s = ""
while n > 0:
    n, r = divmod(n, ___)
    s = str(r) ___ s
print(s, s == oct(100)[2:])''', [['8'], ['+']],
    '8로 나눈 나머지를 앞에 붙여요. 100 = 1×64 + 4×8 + 4 → "144".', expect='144 True')

L.spot('실행하면 **오류**가 나는 줄은?', '''\
a = 0b110
b = int("101", 2)
print(a + b)
c = int("1021", 2)
print(c)''', 4,
    '"1021" 에는 2 가 있어서 2진수가 아니에요 → `ValueError: invalid literal for int() with base 2`. 1~3행은 6 + 5 = 11 을 출력해요.',
    error_line=4)

L.practice('[기출유사] 진수 변환표',
'''양의 정수 N 이 주어져요. 1부터 N 까지 각 수를 2진·8진·16진으로 바꿔 한 줄씩 출력하세요.

**[조건]**
- `bin`·`oct`·`hex` 를 쓰되 **접두사(0b·0o·0x)는 떼고** 출력해요.
- 16진수는 **대문자**로 출력해요. (`upper()`)
- 형식: `10진 2진 8진 16진` (공백 구분)

{ex}

{ex2}''',
'''n = int(input())
for i in range(1, n + 1):
    # 2진·8진·16진을 만들어 출력하세요
    pass''',
'''n = int(input())
for i in range(1, n + 1):
    b = bin(i)[2:]            # 앞 두 글자(0b) 떼기
    o = oct(i)[2:]            # 0o 떼기
    h = hex(i)[2:].upper()    # 0x 떼고 대문자로
    print(i, b, o, h)''',
    ['5', '11'], ['1', '16', '20'],
    ['`bin(i)` 는 `"0b101"` 같은 문자열이니 `[2:]` 로 앞 두 글자를 떼요.',
     '`hex(i)[2:].upper()` 로 16진수를 대문자로.',
     '`print(i, b, o, h)` 는 공백으로 구분해 출력해요.'],
    '`bin`·`oct`·`hex` 결과는 모두 접두사 2글자가 붙은 문자열이라 `[2:]` 하나로 똑같이 처리돼요. `format(i, "X")` 를 써도 대문자 16진수가 나와요.')

L.practice('[기출유사] 2진수 직접 변환 (bin 금지)',
'''0 이상의 정수 N 이 주어질 때, `bin()` 을 쓰지 않고 2진수로 바꿔 출력하고, 2진수에 들어 있는 **1 의 개수**를 출력하세요.

**[조건]**
- `divmod(n, 2)` 로 몫과 나머지를 구해 직접 만들어요.
- N 이 0 이면 2진수는 `0` 이에요.
- 형식: 첫 줄 2진수, 둘째 줄 `1의 개수: ○`

{ex}

{ex2}''',
'''n = int(input())
bits = ""
# divmod 로 2진수를 만드세요
print(bits)''',
'''n = int(input())
bits = ""
ones = 0
if n == 0:
    bits = "0"                 # 0 은 반복이 돌지 않으니 따로
while n > 0:
    n, r = divmod(n, 2)        # 몫은 다시 n, 나머지는 r
    bits = str(r) + bits       # 앞에 붙여 순서 맞추기
    ones += r                  # 나머지가 1 이면 1 개수 +1
print(bits)
print("1의 개수:", ones)''',
    ['13', '64'], ['0', '1', '255', '1000'],
    ['`while n > 0:` 안에서 `n, r = divmod(n, 2)`.',
     '나머지를 **앞에** 붙여요: `bits = str(r) + bits`.',
     'N = 0 이면 반복이 한 번도 안 돌아요. `if n == 0: bits = "0"`.'],
    '2로 나눈 나머지는 가장 낮은 자리부터 나와서 앞에 붙여야 순서가 맞아요. 나머지가 0 또는 1 이니 그대로 더하면 1 의 개수가 돼요.')

L.essay('`print(bin(5) + 1)` 이 오류가 나는 **이유**를 쓰고, "5 를 2진수로 쓴 글자" 와 "그 수에 1 을 더한 값의 2진수" 를 각각 바르게 출력하는 방법을 서술하세요.',
    'bin(5) 의 결과는 정수가 아니라 "0b101" 이라는 문자열이므로 문자열과 정수 1 을 + 로 더할 수 없어 TypeError 가 발생한다. 2진수 글자는 print(bin(5)) 로 출력하고, 1 을 더한 값의 2진수는 정수끼리 먼저 더한 뒤 print(bin(5 + 1)) 처럼 바꾼다(또는 int(bin(5), 2) + 1 로 정수로 되돌린 뒤 계산).',
    ['bin 의 결과는 문자열이다', '문자열 + 정수는 TypeError', '정수끼리 계산한 뒤 bin 을 적용한다'])

# =====================================================================
L = C.lesson('δ-06 정렬 직접 구현: 선택정렬·버블정렬·조기 종료', 35,
'''- **선택정렬**: 남은 칸에서 가장 작은 값의 **위치**를 찾아 맨 앞과 교환. 교환은 바퀴당 1번.
- **버블정렬**: 옆 칸끼리 비교해 큰 값을 뒤로. 바퀴마다 맨 뒤가 고정 → 안쪽은 `n - 1 - i` 까지.
- **조기 종료**: 한 바퀴 동안 교환이 없으면(`swapped == False`) 이미 정렬된 것 → `break`.
- 부등호 방향만 바꾸면 내림차순.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간에는 enumerate·divmod·진수 변환을 출력 추론 도구로 익혔어요.'),
     REVEAL_RUN('`q, r = divmod(29, 8)` 이면 q 와 r 은?', 'q, r = divmod(29, 8)\nprint(q, r)')])
L.match('복습: 식과 결과를 이어 보세요.', [['int("111", 2)', '7'], ['hex(16)', "'0x10'"], ['0o10', '8'], ['bin(2)[2:]', "'10'"]],
    '`0o10` 은 8진수 10 = 정수 8. `bin` 결과는 문자열이에요.', review=True)

L.explain('선택정렬 — 가장 작은 걸 골라 앞으로',
    [T('선택정렬은 **i 번째 자리**에 들어갈 값을 고르는 정렬이에요.\n'
       '`i` 부터 끝까지 중 **가장 작은 값의 위치** `m` 을 찾고, `a[i]` 와 `a[m]` 을 바꿔요.\n'
       '한 바퀴에 교환은 **딱 한 번**이에요.'),
     TRACE('''a = [5, 2, 8, 1]
n = len(a)
for i in range(n - 1):
    m = i
    for j in range(i + 1, n):
        if a[j] < a[m]:
            m = j
    a[i], a[m] = a[m], a[i]
    print(i, a)''', '선택정렬 따라가기')],
    [T('바깥 반복이 한 번 끝날 때마다 **앞쪽이 한 칸씩 완성**돼요.\n'
       '안쪽 반복은 `i + 1` 부터 시작해요. 앞쪽은 이미 정렬된 부분이라 다시 볼 필요가 없거든요.'),
     KEY('찾는 건 최솟**값**이 아니라 최솟값의 **위치(인덱스)** 예요. 위치를 알아야 교환할 수 있어요.'),
     WARN('`m = i` 를 안쪽 for **밖에서**(바퀴 시작마다) 초기화해야 해요.')])

L.output('선택정렬을 **두 바퀴만** 돌린 뒤의 리스트는?', '''\
a = [9, 4, 7, 1, 3]
n = len(a)
for i in range(2):
    m = i
    for j in range(i + 1, n):
        if a[j] < a[m]:
            m = j
    a[i], a[m] = a[m], a[i]
print(a)''',
    '1바퀴: 최솟값 1 과 9 교환 → [1, 4, 7, 9, 3]. 2바퀴: 남은 칸 최솟값 3 과 4 교환 → {out}')

L.order('선택정렬(오름차순) 코드를 순서대로 놓으세요.',
    ['a = [3, 1, 2]', 'n = len(a)', 'for i in range(n - 1):', '    m = i', '    for j in range(i + 1, n):',
     '        if a[j] < a[m]:', '            m = j', '    a[i], a[m] = a[m], a[i]', 'print(a)'],
    '`m = i` → 안쪽에서 더 작은 위치 찾기 → 바퀴 끝에 **한 번** 교환. 교환 줄은 안쪽 for 와 같은 들여쓰기가 아니라 바깥 for 안이에요.',
    check=True, expect='[1, 2, 3]')

L.explain('버블정렬과 "정렬된 부분 제외"',
    [T('버블정렬은 **옆 칸끼리** 비교해 순서가 틀리면 바꿔요.\n'
       '한 바퀴가 끝나면 가장 큰 값이 **맨 뒤에 고정**돼요.\n'
       '그래서 `i` 바퀴째에는 뒤쪽 `i` 칸을 빼고 `range(n - 1 - i)` 까지만 봐요.'),
     CMP(side('정렬된 부분 제외', '안쪽 범위가 바퀴마다 줄어요', 'a = [4, 3, 2, 1]\nn = len(a)\ncnt = 0\nfor i in range(n - 1):\n    for j in range(n - 1 - i):\n        cnt += 1\n        if a[j] > a[j + 1]:\n            a[j], a[j + 1] = a[j + 1], a[j]\nprint(a, "비교", cnt)', 'good'),
         side('항상 끝까지', '결과는 같지만 비교가 쓸데없이 많아요', 'a = [4, 3, 2, 1]\nn = len(a)\ncnt = 0\nfor i in range(n - 1):\n    for j in range(n - 1):\n        cnt += 1\n        if a[j] > a[j + 1]:\n            a[j], a[j + 1] = a[j + 1], a[j]\nprint(a, "비교", cnt)', 'bad'))],
    [T('**조기 종료**: 한 바퀴 동안 교환이 **한 번도 없었다면** 이미 정렬된 거예요. 더 돌 필요가 없어요.\n'
       '바퀴 시작마다 `swapped = False`, 교환할 때 `swapped = True`, 바퀴 끝에 `if not swapped: break`.'),
     TRACE('''a = [1, 3, 2, 4]
n = len(a)
for i in range(n - 1):
    swapped = False
    for j in range(n - 1 - i):
        if a[j] > a[j + 1]:
            a[j], a[j + 1] = a[j + 1], a[j]
            swapped = True
    print(i + 1, "바퀴", a)
    if not swapped:
        break''', '조기 종료 따라가기'),
     EXAM('2024년 18점 문항: 선택정렬 + 버블정렬을 직접 쓰고, **정렬된 부분은 다시 비교하지 않게** 하라는 조건이 있었어요.')])

L.fill('버블정렬에 **조기 종료**를 넣으세요.', '''\
a = [2, 1, 3, 4, 5]
n = len(a)
rounds = 0
for i in range(n - 1):
    swapped = ___
    for j in range(n - 1 - i):
        if a[j] > a[j + 1]:
            a[j], a[j + 1] = a[j + 1], a[j]
            swapped = True
    rounds += 1
    if ___ swapped:
        break
print(a, rounds)''', [['False'], ['not']],
    '바퀴 시작에 `False` 로 두고, 교환이 없었으면(`not swapped`) 멈춰요. 1바퀴에서 교환 1번, 2바퀴에서 교환 0번 → 2바퀴 만에 끝.',
    expect='[1, 2, 3, 4, 5] 2')

L.spot('실행하면 **오류**가 나는 줄은?', '''\
a = [3, 1, 2]
n = len(a)
for i in range(n - 1):
    for j in range(n - i):
        if a[j] > a[j + 1]:
            a[j], a[j + 1] = a[j + 1], a[j]
print(a)''', 5,
    '안쪽이 `range(n - i)` 라 첫 바퀴에 j 가 2 까지 가고, `a[j + 1]` = `a[3]` 은 없는 칸이에요 → `IndexError`. `range(n - 1 - i)` 로 고쳐야 해요. (오류는 5행에서 나지만 원인은 4행!)',
    error_line=5)

L.choice('`[1, 2, 3, 4, 5]` 처럼 **이미 정렬된** 리스트를 조기 종료가 있는 버블정렬로 정렬하면 바깥 반복은 몇 바퀴 돌까요?',
    ['0바퀴', '1바퀴', '4바퀴', '5바퀴'], 2,
    '첫 바퀴에서 비교는 하지만 교환이 한 번도 없어서 `swapped` 가 False → 바로 break. 그래서 **1바퀴**예요. 조기 종료가 없으면 4바퀴 다 돌아요.')

L.bucket('설명이 어느 정렬에 해당하는지 분류하세요.', ['선택정렬', '버블정렬', '둘 다'],
    [['남은 칸에서 최솟값의 위치를 찾는다', 1], ['옆 칸끼리 비교해 교환한다', 2], ['한 바퀴에 교환은 최대 한 번', 1],
     ['swapped 로 조기 종료할 수 있다', 2], ['부등호를 바꾸면 내림차순이 된다', 3], ['바깥 반복은 n - 1 바퀴면 충분하다', 3]],
    '선택정렬은 "고르고 한 번 교환", 버블정렬은 "옆끼리 여러 번 교환". 조기 종료는 교환 여부로 판단하는 버블정렬의 특징이에요.')

L.practice('[기출유사] 학급문고 정리 — 짝수는 선택, 홀수는 버블',
'''학급문고 책 번호들이 한 줄에 공백으로 주어져요. **짝수 번호**는 선택정렬로, **홀수 번호**는 버블정렬로 각각 오름차순 정렬하세요.

**[조건]**
- `sorted()`·`sort()` 를 쓰지 않고 두 정렬을 **직접** 구현해요. (자동 채점은 결과만 봐요)
- 버블정렬은 정렬된 뒷부분을 다시 비교하지 않고(`n - 1 - i`), 교환이 없으면 **조기 종료**해요.
- 1줄: `짝수: …`, 2줄: `홀수: …`, 3줄: `버블 바퀴: ○` (버블정렬 바깥 반복이 실제로 돈 횟수)

{ex}

{ex2}''',
'''a = list(map(int, input().split()))
even = [x for x in a if x % 2 == 0]
odd = [x for x in a if x % 2 == 1]
rounds = 0
# 선택정렬(even), 버블정렬(odd)
print("짝수:", " ".join(map(str, even)))
print("홀수:", " ".join(map(str, odd)))
print("버블 바퀴:", rounds)''',
'''a = list(map(int, input().split()))
even = [x for x in a if x % 2 == 0]
odd = [x for x in a if x % 2 == 1]

# 선택정렬: 남은 칸의 최솟값 위치를 찾아 i 번째와 교환
n = len(even)
for i in range(n - 1):
    m = i
    for j in range(i + 1, n):
        if even[j] < even[m]:
            m = j
    even[i], even[m] = even[m], even[i]

# 버블정렬: 정렬된 뒷부분 제외 + 조기 종료
n = len(odd)
rounds = 0
for i in range(n - 1):
    rounds += 1
    swapped = False
    for j in range(n - 1 - i):
        if odd[j] > odd[j + 1]:
            odd[j], odd[j + 1] = odd[j + 1], odd[j]
            swapped = True
    if not swapped:              # 교환이 없었으면 이미 정렬됨
        break

print("짝수:", " ".join(map(str, even)))
print("홀수:", " ".join(map(str, odd)))
print("버블 바퀴:", rounds)''',
    ['8 3 6 1 4 5', '2 9 7 5 3 1'], ['1 3 5 7 9', '10 8 6', '5', '13 2 11 4 9 6 7'],
    ['짝수·홀수 나누기는 이미 스타터에 있어요. 정렬만 두 번 쓰면 돼요.',
     '선택정렬: `m = i` → 안쪽 `range(i + 1, n)` 에서 더 작은 위치 찾기 → `even[i], even[m] = even[m], even[i]`.',
     '버블정렬: 바퀴 시작에 `rounds += 1`, `swapped = False`. 교환하면 True, 바퀴 끝에 `if not swapped: break`.'],
    '`1 3 5 7 9` 처럼 이미 정렬돼 있으면 버블정렬은 1바퀴 만에 끝나요. 원소가 1개 이하이면 `range(n - 1)` 이 비어서 0바퀴예요.')

L.essay('버블정렬에서 `swapped` 변수를 사용하면 **조기 종료**할 수 있는 이유를 서술하세요.',
    '버블정렬은 옆 칸끼리 비교해 순서가 틀리면 교환한다. 한 바퀴 동안 교환이 한 번도 일어나지 않았다면 모든 옆 칸이 이미 올바른 순서라는 뜻이므로 리스트 전체가 정렬된 상태이다. 그래서 바퀴마다 swapped 를 False 로 두고 교환할 때 True 로 바꾼 뒤, 바퀴가 끝났을 때 False 이면 break 해서 남은 바퀴를 생략할 수 있다.',
    ['교환이 없으면 모든 옆 칸이 올바른 순서', '즉 이미 정렬된 상태', '바퀴 끝에 swapped 가 False 면 break'])

# =====================================================================
L = C.lesson('δ-07 이터레이터: iter·next·__iter__·__next__·StopIteration', 35,
'''- **이터러블**: for 로 돌 수 있는 것(리스트·문자열…). **이터레이터**: `next()` 로 하나씩 꺼내는 것.
- `it = iter(이터러블)` → `next(it)` 반복 → 다 꺼내면 **StopIteration**.
- for 문 = `iter()` 한 번 + `next()` 반복 + StopIteration 이 나면 조용히 끝.
- 이터레이터 클래스: `__iter__` 는 `return self`, `__next__` 는 값 반환 또는 `raise StopIteration`.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간에는 선택정렬·버블정렬을 직접 쓰고 `swapped` 로 조기 종료했어요.'),
     REVEAL_RUN('버블정렬 한 바퀴만 돌린 `[4, 1, 3, 2]` 는?', 'a = [4, 1, 3, 2]\nfor j in range(3):\n    if a[j] > a[j + 1]:\n        a[j], a[j + 1] = a[j + 1], a[j]\nprint(a)',
                '가장 큰 4 가 맨 뒤로 갔어요.')])
L.ox('복습: 선택정렬은 한 바퀴에 교환이 여러 번 일어날 수 있다.', False,
     '선택정렬은 최솟값의 **위치**만 찾고 바퀴 끝에 **한 번** 교환해요. 여러 번 교환하는 건 버블정렬이에요.', review=True)

L.explain('iter() 와 next()',
    [T('리스트는 for 로 돌 수 있는 **이터러블**이에요. `iter(리스트)` 를 하면 **이터레이터**가 나와요.\n'
       '이터레이터는 `next()` 를 부를 때마다 **다음 값 하나**를 줘요. 꺼낸 값은 되돌아가지 않아요.'),
     CODE('''a = [10, 20, 30]
it = iter(a)
print(next(it))
print(next(it))
print(next(it))''', 'next 로 하나씩')],
    [T('값을 다 꺼낸 뒤 또 `next()` 를 부르면 **StopIteration** 오류가 나요.\n'
       '"더 이상 없어요" 라는 신호예요. `try/except StopIteration` 으로 잡을 수 있어요.'),
     CODE('''it = iter("ab")
while True:
    try:
        ch = next(it)
    except StopIteration:
        print("끝!")
        break
    print(ch)''', 'StopIteration 잡기'),
     TIP('`map`·`filter`·`enumerate`·`zip` 의 결과도 모두 이터레이터예요. 그래서 한 번 다 꺼내면 비어요.')])

L.output('출력은?', '''\
it = iter([5, 6, 7, 8])
a = next(it)
for x in it:
    print(x, end=" ")
print()
print(a)''',
    '이미 `next` 로 5 를 꺼냈으니 for 는 **남은 것** 6, 7, 8 만 돌아요.\n\n```\n{out}\n```')

L.explain('for 문의 속사정',
    [T('for 문은 사실 이터레이터를 이렇게 다뤄요. 이 순서는 2024년 16점 문항의 핵심이었어요.'),
     STEPS(('① iter() 한 번', '`for x in obj:` 를 만나면 `iter(obj)` 를 **딱 한 번** 불러 이터레이터를 얻어요. (클래스라면 `__iter__` 호출)'),
           ('② next() 반복', '매 바퀴 시작마다 `next(이터레이터)` 를 불러 값을 `x` 에 넣어요. (클래스라면 `__next__` 호출)'),
           ('③ 몸체 실행', '반복 몸체를 실행하고 다시 ② 로.'),
           ('④ StopIteration', '`next` 가 StopIteration 을 일으키면 for 문이 **오류 없이 조용히** 끝나요.'))],
    [T('그래서 for 문은 아래 while 문과 같아요.'),
     CMP(side('for 문', '', 'for x in [1, 2]:\n    print(x)', 'good'),
         side('똑같은 while', '', 'it = iter([1, 2])\nwhile True:\n    try:\n        x = next(it)\n    except StopIteration:\n        break\n    print(x)', 'good'))])

L.order('`for x in obj:` 가 실행될 때 일어나는 일을 순서대로 놓으세요. (값이 2개인 경우)',
    ['iter(obj) 호출 → 이터레이터 얻기', 'next() 호출 → 첫 값', '몸체 실행', 'next() 호출 → 둘째 값', '몸체 실행',
     'next() 호출 → StopIteration', '반복 종료 (오류 없음)'],
    'iter 는 처음에 **한 번만**, next 는 값 개수 + 1 번(마지막은 StopIteration) 불려요.', mono=False)

L.explain('이터레이터 클래스 만들기',
    [T('클래스에 두 메서드를 만들면 for 로 돌 수 있는 이터레이터가 돼요.\n'
       '`__iter__(self)` → **자기 자신을 돌려줘요**(`return self`).\n'
       '`__next__(self)` → 다음 값을 `return`, 더 없으면 `raise StopIteration`.'),
     TRACE('''class Countdown:
    def __init__(self, start):
        self.cur = start
    def __iter__(self):
        return self
    def __next__(self):
        if self.cur <= 0:
            raise StopIteration
        v = self.cur
        self.cur -= 1
        return v

for n in Countdown(3):
    print(n)''', 'Countdown 따라가기')],
    [T('상태(지금 어디까지 했는지)는 `self.cur` 같은 **속성**에 저장해요. `__next__` 를 부를 때마다 조금씩 바뀌어요.\n'
       '`raise StopIteration` 을 빼먹으면 for 문이 **끝나지 않아요**!'),
     KEY('`__next__` 안에서 **현재 값을 먼저 저장(v)** → 상태를 바꾸고 → `return v`. 순서를 바꾸면 첫 값이 빠져요.')])

L.output('메서드가 **불리는 순서**를 확인하는 코드예요. 출력은?', '''\
class Box:
    def __init__(self, items):
        print("init")
        self.items = items
        self.i = 0
    def __iter__(self):
        print("iter")
        return self
    def __next__(self):
        print("next")
        if self.i >= len(self.items):
            raise StopIteration
        self.i += 1
        return self.items[self.i - 1]

for x in Box(["A", "B"]):
    print(x)''',
    '`init` → for 시작에 `iter` 한 번 → `next`/값 두 번 → 마지막 `next` 에서 StopIteration 으로 끝. next 는 값 개수 + 1 = 3번!\n\n```\n{out}\n```')

L.spot('실행하면 **오류**가 나는 줄은?', '''\
class Evens:
    def __init__(self, n):
        self.n = n
        self.k = 0
    def __iter__(self):
        self.k = 0
    def __next__(self):
        self.k += 2
        if self.k > self.n:
            raise StopIteration
        return self.k

for e in Evens(6):
    print(e)''', 13,
    '`__iter__` 가 아무것도 돌려주지 않아(None) for 문이 이터레이터를 얻지 못해요 → 13행에서 `TypeError: iter() returned non-iterator`. 6행 다음에 `return self` 가 있어야 해요.',
    error_line=13)

L.explain('값을 검사하는 이터레이터 (2025 유형)',
    [T('2025년엔 아이디 목록을 하나씩 돌려주는 `IdIterator` 가 나왔어요. 형식이 틀린 아이디를 만나면 `ValueError` 를 일으켰죠.\n'
       '`__next__` 안에서 **StopIteration 말고 다른 오류**도 raise 할 수 있어요. 그 오류는 for 문 밖의 try 가 잡아요.'),
     CODE('''class CodeIter:
    def __init__(self, codes):
        self.codes = codes
        self.i = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.i == len(self.codes):
            raise StopIteration
        c = self.codes[self.i]
        self.i += 1
        if not c.isdigit():
            raise ValueError(c + " 는 숫자 코드가 아니에요")
        return int(c)

try:
    for c in CodeIter(["12", "7", "x9", "5"]):
        print(c)
except ValueError as e:
    print("중단:", e)''', '__next__ 에서 ValueError')],
    [T('StopIteration 은 for 가 **조용히** 처리하지만, ValueError 는 for 를 **멈추고 밖으로** 나가요.\n'
       '그래서 위 코드는 12, 7 을 출력한 뒤 "x9" 에서 멈추고 "5" 는 출력하지 않아요.'),
     THINK('for 문 **안쪽**에 try 를 두면 어떻게 될까요? → `__next__` 는 for 줄에서 불리니 안쪽 try 로는 못 잡아요. for 전체를 try 로 감싸야 해요.')])

L.match('이름과 역할을 이어 보세요.',
    [['__iter__', '이터레이터 자신을 돌려준다 (return self)'], ['__next__', '다음 값을 돌려준다'],
     ['StopIteration', '값이 더 없다는 신호'], ['iter(obj)', 'obj 의 __iter__ 를 부른다'], ['next(it)', 'it 의 __next__ 를 부른다']],
    '`iter()`·`next()` 내장함수는 각각 `__iter__`·`__next__` 메서드를 불러요. 연산자 `+` 가 `__add__` 를 부르는 것과 같아요.')

L.practice('[기출유사] 학번 생성 이터레이터',
'''학년, 반, 인원이 한 줄에 주어져요. 학번을 하나씩 만들어 주는 이터레이터 클래스 `StudentIds` 를 만들고, for 문으로 모두 출력하세요.

**[조건]**
- 학번 = 학년(1자리) + 반(2자리) + 번호(2자리). 예) 1학년 3반 5번 → `10305`
- 클래스에 `__iter__`(return self)와 `__next__` 를 정의하고, 번호가 인원을 넘으면 `raise StopIteration`.
- 마지막 줄에 `총 ○명` 을 출력해요.
- 두 자리 맞추기는 `f"{c:02d}"` 를 써요.

{ex}

{ex2}''',
'''class StudentIds:
    def __init__(self, g, c, n):
        self.g, self.c, self.n = g, c, n
        self.k = 0
    # __iter__ 와 __next__ 를 만드세요

g, c, n = map(int, input().split())
cnt = 0
# for 문으로 출력하세요
print(f"총 {cnt}명")''',
'''class StudentIds:
    def __init__(self, g, c, n):
        self.g, self.c, self.n = g, c, n
        self.k = 0                          # 지금까지 만든 번호
    def __iter__(self):
        return self                         # 자기 자신이 이터레이터
    def __next__(self):
        if self.k >= self.n:                # 인원을 다 만들었으면 끝
            raise StopIteration
        self.k += 1
        return f"{self.g}{self.c:02d}{self.k:02d}"

g, c, n = map(int, input().split())
cnt = 0
for sid in StudentIds(g, c, n):
    print(sid)
    cnt += 1
print(f"총 {cnt}명")''',
    ['1 3 4', '2 11 2'], ['3 1 0', '1 10 1', '2 5 12'],
    ['`def __iter__(self): return self`',
     '`__next__` 맨 앞에서 `if self.k >= self.n: raise StopIteration`.',
     '`self.k += 1` 한 뒤 `return f"{self.g}{self.c:02d}{self.k:02d}"`.'],
    '인원이 0 이면 첫 `__next__` 에서 바로 StopIteration 이 나서 for 몸체가 한 번도 실행되지 않아요. `:02d` 는 "두 자리, 빈자리는 0" 이라는 뜻이에요.')

L.practice('[기출유사] for 없이 next 로 돌기',
'''단어들이 한 줄에 공백으로 주어져요. **for 문을 쓰지 않고** `iter()`·`next()` 와 `try/except StopIteration` 으로 단어를 하나씩 꺼내, 길이가 3 이상인 단어만 `번호. 단어` 형식으로 출력하세요.

**[조건]**
- `while True:` 안에서 `next()` 를 부르고, StopIteration 이 나면 `break`.
- 번호는 출력한 단어에만 1부터 붙여요.
- 마지막 줄에 꺼낸 단어의 총 개수를 `꺼낸 개수: ○` 로 출력해요.

{ex}

{ex2}''',
'''words = input().split()
it = iter(words)
num = 0
total = 0
# while True + next + try/except
print("꺼낸 개수:", total)''',
'''words = input().split()
it = iter(words)
num = 0
total = 0
while True:
    try:
        w = next(it)                 # 다음 단어 꺼내기
    except StopIteration:            # 더 없으면 반복 종료
        break
    total += 1
    if len(w) >= 3:
        num += 1
        print(f"{num}. {w}")
print("꺼낸 개수:", total)''',
    ['I love my python class', 'go to the sea'], ['a b', 'apple', 'aa bbb cc dddd e fff'],
    ['`w = next(it)` 를 try 안에 넣어요.',
     '`except StopIteration: break`',
     '꺼낼 때마다 `total += 1`, 길이 3 이상이면 `num += 1` 후 출력.'],
    '이 코드가 바로 for 문이 속에서 하는 일이에요. for 를 쓰면 iter·next·StopIteration 처리를 자동으로 해 줘요.')

L.essay('`for x in obj:` 문이 이터레이터 클래스 `obj` 를 사용할 때 `__iter__` 와 `__next__` 가 **언제, 몇 번** 호출되고 반복이 어떻게 끝나는지 서술하세요.',
    'for 문이 시작될 때 obj 의 __iter__ 가 한 번 호출되어 이터레이터(보통 self)를 얻는다. 그 뒤 매 반복마다 __next__ 가 호출되어 돌려준 값이 x 에 들어가고 몸체가 실행된다. 값이 더 없으면 __next__ 가 StopIteration 을 발생시키고, for 문은 이 예외를 처리하며 오류 없이 반복을 끝낸다. 따라서 값이 n 개면 __next__ 는 n + 1 번 호출된다.',
    ['__iter__ 는 시작할 때 한 번', '__next__ 는 매 반복마다', 'StopIteration 이 나면 for 가 조용히 끝난다', '__next__ 는 값 개수 + 1 번'])

# =====================================================================
L = C.lesson('δ-08 제너레이터: yield·제너레이터 표현식·메모리', 30,
'''- 함수 안에 `yield` 가 있으면 **제너레이터 함수**. 부르면 실행되지 않고 제너레이터 객체가 나와요.
- `next()` 할 때마다 다음 `yield` 까지 실행하고 **멈춰서** 값을 줘요. 함수가 끝나면 StopIteration.
- 제너레이터 표현식 `(x*x for x in a)` 는 리스트 컴프와 모양은 같고 **괄호만** 달라요.
- 리스트 컴프는 값을 **한꺼번에 저장**, 제너레이터는 **필요할 때 하나씩** 만들어 메모리를 적게 써요.
- 제너레이터는 **한 번 다 쓰면 끝**.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간에는 `iter`·`next`·StopIteration 과 이터레이터 클래스(`__iter__`·`__next__`)를 만들었어요.'),
     REVEAL_RUN('`it = iter("hey")` 에서 `next(it)` 를 두 번 부르면?', 'it = iter("hey")\nnext(it)\nprint(next(it))')])
L.fill('복습: 이터레이터 클래스의 빈칸을 채우세요.', '''\
class Upto:
    def __init__(self, n):
        self.n, self.k = n, 0
    def __iter__(self):
        return ___
    def __next__(self):
        if self.k >= self.n:
            raise ___
        self.k += 1
        return self.k
print(list(Upto(3)))''', [['self'], ['StopIteration']],
    '`__iter__` 는 자신을, 끝나면 `StopIteration`. `list()` 도 for 처럼 이터레이터를 끝까지 꺼내요.', expect='[1, 2, 3]', review=True)

L.explain('yield — 멈췄다 다시 이어 가는 함수',
    [T('함수 안에 `return` 대신 `yield 값` 을 쓰면 **제너레이터 함수**가 돼요.\n'
       '이 함수를 부르면 몸체가 바로 실행되지 않고 **제너레이터 객체**가 나와요.\n'
       '`next()` 할 때마다 다음 `yield` 까지 실행하고 **그 자리에서 멈춰요**.'),
     TRACE('''def countdown(n):
    print("시작")
    while n > 0:
        yield n
        n -= 1
    print("끝")

g = countdown(2)
print(next(g))
print(next(g))
for x in g:
    print(x)''', 'yield 따라가기')],
    [T('지역 변수(`n`)는 멈춘 상태 그대로 **기억**돼요. 그래서 이어서 실행할 수 있어요.\n'
       '함수 몸체가 끝까지 실행되면 StopIteration 이 나요 → for 문은 조용히 끝나요.'),
     KEY('제너레이터 = **이터레이터를 쉽게 만드는 방법**. `__iter__`·`__next__`·`raise StopIteration` 을 파이썬이 대신 만들어 줘요.')])

L.output('출력은?', '''\
def gen():
    print("A")
    yield 1
    print("B")
    yield 2
    print("C")

g = gen()
print("시작")
print(next(g))
print(next(g))''',
    '`gen()` 을 부를 때는 아무것도 출력되지 않아요. 첫 `next` 에서 A 출력 후 1 에서 멈춤, 둘째 `next` 에서 B 출력 후 2. "C" 는 세 번째 next 가 없어서 출력되지 않아요.\n\n```\n{out}\n```')

L.explain('이터레이터 클래스 → 제너레이터로 바꾸기',
    [T('2025년엔 이터레이터 클래스를 **제너레이터로 바꿔 쓰라는** 문항이 나왔어요.\n'
       '클래스의 속성(상태) → 함수의 지역 변수, `return v` → `yield v`, `raise StopIteration` → 함수가 끝나면 자동!'),
     CMP(side('이터레이터 클래스', '', 'class Squares:\n    def __init__(self, n):\n        self.n, self.k = n, 0\n    def __iter__(self):\n        return self\n    def __next__(self):\n        if self.k >= self.n:\n            raise StopIteration\n        self.k += 1\n        return self.k ** 2\n\nprint(list(Squares(4)))', 'good'),
         side('제너레이터 함수', '', 'def squares(n):\n    for k in range(1, n + 1):\n        yield k ** 2\n\nprint(list(squares(4)))', 'good'))],
    [T('한 줄로 끝나는 경우라면 **제너레이터 표현식**으로도 쓸 수 있어요.\n'
       '리스트 컴프리헨션의 대괄호 `[ ]` 를 소괄호 `( )` 로 바꾸면 돼요.'),
     CODE('''n = 4
g = (k ** 2 for k in range(1, n + 1))
print(g)
print(list(g))''', '제너레이터 표현식'),
     TIP('함수에 넘길 땐 괄호를 하나 생략해요: `sum((x for x in a))` → `sum(x for x in a)`.')])

L.fill('이터레이터 클래스를 제너레이터 함수로 바꿨어요. 빈칸을 채우세요.', '''\
def odds(n):
    k = 1
    while k <= n:
        ___ k
        k += 2

print(list(odds(9)))
print(sum(x for x in ___(7)))''', [['yield'], ['odds']],
    '`yield k` 로 값을 내보내고 멈춰요. `odds(7)` 은 1, 3, 5, 7 → 합 16.', expect='[1, 3, 5, 7, 9]\n16')

L.explain('리스트 컴프 vs 제너레이터 표현식 — 메모리',
    [T('리스트 컴프리헨션은 값을 **모두 만들어 리스트에 저장**해요. 값이 백만 개면 백만 칸이 메모리에 올라가요.\n'
       '제너레이터 표현식은 **만드는 방법만** 기억했다가 `next()` 할 때마다 **하나씩** 만들어요.'),
     CODE('''import sys
a = [x * x for x in range(100000)]
g = (x * x for x in range(100000))
print(sys.getsizeof(a))
print(sys.getsizeof(g))
print(sum(a) == sum(g))''', '크기 비교 (숫자는 환경마다 조금 달라요)')],
    [T('대신 제너레이터는 **한 번 다 쓰면 비어요**. 인덱스(`g[0]`)·`len()` 도 안 돼요.\n'
       '여러 번 쓰거나 인덱스가 필요하면 리스트, 한 번 훑어 합·최댓값만 구하면 제너레이터가 좋아요.'),
     CMP(side('리스트 컴프 [ ]', '전부 저장 · 여러 번 사용 · 인덱스 OK · 메모리 많이', 'a = [x for x in range(3)]\nprint(sum(a), sum(a), a[0])', 'good'),
         side('제너레이터 ( )', '하나씩 생성 · 한 번만 · 인덱스 X · 메모리 적게', 'g = (x for x in range(3))\nprint(sum(g), sum(g))', 'good')),
     EXAM('2024년 8점 서술형: "리스트 컴프리헨션과 제너레이터 표현식의 **메모리 사용 차이**를 서술하시오."')])

L.output('출력은?', '''\
g = (n * 2 for n in [1, 2, 3, 4])
print(next(g))
print(sum(g))
print(list(g))''',
    '`next` 로 2 를 꺼냈으니 `sum` 은 남은 4 + 6 + 8 = 18. 그 뒤엔 다 써서 빈 리스트.\n\n```\n{out}\n```')

L.bucket('설명이 어느 쪽에 맞는지 분류하세요.', ['리스트 컴프리헨션', '제너레이터 표현식'],
    [['[x for x in a]', 1], ['(x for x in a)', 2], ['모든 값을 한꺼번에 메모리에 저장', 1], ['next() 로 값을 하나씩 만든다', 2],
     ['여러 번 반복해서 쓸 수 있다', 1], ['한 번 다 쓰면 비어 있다', 2], ['g[0] 처럼 인덱스로 꺼낼 수 있다', 1]],
    '괄호 모양 하나 차이지만 동작은 완전히 달라요. 리스트는 "저장", 제너레이터는 "필요할 때 생성".')

L.spot('실행하면 **오류**가 나는 줄은?', '''\
nums = [4, 9, 2]
g = (x + 1 for x in nums)
print(max(nums))
print(g[0])
print(sum(g))''', 4,
    '제너레이터는 값을 저장하지 않아서 인덱스로 꺼낼 수 없어요 → `TypeError: \'generator\' object is not subscriptable`. 첫 값이 필요하면 `next(g)` 를 써요.',
    error_line=4)

L.practice('[기출유사] 피보나치 제너레이터',
'''양의 정수 N 이 주어져요. N 이하의 피보나치 수(1, 1, 2, 3, 5, …)를 차례로 만들어 주는 **제너레이터 함수** `fib(limit)` 을 만들고 결과를 출력하세요.

**[조건]**
- `fib` 안에서 `yield` 로 값을 하나씩 내보내요. (리스트에 모아 return 하지 않아요)
- 1줄: 피보나치 수들을 공백으로 구분해 출력
- 2줄: `짝수 합: ○` — 제너레이터 표현식 `sum(x for x in fib(n) if …)` 사용

{ex}

{ex2}''',
'''def fib(limit):
    a, b = 1, 1
    # yield 로 값을 내보내세요

n = int(input())
print(" ".join(map(str, fib(n))))
''',
'''def fib(limit):
    a, b = 1, 1
    while a <= limit:
        yield a              # 값을 내보내고 여기서 멈춤
        a, b = b, a + b      # 다음 피보나치 수로

n = int(input())
print(" ".join(map(str, fib(n))))
print("짝수 합:", sum(x for x in fib(n) if x % 2 == 0))   # 새 제너레이터로 다시''',
    ['20', '100'], ['1', '2', '1000'],
    ['`while a <= limit:` 안에서 `yield a`.',
     '다음 수로 넘어가기: `a, b = b, a + b`.',
     '제너레이터는 한 번 쓰면 비니까, 합을 구할 땐 `fib(n)` 을 **다시 불러** 새로 만들어요.'],
    '첫 줄에서 쓴 제너레이터는 이미 비었어요. 그래서 둘째 줄에서 `fib(n)` 을 한 번 더 불러 새 제너레이터를 만들어요. 변수에 담아 두고 두 번 쓰면 두 번째는 0 이 돼요.')

L.essay('`[x * x for x in range(1000000)]` 과 `(x * x for x in range(1000000))` 의 **메모리 사용 차이**를 동작 방식과 연결해 서술하세요.',
    '리스트 컴프리헨션은 백만 개의 값을 모두 계산해 리스트에 한꺼번에 저장하므로 원소 수에 비례해 메모리를 많이 사용한다. 제너레이터 표현식은 값을 미리 만들지 않고 계산 방법만 가진 제너레이터 객체를 만들어, next() 가 호출될 때마다 값을 하나씩 생성하므로 원소 수와 관계없이 적은 메모리를 사용한다. 대신 제너레이터는 한 번만 순회할 수 있고 인덱스로 접근할 수 없다.',
    ['리스트는 모든 값을 한꺼번에 저장', '제너레이터는 필요할 때 하나씩 생성', '제너레이터가 메모리를 적게 쓴다', '제너레이터는 한 번만 사용 가능'])

# ---- 모듈 예제 실행 도우미: 모듈 파일을 실제로 만든 뒤 import 해서 검증 ----
def MOD_RUN(mods, main):
    head = 'import sys\nsys.path.insert(0, ".")\n'
    for name, src in mods.items():
        head += f'with open({name!r}, "w", encoding="utf-8") as _f:\n    _f.write({src!r})\n'
    return head + main


def MOD_TABS(mods, main, main_name='main.py'):
    """파일별 탭 (읽기용 — 실행 버튼 없음)"""
    tabs = [(name, f'```python\n{src.rstrip()}\n```') for name, src in mods.items()]
    tabs.append((main_name, f'```python\n{main.rstrip()}\n```'))
    return TABS(*tabs)


def MOD_MD(mods, main, main_name='main.py'):
    t = ''
    for name, src in mods.items():
        t += f'**{name}**\n```python\n{src.rstrip()}\n```\n'
    t += f'**{main_name}**\n```python\n{main.rstrip()}\n```'
    return t


# =====================================================================
L = C.lesson('δ-09 모듈 분리와 __name__ — 시계 각도 프로그램', 30,
'''- 모듈 = **.py 파일 하나**. `import add` 하면 `add.py` 를 불러와 `add.함수()` 로 써요.
- `from clock import hour_angle` 이면 `hour_angle()` 로 바로, `import numpy as np` 는 별명.
- import 하면 그 파일의 **최상위 코드가 한 번 실행**돼요.
- 직접 실행하면 `__name__ == "__main__"`, import 되면 `__name__ == "모듈이름"`.
- 시침 각도 = `(h % 12) * 30 + m * 0.5`, 분침 = `m * 6`, 사이 각 = `min(차, 360 - 차)`.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간에는 `yield` 로 제너레이터를 만들고, 리스트 컴프와 제너레이터 표현식의 메모리 차이를 봤어요.'),
     REVEAL_RUN('`g = (x for x in "abc")` 에서 `list(g)` 를 두 번 하면?', 'g = (x for x in "abc")\nprint(list(g))\nprint(list(g))',
                '제너레이터는 한 번 다 쓰면 비어요.')])
L.ox('복습: 제너레이터 함수를 부르면(`g = gen()`) 함수 몸체가 바로 처음부터 끝까지 실행된다.', False,
     '부르기만 하면 제너레이터 **객체**만 만들어지고, 몸체는 `next()` 를 부를 때 다음 `yield` 까지만 실행돼요.', review=True)

ADD = 'def plus(a, b):\n    return a + b\n'
SUB = 'def minus(a, b):\n    return a - b\n'
MAIN1 = 'import add\nfrom sub import minus\n\nprint(add.plus(7, 3))\nprint(minus(7, 3))\n'

L.explain('모듈 — 파일을 나눠 쓰기',
    [T('코드가 길어지면 기능별로 **파일을 나눠요**. 파이썬 파일 하나가 곧 **모듈**이에요.\n'
       '같은 폴더의 `add.py` 를 `import add` 로 불러오면 `add.plus()` 처럼 **모듈이름.함수** 로 써요.'),
     MOD_TABS({'add.py': ADD, 'sub.py': SUB}, MAIN1),
     TIP('이 사이트의 코드 창은 파일 하나만 실행해서, 여러 파일 예제는 **읽기**로 공부해요. 시험지에도 파일이 나뉘어 나와요.')],
    [T('import 하는 방법은 세 가지가 있어요. 부르는 모양이 달라져요.'),
     TABS(('import 모듈', '`import math` → `math.sqrt(16)`', 'import math\nprint(math.sqrt(16))'),
          ('from 모듈 import 이름', '`from math import sqrt` → `sqrt(16)` 바로', 'from math import sqrt, pi\nprint(sqrt(16), round(pi, 2))'),
          ('import 모듈 as 별명', '`import numpy as np` 처럼 짧은 별명', 'import random as rd\nprint(rd.randint(5, 5))')),
     WARN('`from math import sqrt` 만 했다면 `math.sqrt()` 는 **NameError**. `math` 라는 이름은 만들어지지 않았거든요.')])

L.output('세 파일이 같은 폴더에 있어요. `main.py` 를 실행한 출력은?\n\n' + MOD_MD({'add.py': ADD, 'sub.py': SUB}, MAIN1),
    '# main.py\n' + MAIN1.rstrip(),
    '`add.plus(7, 3)` = 10, `minus(7, 3)` = 4. from 으로 가져온 minus 는 모듈 이름 없이 불러요.\n\n```\n{out}\n```',
    run_code=MOD_RUN({'add.py': ADD, 'sub.py': SUB}, MAIN1))

L.spot('실행하면 **오류**가 나는 줄은?', '''\
from math import sqrt
print(sqrt(25))
print(math.floor(3.7))''', 3,
    '`from math import sqrt` 는 sqrt 라는 이름만 가져와요. `math` 라는 이름은 없어서 `NameError`. `import math` 를 따로 쓰거나 `from math import sqrt, floor` 후 `floor(3.7)`.',
    error_line=3)

TOOL = 'print("tool 불러옴:", __name__)\n\ndef double(x):\n    return x * 2\n\nif __name__ == "__main__":\n    print("tool 직접 실행 테스트:", double(5))\n'
MAIN2 = 'import tool\n\nprint("main:", __name__)\nprint(tool.double(4))\n'

L.explain('__name__ 과 if __name__ == "__main__":',
    [T('파이썬은 파일마다 `__name__` 이라는 변수를 자동으로 만들어요.\n'
       '그 파일을 **직접 실행**하면 `"__main__"`, 다른 파일이 **import** 하면 **모듈 이름**(`"tool"`)이 들어가요.'),
     MOD_TABS({'tool.py': TOOL}, MAIN2),
     REVEAL_RUN('`main.py` 를 실행하면?', MOD_RUN({'tool.py': TOOL}, MAIN2),
                'import 할 때 tool.py 의 최상위 코드(첫 print)가 실행돼요. 하지만 tool 안의 `__name__` 은 "tool" 이라 테스트 코드는 실행되지 않아요.')],
    [T('그래서 모듈 파일 맨 아래에 **테스트 코드**를 `if __name__ == "__main__":` 안에 넣어 둬요.\n'
       '직접 실행할 땐 테스트가 돌고, 다른 파일이 import 할 땐 함수만 깔끔하게 가져가요.'),
     CODE(TOOL, 'tool.py 를 직접 실행하면'),
     EXAM('2024년엔 `__name__` 의 값과 리스트 컴프 vs 제너레이터 서술이 한 문항(8점)에 나왔어요.')])

L.output('두 파일이 있어요. `main.py` 를 실행한 출력은?\n\n' + MOD_MD({'shop.py': 'TAX = 10\nprint("shop:", __name__)\n\ndef price(p):\n    return p + p * TAX // 100\n\nif __name__ == "__main__":\n    print(price(1000))\n'},
                                                                'import shop\n\nprint(shop.price(2000))\nprint(__name__)\n'),
    '# main.py\nimport shop\n\nprint(shop.price(2000))\nprint(__name__)',
    'import 순간 shop.py 의 첫 print 가 실행되고, 그 안의 `__name__` 은 "shop". 테스트 블록은 건너뛰어요. main 의 `__name__` 은 "__main__".\n\n```\n{out}\n```',
    run_code=MOD_RUN({'shop.py': 'TAX = 10\nprint("shop:", __name__)\n\ndef price(p):\n    return p + p * TAX // 100\n\nif __name__ == "__main__":\n    print(price(1000))\n'},
                     'import shop\n\nprint(shop.price(2000))\nprint(__name__)\n'))

L.match('import 방식과 함수를 부르는 모양을 이어 보세요.',
    [['import clock', 'clock.hour_angle(3, 0)'], ['from clock import hour_angle', 'hour_angle(3, 0)'],
     ['import clock as ck', 'ck.hour_angle(3, 0)'], ['from clock import *', 'minute_angle(30)  (모든 이름을 바로)']],
    '`import 모듈` 은 모듈 이름을, `from … import 이름` 은 그 이름을, `as` 는 별명을 만들어요.')

CLOCK = 'def hour_angle(h, m):\n    return (h % 12) * 30 + m * 0.5\n\ndef minute_angle(m):\n    return m * 6\n'
MAIN3 = 'from clock import hour_angle, minute_angle\n\nh, m = 3, 30\nd = abs(hour_angle(h, m) - minute_angle(m))\nprint(d, min(d, 360 - d))\n'

L.explain('시계 각도 — 모듈로 나누기',
    [T('시계 문제는 거의 매번 같은 공식을 써요. 12시 방향을 0도로 잡아요.\n\n'
       '- 분침: 1분에 360 ÷ 60 = **6도** → `m * 6`\n'
       '- 시침: 1시간에 360 ÷ 12 = **30도**, 그리고 1분에 **0.5도** 더 → `(h % 12) * 30 + m * 0.5`'),
     KEY('`h % 12` 로 15시를 3시로 바꿔요. 시침은 분에 따라 **조금씩 움직인다**는 걸 잊지 마세요(3시 30분의 시침은 3과 4 사이).')],
    [T('두 바늘의 각도 차는 `abs(시침 - 분침)`. 그런데 각은 양쪽으로 잴 수 있어요.\n'
       '**작은 쪽 각**은 `min(차, 360 - 차)` 예요.'),
     MOD_TABS({'clock.py': CLOCK}, MAIN3),
     REVEAL_RUN('3시 30분, `main.py` 의 출력은?', MOD_RUN({'clock.py': CLOCK}, MAIN3),
                '시침 105도, 분침 180도 → 차 75도. 반대쪽은 285도라 작은 각은 75도.')])

L.output('출력은?', '''\
def hour_angle(h, m):
    return (h % 12) * 30 + m * 0.5

def minute_angle(m):
    return m * 6

for h, m in [(9, 0), (14, 20), (12, 45)]:
    d = abs(hour_angle(h, m) - minute_angle(m))
    print(min(d, 360 - d))''',
    '9:00 → 270 과 0, 차 270 → 작은 각 90. 14:20 → 시침 70, 분침 120 → 50. 12:45 → 시침 22.5, 분침 270 → 차 247.5 → 112.5.\n\n```\n{out}\n```')

L.fill('`clock.py` 를 직접 실행할 때만 테스트가 돌도록 빈칸을 채우세요.', '''\
def minute_angle(m):
    return m * 6

if ___ == "___":
    print(minute_angle(15))''', [['__name__'], ['__main__']],
    '`if __name__ == "__main__":` — 직접 실행하면 참이라 90 이 출력되고, import 되면 거짓이라 출력되지 않아요.', expect='90')

L.practice('[기출유사] 시침과 분침 사이의 각',
'''시각 `H M` (0 ≤ H ≤ 23, 0 ≤ M ≤ 59) 이 한 줄로 주어져요. 시침·분침의 각도와 두 바늘 사이의 **작은 각**을 출력하세요.

**[조건]**
- 함수 `hour_angle(h, m)`, `minute_angle(m)` 을 만들어요. (시험에선 이 두 함수를 `clock.py` 모듈로 분리해요)
- 입력과 출력은 `if __name__ == "__main__":` 블록 안에 작성해요.
- 각도는 12시 방향이 0도, 소수 첫째 자리까지 `f"{값:.1f}"` 로 출력해요.
- 사이 각은 `abs` 와 `min` 으로 구해요.

{ex}

{ex2}''',
'''def hour_angle(h, m):
    pass

def minute_angle(m):
    pass

if __name__ == "__main__":
    h, m = map(int, input().split())
    # 세 줄을 출력하세요
''',
'''def hour_angle(h, m):
    return (h % 12) * 30 + m * 0.5      # 1시간 30도 + 1분에 0.5도

def minute_angle(m):
    return m * 6                         # 1분에 6도

if __name__ == "__main__":               # 직접 실행할 때만 입출력
    h, m = map(int, input().split())
    a = hour_angle(h, m)
    b = minute_angle(m)
    d = abs(a - b)
    print(f"시침: {a:.1f}도")
    print(f"분침: {b:.1f}도")
    print(f"사이 각: {min(d, 360 - d):.1f}도")''',
    ['3 30', '21 15'], ['0 0', '12 0', '6 0', '23 59'],
    ['시침: `(h % 12) * 30 + m * 0.5`, 분침: `m * 6`.',
     '`d = abs(a - b)` 후 작은 각은 `min(d, 360 - d)`.',
     '`print(f"시침: {a:.1f}도")` 처럼 소수 첫째 자리로.'],
    '`h % 12` 덕분에 21시와 9시는 같은 시침 각이 돼요. 6시 정각은 시침 180, 분침 0 이라 사이 각이 정확히 180 이에요.')

L.essay('모듈 파일 맨 아래에 `if __name__ == "__main__":` 를 두고 그 안에 테스트 코드를 쓰는 **이유**를 `__name__` 의 값과 연결해 서술하세요.',
    '파일을 직접 실행하면 그 파일의 __name__ 은 "__main__" 이 되고, 다른 파일에서 import 하면 __name__ 은 모듈 이름이 된다. 따라서 테스트 코드를 if __name__ == "__main__": 안에 두면 직접 실행할 때만 테스트가 실행되고, 다른 파일이 import 할 때는 실행되지 않아 함수만 깔끔하게 가져다 쓸 수 있다.',
    ['직접 실행하면 __name__ 은 "__main__"', 'import 되면 __name__ 은 모듈 이름', 'import 할 때 테스트 코드가 실행되지 않는다'])

# =====================================================================
L = C.lesson('δ-10 파일 심화: 모드 r·w·a, 경로, 인코딩, 읽고 누적하기', 35,
'''- `w` 는 **덮어쓰기**(없으면 새로 만듦), `a` 는 **뒤에 이어 쓰기**, `r` 는 읽기(없으면 FileNotFoundError).
- 윈도우 경로의 `\\` 는 이스케이프 문자! `r"C:\\data\\new.txt"` 나 `/` 를 써요.
- 저장한 인코딩과 **같은 인코딩**으로 읽어야 해요. (utf-8 ↔ euc-kr 섞으면 UnicodeDecodeError)
- 읽기 패턴: `for line in f:` → `strip().split()` → 리스트에 담아 누적·정렬.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간에는 모듈을 나누고 `__name__` 으로 직접 실행/import 를 구분했어요.'),
     REVEAL_RUN('파일을 직접 실행했을 때 `print(__name__)` 의 결과는?', 'print(__name__)')])
L.choice('복습: `from clock import hour_angle` 다음에 쓸 수 있는 호출은?',
    ['clock.hour_angle(3, 0)', 'hour_angle(3, 0)', 'clock(3, 0)', 'import.hour_angle(3, 0)'], 2,
    'from 으로 가져온 이름은 **모듈 이름 없이** 바로 써요. `clock` 이라는 이름은 만들어지지 않아요.', review=True)

L.explain('모드 r · w · a',
    [T('`open(파일, 모드)` 의 모드가 동작을 정해요.\n\n'
       '- `"r"` 읽기 (기본값). 파일이 없으면 **FileNotFoundError**.\n'
       '- `"w"` 쓰기. 파일이 있으면 **내용을 지우고** 새로 써요. 없으면 만들어요.\n'
       '- `"a"` 이어 쓰기. 기존 내용 **뒤에** 붙여요. 없으면 만들어요.'),
     CMP(side('w 를 두 번', '두 번째 w 가 앞 내용을 지워요', 'with open("log.txt", "w") as f:\n    f.write("월\\n")\nwith open("log.txt", "w") as f:\n    f.write("화\\n")\nwith open("log.txt") as f:\n    print(f.read())', 'bad'),
         side('w 다음 a', '앞 내용 뒤에 이어 써요', 'with open("log.txt", "w") as f:\n    f.write("월\\n")\nwith open("log.txt", "a") as f:\n    f.write("화\\n")\nwith open("log.txt") as f:\n    print(f.read())', 'good'))],
    [T('읽는 방법도 세 가지예요. `read()` 는 전부 한 글자열, `readlines()` 는 줄 리스트(줄바꿈 포함), `for line in f` 는 한 줄씩.'),
     CODE('''with open("pets.txt", "w", encoding="utf-8") as f:
    f.write("고양이\\n강아지\\n햄스터\\n")

with open("pets.txt", encoding="utf-8") as f:
    lines = f.readlines()
print(lines)
print([x.strip() for x in lines])''', 'readlines 와 strip'),
     WARN('`readlines()` 의 각 줄 끝에는 `\\n` 이 붙어 있어요. 비교·출력 전에 `strip()`!')])

L.output('`count.txt` 에는 처음에 `5` 한 줄이 들어 있어요. 출력은?', '''\
for _ in range(3):
    with open("count.txt", "a") as f:
        f.write("2\\n")
total = 0
with open("count.txt") as f:
    for line in f:
        total += int(line)
print(total)''',
    '`a` 모드라 기존 5 뒤에 2 가 세 번 붙어요. 5 + 2 + 2 + 2 = {out}. 모드가 `w` 였다면 마지막 2 하나만 남아 2 가 돼요.',
    files={'count.txt': '5\n'})

L.explain('파일 경로와 역슬래시',
    [T('`open("score.txt")` 처럼 이름만 쓰면 **지금 실행 중인 폴더**(상대 경로)에서 찾아요.\n'
       '`"data/score.txt"` 는 그 안의 data 폴더, `"C:/pynest/score.txt"` 처럼 드라이브부터 쓰면 **절대 경로**예요.'),
     STEPS(('상대 경로', '`"score.txt"`, `"data/score.txt"`, `"../score.txt"`(한 칸 위 폴더)'),
           ('절대 경로', '`"C:/pynest/data/score.txt"` — 어디서 실행해도 같은 파일'),
           ('찾지 못하면', '읽기(`r`)는 FileNotFoundError, 쓰기(`w`)는 폴더가 없으면 오류'))],
    [T('윈도우 경로는 `\\` 를 쓰는데, 파이썬 문자열에서 `\\n`·`\\t` 는 **줄바꿈·탭**이에요!\n'
       '그래서 경로가 망가질 수 있어요. 앞에 `r` 을 붙인 **raw 문자열**이나 `/` 를 쓰세요.'),
     CODE(r'''print("C:\new\table.txt")
print(r"C:\new\table.txt")
print("C:/new/table.txt")''', '\\n 과 \\t 의 함정'),
     TIP('`\\\\` 처럼 역슬래시를 두 번 써도 글자 `\\` 하나가 돼요.')])

L.output('출력은? (줄 수에 주의!)', r'''path = "C:\note\new.txt"
print(path)
print(len(r"C:\note"))''',
    '`\\n` 이 두 번 있어서 둘 다 **줄바꿈**으로 바뀌어요. 그래서 경로가 세 줄로 쪼개져 나와요. raw 문자열 `r"C:\\note"` 는 7글자 그대로예요.\n\n```\n{out}\n```')

L.explain('인코딩 — utf-8 과 euc-kr',
    [T('컴퓨터는 글자를 숫자로 바꿔 저장해요. 그 규칙이 **인코딩**이에요.\n'
       '한글은 `utf-8`(요즘 표준, 한 글자 3바이트)과 `euc-kr`(옛 한글 표준, 2바이트)이 많이 쓰여요.\n'
       '**저장한 인코딩으로 읽어야** 글자가 제대로 나와요.'),
     CMP(side('같은 인코딩', '', 'with open("k.txt", "w", encoding="euc-kr") as f:\n    f.write("안녕")\nwith open("k.txt", encoding="euc-kr") as f:\n    print(f.read())', 'good'),
         side('다른 인코딩', 'UnicodeDecodeError', 'with open("k.txt", "w", encoding="euc-kr") as f:\n    f.write("안녕")\nwith open("k.txt", encoding="utf-8") as f:\n    print(f.read())', 'bad', expect_error=True))],
    [T('엑셀·메모장에서 만든 옛 한글 파일은 euc-kr(또는 cp949)인 경우가 많아요. 깨지면 `encoding=` 을 바꿔 보세요.'),
     CODE('''s = "가"
print(len(s.encode("utf-8")))
print(len(s.encode("euc-kr")))''', '같은 글자, 다른 바이트 수'),
     EXAM('2023년엔 "euc-kr 로 저장된 파일을 읽는 코드" 의 인코딩 인자를 고르는 문항(5점)이 나왔어요.')])

L.short('euc-kr 로 저장된 파일 `old.txt` 를 읽으려고 해요. `open("old.txt", "r", encoding="____")` 의 빈칸은?', 'euc-kr',
    '저장할 때 쓴 인코딩과 같아야 해요. `cp949` 도 euc-kr 을 넓힌 것이라 읽을 수 있어요.', alts=['euckr', 'cp949', 'EUC-KR'])

L.explain('읽어서 list of list 로 — 정렬과 누적',
    [T('한 줄에 `이름 점수 점수 …` 가 있는 파일은 `split()` 해서 **리스트의 리스트**로 만들면 다루기 쉬워요.\n'
       '그다음 `sum`, `sorted(key=lambda …)` 를 그대로 쓸 수 있어요.'),
     CODE('''with open("song.txt", "w", encoding="utf-8") as f:
    f.write("민준 80 90\\n서윤 95 85\\n도현 70 99\\n")

rows = []
with open("song.txt", encoding="utf-8") as f:
    for line in f:
        name, *nums = line.split()
        rows.append([name, sum(map(int, nums))])
rows.sort(key=lambda r: r[1], reverse=True)
print(rows)''', '노래자랑 점수 읽기')],
    [T('`name, *nums = line.split()` 은 **첫 칸은 name, 나머지는 리스트 nums** 로 받아요.\n'
       '파일이 없을 수도 있으면 `try/except FileNotFoundError` 로 감싸요.'),
     CODE('''try:
    with open("없는파일.txt") as f:
        print(f.read())
except FileNotFoundError:
    print("파일이 없어요. 이름을 확인하세요.")''', 'FileNotFoundError')])

L.order('파일에서 점수를 읽어 **평균**을 출력하는 코드를 순서대로 놓으세요. (`nums.txt` 에 한 줄에 하나씩 정수)',
    ['with open("nums.txt", "w") as f:', '    f.write("4\\n8\\n9\\n")', 'nums = []', 'with open("nums.txt") as f:',
     '    for line in f:', '        nums.append(int(line.strip()))', 'print(sum(nums) / len(nums))'],
    '쓰기(w) → 빈 리스트 → 읽기(r) 하며 append → 평균. 4, 8, 9 의 평균은 7.0.',
    check=True, expect='7.0')

L.bucket('상황에 맞는 모드를 분류하세요.', ['r', 'w', 'a'],
    [['저장된 점수 파일을 불러와 평균을 구한다', 1], ['매일 공부 기록을 기존 기록 뒤에 추가한다', 3],
     ['결과 파일을 매번 새로 만든다', 2], ['방문자 로그를 계속 쌓는다', 3], ['파일이 없으면 FileNotFoundError 가 날 수 있다', 1],
     ['열자마자 기존 내용이 지워진다', 2]],
    '"새로·덮어쓰기" 는 w, "쌓기·추가" 는 a, "불러오기" 는 r.')

L.practice('[기출유사] 노래자랑 결과 파일',
'''첫 줄에 참가자 수 N, 이어서 N 줄에 `이름 점수1 점수2 점수3` 이 주어져요.

**[조건]**
- 입력받은 줄을 그대로 `entry.txt` 에 **w 모드**로 저장해요.
- `entry.txt` 를 다시 읽어 `[이름, 합계]` 의 리스트(list of list)를 만들어요.
- 합계 **내림차순**(같으면 이름 가나다순)으로 `sorted(key=lambda …)` 정렬해요.
- `등수. 이름 합계` 형식으로 `result.txt` 에 쓰고, `result.txt` 를 읽어 그대로 출력해요.
- 파일 읽기는 `try/except FileNotFoundError` 로 감싸고, 파일이 없으면 `파일 없음` 을 출력해요.

{ex}

{ex2}''',
'''n = int(input())
with open("entry.txt", "w", encoding="utf-8") as f:
    for _ in range(n):
        f.write(input() + "\\n")
rows = []
# entry.txt 를 읽어 rows 를 만들고, 정렬해 result.txt 에 쓰고, 읽어서 출력하세요
''',
'''n = int(input())
with open("entry.txt", "w", encoding="utf-8") as f:     # 1) 입력을 파일로 저장
    for _ in range(n):
        f.write(input() + "\\n")

rows = []
try:
    with open("entry.txt", "r", encoding="utf-8") as f:  # 2) 다시 읽기
        for line in f:
            name, *scores = line.split()
            rows.append([name, sum(map(int, scores))])  # [이름, 합계]
except FileNotFoundError:
    print("파일 없음")

rows = sorted(rows, key=lambda r: (-r[1], r[0]))         # 3) 합계 내림차순, 이름 오름차순

with open("result.txt", "w", encoding="utf-8") as f:      # 4) 결과 파일 쓰기
    for i, (name, total) in enumerate(rows, 1):
        f.write(f"{i}. {name} {total}\\n")

with open("result.txt", encoding="utf-8") as f:           # 5) 결과 읽어서 출력
    print(f.read().rstrip())''',
    ['3\n민준 80 90 70\n서윤 95 85 90\n도현 70 99 80', '2\nbob 50 50 50\namy 60 40 50'],
    ['1\n솔로 100 100 100', '4\nd 1 1 1\nc 3 3 3\nb 2 2 2\na 3 3 3', '3\n가 0 0 0\n나 10 0 0\n다 0 0 10'],
    ['읽을 때 `name, *scores = line.split()` 으로 이름과 점수를 나눠요.',
     '`sorted(rows, key=lambda r: (-r[1], r[0]))` — 합계에 `-` 를 붙여 내림차순.',
     '쓸 때 `enumerate(rows, 1)` 로 등수를 붙이고 `f.write(f"{i}. {name} {total}\\n")`.'],
    '프로그램 안에서 쓴 파일을 다시 읽는 구조라 FileNotFoundError 는 실제로 나지 않지만, 시험에선 "파일이 없을 때" 처리가 채점 기준이에요. `f.read().rstrip()` 은 마지막 줄바꿈을 지워 출력을 깔끔하게 해요.')

L.practice('[기출유사] 공부 기록 쌓기 (a 모드)',
'''첫 줄에 기록 수 N, 이어서 N 줄에 `과목 분` 이 주어져요.

**[조건]**
- 먼저 `study.txt` 를 **w 모드**로 열어 첫 줄에 `과목,분` 이라는 제목을 써요.
- 기록은 한 줄 입력받을 때마다 `study.txt` 를 **a 모드**로 열어 `과목,분` 형식으로 한 줄씩 이어 써요.
- 다 쓴 뒤 파일을 읽어 **제목 줄은 건너뛰고** 과목별 합계를 딕셔너리로 누적해요.
- 처음 나온 과목 순서대로 `과목: ○분` 을 출력하고, 마지막 줄에 `총 ○분` 을 출력해요.

{ex}

{ex2}''',
'''n = int(input())
with open("study.txt", "w", encoding="utf-8") as f:
    f.write("과목,분\\n")
# a 모드로 이어 쓰고, 다시 읽어 누적하세요
''',
'''n = int(input())
with open("study.txt", "w", encoding="utf-8") as f:       # 제목 줄 (새 파일)
    f.write("과목,분\\n")
for _ in range(n):
    subj, m = input().split()
    with open("study.txt", "a", encoding="utf-8") as f:   # 뒤에 이어 쓰기
        f.write(f"{subj},{m}\\n")

total = {}
with open("study.txt", encoding="utf-8") as f:
    f.readline()                                          # 제목 줄 건너뛰기
    for line in f:
        subj, m = line.strip().split(",")
        total[subj] = total.get(subj, 0) + int(m)         # 과목별 누적
for subj in total:
    print(f"{subj}: {total[subj]}분")
print(f"총 {sum(total.values())}분")''',
    ['4\n수학 50\n정보 40\n수학 30\n영어 20', '2\n정보 90\n정보 15'],
    ['1\n국어 0', '3\nA 1\nB 2\nC 3', '5\n물리 10\n화학 20\n물리 30\n화학 40\n생명 50'],
    ['반복 안에서 `with open("study.txt", "a", ...)` 로 열고 `f.write(f"{subj},{m}\\n")`.',
     '읽을 때 `f.readline()` 을 한 번 먼저 부르면 제목 줄을 건너뛰어요.',
     '`total[subj] = total.get(subj, 0) + int(m)` 로 누적.'],
    'a 모드는 열 때마다 파일 끝에 붙이니까 기록이 하나씩 쌓여요. w 모드로 매번 열었다면 마지막 기록 하나만 남았을 거예요.')

L.essay('공부 기록을 날마다 파일에 저장하는 프로그램에서 `open("study.txt", "w")` 를 쓰면 어떤 문제가 생기는지, `"a"` 모드와 비교해 서술하세요.',
    'w 모드는 파일을 열 때 기존 내용을 모두 지우고 새로 쓰기 때문에, 날마다 실행하면 이전 날의 기록이 사라지고 마지막 기록만 남는다. a 모드는 기존 내용을 유지한 채 파일 끝에 이어 쓰므로 기록이 계속 쌓인다. 따라서 기록을 누적하려면 a 모드를 써야 한다.',
    ['w 는 기존 내용을 지우고 새로 쓴다', '이전 기록이 사라진다', 'a 는 파일 끝에 이어 쓴다', '누적하려면 a 모드'])

# =====================================================================
L = C.lesson('δ-11 예외 처리 종합: 환율 계산기', 35,
'''- `try` → 오류 나면 맞는 `except`, 없으면 `else`, 그리고 **항상** `finally`.
- 딕셔너리에 없는 키 → **KeyError**, 숫자로 못 바꾸면 → **ValueError**.
- `raise ValueError("메시지")` 로 직접 오류를 만들고 `except ValueError as e:` 로 메시지 출력.
- except 는 **위에서부터** 검사해요. `except Exception` 을 맨 위에 두면 아래 except 는 쓸모없어요.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간에는 파일 모드(r·w·a), 경로, 인코딩, 파일을 읽어 누적·정렬하는 법을 익혔어요.'),
     REVEAL_RUN('`w` 로 "A", 이어서 `a` 로 "B" 를 쓰면 파일 내용은?',
                'with open("t.txt", "w") as f:\n    f.write("A")\nwith open("t.txt", "a") as f:\n    f.write("B")\nwith open("t.txt") as f:\n    print(f.read())')])
L.spot('복습: 실행하면 오류가 나는 줄은? (`memo.txt` 는 없는 파일)', 'print("시작")\nwith open("memo.txt", "r") as f:\n    print(f.read())', 2,
    '읽기 모드로 없는 파일을 열면 `FileNotFoundError`. 쓰기(w)·이어 쓰기(a) 모드는 파일을 새로 만들어요.', review=True, error_line=2)

L.explain('try · except · else · finally 의 흐름',
    [T('네 블록의 실행 규칙을 정리해 볼게요.'),
     STEPS(('try', '먼저 실행. 중간에 오류가 나면 **남은 줄은 건너뛰고** except 로.'),
           ('except 오류종류', '그 종류의 오류가 났을 때만 실행. 여러 개면 **위에서부터** 맞는 하나만.'),
           ('else', 'try 에서 오류가 **하나도 없을 때만** 실행.'),
           ('finally', '오류가 있든 없든 **항상** 마지막에 실행. (파일 닫기, "종료" 메시지 등)'))],
    [T('같은 코드에 두 가지 입력을 넣어 흐름을 비교해 보세요.'),
     TABS(('정상 입력 "4"', '', 'for s in ["4"]:\n    try:\n        n = 12 // int(s)\n        print("계산 완료")\n    except ValueError:\n        print("숫자 아님")\n    except ZeroDivisionError:\n        print("0 으로 나눔")\n    else:\n        print("결과", n)\n    finally:\n        print("끝")'),
          ('0 입력 "0"', '', 'for s in ["0"]:\n    try:\n        n = 12 // int(s)\n        print("계산 완료")\n    except ValueError:\n        print("숫자 아님")\n    except ZeroDivisionError:\n        print("0 으로 나눔")\n    else:\n        print("결과", n)\n    finally:\n        print("끝")')),
     KEY('오류가 난 줄 **아래의 try 코드**("계산 완료")는 실행되지 않아요. 출력 추론에서 가장 많이 틀리는 곳!')])

L.output('출력은?', '''\
def f(s):
    try:
        print("A")
        n = int(s)
        print("B")
    except ValueError:
        print("C")
    else:
        print("D", n)
    finally:
        print("E")

f("7")
f("칠")''',
    '"7" → A, B, else 의 D 7, finally 의 E. "칠" → A 후 int() 에서 ValueError 라 B 를 건너뛰고 C, 그리고 E.\n\n```\n{out}\n```')

L.explain('KeyError · ValueError · raise',
    [T('환율 계산기처럼 **딕셔너리에서 찾고 + 숫자로 바꾸는** 프로그램엔 두 오류가 단골이에요.\n'
       '없는 키를 `d[키]` 로 찾으면 **KeyError**, `int("abc")` 는 **ValueError**.'),
     CODE('''rates = {"USD": 1400, "JPY": 9}
for code, amt in [("USD", "10"), ("GBP", "10"), ("JPY", "십")]:
    try:
        won = rates[code] * int(amt)
    except KeyError:
        print(code, "→ 없는 통화")
    except ValueError:
        print(amt, "→ 숫자가 아님")
    else:
        print(code, amt, "→", won, "원")''', '두 가지 오류 잡기')],
    [T('파이썬이 오류로 보지 않는 경우(예: 금액이 음수)도 `raise` 로 **직접 오류를 만들** 수 있어요.\n'
       '`except ValueError as e:` 의 `e` 에는 넣은 메시지가 들어 있어요.'),
     CODE('''def to_amount(s):
    if not s.isdigit():
        raise ValueError("금액은 양의 정수로 입력하세요")
    n = int(s)
    if n == 0:
        raise ValueError("금액은 0보다 커야 해요")
    return n

for s in ["300", "-5", "0"]:
    try:
        print(to_amount(s))
    except ValueError as e:
        print("오류:", e)''', 'raise 로 규칙 만들기'),
     TIP('`except (KeyError, ValueError):` 처럼 괄호로 묶으면 여러 오류를 **한 번에** 잡을 수 있어요.')])

L.match('코드와 발생하는 오류를 이어 보세요.',
    [['{"a": 1}["b"]', 'KeyError'], ['int("3.5")', 'ValueError'], ['10 / 0', 'ZeroDivisionError'],
     ['[1, 2][5]', 'IndexError'], ['open("없음.txt")', 'FileNotFoundError'], ['"3" + 4', 'TypeError']],
    '`int("3.5")` 는 소수점이 있는 글자라 정수로 못 바꿔요(`float("3.5")` 는 가능). 오류 이름을 정확히 아는 게 except 작성의 시작이에요.')

L.bucket('`try: n = int(s)` 다음에 `except ValueError` / `else` / `finally` 가 있어요. s 값에 따라 실행되는 블록을 분류하세요. (finally 는 제외하고 생각해요)',
    ['except ValueError', 'else'],
    [['s = "12"', 2], ['s = "1.5"', 1], ['s = " 7 "', 2], ['s = ""', 1], ['s = "-3"', 2], ['s = "3a"', 1]],
    '`int()` 는 앞뒤 공백과 부호(-)는 허용하지만 소수점·빈 글자·문자가 섞이면 ValueError 예요. finally 는 어느 경우든 항상 실행돼요.')

L.explain('except 순서의 함정',
    [T('except 는 **위에서부터** 차례로 검사해서 **처음 맞는 것 하나만** 실행해요.\n'
       '`Exception` 은 거의 모든 오류의 **부모**라서 맨 위에 두면 다 잡아 버려요.'),
     CMP(side('넓은 것을 위에', 'ValueError 블록이 절대 실행되지 않아요', 'try:\n    int("x")\nexcept Exception:\n    print("뭔가 오류")\nexcept ValueError:\n    print("숫자 아님")', 'bad'),
         side('좁은 것을 위에', '구체적인 오류부터 검사', 'try:\n    int("x")\nexcept ValueError:\n    print("숫자 아님")\nexcept Exception:\n    print("뭔가 오류")', 'good'))],
    [THINK('왜 그럴까요? → `ValueError` 는 `Exception` 을 **상속**한 클래스예요. γ 에서 배운 상속 관계가 그대로 쓰여요. 부모로 잡으면 자식 오류도 다 잡혀요.')])

L.fill('환율 계산기의 빈칸을 채우세요. (통화가 없으면 KeyError, 금액이 숫자가 아니면 ValueError)', '''\
rates = {"USD": 1400, "EUR": 1500}
code, amt = "EUR", "20"
try:
    won = rates[code] * int(amt)
except ___:
    print("없는 통화")
except ___:
    print("금액 오류")
___:
    print(won)''', [['KeyError'], ['ValueError'], ['else']],
    '없는 키는 KeyError, 숫자 변환 실패는 ValueError, 성공했을 때는 else. 1500 × 20 = 30000.', expect='30000')

L.output('출력은?', '''\
stock = {"펜": 3, "자": 0}
orders = [("펜", "2"), ("풀", "1"), ("자", "1"), ("펜", "1")]
for item, q in orders:
    try:
        q = int(q)
        if stock[item] < q:
            raise ValueError("재고 부족")
        stock[item] -= q
    except KeyError:
        print(item, "없음")
    except ValueError as e:
        print(item, e)
    else:
        print(item, "OK", stock[item])''',
    '펜 2개 → 남은 1. 풀 → KeyError. 자는 재고 0 < 1 이라 raise 할 때 넣은 메시지 "재고 부족" 이 e 에 들어가요. 마지막 펜 1개 → 남은 0.\n\n```\n{out}\n```')

L.practice('[기출유사] 환율 계산기',
'''두 줄에 걸쳐 **통화 코드**와 **금액**이 주어져요. 원화로 환산해 출력하세요.

환율표: `rates = {"USD": 1400, "EUR": 1500, "JPY": 9, "CNY": 190}`

**[조건]**
- 통화 코드는 소문자로 들어올 수도 있으니 `upper()` 로 바꿔요.
- 금액 변환은 함수 `to_amount(s)` 로 해요. 숫자가 아니면 `raise ValueError("금액은 양의 정수로 입력하세요")`, 0 이면 `raise ValueError("금액은 0보다 커야 해요")`.
- 환율을 **먼저** 찾고(`rates[code]`), 그다음 금액을 변환해요.
- 없는 통화 → `지원하지 않는 통화: ○○○` / 금액 오류 → `오류: (메시지)` / 성공(else) → `○ ○○○ = ○원`
- 마지막엔 **항상**(finally) `계산기를 종료합니다` 를 출력해요.

{ex}

{ex2}''',
'''rates = {"USD": 1400, "EUR": 1500, "JPY": 9, "CNY": 190}

def to_amount(s):
    # 규칙에 맞지 않으면 raise ValueError(...)
    return int(s)

code = input().upper()
s = input()
# try / except KeyError / except ValueError as e / else / finally
''',
'''rates = {"USD": 1400, "EUR": 1500, "JPY": 9, "CNY": 190}

def to_amount(s):
    if not s.isdigit():                                  # 숫자가 아니면(음수 포함)
        raise ValueError("금액은 양의 정수로 입력하세요")
    n = int(s)
    if n == 0:
        raise ValueError("금액은 0보다 커야 해요")
    return n

code = input().upper()
s = input()
try:
    rate = rates[code]                                   # 없으면 KeyError
    amount = to_amount(s)                                # 규칙 위반이면 ValueError
except KeyError:
    print("지원하지 않는 통화:", code)
except ValueError as e:
    print("오류:", e)
else:
    print(f"{amount} {code} = {amount * rate}원")        # 성공했을 때만
finally:
    print("계산기를 종료합니다")                          # 항상''',
    ['usd\n100', 'JPY\n5000'], ['KRW\n100', 'EUR\nabc', 'CNY\n0', 'gbp\nxyz', 'eur\n-5'],
    ['`rate = rates[code]` 가 try 의 첫 줄이에요. 없는 통화면 여기서 바로 KeyError.',
     '`to_amount` 안: `if not s.isdigit(): raise ValueError("…")`, `if n == 0: raise ValueError("…")`.',
     '`except ValueError as e: print("오류:", e)` 그리고 `finally: print("계산기를 종료합니다")`.'],
    '`gbp` + `xyz` 처럼 둘 다 틀리면 환율을 먼저 찾으니 KeyError 만 처리돼요. try 안에서 오류가 난 줄 아래는 실행되지 않으니까요. `"-5".isdigit()` 은 `-` 때문에 False 라 음수도 첫 번째 메시지가 나와요.')

L.practice('[기출유사] 도어락 비밀번호 규칙 검사',
'''첫 줄에 N, 이어서 N 줄에 새 비밀번호 후보가 주어져요. 각 후보를 검사해 결과를 출력하세요.

**[조건]**
- 함수 `check(pw)` 에서 규칙을 **아래 순서대로** 검사하고, 어기면 `raise ValueError(메시지)`.
  1. 길이가 6 미만 → `6자 이상이어야 해요`
  2. 숫자가 하나도 없음 → `숫자가 필요해요`
  3. 숫자로만 되어 있음 → `영문자가 필요해요`
- 통과하면 `check` 는 아무것도 돌려주지 않아요. 호출하는 쪽에서 `try/except ValueError as e/else` 로
  - 실패: `X 메시지`, 성공: `O 사용 가능`
- 마지막 줄에 `통과 ○개` 를 출력해요. (`any`, `isdigit` 활용)

{ex}

{ex2}''',
'''def check(pw):
    pass   # 규칙을 어기면 raise ValueError("...")

n = int(input())
ok = 0
for _ in range(n):
    pw = input()
    # try / except / else
print("통과", str(ok) + "개")''',
'''def check(pw):
    if len(pw) < 6:
        raise ValueError("6자 이상이어야 해요")
    if not any(ch.isdigit() for ch in pw):     # 숫자가 하나라도 있는지
        raise ValueError("숫자가 필요해요")
    if pw.isdigit():                            # 전부 숫자면
        raise ValueError("영문자가 필요해요")

n = int(input())
ok = 0
for _ in range(n):
    pw = input()
    try:
        check(pw)
    except ValueError as e:
        print("X", e)                           # raise 할 때 넣은 메시지
    else:
        print("O 사용 가능")
        ok += 1
print("통과", str(ok) + "개")''',
    ['3\nabc12\nabcdef\nnest2026', '2\n123456\ngo4it99'], ['1\na1', '2\nzzzzz9\n000000', '4\nabcdefgh\nA1B2C3\n12345\n9x9x9x'],
    ['`if len(pw) < 6: raise ValueError("6자 이상이어야 해요")`',
     '숫자가 있는지: `any(ch.isdigit() for ch in pw)`, 전부 숫자인지: `pw.isdigit()`.',
     '`except ValueError as e: print("X", e)` / `else:` 에서 `ok += 1`.'],
    '`raise` 는 그 자리에서 함수를 멈추니 규칙은 **먼저 쓴 것부터** 하나만 걸려요. `"abc12"` 는 길이 5 라 숫자·영문 검사까지 가지 않아요.')

L.essay('환율 계산기에서 `except Exception:` 을 `except KeyError:` 보다 **위에** 두면 어떤 문제가 생기는지, 이유와 함께 서술하세요.',
    'except 는 위에서부터 차례로 검사해 처음 맞는 블록 하나만 실행한다. Exception 은 KeyError·ValueError 등 거의 모든 오류의 부모 클래스이므로 맨 위의 except Exception 이 모든 오류를 먼저 잡아 버린다. 그래서 아래의 except KeyError 블록은 절대 실행되지 않아 "없는 통화" 같은 구체적인 안내를 할 수 없다. 구체적인 오류를 위에, Exception 을 맨 아래에 두어야 한다.',
    ['except 는 위에서부터 처음 맞는 하나만 실행', 'Exception 은 모든 오류의 부모', '아래 KeyError 블록이 실행되지 않는다', '구체적인 오류를 위에 둔다'])

# =====================================================================
L = C.lesson('δ-12 numpy 심화 기초: 슬라이싱·boolean indexing·where·sort·argsort', 40,
'''- 2차원 배열: `a[행, 열]`, `a[1]` 은 1번 행, `a[:, -1]` 은 마지막 열, `a[[0, 2]]` 는 0·2번 행.
- `a[a > 5]` → 조건이 참인 칸의 값만 (1차원). 조건 여러 개는 `(조건1) & (조건2)`, `|`.
- `np.where(조건)` → 참인 칸의 **위치**(2차원이면 행 배열, 열 배열). `np.where(조건, x, y)` 는 골라 바꾸기.
- `np.sort(a)` 는 오름차순 **새 배열**, 내림차순은 `np.sort(a)[::-1]`.
- `np.argsort(a)` 는 정렬했을 때의 **인덱스** → `names[np.argsort(scores)[::-1]]` 로 점수순 이름.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간에는 try/except/else/finally, KeyError·ValueError, raise 로 환율 계산기를 만들었어요.'),
     REVEAL_RUN('`{"a": 1}["b"]` 를 try 로 감싸 `except KeyError as e: print(type(e).__name__)` 하면?',
                'try:\n    {"a": 1}["b"]\nexcept KeyError as e:\n    print(type(e).__name__)')])
L.output('복습: 출력은?', 'for s in ["3", "x"]:\n    try:\n        n = int(s)\n    except ValueError:\n        print("V")\n    else:\n        print(n * 2)\n    finally:\n        print("F")',
    '"3" → else 의 6 → F. "x" → V → F. finally 는 항상!\n\n```\n{out}\n```', review=True)

L.explain('2차원 배열 슬라이싱 — 행과 열 고르기',
    [T('numpy 2차원 배열은 `a[행, 열]` 로 한 칸을 골라요. 쉼표 **앞이 행, 뒤가 열**이에요.\n'
       '`:` 는 "전부", 음수는 뒤에서부터예요. 리스트의 `a[1][2]` 와 같은 칸이에요.'),
     CODE('''import numpy as np
a = np.array([[1, 2, 3, 4],
              [5, 6, 7, 8],
              [9, 10, 11, 12]])
print(a[1, 2])
print(a[1])
print(a[:, -1])
print(a[1:, :2])''', '행·열 슬라이싱 (읽기 전용)', run_=False),
     WARN('이 사이트에선 numpy 가 **실행되지 않아요**. 출력은 아래 문제로 예측해 보세요.')],
    [T('행 번호를 **리스트로** 주면 원하는 행들만 골라요. `a[[0, 2]]` 는 0번·2번 행.\n'
       '`a[[0, 2], -1]` 은 그 행들의 마지막 열 값이에요.'),
     REVEAL_RUN('`a[[0, 2]]` 와 `a[[0, 2], -1]` 의 결과는?', '''import numpy as np
a = np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])
print(a[[0, 2]])
print(a[[0, 2], -1])'''),
     EXAM('2025년엔 "특정 행을 고르고 **마지막 열**만 슬라이싱" 하는 문항(6점)이 나왔어요.')])

L.output('출력을 예측하세요. (numpy — 손으로!)', '''\
import numpy as np
score = np.array([[80, 90, 70],
                  [60, 75, 95],
                  [85, 65, 88]])
print(score[2, 0])
print(score[:, 1])
print(score[0:2, -1])
print(score[[1, 2], :2])''',
    '`score[:, 1]` 은 **모든 행의 1번 열**, `score[0:2, -1]` 은 0~1행의 마지막 열이에요. 결과는 1차원이면 한 줄로 나와요.\n\n```\n{out}\n```')

L.explain('boolean indexing — 조건으로 고르기',
    [T('`a > 5` 처럼 배열에 조건을 쓰면 칸마다 True/False 가 든 **같은 모양의 배열**이 나와요.\n'
       '그 배열을 `a[ ]` 안에 넣으면 **True 인 칸의 값만** 1차원으로 꺼내요.'),
     CODE('''import numpy as np
a = np.array([3, 8, 1, 6, 9, 2])
print(a > 5)
print(a[a > 5])
print(a[a % 2 == 0])''', 'boolean indexing (읽기 전용)', run_=False)],
    [T('조건 두 개는 `and`·`or` 가 아니라 **`&`·`|`** 를 쓰고, 각 조건을 **괄호**로 감싸요.\n'
       '고른 칸에 값을 넣으면 그 칸만 바뀌어요: `a[a < 3] = 0`.'),
     CMP(side('리스트라면', '컴프리헨션으로', 'a = [3, 8, 1, 6, 9, 2]\nprint([x for x in a if 2 < x < 9])', 'good'),
         side('numpy 라면', '괄호 + & — 결과는 `[3 8 6]` (읽기 전용)\n```python\na = np.array([3, 8, 1, 6, 9, 2])\nprint(a[(a > 2) & (a < 9)])\n```', '', 'good')),
     KEY('numpy 의 `a[a > 5]` 는 리스트의 `[x for x in a if x > 5]` 와 같은 일을 해요. 실습은 이 리스트 방식으로 해요.')])

L.output('출력을 예측하세요.', '''\
import numpy as np
a = np.array([[4, 9, 2],
              [7, 5, 8]])
print(a[a >= 5])
print(a[(a > 3) & (a % 2 == 0)])
a[a < 5] = 0
print(a)''',
    '2차원 배열도 조건으로 고르면 **행 순서대로 읽은 1차원** 결과가 나와요. 마지막엔 5 미만 칸(4, 2)만 0 이 돼요.\n\n```\n{out}\n```')

L.spot('실행하면 **오류**가 나는 줄은?', '''\
import numpy as np
a = np.array([2, 5, 7, 10])
print(a[a > 3])
print(a[a > 3 and a < 8])''', 4,
    '`and` 는 True/False **하나**를 원하는데 `a > 3` 은 값이 여러 개인 배열이라 `ValueError: The truth value of an array ... is ambiguous`. `a[(a > 3) & (a < 8)]` 로 써야 해요.',
    error_line=4)

L.explain('np.where — 위치 찾기와 골라 바꾸기',
    [T('`np.where(조건)` 은 조건이 참인 칸의 **위치(인덱스)** 를 돌려줘요.\n'
       '2차원이면 **(행 번호 배열, 열 번호 배열)** 두 개가 나와요. 같은 순서끼리 짝지으면 위치가 돼요.'),
     CODE('''import numpy as np
seat = np.array([[1, 0, 1],
                 [0, 1, 0]])
r, c = np.where(seat == 0)
print(r, c)
for i, j in zip(r, c):
    print(int(i) + 1, "행", int(j) + 1, "열 빈자리")''', '빈자리 찾기 (읽기 전용)', run_=False),
     EXAM('2025년 8점: 좌석 배열에서 `np.where` 로 **빈자리 위치**를 찾는 문항.')],
    [T('`np.where(조건, 참일 때 값, 거짓일 때 값)` 처럼 세 개를 주면 칸마다 골라서 **새 배열**을 만들어요.'),
     REVEAL_RUN('점수 60 이상은 1, 미만은 0 으로 바꾸면?', '''import numpy as np
s = np.array([55, 80, 60, 42])
print(np.where(s >= 60, 1, 0))
print(np.where(s >= 60))'''),
     TIP('1차원 배열의 `np.where(조건)` 도 **튜플 하나**에 배열이 들어 있어요. 그래서 `np.where(...)[0]` 으로 꺼내 쓰는 경우가 많아요.')])

L.output('출력을 예측하세요.', '''\
import numpy as np
hall = np.array([[0, 1, 1],
                 [1, 0, 0],
                 [1, 1, 0]])
r, c = np.where(hall == 0)
print(r)
print(c)
print(len(r))
print(np.where(hall == 1, "X", "O")[1])''',
    '행 우선(0행 → 1행 → 2행)으로 0 인 칸을 찾아 행 번호와 열 번호를 따로 모아요. 빈자리는 (0,0), (1,1), (1,2), (2,2).\n\n```\n{out}\n```')

L.explain('np.sort 와 argsort',
    [T('`np.sort(a)` 는 **오름차순으로 정렬한 새 배열**을 돌려줘요. 원본은 그대로예요.\n'
       '내림차순 옵션이 따로 없어서 `np.sort(a)[::-1]` 로 **뒤집어요**.'),
     CODE('''import numpy as np
a = np.array([30, 10, 50, 20])
b = np.sort(a)
print(b)
print(b[::-1])
print(a)''', 'np.sort (읽기 전용)', run_=False)],
    [T('`np.argsort(a)` 는 값이 아니라 **정렬했을 때 각 자리에 올 원래 인덱스**를 돌려줘요.\n'
       '`a = [30, 10, 50, 20]` 이면 가장 작은 10 은 1번, 다음 20 은 3번 … → `[1 3 0 2]`.\n'
       '이 인덱스로 **다른 배열**(이름)을 같은 순서로 줄 세울 수 있어요.'),
     CODE('''import numpy as np
names = np.array(["가람", "나래", "다온", "라희"])
score = np.array([30, 10, 50, 20])
idx = np.argsort(score)
print(idx)
print(names[idx])
print(names[idx[::-1]])''', 'argsort 로 이름 정렬 (읽기 전용)', run_=False),
     EXAM('2025년엔 np.sort 내림차순(6점)과 argsort 로 이름 배열 정렬(15점)이 나왔어요.')])

L.output('출력을 예측하세요.', '''\
import numpy as np
time = np.array([42, 35, 50, 38])
who = np.array(["A", "B", "C", "D"])
print(np.sort(time)[::-1])
print(np.argsort(time))
print(who[np.argsort(time)][:2])
print(who[np.argsort(time)[::-1][0]])''',
    '오름차순 35(B) 38(D) 42(A) 50(C) → argsort 는 `[1 3 0 2]`. 앞 두 명은 B, D. 뒤집어서 첫 번째는 가장 큰 50 의 C.\n\n```\n{out}\n```')

L.match('코드와 돌려주는 것을 이어 보세요. (`a = np.array([7, 2, 9])`)',
    [['np.sort(a)', '[2 7 9]  (정렬된 값)'], ['np.argsort(a)', '[1 0 2]  (정렬 순서의 인덱스)'], ['np.sort(a)[::-1]', '[9 7 2]  (내림차순 값)'],
     ['a[a > 5]', '[7 9]  (조건에 맞는 값)'], ['np.where(a > 5)', '(array([0, 2]),)  (조건에 맞는 위치)']],
    '**값**을 주는 것(sort, boolean indexing)과 **위치**를 주는 것(argsort, where)을 구분하는 게 핵심이에요.')

L.bucket('결과가 **값**인지 **위치(인덱스)** 인지 분류하세요.', ['값', '위치(인덱스)'],
    [['np.sort(a)', 1], ['np.argsort(a)', 2], ['a[a % 2 == 0]', 1], ['np.where(a == 0)', 2], ['a[:, -1]', 1],
     ['np.argsort(a)[::-1]', 2], ['np.where(a > 0, a, 0)', 1]],
    '`np.where` 에 인자를 세 개 주면 **값**으로 채운 새 배열이에요. 하나만 주면 위치!')

L.fill('점수가 높은 순으로 이름을 출력하세요.', '''\
import numpy as np
names = np.array(["솔", "라", "시"])
score = np.array([70, 95, 80])
idx = np.___(score)___
print(names[idx])''', [['argsort'], ['[::-1]']],
    '`np.argsort(score)` 는 오름차순 인덱스 `[0 2 1]`, `[::-1]` 로 뒤집으면 `[1 2 0]` → 라, 시, 솔.', expect="['라' '시' '솔']")

L.practice('[기출유사] 공연장 빈자리 찾기 (np.where 를 리스트로)',
'''공연장 좌석 상태가 주어져요. 첫 줄에 행 수 R, 이어서 R 줄에 좌석 상태(1 = 예약, 0 = 빈자리)가 공백으로 주어져요.

numpy 의 `np.where(seat == 0)` 이 하는 일을 **순수 파이썬 리스트**로 직접 구현하세요. (사이트에선 numpy 가 실행되지 않아요)

**[조건]**
- 좌석은 리스트의 리스트에 담아요.
- 빈자리를 **행 우선**(위 행부터, 같은 행은 왼쪽부터)으로 찾아 `행 열` 을 한 줄씩 출력해요. (번호는 **1부터**)
- 마지막 줄에 `빈자리 ○석` 을 출력해요. 빈자리가 없으면 `빈자리 0석` 만 출력해요.

{ex}

{ex2}''',
'''r = int(input())
seat = [list(map(int, input().split())) for _ in range(r)]
cnt = 0
# 빈자리 위치를 출력하세요
print(f"빈자리 {cnt}석")''',
'''r = int(input())
seat = [list(map(int, input().split())) for _ in range(r)]   # list of list
cnt = 0
for i, row in enumerate(seat):          # 위 행부터
    for j, v in enumerate(row):         # 왼쪽부터
        if v == 0:                      # np.where(seat == 0) 과 같은 조건
            print(i + 1, j + 1)         # 1부터 번호
            cnt += 1
print(f"빈자리 {cnt}석")''',
    ['2\n1 0 1\n0 1 0', '3\n0 0\n1 1\n1 0'], ['1\n1 1 1', '1\n0', '3\n1 1 0 1\n0 1 1 1\n1 1 1 0'],
    ['`seat = [list(map(int, input().split())) for _ in range(r)]` 는 스타터에 있어요.',
     '`for i, row in enumerate(seat):` 안에 `for j, v in enumerate(row):`.',
     '`if v == 0:` 이면 `print(i + 1, j + 1)` 하고 `cnt += 1`.'],
    'numpy 로는 `r, c = np.where(seat == 0)` 한 줄이에요. np.where 도 행 우선으로 위치를 모으기 때문에 이 이중 for 문과 같은 순서가 나와요.')

L.practice('[기출유사] 기록순 이름 정렬 (argsort 를 리스트로)',
'''달리기 기록 측정 결과예요. 첫 줄에 이름들, 둘째 줄에 기록(초, 정수)이 같은 순서로 공백 구분되어 주어져요. 기록은 모두 달라요.

numpy 의 `np.argsort` 가 하는 일을 순수 파이썬으로 구현하세요.

**[조건]**
- 1줄: `argsort: …` — 기록 **오름차순**으로 정렬했을 때의 원래 인덱스들 (`sorted(range(n), key=lambda i: …)`)
- 2줄: `빠른 순: …` — 그 인덱스로 이름을 줄 세운 결과
- 3줄: `느린 순: …` — 인덱스를 뒤집어(`[::-1]`) 줄 세운 결과
- 4줄: `상위 3명 평균: ○` — 가장 빠른 3명(3명 미만이면 전원) 기록의 평균, 소수 첫째 자리 `f"{값:.1f}"`

{ex}

{ex2}''',
'''names = input().split()
rec = list(map(int, input().split()))
n = len(names)
idx = []   # argsort 결과를 만드세요
''',
'''names = input().split()
rec = list(map(int, input().split()))
n = len(names)
idx = sorted(range(n), key=lambda i: rec[i])        # 기록 오름차순 인덱스 (= np.argsort)
print("argsort:", " ".join(map(str, idx)))
print("빠른 순:", " ".join(names[i] for i in idx))   # 인덱스로 이름 줄 세우기
print("느린 순:", " ".join(names[i] for i in idx[::-1]))
top = [rec[i] for i in idx[:3]]                      # 가장 빠른 3명 (3명 미만이면 전원)
print(f"상위 3명 평균: {sum(top) / len(top):.1f}")''',
    ['A B C D\n42 35 50 38', '하늘 바다 산\n61 58 70'], ['solo\n99', '갑 을\n20 10', 'a b c d e f\n9 3 7 1 8 2'],
    ['`sorted(range(n), key=lambda i: rec[i])` — 인덱스 0~n-1 을 **기록 기준으로** 정렬해요.',
     '이름 줄 세우기: `" ".join(names[i] for i in idx)`.',
     '`idx[:3]` 은 3명 미만이어도 오류 없이 있는 만큼만 잘라요.'],
    'np.argsort 의 정체는 "인덱스를 값 기준으로 정렬한 것" 이에요. 그래서 `sorted(range(n), key=lambda i: rec[i])` 와 결과가 같아요. 이 인덱스 하나로 이름·기록 등 여러 배열을 같은 순서로 줄 세울 수 있어요.')

L.essay('numpy 배열 `a` 에서 `a[a > 3 and a < 8]` 은 오류가 나요. 오류가 나는 **이유**와 올바르게 고친 코드를 서술하세요.',
    '`a > 3` 의 결과는 True/False 하나가 아니라 칸마다 True/False 가 들어 있는 배열이다. and 는 양쪽을 하나의 참/거짓으로 판단해야 하는데 배열은 여러 값이라 참인지 거짓인지 정할 수 없어 ValueError 가 발생한다. 배열의 칸별 논리곱은 & 를 쓰고 연산자 우선순위 때문에 각 조건을 괄호로 감싸 `a[(a > 3) & (a < 8)]` 로 써야 한다.',
    ['a > 3 의 결과는 True/False 배열', 'and 는 하나의 참/거짓이 필요해 ValueError', '& 를 사용', '각 조건을 괄호로 감싼다'])

if __name__ == '__main__':
    C.save(sys.argv[1] if len(sys.argv) > 1 else '/tmp/delta.json')
