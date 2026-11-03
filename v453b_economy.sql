-- PyNest V4.5.3b · v453b_economy.sql
-- 1) 배지 보상(파이포인트)  2) 아이템 가격 배율(관리자 설정)  3) 파이포인트 쓰는 곳: 🎰 뽑기 · 🎁 선물
-- v453_board_badges.sql 다음에 한 번만 실행하세요. (여러 번 실행해도 안전해요)

do $$
begin
  if to_regclass('public.badge_defs') is null or to_regclass('public.avatar_items') is null or to_regclass('public.py_config') is null then
    raise exception 'v450 / v451b / v452 / v453 SQL 을 먼저 실행해주세요.';
  end if;
  if not exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'badge_defs' and column_name = 'tone')
     or not exists (select 1 from public.badge_defs where kind = 'tier') then
    raise exception 'v453_board_badges.sql 을 먼저 실행해주세요.';
  end if;
end $$;

-- 0) 설정 기본값 (이미 있으면 그대로)
insert into public.py_config (key, val) values
  ('badge_reward', '{"blue":10,"green":15,"teal":20,"orange":30,"red":40,"purple":60,"pink":80,"gold":150}'::jsonb),
  ('item_price_mult', '3'::jsonb),
  ('gacha', '{"basic":150,"premium":500}'::jsonb),
  ('gift', '{"fee":10,"min":10,"max":500,"daily":1000}'::jsonb)
on conflict (key) do nothing;

-- 1) 배지 보상
alter table public.badge_defs add column if not exists reward int check (reward is null or reward between 0 and 100000);
drop index if exists public.py_ledger_once;
create unique index if not exists py_ledger_once on public.py_ledger (user_id, reason, ref)
  where ref is not null and reason in ('solve', 'learn', 'rank_week', 'rank_month', 'exam_rank', 'item_reward', 'event_claim', 'badge');

create or replace function public.badge_reward_of(b public.badge_defs) returns int
language sql stable security definer set search_path = public
as $$ select greatest(coalesce(b.reward, nullif(public.py_cfg('badge_reward', '{}'::jsonb) ->> b.tone, '')::int, 0), 0) $$;
revoke all on function public.badge_reward_of(public.badge_defs) from public, anon, authenticated;

create or replace function public.badge_reward_map() returns jsonb
language sql stable security definer set search_path = public
as $$ select case when public.is_approved() then coalesce((select jsonb_object_agg(b.id, public.badge_reward_of(b)) from public.badge_defs b), '{}'::jsonb) end $$;
revoke all on function public.badge_reward_map() from public, anon;
grant execute on function public.badge_reward_map() to authenticated;

-- 배지를 받을 때 파이포인트 지급 (badges_check 와 직접 지급 둘 다)
create or replace function public.badge_pay(p_uid uuid, b public.badge_defs) returns int
language plpgsql security definer set search_path = public
as $$
declare v_r int := public.badge_reward_of(b);
begin
  if v_r > 0 and public.py_is_student(p_uid) then
    perform public.py_add(p_uid, v_r, 'badge', b.id, b.name);
  end if;
  return v_r;
end $$;
revoke all on function public.badge_pay(uuid, public.badge_defs) from public, anon, authenticated;

create or replace function public.badges_check() returns jsonb
language plpgsql security definer set search_path = public
as $$
declare
  v_me uuid := auth.uid();
  v_score int := 0; v_solved int := 0; v_best int := 0; v_learn int := 0; v_first int := 0; v_join int := 0; v_py int := 0;
  v_tier int := 0; v_wins int := 0; v_items int := 0; v_sales int := 0; v_made int := 0; v_att int := 0; v_ev int := 0; v_sh int := 0;
  v_posts int := 0; v_cmts int := 0;
  b public.badge_defs; v_rw int; v_new jsonb := '[]'::jsonb; v_val int;
