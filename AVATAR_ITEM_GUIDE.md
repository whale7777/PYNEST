# PyNest 캐릭터 아이템 JSON 가이드 (pynest-avatar-item-v1, V4.5.1)

관리자 › 🎁 아이템 › "아이템 올리기" 에 파일을 고르거나 붙여넣고 [미리보기] → [올리기].
같은 `id` 로 다시 올리면 덮어써요. 예시는 `avatar_items_sample.json`.

## 형식
```json
{ "format": "pynest-avatar-item-v1",
  "items": [ { "id": "red_cap", "name": "빨간 야구모자", "descr": "설명(선택)", "slot": "hat",
               "svg": "<path d=\"...\" fill=\"#ef4444\"/>",
               "unlock": { "type": "price", "price": 30 } } ] }
```
| 필드 | 설명 |
|---|---|
| id | 영문 소문자·숫자·`_` 2~40자 (바꾸면 다른 아이템) |
| name | 1~30자 |
| slot | `hat` 모자 · `hair` 머리 · `face` 얼굴 · `outfit` 옷 · `back` 뒤(날개·망토) · `deco` 장식 |
| svg | 100×100 칸 기준 도형 조각 (아래 규칙) |
| unlock.type | `free` 누구나 · `score` 랭킹 점수 기준 `value` 이상 · `tier` 큰 등급 `value` 이상(0 Bronze, 1 Silver, 2 Gold, 3 Platinum, 4 Diamond …) · `streak` 연속 출석 최고 기록 `value`일 이상 · `rank1` 주간/월간 랭킹 1등 `value`회 이상 · `price` 파이포인트 `price` · `reward` 문제 보상 전용 · `event` 행사 전용 |

## SVG 규칙
- `<svg>` 태그 없이 **도형 조각만**. 좌표는 0~100 (캐릭터 칸). 칸 밖으로 조금 나가도 돼요.
- 쓸 수 있는 것: `g path circle ellipse rect line polyline polygon defs linearGradient radialGradient stop`
- 쓸 수 없는 것: script, image, text, use, 외부 주소, `on...` 이벤트, style → 올릴 때 거부되거나 지워져요.
- 그리는 순서: back(맨 뒤) → 몸·옷 → outfit → 얼굴 → face → 머리 → hair → 모자 → hat → deco(맨 앞)

## 캐릭터 좌표 (그리는 기준)
- 얼굴 타원: 중심 (50,46), 가로 반지름 24, 세로 26 → 머리 꼭대기 y=20, 턱 y=72
- 눈: (40,46) (60,46) · 입: y≈58~62 · 볼: (35,55) (65,55)
- 목 y 56~70, 몸통은 y 68 아래 · 귀 x≈26, 74
- 모자는 y -4 ~ 40 사이, 날개/망토는 어깨(30,68)·(70,68)에서 퍼지게

## 문제 보상으로 주려면
1. `unlock.type` 을 `reward` 로 올리고
2. 관리자 › 🎁 아이템 › "문제 보상 연결" 에서 문제집 → 문제 → 아이템을 고르면, 그 문제를 **처음 맞춘** 학생에게 자동 지급 + 알림.

## AI 에게 아이템 만들게 하는 프롬프트
> 너는 PyNest 캐릭터 꾸미기 아이템 디자이너야. 아래 규칙으로 아이템 N개를 JSON 하나로만 출력해. 설명 문장 없이 JSON만.
> - format "pynest-avatar-item-v1", items 배열. 각 항목: id(영문 소문자·숫자·_), name(한글 30자 이내), descr, slot(hat/hair/face/outfit/back/deco), svg, unlock{type,value|price}
> - svg 는 `<svg>` 없이 도형 조각만(path, circle, ellipse, rect, polygon, g, linearGradient). 100×100 좌표. script·image·text·외부주소 금지. 문자열 안의 따옴표는 `\"` 로 이스케이프.
> - 캐릭터: 얼굴 타원 중심(50,46) rx24 ry26, 눈 (40,46)(60,46), 입 y≈60, 머리 꼭대기 y=20, 몸통 y≥68. 모자는 머리 위(y -4~40)에, 날개는 어깨 (30,68)(70,68) 뒤로.
> - 귀엽고 단순한 플랫 스타일(외곽선 1~1.5px, 색 2~3개). 주제: (여기에 원하는 주제)
