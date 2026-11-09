-- v5.4.0 시험 단답형(자동 채점) — Supabase SQL 편집기에서 한 번 실행하세요. (여러 번 실행해도 안전해요)
-- 단답형 문제는 exam_problems.kind = 'short' 이고, tests 칸에 정답식 [{"label":"(1)","type":"t","value":"30","alts":[]}, …] 을 넣어요.
-- 학생 화면에서 칸마다 자동 채점하고, 점수는 (맞은 칸 / 전체 칸) × 배점 이에요. (코드 문제와 같은 방식)

alter table public.exam_problems drop constraint if exists exam_problems_kind_check;
alter table public.exam_problems add constraint exam_problems_kind_check check (kind in ('code', 'essay', 'short'));

-- 시험지: 시험 중에 단답형의 정답식도 같이 내려줘요 (코드 문제의 채점 테스트와 같은 수준)
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
             'tests', case when p.kind in ('code', 'short') then p.tests else '[]'::jsonb end) order by p.position, p.id), '[]'::jsonb)
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
