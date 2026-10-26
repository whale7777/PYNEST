-- =====================================================================
--  PyNest V3.2.0 (2) — 라이브에서 만든 문제도 점수가 올라가요
--  * 기존 표·데이터는 지우지 않고 컬럼/뷰를 "추가"하고 함수를 "교체"만 해요. 여러 번 실행해도 안전해요.
--  * v310_ranking.sql 이 먼저 적용돼 있어야 해요. (v320_tiers.sql 은 있어도 없어도 돼요)
--
--  라이브 문제 점수 = 문제에 직접 정한 "랭킹 점수" → 없으면 "난이도 점수" → 둘 다 없으면 0점
--  (그래서 이미 만들어 둔 라이브 문제는 점수가 없는 채로 그대로예요. 점수를 주고 싶으면 문제 수정에서 난이도를 고르세요.)
--  학생이 라이브 문제를 처음 맞춘(AC) 순간에 점수가 들어가요. 같은 문제는 한 번만, 직원은 제외예요.
-- =====================================================================

do $$
begin
  if to_regclass('public.difficulties') is null or to_regprocedure('public.rk_scores(timestamptz)') is null then
    raise exception 'v310_ranking.sql 을 먼저 실행해주세요.';
  end if;
  if to_regclass('public.live_problems') is null then
    raise exception '라이브 표(live_problems)가 없어요.';
  end if;
end $$;

-- 1) 라이브 문제에 난이도 / 랭킹 점수 (둘 다 선택)
alter table public.live_problems add column if not exists difficulty text;
alter table public.live_problems add column if not exists rank_points int;
do $$
begin
  if not exists (select 1 from pg_constraint where conname = 'live_problems_difficulty_fk') then
    alter table public.live_problems
      add constraint live_problems_difficulty_fk foreign key (difficulty) references public.difficulties(name)
      on update cascade on delete set null;
  end if;
  if not exists (select 1 from pg_constraint where conname = 'live_problems_rank_points_check') then
    alter table public.live_problems add constraint live_problems_rank_points_check check (rank_points is null or rank_points >= 0);
  end if;
end $$;

-- 2) 라이브에서 "처음 맞춘" 기록 (점수가 1점 이상인 문제만)
create or replace view public.rk_live_solved as
 select s.user_id, s.problem_id, min(s.created_at) as solved_at, p.session_id, p.difficulty,
        coalesce(p.rank_points, d.points, 0) as pts
   from public.live_submissions s
   join public.live_problems p on p.id = s.problem_id
   left join public.difficulties d on d.name = p.difficulty
  where s.ok
  group by s.user_id, s.problem_id, p.session_id, p.difficulty, p.rank_points, d.points
 having coalesce(p.rank_points, d.points, 0) > 0;
revoke all on public.rk_live_solved from public, anon, authenticated;

-- 3) 점수 합산: 일반 문제 + 라이브 문제 (랭킹·티어·뱃지·프로필이 모두 이 함수를 써요)
create or replace function public.rk_scores(p_from timestamptz default null)
returns table (uid uuid, solved int, pts int)
language sql stable security definer set search_path = public
as $$
  select r.user_id, count(*)::int, coalesce(sum(r.pts), 0)::int
    from (select user_id, pts, solved_at from public.rk_solved
          union all
          select user_id, pts, solved_at from public.rk_live_solved) r
    join public.profiles p on p.id = r.user_id and p.status = 'approved' and p.role <> 'admin'
   where (p_from is null or r.solved_at >= p_from)
     and not exists (select 1 from public.staff_roles sr where sr.user_id = p.id)
   group by r.user_id
$$;
revoke all on function public.rk_scores(timestamptz) from public, anon, authenticated;

-- 4) 프로필: 난이도별 개수 · 최근 푼 문제에 라이브 문제도 보여요
create or replace function public.user_profile(p_uid uuid)
returns jsonb
language plpgsql stable security definer set search_path = public
as $$
declare
  v_p public.profiles;
  v_staff text;
  v_tot record;
  v_w record;
  v_m record;
  v_ws timestamptz := public.rk_period_start('week');
  v_ms timestamptz := public.rk_period_start('month');
  v_rw int;
  v_rm int;
  v_by jsonb;
  v_recent jsonb;
begin
  if not public.is_approved() then return null; end if;
  select * into v_p from public.profiles where id = p_uid and status = 'approved';
  if not found then return null; end if;
  v_staff := case when v_p.role = 'admin' then 'owner'
                  else (select sr.role from public.staff_roles sr where sr.user_id = p_uid) end;
  if v_staff is not null then
    return jsonb_build_object('uid', p_uid, 'name', public.disp(p_uid), 'staff', v_staff,
      'uname', case when public.staff_role() is not null then v_p.username end);
  end if;

  select * into v_tot from public.rk_scores(null) where uid = p_uid;
  select * into v_w from public.rk_scores(v_ws) where uid = p_uid;
  select * into v_m from public.rk_scores(v_ms) where uid = p_uid;
  select 1 + count(*) into v_rw from public.rk_scores(v_ws) x where x.pts > coalesce(v_w.pts, 0);
  select 1 + count(*) into v_rm from public.rk_scores(v_ms) x where x.pts > coalesce(v_m.pts, 0);

  select coalesce(jsonb_agg(jsonb_build_object('difficulty', t.difficulty, 'n', t.n) order by t.n desc), '[]'::jsonb)
    into v_by
    from (select u.difficulty, count(*)::int as n
            from (select r.difficulty from public.rk_solved r where r.user_id = p_uid
                  union all
                  select l.difficulty from public.rk_live_solved l where l.user_id = p_uid and l.difficulty is not null) u
           group by u.difficulty) t;

  select coalesce(jsonb_agg(to_jsonb(x) order by x.at desc), '[]'::jsonb)
    into v_recent
    from (
      select * from (
        select r.exercise_id as id, r.difficulty, r.solved_at as at, r.set_id, r.pts,
               ps.title as set_title, ps.short_name as set_short,
               (select count(*) from public.exercises e2
                 where e2.set_id = r.set_id
                   and ((e2.difficulty = 'ELITE') = (r.difficulty = 'ELITE'))
                   and (e2."position", e2.id) <= (r."pos", r.exercise_id))::int as no,
               false as live
          from public.rk_solved r
          left join public.problem_sets ps on ps.id = r.set_id
         where r.user_id = p_uid
        union all
        select l.problem_id, l.difficulty, l.solved_at, null::bigint, l.pts,
               '라이브 · ' || coalesce(ls.title, ''), null::text, null::int, true
          from public.rk_live_solved l
          left join public.live_sessions ls on ls.id = l.session_id
         where l.user_id = p_uid
      ) z
       order by z.at desc
       limit 10
    ) x;

  return jsonb_build_object(
    'uid', p_uid,
    'name', public.disp(p_uid),
    'uname', case when public.staff_role() is not null then v_p.username end,
    'joined', v_p.created_at,
    'score', coalesce(v_tot.pts, 0),
    'solved', coalesce(v_tot.solved, 0),
    'week', jsonb_build_object('solved', coalesce(v_w.solved, 0), 'pts', coalesce(v_w.pts, 0), 'rank', case when coalesce(v_w.pts, 0) > 0 then v_rw end),
    'month', jsonb_build_object('solved', coalesce(v_m.solved, 0), 'pts', coalesce(v_m.pts, 0), 'rank', case when coalesce(v_m.pts, 0) > 0 then v_rm end),
    'by_diff', v_by,
    'recent', v_recent
  );
end;
$$;

revoke all on function public.user_profile(uuid) from public, anon;
grant execute on function public.user_profile(uuid) to authenticated;
