-- 5.7.0 시험 유형: 정기 시험(regular) / 자유 응시(free)
--  · 정기: 정해진 시각에 모두 같이 시작해 같은 시각에 끝나요 (기존 방식 그대로)
--  · 자유: [start_at ~ close_at] 기간 안에 언제든 입장하고, 입장한 순간부터 duration_min 분 동안 풀어요 (개인 타이머)
alter table public.exams add column if not exists kind text not null default 'regular';
alter table public.exams add column if not exists close_at timestamptz;
alter table public.exams drop constraint if exists exams_kind_check;
alter table public.exams add constraint exams_kind_check check (kind in ('regular', 'free'));

-- 시험 전체가 끝나는 시각 (정기: 시작+시간 / 자유: 응시 마감+시간 = 마지막 사람이 끝나는 시각)
create or replace function public.exam_end(e public.exams) returns timestamptz
language sql immutable as $$
  select case when e.kind = 'free' then coalesce(e.close_at, e.start_at) else e.start_at end + make_interval(mins => e.duration_min)
$$;

-- 이 사람의 시험 끝 시각 (정기: 모두 같음 / 자유: 입장한 시각 + 시간)
create or replace function public.exam_my_end(e public.exams, p_user uuid) returns timestamptz
language sql stable security definer set search_path = public as $$
  select case when e.kind = 'free'
              then (select x.joined_at + make_interval(mins => e.duration_min) from public.exam_entries x where x.exam_id = e.id and x.user_id = p_user)
              else public.exam_end(e) end
$$;
revoke all on function public.exam_my_end(public.exams, uuid) from public, anon;
grant execute on function public.exam_my_end(public.exams, uuid) to authenticated;

create or replace function public.exam_list() returns jsonb
language plpgsql stable security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); v_adm boolean := public.exam_staff();
begin
  if v_me is null or not public.is_approved() then return null; end if;
  return jsonb_build_object('now', now(), 'staff', v_adm, 'exams', coalesce((select jsonb_agg(jsonb_build_object(
      'id', e.id, 'title', e.title, 'descr', e.descr, 'start_at', e.start_at, 'end_at', public.exam_end(e), 'duration_min', e.duration_min,
      'kind', e.kind, 'close_at', e.close_at,
      'my_start', (select x.joined_at from public.exam_entries x where x.exam_id = e.id and x.user_id = v_me),
      'my_end', case when e.kind = 'free' then public.exam_my_end(e, v_me) end,
      'entry_min', e.entry_min, 'status', e.status, 'settled', e.settled_at is not null, 'reward', e.reward, 'finalized', e.finalized,
      'n_problems', (select count(*) from public.exam_problems p where p.exam_id = e.id),
      'n_essay', (select count(*) from public.exam_problems p where p.exam_id = e.id and p.kind = 'essay'),
      'n_entries', (select count(*) from public.exam_entries x where x.exam_id = e.id),
      'entered', exists (select 1 from public.exam_entries x where x.exam_id = e.id and x.user_id = v_me),
      'my_rank', (select r.final_rank from public.exam_results r where r.exam_id = e.id and r.user_id = v_me),
      'my_score', (select r.score from public.exam_results r where r.exam_id = e.id and r.user_id = v_me)) order by e.start_at desc)
    from public.exams e where e.status = 'open' or v_adm), '[]'::jsonb));
end $$;

create or replace function public.exam_enter(p_id bigint) returns text
language plpgsql security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); e public.exams;
begin
  if v_me is null or not public.py_is_student(v_me) then return 'nouser'; end if;
  select * into e from public.exams where id = p_id and status = 'open';
  if not found then return 'nouser'; end if;
  if exists (select 1 from public.exam_entries where exam_id = p_id and user_id = v_me) then return 'ok'; end if;
  if e.kind = 'free' then
    if now() < e.start_at then return 'early'; end if;
    if now() >= coalesce(e.close_at, e.start_at) then return 'closed'; end if;
  else
    if now() < e.start_at - make_interval(mins => e.entry_min) then return 'early'; end if;
    if now() >= public.exam_end(e) then return 'closed'; end if;
  end if;
  insert into public.exam_entries (exam_id, user_id) values (p_id, v_me) on conflict do nothing;
  return 'ok';
end $$;

create or replace function public.exam_get(p_id bigint) returns jsonb
language plpgsql stable security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); e public.exams; v_adm boolean := public.exam_staff();
        v_in boolean; v_live boolean; v_over boolean; v_probs jsonb; v_np int; v_cur int; v_ent timestamptz; v_myend timestamptz;
