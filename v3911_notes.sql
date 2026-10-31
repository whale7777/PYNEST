-- =====================================================================
--  PyNest V3.9.11 — 문제집 설명 글(마크다운) 블록
--  * 새 표 set_notes 하나만 "추가"해요. 기존 표·데이터·정책은 그대로예요. 여러 번 실행해도 안전해요.
--  * 문제와 같은 순서 칸(position)을 써서 문제 사이사이에 글을 끼워 넣어요. 문제 번호·점수·랭킹에는 영향이 없어요.
--  * 실행 전에는 설명 글 기능만 숨겨지고, 나머지는 예전처럼 동작해요.
-- =====================================================================

create table if not exists public.set_notes (
  id bigint generated always as identity primary key,
  set_id bigint not null references public.problem_sets(id) on delete cascade,
  position double precision not null default 0,
  area text not null default 'normal' check (area in ('normal', 'elite')),
  body text not null default '' check (length(body) <= 30000),
  is_public boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists set_notes_set_idx on public.set_notes (set_id, position);

alter table public.set_notes enable row level security;
revoke all on public.set_notes from anon;
grant select, insert, update, delete on public.set_notes to authenticated;

-- 선생님/관리자: 전부
drop policy if exists "notes admin" on public.set_notes;
create policy "notes admin" on public.set_notes for all to authenticated
  using (public.is_admin()) with check (public.is_admin());
drop policy if exists "notes staff" on public.set_notes;
create policy "notes staff" on public.set_notes for all to authenticated
  using (public.staff_can('content')) with check (public.staff_can('content'));

-- 학생: 공개된 문제집의 공개된 글만 읽기
drop policy if exists "notes read" on public.set_notes;
create policy "notes read" on public.set_notes for select to authenticated
  using (public.is_approved() and is_public
         and exists (select 1 from public.problem_sets s where s.id = set_notes.set_id and s.is_public));

-- 등급(SOLVER/LISTENER)별 제한: 문제와 같은 규칙 (문제를 못 보는 등급은 글도 못 봐요)
drop policy if exists tier_problem on public.set_notes;
create policy tier_problem on public.set_notes as restrictive for select to authenticated
  using ((select public.tier_allows('problem'::text)));
