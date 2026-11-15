from plib import *
T = 'while·상태 변수 시뮬레이션'
P(T, 'UP AND DOWN 범위 좁히기', 'I', '1부터 100 사이의 비밀 숫자를 맞히는 게임이다. 플레이어가 숫자를 부를 때마다 판정과 함께 **지금까지의 정보로 가능한 범위**를 알려 준다. 처음 범위는 1~100 이다.\n\n부른 수가 비밀 숫자보다 작으면 `UP`, 크면 `DOWN` 이다. `UP` 이면 범위의 아래 끝이, `DOWN` 이면 위 끝이 좁혀질 수 있다. 이미 알고 있는 범위 밖의 수를 불러도 판정은 하지만 범위는 넓어지지 않는다.',
  '첫 줄에 비밀 숫자, 둘째 줄에 플레이어가 부른 수들이 공백으로 구분되어 주어진다. (1개 이상 20개 이하, 모두 1~100)', '부를 때마다 `UP (L~H)` 또는 `DOWN (L~H)` 를 한 줄씩 출력한다. 맞히면 `정답! N번` 을 출력하고 종료한다(뒤의 수는 무시). 끝까지 못 맞히면 마지막 줄에 `실패 (L~H)` 를 출력한다.',
  'ans = int(input())\ngs = list(map(int, input().split()))\nlo, hi = 1, 100\nn = 0\nhit = False\nfor g in gs:\n    n += 1\n    if g == ans:\n        print(f"정답! {n}번")\n        hit = True\n        break\n    if g < ans:\n        if g + 1 > lo:\n            lo = g + 1\n        print(f"UP ({lo}~{hi})")\n    else:\n        if g - 1 < hi:\n            hi = g - 1\n        print(f"DOWN ({lo}~{hi})")\nif not hit:\n    print(f"실패 ({lo}~{hi})")',
  ['37\n50 25 37 1', '80\n50 90 60 95', '1\n1', '100\n1 2 99', '42\n50 60 30 20 41 43', '7\n100 1 50 8 6 7 7'], gen=lambda r: f"{r.randint(1,100)}\n{RL(r, r.randint(1,10), 1, 100)}", k=5)
P(T, '기숙사 도어락', 'I', '기숙사 도어락은 비밀번호를 **연속으로 3번** 틀리면 잠긴다. 중간에 맞히면 문이 열리고 연속 실패 횟수는 0으로 돌아간다. 문이 열린 뒤에도 다음 사람이 계속 번호를 누를 수 있다. 잠긴 뒤에 누른 번호는 모두 무시한다.',
  '첫 줄에 비밀번호(숫자 4자리 문자열), 둘째 줄에 누른 횟수 `n` (1 ≤ n ≤ 50), 이어서 n줄에 누른 번호가 주어진다.', '누를 때마다 맞으면 `열림`, 틀리면 `틀림 K` (K 는 현재 연속 실패 횟수)를 출력한다. 3번째 연속 실패 때는 `틀림 3` 다음 줄에 `잠김` 을 출력하고 더 이상 출력하지 않는다. 마지막 줄에 문이 열린 총 횟수를 출력한다.',
  'pw = input()\nn = int(input())\nfails = 0\nopened = 0\nlocked = False\ni = 0\nwhile i < n:\n    x = input()\n    i += 1\n    if locked:\n        continue\n    if x == pw:\n        print("열림")\n        opened += 1\n        fails = 0\n    else:\n        fails += 1\n        print(f"틀림 {fails}")\n        if fails == 3:\n            print("잠김")\n            locked = True\nprint(opened)',
  ['0425\n5\n1111\n0425\n2222\n3333\n0425', '1234\n4\n1\n2\n3\n1234', '0000\n1\n0000', '9999\n6\n1\n2\n9999\n3\n4\n9999', '5555\n3\n5555\n5555\n5555', '0425\n7\n425\n4250\n0425\n0000\n1111\n2222\n0425'])
P(T, '매점 계좌 입출금', 'I', '매점 계좌 프로그램이다. 처음 잔액이 주어지고, 명령을 한 줄씩 처리한다.\n\n`입금 x` : x 원을 넣는다. `출금 x` : 잔액이 x 원 이상일 때만 뺀다. `조회` : 잔액을 알려 준다. `종료` : 프로그램을 끝낸다.',
  '첫 줄에 처음 잔액(0 이상 10^6 이하), 둘째 줄부터 명령이 한 줄씩 주어진다. 마지막 명령은 항상 `종료` 이다. 금액은 1 이상 10^6 이하의 정수이다.', '`입금` 은 `입금 완료: 잔액 N원`, `출금` 은 성공하면 `출금 완료: 잔액 N원`, 실패하면 `잔액 부족: D원 모자람`, `조회` 는 `잔액 N원` 을 출력한다. `종료` 를 만나면 `거래 K건` (성공한 입금과 출금의 수)을 출력하고 끝낸다.',
  'bal = int(input())\ncnt = 0\nwhile True:\n    line = input().split()\n    if line[0] == "종료":\n        print(f"거래 {cnt}건")\n        break\n    if line[0] == "조회":\n        print(f"잔액 {bal}원")\n    elif line[0] == "입금":\n        bal += int(line[1])\n        cnt += 1\n        print(f"입금 완료: 잔액 {bal}원")\n    else:\n        x = int(line[1])\n        if x > bal:\n            print(f"잔액 부족: {x - bal}원 모자람")\n        else:\n            bal -= x\n            cnt += 1\n            print(f"출금 완료: 잔액 {bal}원")',
  ['1000\n입금 500\n출금 2000\n출금 1500\n조회\n종료', '0\n종료', '0\n출금 1\n조회\n종료', '5000\n출금 5000\n출금 1\n입금 1\n출금 1\n종료', '100\n조회\n조회\n입금 1000000\n조회\n종료', '777\n출금 700\n출금 70\n출금 7\n출금 7\n종료'])
P(T, '거꾸로 읽어도 같은 수', 'B', '자연수 `n` 의 자릿수를 뒤집은 수를 구하고, 원래 수와 같은지(회문수인지) 판별하시오. 뒤집은 수의 앞에 오는 0은 사라진다. (예: 1200 → 21)',
  '자연수 `n` 이 주어진다. (1 ≤ n ≤ 10^18)', '첫 줄에 뒤집은 수, 둘째 줄에 회문수이면 `YES`, 아니면 `NO` 를 출력한다.',
  'n = int(input())\nm = n\nrev = 0\nwhile m > 0:\n    rev = rev * 10 + m % 10\n    m //= 10\nprint(rev)\nif rev == n:\n    print("YES")\nelse:\n    print("NO")',
  ['1234', '1221', '7', '1200', '1000000000000000001', '10', '12321', '999999999999999998'], gen=lambda r: R(r, 1, 10**6), cond=['문자열로 바꾸지 말고 `while` 과 `%`, `//` 를 사용할 것'])
