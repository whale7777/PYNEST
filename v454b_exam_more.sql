-- PyNest V4.5.4b · v454b_exam_more.sql
-- 시험 보강: ① 선생님(teacher) 계정도 시험 만들기·채점  ② ✍️ 서술형 문제(선생님이 직접 채점)
-- ③ 시험 중에도 문제 수정 (제출 기록은 유지) + 응시자 화면에 자동 반영  ④ 📣 시험 알림 보내기
-- v454_exam.sql 다음에 한 번만 실행하세요. (여러 번 실행해도 안전해요)

do $$
begin
  if to_regclass('public.exams') is null or to_regclass('public.exam_results') is null then
    raise exception 'v454_exam.sql 을 먼저 실행해주세요.';
  end if;
end $$;

-- 0) 시험 관리 권한: OWNER · ADMIN · TEACHER (문제 관리 권한이 있는 직원)
create or replace function public.exam_staff() returns boolean
language sql stable security definer set search_path = public
as $$ select coalesce(public.staff_can('content'::text), false) $$;
grant execute on function public.exam_staff() to authenticated;

alter table public.exam_problems add column if not exists kind text not null default 'code' check (kind in ('code', 'essay'));
alter table public.exam_problems add column if not exists rubric text not null default '' check (length(rubric) <= 5000);
alter table public.exams add column if not exists rev int not null default 1;
alter table public.exams add column if not exists finalized boolean not null default false;

create table if not exists public.exam_grades (
  exam_id bigint not null references public.exams(id) on delete cascade,
  problem_id bigint not null references public.exam_problems(id) on delete cascade,
  user_id uuid not null references public.profiles(id) on delete cascade,
  score int not null check (score >= 0),
  graded_by uuid,
  graded_at timestamptz not null default now(),
  primary key (problem_id, user_id)
);
alter table public.exam_grades enable row level security;
revoke all on public.exam_grades from anon, authenticated;
grant select on public.exam_grades to authenticated;
drop policy if exists exam_grades_read on public.exam_grades;
create policy exam_grades_read on public.exam_grades for select to authenticated using (user_id = auth.uid() or public.exam_staff());

drop policy if exists exams_read on public.exams;
create policy exams_read on public.exams for select to authenticated using (public.is_approved() and (status = 'open' or public.exam_staff()));
drop policy if exists exam_problems_staff on public.exam_problems;
create policy exam_problems_staff on public.exam_problems for select to authenticated using (public.exam_staff());
drop policy if exists exam_entries_own on public.exam_entries;
create policy exam_entries_own on public.exam_entries for select to authenticated using (user_id = auth.uid() or public.exam_staff());
drop policy if exists exam_subs_own on public.exam_subs;
create policy exam_subs_own on public.exam_subs for select to authenticated using (user_id = auth.uid() or public.exam_staff());
drop policy if exists exam_results_own on public.exam_results;
create policy exam_results_own on public.exam_results for select to authenticated using (user_id = auth.uid() or public.exam_staff());

-- 1) 목록
create or replace function public.exam_list() returns jsonb
language plpgsql stable security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); v_adm boolean := public.exam_staff();
begin
  if v_me is null or not public.is_approved() then return null; end if;
  return jsonb_build_object('now', now(), 'staff', v_adm, 'exams', coalesce((select jsonb_agg(jsonb_build_object(
      'id', e.id, 'title', e.title, 'descr', e.descr, 'start_at', e.start_at, 'end_at', public.exam_end(e), 'duration_min', e.duration_min,
      'entry_min', e.entry_min, 'status', e.status, 'settled', e.settled_at is not null, 'reward', e.reward, 'finalized', e.finalized,
      'n_problems', (select count(*) from public.exam_problems p where p.exam_id = e.id),
      'n_essay', (select count(*) from public.exam_problems p where p.exam_id = e.id and p.kind = 'essay'),
      'n_entries', (select count(*) from public.exam_entries x where x.exam_id = e.id),
      'entered', exists (select 1 from public.exam_entries x where x.exam_id = e.id and x.user_id = v_me),
      'my_rank', (select r.final_rank from public.exam_results r where r.exam_id = e.id and r.user_id = v_me),
      'my_score', (select r.score from public.exam_results r where r.exam_id = e.id and r.user_id = v_me)) order by e.start_at desc)
    from public.exams e where e.status = 'open' or v_adm), '[]'::jsonb));
end $$;

