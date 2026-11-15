import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lotc import *

C = Course('γ', '1학년 2학기 1차고사 범위: 예외 처리(try·except·else·finally·raise, ValueError·KeyError·IndexError·FileNotFoundError), '
           '파일 입출력(with open·r/w/a 모드·readlines·인코딩·CSV·단어 빈도·파일 합치기), 모듈(import·from·as·__name__·random·math), '
           '클래스 기초(__init__·self·메서드·__str__), 클래스 변수와 인스턴스 변수·is 와 ==, 상속·super·오버라이딩·NotImplementedError, '
           '다중상속과 MRO(기초), 캡슐화(private 속성·getter/setter·AttributeError), 연산자 오버로딩(__add__·__sub__·__str__), '
           'numpy 기초(array·shape·mean·max·ones·arange·reshape·배열 연산·조건 개수)')

# =====================================================================
L = C.lesson('γ-01 시작하기: 2학기 1차 시험 지도 + β 실력 점검', 20,
'''- 2학기 1차는 **예외 처리 · 파일 · 모듈 · 클래스(객체지향)** 가 중심이에요. 최근엔 **numpy** 도 나와요.
- 큰 문항(12~20점)은 **클래스 + 상속/캡슐화/연산자 오버로딩** 과 **파일 + 딕셔너리** 프로그램이에요.
- β 내용(컴프리헨션·함수·딕셔너리·set)은 클래스의 **메서드 안에서** 그대로 다시 써요.
- 개념 → 확인 문제 → 기출유사 실습 순서. 다 끝나면 **A.C.E. [γ]** 로 실전!''')

L.explain('이번 시험은 이렇게 나와요',
    [T('1학년 2학기 **1차고사(중간)** 는 7~10문항, 100점이에요.\n'
       '1학기보다 **서술형(왜 오류가 나는가)** 비중이 커졌어요. 문항 모양은 다섯 가지예요.'),
     STEPS(('A 출력 추론 (6~12점)', '상속·super·클래스 변수·MRO 코드의 출력을 손으로 따라가 적어요.'),
           ('B 오류 위치·이유 서술 (10~15점)', '"몇 번째 줄에서 어떤 예외가, 왜 나는가" 를 쓰고, 그 예외가 나는 **입력 예시**도 써요.'),
           ('C 클래스 완성 (12~18점)', '__init__·__str__·getter·__add__ 같은 메서드 빈칸을 채우거나 직접 작성해요.'),
           ('D 파일 + 딕셔너리 (12~14점)', 'with open 으로 읽고 쓰기, CSV, 단어 빈도, 파일 합치기.'),
           ('E 모듈·numpy (11~15점)', 'import/from/as 의 차이, __name__ 의 이유, numpy 배열 연산 결과.'))],
    [T('3개년(2023~2025) 동안 자주 나온 소재예요.\n'
       '이 코스의 예제는 이 소재들을 **구조를 바꿔서** 다뤄요.'),
     FLIP(['예외 처리', '3년 연속 — 발생 줄·이유·입력 예시 서술, try/except 로 고치기'],
          ['파일 입출력', '거의 매년 — with open, readlines, CSV, 파일 합치기, FileNotFoundError'],
          ['클래스·상속·super', '매년 — __init__·__str__·오버라이딩·출력 추론'],
          ['캡슐화', '2024·2025 — private 속성 접근 시 AttributeError 이유'],
          ['연산자 오버로딩', '2024·2025 — Vector, Color 의 __add__·__sub__'],
          ['모듈·__name__', '3년 모두 — import 형태, __name__ == "__main__" 이유'],
          ['numpy', '2025 신규 — array·shape·mean·reshape·조건 개수'])],
    [T('공부 순서는 이렇게 추천해요.\n\n'
       '1. 레슨 하나를 끝까지(복습 → 개념 → 확인 → 실습).\n'
       '2. 틀린 문제는 🔁 오답 복습에서 다시.\n'
       '3. 모든 레슨이 끝나면 **A.C.E. [γ]** 문제집으로 실전 연습.'),
     EXAM('서술형은 **"무엇이(예외 이름) · 어디서(줄) · 왜(원인) · 어떻게 고치나"** 네 가지를 다 쓰면 만점에 가까워요.')])

L.choice('다음 중 2학기 1차에서 **3년 동안 빠짐없이** 나온 내용이 아닌 것은?',
    ['예외 처리(try/except)', '클래스와 상속', 'numpy 배열', '모듈 import'], 3,
    'numpy 는 2025년에 **처음** 나왔어요. 예외 처리·클래스·모듈은 3년 모두 나왔어요. 그래도 새로 나온 내용은 다음 해에 또 나올 수 있으니 γ-13 에서 다뤄요.')

L.explain('β 점검 ① 문자열·컴프리헨션·map/filter',
    [T('2학기 문제에서도 데이터 손질은 β 도구로 해요.\n'
       '`split`·`join`·`strip` 과 **컴프리헨션** 한 줄은 거의 모든 문항에 등장해요.'),
     CODE('line = " 3, 8, 15 ,4 "\nnums = [int(x) for x in line.split(",")]\nprint(nums)\nprint([n for n in nums if n % 2 == 0])', '컴프리헨션 복습'),
     TIP('`int(" 15 ")` 처럼 앞뒤 공백이 있어도 int() 는 알아서 무시해요. 하지만 `"15a"` 처럼 다른 글자가 있으면 ValueError!')],
    [T('같은 일을 `map`·`filter`·`lambda` 로도 할 수 있어요. 결과가 **map/filter 객체**라 `list()` 로 감싸야 보여요.'),
     TABS(('컴프리헨션', '', 'a = [1, 2, 3, 4, 5]\nprint([x * x for x in a if x > 2])'),
          ('map + filter', '', 'a = [1, 2, 3, 4, 5]\nprint(list(map(lambda x: x * x, filter(lambda x: x > 2, a))))'),
          ('enumerate', '', 'names = ["kim", "lee"]\nfor i, n in enumerate(names, 1):\n    print(i, n)'))])

L.output('출력 결과를 그대로 쓰세요.', '''\
names = ["Ari", "Bo", "Chan"]
scores = [90, 75, 88]
for i, (n, s) in enumerate(zip(names, scores), 1):
    if s >= 80:
        print(i, n.upper(), s)''',
    '`zip` 으로 이름과 점수를 짝짓고 `enumerate(…, 1)` 로 번호를 1부터 붙였어요. 80 이상만 출력해요.\n\n```\n{out}\n```')

L.explain('β 점검 ② 함수: 기본값·*args·**kwargs·global',
    [T('클래스의 메서드도 결국 **함수**예요. 매개변수 규칙을 다시 떠올려 봐요.\n'
       '`*args` 는 남는 위치 인자를 **튜플**로, `**kwargs` 는 이름 붙은 인자를 **딕셔너리**로 모아요.'),
     CODE('def info(name, *args, grade=1, **kwargs):\n    print(name, args, grade, kwargs)\n\ninfo("kim", 90, 85, grade=2, club="AI")', '매개변수 종류'),
     WARN('함수 안에서 바깥 변수에 **값을 대입**하려면 `global` 이 필요해요. 없으면 UnboundLocalError!')],
    [T('함수 안의 변수는 **지역 변수**라 함수가 끝나면 사라져요. 바깥에 결과를 주려면 `return` 을 써요.'),
     CMP(side('return 으로 돌려주기', '권장 방법', 'def add(a, b=10):\n    return a + b\n\nprint(add(5), add(5, 1))', 'good'),
         side('global 로 바꾸기', '되긴 하지만 꼭 필요할 때만', 'total = 0\ndef add(x):\n    global total\n    total += x\n\nadd(3)\nadd(4)\nprint(total)', 'good'))])

L.fill('여러 개의 점수를 받아 **평균**을 돌려주는 함수를 완성하세요.', '''\
def avg(___):
    return sum(scores) / len(scores)

print(avg(80, 90, 100))''', [['*scores']],
    '`*scores` 는 넘긴 값들을 **튜플** `(80, 90, 100)` 로 모아요. 그래서 sum/len 을 바로 쓸 수 있어요. 결과는 `90.0`.',
    expect='90.0')

L.explain('β 점검 ③ 딕셔너리·set·재귀',
    [T('딕셔너리 **누적**은 `d[k] = d.get(k, 0) + 1` 한 줄이 공식이에요.\n'
       '파일에서 단어 빈도를 셀 때(γ-05) 그대로 써요.'),
     CODE('words = "a b a c b a".split()\nfreq = {}\nfor w in words:\n    freq[w] = freq.get(w, 0) + 1\nprint(freq)', '빈도 세기')],
    [T('set 은 **중복 없음**, 합집합 `|`, 교집합 `&`, 차집합 `-`.\n'
       '재귀는 **종료 조건 + 자기 자신 호출** 두 부분으로 이루어져요.'),
     TRACE('''\
def fact(n):
    if n == 1:
        return 1
    return n * fact(n - 1)

print(fact(4))''', '재귀 따라가기')])

L.match('β 에서 배운 도구와 결과를 이어 보세요.',
    [['{1, 2} | {2, 3}', '{1, 2, 3}'], ['{1, 2} & {2, 3}', '{2}'], ['{1, 2} - {2, 3}', '{1}'],
     ['d.get("x", 0)  (x 가 없을 때)', '0'], ['len(set("banana"))', '3']],
    '`|` 합, `&` 교, `-` 차. `get` 은 키가 없으면 기본값. `set("banana")` 는 {b, a, n} 세 글자.')

L.spot('실행하면 **오류**가 나는 줄은?', '''\
stock = {"pen": 3, "note": 5}
stock["pen"] += 1
print(stock.get("eraser", 0))
print(stock["eraser"])
print(stock)''', 4,
    '`stock["eraser"]` 는 없는 키를 대괄호로 꺼내서 **KeyError** 예요. 3번 줄의 `get` 은 기본값 0 을 돌려줘 안전해요. 이번 γ 에서는 이 오류를 **try/except 로 잡는 법**을 배워요.',
    error_line=4)

L.output('출력은?', '''\
def count_down(n):
    if n == 0:
        return "발사"
    return str(n) + " " + count_down(n - 1)

print(count_down(3))''',
    '`count_down(3)` → "3 " + count_down(2) → … → count_down(0) 이 "발사" 를 돌려주면 차례로 이어 붙어요.\n\n```\n{out}\n```')

L.short('출력값을 쓰세요: `print(len(set([1, 2, 2, 3, 3, 3])))`', '3',
    'set 은 중복을 없애 {1, 2, 3} 만 남아요. 중복 제거 → 개수 세기는 단골 패턴이에요.',
    check_code='print(len(set([1, 2, 2, 3, 3, 3])))')

L.bucket('자료형을 **가변(값을 그 자리에서 바꿀 수 있음)** 과 **불변**으로 분류하세요. 클래스 단원에서도 중요해요.', ['가변', '불변'],
    [['list', 1], ['dict', 1], ['set', 1], ['str', 2], ['tuple', 2], ['int', 2]],
    '리스트·딕셔너리·set 은 append·키 추가·add 로 그 자리에서 바뀌어요. 문자열·튜플·정수는 바꾸면 **새 값**이 만들어져요. γ-08 의 "클래스 변수 리스트 함정" 이 바로 가변 자료형 때문에 생겨요.')

L.ox('`lambda x: x * 2` 는 이름 없이 한 줄로 만드는 함수로, `map(lambda x: x * 2, [1, 2])` 처럼 다른 함수에 넘겨 쓸 수 있다.', True,
     'lambda 는 `def` 없이 만드는 작은 함수예요. map·filter·sorted 의 key 에 자주 넘겨요.')

L.practice('[기출유사] 성적표 — 번호·평균·최고점',
'''첫 줄에 학생 수 N, 다음 N 줄에 `이름 점수` 가 주어져요. 딕셔너리에 저장한 뒤 다음을 출력하세요.

**[조건]**
- `scores = {}` 딕셔너리에 `이름: 점수` 로 저장해요.
- `enumerate(…, 1)` 로 입력 순서대로 `번호. 이름 점수` 를 출력해요.
- 마지막 두 줄: `평균 값` (소수 첫째 자리 `round`), `최고 이름` (같은 점수면 먼저 입력한 사람)

{ex}

{ex2}''',
'''n = int(input())
scores = {}
# N 줄을 읽어 딕셔너리에 저장하세요

# 번호와 함께 출력하세요
''',
'''n = int(input())
scores = {}
for _ in range(n):
    name, s = input().split()     # 이름과 점수 나누기
    scores[name] = int(s)
for i, (name, s) in enumerate(scores.items(), 1):   # 번호는 1부터
    print(f"{i}. {name} {s}")
print("평균", round(sum(scores.values()) / n, 1))
best = max(scores, key=scores.get)  # 점수가 가장 큰 키(동점이면 먼저 넣은 것)
print("최고", best)''',
    ['3\nkim 80\nlee 95\npark 77', '2\nAri 100\nBo 100'], ['1\nsolo 0', '4\na 1\nb 2\nc 3\nd 3', '3\nx 50\ny 51\nz 49'],
    ['`name, s = input().split()` 으로 나누고 `int(s)` 로 저장해요.',
     '`for i, (name, s) in enumerate(scores.items(), 1):` 구조예요.',
     '최고점은 `max(scores, key=scores.get)` — 딕셔너리는 넣은 순서를 기억해서 동점이면 먼저 넣은 키가 나와요.'],
    '`scores.items()` 는 (키, 값) 쌍을 순서대로 줘요. `max(딕셔너리, key=딕셔너리.get)` 은 값이 가장 큰 **키**를 찾는 단골 패턴이에요.')

L.essay('다음 코드는 오류가 나요. **어떤 오류가 왜** 나는지 쓰고, 고치는 방법을 쓰세요.\n\n```python\ncount = 0\ndef up():\n    count += 1\nup()\n```',
    '함수 안에서 count 에 값을 대입하므로 파이썬은 count 를 지역 변수로 본다. 그런데 지역 변수 count 에 아직 값이 없는 상태에서 count + 1 을 계산하려 하므로 UnboundLocalError 가 발생한다. 함수 첫 줄에 `global count` 를 쓰거나, 값을 매개변수로 받아 return 으로 돌려주도록 고친다.',
    ['UnboundLocalError(지역 변수 문제)', '대입이 있으면 지역 변수로 본다', 'global count 추가 또는 return 사용'])

# =====================================================================
L = C.lesson('γ-02 예외 처리 ①: try / except 기초', 25,
'''- **예외(Exception)** = 실행 중에 생기는 오류. 처리하지 않으면 프로그램이 멈춰요.
- `try:` 안에서 예외가 나면 **그 아래 줄은 건너뛰고** 맞는 `except` 로 가요.
- 단골 예외: `ValueError`(int("a")), `ZeroDivisionError`, `IndexError`, `KeyError`, `TypeError`, `FileNotFoundError`.
- `except 예외이름 as e:` 로 오류 메시지를 꺼낼 수 있어요.
- 잘못된 입력을 다시 받으려면 `while True` + `try` + `break`.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간에는 시험 지도와 β 핵심(컴프리헨션, 함수 인자, 딕셔너리 누적, 재귀)을 점검했어요.\n'
       '오늘은 그때 만났던 **KeyError** 같은 오류를 잡는 법을 배워요.'),
     REVEAL_RUN('`d = {}` 일 때 `d.get("a", 0) + 1` 의 값은?', 'd = {}\nprint(d.get("a", 0) + 1)')])
L.output('복습: 출력은?', 'a = [3, 1, 2]\nprint([x * 2 for x in a if x != 1])',
    '1 을 뺀 3, 2 를 두 배로 → {out}', review=True)

L.explain('오류에도 이름이 있어요',
    [T('파이썬 오류는 두 종류예요.\n'
       '- **문법 오류(SyntaxError)**: 실행하기 전에 발견. 괄호·콜론 빠짐 등.\n'
       '- **예외(Exception)**: 문법은 맞지만 **실행 중에** 생긴 문제. 이것을 try/except 로 잡아요.'),
     CODE('n = int("12a")\nprint(n)', '실행해서 예외 이름을 확인해 보세요', expect_error=True)],
    [T('예외 메시지 맨 아래 줄 `ValueError: invalid literal for int()…` 에서 **콜론 앞이 예외 이름**이에요.\n'
       '시험에 자주 나오는 예외를 카드로 외워 봐요.'),
     FLIP(['ValueError', '값의 모양이 잘못됨 — int("abc"), int("3.5")'],
          ['ZeroDivisionError', '0 으로 나눔 — 10 / 0, 10 % 0'],
          ['IndexError', '없는 번호 — [1, 2][5]'],
          ['KeyError', '없는 키 — {"a": 1}["b"]'],
          ['TypeError', '자료형이 안 맞음 — "3" + 4'],
          ['NameError', '없는 이름 — 정의 안 한 변수 사용'],
          ['FileNotFoundError', '없는 파일을 "r" 로 열기'],
          ['AttributeError', '없는 속성·메서드 — (5).append(1), private 속성 접근'])])

L.bucket('각 코드를 실행하면 나는 예외로 분류하세요.', ['ValueError', 'IndexError', 'KeyError', 'ZeroDivisionError', 'TypeError'],
    [['int("seven")', 1], ['[10, 20][2]', 2], ['{"x": 1}["y"]', 3], ['7 // 0', 4], ['"7" + 1', 5],
     ['float("1.2.3")', 1], ['"abc"[-4]', 2], ['len(5)', 5]],
    '값 모양이 틀리면 ValueError, 번호가 범위 밖이면 IndexError, 키가 없으면 KeyError, 0 으로 나누면 ZeroDivisionError, 자료형이 안 맞으면 TypeError 예요. `len(5)` 는 정수에 길이가 없어서 TypeError.')

L.explain('try / except 의 흐름',
    [T('위험한 줄을 `try:` 에 넣고, 예외가 났을 때 할 일을 `except 예외이름:` 에 써요.\n'
       '예외가 나면 프로그램이 멈추지 않고 except 로 **점프**해요.'),
     CODE('try:\n    n = int(input())\n    print(n * 2)\nexcept ValueError:\n    print("숫자가 아니에요")\nprint("끝")', '입력 abc 로 실행', stdin='abc\n')],
    [T('흐름을 한 단계씩 따라가 봐요.'),
     STEPS(('1. try 블록 실행', '위에서부터 한 줄씩 실행해요.'),
           ('2. 예외 발생!', '`int("abc")` 에서 ValueError. **try 의 나머지 줄(print(n * 2))은 건너뛰어요.**'),
           ('3. 맞는 except 찾기', '`except ValueError:` 가 있으니 그 안을 실행해요.'),
           ('4. 계속 진행', 'try/except 다음 줄 `print("끝")` 으로 이어가요. 프로그램은 멈추지 않아요.')),
     KEY('예외가 **나지 않으면** except 블록은 **실행되지 않아요.**')])

L.output('출력은?', '''\
data = ["4", "x", "2"]
total = 0
for d in data:
    try:
        total += int(d)
        print("더함", d)
    except ValueError:
        print("건너뜀", d)
print(total)''',
    '"x" 에서 ValueError → `print("더함", d)` 는 건너뛰고 except 로 가요. 반복은 계속돼요. 합은 4 + 2 = 6.\n\n```\n{out}\n```')

L.explain('잘못 입력하면 다시 받기',
    [T('시험 단골 패턴! **올바른 값이 들어올 때까지** 다시 입력받아요.\n'
       '`while True` 안에 try 를 넣고, 변환에 **성공하면 break** 해요.'),
     CODE('while True:\n    try:\n        age = int(input())\n        break\n    except ValueError:\n        print("다시 입력하세요")\nprint("나이:", age)', '입력: 열다섯 → 15.5 → 15', stdin='열다섯\n15.5\n15\n'),
     WARN('`int("15.5")` 도 **ValueError** 예요. int() 는 정수 모양 문자열만 바꿔요. 실수는 `float()` 로.')])

L.order('올바른 정수가 들어올 때까지 다시 입력받는 코드를 순서대로 놓으세요.',
    ['while True:', '    try:', '        n = int(input())', '        break', '    except ValueError:', '        print("다시")', 'print(n + 1)'],
    '`break` 는 **변환이 성공한 뒤**에 와야 해요. 변환에서 예외가 나면 break 를 건너뛰고 except 로 가서 다시 반복해요.',
    check=True, stdin='a\n9\n', expect='다시\n10')

L.explain('except 여러 개 · as e',
    [T('예외마다 다른 메시지를 주려면 `except` 를 **여러 개** 써요. 위에서부터 맞는 것 **하나만** 실행돼요.\n'
       '`as e` 를 붙이면 오류 메시지를 변수 e 에 담아요.'),
     TABS(('except 여러 개', '', 'for b in ["2", "0", "z"]:\n    try:\n        print(10 / int(b))\n    except ValueError:\n        print("숫자 아님")\n    except ZeroDivisionError:\n        print("0 으로 못 나눠요")'),
          ('튜플로 묶기', '', 'for b in ["0", "z"]:\n    try:\n        print(10 / int(b))\n    except (ValueError, ZeroDivisionError):\n        print("잘못된 입력")'),
          ('as e', '', 'try:\n    print([1, 2][5])\nexcept IndexError as e:\n    print("오류:", e)'))],
    [T('예외 이름 없이 `except:` 만 쓰거나 `except Exception:` 을 쓰면 **모든 예외**를 잡아요.\n'
       '편하지만 **무슨 오류인지 모르고 넘어가니** 시험에서는 예외 이름을 정확히 쓰는 게 좋아요.'),
     THINK('`except Exception:` 을 맨 위에 두고 그 아래 `except ValueError:` 를 두면? 위에서 다 잡아 버려서 **아래 except 는 절대 실행되지 않아요.**')])

L.output('출력은?', '''\
items = [5, 0, "a", 2]
for x in items:
    try:
        print(20 // x)
    except ZeroDivisionError:
        print("Z")
    except TypeError:
        print("T")''',
    '`20 // 0` 은 ZeroDivisionError, `20 // "a"` 는 숫자와 문자열이라 TypeError 예요.\n\n```\n{out}\n```')

L.spot('입력으로 `3.5` 를 주고 실행했어요. **예외가 발생하는 줄**은?', '''\
x = input()
print("입력:", x)
n = int(x)
print(n * 2)''', 3,
    '`int("3.5")` 는 소수점이 있어 정수 모양이 아니므로 **ValueError**. 1~2번 줄은 정상 실행되고 3번 줄에서 멈춰요. `float(x)` 를 쓰면 해결돼요.',
    error_line=3, stdin='3.5\n')

L.ox('`try` 블록 안에서 예외가 발생하면, 예외가 난 줄 **아래의 try 블록 코드도 끝까지 실행된 뒤** except 로 간다.', False,
     '예외가 나는 순간 **바로** except 로 점프해요. try 블록의 나머지 줄은 실행되지 않아요.')

L.practice('[기출유사] 안전한 나눗셈 계산기',
'''두 줄에 걸쳐 나눠지는 수 a 와 나누는 수 b 가 **문자열로** 주어져요. a 를 b 로 나눈 몫과 나머지를 출력하세요.

**[조건]**
- 두 값 모두 `int()` 로 바꿔요. 바꿀 수 없으면 `숫자만 입력하세요` 출력.
- b 가 0 이면 `0으로 나눌 수 없어요` 출력. (if 로 막지 말고 **ZeroDivisionError** 를 잡으세요)
- 정상이면 `몫: q, 나머지: r` 출력.
- 어떤 경우든 마지막 줄에 `계산 종료` 를 출력해요.

{ex}

{ex2}''',
'''a = input()
b = input()
# try / except 로 작성하세요

print("계산 종료")''',
'''a = input()
b = input()
try:
    a = int(a)                       # 숫자가 아니면 ValueError
    b = int(b)
    print(f"몫: {a // b}, 나머지: {a % b}")   # b 가 0 이면 ZeroDivisionError
except ValueError:
    print("숫자만 입력하세요")
except ZeroDivisionError:
    print("0으로 나눌 수 없어요")
print("계산 종료")''',
    ['17\n5', '9\n0'], ['abc\n3', '10\nx', '-7\n2'],
    ['예외 두 가지: `ValueError`(int 변환 실패), `ZeroDivisionError`(0 으로 나눔).',
     'try 안에 변환과 계산·출력을 모두 넣고, except 를 두 개 써요.',
     '`print("계산 종료")` 는 try/except **바깥** 맨 아래에 두면 항상 실행돼요.'],
    '`-7 // 2` 는 -4, `-7 % 2` 는 1 이에요(파이썬은 몫을 **내림**). 예외별로 except 를 나누면 메시지를 다르게 줄 수 있어요.')

L.practice('[기출유사] 숫자만 골라 합계',
'''한 줄에 공백으로 구분된 값들이 주어져요. 그중 **정수로 바꿀 수 있는 것만** 더하세요.

**[조건]**
- 각 값을 `int()` 로 바꾸되, 실패하면 ValueError 를 잡아 **잘못된 값 목록**에 넣어요.
- 첫째 줄: `합계: 값`
- 둘째 줄: `잘못된 값: a, b` (`, ` 로 연결) — 없으면 `잘못된 값: 없음`

{ex}

{ex2}''',
'''tokens = input().split()
total = 0
bad = []
# 이어서 작성하세요
''',
'''tokens = input().split()
total = 0
bad = []
for t in tokens:
    try:
        total += int(t)        # 바꿀 수 있으면 더하기
    except ValueError:
        bad.append(t)          # 실패하면 목록에 저장
print("합계:", total)
if bad:
    print("잘못된 값:", ", ".join(bad))
else:
    print("잘못된 값: 없음")''',
    ['10 abc 5 3.5 -2', '1 2 3'], ['x y z', '0', '7 7a a7 -0'],
    ['for 로 하나씩 꺼내 try 안에서 `int(t)` 를 해요.', '`except ValueError:` 에서 `bad.append(t)`',
     '마지막은 `", ".join(bad)` — bad 가 비었는지 `if bad:` 로 확인해요.'],
    '`"3.5"`·`"7a"` 는 정수 모양이 아니라 ValueError, `"-0"`·`"-2"` 는 정수로 잘 바뀌어요. 예외를 **반복문 안에서** 잡으면 하나가 틀려도 나머지는 계속 처리돼요.')

L.essay('다음 코드에 `10` 과 `0` 을 입력했을 때 **어느 줄에서 어떤 예외가, 왜** 발생하는지 쓰고, 프로그램이 멈추지 않게 고치는 방법을 서술하세요.\n\n```python\na = int(input())   # 1\nb = int(input())   # 2\nprint(a / b)       # 3\n```',
    '3번 줄에서 ZeroDivisionError 가 발생한다. 1·2번 줄의 int 변환은 정상이지만 b 가 0 이므로 a / b 는 0 으로 나누는 계산이 되기 때문이다. 3번 줄을 try 블록에 넣고 `except ZeroDivisionError:` 에서 안내 메시지를 출력하도록 고친다.',
    ['3번 줄', 'ZeroDivisionError', 'b 가 0 이라 0 으로 나눔', 'try / except ZeroDivisionError 로 처리'])

# =====================================================================
L = C.lesson('γ-03 예외 처리 ②: else · finally · raise · 발생 줄 찾기', 25,
'''- `else:` 는 **예외가 없을 때만**, `finally:` 는 **예외가 있든 없든 항상** 실행돼요.
- `raise ValueError("메시지")` 로 예외를 **직접** 일으켜요. 조건에 안 맞는 값을 막을 때 써요.
- 함수 안에서 난 예외는 **호출한 곳의 try** 까지 올라와서 잡혀요.
- 서술형: "몇 번 줄 · 어떤 예외 · 왜 · 그 예외가 나는 입력 예시" 를 쓰는 연습!''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간: try 에서 예외가 나면 나머지를 건너뛰고 맞는 except 로 점프. except 는 여러 개 둘 수 있었어요.'),
     REVEAL('`int("3.5")` 는 어떤 예외?', 'ValueError — int() 는 정수 모양 문자열만 바꿀 수 있어요.')])