P(T, '물 마시기 챌린지', 'I', '하루 물 섭취 목표는 `g` 리터이다. 컵 크기가 다른 컵 여러 개를 **주어진 순서대로 반복해서** 사용해 물을 마신다. (마지막 컵 다음에는 다시 첫 컵) 마신 양이 목표 **이상**이 되면 멈춘다.',
  '첫 줄에 목표 `g` (0.1 이상 10.0 이하, 소수 첫째 자리까지), 둘째 줄에 컵들의 크기(mL, 50 이상 1000 이하의 정수)가 공백으로 구분되어 주어진다. (1개 이상 10개 이하)', '첫 줄에 마신 잔 수, 둘째 줄에 마신 총량(mL), 셋째 줄에 목표를 초과한 양(mL)을 출력한다.',
  'g = input()\ncups = list(map(int, input().split()))\nwhole, frac = g.split(".")\ngoal = int(whole) * 1000 + int(frac) * 100\ndrank = 0\ncnt = 0\nwhile drank < goal:\n    drank += cups[cnt % len(cups)]\n    cnt += 1\nprint(cnt)\nprint(drank)\nprint(drank - goal)',
  ['2.0\n300', '1.5\n500 200', '0.1\n1000', '10.0\n50', '0.3\n100 100 100 100', '2.3\n250 330 500', '0.7\n350'], gen=lambda r: f"{r.randint(0,4)}.{r.randint(1,9)}\n{' '.join(str(r.randint(1,10)*50) for _ in range(r.randint(1,4)))}", cond=['실수 오차를 피하기 위해 목표량을 **mL 단위의 정수**로 바꾸어 계산할 것'])
P(T, '우박수 여행', 'B', '자연수 `n` 에서 시작해 다음 규칙을 1이 될 때까지 반복한다. 짝수이면 2로 나누고, 홀수이면 3을 곱한 뒤 1을 더한다.',
  '자연수 `n` 이 주어진다. (1 ≤ n ≤ 100000)', '첫 줄에 1이 될 때까지 계산한 **횟수**, 둘째 줄에 과정에서 나온 수(시작 수 포함) 중 **가장 큰 수**를 출력한다.',
  'n = int(input())\ncnt = 0\nbest = n\nwhile n != 1:\n    if n % 2 == 0:\n        n //= 2\n    else:\n        n = n * 3 + 1\n    cnt += 1\n    if n > best:\n        best = n\nprint(cnt)\nprint(best)',
  ['6', '1', '2', '27', '100000', '97', '7', '99999'], gen=lambda r: R(r, 1, 3000))
P(T, '한 자리가 될 때까지', 'I', '자연수 `n` 의 각 자리 숫자를 모두 더한다. 결과가 한 자리 수가 될 때까지 이 과정을 반복한다.',
  '자연수 `n` 이 주어진다. (1 ≤ n ≤ 10^18)', '각 단계의 결과를 한 줄씩 출력한다(처음 수는 출력하지 않는다). 처음부터 한 자리 수이면 그 수를 그대로 한 줄 출력한다. 마지막 줄에 자릿수 합을 구한 횟수를 출력한다.',
  'n = int(input())\ncnt = 0\nif n < 10:\n    print(n)\nwhile n >= 10:\n    s = 0\n    while n > 0:\n        s += n % 10\n        n //= 10\n    n = s\n    cnt += 1\n    print(n)\nprint(cnt)',
  ['9875', '5', '10', '999999999999999999', '19', '199', '100000'], gen=lambda r: R(r, 1, 10**9))
P(T, '용돈 모으기', 'B', '갖고 싶은 물건의 가격은 `p` 원이다. 첫 주에 `a` 원을 저금하고, 매주 전 주보다 `d` 원씩 더 많이 저금한다. 저금한 돈이 `p` 원 이상이 되는 것은 몇 주째인지 구하시오.',
  '한 줄에 `p a d` 가 주어진다. (1 ≤ p ≤ 10^7, 1 ≤ a ≤ 10^5, 0 ≤ d ≤ 10^4)', '첫 줄에 걸린 주 수, 둘째 줄에 그때까지 모은 금액을 출력한다.',
  'p, a, d = map(int, input().split())\nsaved = 0\nweek = 0\nwhile saved < p:\n    saved += a + d * week\n    week += 1\nprint(week)\nprint(saved)',
  ['10000 1000 500', '1 1 0', '10000000 1 0'.replace('10000000 1 0', '100000 1 0'), '5000 5000 100', '5001 5000 100', '10000000 100000 10000', '999 100 0'], gen=lambda r: f"{r.randint(1,10**5)} {r.randint(1,3000)} {r.randint(0,500)}")
P(T, '건너뛰며 더하기', 'I', '1부터 차례로 수를 더해 나간다. 단, `k` 의 배수는 **건너뛴다**. 더한 합이 `limit` 을 **넘으면** 즉시 멈춘다. `n` 까지 다 더했는데도 넘지 않으면 거기서 끝난다.',
  '한 줄에 `n k limit` 이 주어진다. (1 ≤ n ≤ 100000, 2 ≤ k ≤ 100, 1 ≤ limit ≤ 10^9)', '첫 줄에 마지막으로 더한 수, 둘째 줄에 그때의 합, 셋째 줄에 건너뛴 수의 개수를 출력한다. 하나도 더하지 못했다면 첫 줄에 0 을 출력한다.',
  'n, k, limit = map(int, input().split())\ni = 0\ntotal = 0\nlast = 0\nskip = 0\nwhile i < n:\n    i += 1\n    if i % k == 0:\n        skip += 1\n        continue\n    total += i\n    last = i\n    if total > limit:\n        break\nprint(last)\nprint(total)\nprint(skip)',
  ['10 3 20', '10 3 1000', '1 2 5', '5 2 0'.replace(' 0', ' 1'), '100000 100 1000000000', '6 2 9', '20 5 50'], gen=lambda r: f"{r.randint(1,200)} {r.randint(2,9)} {r.randint(1,5000)}", cond=['`while` 과 `continue`, `break` 를 사용할 것 (증가식의 위치에 주의)'])
