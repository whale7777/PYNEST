-- v5.5.1 시험: 구간(잠금) + 객관식(mc) + 오류 고치기(fix) — Supabase SQL 편집기에서 한 번 실행하세요. (여러 번 실행해도 안전해요)
--  · 구간: 시험을 구간으로 나눠요. 구간을 마감해야 다음 구간 문제가 열리고, 마감한 구간으로는 돌아갈 수 없어요. (exams.parts, exam_problems.part)
--    exams.parts 예) [{"n":1,"name":"추론·빈칸","run":false},{"n":2,"name":"코딩","run":true}]  — run 은 ▶ 실행 허용 여부. 비어 있으면 예전처럼 구간 없이 진행해요.
--  · 객관식 mc : tests = [{"options":["보기1","보기2",…],"answer":[1],"multi":false}]  (answer 는 0부터 센 번호, 모두 맞아야 정답)
--  · 오류 고치기 fix : 코드 문제와 같은 채점 테스트 + starter(처음 보이는 틀린 코드)

alter table public.exam_problems drop constraint if exists exam_problems_kind_check;
alter table public.exam_problems add constraint exam_problems_kind_check check (kind in ('code', 'essay', 'short', 'mc', 'fix'));
alter table public.exam_problems add column if not exists part int not null default 1 check (part between 1 and 20);
alter table public.exam_problems add column if not exists starter text not null default '' check (length(starter) <= 20000);
alter table public.exams add column if not exists parts jsonb not null default '[]'::jsonb;

create table if not exists public.exam_parts_done (
  exam_id bigint not null references public.exams(id) on delete cascade,
  user_id uuid not null references public.profiles(id) on delete cascade,
  part int not null,
  done_at timestamptz not null default now(),
  primary key (exam_id, user_id, part)
);
alter table public.exam_parts_done enable row level security;
-- 정책 없음: 함수(security definer)로만 읽고 써요

-- 지금 열려 있는 구간 번호 (구간이 없으면 null)
create or replace function public.exam_cur_part(p_exam bigint, p_user uuid) returns int
language sql stable security definer set search_path = public
as $$
  select min((x ->> 'n')::int)
    from public.exams e, jsonb_array_elements(e.parts) x
   where e.id = p_exam
     and not exists (select 1 from public.exam_parts_done d where d.exam_id = e.id and d.user_id = p_user and d.part = (x ->> 'n')::int)
$$;

create or replace function public.exam_get(p_id bigint) returns jsonb
language plpgsql stable security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); e public.exams; v_adm boolean := public.exam_staff();
        v_in boolean; v_live boolean; v_over boolean; v_probs jsonb; v_np int; v_cur int;
