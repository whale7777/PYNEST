# PyNest 카카오톡 챗봇 설정 (V3.4.0)

학생이 PyNest 카카오톡 **채널**을 친구 추가하고 1:1 채팅에서 `랭킹`, `내 프로필`, `티어` 를 치면 답해주는 봇이에요.
(단체/오픈채팅방에는 공식적으로 봇을 넣을 수 없어요.)

## 1. Supabase
1. SQL Editor 에서 `v340_kakao.sql` 한 번 실행 (표 3개 + 함수 추가만 해요).
2. Edge Function 배포 (Supabase CLI):
   ```
   supabase login
   supabase link --project-ref zzvmssovcmaovraebssk
   supabase secrets set BOT_SECRET=아주-긴-아무-문자열
   supabase functions deploy kakao-bot --no-verify-jwt
   ```
   → 스킬 서버 주소: `https://zzvmssovcmaovraebssk.supabase.co/functions/v1/kakao-bot`
   (`--no-verify-jwt` 는 카카오가 Supabase 로그인 토큰을 못 보내서 필요해요. 대신 `x-bot-secret` 헤더로 막아요.)

## 2. 카카오
1. 카카오톡 채널 만들기 (https://center-pf.kakao.com)
2. 카카오 i 오픈빌더 (https://i.kakao.com) 에서 봇 만들기 → 카카오톡 채널 연결 → 배포 승인 대기
3. **스킬** 만들기: URL = 위 스킬 서버 주소, 헤더값에 `x-bot-secret` = `BOT_SECRET` 값
4. **폴백 블록**(어떤 말이든 받는 블록)에 위 스킬을 연결 → 모든 입력이 Edge Function 으로 가요. (명령 해석은 서버가 해요)
5. 배포

## 3. 사용
- 학생: PyNest [설정 → 카카오톡 연동 → 연동 코드 받기] → 채널 채팅에 `연동 123456`
- 명령: `랭킹` `월간랭킹` `전체랭킹` `내 프로필` `티어` `연동해제`

## 참고
- 코드는 10분 유효, 1회용. 틀리게 5번 입력하면 10분 잠겨요.
- 카톡에는 별명(없으면 아이디)만 나가고, 직원 계정은 점수가 나가지 않아요.
- 봇이 먼저 말 거는 알림(푸시)은 카카오 알림톡(유료·사전 심사)이 필요해서 이번 버전엔 없어요.