L.output('복습: 출력은?', 'for v in ["8", "0", "k"]:\n    try:\n        print(16 // int(v))\n    except ValueError:\n        print("V")\n    except ZeroDivisionError:\n        print("Z")',
    '"8" → 2, "0" → ZeroDivisionError, "k" → ValueError.\n\n```\n{out}\n```', review=True)

L.explain('else 와 finally',
    [T('try 문에는 두 칸이 더 있어요.\n'
       '- `else:` — try 에서 예외가 **안 났을 때만** 실행.\n'
       '- `finally:` — 예외가 났든 안 났든 **무조건** 실행. (파일 닫기, "종료" 출력 등)'),
     TRACE('''\
for v in ["5", "z"]:
    try:
        n = int(v)
    except ValueError:
        print("실패", v)
    else:
        print("성공", n)
    finally:
        print("--")''', 'else / finally 따라가기')],
    [T('순서는 항상 **try → except → else → finally** 예요. 순서를 바꾸면 SyntaxError.'),
     CMP(side('else', '예외가 없을 때만. "성공했을 때 할 일"을 try 밖으로 빼서 깔끔하게.', '', 'good'),
         side('finally', '항상 실행. 함수 안에서 return 을 만나도 finally 는 실행돼요.', '', 'good'))])

L.output('출력은?', '''\
def check(x):
    try:
        r = 12 // x
    except ZeroDivisionError:
        print("A")
        return -1
    else:
        print("B")
        return r
    finally:
        print("C")

print(check(4))
print(check(0))''',
    '`check(4)`: 예외 없음 → else 의 B, return 전에 **finally 의 C**, 그다음 3 출력. `check(0)`: A → C → -1.\n\n```\n{out}\n```')

L.explain('raise — 예외를 직접 일으키기',
    [T('문법적으로는 괜찮지만 **조건에 맞지 않는 값**(음수 나이, 0점 미만 점수 등)도 오류로 처리하고 싶을 때가 있어요.\n'
       '`raise 예외이름("메시지")` 로 예외를 직접 일으켜요.'),
     CODE('def set_age(age):\n    if age < 0:\n        raise ValueError("나이는 음수가 될 수 없어요")\n    return age\n\ntry:\n    set_age(-3)\nexcept ValueError as e:\n    print("오류:", e)', 'raise 체험')],
    [T('함수 안에서 raise 된 예외는 함수를 빠져나와 **호출한 곳**으로 올라가요.\n'
       '호출한 곳에 try 가 있으면 거기서 잡히고, 없으면 프로그램이 멈춰요.'),
     KEY('`raise` 는 예외를 **만드는** 것, `except` 는 예외를 **잡는** 것. 짝꿍이에요.'),
     EXAM('2024년에 "변환할 수 없는 글자가 있으면 ValueError 를 raise 하라" 는 조건이 나왔어요.')])

L.fill('점수가 0~100 밖이면 **ValueError** 를 일으키는 함수를 완성하세요.', '''\
def check_score(s):
    if s < 0 or s > 100:
        ___ ValueError("범위 밖")
    return s

try:
    check_score(120)
except ___ as e:
    print(e)''', [['raise'], ['ValueError']],
    '`raise ValueError("범위 밖")` 로 일으키고, `except ValueError as e:` 로 잡아 메시지를 출력해요. 결과는 `범위 밖`.',
    expect='범위 밖')

L.explain('어느 줄에서, 어떤 입력에서 예외가 나나',
    [T('2024년 15점 문항처럼 **"이 코드에서 KeyError/IndexError/ValueError 가 각각 나는 줄과 입력 예시"** 를 묻는 문제가 나와요.\n'
       '줄마다 "여기서 무엇이 잘못될 수 있나" 를 따져 보면 돼요.'),
     CODE('''\
prices = {"apple": 1200, "milk": 2500}
line = input()              # 예: apple 3
parts = line.split()
name = parts[0]
qty = int(parts[1])
print(prices[name] * qty)''', '줄마다 생각해 보기', stdin='apple 3\n')],
    [T('줄마다 따져 봐요.'),
     STEPS(('4번 줄 parts[0]', '아무것도 입력하지 않으면 parts 가 빈 리스트 → **IndexError**'),
           ('5번 줄 parts[1]', '`apple` 처럼 한 단어만 입력 → **IndexError**'),
           ('5번 줄 int(...)', '`apple 세개` 처럼 숫자가 아니면 → **ValueError**'),
           ('6번 줄 prices[name]', '`bread 2` 처럼 없는 상품 → **KeyError**')),
     TIP('입력 예시를 쓸 때는 **그 예외 하나만** 나도록 다른 부분은 정상으로 만들어요.')])

L.match('위 코드(가격표)에 다음 입력을 주면 어떤 예외가 날까요?',
    [['milk', 'IndexError'], ['milk two', 'ValueError'], ['cola 2', 'KeyError'], ['milk 2', '예외 없음 (5000 출력)']],
    '`milk` 는 parts[1] 이 없어 IndexError, `two` 는 int 변환 실패로 ValueError, `cola` 는 가격표에 없어 KeyError 예요.')

L.choice('다음 코드에서 **KeyError** 가 나는 입력은?\n\n```python\nd = {"a": [1, 2], "b": [3]}\nk, i = input().split()\nprint(d[k][int(i)])\n```',
    ['a 1', 'b 1', 'c 0', 'a x'], 3,
    '`c` 는 딕셔너리에 없는 키라 KeyError. `b 1` 은 [3][1] 이라 IndexError, `a x` 는 int("x") 라 ValueError, `a 1` 은 정상(2 출력).')

L.spot('`process([4, 8])` 을 실행하면 예외가 납니다. **예외가 실제로 발생하는 줄**은?', '''\
def get_third(nums):
    return nums[2]

def process(nums):
    value = get_third(nums)
    return value * 2

print(process([4, 8]))''', 2,
    '실제로 터지는 곳은 `nums[2]` 가 있는 **2번 줄**(IndexError)이에요. 오류 메시지(Traceback)는 8 → 5 → 2 순으로 호출 경로를 보여 주고, **마지막에 나온 줄**이 진짜 원인이에요.',
    error_line=2)

L.short('`int(" 42 ")` 를 실행하면 결과는? (예외가 나면 예외 이름을 쓰세요)', '42',
    'int() 는 **앞뒤 공백은 무시**해요. 그래서 42 가 돼요. 하지만 `int("4 2")` 처럼 중간에 공백이 있으면 ValueError.',
    check_code='print(int(" 42 "))')

L.ox('`try:` 다음에 `except` 없이 `finally:` 만 써도 문법 오류가 아니다.', True,
     '`try / finally` 도 올바른 문법이에요. 예외를 잡지는 않지만 정리 작업은 꼭 실행돼요. 단, `try:` 만 있고 except·finally 가 **둘 다 없으면** SyntaxError.')

L.order('try 문의 네 칸을 올바른 순서로 놓으세요. (입력: `4`)',
    ['try:', '    n = 8 // int(input())', 'except ZeroDivisionError:', '    print("0 안 돼요")',
     'else:', '    print("몫", n)', 'finally:', '    print("끝")'],
    '순서는 항상 **try → except → else → finally**. 입력 4 면 예외가 없어서 else 와 finally 가 실행돼요.',
    check=True, stdin='4\n', expect='몫 2\n끝')

L.practice('[기출유사] 매점 주문 처리기',
'''매점 가격표는 `{"빵": 1500, "우유": 1200, "젤리": 800}` 이에요. 첫 줄에 주문 수 N, 다음 N 줄에 `상품 개수` 가 주어져요.

**[조건]**
- 줄마다 try/except 로 처리하고, 정상 주문은 합계에 더해요.
- 개수가 빠져 있으면 `parts[1]` 에서 나는 **IndexError** 를 잡아 `형식 오류` 출력.
- 개수가 정수가 아니면 `개수 오류`. 개수가 0 이하이면 직접 `raise ValueError` 해서 같은 `개수 오류` 출력.
- 없는 상품이면 **KeyError** 를 잡아 `없는 상품: 이름` 출력.
- 정상 주문은 `상품 x개 = 금액원`, 마지막 줄 `합계: 금액원`

{ex}

{ex2}''',
'''prices = {"빵": 1500, "우유": 1200, "젤리": 800}
n = int(input())
total = 0
for _ in range(n):
    parts = input().split()
    # try / except 로 처리하세요

print(f"합계: {total}원")''',
'''prices = {"빵": 1500, "우유": 1200, "젤리": 800}
n = int(input())
total = 0
for _ in range(n):
    parts = input().split()
    try:
        name = parts[0]
        qty = int(parts[1])          # 없으면 IndexError, 숫자 아니면 ValueError
        if qty <= 0:
            raise ValueError("개수는 1 이상")   # 직접 예외 일으키기
        cost = prices[name] * qty     # 없는 상품이면 KeyError
    except IndexError:
        print("형식 오류")
    except ValueError:
        print("개수 오류")
    except KeyError:
        print("없는 상품:", name)
    else:
        total += cost                 # 예외가 없을 때만 더하기
        print(f"{name} {qty}개 = {cost}원")
print(f"합계: {total}원")''',
    ['3\n빵 2\n우유 셋\n콜라 1', '2\n젤리 5\n우유'], ['1\n빵 0', '3\n빵 1\n우유 1\n젤리 1', '2\n라면 -1\n젤리 -2'],
    ['예외 세 가지: parts[1] → IndexError, int() 와 raise → ValueError, prices[name] → KeyError.',
     '`if qty <= 0: raise ValueError(...)` 를 int 변환 바로 아래에 두면 같은 except ValueError 로 가요.',
     '정상일 때만 합계에 더하려면 `else:` 블록에 `total += cost` 와 출력을 넣어요.'],
    '`라면 -1` 은 KeyError 와 ValueError 가 둘 다 될 것 같지만, **먼저 실행되는 줄**에서 난 예외 하나만 잡혀요. 이 코드에선 qty 검사(raise)가 prices[name] 보다 먼저라 `개수 오류` 가 나와요. 줄 순서가 곧 예외 순서예요.')

L.essay('위 매점 코드에서 `라면 -1` 을 입력하면 `없는 상품` 이 아니라 `개수 오류` 가 출력돼요. 그 **이유**를 실행 순서와 연결해 서술하세요.',
    'try 블록은 위에서부터 한 줄씩 실행되고 예외가 처음 발생한 곳에서 바로 except 로 이동한다. qty 가 0 이하인지 검사해 raise ValueError 하는 줄이 prices[name] 으로 가격을 찾는 줄보다 먼저 있으므로, KeyError 가 나기 전에 ValueError 가 먼저 발생하여 except ValueError 의 "개수 오류" 가 출력된다.',
    ['위에서부터 차례로 실행', '처음 발생한 예외에서 바로 except 로 이동', 'raise ValueError 가 prices[name] 보다 먼저', 'KeyError 줄은 실행되지 않음'])

# =====================================================================
L = C.lesson('γ-04 파일 입출력 ①: with open · 모드 · 읽고 쓰기', 25,
'''- `with open("파일", "모드", encoding="utf-8") as f:` — 블록이 끝나면 **자동으로 닫혀요.**
- 모드: `"r"` 읽기(없으면 FileNotFoundError), `"w"` 쓰기(**기존 내용 삭제**), `"a"` 이어 쓰기.
- `f.write(문자열)` 은 줄바꿈을 자동으로 안 넣어요 → `"\\n"` 을 직접!
- 읽기: `read()` 전체 문자열, `readlines()` 줄 리스트(줄 끝에 `\\n` 포함), `for line in f`.
- 줄 끝 `\\n` 은 `strip()` 으로 떼요.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간: `else` 는 예외 없을 때, `finally` 는 항상. `raise` 로 예외를 직접 일으켰어요.\n'
       '오늘 배우는 파일은 **없는 파일 → FileNotFoundError** 처럼 예외와 자주 같이 나와요.'),
     REVEAL('try → except → else → finally 중 **항상** 실행되는 것은?', 'finally')])
L.ox('복습: `raise ValueError("x")` 는 ValueError 를 **잡는** 문장이다.', False,
     '`raise` 는 예외를 **일으키는** 문장이에요. 잡는 것은 `except`.', review=True)

L.explain('파일 열기: open 과 with',
    [T('프로그램이 끝나도 남는 데이터는 **파일**에 저장해요.\n'
       '`open()` 으로 열고, 다 쓰면 `close()` 로 닫아야 해요. 닫지 않으면 내용이 저장되지 않을 수도 있어요.'),
     CMP(side('open / close', '직접 닫아야 해요. 중간에 예외가 나면 close 를 못 할 수도!',
              'f = open("memo.txt", "w", encoding="utf-8")\nf.write("안녕\\n")\nf.close()', 'good'),
         side('with open (권장)', '블록이 끝나면 **자동으로** 닫혀요.',
              'with open("memo.txt", "w", encoding="utf-8") as f:\n    f.write("안녕\\n")', 'good'))],
    [T('`encoding="utf-8"` 은 **한글**을 깨지지 않게 저장·읽기 위한 약속이에요.\n'
       '쓸 때와 읽을 때 같은 인코딩을 써야 해요. 시험 코드에는 거의 항상 붙어 있어요.'),
     WARN('컴퓨터마다 기본 인코딩이 달라서(윈도우는 cp949 등) encoding 을 빼면 한글 파일이 **UnicodeDecodeError** 로 안 읽힐 수 있어요.')])

L.explain('세 가지 모드: r · w · a',
    [T('두 번째 인자 **모드**가 무엇을 할지 정해요.'),
     TABS(('"w" 쓰기', '파일을 **새로** 만들어요. 이미 있으면 **내용을 다 지우고** 처음부터 써요.',
           'with open("t.txt", "w", encoding="utf-8") as f:\n    f.write("첫 줄\\n")\nwith open("t.txt", "w", encoding="utf-8") as f:\n    f.write("덮어씀\\n")\nwith open("t.txt", "r", encoding="utf-8") as f:\n    print(f.read())'),
          ('"a" 이어 쓰기', '기존 내용 **뒤에** 붙여요. 파일이 없으면 새로 만들어요.',
           'with open("t.txt", "w", encoding="utf-8") as f:\n    f.write("첫 줄\\n")\nwith open("t.txt", "a", encoding="utf-8") as f:\n    f.write("추가\\n")\nwith open("t.txt", "r", encoding="utf-8") as f:\n    print(f.read())'),
          ('"r" 읽기', '기본값이에요(생략 가능). 파일이 **없으면 FileNotFoundError**.',
           'with open("t.txt", "w", encoding="utf-8") as f:\n    f.write("읽을 내용\\n")\nwith open("t.txt", encoding="utf-8") as f:\n    print(f.read())')),
     KEY('`write()` 는 **문자열만** 받고, **줄바꿈을 자동으로 넣지 않아요.** 숫자는 `str()` 로 바꾸고 `"\\n"` 을 붙여요.')])

L.output('출력은?', '''\
with open("log.txt", "w", encoding="utf-8") as f:
    f.write("A")
    f.write("B\\n")
with open("log.txt", "a", encoding="utf-8") as f:
    f.write("C\\n")
with open("log.txt", "w", encoding="utf-8") as f:
    f.write("D")
    f.write("E\\n")
with open("log.txt", encoding="utf-8") as f:
    print(f.read())''',
    '마지막 `"w"` 가 앞의 내용(AB, C)을 **모두 지우고** DE 만 남겨요. A 와 B 사이에 줄바꿈이 없었던 것도 기억하세요.\n\n```\n{out}\n```')

L.match('모드와 설명을 이어 보세요.',
    [['"r"', '읽기 — 없으면 FileNotFoundError'], ['"w"', '쓰기 — 기존 내용 삭제'], ['"a"', '이어 쓰기 — 끝에 추가'],
     ['encoding="utf-8"', '한글이 깨지지 않게'], ['with', '블록이 끝나면 자동으로 닫음']],
    '세 모드의 차이는 서술형 단골이에요. 특히 "w 는 기존 내용을 지운다" 를 꼭 기억!')

L.explain('읽는 방법 세 가지',
    [T('읽기에는 세 가지 방법이 있어요. 줄 끝의 **`\\n` 이 남는다**는 점이 중요해요.'),
     TABS(('read()', '파일 전체를 **문자열 하나**로.',
           'with open("s.txt", "w", encoding="utf-8") as f:\n    f.write("사과\\n바나나\\n")\nwith open("s.txt", encoding="utf-8") as f:\n    text = f.read()\nprint(repr(text))'),
          ('readlines()', '**줄 리스트**로. 각 줄 끝에 `\\n` 이 붙어 있어요.',
           'with open("s.txt", "w", encoding="utf-8") as f:\n    f.write("사과\\n바나나\\n")\nwith open("s.txt", encoding="utf-8") as f:\n    lines = f.readlines()\nprint(lines)'),
          ('for line in f', '한 줄씩 꺼내요. 큰 파일에 좋아요.',
           'with open("s.txt", "w", encoding="utf-8") as f:\n    f.write("사과\\n바나나\\n")\nwith open("s.txt", encoding="utf-8") as f:\n    for line in f:\n        print(line.strip(), len(line))'))],
    [T('`line.strip()` 은 앞뒤 공백과 `\\n` 을 지워요.\n'
       '`print(line)` 을 그냥 하면 줄 끝 `\\n` + print 의 줄바꿈 때문에 **빈 줄이 하나씩 더** 생겨요.'),
     TIP('`[line.strip() for line in f]` — 컴프리헨션으로 깨끗한 줄 리스트를 한 번에 만들 수 있어요.')])

L.output('출력은?', '''\
with open("w.txt", "w", encoding="utf-8") as f:
    for word in ["cat", "dog", "owl"]:
        f.write(word + "\\n")
with open("w.txt", encoding="utf-8") as f:
    lines = f.readlines()
print(len(lines))
print(len(lines[0]), len(lines[0].strip()))
print([x.strip().upper() for x in lines])''',
    '`readlines()` 의 각 줄은 `"cat\\n"` 처럼 `\\n` 을 포함해 길이가 4. strip() 하면 3.\n\n```\n{out}\n```')

L.fill('점수 리스트를 한 줄에 하나씩 파일에 저장하는 코드를 완성하세요.', '''\
scores = [90, 85, 77]
with open("sc.txt", "___", encoding="utf-8") as f:
    for s in scores:
        f.write(___(s) + "\\n")
with open("sc.txt", encoding="utf-8") as f:
    print(sum(int(line) for line in f))''', [['w'], ['str']],
    '쓰기 모드 `"w"`, 그리고 write 는 문자열만 받으니 `str(s)`. 읽을 때 `int(line)` 은 줄 끝 `\\n` 을 알아서 무시해요. 합은 252.',
    expect='252')

L.spot('실행하면 **오류**가 나는 줄은?', '''\
nums = [3, 1, 4]
with open("n.txt", "w", encoding="utf-8") as f:
    for n in nums:
        f.write(n)
        f.write("\\n")''', 4,
    '`f.write(n)` 에 **정수**를 넣어서 TypeError 예요. `write()` 는 문자열만 받아요 → `f.write(str(n))`.',
    error_line=4)

L.ox('이미 내용이 있는 파일을 `"w"` 모드로 열고 아무것도 쓰지 않은 채 닫으면, 그 파일은 **빈 파일**이 된다.', True,
     '`"w"` 로 여는 **순간** 기존 내용이 지워져요. 그래서 기록을 계속 쌓을 때는 `"a"` 를 써야 해요.')

L.choice('`f.readlines()` 가 돌려주는 값으로 옳은 것은?',
    ['파일 전체가 담긴 문자열 하나', '각 줄이 문자열로 담긴 리스트 (줄 끝 \\n 포함)', '각 줄이 문자열로 담긴 리스트 (줄 끝 \\n 없음)', '첫 줄 하나만 담긴 문자열'], 2,
    '`readlines()` 는 **줄 리스트**이고 각 줄 끝에 `\\n` 이 남아 있어요(마지막 줄은 없을 수도 있어요). 전체 문자열은 `read()`, 한 줄은 `readline()`.')

L.short('출력값을 쓰세요: `print(len("apple\\n"))`', '6',
    '`\\n` 도 **한 글자**예요. 그래서 파일에서 읽은 줄의 길이는 눈에 보이는 것보다 1 커요. `strip()` 하면 5.',
    check_code='print(len("apple\\n"))')

L.practice('[기출유사] 나만의 단어장 파일',
'''첫 줄에 단어 수 N, 다음 N 줄에 `영어 뜻` 이 주어지고, 마지막 줄에 찾을 영어 단어가 주어져요.

**[조건]**
- 먼저 N 개의 단어를 `words.txt` 에 **`영어:뜻` 형식으로 한 줄에 하나씩** 저장해요(`"w"`, `encoding="utf-8"`).
- 그다음 `words.txt` 를 **다시 열어 읽고**, 줄마다 `strip()` 과 `split(":")` 으로 딕셔너리를 만들어요.
- 첫째 줄: `단어 수: N`
- 둘째 줄: 찾는 단어가 있으면 `영어 = 뜻`, 없으면 `영어 은(는) 단어장에 없어요`

{ex}

{ex2}''',
'''n = int(input())
# 1) 파일에 저장

# 2) 파일에서 읽어 딕셔너리 만들기
book = {}

target = input()
# 3) 출력
''',
'''n = int(input())
with open("words.txt", "w", encoding="utf-8") as f:     # 1) 저장
    for _ in range(n):
        eng, kor = input().split()
        f.write(eng + ":" + kor + "\\n")

book = {}
with open("words.txt", "r", encoding="utf-8") as f:     # 2) 다시 읽기
    for line in f:
        eng, kor = line.strip().split(":")   # 줄 끝 \\n 제거 후 나누기
        book[eng] = kor

target = input()
print("단어 수:", len(book))
if target in book:
    print(target, "=", book[target])
else:
    print(target, "은(는) 단어장에 없어요")''',
    ['3\napple 사과\ntiger 호랑이\nmoon 달\ntiger', '2\nsun 해\nstar 별\nsky'], ['1\na 가\na', '4\nred 빨강\nblue 파랑\ngreen 초록\nblack 검정\nblack', '2\nx 엑스\ny 와이\nX'],
    ['저장할 때 `f.write(eng + ":" + kor + "\\n")` — 줄바꿈을 직접 붙여요.',
     '읽을 때 `for line in f:` → `line.strip().split(":")` 로 두 조각.',
     '`if target in book:` 으로 먼저 확인하면 KeyError 없이 안전해요.'],
    '파일에 쓰고 다시 읽는 것이 핵심이에요. 읽은 줄에는 `\\n` 이 붙어 있어 `strip()` 을 안 하면 뜻이 `"달\\n"` 이 돼요. 대소문자는 다르게 취급하므로 `X` 는 없는 단어예요.')

L.essay('`"w"` 모드와 `"a"` 모드의 차이를 **이미 내용이 있는 파일**을 기준으로 서술하고, 매일 공부 기록을 쌓아 두는 프로그램에는 어떤 모드가 알맞은지 이유와 함께 쓰세요.',
    '"w" 모드는 파일을 열 때 기존 내용을 모두 지우고 처음부터 쓰고, "a" 모드는 기존 내용을 유지한 채 파일 끝에 이어서 쓴다. 매일 기록을 쌓아야 하므로 이전 기록이 지워지지 않는 "a" 모드가 알맞다.',
    ['w 는 기존 내용을 지우고 새로 씀', 'a 는 기존 내용 뒤에 이어 씀', '기록 누적에는 a 모드', '이전 기록이 지워지지 않기 때문'])

# =====================================================================
L = C.lesson('γ-05 파일 입출력 ②: CSV · 단어 빈도 · 파일 합치기', 30,
'''- **CSV** = 쉼표로 구분한 표. 한 줄 = 한 행, `line.strip().split(",")` 로 칸을 나눠요.
- 첫 줄이 **머리글(header)** 이면 `lines[1:]` 또는 `next(f)` 로 건너뛰어요.
- 쓸 때는 `",".join(map(str, 행)) + "\\n"`.
- 단어 빈도 = 파일 읽기 + `d[w] = d.get(w, 0) + 1`.
- 없는 파일을 `"r"` 로 열면 **FileNotFoundError** → try/except 로 처리.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간: `with open(파일, 모드, encoding="utf-8") as f:` 와 r/w/a 모드, 읽은 줄에는 `\\n` 이 붙어 있다는 것을 배웠어요.'),
     REVEAL_RUN('`"kim\\n".strip()` 의 길이는?', 'print(len("kim\\n".strip()))')])
