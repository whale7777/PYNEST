import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lotc import *

C = Course('β', '1학년 1학기 2차고사 범위: 문자열 메서드(split·join·replace·find·count), 리스트 컴프리헨션, '
           'map·filter·zip·enumerate·lambda, 함수(return·기본값 인자·*args·**kwargs·지역/전역 변수), '
           '딕셔너리(누적·get·range 키·중첩·list of dict), set, 재귀 함수, 이진 탐색, 합병 정렬, 메뉴형 CRUD 프로그램')

# =====================================================================
L = C.lesson('β-01 시작하기: 2차 시험 지도 + α 실력 점검', 15,
'''- 1학기 2차는 **함수·딕셔너리·컴프리헨션·재귀·탐색/정렬**이 중심이에요.
- 큰 문항(14~20점)은 대부분 **함수 여러 개 + 딕셔너리 + 메뉴** 프로그램이에요.
- α 내용(리스트·문자열 슬라이싱·while·버블정렬)은 2차에서도 **도구**로 계속 써요.
- 이 코스는 개념 → 확인 문제 → 기출유사 실습 순서. 다 끝나면 **A.C.E. [β]** 로 실전!''')

L.explain('이번 시험은 이렇게 나와요',
    [T('1학년 1학기 **2차고사(기말)** 는 7~10문항, 100점이에요.\n'
       '문항은 크게 다섯 모양으로 나와요.'),
     STEPS(('A 출력 추론 (4~6점)', 'enumerate·재귀·컴프리헨션 코드의 출력을 손으로 따라가 적어요.'),
           ('B 빈칸 채우기 (9~14점)', '㉠~㉥ 빈칸에 들어갈 코드를 써요. 재귀·합병정렬 merge 가 단골이에요.'),
           ('C 조건 + 실행예시 작성 (10~16점)', '[조건]을 지키며 [실행예시]처럼 동작하는 코드를 써요.'),
           ('D 큰 프로그램 (15~20점)', '메뉴형 은행·도서관·스터디원 관리. 함수 여러 개 + 딕셔너리.'),
           ('E 서술형', '"왜 오류인가", "이 알고리즘이 왜 끝나지 않나" 를 조건과 연결해 써요.'))],
    [T('4개년 동안 **거의 매년** 나온 소재를 먼저 기억해 두세요.\n'
       '이 코스의 예제도 이 소재들을 **구조를 바꿔서** 다뤄요.'),
     FLIP(['딕셔너리', '4년 연속 출제 — 누적·get·range 키·중첩'],
          ['함수 분리 + 메뉴', '은행·스터디원·도서 관리 (3/4년)'],
          ['컴프리헨션·map·filter·zip·enumerate', '4년 연속 — 한 줄 코드·출력 추론'],
          ['재귀', '3/4년 — 점화식·호출 횟수·반복문 변환'],
          ['set', '합/교/차 메서드 vs 연산자, 중복 탐지'],
          ['이진탐색·합병정렬', '2026년 첫 등장 — 앞으로 계속 나올 가능성 큼'])],
    [T('공부 순서는 이렇게 추천해요.\n\n'
       '1. 레슨 하나를 끝까지(복습 → 개념 → 확인 → 실습).\n'
       '2. 틀린 문제는 🔁 오답 복습에서 다시.\n'
       '3. 모든 레슨이 끝나면 **A.C.E. [β]** 문제집으로 실전 연습.'),
     EXAM('시험지의 [조건]은 **채점 기준**이에요. "count() 사용 금지" 같은 조건을 어기면 답이 맞아도 감점돼요.')])

L.choice('다음 중 1학기 2차 시험의 **큰 문항(15~20점)** 으로 가장 자주 나온 형태는?',
    ['print 한 줄의 출력 맞히기', '함수 여러 개 + 딕셔너리로 만드는 메뉴형 프로그램',
     'random 으로 숫자 하나 뽑기', '변수 이름 규칙 고르기'], 2,
    '큰 문항은 은행·도서·스터디원처럼 **함수를 나눠 딕셔너리를 다루는 메뉴 프로그램**이 단골이에요. 나머지는 작은 문항 소재예요.')

