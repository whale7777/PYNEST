-- =====================================================================
--  PyNest V4.5.0 — 파이포인트(PYPOINT) · 출석/연속 학습 · 방어권 · 배지 · 관리자 점수 조정
--  * 기존 표·데이터는 지우지 않아요. 새 표/함수를 "추가"하고, 점수 합산 함수만 교체해요. 여러 번 실행해도 안전해요.
--  * 먼저 v310_ranking.sql 이 적용돼 있어야 하고, v380/v390/v410/v420/v440 도 이미 돌렸다면 그대로 이어져요.
--
--  [파이포인트] 랭킹 점수와 별개의 재화예요.
--    얻는 곳: 주간·월간 랭킹 1~3위(동점이면 자리 몫을 나눠 가져요) · 문제 처음 맞출 때 랜덤 · 학습 레슨 끝낼 때 랜덤 · 관리자 지급
--    쓰는 곳: 연속 학습 방어권(최대 2개) · (V4.6.0) 캐릭터 아이템 구매 · 마켓
--  [출석] 문제를 제출하거나 학습을 하면 그날(한국 시간) 출석. 하루를 놓쳐도 방어권이 있으면 자동으로 써서 이어가요.
--  [배지] 점수·푼 문제 수·연속 학습·학습 레슨 수 … 달성하면 자동으로 받아요. 관리자가 새 배지를 만들거나 직접 줄 수도 있어요.
--  [점수 조정] 관리자가 학생에게 랭킹 점수를 더하거나 빼요. (기록이 남고, 랭킹·티어에 바로 반영돼요)
-- =====================================================================

do $$
begin
  if to_regprocedure('public.rk_scores(timestamptz)') is null or to_regclass('public.notifications') is null then
    raise exception 'v310_ranking.sql 과 v440_social.sql 을 먼저 실행해주세요.';
  end if;
end $$;

-- 0) 알림 종류 늘리기
alter table public.notifications drop constraint if exists notifications_kind_check;
alter table public.notifications add constraint notifications_kind_check
  check (kind in ('dm', 'tier', 'notice', 'badge', 'reward', 'exam', 'event', 'item'));

-- 1) 설정값 (관리자가 고칠 수 있어요)
create table if not exists public.py_config (
  key text primary key,
  val jsonb not null,
  updated_at timestamptz not null default now()
);
insert into public.py_config (key, val) values
  ('week_rank',   '[30,20,10]'),     -- 주간 랭킹 1·2·3위 보상
  ('month_rank',  '[100,60,30]'),    -- 월간 랭킹 1·2·3위 보상
  ('solve_rand',  '[2,6]'),          -- 문제 처음 맞출 때 랜덤(최소, 최대)
  ('learn_rand',  '[3,8]'),          -- 학습 레슨 끝낼 때 랜덤
  ('shield_price','60'),             -- 방어권 가격
  ('shield_max',  '2')               -- 방어권 최대 소지 수
on conflict (key) do nothing;
alter table public.py_config enable row level security;
revoke all on public.py_config from anon, authenticated;
grant select on public.py_config to authenticated;
drop policy if exists py_config_read on public.py_config;
create policy py_config_read on public.py_config for select to authenticated using (public.is_approved());

create or replace function public.py_cfg(p_key text, p_def jsonb default 'null')
returns jsonb language sql stable security definer set search_path = public
as $$ select coalesce((select val from public.py_config where key = p_key), p_def) $$;

-- 2) 지갑 · 원장
create table if not exists public.py_wallet (
  user_id uuid primary key references public.profiles(id) on delete cascade,
  balance int not null default 0 check (balance >= 0),
  shields int not null default 0 check (shields between 0 and 9),
  updated_at timestamptz not null default now()
);
create table if not exists public.py_ledger (
  id bigint generated always as identity primary key,
  user_id uuid not null references public.profiles(id) on delete cascade,
  delta int not null,
  reason text not null,
  ref text,
  note text not null default '',
  created_by uuid,
  created_at timestamptz not null default now()
);
create index if not exists py_ledger_user_idx on public.py_ledger (user_id, id desc);
-- 같은 이유·같은 대상으로 두 번 받지 못하게
create unique index if not exists py_ledger_once on public.py_ledger (user_id, reason, ref)
  where ref is not null and reason in ('solve', 'learn', 'rank_week', 'rank_month', 'exam_rank', 'item_reward', 'event_claim');
alter table public.py_wallet enable row level security;
alter table public.py_ledger enable row level security;
revoke all on public.py_wallet, public.py_ledger from anon, authenticated;
grant select on public.py_wallet, public.py_ledger to authenticated;
drop policy if exists py_wallet_own on public.py_wallet;
create policy py_wallet_own on public.py_wallet for select to authenticated using (user_id = auth.uid() or public.staff_role() in ('owner', 'admin'));
drop policy if exists py_ledger_own on public.py_ledger;
create policy py_ledger_own on public.py_ledger for select to authenticated using (user_id = auth.uid() or public.staff_role() in ('owner', 'admin'));

