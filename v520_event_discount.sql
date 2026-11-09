-- =====================================================================
--  PyNest V5.2.1 — 🏷️ 행사 아이템 할인 (n%)
--  * 행사에 "할인율"과 "대상"을 정할 수 있어요. 행사 중에만 적용돼요.
--      대상 shop  : 상점의 파이포인트 구매 아이템 전체 (마켓에서 학생이 판 아이템은 제외)
--      대상 event : 이 행사에 붙인 한정 아이템만
--  * 새 컬럼/함수만 바꿔요. 여러 번 실행해도 안전해요. v452_market_events.sql, v453b_economy.sql 이 먼저 실행돼 있어야 해요.
-- =====================================================================
alter table public.events add column if not exists disc_pct int not null default 0;
alter table public.events add column if not exists disc_scope text not null default 'shop';
alter table public.events drop constraint if exists events_disc_pct_check;
alter table public.events add constraint events_disc_pct_check check (disc_pct >= 0 and disc_pct <= 90);
alter table public.events drop constraint if exists events_disc_scope_check;
alter table public.events add constraint events_disc_scope_check check (disc_scope in ('shop', 'event'));

-- 할인 전 가격 (기본 가격 × 상점 배수)
create or replace function public.item_price_full(i public.avatar_items) returns integer
language sql stable security definer set search_path = public
as $$
  select case when i.market or i.price <= 0 then i.price
              else greatest(1, round(i.price * coalesce(nullif(public.py_cfg('item_price_mult', '3'::jsonb) #>> '{}', '')::numeric, 1)))::int end
$$;

-- 지금 이 아이템에 적용되는 행사 할인율 (여러 행사가 겹치면 가장 큰 것 하나)
create or replace function public.item_disc(i public.avatar_items) returns integer
language sql stable security definer set search_path = public
as $$
  select case when i.market or i.price <= 0 then 0
    else coalesce((select max(e.disc_pct) from public.events e
      where e.status = 'on' and e.disc_pct > 0 and now() >= e.starts_at and now() < e.ends_at
        and ((i.kind = 'price' and e.disc_scope = 'shop') or (i.kind = 'event' and e.id = i.event_id))), 0) end
$$;

-- 실제로 내는 가격 (구입 함수 item_buy 가 이걸 써서 자동으로 할인돼요)
create or replace function public.item_price(i public.avatar_items) returns integer
language sql stable security definer set search_path = public
as $$
  select case when public.item_disc(i) > 0
              then greatest(1, round(public.item_price_full(i) * (100 - public.item_disc(i)) / 100.0))::int
              else public.item_price_full(i) end
$$;
revoke all on function public.item_price_full(public.avatar_items), public.item_disc(public.avatar_items), public.item_price(public.avatar_items) from public, anon, authenticated; -- 구입·카탈로그 함수(security definer) 안에서만 불러요

-- 카탈로그에 할인 전 가격(full_price)·할인율(disc) 추가
create or replace function public.item_catalog() returns jsonb
language plpgsql stable security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); v_p jsonb; v_staff boolean := coalesce(public.staff_role(), '') <> '';
begin
  if v_me is null or not public.is_approved() then return null; end if;
  v_p := public.item_progress(v_me);
  return v_p || jsonb_build_object(
    'py', coalesce((select balance from public.py_wallet where user_id = v_me), 0),
    'items', (select coalesce(jsonb_agg(jsonb_build_object(
        'id', i.id, 'name', i.name, 'descr', i.descr, 'slot', i.slot, 'kind', i.kind, 'val', i.val,
        'price', public.item_price(i), 'full_price', public.item_price_full(i), 'disc', public.item_disc(i), 'base_price', i.price,
        'market', i.market, 'creator', case when i.market then i.created_by end,
        'ev', i.kind = 'event' and exists (select 1 from public.events e where e.id = i.event_id and e.status = 'on' and now() >= e.starts_at and now() < e.ends_at),
        'owned', v_staff or i.kind = 'free' or exists (select 1 from public.avatar_inventory v where v.user_id = v_me and v.item_id = i.id),
        'can_claim', public.item_ok(i, v_p),
        'sales', case when i.market then (select count(*) from public.py_ledger l where l.reason = 'market_sale' and l.ref = i.id) end)
        order by i.market, i.slot, array_position(array['free', 'score', 'streak', 'tier', 'rank1', 'price', 'event', 'reward'], i.kind), i.val, i.price, i.id), '[]'::jsonb)
      from public.avatar_items i where i.status = 'active'));
end $$;

-- 홈 배너용: 진행 중인 행사에 할인율 추가
create or replace function public.event_active() returns jsonb
language sql stable security definer set search_path = public
as $$
  select coalesce(jsonb_agg(jsonb_build_object('id', id, 'title', title, 'descr', descr, 'emoji', emoji, 'tone', tone,
           'ends_at', ends_at, 'starts_at', starts_at, 'mult', py_mult, 'disc', disc_pct, 'disc_scope', disc_scope,
           'items', (select count(*) from public.avatar_items i where i.event_id = e.id and i.status = 'active')) order by ends_at), '[]'::jsonb)
    from public.events e where status = 'on' and now() >= starts_at and now() < ends_at and public.is_approved()
$$;

-- 행사 저장(관리자)에 할인율·대상 추가
create or replace function public.event_upsert(p jsonb) returns text
language plpgsql security definer set search_path = public
as $$
declare v_id int := nullif(p ->> 'id', '')::int; v_disc int := coalesce(nullif(p ->> 'disc_pct', '')::int, 0); v_scope text := coalesce(nullif(p ->> 'disc_scope', ''), 'shop');
begin
  if coalesce(public.staff_role(), '') not in ('owner', 'admin') then return 'forbidden'; end if;
  if v_disc < 0 or v_disc > 90 or v_scope not in ('shop', 'event') then return 'invalid'; end if;
  if v_id is null then
    insert into public.events (title, descr, emoji, tone, starts_at, ends_at, py_mult, status, disc_pct, disc_scope)
    values (p ->> 'title', coalesce(p ->> 'descr', ''), coalesce(nullif(p ->> 'emoji', ''), '🎉'), coalesce(p ->> 'tone', 'orange'),
            (p ->> 'starts_at')::timestamptz, (p ->> 'ends_at')::timestamptz, coalesce((p ->> 'py_mult')::numeric, 1), coalesce(p ->> 'status', 'on'), v_disc, v_scope);
  else
    update public.events set title = p ->> 'title', descr = coalesce(p ->> 'descr', ''), emoji = coalesce(nullif(p ->> 'emoji', ''), '🎉'),
      tone = coalesce(p ->> 'tone', 'orange'), starts_at = (p ->> 'starts_at')::timestamptz, ends_at = (p ->> 'ends_at')::timestamptz,
      py_mult = coalesce((p ->> 'py_mult')::numeric, 1), status = coalesce(p ->> 'status', 'on'), disc_pct = v_disc, disc_scope = v_scope where id = v_id;
  end if;
  return 'ok';
exception when others then return 'invalid';
end $$;
