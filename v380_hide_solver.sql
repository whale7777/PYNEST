-- =====================================================================
--  V3.8.0 — SOLVER 등급 학생은 랭킹·티어·프로필이 "본인과 직원에게만" 보여요
--  * 기존 표·데이터는 그대로예요. 함수만 다시 만들고 여러 번 실행해도 안전해요.
--  * 랭킹(주간/월간) · 이름 옆 티어 배지 · 남이 보는 프로필 · 카톡 봇 랭킹에서 빠져요.
--  * 본인은 자기 랭킹·티어·프로필을 그대로 봐요. 직원(OWNER/ADMIN/TEACHER/MOD)은 전부 봐요.
--  * 등급이 STUDENT/LISTENER 로 바뀌면 바로 다시 보여요.
--  * student_tiers.sql, v310_ranking.sql, v320b_live_points.sql, v340_kakao.sql 이 먼저 실행된 상태여야 해요.
-- =====================================================================

do $$
begin
  if to_regclass('public.student_tiers') is null or to_regprocedure('public.rk_scores(timestamptz)') is null
     or to_regclass('public.rk_live_solved') is null or to_regprocedure('public.bot_rank(text,text)') is null then
    raise exception 'student_tiers.sql / v310 / v320b / v340 을 먼저 실행해주세요.';
  end if;
end $$;

-- 1) 점수 계산: "누가 보느냐" 를 받는 버전 (SOLVER 는 본인·직원에게만 보여요)
create or replace function public.rk_scores_for(p_from timestamptz, p_viewer uuid, p_see_all boolean)
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
     and (coalesce(p_see_all, false) or r.user_id is not distinct from p_viewer
          or not exists (select 1 from public.student_tiers st where st.user_id = p.id and st.tier = 'solver'))
   group by r.user_id
$$;
revoke all on function public.rk_scores_for(timestamptz, uuid, boolean) from public, anon, authenticated;

-- 2) 기존 rk_scores 는 "지금 로그인한 사람" 기준으로 (랭킹·프로필·홈이 그대로 이걸 써요)
create or replace function public.rk_scores(p_from timestamptz default null)
returns table (uid uuid, solved int, pts int)
language sql stable security definer set search_path = public
as $$
  select * from public.rk_scores_for(p_from, auth.uid(), public.staff_role() is not null)
$$;
revoke all on function public.rk_scores(timestamptz) from public, anon, authenticated;

-- 3) 이름표: 남의 SOLVER 는 score = -1 (앱이 티어 배지·프로필 링크를 숨겨요)
create or replace function public.student_directory()
returns table (user_id uuid, name text, nick text, uname text, score int, solved int)
language sql stable security definer set search_path = public
as $$
  select p.id, public.disp(p.id), n.nickname,
         case when public.staff_role() is not null then p.username end,
         case when public.staff_role() is null and p.id is distinct from auth.uid()
                   and exists (select 1 from public.student_tiers st where st.user_id = p.id and st.tier = 'solver')
              then -1 else coalesce(t.pts, 0) end,
         coalesce(t.solved, 0)
    from public.profiles p
    left join public.nicknames n on n.user_id = p.id
    left join public.rk_scores(null) t on t.uid = p.id
   where public.is_approved() and p.status = 'approved' and p.role <> 'admin'
     and not exists (select 1 from public.staff_roles sr where sr.user_id = p.id)
$$;
revoke all on function public.student_directory() from public, anon;
grant execute on function public.student_directory() to authenticated;

-- 4) 프로필: 남의 SOLVER 프로필은 "없는 사람" 처럼 (본인·직원은 정상)
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
  -- SOLVER 등급 학생은 본인과 직원만 프로필을 볼 수 있어요
  if p_uid is distinct from auth.uid() and public.staff_role() is null
     and exists (select 1 from public.student_tiers st where st.user_id = p_uid and st.tier = 'solver') then
    return null;
  end if;
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

