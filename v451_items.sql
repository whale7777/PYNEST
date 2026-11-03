-- =====================================================================
--  PyNest V4.5.1 — 캐릭터 아이템 (로블록스처럼 꾸미기)
--  * 새 표/함수만 "추가"해요. 기존 데이터는 그대로예요. 여러 번 실행해도 안전해요.
--  * 먼저 v440_social.sql, v450_growth.sql 이 실행돼 있어야 해요.
--  [아이템 얻는 법]
--    free   : 누구나 바로 써요 (기본 아이템)
--    score  : 랭킹 점수가 기준 이상이면 "받기" (예: 500점)
--    tier   : 티어(큰 등급)가 기준 이상이면 "받기" (0 Bronze · 1 Silver · 2 Gold · 3 Platinum …)
--    price  : 파이포인트로 구입
--    reward : 특정 문제를 처음 맞추면 자동 지급 (관리자가 문제에 연결)
--    event  : 행사 때 선생님이 지급 (V4.5.2)
--  [아이템 자리] back(뒤) · outfit(옷) · hair(머리) · hat(모자) · face(얼굴) · deco(장식)
-- =====================================================================
do $$
begin
  if to_regclass('public.profile_ext') is null or to_regclass('public.py_wallet') is null then
    raise exception 'v440_social.sql 과 v450_growth.sql 을 먼저 실행해주세요.';
  end if;
end $$;

-- 아이템 그림(SVG 조각)이 안전한지 검사: 100×100 칸 안에 그리는 도형만 허용
create or replace function public.avatar_svg_ok(p text) returns boolean
language sql immutable
as $$
  select p is not null and length(p) between 10 and 8000
     and p !~* '<\s*(script|image|foreignobject|use|a|iframe|style|animate|set|text|tspan|filter|pattern|mask|clippath|symbol|marker|switch|svg)\y'
     and p !~* '\son[a-z]+\s*='
     and p !~* '(javascript:|data:|href\s*=|xlink|@import|expression\s*\()'
     and p !~* 'url\s*\(\s*[^#\s)]'
$$;

create table if not exists public.avatar_items (
  id text primary key check (id ~ '^[a-z0-9_]{2,40}$'),
  name text not null check (length(name) between 1 and 30),
  descr text not null default '' check (length(descr) <= 120),
  slot text not null check (slot in ('back', 'outfit', 'hair', 'hat', 'face', 'deco')),
  svg text not null check (public.avatar_svg_ok(svg)),
  kind text not null default 'free' check (kind in ('free', 'score', 'tier', 'price', 'reward', 'event')),
  val int not null default 0 check (val >= 0),
  price int not null default 0 check (price >= 0),
  status text not null default 'active' check (status in ('active', 'hidden')),
  builtin boolean not null default false,
  created_by uuid,
  created_at timestamptz not null default now()
);
create table if not exists public.avatar_inventory (
  user_id uuid not null references public.profiles(id) on delete cascade,
  item_id text not null references public.avatar_items(id) on delete cascade,
  source text not null default 'claim',
  created_at timestamptz not null default now(),
  primary key (user_id, item_id)
);
create table if not exists public.exercise_rewards (
  exercise_id bigint primary key references public.exercises(id) on delete cascade,
  item_id text not null references public.avatar_items(id) on delete cascade
);
alter table public.avatar_items enable row level security;
alter table public.avatar_inventory enable row level security;
alter table public.exercise_rewards enable row level security;
revoke all on public.avatar_items, public.avatar_inventory, public.exercise_rewards from anon, authenticated;
grant select on public.avatar_items, public.avatar_inventory, public.exercise_rewards to authenticated;
drop policy if exists avatar_items_read on public.avatar_items;
create policy avatar_items_read on public.avatar_items for select to authenticated
  using (public.is_approved() and (status = 'active' or coalesce(public.staff_role(), '') in ('owner', 'admin')));
