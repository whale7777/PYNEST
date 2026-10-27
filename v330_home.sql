-- =====================================================================
--  PyNest V3.3.0 — 홈 화면 문제 현황 (제공되는 문제 · 내가 푼 문제 · 최근 한 주 새 문제 · 아직 아무도 못 푼 문제)
--  * 새 함수 home_stats() 하나만 "추가"해요. 기존 표·데이터는 그대로예요. 여러 번 실행해도 안전해요.
--  * v310_ranking.sql 이 먼저 적용돼 있어야 해요.
--
--  아직 아무도 못 푼 문제 = 자동 채점이 되는 문제 중, 승인된 학생(직원 제외) 누구도 정답(AC)을 낸 적 없는 문제
--  (서술형처럼 선생님이 직접 확인하는 문제는 "못 푼" 것이 아니라서 빼요.)
-- =====================================================================

do $$
begin
  if to_regclass('public.exercises') is null or to_regclass('public.submissions') is null then
    raise exception 'PyNest 문제 표를 찾을 수 없어요.';
  end if;
end $$;

create or replace function public.home_stats()
returns jsonb
language plpgsql stable security definer set search_path = public
as $$
declare
  v_total int;
  v_mine int;
  v_week int;
  v_unsolved int;
  v_new jsonb;
  v_uns jsonb;
begin
  if not public.is_approved() then return null; end if;

  select count(*) into v_total from public.exercises;
  select count(distinct s.exercise_id) into v_mine
    from public.submissions s where s.user_id = auth.uid() and s.judge ->> 'status' = 'AC';
  select count(*) into v_week from public.exercises where created_at >= now() - interval '7 days';

  with uns as (
    select e.id, e.set_id, e.difficulty, e.body
      from public.exercises e
     where (jsonb_array_length(coalesce(e.tests, '[]'::jsonb)) > 0
            or exists (select 1 from jsonb_array_elements(coalesce(e.answers, '[]'::jsonb)) a where a ->> 'type' <> 'm'))
       and not exists (
         select 1 from public.submissions s
           join public.profiles p on p.id = s.user_id and p.status = 'approved' and p.role <> 'admin'
          where s.exercise_id = e.id and s.judge ->> 'status' = 'AC'
            and not exists (select 1 from public.staff_roles sr where sr.user_id = p.id))
  )
  select (select count(*) from uns),
         (select coalesce(jsonb_agg(to_jsonb(x)), '[]'::jsonb) from (
            select u.id, u.set_id, u.difficulty,
                   left(regexp_replace(split_part(btrim(u.body), E'\n', 1), '[`*]', '', 'g'), 60) as title,
                   coalesce(ps.short_name, ps.title) as set_name
              from uns u left join public.problem_sets ps on ps.id = u.set_id
             order by u.id limit 10) x)
    into v_unsolved, v_uns;

  select coalesce(jsonb_agg(to_jsonb(x)), '[]'::jsonb) into v_new from (
    select e.id, e.set_id, e.difficulty, e.created_at,
           left(regexp_replace(split_part(btrim(e.body), E'\n', 1), '[`*]', '', 'g'), 60) as title,
           coalesce(ps.short_name, ps.title) as set_name
      from public.exercises e left join public.problem_sets ps on ps.id = e.set_id
     where e.created_at >= now() - interval '7 days'
     order by e.created_at desc, e.id desc limit 10) x;

  return jsonb_build_object('total', v_total, 'mine', v_mine, 'week', v_week, 'unsolved', v_unsolved,
                            'new_list', v_new, 'unsolved_list', v_uns);
end;
$$;
revoke all on function public.home_stats() from public, anon;
grant execute on function public.home_stats() to authenticated;