-- 이벤트 배수 (V4.6.0 행사 기능이 이 함수를 새로 정의해요)
create or replace function public.py_event_mult() returns numeric
language sql stable security definer set search_path = public as $$ select 1::numeric $$;

-- 내부용: 파이포인트 더하기/빼기. 돌려주는 값: 적용됨(true) / 이미 받은 보상이라 건너뜀(false)
create or replace function public.py_add(p_uid uuid, p_delta int, p_reason text, p_ref text default null, p_note text default '', p_by uuid default null, p_floor boolean default false)
returns boolean
language plpgsql security definer set search_path = public
as $$
declare v_n int; v_bal int;
begin
  if p_delta = 0 then return false; end if;
  insert into public.py_wallet (user_id) values (p_uid) on conflict do nothing;
  select balance into v_bal from public.py_wallet where user_id = p_uid for update;
  if p_delta < 0 and v_bal + p_delta < 0 then
    if not p_floor then raise exception 'insufficient'; end if;
    p_delta := -v_bal;
    if p_delta = 0 then return false; end if;
  end if;
  insert into public.py_ledger (user_id, delta, reason, ref, note, created_by) values (p_uid, p_delta, p_reason, p_ref, coalesce(p_note, ''), p_by)
    on conflict do nothing;
  get diagnostics v_n = row_count;
  if v_n = 0 then return false; end if;
  update public.py_wallet set balance = balance + p_delta, updated_at = now() where user_id = p_uid;
  return true;
end $$;
revoke all on function public.py_add(uuid, int, text, text, text, uuid, boolean) from public, anon, authenticated;

create or replace function public.py_is_student(p_uid uuid) returns boolean
language sql stable security definer set search_path = public
as $$ select exists (select 1 from public.profiles p where p.id = p_uid and p.status = 'approved' and p.role <> 'admin')
        and not exists (select 1 from public.staff_roles sr where sr.user_id = p_uid) $$;

create or replace function public.py_is_solver(p_uid uuid) returns boolean
language plpgsql stable security definer set search_path = public
as $$
begin
  if to_regclass('public.student_tiers') is null then return false; end if;
  return exists (select 1 from public.student_tiers st where st.user_id = p_uid and st.tier = 'solver');
end $$;

create or replace function public.py_rand(p_key text, p_lo int, p_hi int) returns int
language plpgsql stable security definer set search_path = public
as $$
declare v jsonb := public.py_cfg(p_key, jsonb_build_array(p_lo, p_hi)); lo int; hi int;
begin
  lo := coalesce((v ->> 0)::int, p_lo); hi := coalesce((v ->> 1)::int, p_hi);
  if hi < lo then hi := lo; end if;
  return greatest(0, round((lo + floor(random() * (hi - lo + 1))) * public.py_event_mult())::int);
end $$;

create or replace function public.py_notify(p_uid uuid, p_title text, p_body text, p_kind text default 'reward', p_link text default '')
returns void language sql security definer set search_path = public
as $$ insert into public.notifications (user_id, kind, title, body, link) values (p_uid, p_kind, left(p_title, 80), left(coalesce(p_body, ''), 300), left(p_link, 120)) $$;
revoke all on function public.py_notify(uuid, text, text, text, text), public.py_rand(text, int, int), public.py_is_solver(uuid), public.py_is_student(uuid), public.py_cfg(text, jsonb) from public, anon, authenticated;

-- 3) 출석 · 연속 학습
create table if not exists public.attendance (
  user_id uuid not null references public.profiles(id) on delete cascade,
  day date not null,
  kind text not null default 'learn' check (kind in ('learn', 'shield')),
  created_at timestamptz not null default now(),
  primary key (user_id, day)
);
alter table public.attendance enable row level security;
revoke all on public.attendance from anon, authenticated;
grant select on public.attendance to authenticated;
drop policy if exists attendance_own on public.attendance;
create policy attendance_own on public.attendance for select to authenticated using (user_id = auth.uid() or public.staff_role() in ('owner', 'admin'));

create or replace function public.att_mark(p_uid uuid) returns void
language plpgsql security definer set search_path = public
as $$
declare
  v_today date := (now() at time zone 'Asia/Seoul')::date;
  v_prev date; v_gap int; v_sh int; v_i int;
