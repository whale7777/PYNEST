from glib import *

# ============================================================ G1
G1 = lesson('1강. 예외 심화 — 어느 줄에서, 어떤 입력으로, 무엇이 나는가', 45,
'- 예외가 난 줄에서 try 블록의 **나머지는 건너뛰고** 맞는 except 로 간다\n- except 는 **위에서부터** 검사 — 넓은 것(`Exception`)이 위에 있으면 아래는 죽은 코드\n- `else` 는 예외가 **없을 때만**, `finally` 는 **무조건**(return·break 가 있어도) 실행\n- 함수 안에서 못 잡은 예외는 **호출한 쪽으로** 올라간다\n- `raise ValueError("메시지")` 로 직접 발생, `except ValueError as e:` 의 `e` 가 메시지\n- 서술형 3요소: **발생 줄 + 예외 이름 + 이유(어떤 값 때문에)**',
review('🔁 [β] 복습', [T('2학기는 1학기 문법 위에 쌓여요. 손이 기억하는지 확인해요.'), flip(['`d.get(k, 0)` 을 쓰는 이유', '키가 없어도 KeyError 없이 기본값'], ['`"a,b".split(",")` 의 결과 자료형', '문자열의 리스트'], ['`[int(x) for x in s.split()]` 과 같은 map 표현', 'list(map(int, s.split()))'], ['set 에 넣을 수 없는 것', '리스트·딕셔너리(변경 가능한 것)'])]),
outq('복습 — 출력 결과는?', D('''
d = {}
for w in "to be or not to be".split():
    d[w] = d.get(w, 0) + 1
best = max(d, key=d.get)
print(best, d[best], len(d), sorted(d)[0])
'''), review=True),
explain('예외가 나는 순간, 흐름이 꺾인다',
  [T('1학기에는 오류가 나면 프로그램이 끝났어요. 2학기 시험은 **"오류가 나도 끝나지 않게"** 만드는 법을 묻고, 더 나아가 **"몇 번째 줄에서, 왜"** 를 서술하게 해요(2023 1번 12점, 2024 6번 15점).'),
   trace(D('''
data = ["10", "x", "30"]
total = 0
for s in data:
    try:
        n = int(s)
        total += n
        print("더함", n)
    except ValueError:
        print("건너뜀", s)
print(total)
'''), '예외가 난 줄 아래(total += n)는 실행되지 않아요'),
   key('`int("x")` 에서 예외가 나면 그 **아래 두 줄은 건너뛰고** 바로 except 로 가요. try 안에 줄이 많을수록 "어디까지 실행됐는지"를 따져야 해요.')],
  [T('시험에 나오는 예외는 정해져 있어요. **이름과 원인을 짝지어** 외우세요.'),
   tabs(['ValueError', '자료형은 맞는데 **값**이 부적절', 'int("3.5")\nint("abc")\n[1, 2].index(9)\n"a b".split("")'], ['IndexError', '시퀀스의 **범위 밖** 번호', 'a = [1, 2, 3]\na[3]\n"abc"[5]\n[].pop()'], ['KeyError', '딕셔너리에 **없는 키**', 'd = {"a": 1}\nd["b"]\ndel d["z"]'], ['TypeError', '**자료형**이 맞지 않는 연산', '"3" + 4\nlen(5)\n[1, 2] + (3,)'], ['ZeroDivisionError', '0 으로 나눔 (`/`, `//`, `%` 모두)', '10 / 0\n10 % 0'], ['FileNotFoundError', '읽으려는 파일이 없음', 'open("없는파일.txt", "r")'], ['AttributeError', '그 객체에 **없는 속성·메서드**', '"abc".push("d")\n[1, 2].add(3)']),
   warn('`int("3.5")` 는 TypeError 가 아니라 **ValueError** 예요. 문자열이라는 자료형은 맞고, 그 값이 정수 모양이 아닐 뿐이에요. 반대로 `int([1])` 은 TypeError.')],
  [T('except 가 여러 개면 **위에서부터** 맞는지 검사해요. 그래서 순서가 뜻을 바꿔요.'),
   cmp('넓은 것이 위 ❌', 'try:\n    print([1, 2][5])\nexcept Exception:\n    print("알 수 없는 오류")\nexcept IndexError:\n    print("범위 오류")', '좁은 것이 위 ✅', 'try:\n    print([1, 2][5])\nexcept IndexError:\n    print("범위 오류")\nexcept Exception:\n    print("알 수 없는 오류")', lb='IndexError 도 Exception 의 한 종류라 위에서 잡혀요. 아래 except 는 절대 실행되지 않아요.', rb='구체적인 예외 먼저, Exception 은 맨 아래', tones=('bad', 'good')),
   tip('한 except 로 여러 예외를 묶으려면 **튜플**: `except (ValueError, IndexError):`')]),
explain('else · finally · raise',
  [T('try 문의 네 칸은 실행 조건이 모두 달라요.'),
   steps(['try', '일단 실행. 예외가 나면 그 줄에서 멈춤'], ['except', '예외가 **났을 때만** (종류가 맞는 첫 번째 하나)'], ['else', '예외가 **없었을 때만** — try 가 끝까지 간 뒤'], ['finally', '**무조건**. 예외가 나도, 안 나도, return 을 만나도']),
   C(D('''
def div(a, b):
    try:
        r = a // b
    except ZeroDivisionError:
        print("0 으로 나눌 수 없음")
        return -1
    else:
        print("성공")
        return r
    finally:
        print("정리")
print(div(7, 2))
print(div(7, 0))
'''), 'return 을 만나도 finally 는 실행된 뒤에 돌아가요'),
   key('출력 순서: `성공` → `정리` → `3`. **return 값이 정해진 뒤 finally 가 실행되고, 그다음에 함수가 끝나요.**')],
  [T('`raise` 는 예외를 **직접 발생**시켜요. "파이썬은 오류가 아니라고 보지만 우리 규칙으로는 틀린 값"을 걸러낼 때 써요.'),
   C(D('''
def set_score(s):
    if not 0 <= s <= 100:
        raise ValueError(f"점수 범위 오류: {s}")
    return s
for x in [90, 120, -5]:
    try:
        print(set_score(x))
    except ValueError as e:
        print("오류 →", e)
'''), 'as e 로 받은 e 를 출력하면 raise 에 넣은 메시지가 나와요'),
   T('함수 안에서 잡지 않은 예외는 **호출한 쪽으로 올라가요**. 올라가다 try 를 만나면 거기서 잡히고, 끝까지 못 만나면 프로그램이 멈춰요.'),
   C(D('''
def inner():
    print("A")
    int("x")
    print("B")
def outer():
    inner()
    print("C")
try:
    outer()
except ValueError:
    print("D")
print("E")
'''), 'B 와 C 는 출력되지 않아요')],
  [exam('2024 6번(15점): 코드를 주고 **① KeyError 가 나는 줄과 입력 예시 ② IndexError 가 나는 줄과 입력 예시 ③ ValueError …** 를 쓰게 했어요. 푸는 법은 하나예요 — 각 줄에서 "**입력이 어떤 값이면** 이 연산이 실패하는가"를 거꾸로 생각해요.'),
   CX(D('''
menu = {"라면": 3000, "김밥": 2500}      # 1
order = input().split()                 # 2
name = order[0]                         # 3
count = int(order[1])                   # 4
print(menu[name] * count)               # 5
'''), '입력에 따라 세 줄에서 서로 다른 예외가 나요'),
   tabs(['3번 줄', '빈 줄 입력 → `order == []` → `order[0]` 에서 **IndexError**. (4번 줄은 `라면` 만 입력했을 때 IndexError)'], ['4번 줄', '`라면 두개` → `int("두개")` 에서 **ValueError**'], ['5번 줄', '`우동 2` → `menu["우동"]` 에서 **KeyError**']),
   key('서술 틀: "**N번 줄**에서 **(값)** 을 (연산)하려 하므로 **○○Error** 가 발생한다." 줄·값·이름 세 가지가 모두 있어야 만점이에요.')]),
outq('[기출유사] 출력 결과는?', D('''
a = [3, 0, "5", 2]
for x in a:
    try:
        print(12 // x, end=" ")
    except ZeroDivisionError:
        print("Z", end=" ")
    except TypeError:
        print("T", end=" ")
    else:
        print("ok", end=" ")
    finally:
        print("|", end=" ")
'''), '`12 // "5"` 는 숫자와 문자열의 연산이라 TypeError 예요. else 는 성공한 3 과 2 에서만 실행돼요.'),
outq('[기출유사] 출력 결과는?', D('''
def load(d, k):
    try:
        v = d[k]
        print("찾음")
        return v * 2
    except KeyError:
        print("없음")
        return 0
    finally:
        print("끝")
d = {"a": 4}
print(load(d, "a") + load(d, "b"))
'''), '덧셈을 하려면 두 호출이 **모두 끝나야** 해요. 그래서 `8` 은 맨 마지막에 출력돼요.'),
spot('[기출유사] `data = {"민": [90, 85], "솔": [70]}` 일 때 **예외가 발생하는 줄**은?', D('''
data = {"민": [90, 85], "솔": [70]}
names = sorted(data)
first = data[names[0]]
total = first[0] + first[1]
second = data[names[1]]
total += second[0] + second[1]
print(total)
'''), 6, '`second == [70]` 이라 `second[1]` 에서 IndexError 가 나요. 5번 줄까지는 정상이에요.'),
ch('[기출유사] 아래 코드에 `7 0` 을 입력하면 출력은?\n\n```\ntry:\n    a, b = map(int, input().split())\n    print(a / b)\nexcept ValueError:\n    print("입력 오류")\nexcept Exception:\n    print("계산 오류")\nelse:\n    print("완료")\n```', ['입력 오류', '계산 오류', '완료', '아무것도 출력되지 않고 프로그램이 멈춘다'], 2, 'ZeroDivisionError 는 ValueError 가 아니라서 첫 except 를 지나치고, Exception 에서 잡혀요. 예외가 났으니 else 는 실행되지 않아요.'),
bucket('[기출유사] 위 `menu` 코드(`order = input().split()` → `order[0]` → `int(order[1])` → `menu[name]`)에 넣는 **입력**을, 발생하는 예외로 나눠 보세요.', ['IndexError', 'ValueError', 'KeyError', '정상'], [['(빈 줄)', 1], ['김밥', 1], ['김밥 2.5', 2], ['라면 하나', 2], ['떡볶이 1', 3], ['라면  3', 4], ['김밥 0', 4], ['우동 x', 2]], '`우동 x` 는 4번 줄(`int("x")`)이 5번 줄보다 **먼저** 실행되므로 ValueError 예요. `split()` 은 공백이 여러 개여도 잘 잘라요.'),
outq('[심화] 출력 결과는?', D('''
def f(x):
    try:
        if x < 0:
            raise ValueError("음수")
        return 10 // x
    except ValueError as e:
        return str(e)
    finally:
        print("f", x)
out = []
for x in [5, -1, 0]:
    try:
        out.append(f(x))
    except ZeroDivisionError:
        out.append("0!")
print(out)
'''), '`f(0)` 의 ZeroDivisionError 는 f 안에서 잡히지 않아 바깥으로 올라가요. 그래도 f 의 finally 는 실행돼요.'),
fill('[기출유사] 나이가 0~150 이 아니면 **직접 예외를 발생**시키고, 그 메시지를 받아 출력해요.', D('''
def check(age):
    if age < 0 or age > 150:
        ___ ValueError("범위 밖")
    return age
try:
    check(200)
except ValueError ___ e:
    print(e)
'''), ['raise', 'as'], expect='범위 밖'),
essay('[기출유사 · 서술 6점] 아래 코드에서 `숫자 아님` 이 **절대 출력되지 않는 이유**를 쓰고, 고치는 방법을 서술하세요.\n\n```\ntry:\n    n = int(input())\n    print(100 // n)\nexcept Exception:\n    print("오류")\nexcept ValueError:\n    print("숫자 아님")\n```', 'except 는 위에서부터 차례로 검사하는데, ValueError 는 Exception 의 한 종류(하위 예외)이므로 int() 에서 ValueError 가 발생해도 첫 번째 except Exception 에서 먼저 잡힌다. 따라서 두 번째 except ValueError 는 실행될 수 없다. except ValueError 를 위로, except Exception 을 맨 아래로 순서를 바꾸면 된다.', ['except 를 위에서부터 차례로 검사한다고 썼다', 'ValueError 가 Exception 에 포함된다(하위 예외)고 썼다', '첫 except 에서 먼저 잡혀 아래가 실행되지 않는다고 썼다', '구체적인 예외를 위로 올린다고 고쳤다']),
essay('[기출유사 · 서술 6점] `nums = [int(x) for x in input().split()]` 다음 줄 `print(sum(nums) / len(nums))` 이 있어요. **빈 줄**을 입력했을 때 어느 줄에서 어떤 예외가 왜 나는지 서술하세요.', '빈 줄을 입력하면 input().split() 은 빈 리스트 [] 가 되고, 컴프리헨션은 반복할 것이 없어 오류 없이 nums = [] 가 된다. 따라서 첫 줄은 정상이고, 둘째 줄에서 len(nums) 가 0 이므로 sum(nums) / 0 을 계산하려다 ZeroDivisionError 가 발생한다.', ['첫 줄은 오류 없이 빈 리스트가 된다고 썼다', '둘째 줄에서 발생한다고 썼다', 'len 이 0 이라 0 으로 나눈다고 이유를 썼다', 'ZeroDivisionError 라고 이름을 썼다'], '함정은 "첫 줄의 int 에서 ValueError" 라고 쓰는 거예요. 변환할 조각이 **하나도 없으면** int 는 호출조차 되지 않아요.'),
order('try 문의 네 칸을 **쓰는 순서대로** 놓으세요.', ['try:', 'except ValueError:', 'else:', 'finally:'], '`else` 는 except 뒤, finally 앞에만 올 수 있어요.', code=False, mono=True),
prac('[기출유사 · 10점] 숫자만 골라 더하기', '공백으로 구분된 토큰이 한 줄 주어져요. **정수로 바꿀 수 있는 것만** 더하고, 바꿀 수 없는 토큰은 건너뛰어요.\n\n출력: 첫 줄에 합, 둘째 줄에 건너뛴 토큰을 입력 순서대로 공백 구분(없으면 `없음`), 셋째 줄에 정수 토큰의 평균을 소수 둘째 자리까지(`:.2f`). 정수 토큰이 하나도 없으면 셋째 줄은 `평균 없음`.\n\n[조건] ○ `isdigit` 으로 걸러내지 말고 **try / except ValueError** 를 사용할 것 (음수 `-3` 도 정수예요) ○ 평균은 **ZeroDivisionError 를 잡아** 처리할 것',
D('''
tokens = input().split()
total = 0
cnt = 0
bad = []
for t in tokens:
    try:
        total += int(t)
        cnt += 1
    except ValueError:
        bad.append(t)
print(total)
if bad:
    print(*bad)
else:
    print("없음")
try:
    print(f"{total / cnt:.2f}")
except ZeroDivisionError:
    print("평균 없음")
'''), ['10 x -3 4.5 7', 'a b c', '1 2 3 4', '-5 +5 0x1 12', '3.0 3', '100 -100 백'],
  starter=D('''
tokens = input().split()
total = 0
cnt = 0
bad = []
for t in tokens:
    try:
        pass  # 정수로 바꿔 더하기
    except ValueError:
        pass  # 건너뛴 토큰 모으기
'''), hints=['`total += int(t)` 가 실패하면 그 아래 `cnt += 1` 은 실행되지 않아요 — 순서가 중요해요.', '`int("+5")` 는 5, `int("4.5")` 와 `int("0x1")` 은 ValueError', '평균: `try: print(f"{total / cnt:.2f}")` / `except ZeroDivisionError:`'], ex='`"-3".isdigit()` 은 False 라서 isdigit 으로는 음수를 놓쳐요. **"해 보고 안 되면 잡는다"** 가 더 정확한 이유예요.'),
prac('[기출유사 · 15점] 성적 조회기 — 예외 3종', '첫 줄에 학생 수 `n`, 이어서 n 줄에 `이름 점수1 점수2 …` (점수는 1개 이상)가 주어져요. 그다음 줄부터 조회 명령이 `이름 번호` 형식으로 주어지고 `끝` 에서 종료해요. 번호는 **1부터** 세요.\n\n명령마다 한 줄 출력:\n- 정상: `이름 번호차: 점수`\n- 조각이 2개가 아니거나 번호가 정수가 아님: `형식 오류`\n- 없는 이름: `없는 학생`\n- 번호가 범위 밖(0 이하 포함): `없는 회차`\n\n검사 순서는 형식 → 이름 → 번호예요. 마지막 줄에 정상 조회 횟수를 `조회 N회` 로 출력해요.\n\n[조건] ○ **ValueError, KeyError, IndexError 를 각각의 except** 로 처리할 것 ○ 번호가 0 이하일 때는 `raise IndexError` 로 직접 발생시킬 것',
D('''
n = int(input())
data = {}
for _ in range(n):
    p = input().split()
    data[p[0]] = list(map(int, p[1:]))
ok = 0
while True:
    line = input()
    if line == "끝":
        break
    try:
        name, num = line.split()
        num = int(num)
        scores = data[name]
        if num < 1:
            raise IndexError
        print(f"{name} {num}차: {scores[num - 1]}")
        ok += 1
    except ValueError:
        print("형식 오류")
    except KeyError:
        print("없는 학생")
    except IndexError:
        print("없는 회차")
print(f"조회 {ok}회")
'''), ['2\n민 90 85 70\n솔 60\n민 2\n솔 2\n율 1\n민 둘\n민\n민 0\n끝', '1\n가 100\n끝', '1\n가 100\n가 1\n가 1\n가 -1\n나 x\n가 1 2\n끝', '3\na 1 2\nb 3\nc 4 5 6\nc 3\nb 1\na 3\nd 1\nc 0\n끝', '2\nx 5 5\ny 7\ny 1.0\nz z\nx 2\n끝'],
  starter=D('''
n = int(input())
data = {}
for _ in range(n):
    p = input().split()
    data[p[0]] = list(map(int, p[1:]))
ok = 0
while True:
    line = input()
    if line == "끝":
        break
    try:
        name, num = line.split()
        # 이어서 작성
    except ValueError:
        print("형식 오류")
print(f"조회 {ok}회")
'''), hints=['`name, num = line.split()` 은 조각이 2개가 아니면 **ValueError** 를 내요(언패킹 개수 불일치).', '`data[name]` 이 KeyError, `scores[num - 1]` 이 IndexError', '`num - 1` 이 음수면 파이썬은 뒤에서부터 세어 오류가 안 나요 → `if num < 1: raise IndexError`'], ex='`나 x` 는 왜 `없는 학생` 이 아니라 `형식 오류` 일까요? `int("x")` 가 `data[name]` 보다 **먼저 실행**되기 때문이에요. 예외의 종류는 "어느 줄이 먼저 실패하느냐"가 정해요.'),
prac('[심화 · 12점] 검증 함수와 예외 메시지', '회원 가입 정보를 검사하는 함수 `validate(uid, pw, age)` 를 만들어요. 문제가 있으면 **`raise ValueError(메시지)`** 로 알리고, 없으면 `True` 를 반환해요. 검사는 아래 순서로 하고 **처음 걸린 것 하나만** 알려요.\n\n1. 아이디가 4~10자가 아님 → `아이디 길이`\n2. 아이디가 영문자·숫자로만 이루어지지 않음 → `아이디 문자`\n3. 비밀번호가 8자 미만 → `비밀번호 길이`\n4. 비밀번호에 숫자가 하나도 없거나 영문자가 하나도 없음 → `비밀번호 구성`\n5. 나이가 정수가 아님 → `나이 형식` / 14 미만 → `나이 제한`\n\n입력: 첫 줄 `n`, 이어서 n 줄에 `아이디 비밀번호 나이`. 출력: 줄마다 `아이디: 가입 완료` 또는 `아이디: 메시지`. 마지막 줄에 `성공 a명 / 실패 b명`.\n\n[조건] ○ validate 안에서는 print 하지 말 것 ○ 나이의 `int()` 변환 실패도 validate 안에서 잡아 `나이 형식` 메시지로 **다시 raise** 할 것',
D('''
def validate(uid, pw, age):
    if not 4 <= len(uid) <= 10:
        raise ValueError("아이디 길이")
    if not uid.isalnum() or not uid.isascii():
        raise ValueError("아이디 문자")
    if len(pw) < 8:
        raise ValueError("비밀번호 길이")
    has_d = any(c.isdigit() for c in pw)
    has_a = any(c.isalpha() for c in pw)
    if not (has_d and has_a):
        raise ValueError("비밀번호 구성")
    try:
        age = int(age)
    except ValueError:
        raise ValueError("나이 형식")
    if age < 14:
        raise ValueError("나이 제한")
    return True
n = int(input())
ok = fail = 0
for _ in range(n):
    uid, pw, age = input().split()
    try:
        validate(uid, pw, age)
        print(f"{uid}: 가입 완료")
        ok += 1
    except ValueError as e:
        print(f"{uid}: {e}")
        fail += 1
print(f"성공 {ok}명 / 실패 {fail}명")
'''), ['4\nmin01 abcd1234 16\nab abcd1234 16\nsol_2 abcd1234 16\nyul77 abcdefgh 16', '3\nuser1 pass1234 열다섯\nuser2 pass1234 13\nuser3 1234567 20', '1\nabcdefghijk aaaa1111 20', '2\ngood1 12345678 30\ngood2 a2345678 14', '3\nzz99 zz99zz99 14\nzz9 zz99zz99 14\nzz99 zz99 14', '2\nhello hello123 99\nhello! hello1234 99'],
  hints=['`raise ValueError("아이디 길이")` — 걸리는 즉시 함수가 끝나므로 뒤 검사는 자동으로 건너뛰어요.', '영문자·숫자만: `uid.isalnum()` (한글도 True 라서 `uid.isascii()` 를 함께 검사)', '나이: `try: age = int(age)` / `except ValueError: raise ValueError("나이 형식")`'], ex='검사 함수는 **판단만** 하고, 출력은 호출한 쪽이 `except … as e` 로 받아서 해요. 이렇게 나누면 같은 함수를 다른 프로그램에서도 그대로 쓸 수 있어요 — 4강(모듈)에서 이어져요.'),
)

