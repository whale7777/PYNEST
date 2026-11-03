-- PyNest V4.5.4 · v454_exam.sql
-- 1) 모든 가격 10배 (한 번만 적용돼요)  2) 📝 시험 (입장·동시 시작·자동 채점·순위 보상·결과 공개 선택)  3) 시험 풍선 장식 아이템 3종
-- v453b_economy.sql 다음에 한 번만 실행하세요. (여러 번 실행해도 안전해요)

do $$
begin
  if to_regclass('public.py_config') is null or to_regclass('public.avatar_items') is null or to_regclass('public.badge_defs') is null
     or not exists (select 1 from public.py_config where key = 'gacha') then
    raise exception 'v450 ~ v453b SQL 을 먼저 실행해주세요.';
  end if;
end $$;

-- 1) 가격 10배 (py_config 에 price_x10 표시를 남겨서 두 번 곱하지 않아요)
do $$
begin
  if exists (select 1 from public.py_config where key = 'price_x10') then return; end if;
  insert into public.py_config (key, val) values ('item_price_mult', '30'::jsonb)
    on conflict (key) do update set val = to_jsonb(round((public.py_config.val #>> '{}')::numeric * 10)), updated_at = now();
  insert into public.py_config (key, val) values ('shield_price', '600'::jsonb)
    on conflict (key) do update set val = to_jsonb(round((public.py_config.val #>> '{}')::numeric * 10)), updated_at = now();
  update public.py_config set val = jsonb_build_object('basic', (val ->> 'basic')::int * 10, 'premium', (val ->> 'premium')::int * 10), updated_at = now() where key = 'gacha';
  update public.py_config set val = jsonb_set(jsonb_set(jsonb_set(val, '{min}', to_jsonb((val ->> 'min')::int * 10)), '{max}', to_jsonb((val ->> 'max')::int * 10)), '{daily}', to_jsonb((val ->> 'daily')::int * 10)), updated_at = now() where key = 'gift';
  update public.avatar_items set price = price * 10 where market;   -- 학생이 정한 마켓 가격도 10배
  insert into public.py_config (key, val) values ('price_x10', 'true'::jsonb);
end $$;

-- 마켓 가격 범위 100 ~ 20,000
create or replace function public.market_submit(p jsonb) returns text
language plpgsql security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); v_id text := nullif(p ->> 'id', ''); v_price int; v_old public.avatar_items;
begin
  if v_me is null or not public.py_is_student(v_me) then return 'nouser'; end if;
  v_price := (p ->> 'price')::int;
  if v_price is null or v_price < 100 or v_price > 20000 then return 'price'; end if;
  if v_id is not null then
    select * into v_old from public.avatar_items where id = v_id and created_by = v_me and market;
    if not found or v_old.status not in ('pending', 'rejected') then return 'nouser'; end if;
    update public.avatar_items set name = left(p ->> 'name', 30), descr = left(coalesce(p ->> 'descr', ''), 120), slot = p ->> 'slot',
      svg = p ->> 'svg', price = v_price, status = 'pending', reject_note = '' where id = v_id;
    return 'ok';
  end if;
  if (select count(*) from public.avatar_items where created_by = v_me and market and status = 'pending') >= 5 then return 'many'; end if;
  if (select count(*) from public.avatar_items where created_by = v_me and market) >= 40 then return 'limit'; end if;
  v_id := 'm' || substr(md5(random()::text || clock_timestamp()::text || v_me::text), 1, 10);
  insert into public.avatar_items (id, name, descr, slot, svg, kind, val, price, status, market, created_by)
  values (v_id, left(p ->> 'name', 30), left(coalesce(p ->> 'descr', ''), 120), p ->> 'slot', p ->> 'svg', 'price', 0, v_price, 'pending', true, v_me);
  return 'ok';
exception when others then return 'invalid';
end $$;

-- 2) 시험
create table if not exists public.exams (
  id bigint generated always as identity primary key,
  title text not null check (length(title) between 1 and 60),
  descr text not null default '' check (length(descr) <= 2000),
  start_at timestamptz not null,
  duration_min int not null default 60 check (duration_min between 5 and 600),
  entry_min int not null default 60 check (entry_min between 0 and 1440),
  status text not null default 'draft' check (status in ('draft', 'open')),
  reward jsonb not null default '{"pt_rank":[300,200,100],"pt_join":50,"item_first":"exam_balloon_gold","item_top3":"exam_balloon_silver","item_join":"exam_balloon_blue"}'::jsonb,
  settled_at timestamptz,
  created_by uuid,
  created_at timestamptz not null default now()
);
create table if not exists public.exam_problems (
  id bigint generated always as identity primary key,
  exam_id bigint not null references public.exams(id) on delete cascade,
  position int not null default 1,
  title text not null default '' check (length(title) <= 100),
  body text not null default '' check (length(body) <= 20000),
  points int not null default 100 check (points between 1 and 1000),
  tests jsonb not null default '[]'::jsonb
);
create index if not exists exam_problems_exam_idx on public.exam_problems (exam_id, position);
create table if not exists public.exam_entries (
  exam_id bigint not null references public.exams(id) on delete cascade,
  user_id uuid not null references public.profiles(id) on delete cascade,
  joined_at timestamptz not null default now(),
  public boolean not null default true,
  primary key (exam_id, user_id)
);
create table if not exists public.exam_subs (
  id bigint generated always as identity primary key,
  exam_id bigint not null references public.exams(id) on delete cascade,
  problem_id bigint not null references public.exam_problems(id) on delete cascade,
  user_id uuid not null references public.profiles(id) on delete cascade,
  code text not null default '' check (length(code) <= 20000),
  passed int not null default 0,
  total int not null default 0,
  created_at timestamptz not null default now()
);
create index if not exists exam_subs_idx on public.exam_subs (exam_id, user_id, problem_id, id);
create table if not exists public.exam_results (
  exam_id bigint not null references public.exams(id) on delete cascade,
  user_id uuid not null references public.profiles(id) on delete cascade,
  score int not null default 0,
  solved int not null default 0,
  last_at timestamptz,
  final_rank int not null,
  primary key (exam_id, user_id)
);
alter table public.exams enable row level security;
alter table public.exam_problems enable row level security;
alter table public.exam_entries enable row level security;
alter table public.exam_subs enable row level security;
alter table public.exam_results enable row level security;
revoke all on public.exams, public.exam_problems, public.exam_entries, public.exam_subs, public.exam_results from anon, authenticated;
grant select on public.exams, public.exam_problems, public.exam_entries, public.exam_subs, public.exam_results to authenticated;
drop policy if exists exams_read on public.exams;
create policy exams_read on public.exams for select to authenticated
  using (public.is_approved() and (status = 'open' or coalesce(public.staff_role(), '') in ('owner', 'admin')));
drop policy if exists exam_problems_staff on public.exam_problems;
create policy exam_problems_staff on public.exam_problems for select to authenticated using (coalesce(public.staff_role(), '') in ('owner', 'admin'));
drop policy if exists exam_entries_own on public.exam_entries;
create policy exam_entries_own on public.exam_entries for select to authenticated using (user_id = auth.uid() or coalesce(public.staff_role(), '') in ('owner', 'admin'));
drop policy if exists exam_subs_own on public.exam_subs;
create policy exam_subs_own on public.exam_subs for select to authenticated using (user_id = auth.uid() or coalesce(public.staff_role(), '') in ('owner', 'admin'));
drop policy if exists exam_results_own on public.exam_results;
create policy exam_results_own on public.exam_results for select to authenticated using (user_id = auth.uid() or coalesce(public.staff_role(), '') in ('owner', 'admin'));

create or replace function public.exam_end(e public.exams) returns timestamptz
language sql immutable as $$ select e.start_at + make_interval(mins => e.duration_min) $$;

-- 서버 시계 (모두 같은 순간에 시작하도록 브라우저 시계를 보정해요)
create or replace function public.exam_clock() returns timestamptz
language sql stable security definer set search_path = public as $$ select now() $$;
revoke all on function public.exam_clock() from public, anon;
grant execute on function public.exam_clock() to authenticated;

-- 목록 (열린 시험 + 내 상태)
create or replace function public.exam_list() returns jsonb
language plpgsql stable security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); v_adm boolean := coalesce(public.staff_role(), '') in ('owner', 'admin');
begin
  if v_me is null or not public.is_approved() then return null; end if;
  return jsonb_build_object('now', now(), 'exams', coalesce((select jsonb_agg(jsonb_build_object(
      'id', e.id, 'title', e.title, 'descr', e.descr, 'start_at', e.start_at, 'end_at', public.exam_end(e), 'duration_min', e.duration_min,
      'entry_min', e.entry_min, 'status', e.status, 'settled', e.settled_at is not null, 'reward', e.reward,
      'n_problems', (select count(*) from public.exam_problems p where p.exam_id = e.id),
      'n_entries', (select count(*) from public.exam_entries x where x.exam_id = e.id),
      'entered', exists (select 1 from public.exam_entries x where x.exam_id = e.id and x.user_id = v_me),
      'my_rank', (select r.final_rank from public.exam_results r where r.exam_id = e.id and r.user_id = v_me),
      'my_score', (select r.score from public.exam_results r where r.exam_id = e.id and r.user_id = v_me)) order by e.start_at desc)
    from public.exams e where e.status = 'open' or v_adm), '[]'::jsonb));
end $$;

-- 입장 (시작 entry_min 분 전부터 끝날 때까지)
create or replace function public.exam_enter(p_id bigint) returns text
language plpgsql security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); e public.exams;
begin
  if v_me is null or not public.py_is_student(v_me) then return 'nouser'; end if;
  select * into e from public.exams where id = p_id and status = 'open';
  if not found then return 'nouser'; end if;
  if now() < e.start_at - make_interval(mins => e.entry_min) then return 'early'; end if;
  if now() >= public.exam_end(e) then return 'closed'; end if;
  insert into public.exam_entries (exam_id, user_id) values (p_id, v_me) on conflict do nothing;
  return 'ok';
end $$;
revoke all on function public.exam_enter(bigint) from public, anon;
grant execute on function public.exam_enter(bigint) to authenticated;

-- 시험지: 시작 전엔 문제를 안 보여줘요. 끝난 뒤에는 문제만(채점용 테스트 없이) 다시 볼 수 있어요.
create or replace function public.exam_get(p_id bigint) returns jsonb
language plpgsql stable security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); e public.exams; v_adm boolean := coalesce(public.staff_role(), '') in ('owner', 'admin');
        v_in boolean; v_live boolean; v_over boolean; v_probs jsonb;
begin
  if v_me is null or not public.is_approved() then return null; end if;
  select * into e from public.exams where id = p_id and (status = 'open' or v_adm);
  if not found then return null; end if;
  v_in := exists (select 1 from public.exam_entries where exam_id = p_id and user_id = v_me);
  v_live := now() >= e.start_at and now() < public.exam_end(e) + interval '20 seconds';
  v_over := now() >= public.exam_end(e);
  if (v_live and (v_in or v_adm)) then
    select coalesce(jsonb_agg(jsonb_build_object('id', p.id, 'position', p.position, 'title', p.title, 'body', p.body, 'points', p.points, 'tests', p.tests) order by p.position, p.id), '[]'::jsonb)
      into v_probs from public.exam_problems p where p.exam_id = p_id;
  elsif v_over and (v_in or v_adm) then
    select coalesce(jsonb_agg(jsonb_build_object('id', p.id, 'position', p.position, 'title', p.title, 'body', p.body, 'points', p.points) order by p.position, p.id), '[]'::jsonb)
      into v_probs from public.exam_problems p where p.exam_id = p_id;
  else
    v_probs := '[]'::jsonb;
  end if;
  return jsonb_build_object('now', now(), 'id', e.id, 'title', e.title, 'descr', e.descr, 'start_at', e.start_at, 'end_at', public.exam_end(e), 'duration_min', e.duration_min,
    'entry_min', e.entry_min, 'status', e.status, 'settled', e.settled_at is not null, 'reward', e.reward, 'entered', v_in,
    'public', (select x.public from public.exam_entries x where x.exam_id = p_id and x.user_id = v_me),
    'n_problems', (select count(*) from public.exam_problems where exam_id = p_id),
    'n_entries', (select count(*) from public.exam_entries where exam_id = p_id),
    'problems', v_probs,
    'mine', coalesce((select jsonb_object_agg(q.problem_id, jsonb_build_object('passed', q.passed, 'total', q.total, 'code', q.code))
        from (select distinct on (s.problem_id) s.problem_id, s.passed, s.total, s.code from public.exam_subs s
               where s.exam_id = p_id and s.user_id = v_me order by s.problem_id, s.id desc) q), '{}'::jsonb));
end $$;
revoke all on function public.exam_get(bigint) from public, anon;
grant execute on function public.exam_get(bigint) to authenticated;

-- 제출 (브라우저가 채점한 통과 개수를 보내요. 시험 시간 안에서만 받아요)
create or replace function public.exam_submit(p_problem bigint, p_code text, p_passed int, p_total int) returns jsonb
language plpgsql security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); p public.exam_problems; e public.exams; v_n int;
begin
  if v_me is null or not public.py_is_student(v_me) then return jsonb_build_object('status', 'nouser'); end if;
  select * into p from public.exam_problems where id = p_problem;
  if not found then return jsonb_build_object('status', 'nouser'); end if;
  select * into e from public.exams where id = p.exam_id and status = 'open';
  if not found or not exists (select 1 from public.exam_entries where exam_id = e.id and user_id = v_me) then return jsonb_build_object('status', 'nouser'); end if;
  if now() < e.start_at then return jsonb_build_object('status', 'early'); end if;
  if now() >= public.exam_end(e) + interval '15 seconds' then return jsonb_build_object('status', 'closed'); end if;
  select count(*) into v_n from public.exam_subs where exam_id = e.id and user_id = v_me;
  if v_n >= 400 then return jsonb_build_object('status', 'limit'); end if;
  p_total := least(greatest(coalesce(p_total, 0), 0), jsonb_array_length(p.tests));
  p_passed := least(greatest(coalesce(p_passed, 0), 0), p_total);
  insert into public.exam_subs (exam_id, problem_id, user_id, code, passed, total) values (e.id, p.id, v_me, left(coalesce(p_code, ''), 20000), p_passed, p_total);
  return jsonb_build_object('status', 'ok', 'passed', p_passed, 'total', p_total);
