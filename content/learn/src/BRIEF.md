# L.O.T.C. 코스 제작 브리프 (서브에이전트용)

너는 PyNest(광주과학고 1·2학년 정보 시험 대비 학습 사이트)의 **기본편 학습 코스 L.O.T.C.** 한 단계를 만든다.
목표: 이 코스 + 연계 문제집만으로 해당 시험 약 75점(A0). 학생이 읽는 글은 **친근한 존댓말(~해요)**.

## 반드시 먼저 읽을 것
- `/home/claude/pynest/content/learn/src/lotc.py` — 빌더. 모든 정답·출력·테스트를 python3 로 **실제 실행**해 만들고 검사한다. 함수 시그니처를 정독.
- `/home/claude/pynest/content/learn/src/beta.py` — 완성 예시(β 레슨 1~2). **이 밀도·톤·구성을 그대로 따라라.**
- `/home/claude/pynest/LEARN_JSON_GUIDE.md` 의 v2 부분(157행~) — 블록·문제 종류 스펙.

## 산출물
- `/home/claude/pynest/content/learn/src/<이름>.py` (예: gamma.py) — `from lotc import *`, 맨 아래 `C.save(sys.argv[1])`.
- 실행: `cd /home/claude/pynest/content/learn/src && python3 gamma.py $SCRATCH/gamma.json && node validate.js $SCRATCH/gamma.json`
  - `$SCRATCH=/tmp/claude-0/-home-claude-pynest/4d0b004a-377b-5307-9954-7b1c3d85505d/scratchpad`
  - 오류 0, `✅` 와 `OK` 가 나올 때까지 고친다. **git 커밋·푸시·Supabase·메모리 쓰기는 하지 마라**(메인이 한다). 다른 .py 파일은 건드리지 마라. lotc.py 수정이 꼭 필요하면 하지 말고 우회하라.
- 마지막 답변: 레슨 제목 목록, 레슨별 확인문제/실습 수, 코스 설명에 넣은 범위 문구(scope_text), 해석·가정, 남은 문제점. 짧게.

## 코스 규칙 (형 요구 — 반드시)
- `Course(문자, scope_text)` — scope_text 는 "1학년 2학기 1차고사 범위: 개념, 개념, …" 처럼 시험 범위 + 실제 만든 레슨 주제 나열. 설명 형식은 lotc.py 가 자동 생성.
- 레슨 **8~14개**, 제목은 `γ-01 …` 식. 레슨마다 `minutes`, `summary`(핵심 정리 3~5줄 마크다운).
- **레슨 1**: 시험 범위·문항 모양·활용법 안내 + **이전 단계 지식 점검**(확인 문제 포함). 레슨 2부터 **첫 단계는 `L.review(...)`** 로 직전 1~2개 레슨 복습 + 짧은 확인 문제(`review=True`).
- 개념은 `L.explain(title, [묶음1], [묶음2], …)` 로 **쪼갠다**: 묶음 = 글(T) 3~6줄 + 도구 1개. 도구를 골고루: CALL(TIP/WARN/KEY/EXAM/THINK), CMP, TABS, FLIP, REVEAL/REVEAL_RUN, STEPS, TRACE, IDX, SLC, CODE.
- **개념 하나 끝날 때마다 확인 문제.** 레슨당 확인 문제 **6개 이상**(8~10 권장). ox/choice 만 반복 금지 — match·order·bucket·output·spot·fill·short·essay 를 섞는다. output 문제는 정답이 자동 계산되니 해설에 `{out}` 를 써서 출력 표시. 레슨마다 essay 1개 이상(시험 서술형: "오류 이유", "조건과 연결", "차이 서술").
- **레슨마다 practice 필수 + [기출유사] 1~2개**: 제목 `[기출유사] …`. body 는 시험처럼 상황 + **[조건]** 불릿 + `{ex}`/`{ex2}`(실행예시 자동 삽입). 공개 입력 2개 + hidden 경계값 3개 이상. hints 3단계. solution 은 주석 달기. starter 는 뼈대만(자동으로 '스타터가 통과하면 오류' 검사함). 난이도: 시험 4~12점대(Beginner~Intermediate).
- 제약 조건형(sorted 금지 등)은 자동 채점에 금지 검사가 없으니 조건을 지문에 서술만 하고, 훈련은 spot/short/essay 로.
- 흐름: 복습 → 개념(쪼개서) → 확인 → 개념 → 확인 … → 기출유사 실습 → (essay). 레슨당 단계 15~30개 정도(120 이하).
- 기출 단골 소재(은행·도서관·도어락·주사위·시계·비밀번호·주민/우편번호·공부시간·타자연습·학급문고·노래자랑·환율·점자 등)를 쓰되 **시험 원문을 베끼지 말고 구조를 바꾼 변형**으로.
- 기본편 = Beginner + Intermediate 만. Advanced(클로저·데코레이터·다중상속 MRO 심화·큰 종합 프로그램)는 응용편 몫이라 넣지 않거나 아주 가볍게.

## 실행 환경 제약 (중요)
- 사이트는 브라우저 Pyodide 로 실행하며 **numpy·pandas·sklearn 이 로드되지 않는다**. 그런 코드는 `CODE(..., run_=False)` (로컬에서는 실제 실행·검증됨), output 문제는 로컬 실행값이 정답이 되니 OK(학생은 읽고 예측만 함). **practice 의 solution 에는 numpy/pandas/sklearn 금지** — 순수 파이썬으로.
- practice 의 solution/starter 에서 `input("안내문")` 의 안내문은 사이트가 지워 버리니 **그냥 `input()`** 을 써라. random/time 결과에 의존하는 출력 금지.
- 파일 입출력 practice 는 프로그램 안에서 파일을 먼저 쓰고 다시 읽는 식으로(입력 파일 제공 불가). CODE/output 에서 파일을 쓰면 lotc.run 의 files= 인자로 미리 파일을 줄 수 있다(브라우저에선 없을 수 있으니 그런 CODE 는 run_=False).
- 오류를 보여 주는 CODE/side 는 `expect_error=True`. spot 은 가능하면 `error_line=` 로 검증.
- 확신 없는 사실은 쓰지 말고 실행해서 확인. 수식은 `$...$` 대신 평문/코드로(마크다운 렌더러가 LaTeX 를 지원하는지 모름) — 꼭 필요하면 `MSE = (1/n) * Σ (y - ŷ)²` 처럼.
