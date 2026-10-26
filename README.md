# PyNest 설치 안내 🐍

파일 6개(`index.html`, `style.css`, `app.js`, `config.js`, `schema.sql`, `README.md`)로 이루어진 사이트예요.
화면은 GitHub Pages에, 로그인·게시판·파일 저장은 Supabase에 맡기는 구조예요. 둘 다 무료 플랜으로 시작할 수 있어요. (무료 조건은 바뀔 수 있으니 가입할 때 확인해주세요.)

## 1. Supabase 프로젝트 만들기
1. https://supabase.com 에 가입하고 **New project**를 눌러요.
2. 이름은 아무거나, Region은 **Northeast Asia (Seoul)** 을 고르고, DB 비밀번호를 정해서 어딘가에 적어둬요.
3. 프로젝트가 만들어질 때까지 1~2분 기다려요.

## 2. 이메일 확인 끄기 (중요!)
이 사이트는 ID를 가짜 이메일(`아이디@pyclass.site`)로 바꿔서 로그인해요. 진짜 메일은 안 보내니까 확인 기능을 꺼야 해요.
- **Authentication → Sign In / Providers → Email** 로 들어가서 **Confirm email** 을 **끄고** 저장해요.
- (메뉴 이름은 Supabase 업데이트에 따라 조금 다를 수 있어요.)

## 3. 데이터베이스 설정
1. 왼쪽 메뉴 **SQL Editor → New query**.
2. `schema.sql` 내용을 통째로 붙여넣고 **Run**.
3. `Success` 가 뜨면 끝이에요. 'Security Definer View' 경고가 보여도 의도한 거라 괜찮아요.

## 4. 주소와 키 넣기
1. **Project Settings → API** (또는 상단 **Connect**) 에서 두 개를 찾아요.
   - **Project URL**
   - **anon public** 키
2. `config.js` 를 열어서 `여기에_Project_URL`, `여기에_anon_public_key` 자리에 붙여넣어요.
3. **service_role 키는 절대 넣지 마세요.** anon 키는 공개돼도 괜찮게 설계되어 있어요.

## 5. GitHub Pages에 올리기
1. GitHub에서 새 저장소(Repository)를 만들어요. (Public)
2. **Add file → Upload files** 로 `index.html`, `style.css`, `app.js`, `config.js` 4개를 올리고 Commit해요. (`schema.sql`, `README.md`는 안 올려도 돼요.)
3. **Settings → Pages → Branch: main / (root)** 로 저장해요.
4. 1~2분 뒤 `https://아이디.github.io/저장소이름/` 에서 사이트가 열려요.

## 6. 관리자(선생님) 계정 만들기
1. 사이트에서 **가입 신청** 탭으로 형이 쓸 ID와 비밀번호로 가입 신청해요.
2. Supabase **SQL Editor** 에서 아래를 실행해요. (`내아이디` 부분만 바꾸세요)
   ```sql
   update public.profiles set role = 'admin', status = 'approved' where username = '내아이디';
   ```
3. 사이트에서 로그인하면 메뉴에 **🛠️ 관리자**가 보여요.

## 7. 학생 받기
- 학생에게 사이트 주소와 쓸 ID를 알려주면, 학생이 **가입 신청**을 하고 관리자 → 회원 탭에서 **승인**하면 돼요.
- 비밀번호는 학생이 ⚙️ 설정에서 바꿀 수 있고, 잊어버리면 관리자 → 회원 탭의 **비밀번호 초기화** 를 쓰면 돼요.