end $$;
revoke all on function public.exam_submit(bigint, text, int, int) from public, anon;
grant execute on function public.exam_submit(bigint, text, int, int) to authenticated;

-- 정산: 끝난 뒤 처음 부르는 사람이 한 번만 실행돼요 (점수 → 순위 → 보상)
create or replace function public.exam_settle(p_id bigint) returns text
language plpgsql security definer set search_path = public
as $$
declare e public.exams; r record; v_pts jsonb; v_pt int; v_item text; v_has boolean; v_total int; v_rw text;
begin
  if auth.uid() is null or not public.is_approved() then return 'nouser'; end if;
  select * into e from public.exams where id = p_id and status = 'open' for update;
  if not found then return 'nouser'; end if;
  if e.settled_at is not null then return 'done'; end if;
  if now() < public.exam_end(e) + interval '20 seconds' then return 'wait'; end if;
  insert into public.exam_results (exam_id, user_id, score, solved, last_at, final_rank)
  select e.id, s.user_id, s.score, s.solved, s.last_at, row_number() over (order by s.score desc, s.last_at asc nulls last, s.user_id)
    from (
      select x.user_id,
             coalesce(sum(b.sc), 0)::int as score,
             coalesce(sum((b.full)::int), 0)::int as solved,
             max(b.at) as last_at
        from public.exam_entries x
        join public.profiles pr on pr.id = x.user_id
        left join lateral (
          select p.id,
                 max(case when s.total > 0 then (p.points * s.passed) / s.total else 0 end) as sc,
                 bool_or(s.total > 0 and s.passed = s.total) as full,
                 (select min(s2.created_at) from public.exam_subs s2 where s2.problem_id = p.id and s2.user_id = x.user_id
                    and (case when s2.total > 0 then (p.points * s2.passed) / s2.total else 0 end) =
                        max(case when s.total > 0 then (p.points * s.passed) / s.total else 0 end)) as at
            from public.exam_problems p
            join public.exam_subs s on s.problem_id = p.id and s.user_id = x.user_id
           where p.exam_id = e.id
           group by p.id
        ) b on true
       where x.exam_id = e.id and public.py_is_student(x.user_id)
       group by x.user_id
    ) s
  on conflict do nothing;
  v_pts := coalesce(e.reward -> 'pt_rank', '[]'::jsonb);
  for r in select * from public.exam_results where exam_id = e.id order by final_rank loop
    v_pt := coalesce((e.reward ->> 'pt_join')::int, 0);
    if r.final_rank <= jsonb_array_length(v_pts) then v_pt := v_pt + coalesce((v_pts ->> (r.final_rank - 1))::int, 0); end if;
    if v_pt > 0 then perform public.py_add(r.user_id, v_pt, 'exam_rank', e.id::text, e.title || ' · ' || r.final_rank || '위'); end if;
    v_item := case when r.final_rank = 1 then e.reward ->> 'item_first' when r.final_rank <= 3 then e.reward ->> 'item_top3' else null end;
    if v_item is not null and exists (select 1 from public.avatar_items where id = v_item) then
      insert into public.avatar_inventory (user_id, item_id, source) values (r.user_id, v_item, 'exam') on conflict do nothing;
    end if;
    v_item := e.reward ->> 'item_join';
    if v_item is not null and exists (select 1 from public.avatar_items where id = v_item) then
      insert into public.avatar_inventory (user_id, item_id, source) values (r.user_id, v_item, 'exam') on conflict do nothing;
    end if;
    perform public.py_notify(r.user_id, '📝 시험 결과: ' || e.title, r.final_rank || '위 · ' || r.score || '점' || case when v_pt > 0 then ' · 💎 +' || v_pt else '' end, 'exam', '#/exam/' || e.id);
  end loop;
  update public.exams set settled_at = now() where id = e.id;
  return 'ok';