drop policy if exists avatar_inv_read on public.avatar_inventory;
create policy avatar_inv_read on public.avatar_inventory for select to authenticated
  using (user_id = auth.uid() or coalesce(public.staff_role(), '') in ('owner', 'admin'));
drop policy if exists ex_rewards_read on public.exercise_rewards;
create policy ex_rewards_read on public.exercise_rewards for select to authenticated using (public.is_approved());

-- 내 점수 · 티어(큰 등급)
create or replace function public.my_score_tier(p_uid uuid, out score int, out tier int)
language plpgsql stable security definer set search_path = public
as $$
begin
  select coalesce((select pts from public.rk_scores(null) where uid = p_uid), 0) into score;
  select public.tier_major(score) into tier;
end $$;
revoke all on function public.my_score_tier(uuid) from public, anon, authenticated;

create or replace function public.item_owned(p_uid uuid, p_item text) returns boolean
language sql stable security definer set search_path = public
as $$
  select exists (select 1 from public.avatar_items i where i.id = p_item and i.status = 'active'
                   and (i.kind = 'free' or exists (select 1 from public.avatar_inventory v where v.user_id = p_uid and v.item_id = i.id)))
$$;
revoke all on function public.item_owned(uuid, text) from public, anon, authenticated;

-- 내 아이템 목록 (가진 것 / 받을 수 있는 것 / 잠긴 것)
create or replace function public.item_catalog() returns jsonb
language plpgsql stable security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); v_sc int; v_t int; v_staff boolean := coalesce(public.staff_role(), '') <> '';
begin
  if v_me is null or not public.is_approved() then return null; end if;
  select score, tier into v_sc, v_t from public.my_score_tier(v_me);
  return jsonb_build_object('score', v_sc, 'tier', v_t,
    'py', coalesce((select balance from public.py_wallet where user_id = v_me), 0),
    'items', (select coalesce(jsonb_agg(jsonb_build_object(
        'id', i.id, 'name', i.name, 'descr', i.descr, 'slot', i.slot, 'kind', i.kind, 'val', i.val, 'price', i.price,
        'owned', v_staff or i.kind = 'free' or exists (select 1 from public.avatar_inventory v where v.user_id = v_me and v.item_id = i.id),
        'can_claim', (i.kind = 'score' and v_sc >= i.val) or (i.kind = 'tier' and v_t >= i.val)) order by i.slot, i.kind, i.val, i.price, i.id), '[]'::jsonb)
      from public.avatar_items i where i.status = 'active'));
end $$;

create or replace function public.item_claim(p_item text) returns text
language plpgsql security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); i public.avatar_items; v_sc int; v_t int;
begin
  if v_me is null or not public.py_is_student(v_me) then return 'nouser'; end if;
  select * into i from public.avatar_items where id = p_item and status = 'active';
  if not found then return 'nouser'; end if;
  select score, tier into v_sc, v_t from public.my_score_tier(v_me);
  if not ((i.kind = 'score' and v_sc >= i.val) or (i.kind = 'tier' and v_t >= i.val)) then return 'locked'; end if;
  insert into public.avatar_inventory (user_id, item_id, source) values (v_me, i.id, 'claim') on conflict do nothing;
  return 'ok';
end $$;

create or replace function public.item_buy(p_item text) returns text
language plpgsql security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); i public.avatar_items;
begin
  if v_me is null or not public.py_is_student(v_me) then return 'nouser'; end if;
  select * into i from public.avatar_items where id = p_item and status = 'active' and kind = 'price';
  if not found then return 'nouser'; end if;
  if exists (select 1 from public.avatar_inventory where user_id = v_me and item_id = i.id) then return 'have'; end if;
  begin
    perform public.py_add(v_me, -i.price, 'item_buy', i.id, i.name);
  exception when others then return 'poor';
  end;
  insert into public.avatar_inventory (user_id, item_id, source) values (v_me, i.id, 'buy');
  return 'ok';
end $$;

