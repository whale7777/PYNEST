from glib import *

# ============================================================ D7
_ret_bug = D('''
def twice(func):
    def wrapper(x):
        print("호출:", x)
        func(x)
    return wrapper
@twice
def square(x):
    return x * x
r = square(4)
print(r + 1)
''')
assert errline(_ret_bug) == 10 and err(_ret_bug) == 'TypeError'
_arg_bug = D('''
def log(func):
    def wrapper():
        print("start")
        return func()
    return wrapper
@log
def hello():
    return "hi"
@log
def add(a, b):
    return a + b
print(hello())
print(add(1, 2))
''')
assert errline(_arg_bug) == 13 and err(_arg_bug) == 'TypeError'
assert run(D('''
def deco(f):
    print("D")
    def w():
        print("W")
        return f()
    return w
@deco
def a():
    return 1
print("M")
a()
a()
''')) == 'D\nM\nW\nW'

D7 = lesson('7강. 데코레이터 — 함수를 감싸는 함수', 50,
'- 함수는 **값**이다: 변수에 담고, 인자로 넘기고, return 할 수 있다\n- 데코레이터 = **함수를 받아 wrapper(새 함수)를 return 하는 함수**. wrapper 는 원래 함수를 기억하는 **클로저**\n- `@deco` 를 함수 위에 쓰면 `f = deco(f)` 와 같다 → 그 뒤의 `f` 는 사실 **wrapper**\n- 데코레이터의 몸통은 **정의할 때 한 번**, wrapper 의 몸통은 **호출할 때마다** 실행된다\n- 어떤 인자든 받으려면 `wrapper(*args, **kwargs)` → `func(*args, **kwargs)`, 그리고 **`return` 을 빠뜨리면 결과가 None**\n- 두 개를 겹치면 **아래 것이 먼저 감싸고**, 호출하면 **위(바깥) 것이 먼저 실행**된다',
review('🔁 6강 복습', [T('데코레이터는 클로저 위에 세워져요. 6강의 핵심 네 가지를 먼저 확인해요.'), flip(['클로저란?', '바깥 함수의 변수를 **기억하고 있는 안쪽 함수** (바깥 함수가 끝난 뒤에도 기억)'], ['자유 변수', '안쪽 함수가 쓰지만 안쪽에서 만들지 않은, **바깥 함수의 변수**'], ['안쪽에서 바깥 변수에 `total += x` 를 하려면', '`nonlocal total` 선언이 필요 (없으면 UnboundLocalError)'], ['`a = make()` , `b = make()`', 'a 와 b 는 **서로 다른 기억**을 가진다 (호출마다 새 변수)'])]),
outq('복습 — 출력 결과는?', D('''
def make_avg():
    total = 0
    count = 0
    def add(x):
        nonlocal total, count
        total += x
        count += 1
        return total / count
    return add
a = make_avg()
b = make_avg()
a(10)
a(20)
print(a(60), b(5), a(10))
'''), 'a 는 10, 20, 60, 10 을 차례로 기억해 평균 30.0 → 25.0, b 는 따로 5 하나만 기억해요.', review=True),
explain('함수도 값이에요',
  [T('데코레이터를 이해하는 데 필요한 사실은 하나예요. **함수는 숫자나 문자열처럼 값**이라서 변수에 담고, 다른 함수의 **인자로 넘길** 수 있어요. 이때 괄호를 붙이지 않는 것이 핵심이에요.'),
   C(D('''
def hello():
    return "안녕"
def run_twice(func):
    return func() + func()
g = hello            # 괄호 없음 → 함수 자체를 담음
print(g())
print(run_twice(hello))
print(hello.__name__, g.__name__)
'''), 'hello 는 함수 자체, hello() 는 호출한 결과'),
   key('`hello` 는 **함수 자체**, `hello()` 는 **호출한 결과**예요. `run_twice(hello())` 라고 쓰면 문자열 "안녕" 을 넘기게 되어 `func()` 에서 TypeError 가 나요.')],
  [T('6강에서 본 것처럼 함수는 **함수를 return** 할 수도 있어요. 이 둘을 합치면 "함수를 받아서, 앞뒤에 일을 덧붙인 **새 함수**를 돌려주는 함수"를 만들 수 있어요.'),
   C(D('''
def deco(func):
    def wrapper():
        print("== 시작 ==")
        func()
        print("== 끝 ==")
    return wrapper
def greet():
    print("안녕하세요")
new_greet = deco(greet)
new_greet()
'''), 'wrapper 는 func(=greet)를 기억하는 클로저'),
   steps(['① deco(greet) 호출', 'func 에 greet 함수가 들어가요'], ['② wrapper 를 만들어 return', 'wrapper 는 아직 **실행되지 않았어요**. func 를 기억한 채로 반환될 뿐이에요'], ['③ new_greet()', '이제서야 wrapper 의 몸통이 실행 → 시작 출력 → 기억해 둔 greet 호출 → 끝 출력'])],
  [T('이 `deco` 가 바로 **데코레이터**예요. 원래 함수의 코드는 한 글자도 고치지 않고 기능(앞뒤 출력)을 덧붙였어요.'),
   exam('2023 2차의 마지막 문항(10점)이 데코레이터 출력 추론이었어요. 문법이 낯설 뿐, 묻는 것은 "**어느 print 가 언제 실행되는가**"와 "**return 값이 어디로 가는가**" 두 가지예요.')]),
outq('[기출유사] 출력 결과는?', D('''
def apply(func, x):
    return func(func(x))
def inc(n):
    return n + 3
def dbl(n):
    return n * 2
f = dbl
print(apply(inc, 1), apply(f, 5), f(inc(1)), apply(f, inc(0)))
'''), '`apply(inc, 1)` = inc(inc(1)) = 7, `apply(f, 5)` = dbl(dbl(5)) = 20, `f(inc(1))` = dbl(4) = 8. 마지막은 인자 `inc(0)` = 3 이 먼저 계산되어 dbl(dbl(3)) = 12 예요.'),
order('[기출유사] "함수 실행 앞뒤에 줄을 긋는" 데코레이터와 사용 코드예요. 올바른 순서로 놓으세요.', ['def line(func):', '    def wrapper():', '        print("-----")', '        func()', '        print("-----")', '    return wrapper', 'def menu():', '    print("1. 시작")', 'menu = line(menu)', 'menu()'], '`return wrapper` 는 wrapper 의 **밖**, line 의 **안**(들여쓰기 한 칸)에 있어야 해요.'),
explain('@ 는 f = deco(f) 의 줄임말',
  [T('`new_greet = deco(greet)` 처럼 새 이름을 만드는 대신, 보통은 **같은 이름에 다시 담아요**. 파이썬은 이것을 `@` 한 줄로 쓰게 해 줘요.'),
   cmp('직접 쓰기', 'def greet():\n    print("안녕하세요")\ngreet = deco(greet)', '@ 로 쓰기', '@deco\ndef greet():\n    print("안녕하세요")', lb='def 가 끝난 뒤에 감싸요', rb='완전히 같은 뜻이에요. 감싸는 시점도 **def 직후**', tones=('good', 'good')),
   key('`@deco` 아래의 `def f` 는 "f 를 만들자마자 **`f = deco(f)`** 를 실행하라"는 뜻이에요. 그래서 그 뒤로 `f` 라는 이름이 가리키는 것은 원래 함수가 아니라 **wrapper** 예요.')],
  [T('그럼 `deco` 의 몸통과 `wrapper` 의 몸통은 각각 **언제** 실행될까요? 출력 순서 문제는 전부 이 질문이에요.'),
   trace(D('''
def deco(func):
    print("감싸는 중:", func.__name__)
    def wrapper():
        print("앞")
        func()
        print("뒤")
    return wrapper
@deco
def work():
    print("일하는 중")
print("--- 메인 ---")
work()
work()
'''), '"감싸는 중"은 몇 번, 언제 출력될까요?'),
   warn('`deco` 의 몸통(= "감싸는 중")은 `@deco def work` 를 **정의하는 순간 딱 한 번** 실행돼요. `work()` 를 한 번도 부르지 않아도 출력돼요. `wrapper` 의 몸통("앞", "뒤")은 **호출할 때마다** 실행돼요.')],
  [T('감싼 뒤에 `work` 가 정말 wrapper 로 바뀌었는지 이름으로 확인할 수 있어요.'),
   C(D('''
def deco(func):
    def wrapper():
        return func().upper()
    return wrapper
@deco
def word():
    return "python"
print(word())
print(word.__name__)
'''), 'word 의 진짜 정체'),
   tip('서술형에서 "`@deco` 의 의미"를 물으면 ① `word = deco(word)` 와 같다 ② 이후 `word` 를 호출하면 `deco` 가 return 한 **wrapper 가 실행**된다 — 이 두 문장을 쓰면 돼요.')]),
outq('[기출유사] 출력 결과는?', D('''
def tag(func):
    print("A")
    def wrapper():
        print("B")
        func()
        print("C")
    return wrapper
print("D")
@tag
def show():
    print("E")
print("F")
show()
print("G")
'''), '`def tag` 는 정의일 뿐이라 아무것도 출력하지 않아요. D → (`@tag` 에서 tag 몸통 실행) A → F → show() 호출로 B, E, C → G.'),
sh('[기출유사] 아래 코드에서 `"준비"` 는 모두 몇 번 출력될까요?\n\n```\ndef deco(f):\n    print("준비")\n    def w():\n        print("실행")\n        return f()\n    return w\n@deco\ndef a():\n    return 1\n@deco\ndef b():\n    return 2\na(); a(); b()\n```', 2, '`"준비"` 는 deco 의 몸통이라 **@ 를 쓴 횟수(2번)** 만큼만 출력돼요. `"실행"` 은 호출 횟수인 3번이에요.', alts=['2번', '두 번']),
essay('[기출유사 · 서술 5점] 아래 코드에서 `@timer` 가 하는 일을 **대입문 한 줄**로 바꿔 쓰고, 마지막 줄 `study()` 를 실행하면 실제로 **어떤 함수가 실행되는지** 서술하세요.\n\n```\ndef timer(func):\n    def wrapper():\n        print("시작")\n        func()\n        print("종료")\n    return wrapper\n@timer\ndef study():\n    print("공부")\nstudy()\n```', '@timer 는 study 함수를 정의한 직후에 study = timer(study) 를 실행하는 것과 같다. timer 는 원래의 study 를 func 로 기억하는 wrapper 함수를 return 하므로, 이후 study 라는 이름은 wrapper 를 가리킨다. 따라서 study() 를 실행하면 wrapper 가 실행되어 "시작" 을 출력하고, 기억해 둔 원래 study 를 호출해 "공부" 를 출력한 뒤 "종료" 를 출력한다.', ['study = timer(study) 라고 썼다', 'study 가 wrapper 를 가리키게 된다고 썼다', 'wrapper 안에서 원래 함수(func)가 호출된다고 썼다', '출력 순서(시작 → 공부 → 종료)를 맞게 썼다']),
explain('인자와 반환값 — *args 와 return',
  [T('지금까지의 wrapper 는 인자가 없었어요. 그런데 `study = wrapper` 가 되었으니 **`study(3)` 은 곧 `wrapper(3)`** 이에요. wrapper 가 인자를 받지 못하면 TypeError 예요.'),
   CX(_arg_bug, 'add(1, 2) 는 wrapper(1, 2) — wrapper 는 인자를 0개만 받음 → TypeError'),
   key('어떤 함수든 감쌀 수 있게 wrapper 는 **`*args, **kwargs` 로 받아서 그대로 넘겨요**: `def wrapper(*args, **kwargs):` → `func(*args, **kwargs)`. `args` 는 위치 인자를 모은 **튜플**, `kwargs` 는 키워드 인자를 모은 **딕셔너리**예요.')],
  [T('두 번째 함정은 **return** 이에요. 호출한 쪽이 받는 값은 원래 함수의 return 이 아니라 **wrapper 의 return** 이에요.'),
   cmp('return 누락', 'def wrapper(*args):\n    print("호출")\n    func(*args)', 'return 있음', 'def wrapper(*args):\n    print("호출")\n    return func(*args)', lb='func 의 결과를 버려요. wrapper 는 **None** 을 돌려줘요', rb='func 의 결과를 호출한 쪽에 전달해요', tones=('bad', 'good')),
   C(D('''
def log(func):
    def wrapper(*args, **kwargs):
        print("인자:", args, kwargs)
        result = func(*args, **kwargs)
        print("결과:", result)
        return result
    return wrapper
@log
def power(base, exp=2):
    return base ** exp
a = power(3)
b = power(2, exp=5)
print(a + b)
'''), '결과를 변수에 받아 두면 출력도 하고 return 도 할 수 있어요')],
  [T('2023 기출은 "**인자들의 합(또는 곱)을 먼저 출력**하고 원래 함수를 실행"하는 데코레이터였어요. `args` 가 튜플이라는 점만 알면 `sum(args)` 와 for 문으로 끝나요.'),
   C(D('''
def show_sum(func):
    def wrapper(*args):
        print("합:", sum(args))
        return func(*args)
    return wrapper
def show_prod(func):
    def wrapper(*args):
        p = 1
        for x in args:
            p *= x
        print("곱:", p)
        return func(*args)
    return wrapper
@show_sum
def biggest(*nums):
    return max(nums)
@show_prod
def count(*nums):
    return len(nums)
print(biggest(3, 9, 4))
print(count(2, 5, 10))
'''), '출력 순서: wrapper 의 print → 원래 함수의 return 값'),
   exam('출력 추론 순서: ① **wrapper 안의 print** 가 먼저 ② 그다음 `print(biggest(...))` 가 **return 값**을 출력. `print(f(...))` 는 f 가 완전히 끝난 뒤에야 찍힌다는 점을 기억하세요.')]),
outq('[기출유사] 출력 결과는?', D('''
def show_prod(func):
    def wrapper(*args):
        p = 1
        for x in args:
            p *= x
        print("곱", p, end=" / ")
        return func(*args)
    return wrapper
@show_prod
def total(*nums):
    return sum(nums)
@show_prod
def first(*nums):
    return nums[0]
print(total(2, 3, 4))
print(first(5, 0, 7) + total(1, 1))
'''), '둘째 줄: `first(5, 0, 7)` 의 wrapper 가 "곱 0" 을, 이어서 `total(1, 1)` 의 wrapper 가 "곱 1" 을 출력한 **뒤에야** 5 + 2 = 7 이 찍혀요.'),
spot('[기출유사] **예외가 발생하는 줄**은?', _ret_bug, 10, 'wrapper 가 `func(x)` 의 결과를 return 하지 않아서 `r` 은 None 이에요. 9번 줄까지는 "호출: 4" 를 출력하며 정상이고, 10번 줄 `None + 1` 에서 TypeError. 4번 줄을 `return func(x)` 로 고쳐요.'),
fill('[기출유사] 어떤 인자든 그대로 전달하고 결과도 돌려주는 wrapper 를 완성하세요.', D('''
def shout(func):
    def wrapper(___, **kwargs):
        result = func(*args, ___)
        ___ str(result) + "!"
    return wrapper
@shout
def add(a, b=10):
    return a + b
print(add(1), add(2, b=3))
'''), ['*args', '**kwargs', 'return'], '받을 때도 `*args, **kwargs`, 넘길 때도 `*args, **kwargs` 예요.', expect='11! 5!'),
essay('[기출유사 · 서술 6점] 아래 코드는 `None` 을 출력해요. **문제점**을 쓰고 `25` 가 출력되도록 **수정**하세요.\n\n```\ndef check(func):\n    def wrapper(x):\n        if x < 0:\n            x = 0\n        func(x)\n    return wrapper\n@check\ndef square(x):\n    return x * x\nprint(square(5))\n```', '@check 때문에 square 는 wrapper 를 가리키므로 square(5) 는 wrapper(5) 를 실행한다. wrapper 는 안에서 func(x) 를 호출해 25 를 계산하지만 그 결과를 return 하지 않고 버리기 때문에, wrapper 의 반환값은 None 이 되어 None 이 출력된다. wrapper 의 마지막 줄을 return func(x) 로 고치면 원래 함수의 결과가 호출한 쪽으로 전달되어 25 가 출력된다.', ['square(5) 가 실제로는 wrapper(5) 라고 썼다', 'wrapper 가 func 의 결과를 return 하지 않는다고 썼다', 'return 이 없으면 None 이 반환된다고 썼다', 'return func(x) 로 수정했다']),
explain('횟수 세기와 겹쳐 쓰기',
  [T('wrapper 는 클로저라서 **바깥 함수(데코레이터)의 변수**를 기억해요. 여기에 6강의 `nonlocal` 을 더하면 "이 함수가 몇 번 불렸는지" 세는 데코레이터가 돼요.'),
   C(D('''
def counter(func):
    count = 0
    def wrapper(*args):
        nonlocal count
        count += 1
        print(f"{func.__name__} {count}번째 호출")
        return func(*args)
    return wrapper
@counter
def add(a, b):
    return a + b
@counter
def neg(x):
    return -x
add(1, 2)
add(3, 4)
neg(5)
print(add(5, 6))
'''), 'add 와 neg 는 각자의 count 를 가져요'),
   key('`count = 0` 은 데코레이터 몸통에 있으므로 **@ 를 쓴 함수마다 한 번씩** 실행돼요. 그래서 add 와 neg 는 **서로 다른 count** 를 기억해요. `nonlocal` 이 없으면 `count += 1` 에서 UnboundLocalError 예요.')],
  [T('데코레이터를 **두 개** 쌓을 수도 있어요. 읽는 법은 `@` 를 대입문으로 풀어 쓰는 것이에요.'),
   C(D('''
def bold(func):
    def wrapper():
        return "<b>" + func() + "</b>"
    return wrapper
def star(func):
    def wrapper():
        return "*" + func() + "*"
    return wrapper
@bold
@star
def word():
    return "hi"
print(word())
'''), 'word = bold(star(word))'),
   steps(['① 감싸는 순서는 아래 → 위', '`@star` 가 먼저 word 를 감싸고, 그 결과를 `@bold` 가 다시 감싸요: `word = bold(star(word))`'], ['② 실행 순서는 위(바깥) → 아래', '`word()` 는 bold 의 wrapper 를 실행 → 그 안의 func() 가 star 의 wrapper → 그 안의 func() 가 원래 word'], ['③ 결과가 돌아오는 순서는 다시 안 → 밖', '"hi" → "*hi*" → "<b>*hi*</b>"'])],
  [T('print 가 섞이면 순서가 더 헷갈려요. "**func() 호출 앞의 코드는 바깥부터, 뒤의 코드는 안쪽부터**" 실행돼요. 상자 안에 상자를 넣은 모양이에요.'),
   trace(D('''
def outer(func):
    def wrapper():
        print("outer 앞")
        func()
        print("outer 뒤")
    return wrapper
def inner(func):
    def wrapper():
        print("inner 앞")
        func()
        print("inner 뒤")
    return wrapper
@outer
@inner
def core():
    print("core")
core()
'''), '상자 안의 상자'),
   exam('겹친 데코레이터는 반드시 `f = A(B(f))` 로 **풀어 쓴 뒤** 추적하세요. 위에 적힌 것이 바깥 상자예요.')]),
outq('[기출유사] 출력 결과는?', D('''
def counter(func):
    count = 0
    def wrapper(*args):
        nonlocal count
        count += 1
        return f"{count}:{func(*args)}"
    return wrapper
@counter
def add(a, b):
    return a + b
@counter
def mul(a, b):
    return a * b
print(add(1, 2), add(3, 4), mul(3, 4), add(0, 0), mul(1, 1))
'''), 'add 와 mul 은 각자의 count 를 기억해요. add 는 1, 2, 3 번째, mul 은 1, 2 번째 호출이에요.'),
outq('[심화] 출력 결과는?', D('''
def add_one(func):
    def wrapper(x):
        return func(x) + 1
    return wrapper
def double(func):
    def wrapper(x):
        return func(x) * 2
    return wrapper
@add_one
@double
def f(x):
    return x
@double
@add_one
def g(x):
    return x
print(f(5), g(5))
'''), '`f = add_one(double(f))` → (5 × 2) + 1 = 11, `g = double(add_one(g))` → (5 + 1) × 2 = 12. **아래 것이 먼저 적용**돼요.'),
outq('[심화] 출력 결과는?', D('''
def A(func):
    print("A 감쌈")
    def wrapper():
        print("A1", end=" ")
        func()
        print("A2", end=" ")
    return wrapper
def B(func):
    print("B 감쌈")
    def wrapper():
        print("B1", end=" ")
        func()
        print("B2", end=" ")
    return wrapper
@A
@B
def go():
    print("GO", end=" ")
go()
print()
'''), '감싸는 것은 아래(B)부터, 실행은 바깥(A)부터예요. func() 뒤의 코드는 안쪽(B2)이 먼저 끝나요.'),
match('코드와 뜻을 이어 보세요.', [['@deco 를 def f 위에 쓴다', 'f = deco(f)'], ['@A 아래 @B 를 쓰고 def f', 'f = A(B(f))'], ['wrapper(*args)', '위치 인자를 튜플로 모아 받는다'], ['func(*args)', '튜플을 풀어서 인자로 넘긴다'], ['nonlocal count', '바깥 함수의 변수를 고쳐 쓰겠다는 선언']]),
bucket('[기출유사] 아래 코드에서 각 줄이 **언제** 실행되는지 분류하세요.\n\n```\ndef deco(func):\n    print("P")            # ㉠\n    n = 0                 # ㉡\n    def wrapper(*args):\n        print("Q")        # ㉢\n        return func(*args)  # ㉣\n    return wrapper        # ㉤\n@deco\ndef f(x):\n    return x\n```', ['@deco def f 를 정의할 때 한 번', 'f(...) 를 호출할 때마다'], [['㉠ print("P")', 1], ['㉡ n = 0', 1], ['㉢ print("Q")', 2], ['㉣ return func(*args)', 2], ['㉤ return wrapper', 1]], 'deco 의 몸통(㉠㉡㉤)은 정의 시점에 한 번, wrapper 의 몸통(㉢㉣)은 호출마다예요.'),
essay('[심화 · 서술 6점] 아래 코드의 출력은 `1 2 3 2 1` 이에요(공백 구분). 이 순서로 출력되는 **이유**를 `@` 를 대입문으로 풀어 쓴 식과 연결하여 서술하세요.\n\n```\ndef first(func):\n    def wrapper():\n        print(1, end=" ")\n        func()\n        print(1, end=" ")\n    return wrapper\ndef second(func):\n    def wrapper():\n        print(2, end=" ")\n        func()\n        print(2, end=" ")\n    return wrapper\n@first\n@second\ndef core():\n    print(3, end=" ")\ncore()\n```', '데코레이터는 아래에서 위로 적용되므로 core = first(second(core)) 와 같다. 즉 second 의 wrapper 가 원래 core 를 감싸고, first 의 wrapper 가 그것을 다시 감싼다. core() 를 호출하면 가장 바깥인 first 의 wrapper 가 먼저 실행되어 1 을 출력하고, 그 안의 func() 가 second 의 wrapper 를 호출해 2 를 출력하며, 다시 그 안의 func() 가 원래 core 를 호출해 3 을 출력한다. 그 뒤 호출이 끝나는 순서대로 안쪽인 second 의 wrapper 가 2 를, 마지막으로 first 의 wrapper 가 1 을 출력한다.', ['core = first(second(core)) 로 풀어 썼다', '호출하면 바깥(first)의 wrapper 가 먼저 실행된다고 썼다', 'func() 호출이 안쪽 wrapper, 원래 함수로 이어진다고 썼다', 'func() 뒤의 출력은 안쪽부터 끝난다고 썼다']),
prac('[기출유사] 합과 곱을 먼저 알려 주는 데코레이터', '실험 측정값을 처리하는 함수 두 개에 "**인자들의 합/곱을 먼저 출력**하는" 데코레이터를 붙여요.\n\n- 데코레이터 `show_sum` : 원래 함수를 실행하기 전에 `합: S` 를 출력\n- 데코레이터 `show_prod` : 원래 함수를 실행하기 전에 `곱: P` 를 출력\n- `@show_sum` 을 붙인 `spread(*nums)` : 최댓값 - 최솟값을 **return**\n- `@show_prod` 를 붙인 `evens(*nums)` : 짝수의 개수를 **return**\n\n입력: 한 줄에 정수 1개 이상(공백 구분).\n\n출력: `spread` 를 호출한 결과를 `범위: R`, 이어서 `evens` 를 호출한 결과를 `짝수: K개` 로 출력해요. (데코레이터의 출력이 각각 그 앞줄에 나와요)\n\n[조건] ○ 두 wrapper 모두 `*args` 로 인자를 받는다 ○ 원래 함수 안에서는 print 를 쓰지 않는다 ○ 곱은 반복문으로 직접 구한다',
D('''
def show_sum(func):
    def wrapper(*args):
        print("합:", sum(args))
        return func(*args)
    return wrapper
def show_prod(func):
    def wrapper(*args):
        p = 1
        for x in args:
            p *= x
        print("곱:", p)
        return func(*args)
    return wrapper
@show_sum
def spread(*nums):
    return max(nums) - min(nums)
@show_prod
def evens(*nums):
    return len([x for x in nums if x % 2 == 0])
data = list(map(int, input().split()))
print("범위:", spread(*data))
print(f"짝수: {evens(*data)}개")
'''), ['3 8 5', '7', '2 4 6 8', '-3 0 9 1', '1 1 1 1 1', '10 -2 5 -4 3 6'],
  starter=D('''
def show_sum(func):
    def wrapper(*args):
        # 합을 출력하고, 원래 함수의 결과를 return
        pass
    return wrapper

def show_prod(func):
    def wrapper(*args):
        pass
    return wrapper

@show_sum
def spread(*nums):
    return max(nums) - min(nums)

@show_prod
def evens(*nums):
    return len([x for x in nums if x % 2 == 0])

data = list(map(int, input().split()))
print("범위:", spread(*data))
print(f"짝수: {evens(*data)}개")
'''),
  hints=['wrapper 안에서 `args` 는 튜플이에요. `sum(args)` 로 합을 구해요.', '곱은 `p = 1` 에서 시작해 `for x in args: p *= x`.', 'wrapper 의 마지막 줄은 반드시 `return func(*args)` — 빠뜨리면 `범위: None` 이 나와요.'],
  ex='`print("범위:", spread(*data))` 는 spread(= wrapper)가 **끝난 뒤** 출력되므로 "합:" 줄이 먼저 나와요.'),
prac('[기출유사] 호출 횟수를 세는 데코레이터', '자판기 프로그램의 두 함수가 각각 몇 번 불렸는지 세어요.\n\n- 데코레이터 `counter` : 감싼 함수가 불릴 때마다 그 함수의 호출 횟수를 1 늘리고, **`[함수이름 N번째]`** 를 출력한 뒤 원래 함수를 실행해 결과를 return\n- `@counter` 를 붙인 `insert(coin)` : 잔액에 coin 을 더하고 잔액을 return\n- `@counter` 를 붙인 `buy(price)` : 잔액이 price 이상이면 빼고 `True`, 아니면 그대로 두고 `False` 를 return\n\n입력: 첫 줄 `n`, 이어서 n 줄에 `insert 금액` 또는 `buy 가격`.\n\n출력: 명령마다 데코레이터의 출력 한 줄, 그 다음 줄에 `insert` 는 `잔액: B원`, `buy` 는 성공이면 `구매 성공 (잔액: B원)`, 실패면 `잔액 부족`. 마지막 줄에 `남은 돈: B원`.\n\n[조건] ○ 횟수는 전역 변수가 아니라 **데코레이터 안의 변수 + nonlocal** 로 센다 ○ 함수 이름은 `func.__name__` 으로 얻는다 ○ 잔액은 전역 변수 `balance` 를 사용한다',
D('''
def counter(func):
    count = 0
    def wrapper(*args):
        nonlocal count
        count += 1
        print(f"[{func.__name__} {count}번째]")
        return func(*args)
    return wrapper
balance = 0
@counter
def insert(coin):
    global balance
    balance += coin
    return balance
@counter
def buy(price):
    global balance
    if balance >= price:
        balance -= price
        return True
    return False
n = int(input())
for _ in range(n):
    cmd, v = input().split()
    v = int(v)
    if cmd == "insert":
        print(f"잔액: {insert(v)}원")
    else:
        if buy(v):
            print(f"구매 성공 (잔액: {balance}원)")
        else:
            print("잔액 부족")
print(f"남은 돈: {balance}원")
'''), ['4\ninsert 1000\nbuy 700\nbuy 500\ninsert 500', '1\nbuy 100', '5\ninsert 500\ninsert 500\ninsert 500\nbuy 1500\nbuy 1', '3\nbuy 300\ninsert 300\nbuy 300', '6\ninsert 100\nbuy 50\nbuy 50\nbuy 50\ninsert 50\nbuy 50', '2\ninsert 0\nbuy 0'],
  hints=['`count = 0` 은 `counter` 의 몸통(wrapper 밖)에 둬요. 그래야 함수마다 따로 세요.', 'wrapper 안 첫 줄에 `nonlocal count`, 이어서 `count += 1`.', '`print(f"[{func.__name__} {count}번째]")` 뒤 `return func(*args)`'],
  ex='insert 와 buy 는 `@counter` 를 각각 한 번씩 거치므로 서로 다른 count 를 기억해요.'),
prac('[심화] 검사 데코레이터 두 개 겹치기', '점수 계산 함수 앞에 **검사 데코레이터 두 개**를 겹쳐요.\n\n- `non_negative` : 인자 중 음수를 모두 **0 으로 바꿔** 원래 함수에 넘겨요. 바꾼 값이 하나라도 있으면 `음수 K개를 0으로` 를 출력해요.\n- `limit3` : 인자가 3개보다 많으면 **앞의 3개만** 넘기고 `3개만 사용` 을 출력해요.\n- `total(*scores)` : 합을 return\n\n`total` 에는 위에서부터 `@limit3`, `@non_negative` 순서로 붙여요. 즉 **limit3 이 바깥**이라 먼저 3개로 자른 뒤, 남은 값에서 음수를 고쳐요.\n\n입력: 첫 줄 `n`, 이어서 n 줄에 정수 1개 이상(공백 구분).\n\n출력: 줄마다 데코레이터의 안내(있을 때만) → `합계: S`.\n\n[조건] ○ 두 wrapper 모두 `*args` 로 받고 결과를 return ○ `total` 안에는 검사 코드를 쓰지 않는다',
D('''
def limit3(func):
    def wrapper(*args):
        if len(args) > 3:
            print("3개만 사용")
            args = args[:3]
        return func(*args)
    return wrapper
def non_negative(func):
    def wrapper(*args):
        k = len([x for x in args if x < 0])
        if k > 0:
            print(f"음수 {k}개를 0으로")
        fixed = [max(0, x) for x in args]
        return func(*fixed)
    return wrapper
@limit3
@non_negative
def total(*scores):
    return sum(scores)
n = int(input())
for _ in range(n):
    data = list(map(int, input().split()))
    print("합계:", total(*data))
'''), ['3\n10 20 30\n5 -5 5 -5 5\n-1 -2', '2\n-4\n7', '2\n1 2 3 -100 -200\n-1 -2 -3 -4', '1\n100 -50 25 10', '3\n0 0 0 0\n-9\n4 5', '2\n-1 2 -3 4 -5 6\n9 9 9'],
  hints=['`@limit3` 를 위, `@non_negative` 를 아래에 써요: `total = limit3(non_negative(total))`.', 'limit3 의 wrapper: `if len(args) > 3:` 안에서 `args = args[:3]` (튜플 슬라이싱).', 'non_negative 의 wrapper: 음수 개수를 세고 `[max(0, x) for x in args]` 를 `func(*fixed)` 로 넘겨요.'],
  ex='`5 -5 5 -5 5` → 바깥 limit3 이 먼저 `(5, -5, 5)` 로 자르므로 음수는 **1개**만 고쳐져요. 순서를 바꾸면 "음수 2개" 가 나와요.'),
prac('[심화] 계산 결과를 기억하는 데코레이터', '시간이 오래 걸리는 계산의 결과를 **기억해 두었다가** 같은 인자가 다시 오면 계산하지 않고 돌려주는 데코레이터 `remember` 를 만들어요.\n\n- `remember` : 데코레이터 안에 빈 딕셔너리 `saved` 를 두고, wrapper(n) 는 n 이 `saved` 에 없을 때만 원래 함수를 호출해 저장해요. 저장된 값을 return.\n- `@remember` 를 붙인 `div_sum(n)` : `계산 n` 을 출력하고, n 의 모든 약수의 합을 return\n\n입력: 한 줄에 양의 정수 여러 개.\n\n출력: 수마다 `n -> 약수의 합` 을 한 줄씩 (실제로 계산이 일어날 때만 그 앞줄에 `계산 n`). 마지막 줄에 `실제 계산: K번`.\n\n[조건] ○ `saved` 는 전역 변수가 아니라 데코레이터 안의 변수 ○ 실제 계산 횟수는 `div_sum` 안에서 전역 변수 `calls` 로 센다',
D('''
def remember(func):
    saved = {}
    def wrapper(n):
        if n not in saved:
            saved[n] = func(n)
        return saved[n]
    return wrapper
calls = 0
@remember
def div_sum(n):
    global calls
    calls += 1
    print("계산", n)
    return sum(d for d in range(1, n + 1) if n % d == 0)
for n in map(int, input().split()):
    print(n, "->", div_sum(n))
print(f"실제 계산: {calls}번")
'''), ['6 12 6 28 12', '1', '7 7 7 7', '10 20 30', '100 1 100 1 2', '36 49 36 50 49 36'],
  hints=['wrapper 는 `if n not in saved:` 일 때만 `saved[n] = func(n)`.', '딕셔너리 `saved` 는 **내용을 고칠 뿐** 다시 대입하지 않으므로 nonlocal 이 필요 없어요.', '마지막에 `return saved[n]`. `계산 n` 출력과 `calls += 1` 은 원래 함수 `div_sum` 안에 있어요.'],
  ex='같은 수가 다시 오면 wrapper 가 원래 함수를 **부르지 않으므로** "계산" 줄도 나오지 않고 calls 도 늘지 않아요. `saved` 를 기억하는 것은 클로저의 힘이에요.'),
)