-- 2) 시험지 (rev: 선생님이 문제를 고치면 올라가요 → 응시 화면이 알아서 새로 불러와요)
create or replace function public.exam_get(p_id bigint) returns jsonb
language plpgsql stable security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); e public.exams; v_adm boolean := public.exam_staff();
        v_in boolean; v_live boolean; v_over boolean; v_probs jsonb;
begin
  if v_me is null or not public.is_approved() then return null; end if;
  select * into e from public.exams where id = p_id and (status = 'open' or v_adm);
  if not found then return null; end if;
  v_in := exists (select 1 from public.exam_entries where exam_id = p_id and user_id = v_me);
  v_live := now() >= e.start_at and now() < public.exam_end(e) + interval '20 seconds';
  v_over := now() >= public.exam_end(e);
  if (v_live and (v_in or v_adm)) then
    select coalesce(jsonb_agg(jsonb_build_object('id', p.id, 'position', p.position, 'title', p.title, 'body', p.body, 'points', p.points, 'kind', p.kind,
             'tests', case when p.kind = 'code' then p.tests else '[]'::jsonb end) order by p.position, p.id), '[]'::jsonb)
      into v_probs from public.exam_problems p where p.exam_id = p_id;
  elsif v_over and (v_in or v_adm) then
    select coalesce(jsonb_agg(jsonb_build_object('id', p.id, 'position', p.position, 'title', p.title, 'body', p.body, 'points', p.points, 'kind', p.kind) order by p.position, p.id), '[]'::jsonb)
      into v_probs from public.exam_problems p where p.exam_id = p_id;
  else
    v_probs := '[]'::jsonb;
  end if;
  return jsonb_build_object('now', now(), 'id', e.id, 'title', e.title, 'descr', e.descr, 'start_at', e.start_at, 'end_at', public.exam_end(e), 'duration_min', e.duration_min,
    'entry_min', e.entry_min, 'status', e.status, 'settled', e.settled_at is not null, 'finalized', e.finalized, 'rev', e.rev, 'reward', e.reward, 'entered', v_in, 'staff', v_adm,
    'public', (select x.public from public.exam_entries x where x.exam_id = p_id and x.user_id = v_me),
    'n_problems', (select count(*) from public.exam_problems where exam_id = p_id),
    'n_essay', (select count(*) from public.exam_problems where exam_id = p_id and kind = 'essay'),
    'n_entries', (select count(*) from public.exam_entries where exam_id = p_id),
    'problems', v_probs,
    'mine', coalesce((select jsonb_object_agg(q.problem_id, jsonb_build_object('passed', q.passed, 'total', q.total, 'code', q.code))
        from (select distinct on (s.problem_id) s.problem_id, s.passed, s.total, s.code from public.exam_subs s
               where s.exam_id = p_id and s.user_id = v_me order by s.problem_id, s.id desc) q), '{}'::jsonb));
end $$;

-- 가벼운 확인용: 문제가 바뀌었는지(rev)만
create or replace function public.exam_rev(p_id bigint) returns int
language sql stable security definer set search_path = public
as $$ select e.rev from public.exams e where e.id = p_id and (e.status = 'open' or public.exam_staff()) and public.is_approved() $$;
revoke all on function public.exam_rev(bigint) from public, anon;
grant execute on function public.exam_rev(bigint) to authenticated;

-- 3) 제출 (코드 문제: 통과 개수 / 서술형: 답안 글)
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
  if p.kind = 'essay' then p_total := 0; p_passed := 0;
  else
    p_total := least(greatest(coalesce(p_total, 0), 0), jsonb_array_length(p.tests));
    p_passed := least(greatest(coalesce(p_passed, 0), 0), p_total);
  end if;
  insert into public.exam_subs (exam_id, problem_id, user_id, code, passed, total) values (e.id, p.id, v_me, left(coalesce(p_code, ''), 20000), p_passed, p_total);
  return jsonb_build_object('status', 'ok', 'passed', p_passed, 'total', p_total);
end $$;