begin
  if v_me is null or not public.is_approved() then return null; end if;
  select * into e from public.exams where id = p_id and (status = 'open' or v_adm);
  if not found then return null; end if;
  v_in := exists (select 1 from public.exam_entries where exam_id = p_id and user_id = v_me);
  v_live := now() >= e.start_at and now() < public.exam_end(e) + interval '20 seconds';
  v_over := now() >= public.exam_end(e);
  v_np := jsonb_array_length(e.parts);
  v_cur := case when v_np > 0 then public.exam_cur_part(p_id, v_me) else null end;
  if (v_live and (v_in or v_adm)) then
    select coalesce(jsonb_agg(
        case
          when v_adm or v_np = 0 or p.part = v_cur then
            jsonb_build_object('id', p.id, 'position', p.position, 'title', p.title, 'body', p.body, 'points', p.points, 'kind', p.kind, 'part', p.part, 'starter', p.starter,
              'tests', case when p.kind in ('code', 'short', 'mc', 'fix') then p.tests else '[]'::jsonb end)
          when p.part < v_cur then
            jsonb_build_object('id', p.id, 'position', p.position, 'title', p.title, 'body', p.body, 'points', p.points, 'kind', p.kind, 'part', p.part, 'closed', true, 'tests', '[]'::jsonb)
          else
            jsonb_build_object('id', p.id, 'position', p.position, 'title', '', 'body', '', 'points', p.points, 'kind', p.kind, 'part', p.part, 'locked', true, 'tests', '[]'::jsonb)
        end order by p.position, p.id), '[]'::jsonb)
      into v_probs from public.exam_problems p where p.exam_id = p_id;
  elsif v_over and (v_in or v_adm) then
    select coalesce(jsonb_agg(jsonb_build_object('id', p.id, 'position', p.position, 'title', p.title, 'body', p.body, 'points', p.points, 'kind', p.kind, 'part', p.part) order by p.position, p.id), '[]'::jsonb)
      into v_probs from public.exam_problems p where p.exam_id = p_id;
  else
    v_probs := '[]'::jsonb;
  end if;
  return jsonb_build_object('now', now(), 'id', e.id, 'title', e.title, 'descr', e.descr, 'start_at', e.start_at, 'end_at', public.exam_end(e), 'duration_min', e.duration_min,
    'entry_min', e.entry_min, 'status', e.status, 'settled', e.settled_at is not null, 'finalized', e.finalized, 'rev', e.rev, 'reward', e.reward, 'entered', v_in, 'staff', v_adm,
    'parts', e.parts, 'cur_part', case when v_adm then null else v_cur end,
    'public', (select x.public from public.exam_entries x where x.exam_id = p_id and x.user_id = v_me),
    'n_problems', (select count(*) from public.exam_problems where exam_id = p_id),
    'n_essay', (select count(*) from public.exam_problems where exam_id = p_id and kind = 'essay'),
    'n_entries', (select count(*) from public.exam_entries where exam_id = p_id),
    'problems', v_probs,
    'mine', coalesce((select jsonb_object_agg(q.problem_id, jsonb_build_object('passed', q.passed, 'total', q.total, 'code', q.code))
        from (select distinct on (s.problem_id) s.problem_id, s.passed, s.total, s.code from public.exam_subs s
               where s.exam_id = p_id and s.user_id = v_me order by s.problem_id, s.id desc) q), '{}'::jsonb));
end $$;

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
  if jsonb_array_length(e.parts) > 0 and p.part is distinct from public.exam_cur_part(e.id, v_me) then return jsonb_build_object('status', 'partlocked'); end if;
  select count(*) into v_n from public.exam_subs where exam_id = e.id and user_id = v_me;
  if v_n >= 400 then return jsonb_build_object('status', 'limit'); end if;
  if p.kind = 'essay' then p_total := 0; p_passed := 0;
  else
    p_total := least(greatest(coalesce(p_total, 0), 0), jsonb_array_length(p.tests));
    p_passed := least(greatest(coalesce(p_passed, 0), 0), p_total);
  end if;
  insert into public.exam_subs (exam_id, problem_id, user_id, code, passed, total) values (e.id, p.id, v_me, left(coalesce(p_code, ''), 20000), p_passed, p_total);
  return jsonb_build_object('status', 'ok', 'passed', p_passed, 'total', p_total);
end $$;

-- 구간 마감: 지금 열린 구간을 닫고 다음 구간을 열어요 (마지막 구간은 마감할 필요 없어요)
create or replace function public.exam_part_close(p_id bigint, p_part int) returns text
language plpgsql security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); e public.exams; v_cur int; v_max int;
begin
  if v_me is null or not public.py_is_student(v_me) then return 'nouser'; end if;
  select * into e from public.exams where id = p_id and status = 'open';
  if not found or not exists (select 1 from public.exam_entries where exam_id = e.id and user_id = v_me) then return 'nouser'; end if;
  if now() < e.start_at then return 'early'; end if;
  if now() >= public.exam_end(e) + interval '15 seconds' then return 'closed'; end if;
  if jsonb_array_length(e.parts) = 0 then return 'noparts'; end if;
  v_cur := public.exam_cur_part(e.id, v_me);
  if p_part is distinct from v_cur then return 'order'; end if;
  select max((x ->> 'n')::int) into v_max from jsonb_array_elements(e.parts) x;
  if v_cur >= v_max then return 'last'; end if;
  insert into public.exam_parts_done (exam_id, user_id, part) values (e.id, v_me, v_cur) on conflict do nothing;
  return 'ok';
end $$;
revoke all on function public.exam_part_close(bigint, int) from public, anon;
grant execute on function public.exam_part_close(bigint, int) to authenticated;
revoke all on function public.exam_cur_part(bigint, uuid) from public, anon;