# ============================================================ G2
G2 = lesson('2강. 파일 심화 — 모드·포인터·줄바꿈이 만드는 함정', 45,
'- `"w"` 는 **여는 순간** 내용을 모두 지운다 / `"a"` 는 끝에 이어 쓴다 / `"r"` 은 없으면 FileNotFoundError\n- `write` 는 **문자열만**, 줄바꿈을 **자동으로 붙이지 않는다**\n- `read()` 전체 문자열 / `readline()` 한 줄 / `readlines()` 줄 리스트 — 줄 끝의 `\\n` 이 **포함**된다 → `strip()`\n- 한 번 끝까지 읽으면 **포인터가 끝**에 있어 다시 읽으면 빈 문자열\n- `with` 블록을 나가면 자동으로 닫힌다 — 닫힌 뒤 읽으면 ValueError\n- CSV 는 `line.strip().split(",")`, 저장은 `",".join(…) + "\\n"`',
review('🔁 1강 복습', [T('예외의 흐름을 확인해요.'), rev('try 안에서 예외가 나면 그 아래 줄은?', '건너뛰고 맞는 except 로 가요.'), rev('`else` 와 `finally` 의 차이는?', 'else 는 예외가 **없을 때만**, finally 는 **무조건**.'), rev('`int("3.5")` 의 예외 이름은?', 'ValueError')]),
outq('복습 — 출력 결과는?', D('''
def g(s):
    try:
        return int(s)
    except ValueError:
        return 0
    finally:
        print("<" + s + ">", end="")
print(g("7") + g("x") + g("-2"))
'''), review=True),
explain('모드 세 가지와 write 의 성질',
  [T('파일 문제의 절반은 **모드**에서 갈려요(2025 2학기 2차 2번 14점: 경로·누적·모드).'),
   C(D('''
with open("log.txt", "w", encoding="utf-8") as f:
    f.write("첫째\\n")
with open("log.txt", "a", encoding="utf-8") as f:
    f.write("둘째\\n")
with open("log.txt", "w", encoding="utf-8") as f:
    f.write("셋째\\n")
with open("log.txt", "a", encoding="utf-8") as f:
    f.write("넷째\\n")
with open("log.txt", "r", encoding="utf-8") as f:
    print(f.read())
'''), 'w 로 다시 여는 순간 앞의 두 줄이 사라져요'),
   flip(['"r"', '읽기. 파일이 없으면 FileNotFoundError'], ['"w"', '쓰기. 없으면 만들고, **있으면 비운다**'], ['"a"', '이어 쓰기. 없으면 만들고, 있으면 끝에 추가'], ['모드를 생략하면', '"r"']),
   warn('`open("data.txt", "w")` 는 **write 를 한 번도 안 해도** 파일을 비워요. "읽으려고 열었는데 w 로 열어서 자료가 사라졌다"가 단골 서술 문제예요.')],
  [T('`write` 는 `print` 와 달라요.'),
   cmp('print', 'print("a", 3)\nprint("b")', 'write', 'f.write("a")\nf.write(str(3))\nf.write("b")\n# 파일 내용: a3b', lb='여러 값·숫자 OK, 줄바꿈 자동', rb='문자열 **하나만**, 줄바꿈 없음. 숫자는 str() 로', tones=('', '')),
   C(D('''
scores = [90, 85, 70]
with open("s.txt", "w", encoding="utf-8") as f:
    for s in scores:
        f.write(str(s) + "\\n")
    f.write(",".join(map(str, scores)))
with open("s.txt", encoding="utf-8") as f:
    print(f.read())
'''), '숫자를 쓰는 두 가지 방법: 한 줄에 하나 / join 으로 한 줄에'),
   tip('`print("내용", file=f)` 로도 쓸 수 있어요. 이때는 print 처럼 줄바꿈이 붙어요.')]),
explain('읽는 네 가지 방법과 포인터',
  [T('읽는 방법에 따라 **결과의 자료형**이 달라요. 그리고 모든 줄 끝에는 `\\n` 이 붙어 있어요.'),
   C(D('''
with open("t.txt", "w", encoding="utf-8") as f:
    f.write("apple\\nbanana\\ncherry")
with open("t.txt", encoding="utf-8") as f:
    a = f.read()
with open("t.txt", encoding="utf-8") as f:
    b = f.readline()
with open("t.txt", encoding="utf-8") as f:
    c = f.readlines()
print(len(a), len(b), len(c))
print(c)
print([x.strip() for x in c])
'''), '마지막 줄 cherry 뒤에는 \\n 이 없어요 (쓴 그대로)'),
   tabs(['f.read()', '파일 전체를 **문자열 하나**로', 'text = f.read()\nwords = text.split()'], ['f.readline()', '**한 줄**을 문자열로 (줄바꿈 포함). 더 없으면 `""`', 'first = f.readline().strip()'], ['f.readlines()', '모든 줄을 **리스트**로 (각 줄에 줄바꿈 포함)', 'lines = f.readlines()\nn = len(lines)'], ['for line in f', '한 줄씩 반복 — 가장 많이 쓰는 형태', 'for line in f:\n    line = line.strip()']),
   key('`"banana\\n" == "banana"` 는 **False**. 파일에서 읽은 줄을 비교하거나 `int()` 가 아닌 곳에 쓰려면 반드시 `strip()`. (`int("12\\n")` 은 되지만 `"12\\n".isdigit()` 은 False 예요.)')],
  [T('파일을 읽으면 **포인터**(어디까지 읽었는지)가 앞으로 가요. 끝까지 간 뒤에는 더 읽을 것이 없어요.'),
   C(D('''
with open("p.txt", "w", encoding="utf-8") as f:
    f.write("1\\n2\\n3\\n")
with open("p.txt", encoding="utf-8") as f:
    first = f.readline()
    rest = f.readlines()
    again = f.read()
print(repr(first), rest, repr(again))
'''), 'readline 이 한 줄 가져간 뒤, readlines 는 남은 줄만'),
   warn('`n = len(f.readlines())` 로 줄 수를 센 뒤 `for line in f:` 를 돌리면 **한 번도 반복하지 않아요**. 줄 리스트를 변수에 담아 두 번 쓰세요.'),
   CX(D('''
with open("p.txt", encoding="utf-8") as f:
    pass
print(f.read())   # ValueError: I/O operation on closed file
'''), 'with 블록을 나가면 닫혀요')],
  [T('**CSV** 는 쉼표로 나눈 텍스트일 뿐이에요. 2024 2번(14점)처럼 `split(",")` 과 `join` 으로 직접 다뤄요.'),
   C(D('''
with open("score.csv", "w", encoding="utf-8") as f:
    f.write("이름,국어,수학\\n민,90,80\\n솔,70,100\\n")
with open("score.csv", encoding="utf-8") as f:
    header = f.readline().strip().split(",")
    rows = [line.strip().split(",") for line in f]
print(header)
for r in rows:
    print(r[0], sum(map(int, r[1:])))
'''), '첫 줄(제목)은 readline 으로 먼저 떼어 내요'),
   exam('인코딩: 한글 파일은 `encoding="utf-8"` 을 써요. 저장한 방식(`euc-kr`/`cp949`)과 다르게 읽으면 **UnicodeDecodeError** 가 나거나 글자가 깨져요(2023 2학기 2차 11번).')]),
outq('[기출유사] 출력 결과는?', D('''
with open("a.txt", "w", encoding="utf-8") as f:
    f.write("x")
    f.write("y\\n")
    f.write("z")
with open("a.txt", "a", encoding="utf-8") as f:
    f.write("w\\n")
with open("a.txt", encoding="utf-8") as f:
    lines = f.readlines()
print(len(lines), lines[1].strip(), len(lines[0]))
'''), '파일 내용은 `xy\\nzw\\n` — 두 줄이에요. `lines[0]` 은 `"xy\\n"` 이라 길이 3.'),
outq('[기출유사] 출력 결과는?', D('''
with open("n.txt", "w", encoding="utf-8") as f:
    for i in range(1, 6):
        f.write(str(i * 10) + "\\n")
with open("n.txt", encoding="utf-8") as f:
    a = f.readline()
    b = f.readline()
    c = [int(x) for x in f]
    d = f.read()
print(int(a) + int(b), sum(c), len(d))
'''), '`for x in f` 는 **남은 줄**(30, 40, 50)만 돌아요. 그 뒤 read 는 빈 문자열.'),
spot('[기출유사] **예외가 발생하는 줄**은?', D('''
total = 0
with open("sum.txt", "w") as f:
    for n in [3, 4, 5]:
        total += n
        f.write(f"{n}\\n")
    f.write(total)
print("저장 완료")
'''), 6, '`write` 는 문자열만 받아요. `f.write(str(total))` 이어야 해요. 5번 줄은 f-string 이라 문자열이에요.'),
ch('[기출유사] `words.txt` 에 `cat\\ndog\\n` 이 들어 있어요. 아래 코드의 출력은?\n\n```\nwith open("words.txt") as f:\n    words = f.readlines()\nprint("dog" in words)\n```', ['True', 'False', 'ValueError', 'dog'], 2, '리스트의 원소는 `"dog\\n"` 이라 `"dog"` 과 달라요. `[w.strip() for w in f]` 로 읽어야 True 가 돼요.'),
fill('[기출유사] 점수 리스트를 **한 줄에 쉼표로** 저장하고, 다시 읽어 합을 구해요.', D('''
s = [80, 95, 70]
with open("c.csv", "w", encoding="utf-8") as f:
    f.write(",".___(map(str, s)))
with open("c.csv", encoding="utf-8") as f:
    back = f.read().___(",")
print(sum(map(int, back)))
'''), ['join', 'split'], expect='245'),
match('표현과 결과를 이어 보세요. (파일 내용: `a b\\nc\\n`)', [['f.read()', '"a b\\nc\\n"'], ['f.readline()', '"a b\\n"'], ['f.readlines()', '["a b\\n", "c\\n"]'], ['f.read().split()', '["a", "b", "c"]'], ['len(f.readlines())', '2']], '`read().split()` 은 공백·줄바꿈을 모두 구분자로 봐서 단어 리스트가 돼요.'),
outq('[심화] 출력 결과는?', D('''
with open("m.txt", "w", encoding="utf-8") as f:
    f.write("b,2\\na,5\\nb,3\\nc,1\\na,1\\n")
d = {}
with open("m.txt", encoding="utf-8") as f:
    for line in f:
        k, v = line.strip().split(",")
        d[k] = d.get(k, 0) + int(v)
with open("m.txt", "a", encoding="utf-8") as f:
    f.write(f"합,{sum(d.values())}\\n")
with open("m.txt", encoding="utf-8") as f:
    last = f.readlines()[-1].strip()
print(sorted(d.items()), last)
'''), 'a 모드로 연 덕분에 앞의 다섯 줄이 남아 있고, 여섯 번째 줄이 추가돼요.'),
essay('[기출유사 · 서술 6점] 방문 기록을 저장하는 함수예요. 실행할 때마다 **기록이 한 줄만 남는 문제**가 있어요. 원인을 쓰고 고치세요.\n\n```\ndef save(name):\n    with open("visit.txt", "w") as f:\n        f.write(name)\n```', '"w" 모드는 파일을 열 때마다 기존 내용을 모두 지우고 새로 쓰기 때문에 이전 방문 기록이 사라지고 마지막 이름만 남는다. 모드를 "a"(이어 쓰기)로 바꿔야 한다. 또한 write 는 줄바꿈을 자동으로 붙이지 않으므로 f.write(name + "\\n") 으로 고쳐야 이름이 한 줄에 하나씩 저장된다.', ['"w" 모드가 기존 내용을 지운다고 썼다', '"a" 모드로 바꾼다고 썼다', 'write 가 줄바꿈을 붙이지 않는다는 점을 썼다', 'name + "\\n" 으로 고쳤다'], '모드만 고치면 `민솔율` 처럼 붙어서 저장돼요. 두 가지를 다 써야 만점이에요.'),
ox('`with open("a.txt", "r") as f:` 에서 파일이 없으면 빈 파일이 새로 만들어진다.', False, '`"r"` 은 만들지 않고 FileNotFoundError 를 내요. 만들어 주는 건 `"w"` 와 `"a"` 예요.'),
prac('[기출유사 · 14점] 단어 빈도를 CSV 로', '첫 줄에 줄 수 `n`, 이어서 n 줄의 영어 문장이 주어져요.\n\n1. 문장들을 받은 그대로 `memo.txt` 에 한 줄씩 저장해요.\n2. `memo.txt` 를 **다시 읽어** 단어 빈도를 세요. 대소문자는 구분하지 않고(소문자로 통일), 단어 양 끝의 `.` `,` `!` `?` 는 떼어 내요.\n3. 결과를 `count.csv` 에 `단어,횟수` 형식으로 한 줄씩 저장해요. 순서는 **횟수 내림차순, 같으면 단어 사전순**.\n4. `count.csv` 를 다시 읽어 **위에서 3줄**(3줄보다 적으면 전부)을 그대로 출력하고, 마지막 줄에 `단어 종류: N` 을 출력해요.\n\n[조건] ○ 2번은 반드시 파일에서 읽은 내용으로 셀 것 ○ 4번의 N 은 `count.csv` 의 줄 수로 구할 것',
D('''
n = int(input())
with open("memo.txt", "w", encoding="utf-8") as f:
    for _ in range(n):
        f.write(input() + "\\n")
cnt = {}
with open("memo.txt", encoding="utf-8") as f:
    for line in f:
        for w in line.split():
            w = w.lower().strip(".,!?")
            if w:
                cnt[w] = cnt.get(w, 0) + 1
rows = sorted(cnt.items(), key=lambda p: (-p[1], p[0]))
with open("count.csv", "w", encoding="utf-8") as f:
    for w, c in rows:
        f.write(f"{w},{c}\\n")
with open("count.csv", encoding="utf-8") as f:
    lines = f.readlines()
for line in lines[:3]:
    print(line.strip())
print(f"단어 종류: {len(lines)}")
'''), ['2\nThe cat and the dog.\nThe dog runs!', '1\nHello', '3\na b c\nb c\nc', '2\nTo be, or not to be?\nBe happy.', '1\nwow! Wow, WOW? wow.', '2\none two\nthree four five'],
  starter=D('''
n = int(input())
with open("memo.txt", "w", encoding="utf-8") as f:
    for _ in range(n):
        f.write(input() + "\\n")
cnt = {}
with open("memo.txt", encoding="utf-8") as f:
    for line in f:
        pass  # 단어를 세기
'''), hints=['단어 다듬기: `w.lower().strip(".,!?")` — strip 에 여러 글자를 주면 그 글자들을 양 끝에서 모두 떼요.', '정렬: `sorted(cnt.items(), key=lambda p: (-p[1], p[0]))`', '출력할 때 `line.strip()` 을 하지 않으면 빈 줄이 하나씩 끼어요.'], ex='"저장 → 다시 읽기 → 가공 → 저장 → 다시 읽기"가 2024 2번(14점)의 뼈대예요. 읽은 줄에는 `\\n` 이 붙어 있다는 것만 끝까지 기억하면 돼요.'),
prac('[기출유사 · 12점] 파일 합치기와 없는 파일', '첫 줄에 파일 수 `n`, 이어서 n 줄에 `파일이름 내용` 이 주어져요(내용은 공백을 포함할 수 있고, 같은 파일 이름이 다시 나오면 **그 파일에 줄을 추가**해요). 그다음 한 줄에 합칠 파일 이름들이 공백으로 주어져요.\n\n합칠 파일들을 **주어진 순서대로** 읽어 `merged.txt` 에 이어 붙여요. 없는 파일을 만나면 `[없음] 파일이름` 을 출력하고 계속 진행해요.\n\n출력: 없는 파일 안내(해당하는 경우) → `merged.txt` 의 내용을 줄 번호와 함께 `1: 내용` 형식으로 → 마지막 줄에 `총 N줄`. 합쳐진 줄이 하나도 없으면 줄 번호 부분 없이 `총 0줄` 만 출력해요.\n\n[조건] ○ 없는 파일은 **FileNotFoundError 를 잡아** 처리할 것 (이름을 미리 기억해 두고 비교하지 말 것)',
D('''
n = int(input())
made = set()
for _ in range(n):
    name, text = input().split(" ", 1)
    mode = "a" if name in made else "w"
    made.add(name)
    with open(name, mode, encoding="utf-8") as f:
        f.write(text + "\\n")
targets = input().split()
with open("merged.txt", "w", encoding="utf-8") as out:
    for t in targets:
        try:
            with open(t, encoding="utf-8") as f:
                out.write(f.read())
        except FileNotFoundError:
            print(f"[없음] {t}")
with open("merged.txt", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    print(f"{i}: {line.strip()}")
print(f"총 {len(lines)}줄")
'''), ['3\nga.txt 첫 번째 파일\nna.txt 두 번째 파일\nga.txt 가 의 둘째 줄\nna.txt g2_missing_x.txt ga.txt', '1\nq1.txt hello world\ng2_missing_y.txt g2_missing_z.txt', '2\nr1.txt a\nr2.txt b\nr2.txt r1.txt r2.txt', '2\ns1.txt one\ns1.txt two\ns1.txt', '3\nt1.txt x y z\nt2.txt 1 2\nt3.txt !\nt3.txt g2_missing_w.txt t1.txt t2.txt'],
  starter=D('''
n = int(input())
made = set()
for _ in range(n):
    name, text = input().split(" ", 1)
    mode = "a" if name in made else "w"
    made.add(name)
    with open(name, mode, encoding="utf-8") as f:
        f.write(text + "\\n")
targets = input().split()
# 이어서 작성: merged.txt 로 합치기
'''), hints=['`split(" ", 1)` 은 **첫 공백에서 한 번만** 잘라요 — 내용의 공백을 지켜 줘요.', '`try:` 안에서 `with open(t) as f:` 로 열고 `out.write(f.read())`', '같은 파일을 두 번 합치라고 하면 두 번 붙여요. merged.txt 는 `"w"` 로 한 번만 열어야 해요.'], ex='starter 의 `mode` 줄을 보세요. 처음 보는 이름은 `"w"`(새로 만들기), 이미 만든 이름은 `"a"`(이어 쓰기) — 모드를 **상황에 따라 고르는** 코드예요.'),
prac('[심화 · 14점] 이어 쓰는 일지', '일지 프로그램을 만들어요. 시작할 때 `diary.txt` 를 **빈 파일로** 만들고, 명령을 한 줄씩 처리하다 `종료` 에서 끝내요.\n\n- `쓰기 내용` : 내용을 파일 끝에 한 줄 추가하고 `저장 (N번째 줄)` 출력\n- `보기` : 모든 줄을 `번호. 내용` 으로 출력. 비어 있으면 `빈 일지`\n- `찾기 단어` : 그 단어를 **포함한** 줄의 번호를 공백으로 구분해 출력. 없으면 `없음`\n- `지우기 번호` : 그 번호의 줄을 지우고 `삭제 완료`. 번호가 정수가 아니면 `번호 오류`, 범위 밖이면 `없는 줄`\n- `비우기` : 파일을 비우고 `초기화`\n\n[조건] ○ 줄 목록을 리스트 변수에 계속 들고 있지 말고, **명령마다 파일을 열어** 처리할 것 ○ `쓰기` 는 `"a"`, `지우기` 는 전체를 읽은 뒤 `"w"` 로 다시 쓸 것',
D('''
FILE = "diary.txt"
def load():
    with open(FILE, encoding="utf-8") as f:
        return [line.rstrip("\\n") for line in f]
def save(lines):
    with open(FILE, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\\n")
save([])
while True:
    cmd = input()
    if cmd == "종료":
        break
    if cmd.startswith("쓰기 "):
        with open(FILE, "a", encoding="utf-8") as f:
            f.write(cmd[3:] + "\\n")
        print(f"저장 ({len(load())}번째 줄)")
    elif cmd == "보기":
        lines = load()
        if not lines:
            print("빈 일지")
        for i, line in enumerate(lines, 1):
            print(f"{i}. {line}")
    elif cmd.startswith("찾기 "):
        word = cmd[3:]
        hit = [str(i) for i, line in enumerate(load(), 1) if word in line]
        print(" ".join(hit) if hit else "없음")
    elif cmd.startswith("지우기 "):
        try:
            k = int(cmd[4:])
            lines = load()
            if not 1 <= k <= len(lines):
                raise IndexError
            del lines[k - 1]
            save(lines)
            print("삭제 완료")
        except ValueError:
            print("번호 오류")
        except IndexError:
            print("없는 줄")
    elif cmd == "비우기":
        save([])
        print("초기화")
'''), ['보기\n쓰기 파이썬 공부 시작\n쓰기 클래스는 어렵다\n쓰기 파이썬 재밌다\n찾기 파이썬\n지우기 2\n보기\n종료', '쓰기 a\n지우기 x\n지우기 5\n지우기 0\n지우기 1\n보기\n종료', '쓰기 one two\n쓰기 two three\n찾기 two\n찾기 four\n비우기\n보기\n쓰기 again\n보기\n종료', '찾기 a\n비우기\n종료', '쓰기 1\n쓰기 2\n쓰기 3\n지우기 1\n지우기 1\n쓰기 4\n보기\n찾기 4\n종료'],
  hints=['읽기 함수 `load()` 와 쓰기 함수 `save(lines)` 두 개를 먼저 만들면 모든 명령이 짧아져요.', '`cmd[3:]` 은 `"쓰기 "` 뒤의 내용이에요. `지우기 ` 는 4글자라 `cmd[4:]`.', '지우기: `lines = load()` → `del lines[k - 1]` → `save(lines)`'], ex='"읽어서 → 고치고 → **w 로 통째로 다시 쓰기**"는 파일의 가운데를 고치는 유일한 방법이에요. 텍스트 파일에는 "한 줄만 지우기" 기능이 없어요.'),
)