# ============================================================ D8
_fnf = D('''
with open("memo.txt", "w", encoding="utf-8") as f:
    f.write("3\\n")
with open("memo.txt", "a", encoding="utf-8") as f:
    f.write("4\\n")
with open("memo.txt", encoding="utf-8") as f:
    nums = [int(x) for x in f]
with open("memo_backup.txt", encoding="utf-8") as f:
    old = f.read()
print(sum(nums), old)
''')
assert errline(_fnf) == 7 and err(_fnf) == 'FileNotFoundError'
_exc = D('''
price = {"A": 500, "B": 0}
order = ["A", "2", "B", "x", "C", "1"]
total = 0
for i in range(0, len(order), 2):
    name = order[i]
    cnt = int(order[i + 1])
    total += price[name] * cnt
print(total)
''')
assert errline(_exc) == 6 and err(_exc) == 'ValueError'
_exc2 = D('''
price = {"A": 500, "B": 0}
order = ["A", "2", "C", "x"]
total = 0
for i in range(0, len(order), 2):
    name = order[i]
    unit = price[name]
    cnt = int(order[i + 1])
    total += unit * cnt
print(total)
''')
assert errline(_exc2) == 6 and err(_exc2) == 'KeyError'
assert err('d = {"a": 1}\nprint(d["b"])') == 'KeyError'
assert err('print(int("3.5"))') == 'ValueError'
assert err('print(int("12a"))') == 'ValueError'
assert err('a = [1, 2]\nprint(a[2])') == 'IndexError'
assert err('print(10 / 0)') == 'ZeroDivisionError'
assert err('open("no_such_file_x.txt")') == 'FileNotFoundError'
assert err('a, b = "1 2 3".split()') == 'ValueError'
assert err('print("3" + 4)') == 'TypeError'
_es = 'price = {"A": 500, "B": 300}\nname, cnt = input().split()\nunit = price[name]\nn = int(cnt)\nprint(unit * n)'
assert err(_es, 'C x\n') == 'KeyError' and errline(_es, 'C x\n') == 3
assert err(_es, 'A 두개\n') == 'ValueError' and errline(_es, 'A 두개\n') == 4
assert run('with open("t.txt", "w") as f:\n    f.write("a")\nwith open("t.txt", "w") as f:\n    pass\nprint(len(open("t.txt").read()))') == '0'