P(T, '과학관 엘리베이터', 'I', '과학관은 지하 `b` 층부터 지상 `t` 층까지 있다. 지하 1층은 -1, 지상 1층은 1 로 나타내며 **0층은 없다**. 엘리베이터가 1층에서 출발해 명령을 순서대로 수행한다. `U k` 는 k층 위로, `D k` 는 k층 아래로 이동이다. 이동 결과가 건물 범위를 벗어나는 명령은 **무시**한다.',
  '첫 줄에 `b t` (0 ≤ b ≤ 10, 1 ≤ t ≤ 100, b 가 0 이면 지하층이 없다), 둘째 줄부터 명령이 한 줄씩 주어지고 마지막 줄은 `END` 이다. (1 ≤ k ≤ 200, 명령은 100개 이하)', '무시되지 않은 명령마다 도착한 층을 한 줄씩 출력한다. 지하는 `B2` 처럼, 지상은 `3F` 처럼 출력한다. 무시된 명령은 `이동 불가` 를 출력한다. 마지막 줄에 이동한 층수의 합을 출력한다.',
  'b, t = map(int, input().split())\npos = 0\nmoved = 0\nwhile True:\n    line = input().split()\n    if line[0] == "END":\n        break\n    k = int(line[1])\n    if line[0] == "U":\n        np = pos + k\n    else:\n        np = pos - k\n    if np < -b or np > t - 1:\n        print("이동 불가")\n        continue\n    pos = np\n    moved += k\n    if pos >= 0:\n        print(f"{pos + 1}F")\n    else:\n        print(f"B{-pos}")\nprint(moved)',
  ['2 5\nU 2\nD 3\nD 2\nD 1\nU 4\nEND', '0 3\nD 1\nU 2\nU 1\nEND', '1 1\nEND', '10 100\nD 10\nD 1\nU 109\nU 1\nEND', '3 3\nD 1\nD 1\nD 1\nU 1\nEND', '2 2\nU 1\nD 2\nD 1\nD 1\nU 3\nU 1\nEND'])

T = '중첩 반복·패턴 출력'
P(T, '구구단 전광판 역순', 'I', '구구단 9단부터 2단까지를 **큰 단부터** 한 줄에 `k` 개 단씩 나란히 출력한다. 한 묶음은 곱하는 수 1부터 9까지 9줄이다.',
  '정수 `k` 가 주어진다. (1 ≤ k ≤ 8)', '각 칸은 `단x수=곱` 형식이며 곱은 두 자리 폭으로 오른쪽 정렬한다(`{:2d}`). 같은 줄의 칸 사이는 공백 2개로 구분하고 줄 끝에는 공백이 없다. 묶음과 묶음 사이에는 빈 줄을 하나 출력한다.',
  'k = int(input())\ndans = list(range(9, 1, -1))\nfirst = True\nfor s in range(0, 8, k):\n    if not first:\n        print()\n    first = False\n    for j in range(1, 10):\n        row = []\n        for d in dans[s:s + k]:\n            row.append(f"{d}x{j}={d * j:2d}")\n        print("  ".join(row))',
  ['3', '8', '1', '2', '4', '5', '6', '7'])
P(T, 'LED 판의 X와 테두리', 'I', '`n` × `n` 크기의 LED 판에 **테두리**와 **두 대각선(X자)** 위의 LED 를 켠다. 켜진 LED 는 `#`, 꺼진 LED 는 `.` 으로 나타낸다.',
  '정수 `n` 이 주어진다. (1 ≤ n ≤ 30)', 'n줄에 걸쳐 LED 판을 출력한다. 마지막 줄 다음에 켜진 LED 의 개수를 출력한다.',
  'n = int(input())\ncnt = 0\nfor i in range(n):\n    for j in range(n):\n        if i == 0 or i == n - 1 or j == 0 or j == n - 1 or i == j or i + j == n - 1:\n            print("#", end="")\n            cnt += 1\n        else:\n            print(".", end="")\n    print()\nprint(cnt)',
  ['5', '7', '1', '2', '3', '4', '10', '30'])
P(T, '오른쪽 정렬 숫자 계단', 'B', '높이 `n` 인 숫자 계단을 출력한다. i번째 줄에는 공백 n-i개 다음에 1부터 i까지의 수를 붙여서 쓴다. 수가 10 이상이면 **일의 자리**만 쓴다.',
  '정수 `n` 이 주어진다. (1 ≤ n ≤ 30)', 'n줄에 걸쳐 계단을 출력한다.',
  'n = int(input())\nfor i in range(1, n + 1):\n    for j in range(n - i):\n        print(" ", end="")\n    for j in range(1, i + 1):\n        print(j % 10, end="")\n    print()',
  ['4', '1', '2', '12', '30', '7'], cond=['중첩 반복문을 사용할 것'])
P(T, '체크무늬 타일', 'B', '세로 `h`, 가로 `w` 크기의 바닥에 두 종류의 타일을 체크무늬로 깐다. 왼쪽 위 칸에 깔 타일 문자가 주어지고, 이웃한 칸(상하좌우)은 서로 다른 타일이다. 타일은 `#` 과 `.` 두 종류이다.',
  '한 줄에 `h w c` 가 주어진다. (1 ≤ h, w ≤ 30, c 는 `#` 또는 `.`)', 'h줄에 걸쳐 바닥의 모습을 출력한다. 마지막에 `#` 타일의 개수를 출력한다.',
  'h, w, c = input().split()\nh = int(h)\nw = int(w)\nother = "."\nif c == ".":\n    other = "#"\ncnt = 0\nfor i in range(h):\n    for j in range(w):\n        if (i + j) % 2 == 0:\n            ch = c\n        else:\n            ch = other\n        if ch == "#":\n            cnt += 1\n        print(ch, end="")\n    print()\nprint(cnt)',
  ['3 4 #', '3 3 .', '1 1 #', '1 1 .', '2 5 .', '5 5 #', '30 30 .'])
P(T, '다이아몬드 조명', 'I', '홀수 `n` 이 주어지면 가운데 줄의 너비가 `n` 인 다이아몬드를 `*` 로 출력한다. 각 줄에서 `*` 의 왼쪽은 공백으로 채우고 오른쪽에는 공백을 넣지 않는다.',
  '홀수 `n` 이 주어진다. (1 ≤ n ≤ 49)', 'n줄에 걸쳐 다이아몬드를 출력한다.',
  'n = int(input())\nmid = n // 2\nfor i in range(n):\n    d = abs(mid - i)\n    print(" " * d + "*" * (n - 2 * d))',
  ['5', '1', '3', '7', '9', '49'])
