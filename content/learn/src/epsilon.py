import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lotc import *

C = Course('ε', '2학년 1학기 1차고사(인공지능프로그래밍) 범위: 그래프·트리 표현(인접 행렬·인접 리스트), '
           'DFS(재귀·스택), BFS(큐·deque)와 최단 거리·촌수 계산, 상태공간과 8-퍼즐, 휴리스틱(제자리 아닌 타일 수·맨해튼 거리)과 Best-First 탐색, '
           'pandas 탐색(shape·describe·value_counts·조건 필터), 결측치(isna·fillna·dropna)와 원-핫 인코딩(get_dummies), '
           'matplotlib·seaborn 시각화 종류와 용도(상자 그림·상관계수 heatmap), train_test_split, '
           'StandardScaler·MinMaxScaler·RobustScaler 공식과 fit/transform, 선형회귀 가설 y = wx + b, MSE 손실, 경사하강법, 정규방정식, R²')

# 그래프 예제 (여러 레슨에서 사용)
G_SRC = 'graph = {1: [2, 3], 2: [1, 4, 5], 3: [1, 6], 4: [2], 5: [2, 6], 6: [3, 5]}'

DF_SRC = '''import pandas as pd
df = pd.DataFrame({
    'name':  ['지우', '민준', '서연', '하준', '유나', '도윤'],
    'grade': [1, 2, 2, 1, 2, 1],
    'hours': [2, 5, 3, 1, 4, 3],
    'score': [70, 92, 81, 60, 88, 75],
    'club':  ['로봇', '코딩', '코딩', '로봇', 'AI', '코딩'],
})'''

# =====================================================================
L = C.lesson('ε-01 시작하기: 인공지능프로그래밍 1차 지도 + 1학년 점검', 20,
'''- 이 과목 시험은 **서술형**이에요: 코랩 코드 **빈칸** + 개념·**수식** 서술.
- 1차 범위(이 코스의 가정): **탐색**(그래프·DFS·BFS·휴리스틱) → **데이터 다루기**(pandas·시각화) → **전처리**(분할·스케일링) → **선형회귀**.
- 1학년 도구가 그대로 쓰여요: 딕셔너리(그래프), 리스트(스택·큐), 함수(재귀 DFS), numpy(배열 연산).
- 코드는 손으로 따라가고, 개념은 "**왜?**" 까지 한두 문장으로 쓰는 연습을 해요.''')

L.explain('이 과목 시험은 이렇게 나와요',
    [T('2학년 1학기 **인공지능프로그래밍** 기출(2024~2026)은 모두 **서술형**이에요.\n'
       '수업 시간에 코랩(Colab)에서 돌려 본 코드가 그대로 시험지에 나오고, 군데군데가 빈칸이에요.\n'
       '문항 모양은 크게 세 가지로 생각하면 돼요.'),
     STEPS(('코드 빈칸 채우기', '탐색 코드(DFS·BFS), EDA 코드(pandas·seaborn), 모델 코드(sklearn)의 ㉠㉡ 빈칸. 함수 이름·인자·메서드가 단골이에요.'),
           ('과정·결과 쓰기', 'DFS/BFS 방문 순서, 큐·스택의 변화, 맨해튼 거리, MSE 같은 계산 결과를 써요.'),
           ('개념·수식 서술', '"BFS 가 최단 경로를 보장하는 이유", "표준화 공식", "MSE 를 제곱하는 이유" 처럼 문장과 식으로 써요.'))],
    [T('기출 분석이 앞쪽 문항 위주라 **1차/2차 범위 경계가 확실하지 않아요**.\n'
       '이 코스는 아래 네 덩어리를 1차 범위로 보고 만들었어요.\n'
       '(로지스틱 회귀·분류 평가·교차검증·여러 분류 모델은 2차 코스에서 다뤄요.)'),
     FLIP(['탐색 알고리즘', '그래프·트리 표현, DFS(스택/재귀), BFS(큐), 촌수 계산, 8-퍼즐, 휴리스틱'],
          ['데이터 다루기', 'pandas describe·isna·value_counts·fillna·get_dummies, seaborn·matplotlib 그래프'],
          ['전처리', 'train_test_split, StandardScaler·MinMaxScaler·RobustScaler'],
          ['선형회귀', '가설 y = wx + b, MSE, 경사하강법, 정규방정식, R²']),
     WARN('정확한 시험 범위는 **선생님 공지**가 기준이에요. 공지와 다르면 공지를 따르세요.')],
    [T('이 사이트의 ▶ 실행은 브라우저 안 파이썬이라 **pandas·sklearn·numpy 가 없어요**.\n'
       '그래서 그런 코드는 **읽기 전용**으로 보여 주고(결과는 미리 실행해 확인한 값), \n'
       '실습은 같은 계산을 **순수 파이썬(리스트·딕셔너리)** 으로 직접 짜요.'),
     TIP('공식을 직접 코드로 짜 보면 서술형에서 식을 쓸 때 훨씬 덜 헷갈려요. "StandardScaler 가 하는 일" 을 리스트로 계산해 본 학생은 식을 잊지 않아요.')])

L.choice('이 과목 시험 문항 모양으로 **가장 알맞은** 설명은?',
    ['객관식 25문항 OMR', '코랩 코드의 빈칸 채우기 + 개념·수식 서술', '컴퓨터로 직접 코드를 실행하는 실기만', '영어 독해 문항'], 2,
    '기출은 모두 서술형이고, 코랩에서 쓰던 코드의 빈칸과 개념·수식 서술이 중심이에요.')

L.explain('1학년 점검 ① 딕셔너리 — 그래프의 재료',
    [T('딕셔너리는 **키 → 값** 짝을 저장해요.\n'
       '탐색 단원에서는 `{노드: [이웃 노드 리스트]}` 모양으로 **그래프**를 저장해요.\n'
       '`for k in d:` 는 **키**를 하나씩 꺼내고, `d[k]` 로 값을 봐요.'),
     CODE(G_SRC + '\nprint(graph[2])\nprint(len(graph))\nfor v in graph:\n    print(v, "의 이웃 수:", len(graph[v]))', '그래프 딕셔너리')],
    [T('없는 키를 `d[k]` 로 읽으면 **KeyError** 예요.\n'
       '`d.get(k, 기본값)` 은 없을 때 기본값을 돌려줘요. `k in d` 로 미리 검사해도 돼요.'),
     CMP(side('d[k]', '없으면 KeyError', 'd = {"A": 1}\nprint(d["B"])', 'bad', expect_error=True),
         side('d.get(k, 0)', '없으면 기본값', 'd = {"A": 1}\nprint(d.get("B", 0))', 'good'))])

L.output('출력 결과를 그대로 쓰세요.', '''\
graph = {"A": ["B", "C"], "B": ["A"], "C": ["A", "D"], "D": ["C"]}
print(graph["C"])
print(len(graph["A"]) + len(graph["D"]))
print(graph.get("E", []))''',
    '`graph["C"]` 는 리스트 그대로, A 의 이웃 2개 + D 의 이웃 1개 = 3, 없는 키 E 는 `get` 의 기본값 `[]`.\n\n```\n{out}\n```')

L.explain('1학년 점검 ② 리스트 — 스택과 큐의 재료',
    [T('리스트 끝에 넣고 끝에서 빼면 **스택**(나중에 넣은 것이 먼저 나옴, LIFO)이에요.\n'
       '끝에 넣고 **앞에서** 빼면 **큐**(먼저 넣은 것이 먼저 나옴, FIFO)예요.\n'
       '`pop()` 은 맨 뒤, `pop(0)` 은 맨 앞을 꺼내요.'),
     TABS(('스택 (DFS)', 'append + pop()', 's = []\ns.append(1)\ns.append(2)\ns.append(3)\nprint(s.pop())\nprint(s)'),
          ('큐 (BFS)', 'append + pop(0)', 'q = []\nq.append(1)\nq.append(2)\nq.append(3)\nprint(q.pop(0))\nprint(q)'))],
    [T('`x in 리스트` 는 들어 있는지 True/False 로 알려 줘요. 탐색에서 **방문했는지** 확인할 때 써요.'),
     KEY('스택 = 접시 쌓기(위에서 꺼냄), 큐 = 매점 줄서기(앞에서 꺼냄). DFS 는 스택, BFS 는 큐!')])

L.output('출력은?', '''\
data = [5, 7]
data.append(9)
a = data.pop()
b = data.pop(0)
print(a, b, data)''',
    '`pop()` 은 맨 뒤 9, `pop(0)` 은 맨 앞 5 를 꺼내요. 남은 건 7 하나.\n\n```\n{out}\n```')

L.bucket('설명을 스택 / 큐로 분류하세요.', ['스택 (LIFO)', '큐 (FIFO)'],
    [['나중에 넣은 것이 먼저 나온다', 1], ['먼저 넣은 것이 먼저 나온다', 2], ['append + pop()', 1], ['append + pop(0)', 2],
     ['접시 쌓기', 1], ['매점 줄서기', 2]],
    '스택은 위(끝)에서 넣고 빼고, 큐는 뒤로 넣고 앞에서 빼요. 다음 레슨들의 DFS(스택)·BFS(큐)로 바로 이어져요.')

L.explain('1학년 점검 ③ 함수',
    [T('`def` 로 함수를 만들고 `return` 으로 결과를 **돌려줘요**.\n'
       'return 이 없으면 함수는 `None` 을 돌려줘요.\n'
       '평균·MSE 같은 계산을 함수로 만들어 두면 계속 재사용할 수 있어요.'),
     CODE('def mean(nums):\n    return sum(nums) / len(nums)\n\nprint(mean([2, 4, 9]))\nprint(mean([10, 20]))', '평균 함수')],
    [T('함수 안에서 **자기 자신을 다시 부르는** 함수가 재귀 함수예요. DFS 를 재귀로 짤 때 써요.\n'
       '재귀에는 반드시 **멈추는 조건**이 있어야 해요.'),
     WARN('`print` 는 화면에 보여 줄 뿐 값을 돌려주지 않아요. 결과를 다른 계산에 쓰려면 꼭 `return` 하세요.')])

L.spot('리스트의 합을 돌려주는 함수를 만들었는데 마지막 줄이 `None` 을 출력해요. **고쳐야 할 줄**은?', '''\
def total(nums):
    s = 0
    for x in nums:
        s += x
    print(s)

print(total([1, 2, 3]))''', 5,
    '5번 줄이 값을 **출력만** 하고 돌려주지 않아서 함수의 반환값이 None 이에요. `return s` 로 고쳐야 해요.')

L.explain('1학년 점검 ④ numpy 배열 연산',
    [T('numpy 배열은 **원소끼리(element-wise)** 계산해요. 반복문 없이 한 번에 더하고 곱해요.\n'
       '같은 기호라도 **리스트**와 **배열**의 뜻이 달라요.'),
     CMP(side('리스트', '`+` 는 이어 붙이기, `* 2` 는 두 번 반복', 'a = [1, 2, 3]\nprint(a + [10, 20, 30])\nprint(a * 2)'),
         side('numpy 배열', '`+`·`*` 는 원소끼리 계산', 'import numpy as np\na = np.array([1, 2, 3])\nprint(a + np.array([10, 20, 30]))\nprint(a * 2)', 'good'))],
    [T('2차원 배열은 `shape` 으로 (행, 열) 크기를 봐요.\n'
       '`sum(axis=0)` 은 **세로(열마다)**, `sum(axis=1)` 은 **가로(행마다)** 로 더해요.'),
     CODE('import numpy as np\nm = np.array([[1, 2, 3],\n              [4, 5, 6]])\nprint(m.shape)\nprint(m.sum(axis=0))\nprint(m.sum(axis=1))\nprint(m.mean())',
          'shape 와 axis (읽기 전용)', run_=False),
     KEY('axis=0 → 행 방향으로 쭉 내려가며 **열마다** 계산, axis=1 → **행마다** 계산. 결과 길이가 열 수(3) 인지 행 수(2) 인지로 확인해요.')])

L.output('numpy 코드의 출력은? (이 사이트에서는 실행되지 않으니 손으로 예측해요)', '''\
import numpy as np
a = np.array([[2, 4], [6, 8], [1, 3]])
print(a.shape)
print(a.sum(axis=0))
print(a.max())''',
    '행 3개·열 2개라 (3, 2). 열마다 더하면 2+6+1=9, 4+8+3=15. 전체 최댓값 8. (numpy 는 자릿수를 맞추느라 `[ 9 15]` 처럼 앞에 공백을 넣어 출력해요.)\n\n```\n{out}\n```',
    alts=['(3, 2)\n[9 15]\n8'])

L.match('코드와 결과를 이어 보세요.',
    [['[1, 2] + [3, 4]', '[1, 2, 3, 4]'], ['np.array([1, 2]) + np.array([3, 4])', '[4 6]'],
     ['[1, 2] * 2', '[1, 2, 1, 2]'], ['np.array([1, 2]) * 2', '[2 4]']],
    '리스트는 이어 붙이고 반복하고, numpy 배열은 원소끼리 계산해요. 배열은 출력할 때 쉼표 없이 `[4 6]` 처럼 보여요.')

L.practice('[기출유사] numpy 없이 벡터 연산',
'''numpy 의 원소별 연산을 **리스트와 반복문으로 직접** 구현해요. 같은 길이의 정수 두 줄이 주어져요.

**[조건]**
- 첫째 줄: 원소끼리 더한 값 (공백으로 구분)
- 둘째 줄: 원소끼리 곱한 값 (공백으로 구분)
- 셋째 줄: 내적 — 원소끼리 곱한 값을 모두 더한 수
- `zip()` 또는 인덱스 반복을 사용하세요.

{ex}

{ex2}''',
'''a = list(map(int, input().split()))
b = list(map(int, input().split()))
# 원소별 합, 원소별 곱, 내적을 출력하세요
''',
'''a = list(map(int, input().split()))
b = list(map(int, input().split()))
add = [x + y for x, y in zip(a, b)]   # 원소별 합 (np: a + b)
mul = [x * y for x, y in zip(a, b)]   # 원소별 곱 (np: a * b)
print(*add)
print(*mul)
print(sum(mul))                       # 내적 (np: a @ b)''',
    ['1 2 3\n4 5 6', '2 -1\n3 7'], ['5\n5', '0 0 0\n1 2 3', '-2 3 -4 5\n1 1 1 1'],
    ['`zip(a, b)` 는 같은 위치의 원소를 짝지어 줘요.', '`[x + y for x, y in zip(a, b)]` 처럼 컴프리헨션으로 한 줄에 만들 수 있어요.',
     '내적은 원소별 곱 리스트의 `sum()` 이에요. `print(*리스트)` 는 공백으로 띄워 출력해요.'],
    'numpy 로는 `a + b`, `a * b`, `a @ b`(또는 `np.dot(a, b)`) 한 줄씩이에요. 리스트로 직접 짜 보면 numpy 가 "원소끼리" 계산한다는 뜻이 분명해져요.')

L.essay('`[1, 2, 3] + [1, 2, 3]` 과 `np.array([1, 2, 3]) + np.array([1, 2, 3])` 의 결과가 어떻게 다른지, **이유와 함께** 서술하세요.',
    '리스트의 + 는 두 리스트를 이어 붙여 [1, 2, 3, 1, 2, 3] 이 되고, numpy 배열의 + 는 같은 위치의 원소끼리 더해 [2 4 6] 이 된다. 같은 + 기호라도 자료형(list 와 ndarray)마다 연산의 정의가 다르기 때문이다.',
    ['리스트는 이어 붙인다 [1, 2, 3, 1, 2, 3]', '배열은 원소끼리 더한다 [2 4 6]', '자료형마다 + 의 의미가 다르다'])