begin
  if not public.py_is_student(p_uid) then return; end if;
  if exists (select 1 from public.attendance where user_id = p_uid and day = v_today) then return; end if;
  select max(day) into v_prev from public.attendance where user_id = p_uid and day < v_today;
  if v_prev is not null then
    v_gap := v_today - v_prev - 1;                         -- 놓친 날 수
    if v_gap > 0 then
      select coalesce(shields, 0) into v_sh from public.py_wallet where user_id = p_uid;
      v_sh := coalesce(v_sh, 0);
      if v_gap <= v_sh then                                -- 방어권으로 이어붙여요
        for v_i in 1..v_gap loop
          insert into public.attendance (user_id, day, kind) values (p_uid, v_prev + v_i, 'shield') on conflict do nothing;
        end loop;
        update public.py_wallet set shields = shields - v_gap, updated_at = now() where user_id = p_uid;
        perform public.py_notify(p_uid, '🛡️ 방어권을 써서 연속 학습을 지켰어요!', v_gap || '일을 놓쳤지만 방어권 ' || v_gap || '개로 이어졌어요.', 'reward', '#/me/streak');
      end if;
    end if;
  end if;
  insert into public.attendance (user_id, day, kind) values (p_uid, v_today, 'learn') on conflict do nothing;
end $$;
revoke all on function public.att_mark(uuid) from public, anon, authenticated;

-- 연속 학습 정보 (본인)
create or replace function public.streak_info()
returns jsonb
language plpgsql stable security definer set search_path = public
as $$
declare
  v_me uuid := auth.uid();
  v_today date := (now() at time zone 'Asia/Seoul')::date;
  v_last date; v_streak int := 0; v_best int := 0; v_run int := 0; v_gap int; v_sh int := 0;
  r record; v_prev date;
begin
  if v_me is null then return null; end if;
  select coalesce(shields, 0) into v_sh from public.py_wallet where user_id = v_me;
  v_sh := coalesce(v_sh, 0);
  select max(day) into v_last from public.attendance where user_id = v_me;
  -- 최고 기록
  for r in select day from public.attendance where user_id = v_me order by day loop
    if v_prev is not null and r.day = v_prev + 1 then v_run := v_run + 1; else v_run := 1; end if;
    if v_run > v_best then v_best := v_run; end if;
    v_prev := r.day;
  end loop;
  if v_last is not null then
    v_gap := v_today - v_last - 1;
    if v_last = v_today or v_gap <= 0 or v_gap <= v_sh then
      v_streak := 0; v_prev := null;
      for r in select day from public.attendance where user_id = v_me order by day desc loop
        if v_prev is null or r.day = v_prev - 1 then v_streak := v_streak + 1; v_prev := r.day; else exit; end if;
      end loop;
    end if;
  end if;
  return jsonb_build_object(
    'streak', v_streak, 'best', v_best, 'today', coalesce(v_last = v_today, false), 'shields', v_sh,
    'rescue', case when v_last is not null and v_last < v_today and v_gap > 0 and v_gap <= v_sh then v_gap else 0 end,
    'broken', v_last is not null and v_last < v_today and v_streak = 0,
    'days', (select coalesce(jsonb_agg(jsonb_build_object('d', a.day, 'k', a.kind) order by a.day), '[]'::jsonb)
               from public.attendance a where a.user_id = v_me and a.day > v_today - 60));
end $$;

-- 출석 트리거: 제출 / 학습 XP
create or replace function public.trg_att_submission() returns trigger
language plpgsql security definer set search_path = public
as $$ begin perform public.att_mark(new.user_id); return null; end $$;
drop trigger if exists trg_att_submission on public.submissions;
create trigger trg_att_submission after insert on public.submissions for each row execute function public.trg_att_submission();

do $$
begin
  if to_regclass('public.learn_days') is not null then
    execute $f$
      create or replace function public.trg_att_learn() returns trigger
      language plpgsql security definer set search_path = public
      as $b$ begin if coalesce(new.xp, 0) > 0 then perform public.att_mark(new.user_id); end if; return null; end $b$
    $f$;
    drop trigger if exists trg_att_learn on public.learn_days;
    create trigger trg_att_learn after insert or update on public.learn_days for each row execute function public.trg_att_learn();
  end if;
end $$;

-- 방어권 사기
create or replace function public.py_buy_shield() returns text
language plpgsql security definer set search_path = public
as $$
declare
  v_me uuid := auth.uid();
  v_price int := coalesce((public.py_cfg('shield_price', '60'))::text::int, 60);
  v_max int := coalesce((public.py_cfg('shield_max', '2'))::text::int, 2);
  v_sh int;
begin
  if v_me is null or not public.py_is_student(v_me) then return 'nouser'; end if;
  insert into public.py_wallet (user_id) values (v_me) on conflict do nothing;
  select shields into v_sh from public.py_wallet where user_id = v_me for update;
  if v_sh >= v_max then return 'full'; end if;
  begin
    perform public.py_add(v_me, -v_price, 'shield', null, '연속 학습 방어권');
  exception when others then return 'poor';
  end;
  update public.py_wallet set shields = shields + 1, updated_at = now() where user_id = v_me;
  return 'ok';