create or replace function public.exam_save(p jsonb) returns jsonb
language plpgsql security definer set search_path = public
as $$
declare v_id bigint := nullif(p ->> 'id', '')::bigint; e public.exams; q jsonb; i int := 0; v_pid bigint; v_keep bigint[] := '{}';
begin
  if not public.exam_staff() then return jsonb_build_object('status', 'forbidden'); end if;
  if v_id is null then
    insert into public.exams (title, descr, start_at, duration_min, entry_min, status, reward, parts, created_by)
    values (left(p ->> 'title', 60), coalesce(p ->> 'descr', ''), (p ->> 'start_at')::timestamptz, coalesce((p ->> 'duration_min')::int, 60), coalesce((p ->> 'entry_min')::int, 60),
            coalesce(p ->> 'status', 'draft'), coalesce(p -> 'reward', '{}'::jsonb), coalesce(p -> 'parts', '[]'::jsonb), auth.uid())
    returning id into v_id;
  else
    select * into e from public.exams where id = v_id;
    if not found then return jsonb_build_object('status', 'nouser'); end if;
    if e.settled_at is not null then return jsonb_build_object('status', 'settled'); end if;
    update public.exams set title = left(p ->> 'title', 60), descr = coalesce(p ->> 'descr', ''), start_at = (p ->> 'start_at')::timestamptz,
      duration_min = coalesce((p ->> 'duration_min')::int, 60), entry_min = coalesce((p ->> 'entry_min')::int, 60),
      status = coalesce(p ->> 'status', 'draft'), reward = coalesce(p -> 'reward', reward), parts = coalesce(p -> 'parts', parts), rev = rev + 1 where id = v_id;
  end if;
  if p ? 'problems' then
    for q in select * from jsonb_array_elements(p -> 'problems') loop
      i := i + 1;
      v_pid := nullif(q ->> 'id', '')::bigint;
      if v_pid is not null and exists (select 1 from public.exam_problems where id = v_pid and exam_id = v_id) then
        update public.exam_problems set position = i, title = left(coalesce(q ->> 'title', ''), 100), body = coalesce(q ->> 'body', ''),
          points = coalesce((q ->> 'points')::int, 100), tests = coalesce(q -> 'tests', '[]'::jsonb),
          kind = coalesce(nullif(q ->> 'kind', ''), 'code'), rubric = left(coalesce(q ->> 'rubric', ''), 5000),
          part = coalesce((q ->> 'part')::int, 1), starter = left(coalesce(q ->> 'starter', ''), 20000) where id = v_pid;
      else
        insert into public.exam_problems (exam_id, position, title, body, points, tests, kind, rubric, part, starter)
        values (v_id, i, left(coalesce(q ->> 'title', ''), 100), coalesce(q ->> 'body', ''), coalesce((q ->> 'points')::int, 100), coalesce(q -> 'tests', '[]'::jsonb),
               coalesce(nullif(q ->> 'kind', ''), 'code'), left(coalesce(q ->> 'rubric', ''), 5000), coalesce((q ->> 'part')::int, 1), left(coalesce(q ->> 'starter', ''), 20000)) returning id into v_pid;
      end if;
      v_keep := v_keep || v_pid;
    end loop;
    delete from public.exam_problems where exam_id = v_id and not (id = any (v_keep));
  end if;
  return jsonb_build_object('status', 'ok', 'id', v_id);
exception when others then return jsonb_build_object('status', 'invalid', 'msg', sqlerrm);
end $$;

create or replace function public.exam_admin_get(p_id bigint) returns jsonb
language plpgsql stable security definer set search_path = public
as $$
declare e public.exams;
begin
  if not public.exam_staff() then return null; end if;
  select * into e from public.exams where id = p_id;
  if not found then return null; end if;
  return jsonb_build_object('id', e.id, 'title', e.title, 'descr', e.descr, 'start_at', e.start_at, 'duration_min', e.duration_min, 'entry_min', e.entry_min,
    'status', e.status, 'reward', e.reward, 'parts', e.parts, 'settled', e.settled_at is not null, 'finalized', e.finalized, 'n_entries', (select count(*) from public.exam_entries where exam_id = e.id),
    'problems', coalesce((select jsonb_agg(jsonb_build_object('id', p.id, 'title', p.title, 'body', p.body, 'points', p.points, 'tests', p.tests, 'kind', p.kind, 'rubric', p.rubric, 'part', p.part, 'starter', p.starter) order by p.position, p.id) from public.exam_problems p where p.exam_id = p_id), '[]'::jsonb));
end $$;
