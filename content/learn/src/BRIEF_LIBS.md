# 추가 작업: numpy·pandas·sklearn 실행 지원 반영 (V5.10.1~2)

형(선생님)이 사이트에서 **numpy·pandas·scipy·sklearn·matplotlib** 가 실행되게 해 놨다. (seaborn 은 여전히 안 됨, 그림은 화면에 안 뜸)
- 사이트 실행 환경 = Pyodide 0.26.4: Python 3.12, numpy 1.26.4, pandas 2.2.0, scikit-learn 1.4.2, scipy 1.12.
- 로컬 검증은 **반드시** 같은 버전으로: `export LOTC_PY=/tmp/claude-0/-home-claude-pynest/4d0b004a-377b-5307-9954-7b1c3d85505d/scratchpad/pyo/bin/python` 을 하고 빌드한다(lotc.run 이 이 파이썬을 씀).
- 코드에 `import numpy as np` 처럼 import 가 있으면 사이트가 패키지를 자동으로 불러온다. 또 단계에 `"libs": ["numpy"]` 를 적으면 import 없이도 `np`/`pd` 가 자동 import 된다.
- lotc.py 변경(이미 반영됨):
  - `CODE(..., run_=False)` 인데 코드가 numpy/pandas/sklearn/scipy/matplotlib 를 import 하고 seaborn·files·expect_error 가 없으면 **자동으로 실행 가능**(run 버튼)으로 바뀐다. 다른 이유(여러 파일 모듈 예제 등)로 막은 건 그대로.
  - `L.practice(..., libs=['numpy'], after_last_practice=True)` — libs 를 단계에 기록, after_last_practice=True 면 레슨의 마지막 practice 바로 뒤에 끼워 넣는다(essay 앞).
  - `C.find('γ-13')` — 제목 접두사로 레슨 찾기.
- 제약: **TRACE(한 줄씩 추적)에는 라이브러리 코드를 쓰지 마라**(추적기는 패키지를 못 불러옴). 실습 출력은 numpy 배열 repr 대신 `int()`·`round()`·f-string·`tolist()` 로 안정적인 글자로 찍어라. 실습 한 번 실행은 10초 안(작은 데이터). random_state 고정.

## 할 일 (맡은 코스 .py 만 수정)
1. 학생에게 "사이트에서 numpy/pandas/sklearn 이 실행되지 않는다", "▶ 실행 안 됨", "손으로만 예측" 류로 쓴 문장을 **모두** 고친다(이제 ▶ 실행으로 직접 확인해 보라는 식). seaborn 관련 문장은 seaborn 만 안 된다고 정확히.
2. "numpy 없이 / 순수 파이썬으로 흉내" 실습은 **실제 라이브러리로 푸는 실습으로 바꾸거나**, 순수 파이썬판을 남기는 게 학습상 의미 있으면(예: 시험의 '내장함수 안 쓰기') 그대로 두고 **라이브러리판 [기출유사] 실습을 1개 추가**한다. 시험이 numpy/pandas/sklearn 코드를 쓰게 하므로, 라이브러리를 다루는 레슨마다 **실제 라이브러리를 쓰는 [기출유사] 실습이 최소 1개** 있어야 한다. (`libs=[...]`, starter 에도 import 한 줄 넣기, hidden 3개 이상)
3. 라이브러리 레슨의 확인 문제 해설·설명도 자연스럽게 다듬되, 레슨 구조(복습→개념→확인→실습→essay)와 기존 문제 수는 유지. 단계 120 이하.
4. 빌드·검증: `cd /home/claude/pynest/content/learn/src && export LOTC_PY=... && python3 <코스>.py /tmp/claude-0/-home-claude-pynest/4d0b004a-377b-5307-9954-7b1c3d85505d/scratchpad/v2/<코스>.json && node validate.js <같은 경로>` 오류 0. 단, validate.js 는 /home/claude/pynest/app.js(옛 버전) 기준이라 libs 를 무시할 뿐 오류는 안 난다 — OK.
- git·Supabase·메모리 금지, 다른 .py·lotc.py 수정 금지.
- 마지막 답변: 고친 문장 수, 추가/교체한 실습(레슨·제목), 남은 문제. 짧게.