# =====================================================================
L = C.lesson('ε-02 그래프와 트리를 코드로 표현하기', 20,
'''- 그래프 = **노드(정점)** + **간선**. 방향이 없으면 무방향 그래프.
- **인접 행렬**: n×n 2차원 리스트, 연결되면 1. 무방향이면 **대칭**.
- **인접 리스트**: `{노드: [이웃들]}` 딕셔너리. 무방향이면 **양쪽에** 추가.
- **트리**: 사이클 없는 연결 그래프. 루트·부모·자식·리프·깊이. 노드 n개 → 간선 **n-1개**.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간에는 시험 모양과 1학년 도구(딕셔너리·스택/큐·함수·numpy)를 점검했어요.\n'
       '오늘은 딕셔너리로 **그래프**를 저장하는 법을 배워요.'),
     REVEAL_RUN('`s = [1, 2, 3]` 에서 `s.pop()` 과 `s.pop(0)` 을 차례로 하면 꺼낸 값은?',
                's = [1, 2, 3]\nprint(s.pop(), s.pop(0))', '스택은 뒤에서, 큐는 앞에서 꺼내요.')])
L.output('복습: 출력은?', 'q = ["가", "나"]\nq.append("다")\nq.pop(0)\nprint(q)',
    '큐처럼 앞에서 "가" 를 뺐어요. → {out}', review=True)

L.explain('그래프의 말들',
    [T('**그래프**는 대상(노드)과 대상 사이의 관계(간선)를 나타내는 구조예요.\n'
       '지하철 노선, 친구 관계, 퍼즐의 상태 변화가 모두 그래프예요.\n'
       '간선에 방향이 있으면 방향 그래프, 없으면 무방향 그래프예요.'),
     FLIP(['노드(정점, vertex)', '점. 사람·역·상태'], ['간선(edge)', '두 노드를 잇는 선. 관계'],
          ['인접(adjacent)', '간선 하나로 바로 이어져 있음'], ['차수(degree)', '한 노드에 붙은 간선 수 (무방향)'],
          ['경로(path)', '간선을 따라 이어진 노드의 순서'], ['사이클(cycle)', '출발 노드로 되돌아오는 경로'])],
    [T('이 코스에서 계속 쓸 예제 그래프예요. 간선은\n'
       '`1-2, 1-3, 2-4, 2-5, 3-6, 5-6` 여섯 개.\n'
       '1-2-5-6-3-1 로 한 바퀴 도는 **사이클**이 있어요.'),
     THINK('노드 2 의 차수는 몇일까요? 2 에 붙은 간선은 1-2, 2-4, 2-5 → **3** 이에요.')])

L.match('용어와 뜻을 이어 보세요.',
    [['노드', '점(대상)'], ['간선', '두 노드를 잇는 관계'], ['차수', '한 노드에 붙은 간선 수'], ['사이클', '출발점으로 되돌아오는 경로']],
    '시험 서술형에서 "인접 노드", "차수" 같은 말을 정확히 써야 해요.')

L.explain('표현 ① 인접 행렬',
    [T('노드가 n개면 **n×n 2차원 리스트**를 만들고,\n'
       'i 와 j 가 이어져 있으면 `adj[i][j] = 1`, 아니면 0 이에요.\n'
       '노드 번호가 1부터면 크기를 n+1 로 잡아 0번 칸은 비워 두는 경우가 많아요.'),
     CODE('n = 4\nedges = [(1, 2), (1, 3), (3, 4)]\nadj = [[0] * (n + 1) for _ in range(n + 1)]\nfor a, b in edges:\n    adj[a][b] = 1\n    adj[b][a] = 1   # 무방향: 양쪽 모두\nfor i in range(1, n + 1):\n    print(adj[i][1:])', '간선 목록 → 인접 행렬')],
    [T('무방향 그래프의 인접 행렬은 `adj[i][j] == adj[j][i]` 라서 **대각선 기준 대칭**이에요.\n'
       '한 행의 합이 그 노드의 **차수**예요.'),
     WARN('`[[0] * 5] * 5` 로 만들면 다섯 행이 **같은 리스트**를 가리켜서 한 칸을 바꾸면 모든 행이 바뀌어요. 컴프리헨션 `[[0] * 5 for _ in range(5)]` 을 쓰세요.')])

L.output('출력은?', '''\
adj = [[0, 1, 1, 0],
       [1, 0, 1, 1],
       [1, 1, 0, 0],
       [0, 1, 0, 0]]
print(sum(adj[1]))
print(adj[3][0])
print(adj[0][2] == adj[2][0])''',
    '행 1 의 합 3 = 노드 1 의 차수. `adj[3][0]` 은 0(연결 안 됨). 무방향이라 대칭이니 True.\n\n```\n{out}\n```')

L.explain('표현 ② 인접 리스트 (딕셔너리)',
    [T('노드마다 **이웃 노드만** 리스트로 적어 둬요. 딕셔너리 `{노드: [이웃들]}` 로 만들어요.\n'
       '간선이 적은 그래프(대부분의 실제 그래프)에서 공간을 훨씬 적게 써요.'),
     CODE('graph = {}\ndef add_edge(a, b):\n    graph.setdefault(a, []).append(b)\n    graph.setdefault(b, []).append(a)\n\nfor a, b in [(1, 2), (1, 3), (2, 4), (2, 5), (3, 6), (5, 6)]:\n    add_edge(a, b)\nprint(graph)', '간선 목록 → 인접 리스트'),
     TIP('`setdefault(키, [])` 는 키가 없으면 빈 리스트를 넣고 그 리스트를 돌려줘요. 노드 번호가 정해져 있으면 `{i: [] for i in range(1, n + 1)}` 로 미리 만들어도 돼요.')],
    [T('두 방식은 쓰임이 달라요.'),
     CMP(side('인접 행렬', '공간 n×n. "i 와 j 가 이어졌나?" 를 `adj[i][j]` 로 **바로** 확인. 간선이 많을 때 좋아요.'),
         side('인접 리스트', '공간 ≈ 노드 + 간선. **이웃만** 저장해서 이웃을 훑을 때 빨라요. 간선이 적을 때 좋아요.'))])

L.fill('무방향 그래프에 간선 (a, b) 를 추가하는 코드의 빈칸을 채우세요.', '''\
n = 3
graph = {i: [] for i in range(1, n + 1)}
for a, b in [(1, 2), (2, 3)]:
    graph[a].append(___)
    graph[___].append(a)
print(graph)''', [['b'], ['b']],
    '무방향이니 a 의 이웃에 b, b 의 이웃에 a 를 **둘 다** 넣어요. 방향 그래프라면 첫 줄만 써요.',
    expect='{1: [2], 2: [1, 3], 3: [2]}')

L.explain('트리',
    [T('**트리**는 사이클이 없고 모든 노드가 이어진 그래프예요. 가계도·폴더 구조·탐색 과정이 트리예요.\n'
       '맨 위 노드가 **루트**, 위아래로 이어진 두 노드는 **부모-자식**, 자식이 없는 노드는 **리프(잎)** 예요.\n'
       '루트에서 몇 칸 내려왔는지가 **깊이(레벨)** 예요(루트 깊이 0).'),
     CODE('children = {"A": ["B", "C"], "B": ["D", "E"], "C": ["F"], "D": [], "E": [], "F": []}\nleaves = [v for v in children if children[v] == []]\nprint("리프:", leaves)\nedges = sum(len(c) for c in children.values())\nprint("노드", len(children), "개, 간선", edges, "개")', '자식 딕셔너리로 본 트리')],
    [T('트리에서는 두 노드 사이 경로가 **딱 하나**예요. 그래서 노드가 n개면 간선은 항상 **n-1개**예요.\n'
       '간선이 하나라도 더 있으면 사이클이 생기고, 하나라도 모자라면 끊어져요.'),
     KEY('트리 = 연결 + 사이클 없음 → 간선 n-1. 시험에서 "트리인지 판별" 은 이 두 조건으로 서술해요.')])

L.choice('노드가 10개인 트리의 간선 수는?', ['8', '9', '10', '11'], 2,
    '트리는 노드 n개에 간선 n-1개 → 9개예요.')

L.short('위 트리(A 루트: A→B,C / B→D,E / C→F)에서 노드 **E 의 깊이**는? (루트 깊이 0)', '2',
    'A(0) → B(1) → E(2). 루트에서 간선 2개를 내려왔으니 깊이 2 예요.')

L.bucket('설명을 알맞은 표현 방식으로 분류하세요.', ['인접 행렬', '인접 리스트'],
    [['n×n 2차원 리스트', 1], ['{노드: [이웃들]} 딕셔너리', 2], ['두 노드의 연결 여부를 한 번에 확인', 1],
     ['간선이 적을 때 공간 절약', 2], ['무방향이면 대각선 기준 대칭', 1], ['이웃만 빠르게 훑기', 2]],
    '행렬은 "칸 하나로 바로 확인", 리스트는 "이웃만 저장" 이 핵심이에요.')

L.practice('[기출유사] 동아리 친구 관계 정리',
'''학생 n명(1~n번)의 친구 관계 m개가 주어져요. 친구 관계는 서로 친구인 **무방향** 관계예요.

**[조건]**
- 첫째 줄: `n m`, 다음 m줄: 친구인 두 학생 번호 `a b`
- 1번부터 n번까지 `번호: 친구들` 을 출력해요. 친구 번호는 **오름차순**, 친구가 없으면 `번호:` 만 출력해요.
- 마지막 줄: 친구가 **가장 많은** 학생 번호 (여러 명이면 번호가 가장 작은 학생)
- 딕셔너리로 인접 리스트를 만드세요.

{ex}

{ex2}''',
'''n, m = map(int, input().split())
graph = {i: [] for i in range(1, n + 1)}
# m개의 관계를 읽어 인접 리스트를 완성하세요
''',
'''n, m = map(int, input().split())
graph = {i: [] for i in range(1, n + 1)}
for _ in range(m):
    a, b = map(int, input().split())
    graph[a].append(b)      # 무방향: 양쪽에 추가
    graph[b].append(a)
best = 1
for i in range(1, n + 1):
    graph[i].sort()
    print(f"{i}:", *graph[i])
    if len(graph[i]) > len(graph[best]):   # 더 많을 때만 바꿔서 작은 번호 유지
        best = i
print(best)''',
    ['4 3\n1 2\n2 3\n2 4', '5 4\n5 1\n3 5\n1 3\n4 2'], ['1 0', '3 1\n3 2', '4 6\n1 2\n1 3\n1 4\n2 3\n2 4\n3 4'],
    ['`a b` 를 읽을 때마다 `graph[a].append(b)` 와 `graph[b].append(a)` 를 둘 다 해요.',
     '출력 전에 `graph[i].sort()` 로 정렬하고 `print(f"{i}:", *graph[i])` 로 출력해요.',
     '친구 수는 `len(graph[i])`. **더 클 때만** best 를 바꾸면 동점일 때 작은 번호가 남아요.'],
    '`print(f"{i}:", *리스트)` 는 리스트가 비어 있으면 `번호:` 만 출력해요. 친구 수 = 노드의 **차수**예요.')

L.essay('인접 행렬과 인접 리스트의 차이를 **공간**과 **연결 확인/이웃 탐색** 측면에서 서술하세요.',
    '인접 행렬은 노드 수 n에 대해 n×n 칸이 필요해 간선이 적어도 공간을 많이 쓰지만, 두 노드의 연결 여부를 adj[i][j] 로 바로 확인할 수 있다. 인접 리스트는 각 노드의 이웃만 저장해 간선이 적을 때 공간이 적게 들고 이웃을 훑기 빠르지만, 연결 여부를 확인하려면 이웃 리스트를 찾아봐야 한다.',
    ['행렬은 n×n 공간', '행렬은 연결 여부를 바로 확인', '리스트는 이웃만 저장해 공간 절약', '리스트는 이웃 탐색이 빠르다'])

# =====================================================================
L = C.lesson('ε-03 DFS — 깊이 우선 탐색 (재귀·스택)', 25,
'''- DFS 는 **한 방향으로 끝까지** 들어갔다가 막히면 **되돌아와** 다른 길로 가요.
- 재귀 DFS: 방문 표시 → 이웃 중 **방문 안 한 곳**으로 재귀 호출.
- 스택 DFS: `pop()` 으로 꺼내고, 이웃을 **거꾸로** 넣으면 작은 번호부터 방문(재귀와 같은 순서).
- 방문 표시가 없으면 사이클에서 **무한 반복**.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간에는 그래프를 **인접 행렬**과 **인접 리스트(딕셔너리)** 로 저장했어요.\n'
       '오늘부터 이 그래프를 실제로 **탐색**해요. 예제 그래프는 이거예요.'),
     CODE(G_SRC + '\nfor v in graph:\n    print(v, graph[v])', '예제 그래프 (1-2, 1-3, 2-4, 2-5, 3-6, 5-6)')])
L.short('복습: 노드 6 개, 간선 5 개인 그래프가 모두 연결되어 있다면 이 그래프는 무엇일까요? (두 글자)', '트리',
    '연결되어 있고 간선이 n-1 = 5개면 사이클이 없는 **트리**예요.', review=True)

L.explain('DFS 의 아이디어',
    [T('**깊이 우선 탐색(DFS)** 은 미로를 탐험하듯 움직여요.\n'
       '갈 수 있는 길이 있으면 **계속 깊이** 들어가고, 더 갈 곳이 없으면 **바로 전 갈림길로 되돌아와요**(백트래킹).\n'
       '이웃이 여러 개면 보통 **번호가 작은 것부터** 가요.'),
     STEPS(('1 방문', '1 의 이웃 [2, 3] 중 작은 2 로 들어가요.'),
           ('2 방문', '2 의 이웃 [1, 4, 5]. 1 은 방문했으니 4 로.'),
           ('4 방문', '4 의 이웃은 2 뿐(방문함) → 막힘! 2 로 되돌아가요.'),
           ('5 방문', '2 의 다음 이웃 5. 5 의 이웃 [2, 6] 중 6 으로.'),
           ('6 방문', '6 의 이웃 [3, 5] 중 3 이 남았어요.'),
           ('3 방문', '3 의 이웃 1, 6 모두 방문 → 되돌아가며 끝. 순서: **1 2 4 5 6 3**'))],
    [T('DFS 는 "**나중에 발견한 갈림길을 먼저** 처리" 해요. 그래서 **스택(LIFO)** 구조가 어울려요.\n'
       '재귀 함수를 쓰면 파이썬이 내부의 **호출 스택**을 대신 써 줘요.'),
     KEY('DFS = 스택(또는 재귀). BFS = 큐. 시험 빈칸에서 자료구조 이름을 묻는 단골 포인트예요.')])

L.explain('재귀 DFS 코드',
    [T('방문한 노드를 `visited` 리스트에 담아요.\n'
       '① 지금 노드를 방문 표시 ② 이웃을 차례로 보면서 ③ **방문 안 한 이웃**이면 그 이웃으로 재귀 호출.'),
     TRACE(G_SRC + '''
visited = []

def dfs(v):
    visited.append(v)
    for nxt in graph[v]:
        if nxt not in visited:
            dfs(nxt)

dfs(1)
print(visited)''', '재귀 DFS 따라가기', notes={'5': '지금 노드를 방문 표시', '7': '방문 안 한 이웃만 들어가요'})],
    [T('재귀가 끝나고 돌아오는 순간이 바로 **백트래킹**이에요.\n'
       '4 에서 더 갈 곳이 없어 `dfs(4)` 가 끝나면 `dfs(2)` 의 for 문으로 돌아와 다음 이웃 5 를 봐요.'),
     TIP('방문 여부를 리스트 `in` 대신 `visited = [False] * (n + 1)` 처럼 True/False 표로 관리하면 큰 그래프에서 더 빨라요. 시험 코드에서도 두 방식이 다 나와요.')])

L.output('다음 그래프에서 `dfs("A")` 의 출력은?', '''\
graph = {"A": ["B", "C"], "B": ["A", "D"], "C": ["A", "D"], "D": ["B", "C", "E"], "E": ["D"]}
visited = []
def dfs(v):
    visited.append(v)
    for nxt in graph[v]:
        if nxt not in visited:
            dfs(nxt)
dfs("A")
print(" ".join(visited))''',
    'A → B → D → (D 의 이웃 B 방문함) C → C 의 이웃 모두 방문 → 되돌아와 D 의 다음 이웃 E.\n\n```\n{out}\n```')

L.fill('재귀 DFS 의 빈칸을 채우세요.', G_SRC + '''
visited = []
def dfs(v):
    visited.___(v)
    for nxt in graph[v]:
        if nxt ___ visited:
            ___(nxt)
dfs(1)
print(visited)''', [['append'], ['not in'], ['dfs']],
    '방문 표시(`append`) → 방문 안 했으면(`not in`) → 재귀 호출(`dfs(nxt)`). 결과는 `[1, 2, 4, 5, 6, 3]`.',
    expect='[1, 2, 4, 5, 6, 3]')

L.explain('스택으로 DFS',
    [T('재귀 대신 **스택 리스트**를 직접 써도 돼요.\n'
       '스택에서 `pop()` 으로 하나 꺼내 → 이미 방문했으면 건너뛰고 → 아니면 방문 표시 후 이웃을 스택에 넣어요.'),
     CODE(G_SRC + '''
visited = []
stack = [1]
while stack:
    v = stack.pop()
    if v in visited:
        continue
    visited.append(v)
    for nxt in reversed(graph[v]):   # 거꾸로 넣어야 작은 번호가 먼저 나와요
        if nxt not in visited:
            stack.append(nxt)
print(visited)''', '스택 DFS')],
    [T('스택은 **마지막에 넣은 것이 먼저** 나와요.\n'
       '그래서 이웃 [2, 3] 을 그대로 넣으면 3 이 먼저 나와요. 작은 번호부터 가려면 `reversed` 로 **거꾸로** 넣어요.'),
     CMP(side('거꾸로 넣음 (reversed)', '재귀 DFS 와 같은 순서', G_SRC + '\nvisited, stack = [], [1]\nwhile stack:\n    v = stack.pop()\n    if v in visited:\n        continue\n    visited.append(v)\n    for nxt in reversed(graph[v]):\n        stack.append(nxt)\nprint(visited)', 'good'),
         side('그대로 넣음', '큰 번호부터 방문 — 이것도 DFS 지만 순서가 달라요', G_SRC + '\nvisited, stack = [], [1]\nwhile stack:\n    v = stack.pop()\n    if v in visited:\n        continue\n    visited.append(v)\n    for nxt in graph[v]:\n        stack.append(nxt)\nprint(visited)')),
     EXAM('"방문 순서를 쓰시오" 문항은 **이웃을 어떤 순서로 넣는지**를 꼭 확인하고 따라가세요.')])

L.output('이웃을 **거꾸로 넣지 않은** 스택 DFS 예요. 출력은?', '''\
graph = {1: [2, 3], 2: [1, 4], 3: [1, 4], 4: [2, 3]}
visited, stack = [], [1]
while stack:
    v = stack.pop()
    if v in visited:
        continue
    visited.append(v)
    for nxt in graph[v]:
        stack.append(nxt)
print(*visited)''',
    '1 을 꺼내 [2, 3] 을 넣으면 3 이 먼저 나와요. 3 → 이웃 [1, 4] 중 4 가 나중이라 먼저 → 4 → 2.\n\n```\n{out}\n```')

L.order('스택 DFS 코드를 순서대로 놓으세요. (그래프와 visited 는 이미 있어요)',
    ['stack = [start]', 'while stack:', '    v = stack.pop()', '    if v in visited:', '        continue',
     '    visited.append(v)', '    for nxt in reversed(graph[v]):', '        stack.append(nxt)'],
    '꺼내기(pop) → 방문했으면 건너뛰기 → 방문 표시 → 이웃 넣기. pop 은 **반복문 안 맨 처음**이에요.')

L.spot('DFS 가 끝나지 않고 오류(RecursionError)로 멈춰요. **원인이 된 줄**은?', '''\
graph = {1: [2], 2: [1, 3], 3: [2]}
def dfs(v):
    print(v)
    for nxt in graph[v]:
        dfs(nxt)
dfs(1)''', 5,
    '방문 검사 없이 모든 이웃으로 재귀해서 1 → 2 → 1 → 2 … 끝없이 왕복해요. `visited` 에 기록하고 `if nxt not in visited:` 일 때만 `dfs(nxt)` 를 불러야 해요.')

L.ox('DFS 는 시작 노드에서 **가까운 노드부터** 차례로 방문하므로 최단 거리를 구할 때 쓴다.', False,
    '가까운 것부터 층별로 방문하는 건 **BFS** 예요. DFS 는 한 길로 깊이 들어가서 먼 노드를 먼저 방문할 수 있어요.')

L.practice('[기출유사] 던전 방 탐험 순서 (DFS)',
'''던전의 방 n개(1~n번)와 통로 m개가 주어져요. 통로는 양방향이에요. 시작 방에서 **DFS** 로 탐험할 때 방문하는 방 번호를 순서대로 출력하세요.

**[조건]**
- 첫째 줄: `n m 시작방`, 다음 m줄: 통로로 이어진 두 방 `a b`
- 갈 수 있는 방이 여러 개면 **번호가 작은 방부터** 가요.
- 시작 방에서 갈 수 없는 방은 출력하지 않아요.
- 재귀 함수 또는 스택을 사용하세요. 출력은 공백으로 구분해요.

{ex}

{ex2}''',
'''n, m, start = map(int, input().split())
graph = {i: [] for i in range(1, n + 1)}
for _ in range(m):
    a, b = map(int, input().split())
    # 인접 리스트를 만드세요

visited = []
# DFS 를 작성하세요
''',
'''n, m, start = map(int, input().split())
graph = {i: [] for i in range(1, n + 1)}
for _ in range(m):
    a, b = map(int, input().split())
    graph[a].append(b)
    graph[b].append(a)
for v in graph:
    graph[v].sort()            # 작은 번호부터 가기 위해 정렬

visited = []
def dfs(v):
    visited.append(v)          # 방문 표시
    for nxt in graph[v]:
        if nxt not in visited: # 방문 안 한 방만
            dfs(nxt)

dfs(start)
print(*visited)''',
    ['6 6 1\n1 2\n1 3\n2 4\n2 5\n3 6\n5 6', '5 4 3\n3 5\n5 1\n3 2\n1 4'], ['3 0 2', '4 2 1\n1 2\n3 4', '5 5 5\n5 4\n4 3\n3 2\n2 1\n1 5'],
    ['통로는 양방향이니 `graph[a].append(b)`, `graph[b].append(a)` 둘 다.',
     '입력 순서가 섞여 있으니 탐색 전에 `graph[v].sort()` 로 정렬해요.',
     '`def dfs(v): visited.append(v)` → `for nxt in graph[v]: if nxt not in visited: dfs(nxt)`'],
    '이웃 리스트를 정렬해 두는 것이 "작은 번호부터" 조건의 핵심이에요. 시작 방과 연결되지 않은 방은 dfs 가 닿지 않으니 자동으로 빠져요.')

L.practice('[기출유사] 동아리 그룹 수 세기 (DFS 응용)',
'''학생 n명(1~n번)과 친구 관계 m개가 주어져요. 친구의 친구도 같은 그룹이에요. 그룹이 **몇 개**인지와, **가장 큰 그룹의 인원**을 출력하세요.

**[조건]**
- 첫째 줄: `n m`, 다음 m줄: 친구인 두 학생 `a b`
- 친구가 없는 학생은 혼자서 한 그룹이에요.
- 방문하지 않은 학생에서 DFS 를 새로 시작할 때마다 그룹 수가 1 늘어나요.
- 첫째 줄: 그룹 수, 둘째 줄: 가장 큰 그룹 인원

{ex}

{ex2}''',
'''n, m = map(int, input().split())
graph = {i: [] for i in range(1, n + 1)}
for _ in range(m):
    a, b = map(int, input().split())
    graph[a].append(b)
    graph[b].append(a)
# 그룹 수와 가장 큰 그룹 인원을 구하세요
''',
'''n, m = map(int, input().split())
graph = {i: [] for i in range(1, n + 1)}
for _ in range(m):
    a, b = map(int, input().split())
    graph[a].append(b)
    graph[b].append(a)

visited = [False] * (n + 1)
def dfs(v):
    visited[v] = True
    size = 1                      # 나 자신
    for nxt in graph[v]:
        if not visited[nxt]:
            size += dfs(nxt)      # 이웃 쪽 인원을 더해요
    return size

groups, biggest = 0, 0
for i in range(1, n + 1):
    if not visited[i]:            # 새 그룹 발견
        groups += 1
        biggest = max(biggest, dfs(i))
print(groups)
print(biggest)''',
    ['6 3\n1 2\n2 3\n4 5', '5 4\n1 2\n2 3\n3 1\n4 5'], ['1 0', '4 0', '5 4\n1 2\n2 3\n3 4\n4 5'],
    ['1번부터 n번까지 돌면서 **아직 방문 안 한** 학생을 만나면 그룹 수 +1 하고 DFS 를 시작해요.',
     'DFS 가 방문한 학생 수를 `return` 하게 만들면 그룹 인원을 알 수 있어요.',
     '`size = 1` 에서 시작해 `size += dfs(nxt)` 로 이웃 쪽 인원을 더해 `return size`.'],
    '한 번의 DFS 는 시작점과 **이어진 노드 전부**를 방문해요. 그래서 DFS 를 새로 시작한 횟수가 곧 연결된 덩어리(연결 요소)의 개수예요.')