L.explain('α 점검 ① 리스트와 슬라이싱',
    [T('2차 범위의 코드도 결국 **리스트·문자열**을 다뤄요. 빠르게 떠올려 봐요.\n'
       '인덱스는 0부터, 음수는 뒤에서부터. 슬라이싱 `a[s:e]` 는 **e 직전까지**예요.'),
     SLC('nums', [5, 3, 8, 1, 9, 2], 1, 5, 2)],
    [T('리스트 메서드 중 **원본을 바꾸는 것**과 **새 값을 돌려주는 것**을 구분해야 해요.'),
     CMP(side('원본을 바꿔요 (None 반환)', 'append · insert · remove · pop · sort · reverse',
              'a = [3, 1, 2]\na.sort()\nprint(a)', 'good'),
         side('새 값을 돌려줘요', 'sorted(a) · a[::-1] · a + b',
              'a = [3, 1, 2]\nb = sorted(a)\nprint(a, b)', 'good')),
     WARN('`a = a.sort()` 처럼 쓰면 `a` 가 **None** 이 돼요. sort() 는 결과를 돌려주지 않거든요.')])

L.output('출력 결과를 그대로 쓰세요.', '''\
a = [4, 7, 1, 9]
b = a
b.append(3)
c = a[:]
c.append(5)
print(a)
print(len(c))''',
    '`b = a` 는 **같은 리스트**를 가리키니 b 에 넣은 3 이 a 에도 보여요. `a[:]` 는 **복사본**이라 c 에 넣은 5 는 a 와 상관없어요.\n\n```\n{out}\n```')

L.explain('α 점검 ② while·버블정렬',
    [T('`while` 은 **조건이 참인 동안** 반복해요. 언제 멈출지(상태 변수, break)를 꼭 정해야 해요.\n'
       '버블정렬은 **옆 칸끼리 비교해 큰 값을 뒤로** 보내는 정렬이에요.'),
     TRACE('''\
a = [5, 2, 4, 1]
n = len(a)
for i in range(n - 1):
    for j in range(n - 1 - i):
        if a[j] > a[j + 1]:
            a[j], a[j + 1] = a[j + 1], a[j]
print(a)''', '버블정렬 한 줄씩 따라가기')],
    [T('한 바퀴(i) 돌 때마다 **가장 큰 값이 맨 뒤에 고정**돼요. 그래서 안쪽 반복은 `n - 1 - i` 까지만 돌면 돼요.'),
     KEY('부등호 `>` 를 `<` 로 바꾸면 **내림차순**이 돼요. 시험에서 "오름차순으로 고치시오" 로 자주 나와요.')])

L.fill('버블정렬을 **내림차순**으로 만드는 빈칸을 채우세요.', '''\
a = [3, 8, 1, 6]
n = len(a)
for i in range(n - 1):
    for j in range(n - 1 - i):
        if a[j] ___ a[j + 1]:
            a[j], a[j + 1] = a[j + 1], a[j]
print(a)''', [['<']],
    '앞 칸이 **더 작으면** 바꿔야 큰 값이 앞으로 와요. 그래서 `a[j] < a[j + 1]` 일 때 교환해요. 결과는 `[8, 6, 3, 1]`.',
    expect='[8, 6, 3, 1]')

L.match('α 에서 배운 도구와 쓰임을 이어 보세요.',
    [['s[::-1]', '문자열 뒤집기'], ['n % 10', '일의 자리 숫자'], ['n // 10', '일의 자리 떼어 내기'],
     ['break', '반복 즉시 멈추기'], ['continue', '이번 반복만 건너뛰기']],
    '2차 문제에서도 이 다섯 개는 그대로 도구로 써요. 특히 `% 10`, `// 10` 은 자릿수 문제, `[::-1]` 은 회문 문제에 나와요.')

L.spot('실행하면 **오류**가 나는 줄은?', '''\
word = "python"
print(word[0])
print(word[-1])
word[0] = "P"
print(word)''', 4,
    '문자열은 **불변(immutable)** 이라 칸 하나를 바꿀 수 없어요 → `TypeError`. 바꾸려면 `"P" + word[1:]` 처럼 새 문자열을 만들어요.',
    error_line=4)

L.ox('`while True:` 반복문은 안에 `break` 가 없으면 끝나지 않는다.', True,
     '`True` 는 항상 참이니 `break`(또는 프로그램 종료)가 없으면 무한 반복이에요. 도어락·메뉴 프로그램은 이 구조에 **종료 조건 + break** 를 둬요.')

L.explain('α 점검 ③ 입력 받기 한 줄 패턴',
    [T('2차 시험은 **한 줄에 여러 숫자**를 받는 일이 많아요.\n'
       '`input().split()` 은 공백으로 잘라 **글자 리스트**를 만들고, `map(int, …)` 이 하나씩 정수로 바꿔요.'),
     CODE('nums = list(map(int, input().split()))\nprint(nums)\nprint(sum(nums))', '여러 숫자 입력', stdin='3 9 4\n'),
     TIP('`a, b = map(int, input().split())` 처럼 바로 두 변수에 나눠 담을 수도 있어요.')])