-- 4) 정산: 서술형이 있으면 선생님이 "채점 끝 · 정산"(exam_finalize)을 눌러야 해요
create or replace function public.exam_settle(p_id bigint) returns text
language plpgsql security definer set search_path = public
as $$
declare e public.exams; r record; v_pts jsonb; v_pt int; v_item text;
begin
  if auth.uid() is null or not public.is_approved() then return 'nouser'; end if;
  select * into e from public.exams where id = p_id and status = 'open' for update;
  if not found then return 'nouser'; end if;
  if e.settled_at is not null then return 'done'; end if;
  if now() < public.exam_end(e) + interval '20 seconds' then return 'wait'; end if;
  if not e.finalized and exists (select 1 from public.exam_problems where exam_id = e.id and kind = 'essay') then return 'grading'; end if;
  insert into public.exam_results (exam_id, user_id, score, solved, last_at, final_rank)
  select e.id, s.user_id, s.score, s.solved, s.last_at, row_number() over (order by s.score desc, s.last_at asc nulls last, s.user_id)
    from (
      select pp.user_id, coalesce(sum(pp.sc), 0)::int as score, coalesce(sum(pp.full::int), 0)::int as solved, max(pp.at) as last_at
        from (
          select x.user_id, p.id as pid,
                 case when p.kind = 'essay' then least(coalesce(g.score, 0), p.points) else coalesce(c.best, 0) end as sc,
                 case when p.kind = 'essay' then (coalesce(g.score, 0) >= p.points) else coalesce(c.full, false) end as full,
                 case when p.kind = 'essay' then (select max(s4.created_at) from public.exam_subs s4 where s4.problem_id = p.id and s4.user_id = x.user_id) else c.at end as at
            from public.exam_entries x
            join public.profiles pr on pr.id = x.user_id
            cross join public.exam_problems p
            left join public.exam_grades g on g.problem_id = p.id and g.user_id = x.user_id
            left join lateral (
              select q.best, q.full,
                     (select min(s3.created_at) from public.exam_subs s3 where s3.problem_id = p.id and s3.user_id = x.user_id
                         and (case when s3.total > 0 then (p.points * s3.passed) / s3.total else 0 end) = q.best) as at
                from (select max(case when s.total > 0 then (p.points * s.passed) / s.total else 0 end) as best,
                             bool_or(s.total > 0 and s.passed = s.total) as full
                        from public.exam_subs s where s.problem_id = p.id and s.user_id = x.user_id) q
               where q.best is not null
            ) c on true
           where x.exam_id = e.id and p.exam_id = e.id and public.py_is_student(x.user_id)
        ) pp
       group by pp.user_id
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

create or replace function public.exam_finalize(p_id bigint) returns text
language plpgsql security definer set search_path = public
as $$
begin
  if not public.exam_staff() then return 'forbidden'; end if;
  update public.exams set finalized = true where id = p_id and status = 'open' and settled_at is null;
  return public.exam_settle(p_id);
end $$;
revoke all on function public.exam_finalize(bigint) from public, anon;
grant execute on function public.exam_finalize(bigint) to authenticated;

create or replace function public.exam_board(p_id bigint) returns jsonb
language plpgsql security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); v_adm boolean := public.exam_staff(); e public.exams; v_st text;
begin
  if v_me is null or not public.is_approved() then return null; end if;
  select * into e from public.exams where id = p_id and (status = 'open' or v_adm);
  if not found then return null; end if;
  if e.settled_at is null and now() >= public.exam_end(e) + interval '20 seconds' then v_st := public.exam_settle(p_id); end if;
  if v_st = 'grading' then return jsonb_build_object('ready', false, 'grading', true); end if;
  if not exists (select 1 from public.exams where id = p_id and settled_at is not null) then return jsonb_build_object('ready', false); end if;
  return jsonb_build_object('ready', true, 'n', (select count(*) from public.exam_results where exam_id = p_id),
    'rows', coalesce((select jsonb_agg(jsonb_build_object('rank', r.final_rank, 'score', r.score, 'solved', r.solved,
        'uid', case when r.user_id = v_me or v_adm or coalesce(x.public, true) then r.user_id end,
        'name', case when r.user_id = v_me or v_adm or coalesce(x.public, true) then public.disp(r.user_id) end,
        'hidden', not coalesce(x.public, true), 'me', r.user_id = v_me) order by r.final_rank)
      from public.exam_results r left join public.exam_entries x on x.exam_id = r.exam_id and x.user_id = r.user_id where r.exam_id = p_id), '[]'::jsonb));
end $$;

