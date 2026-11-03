-- PyNest V4.5.3 · v453_board_badges.sql
-- 1) 공지 "배너 띄우기" (고정과 따로)  2) 배지 170개 + 새 조건 종류  3) 기존 데이터는 하나도 안 건드려요
-- Supabase SQL Editor 에서 한 번만 실행하세요. (여러 번 실행해도 안전해요)

do $$
begin
  if to_regclass('public.badge_defs') is null or to_regclass('public.posts_view') is null or to_regclass('public.avatar_items') is null then
    raise exception 'v390 / v450 / v451b / v452 SQL 을 먼저 실행해주세요.';
  end if;
end $$;

-- 1) 배너 칸
alter table public.posts add column if not exists banner boolean not null default false;

create or replace function public.posts_guard()
returns trigger
language plpgsql security definer set search_path = public
as $$
begin
  if new.pinned and not (new.board = 'notice' and public.staff_can('notice')) then
    new.pinned := false;
  end if;
  if new.banner and not (new.board = 'notice' and public.staff_can('notice')) then
    new.banner := false;
  end if;
  if new.auto_key is not null and coalesce(current_setting('pynest.autopost', true), '') <> '1' then
    new.auto_key := case when tg_op = 'UPDATE' then old.auto_key else null end;
  end if;
  return new;
end;
$$;

create or replace view public.posts_view as
 select p.id, p.board, p.title, p.content, p.anonymous, p.allow_comments, p.week, p.files, p.created_at, p.updated_at,
        (p.author_id = auth.uid()) as is_mine,
        case when (p.anonymous and (p.author_id <> auth.uid()) and (not public.staff_can('review'::text))) then '익명'::text
             else public.disp(p.author_id) end as author_name,
        case when (p.anonymous and (p.author_id <> auth.uid()) and (not public.staff_can('review'::text))) then null::uuid
             else p.author_id end as author_id,
        p.pinned,
        p.banner
   from (public.posts p join public.profiles pr on pr.id = p.author_id)
  where public.is_approved() and ((p.board <> 'assignment'::text) or (p.author_id = auth.uid()) or public.staff_can('review'::text));

-- 2) 배지 조건 종류 늘리기
alter table public.badge_defs drop constraint if exists badge_defs_kind_check;
alter table public.badge_defs add constraint badge_defs_kind_check check (kind in (
  'score', 'solved', 'streak', 'learn', 'exam_first', 'exam_join', 'pypoint', 'manual',
  'tier', 'rank1', 'items', 'sales', 'market_made', 'attend', 'event', 'shield', 'posts', 'comments'));