L.choice('복습: 기존 기록 **뒤에 이어서** 쓰려면 어떤 모드?', ['"r"', '"w"', '"a"', '"x"'], 3,
    '`"a"`(append) 는 끝에 이어 써요. `"w"` 는 기존 내용을 지워요.', review=True)

L.explain('CSV 파일 읽기',
    [T('**CSV**(Comma-Separated Values)는 엑셀 표를 글자로 저장한 거예요.\n'
       '한 줄이 한 행이고, 칸은 **쉼표**로 나눠요. 보통 첫 줄은 열 이름(머리글)이에요.'),
     CODE('''\
with open("club.csv", "w", encoding="utf-8") as f:
    f.write("이름,학년,점수\\n")
    f.write("민준,1,88\\n")
    f.write("서연,2,95\\n")

with open("club.csv", encoding="utf-8") as f:
    lines = f.readlines()
print(lines[0].strip())          # 머리글
for line in lines[1:]:           # 머리글 건너뛰기
    name, grade, score = line.strip().split(",")
    print(name, int(score) + 5)''', 'CSV 쓰고 읽기')],
    [T('나눈 칸은 모두 **문자열**이에요. 계산하려면 `int()`·`float()` 로 바꿔야 해요.'),
     WARN('`strip()` 을 빼면 마지막 칸이 `"88\\n"` 처럼 줄바꿈을 품고 있어요. `int("88\\n")` 은 괜찮지만 **문자열 비교**(`== "88"`)는 False 가 돼요!'),
     TIP('파이썬에는 `csv` 모듈도 있지만, 시험에서는 `split(",")` 만으로 충분해요.')])

L.output('출력은?', '''\
with open("t.csv", "w", encoding="utf-8") as f:
    f.write("item,price,qty\\npen,500,4\\nbag,12000,1\\n")
total = 0
with open("t.csv", encoding="utf-8") as f:
    next(f)                      # 첫 줄 건너뛰기
    for line in f:
        item, price, qty = line.strip().split(",")
        total += int(price) * int(qty)
print(total)''',
    '`next(f)` 는 첫 줄(머리글)을 하나 읽어 버려요. 500×4 + 12000×1 = {out}')

L.explain('CSV 파일 쓰기',
    [T('리스트를 CSV 한 줄로 만들려면 **join** 을 써요. 숫자가 섞여 있으면 `map(str, …)` 로 먼저 글자로!'),
     CODE('''\
rows = [["kim", 90, 85], ["lee", 70, 100]]
with open("out.csv", "w", encoding="utf-8") as f:
    f.write("name,kor,math\\n")
    for r in rows:
        f.write(",".join(map(str, r)) + "\\n")
with open("out.csv", encoding="utf-8") as f:
    print(f.read())''', 'join 으로 한 줄 만들기'),
     KEY('읽기는 `split(",")`, 쓰기는 `",".join(...)` — 서로 **반대** 작업이에요.')])

L.fill('각 학생의 합계를 CSV 마지막 칸에 붙여 저장하세요.', '''\
data = [["A", 3, 4], ["B", 5, 6]]
with open("s.csv", "w", encoding="utf-8") as f:
    for name, x, y in data:
        row = [name, x, y, x + y]
        f.write(___.join(map(___, row)) + "\\n")
with open("s.csv", encoding="utf-8") as f:
    print(f.read().strip())''', [['","', "','"], ['str']],
    '구분자 `","` 로 join, 숫자는 `map(str, row)` 로 글자로 바꿔요.', expect='A,3,4,7\nB,5,6,11')

L.explain('파일 속 단어 빈도 세기',
    [T('2024년 14점 문항 소재예요. 순서는 **읽기 → 단어로 나누기 → 딕셔너리 누적**.\n'
       '대소문자를 같게 세려면 `lower()`, 문장부호는 `replace` 나 `strip(".,!?")` 로 지워요.'),
     CODE('''\
with open("poem.txt", "w", encoding="utf-8") as f:
    f.write("The sun. The moon!\\nthe STAR, the sun\\n")

freq = {}
with open("poem.txt", encoding="utf-8") as f:
    for line in f:
        for w in line.split():
            w = w.strip(".,!?").lower()
            freq[w] = freq.get(w, 0) + 1
print(freq)
best = max(freq, key=freq.get)
print(best, freq[best])''', '단어 빈도')],
    [T('결과를 다른 파일에 저장할 때는 `f.write(f"{단어},{횟수}\\n")` 처럼 한 줄씩 써요.\n'
       '많이 나온 순서로 정렬하려면 `sorted(freq.items(), key=lambda x: x[1], reverse=True)`.'),
     THINK('`strip(".,!?")` 는 **양 끝**의 그 글자들만 지워요. 단어 가운데 있는 쉼표는 남아요.')])

L.output('출력은?', '''\
with open("v.txt", "w", encoding="utf-8") as f:
    f.write("go stop go\\nGO wait\\n")
freq = {}
with open("v.txt", encoding="utf-8") as f:
    for w in f.read().split():
        w = w.lower()
        freq[w] = freq.get(w, 0) + 1
for k, v in sorted(freq.items(), key=lambda x: x[1], reverse=True):
    print(k, v)''',
    '`read().split()` 은 줄바꿈도 공백으로 보고 모든 단어를 나눠요. go 3번, stop·wait 1번. 횟수가 같으면 원래(처음 나온) 순서를 유지해요.\n\n```\n{out}\n```')

L.explain('파일 합치기와 FileNotFoundError',
    [T('2024년 12점 문항: **여러 파일을 하나로 합치기**. 파일 목록을 돌며 읽어서 결과 파일에 써요.\n'
       '그런데 목록 중 **없는 파일**이 있으면? `"r"` 모드로 여는 순간 FileNotFoundError!'),
     CODE('''\
with open("a.txt", "w", encoding="utf-8") as f:
    f.write("1반 명단\\n")
with open("b.txt", "w", encoding="utf-8") as f:
    f.write("2반 명단\\n")

with open("all.txt", "w", encoding="utf-8") as out:
    for name in ["a.txt", "nope.txt", "b.txt"]:
        try:
            with open(name, encoding="utf-8") as f:
                out.write(f.read())
        except FileNotFoundError:
            print(name, "파일이 없어 건너뜀")

with open("all.txt", encoding="utf-8") as f:
    print(f.read())''', '파일 합치기 + 예외 처리')],
    [T('결과 파일 `out` 은 **바깥 with** 로 한 번만 열고, 원본 파일들은 안쪽에서 하나씩 열어요.\n'
       '결과 파일을 반복문 안에서 `"w"` 로 열면 매번 지워져서 **마지막 파일만** 남아요!'),
     WARN('`"w"`·`"a"` 모드는 파일이 없으면 **새로 만들어요.** FileNotFoundError 는 `"r"` 모드에서만 나요.')])

L.spot('`notes.txt` 라는 파일은 **존재하지 않아요.** 실행하면 **예외가 나는 줄**은?', '''\
with open("log.txt", "a", encoding="utf-8") as f:
    f.write("시작\\n")
with open("log.txt", encoding="utf-8") as f:
    print(f.read())
with open("notes.txt", encoding="utf-8") as f:
    print(f.read())''', 5,
    '1번 줄은 `"a"` 모드라 없으면 새로 만들어요. 5번 줄은 읽기 모드로 **없는 파일**을 열어 FileNotFoundError.',
    error_line=5)

L.bucket('파일이 **없는 상태**에서 실행했을 때 결과로 분류하세요.', ['새 파일이 만들어짐', 'FileNotFoundError'],
    [['open("x.txt", "w")', 1], ['open("x.txt", "a")', 1], ['open("x.txt", "r")', 2], ['open("x.txt")', 2]],
    '모드를 생략하면 `"r"` 이에요. 쓰기 계열(w, a)은 없으면 만들어요.')

L.order('여러 파일을 합치는 코드를 순서대로 놓으세요.',
    ['with open("total.txt", "w", encoding="utf-8") as out:', '    for name in files:',
     '        with open(name, encoding="utf-8") as f:', '            out.write(f.read())'],
    '결과 파일을 **먼저 한 번** 열고, 그 안에서 원본 파일을 하나씩 열어 읽은 내용을 써요.')

L.practice('[기출유사] 동아리 성적 CSV 리포트',
'''첫 줄에 학생 수 N, 다음 N 줄에 `이름,국어,수학` 이 CSV 형식으로 주어져요.

**[조건]**
- 먼저 `scores.csv` 에 머리글 `name,kor,math` 와 N 줄을 그대로 저장해요.
- `scores.csv` 를 **다시 열어** 머리글을 건너뛰고 읽어요.
- 학생마다 `이름: 평균` (평균은 `round(…, 1)`) 을 출력해요.
- 마지막 줄: `1등: 이름` (평균이 같으면 먼저 나온 학생)

{ex}

{ex2}''',
'''n = int(input())
with open("scores.csv", "w", encoding="utf-8") as f:
    f.write("name,kor,math\\n")
    # N 줄 저장

# 다시 읽어서 처리하세요
''',
'''n = int(input())
with open("scores.csv", "w", encoding="utf-8") as f:
    f.write("name,kor,math\\n")
    for _ in range(n):
        f.write(input().strip() + "\\n")      # 입력 줄을 그대로 저장

best_name, best_avg = "", -1
with open("scores.csv", encoding="utf-8") as f:
    lines = f.readlines()
for line in lines[1:]:                           # 머리글 건너뛰기
    name, kor, math = line.strip().split(",")
    avg = round((int(kor) + int(math)) / 2, 1)
    print(f"{name}: {avg}")
    if avg > best_avg:                           # 더 클 때만 바꿔서 동점이면 먼저 나온 학생 유지
        best_name, best_avg = name, avg
print("1등:", best_name)''',
    ['3\n민준,80,95\n서연,90,90\n하준,70,60', '2\n A,100,99\nB,99,100'], ['1\nsolo,0,0', '3\nx,1,2\ny,2,1\nz,0,3', '2\nkim,55,56\nlee,56,56'],
    ['저장은 `f.write(input().strip() + "\\n")` 을 N 번.',
     '읽을 때 `lines[1:]` 로 머리글을 빼고 `line.strip().split(",")` 로 세 칸.',
     '1등은 `if avg > best_avg:` 일 때만 바꾸면 동점일 때 먼저 나온 학생이 남아요.'],
    '쓴 파일을 다시 읽는 흐름이 핵심이에요. 평균 비교에 `>` 대신 `>=` 를 쓰면 동점일 때 **나중** 학생으로 바뀌니 조심!')

L.practice('[기출유사] 일기장 단어 빈도',
'''첫 줄에 줄 수 N, 다음 N 줄에 영어 문장이 주어져요.

**[조건]**
- N 줄을 `diary.txt` 에 저장한 뒤, **다시 읽어서** 단어 빈도를 세요.
- 대소문자는 구분하지 않고(`lower()`), 단어 양 끝의 `.,!?` 는 지워요(`strip(".,!?")`).
- 첫째 줄: `단어 종류: 개수`
- 다음 줄부터: 많이 나온 순서로 **최대 3개** `단어 횟수` (횟수가 같으면 처음 나온 순서)

{ex}

{ex2}''',
'''n = int(input())
# 1) diary.txt 에 저장

# 2) 다시 읽어 빈도 세기
freq = {}

# 3) 출력
''',
'''n = int(input())
with open("diary.txt", "w", encoding="utf-8") as f:
    for _ in range(n):
        f.write(input() + "\\n")

freq = {}
with open("diary.txt", encoding="utf-8") as f:
    for line in f:
        for w in line.split():
            w = w.strip(".,!?").lower()   # 문장부호 제거 + 소문자
            if w:                          # 부호만 있던 경우 빈 문자열은 제외
                freq[w] = freq.get(w, 0) + 1

print("단어 종류:", len(freq))
ranked = sorted(freq.items(), key=lambda x: x[1], reverse=True)   # 안정 정렬: 동점은 처음 순서
for w, c in ranked[:3]:
    print(w, c)''',
    ['2\nI like cats. Cats like me!\nI really like CATS', '1\nHello, hello? HELLO world.'], ['1\nsolo', '3\na b c\nd e f\ng h i', '2\nWow ! wow\nok ok OK.'],
    ['저장 → 다시 열기 → `for line in f:` → `for w in line.split():`',
     '`w = w.strip(".,!?").lower()` 후 `freq[w] = freq.get(w, 0) + 1`',
     '`sorted(freq.items(), key=lambda x: x[1], reverse=True)[:3]` — 파이썬 정렬은 같은 값의 순서를 유지해요.'],
    '`"!"` 처럼 부호만 있는 토큰은 strip 하면 빈 문자열이 되니 `if w:` 로 걸러요. 정렬은 **안정 정렬**이라 횟수가 같으면 딕셔너리에 들어간(처음 나온) 순서가 유지돼요.')

L.essay('여러 파일을 합치는 프로그램에서 목록에 없는 파일 이름이 섞여 있으면 어떤 예외가 왜 발생하는지 쓰고, **나머지 파일은 계속 합쳐지도록** 고치는 방법을 서술하세요.',
    '읽기("r") 모드로 존재하지 않는 파일을 열면 파일을 찾을 수 없으므로 FileNotFoundError 가 발생해 프로그램이 멈춘다. 파일을 여는 부분을 반복문 안에서 try 로 감싸고 except FileNotFoundError 에서 안내 메시지만 출력하면, 그 파일만 건너뛰고 다음 파일을 계속 합칠 수 있다.',
    ['FileNotFoundError', '읽기 모드로 없는 파일을 열었기 때문', '반복문 안에서 try/except', '그 파일만 건너뛰고 계속 진행'])

