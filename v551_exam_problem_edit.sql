-- 5.6.0 시험 미리보기에서 문제 하나만 바로 고치기 (선생님/스태프 전용)
create or replace function public.exam_problem_edit(p_id bigint, p jsonb) returns jsonb
language plpgsql security definer set search_path = public
as $$
declare q public.exam_problems; e public.exams;
begin
  if not public.exam_staff() then return jsonb_build_object('status', 'forbidden'); end if;
  select * into q from public.exam_problems where id = p_id;
  if not found then return jsonb_build_object('status', 'nouser'); end if;
  select * into e from public.exams where id = q.exam_id;
  if e.settled_at is not null then return jsonb_build_object('status', 'settled'); end if;
  update public.exam_problems set
    title = case when p ? 'title' then left(coalesce(p ->> 'title', ''), 100) else title end,
    body = case when p ? 'body' then coalesce(p ->> 'body', '') else body end,
    points = case when p ? 'points' then greatest(1, least(1000, coalesce((p ->> 'points')::int, points))) else points end,
    kind = case when p ? 'kind' then coalesce(nullif(p ->> 'kind', ''), kind) else kind end,
    part = case when p ? 'part' then coalesce((p ->> 'part')::int, part) else part end,
    starter = case when p ? 'starter' then left(coalesce(p ->> 'starter', ''), 20000) else starter end,
    rubric = case when p ? 'rubric' then left(coalesce(p ->> 'rubric', ''), 5000) else rubric end,
    tests = case when p ? 'tests' then coalesce(p -> 'tests', '[]'::jsonb) else tests end
  where id = p_id;
  update public.exams set rev = rev + 1 where id = e.id;
  return jsonb_build_object('status', 'ok');
exception when others then return jsonb_build_object('status', 'invalid', 'msg', sqlerrm);
end $$;
revoke all on function public.exam_problem_edit(bigint, jsonb) from public, anon;
grant execute on function public.exam_problem_edit(bigint, jsonb) to authenticated;