end $$;
revoke all on function public.exam_settle(bigint) from public, anon;
grant execute on function public.exam_settle(bigint) to authenticated;

-- 순위표 (공개를 꺼 둔 학생은 이름 대신 "비공개". 내 줄과 관리자에게는 이름이 보여요)
create or replace function public.exam_board(p_id bigint) returns jsonb
language plpgsql security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); v_adm boolean := coalesce(public.staff_role(), '') in ('owner', 'admin'); e public.exams;
begin
  if v_me is null or not public.is_approved() then return null; end if;
  select * into e from public.exams where id = p_id and (status = 'open' or v_adm);
  if not found then return null; end if;
  if e.settled_at is null and now() >= public.exam_end(e) + interval '20 seconds' then perform public.exam_settle(p_id); end if;
  if not exists (select 1 from public.exams where id = p_id and settled_at is not null) then return jsonb_build_object('ready', false); end if;
  return jsonb_build_object('ready', true, 'n', (select count(*) from public.exam_results where exam_id = p_id),
    'rows', coalesce((select jsonb_agg(jsonb_build_object('rank', r.final_rank, 'score', r.score, 'solved', r.solved,
        'uid', case when r.user_id = v_me or v_adm or coalesce(x.public, true) then r.user_id end,
        'name', case when r.user_id = v_me or v_adm or coalesce(x.public, true) then public.disp(r.user_id) end,
        'hidden', not coalesce(x.public, true), 'me', r.user_id = v_me) order by r.final_rank)
      from public.exam_results r left join public.exam_entries x on x.exam_id = r.exam_id and x.user_id = r.user_id where r.exam_id = p_id), '[]'::jsonb));
