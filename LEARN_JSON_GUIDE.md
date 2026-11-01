# PyNest 학습 JSON 형식 `pynest-learn-v1` (V4.2.0)

📚 **학습** 메뉴(코스 → 레슨 → 단계)에 올리는 파일이에요. **문제집 JSON(`pynest-problemset-v1`)과는 별개**예요.
올리는 곳: 📚 학습 → [＋ JSON으로 코스 추가] (새 코스) / 코스 화면 → [＋ JSON으로 레슨 추가] (레슨만 추가).
먼저 Supabase 에서 `v410_learn.sql` 을 한 번 실행해야 해요. 예시 파일: `learn_sample.json`.

## 1. 전체 모양

```json
{
  "format": "pynest-learn-v1",
  "course": { "title": "파이썬 첫걸음", "description": "한 줄 소개", "sequential": true, "rank_points": 20 },
  "lessons": [
    {
      "title": "print 로 출력하기",
      "minutes": 10,
      "summary": "마크다운 — 레슨을 끝내면 '핵심 정리'로 보여요",
      "steps": [ { "type": "explain", ... }, { "type": "quiz", ... }, { "type": "practice", ... } ]
    }
  ]
}
```

| 자리 | 설명 |
|---|---|
| `course.title` | 코스 이름 (새 코스를 만들 때 필수) |
| `course.description` | 코스 소개 (선택) |
| `course.rank_points` | **레슨 1개를 끝낼 때마다** 받는 랭킹·티어 점수 (기본 0 = 반영 안 함). 코스 화면의 ✏️ 코스 정보에서도 바꿔요 |
| `course.sequential` | `true`(기본)면 앞 레슨을 끝내야 다음 레슨이 열려요. 선생님은 항상 전부 열려요 |
| `lessons[].title` | 레슨 이름 (필수) |
| `lessons[].minutes` | 걸리는 시간(분, 선택) |
| `lessons[].rank_points` | 이 레슨만 따로 정하는 랭킹 점수 (선택, 없으면 코스 점수. `0` 이면 이 레슨만 점수 없음) |
| `lessons[].summary` | 레슨 끝에 보여 줄 핵심 정리 (마크다운, 선택) |
| `lessons[].steps` | 단계 목록 (필수, 1~80개). 위에서 아래 순서대로 한 단계씩 진행 |

학생은 **한 단계씩** 진행해요. 개념(explain)은 읽고 "다음", 확인 문제(quiz)는 **맞혀야** 다음으로, 실습(practice)은 **채점을 통과**해야 다음으로 넘어가요.

## 2. 단계 3종류

### 2-1. `explain` — 개념 설명 (마크다운)

```json
{ "type": "explain", "title": "print 란?",
  "body": "화면에 **출력**할 때 `print()` 를 써요.\n\n- 글자는 따옴표로 감싸요",
  "code": "print(\"안녕\")\nprint(1 + 2)", "run": true }
```