begin
  if v_me is null or not public.py_is_student(v_me) then return '[]'::jsonb; end if;
  select coalesce(pts, 0), coalesce(solved, 0) into v_score, v_solved from public.rk_scores(null) where uid = v_me;
  v_score := coalesce(v_score, 0); v_solved := coalesce(v_solved, 0);
  v_best := coalesce((public.streak_info() ->> 'best')::int, 0);
  v_tier := public.tier_major(v_score);
  if to_regclass('public.learn_progress') is not null then
    execute 'select count(*) from public.learn_progress where user_id = $1 and completed' into v_learn using v_me;
  end if;
  if to_regclass('public.exam_results') is not null then
    execute 'select count(*) from public.exam_results where user_id = $1' into v_join using v_me;
    execute 'select count(*) from public.exam_results where user_id = $1 and final_rank = 1' into v_first using v_me;
  end if;
  select coalesce(sum(delta), 0) into v_py from public.py_ledger where user_id = v_me and delta > 0;
  select count(*) into v_wins from public.rank_wins where user_id = v_me;
  select count(*) into v_items from public.avatar_inventory where user_id = v_me;
  select count(*) into v_sales from public.py_ledger where user_id = v_me and reason = 'market_sale';
  select count(*) into v_made from public.avatar_items where created_by = v_me and market and status = 'active';
  select count(*) into v_att from public.attendance where user_id = v_me and kind = 'learn';
  select count(*) into v_ev from public.py_ledger where user_id = v_me and reason = 'event_claim';
  select count(*) into v_sh from public.py_ledger where user_id = v_me and reason = 'shield';
  select count(*) into v_posts from public.posts where author_id = v_me and board <> 'notice' and auto_key is null;
  select count(*) into v_cmts from public.comments where author_id = v_me;
  for b in select * from public.badge_defs where kind <> 'manual' and threshold > 0 order by position loop
    v_val := case b.kind when 'score' then v_score when 'solved' then v_solved when 'streak' then v_best when 'learn' then v_learn
                         when 'exam_join' then v_join when 'exam_first' then v_first when 'pypoint' then v_py
                         when 'tier' then v_tier when 'rank1' then v_wins when 'items' then v_items when 'sales' then v_sales
                         when 'market_made' then v_made when 'attend' then v_att when 'event' then v_ev when 'shield' then v_sh
                         when 'posts' then v_posts when 'comments' then v_cmts else 0 end;
    if v_val >= b.threshold then
      insert into public.user_badges (user_id, badge_id) values (v_me, b.id) on conflict do nothing;
      if found then
        v_rw := public.badge_pay(v_me, b);
        v_new := v_new || jsonb_build_object('id', b.id, 'name', b.name, 'icon', b.icon, 'reward', v_rw);
        perform public.py_notify(v_me, '🎖️ 새 배지: ' || b.name, b.descr || case when v_rw > 0 then ' · 💎 +' || v_rw else '' end, 'badge', '#/me/badges');
      end if;
    end if;
  end loop;
  return v_new;
end $$;


-- 직접 지급 / 회수 (지급할 때도 보상)
create or replace function public.badge_award(p_uid uuid, p_id text, p_on boolean default true) returns text
language plpgsql security definer set search_path = public
as $$
declare b public.badge_defs; v_rw int := 0;
begin
  if coalesce(public.staff_role(), '') not in ('owner', 'admin') then return 'forbidden'; end if;
  select * into b from public.badge_defs where id = p_id;
  if not found or not public.py_is_student(p_uid) then return 'nouser'; end if;
  if p_on then
    insert into public.user_badges (user_id, badge_id) values (p_uid, p_id) on conflict do nothing;
    if found then
      v_rw := public.badge_pay(p_uid, b);
      perform public.py_notify(p_uid, '🎖️ 새 배지: ' || b.name, b.descr || case when v_rw > 0 then ' · 💎 +' || v_rw else '' end, 'badge', '#/me/badges');
    end if;
  else
    delete from public.user_badges where user_id = p_uid and badge_id = p_id;
  end if;
  return 'ok';
end $$;

-- 배지 만들기/고치기 (보상 칸 포함: 비우면 색 기본값)
create or replace function public.badge_upsert(p jsonb) returns text
language plpgsql security definer set search_path = public
as $$
declare v_rw int := nullif(p ->> 'reward', '')::int;
begin
  if coalesce(public.staff_role(), '') not in ('owner', 'admin') then return 'forbidden'; end if;
  insert into public.badge_defs (id, name, descr, icon, kind, threshold, tone, position, reward)
  values (p ->> 'id', p ->> 'name', coalesce(p ->> 'descr', ''), coalesce(nullif(p ->> 'icon', ''), '🏅'), coalesce(p ->> 'kind', 'manual'),
          coalesce((p ->> 'threshold')::int, 0), coalesce(p ->> 'tone', 'blue'), coalesce((p ->> 'position')::int, 100), v_rw)
  on conflict (id) do update set name = excluded.name, descr = excluded.descr, icon = excluded.icon, kind = excluded.kind,
    threshold = excluded.threshold, tone = excluded.tone, position = excluded.position, reward = excluded.reward;
  return 'ok';
exception when others then return 'invalid';
end $$;