# =====================================================================
L = C.lesson('γ-06 모듈: import · from · as · __name__', 25,
'''- **모듈** = 함수·변수를 모아 둔 `.py` 파일. 다시 쓰기·나눠 관리하기가 장점.
- `import math` → `math.sqrt()` / `from math import sqrt` → `sqrt()` / `import math as m` → `m.sqrt()`
- 모듈을 import 하면 그 파일의 코드가 **한 번 실행**돼요.
- `__name__` 은 직접 실행하면 `"__main__"`, import 되면 **모듈 이름**.
- `if __name__ == "__main__":` 아래 코드는 **직접 실행할 때만** 돌아요(테스트 코드 보호).''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간: CSV 는 `split(",")`/`",".join`, 단어 빈도는 `get` 누적, 없는 파일은 FileNotFoundError.'),
     REVEAL_RUN('`",".join(map(str, [1, 2, 3]))` 의 결과는?', 'print(",".join(map(str, [1, 2, 3])))')])
L.output('복습: 출력은?', 'line = "kim,90,85\\n"\nname, a, b = line.strip().split(",")\nprint(name, int(a) + int(b))',
    '`strip()` 으로 `\\n` 을 떼고 나눠요 → {out}', review=True)

L.explain('모듈이란? import 세 가지 형태',
    [T('**모듈**은 함수·변수·클래스를 모아 둔 `.py` 파일이에요. `math`, `random` 처럼 파이썬에 들어 있는 것도 있고, 직접 만들 수도 있어요.\n'
       '장점: ① 한 번 만든 코드를 **여러 프로그램에서 재사용** ② 긴 프로그램을 **기능별로 나눠** 관리 ③ 이름 충돌을 줄임.'),
     TABS(('import 모듈', '모듈 이름을 앞에 붙여 써요.', 'import math\nprint(math.sqrt(16), math.pi)'),
          ('from 모듈 import 이름', '이름을 바로 써요. 모듈 이름은 못 써요.', 'from math import sqrt, ceil\nprint(sqrt(16), ceil(2.1))'),
          ('import 모듈 as 별명', '긴 이름을 짧게. numpy 를 `np` 로 쓰는 게 대표적이에요.', 'import math as m\nprint(m.floor(3.9))'),
          ('from 모듈 import 이름 as 별명', '함수에도 별명을 줄 수 있어요.', 'from math import factorial as f\nprint(f(5))'))],
    [T('`from math import *` 는 모든 이름을 가져오지만, **어디서 온 이름인지 알기 어렵고** 내 변수와 이름이 겹칠 수 있어 잘 안 써요.'),
     WARN('`from math import sqrt` 만 했다면 `math.pi` 는 **NameError** 예요. `math` 라는 이름 자체는 가져오지 않았거든요.')])

L.match('import 형태와 올바른 호출을 이어 보세요.',
    [['import math', 'math.sqrt(9)'], ['from math import sqrt', 'sqrt(9)'], ['import math as m', 'm.sqrt(9)'],
     ['from math import sqrt as root', 'root(9)']],
    'import 한 **이름**이 무엇인지 보면 돼요. `import math` 는 math, `from … import sqrt` 는 sqrt, `as` 는 별명.')

L.spot('실행하면 **오류**가 나는 줄은?', '''\
from math import sqrt
from random import randint
print(sqrt(25))
r = randint(1, 6)
print(math.pi * r)''', 5,
    '`math` 라는 이름을 import 하지 않았어요(sqrt 만 가져옴). → **NameError: name \'math\' is not defined**. `from math import sqrt, pi` 후 `pi * r` 로 고쳐요.',
    error_line=5)

L.explain('자주 쓰는 내장 모듈: math · random',
    [T('`math` 는 수학 함수 모음이에요.'),
     CODE('import math\nprint(math.ceil(7 / 3))    # 올림\nprint(math.floor(-1.5))    # 내림\nprint(math.gcd(12, 18))    # 최대공약수\nprint(math.factorial(4))\nprint(round(math.sqrt(2), 3))', 'math 모듈')],
    [T('`random` 은 무작위 값을 만들어요. 비밀번호 생성·단어 맞추기 게임 단골이에요.'),
     TABS(('randint', '양 끝을 **포함**한 정수 하나.', 'import random\nprint(random.randint(1, 6))'),
          ('choice', '리스트에서 **하나** 고르기.', 'import random\nprint(random.choice(["가위", "바위", "보"]))'),
          ('sample', '**중복 없이** k 개 뽑아 리스트로.', 'import random\nprint(random.sample(range(1, 46), 6))'),
          ('shuffle', '리스트 **원본**을 섞어요(None 반환).', 'import random\na = [1, 2, 3, 4]\nrandom.shuffle(a)\nprint(a)')),
     KEY('`randint(1, 6)` 은 6 도 나와요. `range(1, 6)` 은 6 이 안 나오는 것과 헷갈리지 마세요!')])

L.choice('리스트 `pool` 에서 **서로 다른** 글자 4개를 뽑는 데 가장 알맞은 것은?',
    ['random.choice(pool) 을 4번', 'random.sample(pool, 4)', 'random.randint(pool, 4)', 'random.shuffle(pool, 4)'], 2,
    '`sample` 은 **중복 없이** 뽑아요. choice 를 여러 번 하면 같은 글자가 또 나올 수 있어요. 중복을 막으려면 set 에 `add` 하며 개수를 확인하는 방법도 있어요.')

L.explain('내 모듈 만들기',
    [T('`calc.py` 라는 파일에 함수를 써 두면, 같은 폴더의 다른 파일에서 `import calc` 로 가져다 쓸 수 있어요.\n'
       '아래 예시는 **파일 두 개**예요. (사이트에서는 파일 하나만 실행되니 읽기만 해 봐요)'),
     CODE('def add(a, b):\n    return a + b\n\nRATE = 1350', 'calc.py (모듈 파일)'),
     T('**main.py** (calc.py 와 같은 폴더)\n```python\nimport calc\nfrom calc import RATE\n\nprint(calc.add(3, 4))\nprint(10 * RATE)\n```'),
     REVEAL_RUN('main.py 를 실행하면?', 'import sys; sys.path.insert(0, ".")\nimport calc\nfrom calc import RATE\n\nprint(calc.add(3, 4))\nprint(10 * RATE)',
                '`import calc` 로는 `calc.add`, `from calc import RATE` 로는 `RATE` 를 바로 써요.',
                files={'calc.py': 'def add(a, b):\n    return a + b\n\nRATE = 1350\n'})],
    [T('**import 하는 순간 모듈 파일의 코드가 위에서부터 한 번 실행돼요.**\n'
       '그래서 모듈 파일에 `print(...)` 같은 테스트 코드가 있으면, import 만 했는데도 출력이 나와 버려요.'),
     THINK('2025년에 `main.py` 가 `str_utils`, `math_utils` 두 모듈을 import 해서 쓰는 문제가 나왔어요. 어떤 함수가 어느 파일에 있는지 따라가는 게 핵심이에요.')])

L.output('`greet.py` 와 `main.py` 가 같은 폴더에 있어요. `main.py` 를 실행하면 출력은?\n\n**greet.py**\n```python\nprint("greet 불러옴")\nprint(__name__)\n\ndef hello(name):\n    return "안녕, " + name\n```',
    '# main.py\nimport greet\nprint(__name__)\nprint(greet.hello("민지"))',
    'import 하는 순간 greet.py 가 실행되어 두 줄이 먼저 나와요. 이때 greet.py 안의 `__name__` 은 **모듈 이름 "greet"**, 직접 실행한 main.py 의 `__name__` 은 **"__main__"** 이에요.\n\n```\n{out}\n```',
    run_code='import sys; sys.path.insert(0, ".")\nimport greet\nprint(__name__)\nprint(greet.hello("민지"))',
    files={'greet.py': 'print("greet 불러옴")\nprint(__name__)\n\ndef hello(name):\n    return "안녕, " + name\n'})

L.explain('if __name__ == "__main__": 의 이유',
    [T('파이썬은 파일마다 `__name__` 이라는 변수를 자동으로 만들어요.\n'
       '- 그 파일을 **직접 실행**하면 `__name__ == "__main__"`\n'
       '- 다른 파일에서 **import** 되면 `__name__ == "모듈 이름"`'),
     CMP(side('직접 실행: python calc.py', '`__name__` 이 "__main__" → if 아래 테스트 코드 **실행됨**',
              'def add(a, b):\n    return a + b\n\nif __name__ == "__main__":\n    print("테스트:", add(2, 3))', 'good'),
         side('import calc 로 불러올 때', '`__name__` 이 "calc" → if 아래 코드 **실행 안 됨**. add 함수만 쓸 수 있어요.', '', 'good'))],
    [T('그래서 모듈 파일에 **테스트 코드**를 넣어 둘 때 이 if 로 감싸요.\n'
       '직접 실행할 땐 테스트가 돌고, 다른 프로그램이 import 할 땐 함수만 깔끔하게 가져가요.'),
     EXAM('2023년 서술형: "`if __name__ == "__main__":` 을 쓰는 이유" — **"import 될 때는 실행되지 않게 하려고"** 가 핵심 문장이에요.')])

L.ox('`if __name__ == "__main__":` 아래의 코드는 그 파일이 다른 파일에서 `import` 될 때도 실행된다.', False,
     'import 되면 `__name__` 은 모듈 이름("calc" 등)이라 조건이 거짓이에요. **직접 실행할 때만** 실행돼요.')

L.fill('`math` 모듈을 `m` 이라는 별명으로 불러와 원의 넓이를 구하세요.', '''\
import math ___ m
r = 3
print(round(___.pi * r ** 2, 2))''', [['as'], ['m']],
    '`import math as m` 이후에는 `m.pi` 로 써요. `math.pi` 라고 쓰면 NameError! 결과는 28.27.', expect='28.27')

L.practice('[기출유사] 비밀번호 검사 모듈',
'''비밀번호 검사 함수를 모듈처럼 만들고, **직접 실행할 때만** 입력을 받아 검사하는 프로그램을 작성하세요.

**[조건]**
- 함수 `check(pw)` 는 통과한 규칙 수(0~4)와 부족한 항목 리스트를 돌려줘요.
- 규칙: ① 길이 8 이상 ② 대문자 포함 ③ 숫자 포함 ④ 특수문자(`!@#$%^&*` 중 하나) 포함 — 부족한 항목 이름은 각각 `길이`, `대문자`, `숫자`, `특수문자`
- 입력·출력 코드는 `if __name__ == "__main__":` 아래에 써요.
- 첫째 줄: 4개 통과 `강함`, 2~3개 `보통`, 0~1개 `약함`
- 둘째 줄: `부족: 항목1, 항목2` (모두 통과하면 `부족: 없음`)

{ex}

{ex2}''',
'''def check(pw):
    passed = 0
    missing = []
    # 네 가지 규칙을 검사하세요
    return passed, missing

if __name__ == "__main__":
    pw = input()
    # 결과를 출력하세요
''',
'''SPECIAL = set("!@#$%^&*")

def check(pw):
    passed = 0
    missing = []
    rules = [("길이", len(pw) >= 8),
             ("대문자", any(c.isupper() for c in pw)),
             ("숫자", any(c.isdigit() for c in pw)),
             ("특수문자", len(set(pw) & SPECIAL) > 0)]   # 교집합이 있으면 포함
    for name, ok in rules:
        if ok:
            passed += 1
        else:
            missing.append(name)
    return passed, missing

if __name__ == "__main__":          # 직접 실행할 때만 입력·출력
    pw = input()
    passed, missing = check(pw)
    if passed == 4:
        print("강함")
    elif passed >= 2:
        print("보통")
    else:
        print("약함")
    print("부족:", ", ".join(missing) if missing else "없음")''',
    ['Nest2026!', 'hello'], ['ABCDEFGH', 'a1!', 'P@ss1234'],
    ['규칙마다 `if` 로 검사해 통과하면 `passed += 1`, 아니면 `missing.append("이름")`.',
     '대문자 포함: `any(c.isupper() for c in pw)`, 특수문자: `set(pw) & set("!@#$%^&*")`',
     '출력: `print("부족:", ", ".join(missing) if missing else "없음")`'],
    '사이트는 이 파일을 **직접 실행**하므로 `__name__` 이 `"__main__"` 이라 입력·출력이 돌아가요. 다른 파일이 `import` 하면 check 함수만 가져가고 input 은 실행되지 않아요.')

L.practice('[기출유사] math 모듈로 택배 계산',
'''첫 줄에 출발지와 도착지 좌표 `x1 y1 x2 y2`, 둘째 줄에 `물건 수 상자 용량` 이 주어져요.

**[조건]**
- `from math import sqrt, ceil` 로 불러와 쓰세요.
- 첫째 줄: `거리: 값` — 두 점 사이 거리 `sqrt((x2-x1)² + (y2-y1)²)` 를 `round(…, 2)`
- 둘째 줄: `상자: 개수` — 물건을 모두 담는 데 필요한 상자 수(올림 `ceil`)
- 셋째 줄: `배송비: 금액원` — 상자 하나에 3000원 + 거리 1 당 100원(거리는 **올림**한 정수로 계산)

{ex}

{ex2}''',
'''from math import sqrt, ceil
x1, y1, x2, y2 = map(int, input().split())
items, cap = map(int, input().split())
# 이어서 작성하세요
''',
'''from math import sqrt, ceil
x1, y1, x2, y2 = map(int, input().split())
items, cap = map(int, input().split())
dist = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)   # 두 점 사이 거리
boxes = ceil(items / cap)                      # 남는 물건이 있으면 상자 하나 더
print("거리:", round(dist, 2))
print("상자:", boxes)
print(f"배송비: {boxes * 3000 + ceil(dist) * 100}원")''',
    ['0 0 3 4\n10 3', '1 2 4 6\n5 5'], ['0 0 0 0\n1 1', '-1 -1 2 3\n7 2', '0 0 1 1\n100 7'],
    ['`from math import sqrt, ceil` 이후에는 `math.` 없이 `sqrt()`, `ceil()` 로 써요.',
     '상자 수는 `ceil(items / cap)` — 10 / 3 = 3.33… → 4',
     '배송비는 `boxes * 3000 + ceil(dist) * 100`'],
    '`ceil` 은 올림, `floor` 는 내림, `round` 는 반올림이에요. 거리 √2 ≈ 1.41 은 올림하면 2 가 돼요.')

L.essay('모듈 파일 끝에 `if __name__ == "__main__":` 을 두고 그 아래에 테스트 코드를 쓰는 **이유**를 `__name__` 값과 연결해 서술하세요.',
    '파일을 직접 실행하면 __name__ 의 값이 "__main__" 이 되어 테스트 코드가 실행되지만, 다른 파일에서 import 하면 __name__ 이 모듈 이름이 되어 조건이 거짓이므로 테스트 코드가 실행되지 않는다. 이렇게 하면 모듈을 가져다 쓰는 쪽에서는 불필요한 출력이나 입력 없이 함수만 사용할 수 있다.',
    ['직접 실행하면 __name__ 은 "__main__"', 'import 되면 __name__ 은 모듈 이름', 'import 될 때 테스트 코드가 실행되지 않게', '함수만 깔끔하게 재사용'])

# =====================================================================
L = C.lesson('γ-07 클래스 기초: __init__ · self · 메서드 · __str__', 30,
'''- **클래스** = 설계도, **객체(인스턴스)** = 설계도로 만든 실물. `acc = Account("kim", 1000)`
- `__init__(self, …)` 은 객체가 만들어질 때 **자동 호출**되는 생성자. `self.속성 = 값` 으로 저장.
- 메서드의 첫 매개변수는 항상 `self`(그 객체 자신). 호출할 땐 self 를 안 넘겨요.
- `__str__` 은 `print(객체)`·`str(객체)` 할 때 보일 **문자열을 return** 해요.
- 객체는 **상태(속성)** 를 기억해서 메서드를 부를 때마다 바뀔 수 있어요.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간: `import`/`from`/`as` 의 차이와 `__name__ == "__main__"` 의 이유를 배웠어요.'),
     REVEAL('`from math import sqrt` 후 `math.sqrt(4)` 를 쓰면?', 'NameError — math 라는 이름은 가져오지 않았어요.')])
L.short('복습: 파일을 **직접 실행**했을 때 `__name__` 의 값은? (따옴표 없이)', '__main__',
    '직접 실행하면 `"__main__"`, import 되면 모듈 이름이에요.', review=True, check_code='print(__name__)')

L.explain('클래스와 객체',
    [T('지금까지는 학생 이름·점수를 **변수 여러 개**나 딕셔너리로 따로 들고 다녔어요.\n'
       '**클래스**는 관련된 데이터(속성)와 기능(메서드)을 **한 덩어리**로 묶는 설계도예요. 이 설계도로 찍어 낸 실물이 **객체**예요.'),
     CODE('''\
class Dog:
    def __init__(self, name, age):
        self.name = name      # 속성 저장
        self.age = age

    def bark(self):           # 메서드
        print(self.name + ": 멍멍!")

a = Dog("초코", 3)
b = Dog("보리", 5)
a.bark()
b.bark()
print(a.age + b.age)''', '첫 클래스')],
    [T('`a = Dog("초코", 3)` 을 실행하면 이런 일이 일어나요.'),
     STEPS(('1. 빈 객체 생성', 'Dog 설계도로 새 객체를 하나 만들어요.'),
           ('2. __init__ 자동 호출', '`__init__(새객체, "초코", 3)` — 새 객체가 **self** 로 들어가요.'),
           ('3. 속성 저장', '`self.name = "초코"`, `self.age = 3` 이 그 객체에 붙어요.'),
           ('4. 변수에 연결', '완성된 객체를 a 가 가리켜요. `a.name` 으로 꺼낼 수 있어요.')),
     KEY('`self` 는 "**지금 이 메서드를 부른 그 객체**" 예요. `a.bark()` 는 사실 `Dog.bark(a)` 와 같아요.')])

L.output('출력은?', '''\
class Rectangle:
    def __init__(self, w, h):
        self.w = w
        self.h = h

    def area(self):
        return self.w * self.h

    def scale(self, k):
        self.w *= k
        self.h *= k

r1 = Rectangle(2, 3)
r2 = Rectangle(4, 1)
r1.scale(2)
print(r1.area(), r2.area())
print(r1.w, r2.w)''',
    '`scale` 은 **r1 의** w, h 만 바꿔요. 객체마다 속성을 따로 가져요. r1 은 4×6=24, r2 는 4.\n\n```\n{out}\n```')

L.explain('메서드로 상태 바꾸기: 은행 계좌',
    [T('객체는 속성을 **기억**해요. 그래서 메서드를 부를 때마다 값이 쌓이거나 바뀌어요.\n'
       '2023년 11점 문항 소재(입출금 내역 + 출금 실패)를 단순하게 만들어 봐요.'),
     TRACE('''\
class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance
        self.history = []

    def deposit(self, amount):
        self.balance += amount
        self.history.append(amount)

    def withdraw(self, amount):
        if amount > self.balance:
            print("잔액 부족")
            return False
        self.balance -= amount
        self.history.append(-amount)
        return True

acc = Account("kim", 1000)
acc.deposit(500)
acc.withdraw(2000)
acc.withdraw(300)
print(acc.balance, acc.history)''', '계좌 따라가기')],
    [T('`self.history = []` 처럼 **리스트 속성**을 두면 기록을 쌓을 수 있어요.\n'
       '실패한 출금은 `return False` 로 **바로 끝내서** 잔액과 기록이 바뀌지 않게 해요.'),
     WARN('메서드 안에서 `balance += amount` 라고 `self.` 을 빼먹으면, 객체 속성이 아니라 **지역 변수**를 찾다가 오류가 나요.')])

L.fill('입금 메서드를 완성하세요.', '''\
class Wallet:
    def __init__(self, money):
        self.money = money

    def add(___, amount):
        ___.money += amount

w = Wallet(100)
w.add(50)
print(w.money)''', [['self'], ['self']],
    '메서드 첫 매개변수는 `self`, 속성은 `self.money` 로 접근해요. 결과는 150.', expect='150')

L.explain('__str__: print 했을 때 보일 모습',
    [T('객체를 그냥 `print` 하면 `<__main__.Book object at 0x…>` 처럼 알아보기 힘든 주소가 나와요.\n'
       '`__str__` 메서드를 만들어 **보여 줄 문자열을 return** 하면 print 가 그것을 써요.'),
     CMP(side('__str__ 없음', '알아보기 힘든 주소', 'class Book:\n    def __init__(self, title):\n        self.title = title\n\nprint(Book("어린 왕자"))', 'bad'),
         side('__str__ 있음', 'return 한 문자열이 출력돼요', 'class Book:\n    def __init__(self, title):\n        self.title = title\n\n    def __str__(self):\n        return "책: " + self.title\n\nprint(Book("어린 왕자"))', 'good'))],
    [T('`__str__` 은 반드시 **문자열을 return** 해야 해요. 안에서 print 만 하고 return 을 안 하면 None 이 돌아와 **TypeError** 가 나요.\n'
       '`str(객체)`, f-string `f"{객체}"` 도 `__str__` 을 써요.'),
     TIP('`__init__`, `__str__` 처럼 앞뒤에 밑줄 두 개가 붙은 메서드를 **특별 메서드(매직 메서드)** 라고 해요. 파이썬이 특정 순간에 알아서 불러요.')])

L.output('출력은?', '''\
class Student:
    def __init__(self, name, score):
        self.name = name
        self.score = score

    def grade(self):
        return "A" if self.score >= 90 else "B"

    def __str__(self):
        return f"{self.name}({self.score}점, {self.grade()})"

s = Student("하린", 93)
print(s)
s.score -= 10
print("결과: " + str(s))''',
    '메서드 안에서 다른 메서드를 부를 때도 `self.grade()` 처럼 써요. score 가 바뀌면 `__str__` 결과도 바뀌어요.\n\n```\n{out}\n```')

L.spot('실행하면 **오류**가 나는 줄은?', '''\
class Circle:
    def __init__(self, r):
        self.r = r

    def area():
        return 3 * self.r ** 2

c = Circle(2)
print(c.area())''', 9,
    '`area` 에 **self 매개변수가 없어요.** `c.area()` 는 c 를 첫 인자로 자동으로 넘기는데 받을 자리가 없으니 **TypeError**(takes 0 positional arguments but 1 was given) 가 호출한 9번 줄에서 나요. `def area(self):` 로 고쳐요.',
    error_line=9)

L.match('용어와 뜻을 이어 보세요.',
    [['클래스', '객체를 만드는 설계도'], ['객체(인스턴스)', '설계도로 만든 실물'], ['__init__', '객체를 만들 때 자동 호출'],
     ['self', '메서드를 부른 그 객체 자신'], ['__str__', 'print 할 때 보일 문자열 반환'], ['속성', 'self.name 처럼 객체가 가진 값']],
    '시험의 클래스 문항은 모두 이 여섯 단어로 설명할 수 있어요.')

L.ox('`__init__` 메서드는 객체를 만든 뒤 `obj.__init__()` 처럼 **직접 불러야** 실행된다.', False,
     '`클래스이름(...)` 으로 객체를 만드는 순간 **자동으로** 불려요. 괄호 안의 값이 `__init__` 의 self 다음 매개변수로 들어가요.')

L.order('`Pet` 클래스를 정의하고 사용하는 코드를 순서대로 놓으세요.',
    ['class Pet:', '    def __init__(self, name):', '        self.name = name', '    def __str__(self):',
     '        return "펫: " + self.name', 'p = Pet("콩이")', 'print(p)'],
    '클래스 정의(생성자 → 메서드)가 먼저, 객체 생성과 사용은 그 **아래**에 와요. 정의 전에 `Pet(...)` 을 쓰면 NameError.',
    check=True, expect='펫: 콩이')

L.practice('[기출유사] 입출금 내역이 남는 계좌',
'''첫 줄에 `이름 처음잔액`, 둘째 줄에 명령 수 N, 다음 N 줄에 `입금 금액` 또는 `출금 금액` 이 주어져요.

**[조건]**
- `Account` 클래스: 속성 `owner`, `balance`, `history`(리스트), 메서드 `deposit`, `withdraw`, `__str__`
- 출금액이 잔액보다 크면 `출금 실패: 잔액 부족` 을 출력하고 잔액·내역을 바꾸지 않아요.
- 내역에는 입금은 `+금액`, 출금은 `-금액` 문자열로 저장해요.
- 마지막 두 줄: `print(acc)` → `이름 님의 잔액: 금액원`, `내역: +500, -200` (`, ` 연결, 없으면 `내역: 없음`)

{ex}

{ex2}''',
'''class Account:
    def __init__(self, owner, balance):
        pass

    def deposit(self, amount):
        pass

    def withdraw(self, amount):
        pass

    def __str__(self):
        return ""

name, money = input().split()
acc = Account(name, int(money))
n = int(input())
for _ in range(n):
    cmd, amount = input().split()
    # 명령에 맞는 메서드를 부르세요

print(acc)
''',
'''class Account:
    def __init__(self, owner, balance):
        self.owner = owner
        self.balance = balance
        self.history = []                 # 거래 기록

    def deposit(self, amount):
        self.balance += amount
        self.history.append(f"+{amount}")

    def withdraw(self, amount):
        if amount > self.balance:         # 잔액보다 많으면 실패
            print("출금 실패: 잔액 부족")
            return
        self.balance -= amount
        self.history.append(f"-{amount}")

    def __str__(self):
        return f"{self.owner} 님의 잔액: {self.balance}원"

name, money = input().split()
acc = Account(name, int(money))
n = int(input())
for _ in range(n):
    cmd, amount = input().split()
    if cmd == "입금":
        acc.deposit(int(amount))
    else:
        acc.withdraw(int(amount))

print(acc)
print("내역:", ", ".join(acc.history) if acc.history else "없음")''',
    ['kim 1000\n3\n입금 500\n출금 2000\n출금 300', 'lee 0\n2\n출금 100\n입금 100'],
    ['park 500\n1\n출금 500', 'choi 10\n2\n출금 11\n출금 11', 'jung 0\n3\n입금 1\n입금 2\n출금 3'],
    ['`__init__` 에서 `self.history = []` 로 빈 리스트를 만들어 둬요.',
     'withdraw: `if amount > self.balance:` 이면 메시지 출력 후 `return` 으로 끝내요.',
     '`__str__` 은 `return f"{self.owner} 님의 잔액: {self.balance}원"`'],
    '잔액과 같은 금액은 출금할 수 있어요(`>` 로 비교). 실패하면 `return` 으로 함수를 끝내 아래 줄(잔액 감소·기록)이 실행되지 않게 하는 게 포인트예요.')