-- 5) 카카오 봇: 랭킹 TOP 10 에서 SOLVER 는 빠지고, 본인이 물으면 본인 순위는 나와요
create or replace function public.bot_rank(p_period text, p_kakao text default null)
returns jsonb
language plpgsql stable security definer set search_path = public
as $$
declare v_from timestamptz; v_me uuid; v_top jsonb; v_mine jsonb; v_cnt int;
begin
  if p_period not in ('week', 'month', 'all') then return null; end if;
  v_from := case when p_period = 'all' then null else public.rk_period_start(p_period) end;
  select user_id into v_me from public.kakao_links where kakao_id = p_kakao;

  with r as (
    select s.uid, s.solved, s.pts, (rank() over (order by s.pts desc))::int as rnk
      from public.rk_scores_for(v_from, v_me, false) s where s.pts > 0
  )
  select (select count(*) from r),
         (select coalesce(jsonb_agg(jsonb_build_object('name', coalesce(n.nickname, p.username), 'solved', r.solved, 'pts', r.pts, 'rnk', r.rnk)
                          order by r.pts desc, r.solved desc, coalesce(n.nickname, p.username)), '[]'::jsonb)
            from (select * from r order by pts desc, solved desc limit 10) r
            join public.profiles p on p.id = r.uid left join public.nicknames n on n.user_id = r.uid),
         (select jsonb_build_object('pts', r.pts, 'solved', r.solved, 'rnk', r.rnk) from r where r.uid = v_me)
    into v_cnt, v_top, v_mine;

  return jsonb_build_object('period', p_period, 'count', v_cnt, 'top', v_top, 'me', v_mine, 'linked', v_me is not null);
end;
$$;

create or replace function public.bot_me(p_kakao text)
returns jsonb
language plpgsql stable security definer set search_path = public
as $$
declare
  v_uid uuid; v_p public.profiles; v_staff text; v_nick text;
  v_tot record; v_w record; v_m record; v_rw int; v_rm int; v_by jsonb;
  v_ws timestamptz := public.rk_period_start('week');
  v_ms timestamptz := public.rk_period_start('month');
begin
  select user_id into v_uid from public.kakao_links where kakao_id = p_kakao;
  if v_uid is null then return null; end if;
  select * into v_p from public.profiles where id = v_uid and status = 'approved';
  if not found then return null; end if;
  select nickname into v_nick from public.nicknames where user_id = v_uid;
  v_staff := case when v_p.role = 'admin' then 'owner' else (select sr.role from public.staff_roles sr where sr.user_id = v_uid) end;
  if v_staff is not null then
    return jsonb_build_object('name', coalesce(v_nick, v_p.username), 'staff', v_staff);
  end if;

  select * into v_tot from public.rk_scores_for(null, v_uid, false) where uid = v_uid;
  select * into v_w from public.rk_scores_for(v_ws, v_uid, false) where uid = v_uid;
  select * into v_m from public.rk_scores_for(v_ms, v_uid, false) where uid = v_uid;
  select 1 + count(*) into v_rw from public.rk_scores_for(v_ws, v_uid, false) x where x.pts > coalesce(v_w.pts, 0);
  select 1 + count(*) into v_rm from public.rk_scores_for(v_ms, v_uid, false) x where x.pts > coalesce(v_m.pts, 0);
  select coalesce(jsonb_agg(jsonb_build_object('difficulty', t.difficulty, 'n', t.n) order by t.n desc), '[]'::jsonb)
    into v_by from (select r.difficulty, count(*)::int as n from public.rk_solved r where r.user_id = v_uid group by r.difficulty) t;

  return jsonb_build_object(
    'name', coalesce(v_nick, v_p.username),
    'score', coalesce(v_tot.pts, 0), 'solved', coalesce(v_tot.solved, 0),
    'week', jsonb_build_object('solved', coalesce(v_w.solved, 0), 'pts', coalesce(v_w.pts, 0), 'rank', case when coalesce(v_w.pts, 0) > 0 then v_rw end),
    'month', jsonb_build_object('solved', coalesce(v_m.solved, 0), 'pts', coalesce(v_m.pts, 0), 'rank', case when coalesce(v_m.pts, 0) > 0 then v_rm end),
    'by_diff', v_by);
end;
$$;

revoke all on function public.bot_rank(text, text), public.bot_me(text) from public, anon, authenticated;
grant execute on function public.bot_rank(text, text), public.bot_me(text) to service_role;