end $$;

-- 4) 점수 조정 (관리자) + 모든 점수 출처를 하나로 모은 보기
create table if not exists public.rank_adjust (
  id bigint generated always as identity primary key,
  user_id uuid not null references public.profiles(id) on delete cascade,
  delta int not null check (delta <> 0 and abs(delta) <= 10000000),
  note text not null default '',
  created_by uuid,
  created_at timestamptz not null default now()
);
create index if not exists rank_adjust_user_idx on public.rank_adjust (user_id, id desc);
alter table public.rank_adjust enable row level security;
revoke all on public.rank_adjust from anon, authenticated;
grant select on public.rank_adjust to authenticated;
drop policy if exists rank_adjust_read on public.rank_adjust;
create policy rank_adjust_read on public.rank_adjust for select to authenticated using (user_id = auth.uid() or public.staff_role() in ('owner', 'admin'));

do $$
begin
  if to_regclass('public.rk_learn_solved') is not null then
    execute $f$
      create or replace view public.rk_events as
        select user_id, pts, solved_at, 'p'::text as kind from public.rk_solved
        union all select user_id, pts, solved_at, 'p' from public.rk_live_solved
        union all select user_id, pts, solved_at, 'l' from public.rk_learn_solved
        union all select user_id, delta, created_at, 'a' from public.rank_adjust
    $f$;
  else
    execute $f$
      create or replace view public.rk_events as
        select user_id, pts, solved_at, 'p'::text as kind from public.rk_solved
        union all select user_id, pts, solved_at, 'p' from public.rk_live_solved
        union all select user_id, delta, created_at, 'a' from public.rank_adjust
    $f$;
  end if;
end $$;
revoke all on public.rk_events from public, anon, authenticated;

do $$
begin
  if to_regprocedure('public.rk_scores_for(timestamptz,uuid,boolean)') is not null then
    execute $fn$
      create or replace function public.rk_scores_for(p_from timestamptz, p_viewer uuid, p_see_all boolean)
      returns table (uid uuid, solved int, pts int)
      language sql stable security definer set search_path = public
      as $body$
        select r.user_id, (count(*) filter (where r.kind = 'p'))::int, greatest(coalesce(sum(r.pts), 0), 0)::int
          from public.rk_events r
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
    execute $fn$
      create or replace function public.rk_scores(p_from timestamptz default null)
      returns table (uid uuid, solved int, pts int)
      language sql stable security definer set search_path = public
      as $body$
        select r.user_id, (count(*) filter (where r.kind = 'p'))::int, greatest(coalesce(sum(r.pts), 0), 0)::int
          from public.rk_events r
          join public.profiles p on p.id = r.user_id and p.status = 'approved' and p.role <> 'admin'
         where (p_from is null or r.solved_at >= p_from)
           and not exists (select 1 from public.staff_roles sr where sr.user_id = p.id)
         group by r.user_id
      $body$
    $fn$;
    revoke all on function public.rk_scores(timestamptz) from public, anon, authenticated;
  end if;
end $$;