| 필드 | 설명 |
|---|---|
| `title` | 단계 제목 (선택) |
| `body` | 설명 글. **마크다운**: `# 제목` · `**굵게**` · `` `코드` `` · 코드 블록(``` ``` ```) · `- 목록` · `1. 번호` · 표 · `> 인용` · `---` · 링크 |
| `code` | 예제 코드 (선택). 학생이 고쳐서 **▶ 실행해 보기** 를 눌러 볼 수 있어요 |
| `run` | `false` 면 실행 버튼 없이 코드만 보여요 (기본 `true`) |

### 2-2. `quiz` — 확인 문제 (4가지 `kind`)

공통: `question`(마크다운), `explanation`(정답/오답 후 보여 줄 해설, 선택). `"type":"ox"` 처럼 줄여 써도 돼요.

**O/X**
```json
{ "type": "quiz", "kind": "ox", "question": "`input()` 의 결과는 처음에 숫자다.", "answer": false, "explanation": "항상 글자예요." }
```
`answer`: `true`/`false` (또는 `"O"`/`"X"`).

**객관식** — 정답 번호는 **1부터** 세요. 정답이 여럿이면 배열.
```json
{ "type": "quiz", "kind": "choice", "question": "오류가 나는 코드는?",
  "options": ["print(\"hi\")", "print('hi')", "print(hi)", "print(5)"], "answer": 3 }
{ "type": "quiz", "kind": "choice", "question": "변수 이름으로 쓸 수 있는 것을 모두 고르세요.",
  "options": ["score", "2nd", "my_name", "for"], "answer": [1, 3] }
```

**단답** — 대소문자·공백 차이는 무시해요. 다른 정답은 `alts`.
```json
{ "type": "quiz", "kind": "short", "question": "`x = 5` 후 `print(x * 2)` 의 출력은?", "answer": "10", "alts": ["열"] }
```

**빈칸** — 코드 안에 `___`(밑줄 3개)을 쓰고, 칸마다 정답을 순서대로. 칸마다 다른 정답은 배열로.
```json
{ "type": "quiz", "kind": "fill", "question": "빈칸을 채우세요.",
  "code": "n = ___(input())\nprint(n + 1)", "answers": [["int"]] }
```
`answers` 의 길이 = 빈칸 개수.

틀린 확인 문제는 자동으로 **🔁 오답 복습**에 모여요. 2번 틀리면 [정답 보기]가 나와요.

### 2-3. `practice` — 코드 실습 (자동 채점)

```json
{ "type": "practice", "title": "두 수의 합",
  "body": "두 정수 A, B 가 한 줄에 하나씩 주어져요. A + B 를 출력하세요.",
  "starter": "a = int(input())\n# 이어서 작성\n",
  "tests": [ { "input": "3\n4\n", "output": "7" }, { "input": "0\n0\n", "output": "0", "hidden": true } ],
  "hints": ["두 번째 값도 `int(input())`", "`print(a + b)`"],
  "solution": "a = int(input())\nb = int(input())\nprint(a + b)",
  "explanation": "int() 로 바꿔야 더할 수 있어요." }
```

| 필드 | 설명 |
|---|---|
| `body` | 문제 설명 (마크다운) |
| `starter` | 처음에 채워 둘 코드 (선택) |
| `tests` | 자동 채점: `{input, output, hidden}` (문제집 `tests` 와 같아요). input 은 줄마다 `\n`. 없으면 채점 없이 "다음"으로 넘어가요 |
| `hints` | 힌트 목록. 학생이 누를 때마다 하나씩 열려요. 힌트를 쓰면 XP 가 조금 줄어요 |
| `solution` | 정답 코드 예시. 통과하면 보여 주고, 막히면 채점 **3번 시도 후** [정답 코드 보기] (보면 XP 없음) |
| `explanation` | 통과 후 해설 (선택) |
| `stdin` | 실행해 볼 때 기본 입력값 (선택, 없으면 첫 공개 테스트의 입력) |

## 3. 점수(XP) · 랭킹 점수 · 연속 학습일
- **랭킹 점수**: 코스(또는 레슨)에 `rank_points` 가 있으면, 학생이 그 레슨의 **모든 단계를 끝내는 순간** 랭킹·티어 점수가 더해져요 (레슨당 한 번). 푼 문제 수에는 안 세요. 먼저 `v420_learn_points.sql` 실행.
- 예) 입문 코스 `20`점 → 레슨 5개 완료 = 100점. 어려운 레슨만 `rank_points: 50` 으로 올릴 수 있어요.
- 개념 1 · 확인 문제 첫 시도 10 / 그 뒤 5 / 정답 보기 0 · 실습 30 (힌트 1개당 −5, 최소 10) · 레슨 완료 보너스 10.
- 하루라도 학습하면 🔥 연속 학습일이 이어져요 (한국 시간 기준). XP 는 랭킹·티어와 **별개**예요.

## 4. 팁
- **설명은 길고 구체적으로, 문제는 많고 다양하게** 만드는 게 학습 효과가 가장 커요. 아래 AI 프롬프트(7~13번)가 그 기준이에요. 한 번에 한 레슨씩 요청하면 AI 가 훨씬 꼼꼼하게 써요.
- 한 단계는 짧게 (설명 → 바로 확인 문제 → 실습). 코드잇처럼 "읽고 → 확인 → 해 보기" 가 반복되면 좋아요.
- 이미 올린 레슨 수정: 코스 화면에서 레슨 ✏️ (JSON 수정). 단계를 끼워 넣거나 빼면 푼 학생의 진도 번호가 어긋날 수 있어요.
- 코스 전체 백업/편집: [⬇️ JSON 내보내기] → 고쳐서 새 코스로 올리기.
- JSON 은 줄바꿈을 `\n`, 큰따옴표를 `\"` 로 써야 해요.

## 5. AI 에게 레슨 만들게 시키는 프롬프트 (그대로 복사)

````
너는 코드잇 스타일의 파이썬 입문 강의 설계자야. PyNest 학습 JSON(pynest-learn-v1)을 만들어줘. 설명 없이 JSON 만 코드블록 하나로 출력해.

[대상] 파이썬을 처음 배우는 중·고등학생. 아직 배운 것: ___ (예: print, 변수, 사칙연산)
[주제] ___ (예: if 조건문)  /  레슨 ___개, 레슨마다 단계 8~12개

[규칙]
1. 최상위: {"format":"pynest-learn-v1","course":{"title","description","sequential":true},"lessons":[...]}
2. 레슨: {"title","minutes","summary"(핵심 정리 마크다운 3~5줄),"steps":[...]}
3. 단계는 "개념 → 확인 문제 → 개념 → 확인 문제 … → 마지막에 실습" 순서. 개념(explain) 하나는 짧게(5~8줄), 예제 code 1개.
   - explain: {"type":"explain","title","body"(마크다운),"code"(실행해 볼 예제, 선택)}
   - quiz 4종: ox {"answer":true/false}, choice {"options":[..],"answer":번호(1부터) 또는 [번호,..]}, short {"answer","alts":[]}, fill {"code":"... ___ ...","answers":[["정답"],...]}.
     모든 quiz 에 "explanation"(왜 그런지 한두 문장) 포함. 레슨마다 ox/choice/short/fill 이 골고루 들어가게.
   - practice: {"type":"practice","title","body","starter","tests":[{"input","output","hidden"}],"hints":[힌트 2~3개, 점점 구체적으로],"solution","explanation"}
     tests 는 보이는 예제 1~2개 + hidden:true 경계값 2~4개. 모든 output 은 solution 을 실제로 실행해서 나온 값이어야 해. input 은 줄마다 \n.
4. 아직 안 배운 문법은 쓰지 마. 한 레슨에는 새 개념 1~2개만.
5. 학생에게 말하듯 친근한 존댓말, 비유와 작은 예제를 써.
6. 유효한 JSON (줄바꿈 \n, 큰따옴표 \", 마지막 쉼표 금지).

[설명은 구체적이고 디테일하게]
7. explain 의 body 는 "정의 → 왜 필요한지(실생활 비유) → 문법 모양 → 예제 코드와 실행 결과 → 자주 하는 실수" 순서로 충분히 풀어서 써. 한 줄 요약으로 끝내지 마. 개념 하나당 body 8~15줄, 마크다운(**굵게**, `코드`, 목록, 표)을 적극 사용.
8. 예제 code 는 실행 결과가 눈에 보이게 print 로 확인할 수 있게 짜고, body 에서 "이 코드를 실행하면 ○○ 가 출력돼요" 처럼 결과를 말로도 설명해. 일부러 오류가 나는 예제(들여쓰기·따옴표·콜론 빠뜨리기)도 하나쯤 보여 주고 어떤 오류 메시지가 나오는지 설명해.
9. 모든 quiz 의 explanation 은 "정답 이유 + 왜 다른 보기는 틀렸는지(또는 흔한 오해)"까지 2~4문장으로 자세히.

[문제(확인 문제·실습)는 풍부하고 디테일하게]
10. 한 레슨 안에 확인 문제를 6~10개: ox, choice(단일), choice(복수 정답), short, fill 을 모두 섞고, "코드 결과 예측하기"·"오류 찾기"·"빈칸 채우기"처럼 유형을 다양하게. 쉬운 것 → 헷갈리는 것 순으로.
11. 틀리기 쉬운 지점(자료형 혼동, 들여쓰기, == 와 =, 0 부터 세기, 문자열 vs 숫자)을 일부러 문제로 만들어. choice 의 오답 보기는 학생이 실제로 하는 실수로 구성해(그럴듯한 오답).
12. 실습(practice)은 레슨마다 3개: ① 따라 치기(starter 가 거의 채워져 있음) ② 응용(starter 에 뼈대만) ③ 도전(starter 는 주석뿐, 레슨 내용을 합쳐서 써야 풀림). 문제 body 에는 상황 설명, 입력 형식, 출력 형식, 예시 입출력을 모두 쓰고, 출력 형식(띄어쓰기·줄바꿈)을 정확히 명시해.
13. hints 는 3단계: ① 방향(어떤 개념을 쓰는지) ② 구조(코드 뼈대) ③ 거의 정답(핵심 한 줄). tests 는 보이는 예제 2개 + hidden 경계값 3~5개(0, 음수, 큰 수, 빈 입력 등). solution 에는 주석으로 한 줄씩 설명을 달아.
````
