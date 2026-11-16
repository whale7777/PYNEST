from glib import *

# ============================================================ G4
G4 = lesson('4강. 모듈과 __name__ — 파일을 나누는 이유', 40,
'- `import m` → `m.f()` / `from m import f` → `f()` / `import m as x` → `x.f()` — **점 앞에 쓰는 이름**이 달라진다\n- `from m import f` 로 가져온 이름은 **내 변수와 충돌**할 수 있다 (뒤에 쓴 것이 이김)\n- import 하면 그 파일이 **위에서 아래로 한 번 실행**된다\n- `__name__` : 직접 실행한 파일에서는 `"__main__"`, import 된 파일에서는 **모듈 이름**\n- `if __name__ == "__main__":` → 직접 실행할 때만 돌릴 코드(테스트·메인)를 넣는 곳\n- 모듈의 장점: **재사용**, **이름 정리**(충돌 방지), **유지보수·협업**',
review('🔁 3강 복습', [T('종합 문제의 뼈대를 확인해요.'), rev('한 줄이 틀려도 나머지를 계속 처리하려면 try 를 어디에?', '반복문 **안**(줄 단위)에 둬요.'), rev('`parts[1]` 과 `a, b = parts` — 조각이 1개일 때 예외는?', '인덱스는 IndexError, 언패킹은 ValueError'), rev('표에 없는 글자를 ValueError 로 알리려면?', code='if ch not in TABLE:\n    raise ValueError(ch)')]),
outq('복습 — 출력 결과는?', D('''
table = {"a": 1, "b": 2}
def score(word):
    total = 0
    for ch in word:
        if ch not in table:
            raise ValueError(ch)
        total += table[ch]
    return total
out = []
for w in ["ab", "abc", "bb", ""]:
    try:
        out.append(score(w))
    except ValueError as e:
        out.append(str(e))
print(out)
'''), review=True),
explain('import 세 가지 — 점 앞에 무엇을 쓰는가',
  [T('모듈은 **함수·변수를 모아 둔 파이썬 파일**이에요. 가져오는 방법에 따라 **부르는 이름**이 달라져요(2023 2번 10점, 2025 4번 11점).'),
   tabs(['import math', '모듈 통째로. 쓸 때 **`모듈이름.`** 을 붙여요.', 'import math\nprint(math.sqrt(16))\nprint(math.pi)'], ['from math import sqrt, pi', '필요한 이름만. **점 없이** 바로 써요. `math.` 은 쓸 수 없어요.', 'from math import sqrt, pi\nprint(sqrt(16))\nprint(pi)'], ['import math as m', '모듈에 **별명**. 원래 이름 `math` 는 쓸 수 없어요.', 'import math as m\nprint(m.sqrt(16))'], ['from math import sqrt as s', '가져온 이름에 별명', 'from math import sqrt as s\nprint(s(16))']),
   key('규칙은 하나예요: **import 문에 적힌 마지막 이름**만 내 코드에서 쓸 수 있어요. `import random as r` 뒤에는 `r` 만, `from math import pi` 뒤에는 `pi` 만.')],
  [T('`from … import …` 는 편하지만, 가져온 이름이 **내 변수와 같은 칸**에 들어와요. 같은 이름을 또 쓰면 덮어써요.'),
   C(D('''
from math import pi
print(pi)
pi = 3
print(pi)
import math
print(math.pi)
'''), 'import math 로 가져오면 math.pi 는 안전해요'),
   CX(D('''
from math import sqrt
def sqrt(x):          # 같은 이름의 함수를 또 만듦 → 덮어씀
    return x / 2
print(sqrt(16))       # 4.0 이 아니라 8.0
''')),
   warn('`from math import *` 는 모듈의 이름을 **전부** 가져와요. 무엇이 들어왔는지 보이지 않아 충돌을 알아채기 어려워요. 시험에서는 "이 방식의 문제점"으로 물어요.')],
  [T('1학기부터 쓰던 두 모듈의 **경계**를 다시 확인해요.'),
   flip(['random.randint(1, 6)', '1 **이상** 6 **이하** — 양 끝 포함 (6가지)'], ['random.sample(range(1, 46), 6)', '**중복 없이** 6개를 뽑은 리스트'], ['random.choice(seq)', '하나를 뽑음 (빈 시퀀스면 IndexError)'], ['math.sqrt(16)', '4.0 — 항상 **실수**'], ['math.floor(-2.5) / math.ceil(-2.5)', '-3 / -2']),
   C(D('''
import random
lotto = sorted(random.sample(range(1, 46), 6))
pw = "".join(random.sample("abcdefgh", 4))
print(len(lotto), len(set(lotto)), len(pw), len(set(pw)))
'''), '뽑힌 값은 매번 달라도, 개수와 "중복 없음"은 항상 같아요')]),
explain('내 모듈 만들기와 __name__',
  [T('내가 만든 `.py` 파일도 모듈이에요. 2025 6번(12점)은 `main.py` 가 `str_utils.py` 와 `math_utils.py` 를 가져다 쓰는 구조였어요.'),
   CX(D('''
def mean(nums):
    return sum(nums) / len(nums)

def spread(nums):
    return max(nums) - min(nums)
'''), 'math_utils.py'),
   CX(D('''
import math_utils
from str_utils import reverse

data = [3, 9, 6]
print(math_utils.mean(data))
print(reverse("abc"))
'''), 'main.py'),
   key('`import math_utils` 를 만나면 파이썬은 `math_utils.py` 를 **위에서 아래로 전부 실행**해요. def 는 함수를 만들 뿐이라 화면에 아무것도 안 나오지만, 그 파일에 `print` 가 있으면 **import 하는 순간 출력**돼요.')],
  [T('그래서 모듈 파일에 넣어 둔 테스트 코드가 문제를 일으켜요. 이걸 막는 장치가 `__name__` 이에요.'),
   C(D('''
print(__name__)
'''), '지금 이 코드는 "직접 실행"한 것이라 __main__'),
   cmp('가드 없음', '# calc.py\ndef add(a, b):\n    return a + b\nprint(add(1, 2))      # 테스트', '가드 있음', '# calc.py\ndef add(a, b):\n    return a + b\nif __name__ == "__main__":\n    print(add(1, 2))  # 테스트', lb='main.py 에서 `import calc` 만 해도 3 이 출력돼요', rb='calc.py 를 직접 실행할 때만 3 이 출력돼요. import 될 때는 `__name__ == "calc"` 라 건너뛰어요', tones=('bad', 'good')),
   tip('`__name__` 은 파이썬이 **파일마다 자동으로 만들어 주는 변수**예요. 값은 둘 중 하나: 직접 실행한 파일이면 `"__main__"`, import 된 파일이면 그 **모듈 이름**(파일 이름에서 `.py` 를 뗀 것).')],
  [exam('서술형으로 두 번 나왔어요. ① "`if __name__ == "__main__":` 을 쓰는 이유" ② "모듈을 사용하는 장점".'),
   steps(['재사용', '한 번 만든 함수를 여러 프로그램에서 import 해서 쓴다'], ['이름 정리', '`모듈.함수` 로 불러 같은 이름끼리 충돌하지 않는다'], ['유지보수·협업', '기능별로 파일을 나눠 고칠 곳을 찾기 쉽고, 여러 사람이 나눠 작업할 수 있다']),
   key('서술 틀: "모듈을 **직접 실행**하면 `__name__` 이 `"__main__"` 이고 **import** 되면 모듈 이름이 된다. 그래서 이 조건문 안의 코드는 직접 실행할 때만 실행되고, 다른 파일에서 import 할 때는 실행되지 않는다."')]),
outq('[기출유사] 출력 결과는?', D('''
import math as m
from math import floor
print(m.floor(-2.5), m.ceil(2.1), m.sqrt(16), int(m.sqrt(17)), floor(7 / 2), round(m.pi, 2))
'''), '`sqrt` 의 결과는 항상 실수(`4.0`), floor 는 **작은 쪽** 정수(-3)예요.'),
bucket('[기출유사] `import random as r` 과 `from math import sqrt` 를 실행한 뒤, 각 줄의 결과는?', ['정상', 'NameError'], [['r.randint(1, 6)', 1], ['random.randint(1, 6)', 2], ['randint(1, 6)', 2], ['sqrt(9)', 1], ['math.sqrt(9)', 2], ['math.pi', 2], ['r.choice("abc")', 1], ['pi', 2]], '**import 문에 적힌 마지막 이름만** 쓸 수 있어요. `r` 과 `sqrt` 만 내 코드에 들어왔고, `random`, `math`, `randint`, `pi` 라는 이름은 없어요.'),
outq('[기출유사] 이 파일을 **직접 실행**했을 때의 출력은?', D('''
def area(w, h):
    return w * h
print("A", __name__)
if __name__ == "__main__":
    print("B", area(3, 4))
if __name__ == "area":
    print("C")
print("D")
''')),
ch('[기출유사] `calc.py` 에 아래 코드가 있어요.\n\n```\ndef add(a, b):\n    return a + b\nprint(add(1, 2))\nif __name__ == "__main__":\n    print(add(3, 4))\n```\n\n`main.py` 에서 `import calc` 다음 줄에 `print(calc.add(10, 20))` 을 쓰고 **main.py 를 실행**하면 출력은?', ['30', '3 과 30 (두 줄)', '3, 7, 30 (세 줄)', '7 과 30 (두 줄)'], 2, 'import 하는 순간 calc.py 가 실행되어 가드 **밖**의 `print(add(1, 2))` 는 출력돼요. 가드 안은 `__name__ == "calc"` 라서 건너뛰어요.'),
sh('[기출유사] `random.randint(3, 8)` 이 돌려줄 수 있는 서로 다른 값은 몇 가지?', 6, '3, 4, 5, 6, 7, 8 — 양 끝을 모두 포함해요. `random.randrange(3, 8)` 이라면 5가지.'),
spot('[기출유사] **예외가 발생하는 줄**은?', D('''
from math import sqrt
nums = [4, 9, 16]
sqrt = [sqrt(n) for n in nums]
print(sqrt)
print(sqrt(25))
'''), 5, '3번 줄에서 `sqrt` 라는 이름이 **리스트**로 바뀌었어요. 5번 줄은 리스트를 함수처럼 호출해서 TypeError. 3번 줄 자체는 오른쪽을 먼저 계산하므로 정상이에요.'),
fill('[기출유사] 별명을 붙여 가져와요.', D('''
from math import pi ___ PI
import math ___ m
print(round(PI, 3), m.floor(PI))
'''), ['as', 'as'], expect='3.142 3'),
outq('[심화] 출력 결과는? (값은 매번 달라도 결과는 항상 같아요)', D('''
import random
lotto = random.sample(range(1, 46), 6)
dice = [random.randint(1, 6) for _ in range(200)]
pick = random.choice(["가", "나"])
print(len(lotto) == len(set(lotto)), min(dice) >= 1, max(dice) <= 6, 0 in dice, pick in "가나다")
'''), '`sample` 은 중복이 없고, `randint(1, 6)` 은 1~6 밖으로 나가지 않아요.'),
essay('[기출유사 · 서술 5점] 모듈 파일 아래쪽에 `if __name__ == "__main__":` 을 쓰고 그 안에 테스트 코드를 넣는 **이유**를 `__name__` 의 값과 연결해 서술하세요.', '__name__ 은 파이썬이 자동으로 만드는 변수로, 그 파일을 직접 실행하면 "__main__" 이 되고 다른 파일에서 import 하면 모듈 이름이 된다. 따라서 이 조건문 안의 코드는 파일을 직접 실행할 때만 실행되고, import 될 때는 실행되지 않는다. 이렇게 하면 모듈을 가져다 쓰는 프로그램에서 테스트 코드의 출력이 섞여 나오지 않으면서, 모듈 단독으로는 테스트를 할 수 있다.', ['직접 실행하면 __name__ 이 "__main__" 이라고 썼다', 'import 되면 모듈 이름이 된다고 썼다', '조건문 안의 코드가 import 될 때는 실행되지 않는다고 썼다', '테스트 코드가 다른 프로그램에서 실행되는 것을 막는다는 목적을 썼다']),
essay('[기출유사 · 서술 6점] ① 모듈을 사용하는 **장점 두 가지**를 쓰고, ② `math` 모듈의 `sqrt` 함수로 16 의 제곱근을 구하는 코드를 **서로 다른 import 방식 세 가지**로 쓰세요.', '① 한 번 만든 함수를 여러 프로그램에서 다시 쓸 수 있다(재사용). 기능별로 파일을 나눠 관리하므로 수정할 곳을 찾기 쉽고 이름 충돌을 줄일 수 있다(유지보수). ② import math → math.sqrt(16) / from math import sqrt → sqrt(16) / import math as m → m.sqrt(16)', ['장점 두 가지(재사용, 유지보수·이름 충돌 방지·협업 중)를 썼다', 'import math 와 math.sqrt(16) 을 짝지어 썼다', 'from math import sqrt 와 sqrt(16) 을 짝지어 썼다', 'import math as 별명 과 별명.sqrt(16) 을 짝지어 썼다'], 'import 방식과 **호출 모양이 짝이 맞아야** 점수예요. `from math import sqrt` 를 쓰고 `math.sqrt(16)` 으로 부르면 감점이에요.'),
match('import 문과 올바른 호출을 이어 보세요.', [['import random', 'random.choice(a)'], ['import random as rd', 'rd.choice(a)'], ['from random import choice', 'choice(a)'], ['from random import choice as pick', 'pick(a)']]),
prac('[기출유사 · 12점] 도구 모듈과 메인 가드', '`str_utils` 와 `math_utils` 에 들어갈 함수들을 한 파일에 만들고, **메인 코드는 `if __name__ == "__main__":` 안**에 작성해요.\n\n문자열 도구\n- `reverse(s)` : 뒤집은 문자열\n- `count_vowels(s)` : 모음(a e i o u, 대소문자 무시)의 개수\n- `is_palindrome(s)` : 공백을 빼고 대소문자를 무시했을 때 회문이면 True\n\n숫자 도구\n- `mean(nums)` : 평균\n- `median(nums)` : 중앙값(개수가 짝수면 가운데 두 수의 평균)\n- `spread(nums)` : 최댓값 - 최솟값\n\n입력: 첫 줄에 문자열, 둘째 줄에 정수들(1개 이상).\n\n출력(한 줄씩): 뒤집은 문자열 / 모음 개수 / 회문이면 `YES` 아니면 `NO` / 평균(소수 둘째 자리) / 중앙값(소수 첫째 자리) / 범위\n\n[조건] ○ 함수 안에서 input·print 를 쓰지 말 것 ○ median 은 원래 리스트를 바꾸지 말 것',
D('''
def reverse(s):
    return s[::-1]
def count_vowels(s):
    return sum(1 for c in s.lower() if c in "aeiou")
def is_palindrome(s):
    t = s.replace(" ", "").lower()
    return t == t[::-1]
def mean(nums):
    return sum(nums) / len(nums)
def median(nums):
    a = sorted(nums)
    n = len(a)
    if n % 2 == 1:
        return a[n // 2]
    return (a[n // 2 - 1] + a[n // 2]) / 2
def spread(nums):
    return max(nums) - min(nums)
if __name__ == "__main__":
    s = input()
    nums = list(map(int, input().split()))
    print(reverse(s))
    print(count_vowels(s))
    print("YES" if is_palindrome(s) else "NO")
    print(f"{mean(nums):.2f}")
    print(f"{median(nums):.1f}")
    print(spread(nums))
'''), ['Never odd or even\n7 1 4 10', 'Python\n5', 'A man a plan\n3 3 3', 'racecar\n9 2 8 1 7 3', 'AEIOU xyz\n-5 5', 'Was it a car\n10 20 30 40 51'],
  starter=D('''
def reverse(s):
    return s[::-1]
def count_vowels(s):
    pass
def is_palindrome(s):
    pass
def mean(nums):
    pass
def median(nums):
    pass
def spread(nums):
    pass
if __name__ == "__main__":
    s = input()
    nums = list(map(int, input().split()))
    print(reverse(s))
    # 이어서 출력
'''), hints=['회문: `t = s.replace(" ", "").lower()` 뒤 `t == t[::-1]`', '중앙값: `a = sorted(nums)` (새 리스트라 원본은 그대로) → 홀수면 `a[n // 2]`, 짝수면 가운데 두 수의 평균', '중앙값 출력은 `f"{median(nums):.1f}"` — 정수여도 `4.0` 처럼 나와요.'], ex='이 파일을 `tools.py` 로 저장하면 다른 프로그램에서 `from tools import median` 으로 바로 쓸 수 있어요. 가드 덕분에 import 할 때 input 을 기다리며 멈추지도 않아요.'),
prac('[기출유사 · 10점] math 모듈로 거리 계산', '운동장에 두 점 A(x1, y1), B(x2, y2) 가 있어요. A 에서 B 까지 **직선으로** 길이 `L` 미터짜리 줄을 이어 붙여 연결하려고 해요.\n\n입력: 첫 줄 `x1 y1 x2 y2` (정수), 둘째 줄 `L` (양의 정수)\n\n출력(한 줄씩)\n1. 두 점 사이의 거리 (소수 둘째 자리)\n2. 필요한 줄의 개수 (모자라면 안 되므로 **올림**) — 두 점이 같으면 0\n3. 자르지 않고 **통째로 다 쓰는** 줄의 개수 (**내림**)\n4. A, B 를 지름의 양 끝으로 하는 원의 넓이 (소수 둘째 자리)\n\n[조건] ○ `math.sqrt`, `math.ceil`, `math.floor`, `math.pi` 를 사용할 것 ○ `import math as m` 방식으로 가져올 것',
D('''
import math as m
x1, y1, x2, y2 = map(int, input().split())
L = int(input())
d = m.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
print(f"{d:.2f}")
print(m.ceil(d / L))
print(m.floor(d / L))
r = d / 2
print(f"{m.pi * r * r:.2f}")
'''), ['0 0 3 4\n2', '1 1 1 1\n5', '0 0 10 0\n5', '-3 -4 3 4\n3', '0 0 1 1\n1', '2 7 9 -1\n4'],
  starter=D('''
import math as m
x1, y1, x2, y2 = map(int, input().split())
L = int(input())
d = 0  # 두 점 사이의 거리
print(f"{d:.2f}")
'''), hints=['거리: `m.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)`', '거리가 정확히 10 이고 L 이 5 면 올림도 내림도 2 예요.', '원의 반지름은 거리의 절반: `m.pi * r * r`'], ex='`import math as m` 으로 가져왔으니 `math.sqrt` 라고 쓰면 NameError 예요. **별명을 붙이면 원래 이름은 사라져요.**'),
prac('[심화 · 14점] 로또 검사 모듈', '로또 용지를 검사하는 함수들을 만들고, 메인 가드 안에서 사용해요.\n\n- `parse(line)` : 공백으로 구분된 문자열을 정수 리스트로. 정수가 아닌 것이 있으면 **ValueError** 가 그대로 올라가게 둬요.\n- `is_valid(nums)` : 숫자가 **정확히 6개**이고, 모두 **1~45** 이며, **중복이 없으면** True\n- `count_match(mine, win)` : 일치하는 번호의 개수 (**set 의 교집합** 사용)\n- `rank(cnt, bonus_hit)` : 6개 → `1등`, 5개+보너스 → `2등`, 5개 → `3등`, 4개 → `4등`, 3개 → `5등`, 그 외 `낙첨`\n\n입력: 첫 줄에 당첨 번호 6개와 보너스 번호 1개(총 7개, 올바른 값), 둘째 줄 `n`, 이어서 n 줄의 용지.\n\n출력: 용지마다 `N개 일치 - 등수` 또는 `무효`(정수가 아닌 값이 있거나 is_valid 가 False). 마지막 줄에 `당첨 a장 / 낙첨 b장 / 무효 c장` (당첨 = 1~5등).\n\n[조건] ○ 네 함수의 이름과 역할을 지킬 것 ○ 메인 코드는 `if __name__ == "__main__":` 안에',
D('''
def parse(line):
    return [int(x) for x in line.split()]
def is_valid(nums):
    return len(nums) == 6 and len(set(nums)) == 6 and all(1 <= x <= 45 for x in nums)
def count_match(mine, win):
    return len(set(mine) & set(win))
def rank(cnt, bonus_hit):
    if cnt == 6:
        return "1등"
    if cnt == 5:
        return "2등" if bonus_hit else "3등"
    if cnt == 4:
        return "4등"
    if cnt == 3:
        return "5등"
    return "낙첨"
if __name__ == "__main__":
    first = parse(input())
    win, bonus = first[:6], first[6]
    n = int(input())
    hit = miss = bad = 0
    for _ in range(n):
        try:
            mine = parse(input())
            if not is_valid(mine):
                raise ValueError
        except ValueError:
            print("무효")
            bad += 1
            continue
        c = count_match(mine, win)
        r = rank(c, bonus in mine)
        print(f"{c}개 일치 - {r}")
        if r == "낙첨":
            miss += 1
        else:
            hit += 1
    print(f"당첨 {hit}장 / 낙첨 {miss}장 / 무효 {bad}장")
'''), ['3 11 19 25 33 42 7\n5\n3 11 19 25 33 42\n3 11 19 25 33 7\n3 11 19 25 33 40\n1 2 3 4 5 6\n3 11 19 25 25 42', '1 2 3 4 5 6 7\n3\n1 2 3 4 5\n1 2 3 4 5 46\n1 2 3 4 5 x', '10 20 30 40 41 42 43\n4\n10 20 30 1 2 3\n10 20 30 40 2 3\n43 10 20 1 2 3\n0 10 20 30 40 41', '5 6 7 8 9 10 45\n2\n45 5 6 7 8 9\n10 9 8 7 6 5', '1 2 3 4 5 6 7\n3\n8 9 10 11 12 13\n1 2 8 9 10 11\n1 2 3 4 5 6 7'],
  hints=['`is_valid`: `len(nums) == 6 and len(set(nums)) == 6 and all(1 <= x <= 45 for x in nums)`', '보너스: `bonus in mine` 의 결과(True/False)를 rank 에 넘겨요.', '무효 처리: `try:` 안에서 `parse` 뒤 `if not is_valid(mine): raise ValueError` — 두 경우를 한 except 로 모아요.'], ex='2023 8번(비밀번호 생성)과 2024 2학기 4번(로또)은 **만드는 쪽**(`random.sample`)이었어요. 여기서는 **검사하는 쪽**을 만들었어요 — `sample` 이 보장하는 것(개수·범위·중복 없음)이 바로 `is_valid` 의 세 조건이에요.'),
)

