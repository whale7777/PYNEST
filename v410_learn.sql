-- =====================================================================
--  PyNest V4.1.0 — 📚 학습 (단계별 학습: 설명 → O/X·확인 문제 → 실습)
--  * 새 표 4개와 함수 1개만 "추가"해요. 기존 표·데이터·정책은 그대로예요. 여러 번 실행해도 안전해요.
--  * 실행 전에는 학습 페이지만 "준비 중"으로 보이고 나머지는 예전처럼 동작해요.
--    learn_courses  코스(예: 파이썬 첫걸음)
--    learn_lessons  레슨(단계 목록 steps 가 jsonb 로 들어 있어요)
--    learn_progress 학생별 진도·획득 XP·틀린 확인문제(오답 복습용)
--    learn_days     날짜별 획득 XP (연속 학습일 계산)
-- =====================================================================

create table if not exists public.learn_courses (
  id bigint generated always as identity primary key,
  title text not null check (length(title) between 1 and 120),
  description text not null default '' check (length(description) <= 2000),
  sequential boolean not null default true,       -- true: 앞 레슨을 끝내야 다음 레슨이 열려요
  position double precision not null default 0,
  is_public boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists public.learn_lessons (
  id bigint generated always as identity primary key,
  course_id bigint not null references public.learn_courses(id) on delete cascade,
  position double precision not null default 0,
  title text not null check (length(title) between 1 and 160),
  summary text not null default '' check (length(summary) <= 20000),
  minutes int,
  steps jsonb not null default '[]'::jsonb,
  is_public boolean not null default true,
  created_at timestamptz not null default now()
);
create index if not exists learn_lessons_course_idx on public.learn_lessons (course_id, position);

create table if not exists public.learn_progress (
  user_id uuid not null references public.profiles(id) on delete cascade,
  lesson_id bigint not null references public.learn_lessons(id) on delete cascade,
  cur int not null default 0,
  done jsonb not null default '{}'::jsonb,
  wrong jsonb not null default '[]'::jsonb,
  xp int not null default 0,
  completed boolean not null default false,
  completed_at timestamptz,
  updated_at timestamptz not null default now(),
  primary key (user_id, lesson_id)
);

create table if not exists public.learn_days (
  user_id uuid not null references public.profiles(id) on delete cascade,
  day date not null,
  xp int not null default 0,
  primary key (user_id, day)
);

alter table public.learn_courses enable row level security;
alter table public.learn_lessons enable row level security;
alter table public.learn_progress enable row level security;
alter table public.learn_days enable row level security;
revoke all on public.learn_courses, public.learn_lessons, public.learn_progress, public.learn_days from anon;
grant select, insert, update, delete on public.learn_courses, public.learn_lessons to authenticated;
grant select, insert, update on public.learn_progress to authenticated;
grant select on public.learn_days to authenticated;

-- 코스·레슨: 선생님/관리자는 전부, 학생은 공개된 것만 읽기
drop policy if exists "learn courses admin" on public.learn_courses;
create policy "learn courses admin" on public.learn_courses for all to authenticated
  using (public.is_admin() or public.staff_can('content')) with check (public.is_admin() or public.staff_can('content'));
drop policy if exists "learn courses read" on public.learn_courses;
create policy "learn courses read" on public.learn_courses for select to authenticated
  using (public.is_approved() and is_public);

drop policy if exists "learn lessons admin" on public.learn_lessons;
create policy "learn lessons admin" on public.learn_lessons for all to authenticated
  using (public.is_admin() or public.staff_can('content')) with check (public.is_admin() or public.staff_can('content'));
drop policy if exists "learn lessons read" on public.learn_lessons;
create policy "learn lessons read" on public.learn_lessons for select to authenticated
  using (public.is_approved() and is_public
         and exists (select 1 from public.learn_courses c where c.id = learn_lessons.course_id and c.is_public));

-- 진도: 내 것만 읽고 쓰기 (선생님은 읽기만)
drop policy if exists "learn progress own" on public.learn_progress;
create policy "learn progress own" on public.learn_progress for all to authenticated
  using (user_id = auth.uid() and public.is_approved()) with check (user_id = auth.uid() and public.is_approved());
drop policy if exists "learn progress staff" on public.learn_progress;
create policy "learn progress staff" on public.learn_progress for select to authenticated
  using (public.is_admin() or public.staff_can('review'));

drop policy if exists "learn days own" on public.learn_days;
create policy "learn days own" on public.learn_days for select to authenticated
  using (user_id = auth.uid());
drop policy if exists "learn days staff" on public.learn_days;
create policy "learn days staff" on public.learn_days for select to authenticated
  using (public.is_admin() or public.staff_can('review'));

-- XP 적립 (한국 시간 날짜별). 한 번에 최대 100, 직접 쓰기는 막혀 있어요.
create or replace function public.learn_add_xp(p_xp int)
returns void language plpgsql security definer set search_path = public as $$
begin
  if auth.uid() is null or not public.is_approved() then return; end if;
  insert into public.learn_days (user_id, day, xp)
  values (auth.uid(), (now() at time zone 'Asia/Seoul')::date, least(greatest(coalesce(p_xp, 0), 0), 100))
  on conflict (user_id, day) do update set xp = public.learn_days.xp + excluded.xp;
end $$;
revoke all on function public.learn_add_xp(int) from public, anon;
grant execute on function public.learn_add_xp(int) to authenticated;