end $$;
revoke all on function public.exam_board(bigint) from public, anon;
grant execute on function public.exam_board(bigint) to authenticated;

create or replace function public.exam_set_public(p_id bigint, p_on boolean) returns text
language plpgsql security definer set search_path = public
as $$
begin
  update public.exam_entries set public = coalesce(p_on, true) where exam_id = p_id and user_id = auth.uid();
  return case when found then 'ok' else 'nouser' end;
end $$;
revoke all on function public.exam_set_public(bigint, boolean) from public, anon;
grant execute on function public.exam_set_public(bigint, boolean) to authenticated;

-- 내 제출 코드/점수 (끝난 뒤 복기용: 문제별 최고 점수)
create or replace function public.exam_review(p_id bigint) returns jsonb
language sql stable security definer set search_path = public
as $$
  select coalesce(jsonb_agg(jsonb_build_object('problem_id', p.id, 'title', p.title, 'points', p.points,
      'score', coalesce((select max(case when s.total > 0 then (p.points * s.passed) / s.total else 0 end) from public.exam_subs s where s.problem_id = p.id and s.user_id = auth.uid()), 0),
      'code', (select s.code from public.exam_subs s where s.problem_id = p.id and s.user_id = auth.uid() order by (case when s.total > 0 then (p.points * s.passed) / s.total else 0 end) desc, s.id desc limit 1)) order by p.position, p.id), '[]'::jsonb)
    from public.exam_problems p join public.exams e on e.id = p.exam_id
   where p.exam_id = p_id and e.status = 'open' and now() >= public.exam_end(e)