do $$
begin
  if to_regprocedure('public.tier_promos(date)') is not null then
    execute $fn$
      create or replace function public.tier_promos(p_day date)
      returns table (uid uuid, name text, from_idx int, to_idx int, from_tier text, to_tier text)
      language sql stable security definer set search_path = public
      as $body$
        with t as (select (p_day::timestamp at time zone 'Asia/Seoul') as t0),
        sc as (
          select e.user_id,
                 greatest(coalesce(sum(e.pts) filter (where e.solved_at < t.t0), 0), 0)::int as b,
                 greatest(coalesce(sum(e.pts) filter (where e.solved_at < t.t0 + interval '1 day'), 0), 0)::int as a
            from public.rk_events e cross join t group by e.user_id
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

create or replace function public.admin_adjust_score(p_uid uuid, p_delta int, p_note text default '')
returns text
language plpgsql security definer set search_path = public
as $$
begin
  if coalesce(public.staff_role(), '') not in ('owner', 'admin') then return 'forbidden'; end if;
  if p_delta is null or p_delta = 0 or abs(p_delta) > 10000000 then return 'invalid'; end if;
  if not public.py_is_student(p_uid) then return 'nouser'; end if;
  insert into public.rank_adjust (user_id, delta, note, created_by) values (p_uid, p_delta, left(coalesce(p_note, ''), 200), auth.uid());
  perform public.py_notify(p_uid, case when p_delta > 0 then '🏆 랭킹 점수 +' || p_delta else '랭킹 점수 ' || p_delta end,
    coalesce(nullif(btrim(p_note), ''), '선생님이 점수를 조정했어요.'), 'reward', '#/me');
  return 'ok';
end $$;

create or replace function public.admin_grant_py(p_uid uuid, p_delta int, p_note text default '')
returns text
language plpgsql security definer set search_path = public
as $$
begin
  if coalesce(public.staff_role(), '') not in ('owner', 'admin') then return 'forbidden'; end if;
  if p_delta is null or p_delta = 0 or abs(p_delta) > 10000000 then return 'invalid'; end if;
  if not public.py_is_student(p_uid) then return 'nouser'; end if;
  perform public.py_add(p_uid, p_delta, 'admin', null, left(coalesce(p_note, ''), 200), auth.uid(), true);
  perform public.py_notify(p_uid, case when p_delta > 0 then '💎 파이포인트 +' || p_delta else '💎 파이포인트 ' || p_delta end,
    coalesce(nullif(btrim(p_note), ''), '선생님이 파이포인트를 조정했어요.'), 'reward', '#/me/wallet');
  return 'ok';
end $$;

-- 관리자: 한 학생의 지갑 · 점수 조정 기록
create or replace function public.admin_user_wallet(p_uid uuid)
returns jsonb
language plpgsql stable security definer set search_path = public
as $$
begin
  if coalesce(public.staff_role(), '') not in ('owner', 'admin') then return null; end if;
  return jsonb_build_object(
    'balance', coalesce((select balance from public.py_wallet where user_id = p_uid), 0),
    'shields', coalesce((select shields from public.py_wallet where user_id = p_uid), 0),
    'score', coalesce((select pts from public.rk_scores(null) where uid = p_uid), 0),
    'ledger', (select coalesce(jsonb_agg(to_jsonb(l) order by l.id desc), '[]'::jsonb) from (select id, delta, reason, note, created_at from public.py_ledger where user_id = p_uid order by id desc limit 30) l),
    'adjust', (select coalesce(jsonb_agg(to_jsonb(a) order by a.id desc), '[]'::jsonb) from (select id, delta, note, created_at from public.rank_adjust where user_id = p_uid order by id desc limit 30) a));
end $$;

-- 5) 문제·학습 보상 (랜덤)
create or replace function public.trg_py_submission() returns trigger
language plpgsql security definer set search_path = public
as $$
declare v_amt int;
begin
  if coalesce(new.judge ->> 'status', '') <> 'AC' then return null; end if;
  if not public.py_is_student(new.user_id) then return null; end if;
  if exists (select 1 from public.submissions s where s.user_id = new.user_id and s.exercise_id = new.exercise_id
               and s.id <> new.id and s.judge ->> 'status' = 'AC') then return null; end if;
  v_amt := public.py_rand('solve_rand', 2, 6);
  if public.py_add(new.user_id, v_amt, 'solve', new.exercise_id::text, '문제를 맞췄어요') then
    perform public.py_notify(new.user_id, '💎 파이포인트 +' || v_amt, '문제를 처음 맞춰서 받았어요.', 'reward', '#/me/wallet');
  end if;
  return null;
end $$;
drop trigger if exists trg_py_submission on public.submissions;
create trigger trg_py_submission after insert on public.submissions for each row execute function public.trg_py_submission();

do $$
begin
  if to_regclass('public.learn_progress') is not null then
    execute $f$
      create or replace function public.trg_py_learn() returns trigger
      language plpgsql security definer set search_path = public
      as $b$
      declare v_amt int;
      begin
        if new.completed and (tg_op = 'INSERT' or not coalesce(old.completed, false)) and public.py_is_student(new.user_id) then
          v_amt := public.py_rand('learn_rand', 3, 8);
          if public.py_add(new.user_id, v_amt, 'learn', new.lesson_id::text, '학습 레슨을 끝냈어요') then
            perform public.py_notify(new.user_id, '💎 파이포인트 +' || v_amt, '학습 레슨을 끝내서 받았어요.', 'reward', '#/me/wallet');
          end if;
        end if;
        return null;
      end $b$
    $f$;
    drop trigger if exists trg_py_learn on public.learn_progress;
    create trigger trg_py_learn after insert or update on public.learn_progress for each row execute function public.trg_py_learn();
  end if;
end $$;

-- 6) 주간·월간 랭킹 보상 (끝난 기간을 처음 확인하는 사람이 한 번만 정산해요)
create table if not exists public.py_settled (
  period_id text primary key,
  settled_at timestamptz not null default now()
);
alter table public.py_settled enable row level security;
revoke all on public.py_settled from anon, authenticated;