insert into public.badge_defs (id, name, descr, icon, kind, threshold, tone, position, builtin) values
  ('score_200', '200점 달성', '랭킹 점수 200점을 넘었어요', '⭐', 'score', 200, 'blue', 200, false),
  ('score_300', '300점 달성', '랭킹 점수 300점을 넘었어요', '⭐', 'score', 300, 'blue', 201, false),
  ('score_400', '400점 달성', '랭킹 점수 400점을 넘었어요', '⭐', 'score', 400, 'teal', 202, false),
  ('score_700', '700점 달성', '랭킹 점수 700점을 넘었어요', '🌟', 'score', 700, 'teal', 203, false),
  ('score_1500', '1,500점 달성', '랭킹 점수 1,500점을 넘었어요', '🌟', 'score', 1500, 'green', 204, false),
  ('score_2000', '2,000점 달성', '랭킹 점수 2,000점을 넘었어요', '💫', 'score', 2000, 'green', 205, false),
  ('score_2500', '2,500점 달성', '랭킹 점수 2,500점을 넘었어요', '💫', 'score', 2500, 'orange', 206, false),
  ('score_4000', '4,000점 달성', '랭킹 점수 4,000점을 넘었어요', '💫', 'score', 4000, 'orange', 207, false),
  ('score_5000', '5,000점 달성', '랭킹 점수 5,000점을 넘었어요', '✨', 'score', 5000, 'red', 208, false),
  ('score_7000', '7,000점 달성', '랭킹 점수 7,000점을 넘었어요', '✨', 'score', 7000, 'red', 209, false),
  ('score_15000', '15,000점 달성', '랭킹 점수 15,000점을 넘었어요', '🏆', 'score', 15000, 'purple', 210, false),
  ('score_20000', '20,000점 달성', '랭킹 점수 20,000점을 넘었어요', '🏆', 'score', 20000, 'purple', 211, false),
  ('score_30000', '30,000점 달성', '랭킹 점수 30,000점을 넘었어요', '🏆', 'score', 30000, 'pink', 212, false),
  ('score_75000', '75,000점 달성', '랭킹 점수 75,000점을 넘었어요', '👑', 'score', 75000, 'pink', 213, false),
  ('score_100000', '100,000점 달성', '랭킹 점수 100,000점을 넘었어요', '👑', 'score', 100000, 'gold', 214, false),
  ('solve_5', '5문제 풀이', '총 5문제를 맞췄어요', '🧩', 'solved', 5, 'blue', 215, false),
  ('solve_15', '15문제 풀이', '총 15문제를 맞췄어요', '🧩', 'solved', 15, 'blue', 216, false),
  ('solve_20', '20문제 풀이', '총 20문제를 맞췄어요', '🧩', 'solved', 20, 'teal', 217, false),
  ('solve_30', '30문제 풀이', '총 30문제를 맞췄어요', '🎯', 'solved', 30, 'teal', 218, false),
  ('solve_40', '40문제 풀이', '총 40문제를 맞췄어요', '🎯', 'solved', 40, 'green', 219, false),
  ('solve_60', '60문제 풀이', '총 60문제를 맞췄어요', '🔥', 'solved', 60, 'green', 220, false),
  ('solve_75', '75문제 풀이', '총 75문제를 맞췄어요', '🔥', 'solved', 75, 'orange', 221, false),
  ('solve_80', '80문제 풀이', '총 80문제를 맞췄어요', '🔥', 'solved', 80, 'orange', 222, false),
  ('solve_150', '150문제 풀이', '총 150문제를 맞췄어요', '💪', 'solved', 150, 'red', 223, false),
  ('solve_200', '200문제 풀이', '총 200문제를 맞췄어요', '💪', 'solved', 200, 'red', 224, false),
  ('solve_250', '250문제 풀이', '총 250문제를 맞췄어요', '🚀', 'solved', 250, 'purple', 225, false),
  ('solve_400', '400문제 풀이', '총 400문제를 맞췄어요', '🚀', 'solved', 400, 'purple', 226, false),
  ('solve_500', '500문제 풀이', '총 500문제를 맞췄어요', '🚀', 'solved', 500, 'pink', 227, false),
  ('solve_700', '700문제 풀이', '총 700문제를 맞췄어요', '🛰️', 'solved', 700, 'pink', 228, false),
  ('solve_1000', '1,000문제 풀이', '총 1,000문제를 맞췄어요', '🛰️', 'solved', 1000, 'gold', 229, false),
  ('streak_2', '2일 연속 학습', '2일 연속으로 학습했어요', '🔥', 'streak', 2, 'blue', 230, false),
  ('streak_10', '10일 연속 학습', '10일 연속으로 학습했어요', '🔥', 'streak', 10, 'blue', 231, false),
  ('streak_20', '20일 연속 학습', '20일 연속으로 학습했어요', '📆', 'streak', 20, 'teal', 232, false),
  ('streak_21', '21일 연속 학습', '21일 연속으로 학습했어요', '📆', 'streak', 21, 'green', 233, false),
  ('streak_45', '45일 연속 학습', '45일 연속으로 학습했어요', '🗓️', 'streak', 45, 'green', 234, false),
  ('streak_50', '50일 연속 학습', '50일 연속으로 학습했어요', '🗓️', 'streak', 50, 'orange', 235, false),
  ('streak_60', '60일 연속 학습', '60일 연속으로 학습했어요', '🏅', 'streak', 60, 'red', 236, false),
  ('streak_75', '75일 연속 학습', '75일 연속으로 학습했어요', '🏅', 'streak', 75, 'purple', 237, false),
  ('streak_150', '150일 연속 학습', '150일 연속으로 학습했어요', '💎', 'streak', 150, 'purple', 238, false),
  ('streak_200', '200일 연속 학습', '200일 연속으로 학습했어요', '💎', 'streak', 200, 'pink', 239, false),
  ('streak_365', '365일 연속 학습', '365일 연속으로 학습했어요', '🌋', 'streak', 365, 'gold', 240, false),
  ('learn_3', '레슨 3개 완료', '학습 레슨을 3개 끝냈어요', '📚', 'learn', 3, 'blue', 241, false),
  ('learn_5', '레슨 5개 완료', '학습 레슨을 5개 끝냈어요', '📚', 'learn', 5, 'teal', 242, false),
  ('learn_20', '레슨 20개 완료', '학습 레슨을 20개 끝냈어요', '📖', 'learn', 20, 'green', 243, false),
  ('learn_30', '레슨 30개 완료', '학습 레슨을 30개 끝냈어요', '📖', 'learn', 30, 'orange', 244, false),
  ('learn_50', '레슨 50개 완료', '학습 레슨을 50개 끝냈어요', '🎓', 'learn', 50, 'red', 245, false),
  ('learn_75', '레슨 75개 완료', '학습 레슨을 75개 끝냈어요', '🎓', 'learn', 75, 'purple', 246, false),
  ('learn_100', '레슨 100개 완료', '학습 레슨을 100개 끝냈어요', '🧠', 'learn', 100, 'pink', 247, false),
  ('learn_150', '레슨 150개 완료', '학습 레슨을 150개 끝냈어요', '🧠', 'learn', 150, 'gold', 248, false),
  ('examj_3', '시험 3회 응시', '시험에 3번 참가했어요', '📝', 'exam_join', 3, 'blue', 249, false),
  ('examj_5', '시험 5회 응시', '시험에 5번 참가했어요', '📝', 'exam_join', 5, 'green', 250, false),
  ('examj_10', '시험 10회 응시', '시험에 10번 참가했어요', '🖊️', 'exam_join', 10, 'red', 251, false),
  ('examj_20', '시험 20회 응시', '시험에 20번 참가했어요', '🎫', 'exam_join', 20, 'pink', 252, false),
  ('examf_3', '시험 1등 3회', '시험에서 1등을 3번 했어요', '🥇', 'exam_first', 3, 'blue', 253, false),
  ('examf_5', '시험 1등 5회', '시험에서 1등을 5번 했어요', '🏆', 'exam_first', 5, 'green', 254, false),
  ('examf_10', '시험 1등 10회', '시험에서 1등을 10번 했어요', '👑', 'exam_first', 10, 'purple', 255, false),
  ('py_100', '파이포인트 100 모음', '파이포인트를 누적 100 모았어요', '🪙', 'pypoint', 100, 'blue', 256, false),
  ('py_300', '파이포인트 300 모음', '파이포인트를 누적 300 모았어요', '🪙', 'pypoint', 300, 'blue', 257, false),
  ('py_500', '파이포인트 500 모음', '파이포인트를 누적 500 모았어요', '🪙', 'pypoint', 500, 'teal', 258, false),
  ('py_2000', '파이포인트 2,000 모음', '파이포인트를 누적 2,000 모았어요', '💰', 'pypoint', 2000, 'green', 259, false),
  ('py_3000', '파이포인트 3,000 모음', '파이포인트를 누적 3,000 모았어요', '💰', 'pypoint', 3000, 'orange', 260, false),
  ('py_5000', '파이포인트 5,000 모음', '파이포인트를 누적 5,000 모았어요', '💎', 'pypoint', 5000, 'red', 261, false),
  ('py_10000', '파이포인트 10,000 모음', '파이포인트를 누적 10,000 모았어요', '💎', 'pypoint', 10000, 'purple', 262, false),
  ('py_20000', '파이포인트 20,000 모음', '파이포인트를 누적 20,000 모았어요', '🏦', 'pypoint', 20000, 'pink', 263, false),
  ('py_50000', '파이포인트 50,000 모음', '파이포인트를 누적 50,000 모았어요', '🏦', 'pypoint', 50000, 'gold', 264, false),
  ('tier_1', '2번째 티어 도달', '티어가 1번 올랐어요', '🌱', 'tier', 1, 'blue', 265, false),
  ('tier_2', '3번째 티어 도달', '티어가 2번 올랐어요', '🌱', 'tier', 2, 'blue', 266, false),
  ('tier_3', '4번째 티어 도달', '티어가 3번 올랐어요', '🌿', 'tier', 3, 'teal', 267, false),
  ('tier_4', '5번째 티어 도달', '티어가 4번 올랐어요', '🌳', 'tier', 4, 'green', 268, false),
  ('tier_5', '6번째 티어 도달', '티어가 5번 올랐어요', '🌳', 'tier', 5, 'orange', 269, false),
  ('tier_6', '7번째 티어 도달', '티어가 6번 올랐어요', '⛰️', 'tier', 6, 'red', 270, false),
  ('tier_7', '8번째 티어 도달', '티어가 7번 올랐어요', '🏔️', 'tier', 7, 'red', 271, false),
  ('tier_8', '9번째 티어 도달', '티어가 8번 올랐어요', '🏔️', 'tier', 8, 'purple', 272, false),
  ('tier_9', '10번째 티어 도달', '티어가 9번 올랐어요', '🌋', 'tier', 9, 'pink', 273, false),
  ('tier_10', '11번째 티어 도달', '티어가 10번 올랐어요', '🌌', 'tier', 10, 'gold', 274, false),
  ('wins_1', '랭킹 1등 1회', '주간·월간 랭킹 1등을 1번 했어요', '🥇', 'rank1', 1, 'blue', 275, false),
  ('wins_2', '랭킹 1등 2회', '주간·월간 랭킹 1등을 2번 했어요', '🥇', 'rank1', 2, 'teal', 276, false),
  ('wins_3', '랭킹 1등 3회', '주간·월간 랭킹 1등을 3번 했어요', '👑', 'rank1', 3, 'green', 277, false),
  ('wins_5', '랭킹 1등 5회', '주간·월간 랭킹 1등을 5번 했어요', '👑', 'rank1', 5, 'red', 278, false),
  ('wins_10', '랭킹 1등 10회', '주간·월간 랭킹 1등을 10번 했어요', '🏆', 'rank1', 10, 'purple', 279, false),
  ('wins_20', '랭킹 1등 20회', '주간·월간 랭킹 1등을 20번 했어요', '🏆', 'rank1', 20, 'pink', 280, false),
  ('items_1', '아이템 1개 보유', '아이템을 1개 모았어요', '🎒', 'items', 1, 'blue', 281, false),
  ('items_3', '아이템 3개 보유', '아이템을 3개 모았어요', '🎒', 'items', 3, 'blue', 282, false),
  ('items_5', '아이템 5개 보유', '아이템을 5개 모았어요', '🧢', 'items', 5, 'teal', 283, false),
  ('items_10', '아이템 10개 보유', '아이템을 10개 모았어요', '🧢', 'items', 10, 'teal', 284, false),
  ('items_15', '아이템 15개 보유', '아이템을 15개 모았어요', '🎩', 'items', 15, 'green', 285, false),
  ('items_20', '아이템 20개 보유', '아이템을 20개 모았어요', '🎩', 'items', 20, 'green', 286, false),
  ('items_30', '아이템 30개 보유', '아이템을 30개 모았어요', '👗', 'items', 30, 'orange', 287, false),
  ('items_40', '아이템 40개 보유', '아이템을 40개 모았어요', '👗', 'items', 40, 'red', 288, false),
  ('items_50', '아이템 50개 보유', '아이템을 50개 모았어요', '🛍️', 'items', 50, 'red', 289, false),
  ('items_60', '아이템 60개 보유', '아이템을 60개 모았어요', '🛍️', 'items', 60, 'purple', 290, false),
  ('items_70', '아이템 70개 보유', '아이템을 70개 모았어요', '🎁', 'items', 70, 'purple', 291, false),
  ('items_80', '아이템 80개 보유', '아이템을 80개 모았어요', '🎁', 'items', 80, 'pink', 292, false),
  ('items_90', '아이템 90개 보유', '아이템을 90개 모았어요', '💼', 'items', 90, 'pink', 293, false),
  ('items_100', '아이템 100개 보유', '아이템을 100개 모았어요', '💼', 'items', 100, 'gold', 294, false),
  ('sales_1', '마켓 판매 1회', '내가 만든 아이템이 1번 팔렸어요', '💸', 'sales', 1, 'blue', 295, false),
  ('sales_3', '마켓 판매 3회', '내가 만든 아이템이 3번 팔렸어요', '💸', 'sales', 3, 'teal', 296, false),
  ('sales_5', '마켓 판매 5회', '내가 만든 아이템이 5번 팔렸어요', '🏪', 'sales', 5, 'green', 297, false),
  ('sales_10', '마켓 판매 10회', '내가 만든 아이템이 10번 팔렸어요', '🏪', 'sales', 10, 'orange', 298, false),
  ('sales_20', '마켓 판매 20회', '내가 만든 아이템이 20번 팔렸어요', '💰', 'sales', 20, 'red', 299, false),
  ('sales_30', '마켓 판매 30회', '내가 만든 아이템이 30번 팔렸어요', '💰', 'sales', 30, 'purple', 300, false),
  ('sales_50', '마켓 판매 50회', '내가 만든 아이템이 50번 팔렸어요', '🏬', 'sales', 50, 'pink', 301, false),
  ('sales_100', '마켓 판매 100회', '내가 만든 아이템이 100번 팔렸어요', '🏬', 'sales', 100, 'gold', 302, false),
  ('mkmade_1', '마켓 아이템 1개 등록', '마켓에 내 아이템을 1개 올렸어요', '🎨', 'market_made', 1, 'blue', 303, false),
  ('mkmade_3', '마켓 아이템 3개 등록', '마켓에 내 아이템을 3개 올렸어요', '🎨', 'market_made', 3, 'teal', 304, false),
  ('mkmade_5', '마켓 아이템 5개 등록', '마켓에 내 아이템을 5개 올렸어요', '🖌️', 'market_made', 5, 'orange', 305, false),
  ('mkmade_10', '마켓 아이템 10개 등록', '마켓에 내 아이템을 10개 올렸어요', '🧵', 'market_made', 10, 'red', 306, false),
  ('mkmade_20', '마켓 아이템 20개 등록', '마켓에 내 아이템을 20개 올렸어요', '🏭', 'market_made', 20, 'pink', 307, false),
  ('att_1', '출석 1일', '학습한 날이 모두 1일이에요', '📅', 'attend', 1, 'blue', 308, false),
  ('att_5', '출석 5일', '학습한 날이 모두 5일이에요', '📅', 'attend', 5, 'blue', 309, false),
  ('att_10', '출석 10일', '학습한 날이 모두 10일이에요', '📅', 'attend', 10, 'teal', 310, false),
  ('att_20', '출석 20일', '학습한 날이 모두 20일이에요', '🗓️', 'attend', 20, 'green', 311, false),
  ('att_30', '출석 30일', '학습한 날이 모두 30일이에요', '🗓️', 'attend', 30, 'green', 312, false),
  ('att_50', '출석 50일', '학습한 날이 모두 50일이에요', '📆', 'attend', 50, 'orange', 313, false),
  ('att_75', '출석 75일', '학습한 날이 모두 75일이에요', '📆', 'attend', 75, 'red', 314, false),
  ('att_100', '출석 100일', '학습한 날이 모두 100일이에요', '📆', 'attend', 100, 'red', 315, false),
  ('att_150', '출석 150일', '학습한 날이 모두 150일이에요', '🏕️', 'attend', 150, 'purple', 316, false),
  ('att_200', '출석 200일', '학습한 날이 모두 200일이에요', '🏕️', 'attend', 200, 'pink', 317, false),
  ('att_300', '출석 300일', '학습한 날이 모두 300일이에요', '🏰', 'attend', 300, 'pink', 318, false),
  ('att_365', '출석 365일', '학습한 날이 모두 365일이에요', '🏰', 'attend', 365, 'gold', 319, false),
  ('event_1', '행사 보상 1회', '행사 보상을 1번 받았어요', '🎉', 'event', 1, 'blue', 320, false),
  ('event_3', '행사 보상 3회', '행사 보상을 3번 받았어요', '🎉', 'event', 3, 'green', 321, false),
  ('event_5', '행사 보상 5회', '행사 보상을 5번 받았어요', '🎊', 'event', 5, 'red', 322, false),
  ('event_10', '행사 보상 10회', '행사 보상을 10번 받았어요', '🎈', 'event', 10, 'pink', 323, false),
  ('shield_1', '방어권 1개 구매', '연속 학습 방어권을 1개 샀어요', '🛡️', 'shield', 1, 'blue', 324, false),
  ('shield_3', '방어권 3개 구매', '연속 학습 방어권을 3개 샀어요', '🛡️', 'shield', 3, 'green', 325, false),
  ('shield_5', '방어권 5개 구매', '연속 학습 방어권을 5개 샀어요', '🏯', 'shield', 5, 'red', 326, false),
  ('shield_10', '방어권 10개 구매', '연속 학습 방어권을 10개 샀어요', '🏯', 'shield', 10, 'pink', 327, false),
  ('post_1', '글 1개 작성', '게시판에 글을 1개 썼어요', '✏️', 'posts', 1, 'blue', 328, false),
  ('post_5', '글 5개 작성', '게시판에 글을 5개 썼어요', '✏️', 'posts', 5, 'teal', 329, false),
  ('post_10', '글 10개 작성', '게시판에 글을 10개 썼어요', '📄', 'posts', 10, 'green', 330, false),
  ('post_20', '글 20개 작성', '게시판에 글을 20개 썼어요', '📰', 'posts', 20, 'red', 331, false),
  ('post_50', '글 50개 작성', '게시판에 글을 50개 썼어요', '📰', 'posts', 50, 'purple', 332, false),
  ('post_100', '글 100개 작성', '게시판에 글을 100개 썼어요', '🖋️', 'posts', 100, 'pink', 333, false),
  ('cmt_1', '댓글 1개 작성', '댓글을 1개 남겼어요', '💬', 'comments', 1, 'blue', 334, false),
  ('cmt_10', '댓글 10개 작성', '댓글을 10개 남겼어요', '💬', 'comments', 10, 'teal', 335, false),
  ('cmt_30', '댓글 30개 작성', '댓글을 30개 남겼어요', '🗨️', 'comments', 30, 'green', 336, false),
  ('cmt_50', '댓글 50개 작성', '댓글을 50개 남겼어요', '🤝', 'comments', 50, 'red', 337, false),
  ('cmt_100', '댓글 100개 작성', '댓글을 100개 남겼어요', '🤝', 'comments', 100, 'purple', 338, false),
  ('cmt_300', '댓글 300개 작성', '댓글을 300개 남겼어요', '🫶', 'comments', 300, 'pink', 339, false),
  ('m_mvp', '이달의 MVP', '선생님이 뽑은 이달의 학생이에요', '🌟', 'manual', 0, 'gold', 340, false),
  ('m_helper', '친절한 도우미', '친구를 잘 도와줬어요', '🤝', 'manual', 0, 'green', 341, false),
  ('m_diligent', '성실상', '꾸준히 열심히 했어요', '📈', 'manual', 0, 'teal', 342, false),
  ('m_creative', '창의상', '아이디어가 반짝였어요', '💡', 'manual', 0, 'orange', 343, false),
  ('m_beta', '베타 테스터', 'PyNest 개선에 도움을 줬어요', '🧪', 'manual', 0, 'purple', 344, false),
  ('m_perfect', '개근상', '한 번도 빠지지 않았어요', '🎖️', 'manual', 0, 'red', 345, false),
  ('m_bug', '버그 사냥꾼', '버그를 찾아서 알려줬어요', '🐛', 'manual', 0, 'pink', 346, false),
  ('m_star', '우수 과제상', '과제를 아주 잘 냈어요', '🥳', 'manual', 0, 'blue', 347, false)