D8 = lesson('8강. 파일·예외·모듈 종합 — 큰 배점 문제의 설계', 50,
'- 모드: `"r"` 읽기(없으면 FileNotFoundError) / `"w"` **여는 순간 비움** / `"a"` 끝에 덧붙임. "읽은 뒤 누적"은 **r 로 읽고 → 계산 → a 로 쓰기**\n- 경로의 `\\` 는 이스케이프 문자: `r"..."` 또는 `/` 를 쓴다. 인코딩은 **저장한 것과 같은 것**으로 읽는다\n- 파일 종합의 뼈대: 줄 → `strip().split()` → **list of list** → `sort(key=lambda …)` → f-string 으로 결과 파일 쓰기\n- `int("abc")` 는 **ValueError**, `d["없는 키"]` 는 **KeyError**. except 는 위에서부터 검사, `else` 는 예외가 없을 때만, `finally` 는 항상\n- 여러 값을 한 줄로 쓰기: `" ".join(map(str, nums))` — join 은 **문자열만** 이을 수 있다\n- 모듈: import 하면 그 파일이 전부 실행된다 → 테스트·메인 코드는 `if __name__ == "__main__":` 안에',
review('🔁 7강 복습', [T('데코레이터의 세 가지 규칙을 확인해요.'), rev('`@deco` 를 `def f` 위에 쓰는 것과 같은 대입문은?', code='f = deco(f)'), rev('deco 의 몸통과 wrapper 의 몸통은 각각 언제 실행될까요?', 'deco 의 몸통은 **정의할 때 한 번**, wrapper 의 몸통은 **호출할 때마다**'), rev('wrapper 에서 `func(*args)` 앞에 return 을 빠뜨리면?', '원래 함수의 결과가 버려지고 호출한 쪽은 **None** 을 받아요')]),
outq('복습 — 출력 결과는?', D('''
def mark(func):
    print("M", end=" ")
    def wrapper(*args):
        print(len(args), end=" ")
        func(*args)
    return wrapper
@mark
def add(a, b):
    return a + b
print("S", end=" ")
r = add(3, 4)
print(r)
'''), '"M" 은 정의할 때 한 번, 그다음 "S", 호출하면 wrapper 가 인자 개수 2 를 출력해요. wrapper 에 return 이 없어서 r 은 None 이에요.', review=True),
explain('모드 세 가지와 "읽은 뒤 누적"',
  [T('2025 2차 2번(14점)은 **파일을 읽어 계산하고, 그 결과를 같은 파일에 덧붙이는** 문제였어요. 모드를 잘못 고르면 그 순간 데이터가 사라져요. 세 모드의 차이를 정확히 구분해요.'),
   tabs(['"r" 읽기', '파일이 **없으면 FileNotFoundError**. 모드를 생략하면 "r" 이에요.', 'with open("score.txt", "r", encoding="utf-8") as f:\n    text = f.read()'], ['"w" 쓰기', '파일이 없으면 만들고, **있으면 여는 순간 내용을 모두 지워요**. write 를 한 번도 안 해도 지워져요.', 'with open("score.txt", "w", encoding="utf-8") as f:\n    f.write("90\\n")'], ['"a" 덧붙이기', '파일이 없으면 만들고, 있으면 **기존 내용 뒤에** 이어 써요.', 'with open("score.txt", "a", encoding="utf-8") as f:\n    f.write("85\\n")']),
   warn('`write` 는 `print` 와 달리 **줄바꿈을 붙여 주지 않아요**. `"\\n"` 을 직접 써야 하고, 숫자는 `str()` 이나 f-string 으로 문자열로 바꿔야 해요(`f.write(90)` 은 TypeError).')],
  [T('"읽은 뒤 누적"의 순서는 정해져 있어요. **① r 로 읽어 리스트에 담기 → ② 계산 → ③ a 로 열어 한 줄 덧붙이기.**'),
   C(D('''
with open("study.txt", "w", encoding="utf-8") as f:   # 준비: 기록 3줄
    f.write("40\\n55\\n25\\n")

with open("study.txt", "r", encoding="utf-8") as f:   # ① 읽기
    minutes = [int(line) for line in f]
total = sum(minutes)                                  # ② 계산
with open("study.txt", "a", encoding="utf-8") as f:   # ③ 덧붙이기
    f.write(f"합계 {total}\\n")

with open("study.txt", encoding="utf-8") as f:
    print(f.read())
'''), '③ 을 "w" 로 바꿔서 실행해 보세요 — 기록 3줄이 사라져요'),
   key('`int(line)` 은 줄 끝의 `"\\n"` 이 있어도 변환돼요(`int("40\\n")` → 40). 하지만 **문자열 비교나 딕셔너리 키**로 쓸 때는 반드시 `strip()` 을 먼저 해야 해요.')],
  [T('이 유형의 감점 포인트는 "**같은 파일을 w 로 먼저 열어 버리는 것**"이에요. 읽기도 전에 내용이 지워져서 합계가 0 이 되거나 오류가 나요.'),
   cmp('틀린 순서', 'f = open("study.txt", "w")\n# 이미 비어 있음!\ng = open("study.txt", "r")\ndata = g.readlines()   # []', '옳은 순서', 'with open("study.txt", "r") as f:\n    data = f.readlines()\nwith open("study.txt", "a") as f:\n    f.write("합계 ...\\n")', lb='"w" 는 여는 순간 비워요', rb='다 읽고 닫은 뒤에 "a" 로 다시 열어요', tones=('bad', 'good')),
   exam('서술형 틀: "**w 모드는 파일을 여는 순간 기존 내용을 모두 지운다.** 따라서 기존 기록이 사라진다. 기존 내용을 유지한 채 뒤에 추가하려면 **a 모드**로 열어야 한다."')]),
outq('[기출유사] 출력 결과는?', D('''
with open("log.txt", "w") as f:
    f.write("A\\n")
    f.write("B")
with open("log.txt", "a") as f:
    f.write("C\\n")
with open("log.txt", "a") as f:
    f.write("D\\n")
with open("log.txt") as f:
    lines = f.readlines()
print(len(lines), lines[0].strip(), lines[1].strip(), lines[-1] == "D")
with open("log.txt", "w") as f:
    pass
with open("log.txt") as f:
    print(len(f.read()))
'''), '"B" 뒤에 줄바꿈이 없어서 "BC" 가 한 줄이 돼요(총 3줄). 마지막 줄은 `"D\\n"` 이라 `"D"` 와 달라요. "w" 로 열기만 해도 내용이 지워져 길이는 0.'),
spot('[기출유사] `memo_backup.txt` 는 어디에서도 만든 적이 없는 파일이에요. **예외가 발생하는 줄**은?', _fnf, 7, '"w", "a" 는 없는 파일을 만들어 주지만 "r"(모드 생략)은 FileNotFoundError 예요. 5번 줄의 `memo.txt` 는 1번 줄에서 만들어졌으므로 정상이에요.'),
essay('[기출유사 · 서술 6점] 아래 코드는 `point.txt` 에 적힌 점수들의 합계를 구해 **파일 끝에 한 줄 추가**하려는 프로그램이에요. 실행하면 기존 점수가 모두 사라져요. **문제점**을 쓰고 올바르게 **수정**하세요.\n\n```\nwith open("point.txt", "r") as f:\n    nums = [int(x) for x in f]\nwith open("point.txt", "w") as f:\n    f.write("합계 " + str(sum(nums)))\n```', '세 번째 줄에서 파일을 "w" 모드로 열었기 때문이다. w 모드는 파일을 여는 순간 기존 내용을 모두 지우고 새로 쓰므로, 원래 있던 점수들이 사라지고 합계 한 줄만 남는다. 기존 내용을 유지한 채 끝에 덧붙이려면 "a" 모드로 열어야 한다. 즉 open("point.txt", "a") 로 고치고, 줄이 이어 붙지 않도록 f.write("합계 " + str(sum(nums)) + "\\n") 처럼 줄바꿈을 함께 쓴다.', ['"w" 모드로 연 것이 문제라고 짚었다', 'w 모드는 여는 순간 기존 내용을 지운다고 썼다', '"a" 모드로 수정했다', 'a 모드는 기존 내용 뒤에 이어 쓴다고(또는 줄바꿈 처리를) 썼다']),
explain('경로와 인코딩 — 한 줄짜리 함정',
  [T('윈도우 경로에는 `\\` 가 들어가요. 그런데 파이썬 문자열에서 `\\n` 은 줄바꿈, `\\t` 는 탭이에요. 그래서 경로를 그대로 쓰면 **다른 글자로 바뀌어요**.'),
   C(D('''
a = "C:\\new\\table.txt"
print(a)
print(len(a))
b = r"C:\\new\\table.txt"
print(b)
print(len(b))
'''), '\\n 과 \\t 가 글자 하나로 바뀌었어요'),
   key('해결은 세 가지예요. ① **raw 문자열** `r"C:\\new\\table.txt"` ② 역슬래시 두 번 `"C:\\\\new\\\\table.txt"` ③ **슬래시** `"C:/new/table.txt"`. 셋 다 같은 파일을 가리켜요.')],
  [T('`"data/score.txt"` 처럼 폴더 이름부터 쓰면 **상대 경로**(지금 실행하는 위치 기준), `"C:/..."` 처럼 처음부터 쓰면 **절대 경로**예요. 파일 이름만 쓰면 실행 위치에서 찾아요.'),
   flip(['"score.txt"', '실행 위치에 있는 score.txt (상대 경로)'], ['"data/score.txt"', '실행 위치의 data 폴더 안 (상대 경로)'], ['"../score.txt"', '실행 위치의 **한 단계 위** 폴더'], ['"C:/work/score.txt"', '드라이브부터 쓴 **절대 경로**']),
   tip('경로가 틀려서 파일을 못 찾으면 읽기 모드에서는 **FileNotFoundError** 예요. "파일은 분명히 있는데 오류가 난다" → 경로의 `\\` 부터 의심하세요.')],
  [T('한글이 든 파일은 **인코딩**도 맞아야 해요. 인코딩은 글자를 바이트로 바꾸는 규칙이고, 대표적으로 `utf-8` 과 `euc-kr`(cp949) 이 있어요. 2023 2차 11번(5점)이 이 내용이었어요.'),
   cmp('저장과 읽기가 다름', 'open("a.txt", "w", encoding="euc-kr")\n...\nopen("a.txt", "r", encoding="utf-8")', '저장과 읽기가 같음', 'open("a.txt", "w", encoding="utf-8")\n...\nopen("a.txt", "r", encoding="utf-8")', lb='한글을 읽다가 **UnicodeDecodeError** 가 나거나 글자가 깨져요', rb='쓸 때와 같은 인코딩으로 읽어요', tones=('bad', 'good')),
   exam('`encoding` 을 생략하면 **운영체제의 기본값**을 써요(컴퓨터마다 다를 수 있어요). 그래서 한글 파일은 `encoding="utf-8"` 을 **쓸 때도 읽을 때도** 명시하는 것이 안전해요. 영어·숫자만 있는 파일은 두 인코딩의 결과가 같아서 문제가 드러나지 않아요.')]),
outq('[기출유사] 출력 결과는?', D('''
a = "C:\\new\\table.txt"
b = r"C:\\new\\table.txt"
c = "C:\\\\new\\\\table.txt"
d = "C:/new/table.txt"
print(len(a), len(b), len(c), len(d), b == c, a == b)
'''), 'a 에서는 `\\n`, `\\t` 가 각각 글자 하나가 되어 2글자가 줄어요. raw 문자열 b 와 역슬래시를 두 번 쓴 c 는 같은 문자열이에요.'),
ch('[기출유사] 메모장에서 **EUC-KR** 로 저장한 한글 파일 `song.txt` 를 읽으려고 해요. 옳은 설명을 **모두** 고르세요.', ['`open("song.txt", encoding="euc-kr")` 로 읽어야 한다', '`open("song.txt", encoding="utf-8")` 로 읽으면 UnicodeDecodeError 가 날 수 있다', '인코딩이 달라도 한글은 항상 정상적으로 읽힌다', '파일 내용이 영어와 숫자뿐이라면 utf-8 로 읽어도 같은 결과가 나온다'], [1, 2, 4], '저장한 인코딩과 같은 인코딩으로 읽어야 해요. 영어·숫자는 두 인코딩에서 바이트가 같아서 차이가 드러나지 않아요.'),
explain('파일 → list of list → 정렬 → 결과 파일',
  [T('2025 2차 4번(14점)은 파일 문제의 종합판이었어요: **읽기 → list of list 로 만들기 → lambda 로 정렬 → 결과를 새 파일에 쓰기 → 없는 파일이면 FileNotFoundError 처리**. 단계마다 한 줄씩 정해진 코드가 있어요.'),
   steps(['① 줄을 조각으로', '`parts = line.strip().split()` — strip 으로 `\\n` 제거, split 으로 조각 내기'], ['② 숫자는 바로 변환해서 담기', '`rows.append([parts[0], int(parts[1]), int(parts[2])])` — 정렬·계산 전에 int 로'], ['③ 정렬 기준은 lambda', '`rows.sort(key=lambda r: (-r[1], r[0]))` — 1번 칸 내림차순, 같으면 이름 오름차순'], ['④ 결과는 f-string + "\\n"', '`f.write(f"{rank}등 {r[0]} {r[1]}\\n")`'])],
  [T('전체를 이어 보면 이래요. 점수를 **문자열인 채로 정렬하면** `"9" > "85"` 가 되어 순서가 틀려요. ② 에서 int 로 바꾸는 이유예요.'),
   C(D('''
with open("stage.txt", "w", encoding="utf-8") as f:
    f.write("하늘 85 9\\n바다 92 7\\n구름 85 10\\n노을 9 8\\n")

rows = []
with open("stage.txt", encoding="utf-8") as f:
    for line in f:
        name, judge, crowd = line.strip().split()
        rows.append([name, int(judge), int(crowd)])
rows.sort(key=lambda r: (-r[1], -r[2]))
with open("result.txt", "w", encoding="utf-8") as f:
    for rank, r in enumerate(rows, 1):
        f.write(f"{rank}등 {r[0]} {r[1]} {r[2]}\\n")
with open("result.txt", encoding="utf-8") as f:
    print(f.read())
'''), '심사 점수 내림차순, 같으면 관객 점수 내림차순'),
   key('`key=lambda r: (-r[1], -r[2])` 처럼 **튜플**을 돌려주면 앞 칸부터 차례로 비교해요. 숫자에 `-` 를 붙이면 내림차순, 문자열은 `-` 를 붙일 수 없으니 오름차순 기준으로만 써요.')],
  [T('여러 숫자를 **한 줄로** 쓰는 문제도 나왔어요(2024 2차 4번, 14점). 조건에 맞는 수를 고르는 방법 두 가지와, 숫자 리스트를 문자열 한 줄로 만드는 `join` 을 같이 물었어요.'),
   cmp('컴프리헨션', 'odd = [x for x in nums if x % 2 == 1]', 'filter + lambda', 'odd = list(filter(lambda x: x % 2 == 1, nums))', lb='조건이 뒤에 붙어요', rb='결과는 **list() 로 감싸야** 리스트', tones=('good', 'good')),
   C(D('''
nums = [7, 12, 33, 40, 5]
odd = list(filter(lambda x: x % 2 == 1, nums))
line = " ".join(map(str, odd))
with open("pick.txt", "w") as f:
    f.write(line + "\\n")
    f.write(",".join([str(x) for x in nums if x >= 10]) + "\\n")
with open("pick.txt") as f:
    print(f.read())
'''), 'join 은 문자열만 이을 수 있어요 → map(str, …)'),
   warn('`" ".join(odd)` 처럼 **정수 리스트를 그대로** join 하면 TypeError 예요. `map(str, odd)` 나 `[str(x) for x in odd]` 로 먼저 문자열로 바꿔요.')]),
outq('[기출유사] 출력 결과는?', D('''
with open("team.txt", "w", encoding="utf-8") as f:
    f.write("다온 7 120\\n가람 10 95\\n나래 7 130\\n라온 9 95\\n")
rows = []
with open("team.txt", encoding="utf-8") as f:
    for line in f:
        p = line.split()
        rows.append([p[0], int(p[1]), int(p[2])])
a = sorted(rows, key=lambda r: (-r[1], r[0]))
b = sorted(rows, key=lambda r: (r[2], r[0]))
print([r[0] for r in a])
print([r[0] for r in b])
print(max(rows, key=lambda r: r[1] * r[2])[0])
'''), 'a: 1번 칸 내림차순(10, 9, 7, 7), 7 이 같은 둘은 이름순(나래, 다온). b: 2번 칸 오름차순, 95 가 같은 둘은 이름순(가람, 라온). 마지막은 곱이 가장 큰 가람(950).'),
fill('[기출유사] 3의 배수만 골라 한 줄로 파일에 쓰는 코드를 완성하세요.', D('''
nums = [3, 8, 9, 14, 21]
pick = list(___(lambda x: x % 3 == 0, nums))
with open("out.txt", "w") as f:
    f.write("-".___(___(str, pick)))
with open("out.txt") as f:
    print(f.read())
'''), ['filter', 'join', 'map'], '고르기는 filter, 문자열로 바꾸기는 map(str, …), 한 줄로 잇기는 join 이에요.', expect='3-9-21'),
order('[기출유사] `score.txt`(한 줄에 `이름 점수`)를 읽어 **점수 내림차순**으로 `rank.txt` 에 쓰는 코드예요. 올바른 순서로 놓으세요.', ['rows = []', 'with open("score.txt", encoding="utf-8") as f:', '    for line in f:', '        name, s = line.strip().split()', '        rows.append([name, int(s)])', 'rows.sort(key=lambda r: -r[1])', 'with open("rank.txt", "w", encoding="utf-8") as f:', '    for r in rows:', '        f.write(f"{r[0]} {r[1]}\\n")'], '읽기(with) → 줄마다 조각 내어 담기 → **with 밖에서** 정렬 → 쓰기 순서예요.', code=False, mono=True),
explain('예외 흐름 설계 — 어느 줄에서, 어떤 예외가',
  [T('2025 2차 3번(12점) 환율 계산기는 **ValueError 와 KeyError 를 구분**해 처리하는 문제였어요. 두 예외가 나는 자리는 정해져 있어요.'),
   flip(['int("abc"), int("3.5"), float("x")', '**ValueError** — 형태가 숫자가 아님'], ['d["없는 키"]', '**KeyError** — 딕셔너리에 그 키가 없음'], ['a, b = "1 2 3".split()', '**ValueError** — 조각 수와 변수 수가 다름'], ['lst[10] (범위 밖)', '**IndexError**'], ['open("없는파일.txt")', '**FileNotFoundError**'], ['"3" + 4', '**TypeError** — 자료형이 맞지 않는 연산']),
   key('큰 문제에서는 "**어느 줄이 먼저 실패하는가**"가 답을 가려요. `int(...)` 가 먼저 있으면 ValueError 가, `d[...]` 가 먼저 있으면 KeyError 가 나요. 예외가 난 줄의 **나머지 줄은 실행되지 않고** except 로 건너뛰어요.')],
  [T('try 문의 네 칸이 실행되는 조건을 한 번에 정리해요.'),
   trace(D('''
rate = {"USD": 1400, "JPY": 9}
def change(text, code):
    try:
        won = int(text)
        r = rate[code]
    except ValueError:
        print("금액 오류")
    except KeyError:
        print("통화 오류")
    else:
        print(won // r, code)
    finally:
        print("--")
change("2800", "USD")
change("많이", "EUR")
change("900", "EUR")
'''), 'else 는 예외가 없을 때만, finally 는 항상'),
   steps(['try', '오류가 날 수 있는 코드. 예외가 나면 **그 줄에서 멈추고** 맞는 except 로'], ['except 이름', '위에서부터 검사해 **처음 맞는 하나만** 실행'], ['else', 'try 가 **예외 없이 끝났을 때만** 실행'], ['finally', '예외가 나든 안 나든 **항상** 마지막에 실행'])],
  [T('정상적인 값이지만 **규칙에 어긋나는 값**(음수 금액 등)은 파이썬이 오류로 여기지 않아요. 이럴 때는 `raise` 로 직접 예외를 일으켜 같은 except 에서 처리해요.'),
   C(D('''
def to_minutes(text):
    h, m = text.split(":")
    h, m = int(h), int(m)
    if not (0 <= h < 24 and 0 <= m < 60):
        raise ValueError("범위를 벗어난 시각")
    return h * 60 + m
for t in ["07:30", "25:00", "7시", "9:5:1"]:
    try:
        print(t, "->", to_minutes(t))
    except ValueError as e:
        print(t, "-> 오류:", e)
'''), 'as e 로 메시지를 받아 출력'),
   warn('except 는 **위에서부터** 검사해요. `except Exception:` 은 거의 모든 예외를 받으므로 **맨 위에 두면** 아래의 `except ValueError:`, `except KeyError:` 는 영영 실행되지 않아요. 구체적인 예외를 위에, 넓은 예외를 아래에 써요.')]),
outq('[기출유사] 출력 결과는?', D('''
menu = {"라면": 3000, "김밥": 2500}
def order(name, cnt):
    try:
        n = int(cnt)
        cost = menu[name] * n
    except ValueError:
        return "V"
    except KeyError:
        return "K"
    else:
        return cost
    finally:
        print("*", end="")
print(order("라면", "2"), order("우동", "1"), order("우동", "한개"), order("김밥", "0"))
'''), '세 번째 호출은 `int("한개")` 가 **먼저** 실패하므로 KeyError 가 아니라 ValueError("V")예요. finally 의 `*` 는 네 번의 호출마다(return 직전에) 출력되므로 `****` 가 먼저 찍혀요.'),
spot('[기출유사] **예외가 발생하는 줄**은? (반복의 몇 번째 바퀴인지도 생각해 보세요)', _exc, 6, '둘째 바퀴(i=2)에서 `int("x")` 가 ValueError 예요. `"C"` 는 price 에 없는 키지만, 그 바퀴(i=4)까지 가기 전에 프로그램이 멈춰요.'),
bucket('[기출유사] 각 코드가 일으키는 예외를 분류하세요. (`d = {"a": 1}`, `lst = [1, 2]`)', ['ValueError', 'KeyError', 'IndexError', 'TypeError'], [['int("12a")', 1], ['d["b"]', 2], ['lst[2]', 3], ['"3" + 4', 4], ['int("3.5")', 1], ['a, b = "1 2 3".split()', 1]], '`int("3.5")` 도 ValueError 예요(정수 형태가 아님). 언패킹 개수가 안 맞는 것도 ValueError.'),
essay('[기출유사 · 서술 6점] 아래 프로그램에 `C x` 를 입력했을 때 발생하는 **예외의 이름과 발생하는 줄, 이유**를 쓰고, 이어서 `A 두개` 를 입력했을 때는 어떻게 달라지는지 서술하세요.\n\n```\n1  price = {"A": 500, "B": 300}\n2  name, cnt = input().split()\n3  unit = price[name]\n4  n = int(cnt)\n5  print(unit * n)\n```', '"C x" 를 입력하면 3번 줄에서 KeyError 가 발생한다. 딕셔너리 price 에 "C" 라는 키가 없는데 price["C"] 로 값을 읽으려 했기 때문이다. 3번 줄에서 프로그램이 멈추므로 4번 줄의 int("x") 는 실행되지 않아 ValueError 는 발생하지 않는다. "A 두개" 를 입력하면 3번 줄은 "A" 가 있는 키라서 정상이고, 4번 줄에서 int("두개") 가 숫자 형태가 아닌 문자열을 정수로 바꾸려 했기 때문에 ValueError 가 발생한다.', ['"C x" → 3번 줄, KeyError 라고 썼다', '딕셔너리에 없는 키를 읽었기 때문이라고 이유를 썼다', '먼저 멈추므로 4번 줄(ValueError)은 실행되지 않는다고 썼다', '"A 두개" → 4번 줄, ValueError(숫자로 바꿀 수 없는 문자열)라고 썼다'], '실제로 실행해 보면 `C x` 는 KeyError, `A 두개` 는 ValueError 로 멈춰요. **먼저 실행되는 줄**의 예외만 발생해요.'),
explain('모듈 분리와 __name__ — 시계 각도',
  [T('2024 2차 7번(13점)은 시침·분침의 각도 계산 함수를 `clock.py` 에 두고 `main.py` 가 가져다 쓰는 문제였어요. 먼저 각도 공식부터 정리해요.'),
   steps(['분침', '1분에 6° (360 ÷ 60) → `m * 6`'], ['시침', '1시간에 30° (360 ÷ 12), 그리고 **1분에 0.5°** 씩 더 움직여요 → `(h % 12) * 30 + m * 0.5`'], ['두 바늘 사이의 각', '`d = abs(시침 - 분침)` 과 `360 - d` 중 **작은 쪽** → `min(d, 360 - d)`']),
   key('`h % 12` 는 12시를 0 으로 맞추기 위한 것이에요. 사이 각을 `abs` 로만 끝내면 9시 정각이 270° 가 되어 틀려요. **`min(d, 360 - d)`** 까지 써야 90° 예요.')],
  [T('파일을 나누면 이런 모양이에요. `main.py` 가 `import clock` 을 만나는 순간 `clock.py` 가 **위에서 아래로 전부 실행**돼요.'),
   CX(D('''
def hour_angle(h, m):
    return (h % 12) * 30 + m * 0.5

def minute_angle(m):
    return m * 6

def between(h, m):
    d = abs(hour_angle(h, m) - minute_angle(m))
    return min(d, 360 - d)

if __name__ == "__main__":
    print(between(3, 0))     # clock.py 를 직접 실행할 때만
'''), 'clock.py'),
   CX(D('''
import clock
from clock import between

print(clock.hour_angle(3, 30))
print(between(9, 0))
'''), 'main.py'),
   tip('`import clock` 이면 `clock.hour_angle(...)`, `from clock import between` 이면 `between(...)` 으로 불러요. **점 앞에 쓰는 이름**이 import 문에 적힌 이름과 같아야 해요.')],
  [T('`__name__` 은 파이썬이 파일마다 자동으로 만드는 변수예요. 값은 둘 중 하나예요.'),
   cmp('clock.py 를 직접 실행', '__name__ == "__main__"', 'main.py 가 import clock', 'clock 안에서 __name__ == "clock"', lb='가드 안의 테스트 코드가 **실행돼요**', rb='가드 안의 코드는 **건너뛰어요**. 함수 정의만 가져와요', tones=('good', 'good')),
   exam('서술 틀: "파일을 **직접 실행**하면 `__name__` 이 `"__main__"` 이고, **import** 되면 모듈 이름이 된다. 따라서 이 조건문 안의 코드는 직접 실행할 때만 실행되고, 다른 파일이 import 할 때는 실행되지 않아 테스트 출력이 섞이지 않는다."')]),
outq('[기출유사] 이 파일을 **직접 실행**했을 때의 출력은?', D('''
def hour_angle(h, m):
    return (h % 12) * 30 + m * 0.5
def minute_angle(m):
    return m * 6
def between(h, m):
    d = abs(hour_angle(h, m) - minute_angle(m))
    return min(d, 360 - d)
print(__name__ == "clock", end=" ")
if __name__ == "__main__":
    print(between(9, 0), between(12, 30), between(3, 15), hour_angle(15, 20))
'''), '9시 정각은 270° 가 아니라 작은 쪽 90.0°. 12시 30분: 시침 15°, 분침 180° → 165.0°. 3시 15분: 시침 97.5°, 분침 90° → 7.5°. 15시는 `% 12` 로 3시가 돼요.'),
ch('[기출유사] `tool.py` 의 내용이 아래와 같아요.\n\n```\nprint("T1")\ndef half(x):\n    return x / 2\nif __name__ == "__main__":\n    print("T2")\nprint("T3", __name__)\n```\n\n`main.py` 에 `import tool` 과 `print(tool.half(5))` 두 줄을 쓰고 **main.py 를 실행**하면 출력되는 것은?', ['2.5', 'T1 → 2.5', 'T1 → T3 tool → 2.5', 'T1 → T2 → T3 __main__ → 2.5'], 3, 'import 하는 순간 tool.py 가 전부 실행돼요. 가드 밖의 T1, T3 은 출력되고, 그때 tool 안의 `__name__` 은 `"tool"` 이라 T2 는 건너뛰어요.'),
essay('[기출유사 · 서술 5점] `clock.py` 의 맨 아래에 `print(between(3, 0))` 이라는 테스트 코드가 있어요. `main.py` 에서 `import clock` 을 하면 원하지 않는 `90.0` 이 출력돼요. 이를 막기 위해 `if __name__ == "__main__":` 을 쓰는데, 이 조건문의 **역할**을 `__name__` 의 값과 연결하여 서술하세요.', '__name__ 은 파이썬이 파일마다 자동으로 만드는 변수로, 그 파일을 직접 실행하면 "__main__" 이 되고 다른 파일에서 import 하면 모듈 이름("clock")이 된다. import 를 하면 모듈 파일의 코드가 전부 실행되므로 테스트 코드도 함께 실행되는데, 테스트 코드를 if __name__ == "__main__": 안에 넣으면 clock.py 를 직접 실행할 때만 조건이 참이 되어 실행되고, main.py 가 import 할 때는 조건이 거짓이라 실행되지 않는다.', ['직접 실행하면 __name__ 이 "__main__" 이라고 썼다', 'import 되면 __name__ 이 모듈 이름이 된다고 썼다', 'import 하면 모듈의 코드가 전부 실행된다는 점을 썼다', '조건문 안의 코드는 직접 실행할 때만 실행된다고 썼다']),
prac('[기출유사] 동아리 발표회 심사 결과', '발표회 심사 기록을 파일로 저장하고, 다시 읽어 순위표를 만들어요.\n\n입력: 첫 줄 `n`, 이어서 n 줄에 `팀이름 심사점수 관객점수` (팀이름은 공백 없음, 점수는 0 이상의 정수). 마지막 줄에 **읽을 파일 이름**.\n\n1. n 줄을 받은 그대로 `show.txt` 에 저장해요.\n2. 마지막 줄의 파일 이름으로 파일을 열어 읽어요. 그 파일이 없으면 `파일이 없습니다: 파일이름` 을 출력하고 끝내요.\n3. 각 줄을 `[팀이름, 심사점수, 관객점수, 총점]` 으로 만들어 리스트에 담아요. 총점 = 심사점수 × 2 + 관객점수.\n4. **총점 내림차순**, 같으면 **심사점수 내림차순**, 그것도 같으면 **팀이름 오름차순**으로 정렬해요.\n5. `award.txt` 에 `1등 팀이름 총점` 형식으로 한 줄씩 저장한 뒤, **award.txt 를 다시 읽어** 내용을 그대로 출력하고, 마지막 줄에 `평균 총점: A` (소수 첫째 자리)를 출력해요.\n\n[조건] ○ 정렬은 `sort` 또는 `sorted` 에 **lambda** 를 key 로 준다 ○ 없는 파일은 **try-except FileNotFoundError** 로 처리한다 ○ 점수는 리스트에 담을 때 int 로 바꾼다',
D('''
n = int(input())
with open("show.txt", "w", encoding="utf-8") as f:
    for _ in range(n):
        f.write(input() + "\\n")
fname = input().strip()
try:
    rows = []
    with open(fname, encoding="utf-8") as f:
        for line in f:
            name, a, b = line.strip().split()
            a, b = int(a), int(b)
            rows.append([name, a, b, a * 2 + b])
except FileNotFoundError:
    print("파일이 없습니다:", fname)
else:
    rows.sort(key=lambda r: (-r[3], -r[1], r[0]))
    with open("award.txt", "w", encoding="utf-8") as f:
        for rank, r in enumerate(rows, 1):
            f.write(f"{rank}등 {r[0]} {r[3]}\\n")
    with open("award.txt", encoding="utf-8") as f:
        print(f.read().rstrip())
    avg = sum(r[3] for r in rows) / len(rows)
    print(f"평균 총점: {avg:.1f}")
'''), ['4\n코딩반 40 15\n로봇반 38 19\n수학반 40 15\n천문반 30 9\nshow.txt', '2\n가 10 5\n나 9 9\nshow_old.txt', '1\n혼자팀 0 0\nshow.txt', '3\n다 10 10\n나 5 20\n가 10 10\nshow.txt', '5\nE 9 100\nD 50 18\nC 49 20\nB 59 0\nA 10 98\nshow.txt', '3\n하나 7 3\n둘 8 1\n셋 6 5\nSHOW.TXT.bak'],
  hints=['`show.txt` 를 "w" 로 쓴 뒤, `try:` 안에서 `open(fname, encoding="utf-8")` 으로 읽어요.', '`rows.append([name, a, b, a * 2 + b])` 로 담고 `rows.sort(key=lambda r: (-r[3], -r[1], r[0]))`.', '쓰기: `for rank, r in enumerate(rows, 1): f.write(f"{rank}등 {r[0]} {r[3]}\\n")`. 평균은 `f"{avg:.1f}"`.'],
  ex='정렬 기준이 세 개일 때는 lambda 가 **튜플**을 돌려주면 돼요. 숫자 내림차순은 `-`, 이름 오름차순은 그대로.'),
prac('[기출유사] 해외 직구 환전 계산기', '원화를 외화로 바꿔 주는 계산기예요. 환율표는 아래와 같아요(외화 1단위의 원화 가격).\n\n`USD` 1400 · `EUR` 1500 · `JPY` 9 · `CNY` 190\n\n입력: 첫 줄 `n`, 이어서 n 줄에 `금액 통화코드` (예: `28000 USD`).\n\n줄마다 이 순서로 처리해요.\n1. 금액을 **정수로 변환**해요. 변환할 수 없으면 `금액 오류: 정수가 아닙니다`\n2. 금액이 0 이하이면 `금액 오류: 양수가 아닙니다`\n3. 통화코드를 **대문자로 바꿔** 환율표에서 찾아요. 없으면 `통화 오류: 코드` (코드는 대문자로 바꾼 것)\n4. 모두 정상이면 `금액원 = 결과 코드` (결과 = 금액 ÷ 환율, 소수 둘째 자리)\n5. 정상이든 오류든 줄마다 마지막에 `- k번 처리 끝` 을 출력해요.\n\n마지막 줄에 `성공 K건` 을 출력해요.\n\n[조건] ○ 줄마다 **try-except-else-finally** 를 쓴다 ○ 정수 변환 실패는 `int()` 가 내는 **ValueError** 로, 없는 통화는 **KeyError** 로 각각의 except 에서 처리한다(`in`·`isdigit` 으로 미리 검사하지 않는다) ○ 0 이하 금액은 `raise ValueError("양수가 아닙니다")` 로 알리고, except 에서 `as e` 로 받은 메시지를 출력한다 ○ 정상 출력과 성공 횟수 증가는 **else**, 처리 끝 안내는 **finally** 에서 한다',
D('''
rate = {"USD": 1400, "EUR": 1500, "JPY": 9, "CNY": 190}
n = int(input())
ok = 0
for k in range(1, n + 1):
    money, code = input().split()
    code = code.upper()
    try:
        try:
            won = int(money)
        except ValueError:
            raise ValueError("정수가 아닙니다")
        if won <= 0:
            raise ValueError("양수가 아닙니다")
        r = rate[code]
    except ValueError as e:
        print("금액 오류:", e)
    except KeyError:
        print("통화 오류:", code)
    else:
        print(f"{won}원 = {won / r:.2f} {code}")
        ok += 1
    finally:
        print(f"- {k}번 처리 끝")
print(f"성공 {ok}건")
'''), ['4\n28000 USD\n만원 EUR\n5000 KRW\n900 jpy', '3\n-500 USD\n0 XYZ\n1500 eur', '1\n1 JPY', '5\n3.5 USD\n100000 cny\nabc abc\n7000 Usd\n19 CNY', '2\n10000 won\n10000 EUR', '3\n1400 USD\n1500 EUR\n190 CNY'],
  hints=['줄마다 try 를 새로 시작해요. try 안의 순서는 **금액 변환 → 양수 검사 → `rate[code]`** — 이 순서가 곧 검사 순서예요.', '`int(money)` 가 내는 ValueError 의 메시지는 영어예요. `int(money)` 만 작은 try 로 감싸 `except ValueError: raise ValueError("정수가 아닙니다")` 로 메시지를 바꿔 다시 던지면 바깥 except 하나로 두 경우를 처리할 수 있어요.', '`except ValueError as e: print("금액 오류:", e)` / `except KeyError: print("통화 오류:", code)` / `else:` 에서 `f"{won}원 = {won / r:.2f} {code}"` / `finally:` 에서 `f"- {k}번 처리 끝"`.'],
  ex='`0 XYZ` 는 금액 검사가 **먼저** 실패하므로 "통화 오류"가 아니라 "금액 오류: 양수가 아닙니다" 가 출력돼요. finally 는 어떤 경우에도 마지막에 실행돼요.'),
prac('[기출유사] 행운 번호 기록지', '추첨기가 뽑은 번호들을 정리해 파일에 기록해요. (난수 대신 입력으로 번호를 받아요)\n\n입력: 첫 줄 `n`, 이어서 n 줄에 회차별 번호(1~45 의 정수 여러 개, 공백 구분).\n\n회차마다 아래 세 줄을 `lucky.txt` 에 **차례로 이어서** 기록해요.\n- `k회: ` + 번호를 **오름차순**으로 정렬해 공백으로 이은 것\n- `홀수: ` + 홀수 번호를 오름차순으로, 쉼표(`,`)로 이은 것 (없으면 `없음`)\n- `30이상: ` + 30 이상인 번호를 오름차순으로, 쉼표로 이은 것 (없으면 `없음`)\n\n모든 회차를 기록한 뒤 `lucky.txt` 를 다시 읽어 내용을 그대로 출력하고, 마지막 줄에 `기록 L줄` 을 출력해요.\n\n[조건] ○ 홀수는 **리스트 컴프리헨션**, 30 이상은 **filter + lambda** 로 고른다 ○ 숫자를 문자열로 바꿀 때 `map(str, …)` 과 `join` 을 쓴다 ○ 1회차는 `"w"`, 2회차부터는 `"a"` 모드로 연다(회차마다 파일을 따로 열어요)',
D('''
n = int(input())
for k in range(1, n + 1):
    nums = sorted(map(int, input().split()))
    odd = [x for x in nums if x % 2 == 1]
    big = list(filter(lambda x: x >= 30, nums))
    mode = "w" if k == 1 else "a"
    with open("lucky.txt", mode, encoding="utf-8") as f:
        f.write(f"{k}회: " + " ".join(map(str, nums)) + "\\n")
        f.write("홀수: " + (",".join(map(str, odd)) if odd else "없음") + "\\n")
        f.write("30이상: " + (",".join(map(str, big)) if big else "없음") + "\\n")
with open("lucky.txt", encoding="utf-8") as f:
    lines = f.readlines()
for line in lines:
    print(line.rstrip())
print(f"기록 {len(lines)}줄")
'''), ['2\n17 3 42 30 8 25\n2 4 6 8 10 12', '1\n45', '3\n31 33 35\n1 2 3\n44 40 36 32', '1\n9 7 5 3 1 29', '2\n30 29\n10 20', '4\n5\n30\n45 1\n22 14'],
  hints=['`nums = sorted(map(int, input().split()))` 로 먼저 정렬해 두면 고른 결과도 오름차순이에요.', '`odd = [x for x in nums if x % 2 == 1]`, `big = list(filter(lambda x: x >= 30, nums))`', '`",".join(map(str, odd)) if odd else "없음"` — 모드는 `"w" if k == 1 else "a"`.'],
  ex='매 회차를 "w" 로 열면 마지막 회차만 남아요. 처음 한 번만 "w"(새 기록지), 그 뒤로는 "a"(이어 쓰기)예요.'),
prac('[심화] 시계 각도 모듈과 기록 누적', '`clock` 모듈에 들어갈 함수들을 만들고, **메인 코드는 `if __name__ == "__main__":` 안**에 작성해요.\n\n함수\n- `parse(text)` : `"시:분"` 문자열을 `(h, m)` 정수 튜플로 return. `:` 로 나눈 조각이 2개가 아니거나 정수가 아니면 **ValueError** 가 나도록 하고, 0 ≤ h ≤ 23, 0 ≤ m ≤ 59 를 벗어나면 `raise ValueError`\n- `hour_angle(h, m)` : 시침 각도 `(h % 12) * 30 + m * 0.5`\n- `minute_angle(m)` : 분침 각도 `m * 6`\n- `between(h, m)` : 두 바늘 사이의 **작은 각**\n\n메인\n1. 첫 줄 `n`, 이어서 n 줄에 시각 문자열을 받아요.\n2. 시각마다 `parse` 를 호출해요. ValueError 면 `시각 오류: 입력한글자` 를 출력하고 다음으로 넘어가요.\n3. 정상이면 `HH:MM 사이각 A도` (시·분은 두 자리, 각은 소수 첫째 자리)를 출력하고, 같은 줄을 `angle.txt` 에 **덧붙여요**.\n4. 모두 끝나면 `angle.txt` 를 읽어 **사이각이 가장 큰 줄**을 `최대: 그 줄` 로 출력해요(같으면 먼저 기록된 줄). 정상 시각이 하나도 없으면 `기록 없음`.\n\n[조건] ○ 함수 안에서 input·print 를 쓰지 않는다 ○ 프로그램을 시작할 때 `angle.txt` 를 `"w"` 로 한 번 열어 비우고, 기록은 `"a"` 로 덧붙인다 ○ 최대 줄은 **파일을 다시 읽어서** 구한다',
D('''
def parse(text):
    h, m = text.split(":")
    h, m = int(h), int(m)
    if not (0 <= h <= 23 and 0 <= m <= 59):
        raise ValueError("범위")
    return h, m
def hour_angle(h, m):
    return (h % 12) * 30 + m * 0.5
def minute_angle(m):
    return m * 6
def between(h, m):
    d = abs(hour_angle(h, m) - minute_angle(m))
    return min(d, 360 - d)
if __name__ == "__main__":
    with open("angle.txt", "w", encoding="utf-8") as f:
        pass
    n = int(input())
    for _ in range(n):
        text = input().strip()
        try:
            h, m = parse(text)
        except ValueError:
            print("시각 오류:", text)
        else:
            line = f"{h:02d}:{m:02d} 사이각 {between(h, m):.1f}도"
            print(line)
            with open("angle.txt", "a", encoding="utf-8") as f:
                f.write(line + "\\n")
    best = None
    with open("angle.txt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            a = float(line.split()[2][:-1])
            if best is None or a > best[0]:
                best = (a, line)
    if best is None:
        print("기록 없음")
    else:
        print("최대:", best[1])
'''), ['4\n3:00\n9:00\n12:30\n25:10', '2\n7시\n1:2:3', '3\n6:00\n18:00\n0:0', '5\n3:15\n15:15\n23:59\n10:60\n-1:30', '1\n12:00', '4\n2:20\n4:40\n8:20\nab:cd'],
  starter=D('''
def parse(text):
    pass

def hour_angle(h, m):
    pass

def minute_angle(m):
    pass

def between(h, m):
    pass

if __name__ == "__main__":
    n = int(input())
    # 이어서 작성
'''),
  hints=['`parse`: `h, m = text.split(":")` (조각이 2개가 아니면 여기서 ValueError) → `int` 변환 → 범위 검사 후 `raise ValueError`.', '`between`: `d = abs(hour_angle(h, m) - minute_angle(m))`, `return min(d, 360 - d)`. 출력은 `f"{h:02d}:{m:02d} 사이각 {between(h, m):.1f}도"`.', '최대 줄: 파일을 줄마다 읽어 `float(line.split()[2][:-1])` 로 각을 꺼내고, **더 클 때만**(`>`) 갱신하면 같은 값은 먼저 기록된 줄이 남아요.'],
  ex='`6:00` 과 `18:00` 은 둘 다 180.0도예요. `>` 로만 갱신하므로 먼저 기록된 `06:00` 이 최대로 남아요. 함수 정의는 가드 밖, 입력·출력은 가드 안에 두는 것이 모듈 설계의 기본이에요.'),
)