P(T, '곱셈표 만들기', 'B', '`r` 행 `c` 열의 곱셈표를 만든다. i행 j열의 값은 i × j 이다(1부터 센다). 각 값은 **네 칸 폭으로 오른쪽 정렬**하여 이어 쓴다.',
  '한 줄에 `r c` 가 주어진다. (1 ≤ r, c ≤ 30)', 'r줄에 걸쳐 곱셈표를 출력한다. 각 값은 `{:4d}` 형식으로 출력하며, 줄 앞쪽의 공백도 그대로 출력한다. 마지막 줄 다음에 표에 있는 모든 값의 합을 출력한다.',
  'r, c = map(int, input().split())\ntotal = 0\nfor i in range(1, r + 1):\n    line = ""\n    for j in range(1, c + 1):\n        line += f"{i * j:4d}"\n        total += i * j\n    print(line)\nprint(total)',
  ['3 4', '1 1', '9 9', '2 5', '30 30', '5 1'])
P(T, '이어지는 번호 삼각형', 'B', '1부터 시작하는 번호를 삼각형 모양으로 쓴다. i번째 줄에는 번호 i개를 공백으로 구분하여 쓰고, 번호는 줄이 바뀌어도 **계속 이어진다**.',
  '줄 수 `n` 이 주어진다. (1 ≤ n ≤ 40)', 'n줄에 걸쳐 삼각형을 출력한다. 마지막 줄 다음에 가장 마지막 번호를 출력한다.',
  'n = int(input())\nk = 0\nfor i in range(1, n + 1):\n    row = []\n    for j in range(i):\n        k += 1\n        row.append(k)\n    print(*row)\nprint(k)',
  ['3', '1', '4', '2', '10', '40'])
P(T, '대각선 LED 번호', 'I', '`n` × `n` LED 판의 LED 에는 왼쪽 위부터 오른쪽으로, 줄이 끝나면 다음 줄로 0부터 차례로 번호가 붙어 있다. **두 대각선(X자)** 위에 있는 LED 의 번호를 모두 구하시오.',
  '정수 `n` 이 주어진다. (1 ≤ n ≤ 50)', '첫 줄에 X자 위에 있는 LED 번호를 오름차순으로 공백으로 구분하여 출력한다. 둘째 줄에 그 개수를 출력한다.',
  'n = int(input())\nout = []\nfor k in range(n * n):\n    r, c = k // n, k % n\n    if r == c or r + c == n - 1:\n        out.append(k)\nprint(*out)\nprint(len(out))',
  ['5', '1', '2', '3', '4', '6', '50'], cond=['번호 k 로부터 행과 열을 **몫과 나머지**로 구할 것'])
P(T, '모래시계', 'I', '홀수 `n` 이 주어지면 맨 윗줄과 맨 아랫줄의 너비가 `n` 인 모래시계를 숫자로 출력한다. 각 줄에는 그 줄의 **너비**를 일의 자리 숫자로 이어 쓴다. (너비 5인 줄은 `55555`) 숫자 왼쪽은 공백으로 채우고 오른쪽에는 공백을 넣지 않는다.',
  '홀수 `n` 이 주어진다. (1 ≤ n ≤ 39)', 'n줄에 걸쳐 모래시계를 출력한다.',
  'n = int(input())\nmid = n // 2\nfor i in range(n):\n    d = mid - abs(mid - i)\n    w = n - 2 * d\n    print(" " * d + str(w % 10) * w)',
  ['5', '1', '3', '7', '11', '39'])
P(T, '시청각실 좌석표', 'I', '시청각실에는 `r` 줄, 한 줄에 `c` 개의 좌석이 있다. 좌석 번호는 맨 앞줄 왼쪽부터 1번이고 오른쪽으로 갈수록, 뒷줄로 갈수록 커진다. 예약된 좌석 번호가 주어질 때 좌석표를 그리시오.',
  '첫 줄에 `r c` (1 ≤ r, c ≤ 20), 둘째 줄에 예약 수 `k` (0 ≤ k ≤ r×c), k 가 1 이상이면 셋째 줄에 예약된 좌석 번호 k개가 공백으로 구분되어 주어진다. 같은 번호가 여러 번 나올 수 있다.', 'r줄에 걸쳐 좌석표를 출력한다. 예약된 좌석은 `X`, 빈 좌석은 `O` 로 나타내고 공백 없이 이어 쓴다. 다음 줄에 빈 좌석의 수를 출력하고, 마지막 줄에 빈 좌석이 가장 많은 줄의 번호(1부터, 여러 줄이면 가장 앞줄)를 출력한다.',
  'r, c = map(int, input().split())\nk = int(input())\nbooked = []\nif k > 0:\n    booked = list(map(int, input().split()))\nempty = 0\nbest = 0\nbest_cnt = -1\nfor i in range(r):\n    line = ""\n    cnt = 0\n    for j in range(c):\n        num = i * c + j + 1\n        if num in booked:\n            line += "X"\n        else:\n            line += "O"\n            cnt += 1\n    print(line)\n    empty += cnt\n    if cnt > best_cnt:\n        best_cnt = cnt\n        best = i + 1\nprint(empty)\nprint(best)',
  ['3 4\n4\n1 6 7 12', '2 2\n0', '1 1\n1\n1', '2 3\n6\n1 2 3 4 5 6', '3 3\n5\n1 1 2 2 9', '4 5\n7\n20 19 18 17 16 1 5'], gen=lambda r: (lambda a, b: f"{a} {b}\n{(k:=r.randint(1,a*b))}\n{RL(r,k,1,a*b)}")(r.randint(1,6), r.randint(1,8)))

T = '문자열·슬라이싱·ASCII'
P(T, '허수 비밀번호 탐지기', 'I', '허수 기능이 있는 도어락은 누른 숫자열 안에 진짜 비밀번호가 **연속으로** 들어 있으면 열린다. 보안 점검을 위해, 누른 숫자열 안에 비밀번호가 **몇 번** 나타나는지와 나타나는 위치를 모두 구하시오. 겹쳐서 나타나는 경우도 각각 센다. (예: 숫자열 `11111` 에서 `111` 은 3번)',
  '첫 줄에 비밀번호, 둘째 줄에 누른 숫자열이 주어진다. (비밀번호 길이 1 이상 10 이하, 숫자열 길이 1 이상 1000 이하)', '첫 줄에 나타난 횟수를 출력한다. 횟수가 1 이상이면 둘째 줄에 각 시작 위치(1부터 셈)를 오름차순으로 공백으로 구분하여 출력한다.',
  'pw = input()\ns = input()\npos = []\nfor i in range(len(s) - len(pw) + 1):\n    if s[i:i + len(pw)] == pw:\n        pos.append(i + 1)\nprint(len(pos))\nif pos:\n    print(*pos)',
  ['1234\n9912345123', '111\n11111', '5\n12345', '99\n123', '12\n1', '808\n80808080', '0425\n0425', '7\n7777777'], gen=lambda r: f"{RL(r, r.randint(1,2), 0, 2).replace(' ','')}\n{RL(r, r.randint(5,30), 0, 2).replace(' ','')}", cond=['`in`, `find()`, `index()`, `count()` 를 사용하지 말고 **슬라이싱과 반복문**으로 찾을 것'])