L.practice('[기출유사] 사각형 클래스',
'''첫 줄에 사각형 수 N, 다음 N 줄에 `가로 세로` 가 주어져요.

**[조건]**
- `Rectangle` 클래스: `__init__(self, w, h)`, `area()`, `perimeter()`, `is_square()`, `__str__`
- `__str__` 은 `가로x세로 넓이=넓이 둘레=둘레` 를 돌려주고, 정사각형이면 끝에 ` (정사각형)` 을 붙여요.
- 사각형마다 `print(객체)` 하고, 마지막 줄에 `가장 넓은 사각형: 번호번` (번호는 1부터, 같으면 앞 번호)

{ex}

{ex2}''',
'''class Rectangle:
    def __init__(self, w, h):
        pass
    # 메서드들을 작성하세요

n = int(input())
''',
'''class Rectangle:
    def __init__(self, w, h):
        self.w = w
        self.h = h

    def area(self):
        return self.w * self.h

    def perimeter(self):
        return 2 * (self.w + self.h)

    def is_square(self):
        return self.w == self.h

    def __str__(self):
        s = f"{self.w}x{self.h} 넓이={self.area()} 둘레={self.perimeter()}"
        if self.is_square():
            s += " (정사각형)"
        return s                          # 반드시 문자열을 return

n = int(input())
rects = []
for _ in range(n):
    w, h = map(int, input().split())
    rects.append(Rectangle(w, h))         # 객체를 리스트에 모으기
best = 0
for i, r in enumerate(rects):
    print(r)
    if r.area() > rects[best].area():
        best = i
print(f"가장 넓은 사각형: {best + 1}번")''',
    ['3\n3 4\n5 5\n2 10', '2\n1 1\n1 1'], ['1\n7 3', '3\n2 8\n4 4\n8 2', '2\n10 1\n3 4'],
    ['객체 리스트 `rects.append(Rectangle(w, h))` 로 모아 두면 나중에 비교하기 편해요.',
     '`__str__` 안에서 `self.area()`, `self.perimeter()` 를 불러 문자열을 만들어요.',
     '최댓값 번호: `if r.area() > rects[best].area(): best = i` → 출력은 `best + 1`'],
    '객체를 리스트에 담으면 `rects[i].area()` 처럼 객체마다 메서드를 부를 수 있어요. `>` 로 비교해야 넓이가 같을 때 앞 번호가 남아요.')

L.essay('메서드를 `def area():` 처럼 `self` 없이 정의하고 `c.area()` 로 부르면 오류가 나요. **`self` 의 역할**과 연결해 오류 이유를 서술하세요.',
    'self 는 메서드를 호출한 객체 자신을 가리키는 매개변수이다. c.area() 로 호출하면 파이썬이 객체 c 를 첫 번째 인자로 자동으로 넘기는데, area 에 이를 받을 매개변수가 없어서 인자 개수가 맞지 않는 TypeError 가 발생한다. 또 self 가 없으면 메서드 안에서 그 객체의 속성(self.r)에 접근할 수도 없다. def area(self): 로 고쳐야 한다.',
    ['self 는 호출한 객체 자신', '호출 시 객체가 첫 인자로 자동 전달', '받을 자리가 없어 TypeError', 'def area(self): 로 수정'])

# =====================================================================
L = C.lesson('γ-08 클래스 변수 vs 인스턴스 변수 · is 와 ==', 25,
'''- **인스턴스 변수** `self.x` — 객체마다 따로. **클래스 변수** (class 바로 아래) — 모든 객체가 **공유**.
- 클래스 변수를 바꿀 땐 `클래스이름.변수 += 1`. `self.변수 = …` 는 그 객체에만 새 속성을 만들어요(함정!).
- 클래스 변수 리스트에 append 하면 모든 객체가 같이 바뀌어요.
- `==` 는 **값**이 같은지, `is` 는 **같은 객체**인지. `id()` 는 객체 고유 번호.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간: `__init__` 으로 속성을 저장하고, 메서드 첫 매개변수 `self`, `__str__` 은 문자열을 return.'),
     REVEAL('`__str__` 안에서 return 없이 print 만 하면?', 'None 이 돌아와서 print(객체) 할 때 TypeError 가 나요.')])
L.output('복습: 출력은?', 'class P:\n    def __init__(self, x):\n        self.x = x\n    def __str__(self):\n        return "P" + str(self.x)\n\na = P(3)\na.x += 4\nprint(a)',
    '속성 x 가 7 로 바뀐 뒤 `__str__` 이 불려요 → {out}', review=True)

L.explain('클래스 변수: 모두가 같이 쓰는 값',
    [T('`class` 바로 아래(메서드 밖)에 만든 변수는 **클래스 변수**예요. 모든 객체가 **하나를 공유**해요.\n'
       '학급문고의 "전체 책 수" 처럼 **객체 전체에 대한 값**을 저장할 때 써요.'),
     CODE('''\
class Book:
    total = 0                      # 클래스 변수 (공유)

    def __init__(self, title):
        self.title = title         # 인스턴스 변수 (책마다)
        Book.total += 1            # 클래스 이름으로 바꾸기

b1 = Book("모모")
b2 = Book("데미안")
print(b1.title, b2.title)
print(Book.total, b1.total, b2.total)''', '학급문고 책 수 세기')],
    [T('두 변수를 비교해 봐요.'),
     CMP(side('인스턴스 변수', '`self.title` — 객체마다 다른 값. `__init__` 안에서 만들어요.', '', 'good'),
         side('클래스 변수', '`Book.total` — 모두 공유. class 바로 아래에 만들고 `클래스이름.변수` 로 바꿔요.', '', 'good')),
     TIP('읽을 때는 `b1.total` 처럼 객체로도 읽을 수 있어요. 객체에 그 이름이 없으면 **클래스에서 찾아** 오거든요.')])

L.output('출력은?', '''\
class Member:
    count = 0
    def __init__(self, name):
        self.name = name
        Member.count += 1
        self.no = Member.count

a = Member("가온")
b = Member("나래")
c = Member("다솜")
print(a.no, b.no, c.no)
print(Member.count, a.count)''',
    '객체를 만들 때마다 공유 카운터가 1 씩 늘고, 그 순간의 값을 **각자의 no** 에 저장해요.\n\n```\n{out}\n```')

L.explain('함정: self.클래스변수 = …',
    [T('클래스 변수를 `self.count += 1` 로 바꾸면 어떻게 될까요?\n'
       '파이썬은 `self.count = self.count + 1` 로 보고, 오른쪽은 클래스 값을 **읽어 오지만** 왼쪽 대입은 **그 객체에만 새 인스턴스 변수**를 만들어요.'),
     TRACE('''\
class Counter:
    count = 0
    def up(self):
        self.count += 1

a = Counter()
b = Counter()
a.up()
a.up()
b.up()
print(a.count, b.count, Counter.count)''', 'self 로 바꾸면?')],
    [T('결과적으로 a 와 b 는 각자 따로 세고, **클래스 변수는 0 그대로**예요.'),
     WARN('공유 값을 바꿀 때는 꼭 `클래스이름.변수` 로! 시험에서 "총 개수가 왜 0 인가" 를 묻는 함정으로 나와요.')])

L.output('출력은?', '''\
class Team:
    members = []          # 클래스 변수 (리스트!)
    def __init__(self, name):
        self.name = name
    def join(self, who):
        self.members.append(who)

t1 = Team("A")
t2 = Team("B")
t1.join("민")
t2.join("준")
print(t1.members)
print(len(Team.members))''',
    '이번엔 대입이 아니라 **append**(원본 수정)라서 새 변수가 생기지 않아요. 모두가 같은 리스트를 공유하니 t1 에도 "준" 이 보여요. 팀마다 따로 두려면 `__init__` 에서 `self.members = []`.\n\n```\n{out}\n```')

L.fill('객체가 만들어질 때마다 **공유 카운터**를 1 늘리세요.', '''\
class Car:
    made = 0
    def __init__(self, model):
        self.model = model
        ___.made += 1

Car("A"); Car("B"); Car("C")
print(Car.made)''', [['Car']],
    '클래스 변수는 `Car.made` 로 바꿔야 공유 값이 늘어요. `self.made += 1` 이면 Car.made 는 0 그대로예요.', expect='3')

L.explain('is 와 ==, 그리고 id()',
    [T('`==` 는 **값이 같은가**, `is` 는 **완전히 같은 객체인가**를 물어요.\n'
       '`id(x)` 는 객체마다 붙은 **고유 번호**예요. `a is b` 는 `id(a) == id(b)` 와 같아요.'),
     CODE('a = [1, 2]\nb = [1, 2]\nc = a\nprint(a == b, a is b)\nprint(a == c, a is c)\nprint(id(a) == id(c))', 'is vs =='),
     KEY('새로 만든 객체 둘은 값이 같아도 `is` 는 False. `c = a` 처럼 대입하면 같은 객체라 True.')],
    [T('직접 만든 클래스의 객체는 `__eq__` 를 따로 정의하지 않으면 `==` 도 **is 처럼** 동작해요(같은 객체일 때만 True).\n'
       '`None` 을 검사할 때는 `x is None` 이 관례예요.'),
     CODE('class P:\n    def __init__(self, n):\n        self.n = n\n\np1 = P(1)\np2 = P(1)\np3 = p1\nprint(p1 == p2, p1 is p3)', '내 클래스의 =='),
     EXAM('2025년 20점 문항에 `is` / `==` / `id()` 비교가 나왔어요. "값 비교 vs 객체 비교" 를 한 문장으로 쓸 수 있어야 해요.')])

L.bucket('각 식의 결과를 분류하세요. (`a = [1, 2]`, `b = [1, 2]`, `c = a`)', ['True', 'False'],
    [['a == b', 1], ['a is b', 2], ['a is c', 1], ['id(a) == id(b)', 2], ['c == b', 1], ['a is not b', 1]],
    '값은 셋 다 같아서 `==` 는 모두 True. 객체는 a·c 가 같은 것, b 는 따로라서 b 와의 `is` 는 False.')

L.spot('모든 객체의 수를 세려고 했는데 마지막에 **0** 이 출력돼요. 원인이 되는 줄은?', '''\
class Ticket:
    sold = 0
    def __init__(self, seat):
        self.seat = seat
        self.sold += 1

Ticket("A1")
Ticket("A2")
print(Ticket.sold)''', 5,
    '`self.sold += 1` 은 객체마다 새 인스턴스 변수 sold 를 만들 뿐, **클래스 변수 Ticket.sold 는 0 그대로**예요. `Ticket.sold += 1` 로 고쳐요.')

L.match('코드와 뜻을 이어 보세요.',
    [['a == b', '값이 같은가'], ['a is b', '같은 객체인가'], ['id(a)', '객체의 고유 번호'], ['x is None', 'None 검사 관례'], ['Book.total', '클래스 변수 접근']],
    '`is` 는 `id()` 가 같은지 보는 것과 같아요.')

L.short('출력값을 쓰세요.\n\n```python\na = [1]\nb = [1]\nprint(a == b, a is b)\n```', 'True False',
    '값은 같지만 따로 만든 두 리스트라 다른 객체예요.', check_code='a = [1]\nb = [1]\nprint(a == b, a is b)')

L.choice('클래스 변수에 대한 설명으로 옳은 것은?',
    ['__init__ 안에서 self.변수 로 만든다', '객체마다 다른 값을 가진다', 'class 바로 아래에 만들고 모든 객체가 공유한다', 'self.변수 += 1 로 바꾸면 모든 객체에 반영된다'], 3,
    '①②는 인스턴스 변수 설명, ④는 함정 — self 로 대입하면 그 객체에만 새 인스턴스 변수가 생겨요.')

L.practice('[기출유사] 학급문고 대출 관리',
'''첫 줄에 명령 수 N, 다음 N 줄에 `등록 제목`, `대출 제목`, `반납 제목` 명령이 주어져요(제목은 한 단어).

**[조건]**
- `Book` 클래스: 클래스 변수 `total`(전체 책 수), `out`(대출 중인 책 수), 인스턴스 변수 `title`, `borrowed`(True/False)
- 등록하면 `total` 이 1 늘어요. 책 객체는 딕셔너리 `shelf = {제목: Book객체}` 에 저장해요.
- 대출: 이미 대출 중이면 `이미 대출 중`, 아니면 `대출 완료`. 반납: 대출 중이 아니면 `대출 기록 없음`, 아니면 `반납 완료`.
- 없는 제목이면 `없는 책`. 마지막 줄: `전체 X권, 대출 중 Y권`

{ex}

{ex2}''',
'''class Book:
    total = 0
    out = 0

    def __init__(self, title):
        pass

shelf = {}
n = int(input())
for _ in range(n):
    cmd, title = input().split()
    # 명령을 처리하세요

print(f"전체 {Book.total}권, 대출 중 {Book.out}권")''',
'''class Book:
    total = 0          # 클래스 변수: 전체 책 수
    out = 0            # 클래스 변수: 대출 중인 책 수

    def __init__(self, title):
        self.title = title
        self.borrowed = False
        Book.total += 1            # 클래스 이름으로 바꾸기

    def lend(self):
        if self.borrowed:
            print("이미 대출 중")
        else:
            self.borrowed = True
            Book.out += 1
            print("대출 완료")

    def give_back(self):
        if not self.borrowed:
            print("대출 기록 없음")
        else:
            self.borrowed = False
            Book.out -= 1
            print("반납 완료")

shelf = {}
n = int(input())
for _ in range(n):
    cmd, title = input().split()
    if cmd == "등록":
        shelf[title] = Book(title)
    elif title not in shelf:
        print("없는 책")
    elif cmd == "대출":
        shelf[title].lend()
    else:
        shelf[title].give_back()

print(f"전체 {Book.total}권, 대출 중 {Book.out}권")''',
    ['5\n등록 모모\n등록 데미안\n대출 모모\n대출 모모\n반납 데미안', '3\n대출 해리\n등록 해리\n반납 해리'],
    ['1\n등록 A', '4\n등록 A\n대출 A\n반납 A\n대출 A', '6\n등록 X\n등록 Y\n대출 X\n대출 Y\n반납 X\n대출 Z'],
    ['`__init__` 에서 `self.borrowed = False` 와 `Book.total += 1`.',
     '대출·반납 메서드를 만들고 `Book.out += 1` / `Book.out -= 1` 로 공유 값을 바꿔요.',
     '명령 처리: 등록이면 `shelf[title] = Book(title)`, 아니면 먼저 `title not in shelf` 를 검사해요.'],
    '책마다 다른 값(제목, 대출 여부)은 인스턴스 변수, 학급문고 전체의 값(총 권수, 대출 중 권수)은 클래스 변수예요. 클래스 변수는 꼭 `Book.` 으로 바꿔야 해요.')

L.essay('클래스 변수와 인스턴스 변수의 차이를 **저장 위치·공유 여부·바꾸는 방법** 측면에서 서술하세요.',
    '클래스 변수는 class 바로 아래에 정의되어 클래스에 하나만 저장되고, 그 클래스로 만든 모든 객체가 공유한다. 바꿀 때는 클래스이름.변수 로 바꾼다. 인스턴스 변수는 __init__ 등에서 self.변수 로 만들어 객체마다 따로 저장되므로 한 객체의 값을 바꿔도 다른 객체에는 영향이 없다. self.클래스변수 = 값 처럼 대입하면 클래스 변수가 바뀌지 않고 그 객체에 새 인스턴스 변수가 생긴다.',
    ['클래스 변수는 모든 객체가 공유', '인스턴스 변수는 객체마다 따로', '클래스 변수는 클래스이름.변수 로 변경', 'self 로 대입하면 새 인스턴스 변수가 생김'])

# =====================================================================
L = C.lesson('γ-09 상속 · super() · 오버라이딩', 30,
'''- `class 자식(부모):` — 부모의 속성·메서드를 **물려받아요**. 자식에서 새 메서드를 더할 수 있어요.
- **오버라이딩**: 부모와 **같은 이름**의 메서드를 자식에서 다시 정의 → 자식 것이 쓰여요.
- `super().__init__(…)` 로 부모의 생성자를 불러 부모 속성을 만들어요. 빼먹으면 AttributeError!
- `super().메서드()` 로 부모 기능을 쓰고 **덧붙일** 수 있어요.
- 부모 메서드에서 `raise NotImplementedError` → "자식이 꼭 오버라이딩하라" 는 약속.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간: 클래스 변수는 모두 공유(`클래스이름.변수` 로 변경), 인스턴스 변수는 객체마다. `is` 는 같은 객체인지, `==` 는 값.'),
     REVEAL('`self.count += 1` 로 클래스 변수를 바꾸려 하면?', '그 객체에만 새 인스턴스 변수 count 가 생기고, 클래스 변수는 그대로예요.')])
L.output('복습: 출력은?', 'class K:\n    n = 0\n    def __init__(self):\n        K.n += 1\n\na = K(); b = K()\nprint(K.n, a.n is b.n)',
    '두 번 만들어 K.n 은 2, a.n 과 b.n 은 같은 클래스 변수를 읽어요 → {out}', review=True)

L.explain('상속: 부모 것을 물려받기',
    [T('비슷한 클래스를 여러 개 만들 때 공통 부분을 **부모 클래스**에 두고, 자식은 `class 자식(부모):` 로 물려받아요.\n'
       '자식은 부모의 메서드를 **그대로 쓸 수 있고**, 자기만의 메서드를 **추가**할 수도 있어요.'),
     CODE('''\
class Animal:
    def __init__(self, name):
        self.name = name
    def eat(self):
        print(self.name, "냠냠")

class Cat(Animal):          # Animal 을 상속
    def meow(self):         # 새 메서드 추가
        print(self.name, "야옹")

c = Cat("나비")
c.eat()        # 부모에게 물려받은 메서드
c.meow()''', '상속 기본')],
    [T('`Cat` 에는 `__init__` 이 없는데도 `Cat("나비")` 가 돼요. 자식에서 못 찾으면 **부모에서 찾아** 쓰거든요.'),
     KEY('메서드를 찾는 순서: **자식 → 부모 → 그 부모 …** 먼저 찾은 것을 써요.')])

L.explain('오버라이딩: 같은 이름으로 다시 정의',
    [T('부모와 **같은 이름**의 메서드를 자식에 다시 만들면, 자식 객체는 **자식의 것**을 써요. 이것을 **오버라이딩(재정의)** 이라고 해요.'),
     TABS(('오버라이딩', '자식이 sound 를 다시 정의', 'class Animal:\n    def sound(self):\n        return "..."\n\nclass Dog(Animal):\n    def sound(self):\n        return "멍멍"\n\nprint(Animal().sound(), Dog().sound())'),
          ('super().메서드()', '부모 결과에 **덧붙이기**', 'class Animal:\n    def info(self):\n        return "동물"\n\nclass Dog(Animal):\n    def info(self):\n        return super().info() + " > 개"\n\nprint(Dog().info())'))],
    [T('부모 메서드 안에서 `self.sound()` 를 부르면, **실제 객체가 자식이면 자식의 sound** 가 불려요.\n'
       '이 점이 출력 추론 문제의 핵심 함정이에요.'),
     THINK('`self` 는 "지금 이 객체" 예요. 메서드가 **어느 클래스에 적혀 있는지**가 아니라 **객체가 누구인지**로 정해져요.')])

L.output('출력은?', '''\
class Shape:
    def name(self):
        return "도형"
    def describe(self):
        return "나는 " + self.name()

class Circle(Shape):
    def name(self):
        return "원"

class Dot(Shape):
    pass

print(Shape().describe())
print(Circle().describe())
print(Dot().describe())''',
    'describe 는 Shape 에만 있지만 그 안의 `self.name()` 은 **객체에 따라** 달라져요. Circle 은 오버라이딩한 "원", Dot 은 물려받은 "도형".\n\n```\n{out}\n```')

L.explain('super().__init__ — 부모 생성자 부르기',
    [T('자식에 **`__init__` 을 새로 만들면** 부모의 `__init__` 은 자동으로 불리지 않아요(오버라이딩이니까요).\n'
       '부모가 만드는 속성도 필요하면 `super().__init__(…)` 로 **직접 불러야** 해요.'),
     CMP(side('super() 빼먹음', '부모 속성 name 이 만들어지지 않아요',
              'class Person:\n    def __init__(self, name):\n        self.name = name\n\nclass Student(Person):\n    def __init__(self, name, sid):\n        self.sid = sid\n\ns = Student("지우", 7)\nprint(s.name)', 'bad', expect_error=True),
         side('super() 사용', '부모가 name 을, 자식이 sid 를 만들어요',
              'class Person:\n    def __init__(self, name):\n        self.name = name\n\nclass Student(Person):\n    def __init__(self, name, sid):\n        super().__init__(name)\n        self.sid = sid\n\ns = Student("지우", 7)\nprint(s.name, s.sid)', 'good'))],
    [T('`super()` 는 "**내 부모 클래스**" 를 뜻해요. `super().__init__(name)` 에는 **self 를 쓰지 않아요.**\n'
       '`Person.__init__(self, name)` 처럼 부모 이름을 직접 쓰는 방법도 있는데, 이때는 self 를 넣어야 해요.'),
     EXAM('2024년 6점: super().__init__ 이 들어간 클래스의 **출력 순서** 추론. 생성자 안의 print 가 어떤 순서로 나오는지 따라가요.')])

L.output('출력은?', '''\
class A:
    def __init__(self):
        print("A 시작")
        self.x = 1

class B(A):
    def __init__(self):
        print("B 시작")
        super().__init__()
        self.x += 10
        print("B 끝", self.x)

class C(B):
    def __init__(self):
        super().__init__()
        print("C 끝", self.x * 2)

C()''',
    'C → super() 로 B → B 가 "B 시작" 출력 후 super() 로 A → "A 시작", x=1 → B 로 돌아와 x=11, "B 끝 11" → C 로 돌아와 "C 끝 22".\n\n```\n{out}\n```')

L.spot('실행하면 **오류**가 나는 줄은?', '''\
class Vehicle:
    def __init__(self, wheels):
        self.wheels = wheels

class Bike(Vehicle):
    def __init__(self, owner):
        self.owner = owner

b = Bike("민호")
print(b.owner)
print(b.wheels)''', 11,
    'Bike 의 `__init__` 이 부모 생성자를 부르지 않아 `wheels` 속성이 없어요 → 11번 줄에서 **AttributeError**. `super().__init__(2)` 를 추가해요.',
    error_line=11)

