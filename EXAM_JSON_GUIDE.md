# 시험 JSON 형식 (pynest-exam-v1)

관리자 › 📝 시험 › **📄 시험 JSON 가져오기** 로 올려요. 올리면 시험 만들기 폼이 채워지고, 시작 시각만 정해서 저장하면 돼요.
문제집 JSON(`pynest-problemset-v1`) 도 그대로 올릴 수 있어요. (아래 "문제집 JSON 규칙" 참고)

## 파일 구조

```json
{
  "format": "pynest-exam-v1",
  "title": "정보과학 중간 시험",
  "descr": "시험 범위, 주의사항 (마크다운)",
  "duration_min": 100,
  "entry_min": 30,
  "problems": [ { ... }, { ... } ]
}
```

- `duration_min` 시험 시간(분), `entry_min` 시작 몇 분 전부터 입장 가능. 둘 다 생략하면 폼의 값을 그대로 둬요.
- 시작 시각·공개 상태·보상은 JSON 에 넣지 않고 폼에서 정해요. 저장하기 전까지는 비공개 준비 상태예요.

## 문제 종류 (kind)

| kind | 학생 화면 | 채점 |
|---|---|---|
| `code` | 코드 입력창, ▶ 실행, ✅ 제출 | `tests` 로 자동 채점 (통과한 테스트 수 ÷ 전체 × 배점) |
| `short` | 칸마다 답을 쓰는 입력 칸 | `answers` 로 칸마다 자동 채점 (맞은 칸 ÷ 전체 칸 × 배점) |
| `essay` | 글로 답을 쓰는 입력창 | 선생님이 점수를 매겨요 (`rubric` 은 선생님만 보여요) |

```json
{ "kind": "code", "title": "성적 등급", "body": "…", "points": 3,
  "tests": [ { "input": "85\n", "output": "B", "hidden": true } ] }

{ "kind": "short", "title": "연산자 계산", "body": "(1) `7 // 2` …", "points": 2,
  "answers": [ { "label": "(1)", "type": "t", "value": "3", "alts": [] },
               { "label": "(2)", "type": "c", "value": "2" } ] }

{ "kind": "essay", "title": "remove 와 pop 의 차이", "body": "…", "points": 4,
  "rubric": "지우는 기준 2점, 돌려주는 값 2점" }
```

- `short` 의 `type`: `t` 글자 그대로 · `c` 번호 선택(①②③ 또는 1 2 3) · `x` 식·코드 한 줄 · `k` 키워드 포함. 서술(`m`)은 단답에 넣을 수 없어요. 서술형은 `essay` 로 따로 만들어요.
- `alts` 는 다른 정답이에요. (예: `"[1, 2]"` 와 `"[1,2]"`)
- `points` 가 없으면 100점이에요. 합계가 얼마든 순위는 점수 합으로 매겨져요.
- 본문(`body`)은 문제집과 같은 서식(```io, ```box, ```program …)을 써요.

## 문제집 JSON 규칙 (pynest-problemset-v1 을 올릴 때)

- 모든 문제를 위에서부터 차례로 가져와요. (`chapters` → `sections` → `problems`, 마지막에 `elite`)
- `tests` 가 있으면 💻 코드, `answers` 에 자동 채점 칸(`t`, `c`, `x`, `k`)이 있으면 📝 단답, 서술(`m`)뿐이거나 둘 다 없으면 ✍️ 서술형이 돼요.
- 서술형의 `check` 와 모범 답안이 채점 기준 칸에 들어가요.
- 문제 제목은 `label` 이 있으면 그것, 없으면 "문제 n" 이에요. `points` 가 `null` 이면 100점이라 가져온 뒤 고쳐 주세요.

## 업데이트 순서 (5.4.0)

1. Supabase SQL 편집기에서 `v540_exam_short.sql` 실행 (한 번만)
2. 사이트 파일(`app.js`, `patchnotes.js`, `style.css`) 올리기
