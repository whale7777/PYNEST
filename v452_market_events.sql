-- =====================================================================
--  PyNest V4.5.2 — 🛍️ 캐릭터 마켓(학생 업로드→승인→판매, 수수료 20%) · 🎪 행사
--  * 새 표/컬럼/함수만 "추가"해요. 기존 데이터는 그대로예요. 여러 번 실행해도 안전해요.
--  * 먼저 v450_growth.sql, v451_items.sql, v451b_items100.sql 이 실행돼 있어야 해요.
--  [마켓] 학생이 아이템 그림을 올리면 → 선생님이 승인해야 마켓에 올라가요. 팔릴 때마다 가격의 80%가 만든 학생의 파이포인트로 들어와요.
--  [행사] 기간·설명·파이포인트 배수(예: 2배)·한정 아이템을 정해요. 행사 중에는 홈에 배너가 떠요.
-- =====================================================================
do $$
begin
  if to_regclass('public.avatar_items') is null or to_regprocedure('public.item_ok(public.avatar_items,jsonb)') is null then
    raise exception 'v451_items.sql 과 v451b_items100.sql 을 먼저 실행해주세요.';
  end if;
end $$;

-- 1) 행사
create table if not exists public.events (
  id int generated always as identity primary key,
  title text not null check (length(title) between 1 and 40),
  descr text not null default '' check (length(descr) <= 300),
  emoji text not null default '🎉' check (length(emoji) <= 8),
  tone text not null default 'orange' check (tone in ('blue', 'green', 'orange', 'purple', 'red', 'gold', 'teal', 'pink')),
  starts_at timestamptz not null,
  ends_at timestamptz not null,
  py_mult numeric(3, 1) not null default 1 check (py_mult >= 1 and py_mult <= 10),
  status text not null default 'on' check (status in ('on', 'off')),
  created_at timestamptz not null default now(),
  check (ends_at > starts_at)
);
alter table public.events enable row level security;
revoke all on public.events from anon, authenticated;
grant select on public.events to authenticated;
drop policy if exists events_read on public.events;
create policy events_read on public.events for select to authenticated using (public.is_approved());

-- 2) 아이템 표 확장: 마켓/행사
alter table public.avatar_items add column if not exists event_id int references public.events(id) on delete set null;
alter table public.avatar_items add column if not exists market boolean not null default false;
alter table public.avatar_items add column if not exists reject_note text not null default '';
alter table public.avatar_items drop constraint if exists avatar_items_status_check;
alter table public.avatar_items add constraint avatar_items_status_check check (status in ('active', 'hidden', 'pending', 'rejected'));
drop policy if exists avatar_items_read on public.avatar_items;
create policy avatar_items_read on public.avatar_items for select to authenticated
  using (public.is_approved() and (status = 'active' or created_by = auth.uid() or coalesce(public.staff_role(), '') in ('owner', 'admin')));

create or replace function public.py_event_mult() returns numeric
language sql stable security definer set search_path = public
as $$ select coalesce(max(py_mult), 1)::numeric from public.events where status = 'on' and now() >= starts_at and now() < ends_at $$;

create or replace function public.event_active() returns jsonb
language sql stable security definer set search_path = public
as $$
  select coalesce(jsonb_agg(jsonb_build_object('id', id, 'title', title, 'descr', descr, 'emoji', emoji, 'tone', tone,
           'ends_at', ends_at, 'starts_at', starts_at, 'mult', py_mult,
           'items', (select count(*) from public.avatar_items i where i.event_id = e.id and i.status = 'active')) order by ends_at), '[]'::jsonb)
    from public.events e where status = 'on' and now() >= starts_at and now() < ends_at and public.is_approved()
$$;

-- 행사 아이템: 행사 중에만 (무료면 받기, 가격이 있으면 구입)
create or replace function public.item_ok(i public.avatar_items, p jsonb) returns boolean
language sql stable
as $$
  select case i.kind
    when 'score' then (p ->> 'score')::int >= i.val
    when 'tier' then (p ->> 'tier')::int >= i.val
    when 'streak' then (p ->> 'streak')::int >= i.val
    when 'rank1' then (p ->> 'wins')::int >= i.val
    when 'event' then i.price = 0 and exists (select 1 from public.events e where e.id = i.event_id and e.status = 'on' and now() >= e.starts_at and now() < e.ends_at)
    else false end