L.essay('스택으로 DFS 를 구현할 때 이웃 노드를 `reversed(graph[v])` 처럼 **거꾸로** 넣는 이유를 스택의 성질과 연결해 서술하세요.',
    '스택은 나중에 넣은 것이 먼저 나오는 후입선출(LIFO) 구조이다. 이웃을 작은 번호부터 그대로 넣으면 가장 큰 번호가 먼저 꺼내져 큰 번호부터 방문하게 된다. 작은 번호부터 방문하려면 거꾸로 넣어 작은 번호가 스택의 맨 위에 오게 해야 한다.',
    ['스택은 후입선출(LIFO)', '그대로 넣으면 큰 번호가 먼저 나온다', '거꾸로 넣으면 작은 번호가 맨 위에 온다'])

# =====================================================================
L = C.lesson('ε-04 BFS — 너비 우선 탐색과 촌수 계산', 25,
'''- BFS 는 시작점에서 **가까운 노드부터 층별로** 방문해요. 자료구조는 **큐(FIFO)**.
- `from collections import deque` → `append` 로 넣고 `popleft()` 로 꺼내요. (`list.pop(0)` 은 느려요)
- 큐에 **넣을 때** 방문 표시를 해야 같은 노드가 두 번 들어가지 않아요.
- `dist[nxt] = dist[v] + 1` → 간선 비용이 모두 같으면 BFS 거리 = **최단 거리**. 촌수 계산이 대표 예.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간에는 DFS 를 재귀와 스택으로 짰어요. 한 길로 깊이 → 막히면 되돌아오기.\n'
       '예제 그래프의 DFS(1) 순서는 `1 2 4 5 6 3` 이었어요. 오늘은 같은 그래프를 **BFS** 로 탐색해요.'),
     REVEAL('DFS 에 쓰는 자료구조와 그 성질은?', '**스택** — 나중에 넣은 것이 먼저 나오는 후입선출(LIFO). 재귀 DFS 는 호출 스택을 써요.')])
L.ox('복습: 재귀 DFS 에서 방문 검사를 빼면 사이클이 있는 그래프에서 끝나지 않을 수 있다.', True,
    '1 → 2 → 1 → 2 … 처럼 계속 되돌아가 무한 호출이 돼요(파이썬은 RecursionError 로 멈춰요).', review=True)

L.explain('BFS 의 아이디어',
    [T('**너비 우선 탐색(BFS)** 은 호수에 돌을 던졌을 때 물결이 퍼지듯 움직여요.\n'
       '시작점 → 거리 1인 노드 전부 → 거리 2인 노드 전부 → … 순서예요.\n'
       '먼저 발견한 노드를 먼저 처리하니 **큐(FIFO)** 를 써요.'),
     STEPS(('시작', '큐 [1]. 1 을 꺼내 이웃 2, 3 을 넣어요 → 큐 [2, 3]'),
           ('2 꺼냄', '이웃 4, 5 를 넣어요(1 은 방문함) → 큐 [3, 4, 5]'),
           ('3 꺼냄', '이웃 6 을 넣어요 → 큐 [4, 5, 6]'),
           ('4, 5, 6 꺼냄', '새로 넣을 이웃이 없어요 → 큐가 비면 끝'),
           ('결과', '방문 순서 **1 2 3 4 5 6** — 거리 0 → 1 → 2 순서예요.'))],
    [T('같은 그래프인데 DFS 는 `1 2 4 5 6 3`, BFS 는 `1 2 3 4 5 6` 이에요.\n'
       'BFS 는 1 과 바로 이어진 3 을 4 보다 먼저 방문해요.'),
     CMP(side('DFS', '스택(재귀) · 깊이 먼저 · 경로 하나를 끝까지'),
         side('BFS', '큐 · 가까운 것 먼저 · 층별로 퍼짐 · 최단 거리'))])

L.explain('큐는 deque 로',
    [T('리스트의 `pop(0)` 도 앞에서 꺼내지만, 뒤의 원소를 **모두 한 칸씩 당겨야** 해서 데이터가 많으면 느려요.\n'
       '`collections.deque` 는 양쪽 끝에서 넣고 빼는 것이 빨라요. BFS 에서는 `append` 와 `popleft` 를 써요.'),
     CODE('from collections import deque\nq = deque([1])\nq.append(2)\nq.append(3)\nprint(q.popleft())\nprint(q)\nprint(len(q))', 'deque 기본')],
    [T('`popleft` 는 **deque 의 메서드**예요. 일반 리스트에는 없어요.'),
     WARN('`queue = []` 로 만들고 `queue.popleft()` 를 부르면 AttributeError 예요. `queue = deque([...])` 로 만들어야 해요.')])

L.spot('실행하면 오류가 나는 줄은?', '''\
from collections import deque
queue = [1]
queue.append(2)
v = queue.popleft()
print(v)''', 4,
    '`queue` 는 그냥 리스트라 `popleft` 가 없어요 → AttributeError. 2번 줄을 `queue = deque([1])` 로 고쳐야 해요.',
    error_line=4)

L.explain('BFS 코드',
    [T('큐에서 하나 꺼내 → 이웃 중 방문 안 한 노드를 **방문 표시하고** 큐에 넣어요.\n'
       '시작 노드도 **넣을 때 바로** 방문 표시해요.'),
     TRACE('from collections import deque\n' + G_SRC + '''
visited = [1]
queue = deque([1])
while queue:
    v = queue.popleft()
    print(v, end=" ")
    for nxt in graph[v]:
        if nxt not in visited:
            visited.append(nxt)
            queue.append(nxt)''', 'BFS 따라가기', notes={'9': '방문 안 한 이웃만', '10': '넣을 때 방문 표시'})],
    [T('넣을 때 표시하지 않고 **꺼낼 때** 표시하면, 6 처럼 여러 노드(3, 5)의 이웃인 노드가 큐에 **두 번** 들어갈 수 있어요.\n'
       '결과가 틀어지거나 시간이 더 걸려요.'),
     KEY('BFS 3박자: `popleft()` → `if nxt not in visited` → `visited` 표시 + `append`.')])

L.output('BFS 의 출력은?', '''\
from collections import deque
graph = {"A": ["B", "C"], "B": ["A", "D"], "C": ["A", "D"], "D": ["B", "C", "E"], "E": ["D"]}
visited = ["A"]
queue = deque(["A"])
while queue:
    v = queue.popleft()
    print(v, end=" ")
    for nxt in graph[v]:
        if nxt not in visited:
            visited.append(nxt)
            queue.append(nxt)''',
    '거리 0: A → 거리 1: B, C → 거리 2: D → 거리 3: E. (지난 시간 DFS 는 A B D C E 였어요.)\n\n```\n{out}\n```')

L.fill('BFS 의 빈칸을 채우세요.', 'from collections import ___\n' + G_SRC + '''
visited = [1]
queue = deque([1])
order = []
while queue:
    v = queue.___()
    order.append(v)
    for nxt in graph[v]:
        if nxt not in visited:
            visited.append(nxt)
            queue.___(nxt)
print(order)''', [['deque'], ['popleft'], ['append']],
    'deque 를 가져와서 앞에서 꺼내고(`popleft`) 뒤에 넣어요(`append`). 결과 `[1, 2, 3, 4, 5, 6]`.',
    expect='[1, 2, 3, 4, 5, 6]')

L.explain('BFS 로 최단 거리 구하기',
    [T('`dist` 에 시작점에서의 거리를 적어요. 시작점은 0.\n'
       '`v` 에서 처음 발견한 이웃은 `dist[nxt] = dist[v] + 1` 이에요.\n'
       '`dist` 에 들어 있는지가 곧 방문 여부라서 visited 가 따로 필요 없어요.'),
     CODE('from collections import deque\n' + G_SRC + '''
dist = {1: 0}
queue = deque([1])
while queue:
    v = queue.popleft()
    for nxt in graph[v]:
        if nxt not in dist:
            dist[nxt] = dist[v] + 1
            queue.append(nxt)
print(dist)''', 'BFS 거리')],
    [T('BFS 는 거리 0 인 노드를 다 처리한 뒤 거리 1, 그다음 거리 2 … 순서로 처리해요.\n'
       '그래서 어떤 노드를 **처음 발견한 순간의 거리**가 가장 짧은 거리예요. 나중에 더 짧은 길이 나타날 수 없어요.'),
     WARN('이건 **모든 간선의 비용이 같을 때**(한 칸 = 1) 이야기예요. 간선마다 비용이 다르면 BFS 만으로는 최단 거리를 보장하지 못해요.')])

L.choice('BFS 로 구한 거리가 최단 거리임이 보장되는 경우는?',
    ['간선마다 비용이 다를 때', '모든 간선의 비용이 같을 때', '그래프에 사이클이 없을 때만', '노드 번호가 정렬되어 있을 때'], 2,
    'BFS 는 간선 개수로 층을 나눠 가까운 층부터 처리하니, 간선 비용이 모두 같을 때 최단 거리를 보장해요.')

L.explain('촌수 계산 = 가계도에서 BFS',
    [T('부모와 자식 사이는 **1촌**이에요. 형제는 부모를 거쳐 2촌, 삼촌은 3촌이에요.\n'
       '가계도를 **무방향 그래프**(부모-자식 간선)로 보면, 두 사람의 **촌수 = 두 사람 사이 최단 거리**예요.\n'
       '그래서 한 사람에서 BFS 를 하고 다른 사람의 dist 를 읽으면 돼요.'),
     CODE('''from collections import deque
pairs = [("할아버지", "아버지"), ("할아버지", "삼촌"), ("아버지", "나"), ("삼촌", "사촌")]
family = {}
for p, c in pairs:
    family.setdefault(p, []).append(c)
    family.setdefault(c, []).append(p)   # 촌수는 위아래 모두 1

dist = {"나": 0}
queue = deque(["나"])
while queue:
    v = queue.popleft()
    for nxt in family[v]:
        if nxt not in dist:
            dist[nxt] = dist[v] + 1
            queue.append(nxt)
print(dist["삼촌"], dist["사촌"])''', '촌수 계산')],
    [T('BFS 가 끝나도 dist 에 없는 사람은 **이어지지 않은** 사람이에요(남남).\n'
       '시험에서는 "관계가 없으면 -1 출력" 같은 조건이 붙어요. `dist.get(사람, -1)` 로 처리하면 깔끔해요.'),
     EXAM('촌수 계산 BFS 는 기출 단골 소재예요. **무방향으로 양쪽에 추가**, **dist[v] + 1**, **연결 안 되면 -1** 세 가지를 꼭 챙기세요.')])

L.output('촌수 계산 BFS 의 출력은?', '''\
from collections import deque
graph = {1: [2, 3], 2: [1, 4, 5], 3: [1], 4: [2], 5: [2], 6: [7], 7: [6]}
dist = {4: 0}
queue = deque([4])
while queue:
    v = queue.popleft()
    for nxt in graph[v]:
        if nxt not in dist:
            dist[nxt] = dist[v] + 1
            queue.append(nxt)
print(dist.get(3, -1), dist.get(5, -1), dist.get(6, -1))''',
    '4 → 2(1) → 1, 5(2) → 3(3). 6 은 4 와 이어져 있지 않아 -1.\n\n```\n{out}\n```')

L.bucket('설명을 DFS / BFS 로 분류하세요.', ['DFS', 'BFS'],
    [['스택 또는 재귀', 1], ['큐(deque)', 2], ['가까운 노드부터 층별로', 2], ['한 길로 끝까지 갔다가 되돌아옴', 1],
     ['간선 비용이 같을 때 최단 거리', 2], ['백트래킹', 1]],
    'DFS 는 "깊이·스택·되돌아오기", BFS 는 "너비·큐·최단 거리" 로 묶어 기억하세요.')

L.practice('[기출유사] 이름으로 촌수 계산',
'''가족의 부모-자식 관계가 이름으로 주어져요. 두 사람의 **촌수**를 출력하세요.

**[조건]**
- 첫째 줄: 관계 수 m, 다음 m줄: `부모이름 자식이름`, 마지막 줄: 촌수를 구할 두 사람 `A B`
- 부모-자식은 1촌이에요. 촌수는 두 사람 사이 **최단 거리**예요.
- 관계가 이어지지 않으면 `-1` 을 출력해요. A 와 B 는 관계 목록에 꼭 한 번 이상 나와요.
- 딕셔너리 인접 리스트와 `deque` 를 사용한 BFS 로 구하세요.

{ex}

{ex2}''',
'''from collections import deque
m = int(input())
family = {}
for _ in range(m):
    p, c = input().split()
    # 양쪽으로 연결하세요

a, b = input().split()
# BFS 로 촌수를 구하세요
''',
'''from collections import deque
m = int(input())
family = {}
for _ in range(m):
    p, c = input().split()
    family.setdefault(p, []).append(c)   # 부모 → 자식
    family.setdefault(c, []).append(p)   # 자식 → 부모 (무방향)

a, b = input().split()
dist = {a: 0}
queue = deque([a])
while queue:
    v = queue.popleft()
    for nxt in family[v]:
        if nxt not in dist:              # 처음 발견 = 최단 거리
            dist[nxt] = dist[v] + 1
            queue.append(nxt)
print(dist.get(b, -1))                  # 연결 안 되면 -1''',
    ['4\n민호 서준\n민호 지아\n서준 하늘\n지아 별\n하늘 별', '3\n철수 영희\n영희 민지\n동수 하나\n민지 하나'],
    ['1\n엄마 나\n나 엄마', '5\n가 나\n나 다\n다 라\n라 마\n마 바\n바 가', '2\n김 이\n박 최\n이 최'],
    ['`family.setdefault(p, []).append(c)` 와 반대 방향 `family.setdefault(c, []).append(p)` 를 둘 다 해요.',
     'A 에서 BFS 를 시작해요: `dist = {a: 0}`, `queue = deque([a])`.',
     '이웃이 dist 에 없으면 `dist[nxt] = dist[v] + 1` 하고 큐에 넣어요. 마지막은 `print(dist.get(b, -1))`.'],
    '촌수는 위로 올라가든 아래로 내려가든 한 칸이 1촌이라 **무방향** 그래프가 돼요. 간선 비용이 모두 1이니 BFS 거리가 곧 최단 거리, 즉 촌수예요.')

L.practice('[기출유사] 소문은 며칠 만에?',
'''학생 n명(1~n번)과 친구 관계 m개가 주어져요. 하루가 지나면 소문을 아는 학생의 **모든 친구**가 소문을 알게 돼요. 0일째에 시작 학생만 소문을 알아요.

**[조건]**
- 첫째 줄: `n m 시작학생 k`, 다음 m줄: 친구인 두 학생 `a b`
- 첫째 줄: 1번부터 n번까지 각 학생이 소문을 알게 되는 날 (끝까지 모르면 `-1`), 공백으로 구분
- 둘째 줄: **k일째까지** 소문을 아는 학생 수 (시작 학생 포함)
- BFS 의 거리(dist)를 이용하세요.

{ex}

{ex2}''',
'''from collections import deque
n, m, s, k = map(int, input().split())
graph = {i: [] for i in range(1, n + 1)}
for _ in range(m):
    a, b = map(int, input().split())
    graph[a].append(b)
    graph[b].append(a)
# BFS 로 각 학생이 소문을 알게 되는 날을 구하세요
''',
'''from collections import deque
n, m, s, k = map(int, input().split())
graph = {i: [] for i in range(1, n + 1)}
for _ in range(m):
    a, b = map(int, input().split())
    graph[a].append(b)
    graph[b].append(a)

day = [-1] * (n + 1)         # -1 = 아직 모름
day[s] = 0
queue = deque([s])
while queue:
    v = queue.popleft()
    for nxt in graph[v]:
        if day[nxt] == -1:   # 처음 듣는 학생
            day[nxt] = day[v] + 1
            queue.append(nxt)
print(*day[1:])
print(sum(1 for d in day[1:] if 0 <= d <= k))''',
    ['6 5 1 1\n1 2\n1 3\n2 4\n4 5\n3 5', '5 3 3 2\n3 4\n4 5\n1 2'], ['1 0 1 0', '4 3 4 0\n1 2\n2 3\n3 4', '5 4 1 9\n1 2\n2 3\n3 4\n4 5'],
    ['소문이 퍼지는 날 = 시작 학생에서의 **BFS 거리**예요.',
     '`day = [-1] * (n + 1)` 로 모두 모름(-1) 으로 두고 `day[s] = 0`.',
     '`if day[nxt] == -1:` 일 때 `day[nxt] = day[v] + 1`. 둘째 줄은 `0 <= d <= k` 인 학생 수.'],
    '"하루에 한 칸씩 퍼진다" 는 BFS 의 층과 똑같아요. day 배열이 방문 표시와 거리 기록을 동시에 해요.')

L.essay('간선 비용이 모두 같은 그래프에서 **BFS 가 최단 경로(최단 거리)를 보장하는 이유**를 큐의 성질과 연결해 서술하세요.',
    'BFS 는 큐(선입선출)를 사용하므로 먼저 발견한 노드를 먼저 처리한다. 그래서 시작점에서 거리 0인 노드를 모두 처리한 뒤 거리 1, 거리 2 순서로 층별로 탐색한다. 어떤 노드를 처음 발견했을 때는 그보다 가까운 층을 이미 모두 살펴본 뒤이므로 더 짧은 경로가 있을 수 없고, 처음 발견한 거리가 최단 거리이다. 단, 모든 간선의 비용이 같을 때 성립한다.',
    ['큐(선입선출)를 쓴다', '가까운 층부터 층별로 탐색한다', '처음 발견한 거리가 최단이다', '간선 비용이 같을 때 성립'])