# ============================================================ G5
G5 = lesson('5강. 클래스 설계 — 상태를 가진 객체와 두 종류의 변수', 50,
'- `__init__` 에서 만든 `self.속성` 은 **객체마다 따로**\n- `__str__` 은 `print(객체)` 가 부르는 메서드 — print 하지 말고 **문자열을 return**\n- 메서드 정의에 `self` 를 빠뜨리면 **호출하는 줄**에서 TypeError\n- 클래스 변수는 **모든 객체가 공유**. 찾는 순서는 인스턴스 → 클래스\n- `self.count += 1` 은 클래스 변수를 바꾸지 않고 **인스턴스에 새 변수**를 만든다 → `클래스이름.count += 1`\n- 클래스 변수가 리스트면 `append` 는 **모두에게** 보인다',
review('🔁 4강 복습', [T('모듈의 규칙을 확인해요.'), flip(['`import math as m` 뒤 `math.pi`', 'NameError — 별명만 쓸 수 있음'], ['직접 실행한 파일의 `__name__`', '"__main__"'], ['import 된 파일의 `__name__`', '모듈 이름 (파일 이름에서 .py 를 뗀 것)'], ['`random.randint(1, 6)` 의 범위', '1 이상 6 이하 (양 끝 포함)'])]),
outq('복습 — 출력 결과는?', D('''
from math import sqrt as root, floor
import math
vals = [root(x) for x in (2, 9, 20)]
print(floor(vals[0]), vals[1], math.ceil(vals[2]), __name__ == "__main__")
'''), review=True),
explain('클래스 = 자료 + 그 자료를 다루는 함수',
  [T('1학기에는 계좌를 `{"이름": …, "잔액": …}` 딕셔너리와 함수 여러 개로 다뤘어요. 클래스는 그 둘을 **한 덩어리**로 묶어요(2023 4번 BankAccount 11점).'),
   C(D('''
class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance
        self.history = []
    def deposit(self, n):
        self.balance += n
        self.history.append(f"입금 {n}")
    def withdraw(self, n):
        if n > self.balance:
            self.history.append(f"출금 실패 {n}")
            return False
        self.balance -= n
        self.history.append(f"출금 {n}")
        return True
a = Account("민", 1000)
b = Account("솔")
a.deposit(500)
print(a.withdraw(2000), a.withdraw(300))
print(a.balance, b.balance)
print(a.history, b.history)
'''), 'a 와 b 는 서로의 잔액·내역에 영향을 주지 않아요'),
   key('`self` 는 "**이 메서드를 부른 그 객체**"예요. `a.deposit(500)` 은 사실 `Account.deposit(a, 500)` — 그래서 정의에는 `self` 가 있고 호출에는 없어요.')],
  [T('`print(객체)` 를 하면 파이썬은 그 객체의 `__str__` 을 불러 **돌려받은 문자열**을 출력해요.'),
   cmp('__str__ 없음', 'class P:\n    def __init__(self, n):\n        self.n = n\nprint(P("민"))\n# <__main__.P object at 0x7f…>', '__str__ 있음', 'class P:\n    def __init__(self, n):\n        self.n = n\n    def __str__(self):\n        return f"학생 {self.n}"\nprint(P("민"))\n# 학생 민', tones=('', 'good')),
   warn('`__str__` 안에서 `print(…)` 를 하고 return 을 빠뜨리면 None 을 돌려주게 되어 **TypeError** 가 나요. `__str__` 은 반드시 **문자열을 return**.'),
   CX(D('''
class Counter:
    def __init__(self):
        self.value = 0
    def up():                 # self 를 빠뜨림
        self.value += 1
c = Counter()
c.up()    # TypeError: up() takes 0 positional arguments but 1 was given
'''), 'self 를 빠뜨리면 — 오류는 정의한 줄이 아니라 **호출한 줄**에서')],
  [T('좋은 메서드 설계의 기준은 시험의 [조건]에 그대로 나와요.'),
   steps(['상태를 바꾸는 메서드', '`deposit`, `withdraw` — 성공 여부를 **True/False 로 return** 하면 호출한 쪽이 메시지를 정할 수 있어요'], ['조회하는 메서드', '`get_balance`, `__str__` — 상태를 바꾸지 않고 값만 돌려줘요'], ['검사는 메서드 안에서', '잔액 부족·음수 금액 같은 규칙은 **클래스가 스스로** 지켜요. 밖에서 `a.balance -= 5000` 처럼 직접 바꾸지 않아요(7강 캡슐화)'], ['기록', '실패한 시도도 history 에 남기라는 조건이 자주 붙어요'])]),
explain('클래스 변수 vs 인스턴스 변수',
  [T('클래스 **바로 아래**에 만든 변수는 **클래스 변수** — 객체가 몇 개든 **하나뿐**이에요. `__init__` 에서 `self.` 으로 만든 변수는 **인스턴스 변수** — 객체마다 하나씩이에요(2023 7번 학급문고 9점).'),
   C(D('''
class Book:
    count = 0                 # 클래스 변수: 모두가 공유
    def __init__(self, title):
        self.title = title    # 인스턴스 변수: 객체마다
        Book.count += 1
a = Book("수학")
b = Book("과학")
print(Book.count, a.count, b.count)
print(a.title, b.title)
'''), 'a.count 로 읽어도 클래스 변수가 나와요'),
   key('`a.count` 를 **읽을 때**: ① a 자신에게 count 가 있나? ② 없으면 클래스에서 찾는다. 이 순서 때문에 아래 두 함정이 생겨요.')],
  [T('**함정 1.** `self.count += 1` 은 `self.count = self.count + 1` 이에요. 오른쪽은 클래스 변수를 **읽고**, 왼쪽은 **인스턴스에 새 변수**를 만들어요.'),
   C(D('''
class T:
    n = 0
    def hit(self):
        self.n += 1           # 인스턴스에 n 이 새로 생김
x = T()
y = T()
x.hit()
x.hit()
y.hit()
print(x.n, y.n, T.n)
'''), '클래스 변수 T.n 은 끝까지 0'),
   cmp('전체 개수가 안 세짐 ❌', 'def __init__(self):\n    self.count += 1', '클래스 이름으로 ✅', 'def __init__(self):\n    Book.count += 1', lb='객체마다 자기 count 가 1 이 될 뿐', rb='하나뿐인 클래스 변수를 고쳐요', tones=('bad', 'good'))],
  [T('**함정 2.** 클래스 변수가 **리스트·딕셔너리**면, `append` 는 대입이 아니라서 새 변수를 만들지 않아요. 하나뿐인 그 리스트가 바뀌고, **모든 객체에게 보여요**.'),
   C(D('''
class Shelf:
    shared = []               # 클래스 변수 (하나)
    def __init__(self, owner):
        self.owner = owner
        self.mine = []        # 인스턴스 변수 (각자)
    def add(self, title):
        self.shared.append(title)
        self.mine.append(title)
a = Shelf("1반")
b = Shelf("2반")
a.add("수학")
b.add("과학")
print(a.shared, b.shared)
print(a.mine, b.mine)
'''), 'shared 는 두 반이 같이 쓰는 한 권의 장부'),
   key('정리: **모두가 함께 쓰는 값**(전체 개수, 공통 규칙) → 클래스 변수, 고칠 때는 `클래스이름.변수`. **객체마다 다른 값** → `__init__` 에서 `self.변수`. "반마다 따로여야 하는 목록"을 클래스 변수로 두면 섞여요.')]),
outq('[기출유사] 출력 결과는?', D('''
class Dog:
    count = 0
    def __init__(self, name):
        self.name = name
        Dog.count += 1
a = Dog("a")
b = Dog("b")
print(a.count, b.count, Dog.count)
a.count = 10
c = Dog("c")
print(a.count, b.count, Dog.count)
'''), '`a.count = 10` 은 a 에게만 인스턴스 변수를 만들어요. 클래스 변수는 c 가 생기며 3 이 되고, b 는 그것을 읽어요.'),
outq('[기출유사] 출력 결과는?', D('''
class Library:
    total = 0
    books = []
    def __init__(self, room):
        self.room = room
    def donate(self, title):
        self.books.append(title)
        self.total += 1
a = Library("1반")
b = Library("2반")
a.donate("가")
a.donate("나")
b.donate("다")
print(len(a.books), len(b.books), a.total, b.total, Library.total)
'''), '`books` 는 append 라서 모두 공유(3권), `total` 은 `+=` 대입이라 각자 따로(2, 1) — 클래스의 total 은 0 그대로예요. 두 함정이 한 코드에 들어 있어요.'),
spot('[기출유사] 실행했을 때 **예외가 발생하는 줄**(오류 메시지가 가리키는 줄)은?', D('''
class Counter:
    def __init__(self):
        self.value = 0
    def up():
        self.value += 1
c = Counter()
c.up()
print(c.value)
'''), 7, '잘못 쓴 곳은 4번 줄(self 누락)이지만, 정의는 그냥 통과하고 **호출하는 7번 줄**에서 "인자 0개를 받는데 1개가 왔다"는 TypeError 가 나요.'),
fill('[기출유사] `print(Rect(3, 4))` 가 `Rect(3x4, 넓이 12)` 를 출력하게 해요.', D('''
class Rect:
    def __init__(self, w, h):
        self.w = w
        self.h = h
    def area(self):
        return self.w * self.h
    def ___(self):
        ___ f"Rect({self.w}x{self.h}, 넓이 {self.area()})"
print(Rect(3, 4))
'''), ['__str__', 'return'], expect='Rect(3x4, 넓이 12)'),
outq('[기출유사] 출력 결과는?', D('''
class Account:
    def __init__(self, balance):
        self.balance = balance
        self.history = []
    def deposit(self, n):
        self.balance += n
        self.history.append(("입금", n))
    def withdraw(self, n):
        if n > self.balance:
            self.history.append(("실패", n))
            return False
        self.balance -= n
        self.history.append(("출금", n))
        return True
a = Account(1000)
r = [a.withdraw(1500), a.deposit(700), a.withdraw(1500)]
print(r, a.balance, len(a.history), a.history[0][0])
'''), '`deposit` 에는 return 이 없어서 **None** 을 돌려줘요. "모든 메서드가 True/False 를 준다"고 넘겨짚으면 틀려요.'),
ch('[기출유사] `print(s)` 의 출력이 `<__main__.Student object at 0x7f3a…>` 로 나왔어요. 원인은?', ['`__init__` 에서 속성을 만들지 않았다', '`__str__` 메서드를 정의하지 않았다', '`self` 를 빠뜨렸다', '객체를 만들 때 괄호를 빠뜨렸다'], 2, '`__str__` 이 없으면 파이썬이 기본 표현(클래스 이름과 메모리 위치)을 출력해요. 괄호를 빠뜨렸다면 `<class \'__main__.Student\'>` 가 나와요.'),
bucket('[기출유사] 학교 도서 대출 프로그램의 `Student` 클래스예요. 어떤 변수로 두어야 할까요?', ['클래스 변수', '인스턴스 변수'], [['학생 이름', 2], ['한 사람이 빌릴 수 있는 최대 권수(모두 5권)', 1], ['지금 빌린 책 목록', 2], ['전체 학생 수', 1], ['학번', 2], ['학교 이름', 1]], '"빌린 책 목록"을 클래스 변수 리스트로 두면 모든 학생의 대출 목록이 한 리스트에 섞여요.'),
outq('[심화] 출력 결과는?', D('''
class Wallet:
    def __init__(self, money):
        self.money = money
    def give(self, other, n):
        if n > self.money:
            n = self.money
        self.money -= n
        other.money += n
        return n
    def __str__(self):
        return f"[{self.money}]"
a = Wallet(500)
b = Wallet(100)
print(a.give(b, 300), b.give(a, 1000), a, b)
'''), '메서드는 **다른 객체**(other)의 속성도 바꿀 수 있어요. 두 번째 호출에서 b 는 가진 400 만 줘요.'),
essay('[기출유사 · 서술 6점] 클래스 변수와 인스턴스 변수의 **차이**를 서술하고, 학급문고 프로그램에서 "모든 반의 책 수 합계 `total`" 과 "각 반의 책 목록 `books`" 를 각각 어느 변수로 두어야 하는지 이유와 함께 쓰세요.', '클래스 변수는 클래스 안(메서드 밖)에 만들며 그 클래스의 모든 객체가 하나의 값을 공유한다. 인스턴스 변수는 __init__ 에서 self.변수 로 만들며 객체마다 따로 값을 가진다. total 은 모든 반이 함께 세는 하나의 값이므로 클래스 변수로 두고 클래스이름.total 로 수정한다. books 는 반마다 내용이 달라야 하므로 인스턴스 변수(self.books)로 둔다. books 를 클래스 변수로 두면 한 반에서 추가한 책이 모든 반의 목록에 나타난다.', ['클래스 변수는 모든 객체가 공유한다고 썼다', '인스턴스 변수는 객체마다 따로라고 썼다', 'total 은 클래스 변수라고 이유와 함께 썼다', 'books 는 인스턴스 변수라고 이유와 함께 썼다']),
ox('메서드 안에서 `self.count += 1` 을 실행하면 클래스 변수 `count` 가 1 늘어난다.', False, '인스턴스에 `count` 가 새로 만들어질 뿐, 클래스 변수는 그대로예요. `클래스이름.count += 1` 로 써야 해요.'),
prac('[기출유사 · 11점] BankAccount 와 거래 내역', '`BankAccount` 클래스를 완성하세요. 아래쪽 메인 코드는 주어져 있어요.\n\n- `__init__(self, owner, balance)` : 예금주, 잔액, 빈 거래 내역 리스트\n- `deposit(self, n)` : n 이 1 이상이면 입금하고 내역에 `입금 n` 을 추가한 뒤 True, 아니면 False (내역에 남기지 않음)\n- `withdraw(self, n)` : n 이 1 미만이면 `"금액 오류"` 를, 잔액보다 크면 내역에 `출금 실패 n` 을 추가하고 `"잔액 부족"` 을, 성공하면 내역에 `출금 n` 을 추가하고 `"출금 완료"` 를 **return**\n- `show_history(self)` : 내역을 `1. 입금 500` 형식으로 한 줄씩 출력, 없으면 `내역 없음`\n- `__str__(self)` : `예금주: 잔액원`\n\n입력: 첫 줄 `예금주 초기잔액`, 이어서 명령 `입금 n` / `출금 n` / `내역` / `잔액` / `종료`',
D('''
class BankAccount:
    def __init__(self, owner, balance):
        self.owner = owner
        self.balance = balance
        self.history = []
    def deposit(self, n):
        if n < 1:
            return False
        self.balance += n
        self.history.append(f"입금 {n}")
        return True
    def withdraw(self, n):
        if n < 1:
            return "금액 오류"
        if n > self.balance:
            self.history.append(f"출금 실패 {n}")
            return "잔액 부족"
        self.balance -= n
        self.history.append(f"출금 {n}")
        return "출금 완료"
    def show_history(self):
        if not self.history:
            print("내역 없음")
        for i, h in enumerate(self.history, 1):
            print(f"{i}. {h}")
    def __str__(self):
        return f"{self.owner}: {self.balance}원"

owner, money = input().split()
acc = BankAccount(owner, int(money))
while True:
    cmd = input().split()
    if cmd[0] == "종료":
        break
    if cmd[0] == "입금":
        print("입금 완료" if acc.deposit(int(cmd[1])) else "금액 오류")
    elif cmd[0] == "출금":
        print(acc.withdraw(int(cmd[1])))
    elif cmd[0] == "내역":
        acc.show_history()
    elif cmd[0] == "잔액":
        print(acc)
'''), ['민 1000\n내역\n입금 500\n출금 2000\n출금 300\n입금 0\n내역\n잔액\n종료', '솔 0\n출금 1\n출금 0\n잔액\n내역\n종료', '율 500\n출금 500\n잔액\n입금 -3\n출금 -3\n내역\n종료', '하 100\n입금 1\n입금 1\n출금 102\n출금 103\n내역\n잔액\n종료', '준 50\n잔액\n종료'],
  starter=D('''
class BankAccount:
    def __init__(self, owner, balance):
        self.owner = owner
        self.balance = balance
        self.history = []
    # deposit, withdraw, show_history, __str__ 를 작성하세요

owner, money = input().split()
acc = BankAccount(owner, int(money))
while True:
    cmd = input().split()
    if cmd[0] == "종료":
        break
    if cmd[0] == "입금":
        print("입금 완료" if acc.deposit(int(cmd[1])) else "금액 오류")
    elif cmd[0] == "출금":
        print(acc.withdraw(int(cmd[1])))
    elif cmd[0] == "내역":
        acc.show_history()
    elif cmd[0] == "잔액":
        print(acc)
'''), hints=['메인 코드를 먼저 읽으세요. `deposit` 은 True/False 를, `withdraw` 는 **문자열**을 돌려줘야 해요.', '검사 순서: 금액 오류(1 미만) → 잔액 부족. 금액 오류는 내역에 남기지 않아요.', '`__str__` 은 `return f"{self.owner}: {self.balance}원"`'], ex='시험의 [프로그램]도 이렇게 **메인 코드가 주어지고 클래스를 채우는** 형태가 많아요. 메인이 메서드를 **어떻게 부르고 결과를 어떻게 쓰는지**가 곧 메서드의 설계도예요.'),
prac('[기출유사 · 9점] 학급문고 — 두 종류의 변수', '반마다 학급문고가 있고, 학교 전체의 책 수도 함께 관리해요.\n\n`ClassLibrary` 클래스\n- 클래스 변수 `total` : 학교 전체 책 수\n- `__init__(self, room)` : 반 이름, 그 반의 책 목록(빈 리스트)\n- `donate(self, title)` : 책을 추가 (그 반 목록과 전체 수가 함께 늘어요)\n- `lend(self, title)` : 그 반에 책이 있으면 목록에서 빼고 전체 수를 줄인 뒤 True, 없으면 False\n\n입력: 명령이 한 줄씩 주어지고 `종료` 에서 끝나요.\n- `기증 반 책` → 출력 없음 (처음 나온 반은 새로 만들어요)\n- `대출 반 책` → `대출 완료` 또는 `없는 책` (없는 반도 `없는 책`)\n- `현황` → 반마다 `반: N권 (책1, 책2)` 을 **반이 처음 등장한 순서**로(책은 기증 순서, 0권이면 `반: 0권`), 마지막에 `전체: N권`\n\n[조건] ○ 전체 책 수는 **클래스 변수**로만 관리 (따로 세는 전역 변수 금지) ○ 반의 책 목록은 **인스턴스 변수**',
D('''
class ClassLibrary:
    total = 0
    def __init__(self, room):
        self.room = room
        self.books = []
    def donate(self, title):
        self.books.append(title)
        ClassLibrary.total += 1
    def lend(self, title):
        if title in self.books:
            self.books.remove(title)
            ClassLibrary.total -= 1
            return True
        return False
rooms = {}
while True:
    cmd = input().split()
    if cmd[0] == "종료":
        break
    if cmd[0] == "기증":
        if cmd[1] not in rooms:
            rooms[cmd[1]] = ClassLibrary(cmd[1])
        rooms[cmd[1]].donate(cmd[2])
    elif cmd[0] == "대출":
        if cmd[1] in rooms and rooms[cmd[1]].lend(cmd[2]):
            print("대출 완료")
        else:
            print("없는 책")
    elif cmd[0] == "현황":
        for r in rooms.values():
            if r.books:
                print(f"{r.room}: {len(r.books)}권 ({', '.join(r.books)})")
            else:
                print(f"{r.room}: 0권")
        print(f"전체: {ClassLibrary.total}권")
'''), ['기증 1반 수학\n기증 2반 과학\n기증 1반 국어\n현황\n대출 1반 과학\n대출 2반 과학\n현황\n종료', '현황\n대출 3반 책\n종료', '기증 a x\n기증 a x\n대출 a x\n현황\n대출 a x\n대출 a x\n현황\n종료', '기증 가 1\n기증 나 2\n기증 다 3\n대출 나 2\n대출 가 3\n현황\n종료', '기증 z q\n대출 z q\n기증 z w\n기증 y w\n현황\n종료'],
  starter=D('''
class ClassLibrary:
    total = 0
    def __init__(self, room):
        self.room = room
        self.books = []
    def donate(self, title):
        pass
    def lend(self, title):
        pass
rooms = {}   # 반 이름 → ClassLibrary 객체
# 명령 처리
'''), hints=['전체 수는 `ClassLibrary.total += 1` — `self.total += 1` 로 쓰면 반마다 따로 세져요.', '`rooms` 딕셔너리는 넣은 순서를 기억하므로 `for r in rooms.values():` 가 등장 순서예요.', '같은 책이 두 권이면 `remove` 는 앞의 한 권만 지워요.'], ex='`self.total += 1` 로 고쳐서 돌려 보세요. 현황의 `전체` 가 0 으로 나올 거예요. 그 차이를 설명하는 것이 2023 7번(9점)이었어요.'),
prac('[심화 · 14점] 시계 클래스 Time', '24시간제 시각을 다루는 `Time` 클래스를 만들어요.\n\n- `__init__(self, h, m)` : 어떤 정수가 들어와도 **0:00 ~ 23:59 로 정리**해서 저장 (예: `Time(25, 70)` → 02:10, `Time(0, -1)` → 23:59)\n- `add(self, minutes)` : minutes 분 뒤(음수면 앞)의 **새 Time 객체**를 반환. 원래 객체는 바뀌지 않아요.\n- `diff(self, other)` : self 에서 other 까지 **시계가 앞으로 가는** 분 수 (0 ~ 1439)\n- `__str__(self)` : `HH:MM` (두 자리)\n\n입력: 첫 줄 `h m` (기준 시각). 이어서 명령.\n- `더하기 n` → 기준 시각에서 n 분 뒤의 시각을 출력 (기준은 그대로)\n- `이동 n` → 기준 시각을 n 분 뒤로 **바꾸고** 출력\n- `차이 h m` → 기준 시각에서 그 시각까지 `N분 (H시간 M분)`\n- `종료`\n\n[조건] ○ 시와 분을 따로 올림 처리하지 말고, **하루의 몇 번째 분인지(0~1439)로 바꿔 `%` 로 정리**할 것',
D('''
class Time:
    def __init__(self, h, m):
        total = (h * 60 + m) % 1440
        self.h = total // 60
        self.m = total % 60
    def add(self, minutes):
        return Time(self.h, self.m + minutes)
    def diff(self, other):
        return ((other.h * 60 + other.m) - (self.h * 60 + self.m)) % 1440
    def __str__(self):
        return f"{self.h:02d}:{self.m:02d}"
h, m = map(int, input().split())
base = Time(h, m)
while True:
    cmd = input().split()
    if cmd[0] == "종료":
        break
    if cmd[0] == "더하기":
        print(base.add(int(cmd[1])))
    elif cmd[0] == "이동":
        base = base.add(int(cmd[1]))
        print(base)
    elif cmd[0] == "차이":
        d = base.diff(Time(int(cmd[1]), int(cmd[2])))
        print(f"{d}분 ({d // 60}시간 {d % 60}분)")
'''), ['23 50\n더하기 20\n더하기 -60\n이동 15\n차이 0 0\n차이 23 0\n종료', '25 70\n더하기 0\n종료', '0 0\n이동 -1\n이동 1440\n차이 23 59\n더하기 3000\n종료', '12 30\n차이 12 29\n차이 12 31\n이동 -750\n이동 -1\n종료', '9 5\n더하기 55\n더하기 895\n차이 33 5\n종료'],
  hints=['정리: `total = (h * 60 + m) % 1440` → `self.h = total // 60`, `self.m = total % 60`. 파이썬의 `%` 는 음수에도 0~1439 를 줘요.', '`add` 는 `return Time(self.h, self.m + minutes)` — 정리는 `__init__` 이 알아서 해요.', '`diff`: `(other 의 분 - self 의 분) % 1440`'], ex='`__init__` 이 값을 정리해 주므로 다른 메서드는 **넘치는 값을 그대로 넘겨도** 돼요. 규칙을 한곳(생성자)에 모으는 설계예요. 그리고 `add` 가 새 객체를 돌려주는 방식은 8강(연산자 오버로딩)의 `__add__` 와 똑같아요.'),
)

