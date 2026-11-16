from glib import *
import re

# ============================================================ D9 검증용 코드
_AND = D('''
import numpy as np
a = np.array([3, 8, 5, 1, 9])
b = a[a > 2]
c = a[(a > 2) & (a < 9)]
d = a[(a > 2) and (a < 9)]
print(b.tolist(), c.tolist(), d.tolist())
''')
assert errline(_AND) == 5 and err(_AND) == 'ValueError'
_PREC = D('''
import numpy as np
a = np.array([3, 8, 5, 1, 9])
print(a[a > 2 & a < 9].tolist())
''')
assert err(_PREC) == 'ValueError'
_SPOT9 = D('''
import numpy as np
a = np.arange(12).reshape(3, 4)
row = a[2]
col = a[:, 3]
sub = a[1:, 1:3]
print(sub[1, 1])
print(col[3])
print(row[3])
''')
assert errline(_SPOT9) == 7 and err(_SPOT9) == 'IndexError'
assert run(D('''
import numpy as np
a = np.arange(12).reshape(3, 4)
print(a[1].ndim, a[1:2].ndim, a[:, -1].ndim, a[:, -1:].ndim, a[a > 5].ndim, a[1, 2].ndim, a[[0, 2]].ndim, a.max().ndim, a[0:2, 1].ndim)
''')) == '1 2 1 2 1 0 2 0 1'
assert run(D('''
import numpy as np
s = np.array([70, 95, 80, 60])
print(np.argsort(s).tolist(), np.argsort(s)[::-1].tolist(), np.sort(s)[::-1].tolist(), int(np.argsort(s)[-1]), np.where(s >= 80)[0].tolist(), np.where(s >= 80, 1, 0).tolist(), s[s >= 80].tolist(), int((s >= 80).sum()))
''')) == '[3, 0, 2, 1] [1, 2, 0, 3] [95, 80, 70, 60] 1 [1, 2] [0, 1, 1, 0] [95, 80] 2'
assert run(D('''
import numpy as np
a = np.array([5, 2, 9])
b = a.sort()
print(b, a.tolist())
''')) == 'None [2, 5, 9]'