# =====================================================================
L = C.lesson('ε-05 상태공간과 휴리스틱: 8-퍼즐과 Best-First', 25,
'''- 문제 풀이 = **상태공간** 탐색: 초기 상태 → (연산자/행동) → … → 목표 상태.
- 8-퍼즐: 3×3 판, 빈칸을 **상·하·좌·우**로 움직여요. 칸 i 의 위치는 `(i // 3, i % 3)`.
- 휴리스틱 h(n): 목표까지 남은 정도를 **추정**. h1 = 제자리 아닌 타일 수, h2 = **맨해튼 거리 합** (빈칸 제외).
- **Best-First**: 펼칠 후보 중 h 가 **가장 작은** 상태부터. 빠르지만 최단 해를 보장하지는 않아요.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간에는 큐로 BFS 를 짜고, `dist[v] + 1` 로 최단 거리와 촌수를 구했어요.\n'
       'DFS·BFS 는 목표에 대한 **정보 없이** 정해진 순서로 다 훑는 탐색이에요(맹목적 탐색).\n'
       '오늘은 "**목표에 가까워 보이는 쪽**"을 먼저 보는 탐색을 배워요.'),
     REVEAL('BFS 에서 방문 표시는 언제 하는 게 좋을까요?', '큐에 **넣을 때**. 그래야 같은 노드가 큐에 두 번 들어가지 않아요.')])
L.fill('복습: BFS 거리 갱신 줄의 빈칸을 채우세요.', '''\
from collections import deque
graph = {1: [2], 2: [1, 3], 3: [2]}
dist = {1: 0}
q = deque([1])
while q:
    v = q.popleft()
    for nxt in graph[v]:
        if nxt not in dist:
            dist[nxt] = ___
            q.append(nxt)
print(dist[3])''', [['dist[v] + 1', 'dist[v]+1', '1 + dist[v]']],
    '이웃까지의 거리는 지금 노드 거리 + 1. 3 까지는 2 예요.', review=True, expect='2')

L.explain('상태공간이란',
    [T('AI 는 문제를 **상태**들 사이를 옮겨 다니는 탐색으로 봐요.\n'
       '상태 하나가 그래프의 **노드**, 한 번의 행동(연산자)이 **간선**이에요.\n'
       '가능한 모든 상태와 그 사이 연결 전체를 **상태공간**이라고 해요.'),
     FLIP(['상태(state)', '문제의 한 순간 모습 (퍼즐 판 배치)'], ['초기 상태', '탐색을 시작하는 상태'],
          ['목표 상태', '도달하고 싶은 상태'], ['연산자(행동)', '상태를 바꾸는 동작 (빈칸 이동)'],
          ['상태공간', '가능한 모든 상태 + 연결 = 거대한 그래프'], ['해(solution)', '초기 → 목표로 가는 행동의 순서'])],
    [T('**8-퍼즐**은 3×3 판에 1~8 타일과 빈칸 하나가 있어요.\n'
       '빈칸과 이웃한 타일을 밀어 넣는 것 = **빈칸을 상·하·좌·우로 옮기는 것**으로 생각하면 편해요.\n'
       '이 코스에서는 목표 상태를 아래처럼 정해요(빈칸 = 0).'),
     CODE('goal = [1, 2, 3,\n        4, 5, 6,\n        7, 8, 0]\nfor r in range(3):\n    print(goal[r * 3: r * 3 + 3])', '목표 상태'),
     TIP('수업·시험에서 목표 상태를 다르게 정할 수도 있어요(예: 빈칸이 가운데). 문제의 목표 상태를 꼭 확인하세요.')])

L.explain('상태를 코드로: 칸 번호 ↔ (행, 열)',
    [T('판을 길이 9 리스트로 펼치면 칸 번호 i 는 **행 = i // 3, 열 = i % 3** 이에요.\n'
       '거꾸로 (r, c) 의 칸 번호는 `r * 3 + c` 예요. 칸을 눌러 확인해 보세요.'),
     IDX('state', [2, 8, 3, 1, 6, 4, 7, 0, 5])],
    [T('빈칸이 (r, c) 에 있으면 위(r-1), 아래(r+1), 왼쪽(c-1), 오른쪽(c+1) 으로 갈 수 있어요.\n'
       '단, **판 밖(0~2 범위 밖)** 으로는 못 가요. 그래서 다음 상태의 수는 빈칸 위치에 따라 2~4개예요.'),
     CODE('''def next_states(state):
    z = state.index(0)            # 빈칸 위치
    r, c = z // 3, z % 3
    result = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:   # 상 하 좌 우
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            s = state[:]                   # 복사본
            nz = nr * 3 + nc
            s[z], s[nz] = s[nz], s[z]      # 빈칸과 맞바꾸기
            result.append(s)
    return result

for s in next_states([1, 2, 3, 4, 0, 5, 6, 7, 8]):
    print(s)''', '다음 상태 만들기'),
     WARN('`s = state` 로 쓰면 **같은 리스트**를 바꿔서 원래 상태가 망가져요. `state[:]` 로 복사하세요.')])

L.output('빈칸 위치에 따라 다음 상태가 몇 개인지 출력해요. 출력은?', '''\
def count_moves(z):
    r, c = z // 3, z % 3
    cnt = 0
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        if 0 <= r + dr < 3 and 0 <= c + dc < 3:
            cnt += 1
    return cnt
print(count_moves(0), count_moves(1), count_moves(4))''',
    '구석(0번 칸)은 2방향, 변(1번 칸)은 3방향, 가운데(4번 칸)는 4방향이에요.\n\n```\n{out}\n```')

L.explain('맹목적 탐색의 한계',
    [T('8-퍼즐의 9칸 배치는 모두 9! = 362,880 가지예요(그중 절반만 실제로 도달할 수 있어요).\n'
       'BFS 는 최단 해를 찾지만 가까운 상태를 **전부** 펼쳐 보느라 상태를 아주 많이 만들어요.\n'
       'DFS 는 엉뚱한 방향으로 깊이 빠질 수 있어요.'),
     THINK('사람은 퍼즐을 풀 때 "이 수를 두면 목표에 더 가까워 보인다" 는 **감**을 써요. 이 감을 숫자로 만든 것이 **휴리스틱**이에요.')])

L.explain('휴리스틱 ① 제자리 아닌 타일 수',
    [T('**휴리스틱 함수 h(n)** 은 상태 n 에서 목표까지 남은 정도를 **추정**한 값이에요. 작을수록 목표에 가까워 보여요.\n'
       '가장 쉬운 것은 **목표 위치에 있지 않은 타일 수(h1)** 예요. **빈칸은 세지 않아요.**'),
     CODE('''goal = [1, 2, 3, 4, 5, 6, 7, 8, 0]
state = [1, 2, 3, 4, 0, 6, 7, 5, 8]
h1 = 0
for i in range(9):
    if state[i] != 0 and state[i] != goal[i]:
        h1 += 1
print(h1)''', '제자리 아닌 타일 수')],
    [T('위 상태는 5 와 8 이 제자리가 아니라 h1 = 2 예요.\n'
       '빈칸(0)도 제자리가 아니지만 타일이 아니라서 빼요.'),
     KEY('빈칸까지 세면 값이 1 커져요. 시험에서 "빈칸 제외" 조건을 꼭 확인하세요.')])

L.explain('휴리스틱 ② 맨해튼 거리',
    [T('**맨해튼 거리**는 타일이 목표 칸까지 가로·세로로만 움직일 때의 칸 수예요.\n'
       '타일 하나: `|현재 행 - 목표 행| + |현재 열 - 목표 열|`.\n'
       '**빈칸을 뺀 모든 타일**의 맨해튼 거리를 더한 값이 h2 예요.'),
     CODE('''goal = [1, 2, 3, 4, 5, 6, 7, 8, 0]
state = [8, 1, 3, 4, 0, 2, 7, 6, 5]
h2 = 0
for i in range(9):
    t = state[i]
    if t == 0:
        continue                  # 빈칸 제외
    g = goal.index(t)             # 목표 칸 번호
    d = abs(i // 3 - g // 3) + abs(i % 3 - g % 3)
    print(t, "→", d)
    h2 += d
print("맨해튼 합:", h2)''', '타일별 맨해튼 거리')],
    [T('타일은 한 번에 한 칸만, 가로·세로로만 움직이니 각 타일은 **최소한 맨해튼 거리만큼은** 움직여야 해요.\n'
       '그래서 h2 는 실제로 필요한 이동 횟수보다 **크지 않은** 추정값이에요.\n'
       'h1 보다 정보가 많아서(얼마나 멀리 있는지까지 봄) 보통 탐색을 더 잘 안내해요.'),
     CMP(side('h1 제자리 아닌 타일 수', '틀린 위치인지 **아닌지만** 봐요. 1칸 차이도 4칸 차이도 똑같이 1.'),
         side('h2 맨해튼 거리 합', '**얼마나 먼지**까지 봐요. 같은 상태에서 h2 ≥ h1.', '', 'good'))])

L.short('목표가 `1 2 3 / 4 5 6 / 7 8 0` 일 때 상태 `1 2 3 / 0 4 6 / 7 5 8` 의 **맨해튼 거리 합**은? (빈칸 제외)', '3',
    '4 는 지금 (1,1), 목표 (1,0) → 1. 5: 지금 (2,1), 목표 (1,1) → 1. 8: 지금 (2,2), 목표 (2,1) → 1. 나머지는 제자리. 합 3.',
    check_code='''goal = [1, 2, 3, 4, 5, 6, 7, 8, 0]
s = [1, 2, 3, 0, 4, 6, 7, 5, 8]
print(sum(abs(i // 3 - goal.index(t) // 3) + abs(i % 3 - goal.index(t) % 3) for i, t in enumerate(s) if t))''')

L.short('같은 상태 `1 2 3 / 0 4 6 / 7 5 8` 의 **제자리 아닌 타일 수**(빈칸 제외)는?', '3',
    '4, 5, 8 세 개가 제자리가 아니에요. 빈칸은 세지 않아요.',
    check_code='goal = [1, 2, 3, 4, 5, 6, 7, 8, 0]\ns = [1, 2, 3, 0, 4, 6, 7, 5, 8]\nprint(sum(1 for i in range(9) if s[i] and s[i] != goal[i]))')

L.explain('Best-First 탐색',
    [T('**Best-First(최고 우선) 탐색**은 펼칠 후보(열린 목록) 중 **h 가 가장 작은 상태**를 먼저 펼쳐요.\n'
       '큐(BFS)·스택(DFS) 대신 "**평가값이 가장 좋은 것부터**" 꺼내는 목록을 쓰는 셈이에요.'),
     STEPS(('1', '초기 상태를 열린 목록에 넣어요.'),
           ('2', '열린 목록에서 h 가 가장 작은 상태를 꺼내요.'),
           ('3', '목표 상태면 끝!'),
           ('4', '아니면 다음 상태들을 만들고, 처음 보는 상태만 h 를 계산해 열린 목록에 넣어요.'),
           ('5', '2번으로 돌아가 반복해요.'))],
    [T('h 만 보고 고르는 방식(탐욕적 Best-First)은 목표 쪽으로 빠르게 가지만,\n'
       '지금까지 몇 번 움직였는지(g)는 보지 않아서 **가장 짧은 해를 보장하지는 않아요**.\n'
       '지나온 비용까지 더해 `f = g + h` 로 고르는 방법이 **A\\*** 탐색이에요.'),
     CMP(side('BFS', '정보 없이 가까운 것부터 전부 · 최단 해 보장 · 상태를 많이 만듦'),
         side('Best-First (h 기준)', '휴리스틱으로 유망한 것부터 · 보통 빠름 · 최단 해 보장 X', '', 'good'))])

L.choice('빈칸을 움직여 만든 다음 상태 세 개의 맨해튼 거리 합이 각각 상 = 5, 좌 = 3, 우 = 4 일 때, Best-First 탐색이 다음에 펼칠 상태는?',
    ['상 (h = 5)', '좌 (h = 3)', '우 (h = 4)', '세 개를 모두 동시에'], 2,
    'Best-First 는 h 가 **가장 작은** 상태부터 펼쳐요. h 는 남은 거리 추정이라 작을수록 목표에 가까워 보여요.')

L.order('Best-First 탐색의 한 바퀴를 순서대로 놓으세요.',
    ['열린 목록에서 h 가 가장 작은 상태를 꺼낸다', '꺼낸 상태가 목표인지 검사한다', '목표가 아니면 다음 상태들을 만든다',
     '처음 보는 상태의 h 를 계산해 열린 목록에 넣는다'],
    '꺼내기 → 목표 검사 → 펼치기 → 평가해서 넣기. BFS 와 뼈대는 같고 "무엇을 먼저 꺼내나" 만 달라요.', mono=False)

L.practice('[기출유사] 8-퍼즐 휴리스틱 계산기',
'''8-퍼즐 상태가 3줄로 주어져요(빈칸은 0). 목표 상태는 `1 2 3 / 4 5 6 / 7 8 0` 이에요.

**[조건]**
- 첫째 줄: 제자리가 아닌 타일 수 (빈칸 제외)
- 둘째 줄: 맨해튼 거리 합 (빈칸 제외)
- 셋째 줄: 목표 상태와 같으면 `목표 도달`, 아니면 `탐색 필요`
- 칸 번호 i 의 위치는 `(i // 3, i % 3)` 로 계산하세요.

{ex}

{ex2}''',
'''state = []
for _ in range(3):
    state += list(map(int, input().split()))
goal = [1, 2, 3, 4, 5, 6, 7, 8, 0]
# h1, h2 를 계산하세요
''',
'''state = []
for _ in range(3):
    state += list(map(int, input().split()))   # 9칸 리스트로 펼치기
goal = [1, 2, 3, 4, 5, 6, 7, 8, 0]

h1, h2 = 0, 0
for i in range(9):
    t = state[i]
    if t == 0:
        continue                       # 빈칸은 세지 않음
    if t != goal[i]:
        h1 += 1
    g = goal.index(t)                  # 목표 칸
    h2 += abs(i // 3 - g // 3) + abs(i % 3 - g % 3)
print(h1)
print(h2)
print("목표 도달" if state == goal else "탐색 필요")''',
    ['1 2 3\n4 0 6\n7 5 8', '8 1 3\n4 0 2\n7 6 5'], ['1 2 3\n4 5 6\n7 8 0', '0 1 2\n3 4 5\n6 7 8', '8 7 6\n5 4 3\n2 1 0'],
    ['세 줄을 읽어 `state += list(map(int, input().split()))` 로 9칸 리스트를 만들어요.',
     '타일 t 의 목표 칸은 `goal.index(t)`, 행은 `// 3`, 열은 `% 3`.',
     '`if t == 0: continue` 로 빈칸을 건너뛰고, h1 은 `t != goal[i]` 일 때 +1, h2 는 행 차 + 열 차를 더해요.'],
    '맨해튼 거리는 각 타일이 목표까지 최소 몇 칸 움직여야 하는지의 합이에요. 빈칸은 타일이 아니라서 두 휴리스틱 모두에서 빼요.')

L.practice('[기출유사] Best-First 한 걸음',
'''8-퍼즐 상태가 3줄로 주어져요(빈칸 0, 목표 `1 2 3 / 4 5 6 / 7 8 0`). 빈칸을 **상·하·좌·우** 순서로 움직여 볼 때, 가능한 각 이동의 결과 상태의 **맨해튼 거리 합**을 출력하고 Best-First 가 고를 이동을 출력하세요.

**[조건]**
- "상" 은 빈칸이 위 칸으로 가는 것이에요(위 칸 타일이 아래로 내려와요). 판 밖으로는 못 가요.
- 가능한 이동마다 한 줄씩 `방향 h` 를 상·하·좌·우 순서로 출력해요.
- 마지막 줄: `선택: 방향` — h 가 가장 작은 이동, 같으면 **먼저 나온** 이동
- 맨해튼 거리는 빈칸을 빼고 계산해요.

{ex}

{ex2}''',
'''state = []
for _ in range(3):
    state += list(map(int, input().split()))
goal = [1, 2, 3, 4, 5, 6, 7, 8, 0]

def manhattan(s):
    # 맨해튼 거리 합을 돌려주세요
    return 0

# 상하좌우로 움직여 보세요
''',
'''state = []
for _ in range(3):
    state += list(map(int, input().split()))
goal = [1, 2, 3, 4, 5, 6, 7, 8, 0]

def manhattan(s):
    total = 0
    for i in range(9):
        if s[i] != 0:                          # 빈칸 제외
            g = goal.index(s[i])
            total += abs(i // 3 - g // 3) + abs(i % 3 - g % 3)
    return total

z = state.index(0)
r, c = z // 3, z % 3
best_dir, best_h = "", None
for name, dr, dc in [("상", -1, 0), ("하", 1, 0), ("좌", 0, -1), ("우", 0, 1)]:
    nr, nc = r + dr, c + dc
    if 0 <= nr < 3 and 0 <= nc < 3:            # 판 안쪽만
        s = state[:]                           # 복사해서 바꾸기
        nz = nr * 3 + nc
        s[z], s[nz] = s[nz], s[z]
        h = manhattan(s)
        print(name, h)
        if best_h is None or h < best_h:       # 더 작을 때만 → 동점이면 먼저 나온 것
            best_dir, best_h = name, h
print("선택:", best_dir)''',
    ['1 2 3\n4 0 6\n7 5 8', '1 2 3\n4 5 6\n7 0 8'], ['0 1 3\n4 2 5\n7 8 6', '1 2 3\n4 5 0\n7 8 6', '2 8 3\n1 6 4\n7 0 5'],
    ['빈칸 위치 `z = state.index(0)`, `r, c = z // 3, z % 3`.',
     '방향마다 `nr, nc` 를 구해 `0 <= nr < 3 and 0 <= nc < 3` 일 때만 `s = state[:]` 복사 후 맞바꿔요.',
     '`if best_h is None or h < best_h:` 처럼 **더 작을 때만** 바꾸면 동점일 때 먼저 나온 방향이 남아요.'],
    '실제 Best-First 는 이 과정을 목표에 닿을 때까지 반복하고, 이미 본 상태는 다시 넣지 않아요. 오늘은 그 핵심인 "다음 상태 만들기 + 휴리스틱으로 고르기" 한 걸음을 짰어요.')

L.essay('8-퍼즐에서 맨해튼 거리 합이 휴리스틱으로 알맞은 이유를 **"실제 이동 횟수"** 와 비교해 서술하고, 제자리 아닌 타일 수(h1)보다 나은 점을 쓰세요.',
    '타일은 한 번에 가로나 세로로 한 칸씩만 움직일 수 있으므로 각 타일은 적어도 자신의 맨해튼 거리만큼은 움직여야 한다. 따라서 맨해튼 거리 합은 실제로 필요한 이동 횟수보다 크지 않은, 목표까지 남은 거리의 합리적인 추정값이다. 제자리 아닌 타일 수는 틀린 위치인지 여부만 보지만 맨해튼 거리는 얼마나 멀리 있는지까지 반영하므로 상태를 더 세밀하게 구분해 탐색을 더 잘 안내한다.',
    ['타일은 한 칸씩 가로·세로로만 움직인다', '실제 이동 횟수보다 크지 않다(과대평가하지 않음)', '얼마나 먼지까지 반영한다', 'h1 보다 상태를 세밀하게 구분'])

# =====================================================================
L = C.lesson('ε-06 pandas 로 데이터 첫인상 보기 (EDA)', 25,
'''- 표 전체는 **DataFrame**, 열 하나는 **Series**. `df['열']` → Series, `df[['열']]` → DataFrame.
- 첫 확인: `head()` · `shape` (행, 열) · `info()` · `describe()` · `columns`.
- `describe()`: count(결측 제외 개수)·mean·**std(n-1 로 나눈 표본 표준편차)**·min·25%·50%·75%·max.
- 범주 개수는 `value_counts()` (많은 순), 조건 필터는 `df[df['열'] >= 값]`.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간까지 **탐색** 단원(그래프·DFS·BFS·휴리스틱)을 끝냈어요.\n'
       '오늘부터는 **데이터 다루기**예요. 모델을 만들기 전에 데이터를 살펴보는 일(EDA, 탐색적 데이터 분석)을 해요.'),
     REVEAL('Best-First 탐색은 열린 목록에서 무엇을 먼저 꺼내나요?', '휴리스틱 값 **h 가 가장 작은**(목표에 가장 가까워 보이는) 상태를 먼저 꺼내요.')])
L.match('복습: 탐색 방법과 쓰는 자료구조/기준을 이어 보세요.',
    [['DFS', '스택(재귀)'], ['BFS', '큐(deque)'], ['Best-First', 'h 가 가장 작은 것부터']],
    'DFS·BFS 는 순서가 정해진 맹목적 탐색, Best-First 는 휴리스틱을 쓰는 탐색이에요.', review=True)

L.explain('DataFrame 과 Series',
    [T('pandas 는 **표 모양 데이터**를 다루는 라이브러리예요. 보통 `import pandas as pd` 로 불러요.\n'
       '코랩에서는 `pd.read_csv("파일.csv")` 로 읽는 경우가 많지만, 여기서는 딕셔너리로 작은 표를 만들어 볼게요.\n'
       '이 레슨 내내 쓰는 예제 표예요(학생 6명).'),
     CODE(DF_SRC + '\nprint(df.head(3))\nprint(df.shape)', '예제 DataFrame (읽기 전용)', run_=False)],
    [T('`df.shape` 은 **(행 수, 열 수)** 튜플이에요. 괄호 없이 쓰는 **속성**이에요.\n'
       '`df["score"]` 처럼 대괄호에 열 이름 하나를 넣으면 **Series**(열 하나)가 나와요.\n'
       '대괄호를 두 겹 `df[["score"]]` 으로 쓰면 열 하나짜리 **DataFrame** 이에요.'),
     CMP(side('df["score"]', 'Series — 1차원, 열 하나'),
         side('df[["name", "score"]]', 'DataFrame — 표, 열 여러 개 고르기')),
     WARN('`df.shape()` 처럼 괄호를 붙이면 오류예요. `shape`·`columns`·`dtypes` 는 속성, `head()`·`describe()`·`info()` 는 메서드예요.')])

L.output('예제 표에서 다음 코드의 출력은? (pandas 는 이 사이트에서 실행되지 않으니 예측해요)', DF_SRC + '''
print(df.shape)
print(len(df.columns))
print(df["hours"].sum())''',
    '6행 5열이라 `(6, 5)`, 열 이름 5개, hours 합 2+5+3+1+4+3 = 18.\n\n```\n{out}\n```')

L.explain('EDA 첫 명령어들',
    [T('새 데이터를 받으면 거의 항상 같은 순서로 확인해요.\n'
       '크기(shape) → 앞부분(head) → 열 정보(info) → 통계 요약(describe) → 결측치(isna) → 범주 분포(value_counts).'),
     FLIP(['df.head(n)', '앞 n행 보기 (기본 5)'], ['df.tail(n)', '뒤 n행 보기'], ['df.shape', '(행 수, 열 수)'],
          ['df.info()', '열 이름·자료형·결측 아닌 개수'], ['df.describe()', '수치형 열의 통계 요약'],
          ['df.isna().sum()', '열마다 결측치 개수'], ['df["열"].value_counts()', '값마다 몇 번 나왔나'],
          ['df["열"].unique()', '서로 다른 값 목록'], ['df["열"].nunique()', '서로 다른 값의 개수'])],
    [T('시험의 EDA 빈칸은 대부분 이 함수 이름이에요. 목적 → 함수를 바로 떠올릴 수 있게 카드로 외워 두세요.'),
     EXAM('"각 열의 결측치 개수를 출력하는 코드" → `df.isna().sum()`. `isnull()` 도 같은 기능이에요.')])

L.match('하고 싶은 일과 코드를 이어 보세요.',
    [['행·열 크기 확인', 'df.shape'], ['수치형 열 통계 요약', 'df.describe()'], ['열마다 결측치 개수', 'df.isna().sum()'],
     ['범주별 개수', 'df["club"].value_counts()'], ['앞 5행 보기', 'df.head()']],
    'EDA 의 다섯 기본기예요. 시험 빈칸 1순위!')

L.ox('`df.shape()` 처럼 괄호를 붙여야 행·열 크기를 얻을 수 있다.', False,
    '`shape` 은 **속성**이라 괄호 없이 `df.shape` 로 써요. 괄호를 붙이면 튜플을 함수처럼 부르게 되어 TypeError 가 나요.')

L.explain('describe() 읽기',
    [T('`describe()` 는 수치형 열마다 8가지 통계를 보여 줘요.\n'
       '`score` 열 하나만 요약해 볼게요.'),
     REVEAL_RUN('`df["score"].describe()` 의 결과는?', DF_SRC + '\nprint(df["score"].describe())')],
    [T('- **count**: 결측치를 **뺀** 값의 개수\n'
       '- **mean**: 평균, **50%**: 중앙값(median)\n'
       '- **25% / 75%**: 1사분위수(Q1) / 3사분위수(Q3)\n'
       '- **std**: 표준편차 — pandas 는 **n-1** 로 나눈 표본 표준편차가 기본이에요.'),
     KEY('평균과 중앙값(50%)이 크게 다르면 한쪽으로 치우쳤거나 이상치가 있다는 신호예요.'),
     WARN('numpy 의 `np.std()` 는 기본이 **n** 으로 나눠요(ddof=0). 같은 데이터라도 pandas `std()` 와 값이 조금 달라요.')])

L.output('출력은?', DF_SRC + '''
print(df["score"].max() - df["score"].min())
print(df["hours"].mean())
print(df["score"].median())''',
    '최고 92 - 최저 60 = 32. hours 평균 18 / 6 = 3.0. score 중앙값은 가운데 두 값 75, 81 의 평균 78.0.\n\n```\n{out}\n```')

L.explain('value_counts 와 조건으로 고르기',
    [T('`value_counts()` 는 범주형 열에서 값마다 개수를 세어 **많은 순서**로 보여 줘요.\n'
       '`df[조건]` 은 조건이 True 인 **행만** 골라요. 조건은 `df["열"] >= 값` 처럼 써요.'),
     REVEAL_RUN('`df["club"].value_counts()` 의 결과는?', DF_SRC + '\nprint(df["club"].value_counts())')],
    [T('조건을 두 개 이상 묶을 때는 `and` 대신 `&`(그리고), `|`(또는) 를 쓰고 **각 조건에 괄호**를 쳐요.'),
     CODE(DF_SRC + '\nhigh = df[df["score"] >= 80]\nprint(len(high))\nboth = df[(df["grade"] == 2) & (df["hours"] >= 4)]\nprint(both["name"].tolist())', '조건 필터 (읽기 전용)', run_=False),
     TIP('그룹별 평균은 `df.groupby("club")["score"].mean()` 처럼 구해요. "동아리별 평균 점수" 같은 문항에 써요.')])

L.fill('2학년 학생만 골라 평균 점수를 출력하는 코드의 빈칸을 채우세요.', DF_SRC + '''
g2 = df[df["grade"] ___ 2]
print(g2["score"].___())''', [['=='], ['mean']],
    '같은지 비교는 `==`, 평균은 `mean()`. 2학년은 민준 92, 서연 81, 유나 88 → 평균 87.0.', expect='87.0')

L.output('출력은?', DF_SRC + '''
print(len(df[df["hours"] >= 3]))
print(df["club"].nunique())
print(df["club"].value_counts()["코딩"])''',
    'hours 가 3 이상인 학생은 민준·서연·유나·도윤 4명. 동아리 종류는 로봇·코딩·AI 3개. 코딩은 3명.\n\n```\n{out}\n```')

L.practice('[기출유사] describe() 직접 만들기',
'''pandas 없이 `describe()` 의 일부를 직접 계산해요. 한 줄에 정수 점수들이 주어져요(2개 이상).

**[조건]**
- `count`, `mean`, `std`, `min`, `max` 를 한 줄씩 `이름 값` 으로 출력해요.
- mean 과 std 는 `f"{값:.2f}"` 로 소수 둘째 자리까지 출력해요.
- std 는 pandas 처럼 **n-1** 로 나눈 표본 표준편차: `std = (Σ(x - 평균)² / (n - 1)) ** 0.5`
- `statistics` 모듈은 쓰지 말고 반복문으로 계산하세요.

{ex}

{ex2}''',
'''data = list(map(int, input().split()))
n = len(data)
# count, mean, std, min, max 를 출력하세요
''',
'''data = list(map(int, input().split()))
n = len(data)
mean = sum(data) / n
sq = 0
for x in data:
    sq += (x - mean) ** 2          # 편차 제곱의 합
std = (sq / (n - 1)) ** 0.5        # 표본 표준편차 (n-1)
print("count", n)
print("mean", f"{mean:.2f}")
print("std", f"{std:.2f}")
print("min", min(data))
print("max", max(data))''',
    ['70 92 81 60 88 75', '3 7'], ['5 5 5', '100 0', '1 2 3 4 5 6 7 8 9 10'],
    ['평균 `mean = sum(data) / n`.', '편차 제곱 `(x - mean) ** 2` 를 모두 더해 `n - 1` 로 나누고 `** 0.5` 로 제곱근.',
     '`print("mean", f"{mean:.2f}")` 처럼 이름과 값을 공백으로 출력해요.'],
    'pandas 의 `std()` 는 기본이 n-1 로 나누는 표본 표준편차예요. 첫 예시(예제 표의 score)의 std 가 describe() 결과 11.84 와 같은지 확인해 보세요.')

L.practice('[기출유사] value_counts() 직접 만들기',
'''학생들이 고른 동아리 이름이 한 줄에 공백으로 주어져요. pandas 의 `value_counts()` 처럼 동아리별 인원을 출력하세요.

**[조건]**
- 딕셔너리로 개수를 세요.
- **개수가 많은 순서**로, 개수가 같으면 **이름의 사전 순서**로 한 줄에 `이름 개수` 를 출력해요.
- 마지막 줄: 서로 다른 동아리 수 (`nunique` 에 해당)

{ex}

{ex2}''',
'''clubs = input().split()
cnt = {}
# 개수를 세고 정렬해 출력하세요
''',
'''clubs = input().split()
cnt = {}
for c in clubs:
    cnt[c] = cnt.get(c, 0) + 1                       # 누적 세기
items = sorted(cnt.items(), key=lambda p: (-p[1], p[0]))   # 개수 내림차순, 이름 오름차순
for name, k in items:
    print(name, k)
print(len(cnt))''',
    ['로봇 코딩 코딩 로봇 AI 코딩', 'b a c a b'], ['수학', 'x y z', '천문 천문 천문 생물 생물 화학 화학'],
    ['`cnt[c] = cnt.get(c, 0) + 1` 로 세요.', '`sorted(cnt.items(), key=lambda p: (-p[1], p[0]))` — 개수에 마이너스를 붙이면 큰 개수가 앞으로 와요.',
     '서로 다른 값의 수는 딕셔너리 키 개수 `len(cnt)` 예요.'],
    '`value_counts()` 는 내부적으로 이렇게 **값 → 개수** 를 세고 많은 순서로 정렬해 보여 주는 기능이에요.')

L.essay('`df.describe()` 결과에서 어떤 열의 `count` 가 전체 행 수(`len(df)`)보다 작게 나왔어요. 그 **이유**와, 이 경우 **확인해야 할 코드**를 서술하세요.',
    'describe 의 count 는 결측치(NaN)를 제외한 값의 개수이므로, count 가 행 수보다 작다는 것은 그 열에 결측치가 있다는 뜻이다. df.isna().sum() 으로 열마다 결측치 개수를 확인하고, 이후 결측치를 삭제(dropna)하거나 채우는(fillna) 처리를 해야 한다.',
    ['count 는 결측치를 제외한 개수', '그 열에 결측치가 있다', 'df.isna().sum() 으로 확인', '결측치 처리(dropna/fillna)가 필요'])

# =====================================================================
DF_NA = '''import pandas as pd
import numpy as np
df = pd.DataFrame({
    'age':    [16, np.nan, 17, 16, np.nan, 18],
    'height': [165, 172, np.nan, 158, 180, 175],
    'city':   ['광주', '서울', '광주', '부산', '서울', '광주'],
})'''

L = C.lesson('ε-07 결측치 처리와 원-핫 인코딩', 25,
'''- 결측치(NaN) 확인: `df.isna().sum()` (열마다 개수).
- 처리: `dropna()` 행 삭제 / `fillna(값)` 채우기 — 평균·중앙값·최빈값 등.
- 결과는 **다시 대입**: `df["age"] = df["age"].fillna(df["age"].mean())`.
- 범주형 → 숫자: `pd.get_dummies(df, columns=["city"])` = **원-핫 인코딩** (값마다 0/1 열).
- 0, 1, 2 로 번호를 매기면 없던 **크기·순서 관계**가 생겨서 원-핫을 써요.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간에는 `shape`·`describe()`·`value_counts()`·조건 필터로 데이터의 첫인상을 봤어요.\n'
       'describe 의 count 가 행 수보다 작으면 **결측치**가 있다는 뜻이었죠. 오늘은 그걸 처리해요.'),
     REVEAL('`df["score"]` 와 `df[["score"]]` 의 차이는?', '앞은 **Series**(열 하나, 1차원), 뒤는 열 하나짜리 **DataFrame**(표)이에요.')])
L.choice('복습: pandas `describe()` 의 `std` 는 무엇으로 나눈 표준편차인가요?', ['n', 'n - 1', 'n + 1', '최댓값'], 2,
    'pandas 는 기본이 n-1 로 나누는 표본 표준편차예요(numpy `np.std` 기본은 n).', review=True)

L.explain('결측치 찾기',
    [T('**결측치**는 값이 비어 있는 칸이에요. pandas 에서는 보통 `NaN`(Not a Number) 으로 보여요.\n'
       '`df.isna()` 는 칸마다 결측이면 True 인 표를 만들고, `.sum()` 을 붙이면 True 를 1 로 세서 **열마다 결측 개수**가 돼요.'),
     CODE(DF_NA + '\nprint(df.isna().sum())\nprint(df.isna().sum().sum())', '결측치가 있는 예제 (읽기 전용)', run_=False)],
    [T('위 예제는 age 에 2개, height 에 1개, city 에 0개가 비어 있어요. 전체 합은 3이에요.\n'
       '평균 같은 통계 함수는 결측치를 **빼고** 계산해요.'),
     REVEAL_RUN('`df["age"].mean()` 과 `df["age"].count()` 는?', DF_NA + '\nprint(df["age"].mean())\nprint(df["age"].count())',
                '16, 17, 16, 18 네 값만으로 계산해요.')])

L.output('출력은?', DF_NA + '''
print(df["height"].isna().sum())
print(df.shape[0] - df["age"].count())''',
    'height 결측 1개. 행 6개 중 age 가 있는 값 4개 → 결측 2개.\n\n```\n{out}\n```')

L.ox('pandas 의 `mean()` 은 결측치(NaN)가 있으면 결과도 NaN 이 된다.', False,
    'pandas 의 `mean()`·`sum()`·`std()` 등은 기본으로 결측치를 **건너뛰고** 계산해요. 그래서 age 평균이 16.75 로 나왔어요.')

L.explain('처리 ① 삭제 dropna, ② 채우기 fillna',
    [T('**삭제**: 결측치가 있는 행을 지워요. 간단하지만 데이터가 줄어들어요.\n'
       '**채우기**: 평균·중앙값(수치형), 최빈값(범주형) 같은 대표값으로 채워요. 데이터는 유지되지만 추측값이 들어가요.'),
     CMP(side('dropna()', '결측이 하나라도 있는 행 삭제 · 데이터 손실', DF_NA + '\nprint(df.dropna().shape)'),
         side('fillna(값)', '빈칸을 값으로 채움 · 행 유지', DF_NA + '\nprint(df.fillna(0).shape)', 'good'))],
    [T('`fillna` 는 **채운 새 결과를 돌려줄 뿐** 원본을 바꾸지 않아요. 반드시 **다시 대입**해야 해요.'),
     CODE(DF_NA + '''
df["age"] = df["age"].fillna(df["age"].mean())          # 평균으로
df["height"] = df["height"].fillna(df["height"].median()) # 중앙값으로
print(df["age"].tolist())
print(df.isna().sum().sum())''', '평균·중앙값으로 채우기 (읽기 전용)', run_=False),
     WARN('`df["age"].fillna(값, inplace=True)` 처럼 열을 꺼내서 inplace 로 바꾸는 코드는 최신 pandas(3.x)에서 **원본 df 를 바꾸지 않아요**. `df["age"] = df["age"].fillna(값)` 으로 쓰세요.')],
    [T('이상치가 있는 열은 평균이 크게 흔들리니 **중앙값**으로 채우는 게 더 안전할 때가 많아요.\n'
       '범주형 열은 평균을 낼 수 없으니 **최빈값** `df["city"].mode()[0]` 으로 채워요.'),
     KEY('수치형 → 평균/중앙값, 범주형 → 최빈값. 결측이 너무 많은 열은 열 자체를 지우기도 해요(`df.drop(columns=["열"])`).')])

L.spot('결측치를 평균으로 채웠는데 마지막 줄이 여전히 `2` 를 출력해요. **고쳐야 할 줄**은?', DF_NA + '''
m = df["age"].mean()
df["age"].fillna(m)
print(df["age"].isna().sum())''', 9,
    '9번 줄은 채운 결과를 만들기만 하고 **어디에도 저장하지 않아요**. `df["age"] = df["age"].fillna(m)` 으로 다시 대입해야 해요.')

L.output('출력은?', DF_NA + '''
df["age"] = df["age"].fillna(df["age"].mean())
print(df["age"].mean())
print(df.dropna().shape)''',
    '평균(16.75)으로 채우면 평균은 그대로 16.75. age 는 채웠고 height 결측 1행만 남아 dropna 하면 5행 3열.\n\n```\n{out}\n```')

L.explain('범주형 데이터와 원-핫 인코딩',
    [T('모델은 **숫자**만 계산할 수 있어요. `city` 같은 글자(범주형) 열은 숫자로 바꿔야 해요.\n'
       '**원-핫 인코딩**은 값마다 열을 하나씩 만들고, 해당하면 1(True), 아니면 0(False) 을 넣어요.\n'
       'pandas 에서는 `pd.get_dummies()` 로 해요.'),
     REVEAL_RUN('`pd.get_dummies(df, columns=["city"], dtype=int)` 의 열 이름과 첫 행은?',
                DF_NA + '\nd = pd.get_dummies(df, columns=["city"], dtype=int)\nprint(list(d.columns))\nprint(d.iloc[0].tolist())',
                '새 열 이름은 `원래열_값` 모양이에요.')],
    [T('그냥 광주=0, 서울=1, 부산=2 로 번호를 매기면 모델이 "부산(2) 이 광주(0) 보다 크다", "서울은 광주와 부산의 중간" 처럼 **없는 순서·크기**를 배울 수 있어요.\n'
       '원-핫은 모든 값을 **대등하게** 표현해요.'),
     CMP(side('번호 매기기 (라벨)', '광주 0 / 서울 1 / 부산 2 → 크기 관계가 생김', '', 'bad'),
         side('원-핫', 'city_광주, city_부산, city_서울 열에 0/1 → 대등', '', 'good')),
     TIP('최신 pandas 의 `get_dummies` 는 기본으로 True/False(bool) 를 넣어요. 0/1 숫자가 필요하면 `dtype=int`. `drop_first=True` 를 주면 첫 열 하나를 빼서 열 수를 줄여요.')])

L.short('`city` 열의 값이 `광주, 서울, 부산, 서울, 대전` 일 때 `pd.get_dummies(df["city"])` 의 **열 개수**는?', '4',
    '서로 다른 값(광주·서울·부산·대전) 마다 열이 하나씩 → 4개예요.',
    check_code='import pandas as pd\nprint(pd.get_dummies(pd.Series(["광주", "서울", "부산", "서울", "대전"])).shape[1])')

L.bucket('각 열을 수치형 / 범주형으로 분류하세요.', ['수치형 (평균·표준화 가능)', '범주형 (원-핫 대상)'],
    [['키(cm)', 1], ['혈액형', 2], ['공부 시간', 1], ['출신 지역', 2], ['동아리 이름', 2], ['몸무게(kg)', 1]],
    '크기 비교와 평균이 의미 있으면 수치형, 이름표 역할이면 범주형이에요.')

L.practice('[기출유사] 결측치를 평균으로 채우기',
'''센서 기록이 한 줄에 공백으로 주어져요. 측정 실패한 칸은 `NA` 로 적혀 있어요. pandas 의 `fillna(평균)` 을 직접 구현하세요.

**[조건]**
- 첫째 줄: 결측(`NA`) 개수
- 둘째 줄: `NA` 를 뺀 값들의 평균, `f"{평균:.1f}"`
- 셋째 줄: `NA` 를 그 평균(`.1f` 형식)으로 바꾼 전체 기록. 원래 값은 입력 그대로 출력해요.
- 숫자는 정수이고, `NA` 가 아닌 값이 최소 1개 있어요.

{ex}

{ex2}''',
'''tokens = input().split()
# 결측 개수, 평균, 채운 결과를 출력하세요
''',
'''tokens = input().split()
values = [int(t) for t in tokens if t != "NA"]     # 결측 제외 (pandas 의 mean 과 같음)
mean = sum(values) / len(values)
print(tokens.count("NA"))
print(f"{mean:.1f}")
filled = [f"{mean:.1f}" if t == "NA" else t for t in tokens]
print(*filled)''',
    ['12 NA 15 9 NA', '20 21 NA'], ['NA 7', '3 4 5', 'NA NA NA 10 NA'],
    ['NA 가 아닌 것만 모아 `int` 로 바꿔 평균을 내요: `[int(t) for t in tokens if t != "NA"]`.',
     '결측 개수는 `tokens.count("NA")`.',
     '셋째 줄은 `[f"{mean:.1f}" if t == "NA" else t for t in tokens]` 를 `print(*...)` 로.'],
    'pandas 의 `mean()` 도 결측치를 빼고 계산해요. 그래서 평균으로 채운 뒤에도 그 열의 평균은 변하지 않아요.')

L.practice('[기출유사] get_dummies() 직접 만들기',
'''학생들의 지역이 한 줄에 공백으로 주어져요. 원-핫 인코딩 표를 출력하세요.

**[조건]**
- 열은 서로 다른 지역을 **정렬한 순서**로 만들어요 (`get_dummies` 도 정렬된 순서로 열을 만들어요).
- 첫째 줄: 열 이름들 (공백 구분)
- 다음 줄부터 학생마다 한 줄: 해당 지역 열은 `1`, 나머지는 `0` (공백 구분)
- 마지막 줄: 열 개수

{ex}

{ex2}''',
'''regions = input().split()
cols = sorted(set(regions))
# 원-핫 표를 출력하세요
''',
'''regions = input().split()
cols = sorted(set(regions))        # 서로 다른 값, 정렬
print(*cols)
for r in regions:
    row = [1 if c == r else 0 for c in cols]   # 내 지역만 1
    print(*row)
print(len(cols))''',
    ['광주 서울 광주 부산', 'B A C A'], ['X', '서울 서울', 'c b a d c'],
    ['열 이름은 `sorted(set(regions))`.', '학생마다 `[1 if c == r else 0 for c in cols]`.', '열 개수는 `len(cols)`.'],
    '원-핫 표에서는 한 행에 1 이 **딱 하나** 있어요. 값의 종류가 많아지면 열도 그만큼 늘어나요.')

L.essay('범주형 열 `city`(광주·서울·부산)를 0, 1, 2 로 바꾸지 않고 **원-핫 인코딩**하는 이유를 서술하세요.',
    '0, 1, 2 처럼 번호를 매기면 모델이 숫자의 크기와 순서를 의미 있는 것으로 받아들여, 부산(2)이 광주(0)보다 크다거나 서울이 둘의 중간이라는 실제로 없는 관계를 학습할 수 있다. 원-핫 인코딩은 값마다 별도의 0/1 열을 만들어 모든 범주를 대등하게 표현하므로 이런 잘못된 순서 관계가 생기지 않는다.',
    ['번호를 매기면 크기·순서 관계가 생긴다', '실제로는 없는 관계를 학습할 수 있다', '원-핫은 값마다 0/1 열', '범주를 대등하게 표현'])

# =====================================================================
L = C.lesson('ε-08 시각화: 어떤 그래프를 언제 쓸까', 20,
'''- **matplotlib**(`plt`) 이 기본 그리기 도구, **seaborn**(`sns`) 은 그 위에서 DataFrame 을 바로 그려요: `sns.xxx(data=df, x=..., y=..., hue=...)`.
- 분포 → `histplot`, 사분위·이상치 → `boxplot`, 두 수치 관계 → `scatterplot`, 범주 개수 → `countplot`, 범주별 평균 → `barplot`.
- 상관관계 → `sns.heatmap(df.corr(numeric_only=True), annot=True)`, 모든 쌍 → `pairplot`.
- 상자 그림 이상치: `Q1 - 1.5×IQR` 보다 작거나 `Q3 + 1.5×IQR` 보다 큰 값 (IQR = Q3 - Q1).
- 상관계수 r: -1 ~ 1, **직선 관계**의 세기. 상관 ≠ 인과.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간에는 결측치를 찾고(`isna().sum()`) 채우거나(`fillna`) 지웠고(`dropna`), 범주형을 원-핫(`get_dummies`)으로 바꿨어요.\n'
       '오늘은 데이터를 **그림으로** 살펴봐요.'),
     REVEAL('`df["age"].fillna(m)` 만 쓰면 왜 원본이 안 바뀌나요?', 'fillna 는 채운 **새 결과를 돌려줄 뿐**이라서, `df["age"] = df["age"].fillna(m)` 처럼 다시 대입해야 해요.')])
L.short('복습: 범주형 값이 `A, B, A, C, B` 일 때 원-핫 인코딩하면 열은 몇 개?', '3',
    '서로 다른 값 A, B, C 마다 열 하나 → 3개.', review=True)

L.explain('matplotlib 과 seaborn',
    [T('**matplotlib** 은 파이썬의 기본 그래프 라이브러리예요. 보통 `import matplotlib.pyplot as plt`.\n'
       '**seaborn** 은 matplotlib 위에서 동작하며, DataFrame 의 열 이름만 주면 통계 그래프를 쉽게 그려요. 보통 `import seaborn as sns`.\n'
       '코랩에서는 마지막에 `plt.show()` 로 그림을 보여 줘요.'),
     CODE(DF_SRC + '''
import matplotlib.pyplot as plt
import seaborn as sns

plt.scatter(df["hours"], df["score"])                 # matplotlib: 값 목록을 직접 넘김
plt.xlabel("hours")
plt.ylabel("score")
plt.show()

sns.scatterplot(data=df, x="hours", y="score", hue="grade")   # seaborn: 열 이름으로
plt.show()''', '같은 산점도, 두 가지 방법 (읽기 전용)', run_=False)],
    [T('seaborn 함수는 대부분 `data=표, x="열", y="열"` 모양이에요.\n'
       '`hue="열"` 을 주면 그 열의 값마다 **색을 다르게** 칠해 그룹을 비교해요.'),
     EXAM('빈칸 단골: `sns.______(data=df, x="hours", y="score")` → 두 수치 열의 관계면 `scatterplot`. 함수 이름과 **용도**를 짝으로 외워요.')])

L.explain('그래프 종류와 용도',
    [T('"무엇을 보고 싶은가" 에 따라 그래프가 정해져요.'),
     FLIP(['sns.histplot(x=수치)', '한 수치 열의 **분포** (어느 구간에 많나)'],
          ['sns.boxplot(x 또는 y=수치)', '중앙값·사분위수·**이상치**'],
          ['sns.scatterplot(x=수치, y=수치)', '두 수치 열의 **관계**'],
          ['sns.countplot(x=범주)', '범주별 **개수** (value_counts 를 그림으로)'],
          ['sns.barplot(x=범주, y=수치)', '범주별 **평균** 막대'],
          ['sns.lineplot(x=시간, y=수치)', '시간에 따른 **추이**'],
          ['sns.heatmap(상관행렬)', '상관계수를 **색**으로'],
          ['sns.pairplot(df)', '모든 수치 열 **쌍**의 산점도 한꺼번에'])],
    [T('plt 에도 비슷한 기본 함수가 있어요: `plt.plot`(선), `plt.scatter`(점), `plt.hist`(히스토그램), `plt.bar`(막대), `plt.boxplot`(상자).'),
     TIP('countplot 은 개수를 **세서** 그리니 y 가 필요 없고, barplot 은 y 값의 **평균**을 그려요. 이 차이를 묻는 문항이 자주 나와요.')])

L.match('보고 싶은 것과 seaborn 함수를 이어 보세요.',
    [['점수의 분포', 'histplot'], ['동아리별 학생 수', 'countplot'], ['공부시간과 점수의 관계', 'scatterplot'],
     ['점수의 이상치 확인', 'boxplot'], ['열들 사이 상관계수 한눈에', 'heatmap']],
    '분포 hist, 개수 count, 관계 scatter, 이상치 box, 상관 heatmap.')

L.explain('상자 그림(boxplot) 읽기',
    [T('상자 그림은 데이터를 다섯 숫자로 요약해 그려요.\n'
       '상자의 아래·위 변이 **Q1(25%)·Q3(75%)**, 상자 안 선이 **중앙값**이에요.\n'
       '상자 길이 **IQR = Q3 - Q1** 에는 가운데 50% 데이터가 들어 있어요.'),
     STEPS(('IQR 구하기', 'IQR = Q3 - Q1'),
           ('경계 구하기', '아래 경계 = Q1 - 1.5 × IQR, 위 경계 = Q3 + 1.5 × IQR'),
           ('수염', '경계 안에 있는 가장 작은 값·가장 큰 값까지 선(수염)을 그려요.'),
           ('이상치', '경계 밖의 값은 **점**으로 따로 찍어요 → 이상치 후보.'))],
    [T('예: Q1 = 10, Q3 = 20 이면 IQR = 10, 위 경계 20 + 15 = 35, 아래 경계 10 - 15 = -5.\n'
       '그래서 40 은 이상치, 30 은 정상 범위예요.'),
     KEY('1.5 × IQR 규칙은 seaborn·matplotlib 상자 그림의 기본 기준이에요. 이상치는 "틀린 값" 이 아니라 "**확인해 볼 값**" 이에요.')])

L.choice('Q1 = 60, Q3 = 80 인 점수 데이터에서 상자 그림의 **위쪽 이상치 경계**는?', ['80', '90', '100', '110'], 4,
    'IQR = 80 - 60 = 20, 위 경계 = Q3 + 1.5 × 20 = 80 + 30 = 110. 110 보다 큰 값이 이상치예요.')

L.explain('상관계수와 heatmap',
    [T('**상관계수 r** 은 두 수치 변수가 **직선 모양으로** 함께 움직이는 정도예요. -1 ~ 1 사이예요.\n'
       'r 이 1 에 가까우면 한쪽이 클 때 다른 쪽도 큼(양의 상관), -1 에 가까우면 반대(음의 상관), 0 근처면 직선 관계가 약해요.\n'
       'pandas `df.corr()` 가 열들 사이 상관계수 표(상관행렬)를 만들어요.'),
     CODE(DF_SRC + '''
import matplotlib.pyplot as plt
import seaborn as sns
corr = df.corr(numeric_only=True)      # 수치형 열만
print(round(corr.loc["hours", "score"], 3))
sns.heatmap(corr, annot=True)          # annot=True: 칸에 숫자 표시
plt.show()''', '상관행렬 heatmap (읽기 전용)', run_=False)],
    [T('예제 표에서 hours 와 score 의 r 은 약 0.979 예요. 공부시간이 많을수록 점수가 높은 경향이 아주 강해요.'),
     WARN('상관이 높다고 **원인과 결과**라는 뜻은 아니에요. 또 r 이 0 이어도 곡선 관계(예: U 자)는 있을 수 있어요. 그래서 산점도를 함께 봐요.')])

L.output('출력은? (상관행렬의 대각선 값에 주의!)', DF_SRC + '''
corr = df.corr(numeric_only=True)
print(corr.shape)
print(corr.loc["score", "score"])''',
    '수치형 열은 grade·hours·score 3개라 3×3. 자기 자신과의 상관계수는 항상 1.0.\n\n```\n{out}\n```')

L.ox('두 변수의 상관계수가 0 이면 두 변수 사이에는 어떤 관계도 없다.', False,
    '상관계수는 **직선** 관계의 세기만 재요. U 자처럼 곡선 관계가 뚜렷해도 r 이 0 에 가까울 수 있어서 산점도를 함께 봐야 해요.')

L.fill('`club` 별 학생 수 막대그래프와 `score` 분포 히스토그램을 그리는 코드의 빈칸을 채우세요. (읽기 전용 코드)', DF_SRC + '''
import matplotlib.pyplot as plt
import seaborn as sns
sns.___(data=df, x="club")
plt.show()
sns.___(data=df, x="score")
plt.show()''', [['countplot'], ['histplot']],
    '범주의 **개수**는 countplot, 수치의 **분포**는 histplot. (seaborn 은 사이트에서 실행되지 않아요.)', expect=True)

L.practice('[기출유사] 텍스트 히스토그램',
'''`histplot` 이 하는 일을 글자로 흉내 내요. 0~100 사이 정수 점수들이 한 줄에 주어져요. 10점 단위 구간별 개수를 `*` 로 그리세요.

**[조건]**
- 구간은 0~9, 10~19, …, 80~89, 90~100 이에요. (100점은 90~100 구간)
- 학생이 **한 명 이상 있는** 구간만, 낮은 구간부터 출력해요.
- 형식: `시작~끝: ***` (90 구간의 끝은 100)
- 마지막 줄: `최빈 구간: 시작~끝` (개수가 같으면 낮은 구간)

{ex}

{ex2}''',
'''scores = list(map(int, input().split()))
cnt = [0] * 10
# 구간별로 세고 출력하세요
''',
'''scores = list(map(int, input().split()))
cnt = [0] * 10
for s in scores:
    b = min(s // 10, 9)          # 100점은 9번 구간(90~100)으로
    cnt[b] += 1

def label(b):
    end = 100 if b == 9 else b * 10 + 9
    return f"{b * 10}~{end}"

best = 0
for b in range(10):
    if cnt[b] > 0:
        print(f"{label(b)}: " + "*" * cnt[b])
    if cnt[b] > cnt[best]:       # 더 클 때만 → 동점이면 낮은 구간
        best = b
print("최빈 구간:", label(best))''',
    ['72 85 91 78 66 88 100 74', '5 15 15 25'], ['0', '100 100 95', '59 60 61 49 50'],
    ['구간 번호는 `s // 10`. 단 100 은 10 이 되니 `min(s // 10, 9)`.',
     '구간 b 의 이름은 `b*10` ~ `b*10+9`, 마지막 구간만 끝이 100.', '`"*" * cnt[b]` 로 별을 개수만큼 만들어요.'],
    'histplot 은 이렇게 수치를 구간(bin)으로 나눠 개수를 막대로 보여 줘요. 구간 폭을 바꾸면 그림 모양도 달라져요.')

L.practice('[기출유사] 상관계수 직접 계산',
'''`df.corr()` 가 계산하는 피어슨 상관계수를 직접 구해요. 첫째 줄에 x 값들, 둘째 줄에 같은 개수의 y 값들이 주어져요.

**[조건]**
- `r = Σ(x - x평균)(y - y평균) / √( Σ(x - x평균)² × Σ(y - y평균)² )`
- 첫째 줄: r 을 `f"{r:.3f}"` 로 출력
- 둘째 줄: r ≥ 0.7 이면 `강한 양의 상관`, r ≤ -0.7 이면 `강한 음의 상관`, 그 밖에는 `약하거나 없음`
- x 와 y 는 모두 같은 값만 있지는 않아요.

{ex}

{ex2}''',
'''x = list(map(float, input().split()))
y = list(map(float, input().split()))
n = len(x)
# 상관계수 r 을 구하세요
''',
'''x = list(map(float, input().split()))
y = list(map(float, input().split()))
n = len(x)
mx, my = sum(x) / n, sum(y) / n
sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))   # 함께 변하는 정도
sxx = sum((a - mx) ** 2 for a in x)
syy = sum((b - my) ** 2 for b in y)
r = sxy / (sxx * syy) ** 0.5
print(f"{r:.3f}")
if r >= 0.7:
    print("강한 양의 상관")
elif r <= -0.7:
    print("강한 음의 상관")
else:
    print("약하거나 없음")''',
    ['2 5 3 1 4 3\n70 92 81 60 88 75', '1 2 3 4\n8 6 4 2'], ['1 2 3\n2 1 3', '-2 -1 0 1 2\n4 1 0 1 4', '10 20 30 40\n1 3 2 5'],
    ['먼저 x 평균 `mx`, y 평균 `my` 를 구해요.', '분자 `sum((a - mx) * (b - my) for a, b in zip(x, y))`, 분모는 두 제곱합의 곱의 제곱근.',
     '`r = sxy / (sxx * syy) ** 0.5` 후 조건문으로 해석을 출력해요.'],
    '첫 예시는 예제 표의 hours·score 라서 0.979 가 나와요. 히든 테스트 중 `-2 -1 0 1 2 / 4 1 0 1 4` 는 U 자 모양이라 관계가 분명한데도 r = 0 이에요. 상관계수는 **직선** 관계만 잰다는 증거예요.')

L.essay('상자 그림에서 이상치를 판단하는 기준을 **Q1, Q3, IQR** 을 사용해 서술하고, 이상치를 발견했을 때 바로 지우면 안 되는 이유를 쓰세요.',
    'IQR = Q3 - Q1 이고, Q1 - 1.5×IQR 보다 작거나 Q3 + 1.5×IQR 보다 큰 값을 이상치로 본다. 이상치는 측정·입력 오류일 수도 있지만 실제로 존재하는 드문 값일 수도 있으므로, 원인을 확인한 뒤 삭제·대체·유지를 결정해야 한다.',
    ['IQR = Q3 - Q1', 'Q1 - 1.5×IQR 미만 또는 Q3 + 1.5×IQR 초과', '오류일 수도, 실제 값일 수도 있다', '원인을 확인하고 처리를 결정'])

# =====================================================================
L = C.lesson('ε-09 데이터 나누기와 스케일링', 25,
'''- `X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)` — **반환 순서** 주의.
- 나누는 이유: 처음 보는 데이터에서의 성능(**일반화**)을 공정하게 평가하려고.
- Standard: `(x - 평균) / 표준편차` → 평균 0·표준편차 1. MinMax: `(x - min) / (max - min)` → 0~1. Robust: `(x - 중앙값) / IQR`.
- **fit 은 train 에만**, test 는 `transform` 만. test 정보가 학습에 새면 **데이터 누수**.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간에는 그래프 종류(hist·box·scatter·count·heatmap)와 상자 그림의 이상치 기준, 상관계수를 배웠어요.\n'
       '이제 데이터를 모델에 넣기 전 **전처리**를 해요.'),
     REVEAL('상자 그림 이상치 경계는?', '`Q1 - 1.5 × IQR` 보다 작거나 `Q3 + 1.5 × IQR` 보다 큰 값 (IQR = Q3 - Q1).')])