P(T, '학생증 번호 검사', 'I', '학생증 번호는 `GSA-YYYY-NNN-C` 형식의 14글자이다. `YYYY` 는 입학 연도(2000 이상 2026 이하), `NNN` 은 세 자리 번호(001 이상), `C` 는 **검증 숫자**이다. 검증 숫자는 YYYY 와 NNN 의 일곱 숫자를 모두 더한 값을 10으로 나눈 나머지이다. 앞의 `GSA` 는 대소문자를 구분하지 않는다.',
  '학생증 번호가 한 줄에 주어진다. (길이 1 이상 30 이하, 공백 없음)', '형식이 틀리면 `형식 오류`, 형식은 맞지만 연도나 번호가 범위를 벗어나면 `범위 오류`, 검증 숫자가 틀리면 `검증 오류 (올바른 값 K)`, 모두 맞으면 `정상 YYYY년 입학 N번` 을 출력한다. N 은 앞의 0을 뗀 번호이다. 오류는 앞에 적힌 것부터 검사한다.',
  's = input()\nok = len(s) == 14 and s[:3].upper() == "GSA" and s[3] == "-" and s[8] == "-" and s[12] == "-"\nif ok:\n    ok = s[4:8].isdigit() and s[9:12].isdigit() and s[13].isdigit()\nif not ok:\n    print("형식 오류")\nelse:\n    y = int(s[4:8])\n    n = int(s[9:12])\n    if y < 2000 or y > 2026 or n < 1:\n        print("범위 오류")\n    else:\n        k = 0\n        for ch in s[4:8] + s[9:12]:\n            k += int(ch)\n        k %= 10\n        if k != int(s[13]):\n            print(f"검증 오류 (올바른 값 {k})")\n        else:\n            print(f"정상 {y}년 입학 {n}번")',
  ['GSA-2026-017-8', 'gsa-2025-120-1', 'GSA-2026-017-0', 'GSA-2027-001-2', 'GSA-2026-000-0', 'GSB-2026-017-8', 'GSA-2026-17-8', 'GSA_2026-017-8', 'GSA-20a6-017-8', 'Gsa-2000-999-9', 'GSA-2026-017-88', 'GSA-1999-001-9'], cond=['**슬라이싱**으로 각 부분을 잘라 검사할 것'])
P(T, '비밀 쪽지 암호', 'I', '쪽지의 영어 알파벳을 `k` 칸씩 뒤로 밀어 암호로 만든다. `z` 다음은 `a`, `Z` 다음은 `A` 로 이어진다. 대문자는 대문자로, 소문자는 소문자로 바뀌며 알파벳이 아닌 글자는 그대로 둔다.',
  '첫 줄에 `k` (0 ≤ k ≤ 1000), 둘째 줄에 쪽지 내용이 주어진다. (길이 1 이상 200 이하, 공백 포함 가능)', '암호로 바꾼 쪽지를 출력한다.',
  'k = int(input())\ns = input()\nout = ""\nfor c in s:\n    if "a" <= c <= "z":\n        out += chr((ord(c) - ord("a") + k) % 26 + ord("a"))\n    elif "A" <= c <= "Z":\n        out += chr((ord(c) - ord("A") + k) % 26 + ord("A"))\n    else:\n        out += c\nprint(out)',
  ['3\nHello, World!', '1\nxyz XYZ', '0\nPyNest', '26\nabc', '1000\nGwangju Science Academy 2026', '25\nb', '13\nUryyb'], cond=['`ord()` 와 `chr()` 를 사용할 것'])
P(T, '거꾸로 말해요', 'B', '문장이 회문인지 판별한다. 회문은 거꾸로 읽어도 같은 문장이다. 이때 **공백은 무시**하고 영어 **대소문자는 구분하지 않는다**.',
  '문장이 한 줄에 주어진다. (길이 1 이상 200 이하, 영문자와 공백으로만 구성되고 영문자가 하나 이상 있다)', '첫 줄에 공백을 없애고 모두 소문자로 바꾼 뒤 **뒤집은** 문자열을 출력한다. 둘째 줄에 회문이면 `회문`, 아니면 `회문 아님` 을 출력한다.',
  's = input().replace(" ", "").lower()\nr = s[::-1]\nprint(r)\nif s == r:\n    print("회문")\nelse:\n    print("회문 아님")',
  ['Never odd or even', 'Python', 'A', 'ab', 'Was it a car or a cat I saw', 'No lemon no melon', 'Step on no pets ', 'abcdcbA'])
P(T, '모음 세기', 'B', '영어 문장에서 모음(a, e, i, o, u)이 각각 몇 번 나오는지 센다. 대소문자는 구분하지 않는다.',
  '문장이 한 줄에 주어진다. (길이 1 이상 300 이하)', '`a e i o u` 순서로 각 모음의 개수를 공백으로 구분하여 한 줄에 출력한다. 둘째 줄에 모음이 아닌 **영어 알파벳**(자음)의 개수를 출력한다.',
  's = input().lower()\nv = "aeiou"\ncnt = [0, 0, 0, 0, 0]\ncons = 0\nfor c in s:\n    found = False\n    for i in range(5):\n        if c == v[i]:\n            cnt[i] += 1\n            found = True\n    if not found and "a" <= c <= "z":\n        cons += 1\nprint(*cnt)\nprint(cons)',
  ['Gwangju Science Academy', 'AEIOU aeiou', 'xyz', '2026!!', 'Education is the most powerful weapon', 'I', 'queueing'], cond=['문자열의 `count()` 메서드를 사용하지 말 것'])
P(T, '개인정보 가리기', 'B', '이름과 전화번호를 가려서 출력한다. 이름은 **첫 글자와 마지막 글자**만 남기고 가운데를 `*` 로 바꾼다. 이름이 두 글자이면 마지막 글자만 `*` 로 바꾼다. 전화번호는 `010-ABCD-EFGH` 형식이며 가운데 네 자리를 `****` 로 바꾼다.',
  '첫 줄에 이름(2글자 이상 10글자 이하), 둘째 줄에 전화번호(13글자)가 주어진다.', '첫 줄에 가린 이름, 둘째 줄에 가린 전화번호를 출력한다.',
  'name = input()\ntel = input()\nif len(name) == 2:\n    print(name[0] + "*")\nelse:\n    print(name[0] + "*" * (len(name) - 2) + name[-1])\nprint(tel[:4] + "****" + tel[8:])',
  ['홍길동\n010-1234-5678', '이산\n010-0000-9999', '남궁민수\n010-4321-8765', 'Alexander\n010-1111-2222', '김철\n010-5555-0000', '선우은숙이\n010-9876-5432'], cond=['슬라이싱과 문자열 반복(`*`)을 사용할 것'])