L.bucket('각 코드의 결과 자료형을 분류해 보세요.', ['문자열(str)', '리스트(list)', '정수(int)'],
    [['input()', 1], ['input().split()', 2], ['len("abc")', 3], ['"a,b".split(",")', 2],
     ['"-".join(["a", "b"])', 1], ['int("7")', 3]],
    '`input()` 은 항상 글자, `split()` 은 글자들의 **리스트**, `join()` 은 다시 **글자 하나**로 합쳐요.')

L.practice('[기출유사] 점수 처리 — 최고·최저 빼고 평균',
'''심사위원 점수가 **한 줄에 공백으로** 주어져요. 가장 높은 점수 1개와 가장 낮은 점수 1개를 빼고 나머지의 평균을 **소수 첫째 자리까지 반올림**해 출력하세요.

**[조건]**
- 점수는 3개 이상, 모두 정수예요.
- `list(map(int, input().split()))` 으로 입력을 받으세요.
- 평균은 `round(값, 1)` 로 반올림해요.

{ex}

{ex2}''',
'''scores = list(map(int, input().split()))
# 최고·최저를 하나씩 빼고 평균을 출력하세요
''',
'''scores = list(map(int, input().split()))
scores.remove(max(scores))   # 최고점 하나 빼기
scores.remove(min(scores))   # 최저점 하나 빼기
print(round(sum(scores) / len(scores), 1))''',
    ['7 9 8 10 6', '85 92 77'], ['5 5 5 5', '100 0 50 51', '1 2 3 4 5 6 7 8 9 10'],
    ['최고점은 `max(scores)`, 최저점은 `min(scores)` 로 찾아요.',
     '`remove(값)` 은 그 값을 **하나만** 지워요. 같은 점수가 여러 개여도 하나만 빠져요.',
     '마지막은 `print(round(sum(scores) / len(scores), 1))`'],
    '`remove` 는 값을 하나만 지우기 때문에 최고점이 두 개여도 한 개만 빠져요. 정렬 후 `scores[1:-1]` 로 잘라도 같은 결과예요.')

L.essay('`a = [3, 1, 2]` 다음에 `a = a.sort()` 를 실행하고 `print(a)` 를 하면 어떻게 되는지, **이유와 함께** 서술하세요.',
    '`None` 이 출력된다. `sort()` 는 리스트 원본을 정렬하고 아무 값도 돌려주지 않으므로(None 반환) 그 반환값 None 이 a 에 다시 저장되기 때문이다. 정렬된 리스트를 얻으려면 `a.sort()` 만 쓰거나 `a = sorted(a)` 를 써야 한다.',
    ['None 이 출력된다', 'sort() 는 원본을 바꾸고 None 을 반환한다', '반환값 None 이 a 에 저장된다', 'a.sort() 또는 sorted(a) 로 고친다'])