L.match('복습: 그래프와 용도를 이어 보세요.',
    [['histplot', '한 수치의 분포'], ['scatterplot', '두 수치의 관계'], ['countplot', '범주별 개수']],
    '분포·관계·개수!', review=True)

L.explain('왜 train / test 로 나눌까',
    [T('모델을 만든 데이터로 다시 평가하면, 답을 **외운** 모델도 좋은 점수를 받아요.\n'
       '시험 문제를 미리 보고 공부한 뒤 같은 문제로 시험을 보면 실력을 알 수 없는 것과 같아요.\n'
       '그래서 일부(test)를 **떼어 두고**, 나머지(train)로만 학습한 뒤 test 로 평가해요. 처음 보는 데이터에서도 잘하는 능력을 **일반화**라고 해요.'),
     FLIP(['X (특성, feature)', '입력으로 쓰는 열들. 보통 대문자 (2차원 표)'], ['y (타깃, target, 레이블)', '맞히고 싶은 정답 열 (1차원)'],
          ['train 세트', '모델이 학습하는 데이터'], ['test 세트', '마지막에 성능을 재는, 학습에 쓰지 않은 데이터'])],
    [T('sklearn 의 `train_test_split` 이 섞어서(shuffle) 나눠 줘요.\n'
       '`test_size=0.2` 는 20% 를 test 로, `random_state` 는 섞는 방식을 고정해 **매번 같은 결과**가 나오게 해요.\n'
       'test_size 를 안 주면 기본 25% 가 test 예요.'),
     CODE(DF_SRC + '''
from sklearn.model_selection import train_test_split
X = df[["hours"]]          # 2차원 (대괄호 두 겹)
y = df["score"]            # 1차원
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=42)
print(X_train.shape, X_test.shape)
print(y_train.shape, y_test.shape)''', 'train_test_split (읽기 전용)', run_=False),
     KEY('반환 순서: **X_train, X_test, y_train, y_test** — X 둘 먼저, 그다음 y 둘.')])