L.explain('NotImplementedError — "자식이 꼭 만들어!"',
    [T('부모 클래스가 "모든 도형은 넓이를 구할 수 있어야 해" 처럼 **틀만 정해 두고** 실제 계산은 자식에게 맡길 때가 있어요.\n'
       '부모 메서드에서 `raise NotImplementedError` 를 하면, 자식이 오버라이딩하지 않았을 때 **바로 알 수 있어요.**'),
     CODE('''\
class Shape:
    def area(self):
        raise NotImplementedError("자식 클래스에서 area 를 만드세요")

class Square(Shape):
    def __init__(self, s):
        self.s = s
    def area(self):
        return self.s ** 2

class Blob(Shape):
    pass

print(Square(3).area())
try:
    Blob().area()
except NotImplementedError as e:
    print("오류:", e)''', '추상 메서드 흉내')],
    [T('Square 는 area 를 오버라이딩해서 정상, Blob 은 안 해서 부모의 raise 가 실행돼요.'),
     TIP('2023년 6점 문항 소재예요. "왜 NotImplementedError 를 쓰는가" → **자식 클래스가 반드시 재정의하도록 강제**하기 위해.')])

L.order('`Teacher` 가 `Person` 을 상속하고 부모 생성자를 부르도록 순서대로 놓으세요.',
    ['class Person:', '    def __init__(self, name):', '        self.name = name', 'class Teacher(Person):',
     '    def __init__(self, name, subject):', '        super().__init__(name)', '        self.subject = subject',
     't = Teacher("윤", "정보")', 'print(t.name, t.subject)'],
    '부모 클래스를 먼저 정의하고, 자식 생성자 첫 줄에서 `super().__init__(name)` 으로 부모 속성을 만든 다음 자기 속성을 더해요.',
    check=True, expect='윤 정보')

L.match('설명과 용어를 이어 보세요.',
    [['부모 기능을 물려받음', '상속'], ['같은 이름 메서드를 자식이 다시 정의', '오버라이딩'], ['부모 클래스를 가리킴', 'super()'],
     ['자식이 꼭 재정의하게 강제', 'raise NotImplementedError'], ['자식 __init__ 에서 부모 속성 만들기', 'super().__init__(...)']],
    '상속 단원 서술형은 이 다섯 용어로 거의 다 설명돼요.')

L.choice('자식 생성자에서 부모 생성자를 부르는 **올바른** 코드는? (부모 생성자: `def __init__(self, name)`)',
    ['super().__init__(self, name)', 'super().__init__(name)', 'super.__init__(name)', '__init__(name)'], 2,
    '`super()` 가 이미 self 를 알고 있어서 **self 를 넣지 않아요.** 부모 이름으로 직접 부를 땐 `Person.__init__(self, name)` 처럼 self 를 넣어요. `super` 뒤 괄호도 꼭!')

L.practice('[기출유사] 도형 넓이 계산기',
'''첫 줄에 도형 수 N, 다음 N 줄에 `rect 가로 세로`, `square 한변`, `tri 밑변 높이` 또는 그 밖의 이름(예: `circle 3`)이 주어져요.

**[조건]**
- 부모 `Shape(name)`: `area()` 는 `raise NotImplementedError`, `describe()` 는 `이름 넓이: 값` 을 돌려줘요(값은 `self.area()`).
- `Rect(Shape)`, `Tri(Shape)` 는 area 를 오버라이딩. `Square(Rect)` 는 `super().__init__` 으로 Rect 를 재사용하고 이름만 `정사각형` 으로.
- 이름: Rect `직사각형`, Square `정사각형`, Tri `삼각형`(넓이는 `밑변 * 높이 / 2`)
- 모르는 도형은 `Shape(그 이름)` 으로 만들고, describe 할 때 나는 NotImplementedError 를 잡아 `계산 불가: 이름` 출력.

{ex}

{ex2}''',
'''class Shape:
    def __init__(self, name):
        self.name = name
    def area(self):
        raise NotImplementedError
    def describe(self):
        return f"{self.name} 넓이: {self.area()}"

# Rect, Square, Tri 를 만드세요

n = int(input())
''',
'''class Shape:
    def __init__(self, name):
        self.name = name
    def area(self):
        raise NotImplementedError          # 자식이 꼭 재정의해야 함
    def describe(self):
        return f"{self.name} 넓이: {self.area()}"

class Rect(Shape):
    def __init__(self, w, h):
        super().__init__("직사각형")       # 부모 생성자로 name 설정
        self.w, self.h = w, h
    def area(self):
        return self.w * self.h

class Square(Rect):
    def __init__(self, s):
        super().__init__(s, s)             # Rect 의 생성자 재사용
        self.name = "정사각형"             # 이름만 바꾸기

class Tri(Shape):
    def __init__(self, b, h):
        super().__init__("삼각형")
        self.b, self.h = b, h
    def area(self):
        return self.b * self.h / 2

n = int(input())
for _ in range(n):
    p = input().split()
    kind, nums = p[0], list(map(int, p[1:]))
    if kind == "rect":
        s = Rect(nums[0], nums[1])
    elif kind == "square":
        s = Square(nums[0])
    elif kind == "tri":
        s = Tri(nums[0], nums[1])
    else:
        s = Shape(kind)
    try:
        print(s.describe())
    except NotImplementedError:
        print("계산 불가:", s.name)''',
    ['3\nrect 3 4\nsquare 5\ntri 6 3', '2\ncircle 2\ntri 5 5'], ['1\nsquare 1', '4\nhexagon 1\nrect 10 0\ntri 1 1\nsquare 12', '2\nrect 7 7\nstar 5'],
    ['Rect 의 `__init__` 첫 줄: `super().__init__("직사각형")`',
     'Square 는 `class Square(Rect):` 이고 `super().__init__(s, s)` 후 `self.name = "정사각형"`',
     '출력은 `try: print(s.describe())` / `except NotImplementedError: print("계산 불가:", s.name)`'],
    'describe 는 부모에만 있지만 `self.area()` 는 실제 객체의 area 를 불러요. Square 는 Rect 의 area 를 물려받아 따로 만들 필요가 없어요. 삼각형 넓이는 `/` 라서 실수(9.0)로 나와요.')

L.practice('[기출유사] 직원 급여 계산',
'''첫 줄에 직원 수 N, 다음 N 줄에 `종류 이름 기본급` (매니저는 끝에 `보너스` 가 하나 더) 이 주어져요. 단위는 만원이에요.

**[조건]**
- `Employee(name, base)`: `pay()` 는 base 를 돌려주고, `__str__` 은 `이름(직급): 급여만원` (직급은 클래스 변수 `title = "사원"`)
- `Manager(Employee)`: 클래스 변수 `title = "매니저"`, 생성자에서 `super().__init__` + `bonus` 저장, `pay()` 는 `super().pay() + bonus`
- `Intern(Employee)`: `title = "인턴"`, `pay()` 는 기본급의 절반을 **정수 나눗셈** `// 2`
- 종류: `emp`, `manager`, `intern`. 마지막 줄: `총 급여: 합계만원`

{ex}

{ex2}''',
'''class Employee:
    title = "사원"
    def __init__(self, name, base):
        pass
    def pay(self):
        pass
    def __str__(self):
        return f"{self.name}({self.title}): {self.pay()}만원"

# Manager, Intern 을 만드세요

n = int(input())
''',
'''class Employee:
    title = "사원"
    def __init__(self, name, base):
        self.name = name
        self.base = base
    def pay(self):
        return self.base
    def __str__(self):
        return f"{self.name}({self.title}): {self.pay()}만원"   # title, pay 는 객체에 따라 달라짐

class Manager(Employee):
    title = "매니저"                     # 클래스 변수도 오버라이딩
    def __init__(self, name, base, bonus):
        super().__init__(name, base)      # 부모가 name, base 를 저장
        self.bonus = bonus
    def pay(self):
        return super().pay() + self.bonus  # 부모 결과에 보너스 덧붙이기

class Intern(Employee):
    title = "인턴"
    def pay(self):
        return self.base // 2

n = int(input())
staff = []
for _ in range(n):
    p = input().split()
    if p[0] == "manager":
        staff.append(Manager(p[1], int(p[2]), int(p[3])))
    elif p[0] == "intern":
        staff.append(Intern(p[1], int(p[2])))
    else:
        staff.append(Employee(p[1], int(p[2])))
for e in staff:
    print(e)
print(f"총 급여: {sum(e.pay() for e in staff)}만원")''',
    ['3\nemp 김 300\nmanager 이 400 80\nintern 박 201', '1\nmanager 최 500 0'], ['1\nintern 정 1', '2\nemp a 0\nemp b 0', '3\nintern x 99\nmanager y 1 1\nemp z 10'],
    ['Manager 생성자: `super().__init__(name, base)` 다음 `self.bonus = bonus`',
     'Manager 의 pay: `return super().pay() + self.bonus`',
     'Intern 은 생성자를 새로 만들 필요 없이 `pay` 만 오버라이딩: `return self.base // 2`'],
    '`__str__` 은 부모에만 있지만 `self.title` 과 `self.pay()` 는 **객체의 클래스**에서 먼저 찾아요. 그래서 Manager 객체는 "매니저" 와 보너스가 더해진 급여를 보여 줘요.')

L.essay('부모 클래스의 메서드에 `raise NotImplementedError` 를 넣어 두는 **이유**를 오버라이딩과 연결해 서술하고, 자식이 그 메서드를 오버라이딩하지 않으면 어떻게 되는지 쓰세요.',
    '부모 클래스는 모든 자식이 가져야 할 메서드의 이름(틀)만 정해 두고, 실제 내용은 자식 클래스가 오버라이딩해서 만들도록 강제하기 위해 raise NotImplementedError 를 넣는다. 자식이 그 메서드를 오버라이딩하지 않으면 부모의 메서드가 그대로 실행되어 NotImplementedError 가 발생하므로, 재정의를 빠뜨린 것을 바로 알 수 있다.',
    ['자식이 반드시 오버라이딩하도록 강제', '부모는 틀(이름)만 정함', '재정의 안 하면 부모 메서드 실행', 'NotImplementedError 발생'])

# =====================================================================
L = C.lesson('γ-10 다중상속과 MRO (기초)', 20,
'''- `class C(A, B):` — 부모를 **여러 개** 물려받을 수 있어요.
- 같은 이름 메서드가 여러 부모에 있으면 **왼쪽 부모부터** 찾아요.
- 찾는 순서 = **MRO**. `클래스.mro()` 또는 `클래스.__mro__` 로 확인. 끝은 항상 `object`.
- `isinstance(객체, 클래스)` 는 그 클래스나 **자손**이면 True.
- 기본편 목표: MRO 를 보고 **출력을 추론**하는 것까지.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간: 상속·오버라이딩·`super().__init__`·NotImplementedError 를 배웠어요.'),
     REVEAL('자식에 __init__ 을 새로 만들고 super().__init__ 을 빼먹으면?', '부모가 만드는 속성이 생기지 않아, 그 속성을 쓸 때 AttributeError 가 나요.')])
L.output('복습: 출력은?', 'class P:\n    def hi(self):\n        return "P"\n    def run(self):\n        return "[" + self.hi() + "]"\n\nclass Q(P):\n    def hi(self):\n        return "Q"\n\nprint(Q().run())',
    'run 은 P 에 있지만 `self.hi()` 는 Q 의 것 → {out}', review=True)

L.explain('다중상속: 부모가 둘 이상',
    [T('`class 자식(부모1, 부모2):` 처럼 괄호에 부모를 여러 개 쓰면 **둘의 기능을 모두** 물려받아요.\n'
       '2024년에 `CTO(Manager, Engineer)` 처럼 두 역할을 합친 클래스가 나왔어요.'),
     CODE('''\
class Manager:
    def plan(self):
        return "계획 세우기"
    def work(self):
        return "회의"

class Engineer:
    def code(self):
        return "코드 작성"
    def work(self):
        return "개발"

class CTO(Manager, Engineer):
    pass

c = CTO()
print(c.plan(), "/", c.code())
print(c.work())''', '두 부모 물려받기')],
    [T('`plan` 과 `code` 는 한쪽에만 있어 문제없어요. 그런데 `work` 는 **양쪽에 다** 있어요. 누구 것을 쓸까요?'),
     KEY('**왼쪽에 쓴 부모부터** 찾아요. `CTO(Manager, Engineer)` 이니 Manager 의 work → "회의".')])

L.choice('`class CTO(Engineer, Manager):` 로 **순서를 바꾸면** `CTO().work()` 의 결과는? (위 코드 기준)',
    ['회의', '개발', '회의 개발', 'TypeError'], 2,
    '이제 Engineer 가 왼쪽이라 Engineer 의 work → "개발". 괄호 속 부모 순서가 곧 찾는 순서예요.')

L.explain('MRO: 메서드를 찾는 순서표',
    [T('**MRO**(Method Resolution Order)는 메서드·속성을 찾는 순서예요. `클래스.mro()` 로 볼 수 있어요.'),
     CODE('''\
class Employee:
    def work(self):
        return "일반 업무"
class Manager(Employee):
    pass
class Engineer(Employee):
    def work(self):
        return "개발"
class CTO(Manager, Engineer):
    pass

print([k.__name__ for k in CTO.mro()])
print(CTO().work())''', 'mro() 확인')],
    [T('읽는 규칙(기본편 수준)은 이렇게 기억해요.'),
     STEPS(('1. 자기 자신', '먼저 CTO 에서 찾아요.'),
           ('2. 왼쪽 부모', '다음은 Manager.'),
           ('3. 오른쪽 부모', '그다음 Engineer. **공통 조상(Employee)은 자식들을 다 본 뒤에!**'),
           ('4. 공통 조상 → object', 'Employee, 마지막은 항상 object.')),
     THINK('Manager 에 work 가 없지만 바로 Employee 로 가지 않고 **Engineer 를 먼저** 봐요. 그래서 결과가 "개발" 이에요.')])

L.order('위 코드에서 `CTO.mro()` 의 순서대로 놓으세요.', ['CTO', 'Manager', 'Engineer', 'Employee', 'object'],
    '자기 → 왼쪽 부모 → 오른쪽 부모 → 공통 조상 → object.', mono=True)

L.explain('여러 단계 상속과 super() 출력 추론',
    [T('2025년 20점 문항은 `Person → Student → HighSchoolStudent` 처럼 **여러 단계** 상속과 출력 추론이었어요.\n'
       '`super()` 를 따라 한 칸씩 올라갔다가 **돌아오면서** 나머지 줄을 실행해요.'),
     TRACE('''\
class Person:
    def __init__(self, name):
        self.name = name
    def intro(self):
        return "저는 " + self.name

class Student(Person):
    def intro(self):
        return super().intro() + ", 학생"

class HighSchoolStudent(Student):
    def intro(self):
        return super().intro() + ", 고등학생"

h = HighSchoolStudent("서준")
print(h.intro())
print(isinstance(h, Person), isinstance(Person("a"), Student))''', '단계별 super')],
    [T('`isinstance(객체, 클래스)` 는 객체가 그 클래스이거나 **자손 클래스**의 객체면 True 예요. 부모 객체는 자식 클래스의 인스턴스가 아니에요.'),
     TIP('`issubclass(자식, 부모)` 는 클래스끼리 관계를 물어요. `issubclass(Student, Person)` → True.')])

L.bucket('위 코드 기준으로 결과를 분류하세요. (`h = HighSchoolStudent("서준")`, `p = Person("하윤")`)', ['True', 'False'],
    [['isinstance(h, Student)', 1], ['isinstance(h, Person)', 1], ['isinstance(p, Student)', 2],
     ['issubclass(Student, Person)', 1], ['issubclass(Person, HighSchoolStudent)', 2], ['isinstance(h, object)', 1]],
    '자손은 조상의 인스턴스로 인정돼요(고등학생은 사람). 반대로 조상은 자손이 아니에요. 모든 클래스는 object 의 자손.')

L.output('출력은?', '''\
class A:
    def who(self):
        return "A"
class B(A):
    pass
class C(A):
    def who(self):
        return "C"
class D(B, C):
    pass

print(D().who())
print([k.__name__ for k in D.mro()])''',
    'D 에도 B 에도 who 가 없어요. 바로 A 로 가는 게 아니라 MRO 순서(D → B → **C** → A)대로 찾으니 C 의 who 가 먼저 찾아져요. 공통 조상 A 는 자식들을 다 본 뒤에!\n\n```\n{out}\n```')

L.ox('`class X(A, B):` 에서 A 와 B 에 같은 이름의 메서드가 있으면 **B 의 메서드**가 쓰인다.', False,
     '괄호 안 **왼쪽(A)** 부터 찾아요. A 에 있으면 A 의 것을 써요.')

L.short('`class Z(Y, X): pass` 일 때 `Z.mro()[1].__name__` 의 값은? (Y, X 는 object 만 상속)', 'Y',
    'MRO 는 Z → Y → X → object. 인덱스 1 은 왼쪽 부모 Y.',
    check_code='class X: pass\nclass Y: pass\nclass Z(Y, X): pass\nprint(Z.mro()[1].__name__)')

L.fill('클래스 D 의 메서드 탐색 순서를 이름으로 출력하세요.', 'class A: pass\nclass B(A): pass\nclass D(B): pass\nprint([k.__name__ for k in D.___()])', [['mro']],
    '`클래스.mro()` 는 탐색 순서대로 클래스 리스트를 돌려줘요. 결과는 `["D", "B", "A", "object"]` 모양(실제 출력은 작은따옴표)이에요.',
    expect="['D', 'B', 'A', 'object']")

L.ox('직접 만든 모든 클래스의 MRO 맨 끝에는 `object` 가 있다.', True,
     '파이썬 3 의 모든 클래스는 `object` 를 조상으로 가져요. 그래서 `__str__` 을 안 만들어도 object 의 기본 `__str__` 이 쓰여요.')

L.practice('[기출유사] 동아리 역할 카드',
'''첫 줄에 회원 수 N, 다음 N 줄에 `이름 종류` 가 주어져요. 종류는 `student`, `coder`, `leader` 예요.

**[조건]** — 아래 클래스를 그대로 만들어 쓰세요.
- `Student(name)`: `role()` → `"학생"`, `card()` → `이름[역할]` (역할은 `self.role()`)
- `Coder`: `role()` → `"코더"` / `Leader`: `role()` → `"부장"` (둘 다 생성자 없음)
- `StudentCoder(Coder, Student)`, `StudentLeader(Leader, Coder, Student)` — 몸체는 `pass`
- 각 회원마다 `card()` 를 출력하고, 같은 줄에 ` / ` 뒤에 MRO 클래스 이름을 `>` 로 연결해요(object 제외).

{ex}

{ex2}''',
'''class Student:
    def __init__(self, name):
        self.name = name
    def role(self):
        return "학생"
    def card(self):
        return f"{self.name}[{self.role()}]"

# Coder, Leader, StudentCoder, StudentLeader 를 만드세요

n = int(input())
''',
'''class Student:
    def __init__(self, name):
        self.name = name
    def role(self):
        return "학생"
    def card(self):
        return f"{self.name}[{self.role()}]"

class Coder:
    def role(self):
        return "코더"

class Leader:
    def role(self):
        return "부장"

class StudentCoder(Coder, Student):            # role 은 Coder 것, __init__·card 는 Student 것
    pass

class StudentLeader(Leader, Coder, Student):   # role 은 가장 왼쪽 Leader 것
    pass

kinds = {"student": Student, "coder": StudentCoder, "leader": StudentLeader}
n = int(input())
for _ in range(n):
    name, kind = input().split()
    m = kinds[kind](name)                        # 딕셔너리에서 클래스를 꺼내 객체 생성
    path = ">".join(k.__name__ for k in type(m).mro() if k is not object)
    print(m.card(), "/", path)''',
    ['3\n지민 student\n태오 coder\n예린 leader', '1\n하루 coder'], ['1\nA student', '2\nB leader\nC leader', '3\nx coder\ny student\nz coder'],
    ['Coder, Leader 는 `role` 하나만 있는 작은 클래스예요.',
     '`class StudentCoder(Coder, Student): pass` — 생성자는 MRO 를 따라 Student 에서 찾아져요.',
     'MRO 이름: `">".join(k.__name__ for k in type(m).mro() if k is not object)`'],
    'StudentCoder 에는 아무것도 없지만 MRO(StudentCoder → Coder → Student) 순서로 찾아서 `__init__`·`card` 는 Student 것, `role` 은 Coder 것을 써요. card 안의 `self.role()` 도 MRO 를 따라요.')

L.essay('`class CTO(Manager, Engineer):` 에서 Manager 와 Engineer 에 모두 `work()` 가 있을 때 `CTO().work()` 가 어떤 메서드를 실행하는지 **MRO 와 연결해** 서술하세요.',
    '파이썬은 메서드를 MRO(메서드 결정 순서)에 따라 찾는다. CTO 의 MRO 는 CTO → Manager → Engineer → … → object 순서이므로, CTO 에 work 가 없으면 괄호 안에서 왼쪽에 쓴 Manager 를 먼저 찾아 Manager 의 work() 가 실행된다. Engineer 의 work() 는 실행되지 않는다.',
    ['MRO 순서로 메서드를 찾는다', '자기 자신 → 왼쪽 부모 → 오른쪽 부모', 'Manager 의 work() 실행', 'CTO.mro() 로 확인 가능'])

# =====================================================================
L = C.lesson('γ-11 캡슐화: private 속성 · getter/setter · AttributeError', 25,
'''- **캡슐화** = 중요한 데이터를 밖에서 함부로 바꾸지 못하게 숨기고, **메서드로만** 다루게 하기.
- 이름 앞에 `__` 두 개(`self.__balance`)를 붙이면 private → 밖에서 `obj.__balance` 는 **AttributeError**.
- 이유: 파이썬이 이름을 `_클래스명__balance` 로 바꿔(name mangling) 저장하기 때문.
- 읽기는 **getter**(`get_balance()`), 바꾸기는 **setter**(`set_…()`) 에서 **검사 후** 변경.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간: 다중상속은 왼쪽 부모부터, 찾는 순서는 `mro()`, `isinstance` 는 자손도 True.'),
     REVEAL_RUN('`class C(A, B): pass` 일 때 MRO 는?', 'class A: pass\nclass B: pass\nclass C(A, B): pass\nprint([k.__name__ for k in C.mro()])')])
L.ox('복습: `isinstance(부모객체, 자식클래스)` 는 True 이다.', False,
     '자식 객체는 부모의 인스턴스로 인정되지만, 부모 객체는 자식 클래스의 인스턴스가 아니에요.', review=True)