create or replace function public.py_settle_period(p_id text, p_from timestamptz, p_to timestamptz, p_cfg text, p_label text)
returns void
language plpgsql security definer set search_path = public
as $$
declare x record; v_rewards jsonb := public.py_cfg(p_cfg, '[]'); v_n int := jsonb_array_length(public.py_cfg(p_cfg, '[]'));
begin
  insert into public.py_settled (period_id) values (p_id) on conflict do nothing;
  if not found then return; end if;
  for x in
    with per as (
      select e.user_id as uid, greatest(sum(e.pts), 0)::int as sc
        from public.rk_events e
        join public.profiles p on p.id = e.user_id and p.status = 'approved' and p.role <> 'admin'
       where e.solved_at >= p_from and e.solved_at < p_to
         and not exists (select 1 from public.staff_roles sr where sr.user_id = p.id)
         and not (to_regclass('public.student_tiers') is not null and public.py_is_solver(p.id))
       group by e.user_id having sum(e.pts) > 0),
    rk as (select uid, (rank() over (order by sc desc))::int as rnk from per),
    g as (select rnk, count(*)::int as n from rk group by rnk)
    select rk.uid, rk.rnk, g.n,
           (select coalesce(sum((v_rewards ->> (s - 1))::int), 0) from generate_series(rk.rnk, rk.rnk + g.n - 1) s where s <= v_n)::int / g.n as amt
      from rk join g on g.rnk = rk.rnk where rk.rnk <= v_n
  loop
    if x.amt > 0 and public.py_add(x.uid, x.amt, split_part(p_id, ':', 1), p_id, p_label || ' ' || x.rnk || '위') then
      perform public.py_notify(x.uid, '🏅 ' || p_label || ' ' || x.rnk || '위!', '파이포인트 +' || x.amt || ' 을 받았어요.', 'reward', '#/ranking');
    end if;
  end loop;
end $$;
revoke all on function public.py_settle_period(text, timestamptz, timestamptz, text, text) from public, anon, authenticated;

create or replace function public.py_settle() returns void
language plpgsql security definer set search_path = public
as $$
declare w0 timestamptz := public.rk_period_start('week'); m0 timestamptz := public.rk_period_start('month');
begin
  if not public.is_approved() then return; end if;
  perform public.py_settle_period('rank_week:' || to_char((w0 - interval '7 days') at time zone 'Asia/Seoul', 'YYYY-MM-DD'), w0 - interval '7 days', w0, 'week_rank', '지난주 랭킹');
  perform public.py_settle_period('rank_month:' || to_char((m0 - interval '1 month') at time zone 'Asia/Seoul', 'YYYY-MM'),
    (((m0 at time zone 'Asia/Seoul') - interval '1 month') at time zone 'Asia/Seoul'), m0, 'month_rank', '지난달 랭킹');
end $$;

-- 7) 배지
create table if not exists public.badge_defs (
  id text primary key check (id ~ '^[a-z0-9_]{2,40}$'),
  name text not null check (length(name) between 1 and 30),
  descr text not null default '' check (length(descr) <= 120),
  icon text not null default '🏅' check (length(icon) <= 8),
  kind text not null check (kind in ('score', 'solved', 'streak', 'learn', 'exam_first', 'exam_join', 'pypoint', 'manual')),
  threshold int not null default 0,
  tone text not null default 'blue' check (tone in ('blue', 'green', 'orange', 'purple', 'red', 'gold', 'teal', 'pink')),
  position int not null default 100,
  builtin boolean not null default false
);
create table if not exists public.user_badges (
  user_id uuid not null references public.profiles(id) on delete cascade,
  badge_id text not null references public.badge_defs(id) on delete cascade,
  earned_at timestamptz not null default now(),
  primary key (user_id, badge_id)
);
alter table public.badge_defs enable row level security;
alter table public.user_badges enable row level security;
revoke all on public.badge_defs, public.user_badges from anon, authenticated;
grant select on public.badge_defs, public.user_badges to authenticated;
drop policy if exists badge_defs_read on public.badge_defs;
create policy badge_defs_read on public.badge_defs for select to authenticated using (public.is_approved());
drop policy if exists user_badges_read on public.user_badges;
create policy user_badges_read on public.user_badges for select to authenticated using (public.is_approved());