L.fill('반환 순서에 맞게 빈칸을 채우세요.', '''\
import numpy as np
from sklearn.model_selection import train_test_split
X = np.arange(20).reshape(10, 2)
y = np.arange(10)
X_train, ___, y_train, ___ = train_test_split(X, y, test_size=0.3, random_state=0)
print(len(X_train), len(y_test))''', [['X_test'], ['y_test']],
    'X_train, **X_test**, y_train, **y_test** 순서예요. 10개 중 30% 인 3개가 test.', expect='7 3')

L.output('출력은? (100행 데이터)', '''\
import numpy as np
from sklearn.model_selection import train_test_split
X = np.zeros((100, 3))
y = np.zeros(100)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)
print(X_train.shape)
print(y_test.shape)''',
    '100행 중 20% = 20행이 test, 80행이 train. 열 수(3)는 그대로예요. y 는 1차원이라 `(20,)`.\n\n```\n{out}\n```')

L.explain('스케일링이 필요한 이유',
    [T('특성마다 **단위와 범위**가 달라요. 키는 150~190, 용돈은 10,000~100,000 처럼요.\n'
       '거리를 재거나 경사하강법으로 학습할 때, 숫자 범위가 큰 특성이 결과를 **지배**해 버릴 수 있어요.\n'
       '그래서 특성들을 비슷한 범위로 맞추는 것이 **스케일링**이에요.'),
     THINK('키 차이 10cm 와 용돈 차이 10원을 그대로 더하면 둘이 같은 무게로 취급돼요. 정말 같은 의미일까요?')])

L.explain('스케일러 세 가지',
    [T('sklearn 의 `sklearn.preprocessing` 에 있어요. 공식은 시험 서술형 단골이에요.'),
     TABS(('StandardScaler', '**표준화**: `z = (x - 평균) / 표준편차`\n\n결과의 평균은 0, 표준편차는 1. 표준편차는 **n 으로 나눈** 값을 써요(pandas std 의 n-1 과 다름).'),
          ('MinMaxScaler', '**정규화**: `(x - 최솟값) / (최댓값 - 최솟값)`\n\n결과가 0~1 범위. 최솟값 → 0, 최댓값 → 1. 이상치 하나가 범위를 크게 바꾸니 **이상치에 민감**해요.'),
          ('RobustScaler', '`(x - 중앙값) / IQR` (IQR = Q3 - Q1)\n\n중앙값·사분위수는 극단값에 덜 흔들려서 **이상치에 강해요(robust)**.'))],
    [T('직접 확인해 볼게요. `[1, 2, 3, 4]` 를 StandardScaler 로 바꾸면 평균 2.5, 표준편차(n) 약 1.118 로 계산돼요.'),
     REVEAL_RUN('StandardScaler / MinMaxScaler 결과는?', '''import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
X = np.array([[1], [2], [3], [4]])
print(StandardScaler().fit_transform(X).ravel().round(3))
print(MinMaxScaler().fit_transform(X).ravel().round(3))''')])

L.match('스케일러와 공식을 이어 보세요.',
    [['StandardScaler', '(x - 평균) / 표준편차'], ['MinMaxScaler', '(x - min) / (max - min)'], ['RobustScaler', '(x - 중앙값) / IQR']],
    '세 공식은 서술형에 그대로 써야 하니 꼭 외워요.')

L.short('MinMaxScaler 로 데이터 `[20, 50, 80]` 을 학습(fit)했어요. 값 **35** 를 변환하면? (소수로)', '0.25',
    '(35 - 20) / (80 - 20) = 15 / 60 = 0.25.', alts=['1/4', '.25'],
    check_code='print((35 - 20) / (80 - 20))')

