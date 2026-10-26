-- =====================================================================
--  PyNest V3.1.0 — 별명 · 주간/월간 랭킹 · 티어 · 프로필 · 난이도(점수)
--  * 기존 표·데이터는 지우지 않아요. 새 표/함수/컬럼을 "추가"하고, 여러 번 실행해도 안전해요.
--  * 단 하나, exercises.difficulty 의 "4개만 허용" 검사(CHECK)는 사용자 지정 난이도를 위해
--    "난이도 표(difficulties)에 있는 이름만 허용"(외래키)으로 바꿔요. 기존 4개 난이도는 그대로 통과해요.
--  * staff_roles.sql 이 먼저 적용돼 있어야 해요. (student_tiers.sql 은 있어도 없어도 돼요)
--
--  점수  = 푼(AC) 문제의 점수 합 (같은 문제는 1번만)
--          문제 점수 = 문제에 직접 지정한 "랭킹 점수" → 없으면 난이도 점수 → 없으면 10
--  랭킹  = 이번 주(월~일) / 이번 달 에 "처음 맞춘" 서로 다른 문제 개수  (한국 시간 기준)
--  티어  = 누적 점수 (뱃지·구간은 app.js 의 TIERS)
-- =====================================================================

do $$
begin
  if to_regprocedure('public.staff_can(text)') is null then
    raise exception 'staff_roles.sql 을 먼저 실행해주세요.';
  end if;
end $$;

-- ---------------------------------------------------------------------
-- 1) 난이도 표 (사용자 지정 난이도 + 난이도별 점수)
-- ---------------------------------------------------------------------
create table if not exists public.difficulties (
  name text primary key check (length(btrim(name)) between 1 and 24),
  points int not null default 10 check (points between 0 and 100000),
  color text check (color is null or color ~ '^#[0-9a-fA-F]{6}$'),
  position int not null default 100,
  builtin boolean not null default false,
  created_at timestamptz not null default now()
);
insert into public.difficulties (name, points, color, position, builtin) values
  ('Beginner',      5, '#16a34a', 10, true),
  ('Intermediate', 10, '#2563eb', 20, true),
  ('Advanced',     20, '#7e22ce', 30, true),
  ('ELITE',        30, '#db2777', 40, true)
on conflict (name) do nothing;

alter table public.difficulties enable row level security;
revoke all on public.difficulties from anon;
grant select, insert, update, delete on public.difficulties to authenticated;
drop policy if exists difficulties_read on public.difficulties;
create policy difficulties_read on public.difficulties for select to authenticated using (public.is_approved());
drop policy if exists difficulties_ins on public.difficulties;
create policy difficulties_ins on public.difficulties for insert to authenticated with check (public.staff_can('content'));
drop policy if exists difficulties_upd on public.difficulties;
create policy difficulties_upd on public.difficulties for update to authenticated
  using (public.staff_can('content')) with check (public.staff_can('content'));
drop policy if exists difficulties_del on public.difficulties;
create policy difficulties_del on public.difficulties for delete to authenticated
  using (public.staff_can('content') and not builtin);

-- 기본 4개는 이름·성격을 못 바꾸고, 직접 만든 난이도는 항상 "직접 만든 것"
create or replace function public.difficulties_guard()
returns trigger language plpgsql set search_path = public
as $$
begin
  if tg_op = 'INSERT' then
    if auth.uid() is not null then new.builtin := false; end if;
    new.name := btrim(new.name);
    return new;
  end if;
  if old.builtin and (new.name is distinct from old.name or new.builtin is distinct from old.builtin) then
    raise exception 'builtin difficulty';
  end if;
  if not old.builtin and new.builtin then raise exception 'not allowed'; end if;
  new.name := btrim(new.name);
  return new;
end;
$$;
drop trigger if exists difficulties_guard on public.difficulties;
create trigger difficulties_guard before insert or update on public.difficulties
  for each row execute function public.difficulties_guard();