insert into public.badge_defs (id, name, descr, icon, kind, threshold, tone, position, builtin) values
  ('score_100',   '100점 달성',     '랭킹 점수 100점을 넘었어요',        '⭐', 'score', 100,    'blue',   10, true),
  ('score_500',   '500점 달성',     '랭킹 점수 500점을 넘었어요',        '🌟', 'score', 500,    'blue',   11, true),
  ('score_1000',  '1,000점 달성',   '랭킹 점수 1,000점을 넘었어요',      '💫', 'score', 1000,   'teal',   12, true),
  ('score_3000',  '3,000점 달성',   '랭킹 점수 3,000점을 넘었어요',      '✨', 'score', 3000,   'teal',   13, true),
  ('score_10000', '10,000점 달성',  '랭킹 점수 10,000점을 넘었어요',     '🏆', 'score', 10000,  'gold',   14, true),
  ('score_50000', '50,000점 달성',  '랭킹 점수 50,000점을 넘었어요',     '👑', 'score', 50000,  'gold',   15, true),
  ('solve_1',     '첫 문제 해결',   '처음으로 문제를 맞췄어요',          '🎯', 'solved', 1,     'green',  20, true),
  ('solve_10',    '10문제 풀이',    '총 10문제를 맞췄어요',              '🧩', 'solved', 10,    'green',  21, true),
  ('solve_50',    '50문제 풀이',    '총 50문제를 맞췄어요',              '🔥', 'solved', 50,    'orange', 22, true),
  ('solve_100',   '100문제 풀이',   '총 100문제를 맞췄어요',             '💪', 'solved', 100,   'orange', 23, true),
  ('solve_300',   '300문제 풀이',   '총 300문제를 맞췄어요',             '🚀', 'solved', 300,   'purple', 24, true),
  ('streak_3',    '3일 연속 학습',  '3일 연속으로 학습했어요',           '🔥', 'streak', 3,     'orange', 30, true),
  ('streak_5',    '5일 연속 학습',  '5일 연속으로 학습했어요',           '🔥', 'streak', 5,     'orange', 31, true),
  ('streak_7',    '7일 연속 학습',  '일주일 내내 학습했어요',            '📆', 'streak', 7,     'red',    32, true),
  ('streak_14',   '14일 연속 학습', '2주 연속으로 학습했어요',           '🗓️', 'streak', 14,    'red',    33, true),
  ('streak_30',   '30일 연속 학습', '한 달 연속으로 학습했어요',         '🏅', 'streak', 30,    'gold',   34, true),
  ('streak_100',  '100일 연속 학습','100일 연속! 대단해요',              '💎', 'streak', 100,   'purple', 35, true),
  ('learn_1',     '첫 레슨 완료',   '학습 레슨을 처음 끝냈어요',         '📚', 'learn', 1,      'teal',   40, true),
  ('learn_10',    '레슨 10개 완료', '학습 레슨을 10개 끝냈어요',         '🎓', 'learn', 10,     'teal',   41, true),
  ('exam_join',   '첫 시험 응시',   '시험에 처음 참가했어요',            '📝', 'exam_join', 1,  'pink',   50, true),
  ('exam_first',  '시험 1등',       '시험에서 1등을 했어요',             '🥇', 'exam_first', 1, 'gold',   51, true),
  ('py_1000',     '파이포인트 부자','파이포인트를 누적 1,000 모았어요',  '💎', 'pypoint', 1000, 'purple', 60, true)
on conflict (id) do nothing;

create or replace function public.badges_check() returns jsonb
language plpgsql security definer set search_path = public
as $$
declare
  v_me uuid := auth.uid();
  v_score int := 0; v_solved int := 0; v_best int := 0; v_learn int := 0; v_first int := 0; v_join int := 0; v_py int := 0;
  r record; b record; v_new jsonb := '[]'::jsonb; v_val int;
begin
  if v_me is null or not public.py_is_student(v_me) then return '[]'::jsonb; end if;
  select coalesce(pts, 0), coalesce(solved, 0) into v_score, v_solved from public.rk_scores(null) where uid = v_me;
  v_score := coalesce(v_score, 0); v_solved := coalesce(v_solved, 0);
  v_best := coalesce((public.streak_info() ->> 'best')::int, 0);
  if to_regclass('public.learn_progress') is not null then
    execute 'select count(*) from public.learn_progress where user_id = $1 and completed' into v_learn using v_me;
  end if;
  if to_regclass('public.exam_results') is not null then
    execute 'select count(*) from public.exam_results where user_id = $1' into v_join using v_me;
    execute 'select count(*) from public.exam_results where user_id = $1 and final_rank = 1' into v_first using v_me;
  end if;
  select coalesce(sum(delta), 0) into v_py from public.py_ledger where user_id = v_me and delta > 0;
  for b in select * from public.badge_defs where kind <> 'manual' order by position loop
    v_val := case b.kind when 'score' then v_score when 'solved' then v_solved when 'streak' then v_best when 'learn' then v_learn
                         when 'exam_join' then v_join when 'exam_first' then v_first when 'pypoint' then v_py else 0 end;
    if v_val >= b.threshold and b.threshold > 0 then
      insert into public.user_badges (user_id, badge_id) values (v_me, b.id) on conflict do nothing;
      if found then
        v_new := v_new || jsonb_build_object('id', b.id, 'name', b.name, 'icon', b.icon);
        perform public.py_notify(v_me, '🎖️ 새 배지: ' || b.name, b.descr, 'badge', '#/me/badges');
      end if;
    end if;
  end loop;
  return v_new;