L.explain('fit 은 train 에만!',
    [T('스케일러에는 세 메서드가 있어요.\n'
       '- `fit(X)`: 평균·표준편차(또는 min·max) 같은 **기준을 계산해 기억**\n'
       '- `transform(X)`: 기억한 기준으로 **변환**\n'
       '- `fit_transform(X)`: 둘을 한 번에'),
     CMP(side('맞아요', 'train 으로 fit, test 는 transform 만', '''import numpy as np
from sklearn.preprocessing import StandardScaler
X_train = np.array([[1.0], [2.0], [3.0]])
X_test = np.array([[4.0]])
sc = StandardScaler()
X_train_s = sc.fit_transform(X_train)
X_test_s = sc.transform(X_test)
print(X_test_s.ravel().round(3))''', 'good'),
         side('틀려요', 'test 로 다시 fit — 기준이 바뀌고 정보가 샘', '''import numpy as np
from sklearn.preprocessing import StandardScaler
X_train = np.array([[1.0], [2.0], [3.0]])
X_test = np.array([[4.0]])
sc = StandardScaler()
X_train_s = sc.fit_transform(X_train)
X_test_s = sc.fit_transform(X_test)
print(X_test_s.ravel())''', 'bad'))],
    [T('test 는 "**미래에 들어올 새 데이터**" 역할이에요. 미래 데이터의 평균을 미리 알 수는 없죠.\n'
       'test 로 fit 하면 test 의 정보가 전처리에 섞여 평가가 실제보다 좋게 나올 수 있어요. 이걸 **데이터 누수**라고 해요.\n'
       '또 train 과 test 가 **서로 다른 기준**으로 바뀌어서 같은 값이 다른 숫자가 돼요.'),
     KEY('순서: ① split ② train 으로 fit ③ train·test 모두 그 기준으로 transform. 스케일링을 split **전에** 전체로 fit 해도 누수예요.')])

L.spot('데이터 누수가 생기는 줄은?', '''\
import numpy as np
from sklearn.preprocessing import MinMaxScaler
X_train = np.array([[10.0], [20.0], [30.0]])
X_test = np.array([[25.0], [40.0]])
scaler = MinMaxScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.fit_transform(X_test)
print(X_test_s.ravel())''', 7,
    '7번 줄이 test 로 다시 fit 해서 test 의 min·max 가 기준이 돼요. `scaler.transform(X_test)` 로 고쳐야 해요.')

L.ox('train 의 최솟값·최댓값으로 학습한 MinMaxScaler 로 test 를 변환하면, 결과가 0~1 범위를 벗어날 수도 있다.', True,
    'test 에 train 의 최댓값보다 큰 값이 있으면 1 보다 커지고, 최솟값보다 작으면 음수가 돼요. 이건 오류가 아니라 정상이에요.')

L.practice('[기출유사] 표준화·정규화 직접 계산',
'''한 특성의 값들이 한 줄에 주어져요(2개 이상, 모두 같지는 않음). StandardScaler 와 MinMaxScaler 의 결과를 직접 계산하세요.

**[조건]**
- 첫째 줄: 평균, 둘째 줄: 표준편차 — **n 으로 나눈** 표준편차 (StandardScaler 와 같게)
- 셋째 줄: 표준화 값 `(x - 평균) / 표준편차` 들
- 넷째 줄: MinMax 값 `(x - min) / (max - min)` 들
- 모든 실수는 `f"{값:.2f}"` 로, 여러 값은 공백으로 구분해요.

{ex}

{ex2}''',
'''data = list(map(float, input().split()))
n = len(data)
# 평균, 표준편차, 표준화, MinMax 를 출력하세요
''',
'''data = list(map(float, input().split()))
n = len(data)
mean = sum(data) / n
std = (sum((x - mean) ** 2 for x in data) / n) ** 0.5     # n 으로 나눔
lo, hi = min(data), max(data)
print(f"{mean:.2f}")
print(f"{std:.2f}")
print(*[f"{(x - mean) / std:.2f}" for x in data])          # StandardScaler
print(*[f"{(x - lo) / (hi - lo):.2f}" for x in data])      # MinMaxScaler''',
    ['1 2 3 4', '160 170 180 150 190'], ['0 10', '5 5 5 20', '-3 0 3 6 9 100'],
    ['표준편차는 `(sum((x - mean) ** 2 for x in data) / n) ** 0.5`. n-1 이 아니라 **n** 이에요.',
     '표준화 리스트: `[f"{(x - mean) / std:.2f}" for x in data]`.',
     'MinMax 는 `(x - lo) / (hi - lo)`. 최솟값은 0.00, 최댓값은 1.00 이 나와야 해요.'],
    '히든 테스트의 `-3 0 3 6 9 100` 을 보세요. 이상치 100 때문에 MinMax 값들이 0 근처로 몰려요. MinMax 가 이상치에 민감하다는 뜻이에요.')

L.practice('[기출유사] train 기준으로 test 변환',
'''첫째 줄은 train 값들, 둘째 줄은 test 값들이에요. MinMaxScaler 를 **train 으로만 fit** 한 뒤 train 과 test 를 모두 변환하세요.

**[조건]**
- 첫째 줄: `min max` — train 의 최솟값·최댓값 (입력 그대로 정수로)
- 둘째 줄: 변환한 train 값들, 셋째 줄: 변환한 test 값들 (`f"{값:.2f}"`, 공백 구분)
- 넷째 줄: test 중 0~1 범위를 **벗어난** 값의 개수
- train 값은 모두 같지는 않아요. 모든 값은 정수예요.

{ex}

{ex2}''',
'''train = list(map(int, input().split()))
test = list(map(int, input().split()))
# train 으로 fit, train/test 를 transform 하세요
''',
'''train = list(map(int, input().split()))
test = list(map(int, input().split()))
lo, hi = min(train), max(train)               # fit: train 에서만 기준 계산

def transform(v):
    return (v - lo) / (hi - lo)               # 같은 기준으로 변환

print(lo, hi)
print(*[f"{transform(v):.2f}" for v in train])
t = [transform(v) for v in test]
print(*[f"{v:.2f}" for v in t])
print(sum(1 for v in t if v < 0 or v > 1))''',
    ['10 20 30\n25 40', '0 50 100\n-10 50 120 100'], ['1 2\n1 2', '5 15\n0 10 20 30', '100 200 300 400\n150'],
    ['fit = `lo, hi = min(train), max(train)`. test 의 min·max 는 **쓰지 않아요**.',
     '`transform(v)` 함수를 만들어 train 과 test 모두에 적용해요.', '범위를 벗어난 값: `v < 0 or v > 1`.'],
    'test 에 train 범위 밖의 값이 있으면 0 보다 작거나 1 보다 커져요. 이게 정상이에요. test 로 다시 fit 하면 이 차이가 사라져 마치 0~1 에 딱 맞는 것처럼 보이지만, 실제 새 데이터를 다룰 때와 다른 조건으로 평가하게 돼요.')

L.essay('StandardScaler 를 **train 데이터로만 fit** 하고 test 데이터에는 transform 만 하는 이유를 서술하세요.',
    'test 데이터는 학습에 쓰지 않은 새로운 데이터로 모델의 일반화 성능을 평가하는 역할이다. test 로 fit 하면 test 의 평균과 표준편차라는 정보가 전처리에 들어가 데이터 누수가 생기고 평가 결과가 실제보다 좋게 나올 수 있다. 또 train 과 test 가 서로 다른 기준으로 변환되면 같은 값이 다른 숫자가 되어 모델이 학습한 기준과 맞지 않는다. 따라서 train 으로 구한 평균·표준편차로 train 과 test 를 모두 변환해야 한다.',
    ['test 는 새 데이터(일반화 평가) 역할', 'test 로 fit 하면 데이터 누수', '평가가 실제보다 좋게 나올 수 있다', 'train 과 같은 기준으로 변환해야 한다'])

# =====================================================================
L = C.lesson('ε-10 선형회귀: 가설 y = wx + b 와 MSE', 20,
'''- **회귀**: 연속적인 숫자를 예측 (공부시간 → 점수). 정답 y 가 있는 데이터로 배우는 **지도학습**.
- 가설(모델): `ŷ = w·x + b` — w 는 기울기(가중치), b 는 절편(편향).
- 오차 = `y - ŷ`. **MSE = (1/n) × Σ (y - ŷ)²** — 작을수록 좋은 직선.
- 제곱하는 이유: ① 부호 상쇄 방지 ② 큰 오차에 큰 벌점 ③ 미분하기 좋은 매끄러운 식.
- RMSE = √MSE (단위가 y 와 같아짐), MAE = 평균 |y - ŷ|.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간에는 `train_test_split` 으로 나누고, StandardScaler·MinMaxScaler·RobustScaler 로 범위를 맞췄어요.\n'
       '핵심은 **train 으로만 fit** 이었죠. 이제 드디어 **모델**을 만들어요.'),
     REVEAL('StandardScaler 의 공식은?', '`z = (x - 평균) / 표준편차` (sklearn 은 n 으로 나눈 표준편차). 결과의 평균은 0, 표준편차는 1.')])
L.short('복습: 데이터 `[2, 4, 6]` 의 평균은 4, 표준편차(n)는 약 1.633 이에요. 6 을 표준화한 값을 소수 둘째 자리까지 쓰세요.', '1.22',
    '(6 - 4) / 1.633 ≈ 1.22.', review=True,
    check_code='d = [2, 4, 6]\nm = sum(d) / 3\ns = (sum((x - m) ** 2 for x in d) / 3) ** 0.5\nprint(f"{(6 - m) / s:.2f}")')

L.explain('회귀란?',
    [T('**지도학습**은 입력 X 와 정답 y 가 함께 있는 데이터로 규칙을 배워요.\n'
       '그중 y 가 **연속적인 숫자**(점수·키·집값)면 **회귀**, y 가 **종류**(합격/불합격, 고양이/개)면 **분류**예요.\n'
       '이번 1차 범위는 회귀의 가장 기본인 **선형회귀**예요. (분류는 2차에서 다뤄요.)'),
     CMP(side('회귀', '숫자 예측: 공부시간 → 점수 85.3점'), side('분류', '종류 예측: 공부시간 → 합격 / 불합격'))])

L.bucket('회귀 / 분류 문제로 분류하세요.', ['회귀 (숫자 예측)', '분류 (종류 예측)'],
    [['내일 최고 기온 예측', 1], ['메일이 스팸인지 판별', 2], ['집 크기로 집값 예측', 1],
     ['사진 속 동물 종류 맞히기', 2], ['공부시간으로 시험 점수 예측', 1], ['시험 합격 여부 예측', 2]],
    '답이 "몇 점·몇 도·얼마" 면 회귀, "어느 쪽" 이면 분류예요.')

L.explain('가설: ŷ = wx + b',
    [T('선형회귀는 데이터를 가장 잘 지나가는 **직선**을 찾아요.\n'
       '이 직선 식 `ŷ = w·x + b` 를 **가설(hypothesis)** 이라고 해요. `ŷ`(와이 햇)은 **예측값**이에요.\n'
       '**w(가중치, weight)** 는 기울기: x 가 1 늘 때 ŷ 가 얼마나 느나. **b(편향, bias)** 는 절편: x = 0 일 때의 값.'),
     CODE('''w, b = 8, 53
hours = [1, 2, 3, 4, 5]
for x in hours:
    y_hat = w * x + b
    print(x, "시간 →", y_hat, "점")''', '가설로 예측하기')],
    [T('"학습" 이란 데이터에 가장 잘 맞는 **w 와 b 를 찾는 것**이에요.\n'
       '그러려면 "잘 맞는다" 를 숫자로 재는 기준이 필요해요 → **손실 함수**.'),
     KEY('특성이 여러 개면 `ŷ = w1·x1 + w2·x2 + … + b` 로 늘어나요. 원리는 같아요.')])

L.output('출력은?', '''\
def predict(x, w, b):
    return w * x + b
print(predict(3, 2, 1))
print(predict(0, 5, -4))
print([predict(x, 0.5, 10) for x in [2, 4]])''',
    '2×3+1 = 7, x 가 0 이면 b 만 남아 -4, 0.5×2+10 = 11.0 과 0.5×4+10 = 12.0.\n\n```\n{out}\n```')

L.choice('가설 `ŷ = 8x + 53` (x: 공부시간, ŷ: 예측 점수) 에서 **8** 의 뜻으로 알맞은 것은?',
    ['공부를 안 했을 때의 예측 점수', '공부시간이 1시간 늘 때 예측 점수가 늘어나는 양', '데이터의 개수', '예측의 평균 오차'], 2,
    '8 은 기울기 w — x 가 1 늘 때 ŷ 가 8 늘어요. 공부를 안 했을 때(x = 0) 의 예측 점수는 절편 b = 53 이에요.')

L.explain('오차와 MSE',
    [T('데이터 한 개의 **오차(잔차)** 는 `y - ŷ` (실제 - 예측) 이에요.\n'
       '오차를 그냥 더하면 +와 −가 **서로 지워져서** 엉망인 직선도 합이 0 이 될 수 있어요.\n'
       '그래서 오차를 **제곱해서 평균** 낸 **MSE(평균제곱오차)** 를 써요.'),
     CMP(side('오차를 그냥 더하면', '+5 와 -5 가 지워져 0 — 좋아 보이는 착각', 'y = [10, 20]\ny_hat = [15, 15]\nprint(sum(a - b for a, b in zip(y, y_hat)))', 'bad'),
         side('제곱해서 평균 (MSE)', '25 + 25 → 평균 25', 'y = [10, 20]\ny_hat = [15, 15]\nprint(sum((a - b) ** 2 for a, b in zip(y, y_hat)) / len(y))', 'good'))],
    [T('**MSE = (1/n) × Σ (y - ŷ)²**\n\n'
       '제곱의 장점 세 가지:\n'
       '① 음수가 없어 **부호 상쇄가 없어요**. ② 오차 2 는 4, 오차 10 은 100 — **큰 오차에 훨씬 큰 벌점**.\n'
       '③ 매끄러운 2차식이라 **미분해서 최솟값을 찾기 좋아요**(경사하강법).'),
     TABS(('MSE', '평균 (y - ŷ)². 제곱이라 단위도 제곱(점²).'),
          ('RMSE', '√MSE. 단위가 y 와 같아져 해석이 쉬워요.'),
          ('MAE', '평균 |y - ŷ|. 절댓값이라 이상치에 덜 민감해요.'))])

L.short('실제값 `y = [3, 5, 9]`, 예측값 `ŷ = [4, 5, 7]` 일 때 MSE 는? (소수 둘째 자리까지)', '1.67',
    '오차 -1, 0, 2 → 제곱 1, 0, 4 → 합 5 → 5 / 3 ≈ 1.67.', alts=['1.666', '1.667'],
    check_code='y = [3, 5, 9]\nh = [4, 5, 7]\nprint(f"{sum((a - b) ** 2 for a, b in zip(y, h)) / 3:.2f}")')

L.order('MSE 를 손으로 계산하는 순서대로 놓으세요.',
    ['가설로 각 x 의 예측값 ŷ 를 구한다', '오차 y - ŷ 를 구한다', '오차를 제곱한다', '제곱한 값을 모두 더한다', '데이터 개수 n 으로 나눈다'],
    '예측 → 오차 → 제곱 → 합 → 평균. 이름 그대로 "평균(Mean) 제곱(Squared) 오차(Error)" 를 거꾸로 따라가요.', mono=False)

L.fill('MSE 함수의 빈칸을 채우세요.', '''\
def mse(y, y_hat):
    total = 0
    for a, b in zip(y, y_hat):
        total += (a - b) ___ 2
    return total / ___(y)
print(mse([1, 2, 3], [2, 2, 2]))''', [['**'], ['len']],
    '오차를 제곱(`** 2`)해 더하고 개수(`len`)로 나눠요. (1 + 0 + 1) / 3 ≈ 0.667.', expect='0.6666666666666666')

L.explain('손실 함수의 모양',
    [T('데이터를 고정하고 w 만 바꿔 가며 MSE 를 그리면 **아래로 볼록한 U 자(2차 함수)** 모양이 돼요.\n'
       '바닥(최솟값) 하나가 가장 좋은 w 예요. 학습은 이 **바닥을 찾는 일**이에요.'),
     CODE('''x = [1, 2, 3]
y = [2, 4, 6]          # 정답 직선은 y = 2x
for w in [0, 1, 2, 3, 4]:
    mse = sum((yi - w * xi) ** 2 for xi, yi in zip(x, y)) / len(x)
    print("w =", w, " MSE =", round(mse, 2))''', 'w 에 따른 MSE (b = 0 고정)')],
    [T('w = 2 일 때 MSE 가 0 으로 가장 작고, 멀어질수록 같은 모양으로 커져요(w=1 과 w=3 이 같음).\n'
       '후보를 하나하나 다 넣어 보는 건 느리니까, 다음 시간에 **기울기를 따라 내려가는 방법(경사하강법)** 을 배워요.'),
     THINK('MSE 가 U 자 모양인 건 `(y - wx)²` 이 w 에 대한 **2차식**이기 때문이에요.')])

L.output('세 후보 직선 중 MSE 가 가장 작은 것을 고르는 코드예요. 출력은?', '''\
x = [1, 2, 3, 4]
y = [3, 5, 7, 9]
best = None
for w, b in [(1, 3), (2, 1), (3, -1)]:
    m = sum((yi - (w * xi + b)) ** 2 for xi, yi in zip(x, y)) / len(x)
    print(w, b, m)
    if best is None or m < best[2]:
        best = (w, b, m)
print("best:", best[0], best[1])''',
    '데이터는 정확히 y = 2x + 1 위에 있어서 (2, 1) 의 MSE 가 0 이에요.\n\n```\n{out}\n```')

L.practice('[기출유사] 어느 직선이 가장 잘 맞을까',
'''공부시간 x 와 점수 y 데이터, 그리고 후보 직선 k개가 주어져요. 각 직선의 MSE 를 계산하고 가장 좋은 직선을 고르세요.

**[조건]**
- 첫째 줄: x 값들, 둘째 줄: 같은 개수의 y 값들 (정수)
- 셋째 줄: 후보 수 k, 다음 k줄: 정수 `w b`
- 후보마다 한 줄: `w b MSE` (MSE 는 `f"{값:.2f}"`)
- 마지막 줄: `최적: w b` — MSE 가 가장 작은 후보 (같으면 먼저 나온 것)
- MSE 는 함수로 만들어 쓰세요.

{ex}

{ex2}''',
'''x = list(map(int, input().split()))
y = list(map(int, input().split()))
k = int(input())

def mse(w, b):
    # MSE 를 돌려주세요
    return 0
''',
'''x = list(map(int, input().split()))
y = list(map(int, input().split()))
k = int(input())

def mse(w, b):
    total = 0
    for xi, yi in zip(x, y):
        total += (yi - (w * xi + b)) ** 2   # (실제 - 예측)²
    return total / len(x)

best = None
for _ in range(k):
    w, b = map(int, input().split())
    m = mse(w, b)
    print(w, b, f"{m:.2f}")
    if best is None or m < best[2]:        # 더 작을 때만 바꿔요
        best = (w, b, m)
print("최적:", best[0], best[1])''',
    ['1 2 3 4\n60 70 75 85\n3\n10 50\n8 53\n5 60', '2 4 6\n5 9 13\n2\n2 1\n1 3'],
    ['5\n7\n2\n1 2\n0 7', '1 2\n0 0\n2\n1 0\n-1 0', '1 2 3\n2 2 2\n3\n0 2\n1 0\n0 3'],
    ['`mse(w, b)` 는 모든 (xi, yi) 에 대해 `(yi - (w * xi + b)) ** 2` 를 더해 개수로 나눠요.',
     '후보를 읽을 때마다 MSE 를 계산해 출력하고, 지금까지의 최솟값과 비교해요.',
     '`if best is None or m < best[2]:` 로 **더 작을 때만** 바꾸면 동점일 때 먼저 나온 후보가 남아요.'],
    'MSE 는 "직선이 데이터에서 얼마나 벗어났나" 를 하나의 숫자로 만든 것이라, 직선끼리 비교할 수 있게 해 줘요. 실제 학습은 후보를 사람이 주지 않고 경사하강법으로 w, b 를 찾아가요.')

L.essay('선형회귀의 손실 함수로 오차의 합 대신 **MSE(오차 제곱의 평균)** 를 쓰는 이유를 두 가지 이상 서술하세요.',
    '오차를 그냥 더하면 양수 오차와 음수 오차가 서로 상쇄되어 예측이 크게 틀려도 합이 0에 가까울 수 있다. 제곱하면 모든 값이 0 이상이 되어 상쇄가 일어나지 않는다. 또 제곱은 큰 오차에 더 큰 벌점을 주어 크게 틀린 예측을 줄이도록 하고, 매끄러운 2차식이 되어 미분으로 기울기를 구해 경사하강법으로 최솟값을 찾기 좋다.',
    ['그냥 더하면 부호가 상쇄된다', '제곱하면 모두 0 이상', '큰 오차에 큰 벌점', '미분 가능한 매끄러운 식(경사하강법에 유리)'])

# =====================================================================
L = C.lesson('ε-11 경사하강법 · 정규방정식 · R²', 30,
'''- **경사하강법**: 손실의 기울기(미분)의 **반대 방향**으로 조금씩 이동. `w ← w - α × ∂MSE/∂w`.
- `∂MSE/∂w = (2/n) × Σ (ŷ - y)·x`, `∂MSE/∂b = (2/n) × Σ (ŷ - y)`. α(학습률)가 너무 크면 발산, 너무 작으면 느림.
- **정규방정식**: 반복 없이 한 번에 `w = (XᵀX)⁻¹ Xᵀ y`. 특성이 하나면 `w = Σ(x-x̄)(y-ȳ) / Σ(x-x̄)²`, `b = ȳ - w·x̄`.
- sklearn `LinearRegression()` → `fit` · `predict` · `coef_`(w) · `intercept_`(b) · `score`(R²).
- **R² = 1 - Σ(y - ŷ)² / Σ(y - ȳ)²**. 1 이면 완벽, 0 이면 평균만 찍는 수준, 음수도 가능.''')

L.review('🔁 지난 시간 복습',
    [T('지난 시간에는 가설 `ŷ = wx + b` 와 손실 `MSE = (1/n) Σ (y - ŷ)²` 를 배웠어요.\n'
       'MSE 는 w 에 대해 U 자 모양이라 바닥 하나를 찾으면 돼요. 오늘은 그 바닥을 찾는 두 방법과 모델 평가 지표 R² 를 배워요.'),
     REVEAL('MSE 에서 오차를 제곱하는 이유 세 가지는?', '① 부호 상쇄 방지 ② 큰 오차에 큰 벌점 ③ 미분하기 좋은 매끄러운 식')])
L.output('복습: 출력은?', 'y = [4, 6]\ny_hat = [5, 3]\nprint(sum((a - b) ** 2 for a, b in zip(y, y_hat)) / 2)',
    '오차 -1, 3 → 제곱 1, 9 → 평균 {out}', review=True)

L.explain('경사하강법의 아이디어',
    [T('안개 낀 산에서 눈을 가리고 골짜기로 내려가려면, 발밑의 **경사**를 느끼고 **내려가는 쪽**으로 한 걸음씩 가면 돼요.\n'
       '손실 함수 그래프에서 경사 = **미분(기울기)** 이에요.\n'
       '기울기가 양수면 w 를 줄이고, 음수면 w 를 늘려요. 즉 **기울기의 반대 방향**으로 움직여요.'),
     KEY('갱신 규칙: `w ← w - α × (손실을 w 로 미분한 값)`. α(알파)는 한 걸음 크기 = **학습률(learning rate)**.')],
    [T('MSE 를 w, b 로 미분하면(합성함수 미분) 이렇게 돼요.\n\n'
       '- `∂MSE/∂w = (2/n) × Σ (ŷ - y) × x`\n'
       '- `∂MSE/∂b = (2/n) × Σ (ŷ - y)`\n\n'
       '`(y - ŷ)²` 을 미분하면 `2(y - ŷ) × (-x)` = `2(ŷ - y) × x` 가 돼서 이런 모양이 나와요.'),
     EXAM('기울기 식에서 **x 가 곱해지는 쪽은 w**, b 쪽은 x 가 없어요. 빈칸·서술형에서 자주 헷갈리는 부분이에요.')])

L.explain('경사하강법을 손으로 따라가기',
    [T('데이터 x = [1, 2, 3], y = [2, 4, 6] (정답 w = 2, b = 0) 에서 w = 0, b = 0 으로 시작해 봐요.\n'
       '학습률 α = 0.1 로 세 번 갱신해요.'),
     TRACE('''x = [1, 2, 3]
y = [2, 4, 6]
w, b, lr = 0.0, 0.0, 0.1
n = len(x)
for step in range(3):
    gw, gb = 0.0, 0.0
    for xi, yi in zip(x, y):
        err = (w * xi + b) - yi       # ŷ - y
        gw += 2 * err * xi / n
        gb += 2 * err / n
    w = w - lr * gw                   # 기울기 반대로
    b = b - lr * gb
    print(step + 1, round(w, 3), round(b, 3))''', '경사하강법 3스텝', notes={'8': '예측 - 실제', '11': 'w 갱신: 기울기 반대 방향'})],
    [T('첫 스텝에서 예측이 모두 0 이라 오차가 음수 → 기울기가 음수 → w 가 **커져요**.\n'
       '1 스텝 뒤 w = 0 - 0.1 × (-18.667) ≈ 1.867. 바닥(2) 근처로 금방 다가가요.'),
     TIP('기울기는 **모든 데이터의 오차를 다 모은 뒤** 한 번에 w, b 를 갱신해요. w 를 먼저 바꾸고 그 w 로 b 의 기울기를 구하면 다른 결과가 돼요.')])

L.output('경사하강법 1스텝 후 w 와 b 는?', '''\
x = [1, 2]
y = [3, 5]
w, b, lr = 0.0, 0.0, 0.1
gw = sum(2 * ((w * xi + b) - yi) * xi for xi, yi in zip(x, y)) / len(x)
gb = sum(2 * ((w * xi + b) - yi) for xi, yi in zip(x, y)) / len(x)
w -= lr * gw
b -= lr * gb
print(round(gw, 2), round(gb, 2))
print(round(w, 2), round(b, 2))''',
    'gw = (2/2)×[(0-3)×1 + (0-5)×2] = -13, gb = (2/2)×[(0-3)+(0-5)] = -8. w = 0 - 0.1×(-13) = 1.3, b = 0.8.\n\n```\n{out}\n```')

L.explain('학습률 α 고르기',
    [T('학습률은 한 걸음의 크기예요. 직접 정해 주는 값(**하이퍼파라미터**)이에요.\n'
       '너무 작으면 바닥까지 **아주 오래** 걸리고, 너무 크면 바닥을 **건너뛰며 튕겨 나가** 손실이 오히려 커질 수 있어요(발산).'),
     CMP(side('α = 0.05 (적당)', 'w 가 2 로 점점 다가가요', 'x, y = [1, 2, 3], [2, 4, 6]\nw = 0.0\nfor _ in range(5):\n    g = sum(2 * (w * a - c) * a for a, c in zip(x, y)) / 3\n    w -= 0.05 * g\n    print(round(w, 3))', 'good'),
         side('α = 0.5 (너무 큼)', 'w 가 2 를 넘나들며 점점 멀어져요', 'x, y = [1, 2, 3], [2, 4, 6]\nw = 0.0\nfor _ in range(5):\n    g = sum(2 * (w * a - c) * a for a, c in zip(x, y)) / 3\n    w -= 0.5 * g\n    print(round(w, 3))', 'bad'))],
    [T('전체 데이터를 한 번 다 써서 학습하는 것을 **1 에포크(epoch)** 라고 불러요. 위 코드는 반복 한 번이 1 에포크예요.\n'
       '특성들의 범위가 크게 다르면 경사가 한쪽으로 치우쳐 학습이 불안정해져요. 그래서 경사하강법 전에 **스케일링**을 해요.'),
     KEY('α 크다 → 발산·진동, α 작다 → 느림. 반복 횟수가 모자라면 바닥에 못 닿아요.')])

L.bucket('상황에 맞는 원인을 분류하세요.', ['학습률이 너무 큼', '학습률이 너무 작음'],
    [['손실이 줄지 않고 점점 커진다', 1], ['손실이 아주 천천히 줄어든다', 2], ['w 가 정답 양쪽을 크게 오가며 멀어진다', 1],
     ['1000번 반복해도 아직 바닥에서 멀다', 2]],
    '튕겨 나가면 큰 것, 거북이처럼 느리면 작은 것!')

L.explain('정규방정식: 한 번에 구하기',
    [T('MSE 를 미분한 값이 0 이 되는 w, b 를 **식으로 바로** 풀 수도 있어요. 이것이 **정규방정식**이에요.\n'
       '반복도 학습률도 필요 없어요.\n'
       '특성이 하나일 때는 이렇게 정리돼요.\n\n'
       '- `w = Σ(x - x̄)(y - ȳ) / Σ(x - x̄)²`\n- `b = ȳ - w × x̄`'),
     CODE('''x = [2, 5, 3, 1, 4, 3]
y = [70, 92, 81, 60, 88, 75]
n = len(x)
mx, my = sum(x) / n, sum(y) / n
w = sum((a - mx) * (c - my) for a, c in zip(x, y)) / sum((a - mx) ** 2 for a in x)
b = my - w * mx
print(round(w, 3), round(b, 3))''', '공식으로 w, b 구하기 (예제 표의 hours → score)')],
    [T('특성이 여러 개면 행렬로 써요. X 맨 앞에 1 로 된 열을 붙여(절편 b 용) `θ = (XᵀX)⁻¹ Xᵀ y`.'),
     CODE('''import numpy as np
x = np.array([2, 5, 3, 1, 4, 3])
y = np.array([70, 92, 81, 60, 88, 75])
X = np.column_stack([np.ones(len(x)), x])     # [1, x] 열
theta = np.linalg.inv(X.T @ X) @ X.T @ y       # (XᵀX)⁻¹ Xᵀ y
print(theta.round(3))                          # [b, w]''', '정규방정식 numpy (읽기 전용)', run_=False),
     CMP(side('경사하강법', '반복해서 조금씩 · 학습률·반복 횟수 정해야 함 · 데이터·특성이 많아도 사용 가능'),
         side('정규방정식', '한 번에 정확한 해 · 학습률 필요 없음 · 특성이 아주 많으면 역행렬 계산이 무거움'))])