P(T, '문자열 압축기', 'I', '같은 글자가 연속으로 나오면 `글자 + 개수` 로 줄여 쓴다. 한 번만 나온 글자는 개수를 쓰지 않는다. (예: `aaabccdddd` → `a3bc2d4`)',
  '영어 소문자로 이루어진 문자열이 주어진다. (길이 1 이상 1000 이하)', '첫 줄에 압축한 문자열, 둘째 줄에 `원래 길이 -> 압축 길이` 를 출력한다.',
  's = input()\nout = ""\nrun = 1\nfor i in range(1, len(s) + 1):\n    if i < len(s) and s[i] == s[i - 1]:\n        run += 1\n    else:\n        out += s[i - 1]\n        if run > 1:\n            out += str(run)\n        run = 1\nprint(out)\nprint(f"{len(s)} -> {len(out)}")',
  ['aaabccdddd', 'a', 'abc', 'zzzzzzzzzzzz', 'aabbaa', 'abbbbbbbbbbbbbbbbbbbbba', 'aab'], gen=lambda r: "".join(r.choice("ab") * r.randint(1,4) for _ in range(r.randint(1,8))))
P(T, '글자를 이진수로', 'I', '컴퓨터는 글자를 숫자 코드로 저장한다. 문자열의 각 글자에 대해 ASCII 코드와 그 코드를 **8자리 이진수**로 나타낸 값을 구하시오.',
  '문자열이 한 줄에 주어진다. (길이 1 이상 20 이하, 영문자·숫자로만 구성)', '각 글자마다 `글자 코드 이진수` 를 한 줄씩 출력한다. 이진수는 8자리가 되도록 앞을 0으로 채운다. 마지막 줄에 모든 코드의 합을 출력한다.',
  's = input()\ntotal = 0\nfor c in s:\n    n = ord(c)\n    total += n\n    b = ""\n    m = n\n    while m > 0:\n        b = str(m % 2) + b\n        m //= 2\n    b = "0" * (8 - len(b)) + b\n    print(c, n, b)\nprint(total)',
  ['Hi', 'A', 'a0Z', 'GSA2026', 'z', '0', 'Python'], cond=['`bin()` 과 `format()`, f-string 의 이진수 서식을 사용하지 말고 **2로 나눈 나머지**를 이용해 직접 구할 것'])
P(T, '대소문자 뒤집기', 'B', '문자열의 영어 대문자는 소문자로, 소문자는 대문자로 바꾼다. 다른 글자는 그대로 둔다.',
  '문자열이 한 줄에 주어진다. (길이 1 이상 200 이하)', '첫 줄에 바꾼 문자열, 둘째 줄에 바뀐 글자의 수를 출력한다.',
  's = input()\nout = ""\ncnt = 0\nfor c in s:\n    if "a" <= c <= "z":\n        out += chr(ord(c) - 32)\n        cnt += 1\n    elif "A" <= c <= "Z":\n        out += chr(ord(c) + 32)\n        cnt += 1\n    else:\n        out += c\nprint(out)\nprint(cnt)',
  ['PyNest 2026', 'abc', 'ABC', '1234', 'Hello, World!', 'zZ', 'gSA rOCKS'], cond=['`swapcase()`, `upper()`, `lower()` 를 사용하지 말고 `ord()` 와 `chr()` 를 사용할 것'])
P(T, '가장 긴 숫자 구간', 'I', '문자열에서 숫자가 **연속으로** 이어진 구간 중 가장 긴 것을 찾으시오. 길이가 같은 구간이 여러 개이면 가장 먼저 나오는 것을 고른다.',
  '문자열이 한 줄에 주어진다. (길이 1 이상 500 이하, 영문자·숫자로만 구성)', '첫 줄에 가장 긴 숫자 구간을 출력하고, 둘째 줄에 그 구간의 시작 위치(1부터 셈)와 길이를 공백으로 구분하여 출력한다. 숫자가 하나도 없으면 `없음` 만 출력한다.',
  's = input()\nbest = ""\nbest_pos = 0\ncur = ""\nfor i in range(len(s)):\n    if s[i].isdigit():\n        cur += s[i]\n        if len(cur) > len(best):\n            best = cur\n            best_pos = i - len(cur) + 2\n    else:\n        cur = ""\nif best == "":\n    print("없음")\nelse:\n    print(best)\n    print(best_pos, len(best))',
  ['ab123cd4567ef89', 'abc', '2026', 'a1b22c33', '12ab34', 'x9', '007bond0070'], gen=lambda r: "".join(r.choice("ab01234") for _ in range(r.randint(3,25))))

T = '리스트 다루기'
P(T, '급식 대기 줄', 'I', '급식실 대기 줄을 관리한다. 처음 줄에 서 있는 학생들의 이름이 앞에서부터 주어지고, 명령을 차례로 수행한다.\n\n`IN 이름` : 맨 뒤에 선다. `CUT 이름 k` : 앞에서 k번째 자리(1부터)에 끼어든다. k 가 줄의 길이보다 크면 맨 뒤에 선다. `OUT 이름` : 그 학생이 줄에서 나간다(줄에 없으면 무시). `EAT` : 맨 앞 학생이 식사하러 들어간다(줄이 비었으면 무시).',
  '첫 줄에 처음 줄의 이름들이 공백으로 구분되어 주어진다(1명 이상 20명 이하). 둘째 줄에 명령 수 `q` (1 ≤ q ≤ 50), 이어서 q줄에 명령이 주어진다. 이름은 서로 다르며, 줄에 이미 있는 이름으로 `IN` 이나 `CUT` 이 주어지지 않는다.', '`EAT` 명령으로 학생이 들어갈 때마다 그 학생의 이름을 한 줄씩 출력한다. 모든 명령이 끝난 뒤 남은 줄을 앞에서부터 공백으로 구분하여 출력한다. 줄이 비었으면 `빈 줄` 을 출력한다.',
  'line = input().split()\nq = int(input())\nfor _ in range(q):\n    cmd = input().split()\n    if cmd[0] == "IN":\n        line.append(cmd[1])\n    elif cmd[0] == "CUT":\n        line.insert(int(cmd[2]) - 1, cmd[1])\n    elif cmd[0] == "OUT":\n        if cmd[1] in line:\n            line.remove(cmd[1])\n    else:\n        if line:\n            print(line.pop(0))\nif line:\n    print(*line)\nelse:\n    print("빈 줄")',
  ['민 솔 준\n5\nIN 하\nCUT 율 2\nEAT\nOUT 솔\nEAT', 'A\n3\nEAT\nEAT\nIN B', 'A B\n2\nOUT C\nOUT A', 'A B C\n4\nCUT D 10\nCUT E 1\nEAT\nEAT', 'A\n2\nEAT\nEAT', 'a b c d e\n6\nOUT c\nCUT c 5\nEAT\nIN f\nOUT a\nEAT'], cond=['리스트 메서드 `append`, `insert`, `remove`, `pop` 을 활용할 것'])