end $$;

-- 한 번에: 앱을 열거나 활동한 뒤 부르는 요약 (순위 보상 정산 + 배지 확인 + 내 지갑·연속 학습)
create or replace function public.growth_boot() returns jsonb
language plpgsql security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); v_new jsonb := '[]'::jsonb;
begin
  if v_me is null or not public.is_approved() then return null; end if;
  perform public.py_settle();
  if public.py_is_student(v_me) then v_new := public.badges_check(); end if;
  return jsonb_build_object(
    'py', coalesce((select balance from public.py_wallet where user_id = v_me), 0),
    'shields', coalesce((select shields from public.py_wallet where user_id = v_me), 0),
    'streak', public.streak_info(),
    'new_badges', v_new,
    'student', public.py_is_student(v_me),
    'cfg', jsonb_build_object('shield_price', public.py_cfg('shield_price', '60'), 'shield_max', public.py_cfg('shield_max', '2')));
end $$;

-- 관리자: 배지 만들기/고치기/지우기/직접 주기·회수, 설정값 고치기
create or replace function public.badge_upsert(p jsonb) returns text
language plpgsql security definer set search_path = public
as $$
begin
  if coalesce(public.staff_role(), '') not in ('owner', 'admin') then return 'forbidden'; end if;
  insert into public.badge_defs (id, name, descr, icon, kind, threshold, tone, position)
  values (p ->> 'id', p ->> 'name', coalesce(p ->> 'descr', ''), coalesce(nullif(p ->> 'icon', ''), '🏅'), coalesce(p ->> 'kind', 'manual'),
          coalesce((p ->> 'threshold')::int, 0), coalesce(p ->> 'tone', 'blue'), coalesce((p ->> 'position')::int, 100))
  on conflict (id) do update set name = excluded.name, descr = excluded.descr, icon = excluded.icon, kind = excluded.kind,
    threshold = excluded.threshold, tone = excluded.tone, position = excluded.position;
  return 'ok';
exception when others then return 'invalid';
end $$;
create or replace function public.badge_delete(p_id text) returns text
language plpgsql security definer set search_path = public
as $$
begin
  if coalesce(public.staff_role(), '') not in ('owner', 'admin') then return 'forbidden'; end if;
  delete from public.badge_defs where id = p_id and not builtin;
  return 'ok';
end $$;
create or replace function public.badge_award(p_uid uuid, p_id text, p_on boolean default true) returns text
language plpgsql security definer set search_path = public
as $$
declare b public.badge_defs;
begin
  if coalesce(public.staff_role(), '') not in ('owner', 'admin') then return 'forbidden'; end if;
  select * into b from public.badge_defs where id = p_id;
  if not found or not public.py_is_student(p_uid) then return 'nouser'; end if;
  if p_on then
    insert into public.user_badges (user_id, badge_id) values (p_uid, p_id) on conflict do nothing;
    if found then perform public.py_notify(p_uid, '🎖️ 새 배지: ' || b.name, b.descr, 'badge', '#/me/badges'); end if;
  else
    delete from public.user_badges where user_id = p_uid and badge_id = p_id;
  end if;
  return 'ok';
end $$;
create or replace function public.py_cfg_set(p_key text, p_val jsonb) returns text
language plpgsql security definer set search_path = public
as $$
begin
  if coalesce(public.staff_role(), '') not in ('owner', 'admin') then return 'forbidden'; end if;
  if p_key not in ('week_rank', 'month_rank', 'solve_rand', 'learn_rand', 'shield_price', 'shield_max') then return 'invalid'; end if;
  insert into public.py_config (key, val) values (p_key, p_val) on conflict (key) do update set val = excluded.val, updated_at = now();
  return 'ok';
end $$;

revoke all on function public.streak_info(), public.py_buy_shield(), public.py_settle(), public.badges_check(), public.growth_boot(),
  public.admin_adjust_score(uuid, int, text), public.admin_grant_py(uuid, int, text), public.admin_user_wallet(uuid),
  public.badge_upsert(jsonb), public.badge_delete(text), public.badge_award(uuid, text, boolean), public.py_cfg_set(text, jsonb) from public, anon;
grant execute on function public.streak_info(), public.py_buy_shield(), public.py_settle(), public.badges_check(), public.growth_boot(),
  public.admin_adjust_score(uuid, int, text), public.admin_grant_py(uuid, int, text), public.admin_user_wallet(uuid),
  public.badge_upsert(jsonb), public.badge_delete(text), public.badge_award(uuid, text, boolean), public.py_cfg_set(text, jsonb) to authenticated;