# ============================================================ D9
D9 = lesson('9강. numpy 심화 — where·boolean indexing·argsort', 50,
'- 정수 인덱스는 **차원을 하나 줄이고**, 슬라이스는 **차원을 유지**해요: `a[1]` 은 1차원, `a[1:2]` 는 2차원\n- `a[:, -1]` 은 마지막 열, `a[1:, :2]` 는 "1번 행부터 · 앞의 두 열"\n- `a[조건]` 의 결과는 항상 **1차원**(복사본). 조건 두 개는 `(조건1) & (조건2)` — `and` 를 쓰면 **ValueError**\n- `np.where(조건)` 은 **위치**(축마다 배열 하나씩 든 튜플), `np.where(조건, x, y)` 는 **골라 바꾼 새 배열**\n- `np.sort(a)` 는 새 배열(내림차순은 `[::-1]`), `a.sort()` 는 원본을 바꾸고 None\n- `np.argsort(a)` 는 **정렬했을 때 올 원소의 원래 인덱스** → `names[np.argsort(scores)]` 로 다른 배열을 같은 순서로 정렬',
review('🔁 8강 복습', [T('파일 모드, 예외의 흐름, `__name__` 을 확인해요.'), flip(['`"w"` 로 여는 순간', '기존 내용이 모두 지워짐 (없으면 새로 만듦)'], ['`"a"` 로 열면', '기존 내용 뒤에 이어 씀 (없으면 새로 만듦)'], ['`"r"` 로 없는 파일을 열면', 'FileNotFoundError'], ['try 에서 오류가 **안** 나면', 'else → finally 순서로 실행'], ['import 된 파일 안의 `__name__`', '모듈 이름 ("__main__" 이 아님)'])]),
outq('복습 — 출력 결과는?', D('''
with open("memo.txt", "w") as f:
    f.write("a\\nb\\n")
with open("memo.txt", "a") as f:
    f.write("c\\n")
out = []
for name in ["memo.txt", "none.txt"]:
    try:
        with open(name) as f:
            n = len(f.readlines())
    except FileNotFoundError:
        out.append("X")
    else:
        out.append(n)
    finally:
        out.append("|")
print(*out)
'''), review=True),
explain('2차원 슬라이싱 — 차원이 줄어드는가, 유지되는가',
  [T('2025학년도 2차 고사는 9문항 중 **5문항(50점)** 이 numpy 였어요. 기본편에서 문법은 배웠으니, 여기서는 **결과의 모양**을 정확히 예측하는 연습을 해요. 출력 추론 문제에서 대괄호가 한 겹인지 두 겹인지가 곧 점수예요.'),
   C(D('''
import numpy as np
a = np.arange(1, 13).reshape(3, 4)
print(a.tolist())
print(a[1].tolist(), a[1].shape)
print(a[1:2].tolist(), a[1:2].shape)
print(a[:, -1].tolist(), a[:, -1].shape)
print(a[:, -1:].tolist(), a[:, -1:].shape)
print(a[1:, :2].tolist(), a[1:, :2].shape)
'''), '정수로 고르면 그 축이 사라지고, 슬라이스(:)로 고르면 남아요'),
   key('**정수 인덱스 하나 = 차원 하나 감소**, **슬라이스 = 차원 유지**. `a[1]` 은 1차원 `[5, 6, 7, 8]`, `a[1:2]` 는 2차원 `[[5, 6, 7, 8]]` 이에요. `a[:, -1]` 은 행은 전부(슬라이스), 열은 정수라서 1차원이 돼요.')],
  [T('행·열을 고르는 다섯 가지 모양을 한눈에 정리해요. 쉼표 **앞이 행, 뒤가 열**이에요.'),
   tabs(['a[1]', '1번 행 전체 — 1차원. `a[1, :]` 과 같아요.', 'a[1].tolist()        # [5, 6, 7, 8]'], ['a[:, -1]', '**마지막 열** — 모든 행의 마지막 칸. 1차원.', 'a[:, -1].tolist()    # [4, 8, 12]'], ['a[1:, :2]', '1번 행부터 끝까지 · 0~1번 열 — 2차원 (2, 2).', 'a[1:, :2].tolist()   # [[5, 6], [9, 10]]'], ['a[[0, 2]]', '리스트로 고르면 0번·2번 **행 여러 개** — 2차원 (2, 4).', 'a[[0, 2]].tolist()   # [[1, 2, 3, 4], [9, 10, 11, 12]]'], ['a[2, 1]', '정수 두 개 — 값 하나.', 'int(a[2, 1])         # 10']),
   exam('"k번 학생의 점수 전체"는 `a[k]`, "마지막 시험 점수만"은 `a[:, -1]`. 2025 6번(6점)이 이 두 줄이었어요. `a[-1]` (마지막 **행**) 과 `a[:, -1]` (마지막 **열**) 을 바꿔 쓰는 실수가 가장 많아요.')],
  [T('슬라이스로 잘라 낸 배열은 원본과 **같은 메모리를 보는 창(뷰)** 이에요. 그래서 잘라 낸 쪽에 대입하면 원본이 함께 바뀌어요. 리스트 슬라이싱(복사)과 다른 점이에요.'),
   C(D('''
import numpy as np
a = np.arange(6)
part = a[1:4]
part[0] = 99
print(a.tolist())

lst = [0, 1, 2, 3, 4, 5]
p2 = lst[1:4]
p2[0] = 99
print(lst)

pick = a[a > 3]
pick[0] = -1
print(a.tolist(), pick.tolist())
'''), '슬라이스는 뷰(원본이 바뀜), 조건으로 고른 것은 복사본'),
   warn('`part = a[1:4]` 뒤 `part[0] = 99` → **a 도 바뀌어요**. 반대로 `a[a > 3]` 처럼 조건으로 골라 **새 이름에 담은 배열**은 복사본이라 고쳐도 원본은 그대로예요. 원본을 지키려면 `a[1:4].copy()`.')]),
explain('boolean indexing — 조건으로 고르고, 세고, 바꾸기',
  [T('`a > 5` 는 a 와 **모양이 같은 True/False 배열**이에요. 이 배열을 대괄호에 넣으면 True 인 칸의 값만 모여요. 2차원에서 골라도 결과는 **항상 1차원**이에요(행 순서대로 왼쪽 → 오른쪽).'),
   C(D('''
import numpy as np
a = np.array([[7, 2, 9],
              [4, 8, 1]])
mask = a > 5
print(mask.tolist(), mask.shape)
print(a[mask].tolist())
print(int(mask.sum()), mask.sum(axis=1).tolist())
print(a[a % 2 == 0].tolist(), a[a > 100].tolist())
'''), '조건 배열 → 고르기 / 개수 세기'),
   key('**고르기**는 `a[조건]` (값들의 1차원 배열), **세기**는 `(조건).sum()` (True 가 1). 조건에 맞는 것이 없으면 오류가 아니라 **빈 배열** `[]` 이에요.')],
  [T('조건이 두 개일 때가 감점 1순위예요. numpy 에서는 `and`·`or`·`not` 대신 **`&`·`|`·`~`** 를 쓰고, 각 조건을 **괄호로** 감싸요.'),
   cmp('원소마다 따지는 &', 'a[(a > 2) & (a < 9)]', '배열에 and', 'a[(a > 2) and (a < 9)]', '같은 자리끼리 True/False 를 계산해 조건 배열을 만들어요.', '**ValueError** — `and` 는 배열 전체를 True/False **하나**로 바꾸려 하는데, 원소가 여러 개면 참·거짓을 정할 수 없어요.'),
   warn('괄호도 필수예요. `&` 는 비교 연산자보다 **먼저** 계산돼서 `a > 2 & a < 9` 는 `a > (2 & a) < 9` 로 읽혀요. 이것도 결국 ValueError 로 끝나요.')],
  [T('대괄호 조건을 **대입문의 왼쪽**에 쓰면 조건에 맞는 칸만 바뀌어요. 이때는 원본이 직접 바뀌어요(복사본이 아니에요).'),
   C(D('''
import numpy as np
t = np.array([[12, -3, 105],
              [40, 100, -1]])
print(int(((t < 0) | (t > 100)).sum()))
t[t < 0] = 0
t[t > 100] = 100
print(t.tolist())
names = np.array(["가", "나", "다"])
score = np.array([55, 90, 72])
print(names[score >= 70].tolist())
'''), '범위를 벗어난 값 고치기 / 다른 배열을 조건으로 고르기'),
   steps(['세기', '`((t < 0) | (t > 100)).sum()` — 조건 전체를 한 번 더 괄호로'], ['바꾸기', '`t[t < 0] = 0` — 조건에 맞는 칸에만 대입'], ['다른 배열 고르기', '`names[score >= 70]` — 조건 배열과 **길이만 같으면** 다른 배열을 고를 수 있어요'], ['행별 개수', '`(t >= 50).sum(axis=1)` — 행마다 True 의 개수']),
   exam('"슬라이싱으로 일부를 잘라 낸 뒤 조건으로 고르기"가 2025 8번(15점)이에요. `a[:, -1]` 로 열을 뽑고 → 그 열로 조건을 만들고 → `names[조건]` 으로 이름을 고르는 세 단계를 한 줄씩 쓰면 돼요.')]),
explain('np.where 의 두 얼굴',
  [T('`np.where(조건)` 처럼 **조건만** 주면 True 인 칸의 **위치(인덱스)** 를 돌려줘요. 값이 아니라 위치라는 점이 boolean indexing 과 달라요.'),
   C(D('''
import numpy as np
s = np.array([70, 95, 80, 60])
pos = np.where(s >= 80)
print(type(pos).__name__, len(pos), pos[0].tolist())

seat = np.array([[1, 0, 1],
                 [0, 1, 0]])
rows, cols = np.where(seat == 0)
print(rows.tolist(), cols.tolist())
for r, c in zip(rows.tolist(), cols.tolist()):
    print(r, c)
'''), '1차원이어도 결과는 튜플 — [0] 을 붙여야 인덱스 배열'),
   key('결과는 **튜플**이고, 그 안에 **축(차원)마다 배열이 하나씩** 들어 있어요. 1차원이면 `(인덱스 배열,)`, 2차원이면 `(행 번호 배열, 열 번호 배열)`. 같은 자리끼리 짝지으면 (0,1), (1,0), (1,2) 가 빈자리예요.')],
  [T('인자를 **세 개** 주면 전혀 다른 일을 해요. `np.where(조건, 참일 때 값, 거짓일 때 값)` 은 원소마다 if-else 를 적용한 **새 배열**을 만들어요. 모양은 원래 배열과 같아요.'),
   C(D('''
import numpy as np
s = np.array([70, 95, 80, 60])
print(np.where(s >= 80, "P", "F").tolist())
print(np.where(s >= 80, s, 0).tolist())
print(np.where(s < 70, 70, s).tolist())
print(s.tolist())
'''), '참이면 둘째, 거짓이면 셋째 인자 — 원본은 그대로'),
   tabs(['np.where(조건)', '**어디에** 있는가 → 위치 튜플', 'np.where(s >= 80)[0].tolist()     # [1, 2]'], ['s[조건]', '**무엇이** 있는가 → 값들', 's[s >= 80].tolist()               # [95, 80]'], ['np.where(조건, x, y)', '**골라 바꾼** 같은 모양의 새 배열', 'np.where(s >= 80, 1, 0).tolist()  # [0, 1, 1, 0]'], ['(조건).sum()', '**몇 개** 인가', 'int((s >= 80).sum())              # 2']),
   exam('"빈자리의 위치를 출력하라"(2025 5번, 8점)는 `np.where(조건)`, "기준 미만은 0 으로 바꿔라"는 `np.where(조건, 0, a)` 예요. 문제의 동사(**찾아라 / 바꿔라**)로 인자 개수를 정하세요.')]),
explain('np.sort 와 np.argsort',
  [T('`np.sort(a)` 는 오름차순으로 정렬한 **새 배열**을 돌려줘요. 내림차순 옵션이 없어서 **`[::-1]` 로 뒤집어요**(2025 7번, 6점). 2차원에서는 기본이 **행마다**(axis=1 과 같은 마지막 축) 정렬이에요.'),
   C(D('''
import numpy as np
a = np.array([5, 2, 9, 1])
print(np.sort(a).tolist(), np.sort(a)[::-1].tolist(), a.tolist())
m = np.array([[3, 1, 2],
              [9, 7, 8]])
print(np.sort(m).tolist())
print(np.sort(m, axis=0).tolist())
print(np.sort(m)[:, ::-1].tolist())
b = a.sort()
print(b, a.tolist())
'''), 'np.sort(a) 는 새 배열, a.sort() 는 원본을 바꾸고 None'),
   warn('`b = a.sort()` 는 리스트의 `sort()` 처럼 **None** 을 돌려줘요. 그리고 2차원에서 `np.sort(m)[::-1]` 은 **행의 순서**를 뒤집을 뿐이에요. 행 안에서 내림차순은 `np.sort(m)[:, ::-1]`.')],
  [T('`np.argsort(a)` 는 값이 아니라 **인덱스**를 돌려줘요. "정렬하면 맨 앞에 올 원소가 원래 몇 번 칸에 있었는가"를 차례로 적은 배열이에요. 이 인덱스 배열로 **다른 배열**을 같은 순서로 줄 세울 수 있어요.'),
   C(D('''
import numpy as np
names = np.array(["민", "솔", "준", "하"])
score = np.array([70, 95, 80, 60])
order = np.argsort(score)
print(order.tolist())
print(score[order].tolist())
print(names[order].tolist())
print(names[order[::-1]].tolist())
print(names[order[::-1][:2]].tolist())
'''), '점수로 정렬한 순서대로 이름을 꺼내기'),
   steps(['order = np.argsort(score)', '`[3, 0, 2, 1]` — 가장 작은 60 이 3번 칸, 그다음 70 이 0번 칸 …'], ['score[order]', '`np.sort(score)` 와 같은 결과'], ['names[order]', '점수 오름차순으로 이름이 정렬돼요'], ['order[::-1]', '내림차순 인덱스 — 1등부터'], ['order[::-1][:k]', '상위 k명의 인덱스']),
   exam('"점수 순으로 **이름**을 출력하라"(2025 9번, 15점)는 `np.sort(names)` 가 아니에요(그건 가나다순). **점수의 argsort 로 이름 배열을 인덱싱**해야 해요. `order[0]` 은 "꼴찌의 인덱스"이지 "0번 학생의 등수"가 아니라는 점도 서술형 단골이에요.')]),
outq('[기출유사] 출력 결과는?', D('''
import numpy as np
a = np.arange(10, 22).reshape(3, 4)
print(a[2].tolist(), a[:, -1].tolist(), a[-1, -1])
print(a[:2, 1:3].tolist(), a[1:2].shape, a[1].shape, a[:, :1].shape)
'''), '`a` 는 10~21 을 3행 4열로 놓은 배열이에요. `a[1:2]` 는 슬라이스라 2차원 (1, 4), `a[1]` 은 정수라 1차원 (4,), `a[:, :1]` 은 둘 다 슬라이스라 (3, 1).'),
bucket('`a = np.arange(12).reshape(3, 4)` 일 때 결과의 **차원**으로 분류하세요.', ['값 하나', '1차원 배열', '2차원 배열'], [['a[1, 2]', 1], ['a[1]', 2], ['a[1:2]', 3], ['a[:, -1]', 2], ['a[:, -1:]', 3], ['a[a > 5]', 2], ['a[[0, 2]]', 3], ['a.max()', 1], ['a[0:2, 1]', 2]], '정수 인덱스 하나마다 차원이 하나 줄어요. 슬라이스와 리스트 인덱스는 차원을 유지하고, 조건으로 고르면 언제나 1차원이에요.'),
outq('[기출유사] 출력 결과는?', D('''
import numpy as np
t = np.array([[36, 41, 38],
              [35, 37, 40],
              [39, 36, 42]])
hot = t >= 38
print(t[hot].tolist(), int(hot.sum()), hot.sum(axis=0).tolist())
print(t[(t > 35) & (t < 39)].tolist(), t[(t < 36) | (t > 41)].tolist())
last = t[:, -1]
print(t[last >= 40].tolist())
'''), '마지막 줄이 핵심이에요. `last >= 40` 은 길이 3 의 조건 배열 `[False, True, True]` 이고, 이것으로 2차원 배열을 고르면 **행 단위로** 골라져요(1번·2번 행).'),
spot('[기출유사] **예외가 발생하는 줄**은?', _AND, 5, '`and` 는 양쪽을 True/False **하나**로 바꿔야 하는데, 원소가 여러 개인 배열은 참·거짓을 하나로 정할 수 없어서 ValueError 가 나요. 원소별로 따지는 `&` 를 써야 해요(4번 줄).'),
essay('[기출유사 · 서술형] 아래 코드를 실행하면 오류가 발생해요. **오류의 종류와 이유**를 쓰고, 2 보다 크고 9 보다 작은 원소를 고르도록 **수정한 코드**를 쓰세요.\n\n```\nimport numpy as np\na = np.array([3, 8, 5, 1, 9])\nprint(a[a > 2 and a < 9])\n```', 'ValueError 가 발생한다. a > 2 와 a < 9 는 각각 원소마다 True/False 가 들어 있는 배열인데, and 는 양쪽을 하나의 참/거짓 값으로 판단하려고 한다. 원소가 여러 개인 배열은 전체를 참 또는 거짓 하나로 정할 수 없으므로(모호하므로) 오류가 난다. 원소별로 논리 연산을 하는 & 를 쓰고, & 가 비교 연산자보다 먼저 계산되므로 각 조건을 괄호로 감싸 print(a[(a > 2) & (a < 9)]) 로 고친다.', ['ValueError 라고 썼다', 'and 는 배열 전체를 참/거짓 하나로 판단하려 하는데 원소가 여러 개라 정할 수 없다는 이유를 썼다', '원소별 연산자 & 로 바꿨다', '각 조건을 괄호로 감쌌다']),
outq('[기출유사] 출력 결과는?', D('''
import numpy as np
room = np.array([[1, 1, 0, 1],
                 [0, 1, 1, 0],
                 [1, 1, 1, 1]])
r, c = np.where(room == 0)
print(r.tolist(), c.tolist(), len(r))
print(np.where(room[1] == 1)[0].tolist())
print(np.where(room == 0, "빈", "-")[0].tolist())
print(np.where(room.sum(axis=1) == 4)[0].tolist())
'''), '`np.where(조건)` 은 위치예요. 2차원이면 행 번호 배열과 열 번호 배열로 나뉘어 나와서 (0,2), (1,0), (1,3) 이 빈칸이에요. 마지막 줄은 "행의 합이 4 인 행 번호" = 꽉 찬 줄.'),
essay('[기출유사 · 서술형] `s = np.array([70, 95, 80, 60])` 일 때 `idx = np.where(s >= 80)` 을 실행한 뒤 `print(idx[0])` 처럼 **`[0]` 을 붙여야** 인덱스 배열을 얻을 수 있어요. 그 이유를 `np.where` 가 돌려주는 값의 **자료형과 구조**와 연결하여 서술하고, 2차원 배열에서는 결과가 어떻게 달라지는지 쓰세요.', 'np.where(조건) 은 조건이 참인 원소의 위치를 튜플로 돌려주며, 튜플 안에는 배열의 축(차원)마다 인덱스 배열이 하나씩 들어 있다. s 는 1차원이므로 결과는 인덱스 배열 하나만 든 튜플 (array([1, 2]),) 이고, 인덱스 배열 자체를 쓰려면 튜플의 첫 번째 요소인 idx[0] 을 꺼내야 한다. 2차원 배열이면 튜플에 행 번호 배열과 열 번호 배열 두 개가 들어 있어, 같은 순서의 원소끼리 짝지으면 (행, 열) 위치가 된다.', ['결과가 튜플이라고 썼다', '튜플 안에 축(차원)마다 인덱스 배열이 하나씩 들어 있다고 썼다', '1차원이라 배열이 하나뿐이므로 [0] 으로 꺼낸다고 썼다', '2차원이면 행 번호 배열과 열 번호 배열 두 개가 나온다고 썼다']),
match('`s = np.array([70, 95, 80, 60])` 일 때 표현과 결과를 이어 보세요.', [['np.argsort(s).tolist()', '[3, 0, 2, 1]'], ['np.argsort(s)[::-1].tolist()', '[1, 2, 0, 3]'], ['np.sort(s)[::-1].tolist()', '[95, 80, 70, 60]'], ['np.where(s >= 80)[0].tolist()', '[1, 2]'], ['np.where(s >= 80, 1, 0).tolist()', '[0, 1, 1, 0]'], ['s[s >= 80].tolist()', '[95, 80]'], ['int((s >= 80).sum())', '2'], ['int(np.argsort(s)[-1])', '1']], 'argsort 는 **인덱스**, sort 는 **값**, where(조건) 은 **위치**, where(조건, x, y) 는 **바꾼 배열**이에요. `np.argsort(s)[-1]` 은 가장 큰 값의 인덱스.'),
outq('[기출유사] 출력 결과는?', D('''
import numpy as np
club = np.array(["축구", "농구", "배구", "탁구", "야구"])
member = np.array([18, 25, 9, 14, 21])
order = np.argsort(member)
print(order.tolist())
print(club[order].tolist())
print(club[order[::-1][:3]].tolist(), member[order[-1]], club[order[0]])
'''), '`order` 는 인원이 적은 동아리부터의 **인덱스**예요. `order[::-1][:3]` 은 많은 순 상위 3개, `order[-1]` 은 가장 많은 동아리의 인덱스, `order[0]` 은 가장 적은 동아리의 인덱스.'),
essay('[기출유사 · 서술형] `score = np.array([70, 95, 80, 60])` 에서 `np.argsort(score)` 의 결과는 `[3 0 2 1]` 이에요. ① 이 결과의 **첫 번째 값 3 이 뜻하는 것**을 쓰고, ② "0번 학생의 등수가 3등이라는 뜻"이라는 해석이 **왜 틀렸는지** 설명하고, ③ 이름 배열 `names` 를 **점수가 높은 순**으로 출력하는 코드를 쓰세요.', '① np.argsort 는 배열을 오름차순으로 정렬했을 때 각 자리에 올 원소의 원래 인덱스를 돌려준다. 첫 번째 값 3 은 가장 작은 값(60)이 원래 3번 인덱스에 있다는 뜻이다. ② 결과의 k번째 값은 "k번 원소의 등수"가 아니라 "k번째로 작은 원소가 있던 위치"이다. 0번 학생(70점)은 결과에서 1번 자리에 0 으로 나타나므로 오름차순으로 두 번째이다. ③ print(names[np.argsort(score)[::-1]]) — argsort 결과를 [::-1] 로 뒤집어 내림차순 인덱스로 만들고 그것으로 names 를 인덱싱한다.', ['argsort 는 정렬된 순서대로 원래 인덱스를 돌려준다고 썼다', '3 은 가장 작은 값이 3번 인덱스에 있다는 뜻이라고 썼다', '등수가 아니라 위치(인덱스)라는 점을 설명했다', 'names[np.argsort(score)[::-1]] 형태의 코드를 썼다']),
fill('[기출유사] 기록이 **빠른(작은) 순**으로 이름을 출력하고, 30 초 미만인 기록의 **위치**를 구해요.', D('''
import numpy as np
names = np.array(["가", "나", "다", "라"])
rec = np.array([31, 28, 35, 29])
print(names[np.___(rec)].tolist())
print(np.___(rec < 30)[___].tolist())
'''), ['argsort', 'where', '0'], expect="['나', '라', '가', '다']\n[1, 3]"),
outq('[심화] 출력 결과는? (뷰와 복사)', D('''
import numpy as np
a = np.arange(1, 9).reshape(2, 4)
row = a[0]
row[0] = 50
big = a[a > 5]
big[0] = -1
a[a % 2 == 0] = 0
col = a[:, -1]
col[1] = 7
print(a.tolist(), big.tolist())
'''), '`row` 와 `col` 은 슬라이스·정수 인덱싱으로 얻은 **뷰**라서 대입하면 a 가 바뀌어요. `big = a[a > 5]` 는 **복사본**이라 `big[0] = -1` 은 a 에 영향이 없어요. `a[조건] = 0` 은 대입문의 왼쪽이라 a 를 직접 바꿔요.'),
spot('[심화] **예외가 발생하는 줄**은?', _SPOT9, 7, '`col = a[:, 3]` 은 행이 3개라 길이 3 인 1차원 배열(인덱스 0~2)이에요. `col[3]` 은 범위를 벗어나 IndexError. `sub` 는 (2, 2) 라 `sub[1, 1]` 은 정상, `row` 는 길이 4 라 `row[3]` 도 정상이에요.'),
ch('[심화] `a = np.array([5, 2, 9])` 일 때 옳은 설명을 **모두** 고르세요.', ['`b = np.sort(a)` 뒤 a 는 `[5, 2, 9]` 그대로다', '`b = a.sort()` 뒤 b 는 `[2, 5, 9]` 다', '`np.sort(a)[::-1]` 은 내림차순 배열이다', '`np.argsort(a)[0]` 은 가장 작은 값 2 다'], [1, 3], '②: `a.sort()` 는 원본을 정렬하고 **None** 을 돌려줘요. ④: argsort 는 값이 아니라 인덱스를 주므로 `np.argsort(a)[0]` 은 2 가 있는 **위치 1** 이에요.'),
prac('[기출유사] 독서실 빈자리 지도 (np.where)', '독서실 좌석표가 주어져요. `1` 은 사용 중, `0` 은 빈자리예요.\n\n입력: 첫 줄에 행 수 `R` 과 열 수 `C`, 이어서 R 줄에 0 또는 1 이 C 개씩(공백 구분).\n\n출력\n1. `빈자리: K개`\n2. 빈자리를 위쪽 행부터, 같은 행에서는 왼쪽부터 한 줄에 하나씩 `r행 c열` (**1부터** 세요). 빈자리가 없으면 `만석` 한 줄\n3. 좌석 지도: 빈자리는 `O`, 사용 중은 `X` 로 바꿔 행마다 붙여서 출력\n4. `줄별 빈자리: [..]` — 행마다 빈자리 수를 리스트로\n\n[조건] ○ 빈자리의 위치는 **`np.where(조건)`** 으로 구해요 ○ 지도는 **`np.where(조건, "O", "X")`** 로 만들어요 ○ 좌석을 하나씩 검사하는 if 문은 쓰지 않아요',
D('''
import numpy as np
r, c = map(int, input().split())
seat = np.array([list(map(int, input().split())) for _ in range(r)])
rows, cols = np.where(seat == 0)      # 빈자리의 행 번호들, 열 번호들
print(f"빈자리: {len(rows)}개")
for i, j in zip(rows.tolist(), cols.tolist()):
    print(f"{i + 1}행 {j + 1}열")
if len(rows) == 0:
    print("만석")
mark = np.where(seat == 0, "O", "X")  # 같은 모양의 새 배열
for line in mark.tolist():
    print("".join(line))
print("줄별 빈자리:", (seat == 0).sum(axis=1).tolist())
'''), ['2 3\n1 0 1\n0 1 0', '2 2\n1 1\n1 1', '1 5\n0 0 1 0 0', '3 4\n1 1 0 1\n0 1 1 0\n1 1 1 1', '3 1\n0\n1\n0', '2 4\n0 0 0 0\n0 0 0 0', '4 3\n1 1 1\n1 0 1\n1 1 1\n0 1 1'],
  hints=['`rows, cols = np.where(seat == 0)` — 2차원이라 행 번호 배열과 열 번호 배열이 따로 나와요.', '`for i, j in zip(rows.tolist(), cols.tolist()):` 로 짝지어 `i + 1`, `j + 1` 을 출력해요.', '지도는 `np.where(seat == 0, "O", "X")`, 줄별 개수는 `(seat == 0).sum(axis=1).tolist()`'],
  ex='조건만 주면 **위치**, 세 개를 주면 **골라 바꾼 배열** — np.where 의 두 얼굴을 한 문제에서 모두 썼어요.'),
prac('[기출유사] 체력 측정 기록표 (행 선택 · 마지막 열 · boolean indexing)', '학생 n 명이 m 종목의 체력 측정을 했어요.\n\n입력: 첫 줄 `n m` (m 은 2 이상), 이어서 n 줄에 `이름 점수1 … 점수m`, 마지막 줄에 `k t` (k 는 1 부터 세는 학생 번호, t 는 기준 점수).\n\n출력\n1. `이름: [k번 학생의 점수 전체]`\n2. `마지막 종목: [모든 학생의 마지막 종목 점수]`\n3. `통과: ` 마지막 종목이 t 이상인 학생 이름(입력 순, 공백 구분). 없으면 `없음`\n4. `향상: ` 마지막 종목 점수가 첫 종목보다 **높은** 학생 이름. 없으면 `없음`\n5. `첫 두 종목 모두 t 이상: K명`\n6. `t 이상인 칸: K개` (전체 점수표에서)\n\n[조건] ○ 마지막 종목은 **슬라이싱 `[:, -1]`** 으로 ○ 이름은 **boolean indexing** 으로 골라요 ○ 5번은 `&` 를 사용 ○ 학생을 하나씩 도는 반복문은 입력에만',
D('''
import numpy as np
n, m = map(int, input().split())
names, rows = [], []
for _ in range(n):
    p = input().split()
    names.append(p[0])
    rows.append(list(map(int, p[1:])))
k, t = map(int, input().split())
names = np.array(names)
a = np.array(rows)
print(f"{names[k - 1]}: {a[k - 1].tolist()}")     # 행 선택
last = a[:, -1]                                   # 마지막 열
print("마지막 종목:", last.tolist())
ok = names[last >= t]                             # 조건으로 이름 고르기
print("통과:", " ".join(ok.tolist()) if len(ok) else "없음")
up = names[last > a[:, 0]]
print("향상:", " ".join(up.tolist()) if len(up) else "없음")
both = (a[:, 0] >= t) & (a[:, 1] >= t)
print(f"첫 두 종목 모두 {t} 이상: {int(both.sum())}명")
print(f"{t} 이상인 칸: {int((a >= t).sum())}개")
'''), ['3 3\n민서 70 80 90\n준호 85 60 75\n하린 50 55 40\n2 75', '2 2\n가 10 10\n나 20 5\n1 50', '4 3\n도윤 90 95 100\n서아 60 70 80\n지호 80 80 80\n유나 100 90 70\n4 80', '1 4\n솔 30 40 50 60\n1 45', '3 2\n가 99 100\n나 100 99\n다 100 100\n3 100', '5 3\n a 1 2 3\n b 3 2 1\n c 5 5 5\n d 0 9 4\n e 7 0 8\n5 4'],
  hints=['`a[k - 1]` 이 k번 학생의 행, `a[:, -1]` 이 마지막 종목 열이에요.', '`names[last >= t]` — 조건 배열의 길이가 n 이라 이름 배열을 그대로 고를 수 있어요.', '`both = (a[:, 0] >= t) & (a[:, 1] >= t)` 뒤 `int(both.sum())`'],
  ex='열을 뽑고(`[:, -1]`) → 그 열로 조건을 만들고 → 다른 배열(`names`)을 고르는 세 단계가 2025 8번의 구조예요.'),
prac('[기출유사] 달리기 기록순 이름 정렬 (np.sort · np.argsort)', '달리기 기록(초)이 주어져요. 기록은 **작을수록 빠르고**, 모든 기록은 서로 달라요.\n\n입력: 첫 줄 `n`, 둘째 줄에 이름 n 개, 셋째 줄에 기록 n 개(정수), 넷째 줄에 `k` (1 ≤ k ≤ n).\n\n출력\n1. `정렬된 기록: [..]` — 오름차순\n2. `느린 기록부터: [..]` — 내림차순\n3. `빠른 순: ` 이름을 빠른 순으로(공백 구분)\n4. `상위 k명: ` `이름(기록)` 을 빠른 순으로 k명\n5. `꼴찌: 이름`\n6. `평균보다 빠른 학생: ` 기록이 평균보다 작은 학생을 **빠른 순**으로\n\n[조건] ○ 1·2번은 **`np.sort`** 와 `[::-1]` ○ 3~6번은 **`np.argsort`** 로 구한 인덱스로 이름 배열을 인덱싱 ○ `sorted`, 리스트의 `sort` 는 쓰지 않아요',
D('''
import numpy as np
n = int(input())
names = np.array(input().split())
rec = np.array(list(map(int, input().split())))
k = int(input())
print("정렬된 기록:", np.sort(rec).tolist())
print("느린 기록부터:", np.sort(rec)[::-1].tolist())
order = np.argsort(rec)                 # 빠른 순서의 인덱스
print("빠른 순:", " ".join(names[order].tolist()))
top = order[:k]
print(f"상위 {k}명:", " ".join(f"{names[i]}({rec[i]})" for i in top.tolist()))
print("꼴찌:", names[order[-1]])
sn, sr = names[order], rec[order]       # 둘 다 빠른 순으로 정렬
print("평균보다 빠른 학생:", " ".join(sn[sr < rec.mean()].tolist()))
'''), ['4\n민 솔 준 하\n31 28 35 29\n2', '1\n혼자\n50\n1', '5\n가 나 다 라 마\n15 14 13 12 11\n5', '3\n도윤 서아 지호\n20 40 30\n1', '6\na b c d e f\n9 3 7 1 8 100\n3', '2\n토끼 거북\n12 300\n2'],
  hints=['`order = np.argsort(rec)` 가 "빠른 순서의 인덱스"예요. `names[order]` 가 빠른 순 이름.', '상위 k명은 `order[:k]`, 꼴찌는 `order[-1]`.', '`sn, sr = names[order], rec[order]` 로 둘 다 정렬한 뒤 `sn[sr < rec.mean()]`'],
  ex='`np.sort(names)` 는 이름의 가나다순일 뿐이에요. **기록의 argsort** 로 이름을 인덱싱해야 "기록순 이름"이 돼요.'),
prac('[심화] 미세먼지 센서 보정 (조건 대입 · where 겹치기 · 행별 정렬)', '측정소 R 곳에서 C 번씩 잰 미세먼지 값이 주어져요(C 는 2 이상). 센서 오류로 음수나 100 초과 값이 섞여 있어요.\n\n입력: 첫 줄 `R C`, 이어서 R 줄에 정수 C 개씩.\n\n출력\n1. `오류 값: K개` — 0 미만이거나 100 초과인 칸의 수\n2. 보정한 표: 음수는 `0`, 100 초과는 `100` 으로 바꿔 행마다 공백 구분\n3. 등급 표: 보정한 값이 70 이상이면 `H`, 30 이상이면 `M`, 나머지는 `L` 을 행마다 붙여서\n4. `측정소별 H: [..]` — 행마다 H 의 개수\n5. `측정소별 상위 2개 합: [..]` — 행마다 큰 값 두 개의 합\n6. `최댓값 V: (r,c) (r,c) …` — 보정한 표에서 최댓값이 있는 모든 위치(1부터, 위쪽 행·왼쪽 열 먼저)\n\n[조건] ○ 보정은 **`a[조건] = 값`** 으로 ○ 등급은 **`np.where` 를 겹쳐서** ○ 5번은 `np.sort` 로 행마다 정렬한 뒤 슬라이싱 ○ 6번은 `np.where(조건)`',
D('''
import numpy as np
r, c = map(int, input().split())
a = np.array([list(map(int, input().split())) for _ in range(r)])
bad = (a < 0) | (a > 100)
print(f"오류 값: {int(bad.sum())}개")
a[a < 0] = 0                      # 조건에 맞는 칸만 대입
a[a > 100] = 100
for row in a.tolist():
    print(*row)
g = np.where(a >= 70, "H", np.where(a >= 30, "M", "L"))
for row in g.tolist():
    print("".join(row))
print("측정소별 H:", (a >= 70).sum(axis=1).tolist())
desc = np.sort(a)[:, ::-1]        # 행마다 내림차순
print("측정소별 상위 2개 합:", desc[:, :2].sum(axis=1).tolist())
rr, cc = np.where(a == a.max())
print(f"최댓값 {int(a.max())}:", " ".join(f"({i + 1},{j + 1})" for i, j in zip(rr.tolist(), cc.tolist())))
'''), ['2 3\n12 -3 105\n40 100 -1', '1 2\n50 50', '3 3\n70 30 29\n0 100 69\n101 -50 31', '2 4\n-1 -2 -3 -4\n200 300 400 500', '3 2\n10 20\n30 40\n50 60', '2 5\n99 98 97 96 95\n1 2 3 4 5', '4 2\n70 70\n69 71\n100 0\n30 29'],
  hints=['오류 개수는 `((a < 0) | (a > 100)).sum()` — **보정하기 전에** 세야 해요.', '등급: `np.where(a >= 70, "H", np.where(a >= 30, "M", "L"))` — 거짓일 때 값 자리에 where 를 한 번 더.', '행마다 내림차순은 `np.sort(a)[:, ::-1]`, 앞의 두 열은 `[:, :2]`, 행별 합은 `.sum(axis=1)`'],
  ex='`np.sort(a)[::-1]` 은 **행의 순서**만 뒤집어요. 행 안에서 뒤집으려면 `[:, ::-1]`. 그리고 오류 개수는 보정 전에 세야 한다는 **순서**가 숨은 채점 포인트예요.'),
)