-- 내부용: 아이템 지급 (알림 포함). 새로 받았으면 true
create or replace function public.item_give(p_uid uuid, p_item text, p_src text default 'reward') returns boolean
language plpgsql security definer set search_path = public
as $$
declare i public.avatar_items;
begin
  select * into i from public.avatar_items where id = p_item;
  if not found then return false; end if;
  insert into public.avatar_inventory (user_id, item_id, source) values (p_uid, p_item, p_src) on conflict do nothing;
  if not found then return false; end if;
  perform public.py_notify(p_uid, '🎁 새 아이템: ' || i.name, '캐릭터 꾸미기에서 입어보세요!', 'item', '#/me/avatar');
  return true;
end $$;
revoke all on function public.item_give(uuid, text, text) from public, anon, authenticated;

-- 캐릭터 저장 검사: 가지지 않은 아이템은 못 입어요 (직접 저장해도 막혀요)
create or replace function public.profile_ext_items_guard() returns trigger
language plpgsql security definer set search_path = public
as $$
declare k text; v jsonb; its jsonb;
begin
  its := new.avatar -> 'items';
  if its is null or jsonb_typeof(its) <> 'object' then
    if its is not null then new.avatar := new.avatar - 'items'; end if;
    return new;
  end if;
  if coalesce(public.staff_role(), '') <> '' then return new; end if;
  for k, v in select * from jsonb_each(its) loop
    if jsonb_typeof(v) <> 'string' or not public.item_owned(new.user_id, v #>> '{}')
       or not exists (select 1 from public.avatar_items i where i.id = v #>> '{}' and i.slot = k) then
      new.avatar := jsonb_set(new.avatar, '{items}', its - k);
      its := its - k;
    end if;
  end loop;
  return new;
end $$;
drop trigger if exists trg_profile_ext_items on public.profile_ext;
create trigger trg_profile_ext_items before insert or update of avatar on public.profile_ext
  for each row execute function public.profile_ext_items_guard();

-- 문제 보상 아이템: 그 문제를 처음 맞추면 지급
create or replace function public.trg_item_reward() returns trigger
language plpgsql security definer set search_path = public
as $$
declare v_item text;
begin
  if coalesce(new.judge ->> 'status', '') <> 'AC' or not public.py_is_student(new.user_id) then return null; end if;
  select item_id into v_item from public.exercise_rewards where exercise_id = new.exercise_id;
  if v_item is null then return null; end if;
  perform public.item_give(new.user_id, v_item, 'reward');
  return null;
end $$;
drop trigger if exists trg_item_reward on public.submissions;
create trigger trg_item_reward after insert on public.submissions for each row execute function public.trg_item_reward();

-- 관리자
create or replace function public.item_upsert(p jsonb) returns text
language plpgsql security definer set search_path = public
as $$
begin
  if coalesce(public.staff_role(), '') not in ('owner', 'admin') then return 'forbidden'; end if;
  insert into public.avatar_items (id, name, descr, slot, svg, kind, val, price, status, created_by)
  values (p ->> 'id', p ->> 'name', coalesce(p ->> 'descr', ''), p ->> 'slot', p ->> 'svg', coalesce(p ->> 'kind', 'free'),
          coalesce((p ->> 'val')::int, 0), coalesce((p ->> 'price')::int, 0), coalesce(p ->> 'status', 'active'), auth.uid())
  on conflict (id) do update set name = excluded.name, descr = excluded.descr, slot = excluded.slot, svg = excluded.svg,
    kind = excluded.kind, val = excluded.val, price = excluded.price, status = excluded.status;
  return 'ok';
exception when others then return 'invalid';
end $$;
create or replace function public.item_delete(p_id text) returns text
language plpgsql security definer set search_path = public
as $$
begin
  if coalesce(public.staff_role(), '') not in ('owner', 'admin') then return 'forbidden'; end if;
  delete from public.avatar_items where id = p_id and not builtin;
  update public.avatar_items set status = 'hidden' where id = p_id and builtin;
  return 'ok';
end $$;
create or replace function public.item_give_admin(p_uid uuid, p_item text) returns text
language plpgsql security definer set search_path = public
as $$
begin
  if coalesce(public.staff_role(), '') not in ('owner', 'admin') then return 'forbidden'; end if;
  if not public.py_is_student(p_uid) then return 'nouser'; end if;
  perform public.item_give(p_uid, p_item, 'admin');
  return 'ok';
end $$;
create or replace function public.reward_set(p_ex bigint, p_item text) returns text
language plpgsql security definer set search_path = public
as $$
begin
  if coalesce(public.staff_role(), '') not in ('owner', 'admin') then return 'forbidden'; end if;
  if p_item is null or p_item = '' then delete from public.exercise_rewards where exercise_id = p_ex; return 'ok'; end if;
  insert into public.exercise_rewards (exercise_id, item_id) values (p_ex, p_item)
    on conflict (exercise_id) do update set item_id = excluded.item_id;
  return 'ok';
exception when others then return 'invalid';
end $$;

revoke all on function public.item_catalog(), public.item_claim(text), public.item_buy(text), public.item_upsert(jsonb), public.item_delete(text),
  public.item_give_admin(uuid, text), public.reward_set(bigint, text) from public, anon;
grant execute on function public.item_catalog(), public.item_claim(text), public.item_buy(text), public.item_upsert(jsonb), public.item_delete(text),
  public.item_give_admin(uuid, text), public.reward_set(bigint, text) to authenticated;

-- 기본 아이템 (그림은 100×100 칸 기준)
insert into public.avatar_items (id, name, descr, slot, svg, kind, val, price, builtin) values
 ('cat_ears', '고양이 귀', '쫑긋 고양이 귀', 'hat', '<path d="M27 34 L30 10 L44 26Z" fill="#f59e0b"/><path d="M73 34 L70 10 L56 26Z" fill="#f59e0b"/><path d="M31 27 L32 17 L38 25Z M69 27 L68 17 L62 25Z" fill="#fda4af"/>', 'free', 0, 0, true),
 ('scarf', '빨간 목도리', '따뜻한 목도리', 'outfit', '<path d="M34 64 Q50 78 66 64 L68 72 Q50 86 32 72Z" fill="#ef4444"/><path d="M58 74 L66 92 L58 94 L52 78Z" fill="#dc2626"/><path d="M36 69 Q50 80 64 69" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="1.5" stroke-dasharray="3 3"/>', 'free', 0, 0, true),
 ('mustache', '멋진 콧수염', '신사의 콧수염', 'face', '<path d="M50 55 C46 50 38 52 37 57 C42 56 46 58 50 56 C54 58 58 56 63 57 C62 52 54 50 50 55Z" fill="#3f2a1d"/>', 'free', 0, 0, true),
 ('star_cheek', '별 볼터치', '볼에 반짝 별', 'face', '<path d="M31 56 l1.6 3.2 3.4.5 -2.5 2.4 .6 3.4 -3.1 -1.6 -3.1 1.6 .6 -3.4 -2.5 -2.4 3.4 -.5Z M69 56 l1.6 3.2 3.4.5 -2.5 2.4 .6 3.4 -3.1 -1.6 -3.1 1.6 .6 -3.4 -2.5 -2.4 3.4 -.5Z" fill="#fbbf24"/>', 'free', 0, 0, true),
 ('party_hat', '파티 모자', '파티 분위기!', 'hat', '<path d="M50 -2 L66 34 H34Z" fill="#8b5cf6"/><path d="M40 22 L60 22 M37 29 L63 29" stroke="#fde047" stroke-width="3"/><circle cx="50" cy="-1" r="4.5" fill="#f472b6"/>', 'price', 0, 30, true),
 ('star_shades', '별 선글라스', '반짝반짝 선글라스', 'face', '<path d="M40 38 l2.5 5 5.5.8 -4 3.9 1 5.5 -5 -2.6 -5 2.6 1 -5.5 -4 -3.9 5.5 -.8Z M60 38 l2.5 5 5.5.8 -4 3.9 1 5.5 -5 -2.6 -5 2.6 1 -5.5 -4 -3.9 5.5 -.8Z" fill="#fbbf24" stroke="#b45309" stroke-width="1.5" stroke-linejoin="round"/><path d="M47 47 H53" stroke="#b45309" stroke-width="2"/>', 'price', 0, 50, true),
 ('balloon', '풍선', '둥실둥실 풍선', 'deco', '<path d="M86 60 Q84 74 88 86" fill="none" stroke="#94a3b8" stroke-width="1.2"/><ellipse cx="84" cy="48" rx="8" ry="10" fill="#ef4444"/><path d="M82 56 l2 3 2 -3Z" fill="#dc2626"/><ellipse cx="81" cy="44" rx="2" ry="3" fill="#fff" fill-opacity=".55"/>', 'price', 0, 40, true),
 ('cape', '영웅 망토', 'Silver 티어 이상', 'back', '<path d="M30 66 Q50 72 70 66 L88 100 L12 100Z" fill="#dc2626"/><path d="M50 72 L50 100" stroke="#b91c1c" stroke-width="2"/>', 'tier', 1, 0, true),
 ('wings', '천사 날개', '500점 달성', 'back', '<path d="M30 68 C10 52 2 40 6 28 C16 32 24 38 36 54Z M70 68 C90 52 98 40 94 28 C84 32 76 38 64 54Z" fill="#fff" stroke="#cbd5e1" stroke-width="1.5" stroke-linejoin="round"/>', 'score', 500, 0, true),
 ('halo', '천사 고리', '1,500점 달성', 'hat', '<ellipse cx="50" cy="12" rx="17" ry="5" fill="none" stroke="#facc15" stroke-width="4"/>', 'score', 1500, 0, true),
 ('flame_aura', '불꽃 오라', 'Gold 티어 이상', 'deco', '<path d="M12 90 C6 78 14 70 12 60 C20 68 22 78 18 90Z M88 90 C94 78 86 70 88 60 C80 68 78 78 82 90Z" fill="#f97316"/><path d="M13 90 C11 82 15 78 14 72 C18 77 18 84 16 90Z M87 90 C89 82 85 78 86 72 C82 77 82 84 84 90Z" fill="#fde047"/>', 'tier', 2, 0, true),
 ('gold_crown', '황금 왕관', 'Platinum 티어 이상', 'hat', '<path d="M26 32 L28 8 L40 20 L50 2 L60 20 L72 8 L74 32Z" fill="#fbbf24" stroke="#b45309" stroke-width="1.5" stroke-linejoin="round"/><circle cx="50" cy="22" r="3" fill="#ef4444"/><circle cx="36" cy="25" r="2" fill="#38bdf8"/><circle cx="64" cy="25" r="2" fill="#38bdf8"/>', 'tier', 3, 0, true),
 ('trophy', '우승 트로피', '특별 문제 보상용', 'deco', '<path d="M8 68 H24 V72 C24 80 20 84 16 84 C12 84 8 80 8 72Z" fill="#fbbf24" stroke="#b45309" stroke-width="1.2"/><rect x="13" y="84" width="6" height="5" fill="#b45309"/><rect x="9" y="89" width="14" height="4" rx="1.5" fill="#92400e"/>', 'reward', 0, 0, true),
 ('sparkles', '반짝이', '주변에 반짝반짝', 'deco', '<g fill="#fde047"><path d="M14 22 l2 5 5 2 -5 2 -2 5 -2 -5 -5 -2 5 -2Z"/><path d="M86 30 l1.6 4 4 1.6 -4 1.6 -1.6 4 -1.6 -4 -4 -1.6 4 -1.6Z"/><path d="M80 10 l1.2 3 3 1.2 -3 1.2 -1.2 3 -1.2 -3 -3 -1.2 3 -1.2Z"/></g>', 'price', 0, 25, true)
on conflict (id) do nothing;
