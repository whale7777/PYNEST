-- =====================================================================
--  PyNest V3.6.0 — 비공개 / 바로 게시
--  * 문제집·문제에 "공개 여부(is_public)"를 "추가"해요. 지금 있는 문제집·문제는 모두 그대로 "공개"예요.
--  * 비공개로 두면 학생은 목록·번호 보기·직접 주소·API 어디서도 볼 수 없어요. 선생님/관리자는 그대로 다 보여요.
--  * 여러 번 실행해도 안전해요.
-- =====================================================================

do $$
begin
  if to_regclass('public.problem_sets') is null or to_regclass('public.exercises') is null then
    raise exception 'PyNest 문제 표를 찾을 수 없어요.';
  end if;
end $$;

-- 1) 새 칸 (기본값 true = 공개이므로 기존 데이터는 그대로)
alter table public.problem_sets add column if not exists is_public boolean not null default true;
alter table public.problem_sets add column if not exists published_at timestamptz;
alter table public.exercises add column if not exists is_public boolean not null default true;
alter table public.exercises add column if not exists published_at timestamptz;

-- 2) 공개로 바뀌는 순간을 기록 ("최근 한 주간 생긴 문제"는 이 시각을 써요)
create or replace function public.set_published_at()
returns trigger language plpgsql
as $$
begin
  if new.is_public and (tg_op = 'INSERT' or coalesce(old.is_public, true) = false) then
    new.published_at := now();
  end if;
  return new;
end;
$$;
drop trigger if exists trg_sets_published on public.problem_sets;
create trigger trg_sets_published before insert or update of is_public on public.problem_sets
  for each row execute function public.set_published_at();
drop trigger if exists trg_ex_published on public.exercises;
create trigger trg_ex_published before insert or update of is_public on public.exercises
  for each row execute function public.set_published_at();

-- 3) 학생이 읽는 규칙만 "공개된 것만"으로 바꿔요 (직원·관리자 규칙은 그대로라 다 보여요)
drop policy if exists "sets read" on public.problem_sets;
create policy "sets read" on public.problem_sets for select to authenticated
  using (public.is_approved() and is_public);

drop policy if exists "exercises read" on public.exercises;
create policy "exercises read" on public.exercises for select to authenticated
  using (public.is_approved() and is_public
         and exists (select 1 from public.problem_sets s where s.id = exercises.set_id and s.is_public));

do $$
begin
  if to_regclass('public.homeworks') is not null then
    drop policy if exists "homeworks read" on public.homeworks;
    create policy "homeworks read" on public.homeworks for select to authenticated
      using (public.is_approved() and exists (select 1 from public.problem_sets s where s.id = homeworks.set_id and s.is_public));
  end if;
end $$;

-- 보이지 않는 문제에는 제출도 못 해요 (위 규칙 덕분에 학생에게는 비공개 문제가 안 보여요)
drop policy if exists "submissions insert" on public.submissions;
create policy "submissions insert" on public.submissions for insert to authenticated
  with check (public.is_approved() and user_id = auth.uid()
              and exists (select 1 from public.exercises e where e.id = submissions.exercise_id));

-- 4) 홈 화면 현황(home_stats)도 공개된 문제만 세도록 다시 만들어요 (v330_home.sql 을 안 돌렸어도 같이 만들어져요)
create or replace function public.home_stats()
returns jsonb
language plpgsql stable security definer set search_path = public
as $$
declare
  v_total int; v_mine int; v_week int; v_unsolved int; v_new jsonb; v_uns jsonb;
begin
  if not public.is_approved() then return null; end if;

  select count(*) into v_total from public.exercises e join public.problem_sets s on s.id = e.set_id
   where e.is_public and s.is_public;
  select count(distinct sb.exercise_id) into v_mine
    from public.submissions sb join public.exercises e on e.id = sb.exercise_id join public.problem_sets s on s.id = e.set_id
   where sb.user_id = auth.uid() and sb.judge ->> 'status' = 'AC' and e.is_public and s.is_public;
  select count(*) into v_week from public.exercises e join public.problem_sets s on s.id = e.set_id
   where e.is_public and s.is_public
     and greatest(coalesce(e.published_at, e.created_at), coalesce(s.published_at, s.created_at)) >= now() - interval '7 days';

  with uns as (
    select e.id, e.set_id, e.difficulty, e.body
      from public.exercises e join public.problem_sets s on s.id = e.set_id and s.is_public
     where e.is_public
       and (jsonb_array_length(coalesce(e.tests, '[]'::jsonb)) > 0
            or exists (select 1 from jsonb_array_elements(coalesce(e.answers, '[]'::jsonb)) a where a ->> 'type' <> 'm'))
       and not exists (
         select 1 from public.submissions sb
           join public.profiles p on p.id = sb.user_id and p.status = 'approved' and p.role <> 'admin'
          where sb.exercise_id = e.id and sb.judge ->> 'status' = 'AC'
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
    select e.id, e.set_id, e.difficulty,
           greatest(coalesce(e.published_at, e.created_at), coalesce(ps.published_at, ps.created_at)) as created_at,
           left(regexp_replace(split_part(btrim(e.body), E'\n', 1), '[`*]', '', 'g'), 60) as title,
           coalesce(ps.short_name, ps.title) as set_name
      from public.exercises e join public.problem_sets ps on ps.id = e.set_id
     where e.is_public and ps.is_public
       and greatest(coalesce(e.published_at, e.created_at), coalesce(ps.published_at, ps.created_at)) >= now() - interval '7 days'
     order by 4 desc, e.id desc limit 10) x;

  return jsonb_build_object('total', v_total, 'mine', v_mine, 'week', v_week, 'unsolved', v_unsolved,
                            'new_list', v_new, 'unsolved_list', v_uns);
end;
$$;
revoke all on function public.home_stats() from public, anon;
grant execute on function public.home_stats() to authenticated;