# ============================================================ D10 검증용 코드
_M6 = D('''
d = {"a": "4", "b": "x"}
k = int(d.get("c", "0"))
try:
    n = int(d["a"])
    m = int(d["c"])
except ValueError:
    m = 0
print(n + m + k)
''')
assert errline(_M6) == 5 and err(_M6) == 'KeyError'
_M8 = D('''
def make():
    total = 0
    def add(x):
        total += x
        return total
    return add
f = make()
print(f(3))
''')
assert err(_M8) == 'UnboundLocalError' and errline(_M8) == 4
assert run(_M8.replace('        total += x', '        nonlocal total\n        total += x') + '\nprint(f(4))') == '3\n7'

# ============================================================ D10
D10 = lesson('10강. 만점 모의고사 — 2학기 2차 고사 실전', 60,
'- 시간 배분: 소형 문항(출력 추론·서술) 20분 → 중형 15분 → 대형 20분 → 검토 5분\n- 출력 추론: map·filter·제너레이터는 **꺼낼 때** 실행되고 **한 번 쓰면 끝**\n- 데코레이터: `@` 줄에서 바깥 함수가 **정의 시점에 한 번**, wrapper 는 **호출할 때마다**\n- 서술형 3요소: **이름**(무엇이) + **이유**(왜) + **해결/효과**(그래서)\n- [조건] 의 금지 함수부터 동그라미 — 직접 구현은 "변수 하나 + 한 번 훑기"\n- numpy: **값**은 `a[조건]`, **위치**는 `np.where(조건)`, **순서**는 `np.argsort`',
review('🔁 마스터의 스킬 [δ] 총정리', [T('아홉 강의 핵심을 한 장씩 확인해요.'), flip(['1강 — map·filter 의 결과', '필요할 때 하나씩 만드는 이터레이터 — 한 번 다 쓰면 빈 것'], ['2강 — sorted·max·set·count 금지', '변수 하나를 두고 한 번 훑으며 직접 비교·갱신'], ['3강 — swapped 의 역할', '한 바퀴 동안 교환이 없으면 이미 정렬 → break (조기 종료)'], ['4강 — for 문의 속사정', '`iter()` 한 번 → `next()` 반복 → StopIteration 이면 종료'], ['5강 — 제너레이터와 메모리', '값을 한꺼번에 저장하지 않고 필요할 때 하나씩 만든다'], ['6강 — nonlocal', '바깥 함수의 변수에 **대입**하려면 필요 (없으면 UnboundLocalError)'], ['7강 — @deco', '`f = deco(f)` — 정의할 때 바로 실행된다'], ['8강 — "w" 와 "a"', 'w 는 여는 순간 지움, a 는 뒤에 이어 씀'], ['9강 — argsort', '정렬 순서대로 늘어놓은 **원래 인덱스**'])]),
explain('모의고사 안내',
  [T('실제 2차 고사와 같은 구성이에요. 확인 문제 8개는 소형 문항, 실습 5개는 중·대형 문항이에요. **50분** 타이머를 켜고 풀어 보세요.'),
   steps(['소형 문항 (42점)', '출력 추론 4 (1·2·3·7번, 23점) · 서술 2 (4·5번, 11점) · 오류 줄 찾기 1 (6번, 4점) · 선택 1 (8번, 4점)'], ['중형 문항 (22점)', '실습 9번(10점), 10번(12점)'], ['대형 문항 (36점)', '실습 11번(12점), 12번(12점), 13번(12점)']),
   exam('틀린 문제는 🔁 오답 복습으로 다시 풀고 해당 강의 설명을 다시 읽으세요. 이어서 **The MASTER [δ]** 문제로 몸에 익히면 준비가 끝나요.')]),
outq('[모의 1 · 5점] 출력 결과는?', D('''
nums = [0b101, 0o17, 0x1F, int("11", 2)]
print(nums, bin(10), hex(255), int("ff", 16))
words = ["kiwi", "fig", "banana", "plum"]
print(sorted(words, key=len), max(words, key=len))
print(sorted(words, key=lambda w: (-len(w), w))[1])
print(all(n % 2 for n in nums), any(len(w) > 5 for w in words), all([]))
''')),
outq('[모의 2 · 6점] 출력 결과는?', D('''
class Up:
    def __init__(self, n):
        self.n = n
        self.i = 0
    def __iter__(self):
        print("I", end=" ")
        return self
    def __next__(self):
        if self.i >= self.n:
            raise StopIteration
        self.i += 1
        return self.i
def gen(it):
    for x in it:
        print("g", end=" ")
        yield x * 10
u = Up(3)
g = gen(u)
print("start")
print(next(g))
print(list(g), list(g), len(list(u)))
''')),
outq('[모의 3 · 6점] 출력 결과는?', D('''
def twice(f):
    print("D")
    def wrapper(*args):
        print("W", args)
        return f(*args) * 2
    return wrapper
def counter():
    c = 0
    def inc():
        nonlocal c
        c += 1
        return c
    return inc
@twice
def add(*nums):
    return sum(nums)
k = counter()
print("S")
print(add(1, 2, 3))
print(k(), k(), add(k()))
''')),
essay('[모의 4 · 6점] 1 부터 1000만까지 수의 제곱의 합을 구하는 두 코드가 있어요. 결과는 같지만 **(나)가 메모리를 훨씬 적게 써요.** 그 이유를 두 표현식이 **값을 만드는 방식**과 연결하여 서술하고, (나)의 `g` 로 합을 한 번 구한 뒤 `sum(g)` 을 **다시** 호출하면 결과가 무엇인지와 그 이유를 쓰세요.\n\n```\n(가) a = [x * x for x in range(1, 10000001)]\n     print(sum(a))\n(나) g = (x * x for x in range(1, 10000001))\n     print(sum(g))\n```', '(가)의 리스트 컴프리헨션은 1000만 개의 제곱 값을 모두 계산해 리스트에 한꺼번에 저장하므로 원소 개수에 비례하는 메모리가 필요하다. (나)의 제너레이터 표현식은 값을 미리 만들어 저장하지 않고, sum 이 다음 값을 요구할 때마다 하나씩 계산해 넘겨주고 버리므로(지연 평가) 한 번에 값 하나 분량의 메모리만 쓴다. 제너레이터는 한 번 끝까지 꺼내면 소진되어 다시 처음으로 돌아가지 않으므로, sum(g) 을 다시 호출하면 꺼낼 값이 없어 0 이 나온다.', ['(가)는 모든 값을 리스트에 한꺼번에 저장한다고 썼다', '(나)는 필요할 때 값을 하나씩 만들어 낸다(저장하지 않는다)고 썼다', '두 번째 sum(g) 의 결과가 0 이라고 썼다', '제너레이터는 한 번 쓰면 소진된다는 이유를 썼다']),
essay('[모의 5 · 5점] 아래 버블 정렬에서 **변수 `swapped` 의 역할**을 쓰고, `[1, 2, 3, 4, 5]` 를 정렬할 때 `swapped` 가 **있을 때와 없을 때**(6~7번 줄과 2번 줄 삭제) 비교 횟수가 각각 몇 번인지 근거와 함께 쓰세요.\n\n```\n1 for i in range(len(a) - 1):\n2     swapped = False\n3     for j in range(len(a) - 1 - i):\n4         if a[j] > a[j + 1]:\n5             a[j], a[j + 1] = a[j + 1], a[j]\n6             swapped = True  (5번 줄과 같은 들여쓰기)\n7     if not swapped: break\n```', 'swapped 는 바깥 반복 한 바퀴 동안 교환이 한 번이라도 일어났는지를 기록하는 변수이다. 한 바퀴 동안 교환이 없었다면 모든 이웃한 쌍이 이미 순서대로라는 뜻이므로 리스트가 정렬된 것이고, 남은 바퀴를 돌 필요가 없어 break 로 반복을 끝낸다(조기 종료). [1, 2, 3, 4, 5] 는 이미 정렬되어 있으므로 swapped 가 있으면 첫 바퀴에서 4번 비교한 뒤 교환이 없어 바로 끝나 4번이다. swapped 가 없으면 끝까지 돌아 4 + 3 + 2 + 1 = 10번 비교한다.', ['한 바퀴 동안 교환이 있었는지 기록한다고 썼다', '교환이 없으면 이미 정렬된 것이므로 반복을 끝낸다(조기 종료)고 썼다', '있을 때 4번이라고 썼다', '없을 때 10번(4+3+2+1)이라고 썼다']),
spot('[모의 6 · 4점] **예외가 발생하는 줄**은?', _M6, 5, '2번 줄의 `d.get("c", "0")` 은 키가 없어도 기본값을 주므로 정상이에요. 5번 줄 `d["c"]` 에서 **KeyError** 가 나는데 except 는 ValueError 만 받으므로 처리되지 않고 프로그램이 멈춰요.'),
outq('[모의 7 · 6점] 출력 결과는?', D('''
import numpy as np
a = np.array([[7, 2, 9],
              [4, 8, 1],
              [6, 3, 5]])
print(a[:, -1].tolist(), a[1:, :2].tolist(), a[a > 6].tolist())
r, c = np.where(a < 3)
print(r.tolist(), c.tolist(), np.sort(a[0])[::-1].tolist())
names = np.array(["가", "나", "다"])
print(names[np.argsort(a[:, 1])].tolist(), int((a % 2 == 0).sum()), np.where(a[2] > 4, 1, 0).tolist())
''')),
ch('[모의 8 · 4점] 아래 코드에 대한 설명으로 옳은 것은?\n\n```\ndef make():\n    total = 0\n    def add(x):\n        total += x\n        return total\n    return add\nf = make()\nprint(f(3))\n```', ['`3` 이 출력된다', '`total += x` 에서 UnboundLocalError 가 난다. `add` 안에 `nonlocal total` 을 넣으면 `3` 이 출력된다', '`f = make()` 에서 TypeError 가 난다', '`total += x` 에서 NameError 가 난다. `global total` 을 넣으면 고쳐진다'], 2, '함수 안에서 **대입**하는 이름은 그 함수의 지역 변수로 취급돼요. 그래서 `total += x` 는 아직 값이 없는 지역 변수 total 을 읽으려다 UnboundLocalError 가 나요. 바깥 함수의 변수를 고치려면 `nonlocal`(전역이 아니므로 global 은 안 돼요).'),
prac('[모의 9 · 10점] 응원 점수 분석 — 내장함수 없이', '응원전 심사 점수(정수)가 한 줄에 공백으로 구분되어 2개 이상 주어져요.\n\n출력\n1. `가장 큰 두 수의 합: S` — 가장 큰 값과 그다음으로 큰 값의 합 (같은 값이 두 번 있으면 그 둘)\n2. `중복 제거: ` 처음 나온 순서를 지켜 중복을 없앤 점수(공백 구분)\n3. `최빈 점수: V (C번)` — 가장 많이 나온 점수. 횟수가 같으면 **먼저 나온** 점수\n\n[조건] ○ `sorted`, `sort`, `max`, `min`, `sum`, `set`, `count` 를 쓰지 않아요 ○ 딕셔너리와 반복문으로 직접 구해요',
D('''
a = list(map(int, input().split()))
# 1. 가장 큰 두 수: first, second 를 한 번 훑으며 갱신
if a[0] >= a[1]:
    first, second = a[0], a[1]
else:
    first, second = a[1], a[0]
for x in a[2:]:
    if x > first:
        first, second = x, first
    elif x > second:
        second = x
print("가장 큰 두 수의 합:", first + second)
# 2. 중복 제거 (순서 유지)
uniq = []
for x in a:
    if x not in uniq:
        uniq.append(x)
print("중복 제거:", *uniq)
# 3. 최빈 점수: 딕셔너리로 세고, uniq 순서대로 가장 큰 횟수 찾기
cnt = {}
for x in a:
    cnt[x] = cnt.get(x, 0) + 1
best = uniq[0]
for x in uniq:
    if cnt[x] > cnt[best]:
        best = x
print(f"최빈 점수: {best} ({cnt[best]}번)")
'''), ['7 9 7 8 9 9', '5 5', '3 1 2', '-4 -9 -4 -1 -9', '10 20 30 40 50 60', '8 8 6 6 8 6 9', '1 100 1 100'],
  hints=['처음 두 값으로 `first`, `second` 를 정한 뒤 세 번째 값부터 훑어요. `x > first` 이면 **기존 first 가 second 로 내려가요**.', '중복 제거는 `if x not in uniq: uniq.append(x)`.', '`cnt[x] = cnt.get(x, 0) + 1` 로 센 뒤, `uniq` 순서로 돌며 `>` (같으면 바꾸지 않음) 로 비교하면 먼저 나온 값이 남아요.']),
prac('[모의 10 · 12점] 대기 번호 정렬 — 버블 정렬과 조기 종료', '정수가 한 줄에 공백으로 구분되어 주어져요. **버블 정렬**로 오름차순 정렬하면서 과정을 출력해요.\n\n- 한 바퀴는 앞에서부터 이웃한 두 값을 비교해 앞이 더 크면 교환해요.\n- 바퀴가 끝날 때마다 맨 뒤에 확정된 값은 다음 바퀴의 비교에서 **제외**해요.\n- 한 바퀴 동안 교환이 **한 번도 없으면** 그 바퀴를 끝으로 정렬을 멈춰요.\n\n출력\n1. 바퀴마다 `k바퀴: ` 뒤에 그 바퀴가 끝난 뒤의 리스트(공백 구분)\n2. `비교 A번, 교환 B번`\n3. `결과: ` 정렬된 리스트\n\n값이 하나뿐이면 바퀴 줄 없이 2·3번만 출력해요.\n\n[조건] ○ `sorted`, `sort` 를 쓰지 않아요 ○ 교환 여부를 기록하는 변수를 사용해 조기 종료해요',
D('''
a = list(map(int, input().split()))
n = len(a)
comp = swap = 0
for i in range(n - 1):
    swapped = False
    for j in range(n - 1 - i):          # 뒤쪽 i 칸은 이미 확정
        comp += 1
        if a[j] > a[j + 1]:
            a[j], a[j + 1] = a[j + 1], a[j]
            swap += 1
            swapped = True
    print(f"{i + 1}바퀴:", *a)
    if not swapped:                     # 교환이 없었으면 이미 정렬됨
        break
print(f"비교 {comp}번, 교환 {swap}번")
print("결과:", *a)
'''), ['5 1 4 2 8', '1 2 3 4 5', '9', '3 2 1', '2 1 3 4 5 6', '4 4 4 4', '6 5 4 3 2 1 0'],
  hints=['바깥 `for i in range(n - 1)`, 안쪽 `for j in range(n - 1 - i)` — `- i` 가 "확정된 부분 제외"예요.', '바퀴를 시작할 때 `swapped = False`, 교환하면 `True`.', '바퀴 줄을 **출력한 뒤** `if not swapped: break` — 교환이 없던 마지막 바퀴도 출력돼요.']),
prac('[모의 11 · 12점] 수업 종 시각 — 이터레이터와 제너레이터', '수업 시작 종이 울리는 시각을 차례로 만들어 주는 이터레이터 클래스 `Bell` 을 만들어요.\n\n- `Bell(h, m, gap, n)` : `h`시 `m`분부터 `gap` 분 간격으로 **n 번** 울려요. `gap` 이 1 미만이거나 `n` 이 0 미만이면 생성자에서 `ValueError("잘못된 설정")` 을 발생시켜요.\n- `__iter__` 는 자기 자신을, `__next__` 는 다음 시각을 `"HH:MM"` 문자열(두 자리씩)로 돌려주고 n 번을 넘으면 `StopIteration`. 24시를 넘으면 00시부터 다시 세요.\n- 제너레이터 함수 `morning(it)` : 이터레이터 `it` 에서 꺼낸 시각 중 **12:00 이전**인 것만 `yield`\n\n입력: 한 줄에 `h m gap n`\n\n출력\n1. 설정이 잘못되면 `오류: 잘못된 설정` 한 줄만 출력하고 끝\n2. `전체: ` 모든 시각(공백 구분, for 문 사용). 하나도 없으면 `전체: 없음`\n3. `오전: K번` — **새 Bell 객체**를 `morning` 에 넣어 센 개수\n4. 2번에서 다 쓴 객체에 `next()` 를 한 번 더 호출해, StopIteration 이면 `더 없음`\n\n[조건] ○ `__iter__`, `__next__`, `raise StopIteration` 을 직접 구현 ○ `morning` 은 `yield` 사용 ○ 오류는 try/except 로 처리',
D('''
class Bell:
    def __init__(self, h, m, gap, n):
        if gap < 1 or n < 0:
            raise ValueError("잘못된 설정")
        self.t = h * 60 + m      # 다음에 울릴 시각(분)
        self.gap = gap
        self.left = n            # 남은 횟수
    def __iter__(self):
        return self
    def __next__(self):
        if self.left == 0:
            raise StopIteration
        t = self.t % (24 * 60)
        self.t += self.gap
        self.left -= 1
        return f"{t // 60:02d}:{t % 60:02d}"

def morning(it):
    for s in it:
        if s < "12:00":          # "HH:MM" 은 문자열 비교가 곧 시각 비교
            yield s

h, m, gap, n = map(int, input().split())
try:
    b = Bell(h, m, gap, n)
except ValueError as e:
    print("오류:", e)
else:
    times = [s for s in b]
    print("전체:", " ".join(times) if times else "없음")
    print(f"오전: {sum(1 for _ in morning(Bell(h, m, gap, n)))}번")
    try:
        next(b)
    except StopIteration:
        print("더 없음")
'''), ['8 40 60 5', '9 0 0 3', '23 30 20 4', '11 55 5 3', '13 0 50 2', '0 0 1 0', '7 5 -10 2', '6 0 180 4'],
  hints=['시각을 **분 하나**(`h * 60 + m`)로 저장하면 `+= gap` 만 하면 돼요. 꺼낼 때 `% (24 * 60)`.', '`__next__`: 남은 횟수가 0 이면 `raise StopIteration`, 아니면 `f"{t // 60:02d}:{t % 60:02d}"` 를 return.', '`morning` 은 `for s in it: if s < "12:00": yield s`. 다 쓴 `b` 는 다시 쓸 수 없으니 오전 개수는 **새 Bell** 로 세요.']),
prac('[모의 12 · 12점] 퀴즈 대회 결과 파일 — 파일 · 예외 · 정렬', '퀴즈 대회 기록을 파일로 저장하고 다시 읽어 순위를 만들어요.\n\n입력: 첫 줄 `n`, 이어서 n 줄에 `이름 점수1 점수2 …` (점수는 1개 이상이어야 정상).\n\n1. 입력받은 n 줄을 그대로 `quiz.txt` 에 저장한 뒤 **파일을 읽어** 처리해요.\n2. 줄마다 검사: 이름만 있거나 빈 줄 → `N번 줄: 점수 없음` / 점수 중 정수가 아닌 것이 있음 → `N번 줄: 숫자 아님` (그 줄은 건너뛰어요)\n3. 정상 기록을 **총점 내림차순, 같으면 이름 사전순**으로 정렬해 `result.txt` 에 `순위 이름 총점` 형식으로 한 줄씩 저장(순위는 1부터 차례로). 정상 기록이 없으면 `참가자 없음` 한 줄만 저장.\n4. `bonus.txt` 를 읽기 모드로 열어 보고, 없으면 `보너스 파일 없음` 을 출력해요(이 파일은 만들지 않아요).\n\n출력: 오류 줄 메시지(순서대로) → `보너스 파일 없음` → `result.txt` 의 내용 그대로.\n\n[조건] ○ 점수 없음은 **IndexError**, 숫자 아님은 **ValueError** 를 각각의 except 로 ○ try 는 줄 단위로 ○ 정렬은 `sorted` 또는 `sort` 에 `key=lambda` ○ 없는 파일은 **FileNotFoundError** 로 처리',
D('''
n = int(input())
with open("quiz.txt", "w", encoding="utf-8") as f:
    for _ in range(n):
        f.write(input() + "\\n")
data = []
with open("quiz.txt", encoding="utf-8") as f:
    for no, line in enumerate(f, 1):
        parts = line.split()
        try:
            name = parts[0]            # 빈 줄이면 IndexError
            first = parts[1]           # 이름만 있으면 IndexError
            total = sum(int(x) for x in parts[1:])   # 숫자가 아니면 ValueError
        except IndexError:
            print(f"{no}번 줄: 점수 없음")
        except ValueError:
            print(f"{no}번 줄: 숫자 아님")
        else:
            data.append([name, total])
try:
    with open("bonus.txt", encoding="utf-8") as f:
        bonus = f.read()
except FileNotFoundError:
    print("보너스 파일 없음")
data.sort(key=lambda d: (-d[1], d[0]))
with open("result.txt", "w", encoding="utf-8") as f:
    if not data:
        f.write("참가자 없음\\n")
    for rank, (name, total) in enumerate(data, 1):
        f.write(f"{rank} {name} {total}\\n")
with open("result.txt", encoding="utf-8") as f:
    print(f.read().rstrip())
'''), ['4\n민서 30 40 20\n준호 50 x 10\n하린\n도윤 45 45', '2\n가 abc\n나', '3\n다 10\n가 10\n나 10', '1\n솔 100 100 100', '5\na 1 2 3\nb 3 2 1\nc 6\nd -5 20\ne 2.5 3', '3\n가 0\n\n나 5 5', '4\n유나 70 80\n서아 80 70\n지호 90 61\n태민 10 1o'],
  hints=['`parts[0]`, `parts[1]` 을 **읽는 것만으로** 조각이 모자라면 IndexError 가 나요. 그다음 `int()` 변환에서 ValueError.', 'except 두 개 + `else:` 에서 `data.append([name, total])`.', '`data.sort(key=lambda d: (-d[1], d[0]))`, 순위는 `enumerate(data, 1)`.']),
prac('[모의 13 · 12점] 모의고사 성적 분석 — numpy', '학생 n 명의 시험 m 회 점수가 주어져요(m 은 2 이상). **학생들의 총점은 모두 달라요.**\n\n입력: 첫 줄 `n m`, 이어서 n 줄에 `이름 점수1 … 점수m`.\n\n출력\n1. `마지막 시험: [..]` — 모든 학생의 마지막 시험 점수\n2. `평균 이상: ` 마지막 시험 점수가 그 시험의 평균 **이상**인 학생 이름(입력 순, 공백 구분)\n3. `총점 순위: ` 이름을 총점이 높은 순으로(공백 구분)\n4. `1등: 이름 [점수들을 높은 순으로]`\n5. `재시험: ` 마지막 시험이 60 미만인 학생의 **번호**(1부터, 공백 구분). 없으면 `없음`\n6. `보정 총합: T` — 40 미만인 점수를 모두 40 으로 올렸을 때 전체 점수의 합\n\n[조건] ○ 1번은 슬라이싱 ○ 2번은 boolean indexing ○ 3·4번은 `np.argsort`, `np.sort` 와 `[::-1]` ○ 5번은 `np.where(조건)` ○ 6번은 `np.where(조건, x, y)` ○ `sorted` 와 학생을 하나씩 검사하는 if 문은 쓰지 않아요',
D('''
import numpy as np
n, m = map(int, input().split())
names, rows = [], []
for _ in range(n):
    p = input().split()
    names.append(p[0])
    rows.append(list(map(int, p[1:])))
names = np.array(names)
a = np.array(rows)
last = a[:, -1]
print("마지막 시험:", last.tolist())
print("평균 이상:", " ".join(names[last >= last.mean()].tolist()))
order = np.argsort(a.sum(axis=1))[::-1]       # 총점 내림차순 인덱스
print("총점 순위:", " ".join(names[order].tolist()))
top = order[0]
print(f"1등: {names[top]} {np.sort(a[top])[::-1].tolist()}")
low = np.where(last < 60)[0]
print("재시험:", " ".join(str(i + 1) for i in low.tolist()) if len(low) else "없음")
print("보정 총합:", int(np.where(a < 40, 40, a).sum()))
'''), ['3 3\n민서 70 80 90\n준호 85 60 55\n하린 30 95 40', '2 2\n가 100 100\n나 99 100', '4 2\n도윤 10 20\n서아 39 40\n지호 41 59\n유나 60 61', '1 3\n솔 35 36 37', '5 4\na 50 50 50 50\nb 90 10 90 11\nc 0 0 0 100\nd 60 60 60 61\ne 70 80 90 100', '3 2\n가 59 60\n나 60 58\n다 100 0'],
  hints=['`last = a[:, -1]`, 이름 고르기는 `names[last >= last.mean()]`.', '`order = np.argsort(a.sum(axis=1))[::-1]` — 총점의 argsort 를 뒤집으면 1등부터의 인덱스.', '재시험 번호는 `np.where(last < 60)[0]` 에 1 을 더해 출력, 보정 총합은 `np.where(a < 40, 40, a).sum()`']),
)

# 배점 합계 100 확인
_pts = [int(re.search(r'\[모의 \d+ · (\d+)점\]', s.get('question') or s.get('title') or '').group(1)) for s in D10['steps'] if '[모의' in (s.get('question') or s.get('title') or '')]
assert len(_pts) == 13 and sum(_pts) == 100 and sum(_pts[:8]) == 42 and sum(_pts[8:10]) == 22 and sum(_pts[10:]) == 36, _pts

D9['libs'] = ['numpy']
D10['libs'] = ['numpy']