create or replace function public.exam_review(p_id bigint) returns jsonb
language sql stable security definer set search_path = public
as $$
  select coalesce(jsonb_agg(jsonb_build_object('problem_id', p.id, 'title', p.title, 'points', p.points, 'kind', p.kind,
      'score', case when p.kind = 'essay' then coalesce((select g.score from public.exam_grades g where g.problem_id = p.id and g.user_id = auth.uid()), 0)
                    else coalesce((select max(case when s.total > 0 then (p.points * s.passed) / s.total else 0 end) from public.exam_subs s where s.problem_id = p.id and s.user_id = auth.uid()), 0) end,
      'graded', p.kind <> 'essay' or exists (select 1 from public.exam_grades g where g.problem_id = p.id and g.user_id = auth.uid()),
      'code', case when p.kind = 'essay' then (select s.code from public.exam_subs s where s.problem_id = p.id and s.user_id = auth.uid() order by s.id desc limit 1)
                   else (select s.code from public.exam_subs s where s.problem_id = p.id and s.user_id = auth.uid() order by (case when s.total > 0 then (p.points * s.passed) / s.total else 0 end) desc, s.id desc limit 1) end)
      order by p.position, p.id), '[]'::jsonb)
    from public.exam_problems p join public.exams e on e.id = p.exam_id
   where p.exam_id = p_id and e.status = 'open' and now() >= public.exam_end(e)
$$;

-- 5) 관리자(선생님 포함): 만들기/고치기 — 문제는 id 를 유지하며 고쳐서 제출 기록이 남아요
create or replace function public.exam_save(p jsonb) returns jsonb
language plpgsql security definer set search_path = public
as $$
declare v_id bigint := nullif(p ->> 'id', '')::bigint; e public.exams; q jsonb; i int := 0; v_pid bigint; v_keep bigint[] := '{}';
begin
  if not public.exam_staff() then return jsonb_build_object('status', 'forbidden'); end if;
  if v_id is null then
    insert into public.exams (title, descr, start_at, duration_min, entry_min, status, reward, created_by)
    values (left(p ->> 'title', 60), coalesce(p ->> 'descr', ''), (p ->> 'start_at')::timestamptz, coalesce((p ->> 'duration_min')::int, 60), coalesce((p ->> 'entry_min')::int, 60),
            coalesce(p ->> 'status', 'draft'), coalesce(p -> 'reward', '{}'::jsonb), auth.uid())
    returning id into v_id;
  else
    select * into e from public.exams where id = v_id;
    if not found then return jsonb_build_object('status', 'nouser'); end if;
    if e.settled_at is not null then return jsonb_build_object('status', 'settled'); end if;
    update public.exams set title = left(p ->> 'title', 60), descr = coalesce(p ->> 'descr', ''), start_at = (p ->> 'start_at')::timestamptz,
      duration_min = coalesce((p ->> 'duration_min')::int, 60), entry_min = coalesce((p ->> 'entry_min')::int, 60),
      status = coalesce(p ->> 'status', 'draft'), reward = coalesce(p -> 'reward', reward), rev = rev + 1 where id = v_id;
  end if;
  if p ? 'problems' then
    for q in select * from jsonb_array_elements(p -> 'problems') loop
      i := i + 1;
      v_pid := nullif(q ->> 'id', '')::bigint;
      if v_pid is not null and exists (select 1 from public.exam_problems where id = v_pid and exam_id = v_id) then
        update public.exam_problems set position = i, title = left(coalesce(q ->> 'title', ''), 100), body = coalesce(q ->> 'body', ''),
          points = coalesce((q ->> 'points')::int, 100), tests = coalesce(q -> 'tests', '[]'::jsonb),
          kind = coalesce(nullif(q ->> 'kind', ''), 'code'), rubric = left(coalesce(q ->> 'rubric', ''), 5000) where id = v_pid;
      else
        insert into public.exam_problems (exam_id, position, title, body, points, tests, kind, rubric)
        values (v_id, i, left(coalesce(q ->> 'title', ''), 100), coalesce(q ->> 'body', ''), coalesce((q ->> 'points')::int, 100), coalesce(q -> 'tests', '[]'::jsonb),
               coalesce(nullif(q ->> 'kind', ''), 'code'), left(coalesce(q ->> 'rubric', ''), 5000)) returning id into v_pid;
      end if;
      v_keep := v_keep || v_pid;
    end loop;
    delete from public.exam_problems where exam_id = v_id and not (id = any (v_keep));
  end if;
  return jsonb_build_object('status', 'ok', 'id', v_id);
exception when others then return jsonb_build_object('status', 'invalid', 'msg', sqlerrm);
end $$;