begin
  if v_me is null or not public.is_approved() then return null; end if;
  select * into e from public.exams where id = p_id and (status = 'open' or v_adm);
  if not found then return null; end if;
  v_in := exists (select 1 from public.exam_entries where exam_id = p_id and user_id = v_me);
  if e.kind = 'free' then
    select x.joined_at into v_ent from public.exam_entries x where x.exam_id = p_id and x.user_id = v_me;
    v_myend := case when v_ent is not null then v_ent + make_interval(mins => e.duration_min) end;
    v_live := case when v_adm then now() >= e.start_at and now() < public.exam_end(e) + interval '20 seconds'
                   else v_ent is not null and now() < v_myend + interval '20 seconds' end;
  else
    v_live := now() >= e.start_at and now() < public.exam_end(e) + interval '20 seconds';
  end if;
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
    'kind', e.kind, 'close_at', e.close_at, 'my_start', v_ent, 'my_end', v_myend,
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

create or replace function public.exam_part_close(p_id bigint, p_part int) returns text
language plpgsql security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); e public.exams; v_cur int; v_max int;
begin
  if v_me is null or not public.py_is_student(v_me) then return 'nouser'; end if;
  select * into e from public.exams where id = p_id and status = 'open';
  if not found or not exists (select 1 from public.exam_entries where exam_id = e.id and user_id = v_me) then return 'nouser'; end if;
  if now() < e.start_at then return 'early'; end if;
  if now() >= public.exam_my_end(e, v_me) + interval '15 seconds' then return 'closed'; end if;
  if jsonb_array_length(e.parts) = 0 then return 'noparts'; end if;
  v_cur := public.exam_cur_part(e.id, v_me);
  if p_part is distinct from v_cur then return 'order'; end if;
  select max((x ->> 'n')::int) into v_max from jsonb_array_elements(e.parts) x;
  if v_cur >= v_max then return 'last'; end if;
  insert into public.exam_parts_done (exam_id, user_id, part) values (e.id, v_me, v_cur) on conflict do nothing;
  return 'ok';
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
  if now() >= public.exam_my_end(e, v_me) + interval '15 seconds' then return jsonb_build_object('status', 'closed'); end if;
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

create or replace function public.exam_save(p jsonb) returns jsonb
language plpgsql security definer set search_path = public
as $$
declare v_id bigint := nullif(p ->> 'id', '')::bigint; e public.exams; q jsonb; i int := 0; v_pid bigint; v_keep bigint[] := '{}';
        v_kind text := case when p ->> 'kind' = 'free' then 'free' else 'regular' end;
        v_close timestamptz := case when p ->> 'kind' = 'free' then nullif(p ->> 'close_at', '')::timestamptz end;
begin
  if not public.exam_staff() then return jsonb_build_object('status', 'forbidden'); end if;
  if v_kind = 'free' and (v_close is null or v_close <= (p ->> 'start_at')::timestamptz) then return jsonb_build_object('status', 'invalid', 'msg', '응시 마감은 시작보다 뒤여야 해요'); end if;
  if v_id is null then
    insert into public.exams (title, descr, start_at, duration_min, entry_min, status, reward, parts, kind, close_at, created_by)
    values (left(p ->> 'title', 60), coalesce(p ->> 'descr', ''), (p ->> 'start_at')::timestamptz, coalesce((p ->> 'duration_min')::int, 60), coalesce((p ->> 'entry_min')::int, 60),
            coalesce(p ->> 'status', 'draft'), coalesce(p -> 'reward', '{}'::jsonb), coalesce(p -> 'parts', '[]'::jsonb), v_kind, v_close, auth.uid())
    returning id into v_id;
  else
    select * into e from public.exams where id = v_id;
    if not found then return jsonb_build_object('status', 'nouser'); end if;
    if e.settled_at is not null then return jsonb_build_object('status', 'settled'); end if;
    update public.exams set title = left(p ->> 'title', 60), descr = coalesce(p ->> 'descr', ''), start_at = (p ->> 'start_at')::timestamptz,
      duration_min = coalesce((p ->> 'duration_min')::int, 60), entry_min = coalesce((p ->> 'entry_min')::int, 60), kind = v_kind, close_at = v_close,
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
    'kind', e.kind, 'close_at', e.close_at,
    'status', e.status, 'reward', e.reward, 'parts', e.parts, 'settled', e.settled_at is not null, 'finalized', e.finalized, 'n_entries', (select count(*) from public.exam_entries where exam_id = e.id),
    'problems', coalesce((select jsonb_agg(jsonb_build_object('id', p.id, 'title', p.title, 'body', p.body, 'points', p.points, 'tests', p.tests, 'kind', p.kind, 'rubric', p.rubric, 'part', p.part, 'starter', p.starter) order by p.position, p.id) from public.exam_problems p where p.exam_id = p_id), '[]'::jsonb));
end $$;
