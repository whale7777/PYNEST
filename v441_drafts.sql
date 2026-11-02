-- =====================================================================
--  PyNest V4.4.1 — 문제 임시 저장 · 문제집 마지막 위치 (기기가 바뀌어도 이어져요)
--  * 기존 표·데이터는 건드리지 않고 새 표 2개만 "추가"해요. 여러 번 실행해도 안전해요.
--  * 이 SQL 을 안 돌려도 앱은 이 브라우저에만 저장하는 방식으로 동작해요. (돌리면 다른 기기에서도 이어져요)
--  * 본인 것만 보고 쓸 수 있어요. (선생님도 남의 임시 저장은 볼 수 없어요)
-- =====================================================================

do $$
begin
  if to_regclass('public.exercises') is null or to_regclass('public.problem_sets') is null then
    raise exception '문제 표(exercises, problem_sets)가 없어요.';
  end if;
end $$;

-- 1) 문제별 임시 저장 (코드 + 정답 칸 답)
create table if not exists public.problem_drafts (
  user_id uuid not null references public.profiles(id) on delete cascade,
  exercise_id bigint not null references public.exercises(id) on delete cascade,
  set_id bigint,
  code text not null default '' check (length(code) <= 30000),
  vals jsonb check (vals is null or length(vals::text) <= 30000),
  updated_at timestamptz not null default now(),
  primary key (user_id, exercise_id)
);
create index if not exists problem_drafts_set_idx on public.problem_drafts (user_id, set_id);

-- 2) 문제집마다 마지막으로 풀거나 본 문제
create table if not exists public.set_last (
  user_id uuid not null references public.profiles(id) on delete cascade,
  set_id bigint not null references public.problem_sets(id) on delete cascade,
  exercise_id bigint not null,
  updated_at timestamptz not null default now(),
  primary key (user_id, set_id)
);

do $$
declare t text;
begin
  foreach t in array array['problem_drafts', 'set_last'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('revoke all on public.%I from anon', t);
    execute format('grant select, insert, update, delete on public.%I to authenticated', t);
    execute format('drop policy if exists %I on public.%I', t || '_own', t);
    execute format('create policy %I on public.%I for all to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid())', t || '_own', t);
  end loop;
end $$;