$$;
revoke all on function public.item_ok(public.avatar_items, jsonb) from public, anon, authenticated;

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
        'id', i.id, 'name', i.name, 'descr', i.descr, 'slot', i.slot, 'kind', i.kind, 'val', i.val, 'price', i.price,
        'market', i.market, 'creator', case when i.market then i.created_by end,
        'ev', i.kind = 'event' and exists (select 1 from public.events e where e.id = i.event_id and e.status = 'on' and now() >= e.starts_at and now() < e.ends_at),
        'owned', v_staff or i.kind = 'free' or exists (select 1 from public.avatar_inventory v where v.user_id = v_me and v.item_id = i.id),
        'can_claim', public.item_ok(i, v_p),
        'sales', case when i.market then (select count(*) from public.py_ledger l where l.reason = 'market_sale' and l.ref = i.id) end)
        order by i.market, i.slot, array_position(array['free', 'score', 'streak', 'tier', 'rank1', 'price', 'event', 'reward'], i.kind), i.val, i.price, i.id), '[]'::jsonb)
      from public.avatar_items i where i.status = 'active'));
end $$;

-- 구입: 일반(price) · 행사(event, 가격>0 & 행사 중) · 마켓(만든 학생에게 80%)
create or replace function public.item_buy(p_item text) returns text
language plpgsql security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); i public.avatar_items; v_net int;
begin
  if v_me is null or not public.py_is_student(v_me) then return 'nouser'; end if;
  select * into i from public.avatar_items where id = p_item and status = 'active'
    and (kind = 'price' or (kind = 'event' and price > 0 and exists (select 1 from public.events e where e.id = event_id and e.status = 'on' and now() >= e.starts_at and now() < e.ends_at)));
  if not found then return 'nouser'; end if;
  if exists (select 1 from public.avatar_inventory where user_id = v_me and item_id = i.id) or i.created_by = v_me and i.market then return 'have'; end if;
  begin
    perform public.py_add(v_me, -i.price, 'item_buy', i.id, i.name);
  exception when others then return 'poor';
  end;
  insert into public.avatar_inventory (user_id, item_id, source) values (v_me, i.id, case when i.market then 'market' else 'buy' end);
  if i.market and i.created_by is not null then
    v_net := (i.price * 80) / 100;                     -- 수수료 20%
    if v_net > 0 then
      perform public.py_add(i.created_by, v_net, 'market_sale', i.id, i.name || ' 판매');
      perform public.py_notify(i.created_by, '💰 내 아이템이 팔렸어요!', i.name || ' · 파이포인트 +' || v_net, 'item', '#/me/avatar');
    end if;
  end if;
  return 'ok';
end $$;

-- 3) 마켓: 학생 업로드
create or replace function public.market_submit(p jsonb) returns text
language plpgsql security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); v_id text := nullif(p ->> 'id', ''); v_price int; v_old public.avatar_items;
begin
  if v_me is null or not public.py_is_student(v_me) then return 'nouser'; end if;
  v_price := (p ->> 'price')::int;
  if v_price is null or v_price < 10 or v_price > 2000 then return 'price'; end if;
  if v_id is not null then
    select * into v_old from public.avatar_items where id = v_id and created_by = v_me and market;
    if not found or v_old.status not in ('pending', 'rejected') then return 'nouser'; end if;
    update public.avatar_items set name = left(p ->> 'name', 30), descr = left(coalesce(p ->> 'descr', ''), 120), slot = p ->> 'slot',
      svg = p ->> 'svg', price = v_price, status = 'pending', reject_note = '' where id = v_id;
    return 'ok';
  end if;
  if (select count(*) from public.avatar_items where created_by = v_me and market and status = 'pending') >= 5 then return 'many'; end if;
  if (select count(*) from public.avatar_items where created_by = v_me and market) >= 40 then return 'limit'; end if;
  v_id := 'm' || substr(md5(random()::text || clock_timestamp()::text || v_me::text), 1, 10);
  insert into public.avatar_items (id, name, descr, slot, svg, kind, val, price, status, market, created_by)
  values (v_id, left(p ->> 'name', 30), left(coalesce(p ->> 'descr', ''), 120), p ->> 'slot', p ->> 'svg', 'price', 0, v_price, 'pending', true, v_me);
  return 'ok';
exception when others then return 'invalid';
end $$;

create or replace function public.market_mine() returns jsonb
language sql stable security definer set search_path = public
as $$
  select coalesce(jsonb_agg(jsonb_build_object('id', i.id, 'name', i.name, 'slot', i.slot, 'price', i.price, 'status', i.status, 'note', i.reject_note,
    'descr', i.descr, 'svg', i.svg,
    'sales', (select count(*) from public.py_ledger l where l.reason = 'market_sale' and l.ref = i.id),
    'earned', (select coalesce(sum(delta), 0) from public.py_ledger l where l.reason = 'market_sale' and l.ref = i.id)) order by i.created_at desc), '[]'::jsonb)
    from public.avatar_items i where i.created_by = auth.uid() and i.market