P(T, '기록의 중앙값', 'B', '달리기 기록 `n` 개가 주어진다. 중앙값은 기록을 크기순으로 늘어놓았을 때 가운데 값이다. `n` 이 짝수이면 가운데 두 값의 평균이다.',
  '첫 줄에 `n` (1 ≤ n ≤ 99), 둘째 줄에 n개의 기록(1 이상 1000 이하의 정수)이 주어진다.', '첫 줄에 중앙값, 둘째 줄에 평균을 출력한다. 둘 다 소수 첫째 자리까지 출력한다. 셋째 줄에 **입력받은 순서 그대로**의 기록 중 중앙값보다 큰 기록의 개수를 출력한다.',
  'n = int(input())\na = list(map(int, input().split()))\nb = a.copy()\nb.sort()\nif n % 2 == 1:\n    med = b[n // 2]\nelse:\n    med = (b[n // 2 - 1] + b[n // 2]) / 2\nprint(f"{med:.1f}")\nprint(f"{sum(a) / n:.1f}")\ncnt = 0\nfor x in a:\n    if x > med:\n        cnt += 1\nprint(cnt)',
  ['5\n7 1 9 3 5', '4\n4 8 2 6', '1\n10', '2\n1 2', '6\n5 5 5 5 5 5', '3\n1000 1 1'], gen=lambda r: (lambda n: f"{n}\n{RL(r,n,1,100)}")(r.randint(1,15)))
P(T, '공부 시간 흐름 분석', 'I', '`n` 일 동안의 공부 시간이 주어진다. 전날보다 공부 시간이 **줄어들지 않은**(같거나 늘어난) 날이 이어지는 가장 긴 구간을 찾으시오. 구간의 길이는 그 구간에 포함된 **날의 수**이다. (하루만 있어도 길이 1)',
  '첫 줄에 `n` (1 ≤ n ≤ 1000), 둘째 줄에 n개의 공부 시간(0 이상 1440 이하의 정수)이 주어진다.', '첫 줄에 가장 긴 구간의 길이, 둘째 줄에 그 구간의 시작 날과 끝 날의 번호(1부터)를 공백으로 구분하여 출력한다. 길이가 같은 구간이 여러 개이면 가장 먼저 나오는 구간을 출력한다.',
  'n = int(input())\nt = list(map(int, input().split()))\nrun = 1\nbest = 1\nbest_end = 0\nfor i in range(1, n):\n    if t[i] >= t[i - 1]:\n        run += 1\n    else:\n        run = 1\n    if run > best:\n        best = run\n        best_end = i\nprint(best)\nprint(best_end - best + 2, best_end + 1)',
  ['7\n3 5 5 2 4 6 7', '1\n10', '4\n9 7 5 3', '5\n1 1 1 1 1', '6\n1 2 1 2 1 2', '8\n5 6 7 1 2 3 0 0'], gen=lambda r: (lambda n: f"{n}\n{RL(r,n,0,6)}")(r.randint(1,20)))
P(T, '당번표 돌리기', 'B', '청소 당번표에 `n` 명의 번호가 적혀 있다. 매주 당번표를 **오른쪽으로 한 칸씩** 돌린다(맨 뒤 사람이 맨 앞으로 온다). `k` 주 뒤의 당번표를 구하시오.',
  '첫 줄에 `n k` (1 ≤ n ≤ 100, 0 ≤ k ≤ 10^9), 둘째 줄에 n개의 번호가 주어진다.', '`k` 주 뒤의 당번표를 공백으로 구분하여 출력한다.',
  'n, k = map(int, input().split())\na = input().split()\nk %= n\nb = a[n - k:] + a[:n - k]\nprint(*b)',
  ['5 2\n1 2 3 4 5', '3 0\n7 8 9', '1 100\n4', '4 4\n1 2 3 4', '4 1000000000\n1 2 3 4', '6 7\n10 20 30 40 50 60', '2 3\n5 6'], cond=['`k` 가 매우 클 수 있으므로 **나머지 연산**으로 줄인 뒤 **슬라이싱**으로 해결할 것'])
P(T, '중복 신청 걸러내기', 'B', '동아리 신청 명단에 같은 학번이 여러 번 적혀 있다. 처음 적힌 것만 남기고 중복을 없앤다. 순서는 처음 적힌 순서를 유지한다.',
  '첫 줄에 `n` (1 ≤ n ≤ 1000), 둘째 줄에 n개의 학번(1 이상 99999 이하의 정수)이 주어진다.', '첫 줄에 중복을 없앤 명단을 공백으로 구분하여 출력한다. 둘째 줄에 지워진 항목의 수를 출력한다.',
  'n = int(input())\na = input().split()\nout = []\nfor x in a:\n    if x not in out:\n        out.append(x)\nprint(*out)\nprint(n - len(out))',
  ['7\n3 5 3 7 5 5 1', '1\n9', '4\n2 2 2 2', '5\n1 2 3 4 5', '6\n10 1 10 1 10 1', '3\n99999 1 99999'], gen=lambda r: (lambda n: f"{n}\n{RL(r,n,1,8)}")(r.randint(1,25)), cond=['`set` 과 딕셔너리를 사용하지 말고 리스트와 `in` 으로 해결할 것'])