create or replace function public.exam_delete(p_id bigint) returns text
language plpgsql security definer set search_path = public
as $$
begin
  if not public.exam_staff() then return 'forbidden'; end if;
  delete from public.exams where id = p_id;
  return 'ok';
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
    'status', e.status, 'reward', e.reward, 'settled', e.settled_at is not null, 'finalized', e.finalized, 'n_entries', (select count(*) from public.exam_entries where exam_id = e.id),
    'problems', coalesce((select jsonb_agg(jsonb_build_object('id', p.id, 'title', p.title, 'body', p.body, 'points', p.points, 'tests', p.tests, 'kind', p.kind, 'rubric', p.rubric) order by p.position, p.id) from public.exam_problems p where p.exam_id = p_id), '[]'::jsonb));
end $$;

-- 6) 📣 알림 (응시자에게 / 전체 학생에게)
create or replace function public.exam_notify(p_id bigint, p_msg text, p_scope text default 'entrants') returns int
language plpgsql security definer set search_path = public
as $$
declare e public.exams; r record; n int := 0;
begin
  if not public.exam_staff() then return -1; end if;
  select * into e from public.exams where id = p_id;
  if not found or p_msg is null or length(btrim(p_msg)) < 1 or length(p_msg) > 200 then return -2; end if;
  for r in
    select pr.id from public.profiles pr
     where pr.status = 'approved' and public.py_is_student(pr.id)
       and (p_scope = 'all' or exists (select 1 from public.exam_entries x where x.exam_id = p_id and x.user_id = pr.id))
  loop
    perform public.py_notify(r.id, '📝 ' || e.title, btrim(p_msg), 'exam', '#/exam/' || p_id);
    n := n + 1;
  end loop;
  return n;
end $$;
revoke all on function public.exam_notify(bigint, text, text) from public, anon;
grant execute on function public.exam_notify(bigint, text, text) to authenticated;

-- 7) ✍️ 서술형 채점
create or replace function public.exam_essays(p_id bigint) returns jsonb
language plpgsql stable security definer set search_path = public
as $$
begin
  if not public.exam_staff() then return null; end if;
  return coalesce((select jsonb_agg(jsonb_build_object('id', p.id, 'title', p.title, 'body', p.body, 'points', p.points, 'rubric', p.rubric,
      'answers', coalesce((select jsonb_agg(jsonb_build_object('uid', x.user_id, 'name', public.disp(x.user_id),
          'answer', (select s.code from public.exam_subs s where s.problem_id = p.id and s.user_id = x.user_id order by s.id desc limit 1),
          'score', (select g.score from public.exam_grades g where g.problem_id = p.id and g.user_id = x.user_id)) order by public.disp(x.user_id))
        from public.exam_entries x where x.exam_id = p_id and public.py_is_student(x.user_id)), '[]'::jsonb)) order by p.position, p.id)
    from public.exam_problems p where p.exam_id = p_id and p.kind = 'essay'), '[]'::jsonb);
end $$;
revoke all on function public.exam_essays(bigint) from public, anon;
grant execute on function public.exam_essays(bigint) to authenticated;

create or replace function public.exam_grade(p_problem bigint, p_user uuid, p_score int) returns text
language plpgsql security definer set search_path = public
as $$
declare p public.exam_problems; e public.exams;
begin
  if not public.exam_staff() then return 'forbidden'; end if;
  select * into p from public.exam_problems where id = p_problem and kind = 'essay';
  if not found then return 'nouser'; end if;
  select * into e from public.exams where id = p.exam_id;
  if e.settled_at is not null then return 'settled'; end if;
  if p_score is null or p_score < 0 or p_score > p.points then return 'score'; end if;
  insert into public.exam_grades (exam_id, problem_id, user_id, score, graded_by) values (e.id, p.id, p_user, p_score, auth.uid())
  on conflict (problem_id, user_id) do update set score = excluded.score, graded_by = excluded.graded_by, graded_at = now();
  return 'ok';
end $$;
revoke all on function public.exam_grade(bigint, uuid, int) from public, anon;
grant execute on function public.exam_grade(bigint, uuid, int) to authenticated;

revoke all on function public.exam_list(), public.exam_get(bigint), public.exam_submit(bigint, text, int, int), public.exam_settle(bigint), public.exam_board(bigint), public.exam_review(bigint),
  public.exam_save(jsonb), public.exam_delete(bigint), public.exam_admin_get(bigint) from public, anon;
grant execute on function public.exam_list(), public.exam_get(bigint), public.exam_submit(bigint, text, int, int), public.exam_settle(bigint), public.exam_board(bigint), public.exam_review(bigint),
  public.exam_save(jsonb), public.exam_delete(bigint), public.exam_admin_get(bigint) to authenticated;