L.match('방법과 특징을 이어 보세요.',
    [['경사하강법', '학습률을 정하고 반복해서 갱신'], ['정규방정식', '역행렬 계산으로 한 번에 해'], ['학습률', '한 걸음의 크기'], ['에포크', '전체 데이터를 한 번 다 사용']],
    '"반복 vs 한 번에" 가 둘의 가장 큰 차이예요.')

L.explain('sklearn LinearRegression',
    [T('sklearn 에서는 몇 줄이면 돼요. `fit(X, y)` 로 학습하고 `predict(X)` 로 예측해요.\n'
       '학습된 기울기는 `coef_`(배열), 절편은 `intercept_` 에 들어 있어요. 이름 끝의 **밑줄 `_`** 은 "학습으로 얻은 값" 이라는 뜻이에요.\n'
       '`LinearRegression` 은 경사하강법처럼 반복하지 않고 최소제곱 해를 바로 계산해요.'),
     CODE(DF_SRC + '''
from sklearn.linear_model import LinearRegression
X = df[["hours"]]               # 2차원!
y = df["score"]
model = LinearRegression()
model.fit(X, y)
print(model.coef_, round(model.intercept_, 3))
print(model.predict(pd.DataFrame({"hours": [6]})).round(2))
print(round(model.score(X, y), 3))      # R²''', 'LinearRegression (읽기 전용)', run_=False),
     WARN('`X` 는 2차원(`df[["hours"]]`) 이어야 해요. `df["hours"]` 처럼 1차원을 넣으면 오류가 나요.')])

L.output('출력은? (위 공식 코드와 같은 데이터)', DF_SRC + '''
from sklearn.linear_model import LinearRegression
model = LinearRegression()
model.fit(df[["hours"]], df["score"])
print(model.coef_[0])
print(round(model.intercept_, 2))''',
    '기울기 8.2 — 공부시간이 1시간 늘면 점수가 약 8.2점 오른다는 뜻. 절편 약 53.07. 위에서 공식으로 손 계산한 값과 같아요.\n\n```\n{out}\n```')

L.explain('R² (결정계수)',
    [T('MSE 는 y 의 단위에 따라 크기가 달라서 "좋은지" 바로 알기 어려워요. 그래서 **R²** 를 함께 봐요.\n\n'
       '**R² = 1 - Σ(y - ŷ)² / Σ(y - ȳ)²**\n\n'
       '분모는 "**평균 ȳ 하나로만** 예측했을 때의 오차", 분자는 "모델의 오차" 예요.\n'
       '즉 R² 는 평균만 찍는 것보다 오차를 **얼마나 줄였나**의 비율이에요.'),
     STEPS(('R² = 1', '모든 점을 정확히 맞힘 (분자 0)'), ('R² = 0', '평균으로 찍는 것과 같은 수준'),
           ('R² < 0', '평균으로 찍는 것보다도 나쁨 (가능해요!)'), ('regressor.score()', 'sklearn 회귀 모델의 `score(X, y)` 는 R² 를 돌려줘요'))],
    [T('예: y = [2, 4, 6], ŷ = [3, 4, 5]. ȳ = 4.\n'
       '분자 = 1 + 0 + 1 = 2, 분모 = 4 + 0 + 4 = 8 → R² = 1 - 2/8 = **0.75**.'),
     WARN('R² 는 test 데이터로도 꼭 확인해요. train 의 R² 만 높고 test 가 낮으면 외워 버린 모델일 수 있어요.')])

L.short('y = [1, 3, 5, 7], ŷ = [2, 3, 5, 6] 일 때 R² 는? (소수 둘째 자리까지)', '0.9',
    'ȳ = 4. 분자 = 1 + 0 + 0 + 1 = 2, 분모 = 9 + 1 + 1 + 9 = 20 → 1 - 2/20 = 0.90.', alts=['0.90', '.9'],
    check_code='y = [1, 3, 5, 7]\nh = [2, 3, 5, 6]\nm = sum(y) / 4\nprint(round(1 - sum((a - b) ** 2 for a, b in zip(y, h)) / sum((a - m) ** 2 for a in y), 2))')

L.ox('모든 예측값을 y 의 평균 ȳ 로 똑같이 내놓는 모델의 R² 는 0 이다.', True,
    'ŷ = ȳ 이면 분자와 분모가 같아져서 1 - 1 = 0 이에요. 그래서 R² 0 을 "평균 수준" 이라고 해요.')

L.practice('[기출유사] 경사하강법 k 스텝',
'''x, y 데이터로 `ŷ = wx + b` 를 경사하강법으로 학습해요. w = 0, b = 0 에서 시작해요.

**[조건]**
- 첫째 줄: x 값들, 둘째 줄: y 값들, 셋째 줄: `학습률 반복횟수`
- 기울기: `gw = (2/n) × Σ(ŷ - y)·x`, `gb = (2/n) × Σ(ŷ - y)` — **현재 w, b 로 모두 계산한 뒤** 동시에 갱신
- 갱신: `w = w - 학습률 × gw`, `b = b - 학습률 × gb`
- 매 스텝 한 줄: `스텝번호 w b` (w, b 는 `f"{값:.4f}"`)
- 마지막 줄: `MSE 값` — 마지막 w, b 의 MSE (`f"{값:.4f}"`)

{ex}

{ex2}''',
'''x = list(map(float, input().split()))
y = list(map(float, input().split()))
lr, k = input().split()
lr, k = float(lr), int(k)
n = len(x)
w, b = 0.0, 0.0
# 경사하강법을 k 번 반복하세요
''',
'''x = list(map(float, input().split()))
y = list(map(float, input().split()))
lr, k = input().split()
lr, k = float(lr), int(k)
n = len(x)
w, b = 0.0, 0.0
for step in range(1, k + 1):
    gw, gb = 0.0, 0.0
    for xi, yi in zip(x, y):
        err = (w * xi + b) - yi          # ŷ - y
        gw += 2 * err * xi / n
        gb += 2 * err / n
    w, b = w - lr * gw, b - lr * gb      # 동시에 갱신
    print(step, f"{w:.4f}", f"{b:.4f}")
mse = sum((yi - (w * xi + b)) ** 2 for xi, yi in zip(x, y)) / n
print("MSE", f"{mse:.4f}")''',
    ['1 2 3\n2 4 6\n0.1 3', '1 2\n3 5\n0.1 2'], ['1\n1\n0.5 1', '0 1 2 3\n1 3 5 7\n0.05 4', '1 2 3\n2 4 6\n0.5 3'],
    ['한 스텝 안에서 `gw`, `gb` 를 0 으로 두고 모든 데이터의 `err = (w * xi + b) - yi` 로 더해요.',
     '`gw += 2 * err * xi / n`, `gb += 2 * err / n`.',
     '갱신은 `w, b = w - lr * gw, b - lr * gb` 로 동시에. 반복이 끝난 뒤 MSE 를 계산해요.'],
    '히든 테스트의 `0.5` 학습률은 일부러 너무 크게 잡았어요. w, b 가 점점 커지며 MSE 가 폭발하는 **발산**을 확인할 수 있어요.')

L.practice('[기출유사] 공식으로 회귀선 + R²',
'''정규방정식(특성 하나)으로 회귀선을 한 번에 구하고 R² 로 평가해요.

**[조건]**
- 첫째 줄: x 값들, 둘째 줄: y 값들 (x 끼리, y 끼리 모두 같지는 않아요)
- `w = Σ(x - x̄)(y - ȳ) / Σ(x - x̄)²`, `b = ȳ - w × x̄`
- `R² = 1 - Σ(y - ŷ)² / Σ(y - ȳ)²`
- 출력: 첫째 줄 `w`, 둘째 줄 `b`, 셋째 줄 `R²` — 모두 `f"{값:.3f}"`
- 넷째 줄: R² ≥ 0.8 이면 `설명력 높음`, 아니면 `설명력 낮음`

{ex}

{ex2}''',
'''x = list(map(float, input().split()))
y = list(map(float, input().split()))
n = len(x)
# w, b, R² 를 구하세요
''',
'''x = list(map(float, input().split()))
y = list(map(float, input().split()))
n = len(x)
mx, my = sum(x) / n, sum(y) / n
w = sum((a - mx) * (c - my) for a, c in zip(x, y)) / sum((a - mx) ** 2 for a in x)
b = my - w * mx                                         # 절편
pred = [w * a + b for a in x]                           # ŷ
ss_res = sum((c - p) ** 2 for c, p in zip(y, pred))     # 모델 오차
ss_tot = sum((c - my) ** 2 for c in y)                  # 평균으로 찍은 오차
r2 = 1 - ss_res / ss_tot
print(f"{w:.3f}")
print(f"{b:.3f}")
print(f"{r2:.3f}")
print("설명력 높음" if r2 >= 0.8 else "설명력 낮음")''',
    ['2 5 3 1 4 3\n70 92 81 60 88 75', '1 2 3 4 5\n3 5 7 9 11'], ['1 2\n5 1', '1 2 3 4\n2 1 4 3', '10 20 30 40 50\n15 11 40 22 30'],
    ['먼저 평균 `mx`, `my`. w 의 분자는 `(a - mx) * (c - my)` 의 합, 분모는 `(a - mx) ** 2` 의 합.',
     '`b = my - w * mx`. 예측 `pred = [w * a + b for a in x]`.',
     'R² 는 `1 - ss_res / ss_tot`. ss_tot 은 y 와 평균의 차이 제곱합이에요.'],
    '첫 예시는 예제 표 데이터라 sklearn `LinearRegression` 결과(w = 8.2, b ≈ 53.067, R² ≈ 0.959)와 같아요. 두 번째 예시는 점이 정확히 직선 위에 있어 R² = 1 이에요.')

L.essay('선형회귀에서 **경사하강법**과 **정규방정식**으로 w, b 를 구하는 방식의 차이를 서술하세요. (계산 방식, 학습률 필요 여부, 장단점 포함)',
    '경사하강법은 손실 함수의 기울기를 구해 기울기의 반대 방향으로 w 와 b 를 학습률만큼 조금씩 반복해서 갱신하며 최솟값에 다가간다. 학습률과 반복 횟수를 정해야 하고 학습률이 크면 발산, 작으면 느리지만 특성과 데이터가 많아도 쓸 수 있다. 정규방정식은 손실의 미분이 0 이 되는 해를 (XᵀX)⁻¹Xᵀy 로 한 번에 계산하므로 반복과 학습률이 필요 없고 정확한 해를 얻지만, 특성이 매우 많으면 역행렬 계산 비용이 커진다.',
    ['경사하강법은 기울기 반대 방향으로 반복 갱신', '학습률·반복 횟수가 필요', '정규방정식은 한 번에 계산 (XᵀX)⁻¹Xᵀy', '특성이 많으면 역행렬 계산이 무겁다'])

L.essay('어떤 회귀 모델의 R² 가 0 이 나왔어요. 이것이 무슨 뜻인지 R² 식과 연결해 서술하세요.',
    'R² = 1 - Σ(y - ŷ)² / Σ(y - ȳ)² 이다. R² 가 0 이면 모델의 오차 제곱합이 모든 값을 평균 ȳ 로 예측했을 때의 오차 제곱합과 같다는 뜻이므로, 이 모델은 평균값 하나로 예측하는 것보다 나을 것이 없다(설명력이 없다).',
    ['R² = 1 - Σ(y-ŷ)²/Σ(y-ȳ)²', '모델 오차 = 평균 예측의 오차', '평균으로 찍는 것과 같은 수준', '설명력이 없다'])

if __name__ == '__main__':
    C.save(sys.argv[1] if len(sys.argv) > 1 else '/tmp/epsilon.json')
