-- =====================================================================
--  PyNest V3.7.0 — 공용 함수 (선생님이 미리 만들어 두는 함수)
--  * 새 표 prelude_funcs 하나만 "추가"해요. 기존 표·데이터는 그대로예요. 여러 번 실행해도 안전해요.
--  * 학생이 코드를 실행·채점·제출할 때 여기 저장된 함수들이 먼저 불러와져서, 학생은 함수 이름만 쓰면 돼요.
--    scope = 'all'  → 모든 문제 + 라이브 문제 (공용)
--    scope = 'live' → 라이브 문제에서만
--  * 학생 화면에서도 읽을 수 있어야 실행되므로(브라우저에서 파이썬을 돌려요) 읽기는 승인된 사용자 전체,
--    쓰기는 선생님/관리자만 가능해요. 정답을 숨기는 용도는 아니에요.
-- =====================================================================

create table if not exists public.prelude_funcs (
  id bigint generated always as identity primary key,
  name text not null default '' check (length(name) <= 80),
  code text not null default '' check (length(code) <= 20000),
  scope text not null default 'all' check (scope in ('all', 'live')),
  enabled boolean not null default true,
  position int not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.prelude_funcs enable row level security;
revoke all on public.prelude_funcs from anon;
grant select, insert, update, delete on public.prelude_funcs to authenticated;

drop policy if exists prelude_read on public.prelude_funcs;
create policy prelude_read on public.prelude_funcs for select to authenticated using (public.is_approved());

drop policy if exists prelude_write on public.prelude_funcs;
create policy prelude_write on public.prelude_funcs for all to authenticated
  using (public.is_admin() or public.staff_can('content'))
  with check (public.is_admin() or public.staff_can('content'));
