-- =====================================================================
--  PyNest V4.2.0 — 학습(📚)을 끝내면 랭킹·티어 점수가 올라요
--  * 코스마다 "레슨 1개를 끝낼 때 받는 랭킹 점수" 를 정해요 (0 = 점수 없음, 기본값). 레슨마다 따로 정할 수도 있어요.
--  * 기존 표·데이터는 그대로예요. 컬럼 2개 + 뷰 1개 + 함수 갱신만 해요. 여러 번 실행해도 안전해요.
--  * 먼저 v410_learn.sql 이 실행돼 있어야 해요. v380(SOLVER 숨김)·v390(승급 배너)을 이미 실행했다면 그 함수도 같이 갱신하고,
--    아직이면 예전 점수 함수(rk_scores)를 갱신해요. (나중에 v380/v390 을 실행하면 학습 점수가 빠지니, 순서를 바꾸면 이 파일을 한 번 더 실행하세요.)
--  * 학습 점수는 "푼 문제 수" 에는 안 세고 점수에만 더해져요.
-- =====================================================================

do $$
begin
  if to_regclass('public.learn_progress') is null or to_regprocedure('public.rk_scores(timestamptz)') is null
     or to_regclass('public.rk_live_solved') is null then
    raise exception 'v410_learn.sql (그리고 v310, v320b) 을 먼저 실행해주세요.';
  end if;
end $$;

-- 1) 점수 설정 칸
alter table public.learn_courses add column if not exists rank_points int not null default 0;
alter table public.learn_lessons add column if not exists rank_points int;
do $$
begin
  if not exists (select 1 from pg_constraint where conname = 'learn_courses_rank_points_check') then
    alter table public.learn_courses add constraint learn_courses_rank_points_check check (rank_points >= 0 and rank_points <= 100000);
  end if;
  if not exists (select 1 from pg_constraint where conname = 'learn_lessons_rank_points_check') then
    alter table public.learn_lessons add constraint learn_lessons_rank_points_check check (rank_points is null or (rank_points >= 0 and rank_points <= 100000));
  end if;
end $$;

-- 2) 학습으로 "처음 끝낸" 기록 (점수가 1점 이상인 레슨만). 레슨 점수 → 없으면 코스 점수
create or replace view public.rk_learn_solved as
 select p.user_id, p.lesson_id, l.course_id, p.completed_at as solved_at,
        coalesce(l.rank_points, c.rank_points, 0) as pts
   from public.learn_progress p
   join public.learn_lessons l on l.id = p.lesson_id
   join public.learn_courses c on c.id = l.course_id
  where p.completed and p.completed_at is not null
    and coalesce(l.rank_points, c.rank_points, 0) > 0;
revoke all on public.rk_learn_solved from public, anon, authenticated;

-- 3) 진도 보호: 끝냄(completed)은 "모든 단계를 끝냈을 때만", 시각은 서버 시각, 한 번 끝낸 건 되돌리지 않아요
create or replace function public.learn_progress_guard()
returns trigger language plpgsql security definer set search_path = public as $$
declare
  v_n int;
  v_ok int;
begin
  if tg_op = 'UPDATE' and old.completed then
    new.completed := true;
    new.completed_at := old.completed_at;
    return new;
  end if;
  if new.completed then
    select jsonb_array_length(steps) into v_n from public.learn_lessons where id = new.lesson_id;
    select count(*)::int into v_ok from jsonb_object_keys(coalesce(new.done, '{}'::jsonb)) k
     where k ~ '^[0-9]+$' and k::int < coalesce(v_n, 0);
    if coalesce(v_n, 0) = 0 or v_ok < v_n then
      new.completed := false;
      new.completed_at := null;
    else
      new.completed_at := now();
    end if;
  else
    new.completed_at := null;
  end if;
  return new;
end $$;
drop trigger if exists trg_learn_progress_guard on public.learn_progress;
create trigger trg_learn_progress_guard before insert or update on public.learn_progress
  for each row execute function public.learn_progress_guard();