L.explain('왜 숨겨야 할까?',
    [T('계좌 잔액을 아무나 `acc.balance = -999999` 처럼 바꿀 수 있으면 큰일이에요.\n'
       '**캡슐화**는 중요한 속성을 숨기고, 정해진 **메서드를 통해서만** 읽고 바꾸게 하는 거예요. 메서드 안에서 값이 올바른지 **검사**할 수 있거든요.'),
     CMP(side('공개 속성', '밖에서 마음대로 바꿀 수 있어요',
              'class Card:\n    def __init__(self):\n        self.money = 1000\n\nc = Card()\nc.money = -5000\nprint(c.money)', 'bad'),
         side('private 속성', '밖에서 직접 읽으면 AttributeError',
              'class Card:\n    def __init__(self):\n        self.__money = 1000\n\nc = Card()\nprint(c.__money)', 'good', expect_error=True))],
    [T('**클래스 안**에서는 `self.__money` 로 자유롭게 쓸 수 있어요. 막히는 건 **클래스 밖**에서 접근할 때뿐이에요.'),
     KEY('`__이름` (앞에 밑줄 두 개) = private. 단, `__init__` 처럼 **뒤에도** 밑줄 두 개가 있으면 특별 메서드라 private 이 아니에요.')])

L.spot('실행하면 **오류**가 나는 줄은?', '''\
class Timer:
    def __init__(self):
        self.__total_time = 0
    def add(self, m):
        self.__total_time += m

t = Timer()
t.add(30)
t.add(15)
print(t.__total_time)''', 10,
    '클래스 안(5번 줄)에서 `self.__total_time` 을 쓰는 건 괜찮아요. 10번 줄은 **클래스 밖**에서 private 속성에 접근해 **AttributeError**. getter 메서드를 만들어 `t.get_total_time()` 으로 읽어야 해요.',
    error_line=10)

L.explain('AttributeError 가 나는 진짜 이유: 이름 바꾸기',
    [T('파이썬은 클래스 안에서 `__total_time` 이라고 쓴 이름을 몰래 **`_Timer__total_time`** 으로 바꿔 저장해요(name mangling).\n'
       '그래서 밖에서 `t.__total_time` 을 찾으면 그런 이름의 속성이 **없어서** AttributeError 가 나요.'),
     CODE('class Timer:\n    def __init__(self):\n        self.__total_time = 45\n\nt = Timer()\nprint(t.__dict__)          # 실제 저장된 속성 이름\nprint(t._Timer__total_time)', '진짜 이름 확인'),
     WARN('`_Timer__total_time` 으로 억지로 꺼낼 수는 있지만 **하면 안 되는 방법**이에요. 캡슐화를 깨뜨려요.')],
    [T('함정 하나 더! 밖에서 `t.__total_time = 100` 처럼 **대입**하면 오류가 안 나요.\n'
       '이건 private 속성을 바꾼 게 아니라 `__total_time` 이라는 **새 공개 속성**을 하나 만든 것뿐이에요.'),
     CODE('class Timer:\n    def __init__(self):\n        self.__total_time = 45\n    def get(self):\n        return self.__total_time\n\nt = Timer()\nt.__total_time = 100\nprint(t.get(), t.__total_time)', '대입은 새 속성을 만들어요'),
     EXAM('2024·2025년 연속 서술형: "private 속성에 접근하면 왜 AttributeError 가 나는가" → **이름이 _클래스명__속성 으로 바뀌어 저장되므로 밖에서는 그 이름으로 찾을 수 없다.**')])

L.output('출력은?', '''\
class Locker:
    def __init__(self, pw):
        self.__pw = pw
    def check(self, guess):
        return guess == self.__pw

k = Locker("1234")
k.__pw = "0000"
print(k.check("0000"))
print(k.check("1234"))
try:
    print(Locker("9").__pw)
except AttributeError:
    print("접근 불가")''',
    '`k.__pw = "0000"` 은 새 공개 속성을 만들 뿐 진짜 비밀번호(`_Locker__pw`)는 "1234" 그대로예요. 새 Locker 에는 공개 `__pw` 가 없으니 AttributeError.\n\n```\n{out}\n```')

L.explain('getter 와 setter',
    [T('private 속성은 **getter**(읽기 메서드)와 **setter**(바꾸기 메서드)로 다뤄요.\n'
       'setter 안에서 **값을 검사**하는 것이 캡슐화의 핵심이에요.'),
     CODE('''\
class Student:
    def __init__(self, name, score):
        self.__name = name
        self.__score = 0
        self.set_score(score)          # 생성할 때도 검사

    def get_score(self):               # getter
        return self.__score

    def set_score(self, s):            # setter
        if 0 <= s <= 100:
            self.__score = s
        else:
            print("잘못된 점수:", s)

st = Student("다인", 88)
st.set_score(150)
st.set_score(95)
print(st.get_score())''', 'getter / setter')],
    [T('파이썬에는 `@property` 로 getter 를 속성처럼 쓰는 방법도 있지만, 시험에서는 `get_…()`, `set_…()` 메서드 형태가 주로 나와요.'),
     TIP('getter 만 있고 setter 가 없으면 **읽기 전용** 속성이 돼요. 잔액처럼 입금·출금 메서드로만 바뀌어야 하는 값에 좋아요.')])

L.fill('결제 금액이 잔액 이하일 때만 차감하는 메서드와 getter 를 완성하세요.', '''\
class Pay:
    def __init__(self, money):
        self.__money = money
    def pay(self, amount):
        if amount <= self.___:
            self.__money -= amount
    def get_money(self):
        return ___

p = Pay(5000)
p.pay(7000)
p.pay(1500)
print(p.get_money())''', [['__money'], ['self.__money']],
    '클래스 안에서는 `self.__money` 로 private 속성을 그대로 써요. 7000 은 잔액보다 커서 결제 안 되고, 1500 만 빠져 3500.',
    expect='3500')

L.choice('private 속성 `self.__balance` 에 대한 설명으로 **틀린** 것은?',
    ['클래스 안의 메서드에서는 self.__balance 로 쓸 수 있다', '클래스 밖에서 obj.__balance 를 읽으면 AttributeError 가 난다',
     '밖에서 obj.__balance = 0 을 하면 private 값이 0 으로 바뀐다', '실제로는 _클래스명__balance 라는 이름으로 저장된다'], 3,
    '밖에서 대입하면 **새 공개 속성**이 생길 뿐, 진짜 private 값(`_클래스명__balance`)은 그대로예요.')

L.bucket('`class Box:` 안에 `self.__secret = 7` 이 있고 `b = Box()` 일 때, 각 코드의 결과를 분류하세요.', ['정상 실행', 'AttributeError'],
    [['메서드 안의 return self.__secret', 1], ['클래스 밖 print(b.__secret)', 2], ['클래스 밖 b.get_secret() (getter)', 1],
     ['클래스 밖 print(b._Box__secret)', 1], ['클래스 밖 b.__secret = 0 (대입)', 1]],
    '밖에서 **읽기**만 AttributeError. `_Box__secret` 은 진짜 이름이라 되지만 쓰면 안 되는 방법, 밖에서 **대입**은 새 공개 속성을 만들 뿐 오류가 아니에요.')

L.order('점수를 private 로 저장하고 getter/setter 로 다루는 코드를 순서대로 놓으세요.',
    ['class Score:', '    def __init__(self):', '        self.__v = 0', '    def set_v(self, v):', '        if 0 <= v <= 100:',
     '            self.__v = v', '    def get_v(self):', '        return self.__v', 's = Score()', 's.set_v(120)', 's.set_v(80)', 'print(s.get_v())'],
    'setter 에서 범위를 검사해 120 은 무시되고 80 만 저장돼요. 출력은 80.',
    check=True, expect='80')

L.short('`class Timer:` 안에서 `self.__total = 0` 으로 만든 속성은 실제로 어떤 이름으로 저장될까요?', '_Timer__total',
    '파이썬이 `_클래스명__속성` 으로 이름을 바꿔요(name mangling). 그래서 밖에서 `__total` 로는 못 찾아요.',
    check_code='class Timer:\n    def __init__(self):\n        self.__total = 0\nprint(list(Timer().__dict__)[0])')

L.practice('[기출유사] 간편결제 카드',
'''첫 줄에 `이름 처음잔액`, 둘째 줄에 명령 수 N, 다음 N 줄에 `충전 금액`, `결제 금액`, `조회` 명령이 주어져요.

**[조건]**
- `PayCard` 클래스의 잔액은 **private** `self.__balance` 로 저장하고, 밖에서는 `get_balance()` 로만 읽어요.
- `charge(amount)`: 0 이하면 `충전 실패`, 아니면 더하고 `충전: 금액원`
- `pay(amount)`: 잔액보다 크면 `결제 실패: 잔액 부족`, 아니면 빼고 `결제: 금액원`
- `조회` 는 `잔액: 금액원` (getter 사용). 마지막 줄 `print(card)` → `이름 카드 (잔액 금액원)`

{ex}

{ex2}''',
'''class PayCard:
    def __init__(self, owner, balance):
        self.owner = owner
        self.__balance = balance
    # get_balance, charge, pay, __str__ 을 만드세요

name, money = input().split()
card = PayCard(name, int(money))
n = int(input())
for _ in range(n):
    cmd = input().split()
    # 명령 처리

print(card)''',
'''class PayCard:
    def __init__(self, owner, balance):
        self.owner = owner
        self.__balance = balance          # private 속성

    def get_balance(self):                # getter
        return self.__balance

    def charge(self, amount):
        if amount <= 0:                   # 검사 후 변경
            print("충전 실패")
            return
        self.__balance += amount
        print(f"충전: {amount}원")

    def pay(self, amount):
        if amount > self.__balance:
            print("결제 실패: 잔액 부족")
            return
        self.__balance -= amount
        print(f"결제: {amount}원")

    def __str__(self):
        return f"{self.owner} 카드 (잔액 {self.__balance}원)"

name, money = input().split()
card = PayCard(name, int(money))
n = int(input())
for _ in range(n):
    cmd = input().split()
    if cmd[0] == "충전":
        card.charge(int(cmd[1]))
    elif cmd[0] == "결제":
        card.pay(int(cmd[1]))
    else:
        print(f"잔액: {card.get_balance()}원")   # 밖에서는 getter 로만

print(card)''',
    ['민지 10000\n4\n결제 3000\n충전 -500\n결제 8000\n조회', '준 0\n3\n충전 2000\n결제 2000\n조회'],
    ['a 0\n1\n조회', 'b 100\n2\n충전 0\n결제 101', 'c 5\n3\n결제 5\n충전 1\n조회'],
    ['`self.__balance` 는 클래스 안의 모든 메서드에서 그대로 써요.',
     'charge: `if amount <= 0:` 이면 실패 출력 후 `return`',
     '조회는 클래스 밖이니까 `card.get_balance()` — `card.__balance` 로 쓰면 AttributeError!'],
    'private 속성은 메서드 안에서만 바뀌고, 메서드마다 **검사**(0 이하 충전, 잔액 초과 결제)를 해서 잘못된 값이 들어가는 것을 막아요. 이것이 캡슐화의 목적이에요.')

L.practice('[기출유사] 공부 시간 기록기',
'''첫 줄에 기록 수 N, 다음 N 줄에 `과목 분` 이 주어져요.

**[조건]**
- `StudyLog` 클래스: private `__total_time`(전체 분), private `__by_subject`(과목별 분 딕셔너리)
- `add(subject, minutes)`: minutes 가 0 이하이면 `raise ValueError`. 바깥에서 잡아 `무시: 과목 분` 출력.
- 분이 정수가 아니어도 ValueError 이므로 같은 메시지로 처리해요.
- getter `get_total_time()`, `get_subject(subject)`(없으면 0)
- 출력: 과목별로(처음 나온 순서) `과목 X시간 Y분`, 마지막 줄 `합계 X시간 Y분`

{ex}

{ex2}''',
'''class StudyLog:
    def __init__(self):
        self.__total_time = 0
        self.__by_subject = {}
    # add, get_total_time, get_subject 를 만드세요

log = StudyLog()
order = []
n = int(input())
for _ in range(n):
    subject, m = input().split()
    # try / except 로 기록하세요
''',
'''class StudyLog:
    def __init__(self):
        self.__total_time = 0
        self.__by_subject = {}

    def add(self, subject, minutes):
        if minutes <= 0:
            raise ValueError("시간은 양수")       # 잘못된 값은 예외로 거부
        self.__total_time += minutes
        self.__by_subject[subject] = self.__by_subject.get(subject, 0) + minutes

    def get_total_time(self):
        return self.__total_time

    def get_subject(self, subject):
        return self.__by_subject.get(subject, 0)

def hm(m):
    return f"{m // 60}시간 {m % 60}분"

log = StudyLog()
order = []                                       # 과목이 처음 나온 순서
n = int(input())
for _ in range(n):
    subject, m = input().split()
    try:
        log.add(subject, int(m))                 # int 변환 실패도 ValueError
        if subject not in order:
            order.append(subject)
    except ValueError:
        print("무시:", subject, m)
for s in order:
    print(s, hm(log.get_subject(s)))
print("합계", hm(log.get_total_time()))''',
    ['4\n수학 50\n정보 90\n수학 40\n국어 -10', '2\n영어 125\n영어 abc'], ['1\n정보 1', '3\nA 0\nB 60\nA 59', '2\n물리 600\n화학 61'],
    ['add 안에서 `if minutes <= 0: raise ValueError(...)`',
     '과목별 누적: `self.__by_subject[subject] = self.__by_subject.get(subject, 0) + minutes`',
     '시간 표시: `f"{m // 60}시간 {m % 60}분"`, 순서는 별도 리스트 `order` 에 처음 나올 때만 추가'],
    'private 속성은 add 를 거쳐서만 바뀌므로 음수 시간이 섞일 수 없어요. 밖에서는 getter 로만 읽어요. `int("abc")` 도 ValueError 라 같은 except 에서 처리돼요.')

L.essay('`acc = Account(1000)` 에서 잔액을 private 속성 `self.__balance` 로 저장했어요. 클래스 밖에서 `print(acc.__balance)` 를 실행하면 어떤 오류가 **왜** 나는지 쓰고, 올바르게 잔액을 읽는 방법을 서술하세요.',
    'AttributeError 가 발생한다. 클래스 안에서 앞에 밑줄 두 개를 붙인 속성 __balance 는 파이썬이 이름을 _Account__balance 로 바꿔 저장(name mangling)하기 때문에, 클래스 밖에서 __balance 라는 이름으로 찾으면 그런 속성이 없다. 잔액을 돌려주는 getter 메서드 get_balance() 를 만들어 acc.get_balance() 로 읽어야 한다.',
    ['AttributeError', '__ 가 붙은 private 속성', '이름이 _Account__balance 로 바뀌어 저장', 'getter 메서드로 읽기'])

# =====================================================================
L = C.lesson('γ-12 연산자 오버로딩: __add__ · __sub__ · __str__', 25,
'''- `a + b` 는 사실 `a.__add__(b)`, `a - b` 는 `a.__sub__(b)` 를 부르는 거예요.
- 내 클래스에 `__add__` 를 만들면 객체끼리 `+` 를 쓸 수 있어요 → **새 객체를 return**.
- `__str__` 과 함께 쓰면 `print(v1 + v2)` 가 예쁘게 나와요.
- 값 범위 제한(RGB 0~255): `max(0, min(255, 값))`.
- `__eq__` 가 없으면 `==` 는 같은 객체인지만 봐요.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간: private 속성 `self.__x` 는 밖에서 접근하면 AttributeError(이름이 `_클래스__x` 로 바뀜), getter/setter 로 다뤄요.'),
     REVEAL('밖에서 `obj.__x = 5` 를 하면 private 값이 바뀔까?', '아니요. `__x` 라는 새 공개 속성이 생길 뿐 진짜 값(`_클래스__x`)은 그대로예요.')])
L.output('복습: 출력은?', 'class S:\n    def __init__(self):\n        self.__v = 1\n    def up(self):\n        self.__v += 1\n        return self.__v\n\ns = S()\ns.up()\nprint(s.up())',
    '클래스 안에서는 private 속성을 자유롭게 써요. 두 번 올려 {out}', review=True)

L.explain('+ 가 하는 일의 정체',
    [T('`3 + 4`, `"a" + "b"`, `[1] + [2]` — 같은 `+` 인데 하는 일이 달라요.\n'
       '파이썬은 `a + b` 를 만나면 **`a.__add__(b)`** 를 불러요. 자료형마다 `__add__` 가 다르게 만들어져 있는 거예요.'),
     CODE('print(3 + 4, (3).__add__(4))\nprint("py".__add__("thon"))\nprint([1].__add__([2]))', '+ 는 __add__'),
     KEY('**연산자 오버로딩** = 내가 만든 클래스에 `__add__` 같은 특별 메서드를 정의해서 `+`, `-` 등을 쓸 수 있게 하는 것.')],
    [T('자주 나오는 특별 메서드를 카드로 외워요.'),
     FLIP(['a + b', 'a.__add__(b)'], ['a - b', 'a.__sub__(b)'], ['a * b', 'a.__mul__(b)'],
          ['a == b', 'a.__eq__(b)'], ['a < b', 'a.__lt__(b)'], ['print(a), str(a)', 'a.__str__()'], ['len(a)', 'a.__len__()'])])

L.explain('Vector2D 만들기',
    [T('2024년 15점 문항 소재예요. 2차원 벡터 `(x, y)` 끼리 더하고 빼요.\n'
       '`__add__(self, other)` 에서 **self 는 + 왼쪽, other 는 + 오른쪽** 객체예요.'),
     CODE('''\
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

a = Vector2D(3, 5)
b = Vector2D(1, 2)
print(a + b)
print(a - b)
print(a + b + b)''', 'Vector2D')],
    [T('`__add__` 는 원래 객체를 바꾸지 않고 **새 객체를 만들어 return** 해요. 그래서 `a + b + b` 처럼 이어서 쓸 수 있어요.'),
     CMP(side('새 객체 return', 'a, b 는 그대로. 결과가 새 Vector2D.', '', 'good'),
         side('self 를 바꾸고 return 없음', '`a + b` 의 결과가 None! `a + b + b` 는 None + b 라서 TypeError.', '', 'bad'))])

L.output('출력은?', '''\
class Money:
    def __init__(self, won):
        self.won = won
    def __add__(self, other):
        return Money(self.won + other.won)
    def __sub__(self, other):
        return Money(self.won - other.won)
    def __str__(self):
        return f"{self.won}원"

a = Money(5000)
b = Money(1200)
c = a - b + b - b
print(c)
print(a, b)''',
    '왼쪽부터 차례로 계산: 5000-1200=3800 → +1200=5000 → -1200=3800. a 와 b 는 바뀌지 않아요.\n\n```\n{out}\n```')

L.spot('실행하면 **오류**가 나는 줄은?', '''\
class Point:
    def __init__(self, x):
        self.x = x
    def __add__(self, other):
        self.x += other.x

p = Point(1)
q = Point(2)
r = p + q
s = r + q''', 10,
    '`__add__` 가 아무것도 return 하지 않아 `r` 은 **None** 이에요. 10번 줄 `None + q` 에서 TypeError. `return Point(self.x + other.x)` 로 고쳐요.',
    error_line=10)

L.explain('범위가 있는 값: Color(RGB)',
    [T('2025년 12점 문항 소재: RGB 색 `(r, g, b)` 를 더하고 빼는데, 각 값은 **0~255** 를 넘으면 안 돼요.\n'
       '`max(0, min(255, 값))` 한 줄이면 0 아래는 0, 255 위는 255 로 **잘라내요**(clamp).'),
     CODE('''\
def clamp(v):
    return max(0, min(255, v))

print(clamp(300), clamp(-20), clamp(128))''', 'clamp 함수'),
     TIP('`min(255, v)` 가 먼저 위쪽을 자르고, `max(0, …)` 가 아래쪽을 잘라요. 순서를 바꿔 `min(255, max(0, v))` 도 같아요.')],
    [T('클래스 안에서는 세 값을 한 번에 처리하려고 **컴프리헨션 + zip** 을 써도 좋아요.'),
     CODE('''\
class Color:
    def __init__(self, r, g, b):
        self.rgb = [max(0, min(255, v)) for v in (r, g, b)]
    def __add__(self, other):
        return Color(*[a + b for a, b in zip(self.rgb, other.rgb)])
    def __str__(self):
        return "RGB(" + ", ".join(map(str, self.rgb)) + ")"

print(Color(200, 100, 0) + Color(100, 100, 50))''', '컴프리헨션으로 Color'),
     THINK('`Color(*리스트)` 의 `*` 는 리스트를 풀어서 r, g, b 세 인자로 넘겨요. β 에서 배운 `*args` 의 반대 방향이에요.')])

L.fill('두 색을 뺄 때 음수는 0 이 되도록 `__sub__` 를 완성하세요.', '''\
class Color:
    def __init__(self, r, g, b):
        self.r, self.g, self.b = r, g, b
    def __sub__(self, other):
        return Color(___(0, self.r - other.r),
                     max(0, self.g - other.g),
                     max(0, self.b - other.b))
    def __str__(self):
        return f"({self.r}, {self.g}, {self.b})"

print(Color(100, 50, 30) ___ Color(40, 80, 30))''', [['max'], ['-']],
    '`max(0, 음수)` 는 0 이에요. `-` 연산자가 `__sub__` 를 불러요. 결과는 `(60, 0, 0)`.', expect='(60, 0, 0)')

L.explain('== 도 오버로딩: __eq__',
    [T('`__eq__` 가 없으면 내 객체끼리 `==` 는 **같은 객체일 때만** True 예요(γ-08 의 is 처럼).\n'
       '값이 같으면 같다고 하고 싶으면 `__eq__` 를 만들어 **True/False 를 return** 해요.'),
     TABS(('__eq__ 없음', '', 'class V:\n    def __init__(self, x):\n        self.x = x\n\nprint(V(1) == V(1))'),
          ('__eq__ 있음', '', 'class V:\n    def __init__(self, x):\n        self.x = x\n    def __eq__(self, other):\n        return self.x == other.x\n\nprint(V(1) == V(1), V(1) is V(1))'))])

L.match('코드와 실제로 불리는 메서드를 이어 보세요.',
    [['v1 + v2', 'v1.__add__(v2)'], ['v2 - v1', 'v2.__sub__(v1)'], ['print(v1)', 'v1.__str__()'],
     ['v1 == v2', 'v1.__eq__(v2)'], ['Vector2D(1, 2)', '__init__(새객체, 1, 2)']],
    '연산자의 **왼쪽 객체**의 메서드가 불리고, 오른쪽 객체가 other 로 들어가요. 그래서 `v2 - v1` 은 v2 의 `__sub__`.')

L.ox('`a + b` 를 실행하면 `b.__add__(a)` 가 불리고, 매개변수 other 에는 a 가 들어간다.', False,
     '**왼쪽 객체**의 메서드가 불려요: `a.__add__(b)`. self 가 a, other 가 b 예요.')

L.short('`a * b` 를 실행하면 파이썬이 부르는 특별 메서드 이름은? (예: __add__)', '__mul__',
    '`*` 는 `__mul__`, `/` 는 `__truediv__`, `//` 는 `__floordiv__` 예요. 시험엔 주로 `__add__`, `__sub__` 가 나와요.',
    check_code='print((3).__mul__.__name__)')

L.practice('[기출유사] RGB 색 섞기',
'''두 줄에 걸쳐 색 A, B 의 `R G B` 값이 주어져요.

**[조건]**
- `Color` 클래스에 `__init__`, `__add__`, `__sub__`, `__str__` 을 만들어요.
- `+` 는 각 값을 더하되 **255 를 넘으면 255**, `-` 는 각 값을 빼되 **0 보다 작으면 0**.
- `__str__` 은 `(R, G, B)` 형식.
- 출력 세 줄: `A+B = …`, `A-B = …`, `B-A = …`

{ex}

{ex2}''',
'''class Color:
    def __init__(self, r, g, b):
        self.r, self.g, self.b = r, g, b
    # __add__, __sub__, __str__ 을 만드세요

a = Color(*map(int, input().split()))
b = Color(*map(int, input().split()))
''',
'''class Color:
    def __init__(self, r, g, b):
        self.r, self.g, self.b = r, g, b

    def __add__(self, other):
        return Color(min(255, self.r + other.r),      # 255 넘으면 255
                     min(255, self.g + other.g),
                     min(255, self.b + other.b))

    def __sub__(self, other):
        return Color(max(0, self.r - other.r),        # 0 보다 작으면 0
                     max(0, self.g - other.g),
                     max(0, self.b - other.b))

    def __str__(self):
        return f"({self.r}, {self.g}, {self.b})"

a = Color(*map(int, input().split()))
b = Color(*map(int, input().split()))
print("A+B =", a + b)
print("A-B =", a - b)
print("B-A =", b - a)''',
    ['200 100 50\n100 100 100', '0 0 0\n255 255 255'], ['10 20 30\n10 20 30', '255 0 128\n1 1 128', '128 128 128\n127 129 128'],
    ['`__add__(self, other)` 안에서 `self.r + other.r` 처럼 같은 칸끼리 계산해요.',
     '더하기는 `min(255, …)`, 빼기는 `max(0, …)` 로 범위를 잘라요.',
     '반드시 `return Color(...)` 로 **새 객체**를 돌려줘야 print 에서 `__str__` 이 쓰여요.'],
    '연산자의 왼쪽이 self, 오른쪽이 other 예요. 그래서 `a - b` 와 `b - a` 는 다른 결과가 나와요. 결과를 새 Color 로 돌려주면 그대로 print 할 수 있어요.')

L.practice('[기출유사] 시각 더하기 (Time 클래스)',
'''첫 줄에 지금 시각 `시 분`, 둘째 줄에 걸리는 시간 `시 분`, 셋째 줄에 비교할 시각 `시 분` 이 주어져요.

**[조건]**
- `Time(h, m)` 클래스: 만들 때 분이 60 이상이면 시로 올리고, 시는 24 로 나눈 나머지로 저장해요.
- `__add__`: 두 Time 을 더한 **새 Time** / `__sub__`: 두 시각의 차이를 **분(정수)** 으로 돌려줘요(왼쪽 − 오른쪽, 음수 가능).
- `__str__`: `HH:MM` (두 자리, 예 `07:05`) — `f"{h:02d}:{m:02d}"`
- 출력: `도착: HH:MM`, `차이: 분` (도착 − 비교 시각)

{ex}

{ex2}''',
'''class Time:
    def __init__(self, h, m):
        pass
    # __add__, __sub__, __str__

now = Time(*map(int, input().split()))
dur = Time(*map(int, input().split()))
other = Time(*map(int, input().split()))
''',
'''class Time:
    def __init__(self, h, m):
        total = h * 60 + m                  # 전부 분으로 바꿔서
        self.h = (total // 60) % 24         # 시는 24 로 나눈 나머지
        self.m = total % 60

    def __add__(self, other):
        return Time(self.h + other.h, self.m + other.m)   # 올림 처리는 __init__ 이 해 줌

    def __sub__(self, other):
        return (self.h * 60 + self.m) - (other.h * 60 + other.m)   # 분 차이(정수)

    def __str__(self):
        return f"{self.h:02d}:{self.m:02d}"

now = Time(*map(int, input().split()))
dur = Time(*map(int, input().split()))
other = Time(*map(int, input().split()))
arrive = now + dur
print("도착:", arrive)
print("차이:", arrive - other)''',
    ['9 40\n1 35\n11 0', '23 50\n0 20\n0 0'], ['0 0\n0 0\n0 0', '7 5\n2 55\n12 0', '22 59\n1 1\n0 30'],
    ['생성자에서 `total = h * 60 + m` 으로 분으로 바꾼 뒤 `//`, `%` 로 시·분을 다시 구해요.',
     '`__add__` 는 `return Time(self.h + other.h, self.m + other.m)` — 올림은 생성자가 해 줘요.',
     '`__sub__` 는 객체가 아니라 **정수**를 돌려줘도 돼요: 두 시각을 분으로 바꿔 빼기.'],
    '정리하는 일을 생성자에 맡기면 `__add__` 가 아주 짧아져요. 연산자 메서드는 꼭 같은 클래스의 객체를 돌려줄 필요는 없어요(`__sub__` 는 정수). 23:50 + 0:20 = 24:10 → 00:10.')

L.essay('`Vector2D` 의 `__add__` 를 `self.x += other.x; self.y += other.y` 만 하고 return 없이 만들었어요. `c = a + b` 후 `print(c)` 를 하면 어떻게 되는지, 그리고 이 방식의 **문제점 두 가지**를 서술하세요.',
    'return 이 없으므로 a + b 의 결과는 None 이 되어 c 에 None 이 저장되고 print(c) 는 None 을 출력한다. 문제점은 첫째, 결과를 돌려주지 않으므로 c 로 결과를 쓸 수 없고 a + b + b 처럼 이어 쓰면 None + b 가 되어 TypeError 가 난다. 둘째, 더하기를 했을 뿐인데 원래 객체 a 의 값이 바뀌어 버린다. 새 Vector2D 객체를 만들어 return 해야 한다.',
    ['결과가 None', '이어서 더하면 TypeError', '원래 객체 a 가 바뀜', '새 객체를 만들어 return 해야 함'])

# =====================================================================
L = C.lesson('γ-13 numpy 기초: 배열 · shape · 통계 · 조건 개수', 25,
'''- `import numpy as np` → `np.array([...])` 로 배열. **같은 자료형**만 담고, 연산이 **칸마다(원소별)** 일어나요.
- `a.shape` 모양(행, 열), `a.sum()`, `a.mean()`, `a.max()`, `a.min()`
- `np.ones(n)`·`np.zeros(n)` (실수 1.·0.), `np.arange(n)` (0~n-1), `.reshape(행, 열)` — 칸 수가 맞아야 해요.
- `a > 0` 은 True/False 배열 → `(a > 0).sum()` 이 **조건에 맞는 개수**, `a[a > 0]` 은 그 값들.
- 이 사이트에서 numpy 코드를 **▶ 실행**할 수 있어요. 먼저 결과를 예측하고, 실행해서 맞는지 확인해요.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간: `a + b` 는 `a.__add__(b)`, 새 객체를 return, 범위 제한은 `max(0, min(255, v))`.\n'
       '오늘 배울 numpy 배열도 사실 `__add__` 가 **칸마다 더하도록** 만들어진 클래스예요!'),
     REVEAL_RUN('`[1, 2] + [3, 4]` (리스트) 의 결과는?', 'print([1, 2] + [3, 4])')])