$$;
revoke all on function public.exam_review(bigint) from public, anon;
grant execute on function public.exam_review(bigint) to authenticated;

-- 관리자: 시험 만들기/고치기 (문제까지 한 번에) · 지우기 · 바로 정산
create or replace function public.exam_save(p jsonb) returns jsonb
language plpgsql security definer set search_path = public
as $$
declare v_id bigint := nullif(p ->> 'id', '')::bigint; e public.exams; q jsonb; i int := 0;
begin
  if coalesce(public.staff_role(), '') not in ('owner', 'admin') then return jsonb_build_object('status', 'forbidden'); end if;
  if v_id is null then
    insert into public.exams (title, descr, start_at, duration_min, entry_min, status, reward, created_by)
    values (left(p ->> 'title', 60), coalesce(p ->> 'descr', ''), (p ->> 'start_at')::timestamptz, coalesce((p ->> 'duration_min')::int, 60), coalesce((p ->> 'entry_min')::int, 60),
            coalesce(p ->> 'status', 'draft'), coalesce(p -> 'reward', '{}'::jsonb), auth.uid())
    returning id into v_id;
  else
    select * into e from public.exams where id = v_id;
    if not found then return jsonb_build_object('status', 'nouser'); end if;
    if e.settled_at is not null then return jsonb_build_object('status', 'settled'); end if;
    if now() >= e.start_at and exists (select 1 from public.exam_entries where exam_id = v_id) and p ? 'problems' then return jsonb_build_object('status', 'started'); end if;
    update public.exams set title = left(p ->> 'title', 60), descr = coalesce(p ->> 'descr', ''), start_at = (p ->> 'start_at')::timestamptz,
      duration_min = coalesce((p ->> 'duration_min')::int, 60), entry_min = coalesce((p ->> 'entry_min')::int, 60),
      status = coalesce(p ->> 'status', 'draft'), reward = coalesce(p -> 'reward', reward) where id = v_id;
  end if;
  if p ? 'problems' then
    delete from public.exam_problems where exam_id = v_id;
    for q in select * from jsonb_array_elements(p -> 'problems') loop
      i := i + 1;
      insert into public.exam_problems (exam_id, position, title, body, points, tests)
      values (v_id, i, left(coalesce(q ->> 'title', ''), 100), coalesce(q ->> 'body', ''), coalesce((q ->> 'points')::int, 100), coalesce(q -> 'tests', '[]'::jsonb));
    end loop;
  end if;
  return jsonb_build_object('status', 'ok', 'id', v_id);