# =====================================================================
L = C.lesson('β-02 문자열 무기: split·join·replace·find·count', 25,
'''- `split(구분자)` → 리스트, `구분자.join(리스트)` → 문자열 (서로 반대!)
- `replace(a, b)` 는 **새 문자열**을 돌려줘요. 원본은 그대로.
- `find` 는 없으면 **-1**, `index` 는 없으면 **ValueError**.
- `count` 금지 조건이면 for 로 직접 세요.
- `s == s[::-1]` 이면 회문.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간에는 2차 시험의 모양과 α 핵심(리스트 복사, 버블정렬, 한 줄 입력)을 점검했어요.'),
     REVEAL_RUN('`list(map(int, "4 5 6".split()))` 의 결과는?', 'print(list(map(int, "4 5 6".split())))')])
L.output('복습: 출력은?', 'a = [1, 2, 3]\nb = a[:]\nb[0] = 9\nprint(a[0] + b[0])',
    '`a[:]` 는 복사본이라 b[0] 만 9 가 되고 a[0] 은 1 그대로예요. 1 + 9 = {out}', review=True)

L.explain('split 과 join — 자르고 붙이기',
    [T('`split()` 은 문자열을 **잘라서 리스트**로 만들어요. 괄호 안이 비면 **공백(여러 칸도 하나로)** 기준이에요.\n'
       '`split("@")` 처럼 구분자를 주면 그 글자를 기준으로 잘라요.'),
     CODE('email = "nest2026@pynest.kr"\nparts = email.split("@")\nprint(parts)\nprint(parts[0], parts[1])', 'split 체험')],
    [T('`join` 은 반대예요. **구분자 문자열**이 앞에 오고, 괄호 안에 **문자열 리스트**를 넣어요.'),
     CMP(side('맞아요', '구분자.join(리스트)', 'words = ["red", "blue"]\nprint("-".join(words))', 'good'),
         side('틀려요', '리스트에 join 은 없어요', 'words = ["red", "blue"]\nprint(words.join("-"))', 'bad', expect_error=True)),
     WARN('`join` 할 리스트에 **숫자가 있으면 TypeError**. `"-".join(map(str, nums))` 처럼 글자로 바꿔야 해요.')])

L.output('출력은?', 'line = "  apple   banana  kiwi "\nwords = line.split()\nprint(len(words))\nprint("/".join(words))',
    '인자 없는 `split()` 은 여러 칸 공백과 앞뒤 공백을 모두 무시해요. 그래서 단어 3개.\n\n```\n{out}\n```')

L.fill('전화번호 `010-1234-5678` 에서 가운데 4자리만 꺼내 출력하세요.', '''\
phone = "010-1234-5678"
parts = phone.___("-")
print(parts[___])''', [['split'], ['1']],
    '`split("-")` 하면 `["010", "1234", "5678"]` 이 되고, 가운데는 인덱스 **1** 이에요.', expect='1234')

L.explain('replace · find · count',
    [T('`replace(old, new)` 는 old 를 **모두** new 로 바꾼 **새 문자열**을 돌려줘요.\n'
       '문자열은 불변이라 원본은 그대로예요. 결과를 쓰려면 변수에 다시 담아요.'),
     CODE('s = "banana"\nt = s.replace("a", "o")\nprint(s)\nprint(t)', 'replace 는 새 문자열')],
    [T('찾기 도구는 두 가지예요. **없을 때** 반응이 달라요.'),
     CMP(side('find', '없으면 **-1** 을 돌려줘요 (오류 없음)', 's = "hello"\nprint(s.find("l"))\nprint(s.find("z"))', 'good'),
         side('index', '없으면 **ValueError** 로 멈춰요', 's = "hello"\nprint(s.index("z"))', 'bad', expect_error=True)),
     EXAM('2026년 1차에 `list.index` 의 ValueError 를 `in` 으로 미리 검사하는 문제가 나왔어요. `if x in s:` 로 먼저 확인하는 습관!')],
    [T('`count(글자)` 는 몇 번 나오는지 세요. 그런데 시험엔 **"count() 사용 금지"** 조건이 자주 붙어요.\n'
       '그럴 땐 for 로 한 글자씩 보며 직접 세면 돼요.'),
     TABS(('count 사용', '', 's = "2026-07-17"\nprint(s.count("7"))'),
          ('직접 세기', '', 's = "2026-07-17"\ncnt = 0\nfor ch in s:\n    if ch == "7":\n        cnt += 1\nprint(cnt)'))])

L.choice('`s = "mississippi"` 일 때 값이 **-1** 인 것은?',
    ['s.find("s")', 's.count("z")', 's.find("ss", 5)', 's.find("x")'], 4,
    '`find("x")` 는 x 가 없어 -1. `find("s")`=2, `count("z")`=0, `find("ss", 5)` 는 5번부터 찾아 5 예요.')

L.output('출력은?', 's = "level up level"\nprint(s.count("level"))\nprint(s.replace("level", "LV", 1))\nprint(s.find("up"))',
    '`replace` 의 세 번째 인자 1 은 **앞에서 1개만** 바꾸라는 뜻이에요.\n\n```\n{out}\n```')

L.explain('뒤집기와 회문',
    [T('`s[::-1]` 은 step 이 -1 이라 **뒤에서부터 한 칸씩** 읽어요. 그래서 뒤집힌 문자열이 돼요.'),
     SLC('s', 'LEVEL', None, None, -1)],
    [T('**회문**은 앞으로 읽으나 뒤로 읽으나 같은 말이에요. `s == s[::-1]` 한 줄로 판별해요.\n'
       '대소문자·공백을 무시하라는 조건이 있으면 먼저 `lower()`, `replace(" ", "")` 로 정리해요.'),
     CODE('s = "Was it a car or a cat I saw"\nt = s.lower().replace(" ", "")\nprint(t)\nprint(t == t[::-1])', '정리 후 회문 검사'),
     TIP('메서드는 `.` 으로 **이어 쓸 수 있어요**. 왼쪽부터 차례로 실행돼요.')])

L.order('문장의 **단어 순서**를 뒤집어 출력하는 코드를 순서대로 놓으세요. (입력: `I love python` → `python love I`)',
    ['s = input()', 'words = s.split()', 'words = words[::-1]', 'print(" ".join(words))'],
    '자르기(split) → 뒤집기([::-1]) → 붙이기(join). 글자가 아니라 **단어 리스트**를 뒤집는 게 포인트예요.',
    check=True, stdin='I love python\n', expect='python love I')

L.spot('`count` 를 쓰지 않고 `a` 의 개수를 세려 했는데 **결과가 틀려요**. 잘못된 줄은?', '''\
s = "banana"
cnt = 0
for ch in s:
    if ch == "a":
        cnt = 1
print(cnt)''', 5,
    '`cnt = 1` 은 매번 1 로 **덮어써요**. 하나씩 더하려면 `cnt += 1`. 지금 코드는 3 이 아니라 1 을 출력해요.')

L.practice('[기출유사] 아이디 정리기',
'''회원가입 아이디가 이메일 형식으로 한 줄 주어져요. 다음 순서로 처리해 출력하세요.

**[조건]**
- `@` 앞부분(아이디)만 사용해요. (`split` 사용)
- 아이디의 **대문자는 소문자로** 바꿔요.
- 아이디에 들어 있는 `.` 은 모두 지워요. (`replace` 사용)
- 첫째 줄: 정리된 아이디, 둘째 줄: 아이디 글자 수
- 셋째 줄: 아이디가 회문이면 `회문`, 아니면 `회문 아님`

{ex}

{ex2}''',
'''email = input()
# 이어서 작성하세요
''',
'''email = input()
user = email.split("@")[0]          # @ 앞부분
user = user.lower().replace(".", "")  # 소문자 + 점 지우기
print(user)
print(len(user))
if user == user[::-1]:
    print("회문")
else:
    print("회문 아님")''',
    ['Kim.Nest@pynest.kr', 'A.n.N.a@mail.com'], ['abc@x.y', 'x@a.b', '...RaCeCaR...@z.com'],
    ['`email.split("@")[0]` 이 아이디예요.', '`lower()` 와 `replace(".", "")` 를 이어 쓰면 한 줄로 돼요.',
     '회문 검사: `if user == user[::-1]:`'],
    '메서드를 이어 쓰면(`lower().replace(...)`) 왼쪽부터 차례로 적용돼요. 점을 지운 **뒤에** 회문을 검사해야 해요.')

L.practice('[기출유사] 7 이 몇 번? (count 금지)',
'''양의 정수 N 이 주어질 때, 1 부터 N 까지의 모든 수를 적었을 때 숫자 **7** 이 모두 몇 번 쓰이는지 출력하세요.

**[조건]**
- `count()` 함수를 사용하지 않아요. (자동 채점은 결과만 보지만, 시험이라면 감점이에요)
- 각 수를 `str()` 로 바꾸고 한 글자씩 비교하세요.

{ex}

{ex2}''',
'''n = int(input())
total = 0
# 1부터 n까지 7을 세세요
print(total)''',
'''n = int(input())
total = 0
for i in range(1, n + 1):
    for ch in str(i):      # 수를 글자로 바꿔 한 글자씩
        if ch == "7":
            total += 1
print(total)''',
    ['20', '77'], ['6', '7', '1000'],
    ['바깥 for 로 1~N, 안쪽 for 로 `str(i)` 의 글자를 하나씩 봐요.', '`if ch == "7": total += 1`',
     '77 에는 7 이 두 번! 글자 단위로 세야 해요.'],
    '숫자를 문자열로 바꾸면 자릿수를 글자 하나하나로 다룰 수 있어요. `% 10` 과 `// 10` 으로 자릿수를 떼어 내도 같은 결과예요.')

L.essay('`s.find("z")` 와 `s.index("z")` 의 차이를 **"찾는 글자가 없을 때"** 를 중심으로 서술하고, index 를 안전하게 쓰는 방법을 쓰세요.',
    'find 는 찾는 글자가 없으면 -1 을 돌려주어 프로그램이 계속 실행되지만, index 는 없으면 ValueError 가 발생해 프로그램이 멈춘다. index 를 쓰기 전에 `if "z" in s:` 로 들어 있는지 먼저 확인하면 안전하다.',
    ['find 는 없으면 -1', 'index 는 없으면 ValueError', 'in 으로 먼저 검사한다'])

import beta2, beta3
beta2.build(C)
beta3.build(C)

if __name__ == '__main__':
    C.save(sys.argv[1] if len(sys.argv) > 1 else '/tmp/beta.json')