## 이용 방법 요약
- **강의**: 관리자 → 강의 탭에서 주차, 제목, YouTube 일부 공개 링크를 넣으면 사이트 안에서 재생돼요.
- **문제**: 관리자 → 문제 탭에서 PDF를 올리면 로그인한 학생만 받을 수 있어요.
- **공지**: 선생님만 쓸 수 있어요.
- **질문 게시판**: 학생이 익명 여부와 댓글 허용 여부를 고를 수 있어요.
- **과제**: 내용에 코드를 붙여넣거나(```로 감싸면 코드 모양) 파일을 첨부해요. 본인과 선생님만 볼 수 있고, 선생님이 댓글로 피드백해요.
- **다크모드**: 상단 🌙/☀️ 버튼이나 설정에서 켜고 꺼요.

## 알아둘 점
- 익명은 **화면상 익명**이에요. 선생님에게는 항상 작성자가 보이고(`익명 작성` 표시), 학생끼리는 이름이 가려져요. 다만 개발자 도구로 서버를 직접 뒤지는 학생까지 완벽히 막는 건 아니에요.
- 무료 Supabase 프로젝트는 일주일쯤 아무도 접속하지 않으면 일시정지될 수 있어요. 대시보드에서 다시 켜면 돼요.
- 게시글 수정 기능은 아직 없어요. 삭제 후 다시 쓰면 돼요.
- 비밀번호 초기화(`admin_reset_password`)는 Supabase 내부 인증 테이블을 직접 바꾸는 방식이라 꼭 한 번 테스트해보세요. 오류가 나면 오류 메시지를 알려주세요.
- 온라인 저지와 라이브 메뉴는 자리만 만들어 뒀어요.

## 직원 권한 (OWNER / ADMIN / TEACHER / MOD)
- **`staff_roles.sql`** 을 Supabase SQL Editor 에서 한 번 실행하세요 (민혁닷컴 저장소의 같은 파일이에요). 기존 데이터·정책은 그대로 두고 "추가"만 해요.
- 원래 관리자(imadmin)는 자동으로 OWNER 예요. 🛠️ 관리자 › **🎖️ 권한** 탭에서 PyNest ID 로 역할을 부여해요 (민혁닷컴과 공유).
- OWNER 전부 · ADMIN 전부(ADMIN 임명 제외) · TEACHER 강의·문제집·문제·숙제·제출함 · MOD 회원 승인/중지·글·댓글 삭제
- 제출함·채점은 OWNER/ADMIN/TEACHER, 라이브는 OWNER/ADMIN 만 볼 수 있어요.

## 학생 등급 (STUDENT / SOLVER / LISTENER)
- **`student_tiers.sql`** 을 Supabase SQL Editor 에서 한 번 실행하세요 (`staff_roles.sql` 이 먼저 적용돼 있어야 해요). 기존 정책은 그대로 두고 제한만 "추가"해요.
- 등급이 없는 기존 학생은 전부 **STUDENT** (지금과 똑같이 전부 이용).
- **SOLVER** 문제(문제집·숙제·제출)만 · 강의·라이브 X / **LISTENER** 강의·라이브 시청 O · 문제·라이브 문제 X. 공지·질문·과제·자유 게시판은 모두 가능.
- 직원(OWNER/ADMIN/TEACHER/MOD)은 등급과 상관없이 제한 없음. 부여는 🛠️ 관리자 › 👥 회원 › 승인된 학생 옆 버튼 (회원 관리 권한: OWNER/ADMIN/MOD).
- 표를 바꾸려면 SQL 의 `tier_allows()` 와 `app.js` 의 `TIER_OK`(그리고 `golive.js` 의 `tierCan`)를 같이 고쳐요.

## V3.1.0 — 별명 · 랭킹 · 티어 · 프로필 · 난이도
- **`v310_ranking.sql`** 을 Supabase SQL Editor 에서 한 번 실행하세요 (`staff_roles.sql` 먼저). 기존 데이터는 그대로예요. 실행 전에는 예전처럼 동작해요.
- **별명**: 🛠️ 관리자 › 🏷️ 별명 (직원 누구나). 학생에겐 별명만, 직원에겐 `별명 (ID)` 로 보여요.
- **랭킹**: 🏆 랭킹 — 주간(월~일)/월간, 그 기간에 새로 맞춘 서로 다른 문제 개수 순 (한국 시간).
- **티어**: 누적 점수 → Bronze 0 · Silver 100 · Gold 500 · Platinum 1500 · Diamond 3500 · Emerald 7000 · Master 12000 · The Programmer 20000, 각 티어 V~I(I 최고). 뱃지로 표시, 구간은 `app.js` 의 `TIERS`.
- **프로필**: 이름을 누르면 점수·티어·주/월 순위·난이도별 푼 개수·최근 푼 문제(`Advanced 12 (#345)` = 문제집 안 번호 + 고유 번호).
- **점수**: 문제 점수 = 문제의 🏆 랭킹 점수(선택) → 없으면 난이도 점수. 🛠️ 관리자 › 🎯 난이도에서 점수 조정·난이도 추가. 기본 Beginner 10 / Intermediate 30 / Advanced 60 / ELITE 100. (기존 "배점"은 그대로 따로 있어요.)