# ============================================================ G6
G6 = lesson('6강. 상속 · 다중상속 · MRO — super() 는 어디로 가는가', 50,
'- 자식의 `__init__` 에서 `super().__init__(…)` 을 **부르지 않으면** 부모가 만드는 속성이 없다 → AttributeError\n- 오버라이딩: 같은 이름의 메서드를 자식이 다시 정의. 부모 것에 덧붙이려면 `super().메서드()`\n- 부모의 메서드가 `self.메서드()` 를 부르면 **실제 객체의 클래스** 것이 실행된다\n- `raise NotImplementedError` — "자식이 반드시 다시 만들어야 하는 메서드"\n- MRO(메서드 탐색 순서): **자신 → 괄호 안 왼쪽부터 → 공통 부모는 맨 뒤에 한 번**\n- `super()` 는 "부모"가 아니라 **MRO 의 다음 클래스**',
review('🔁 5강 복습', [T('두 종류의 변수를 확인해요.'), rev('`self.count += 1` 이 클래스 변수를 바꾸지 못하는 이유는?', '오른쪽은 클래스 변수를 읽지만, 왼쪽 대입이 **인스턴스에 새 변수**를 만들기 때문이에요.'), rev('클래스 변수가 리스트일 때 `self.books.append(x)` 는?', '하나뿐인 리스트가 바뀌어 **모든 객체**에게 보여요.'), rev('`__str__` 이 해야 하는 일은?', 'print 가 아니라 문자열을 **return**')]),
outq('복습 — 출력 결과는?', D('''
class Team:
    members = []
    size = 0
    def __init__(self, name):
        self.name = name
    def join(self, who):
        self.members.append(who)
        Team.size += 1
        self.size += 10
a = Team("A")
b = Team("B")
a.join("민")
b.join("솔")
print(len(b.members), Team.size, a.size, b.size)
'''), review=True),
explain('상속과 super()',
  [T('상속은 부모 클래스의 속성과 메서드를 **물려받아** 필요한 것만 더하거나 바꾸는 거예요(2024 1번 6점, 2023 6번 6점).'),
   C(D('''
class Person:
    def __init__(self, name):
        print("Person 생성")
        self.name = name
    def hello(self):
        return f"안녕, {self.name}"
class Student(Person):
    def __init__(self, name, school):
        print("Student 생성 시작")
        super().__init__(name)
        self.school = school
        print("Student 생성 끝")
s = Student("민", "광곽고")
print(s.hello(), s.school)
'''), 'super().__init__(name) 이 부모의 생성자를 실행해요'),
   warn('자식이 `__init__` 을 **새로 만들면** 부모의 `__init__` 은 자동으로 실행되지 않아요. `super().__init__(…)` 을 빠뜨리면 `self.name` 이 만들어지지 않아 **AttributeError** 가 나요.')],
  [T('**오버라이딩**: 자식이 부모와 같은 이름의 메서드를 다시 만들면 자식 것이 쓰여요. 부모 것을 **버리지 않고 덧붙이려면** `super().메서드()` 를 불러요.'),
   C(D('''
class Animal:
    def __init__(self, name):
        self.name = name
    def speak(self):
        return "..."
    def intro(self):
        return f"{self.name}: {self.speak()}"
class Dog(Animal):
    def speak(self):
        return "멍"
class Puppy(Dog):
    def speak(self):
        return super().speak() * 2 + "!"
for a in [Animal("가"), Dog("나"), Puppy("다")]:
    print(a.intro())
'''), 'intro 는 Animal 에만 있지만, 그 안의 self.speak() 는 실제 객체의 것'),
   key('`intro` 를 부모에서 물려받았어도, 그 안의 `self` 는 **실제 객체**(Dog, Puppy)예요. 그래서 `self.speak()` 는 자식이 오버라이딩한 것을 불러요. 출력 추론 문제의 핵심이에요.')],
  [T('부모가 "**이 메서드는 자식이 꼭 만들어야 한다**"고 표시하는 방법이 `NotImplementedError` 예요.'),
   C(D('''
class Shape:
    def area(self):
        raise NotImplementedError
    def describe(self):
        return f"넓이 {self.area()}"
class Square(Shape):
    def __init__(self, s):
        self.s = s
    def area(self):
        return self.s ** 2
class Line(Shape):
    pass
print(Square(3).describe())
try:
    print(Line().describe())
except NotImplementedError:
    print("Line 은 area 를 만들지 않았어요")
print(isinstance(Square(1), Shape), isinstance(Square(1), Line))
'''), 'isinstance(객체, 클래스) 는 부모 클래스에도 True'),
   tip('`isinstance(x, Shape)` 는 x 가 Shape **이거나 그 자식**이면 True 예요. "학생이면서 사람"처럼 위쪽 클래스 모두에 True.')]),
explain('다중상속과 MRO',
  [T('`class C(A, B):` 처럼 부모를 **둘 이상** 적을 수 있어요. 같은 이름의 메서드가 양쪽에 다 있으면 어느 것이 쓰일까요? 답은 **MRO**(Method Resolution Order, 메서드 탐색 순서)에 있어요(2024 5번 12점, 2025 1번 20점).'),
   C(D('''
class Manager:
    def work(self):
        return "회의"
class Engineer:
    def work(self):
        return "코딩"
    def debug(self):
        return "디버깅"
class CTO(Manager, Engineer):
    pass
c = CTO()
print(c.work(), c.debug())
print([k.__name__ for k in CTO.mro()])
'''), '괄호 안 왼쪽(Manager)이 먼저'),
   key('파이썬은 메서드를 찾을 때 `클래스.mro()` 의 순서대로 뒤져서 **처음 발견한 것**을 써요. `work` 는 Manager 에서, `debug` 는 Manager 에 없으니 다음인 Engineer 에서 찾아요.')],
  [T('부모들이 **같은 조상**을 가지면 다이아몬드 모양이 돼요. 이때의 순서를 구하는 규칙이에요.'),
   steps(['① 자기 자신이 맨 앞', '`D`'], ['② 괄호 안에 적은 순서대로(왼쪽 먼저)', '`D(B, C)` → B 가 C 보다 앞'], ['③ 자식은 항상 부모보다 앞', 'B, C 가 모두 나온 **뒤에야** 공통 부모 A'], ['④ 맨 끝은 object', '모든 클래스의 조상']),
   C(D('''
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
print([k.__name__ for k in D.mro()])
print(D().who())
'''), 'B 에 who 가 없으면 B 의 부모 A 가 아니라, MRO 의 다음인 C 로'),
   warn('"B 에 없으면 B 의 부모인 A 로 올라간다"고 생각하면 **틀려요**. MRO 는 `D → B → C → A` 라서 C 의 `who` 가 먼저 발견돼요.')],
  [T('마지막 퍼즐: `super()` 는 "내 부모"가 아니라 **MRO 에서 내 다음 클래스**를 가리켜요.'),
   C(D('''
class A:
    def __init__(self):
        print("A", end=" ")
class B(A):
    def __init__(self):
        print("B", end=" ")
        super().__init__()
class C(A):
    def __init__(self):
        print("C", end=" ")
        super().__init__()
class D(B, C):
    def __init__(self):
        print("D", end=" ")
        super().__init__()
D()
print()
B()
'''), 'D() 일 때 B 의 super() 는 A 가 아니라 C'),
   key('`D()` 로 만들면 MRO 가 `D B C A` 이므로 B 안의 `super()` 는 **C** 예요. 같은 B 클래스의 같은 코드인데 `B()` 로 만들면 MRO 가 `B A` 라서 **A** 로 가요. super() 의 목적지는 **실제 객체의 MRO** 가 정해요.'),
   exam('출력 추론 순서: ① 객체의 클래스로 MRO 를 한 줄로 적는다 ② super() 를 만날 때마다 **그 줄에서 오른쪽으로 한 칸**.')]),
outq('[기출유사] 출력 결과는?', D('''
class A:
    def __init__(self):
        print("A", end=" ")
class B(A):
    def __init__(self):
        super().__init__()
        print("B", end=" ")
class C(B):
    def __init__(self):
        print("C1", end=" ")
        super().__init__()
        print("C2", end=" ")
C()
'''), 'B 는 super 를 **먼저** 부르고 자기 것을 출력해요. 호출과 출력의 순서를 줄마다 따라가세요.'),
outq('[기출유사] 출력 결과는?', D('''
class Base:
    def __init__(self, x):
        self.x = x
    def value(self):
        return self.x
    def show(self):
        return self.value() * 2
class Plus(Base):
    def value(self):
        return super().value() + 1
class Twice(Plus):
    def show(self):
        return super().show() + self.value()
print(Base(5).show(), Plus(5).show(), Twice(5).show())
'''), '`Twice(5).show()` = `Base.show`(= 실제 객체의 value 6 × 2 = 12) + 6 = 18.'),
outq('[기출유사] 출력 결과는?', D('''
class A:
    def go(self):
        return ["A"]
class B(A):
    def go(self):
        return ["B"] + super().go()
class C(A):
    def go(self):
        return ["C"] + super().go()
class D(B, C):
    def go(self):
        return ["D"] + super().go()
print(D().go(), B().go(), C().go())
'''), 'D 객체일 때 B 의 super 는 C, B 객체일 때 B 의 super 는 A.'),
outq('[기출유사] 출력 결과는?', D('''
class Manager:
    def __init__(self):
        self.role = "관리"
    def work(self):
        return "회의"
class Engineer:
    def __init__(self):
        self.role = "개발"
        self.lang = "Python"
    def work(self):
        return "코딩"
class CTO(Manager, Engineer):
    def work(self):
        return Engineer.work(self) + "+" + super().work()
c = CTO()
print(c.role, c.work(), hasattr(c, "lang"), [k.__name__ for k in CTO.mro()][1:3])
'''), 'CTO 에 `__init__` 이 없어 MRO 의 첫 번째인 Manager 의 것만 실행돼요. Manager 가 super().__init__() 을 부르지 않으므로 Engineer 의 생성자는 **실행되지 않고**, `lang` 속성은 없어요.'),
ch('[기출유사] 출력 결과는?\n\n```\nclass P:\n    def __init__(self, name):\n        self.name = name\nclass S(P):\n    def __init__(self, name, grade):\n        self.grade = grade\ns = S("민", 1)\nprint(s.grade, s.name)\n```', ['1 민', 'AttributeError', 'TypeError', '1 None'], 2, '자식이 `__init__` 을 새로 만들고 `super().__init__(name)` 을 부르지 않아 `self.name` 이 만들어지지 않았어요. `s.grade` 까지는 계산되지만 `s.name` 에서 AttributeError.'),
spot('[기출유사] `NotImplementedError` 가 **발생(raise)하는 줄**은?', D('''
class Shape:
    def area(self):
        raise NotImplementedError
class Sq(Shape):
    def __init__(self, s):
        self.s = s
    def area(self):
        return self.s ** 2
class Tri(Shape):
    def __init__(self, b, h):
        self.b, self.h = b, h
shapes = [Sq(2), Tri(3, 4)]
print(sum(x.area() for x in shapes))
'''), 3, 'Tri 가 `area` 를 오버라이딩하지 않아서 부모 Shape 의 `area`(3번 줄)가 실행돼요. 고칠 곳은 Tri 클래스(메서드 추가)예요.'),
fill('[기출유사] 부모의 생성자를 불러 `name` 을 만들고, 부모의 `info` 에 학년을 덧붙여요.', D('''
class Person:
    def __init__(self, name):
        self.name = name
    def info(self):
        return self.name
class Student(Person):
    def __init__(self, name, grade):
        ___.__init__(name)
        self.grade = grade
    def info(self):
        return super().___() + f" {self.grade}학년"
print(Student("민", 2).info())
'''), ['super()', 'info'], expect='민 2학년'),
order('[기출유사] `class D(B, C)`, `class B(A)`, `class C(A)` 일 때 `D.mro()` 의 순서대로 놓으세요.', ['D', 'B', 'C', 'A', 'object'], '자신 → 왼쪽 부모 → 오른쪽 부모 → 공통 조상 → object', code=False, mono=True),
sh('[심화] `class X(Y, Z)`, `class Y(W)`, `class Z(W)`, `class W` 일 때 `len(X.mro())` 의 값은?', 5, 'X, Y, Z, W, object — 공통 부모 W 는 **한 번만** 들어가고, object 도 세요.'),
ox('`super()` 는 항상 `class` 문의 괄호 안에 적힌 첫 번째 부모 클래스를 가리킨다.', False, '`super()` 는 **실제 객체의 MRO 에서 현재 클래스의 다음**을 가리켜요. `D(B, C)` 의 객체에서 B 안의 super() 는 B 의 부모 A 가 아니라 C 예요.'),
essay('[기출유사 · 서술 6점] `class CTO(Manager, Engineer): pass` 에서 두 부모 모두 `work()` 를 가지고 있어요. `CTO().work()` 를 호출하면 **어느 클래스의 메서드가 실행되는지**, 그 이유를 **MRO** 라는 말을 써서 서술하세요. 또 Engineer 의 것이 실행되게 하려면 어떻게 고치면 되는지 쓰세요.', 'Manager 의 work() 가 실행된다. 파이썬은 메서드를 MRO(메서드 탐색 순서)에 따라 찾는데, CTO 의 MRO 는 CTO → Manager → Engineer → object 로, 클래스 정의의 괄호 안에 왼쪽에 적은 부모가 먼저 오기 때문이다. CTO 자신에게 work 가 없으므로 그다음인 Manager 에서 처음 발견된 work 가 실행된다. Engineer 의 것이 실행되게 하려면 class CTO(Engineer, Manager) 로 부모의 순서를 바꾸면 된다.', ['Manager 의 work 가 실행된다고 썼다', 'MRO 가 CTO → Manager → Engineer 순이라고 썼다', '괄호 안 왼쪽 부모가 먼저 탐색된다는 이유를 썼다', '부모 순서를 바꾸거나(또는 CTO 에서 Engineer.work 를 직접 호출해) 고친다고 썼다']),
prac('[기출유사 · 10점] 도형과 NotImplementedError', '부모 클래스 `Shape` 와 자식 도형들을 만들어요.\n\n- `Shape` : `__init__(self, name)`, `area(self)` 는 **NotImplementedError 를 raise**, `describe(self)` 는 `이름 넓이: X.XX` 문자열을 return (넓이는 `self.area()` 로)\n- `Rect(w, h)` 이름 `사각형`, `Circle(r)` 이름 `원` (원주율 3.14), `Triangle(b, h)` 이름 `삼각형`\n- `Line(l)` 이름 `선` — `area` 를 **만들지 않아요**\n\n입력: 첫 줄 `n`, 이어서 n 줄에 `사각형 w h` / `원 r` / `삼각형 b h` / `선 l` (값은 정수)\n\n출력: 도형마다 `describe()` 의 결과. 넓이를 구할 수 없는 도형은 `이름: 넓이를 구할 수 없음`. 마지막 줄에 `총 넓이: X.XX` (구할 수 있는 것만 합산)\n\n[조건] ○ 자식의 `__init__` 에서 `super().__init__(이름)` 을 호출할 것 ○ `describe` 는 Shape 에만 만들 것 ○ 넓이를 구할 수 없는 경우는 **NotImplementedError 를 잡아** 처리 (isinstance 나 이름 비교 금지)',
D('''
class Shape:
    def __init__(self, name):
        self.name = name
    def area(self):
        raise NotImplementedError
    def describe(self):
        return f"{self.name} 넓이: {self.area():.2f}"
class Rect(Shape):
    def __init__(self, w, h):
        super().__init__("사각형")
        self.w, self.h = w, h
    def area(self):
        return self.w * self.h
class Circle(Shape):
    def __init__(self, r):
        super().__init__("원")
        self.r = r
    def area(self):
        return 3.14 * self.r * self.r
class Triangle(Shape):
    def __init__(self, b, h):
        super().__init__("삼각형")
        self.b, self.h = b, h
    def area(self):
        return self.b * self.h / 2
class Line(Shape):
    def __init__(self, l):
        super().__init__("선")
        self.l = l
make = {"사각형": Rect, "원": Circle, "삼각형": Triangle, "선": Line}
n = int(input())
total = 0
for _ in range(n):
    p = input().split()
    s = make[p[0]](*map(int, p[1:]))
    try:
        print(s.describe())
        total += s.area()
    except NotImplementedError:
        print(f"{s.name}: 넓이를 구할 수 없음")
print(f"총 넓이: {total:.2f}")
'''), ['4\n사각형 3 4\n원 2\n선 10\n삼각형 3 5', '1\n선 5', '2\n원 1\n원 10', '3\n삼각형 1 1\n사각형 1 1\n삼각형 7 3', '5\n선 1\n사각형 10 10\n선 2\n원 3\n삼각형 4 4'],
  starter=D('''
class Shape:
    def __init__(self, name):
        self.name = name
    def area(self):
        raise NotImplementedError
    def describe(self):
        return f"{self.name} 넓이: {self.area():.2f}"
class Rect(Shape):
    def __init__(self, w, h):
        super().__init__("사각형")
        self.w, self.h = w, h
    def area(self):
        return self.w * self.h
# Circle, Triangle, Line 과 메인 코드를 작성하세요
'''), hints=['`Line` 은 `__init__` 만 만들고 `area` 는 만들지 않아요. 그러면 부모의 `area` 가 실행되어 예외가 나요.', '`try: print(s.describe())` / `except NotImplementedError:`', '이름 → 클래스 딕셔너리 `{"사각형": Rect, …}` 를 쓰면 `make[p[0]](*map(int, p[1:]))` 로 한 줄에 만들 수 있어요(if-elif 로 해도 돼요).'], ex='`describe` 는 Shape 에 **한 번만** 썼는데 도형마다 다른 넓이가 나와요. 부모의 메서드 안에서 `self.area()` 가 **실제 객체의 area** 를 부르기 때문이에요.'),
prac('[기출유사 · 12점] CTO — 다중상속과 협력하는 super()', '회사 직원 클래스를 만들어요. 모든 `work` 메서드는 **자기 일 + `super().work()`** 를 돌려줘요.\n\n- `Employee` : `__init__(self, name)`, `work(self)` → `["출근"]`\n- `Manager(Employee)` : `work` → `["회의"] + super().work()`\n- `Engineer(Employee)` : `work` → `["코딩"] + super().work()`\n- `CTO(Manager, Engineer)` : `work` → `["전략"] + super().work()`\n- `Intern(Engineer)` : `work` 를 만들지 않아요\n\n입력: 첫 줄 `n`, 이어서 n 줄에 `직책 이름` (직책은 `직원` `관리자` `개발자` `CTO` `인턴`)\n\n출력: 사람마다 두 줄\n- `이름: 일1 일2 …`\n- `MRO: 클래스1 > 클래스2 > …` (object 는 빼고, 클래스 이름은 영어 그대로)\n\n[조건] ○ `work` 안에서 부모 클래스 이름을 직접 쓰지 말고 **super() 만** 사용 ○ MRO 는 `type(객체).mro()` 로 구할 것',
D('''
class Employee:
    def __init__(self, name):
        self.name = name
    def work(self):
        return ["출근"]
class Manager(Employee):
    def work(self):
        return ["회의"] + super().work()
class Engineer(Employee):
    def work(self):
        return ["코딩"] + super().work()
class CTO(Manager, Engineer):
    def work(self):
        return ["전략"] + super().work()
class Intern(Engineer):
    pass
kinds = {"직원": Employee, "관리자": Manager, "개발자": Engineer, "CTO": CTO, "인턴": Intern}
n = int(input())
for _ in range(n):
    job, name = input().split()
    p = kinds[job](name)
    print(f"{p.name}: {' '.join(p.work())}")
    names = [k.__name__ for k in type(p).mro()][:-1]
    print("MRO: " + " > ".join(names))
'''), ['2\nCTO 민\n관리자 솔', '1\n직원 율', '3\n인턴 하\n개발자 준\nCTO 온', '2\n인턴 a\n인턴 b', '4\n관리자 k\nCTO m\n직원 n\n개발자 p'],
  starter=D('''
class Employee:
    def __init__(self, name):
        self.name = name
    def work(self):
        return ["출근"]
class Manager(Employee):
    def work(self):
        return ["회의"] + super().work()
# Engineer, CTO, Intern 과 메인 코드를 작성하세요
'''), hints=['CTO 의 결과는 `전략 회의 코딩 출근` 이에요. Manager 의 `super().work()` 가 Employee 가 아니라 **Engineer** 로 가기 때문이에요.', '`[k.__name__ for k in type(p).mro()][:-1]` — 마지막 object 를 슬라이싱으로 빼요.', '`" > ".join(names)`'], ex='관리자 솔의 결과는 `회의 출근`, CTO 민의 결과는 `전략 회의 코딩 출근`. **같은 Manager.work 코드**가 객체에 따라 다른 곳으로 이어져요. 이것이 "super() 는 MRO 의 다음"이라는 말의 뜻이에요.'),
prac('[심화 · 16점] Person · Student · HighSchoolStudent', '3단 상속 구조를 만들어요.\n\n- `Person(name, age)` : `__str__` → `이름(나이)`\n- `Student(Person)` : `school` 추가. `__str__` → `이름(나이) - 학교`\n- `HighSchoolStudent(Student)` : `grade` 추가. `__str__` → `이름(나이) - 학교 N학년`\n\n자식의 `__str__` 은 **부모의 `__str__` 결과에 덧붙이는** 방식으로 만들어요.\n\n입력: 첫 줄 `n`, 이어서 n 줄. `P 이름 나이` / `S 이름 나이 학교` / `H 이름 나이 학교 학년`\n\n출력\n1. 입력 순서대로 각 객체를 print\n2. `Person a명 / Student b명 / HighSchoolStudent c명` — **isinstance** 로 세요 (고등학생은 Student 이기도, Person 이기도 해요)\n3. Student(자식 포함) 중 나이가 가장 많은 사람의 이름 (같으면 먼저 입력된 사람). 없으면 `학생 없음`\n4. 고등학생의 학년별 인원을 학년 오름차순으로 `N학년 k명` 한 줄씩. 고등학생이 없으면 출력하지 않아요.\n\n[조건] ○ 모든 자식의 `__init__` 은 `super().__init__` 을, `__str__` 은 `super().__str__()` 을 사용할 것',
D('''
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    def __str__(self):
        return f"{self.name}({self.age})"
class Student(Person):
    def __init__(self, name, age, school):
        super().__init__(name, age)
        self.school = school
    def __str__(self):
        return super().__str__() + f" - {self.school}"
class HighSchoolStudent(Student):
    def __init__(self, name, age, school, grade):
        super().__init__(name, age, school)
        self.grade = grade
    def __str__(self):
        return super().__str__() + f" {self.grade}학년"
n = int(input())
people = []
for _ in range(n):
    p = input().split()
    if p[0] == "P":
        people.append(Person(p[1], int(p[2])))
    elif p[0] == "S":
        people.append(Student(p[1], int(p[2]), p[3]))
    else:
        people.append(HighSchoolStudent(p[1], int(p[2]), p[3], int(p[4])))
for x in people:
    print(x)
a = sum(isinstance(x, Person) for x in people)
b = sum(isinstance(x, Student) for x in people)
c = sum(isinstance(x, HighSchoolStudent) for x in people)
print(f"Person {a}명 / Student {b}명 / HighSchoolStudent {c}명")
students = [x for x in people if isinstance(x, Student)]
if students:
    oldest = students[0]
    for s in students:
        if s.age > oldest.age:
            oldest = s
    print(oldest.name)
else:
    print("학생 없음")
grades = {}
for x in people:
    if isinstance(x, HighSchoolStudent):
        grades[x.grade] = grades.get(x.grade, 0) + 1
for g in sorted(grades):
    print(f"{g}학년 {grades[g]}명")
'''), ['4\nP 김선생 40\nS 민 13 광곽중\nH 솔 17 광곽고 2\nH 율 16 광곽고 1', '1\nP 홍 30', '3\nH a 17 x고 3\nH b 17 x고 3\nS c 17 y중', '2\nS k 12 초등\nS m 14 중등', '5\nH q 18 z고 3\nP w 50\nH e 16 z고 1\nH r 17 z고 2\nH t 16 z고 1'],
  hints=['`HighSchoolStudent.__init__` 은 `super().__init__(name, age, school)` — 한 단계 위(Student)만 부르면 Student 가 다시 Person 을 불러요.', '`sum(isinstance(x, Student) for x in people)` — True 는 1 로 더해져요.', '가장 나이 많은 사람: `>` 로만 갱신해야 같을 때 먼저 입력된 사람이 남아요.'], ex='`print(솔)` 한 번에 `__str__` 이 **세 번** 이어져요: HighSchoolStudent → Student → Person. 각 클래스는 **자기가 추가한 부분만** 책임져요. 2025 1번(20점)이 이 구조에 is/== 를 더한 문제였어요 — 다음 강에서 이어져요.'),
)