L.output('복습: 출력은?', 'class N:\n    def __init__(self, v):\n        self.v = v\n    def __add__(self, o):\n        return N(self.v * 10 + o.v)\n    def __str__(self):\n        return str(self.v)\n\nprint(N(1) + N(2) + N(3))',
    '(1×10+2)=12 → (12×10+3)=123 → {out}', review=True)

L.explain('numpy 배열은 리스트와 무엇이 다를까',
    [T('**numpy** 는 숫자 계산을 빠르게 해 주는 외부 모듈이에요. 보통 `import numpy as np` 로 불러요(γ-06 의 **as**!).\n'
       '배열은 리스트처럼 보이지만 **연산이 칸마다** 일어나요.'),
     CMP(side('리스트', '`[1, 2, 3] * 2` → `[1, 2, 3, 1, 2, 3]` (반복)\n`[1, 2] + [3, 4]` → `[1, 2, 3, 4]` (이어 붙이기)\n`[1, 2] + 1` → TypeError', '', 'bad'),
         side('numpy 배열', '`np.array([1, 2, 3]) * 2` → `[2 4 6]` (칸마다)\n`np.array([1, 2]) + np.array([3, 4])` → `[4 6]`\n`np.array([1, 2]) + 1` → `[2 3]`', '', 'good'))],
    [T('직접 확인해 봐요. 결과를 먼저 머릿속으로 예측한 뒤 **▶ 실행**으로 맞춰 보세요. (정답 보기로도 확인할 수 있어요)'),
     CODE('import numpy as np\na = np.array([1, 2, 3])\nprint(a * 2)\nprint(a + 10)\nprint(type(a))', 'numpy 첫걸음', run_=False),
     REVEAL_RUN('위 코드의 실행 결과는?', 'import numpy as np\na = np.array([1, 2, 3])\nprint(a * 2)\nprint(a + 10)\nprint(type(a))',
                '배열을 print 하면 **쉼표 없이** 공백으로 구분해 보여 줘요.')])

L.output('출력은? (numpy 배열은 쉼표 없이 출력돼요)', '''\
import numpy as np
a = np.array([4, 7, 3])
b = np.array([1, 1, 2])
print(a - b)
print(a * b)
print([4, 7, 3] * 2)''',
    '배열끼리는 **같은 칸끼리** 빼고 곱해요. 마지막 줄은 그냥 리스트라 두 번 반복돼요.\n\n```\n{out}\n```')

L.explain('모양(shape)과 2차원 배열',
    [T('리스트 안에 리스트를 넣어 만들면 **2차원 배열**(표)이 돼요.\n'
       '`a.shape` 는 `(행 수, 열 수)` 튜플, `a.ndim` 은 차원 수, `a.size` 는 전체 칸 수예요.'),
     CODE('import numpy as np\na = np.array([[90, 80, 70],\n              [60, 85, 95]])\nprint(a)\nprint(a.shape, a.ndim, a.size)\nprint(a[1, 2], a[0])', '2차원 배열', run_=False),
     REVEAL_RUN('실행 결과는?', 'import numpy as np\na = np.array([[90, 80, 70],\n              [60, 85, 95]])\nprint(a)\nprint(a.shape, a.ndim, a.size)\nprint(a[1, 2], a[0])',
                '`a[1, 2]` 는 1행 2열(0부터 셈). 리스트의 `a[1][2]` 와 같은 칸이에요.')],
    [T('통계 함수는 메서드로 바로 불러요. 2025년 15점 문항에 `shape`·`mean`·`max` 가 나왔어요.'),
     CODE('import numpy as np\na = np.array([[90, 80, 70],\n              [60, 85, 95]])\nprint(a.sum(), a.max(), a.min())\nprint(a.mean())\nprint(a.max(axis=1))   # 행마다 최댓값', '통계 메서드', run_=False),
     TIP('`axis=0` 은 **세로(열마다)**, `axis=1` 은 **가로(행마다)** 계산이에요. 기본편에서는 axis 없이 전체 계산을 확실히!')])

L.output('출력은?', '''\
import numpy as np
s = np.array([[3, 9], [5, 1], [7, 5]])
print(s.shape)
print(s.sum(), s.max())
print(s.mean())''',
    '3행 2열이라 shape 는 (3, 2). 합 30, 최댓값 9, 평균 30 / 6 = 5.0.\n\n```\n{out}\n```')

L.explain('ones · zeros · arange · reshape',
    [T('배열을 **만드는** 함수들이에요.\n'
       '- `np.ones(3)` → `[1. 1. 1.]` (실수!), `np.zeros((2, 3))` → 0 으로 찬 2×3\n'
       '- `np.arange(6)` → `[0 1 2 3 4 5]` (range 와 같은 규칙)\n'
       '- `.reshape(2, 3)` → 같은 값을 2행 3열로 **다시 배치**'),
     CODE('import numpy as np\nprint(np.ones(3))\nprint(np.ones((2, 2), dtype=int))\nprint(np.arange(1, 7).reshape(2, 3))', '배열 만들기', run_=False),
     REVEAL_RUN('실행 결과는?', 'import numpy as np\nprint(np.ones(3))\nprint(np.ones((2, 2), dtype=int))\nprint(np.arange(1, 7).reshape(2, 3))',
                '`np.ones` 의 기본 자료형은 실수라 `1.` 로 보여요. `dtype=int` 를 주면 정수.')],
    [T('`reshape` 는 **칸 수가 같아야** 해요. 6칸짜리를 4×2(8칸)로 바꾸면 ValueError!'),
     WARN('`np.ones(3) * 5` 는 `[5. 5. 5.]` — 실수 배열에 곱하면 결과도 실수예요. 출력에 점(.)이 붙는지 꼭 확인!')])

L.spot('실행하면 **오류**가 나는 줄은?', '''\
import numpy as np
a = np.arange(12)
b = a.reshape(3, 4)
c = b.reshape(2, 6)
d = c.reshape(5, 2)
print(d)''', 5,
    '12칸은 3×4, 2×6 으로는 바꿀 수 있지만 5×2 = 10칸으로는 못 바꿔요 → **ValueError**(cannot reshape array of size 12 into shape (5,2)).',
    error_line=5)

L.explain('조건으로 세기와 고르기',
    [T('`a > 0` 처럼 배열에 비교를 하면 **칸마다 True/False** 인 배열이 나와요.\n'
       'True 는 1, False 는 0 으로 계산되니 `(a > 0).sum()` 이 **조건을 만족하는 개수**예요.\n'
       '`a[a > 0]` 처럼 대괄호에 넣으면 **조건에 맞는 값만** 골라내요.'),
     CODE('import numpy as np\nhp = np.array([30, -5, 0, 12, -1])\nprint(hp > 0)\nprint((hp <= 0).sum())\nprint(hp[hp > 0])\nprint(hp[hp > 0].sum())', '조건 개수', run_=False),
     REVEAL_RUN('실행 결과는?', 'import numpy as np\nhp = np.array([30, -5, 0, 12, -1])\nprint(hp > 0)\nprint((hp <= 0).sum())\nprint(hp[hp > 0])\nprint(hp[hp > 0].sum())')],
    [T('2025년 12점 문항: `ones` 로 체력 배열을 만들고 `arange().reshape()` 로 만든 피해량을 **빼서**, 합계와 **0 이하인 칸의 개수**를 구했어요. 아래 문제로 연습해요.'),
     EXAM('순수 파이썬이라면 `sum(1 for x in a if x <= 0)` 을, numpy 는 `(a <= 0).sum()` 한 줄로 해요. 둘 다 쓸 수 있게! 실습에서는 진짜 numpy 로 풀어 봐요.')])

L.output('출력은?', '''\
import numpy as np
hp = np.ones((2, 3), dtype=int) * 5
dmg = np.arange(6).reshape(2, 3)
left = hp - dmg
print(left)
print(left.sum())
print((left <= 0).sum())''',
    'hp 는 모두 5, dmg 는 [[0 1 2] [3 4 5]]. 칸마다 빼면 [[5 4 3] [2 1 0]]. 합 15, 0 이하는 0 한 칸. 2차원 배열은 행마다 줄을 바꾸고 둘째 줄 앞에 공백 한 칸이 붙어요. (음수나 두 자리 수가 섞이면 numpy 가 칸 너비를 맞추느라 공백을 더 넣어요)\n\n```\n{out}\n```')

L.bucket('다음 중 결과를 분류하세요. (`a = np.array([1, 2, 3])`)', ['칸마다 계산된 배열', '리스트처럼 이어 붙이거나 반복', '오류'],
    [['a + 1', 1], ['a * a', 1], ['[1, 2, 3] * 2', 2], ['[1, 2] + [3]', 2], ['[1, 2, 3] + 1', 3], ['np.arange(6).reshape(4, 2)', 3], ['a > 1', 1]],
    '배열은 칸마다 계산, 리스트의 `+`·`*` 는 이어 붙이기·반복. 리스트 + 정수, 칸 수가 안 맞는 reshape 는 오류예요.')

L.choice('`np.arange(2, 11, 2)` 의 결과는?', ['[2 4 6 8 10]', '[2 4 6 8]', '[2 3 4 5 6 7 8 9 10]', '[0 2 4 6 8 10]'], 1,
    'range 와 같은 규칙: 2 부터 11 **직전**까지 2 씩 → 2, 4, 6, 8, 10.')

L.practice('[기출유사] 몬스터 체력판 (numpy)',
'''numpy 의 `ones` · `arange().reshape()` · 배열 빼기를 **진짜 numpy 로** 써 보는 문제예요.
한 줄에 `R C H` 가 주어져요. R행 C열 몬스터의 체력은 모두 H 이고, 칸마다 받은 피해는 **0, 1, 2, … 를 왼쪽 위부터 차례로** 채운 값이에요.

**[조건]**
- `import numpy as np` 를 쓰고, 체력은 `np.ones((R, C), dtype=int) * H`, 피해는 `np.arange(R * C).reshape(R, C)` 로 만들어요.
- 남은 체력 = 체력 배열 − 피해 배열 (배열끼리 **한 번에** 빼기)
- 행마다 값을 공백으로 이어 출력해요. (배열을 그대로 print 하지 말고 `tolist()` 로 바꿔 출력)
- 다음 줄 `합계: 값`, 마지막 줄 `쓰러짐: 개수` (남은 체력이 **0 이하**인 칸 수, `(배열 <= 0).sum()`)

{ex}

{ex2}''',
'''import numpy as np

r, c, h = map(int, input().split())
# hp, dmg 배열을 만들고 빼서 출력하세요
''',
'''import numpy as np

r, c, h = map(int, input().split())
hp = np.ones((r, c), dtype=int) * h          # 모든 칸이 h 인 r×c 배열
dmg = np.arange(r * c).reshape(r, c)         # 0, 1, 2, ... 를 행 순서로 채움
left = hp - dmg                              # 칸마다 빼기 (원소별 연산)
for row in left.tolist():                    # 배열 → 2차원 리스트
    print(" ".join(map(str, row)))
print("합계:", int(left.sum()))              # 전체 합
print("쓰러짐:", int((left <= 0).sum()))     # True 를 1 로 세어 개수''',
    ['2 3 4', '3 3 5'], ['1 1 0', '1 5 2', '4 2 10'],
    ['체력: `hp = np.ones((r, c), dtype=int) * h` — `dtype=int` 가 없으면 `4.0` 처럼 실수로 나와요.',
     '피해: `dmg = np.arange(r * c).reshape(r, c)`, 남은 체력: `left = hp - dmg`',
     '출력: `for row in left.tolist(): print(" ".join(map(str, row)))`, 개수는 `int((left <= 0).sum())`'],
    '`np.ones` 의 기본 자료형은 실수라 `dtype=int` 가 중요해요. `(left <= 0)` 은 True/False 배열이고 `.sum()` 은 True 를 1 로 세어 개수가 돼요. 순수 파이썬으로 하려면 `(i, j)` 칸의 피해가 `i * c + j` 라는 걸 이용해 이중 for 로 만들면 돼요 — reshape 가 "왼쪽 위부터 행 순서로 채운다" 는 뜻이에요.',
    libs=['numpy'])

L.practice('[기출유사] 성적 배열 통계 (numpy)',
'''첫 줄에 `행 열`(학생 수, 과목 수), 다음 줄들에 점수표가 주어져요. 점수표를 **numpy 배열**로 만들어 `shape`, `mean()`, `max()`, 조건 개수를 구해 보세요.

**[조건]**
- `import numpy as np` 를 쓰고 `a = np.array(점수표)` 로 2차원 배열을 만들어요.
- 첫째 줄: `shape: (행, 열)` — `a.shape` 를 그대로 print 한 모양
- 둘째 줄: `평균: 값` (`a.mean()` 을 `round(float(…), 2)`)
- 셋째 줄: `최고: 값` (`a.max()`)
- 넷째 줄: `평균 이상: 개수` (전체 평균 **이상**인 칸 수, `(a >= a.mean()).sum()`)
- 다섯째 줄: `학생별 최고: a b c` (행마다 최댓값 — `a.max(axis=1)`)

{ex}

{ex2}''',
'''import numpy as np

r, c = map(int, input().split())
scores = [list(map(int, input().split())) for _ in range(r)]
# a = np.array(scores) 로 만들고 통계를 출력하세요
''',
'''import numpy as np

r, c = map(int, input().split())
scores = [list(map(int, input().split())) for _ in range(r)]
a = np.array(scores)                                  # 2차원 배열
print("shape:", a.shape)                              # (행, 열) 튜플
print("평균:", round(float(a.mean()), 2))             # 전체 평균
print("최고:", int(a.max()))                          # 전체 최댓값
print("평균 이상:", int((a >= a.mean()).sum()))       # 조건을 만족하는 칸 수
print("학생별 최고:", " ".join(map(str, a.max(axis=1).tolist())))   # 행마다 최댓값''',
    ['2 3\n90 80 70\n60 85 95', '3 2\n10 20\n30 40\n50 60'], ['1 1\n77', '2 2\n0 0\n0 0', '2 4\n1 2 3 4\n100 0 50 49'],
    ['`a = np.array(scores)` 하면 `a.shape` 가 바로 `(r, c)` 예요.',
     '평균 이상은 반올림 **전** 값으로: `(a >= a.mean()).sum()`. 출력은 `int(...)` 로 감싸요.',
     '행마다 최댓값: `a.max(axis=1).tolist()` 를 `" ".join(map(str, ...))`'],
    '`axis=1` 은 가로(행마다) 계산이라 학생별 최고가 나와요. numpy 값은 `int()`·`float()`·`tolist()` 로 바꿔 찍으면 출력 모양이 깔끔해요. 순수 파이썬이라면 `flat = [v for row in scores for v in row]` 로 펼쳐 `sum(flat) / len(flat)`, `max(flat)`, `sum(1 for v in flat if v >= avg)` 로 같은 값을 구할 수 있어요.',
    libs=['numpy'])

L.essay('파이썬 리스트 `[1, 2, 3]` 과 numpy 배열 `np.array([1, 2, 3])` 에 각각 `* 2` 를 했을 때 결과가 어떻게 다른지 쓰고, 그 차이가 생기는 이유를 **연산자 오버로딩**과 연결해 서술하세요.',
    '리스트에 * 2 를 하면 리스트 전체가 두 번 반복된 [1, 2, 3, 1, 2, 3] 이 되고, numpy 배열에 * 2 를 하면 각 칸에 2 를 곱한 [2 4 6] 이 된다. * 연산자는 왼쪽 객체의 __mul__ 메서드를 호출하는데, list 클래스의 __mul__ 은 반복하도록, numpy 배열(ndarray) 클래스의 __mul__ 은 원소마다 곱하도록 서로 다르게 정의(오버로딩)되어 있기 때문이다.',
    ['리스트는 반복 [1, 2, 3, 1, 2, 3]', '배열은 칸마다 곱 [2 4 6]', '* 는 __mul__ 호출', '클래스마다 __mul__ 이 다르게 정의됨(오버로딩)'])

if __name__ == '__main__':
    C.save(sys.argv[1] if len(sys.argv) > 1 else '/tmp/gamma.json')
