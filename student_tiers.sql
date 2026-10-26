-- =====================================================================
--  학생 등급(STUDENT / SOLVER / LISTENER) — PyNest 전용
--  * 기존 표·정책·데이터는 지우거나 바꾸지 않아요. "추가"만 하고, 여러 번 실행해도 안전해요.
--  * 등급이 없는 기존 학생은 전부 STUDENT(= 지금과 똑같이 전부 이용)예요.
--  * 직원(OWNER/ADMIN/TEACHER/MOD)은 등급과 상관없이 제한받지 않아요.
--  * staff_roles.sql 을 먼저 실행한 상태여야 해요.
--
--  등급        강의   문제(문제집·숙제·제출)   라이브(방송 시청)   라이브 문제
--  STUDENT      O          O                     O                  O
--  SOLVER       X          O                     X                  X
--  LISTENER     O          X                     O                  X
--  (공지·질문·과제·자유 게시판은 모두 이용 가능)
--
--  등급 부여는 "members(회원 승인/중지)" 권한이 있는 직원(OWNER/ADMIN/MOD)이 해요.
--  표를 바꾸고 싶으면 아래 tier_allows() 함수의 case 문만 고치면 돼요.
-- =====================================================================

do $$
begin
  if to_regprocedure('public.staff_can(text)') is null then
    raise exception 'staff_roles.sql 을 먼저 실행해주세요.';
  end if;
end $$;

-- 1) 등급 표 (행이 없으면 STUDENT) — 직접 쓰기 금지, 아래 함수로만 바꿔요
create table if not exists public.student_tiers (
  user_id uuid primary key references public.profiles(id) on delete cascade,
  username text not null default '',
  tier text not null check (tier in ('solver', 'listener')),
  granted_by uuid,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.student_tiers enable row level security;
revoke all on public.student_tiers from anon, authenticated;
grant select on public.student_tiers to authenticated;

drop policy if exists student_tiers_read on public.student_tiers;
create policy student_tiers_read on public.student_tiers for select to authenticated
  using (user_id = auth.uid() or public.staff_can('members'));

-- 2) 내 등급: 'student' / 'solver' / 'listener'
create or replace function public.my_tier()
returns text
language sql stable security definer set search_path = public
as $$
  select coalesce((select t.tier from public.student_tiers t where t.user_id = auth.uid()), 'student')
$$;

-- 이 기능을 쓸 수 있나? feat: lecture(강의) / live(방송 시청) / problem(문제·숙제·제출) / live_problem(라이브 문제)
create or replace function public.tier_allows(p_feat text)
returns boolean
language sql stable security definer set search_path = public
as $$
  select case
    when public.staff_role() is not null then true   -- 직원은 제한 없음
    else coalesce(case public.my_tier()
      when 'solver'   then p_feat = 'problem'
      when 'listener' then p_feat = any (array['lecture', 'live'])
      else true
    end, true)
  end
$$;

grant execute on function public.my_tier() to authenticated;
grant execute on function public.tier_allows(text) to anon, authenticated;

-- 3) 등급 관리 함수 (members 권한: OWNER / ADMIN / MOD)
create or replace function public.student_tier_list()
returns table (uid uuid, uname text, tier text)
language plpgsql stable security definer set search_path = public
as $$
begin
  if not public.staff_can('members') then raise exception 'not allowed'; end if;
  return query select t.user_id, p.username, t.tier from public.student_tiers t join public.profiles p on p.id = t.user_id;
end;
$$;

-- p_tier: student(기본으로 되돌리기) / solver / listener
-- 결과: ok / invalid / not_found / is_staff
create or replace function public.student_set_tier(p_username text, p_tier text)
returns text
language plpgsql security definer set search_path = public
as $$
declare
  v_caller uuid := auth.uid();
  v_tid uuid;
  v_tname text;
begin
  if v_caller is null or not public.staff_can('members') then raise exception 'not allowed'; end if;
  if p_tier is null or p_tier not in ('student', 'solver', 'listener') then return 'invalid'; end if;
  select p.id, p.username into v_tid, v_tname from public.profiles p
   where lower(p.username) = lower(trim(p_username)) limit 1;
  if v_tid is null then return 'not_found'; end if;
  if public.staff_rank(v_tid) > 0 then return 'is_staff'; end if;
  if p_tier = 'student' then
    delete from public.student_tiers where user_id = v_tid;
    return 'ok';
  end if;
  insert into public.student_tiers (user_id, username, tier, granted_by)
    values (v_tid, v_tname, p_tier, v_caller)
  on conflict (user_id) do update
    set tier = excluded.tier, username = excluded.username, granted_by = excluded.granted_by, updated_at = now();
  return 'ok';
end;
$$;

revoke all on function public.student_tier_list() from public, anon;
revoke all on function public.student_set_tier(text, text) from public, anon;
grant execute on function public.student_tier_list() to authenticated;
grant execute on function public.student_set_tier(text, text) to authenticated;

-- 4) 등급 제한 — RESTRICTIVE 정책 (기존 허용 정책은 그대로 두고 "그리고 이것도 만족해야" 를 더해요)
-- 강의
drop policy if exists tier_lecture on public.lectures;
create policy tier_lecture on public.lectures as restrictive for select to authenticated
  using ((select public.tier_allows('lecture')));
-- 라이브 방송 / 접속 표시
drop policy if exists tier_live on public.live_sessions;
create policy tier_live on public.live_sessions as restrictive for select to authenticated
  using ((select public.tier_allows('live')));
drop policy if exists tier_live on public.live_presence;
create policy tier_live on public.live_presence as restrictive for all to authenticated
  using ((select public.tier_allows('live'))) with check ((select public.tier_allows('live')));
-- 라이브 문제 / 라이브 제출
drop policy if exists tier_live_problem on public.live_problems;
create policy tier_live_problem on public.live_problems as restrictive for select to authenticated
  using ((select public.tier_allows('live_problem')));
drop policy if exists tier_live_problem on public.live_submissions;
create policy tier_live_problem on public.live_submissions as restrictive for all to authenticated
  using ((select public.tier_allows('live_problem'))) with check ((select public.tier_allows('live_problem')));
-- 문제집 / 문제 / 숙제 / 제출
drop policy if exists tier_problem on public.problem_sets;
create policy tier_problem on public.problem_sets as restrictive for select to authenticated
  using ((select public.tier_allows('problem')));
drop policy if exists tier_problem on public.exercises;
create policy tier_problem on public.exercises as restrictive for select to authenticated
  using ((select public.tier_allows('problem')));
drop policy if exists tier_problem on public.problems;
create policy tier_problem on public.problems as restrictive for select to authenticated
  using ((select public.tier_allows('problem')));
drop policy if exists tier_problem on public.homeworks;
create policy tier_problem on public.homeworks as restrictive for select to authenticated
  using ((select public.tier_allows('problem')));
drop policy if exists tier_problem on public.homework_items;
create policy tier_problem on public.homework_items as restrictive for select to authenticated
  using ((select public.tier_allows('problem')));
drop policy if exists tier_problem on public.submissions;
create policy tier_problem on public.submissions as restrictive for all to authenticated
  using ((select public.tier_allows('problem'))) with check ((select public.tier_allows('problem')));