-- 문제: "4개만 허용" 검사 → 난이도 표 참조로 교체 / 문제별 랭킹 점수(선택)
alter table public.exercises drop constraint if exists exercises_difficulty_check;
do $$
begin
  if not exists (select 1 from pg_constraint where conname = 'exercises_difficulty_fk') then
    alter table public.exercises
      add constraint exercises_difficulty_fk foreign key (difficulty) references public.difficulties(name) on update cascade;
  end if;
end $$;
alter table public.exercises add column if not exists rank_points int;
do $$
begin
  if not exists (select 1 from pg_constraint where conname = 'exercises_rank_points_check') then
    alter table public.exercises add constraint exercises_rank_points_check check (rank_points is null or rank_points >= 0);
  end if;
end $$;

-- ---------------------------------------------------------------------
-- 2) 별명 (직원만 설정 · 학생에게는 별명만, 직원에게는 "별명 (ID)" 로 보여요)
-- ---------------------------------------------------------------------
create table if not exists public.nicknames (
  user_id uuid primary key references public.profiles(id) on delete cascade,
  nickname text not null check (length(btrim(nickname)) between 1 and 20),
  set_by uuid,
  updated_at timestamptz not null default now()
);
create unique index if not exists nicknames_lower_uidx on public.nicknames (lower(nickname));
alter table public.nicknames enable row level security;
revoke all on public.nicknames from anon, authenticated;
grant select on public.nicknames to authenticated;
drop policy if exists nicknames_read on public.nicknames;
create policy nicknames_read on public.nicknames for select to authenticated
  using (user_id = auth.uid() or public.staff_role() is not null);

-- 화면에 보일 이름
create or replace function public.disp(p_uid uuid)
returns text
language sql stable security definer set search_path = public
as $$
  select case
    when n.nickname is null then p.username
    when public.staff_role() is not null then n.nickname || ' (' || p.username || ')'
    else n.nickname
  end
  from public.profiles p left join public.nicknames n on n.user_id = p.id
  where p.id = p_uid and public.is_approved()
$$;
revoke all on function public.disp(uuid) from public, anon;
grant execute on function public.disp(uuid) to authenticated;  -- 보기(view)가 호출하므로 필요해요

-- 별명 설정. p_nick 이 비어 있으면 별명 삭제. 결과: ok / invalid / not_found / taken
create or replace function public.nickname_set(p_username text, p_nick text)
returns text
language plpgsql security definer set search_path = public
as $$
declare
  v_tid uuid;
  v_nick text := btrim(coalesce(p_nick, ''));
begin
  if auth.uid() is null or public.staff_role() is null then raise exception 'not allowed'; end if;
  select p.id into v_tid from public.profiles p where lower(p.username) = lower(btrim(p_username)) limit 1;
  if v_tid is null then return 'not_found'; end if;
  if v_nick = '' then
    delete from public.nicknames where user_id = v_tid;
    return 'ok';
  end if;
  if length(v_nick) > 20 then return 'invalid'; end if;
  -- 다른 사람의 ID 와 같은 별명은 못 써요 (사칭 방지)
  if exists (select 1 from public.profiles p where lower(p.username) = lower(v_nick) and p.id <> v_tid) then return 'taken'; end if;
  begin
    insert into public.nicknames (user_id, nickname, set_by) values (v_tid, v_nick, auth.uid())
    on conflict (user_id) do update set nickname = excluded.nickname, set_by = excluded.set_by, updated_at = now();
  exception when unique_violation then
    return 'taken';
  end;
  return 'ok';
end;
$$;
revoke all on function public.nickname_set(text, text) from public, anon;
grant execute on function public.nickname_set(text, text) to authenticated;