-- 설정 저장 (새 키 허용)
create or replace function public.py_cfg_set(p_key text, p_val jsonb) returns text
language plpgsql security definer set search_path = public
as $$
begin
  if coalesce(public.staff_role(), '') not in ('owner', 'admin') then return 'forbidden'; end if;
  if p_key not in ('week_rank', 'month_rank', 'solve_rand', 'learn_rand', 'shield_price', 'shield_max', 'badge_reward', 'item_price_mult', 'gacha', 'gift') then return 'invalid'; end if;
  if p_key = 'item_price_mult' and (jsonb_typeof(p_val) <> 'number' or (p_val #>> '{}')::numeric not between 0.1 and 100) then return 'invalid'; end if;
  if p_key in ('badge_reward', 'gacha', 'gift') and jsonb_typeof(p_val) <> 'object' then return 'invalid'; end if;
  insert into public.py_config (key, val) values (p_key, p_val) on conflict (key) do update set val = excluded.val, updated_at = now();
  return 'ok';
end $$;

-- 2) 아이템 가격 배율 (마켓 상품은 학생이 정한 가격 그대로)
create or replace function public.item_price(i public.avatar_items) returns int
language sql stable security definer set search_path = public
as $$
  select case when i.market or i.price <= 0 then i.price
              else greatest(1, round(i.price * coalesce(nullif(public.py_cfg('item_price_mult', '3'::jsonb) #>> '{}', '')::numeric, 1)))::int end
$$;
revoke all on function public.item_price(public.avatar_items) from public, anon, authenticated;

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
        'id', i.id, 'name', i.name, 'descr', i.descr, 'slot', i.slot, 'kind', i.kind, 'val', i.val, 'price', public.item_price(i), 'base_price', i.price,
        'market', i.market, 'creator', case when i.market then i.created_by end,
        'ev', i.kind = 'event' and exists (select 1 from public.events e where e.id = i.event_id and e.status = 'on' and now() >= e.starts_at and now() < e.ends_at),
        'owned', v_staff or i.kind = 'free' or exists (select 1 from public.avatar_inventory v where v.user_id = v_me and v.item_id = i.id),
        'can_claim', public.item_ok(i, v_p),
        'sales', case when i.market then (select count(*) from public.py_ledger l where l.reason = 'market_sale' and l.ref = i.id) end)
        order by i.market, i.slot, array_position(array['free', 'score', 'streak', 'tier', 'rank1', 'price', 'event', 'reward'], i.kind), i.val, i.price, i.id), '[]'::jsonb)
      from public.avatar_items i where i.status = 'active'));
end $$;

create or replace function public.item_buy(p_item text) returns text
language plpgsql security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); i public.avatar_items; v_net int; v_price int;
begin
  if v_me is null or not public.py_is_student(v_me) then return 'nouser'; end if;
  select * into i from public.avatar_items where id = p_item and status = 'active'
    and (kind = 'price' or (kind = 'event' and price > 0 and exists (select 1 from public.events e where e.id = event_id and e.status = 'on' and now() >= e.starts_at and now() < e.ends_at)));
  if not found then return 'nouser'; end if;
  if exists (select 1 from public.avatar_inventory where user_id = v_me and item_id = i.id) or i.created_by = v_me and i.market then return 'have'; end if;
  v_price := public.item_price(i);
  begin
    perform public.py_add(v_me, -v_price, 'item_buy', i.id, i.name);
  exception when others then return 'poor';
  end;
  insert into public.avatar_inventory (user_id, item_id, source) values (v_me, i.id, case when i.market then 'market' else 'buy' end);
  if i.market and i.created_by is not null then
    v_net := (v_price * 80) / 100;                     -- 수수료 20%
    if v_net > 0 then
      perform public.py_add(i.created_by, v_net, 'market_sale', i.id, i.name || ' 판매');
      perform public.py_notify(i.created_by, '💰 내 아이템이 팔렸어요!', i.name || ' · 파이포인트 +' || v_net, 'item', '#/me/avatar');
    end if;
  end if;
  return 'ok';
end $$;


-- 3) 파이포인트 쓰는 곳
-- 3-1) 상점 정보 (가격 · 오늘 보낸 선물)
create or replace function public.py_shop_info() returns jsonb
language plpgsql stable security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); v_g jsonb := public.py_cfg('gift', '{"fee":10,"min":10,"max":500,"daily":1000}'::jsonb);
begin
  if v_me is null or not public.is_approved() then return null; end if;
  return jsonb_build_object('gacha', public.py_cfg('gacha', '{"basic":150,"premium":500}'::jsonb), 'gift', v_g,
    'sent_today', coalesce((select -sum(delta) from public.py_ledger where user_id = v_me and reason = 'gift_out'
                              and created_at >= (date_trunc('day', now() at time zone 'Asia/Seoul') at time zone 'Asia/Seoul')), 0),
    'mult', public.py_cfg('item_price_mult', '3'::jsonb),
    'left_basic', (select count(*) from public.avatar_items i where i.status = 'active' and not i.market and i.kind = 'price'
                     and not exists (select 1 from public.avatar_inventory v where v.user_id = v_me and v.item_id = i.id)),
    'left_premium', (select count(*) from public.avatar_items i where i.status = 'active' and not i.market and i.kind in ('price', 'score', 'streak', 'tier', 'rank1')
                     and not exists (select 1 from public.avatar_inventory v where v.user_id = v_me and v.item_id = i.id)));
