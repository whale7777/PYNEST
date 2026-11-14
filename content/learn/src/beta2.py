import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lotc import *


def build(C):
    # =====================================================================
    L = C.lesson('β-03 리스트 컴프리헨션 + 한 줄 입력', 25,
'''- `[식 for x in 반복 if 조건]` = for + if + append 를 **한 줄**로.
- 거르기 `if` 는 **뒤**, 바꾸기 `A if 조건 else B` 는 **앞**.
- `[int(x) for x in input().split()]` 는 `list(map(int, input().split()))` 와 같아요.
- 행렬은 `[[0] * c for _ in range(r)]`. `[[0] * c] * r` 은 **같은 줄을 복사**해서 위험!''')

    L.review('🔁 지난 시간 복습',
        [T('지난 시간에는 `split` 으로 자르고 `join` 으로 붙이는 연습을 했어요.\n'
           '이번 시간에는 자른 조각들을 **한 줄에 한꺼번에 바꾸는** 컴프리헨션을 배워요.'),
         REVEAL_RUN('`"-".join("2026 07 17".split())` 의 결과는?', 'print("-".join("2026 07 17".split()))')])
    L.output('복습: 출력은?', 's = "Py Nest Py"\nprint(s.split().count("Py"))\nprint(s.replace(" ", ""))',
        '`split()` 하면 `["Py", "Nest", "Py"]` 이라 "Py" 가 2개. `replace(" ", "")` 는 공백을 모두 지워요.\n\n```\n{out}\n```', review=True)

    L.explain('컴프리헨션 = for + append 한 줄 요약',
        [T('빈 리스트를 만들고 for 로 돌며 `append` 하는 코드는 아주 자주 써요.\n'
           '파이썬은 이걸 **대괄호 안에 한 줄로** 쓰게 해 줘요. 이게 **리스트 컴프리헨션**이에요.\n'
           '모양: `[만들 값 for 변수 in 반복할 것]`'),
         CMP(side('for + append', '세 줄', 'sq = []\nfor x in range(1, 5):\n    sq.append(x * x)\nprint(sq)', 'good'),
             side('컴프리헨션', '한 줄', 'sq = [x * x for x in range(1, 5)]\nprint(sq)', 'good'))],
        [T('읽는 순서는 **for 부터** 읽고, 맨 앞의 식으로 돌아가면 쉬워요.\n'
           '"range(1, 5) 에서 x 를 하나씩 꺼내서 → x * x 를 담는다."'),
         TABS(('글자 바꾸기', '', 'words = ["cat", "dog"]\nprint([w.upper() for w in words])'),
              ('길이 재기', '', 'words = ["cat", "horse"]\nprint([len(w) for w in words])'),
              ('문자열 돌기', '', 'print([ch * 2 for ch in "abc"])')),
         KEY('결과는 **항상 새 리스트**예요. 원래 리스트는 바뀌지 않아요.')])

    L.output('출력은?', 'a = [3, 1, 4]\nb = [x * 10 for x in a]\nprint(a)\nprint(b)',
        '컴프리헨션은 **새 리스트**를 만들어요. a 는 그대로예요.\n\n```\n{out}\n```')

    L.fill('`[1, 2, 3, 4]` 의 각 값에 1 을 더한 리스트를 컴프리헨션으로 만드세요.',
        'nums = [1, 2, 3, 4]\nplus = [___ for n in ___]\nprint(plus)', [['n + 1', 'n+1', '1 + n', '1+n'], ['nums']],
        '앞에는 **만들 값** `n + 1`, for 뒤에는 **꺼낼 곳** `nums` 를 써요.', expect='[2, 3, 4, 5]')

    L.explain('조건 붙이기 — 거르기와 바꾸기',
        [T('**뒤에 붙는 `if`** 는 "조건에 맞는 것만 담아라" 는 **거르기**예요.\n'
           '조건이 거짓인 값은 아예 빠져서 결과 길이가 줄어요.'),
         CODE('scores = [72, 95, 88, 59, 91]\nhigh = [s for s in scores if s >= 90]\nprint(high)', '90점 이상만')],
        [T('**앞에 붙는 `A if 조건 else B`** 는 "모두 담되 **값을 바꿔라**" 예요.\n'
           '결과 길이는 원래와 같아요.'),
         CMP(side('거르기 (if 가 뒤)', '맞는 것만 남김', 'a = [5, -2, 7, -1]\nprint([x for x in a if x > 0])', 'good'),
             side('바꾸기 (if-else 가 앞)', '전부 남기고 값만 바꿈', 'a = [5, -2, 7, -1]\nprint([x if x > 0 else 0 for x in a])', 'good')),
         WARN('`[x for x in a if x > 0 else 0]` 처럼 **뒤에 else** 를 쓰면 SyntaxError 예요. else 가 필요하면 for **앞**으로!')])

    L.spot('실행하면 **오류**가 나는 줄은?', '''\
a = [4, -3, 8, -6]
b = [x for x in a if x > 0]
c = [x * 2 for x in b]
d = [x for x in a if x > 0 else -x]
print(b, c, d)''', 4,
        '`else` 가 붙은 조건식은 for **앞**에 와야 해요. 4번 줄은 `[x if x > 0 else -x for x in a]` 로 고쳐요.', error_line=4)

    L.bucket('결과 리스트의 **길이**가 원래 `a`(길이 5)와 같은지 분류하세요.', ['길이 5 그대로', '길이가 줄 수 있음'],
        [['[x * 2 for x in a]', 1], ['[x for x in a if x % 2 == 0]', 2], ['[0 if x < 0 else x for x in a]', 1],
         ['[x for x in a if x != 3]', 2], ['[str(x) for x in a]', 1]],
        '뒤에 붙은 `if` 는 **거르기**라 길이가 줄 수 있어요. 앞에 붙은 `if-else` 나 조건 없는 식은 모두 담아서 길이가 그대로예요.')

    L.explain('한 줄 입력 + 컴프리헨션',
        [T('`input().split()` 은 **글자 리스트**예요. 숫자로 쓰려면 하나씩 `int` 로 바꿔야 하죠.\n'
           '컴프리헨션으로 쓰면 `map` 과 똑같은 일을 해요.'),
         CMP(side('map 사용', '', 'nums = list(map(int, "3 8 5".split()))\nprint(nums)', 'good'),
             side('컴프리헨션 사용', '', 'nums = [int(x) for x in "3 8 5".split()]\nprint(nums)', 'good'))],
        [T('입력 받기 + 거르기 + 바꾸기를 **한 번에** 할 수도 있어요.\n'
           '시험에서 "한 줄 코드로 작성하시오" 가 나오면 이 모양이에요.'),
         CODE('words = input().split()\nbig = [w.upper() for w in words if len(w) >= 4]\nprint(" ".join(big))', '4글자 이상만 대문자로',
              stdin='i love python and java\n'),
         EXAM('2024년에 **split → 컴프리헨션 → join** 이 한 문제에 같이 나왔어요. 자르고, 바꾸고, 다시 붙이기!')])

    L.order('입력 `"5 12 7 20"` 에서 **10 이상인 수의 합**을 출력하는 코드를 순서대로 놓으세요.',
        ['line = input()', 'nums = [int(x) for x in line.split()]', 'big = [n for n in nums if n >= 10]', 'print(sum(big))'],
        '입력 → 정수 리스트 → 거르기 → 합계. 출력은 12 + 20 = 32 예요.', check=True, stdin='5 12 7 20\n', expect='32')

    L.explain('2중 컴프리헨션 — 행렬 만들기',
        [T('행렬(2차원 리스트)은 **리스트 안에 리스트**예요. `m[행][열]` 로 꺼내요.\n'
           '컴프리헨션 안에 컴프리헨션을 넣으면 행렬을 한 줄로 만들어요.\n'
           '**바깥**이 행(줄), **안쪽**이 열(칸)이에요.'),
         CODE('m = [[i * j for j in range(1, 4)] for i in range(1, 3)]\nfor row in m:\n    print(row)', '구구단 표 일부')],
        [T('0 으로 채운 r×c 행렬을 만들 때 **함정**이 있어요.\n'
           '`[[0] * 3] * 2` 는 **같은 줄 하나를 두 번 가리켜요.** 한 칸만 바꿔도 두 줄이 같이 바뀌어요.'),
         CMP(side('안전', '줄마다 새 리스트', 'm = [[0] * 3 for _ in range(2)]\nm[0][1] = 7\nprint(m)', 'good'),
             side('위험', '같은 줄을 복사', 'm = [[0] * 3] * 2\nm[0][1] = 7\nprint(m)', 'bad')),
         TIP('`_` 는 "이 변수는 안 써요" 라는 뜻으로 쓰는 이름이에요.')],
        [T('반대로 행렬을 **한 줄로 펴는**(평탄화) 것도 컴프리헨션으로 돼요.\n'
           'for 를 **두 번 이어 쓰면** 바깥 for → 안쪽 for 순서로 돌아요. 일반 2중 for 와 순서가 같아요.'),
         TRACE('m = [[1, 2], [3, 4], [5, 6]]\nflat = [x for row in m for x in row]\nprint(flat)\nprint(sum(flat))', '행렬 펴기')])

    L.output('출력은?', 'm = [[r * 10 + c for c in range(3)] for r in range(2)]\nprint(m)\nprint(m[1][2])',
        '바깥 r 이 행, 안쪽 c 가 열이에요. `m[1][2]` 는 r=1, c=2 → 12.\n\n```\n{out}\n```')

    L.output('출력은?', 'a = [[0] * 2] * 3\na[2][0] = 5\nprint(a)',
        '`* 3` 은 **같은 줄 하나**를 세 번 가리키게 해요. 그래서 한 칸을 바꾸면 세 줄이 모두 바뀌어 보여요.\n\n```\n{out}\n```')

    L.match('코드와 결과를 이어 보세요.',
        [['[x for x in range(5) if x % 2]', '[1, 3]'], ['[x % 2 for x in range(4)]', '[0, 1, 0, 1]'],
         ['[c for c in "a1b2" if c.isdigit()]', "['1', '2']"], ['[[0] * 2 for _ in range(2)]', '[[0, 0], [0, 0]]'],
         ['[len(w) for w in "hi you".split()]', '[2, 3]']],
        '`if x % 2` 는 나머지가 1(참)일 때만 남겨요. `isdigit()` 은 숫자 글자인지 검사해요.')

    L.practice('[기출유사] 해시태그 만들기',
'''한 줄의 문장이 주어지면, **2글자 이상인 단어**만 골라 **대문자**로 바꾸고 앞에 `#` 을 붙인 해시태그를 만드세요.

**[조건]**
- 해시태그 리스트는 **리스트 컴프리헨션 한 줄**로 만드세요.
- 첫째 줄: 해시태그를 공백 한 칸으로 이어 출력 (`join` 사용)
- 둘째 줄: 해시태그 개수
- 해시태그가 하나도 없으면 첫째 줄에 `없음` 을 출력하고 둘째 줄에 0 을 출력해요.

{ex}

{ex2}''',
'''words = input().split()
tags = []   # 컴프리헨션으로 바꿔 보세요
''',
'''words = input().split()
# 2글자 이상만 거르고(if 뒤), "#" + 대문자로 바꾸기(앞의 식)
tags = ["#" + w.upper() for w in words if len(w) >= 2]
if tags:
    print(" ".join(tags))
else:
    print("없음")
print(len(tags))''',
        ['i love python so much', 'go to pynest'], ['a b c', 'ok', 'x yy zzz w'],
        ['거르기 조건은 `if len(w) >= 2` 이고 for **뒤**에 붙여요.', '만들 값은 `"#" + w.upper()` 예요.',
         '빈 리스트는 거짓이라 `if tags:` 로 하나라도 있는지 검사할 수 있어요.'],
        '컴프리헨션의 **앞 식**은 바꾸기, **뒤 if** 는 거르기예요. 자르기(split) → 바꾸기·거르기 → 붙이기(join) 흐름을 기억해요.')

    L.practice('[기출유사] 행렬 두 배 + 행 합계',
'''첫째 줄에 행 수 r 과 열 수 c 가, 다음 r 줄에 행렬의 각 줄이 공백으로 주어져요. 모든 원소를 **2배** 한 행렬을 출력하고, 마지막 줄에 각 행의 합을 출력하세요.

**[조건]**
- 2배 행렬은 **2중 컴프리헨션**으로 만드세요.
- 각 행은 숫자를 공백 한 칸으로 이어 출력해요.
- 마지막 줄은 `행 합계: ` 뒤에 2배 행렬의 각 행 합을 공백으로 이어 출력해요.

{ex}

{ex2}''',
'''r, c = map(int, input().split())
m = [list(map(int, input().split())) for _ in range(r)]
# 2배 행렬을 만들고 출력하세요
''',
'''r, c = map(int, input().split())
m = [list(map(int, input().split())) for _ in range(r)]   # r 줄 입력
d = [[x * 2 for x in row] for row in m]                    # 바깥=행, 안쪽=칸
for row in d:
    print(" ".join(str(x) for x in row))
sums = [sum(row) for row in d]
print("행 합계:", " ".join(str(s) for s in sums))''',
        ['2 3\n1 2 3\n4 5 6', '3 2\n1 0\n-1 5\n7 7'], ['1 1\n0', '1 4\n10 20 30 40', '2 2\n-3 -4\n100 -100'],
        ['바깥 컴프는 `for row in m`, 안쪽 컴프는 `for x in row` 예요.', '`[[x * 2 for x in row] for row in m]`',
         '숫자 리스트를 join 하려면 `str(x)` 로 바꿔야 해요. 행 합은 `[sum(row) for row in d]`.'],
        '입력부터 `[list(map(int, input().split())) for _ in range(r)]` 로 r 줄을 한 번에 받을 수 있어요. 2차원은 "바깥=줄, 안쪽=칸" 만 기억하면 돼요.')

    L.essay('0 으로 채운 3×3 행렬을 `m = [[0] * 3] * 3` 으로 만들고 `m[0][0] = 1` 을 했더니 첫 열이 모두 1 이 되었어요. **이유**와 **올바른 코드**를 서술하세요.',
        '`[[0] * 3] * 3` 은 [0, 0, 0] 리스트 하나를 만든 뒤 그 **같은 리스트를 3번 가리키는** 리스트를 만든다. 세 줄이 모두 같은 리스트이므로 한 줄의 칸을 바꾸면 세 줄 모두 바뀐 것처럼 보인다. `m = [[0] * 3 for _ in range(3)]` 처럼 컴프리헨션으로 줄마다 새 리스트를 만들어야 한다.',
        ['같은 리스트(줄)를 3번 가리킨다', '한 칸을 바꾸면 모든 줄이 바뀐다', '[[0] * 3 for _ in range(3)] 로 고친다'])

    # =====================================================================
    L = C.lesson('β-04 enumerate·zip·map·filter·lambda', 25,
'''- `enumerate(a, start=1)` → (번호, 값) 쌍. 번호를 1부터 셀 때 `start=1`.
- `zip(a, b)` → 같은 위치끼리 묶기. **짧은 쪽에서 멈춰요.**
- `lambda x: 식` = 이름 없는 한 줄 함수.
- `map(함수, a)` 는 모두 바꾸기, `filter(함수, a)` 는 참인 것만 남기기. 결과는 `list()` 로 감싸서 봐요.''')

    L.review('🔁 지난 시간 복습',
        [T('지난 시간에는 컴프리헨션으로 **거르기(if 뒤)** 와 **바꾸기(if-else 앞)** 를 했고, 2중 컴프로 행렬을 만들었어요.'),
         REVEAL_RUN('`[x if x % 2 else 0 for x in range(1, 6)]` 의 결과는?', 'print([x if x % 2 else 0 for x in range(1, 6)])')])
    L.output('복습: 출력은?', 'm = [[1, 2], [3, 4]]\nprint([row[0] for row in m])\nprint([x for row in m for x in row if x > 1])',
        '첫 줄은 각 행의 0번 칸, 둘째 줄은 행렬을 펴면서 1 보다 큰 값만 남겨요.\n\n```\n{out}\n```', review=True)

    L.explain('enumerate — 번호 붙여 돌기',
        [T('리스트를 돌 때 **몇 번째인지**도 필요하면 `enumerate` 를 써요.\n'
           '`for i, x in enumerate(a):` 하면 i 에 번호(0부터), x 에 값이 들어와요.\n'
           '`range(len(a))` 로 돌며 `a[i]` 를 쓰는 것보다 깔끔해요.'),
         CMP(side('range(len()) 방식', '', 'menu = ["라면", "김밥"]\nfor i in range(len(menu)):\n    print(i, menu[i])', 'good'),
             side('enumerate 방식', '', 'menu = ["라면", "김밥"]\nfor i, m in enumerate(menu):\n    print(i, m)', 'good'))],
        [T('사람에게 보여 줄 번호는 보통 **1번부터**죠. 그럴 땐 `start=1` 을 줘요.\n'
           '`start` 는 **번호만** 바꿔요. 꺼내는 값은 여전히 처음부터예요.'),
         TRACE('menu = ["라면", "김밥", "떡볶이"]\nfor no, m in enumerate(menu, start=1):\n    print(f"{no}번 {m}")', '1번부터 번호 붙이기'),
         WARN('`enumerate(menu, start=1)` 이라고 `menu[1]` 부터 꺼내는 게 **아니에요.** 시험 출력 추론 단골 함정이에요.')])

    L.output('출력은?', 'a = ["x", "y", "z"]\nfor i, v in enumerate(a, start=3):\n    print(i, v)',
        '`start=3` 은 번호만 3 부터 셀 뿐, 값은 처음 "x" 부터 꺼내요.\n\n```\n{out}\n```')

    L.explain('zip — 같은 위치끼리 묶기',
        [T('`zip(a, b)` 는 a 와 b 의 **같은 위치**끼리 짝을 지어 줘요.\n'
           '이름 리스트와 점수 리스트처럼 **따로 받은 두 리스트**를 함께 돌 때 써요.'),
         CODE('names = ["민지", "서준", "하린"]\nscores = [88, 95, 72]\nfor n, s in zip(names, scores):\n    print(n, s)', '이름-점수 짝')],
        [T('길이가 다르면 **짧은 쪽에서 멈춰요.** 남는 값은 그냥 버려져요 (오류 아님!).\n'
           '`list(zip(...))` 로 감싸면 튜플 쌍의 리스트를 볼 수 있어요.'),
         REVEAL_RUN('`list(zip([1, 2, 3], "ab"))` 는?', 'print(list(zip([1, 2, 3], "ab")))')],
        [T('**행렬 덧셈**에 zip 이 딱이에요. 두 행렬의 같은 줄을 zip 으로 묶고, 그 줄 안의 같은 칸을 또 zip 으로 묶어요.\n'
           '2중 컴프리헨션 + zip 두 번 = 한 줄 행렬 덧셈!'),
         CODE('A = [[1, 2], [3, 4]]\nB = [[10, 20], [30, 40]]\nC = [[x + y for x, y in zip(ra, rb)] for ra, rb in zip(A, B)]\nprint(C)', '행렬 덧셈 한 줄'),
         EXAM('2023년과 2025년 모두 **zip + 컴프리헨션** 이 나왔어요. 바깥 zip 은 줄끼리, 안쪽 zip 은 칸끼리!')])

    L.fill('두 리스트의 같은 위치끼리 **곱한** 리스트를 만드세요.',
        'a = [1, 2, 3]\nb = [4, 5, 6]\nc = [x * y for x, y in ___(a, b)]\nprint(c)', [['zip']],
        '같은 위치끼리 짝을 지어 주는 건 `zip` 이에요. 결과는 `[4, 10, 18]`.', expect='[4, 10, 18]')

    L.output('출력은?', 'a = [5, 6, 7, 8]\nb = [1, 2]\nprint(len(list(zip(a, b))))\nfor i, (x, y) in enumerate(zip(a, b)):\n    print(i, x - y)',
        'zip 은 짧은 b(길이 2)에서 멈춰요. `enumerate(zip(...))` 는 (번호, (x, y)) 모양이라 괄호로 풀어요.\n\n```\n{out}\n```')

    L.explain('lambda + map / filter',
        [T('`lambda 매개변수: 식` 은 **이름 없는 한 줄 함수**예요. `return` 을 쓰지 않아도 식의 값이 돌려져요.\n'
           '`def` 로 만든 함수와 똑같이 호출할 수 있어요.'),
         CMP(side('def', '', 'def double(x):\n    return x * 2\nprint(double(7))', 'good'),
             side('lambda', '', 'double = lambda x: x * 2\nprint(double(7))', 'good'))],
        [T('`map(함수, 리스트)` 는 모든 값에 함수를 적용해요 (**바꾸기**).\n'
           '`filter(함수, 리스트)` 는 함수 결과가 **참인 값만** 남겨요 (**거르기**).\n'
           '둘 다 결과가 바로 리스트가 아니라서 `list()` 로 감싸요.'),
         TABS(('map', '모두 바꾸기', 'a = [1, 2, 3, 4]\nprint(list(map(lambda x: x * x, a)))'),
              ('filter', '참인 것만', 'a = [1, 2, 3, 4]\nprint(list(filter(lambda x: x % 2 == 0, a)))'),
              ('같은 컴프', '', 'a = [1, 2, 3, 4]\nprint([x * x for x in a])\nprint([x for x in a if x % 2 == 0])'))],
        [T('`list()` 로 감싸지 않고 print 하면 값 대신 **map 객체** 가 보여요.\n'
           '또 map 결과는 **인덱스로 꺼낼 수 없고**, 한 번 다 꺼내 쓰면 **비어 버려요.**'),
         CODE('m = map(int, ["1", "2"])\nprint(list(m))\nprint(list(m))', '한 번 쓰면 비어요'),
         KEY('map ↔ `[f(x) for x in a]`, filter ↔ `[x for x in a if 조건]`. 시험에서 서로 바꿔 쓰라는 문제가 나와요.')])

    L.match('코드와 결과를 이어 보세요.',
        [['list(map(lambda x: x + 1, [1, 2]))', '[2, 3]'], ['list(filter(lambda x: x > 2, [1, 2, 3]))', '[3]'],
         ['list(map(str, [1, 2]))', "['1', '2']"], ['list(map(len, ["ab", "c"]))', '[2, 1]'],
         ['list(filter(lambda s: "a" in s, ["ab", "c"]))', "['ab']"]],
        '`map(str, …)` 처럼 이미 있는 함수 이름을 그대로 넣어도 돼요. filter 는 조건이 참인 값만 남겨요.')

    L.spot('실행하면 **오류**가 나는 줄은?', '''\
nums = [3, 6, 9]
m = map(lambda x: x // 3, nums)
print(type(m))
print(m[0])''', 4,
        'map 의 결과는 리스트가 아니라 **map 객체**라서 `m[0]` 처럼 인덱스로 꺼낼 수 없어요 → TypeError. `list(m)[0]` 처럼 바꿔야 해요.', error_line=4)

    L.output('출력은?', 'words = ["Apple", "kiwi", "Banana", "fig"]\nlong_w = list(filter(lambda w: len(w) > 3, words))\nprint(list(map(lambda w: w.lower(), long_w)))\nprint(len(list(map(len, words))))',
        'filter 로 4글자 이상만 남기고, map 으로 소문자로 바꿔요. 마지막 줄은 map 결과의 개수라 원래 길이 4 예요.\n\n```\n{out}\n```')

    L.practice('[기출유사] 행렬 덧셈',
'''첫째 줄에 행렬의 행 수 n 이 주어지고, 다음 n 줄에 행렬 A, 그다음 n 줄에 행렬 B 가 주어져요 (두 행렬의 크기는 같아요). A + B 를 출력하세요.

**[조건]**
- 덧셈은 `zip` 과 **컴프리헨션**으로 하세요.
- 각 행은 숫자를 공백 한 칸으로 이어 출력해요.

{ex}

{ex2}''',
'''n = int(input())
A = [list(map(int, input().split())) for _ in range(n)]
B = [list(map(int, input().split())) for _ in range(n)]
# A + B 를 만들어 출력하세요
''',
'''n = int(input())
A = [list(map(int, input().split())) for _ in range(n)]
B = [list(map(int, input().split())) for _ in range(n)]
# 바깥 zip: 같은 줄끼리 / 안쪽 zip: 같은 칸끼리
S = [[x + y for x, y in zip(ra, rb)] for ra, rb in zip(A, B)]
for row in S:
    print(" ".join(map(str, row)))''',
        ['2\n1 2 3\n4 5 6\n10 20 30\n40 50 60', '1\n7 -2\n3 2'], ['1\n0\n0', '3\n1\n2\n3\n-1\n-2\n-3', '2\n5 5\n5 5\n-10 0\n0 -10'],
        ['먼저 `for ra, rb in zip(A, B)` 로 같은 줄을 묶어요.', '줄 안에서 `for x, y in zip(ra, rb)` 로 같은 칸을 묶어 `x + y`.',
         '출력은 `" ".join(map(str, row))`.'],
        '2중 컴프리헨션의 바깥은 줄, 안쪽은 칸이에요. 같은 위치를 짝짓는 건 언제나 zip 이에요.')

    L.practice('[기출유사] 평균 이상 명단',
'''첫째 줄에 이름들이, 둘째 줄에 같은 순서로 점수들이 공백으로 주어져요. 평균을 출력하고, **평균 이상**인 학생을 번호를 붙여 출력하세요.

**[조건]**
- 첫째 줄: `평균: ` 뒤에 평균을 소수 첫째 자리까지 (`round(값, 1)`)
- 이름과 점수는 `zip` 으로 묶어요.
- 명단 번호는 `enumerate(..., start=1)` 로 붙여 `번호. 이름 점수` 모양으로 출력해요.

{ex}

{ex2}''',
'''names = input().split()
scores = list(map(int, input().split()))
# 이어서 작성하세요
''',
'''names = input().split()
scores = list(map(int, input().split()))
avg = sum(scores) / len(scores)
print("평균:", round(avg, 1))
# zip 으로 짝지어 평균 이상만 거르기
good = [(n, s) for n, s in zip(names, scores) if s >= avg]
for no, (n, s) in enumerate(good, start=1):   # 번호는 1부터
    print(f"{no}. {n} {s}")''',
        ['민지 서준 하린 도윤\n80 95 70 85', '가 나 다\n50 50 50'], ['혼자\n0', 'A B\n100 99', 'a b c d e\n1 2 3 4 100'],
        ['평균은 `sum(scores) / len(scores)`.', '`[(n, s) for n, s in zip(names, scores) if s >= avg]` 로 거르기.',
         '`for no, (n, s) in enumerate(good, start=1):` 처럼 괄호로 쌍을 풀어요.'],
        '거른 **뒤에** 번호를 붙여야 1, 2, 3 이 빈틈없이 이어져요. 원래 리스트에 enumerate 를 쓰면 번호가 건너뛰어요.')

    L.essay('`m = map(int, ["1", "2", "3"])` 다음에 `print(m)` 을 하면 `[1, 2, 3]` 이 나오지 않아요. **이유**와 **고치는 방법**, 그리고 `list(m)` 을 두 번 하면 두 번째에 무엇이 나오는지 서술하세요.',
        'map 은 결과를 바로 리스트로 만들지 않고 값을 하나씩 꺼내 주는 map 객체를 돌려주기 때문에 print 하면 `<map object ...>` 가 출력된다. `print(list(m))` 처럼 list() 로 감싸야 [1, 2, 3] 이 보인다. map 객체는 한 번 다 꺼내면 비므로 두 번째 list(m) 은 빈 리스트 [] 가 된다.',
        ['map 객체를 돌려준다', 'list() 로 감싼다', '두 번째는 빈 리스트 []'])

    # =====================================================================
    L = C.lesson('β-05 함수 ①: def·return·지역/전역 변수', 30,
'''- `def 이름(매개변수):` 로 만들고 `이름(인자)` 로 부르기. **정의가 호출보다 먼저.**
- `return` 은 값을 **돌려주고 함수를 끝내요.** 없으면 `None` 을 돌려줘요.
- `return a, b` 는 **튜플** 하나를 돌려줘요 → `x, y = f()` 로 풀기.
- 함수 안에서 만든 변수는 **지역 변수**. 전역 변수를 **바꾸려면** `global 이름`.''')

    L.review('🔁 지난 시간 복습',
        [T('지난 시간에는 `enumerate(start=1)`, `zip`, `lambda` 와 `map/filter` 를 배웠어요.\n'
           'lambda 는 "이름 없는 한 줄 함수" 였죠. 오늘은 **이름 있는 함수**를 `def` 로 제대로 만들어요.'),
         REVEAL_RUN('`list(zip("ab", map(lambda x: x * 3, [1, 2])))` 의 결과는?', 'print(list(zip("ab", map(lambda x: x * 3, [1, 2]))))')])
    L.output('복습: 출력은?', 'a = [10, 20, 30]\nfor i, v in enumerate(a, start=1):\n    if i % 2:\n        print(i, v)',
        '번호 i 가 1, 3 (홀수)일 때만 출력해요. 값은 처음부터 꺼내니 10, 30.\n\n```\n{out}\n```', review=True)

    L.explain('def 와 호출 — 함수는 "작은 기계"',
        [T('함수는 **입력(매개변수)을 받아 일을 하고 결과(return)를 내놓는 작은 기계**예요.\n'
           '같은 일을 여러 번 할 때, 큰 프로그램을 나눌 때 써요. 2차 큰 문항은 거의 다 함수로 나눠요.'),
         CODE('def area(w, h):\n    return w * h\n\nprint(area(3, 4))\nprint(area(5, 2) + 1)', '넓이 함수')],
        [T('호출하면 이런 순서로 움직여요.'),
         STEPS(('① 호출', '`area(3, 4)` 를 만나면 함수로 점프해요.'),
               ('② 값 넣기', '인자 3, 4 가 매개변수 w, h 에 **순서대로** 들어가요.'),
               ('③ 실행', '함수 몸통을 위에서부터 실행해요.'),
               ('④ return', '`return` 을 만나면 값을 들고 **호출한 자리로 돌아가요.** 그 아래 줄은 실행 안 돼요.')),
         WARN('파이썬은 위에서 아래로 읽어요. **def 보다 위에서** 함수를 부르면 NameError 예요.')])

    L.spot('실행하면 **오류**가 나는 줄은?', '''\
x = 5
print(triple(x))
def triple(n):
    return n * 3
print(triple(2))''', 2,
        '2번 줄을 실행할 때는 아직 `def triple` 을 읽지 않았어요 → NameError. 함수 정의를 **호출보다 위로** 올려야 해요.', error_line=2)

    L.explain('return vs print, 그리고 None',
        [T('`print` 는 **화면에 보여 주기만** 하고, `return` 은 **값을 돌려줘서** 다른 계산에 쓸 수 있게 해요.\n'
           '함수에 `return` 이 없으면 파이썬은 자동으로 **None** 을 돌려줘요.'),
         CMP(side('return 함수', '값을 돌려줌', 'def add(a, b):\n    return a + b\nr = add(2, 3)\nprint(r * 10)', 'good'),
             side('print 함수', '보여 주기만, 반환은 None', 'def add(a, b):\n    print(a + b)\nr = add(2, 3)\nprint(r)', 'bad'))],
        [T('`return` 은 함수를 **즉시 끝내요.** 그래서 조건에 따라 일찍 return 하는 모양을 자주 써요.\n'
           'if/elif 마다 return 이 있으면 맞는 곳 하나에서 끝나요.'),
         TRACE('def grade(score):\n    if score >= 90:\n        return "A"\n    if score >= 80:\n        return "B"\n    return "C"\n\nprint(grade(85))\nprint(grade(95))', '일찍 return'),
         THINK('`return` 뒤에 아무것도 안 쓰면(`return`)? 역시 None 을 돌려주며 끝나요.')])

    L.output('출력은?', 'def hello(name):\n    print("안녕", name)\n\nresult = hello("둥지")\nprint(result)',
        '함수 안의 print 가 먼저 "안녕 둥지" 를 찍고, return 이 없으니 result 는 None 이에요.\n\n```\n{out}\n```')

    L.output('출력은?', 'def check(n):\n    for i in range(2, n):\n        if n % i == 0:\n            return False\n    return True\n\nprint(check(7), check(9))\nprint([n for n in range(2, 12) if check(n)])',
        '나누어떨어지는 수를 만나면 **바로 return False** 로 끝나요. 끝까지 못 찾으면 True. 즉 소수 판별 함수예요.\n\n```\n{out}\n```')

    L.explain('값 여러 개 돌려주기 — 튜플',
        [T('`return a, b` 처럼 쉼표로 여러 값을 쓰면 **튜플 하나**로 묶여 돌아와요.\n'
           '받는 쪽에서 `x, y = f()` 로 **풀어서** 받을 수 있어요.'),
         CODE('def min_max(nums):\n    return min(nums), max(nums)\n\nr = min_max([4, 9, 1])\nprint(r, type(r))\nlo, hi = min_max([4, 9, 1])\nprint(lo, hi)', '최솟값·최댓값 한꺼번에')],
        [T('주민번호·날짜처럼 **한 번에 여러 정보를 뽑는** 함수에 아주 좋아요.\n'
           '받는 변수 개수와 돌려주는 값 개수가 다르면 ValueError 가 나요.'),
         KEY('`return a, b` = `return (a, b)`. 괄호가 없어도 **튜플**이에요.')])

    L.fill('시·분을 돌려주는 함수를 완성하세요. (`130` 분 → `2 10`)',
        'def to_hm(m):\n    return m // 60, ___\n\nh, mm = ___(130)\nprint(h, mm)', [['m % 60', 'm%60'], ['to_hm']],
        '분은 60 으로 나눈 **나머지** `m % 60`. 함수가 튜플을 돌려주니 `h, mm = to_hm(130)` 으로 풀어 받아요.', expect='2 10')

    L.explain('지역 변수와 전역 변수',
        [T('함수 **안에서 만든 변수**는 **지역 변수**예요. 함수가 끝나면 사라지고, 밖에서는 안 보여요.\n'
           '함수 **밖에서 만든 변수**는 **전역 변수**. 함수 안에서 **읽기**는 그냥 돼요.'),
         CODE('rate = 2          # 전역\ndef calc(x):\n    y = x * rate  # 전역 읽기 OK, y 는 지역\n    return y\nprint(calc(5))', '읽기는 자유')],
        [T('그런데 함수 안에서 전역 변수에 **값을 대입**하면, 파이썬은 그걸 **새 지역 변수**로 봐요.\n'
           '그래서 `count += 1` 처럼 읽고 바꾸면 "아직 값이 없는 지역 변수" 를 읽게 돼서 **UnboundLocalError** 가 나요.'),
         CMP(side('오류', 'global 없음', 'count = 0\ndef up():\n    count += 1\nup()', 'bad', expect_error=True),
             side('정상', 'global 선언', 'count = 0\ndef up():\n    global count\n    count += 1\nup()\nup()\nprint(count)', 'good'))],
        [T('`global 이름` 은 "이 이름은 **밖의 그 변수**를 쓰겠다" 는 선언이에요.\n'
           '은행 잔액처럼 여러 함수가 **함께 바꾸는 값**에 써요.'),
         TRACE('total = 100\ndef spend(x):\n    global total\n    total -= x\ndef show():\n    tmp = total * 2\n    return tmp\nspend(30)\nprint(total, show())', '전역 바꾸기'),
         EXAM('은행·포인트 프로그램 빈칸 문제에서 `global balance` 자리가 빈칸으로 자주 나와요.')])

    L.spot('`add_point()` 를 부르면 **오류**가 나요. 오류가 나는 줄은?', '''\
point = 10
def add_point():
    point = point + 5
    return point
print(add_point())''', 3,
        '함수 안에서 `point = …` 로 대입하니 point 는 **지역 변수**가 돼요. 그런데 오른쪽에서 아직 값이 없는 지역 point 를 읽어 UnboundLocalError. `global point` 를 넣거나 매개변수로 받아야 해요.', error_line=3)

    L.output('출력은?', 'x = 1\ndef f():\n    x = 50\n    return x\ndef g():\n    global x\n    x = 7\nprint(f(), x)\ng()\nprint(x)',
        'f 안의 x 는 **지역 변수**라 전역 x(1)는 그대로예요. g 는 global 선언을 했으니 전역 x 를 7 로 바꿔요.\n\n```\n{out}\n```')

    L.bucket('각 설명이 지역 변수인지 전역 변수인지 분류하세요.', ['지역 변수', '전역 변수'],
        [['함수 안에서 처음 대입한 변수', 1], ['함수 밖(맨 위)에서 만든 변수', 2], ['함수가 끝나면 사라진다', 1],
         ['`global` 로 선언한 뒤 함수 안에서 바꾼 변수', 2], ['함수의 매개변수', 1]],
        '매개변수도 함수 안에서만 쓰는 **지역 변수**예요. global 로 선언하면 함수 안에서도 **밖의 변수**를 가리켜요.')

    L.practice('[기출유사] 주민번호로 생일·성별 알기',
'''주민등록번호가 `YYMMDD-GNNNNNN` 모양으로 주어져요 (G 는 뒷자리 첫 숫자). 두 함수를 만들어 생일과 성별을 출력하세요.

**[조건]**
- `birth(rrn)` : (연, 월, 일)을 **정수 튜플**로 return. G 가 1·2 면 1900년대, 3·4 면 2000년대.
- `gender(rrn)` : G 가 홀수면 `"남자"`, 짝수면 `"여자"` 를 return.
- 입력을 받아 두 함수를 호출하고, `2006년 3월 15일생` 과 성별을 두 줄로 출력해요.

{ex}

{ex2}''',
'''def birth(rrn):
    pass

def gender(rrn):
    pass

rrn = input()
''',
'''def birth(rrn):
    g = int(rrn[7])                     # 뒷자리 첫 숫자
    base = 1900 if g in (1, 2) else 2000
    y = base + int(rrn[0:2])
    m = int(rrn[2:4])
    d = int(rrn[4:6])
    return y, m, d                      # 튜플로 여러 값 돌려주기

def gender(rrn):
    if int(rrn[7]) % 2 == 1:
        return "남자"
    return "여자"

rrn = input()
y, m, d = birth(rrn)                    # 튜플 풀어 받기
print(f"{y}년 {m}월 {d}일생")
print(gender(rrn))''',
        ['060315-3123456', '991231-2654321'], ['000101-4000000', '850707-1111111', '101010-3999999'],
        ['`-` 가 6번 칸이라 G 는 `rrn[7]` 이에요.', '연도 두 자리는 `rrn[0:2]`, 월은 `rrn[2:4]`, 일은 `rrn[4:6]`. `int()` 로 바꾸면 앞의 0 이 사라져요.',
         '`return y, m, d` 로 돌려주고 `y, m, d = birth(rrn)` 으로 받아요.'],
        '함수가 **return 으로 값을 돌려주면** 출력 형식은 밖에서 자유롭게 정할 수 있어요. 함수 안에서 print 해 버리면 다른 곳에 재사용하기 어려워요.')

    L.practice('[기출유사] 통장 관리 (global)',
'''잔액 0 원에서 시작하는 통장이 있어요. 첫째 줄에 명령 수 N, 다음 N 줄에 `입금 금액` 또는 `출금 금액` 이 주어져요.

**[조건]**
- 전역 변수 `balance` 와 함수 `deposit(money)`, `withdraw(money)` 를 만들어요. 두 함수는 `global balance` 로 잔액을 바꿔요.
- `withdraw` 는 잔액이 모자라면 잔액을 바꾸지 않고 `False`, 성공하면 `True` 를 return 해요.
- 입금 후: `입금 완료: 잔액원`, 출금 성공: `출금 완료: 잔액원`, 실패: `잔액 부족`
- 마지막 줄: `최종 잔액: 잔액원`

{ex}

{ex2}''',
'''balance = 0

def deposit(money):
    pass

def withdraw(money):
    pass

n = int(input())
''',
'''balance = 0

def deposit(money):
    global balance          # 밖의 balance 를 바꾸겠다는 선언
    balance += money

def withdraw(money):
    global balance
    if money > balance:
        return False        # 바꾸지 않고 실패
    balance -= money
    return True

n = int(input())
for _ in range(n):
    cmd, amount = input().split()
    amount = int(amount)
    if cmd == "입금":
        deposit(amount)
        print(f"입금 완료: {balance}원")
    elif withdraw(amount):
        print(f"출금 완료: {balance}원")
    else:
        print("잔액 부족")
print(f"최종 잔액: {balance}원")''',
        ['3\n입금 5000\n출금 3000\n출금 4000', '2\n출금 100\n입금 100'], ['1\n입금 0', '2\n입금 1000\n출금 1000', '4\n입금 10\n입금 20\n출금 31\n출금 30'],
        ['두 함수 첫 줄에 `global balance` 가 필요해요.', '`withdraw` 에서 `if money > balance: return False` 로 먼저 막아요.',
         '`elif withdraw(amount):` 처럼 함수 결과(True/False)를 바로 조건에 쓸 수 있어요.'],
        'global 이 없으면 `balance += money` 에서 UnboundLocalError 가 나요. 성공/실패를 True/False 로 돌려주면 메시지는 밖에서 고를 수 있어요.')

    L.essay('다음 코드를 실행하면 `UnboundLocalError` 가 나요. **이유**를 지역 변수와 연결해 서술하고 고치는 방법을 쓰세요.\n\n```python\nscore = 0\ndef add():\n    score += 10\nadd()\n```',
        '함수 안에서 score 에 값을 대입(score += 10)하면 파이썬은 score 를 함수의 지역 변수로 본다. 그런데 += 는 먼저 score 의 값을 읽어야 하는데, 지역 변수 score 에는 아직 값이 없어서 UnboundLocalError 가 발생한다. 함수 첫 줄에 `global score` 를 써서 전역 변수를 쓰겠다고 선언하거나, score 를 매개변수로 받아 결과를 return 하도록 고친다.',
        ['함수 안 대입 → 지역 변수로 취급', '값이 없는 지역 변수를 읽는다', 'global score 선언 (또는 매개변수 + return)'])

    # =====================================================================
    L = C.lesson('β-06 함수 ②: 기본값 인자·*args·**kwargs', 30,
'''- 기본값 인자 `def f(w, fee=3500):` → 안 넣으면 3500. **기본값 있는 매개변수는 뒤에.**
- 키워드 인자 `f(w=3, fee=5000)` 은 순서 상관없이 이름으로 넣기.
- `*args` 는 남는 위치 인자를 **튜플**로, `**kwargs` 는 남는 키워드 인자를 **딕셔너리**로 받아요.
- 순서: `def f(일반, 기본값, *args, **kwargs)`. kwargs 는 `.items()` 로 돌아요.''')

    L.review('🔁 지난 시간 복습',
        [T('지난 시간에는 `return` 이 없으면 **None**, `return a, b` 는 **튜플**, 전역 변수를 바꾸려면 `global` 이라는 걸 배웠어요.'),
         REVEAL_RUN('아래 코드의 출력은?', 'def f(x):\n    if x > 0:\n        return x, -x\nprint(f(3))\nprint(f(-1))',
                    '`f(-1)` 은 if 를 건너뛰고 return 없이 끝나요.')])
    L.output('복습: 출력은?', 'n = 3\ndef g():\n    global n\n    n = n * 2\n    return n + 1\nprint(g(), n)',
        'global 선언으로 전역 n 을 6 으로 바꾸고 7 을 돌려줘요. print 는 g() 를 먼저 계산한 뒤 n 을 읽어요.\n\n```\n{out}\n```', review=True)

    L.explain('기본값 인자 — 안 넣으면 이 값',
        [T('매개변수에 `=값` 을 붙이면 **기본값 인자**예요. 호출할 때 안 넣으면 기본값을 써요.\n'
           '택배비처럼 "보통은 3500원인데 가끔 다르게" 같은 상황에 딱이에요.'),
         CODE('def fee(weight, small_fee=3500):\n    if weight <= 2:\n        return small_fee\n    elif weight <= 5:\n        return small_fee + 1500\n    return small_fee + 3000\n\nprint(fee(1))\nprint(fee(4))\nprint(fee(4, 5000))', '구간별 택배비')],
        [T('**키워드 인자**로 이름을 붙여 넣으면 순서를 바꿔도 돼요.\n'
           '예: `fee(small_fee=4000, weight=7)`'),
         CMP(side('정상', '기본값은 뒤에', 'def f(a, b=2):\n    return a + b\nprint(f(1), f(1, b=10))', 'good'),
             side('SyntaxError', '기본값 뒤에 일반 매개변수', 'def f(a=1, b):\n    return a + b', 'bad', expect_error=True)),
         WARN('기본값이 있는 매개변수 **뒤에** 기본값 없는 매개변수가 오면 SyntaxError 예요.')])

    L.output('출력은?', 'def ticket(age, price=10000):\n    if age < 13:\n        return price // 2\n    return price\n\nprint(ticket(10))\nprint(ticket(20, 8000))\nprint(ticket(price=6000, age=5))',
        '키워드 인자는 이름으로 짝지으니 순서가 달라도 돼요. 13살 미만은 반값.\n\n```\n{out}\n```')

    L.spot('실행하면 **오류**가 나는 줄은?', '''\
def order(menu, size="M", count):
    return menu + size * count

print(order("라떼", "L", 2))''', 1,
        '기본값 있는 `size="M"` 뒤에 기본값 없는 `count` 가 와서 **SyntaxError** 예요. `def order(menu, count, size="M"):` 처럼 기본값 매개변수를 뒤로 보내요.', error_line=1)

    L.explain('*args — 몇 개든 받기 (튜플)',
        [T('매개변수 앞에 `*` 를 붙이면 **남는 위치 인자를 전부 모아 튜플**로 받아요.\n'
           '이름은 보통 `args` 지만 `*menus` 처럼 아무 이름이나 돼요.'),
         CODE('def total(*nums):\n    print(nums, type(nums))\n    s = 0\n    for n in nums:\n        s += n\n    return s\n\nprint(total(1, 2, 3))\nprint(total())', '개수 상관없는 합계')],
        [T('일반 매개변수와 같이 쓰면 **앞의 것부터 채우고 남는 것**이 args 로 가요.\n'
           '하나도 안 남으면 **빈 튜플** `()` 이에요.'),
         REVEAL_RUN('`f("A반", 90, 80)` 의 출력은?', 'def f(cls, *scores):\n    print(cls, scores, len(scores))\nf("A반", 90, 80)'),
         TIP('반대로 **호출할 때** `f(*리스트)` 라고 쓰면 리스트를 풀어서 인자 여러 개로 넣어 줘요.')])

    L.output('출력은?', 'def pick(first, *rest):\n    return first, rest\n\na, b = pick(5, 6, 7)\nprint(a)\nprint(b)\nprint(pick("x"))',
        'first 가 5 를 받고 남은 6, 7 이 **튜플**로 rest 에 들어가요. 하나만 주면 rest 는 빈 튜플.\n\n```\n{out}\n```')

    L.explain('**kwargs — 이름=값 모으기 (딕셔너리)',
        [T('`**` 를 붙이면 **남는 키워드 인자**(`이름=값`)를 모아 **딕셔너리**로 받아요.\n'
           '키는 이름(문자열), 값은 넣은 값이에요. `.items()` 로 키와 값을 함께 돌아요.'),
         CODE('def profile(name, **info):\n    print(name, type(info))\n    for k, v in info.items():\n        print(k, "=", v)\n\nprofile("둥지", age=17, club="방송부")', '추가 정보 받기')],
        [T('네 가지를 다 쓸 때 순서는 정해져 있어요.\n'
           '`def f(일반, 기본값=, *args, **kwargs)`'),
         TRACE('def order(table, *menus, **requests):\n    print(table)\n    print(menus)\n    print(requests)\n\norder(3, "라떼", "케이크", shot=2, ice="적게")', '세 종류가 나뉘는 모습'),
         EXAM('2026년에 `*menus`, `**requests` 의 **자료형(tuple / dict)** 과 `.items()` 출력이 나왔어요.')])

    L.bucket('`def f(a, *args, **kwargs):` 를 `f(1, 2, 3, x=4, y=5)` 로 불렀어요. 각 값이 어디로 갈까요?', ['a', 'args (튜플)', 'kwargs (딕셔너리)'],
        [['1', 1], ['2', 2], ['3', 2], ['x=4', 3], ['y=5', 3]],
        '첫 위치 인자는 a, 남는 위치 인자는 args 튜플 `(2, 3)`, 이름=값 은 kwargs 딕셔너리 `{"x": 4, "y": 5}` 로 가요.')

    L.output('출력은?', 'def cafe(*menus, **req):\n    print(type(menus).__name__, len(menus))\n    print(type(req).__name__, list(req.keys()))\n    for k, v in req.items():\n        print(f"{k}:{v}")\n\ncafe("아메리카노", "라떼", size="L", shot=2)',
        '`type(x).__name__` 은 자료형 이름만 보여 줘요. menus 는 tuple, req 는 dict.\n\n```\n{out}\n```')

    L.match('매개변수 모양과 받는 방식을 이어 보세요.',
        [['def f(a, b)', '정해진 개수만 순서대로'], ['def f(a, b=0)', 'b 는 안 넣으면 0'],
         ['def f(*args)', '위치 인자 여러 개 → 튜플'], ['def f(**kwargs)', '이름=값 여러 개 → 딕셔너리'],
         ['f(*[1, 2])', '리스트를 풀어 인자로 넣기']],
        '`*` 는 튜플, `**` 는 딕셔너리! 호출 쪽의 `*` 는 반대로 **풀어서** 넣는 거예요.')

    L.practice('[기출유사] 택배비 계산기 (기본값 인자)',
'''무게(kg)와 지역이 한 줄에 주어져요. 함수로 택배비를 계산해 출력하세요.

**[조건]**
- `def delivery_fee(weight, small_fee=3500):` 를 만들고 구간에 따라 **return** 해요.
  - 1kg 이하: `small_fee` / 5kg 이하: `small_fee + 2000` / 10kg 이하: `small_fee + 4000` / 10kg 초과: `-1`
- 지역이 `일반` 이면 `delivery_fee(무게)`, `도서산간` 이면 `small_fee` 를 **6000** 으로 넣어 호출해요.
- 결과가 -1 이면 `배송 불가`, 아니면 `택배비: 금액원` 을 출력해요.

{ex}

{ex2}''',
'''def delivery_fee(weight, small_fee=3500):
    pass

w, area = input().split()
''',
'''def delivery_fee(weight, small_fee=3500):
    if weight <= 1:
        return small_fee
    elif weight <= 5:
        return small_fee + 2000
    elif weight <= 10:
        return small_fee + 4000
    return -1                      # 10kg 초과

w, area = input().split()
w = float(w)
if area == "도서산간":
    fee = delivery_fee(w, 6000)    # 기본값 대신 6000
else:
    fee = delivery_fee(w)          # 기본값 3500 사용
if fee == -1:
    print("배송 불가")
else:
    print(f"택배비: {fee}원")''',
        ['3 일반', '0.5 도서산간'], ['1 일반', '10 도서산간', '10.5 일반'],
        ['무게는 소수일 수 있으니 `float()` 로 바꿔요.', '구간은 작은 것부터 `if weight <= 1: return …` / `elif weight <= 5:` …',
         '도서산간이면 `delivery_fee(w, 6000)` 으로 두 번째 인자를 넣어 기본값을 덮어써요.'],
        '기본값 인자는 "대부분의 호출" 을 짧게 만들어 줘요. 경계값(1, 5, 10)은 `<=` 라서 아래 구간에 들어가는 점에 주의해요.')

    L.practice('[기출유사] 카페 주문서 (*menus, **requests)',
'''첫째 줄에 테이블 번호, 둘째 줄에 메뉴들(공백 구분), 셋째 줄에 요청 사항이 `이름=값` 모양으로 공백 구분되어 주어져요 (요청이 없으면 `없음`).

**[조건]**
- `def order(table, *menus, **requests):` 를 만들고 함수 안에서 출력해요.
- 첫 줄: `테이블번호번 테이블 / 메뉴 개수개`
- 메뉴는 `enumerate(menus, start=1)` 로 `번호. 메뉴` 출력
- 요청은 `requests.items()` 로 `- 이름: 값` 출력, 없으면 `- 요청 없음`
- 마지막 줄: `menus` 와 `requests` 의 자료형 이름 (`type(x).__name__`) 을 공백으로 출력
- 호출은 `order(table, *menu_list, **req_dict)` 처럼 풀어서 넣어요.

{ex}

{ex2}''',
'''def order(table, *menus, **requests):
    pass

table = int(input())
menu_list = input().split()
line = input()
''',
'''def order(table, *menus, **requests):
    print(f"{table}번 테이블 / {len(menus)}개")
    for no, m in enumerate(menus, start=1):
        print(f"{no}. {m}")
    if requests:                         # 빈 딕셔너리면 거짓
        for k, v in requests.items():
            print(f"- {k}: {v}")
    else:
        print("- 요청 없음")
    print(type(menus).__name__, type(requests).__name__)

table = int(input())
menu_list = input().split()
line = input()
req_dict = {}
if line != "없음":
    for item in line.split():
        k, v = item.split("=")           # "샷=추가" → "샷", "추가"
        req_dict[k] = v
order(table, *menu_list, **req_dict)     # 리스트·딕셔너리를 풀어서 넣기''',
        ['3\n라떼 케이크\n샷=추가 얼음=적게', '7\n아메리카노\n없음'], ['1\n물\n없음', '12\n a b c d\n포장=예', '5\n쿠키 쿠키\n시럽=1 샷=2 우유=두유'],
        ['`*menus` 는 튜플이라 `len(menus)` 와 enumerate 를 그대로 쓸 수 있어요.', '요청 줄은 `split()` 후 각각 `split("=")` 해서 딕셔너리에 담아요.',
         '호출 때 `*menu_list` 는 리스트를, `**req_dict` 는 딕셔너리를 풀어서 넣어요.'],
        '정의할 때의 `*`/`**` 는 **모으기**, 호출할 때의 `*`/`**` 는 **풀기**예요. 그래서 함수 안에서는 항상 tuple, dict 로 보여요.')

    L.essay('`def f(*args, **kwargs):` 에서 args 와 kwargs 가 각각 **어떤 인자를, 어떤 자료형으로** 받는지 서술하고, `f(1, 2, k=3)` 일 때 두 값을 쓰세요.',
        'args 는 이름 없이 넣은 위치 인자들을 모아 튜플로 받고, kwargs 는 이름=값 모양의 키워드 인자들을 모아 딕셔너리로 받는다. f(1, 2, k=3) 이면 args 는 (1, 2), kwargs 는 {"k": 3} 이다.',
        ['args 는 위치 인자 → 튜플', 'kwargs 는 키워드 인자 → 딕셔너리', 'args = (1, 2)', "kwargs = {'k': 3}"])

    # =====================================================================
    L = C.lesson('β-07 딕셔너리 ①: 만들기·get·누적·최댓값', 30,
'''- `d = {키: 값}`, 꺼내기 `d[키]`, 추가·수정 `d[키] = 값`.
- 없는 키를 `d[키]` 로 꺼내면 **KeyError**, `d.get(키, 기본값)` 은 안전.
- 세기 공식: `cnt[w] = cnt.get(w, 0) + 1`
- `keys()`·`values()`·`items()`, 최고 점수는 `max(d.values())`, 최빈은 **갱신 패턴**.
- `in` 은 **키**를 검사해요.''')

    L.review('🔁 지난 시간 복습',
        [T('지난 시간에는 기본값 인자, `*args`(튜플), `**kwargs`(딕셔너리) 를 배웠어요.\n'
           'kwargs 를 `.items()` 로 돌았던 것, 기억하죠? 오늘은 그 **딕셔너리**를 제대로 파헤쳐요.'),
         REVEAL_RUN('아래 코드의 출력은?', 'def f(a, b=5, *c, **d):\n    print(a, b, c, d)\nf(1)\nf(1, 2, 3, x=4)')])
    L.output('복습: 출력은?', 'def f(*nums, unit="점"):\n    return str(max(nums)) + unit\nprint(f(3, 9, 4))\nprint(f(7, unit="개"))',
        '`*nums` 뒤의 unit 은 **이름으로만** 넣을 수 있어요. 안 넣으면 기본값 "점".\n\n```\n{out}\n```', review=True)

    L.explain('딕셔너리 만들기와 꺼내기',
        [T('딕셔너리는 **키(key) → 값(value)** 의 짝을 모은 자료형이에요. 번호 대신 **이름표(키)** 로 꺼내요.\n'
           '`d[키] = 값` 은 키가 없으면 **추가**, 있으면 **수정**이에요.'),
         CODE('scores = {"민지": 88, "서준": 95}\nprint(scores["민지"])\nscores["하린"] = 72   # 추가\nscores["민지"] = 90   # 수정\nprint(scores)\nprint(len(scores))', '추가와 수정')],
        [T('없는 키를 `d[키]` 로 꺼내면 **KeyError** 로 멈춰요.\n'
           '`d.get(키)` 는 없으면 **None**, `d.get(키, 기본값)` 은 없으면 **기본값**을 돌려줘요.'),
         CMP(side('d[키]', '없으면 KeyError', 'd = {"a": 1}\nprint(d["z"])', 'bad', expect_error=True),
             side('d.get(키, 기본값)', '없으면 기본값', 'd = {"a": 1}\nprint(d.get("z"))\nprint(d.get("z", 0))\nprint(d.get("a", 0))', 'good')),
         KEY('`"z" in d` 는 **키**가 있는지 검사해요. 값을 검사하려면 `in d.values()`.')])

    L.spot('실행하면 **오류**가 나는 줄은?', '''\
stock = {"사과": 3, "배": 0}
print(stock.get("귤", 0))
stock["배"] += 5
print(stock["귤"])
print(stock)''', 4,
        '`get` 은 없는 키도 안전하지만, `stock["귤"]` 은 키가 없어서 **KeyError**. 3번 줄은 있는 키라 괜찮아요.', error_line=4)

    L.explain('누적 — 단어 빈도 세기',
        [T('딕셔너리의 단골 용도는 **세기**예요. 처음 나온 단어는 0 에서 시작해 1, 이미 있으면 +1.\n'
           '`get(w, 0)` 이 "없으면 0" 을 해 주니 if 없이 한 줄로 돼요.'),
         CMP(side('if 로 나누기', '', 'cnt = {}\nfor w in "a b a".split():\n    if w in cnt:\n        cnt[w] += 1\n    else:\n        cnt[w] = 1\nprint(cnt)', 'good'),
             side('get 한 줄', '', 'cnt = {}\nfor w in "a b a".split():\n    cnt[w] = cnt.get(w, 0) + 1\nprint(cnt)', 'good'))],
        [T('한 줄씩 따라가 보며 딕셔너리가 어떻게 자라는지 확인해 봐요.'),
         TRACE('text = "공부 운동 공부 독서 공부"\ncnt = {}\nfor w in text.split():\n    cnt[w] = cnt.get(w, 0) + 1\nprint(cnt)', '단어 빈도'),
         EXAM('2026년에 **split + dict.get** 단어 빈도가 그대로 나왔어요. `cnt.get(w, 0) + 1` 은 외워 두세요.')])

    L.fill('글자마다 몇 번 나왔는지 세는 코드를 완성하세요.',
        'cnt = {}\nfor ch in "banana":\n    cnt[ch] = cnt.___(ch, ___) + 1\nprint(cnt)', [['get'], ['0']],
        '없으면 0 부터 시작해야 하니 `cnt.get(ch, 0) + 1`.', expect="{'b': 1, 'a': 3, 'n': 2}")

    L.explain('keys · values · items 로 돌기',
        [T('`for k in d:` 는 **키**를 돌아요. 값까지 필요하면 `d.items()` 로 (키, 값) 을 함께 받아요.\n'
           '딕셔너리는 **넣은 순서**를 기억해요.'),
         TABS(('keys()', '키만', 'd = {"민지": 88, "서준": 95}\nfor k in d.keys():\n    print(k)'),
              ('values()', '값만', 'd = {"민지": 88, "서준": 95}\nprint(sum(d.values()))'),
              ('items()', '키와 값', 'd = {"민지": 88, "서준": 95}\nfor k, v in d.items():\n    print(f"{k}({v})")'))],
        [T('값만 모아서 쓰면 통계가 쉬워요.\n'
           '평균 `sum(d.values()) / len(d)`, 최고 점수 `max(d.values())`, 최저 `min(d.values())`.\n'
           '조건에 맞는 것만 모으려면 items + 컴프리헨션!'),
         CODE('scores = {"민지": 92, "서준": 85, "하린": 97}\nprint(sum(scores.values()) / len(scores))\nprint(max(scores.values()), min(scores.values()))\ntop = [f"{n}({s})" for n, s in scores.items() if s >= 90]\nprint(", ".join(top))', '통계 + 90점 이상'),
         WARN('`max(scores)` 는 **키** 중에서 최댓값(글자 순서로 가장 뒤)을 줘요. 점수 최댓값은 `max(scores.values())`!')])

    L.output('출력은?', 'd = {"b": 3, "a": 9, "c": 1}\nprint(max(d))\nprint(max(d.values()))\nprint("a" in d, 9 in d)',
        '`max(d)` 는 **키** 비교라 "c". `9 in d` 는 키 중에 9 가 있는지 묻는 거라 False.\n\n```\n{out}\n```')

    L.match('표현과 의미를 이어 보세요.',
        [['d[k]', '없으면 KeyError'], ['d.get(k, 0)', '없으면 0'], ['d.items()', '(키, 값) 쌍들'],
         ['k in d', '키가 있는지 검사'], ['len(d)', '키의 개수']],
        '`in` 과 `len` 은 모두 **키** 기준이에요.')

    L.short('`d = {"사과": 3, "배": 5}` 일 때 `d.get("귤", 0) + d.get("배", 0)` 의 값을 쓰세요.', '5',
        '"귤" 은 없어서 기본값 0, "배" 는 5. 0 + 5 = 5 예요.',
        check_code='d = {"사과": 3, "배": 5}\nprint(d.get("귤", 0) + d.get("배", 0))')

    L.explain('최댓값 주인 찾기 — 갱신 패턴',
        [T('"가장 많이 나온 단어" 처럼 **값이 최대인 키**가 필요할 때가 많아요.\n'
           '가장 기본은 **갱신 패턴**: 지금까지 최고(best)를 기억하고, 더 큰 값을 만나면 바꿔요.\n'
           '`>` 를 쓰면 동점일 때 **먼저 나온 것**이 남아요.'),
         TRACE('cnt = {"공부": 3, "운동": 1, "독서": 3}\nbest = ""\nbest_cnt = 0\nfor w, c in cnt.items():\n    if c > best_cnt:\n        best = w\n        best_cnt = c\nprint(best, best_cnt)', '최빈 갱신')],
        [T('같은 일을 `max(d, key=d.get)` 한 줄로도 할 수 있어요. "키들 중에서, d.get(키) 값이 가장 큰 키" 라는 뜻이에요.'),
         CODE('cnt = {"공부": 3, "운동": 1, "독서": 3}\nprint(max(cnt, key=cnt.get))', 'key= 사용'),
         THINK('`>` 대신 `>=` 를 쓰면 동점일 때 누가 남을까요? → **나중에 나온 것**("독서")이 남아요.')])

    L.order('딕셔너리 `scores` 에서 **최고 점수 학생 이름**을 찾는 코드를 순서대로 놓으세요.',
        ['scores = {"A": 70, "B": 95, "C": 88}', 'best, best_s = "", -1', 'for n, s in scores.items():', '    if s > best_s:',
         '        best, best_s = n, s', 'print(best)'],
        '처음 최고값은 어떤 점수보다 작게(-1), 돌면서 더 큰 값을 만나면 이름과 점수를 **같이** 바꿔요.',
        check=True, expect='B')

    L.choice('최빈 갱신 패턴에서 `if c > best_c:` 를 `if c >= best_c:` 로 바꾸면 어떻게 될까요?',
        ['오류가 난다', '동점일 때 나중에 나온 키가 남는다', '동점일 때 먼저 나온 키가 남는다', '결과가 항상 같다'], 2,
        '`>=` 는 같은 값일 때도 바꾸니까 동점이면 **나중에 나온 키**로 덮어써요. 시험 조건이 "먼저 나온 것" 이면 `>` 를 써야 해요.')

    L.practice('[기출유사] 성적 딕셔너리 분석',
'''첫째 줄에 학생 수 N, 다음 N 줄에 `이름 점수` 가 주어져요. 딕셔너리에 담아 분석하세요.

**[조건]**
- `scores` 딕셔너리(이름 → 점수)에 담아요.
- 1줄: `평균: ` + 평균(`round(값, 1)`)
- 2줄: `최고: ` + `max(scores.values())`, 3줄: `최저: ` + `min(scores.values())`
- 4줄: 90점 이상 학생을 입력 순서대로 `이름(점수)` 로 만들어 `, ` 로 이어 출력. 없으면 `90점 이상 없음`

{ex}

{ex2}''',
'''n = int(input())
scores = {}
# 이어서 작성하세요
''',
'''n = int(input())
scores = {}
for _ in range(n):
    name, s = input().split()
    scores[name] = int(s)                  # 이름 → 점수
vals = scores.values()
print("평균:", round(sum(vals) / len(scores), 1))
print("최고:", max(vals))
print("최저:", min(vals))
top = [f"{k}({v})" for k, v in scores.items() if v >= 90]
if top:
    print(", ".join(top))
else:
    print("90점 이상 없음")''',
        ['4\n민지 92\n서준 85\n하린 97\n도윤 60', '2\n가 89\n나 70'], ['1\n혼자 90', '3\nA 100\nB 100\nC 0', '2\nx 89\ny 91'],
        ['점수는 `int()` 로 바꿔서 `scores[name] = int(s)`.', '평균은 `sum(scores.values()) / len(scores)`.',
         '`[f"{k}({v})" for k, v in scores.items() if v >= 90]` 후 `", ".join(...)`.'],
        'items + 컴프리헨션 + join 은 "조건에 맞는 항목을 모양 맞춰 출력" 하는 만능 조합이에요. 경계 90점은 `>=` 라서 포함돼요.')

    L.practice('[기출유사] 가장 많이 나온 단어',
'''한 줄의 문장이 주어지면 단어별 빈도를 세서 **가장 많이 나온 단어**와 횟수를 출력하세요.

**[조건]**
- 대소문자는 구분하지 않아요 (모두 소문자로 바꿔서 세요).
- 빈도는 딕셔너리와 `get` 으로 세요.
- 최빈 단어는 **갱신 패턴**으로 찾고, 횟수가 같으면 **먼저 나온 단어**를 출력해요.
- 출력: 1줄 `단어 횟수`, 2줄 서로 다른 단어 수

{ex}

{ex2}''',
'''words = input().lower().split()
cnt = {}
# 이어서 작성하세요
''',
'''words = input().lower().split()
cnt = {}
for w in words:
    cnt[w] = cnt.get(w, 0) + 1     # 없으면 0 에서 시작
best, best_c = "", 0
for w, c in cnt.items():           # 넣은 순서 = 처음 나온 순서
    if c > best_c:                 # > 라서 동점이면 먼저 나온 단어 유지
        best, best_c = w, c
print(best, best_c)
print(len(cnt))''',
        ['I like python and I like code', 'Go go GO stop'], ['hello', 'a b c', 'x y y x z'],
        ['`cnt[w] = cnt.get(w, 0) + 1`', '딕셔너리는 넣은 순서를 기억하니 items() 순서가 곧 처음 나온 순서예요.',
         '`if c > best_c:` (>= 가 아니라 >) 로 갱신하면 동점일 때 앞의 단어가 남아요.'],
        '세기(get 누적) → 최댓값 주인 찾기(갱신) 는 딕셔너리 문제의 기본 2단 콤보예요.')

    L.essay('딕셔너리 `d` 에 없는 키 `"x"` 를 `d["x"]` 와 `d.get("x", 0)` 으로 꺼낼 때의 차이를 서술하고, 단어 빈도를 셀 때 get 이 편리한 이유를 쓰세요.',
        'd["x"] 는 키가 없으면 KeyError 가 나서 프로그램이 멈추지만, d.get("x", 0) 은 키가 없으면 기본값 0 을 돌려주어 오류가 나지 않는다. 단어 빈도를 셀 때 처음 나온 단어는 키가 없는데, cnt[w] = cnt.get(w, 0) + 1 로 쓰면 if 로 키가 있는지 따로 검사하지 않고 한 줄로 셀 수 있다.',
        ['d["x"] 는 KeyError', 'get 은 기본값을 돌려준다', '처음 나온 단어도 if 없이 한 줄로 센다'])

    # =====================================================================
    L = C.lesson('β-08 딕셔너리 ②: range 키·중첩·list of dict·삭제', 35,
'''- `{range(1, 10): "A구역"}` 처럼 **range 를 키**로 쓰고, for 로 돌며 `n in 범위` 로 구간 찾기.
- 중첩 딕셔너리: `members[아이디]["이름"]` 처럼 **대괄호 두 번**.
- list of dict: `[{"제목": …, "저자": …}, …]` 를 for 로 돌며 검색.
- 삭제: `del d[k]`(없으면 KeyError), `d.pop(k, 기본값)`(지운 값을 돌려줌).''')

    L.review('🔁 지난 시간 복습',
        [T('지난 시간에는 `get` 으로 안전하게 꺼내고, `cnt.get(w, 0) + 1` 로 세고, `items()` 로 돌며 최댓값 주인을 찾았어요.'),
         REVEAL_RUN('아래 코드의 출력은?', 'cnt = {}\nfor ch in "level":\n    cnt[ch] = cnt.get(ch, 0) + 1\nprint(cnt)\nprint(max(cnt, key=cnt.get))')])
    L.output('복습: 출력은?', 'd = {"민지": 92, "서준": 85}\nd["서준"] = d.get("서준", 0) + 10\nd["하린"] = d.get("하린", 0) + 10\nprint(d)\nprint([k for k, v in d.items() if v >= 90])',
        '있는 키는 원래 값에, 없는 키는 0 에 10 을 더해요.\n\n```\n{out}\n```', review=True)

    L.explain('range 를 키로 — 구간 찾기',
        [T('점수 구간·우편번호·주민번호 지역처럼 **범위마다 이름**이 붙는 표가 있어요.\n'
           '파이썬에서는 `range` 도 딕셔너리의 **키**가 될 수 있어요.\n'
           '그리고 `n in range(a, b)` 는 n 이 그 범위 안에 있는지 검사해요.'),
         CODE('zone = {range(0, 50): "1구역", range(50, 80): "2구역", range(80, 100): "3구역"}\nn = 63\nfor r, name in zone.items():\n    if n in r:\n        print(name)', '구간 이름 찾기')],
        [T('그런데 `zone[63]` 처럼 숫자로 바로 꺼내면 **KeyError** 예요. 키는 `range(50, 80)` 그 자체지 63 이 아니거든요.\n'
           '그래서 range 키 표는 **반드시 for 로 돌며 `in` 으로 검사**해요.'),
         CMP(side('정답 방식', 'for + in', 'zone = {range(0, 50): "1구역", range(50, 100): "2구역"}\nfor r, name in zone.items():\n    if 63 in r:\n        print(name)', 'good'),
             side('KeyError', '숫자로 바로 꺼내기', 'zone = {range(0, 50): "1구역", range(50, 100): "2구역"}\nprint(zone[63])', 'bad', expect_error=True)),
         WARN('`range(50, 80)` 에 80 은 **안 들어가요.** 경계값 문제의 단골이에요.')],
        [T('함수로 만들면 쓰기 편해요. 찾으면 바로 `return`, 끝까지 못 찾으면 `None`(또는 "없음") 을 돌려줘요.'),
         CODE('def find_zone(n):\n    zone = {range(0, 50): "1구역", range(50, 100): "2구역"}\n    for r, name in zone.items():\n        if n in r:\n            return name\n    return None\n\nprint(find_zone(10), find_zone(100))', '구간 찾기 함수'),
         EXAM('2023년 주민번호 지역, 2024년 우편번호 지역이 **range 키 딕셔너리** 로 나왔어요. 입력 검사(`len`, `isdigit`) + 메시지 여러 종류가 같이 붙어요.')])

    L.output('출력은?', 'table = {range(1, 4): "봄", range(4, 7): "여름", range(7, 10): "가을"}\nfor m in [3, 4, 9, 10]:\n    found = "없음"\n    for r, s in table.items():\n        if m in r:\n            found = s\n    print(m, found)',
        '`range(1, 4)` 는 1, 2, 3. 4 는 "여름" 쪽, 10 은 어느 범위에도 없어요.\n\n```\n{out}\n```')

    L.spot('번호 `25` 의 구역을 출력하려 했는데 **오류**가 나요. 오류가 나는 줄은?', '''\
zone = {range(1, 20): "A", range(20, 40): "B"}
num = 25
print(num in range(20, 40))
print(zone[num])''', 4,
        '키는 `range(20, 40)` 이지 25 가 아니라서 `zone[num]` 은 **KeyError** 예요. `for r, z in zone.items(): if num in r:` 로 찾아야 해요.', error_line=4)

    L.explain('중첩 딕셔너리 — 값이 또 딕셔너리',
        [T('딕셔너리의 **값**으로 딕셔너리를 넣을 수 있어요.\n'
           '회원 관리처럼 "아이디 하나에 정보 여러 개" 를 담을 때 써요.\n'
           '꺼낼 때는 **대괄호를 두 번**: `members["nest01"]["이름"]`'),
         CODE('members = {\n    "nest01": {"이름": "김둥지", "비번": "pw123456"},\n    "radio7": {"이름": "이방송", "비번": "onair777"},\n}\nprint(members["radio7"]["이름"])\nprint(len(members))', '방송부 회원 명부')],
        [T('새 회원 추가는 **바깥 키에 딕셔너리 통째로** 넣고, 정보 수정은 **두 번 들어가서** 바꿔요.\n'
           '가입 전 중복 검사는 `if 아이디 in members:` 예요.'),
         TRACE('members = {"nest01": {"이름": "김둥지", "비번": "pw123456"}}\nnew_id = "mic9"\nif new_id in members:\n    print("중복")\nelse:\n    members[new_id] = {"이름": "박마이크", "비번": "abc12345"}\nmembers["nest01"]["비번"] = "newpw999"\nfor uid, info in members.items():\n    print(uid, info["이름"], info["비번"])', '추가·수정·출력'),
         TIP('이메일에서 아이디만 뽑을 땐 `email.split("@")[0]` — β-02 에서 배운 그거예요!')])

    L.fill('회원 `"mic9"` 의 이름을 출력하고, 비밀번호를 `"z9z9z9z9"` 로 바꾸세요.',
        'members = {"mic9": {"이름": "박마이크", "비번": "abc12345"}}\nprint(members["mic9"][___])\nmembers[___]["비번"] = "z9z9z9z9"\nprint(members)',
        [['"이름"', "'이름'"], ['"mic9"', "'mic9'"]],
        '바깥 키(아이디) → 안쪽 키(정보 이름) 순서로 대괄호 두 번이에요.',
        expect="박마이크\n{'mic9': {'이름': '박마이크', '비번': 'z9z9z9z9'}}")

    L.explain('list of dict — 표(테이블) 다루기',
        [T('**딕셔너리들의 리스트**는 엑셀 표와 같아요. 리스트의 한 칸 = 한 줄(행), 딕셔너리의 키 = 열 이름.\n'
           '도서 목록·스터디원 명단처럼 **같은 모양의 기록이 여러 개**일 때 써요.'),
         CODE('books = [\n    {"제목": "Python Basic", "저자": "Kim", "대출": False},\n    {"제목": "Data Story", "저자": "Lee", "대출": True},\n]\nfor no, b in enumerate(books, start=1):\n    state = "대출중" if b["대출"] else "가능"\n    print(no, b["제목"], state)', '도서 목록')],
        [T('검색은 for 로 돌며 조건을 검사해요. **대소문자 무시** 검색은 둘 다 `lower()` 해서 `in` 으로 비교해요.\n'
           '컴프리헨션으로 한 줄 검색도 돼요.'),
         CODE('books = [{"제목": "Python Basic"}, {"제목": "Data Story"}, {"제목": "PYTHON Game"}]\nkey = "python"\nfound = [b["제목"] for b in books if key.lower() in b["제목"].lower()]\nprint(found)', '대소문자 무시 검색'),
         EXAM('2025년에 **도서 검색: enumerate + lower + in + 컴프리헨션** 이 나왔어요.')])

    L.output('출력은?', 'team = [{"이름": "A", "점수": 80}, {"이름": "B", "점수": 95}, {"이름": "C", "점수": 70}]\nteam.append({"이름": "D", "점수": 88})\nprint(len(team), team[1]["이름"])\nprint(sum(m["점수"] for m in team) // len(team))\nprint([m["이름"] for m in team if m["점수"] > 85])',
        '`team[1]` 은 두 번째 딕셔너리. 합은 333, 4 로 나눈 몫은 83.\n\n```\n{out}\n```')

    L.match('자료 구조와 꺼내는 코드를 이어 보세요.',
        [['{"id1": {"이름": "가"}}', 'd["id1"]["이름"]'], ['[{"이름": "가"}]', 'd[0]["이름"]'],
         ['{range(1, 5): "가"}', 'for r, v in d.items(): if n in r'], ['{"가": [1, 2]}', 'd["가"][1]']],
        '바깥이 딕셔너리면 **키**로, 리스트면 **번호**로 먼저 들어가요. range 키는 for + in.')

    L.explain('지우기 — del 과 pop',
        [T('`del d[키]` 는 그 키를 지워요. 없는 키면 **KeyError**.\n'
           '`d.pop(키)` 는 지우면서 **지운 값을 돌려줘요.** `d.pop(키, 기본값)` 은 없어도 오류 없이 기본값을 돌려줘요.'),
         CMP(side('del', '지우기만', 'd = {"a": 1, "b": 2}\ndel d["a"]\nprint(d)', 'good'),
             side('pop', '지우고 값 돌려받기', 'd = {"a": 1, "b": 2}\nv = d.pop("a")\nprint(v, d)\nprint(d.pop("z", "없음"))', 'good'))],
        [T('회원 탈퇴처럼 **없을 수도 있는 키**를 지울 땐 `if 키 in d:` 로 먼저 검사하거나 `pop(키, None)` 을 써요.\n'
           '또 딕셔너리를 **돌면서 지우면** RuntimeError 가 나요. 지울 키를 따로 모은 뒤 지우거나 `list(d)` 를 돌아요.'),
         CODE('d = {"a": 50, "b": 90, "c": 40}\nfor k in list(d):        # 키 목록을 복사해서 돌기\n    if d[k] < 60:\n        del d[k]\nprint(d)', '조건에 맞는 키 지우기'),
         WARN('list of dict 에서 한 줄을 지울 땐 리스트 메서드 `pop(번호)` / `remove(딕셔너리)` 를 써요.')])

    L.bucket('없는 키 `"z"` 로 실행했을 때 결과를 분류하세요. (`d = {"a": 1}`)', ['오류(KeyError)', '오류 없음'],
        [['del d["z"]', 1], ['d.pop("z")', 1], ['d.pop("z", 0)', 2], ['d.get("z")', 2], ['d["z"]', 1], ['d["z"] = 5', 2]],
        '꺼내거나 지울 때 기본값이 없으면 KeyError. `d["z"] = 5` 는 **추가**라서 괜찮아요.')

    L.ox('`d.pop("a")` 는 키 "a" 를 지우고, 지운 **값**을 돌려준다.', True,
         '그래서 `v = d.pop("a")` 처럼 받을 수 있어요. `del` 은 값을 돌려주지 않아요.')

    L.practice('[기출유사] 우편번호 지역 찾기',
'''다섯 자리 우편번호를 입력받아 지역을 알려 주세요. (번호표는 문제용으로 단순화한 가상의 표예요)

| 앞 두 자리 | 지역 |
|---|---|
| 01~09 | 서울 |
| 10~20 | 경기 |
| 34~35 | 대전 |
| 61~62 | 광주 |
| 63 | 제주 |

**[조건]**
- `area = {range(1, 10): "서울", range(10, 21): "경기", range(34, 36): "대전", range(61, 63): "광주", range(63, 64): "제주"}` 를 쓰세요.
- `find_area(code)` 함수는 앞 두 자리로 지역을 찾아 return, 없으면 `None` 을 return 해요.
- 입력이 5글자가 아니거나 숫자가 아닌 글자가 있으면 `형식 오류` (`len`, `isdigit` 사용)
- 표에 없으면 `없는 번호`, 있으면 `우편번호 지역: 지역`

{ex}

{ex2}''',
'''area = {range(1, 10): "서울", range(10, 21): "경기", range(34, 36): "대전",
        range(61, 63): "광주", range(63, 64): "제주"}

def find_area(code):
    pass

code = input()
''',
'''area = {range(1, 10): "서울", range(10, 21): "경기", range(34, 36): "대전",
        range(61, 63): "광주", range(63, 64): "제주"}

def find_area(code):
    front = int(code[:2])            # 앞 두 자리
    for r, name in area.items():     # range 키는 for + in 으로
        if front in r:
            return name
    return None                      # 끝까지 못 찾음

code = input()
if len(code) != 5 or not code.isdigit():
    print("형식 오류")
else:
    name = find_area(code)
    if name is None:
        print("없는 번호")
    else:
        print(f"우편번호 지역: {name}")''',
        ['61005', '3400'], ['00123', '6a005', '63999', '20999', '21000'],
        ['형식 검사를 **먼저** 해야 `int(code[:2])` 에서 오류가 안 나요.', '`for r, name in area.items(): if front in r: return name`',
         '함수가 None 을 돌려주면 `if name is None:` 으로 검사해요.'],
        '메시지가 3종(형식 오류/없는 번호/지역)일 땐 **검사 순서**가 중요해요. 형식이 틀린 입력으로 숫자 변환을 하면 ValueError 가 나니까요.')

    L.practice('[기출유사] 방송부 회원 가입',
'''첫째 줄에 가입 신청 수 N, 다음 N 줄에 `이메일 비밀번호 이름` 이 주어져요. 아이디는 이메일의 `@` 앞부분이에요.

**[조건]**
- `members` 중첩 딕셔너리(아이디 → `{"이름": …, "비번": …}`)에 저장해요.
- 각 신청마다 순서대로 검사해 한 줄씩 출력해요.
  - 아이디가 이미 있으면 `아이디: 중복 아이디`
  - 비밀번호가 8자 미만이거나, 영문자가 없거나, 숫자가 없으면 `아이디: 비밀번호 오류`
  - 통과하면 저장하고 `아이디: 가입 완료`
- 함수 `check_pw(pw)` 로 비밀번호 검사 결과(True/False)를 return 하세요.
- 마지막에 `회원 수: 수` 와, 회원마다 `아이디 - 이름` 을 가입 순서대로 출력해요.

{ex}

{ex2}''',
'''def check_pw(pw):
    pass

members = {}
n = int(input())
''',
'''def check_pw(pw):
    if len(pw) < 8:
        return False
    has_alpha = False
    has_digit = False
    for ch in pw:
        if ch.isalpha():
            has_alpha = True
        elif ch.isdigit():
            has_digit = True
    return has_alpha and has_digit   # 둘 다 있어야 True

members = {}
n = int(input())
for _ in range(n):
    email, pw, name = input().split()
    uid = email.split("@")[0]        # @ 앞부분이 아이디
    if uid in members:
        print(f"{uid}: 중복 아이디")
    elif not check_pw(pw):
        print(f"{uid}: 비밀번호 오류")
    else:
        members[uid] = {"이름": name, "비번": pw}
        print(f"{uid}: 가입 완료")
print(f"회원 수: {len(members)}")
for uid, info in members.items():
    print(uid, "-", info["이름"])''',
        ['3\nnest01@gsa.kr abc12345 김둥지\nradio@gsa.kr 12345678 이방송\nnest01@mail.com zz998877 박중복',
         '2\nmic@a.kr abcdefg1 최마이크\non@a.kr ab1 정온에어'],
        ['1\nx@y.z 1234567a 하나', '2\na@b.c abcdefgh 가\na@b.c abcdefg9 나', '3\np@q.r 1a2b3c4d 갑\np@s.t 9z9z9z9z 을\nq@q.q AAAA1111 병'],
        ['아이디는 `email.split("@")[0]`.', 'check_pw 는 길이 먼저 검사하고, for 로 돌며 `isalpha()`/`isdigit()` 깃발을 세워요.',
         '저장은 `members[uid] = {"이름": name, "비번": pw}`, 출력은 `for uid, info in members.items():`'],
        '중첩 딕셔너리는 "바깥 키 = 찾는 기준(아이디), 안쪽 = 그 사람의 정보" 예요. 중복 검사를 비밀번호 검사보다 먼저 하라는 **순서 조건**도 꼭 지켜요.')

    L.essay('`zone = {range(1, 50): "A", range(50, 100): "B"}` 에서 `zone[70]` 이 KeyError 가 나는 **이유**를 서술하고, 70 의 구역을 찾는 올바른 방법을 쓰세요.',
        '딕셔너리의 키는 range(1, 50), range(50, 100) 이라는 range 객체 자체이고, 정수 70 이라는 키는 없기 때문에 zone[70] 은 KeyError 가 난다. `for r, name in zone.items():` 로 키를 하나씩 돌면서 `if 70 in r:` 로 70 이 그 범위에 들어 있는지 검사해 맞으면 name 을 사용해야 한다.',
        ['키는 range 객체 자체다', '정수 70 키는 없다 → KeyError', 'for 로 items() 를 돌며 in 으로 검사'])