exception when others then return jsonb_build_object('status', 'invalid', 'msg', sqlerrm);
end $$;
revoke all on function public.exam_save(jsonb) from public, anon;
grant execute on function public.exam_save(jsonb) to authenticated;

create or replace function public.exam_delete(p_id bigint) returns text
language plpgsql security definer set search_path = public
as $$
begin
  if coalesce(public.staff_role(), '') not in ('owner', 'admin') then return 'forbidden'; end if;
  delete from public.exams where id = p_id;
  return 'ok';
end $$;
revoke all on function public.exam_delete(bigint) from public, anon;
grant execute on function public.exam_delete(bigint) to authenticated;

-- 관리자: 시험 문제 전체 (편집용, 채점 테스트 포함)
create or replace function public.exam_admin_get(p_id bigint) returns jsonb
language plpgsql stable security definer set search_path = public
as $$
declare e public.exams;
begin
  if coalesce(public.staff_role(), '') not in ('owner', 'admin') then return null; end if;
  select * into e from public.exams where id = p_id;
  if not found then return null; end if;
  return jsonb_build_object('id', e.id, 'title', e.title, 'descr', e.descr, 'start_at', e.start_at, 'duration_min', e.duration_min, 'entry_min', e.entry_min,
    'status', e.status, 'reward', e.reward, 'settled', e.settled_at is not null,
    'problems', coalesce((select jsonb_agg(jsonb_build_object('title', p.title, 'body', p.body, 'points', p.points, 'tests', p.tests) order by p.position, p.id) from public.exam_problems p where p.exam_id = p_id), '[]'::jsonb));