end $$;
revoke all on function public.py_shop_info() from public, anon;
grant execute on function public.py_shop_info() to authenticated;

-- 3-2) 🎰 아이템 뽑기: basic = 상점 아이템, premium = 조건부 아이템까지 (아직 없는 것 중에서 무작위)
create or replace function public.py_gacha(p_tier text) returns jsonb
language plpgsql security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); v_cost int; i public.avatar_items; v_kinds text[];
begin
  if v_me is null or not public.py_is_student(v_me) then return jsonb_build_object('status', 'nouser'); end if;
  if p_tier not in ('basic', 'premium') then return jsonb_build_object('status', 'invalid'); end if;
  v_cost := coalesce((public.py_cfg('gacha', '{}'::jsonb) ->> p_tier)::int, case p_tier when 'basic' then 150 else 500 end);
  v_kinds := case p_tier when 'basic' then array['price'] else array['price', 'score', 'streak', 'tier', 'rank1'] end;
  select * into i from public.avatar_items a
   where a.status = 'active' and not a.market and a.kind = any (v_kinds)
     and not exists (select 1 from public.avatar_inventory v where v.user_id = v_me and v.item_id = a.id)
   order by random() limit 1;
  if not found then return jsonb_build_object('status', 'empty'); end if;
  begin
    perform public.py_add(v_me, -v_cost, 'gacha', null, case p_tier when 'basic' then '일반 뽑기' else '고급 뽑기' end || ' · ' || i.name);
  exception when others then return jsonb_build_object('status', 'poor');
  end;
  insert into public.avatar_inventory (user_id, item_id, source) values (v_me, i.id, 'gacha') on conflict do nothing;
  return jsonb_build_object('status', 'ok', 'item', jsonb_build_object('id', i.id, 'name', i.name, 'slot', i.slot), 'cost', v_cost);
end $$;
revoke all on function public.py_gacha(text) from public, anon;
grant execute on function public.py_gacha(text) to authenticated;

-- 3-3) 🎁 파이포인트 선물 (수수료·1회 한도·하루 한도는 관리자 설정)
create or replace function public.py_gift(p_to uuid, p_amt int) returns text
language plpgsql security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); g jsonb := public.py_cfg('gift', '{"fee":10,"min":10,"max":500,"daily":1000}'::jsonb);
        v_fee int; v_net int; v_sent int; v_name text;
begin
  if v_me is null or not public.py_is_student(v_me) or p_to is null or p_to = v_me or not public.py_is_student(p_to) then return 'nouser'; end if;
  if p_amt is null or p_amt < coalesce((g ->> 'min')::int, 10) or p_amt > coalesce((g ->> 'max')::int, 500) then return 'amount'; end if;
  select coalesce(-sum(delta), 0) into v_sent from public.py_ledger
   where user_id = v_me and reason = 'gift_out' and created_at >= (date_trunc('day', now() at time zone 'Asia/Seoul') at time zone 'Asia/Seoul');
  if v_sent + p_amt > coalesce((g ->> 'daily')::int, 1000) then return 'daily'; end if;
  v_fee := coalesce((g ->> 'fee')::int, 10);
  v_net := (p_amt * (100 - least(greatest(v_fee, 0), 100))) / 100;
  begin
    perform public.py_add(v_me, -p_amt, 'gift_out', null, '선물');
  exception when others then return 'poor';
  end;
  if v_net > 0 then
    perform public.py_add(p_to, v_net, 'gift_in', null, '친구의 선물');
    select coalesce((select nickname from public.nicknames where user_id = v_me), (select username from public.profiles where id = v_me)) into v_name;
    perform public.py_notify(p_to, '🎁 ' || coalesce(v_name, '친구') || ' 님이 선물을 보냈어요!', '파이포인트 +' || v_net, 'badge', '#/me/wallet');
  end if;
  return 'ok';
end $$;
revoke all on function public.py_gift(uuid, int) from public, anon;
grant execute on function public.py_gift(uuid, int) to authenticated;

revoke all on function public.badges_check(), public.badge_award(uuid, text, boolean), public.badge_upsert(jsonb), public.py_cfg_set(text, jsonb) from public, anon;
grant execute on function public.badges_check(), public.badge_award(uuid, text, boolean), public.badge_upsert(jsonb), public.py_cfg_set(text, jsonb) to authenticated;
revoke all on function public.item_catalog(), public.item_buy(text) from public, anon;
grant execute on function public.item_catalog(), public.item_buy(text) to authenticated;