-- 4) 점수 합산에 학습 점수 더하기
do $$
begin
  if to_regprocedure('public.rk_scores_for(timestamptz,uuid,boolean)') is not null then
    -- v380 이후: SOLVER 숨김 규칙을 그대로 두고 학습 점수만 더해요
    execute $fn$
      create or replace function public.rk_scores_for(p_from timestamptz, p_viewer uuid, p_see_all boolean)
      returns table (uid uuid, solved int, pts int)
      language sql stable security definer set search_path = public
      as $body$
        select r.user_id, (count(*) filter (where r.kind <> 'l'))::int, coalesce(sum(r.pts), 0)::int
          from (select user_id, pts, solved_at, 'p'::text as kind from public.rk_solved
                union all
                select user_id, pts, solved_at, 'p' from public.rk_live_solved
                union all
                select user_id, pts, solved_at, 'l' from public.rk_learn_solved) r
          join public.profiles p on p.id = r.user_id and p.status = 'approved' and p.role <> 'admin'
         where (p_from is null or r.solved_at >= p_from)
           and not exists (select 1 from public.staff_roles sr where sr.user_id = p.id)
           and (coalesce(p_see_all, false) or r.user_id is not distinct from p_viewer
                or not exists (select 1 from public.student_tiers st where st.user_id = p.id and st.tier = 'solver'))
         group by r.user_id
      $body$
    $fn$;
    revoke all on function public.rk_scores_for(timestamptz, uuid, boolean) from public, anon, authenticated;
  else
    -- v380 전: 예전 점수 함수에 학습 점수를 더해요
    execute $fn$
      create or replace function public.rk_scores(p_from timestamptz default null)
      returns table (uid uuid, solved int, pts int)
      language sql stable security definer set search_path = public
      as $body$
        select r.user_id, (count(*) filter (where r.kind <> 'l'))::int, coalesce(sum(r.pts), 0)::int
          from (select user_id, pts, solved_at, 'p'::text as kind from public.rk_solved
                union all
                select user_id, pts, solved_at, 'p' from public.rk_live_solved
                union all
                select user_id, pts, solved_at, 'l' from public.rk_learn_solved) r
          join public.profiles p on p.id = r.user_id and p.status = 'approved' and p.role <> 'admin'
         where (p_from is null or r.solved_at >= p_from)
           and not exists (select 1 from public.staff_roles sr where sr.user_id = p.id)
         group by r.user_id
      $body$
    $fn$;
    revoke all on function public.rk_scores(timestamptz) from public, anon, authenticated;
  end if;
end $$;

-- 5) 티어 승급 배너(v390)에도 학습 점수 반영
do $$
begin
  if to_regprocedure('public.tier_promos(date)') is not null then
    execute $fn$
      create or replace function public.tier_promos(p_day date)
      returns table (uid uuid, name text, from_idx int, to_idx int, from_tier text, to_tier text)
      language sql stable security definer set search_path = public
      as $body$
        with t as (select (p_day::timestamp at time zone 'Asia/Seoul') as t0),
        ev as (
          select user_id, pts, solved_at from public.rk_solved
          union all
          select user_id, pts, solved_at from public.rk_live_solved
          union all
          select user_id, pts, solved_at from public.rk_learn_solved
        ),
        sc as (
          select e.user_id,
                 coalesce(sum(e.pts) filter (where e.solved_at < t.t0), 0)::int as b,
                 coalesce(sum(e.pts) filter (where e.solved_at < t.t0 + interval '1 day'), 0)::int as a
            from ev e cross join t group by e.user_id
        )
        select x.user_id, coalesce(n.nickname, p.username),
               public.tier_major(x.b), public.tier_major(x.a),
               public.tier_name_of(public.tier_major(x.b)), public.tier_name_of(public.tier_major(x.a))
          from sc x
          join public.profiles p on p.id = x.user_id and p.status = 'approved' and p.role <> 'admin'
          left join public.nicknames n on n.user_id = x.user_id
         where public.tier_major(x.a) > public.tier_major(x.b)
           and not exists (select 1 from public.staff_roles sr where sr.user_id = p.id)
           and not exists (select 1 from public.student_tiers st where st.user_id = p.id and st.tier = 'solver')
      $body$
    $fn$;
    revoke all on function public.tier_promos(date) from public, anon, authenticated;
  end if;
end $$;