P(T, '은메달의 주인', 'I', '대회 점수 `n` 개가 주어진다. **두 번째로 높은 점수**를 구하시오. 가장 높은 점수와 같은 점수는 모두 1등이므로, 1등보다 낮은 점수 중 가장 높은 점수가 두 번째이다.',
  '첫 줄에 `n` (1 ≤ n ≤ 1000), 둘째 줄에 n개의 점수(0 이상 10000 이하의 정수)가 주어진다.', '첫 줄에 두 번째로 높은 점수를 출력하고, 둘째 줄에 그 점수를 받은 사람의 수를 출력한다. 두 번째로 높은 점수가 없으면 `없음` 만 출력한다.',
  'n = int(input())\na = list(map(int, input().split()))\nbest = a[0]\nfor x in a:\n    if x > best:\n        best = x\nsecond = -1\nfor x in a:\n    if x < best and x > second:\n        second = x\nif second == -1:\n    print("없음")\nelse:\n    cnt = 0\n    for x in a:\n        if x == second:\n            cnt += 1\n    print(second)\n    print(cnt)',
  ['5\n90 100 100 80 90', '1\n50', '3\n7 7 7', '2\n0 1', '6\n1 2 3 4 5 6', '4\n10000 0 0 0'], gen=lambda r: (lambda n: f"{n}\n{RL(r,n,0,9)}")(r.randint(1,15)), cond=['`sort()`, `sorted()`, `max()`, `set` 을 사용하지 말 것'])
P(T, '출석 번호 찾기', 'B', '명단에서 찾는 이름이 적힌 **모든 위치**를 찾는다.',
  '첫 줄에 명단의 이름들이 공백으로 구분되어 주어진다(1개 이상 200개 이하). 둘째 줄에 찾는 이름이 주어진다.', '찾는 이름이 있는 위치(1부터)를 오름차순으로 공백으로 구분하여 출력한다. 하나도 없으면 `-1` 을 출력한다. 둘째 줄에 명단에서 찾는 이름이 **아닌** 이름의 개수를 출력한다.',
  'a = input().split()\nx = input()\npos = []\nfor i in range(len(a)):\n    if a[i] == x:\n        pos.append(i + 1)\nif pos:\n    print(*pos)\nelse:\n    print(-1)\nprint(len(a) - len(pos))',
  ['kim lee kim park\nkim', 'kim lee\nchoi', 'a\na', 'a a a a\na', 'x y z y x\ny', 'Kim kim KIM\nkim'], cond=['`index()` 와 `count()` 를 사용하지 말고 for 문으로 직접 찾을 것'])
P(T, '만보기 누적 그래프', 'I', '`n` 일 동안의 걸음 수가 주어진다. 날마다 **그날까지의 누적 걸음 수**를 구하고, 누적 걸음 수가 처음으로 목표 `g` 이상이 되는 날을 찾으시오.',
  '첫 줄에 `n g` (1 ≤ n ≤ 1000, 1 ≤ g ≤ 10^9), 둘째 줄에 n개의 걸음 수(0 이상 100000 이하의 정수)가 주어진다.', '첫 줄에 누적 걸음 수를 날짜 순으로 공백으로 구분하여 출력한다. 둘째 줄에 목표를 처음 달성한 날의 번호(1부터)를 출력하되 달성하지 못하면 `미달성` 을 출력한다. 셋째 줄에 하루 걸음 수가 **전체 평균 이상**인 날의 수를 출력한다.',
  'n, g = map(int, input().split())\na = list(map(int, input().split()))\nacc = []\ntotal = 0\nday = 0\nfor i in range(n):\n    total += a[i]\n    acc.append(total)\n    if day == 0 and total >= g:\n        day = i + 1\nprint(*acc)\nif day:\n    print(day)\nelse:\n    print("미달성")\ncnt = 0\nfor x in a:\n    if x * n >= total:\n        cnt += 1\nprint(cnt)',
  ['5 10000\n3000 4000 2000 5000 1000', '1 1\n0', '3 6\n1 2 3', '3 7\n1 2 3', '4 1\n0 0 0 0', '2 100000\n100000 0'], gen=lambda r: (lambda n: f"{n} {r.randint(1,400)}\n{RL(r,n,0,60)}")(r.randint(1,12)))
P(T, '짝수 먼저 세우기', 'B', '번호표를 가진 학생들이 한 줄로 서 있다. 번호가 **짝수인 학생을 앞**으로, 홀수인 학생을 뒤로 보낸다. 짝수끼리, 홀수끼리는 원래 순서를 유지한다.',
  '첫 줄에 `n` (1 ≤ n ≤ 1000), 둘째 줄에 n개의 번호(1 이상 10^6 이하의 정수)가 주어진다.', '첫 줄에 다시 선 줄을 공백으로 구분하여 출력한다. 둘째 줄에 짝수의 개수와 홀수의 개수를 공백으로 구분하여 출력한다.',
  'n = int(input())\na = list(map(int, input().split()))\neven = []\nodd = []\nfor x in a:\n    if x % 2 == 0:\n        even.append(x)\n    else:\n        odd.append(x)\nprint(*(even + odd))\nprint(len(even), len(odd))',
  ['6\n3 8 5 2 9 4', '1\n7', '1\n8', '4\n2 4 6 8', '4\n1 3 5 7', '5\n1000000 1 999999 2 3'], gen=lambda r: (lambda n: f"{n}\n{RL(r,n,1,50)}")(r.randint(1,15)))
P(T, '기온 급변 구간', 'I', '`n` 일 동안의 기온이 주어진다. **이웃한 두 날**의 기온 차(절댓값)가 가장 큰 곳을 찾으시오. 차가 같은 곳이 여러 개이면 가장 먼저 나오는 곳을 고른다.',
  '첫 줄에 `n` (2 ≤ n ≤ 1000), 둘째 줄에 n개의 기온(-50 이상 50 이하의 정수)이 주어진다.', '첫 줄에 가장 큰 기온 차를 출력한다. 둘째 줄에 그 두 날의 번호(1부터)를 공백으로 구분하여 출력한다. 셋째 줄에 뒷날의 기온이 더 높으면 `상승`, 더 낮으면 `하강`, 차가 0 이면 `변화 없음` 을 출력한다.',
  'n = int(input())\nt = list(map(int, input().split()))\nbest = -1\npos = 0\nfor i in range(1, n):\n    d = t[i] - t[i - 1]\n    if d < 0:\n        d = -d\n    if d > best:\n        best = d\n        pos = i\nprint(best)\nprint(pos, pos + 1)\nif t[pos] > t[pos - 1]:\n    print("상승")\nelif t[pos] < t[pos - 1]:\n    print("하강")\nelse:\n    print("변화 없음")',
  ['5\n10 12 5 6 13', '2\n3 3', '2\n-50 50', '4\n1 2 3 4', '4\n9 5 1 5', '3\n0 -7 0'], gen=lambda r: (lambda n: f"{n}\n{RL(r,n,-10,30)}")(r.randint(2,15)), cond=['`abs()`, `max()` 를 사용하지 말 것'])