# ============================================================ G3
G3 = lesson('3강. 파일 + 예외 + 딕셔너리 — 15점짜리 종합 문제', 50,
'- 큰 문제의 뼈대: **읽기 → 줄 단위 파싱 → 검증(예외) → 집계(딕셔너리) → 쓰기**\n- try 는 **줄 하나 단위**로 — 한 줄이 틀려도 나머지를 계속 처리\n- 표(딕셔너리)에 없는 값은 `KeyError`, 규칙에 어긋난 값은 `raise ValueError`\n- 지문에 **변환 표**가 주어지면 그대로 딕셔너리로 옮긴다 (점자·모스 부호·환율)\n- 오류 줄은 **번호와 이유**를 함께 기록\n- 결과 파일을 쓴 뒤 다시 읽어 확인하는 형태가 많다',
review('🔁 1~2강 복습', [T('예외와 파일을 함께 쓸 준비가 됐는지 확인해요.'), flip(['파일에서 읽은 줄 끝에 붙어 있는 것', '줄바꿈 \\n → strip()'], ['"w" 로 여는 순간 일어나는 일', '기존 내용이 모두 지워짐'], ['`a, b = "x".split(",")` 의 예외', 'ValueError (언패킹 개수 불일치)'], ['없는 파일을 "r" 로 열면', 'FileNotFoundError'])]),
outq('복습 — 출력 결과는?', D('''
with open("r.txt", "w", encoding="utf-8") as f:
    f.write("3\\nx\\n4\\n")
total = 0
bad = 0
with open("r.txt", encoding="utf-8") as f:
    for line in f:
        try:
            total += int(line)
        except ValueError:
            bad += 1
print(total, bad)
'''), review=True),
explain('큰 문제를 다섯 단계로 자르기',
  [T('2학기 1차의 가장 큰 문항은 **파일·예외·딕셔너리를 한꺼번에** 써요(2024 8번 점자 변환 12점, 2025 2차 노래자랑 14점·환율 12점). 길어 보여도 뼈대는 늘 같아요.'),
   steps(['① 읽기', '`with open(…) as f:` — 없는 파일이면 FileNotFoundError 처리'], ['② 파싱', '`line.strip().split(",")` 로 조각내고 형변환'], ['③ 검증', '조각 수·자료형·범위 — 어긋나면 except 또는 raise'], ['④ 집계', '딕셔너리에 누적 (`d.get(k, 0) + v`)'], ['⑤ 쓰기', '결과를 형식에 맞춰 파일로 — `"w"` 와 `"\\n"`']),
   key('가장 중요한 결정은 **try 를 어디에 두느냐**예요. 반복문 **안**에 두면 틀린 줄만 건너뛰고, **밖**에 두면 첫 오류에서 전체가 멈춰요.')],
  [cmp('try 가 반복문 밖 ❌', 'try:\n    for line in lines:\n        total += int(line)\nexcept ValueError:\n    print("오류")', 'try 가 반복문 안 ✅', 'for line in lines:\n    try:\n        total += int(line)\n    except ValueError:\n        print("오류")', lb='첫 오류에서 반복이 끝나요. 뒤의 정상 줄을 잃어요.', rb='오류 줄만 건너뛰고 끝까지 처리', tones=('bad', 'good')),
   C(D('''
lines = ["민,90", "솔", "율,구십", "하,105", "준,70"]
ok = {}
errors = []
for i, line in enumerate(lines, 1):
    try:
        name, s = line.split(",")
        s = int(s)
        if not 0 <= s <= 100:
            raise ValueError("범위")
        ok[name] = s
    except ValueError as e:
        errors.append(i)
print(ok)
print(errors)
'''), '세 가지 다른 원인이 모두 ValueError 로 모여요'),
   T('위 코드에서 2번 줄은 **언패킹 실패**, 3번 줄은 **int 변환 실패**, 4번 줄은 **직접 raise** 예요. 원인을 구분해서 알려야 하면 메시지를 다르게 주거나 예외 종류를 나눠요.')],
  [T('**변환 표**가 주어지는 문제는 표를 딕셔너리로 옮기는 것이 전부예요. 표에 없는 글자를 만났을 때의 처리가 채점 포인트예요.'),
   C(D('''
MORSE = {"a": ".-", "b": "-...", "c": "-.-.", "e": ".", "s": "...", "o": "---"}
def encode(word):
    out = []
    for ch in word:
        if ch not in MORSE:
            raise ValueError(f"변환할 수 없는 문자: {ch}")
        out.append(MORSE[ch])
    return " ".join(out)
for w in ["sos", "cab", "bee", "abz"]:
    try:
        print(w, "→", encode(w))
    except ValueError as e:
        print(w, "→", e)
'''), 'KeyError 가 나기 전에 먼저 검사해서 ValueError 로 알려요'),
   tip('`MORSE[ch]` 를 그냥 쓰고 `except KeyError` 로 잡아도 돼요. 다만 문제에서 "**ValueError 를 발생시킬 것**"이라고 하면 위처럼 `raise` 를 써야 해요. [조건]을 그대로 따르는 게 점수예요.')]),
outq('[기출유사] 출력 결과는?', D('''
price = {"연필": 500, "공책": 1500}
orders = ["연필 4", "지우개 2", "공책 둘", "공책 1", "연필"]
total = 0
log = ""
for o in orders:
    try:
        name, n = o.split()
        total += price[name] * int(n)
        log += "O"
    except KeyError:
        log += "K"
    except ValueError:
        log += "V"
print(total, log)
'''), '`공책 둘` 은 `price["공책"]` 까지는 성공하고 `int("둘")` 에서 실패해요. 한 줄 전체가 실패라 total 에 더해지지 않아요.'),
outq('[기출유사] 출력 결과는?', D('''
with open("in.txt", "w", encoding="utf-8") as f:
    f.write("A,3\\nB,x\\nA,4\\nC\\nB,5\\n")
d = {}
skip = []
with open("in.txt", encoding="utf-8") as f:
    for no, line in enumerate(f, 1):
        try:
            k, v = line.strip().split(",")
            d[k] = d.get(k, 0) + int(v)
        except ValueError:
            skip.append(no)
with open("out.txt", "w", encoding="utf-8") as f:
    for k in sorted(d, key=lambda k: -d[k]):
        f.write(f"{k}:{d[k]}\\n")
with open("out.txt", encoding="utf-8") as f:
    print(f.read().split(), skip)
'''), '2번 줄은 int 실패, 4번 줄은 언패킹 실패예요.'),
spot('[기출유사] `stock.txt` 에 `사과,10` / `배` / `감,3` 세 줄이 있을 때, **처음으로 예외가 발생하는 줄**은?', D('''
stock = {}
f = open("stock.txt", encoding="utf-8")
for line in f:
    parts = line.strip().split(",")
    name = parts[0]
    count = int(parts[1])
    stock[name] = count
f.close()
'''), 6, '둘째 줄 `배` 는 `parts == ["배"]` 라서 `parts[1]` 에서 IndexError 예요. 언패킹(`a, b = …`)이 아니라 **인덱스**로 꺼내면 예외 이름이 달라져요.'),
ch('[기출유사] 위 코드처럼 `parts[1]` 로 꺼낼 때와 `name, count = parts` 로 꺼낼 때, 조각이 1개인 줄에서 나는 예외를 순서대로 고르면?', ['IndexError, IndexError', 'IndexError, ValueError', 'ValueError, IndexError', 'ValueError, ValueError'], 2, '인덱스로 꺼내면 IndexError, 언패킹은 "값의 개수가 맞지 않음"이라 ValueError 예요. 어떤 except 를 써야 할지가 여기서 갈려요.'),
fill('[기출유사] 환율표에 없는 통화는 **KeyError**, 금액이 숫자가 아니면 **ValueError** 로 처리해요.', D('''
rate = {"USD": 1400, "JPY": 9}
for q in ["USD 3", "EUR 5", "JPY 백"]:
    cur, amt = q.split()
    try:
        print(rate[cur] * int(amt))
    except ___:
        print("없는 통화")
    except ___:
        print("금액 오류")
'''), ['KeyError', 'ValueError'], expect='4200\n없는 통화\n금액 오류'),
essay('[기출유사 · 서술 8점] 성적 파일을 읽어 평균을 구하는 코드예요. 파일에 `민,90` / `솔,결석` / `율,80` 세 줄이 있을 때 **출력 결과**를 쓰고, "결석한 학생만 빼고 평균을 구한다"는 의도대로 동작하지 않는 **이유**와 **고치는 방법**을 서술하세요.\n\n```\ntotal = 0; n = 0\ntry:\n    for line in open("score.txt"):\n        name, s = line.strip().split(",")\n        total += int(s)\n        n += 1\nexcept ValueError:\n    print("잘못된 줄")\nprint(total / n)\n```', '출력은 "잘못된 줄" 과 90.0 이다. try 가 반복문 전체를 감싸고 있어서, 둘째 줄의 int("결석") 에서 ValueError 가 발생하면 반복문 자체를 빠져나와 except 로 가 버린다. 그래서 셋째 줄(율,80)은 읽지도 않고, 첫째 줄만으로 평균 90.0 이 계산된다. try/except 를 반복문 안으로 옮겨 한 줄 단위로 감싸면, 오류가 난 줄만 건너뛰고 나머지 줄을 계속 처리하여 평균 85.0 이 된다.', ['출력이 "잘못된 줄" 과 90.0 이라고 썼다', 'try 가 반복문 전체를 감싸고 있다는 점을 짚었다', '예외가 나면 반복문을 빠져나가 뒤의 줄을 처리하지 못한다고 썼다', 'try 를 반복문 안(줄 단위)으로 옮긴다고 고쳤다']),
order('[기출유사] 파일의 각 줄을 처리하는 코드를 올바른 순서로 놓으세요.', ['with open("data.txt") as f:', '    for line in f:', '        try:', '            k, v = line.strip().split(",")', '            d[k] = d.get(k, 0) + int(v)', '        except ValueError:', '            continue'], code=False, mono=True),
prac('[기출유사 · 12점] 점자 변환기', '알파벳 a~j 의 점자는 가로 2칸 × 세로 3칸의 점으로 나타내요. 아래 표는 각 글자의 점 6개를 **위 줄부터, 왼쪽에서 오른쪽으로** 적은 것이에요(`o` 볼록한 점, `.` 평평한 점).\n\n```box 점자 표\na: o. .. ..    b: o. o. ..    c: oo .. ..    d: oo .o ..    e: o. .o ..\nf: oo o. ..    g: oo oo ..    h: o. oo ..    i: .o o. ..    j: .o oo ..\n```\n\n첫 줄에 단어 수 `n`, 이어서 n 줄에 단어가 주어져요.\n\n1. 단어들을 `words.txt` 에 한 줄씩 저장한 뒤 **다시 읽어서** 변환해요.\n2. 단어마다 점자를 3줄로 출력해요. 글자와 글자 사이는 공백 한 칸.\n3. 표에 없는 문자가 들어 있으면 그 단어는 3줄 대신 `변환 불가: 단어 (문자)` 한 줄을 출력해요. 문자는 **처음 만난** 표에 없는 문자예요.\n4. 단어와 단어 사이에는 빈 줄을 넣지 않아요. 마지막 줄에 `변환 a개 / 실패 b개` 를 출력해요.\n\n[조건] ○ 표는 딕셔너리로 만들 것 ○ 변환 함수는 표에 없는 문자를 만나면 **ValueError 를 raise** 할 것 ○ 대문자는 소문자로 바꿔 변환',
D('''
BRAILLE = {"a": "o.....", "b": "o.o...", "c": "oo....", "d": "oo.o..", "e": "o..o..",
           "f": "ooo...", "g": "oooo..", "h": "o.oo..", "i": ".oo...", "j": ".ooo.."}
def convert(word):
    rows = ["", "", ""]
    cells = []
    for ch in word.lower():
        if ch not in BRAILLE:
            raise ValueError(ch)
        cells.append(BRAILLE[ch])
    for r in range(3):
        rows[r] = " ".join(c[r * 2:r * 2 + 2] for c in cells)
    return rows
n = int(input())
with open("words.txt", "w", encoding="utf-8") as f:
    for _ in range(n):
        f.write(input() + "\\n")
ok = fail = 0
with open("words.txt", encoding="utf-8") as f:
    for line in f:
        word = line.strip()
        try:
            for row in convert(word):
                print(row)
            ok += 1
        except ValueError as e:
            print(f"변환 불가: {word} ({e})")
            fail += 1
print(f"변환 {ok}개 / 실패 {fail}개")
'''), ['2\nbad\ncab', '3\nhi\njazz\nBEE', '1\na', '2\nxyz\nk9', '2\nfig\nDice', '1\nabcdefghij'],
  starter=D('''
BRAILLE = {"a": "o.....", "b": "o.o...", "c": "oo....", "d": "oo.o..", "e": "o..o..",
           "f": "ooo...", "g": "oooo..", "h": "o.oo..", "i": ".oo...", "j": ".ooo.."}
def convert(word):
    # 점자 3줄을 리스트로 반환, 표에 없는 문자면 raise ValueError(문자)
    pass
'''), hints=['표의 값 6글자에서 r번째 줄은 `c[r * 2:r * 2 + 2]` (r = 0, 1, 2)', '한 줄: `" ".join(c[r*2:r*2+2] for c in cells)`', '`raise ValueError(ch)` 로 문자를 실어 보내면 `except ValueError as e` 에서 `{e}` 로 꺼낼 수 있어요.'], ex='지문의 표를 **딕셔너리로 옮기는 순간** 문제의 절반이 끝나요. 수업에서 안 배운 내용(점자)이 나와도 지문이 규칙을 다 알려 줘요 — 읽고 옮기면 돼요.'),
prac('[기출유사 · 14점] 성적 파일 정리', '첫 줄에 줄 수 `n`, 이어서 n 줄의 자료가 주어져요. 올바른 줄은 `이름,점수` 형식이고 점수는 0~100 의 정수예요.\n\n1. 받은 줄을 그대로 `raw.csv` 에 저장한 뒤 다시 읽어 처리해요.\n2. 잘못된 줄은 건너뛰되, **줄 번호와 이유**를 기록해요.\n   - 쉼표로 나눈 조각이 2개가 아님 → `형식`\n   - 점수가 정수가 아님 → `숫자`\n   - 점수가 0~100 밖 → `범위`\n3. 같은 이름이 여러 번 나오면 **가장 높은 점수**만 남겨요.\n4. 결과를 `clean.csv` 에 `이름,점수` 로 저장해요(점수 내림차순, 같으면 이름 사전순).\n\n출력: `clean.csv` 를 다시 읽어 그대로 출력 → 오류 줄을 `N번 줄: 이유` 로 줄 번호 순서대로 → 마지막 줄에 `평균 X` (소수 첫째 자리까지, 유효한 학생이 없으면 `평균 없음`).\n\n[조건] ○ 한 줄 단위로 try/except 를 사용할 것 ○ 범위 오류는 `raise` 로 발생시킬 것',
D('''
n = int(input())
with open("raw.csv", "w", encoding="utf-8") as f:
    for _ in range(n):
        f.write(input() + "\\n")
best = {}
errors = []
with open("raw.csv", encoding="utf-8") as f:
    for no, line in enumerate(f, 1):
        parts = line.strip().split(",")
        try:
            if len(parts) != 2:
                raise ValueError("형식")
            try:
                s = int(parts[1])
            except ValueError:
                raise ValueError("숫자")
            if not 0 <= s <= 100:
                raise ValueError("범위")
            name = parts[0]
            if name not in best or s > best[name]:
                best[name] = s
        except ValueError as e:
            errors.append(f"{no}번 줄: {e}")
rows = sorted(best.items(), key=lambda p: (-p[1], p[0]))
with open("clean.csv", "w", encoding="utf-8") as f:
    for name, s in rows:
        f.write(f"{name},{s}\\n")
with open("clean.csv", encoding="utf-8") as f:
    for line in f:
        print(line.strip())
for e in errors:
    print(e)
if best:
    print(f"평균 {sum(best.values()) / len(best):.1f}")
else:
    print("평균 없음")
'''), ['6\n민,90\n솔\n율,구십\n하,105\n민,95\n준,70', '2\na,b,c\nx,-1', '3\n가,50\n나,50\n가,40', '4\nk,100\nk,100\nm,0\nm,3.5', '1\n,\n', '5\np,10\nq,20\nr,30\ns,\nt,40'],
  starter=D('''
n = int(input())
with open("raw.csv", "w", encoding="utf-8") as f:
    for _ in range(n):
        f.write(input() + "\\n")
best = {}
errors = []
with open("raw.csv", encoding="utf-8") as f:
    for no, line in enumerate(f, 1):
        parts = line.strip().split(",")
        # 이어서 작성
'''), hints=['이유를 구분하려면 메시지를 실어 보내요: `raise ValueError("형식")` → `except ValueError as e: errors.append(f"{no}번 줄: {e}")`', '`int()` 가 내는 ValueError 의 메시지는 영어라서, 안쪽 try 로 잡아 `raise ValueError("숫자")` 로 **바꿔서 다시** 던져요.', '최고 점수: `if name not in best or s > best[name]: best[name] = s`'], ex='`,` 한 글자만 있는 줄은 조각이 2개(`["", ""]`)라 형식은 통과하고, `int("")` 에서 `숫자` 오류가 돼요. **검사 순서가 곧 결과**예요.'),
prac('[심화 · 16점] 매점 주문 정산', '매점 가격표와 주문 내역을 처리해요.\n\n입력: 첫 줄 `m`, 이어서 m 줄에 `상품 가격`. 다음 줄 `k`, 이어서 k 줄에 주문 `학생 상품 수량`.\n\n1. 가격표를 `price.txt` 에, 주문을 `order.txt` 에 저장한 뒤 **두 파일을 읽어** 처리해요.\n2. 주문 한 줄마다 검사해요(이 순서로). 조각이 3개가 아님 → `형식 오류` / 가격표에 없는 상품 → `없는 상품` / 수량이 정수가 아니거나 1 미만 → `수량 오류`\n3. 정상 주문은 학생별로 금액을 누적해요.\n4. 결과를 `bill.txt` 에 저장해요: 학생별 `학생 금액원` (금액 내림차순, 같으면 이름 사전순), 마지막 줄 `합계 금액원`.\n\n출력: 오류가 난 주문을 `[N] 이유` (N 은 주문 번호, 1부터)로 순서대로 → `bill.txt` 의 내용 그대로. 정상 주문이 하나도 없으면 `bill.txt` 에는 `합계 0원` 한 줄만 있어요.\n\n[조건] ○ 없는 상품은 **KeyError**, 형식·수량은 **ValueError** 로 서로 다른 except 에서 처리할 것 ○ 가격을 읽는 함수 `load_price()`, 주문 한 줄을 처리하는 함수 `parse(line, price)` 로 나눌 것',
D('''
def load_price():
    price = {}
    with open("price.txt", encoding="utf-8") as f:
        for line in f:
            name, p = line.split()
            price[name] = int(p)
    return price
def parse(line, price):
    parts = line.split()
    if len(parts) != 3:
        raise ValueError("형식 오류")
    who, item, n = parts
    unit = price[item]
    try:
        n = int(n)
    except ValueError:
        raise ValueError("수량 오류")
    if n < 1:
        raise ValueError("수량 오류")
    return who, unit * n
m = int(input())
with open("price.txt", "w", encoding="utf-8") as f:
    for _ in range(m):
        f.write(input() + "\\n")
k = int(input())
with open("order.txt", "w", encoding="utf-8") as f:
    for _ in range(k):
        f.write(input() + "\\n")
price = load_price()
bill = {}
with open("order.txt", encoding="utf-8") as f:
    for no, line in enumerate(f, 1):
        try:
            who, money = parse(line, price)
            bill[who] = bill.get(who, 0) + money
        except KeyError:
            print(f"[{no}] 없는 상품")
        except ValueError as e:
            print(f"[{no}] {e}")
with open("bill.txt", "w", encoding="utf-8") as f:
    for who in sorted(bill, key=lambda w: (-bill[w], w)):
        f.write(f"{who} {bill[who]}원\\n")
    f.write(f"합계 {sum(bill.values())}원\\n")
with open("bill.txt", encoding="utf-8") as f:
    print(f.read().strip())
'''), ['3\n빵 1500\n우유 1000\n젤리 700\n6\n민 빵 2\n솔 콜라 1\n민 우유 1\n율 젤리 세개\n솔 젤리 3\n하 빵', '1\n물 500\n2\n가 물 0\n나 차 x', '2\na 100\nb 200\n4\nx a 3\ny b 1\nz a 2\nx b 1', '1\n껌 300\n3\n민 껌 -1\n민 껌 1.5\n민 껌 1 개', '2\n김밥 3000\n라면 3500\n3\n준 라면 1\n준 김밥 1\n준 떡볶이 1'],
  hints=['`parse` 는 성공하면 `(학생, 금액)` 을 반환하고, 실패하면 예외를 던져요. 출력은 하지 않아요.', '`unit = price[item]` 을 수량 변환보다 **먼저** 실행해야 "없는 상품"이 "수량 오류"보다 먼저 검사돼요.', '메인: `except KeyError:` 와 `except ValueError as e:` 두 개'], ex='함수가 **예외를 던지고**, 호출한 쪽이 **종류별로 받아** 메시지를 정해요. 1강의 "예외는 호출한 쪽으로 올라간다"가 설계 도구가 되는 순간이에요.'),
)