-- 글·댓글 작성자: 별명으로 + 프로필 링크용 author_id (익명이면 가려요). 기존 컬럼은 그대로, 맨 뒤에 추가만 해요.
create or replace view public.posts_view as
 SELECT p.id, p.board, p.title, p.content, p.anonymous, p.allow_comments, p.week, p.files, p.created_at, p.updated_at,
    (p.author_id = auth.uid()) AS is_mine,
    CASE WHEN (p.anonymous AND (p.author_id <> auth.uid()) AND (NOT public.staff_can('review'))) THEN '익명'::text ELSE public.disp(p.author_id) END AS author_name,
    CASE WHEN (p.anonymous AND (p.author_id <> auth.uid()) AND (NOT public.staff_can('review'))) THEN NULL::uuid ELSE p.author_id END AS author_id
   FROM (public.posts p JOIN public.profiles pr ON ((pr.id = p.author_id)))
  WHERE (public.is_approved() AND ((p.board <> 'assignment'::text) OR (p.author_id = auth.uid()) OR public.staff_can('review')));

create or replace view public.comments_view as
 SELECT c.id, c.post_id, c.content, c.anonymous, c.created_at,
    (c.author_id = auth.uid()) AS is_mine,
    (((pr.role = 'admin'::text) OR EXISTS (SELECT 1 FROM public.staff_roles sr WHERE sr.user_id = pr.id AND sr.role IN ('admin', 'teacher'))) AND (NOT c.anonymous)) AS by_admin,
    CASE WHEN (c.anonymous AND (c.author_id <> auth.uid()) AND (NOT public.staff_can('review'))) THEN '익명'::text ELSE public.disp(c.author_id) END AS author_name,
    CASE WHEN (c.anonymous AND (c.author_id <> auth.uid()) AND (NOT public.staff_can('review'))) THEN NULL::uuid ELSE c.author_id END AS author_id
   FROM ((public.comments c JOIN public.profiles pr ON ((pr.id = c.author_id))) JOIN public.posts p ON ((p.id = c.post_id)))
  WHERE (public.is_approved() AND ((p.board <> 'assignment'::text) OR (p.author_id = auth.uid()) OR public.staff_can('review')));

-- ---------------------------------------------------------------------
-- 3) 점수 · 랭킹 (집계는 서버에서, 학생끼리는 서로의 제출 내용을 못 봐요 — 숫자만 보여요)
-- ---------------------------------------------------------------------
-- 학생별 "처음 맞춘" 문제 (API 로는 못 읽어요)
create or replace view public.rk_solved as
 select s.user_id, s.exercise_id, min(s.created_at) as solved_at,
        e.set_id, e.difficulty, e."position" as pos,
        coalesce(e.rank_points, d.points, 10) as pts
   from public.submissions s
   join public.exercises e on e.id = s.exercise_id
   left join public.difficulties d on d.name = e.difficulty
  where s.judge ->> 'status' = 'AC'
  group by s.user_id, s.exercise_id, e.set_id, e.difficulty, e."position", e.rank_points, d.points;
revoke all on public.rk_solved from public, anon, authenticated;

-- 승인된 "학생"(직원 제외)의 기간별 푼 개수·점수. p_from 이 null 이면 전체 기간
create or replace function public.rk_scores(p_from timestamptz default null)
returns table (uid uuid, solved int, pts int)
language sql stable security definer set search_path = public
as $$
  select r.user_id, count(*)::int, coalesce(sum(r.pts), 0)::int
    from public.rk_solved r
    join public.profiles p on p.id = r.user_id and p.status = 'approved' and p.role <> 'admin'
   where (p_from is null or r.solved_at >= p_from)
     and not exists (select 1 from public.staff_roles sr where sr.user_id = p.id)
   group by r.user_id
$$;
revoke all on function public.rk_scores(timestamptz) from public, anon, authenticated;

-- 이번 주(월요일 시작) / 이번 달 시작 시각 (한국 시간)
create or replace function public.rk_period_start(p_period text)
returns timestamptz
language sql stable set search_path = public
as $$
  select case p_period
    when 'week'  then date_trunc('week',  now() at time zone 'Asia/Seoul') at time zone 'Asia/Seoul'
    when 'month' then date_trunc('month', now() at time zone 'Asia/Seoul') at time zone 'Asia/Seoul'
    else null end
$$;
revoke all on function public.rk_period_start(text) from public, anon, authenticated;