on conflict (id) do nothing;

-- 3) 배지 확인 (새 종류 포함)
create or replace function public.badges_check() returns jsonb
language plpgsql security definer set search_path = public
as $$
declare
  v_me uuid := auth.uid();
  v_score int := 0; v_solved int := 0; v_best int := 0; v_learn int := 0; v_first int := 0; v_join int := 0; v_py int := 0;
  v_tier int := 0; v_wins int := 0; v_items int := 0; v_sales int := 0; v_made int := 0; v_att int := 0; v_ev int := 0; v_sh int := 0;
  v_posts int := 0; v_cmts int := 0;
  b record; v_new jsonb := '[]'::jsonb; v_val int;
begin
  if v_me is null or not public.py_is_student(v_me) then return '[]'::jsonb; end if;
  select coalesce(pts, 0), coalesce(solved, 0) into v_score, v_solved from public.rk_scores(null) where uid = v_me;
  v_score := coalesce(v_score, 0); v_solved := coalesce(v_solved, 0);
  v_best := coalesce((public.streak_info() ->> 'best')::int, 0);
  v_tier := public.tier_major(v_score);
  if to_regclass('public.learn_progress') is not null then
    execute 'select count(*) from public.learn_progress where user_id = $1 and completed' into v_learn using v_me;
  end if;
  if to_regclass('public.exam_results') is not null then
    execute 'select count(*) from public.exam_results where user_id = $1' into v_join using v_me;
    execute 'select count(*) from public.exam_results where user_id = $1 and final_rank = 1' into v_first using v_me;
  end if;
  select coalesce(sum(delta), 0) into v_py from public.py_ledger where user_id = v_me and delta > 0;
  select count(*) into v_wins from public.rank_wins where user_id = v_me;
  select count(*) into v_items from public.avatar_inventory where user_id = v_me;
  select count(*) into v_sales from public.py_ledger where user_id = v_me and reason = 'market_sale';
  select count(*) into v_made from public.avatar_items where created_by = v_me and market and status = 'active';
  select count(*) into v_att from public.attendance where user_id = v_me and kind = 'learn';
  select count(*) into v_ev from public.py_ledger where user_id = v_me and reason = 'event_claim';
  select count(*) into v_sh from public.py_ledger where user_id = v_me and reason = 'shield';
  select count(*) into v_posts from public.posts where author_id = v_me and board <> 'notice' and auto_key is null;
  select count(*) into v_cmts from public.comments where author_id = v_me;
  for b in select * from public.badge_defs where kind <> 'manual' and threshold > 0 order by position loop
    v_val := case b.kind when 'score' then v_score when 'solved' then v_solved when 'streak' then v_best when 'learn' then v_learn
                         when 'exam_join' then v_join when 'exam_first' then v_first when 'pypoint' then v_py
                         when 'tier' then v_tier when 'rank1' then v_wins when 'items' then v_items when 'sales' then v_sales
                         when 'market_made' then v_made when 'attend' then v_att when 'event' then v_ev when 'shield' then v_sh
                         when 'posts' then v_posts when 'comments' then v_cmts else 0 end;
    if v_val >= b.threshold then
      insert into public.user_badges (user_id, badge_id) values (v_me, b.id) on conflict do nothing;
      if found then
        v_new := v_new || jsonb_build_object('id', b.id, 'name', b.name, 'icon', b.icon);
        perform public.py_notify(v_me, '🎖️ 새 배지: ' || b.name, b.descr, 'badge', '#/me/badges');
      end if;
    end if;
  end loop;
  return v_new;
end $$;
revoke all on function public.badges_check() from public, anon;
grant execute on function public.badges_check() to authenticated;