# ============================================================ G7
G7 = lesson('7강. 캡슐화 · is 와 == — 서술형이 묻는 "왜"', 45,
'- `self.__x` 는 클래스 **밖에서** `obj.__x` 로 읽을 수 없다 → **AttributeError**\n- 실제로는 `_클래스이름__x` 라는 이름으로 저장된다 (name mangling)\n- 밖에서 `obj.__x = 값` 을 **대입**하면 오류 없이 **엉뚱한 새 속성**이 생긴다 — 진짜 값은 그대로\n- getter 로 읽고, setter 에서 **검증**한 뒤 바꾼다\n- `==` 는 **값**이 같은가, `is` 는 **같은 객체**인가(`id` 가 같은가)\n- `__eq__` 가 없는 클래스의 `==` 는 `is` 처럼 동작한다',
review('🔁 6강 복습', [T('MRO 를 확인해요.'), flip(['`class D(B, C)`, B 와 C 의 부모가 A 일 때 MRO', 'D → B → C → A → object'], ['`super()` 가 가리키는 것', '실제 객체의 MRO 에서 현재 클래스의 다음'], ['자식 `__init__` 에서 `super().__init__()` 을 빠뜨리면', '부모가 만드는 속성이 없어 AttributeError'], ['`raise NotImplementedError` 의 의미', '자식이 반드시 오버라이딩해야 하는 메서드'])]),
outq('복습 — 출력 결과는?', D('''
class A:
    def f(self):
        return "A"
class B(A):
    def f(self):
        return "B" + super().f()
class C(A):
    def f(self):
        return "C" + super().f()
class D(C, B):
    pass
print(D().f(), [k.__name__ for k in D.mro()][1])
'''), review=True),
explain('캡슐화 — 밑줄 두 개의 의미',
  [T('5강에서 "잔액은 메서드로만 바꾸자"고 했어요. 하지만 `acc.balance = 999999` 를 막을 방법이 없었죠. 속성 이름 앞에 **밑줄 두 개**를 붙이면 클래스 밖에서 그 이름으로 접근할 수 없어요(2024 3번 14점, 2025 2번 18점).'),
   C(D('''
class Gpay:
    def __init__(self, owner, balance):
        self.owner = owner
        self.__balance = balance
    def get_balance(self):
        return self.__balance
g = Gpay("민", 5000)
print(g.owner)
print(g.get_balance())
try:
    print(g.__balance)
except AttributeError as e:
    print("AttributeError:", e)
'''), '클래스 안(메서드)에서는 self.__balance 로 자유롭게 써요'),
   key('오류 메시지는 "**그런 속성이 없다**"예요. 접근이 "금지"된 게 아니라, 밖에서는 그 이름을 **찾을 수 없는** 거예요. 이유는 다음 장에.')],
  [T('파이썬은 클래스 안에서 `__balance` 를 만나면 이름을 **`_Gpay__balance`** 로 바꿔서 저장해요(name mangling). 그래서 밖에서 `g.__balance` 를 찾으면 그런 이름이 없어요.'),
   C(D('''
class Gpay:
    def __init__(self, balance):
        self.__balance = balance
    def get_balance(self):
        return self.__balance
g = Gpay(5000)
print(list(vars(g)))
g.__balance = 0
print(list(vars(g)))
print(g.get_balance())
'''), '밖에서 대입하면? 오류 없이 "다른" 속성이 하나 더 생겨요'),
   warn('**읽기**(`print(g.__balance)`)는 AttributeError, **쓰기**(`g.__balance = 0`)는 오류 없이 **새 속성 `__balance`** 가 생겨요. 진짜 잔액 `_Gpay__balance` 는 그대로 5000. "해킹했는데 잔액이 안 바뀌는 이유"를 묻는 문제의 답이에요.')],
  [T('숨긴 속성은 **메서드를 통해서만** 읽고 바꿔요. 바꾸는 메서드(setter)에 **검증**을 넣으면 잘못된 값이 들어올 길이 없어져요.'),
   C(D('''
class Timer:
    def __init__(self):
        self.__total = 0
    def get_total(self):               # getter
        return self.__total
    def add(self, minutes):            # setter 역할
        if minutes <= 0:
            return False
        self.__total += minutes
        return True
t = Timer()
print(t.add(50), t.add(-30), t.get_total())
'''), '음수 시간은 들어올 수 없어요'),
   steps(['왜 숨기나', '밖에서 마음대로 바꿔 **잘못된 상태**(음수 잔액 등)가 되는 것을 막으려고'], ['어떻게 읽나', 'getter 메서드 (`get_balance`)'], ['어떻게 바꾸나', '검증이 들어 있는 메서드 (`charge`, `pay`, `set_…`)'], ['밑줄 한 개 `_x`', '"건드리지 말자"는 **약속**일 뿐, 이름은 바뀌지 않아요']),
   exam('서술 틀: "`__total` 은 **private 속성**이라 클래스 외부에서 그 이름으로 접근할 수 없어(이름이 `_Timer__total` 로 바뀌어 저장됨) **AttributeError** 가 발생한다. **getter 메서드**를 만들어 `t.get_total()` 로 읽어야 한다."')]),
explain('is 와 == — 같은 "값"과 같은 "객체"',
  [T('`==` 는 **내용**이 같은지, `is` 는 **메모리의 같은 객체**인지를 물어요. `a is b` 는 `id(a) == id(b)` 와 같아요(2025 1번 20점).'),
   C(D('''
a = [1, 2]
b = [1, 2]
c = a
print(a == b, a is b)
print(a == c, a is c)
c.append(3)
print(a, b)
print(id(a) == id(c), id(a) == id(b))
'''), 'c = a 는 복사가 아니라 같은 리스트에 이름을 하나 더 붙인 것'),
   key('쌍둥이는 `==` 이지만 `is` 가 아니에요. `c = a` 는 한 사람의 **별명**이라 `is` 예요. 별명으로 바꾸면 본인이 바뀌어요.')],
  [T('내가 만든 클래스의 객체는 어떨까요? **`__eq__` 를 만들지 않으면** 파이썬은 `==` 를 `is` 와 똑같이 처리해요.'),
   C(D('''
class P:
    def __init__(self, name):
        self.name = name
class Q:
    def __init__(self, name):
        self.name = name
    def __eq__(self, other):
        return self.name == other.name
p1, p2 = P("민"), P("민")
q1, q2 = Q("민"), Q("민")
print(p1 == p2, p1 is p2)
print(q1 == q2, q1 is q2)
'''), '__eq__ 가 "같다"의 기준을 정해요'),
   warn('속성이 전부 같아도 `P("민") == P("민")` 은 **False** 예요. 파이썬은 내 클래스의 "같음"이 무엇인지 모르기 때문이에요.')],
  [T('마지막으로, 언제 무엇을 쓰는지 정리해요.'),
   tabs(['값 비교는 ==', '숫자·문자열·리스트의 내용을 비교할 때는 항상 `==`', 'if name == "민":\nif scores == [90, 80]:'], ['None 은 is', '`None` 은 하나뿐이라 `is None` / `is not None` 으로 써요', 'if result is None:'], ['같은 객체인지 확인할 때 is', '"한쪽을 바꾸면 다른 쪽도 바뀌는가"를 물을 때', 'b = a\nprint(b is a)   # True\nb = a[:]\nprint(b is a)   # False']),
   tip('숫자나 문자열에 `is` 를 쓰면 파이썬이 내부적으로 같은 객체를 재사용하는 경우가 있어 결과가 들쭉날쭉해요. 시험 답안에서는 **값 비교에 is 를 쓰지 않는다**만 기억하면 돼요.')]),
outq('[기출유사] 출력 결과는?', D('''
a = [1, 2]
b = [1, 2]
c = a
c.append(3)
d = a[:]
print(a == b, a is b, a is c, a == c, d == a, d is a, len(a))
'''), '`c` 는 a 의 별명이라 append 가 a 에도 보여요. `a[:]` 는 내용이 같은 **새** 리스트예요.'),
outq('[기출유사] 출력 결과는?', D('''
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
class Student(Person):
    def __eq__(self, other):
        return self.name == other.name and self.age == other.age
p1 = Person("민", 16)
p2 = Person("민", 16)
p3 = p1
s1 = Student("민", 16)
s2 = Student("민", 16)
print(p1 == p2, p1 is p3, p1 == p3, s1 == s2, s1 is s2, id(s1) == id(s2))
'''), 'Person 에는 `__eq__` 가 없어 `p1 == p2` 는 False. Student 는 `__eq__` 를 정의해 값으로 비교해요.'),
outq('[기출유사] 출력 결과는?', D('''
class Safe:
    def __init__(self):
        self.__code = 1234
        self.hint = "숫자"
    def check(self, c):
        return c == self.__code
s = Safe()
s.__code = 0
print(s.check(0), s.check(1234), sorted(vars(s)))
'''), '밖에서 한 `s.__code = 0` 은 새 속성 `__code` 를 만들 뿐이에요. 진짜 비밀번호는 `_Safe__code` 에 그대로 1234.'),
spot('[기출유사] **예외가 발생하는 줄**은?', D('''
class Timer:
    def __init__(self):
        self.__total = 0
    def add(self, m):
        self.__total += m
t = Timer()
t.add(30)
t.add(20)
print(t.__total)
'''), 9, '클래스 **안**(5번 줄)에서는 `self.__total` 을 쓸 수 있어요. 클래스 **밖**(9번 줄)에서 읽으려 하면 AttributeError.'),
ch('[심화] 출력 결과는?\n\n```\nclass A:\n    def __init__(self):\n        self.__v = 1\nclass B(A):\n    def show(self):\n        return self.__v\nprint(B().show())\n```', ['1', 'AttributeError', 'None', 'NameError'], 2, 'A 안의 `__v` 는 `_A__v` 로, B 안의 `self.__v` 는 `_B__v` 로 바뀌어요. 이름이 달라서 **자식 클래스에서도** 부모의 private 속성을 직접 쓸 수 없어요. 부모의 getter 를 불러야 해요.'),
fill('[기출유사] 잔액을 읽는 getter 와, 검증하는 충전 메서드를 완성해요.', D('''
class Gpay:
    def __init__(self):
        self.___ = 0
    def get_balance(self):
        ___ self.__balance
    def charge(self, n):
        if n > 0:
            self.__balance += n
g = Gpay()
g.charge(3000)
g.charge(-500)
print(g.get_balance())
'''), ['__balance', 'return'], expect='3000'),
outq('[기출유사] 출력 결과는?', D('''
def add_item(box, x):
    box.append(x)
    return box
a = [1]
b = add_item(a, 2)
c = add_item(a[:], 3)
print(b is a, c is a, a, c, a == b)
'''), '함수에 리스트를 넘기면 **같은 객체**가 전달돼요. `a[:]` 를 넘기면 복사본이 바뀔 뿐이에요.'),
bucket('결과가 True 인 것과 False 인 것을 나눠 보세요. (`x = [0]`, `y = x`, `z = [0]`)', ['True', 'False'], [['x == z', 1], ['x is z', 2], ['x is y', 1], ['[] == []', 1], ['[] is []', 2], ['None is None', 1], ['y is not z', 1], ['x[:] is x', 2]]),
outq('[심화] 출력 결과는?', D('''
class S:
    def __init__(self, sid, name):
        self.sid = sid
        self.name = name
    def __eq__(self, other):
        return self.sid == other.sid
roster = [S(1, "민"), S(2, "솔")]
x = S(2, "솔이")
print(x in roster, roster.index(x), roster.count(S(3, "민")), x is roster[1])
'''), '`in`, `index`, `count` 는 모두 **`==`**(즉 `__eq__`)로 비교해요. 학번만 같으면 같은 학생으로 봐요.'),
essay('[기출유사 · 서술 7점] 아래 코드의 마지막 줄에서 오류가 발생해요. **오류의 이름과 이유**를 쓰고, 클래스의 설계 의도(캡슐화)를 지키면서 총 공부 시간을 출력하도록 **고치는 방법**을 서술하세요.\n\n```\nclass Study:\n    def __init__(self):\n        self.__total_time = 0\n    def add(self, m):\n        self.__total_time += m\ns = Study()\ns.add(40)\nprint(s.__total_time)\n```', 'AttributeError 가 발생한다. __total_time 은 이름 앞에 밑줄 두 개가 붙은 private 속성이어서 클래스 외부에서는 그 이름으로 접근할 수 없기 때문이다(내부적으로 _Study__total_time 이라는 이름으로 바뀌어 저장된다). 클래스 안에 def get_total_time(self): return self.__total_time 과 같은 getter 메서드를 만들고, 밖에서는 print(s.get_total_time()) 으로 값을 읽어야 한다.', ['AttributeError 라고 썼다', 'private 속성(밑줄 두 개)이라 클래스 외부에서 접근할 수 없다고 이유를 썼다', 'getter 메서드를 클래스 안에 만든다고 썼다', '밖에서 getter 를 호출해 출력한다고 썼다'], '`print(s._Study__total_time)` 으로도 값은 나오지만, "캡슐화를 지키면서"라는 조건에 어긋나요. 답안은 getter 로 쓰세요.'),
ox('`__eq__` 를 정의하지 않은 클래스의 두 객체는 모든 속성의 값이 같아도 `==` 의 결과가 False 이다.', True, '`__eq__` 가 없으면 `==` 는 `is` 처럼 "같은 객체인가"를 봐요.'),
prac('[기출유사 · 18점] Gpay — private 잔액', '간편 결제 클래스 `Gpay` 를 만들어요.\n\n- `__init__(self, owner, balance)` : 예금주(공개), 잔액(**private**), 결제 횟수(**private**, 0)\n- `get_balance(self)` , `get_count(self)` : getter\n- `charge(self, n)` : n 이 1 이상 100000 이하이면 충전하고 True, 아니면 False\n- `pay(self, n)` : n 이 1 미만이면 `"금액 오류"`, 잔액보다 크면 `"잔액 부족"`, 아니면 결제하고 결제 횟수를 1 늘린 뒤 `"결제 완료"` 를 return\n- `__str__(self)` : `예금주님의 잔액: N원 (결제 K회)`\n\n입력: 첫 줄 `예금주 초기잔액`, 이어서 명령.\n- `충전 n` → `충전 완료` / `충전 실패`\n- `결제 n` → pay 의 반환값\n- `조회` → print(객체)\n- `해킹 n` → 메인 코드에서 `g.__balance = n` 을 실행한 뒤 `해킹 시도 → 실제 잔액 N원` 을 출력 (N 은 getter 로 읽은 값)\n- `종료`\n\n[조건] ○ 잔액과 결제 횟수는 이름 앞에 밑줄 두 개 ○ 메인 코드에서 잔액을 읽을 때는 getter 만 사용',
D('''
class Gpay:
    def __init__(self, owner, balance):
        self.owner = owner
        self.__balance = balance
        self.__count = 0
    def get_balance(self):
        return self.__balance
    def get_count(self):
        return self.__count
    def charge(self, n):
        if 1 <= n <= 100000:
            self.__balance += n
            return True
        return False
    def pay(self, n):
        if n < 1:
            return "금액 오류"
        if n > self.__balance:
            return "잔액 부족"
        self.__balance -= n
        self.__count += 1
        return "결제 완료"
    def __str__(self):
        return f"{self.owner}님의 잔액: {self.__balance}원 (결제 {self.__count}회)"
owner, money = input().split()
g = Gpay(owner, int(money))
while True:
    cmd = input().split()
    if cmd[0] == "종료":
        break
    if cmd[0] == "충전":
        print("충전 완료" if g.charge(int(cmd[1])) else "충전 실패")
    elif cmd[0] == "결제":
        print(g.pay(int(cmd[1])))
    elif cmd[0] == "조회":
        print(g)
    elif cmd[0] == "해킹":
        g.__balance = int(cmd[1])
        print(f"해킹 시도 → 실제 잔액 {g.get_balance()}원")
'''), ['민 5000\n결제 3000\n결제 3000\n충전 100001\n충전 100000\n해킹 9999999\n조회\n종료', '솔 0\n결제 0\n결제 1\n충전 0\n조회\n종료', '율 100\n해킹 0\n결제 100\n결제 1\n조회\n해킹 500\n결제 1\n종료', '하 10\n충전 1\n충전 1\n결제 12\n결제 13\n조회\n종료', '준 777\n조회\n종료'],
  starter=D('''
class Gpay:
    def __init__(self, owner, balance):
        self.owner = owner
        self.__balance = balance
        self.__count = 0
    # getter 2개, charge, pay, __str__ 를 작성하세요

owner, money = input().split()
g = Gpay(owner, int(money))
while True:
    cmd = input().split()
    if cmd[0] == "종료":
        break
    if cmd[0] == "충전":
        print("충전 완료" if g.charge(int(cmd[1])) else "충전 실패")
    elif cmd[0] == "결제":
        print(g.pay(int(cmd[1])))
    elif cmd[0] == "조회":
        print(g)
    elif cmd[0] == "해킹":
        g.__balance = int(cmd[1])
        print(f"해킹 시도 → 실제 잔액 {g.get_balance()}원")
'''), hints=['클래스 **안**에서는 `self.__balance` 로 그대로 써요. 이름이 바뀌는 건 파이썬이 알아서 해요.', '`pay` 의 검사 순서: 금액 오류 → 잔액 부족 → 결제', '`__str__` 안에서도 `self.__balance`, `self.__count` 를 직접 써도 돼요(클래스 안이니까).'], ex='`해킹 9999999` 뒤에도 잔액은 그대로예요. 메인 코드의 `g.__balance = …` 는 `_Gpay__balance` 가 아니라 **`__balance` 라는 새 속성**을 만들었을 뿐이에요. 이 차이를 글로 설명하는 것이 2025 2번(18점)의 서술 부분이었어요.'),
prac('[기출유사 · 14점] 공부 시간 기록장', '`StudyLog` 클래스로 과목별 공부 시간을 기록해요.\n\n- private 속성: 과목별 누적 시간 딕셔너리 `__times`\n- `add(self, subject, minutes)` : minutes 가 1~600 이 아니면 **ValueError 를 raise**. 정상이면 누적\n- `get_total(self)` : 전체 시간(분)\n- `get_best(self)` : 가장 오래 공부한 과목 이름 (같으면 **먼저 기록된** 과목, 기록이 없으면 None)\n- `report(self)` : 과목을 **시간 내림차순, 같으면 이름 사전순**으로 `(과목, 분)` 튜플의 리스트로 return\n\n입력: 명령이 한 줄씩, `종료` 에서 끝.\n- `기록 과목 분` → `기록 완료` / (ValueError 또는 분이 정수가 아님) `시간 오류`\n- `합계` → `총 H시간 M분`\n- `최고` → 과목 이름 또는 `기록 없음`\n- `보고` → 과목마다 `과목: N분` 한 줄씩, 없으면 `기록 없음`\n\n[조건] ○ `__times` 는 클래스 밖에서 직접 쓰지 않을 것 ○ `get_best` 의 "없음"은 **`is None`** 으로 검사할 것',
D('''
class StudyLog:
    def __init__(self):
        self.__times = {}
    def add(self, subject, minutes):
        if not 1 <= minutes <= 600:
            raise ValueError("시간 범위")
        self.__times[subject] = self.__times.get(subject, 0) + minutes
    def get_total(self):
        return sum(self.__times.values())
    def get_best(self):
        best = None
        for s in self.__times:
            if best is None or self.__times[s] > self.__times[best]:
                best = s
        return best
    def report(self):
        return sorted(self.__times.items(), key=lambda p: (-p[1], p[0]))
log = StudyLog()
while True:
    cmd = input().split()
    if cmd[0] == "종료":
        break
    if cmd[0] == "기록":
        try:
            log.add(cmd[1], int(cmd[2]))
            print("기록 완료")
        except ValueError:
            print("시간 오류")
    elif cmd[0] == "합계":
        t = log.get_total()
        print(f"총 {t // 60}시간 {t % 60}분")
    elif cmd[0] == "최고":
        b = log.get_best()
        print("기록 없음" if b is None else b)
    elif cmd[0] == "보고":
        rows = log.report()
        if not rows:
            print("기록 없음")
        for s, m in rows:
            print(f"{s}: {m}분")
'''), ['최고\n기록 수학 50\n기록 정보 90\n기록 수학 40\n기록 영어 0\n기록 영어 한시간\n합계\n최고\n보고\n종료', '합계\n보고\n종료', '기록 a 600\n기록 b 601\n기록 b 600\n최고\n보고\n합계\n종료', '기록 국어 30\n기록 과학 30\n기록 국어 1\n기록 과학 1\n최고\n보고\n종료', '기록 x -5\n기록 x 5.5\n최고\n기록 x 59\n기록 y 61\n합계\n최고\n종료'],
  hints=['`int(cmd[2])` 가 실패해도 ValueError, `add` 가 raise 해도 ValueError — 한 except 로 둘 다 잡혀요.', '`get_best`: `best = None` 에서 시작해 `if best is None or 시간 > 최고시간:` 으로 갱신(`>` 라서 같으면 먼저 것 유지)', '`report`: `sorted(self.__times.items(), key=lambda p: (-p[1], p[0]))`'], ex='`report` 가 딕셔너리 자체가 아니라 **새 리스트**를 돌려주는 점을 보세요. `return self.__times` 로 내주면 밖에서 `log.report()["수학"] = 9999` 로 바꿀 수 있어요 — 같은 객체(`is`)를 내준 셈이라 캡슐화가 뚫려요.'),
prac('[심화 · 14점] 같은 학생, 같은 객체', '출석부를 정리해요. `Student(sid, name)` 클래스에 **학번이 같으면 같은 학생**이 되도록 `__eq__` 를 정의하세요.\n\n입력: 첫 줄 `n`, 이어서 n 줄에 `학번 이름`. 그다음 줄 `q`, 이어서 q 줄에 질의.\n\n처리\n1. 입력 순서대로 Student 객체를 만들어요. 이미 명단에 **같은 학생**(`==`)이 있으면 추가하지 않고 `중복: 학번 (기존이름/새이름)` 을 출력해요.\n2. 등록이 끝나면 `등록 N명` 을 출력해요.\n3. 질의\n   - `비교 i j` : 명단의 i 번째와 j 번째(1부터)가 **같은 객체**면 `같은 객체`, 아니면 `다른 객체`\n   - `검색 학번` : 그 학번의 학생이 명단에 있으면 `K번째 이름`, 없으면 `없음`\n   - `별명 i 새이름` : `alias = 명단[i]` 로 꺼낸 뒤 `alias.name` 을 바꾸고, 명단 i 번째 학생의 이름을 출력\n   - `복사 i 새이름` : i 번째와 학번·이름이 같은 **새 객체**를 만들어 그 이름을 바꾼 뒤, 명단 i 번째 학생의 이름 / 새 객체와 `==` 인지(`같은 학생`/`다른 학생`) / `is` 인지(`같은 객체`/`다른 객체`) 를 공백으로 구분해 한 줄에 출력\n\n[조건] ○ 중복 검사는 `in`, 검색은 `index` 를 사용할 것 (학번을 꺼내 직접 비교하는 반복문 금지) ○ 검색에서 없는 경우는 **ValueError** 로 처리',
D('''
class Student:
    def __init__(self, sid, name):
        self.sid = sid
        self.name = name
    def __eq__(self, other):
        return self.sid == other.sid
n = int(input())
roster = []
for _ in range(n):
    sid, name = input().split()
    s = Student(sid, name)
    if s in roster:
        old = roster[roster.index(s)]
        print(f"중복: {sid} ({old.name}/{name})")
    else:
        roster.append(s)
print(f"등록 {len(roster)}명")
q = int(input())
for _ in range(q):
    cmd = input().split()
    if cmd[0] == "비교":
        i, j = int(cmd[1]) - 1, int(cmd[2]) - 1
        print("같은 객체" if roster[i] is roster[j] else "다른 객체")
    elif cmd[0] == "검색":
        try:
            k = roster.index(Student(cmd[1], ""))
            print(f"{k + 1}번째 {roster[k].name}")
        except ValueError:
            print("없음")
    elif cmd[0] == "별명":
        alias = roster[int(cmd[1]) - 1]
        alias.name = cmd[2]
        print(roster[int(cmd[1]) - 1].name)
    elif cmd[0] == "복사":
        src = roster[int(cmd[1]) - 1]
        copy = Student(src.sid, src.name)
        copy.name = cmd[2]
        a = "같은 학생" if copy == src else "다른 학생"
        b = "같은 객체" if copy is src else "다른 객체"
        print(src.name, a, b)
'''), ['4\n1001 민\n1002 솔\n1001 민수\n1003 율\n5\n비교 1 1\n비교 1 2\n검색 1002\n검색 1009\n별명 2 솔이', '1\n7 가\n3\n복사 1 나\n별명 1 다\n복사 1 라', '3\na x\na y\na z\n2\n검색 a\n비교 1 1', '2\n10 김\n20 이\n4\n별명 1 박\n검색 10\n복사 2 최\n검색 20', '5\n1 a\n2 b\n3 c\n2 d\n1 e\n3\n검색 3\n비교 3 2\n복사 3 z'],
  hints=['`__eq__`: `return self.sid == other.sid` — 이제 `s in roster` 와 `roster.index(s)` 가 학번으로 비교해요.', '검색: 이름은 아무거나 넣은 임시 객체 `Student(학번, "")` 로 `roster.index(…)` 를 불러요. 없으면 ValueError.', '`별명` 은 같은 객체라 명단이 바뀌고, `복사` 는 새 객체라 명단이 안 바뀌어요.'], ex='`별명` 과 `복사` 의 출력 차이가 이 강의 전부예요. **`=` 는 복사가 아니다** — 같은 객체(`is`)에 이름을 하나 더 붙일 뿐이에요. `==` 가 True 여도 `is` 는 False 일 수 있고, 그 기준(`__eq__`)은 내가 정해요.'),
)