-- 랭킹. p_period: week / month. 순위는 "푼 개수"로만 매기고(같으면 공동), 같은 개수끼리는 점수 순으로 보여줘요.
create or replace function public.rank_board(p_period text)
returns table (user_id uuid, name text, solved int, pts int, rnk int, score int)
language sql stable security definer set search_path = public
as $$
  with per as (select * from public.rk_scores(public.rk_period_start(p_period))),
       tot as (select * from public.rk_scores(null))
  select per.uid, public.disp(per.uid), per.solved, per.pts,
         (rank() over (order by per.solved desc))::int,
         coalesce(tot.pts, 0)
    from per left join tot on tot.uid = per.uid
   where public.is_approved() and p_period in ('week', 'month')
   order by per.solved desc, per.pts desc, 2
$$;

-- 이름 + 누적 점수 (뱃지·이름 표시용). 직원에게만 원래 ID(uname)도 내려가요.
create or replace function public.student_directory()
returns table (user_id uuid, name text, nick text, uname text, score int, solved int)
language sql stable security definer set search_path = public
as $$
  select p.id, public.disp(p.id), n.nickname,
         case when public.staff_role() is not null then p.username end,
         coalesce(t.pts, 0), coalesce(t.solved, 0)
    from public.profiles p
    left join public.nicknames n on n.user_id = p.id
    left join public.rk_scores(null) t on t.uid = p.id
   where public.is_approved() and p.status = 'approved' and p.role <> 'admin'
     and not exists (select 1 from public.staff_roles sr where sr.user_id = p.id)
$$;

-- 프로필 (백준처럼 다른 학생도 볼 수 있어요). 푼 문제의 코드·답은 안 나가요.
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
  select 1 + count(*) into v_rw from public.rk_scores(v_ws) x where x.solved > coalesce(v_w.solved, 0);
  select 1 + count(*) into v_rm from public.rk_scores(v_ms) x where x.solved > coalesce(v_m.solved, 0);

  select coalesce(jsonb_agg(jsonb_build_object('difficulty', t.difficulty, 'n', t.n) order by t.n desc), '[]'::jsonb)
    into v_by
    from (select r.difficulty, count(*)::int as n from public.rk_solved r where r.user_id = p_uid group by r.difficulty) t;

  select coalesce(jsonb_agg(to_jsonb(x) order by x.at desc), '[]'::jsonb)
    into v_recent
    from (
      select r.exercise_id as id, r.difficulty, r.solved_at as at, r.set_id, r.pts,
             ps.title as set_title, ps.short_name as set_short,
             (select count(*) from public.exercises e2
               where e2.set_id = r.set_id
                 and ((e2.difficulty = 'ELITE') = (r.difficulty = 'ELITE'))
                 and (e2."position", e2.id) <= (r."pos", r.exercise_id))::int as no
        from public.rk_solved r
        left join public.problem_sets ps on ps.id = r.set_id
       where r.user_id = p_uid
       order by r.solved_at desc
       limit 10
    ) x;

  return jsonb_build_object(
    'uid', p_uid,
    'name', public.disp(p_uid),
    'uname', case when public.staff_role() is not null then v_p.username end,
    'joined', v_p.created_at,
    'score', coalesce(v_tot.pts, 0),
    'solved', coalesce(v_tot.solved, 0),
    'week', jsonb_build_object('solved', coalesce(v_w.solved, 0), 'rank', case when coalesce(v_w.solved, 0) > 0 then v_rw end),
    'month', jsonb_build_object('solved', coalesce(v_m.solved, 0), 'rank', case when coalesce(v_m.solved, 0) > 0 then v_rm end),
    'by_diff', v_by,
    'recent', v_recent
  );
end;
$$;

revoke all on function public.rank_board(text) from public, anon;
revoke all on function public.student_directory() from public, anon;
revoke all on function public.user_profile(uuid) from public, anon;
grant execute on function public.rank_board(text) to authenticated;
grant execute on function public.student_directory() to authenticated;
grant execute on function public.user_profile(uuid) to authenticated;