$$;

create or replace function public.market_withdraw(p_id text) returns text
language plpgsql security definer set search_path = public
as $$
begin
  update public.avatar_items set status = 'hidden' where id = p_id and created_by = auth.uid() and market and status in ('active', 'pending');
  return 'ok';
end $$;

create or replace function public.market_review(p_id text, p_ok boolean, p_note text default '') returns text
language plpgsql security definer set search_path = public
as $$
declare i public.avatar_items;
begin
  if coalesce(public.staff_role(), '') not in ('owner', 'admin') then return 'forbidden'; end if;
  select * into i from public.avatar_items where id = p_id and market and status = 'pending';
  if not found then return 'nouser'; end if;
  if p_ok then
    update public.avatar_items set status = 'active', reject_note = '' where id = p_id;
    insert into public.avatar_inventory (user_id, item_id, source) values (i.created_by, p_id, 'creator') on conflict do nothing;
    perform public.py_notify(i.created_by, '✅ 마켓에 올라갔어요: ' || i.name, '다른 친구들이 사면 파이포인트가 들어와요!', 'item', '#/me/avatar');
  else
    update public.avatar_items set status = 'rejected', reject_note = left(coalesce(p_note, ''), 200) where id = p_id;
    perform public.py_notify(i.created_by, '아이템이 반려됐어요: ' || i.name, coalesce(nullif(btrim(p_note), ''), '고쳐서 다시 올려주세요.'), 'item', '#/me/avatar');
  end if;
  return 'ok';
end $$;

-- 4) 행사 관리(관리자)
create or replace function public.event_upsert(p jsonb) returns text
language plpgsql security definer set search_path = public
as $$
declare v_id int := nullif(p ->> 'id', '')::int;
begin
  if coalesce(public.staff_role(), '') not in ('owner', 'admin') then return 'forbidden'; end if;
  if v_id is null then
    insert into public.events (title, descr, emoji, tone, starts_at, ends_at, py_mult, status)
    values (p ->> 'title', coalesce(p ->> 'descr', ''), coalesce(nullif(p ->> 'emoji', ''), '🎉'), coalesce(p ->> 'tone', 'orange'),
            (p ->> 'starts_at')::timestamptz, (p ->> 'ends_at')::timestamptz, coalesce((p ->> 'py_mult')::numeric, 1), coalesce(p ->> 'status', 'on'));
  else
    update public.events set title = p ->> 'title', descr = coalesce(p ->> 'descr', ''), emoji = coalesce(nullif(p ->> 'emoji', ''), '🎉'),
      tone = coalesce(p ->> 'tone', 'orange'), starts_at = (p ->> 'starts_at')::timestamptz, ends_at = (p ->> 'ends_at')::timestamptz,
      py_mult = coalesce((p ->> 'py_mult')::numeric, 1), status = coalesce(p ->> 'status', 'on') where id = v_id;
  end if;
  return 'ok';
exception when others then return 'invalid';
end $$;
create or replace function public.event_delete(p_id int) returns text
language plpgsql security definer set search_path = public
as $$
begin
  if coalesce(public.staff_role(), '') not in ('owner', 'admin') then return 'forbidden'; end if;
  delete from public.events where id = p_id;
  return 'ok';
end $$;
-- 아이템을 행사에 붙이기 (조건이 "행사 한정"으로 바뀌어요). p_event 가 null 이면 떼기(= 숨김 처리)
create or replace function public.event_item_set(p_event int, p_item text, p_price int default 0) returns text
language plpgsql security definer set search_path = public
as $$
begin
  if coalesce(public.staff_role(), '') not in ('owner', 'admin') then return 'forbidden'; end if;
  if p_event is null then
    update public.avatar_items set event_id = null, status = 'hidden' where id = p_item and kind = 'event';
  else
    update public.avatar_items set kind = 'event', event_id = p_event, price = greatest(coalesce(p_price, 0), 0), val = 0 where id = p_item and not market;
  end if;
  return 'ok';
exception when others then return 'invalid';
end $$;

revoke all on function public.event_active(), public.market_submit(jsonb), public.market_mine(), public.market_withdraw(text),
  public.market_review(text, boolean, text), public.event_upsert(jsonb), public.event_delete(int), public.event_item_set(int, text, int),
  public.item_catalog(), public.item_buy(text) from public, anon;
grant execute on function public.event_active(), public.market_submit(jsonb), public.market_mine(), public.market_withdraw(text),
  public.market_review(text, boolean, text), public.event_upsert(jsonb), public.event_delete(int), public.event_item_set(int, text, int),
  public.item_catalog(), public.item_buy(text) to authenticated;