end $$;
revoke all on function public.exam_admin_get(bigint) from public, anon;
grant execute on function public.exam_admin_get(bigint) to authenticated;

-- 3) 시험 풍선 장식 (시험 보상 기본값)
insert into public.avatar_items (id, name, descr, slot, svg, kind, val, price, builtin) values
 ('exam_balloon_gold', '금빛 풍선', '시험 1등 보상', 'deco',
  $svg$<path d="M86 14 C77 14 75 28 86 36 C97 28 95 14 86 14Z" fill="#fbbf24" stroke="#d97706" stroke-width="1.2"/><path d="M86 36 L84 40 H88Z" fill="#d97706"/><path d="M86 40 C83 47 89 52 86 60" fill="none" stroke="#94a3b8" stroke-width="1"/><path d="M81 19 C80 23 81 26 83 28" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="1.4" stroke-linecap="round"/>$svg$, 'reward', 0, 0, true),
 ('exam_balloon_silver', '은빛 풍선', '시험 3등 안 보상', 'deco',
  $svg$<path d="M86 14 C77 14 75 28 86 36 C97 28 95 14 86 14Z" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.2"/><path d="M86 36 L84 40 H88Z" fill="#94a3b8"/><path d="M86 40 C83 47 89 52 86 60" fill="none" stroke="#94a3b8" stroke-width="1"/><path d="M81 19 C80 23 81 26 83 28" fill="none" stroke="#fff" stroke-opacity=".8" stroke-width="1.4" stroke-linecap="round"/>$svg$, 'reward', 0, 0, true),
 ('exam_balloon_blue', '파란 풍선', '시험에 참가한 기념', 'deco',
  $svg$<path d="M86 14 C77 14 75 28 86 36 C97 28 95 14 86 14Z" fill="#60a5fa" stroke="#2563eb" stroke-width="1.2"/><path d="M86 36 L84 40 H88Z" fill="#2563eb"/><path d="M86 40 C83 47 89 52 86 60" fill="none" stroke="#94a3b8" stroke-width="1"/><path d="M81 19 C80 23 81 26 83 28" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="1.4" stroke-linecap="round"/>$svg$, 'reward', 0, 0, true)
on conflict (id) do nothing;

grant execute on function public.market_submit(jsonb) to authenticated;
