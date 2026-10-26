-- =====================================================================
--  PyNest V3.2.0 — 티어 편집(추가·수정·삭제) + m저지용 난이도 6개
--  * 기존 표·데이터는 지우거나 바꾸지 않고 "추가"만 해요. 여러 번 실행해도 안전해요.
--  * v310_ranking.sql(난이도 표)과 staff_roles.sql 이 먼저 적용돼 있어야 해요.
--
--  1) tiers 표      : 티어 이름 · 시작 점수 · 색 · 뱃지 문양 (OWNER / ADMIN 만 고칠 수 있어요)
--                     처음 12개를 넣어 둬요. 앱의 [관리 → 🏅 티어] 에서 마음대로 바꾸세요.
--  2) 난이도 6개    : Bronze 3 · Iron 15 · Gold 50 · Diamond 100 · Ruby 250 · Master 400 점
--                     (이미 같은 이름이 있으면 건드리지 않아요. 점수는 [관리 → 🎯 난이도]에서 바꿀 수 있어요.)
--  ※ 난이도 이름(Bronze, Gold…)과 티어 이름(Bronze, Gold…)은 서로 아무 관련이 없어요.
-- =====================================================================

do $$
begin
  if to_regprocedure('public.mh_is_admin()') is null then
    raise exception 'staff_roles.sql 을 먼저 실행해주세요.';
  end if;
  if to_regclass('public.difficulties') is null then
    raise exception 'v310_ranking.sql 을 먼저 실행해주세요.';
  end if;
end $$;

-- ---------------------------------------------------------------------
-- 1) 티어 표
-- ---------------------------------------------------------------------
create table if not exists public.tiers (
  id bigint generated always as identity primary key,
  name text not null unique check (length(btrim(name)) between 1 and 24),
  min_score int not null unique check (min_score between 0 and 10000000),
  c1 text not null default '#f0b27a' check (c1 ~ '^#[0-9a-fA-F]{6}$'),
  c2 text not null default '#9c5a1e' check (c2 ~ '^#[0-9a-fA-F]{6}$'),
  glyph text not null default 'circle' check (glyph ~ '^[a-z0-9_]{1,16}$'),
  created_at timestamptz not null default now()
);

alter table public.tiers enable row level security;
revoke all on public.tiers from anon;
grant select, insert, update, delete on public.tiers to authenticated;
drop policy if exists tiers_read on public.tiers;
create policy tiers_read on public.tiers for select to authenticated using (public.is_approved());
drop policy if exists tiers_ins on public.tiers;
create policy tiers_ins on public.tiers for insert to authenticated with check (public.mh_is_admin());
drop policy if exists tiers_upd on public.tiers;
create policy tiers_upd on public.tiers for update to authenticated
  using (public.mh_is_admin()) with check (public.mh_is_admin());
drop policy if exists tiers_del on public.tiers;
create policy tiers_del on public.tiers for delete to authenticated using (public.mh_is_admin());

-- 점수 0 에서 시작하는 티어는 항상 하나 있어야 해요 (모든 학생이 어딘가에 속해야 하니까요)
create or replace function public.tiers_guard()
returns trigger language plpgsql set search_path = public
as $$
begin
  if tg_op = 'INSERT' then
    new.name := btrim(new.name);
    return new;
  end if;
  if tg_op = 'DELETE' then
    if old.min_score = 0 then raise exception 'base tier'; end if;
    return old;
  end if;
  if old.min_score = 0 and new.min_score <> 0 then raise exception 'base tier'; end if;
  new.name := btrim(new.name);
  return new;
end;
$$;
drop trigger if exists tiers_guard on public.tiers;
create trigger tiers_guard before insert or update or delete on public.tiers
  for each row execute function public.tiers_guard();

-- 처음 12개 티어 (이미 있으면 그대로 둬요)
insert into public.tiers (name, min_score, c1, c2, glyph) values
  ('Bronze',         0,    '#f0b27a', '#9c5a1e', 'circle'),
  ('Silver',         100,  '#f1f5f9', '#8795a8', 'tri'),
  ('Gold',           500,  '#ffe27a', '#d19a00', 'sq'),
  ('Platinum',       1500, '#8ff0e0', '#16a394', 'dia'),
  ('Diamond',        3500, '#9fd4ff', '#2563eb', 'hex'),
  ('Sapphire',       5000, '#7aa2ff', '#1e3a8a', 'drop'),
  ('Emerald',        7000, '#7df2a8', '#0e8a4f', 'spark'),
  ('Amethyst',       9500, '#f0abfc', '#a21caf', 'gem'),
  ('Master',         12000,'#d9a8ff', '#7c2ae0', 'star'),
  ('Grandmaster',    15000,'#ffb36b', '#c2410c', 'flame'),
  ('Obsidian',       17500,'#9ca3af', '#111827', 'oct'),
  ('The Programmer', 20000,'#ff8aa8', '#e11d48', 'crown')
on conflict do nothing;

-- ---------------------------------------------------------------------
-- 2) m저지용 난이도 6개 (문제에 붙이는 난이도 — 티어와는 별개)
-- ---------------------------------------------------------------------
insert into public.difficulties (name, points, color, position, builtin) values
  ('Bronze',   3,   '#b45309', 50, false),
  ('Iron',     15,  '#64748b', 60, false),
  ('Gold',     50,  '#ca8a04', 70, false),
  ('Diamond',  100, '#0ea5e9', 80, false),
  ('Ruby',     250, '#dc2626', 90, false),
  ('Master',   400, '#7c3aed', 95, false)
on conflict (name) do nothing;
