-- =====================================================================
--  PyNest V4.5.1b — 조건부 캐릭터 아이템 85개 추가 (기본 15 + 85 = 100)
--  * 먼저 v451_items.sql 이 실행돼 있어야 해요. 여러 번 실행해도 안전해요. 기존 데이터는 그대로예요.
--  [새 조건] streak : 연속 출석 최고 기록이 N일 이상 · rank1 : 주간/월간 랭킹 1등을 N번 한 사람
--  * 1등 횟수는 지금부터 주·월 정산할 때마다 기록돼요. 이미 정산된 1위(보상 기록이 있는 것)는 자동으로 가져와요.
-- =====================================================================
do $$
begin
  if to_regclass('public.avatar_items') is null then raise exception 'v451_items.sql 을 먼저 실행해주세요.'; end if;
end $$;

alter table public.avatar_items drop constraint if exists avatar_items_kind_check;
alter table public.avatar_items add constraint avatar_items_kind_check
  check (kind in ('free', 'score', 'streak', 'tier', 'rank1', 'price', 'reward', 'event'));

-- 랭킹 1등 기록 (보상 금액이 0이어도 남아요)
create table if not exists public.rank_wins (
  user_id uuid not null references public.profiles(id) on delete cascade,
  period_id text not null,
  primary key (user_id, period_id)
);
alter table public.rank_wins enable row level security;
revoke all on public.rank_wins from anon, authenticated;
grant select on public.rank_wins to authenticated;
drop policy if exists rank_wins_read on public.rank_wins;
create policy rank_wins_read on public.rank_wins for select to authenticated using (user_id = auth.uid() or coalesce(public.staff_role(), '') in ('owner', 'admin'));
insert into public.rank_wins (user_id, period_id)
  select user_id, ref from public.py_ledger where reason in ('rank_week', 'rank_month') and ref is not null and note like '% 1위' on conflict do nothing;

create or replace function public.py_settle_period(p_id text, p_from timestamptz, p_to timestamptz, p_cfg text, p_label text)
returns void
language plpgsql security definer set search_path = public
as $$
declare x record; v_rewards jsonb := public.py_cfg(p_cfg, '[]'); v_n int := jsonb_array_length(public.py_cfg(p_cfg, '[]'));
begin
  insert into public.py_settled (period_id) values (p_id) on conflict do nothing;
  if not found then return; end if;
  for x in
    with per as (
      select e.user_id as uid, greatest(sum(e.pts), 0)::int as sc
        from public.rk_events e
        join public.profiles p on p.id = e.user_id and p.status = 'approved' and p.role <> 'admin'
       where e.solved_at >= p_from and e.solved_at < p_to
         and not exists (select 1 from public.staff_roles sr where sr.user_id = p.id)
         and not (to_regclass('public.student_tiers') is not null and public.py_is_solver(p.id))
       group by e.user_id having sum(e.pts) > 0),
    rk as (select uid, (rank() over (order by sc desc))::int as rnk from per),
    g as (select rnk, count(*)::int as n from rk group by rnk)
    select rk.uid, rk.rnk, g.n,
           (select coalesce(sum((v_rewards ->> (s - 1))::int), 0) from generate_series(rk.rnk, rk.rnk + g.n - 1) s where s <= v_n)::int / g.n as amt
      from rk join g on g.rnk = rk.rnk where rk.rnk <= greatest(v_n, 1)
  loop
    if x.rnk = 1 then insert into public.rank_wins (user_id, period_id) values (x.uid, p_id) on conflict do nothing; end if;
    if x.amt > 0 and public.py_add(x.uid, x.amt, split_part(p_id, ':', 1), p_id, p_label || ' ' || x.rnk || '위') then
      perform public.py_notify(x.uid, '🏅 ' || p_label || ' ' || x.rnk || '위!', '파이포인트 +' || x.amt || ' 을 받았어요.', 'reward', '#/ranking');
    end if;
  end loop;
end $$;
revoke all on function public.py_settle_period(text, timestamptz, timestamptz, text, text) from public, anon, authenticated;

-- 연속 출석 최고 기록
create or replace function public.att_best(p_uid uuid) returns int
language sql stable security definer set search_path = public
as $$
  select coalesce(max(c), 0)::int from (
    select count(*) as c from (select day - (row_number() over (order by day))::int as g from public.attendance where user_id = p_uid) t group by g) x
$$;
revoke all on function public.att_best(uuid) from public, anon, authenticated;

-- 내 진행 상황 (점수 · 큰 등급 · 연속 출석 최고 · 1등 횟수)
create or replace function public.item_progress(p_uid uuid) returns jsonb
language plpgsql stable security definer set search_path = public
as $$
declare v_sc int; v_t int;
begin
  select score, tier into v_sc, v_t from public.my_score_tier(p_uid);
  return jsonb_build_object('score', v_sc, 'tier', v_t, 'streak', public.att_best(p_uid),
    'wins', (select count(*) from public.rank_wins where user_id = p_uid));
end $$;
revoke all on function public.item_progress(uuid) from public, anon, authenticated;

create or replace function public.item_ok(i public.avatar_items, p jsonb) returns boolean
language sql immutable
as $$
  select case i.kind
    when 'score' then (p ->> 'score')::int >= i.val
    when 'tier' then (p ->> 'tier')::int >= i.val
    when 'streak' then (p ->> 'streak')::int >= i.val
    when 'rank1' then (p ->> 'wins')::int >= i.val
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
        'owned', v_staff or i.kind = 'free' or exists (select 1 from public.avatar_inventory v where v.user_id = v_me and v.item_id = i.id),
        'can_claim', public.item_ok(i, v_p))
        order by i.slot, array_position(array['free', 'score', 'streak', 'tier', 'rank1', 'price', 'reward', 'event'], i.kind), i.val, i.price, i.id), '[]'::jsonb)
      from public.avatar_items i where i.status = 'active'));
end $$;

create or replace function public.item_claim(p_item text) returns text
language plpgsql security definer set search_path = public
as $$
declare v_me uuid := auth.uid(); i public.avatar_items;
begin
  if v_me is null or not public.py_is_student(v_me) then return 'nouser'; end if;
  select * into i from public.avatar_items where id = p_item and status = 'active';
  if not found then return 'nouser'; end if;
  if not public.item_ok(i, public.item_progress(v_me)) then return 'locked'; end if;
  insert into public.avatar_inventory (user_id, item_id, source) values (v_me, i.id, 'claim') on conflict do nothing;
  return 'ok';
end $$;
revoke all on function public.item_catalog(), public.item_claim(text) from public, anon;
grant execute on function public.item_catalog(), public.item_claim(text) to authenticated;

insert into public.avatar_items (id, name, descr, slot, svg, kind, val, price, builtin) values
 ('it016_beanie', '파란 비니', '랭킹 점수 150점 달성', 'hat', $svg$<path d="M24 38 C24 10 76 10 76 38Z" fill="#3b82f6"/><rect x="22" y="33" width="56" height="8" rx="4" fill="#93c5fd"/><circle cx="50" cy="10" r="5" fill="#93c5fd"/>$svg$, 'score', 150, 0, true),
 ('it017_roundglasses', '동그란 안경', '랭킹 점수 250점 달성', 'face', $svg$<g fill="#bfdbfe" fill-opacity=".35" stroke="#334155" stroke-width="2"><circle cx="40" cy="46" r="7.5"/><circle cx="60" cy="46" r="7.5"/></g><path d="M47.5 46 H52.5" stroke="#334155" stroke-width="2"/>$svg$, 'score', 250, 0, true),
 ('it018_bowtie', '빨간 나비넥타이', '랭킹 점수 400점 달성', 'outfit', $svg$<path d="M50 79 L35 70 V88Z M50 79 L65 70 V88Z" fill="#ef4444"/><circle cx="50" cy="79" r="4" fill="#fecaca"/>$svg$, 'score', 400, 0, true),
 ('it019_floathearts', '두근두근 하트', '랭킹 점수 600점 달성', 'deco', $svg$<path d="M12 30 l4 -4 l4 4 l-4 6Z M84 16 l3 -3 l3 3 l-3 5Z" fill="#ec4899"/><path d="M80 40 l2.4 -2.4 l2.4 2.4 l-2.4 3.6Z" fill="#ef4444"/>$svg$, 'score', 600, 0, true),
 ('it020_freckles', '주근깨', '랭킹 점수 800점 달성', 'face', $svg$<circle cx="33" cy="54" r="1.3" fill="#b45309"/><circle cx="37" cy="57" r="1.3" fill="#b45309"/><circle cx="41" cy="54" r="1.3" fill="#b45309"/><circle cx="59" cy="54" r="1.3" fill="#b45309"/><circle cx="63" cy="57" r="1.3" fill="#b45309"/><circle cx="67" cy="54" r="1.3" fill="#b45309"/>$svg$, 'score', 800, 0, true),
 ('it021_propeller', '프로펠러 모자', '랭킹 점수 1,000점 달성', 'hat', $svg$<path d="M26 34 C28 14 72 14 74 34Z" fill="#ef4444"/><rect x="47" y="8" width="6" height="8" fill="#facc15"/><ellipse cx="50" cy="7" rx="18" ry="2.5" fill="#facc15"/>$svg$, 'score', 1000, 0, true),
 ('it022_notes', '흥겨운 음표', '랭킹 점수 1,300점 달성', 'deco', $svg$<g fill="#3b82f6"><circle cx="14" cy="34" r="3.5"/><circle cx="26" cy="28" r="3.5"/></g><path d="M17.5 34 V18 L29.5 14 V28" fill="none" stroke="#3b82f6" stroke-width="1.8"/><circle cx="86" cy="22" r="3" fill="#ec4899"/><path d="M89 22 V10" stroke="#ec4899" stroke-width="1.8"/>$svg$, 'score', 1300, 0, true),
 ('it023_necktie', '보라 넥타이', '랭킹 점수 1,700점 달성', 'outfit', $svg$<path d="M45 73 H55 L53 78 L58 94 L50 100 L42 94 L47 78Z" fill="#8b5cf6"/><path d="M45 73 H55 L53 78 H47Z" fill="#5b21b6"/>$svg$, 'score', 1700, 0, true),
 ('it024_chef', '요리사 모자', '랭킹 점수 2,200점 달성', 'hat', $svg$<circle cx="36" cy="14" r="11" fill="#ffffff"/><circle cx="50" cy="8" r="13" fill="#ffffff"/><circle cx="64" cy="14" r="11" fill="#ffffff"/><rect x="33" y="18" width="34" height="14" rx="2" fill="#ffffff"/><rect x="33" y="27" width="34" height="5" fill="#e2e8f0"/>$svg$, 'score', 2200, 0, true),
 ('it025_cat', '어깨 위 고양이', '랭킹 점수 2,800점 달성', 'deco', $svg$<circle cx="16" cy="88" r="9" fill="#fbbf24"/><path d="M8 84 L9 74 L16 80Z M24 84 L23 74 L16 80Z" fill="#fbbf24"/><circle cx="12.5" cy="87" r="1.3" fill="#27272a"/><circle cx="19.5" cy="87" r="1.3" fill="#27272a"/><path d="M15 91 H17" stroke="#ec4899" stroke-width="1.5"/>$svg$, 'score', 2800, 0, true),
 ('it026_squareglasses', '네모 안경', '랭킹 점수 3,500점 달성', 'face', $svg$<g fill="#e0f2fe" fill-opacity=".35" stroke="#0f172a" stroke-width="2.4"><rect x="31" y="40" width="17" height="12" rx="2.5"/><rect x="52" y="40" width="17" height="12" rx="2.5"/></g><path d="M48 45 H52" stroke="#0f172a" stroke-width="2"/>$svg$, 'score', 3500, 0, true),
 ('it027_buns', '양쪽 똥머리 장식', '랭킹 점수 4,500점 달성', 'hair', $svg$<circle cx="28" cy="16" r="10" fill="#f472b6"/><circle cx="72" cy="16" r="10" fill="#f472b6"/><circle cx="28" cy="16" r="4" fill="#facc15"/><circle cx="72" cy="16" r="4" fill="#facc15"/>$svg$, 'score', 4500, 0, true),
 ('it028_clouds', '포근한 구름', '랭킹 점수 6,000점 달성', 'back', $svg$<ellipse cx="20" cy="82" rx="16" ry="9" fill="#ffffff"/><ellipse cx="32" cy="76" rx="12" ry="9" fill="#ffffff"/><ellipse cx="80" cy="86" rx="16" ry="9" fill="#ffffff"/><ellipse cx="70" cy="80" rx="11" ry="8" fill="#e0f2fe"/>$svg$, 'score', 6000, 0, true),
 ('it029_square', '대괄호 [ ]', '랭킹 점수 8,000점 달성', 'deco', $svg$<path d="M20 12 H10 V42 H20 M80 12 H90 V42 H80" fill="none" stroke="#22c55e" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>$svg$, 'score', 8000, 0, true),
 ('it030_cowboy', '카우보이 모자', '랭킹 점수 10,000점 달성', 'hat', $svg$<path d="M32 30 C32 6 68 6 68 30Z" fill="#a16207"/><rect x="33" y="23" width="34" height="6" fill="#fde68a"/><path d="M12 28 Q50 40 88 28 Q82 36 50 38 Q18 36 12 28Z" fill="#a16207"/>$svg$, 'score', 10000, 0, true),
 ('it031_backpack', '모험 가방', '랭킹 점수 13,000점 달성', 'back', $svg$<rect x="12" y="68" width="16" height="26" rx="6" fill="#f97316"/><rect x="72" y="68" width="16" height="26" rx="6" fill="#f97316"/><rect x="14" y="78" width="12" height="6" rx="2" fill="#facc15"/><rect x="74" y="78" width="12" height="6" rx="2" fill="#facc15"/>$svg$, 'score', 13000, 0, true),
 ('it032_whiskers', '고양이 수염', '랭킹 점수 17,000점 달성', 'face', $svg$<g stroke="#475569" stroke-width="1.4" stroke-linecap="round"><path d="M22 54 L36 56 M22 60 L36 59 M78 54 L64 56 M78 60 L64 59"/></g><path d="M47 52 L53 52 L50 55Z" fill="#ec4899"/>$svg$, 'score', 17000, 0, true),
 ('it033_paws', '발자국', '랭킹 점수 22,000점 달성', 'deco', $svg$<g fill="#92400e" transform="translate(14 84) scale(1.2)"><ellipse cx="0" cy="2" rx="3.4" ry="3"/><circle cx="-4" cy="-3" r="1.5"/><circle cx="-1.4" cy="-5" r="1.5"/><circle cx="1.4" cy="-5" r="1.5"/><circle cx="4" cy="-3" r="1.5"/></g><g fill="#92400e" transform="translate(26 92) scale(1)"><ellipse cx="0" cy="2" rx="3.4" ry="3"/><circle cx="-4" cy="-3" r="1.5"/><circle cx="-1.4" cy="-5" r="1.5"/><circle cx="1.4" cy="-5" r="1.5"/><circle cx="4" cy="-3" r="1.5"/></g><g fill="#92400e" transform="translate(88 40) scale(1.1)"><ellipse cx="0" cy="2" rx="3.4" ry="3"/><circle cx="-4" cy="-3" r="1.5"/><circle cx="-1.4" cy="-5" r="1.5"/><circle cx="1.4" cy="-5" r="1.5"/><circle cx="4" cy="-3" r="1.5"/></g>$svg$, 'score', 22000, 0, true),
 ('it034_mohawk', '핑크 모히칸', '랭킹 점수 30,000점 달성', 'hair', $svg$<path d="M42 28 L44 2 L50 14 L56 2 L58 28Z" fill="#ec4899"/>$svg$, 'score', 30000, 0, true),
 ('it035_curly', '중괄호 { }', '랭킹 점수 40,000점 달성', 'deco', $svg$<path d="M17 12 C9 12 13 24 7 27 C13 30 9 42 17 42" fill="none" stroke="#14b8a6" stroke-width="2.8" stroke-linecap="round"/><path d="M83 12 C91 12 87 24 93 27 C87 30 91 42 83 42" fill="none" stroke="#14b8a6" stroke-width="2.8" stroke-linecap="round"/><circle cx="50" cy="94" r="0" fill="None"/>$svg$, 'score', 40000, 0, true),
 ('it036_labcoat', '연구원 가운', '랭킹 점수 55,000점 달성', 'outfit', $svg$<path d="M40 68 L50 98 L30 100 L16 100 C18 86 28 72 40 68Z" fill="#f8fafc"/><path d="M60 68 L50 98 L70 100 L84 100 C82 86 72 72 60 68Z" fill="#f8fafc"/><path d="M40 68 L50 90 L60 68" fill="none" stroke="#94a3b8" stroke-width="1.6"/>$svg$, 'score', 55000, 0, true),
 ('it037_gears', '톱니바퀴', '랭킹 점수 70,000점 달성', 'back', $svg$<circle cx="14" cy="30" r="10" fill="none" stroke="#64748b" stroke-width="6" stroke-dasharray="4 3.2"/><circle cx="14" cy="30" r="4" fill="#fbbf24"/><circle cx="88" cy="56" r="8" fill="none" stroke="#64748b" stroke-width="5" stroke-dasharray="3.4 2.8"/><circle cx="88" cy="56" r="3" fill="#fbbf24"/>$svg$, 'score', 70000, 0, true),
 ('it038_planet', '작은 행성', '랭킹 점수 90,000점 달성', 'deco', $svg$<circle cx="84" cy="22" r="9" fill="#8b5cf6"/><ellipse cx="84" cy="22" rx="15" ry="4" fill="none" stroke="#facc15" stroke-width="2" transform="rotate(-20 84 22)"/>$svg$, 'score', 90000, 0, true),
 ('it039_witch', '마녀 모자', '랭킹 점수 120,000점 달성', 'hat', $svg$<path d="M28 32 Q46 22 44 4 L58 -8 L56 8 Q58 24 72 32Z" fill="#8b5cf6"/><rect x="20" y="30" width="60" height="7" rx="3.5" fill="#8b5cf6"/><rect x="32" y="25" width="36" height="6" fill="#fbbf24"/>$svg$, 'score', 120000, 0, true),
 ('it040_butterfly', '나비 날개', '랭킹 점수 160,000점 달성', 'back', $svg$<ellipse cx="18" cy="52" rx="14" ry="18" fill="#ec4899" transform="rotate(-20 18 52)"/><ellipse cx="22" cy="78" rx="10" ry="12" fill="#fbcfe8" transform="rotate(20 22 78)"/><ellipse cx="82" cy="52" rx="14" ry="18" fill="#ec4899" transform="rotate(20 82 52)"/><ellipse cx="78" cy="78" rx="10" ry="12" fill="#fbcfe8" transform="rotate(-20 78 78)"/>$svg$, 'score', 160000, 0, true),
 ('it041_gem', '푸른 보석', '랭킹 점수 220,000점 달성', 'deco', $svg$<path d="M80 14 L90 14 L95 21 L85 36 L75 21Z" fill="#38bdf8"/><path d="M75 21 H95 M80 14 L85 21 L90 14 M85 21 L85 36" fill="none" stroke="#e0f2fe" stroke-width="1.1"/>$svg$, 'score', 220000, 0, true),
 ('it042_bigstar', '황금 별 후광', '랭킹 점수 300,000점 달성', 'back', $svg$<polygon points="50.0,2.0 62.9,32.2 95.7,35.2 70.9,56.8 78.2,88.8 50.0,72.0 21.8,88.8 29.1,56.8 4.3,35.2 37.1,32.2" fill="#fbbf24"/>$svg$, 'score', 300000, 0, true),
 ('it043_flames', '작은 불꽃', '2일 연속 출석', 'deco', $svg$<path d="M12 90 C6 78 14 70 12 60 C20 68 22 78 18 90Z M88 90 C94 78 86 70 88 60 C80 68 78 78 82 90Z" fill="#f97316"/><path d="M13 90 C11 82 15 78 14 72 C18 77 18 84 16 90Z M87 90 C89 82 85 78 86 72 C82 77 82 84 84 90Z" fill="#facc15"/>$svg$, 'streak', 2, 0, true),
 ('it044_bandana', '해적 두건', '3일 연속 출석', 'hat', $svg$<path d="M24 38 C26 14 74 14 76 38 Q50 28 24 38Z" fill="#ef4444"/><circle cx="38" cy="26" r="2" fill="#ffffff"/><circle cx="52" cy="22" r="2" fill="#ffffff"/><circle cx="64" cy="28" r="2" fill="#ffffff"/><path d="M74 34 L90 26 L86 42Z" fill="#ef4444"/>$svg$, 'streak', 3, 0, true),
 ('it045_scarf', '주황 목도리', '4일 연속 출석', 'outfit', $svg$<path d="M32 72 Q50 88 68 72 L70 81 Q50 96 30 81Z" fill="#fb923c"/><path d="M60 84 L68 100 L59 100 L54 88Z" fill="#fdba74"/>$svg$, 'streak', 4, 0, true),
 ('it046_paint', '얼굴 페인팅', '5일 연속 출석', 'face', $svg$<g stroke="#ef4444" stroke-width="2.4" stroke-linecap="round"><path d="M28 50 L38 53 M28 56 L37 57"/></g><g stroke="#3b82f6" stroke-width="2.4" stroke-linecap="round"><path d="M72 50 L62 53 M72 56 L63 57"/></g>$svg$, 'streak', 5, 0, true),
 ('it047_streak', '불꽃 브릿지', '6일 연속 출석', 'hair', $svg$<path d="M32 26 Q50 17 68 26" fill="none" stroke="#ef4444" stroke-width="3" stroke-linecap="round"/><path d="M30 31 Q50 21 70 31" fill="none" stroke="#f97316" stroke-width="3" stroke-linecap="round"/>$svg$, 'streak', 6, 0, true),
 ('it048_leaves', '낙엽', '7일 연속 출석', 'deco', $svg$<path d="M10 24 C10 14 22 12 26 16 C24 26 14 30 10 24Z" fill="#16a34a"/><path d="M80 34 C80 24 92 22 96 26 C94 36 84 40 80 34Z" fill="#f59e0b"/><path d="M84 12 C84 6 90 5 92 7 C91 12 86 14 84 12Z" fill="#16a34a"/>$svg$, 'streak', 7, 0, true),
 ('it049_sailor', '세일러 모자', '9일 연속 출석', 'hat', $svg$<rect x="28" y="22" width="44" height="14" rx="5" fill="#ffffff"/><path d="M26 34 H74 L70 40 H30Z" fill="#1e3a8a"/><circle cx="50" cy="28" r="3" fill="#1e3a8a"/>$svg$, 'streak', 9, 0, true),
 ('it050_overalls', '멜빵바지', '10일 연속 출석', 'outfit', $svg$<path d="M30 100 L38 72 M70 100 L62 72" stroke="#2563eb" stroke-width="6" stroke-linecap="round"/><circle cx="38" cy="78" r="2.2" fill="#fbbf24"/><circle cx="62" cy="78" r="2.2" fill="#fbbf24"/><rect x="38" y="88" width="24" height="12" rx="2" fill="#2563eb"/>$svg$, 'streak', 10, 0, true),
 ('it051_snow', '눈송이', '12일 연속 출석', 'deco', $svg$<g stroke="#7dd3fc" stroke-width="1.6" stroke-linecap="round" transform="translate(12 22)"><path d="M0 -5 V5 M-4.3 -2.5 L4.3 2.5 M-4.3 2.5 L4.3 -2.5"/></g><g stroke="#7dd3fc" stroke-width="1.6" stroke-linecap="round" transform="translate(88 30)"><path d="M0 -5 V5 M-4.3 -2.5 L4.3 2.5 M-4.3 2.5 L4.3 -2.5"/></g><g stroke="#7dd3fc" stroke-width="1.6" stroke-linecap="round" transform="translate(20 50)"><path d="M0 -5 V5 M-4.3 -2.5 L4.3 2.5 M-4.3 2.5 L4.3 -2.5"/></g><g stroke="#7dd3fc" stroke-width="1.6" stroke-linecap="round" transform="translate(84 56)"><path d="M0 -5 V5 M-4.3 -2.5 L4.3 2.5 M-4.3 2.5 L4.3 -2.5"/></g>$svg$, 'streak', 12, 0, true),
 ('it052_pigtails', '양갈래 머리', '14일 연속 출석', 'hair', $svg$<path d="M27 42 C8 42 6 64 16 74 C20 62 26 54 31 48Z" fill="#7c3aed"/><circle cx="26" cy="40" r="3.5" fill="#ec4899"/><g transform="translate(100 0) scale(-1 1)"><path d="M27 42 C8 42 6 64 16 74 C20 62 26 54 31 48Z" fill="#7c3aed"/><circle cx="26" cy="40" r="3.5" fill="#ec4899"/></g>$svg$, 'streak', 14, 0, true),
 ('it053_stickers', '별 스티커', '17일 연속 출석', 'face', $svg$<polygon points="33.0,51.5 34.2,54.4 37.3,54.6 34.9,56.6 35.6,59.6 33.0,58.0 30.4,59.6 31.1,56.6 28.7,54.6 31.8,54.4" fill="#facc15"/><polygon points="67.0,51.5 68.2,54.4 71.3,54.6 68.9,56.6 69.6,59.6 67.0,58.0 64.4,59.6 65.1,56.6 62.7,54.6 65.8,54.4" fill="#facc15"/>$svg$, 'streak', 17, 0, true),
 ('it054_sunburst', '햇살 후광', '21일 연속 출석', 'back', $svg$<g fill="#facc15" fill-opacity=".55"><polygon points="50,50 107.6,43.1 107.6,56.9"/><polygon points="50,50 103.3,72.8 96.4,84.8"/><polygon points="50,50 84.8,96.4 72.8,103.3"/><polygon points="50,50 56.9,107.6 43.1,107.6"/><polygon points="50,50 27.2,103.3 15.2,96.4"/><polygon points="50,50 3.6,84.8 -3.3,72.8"/><polygon points="50,50 -7.6,56.9 -7.6,43.1"/><polygon points="50,50 -3.3,27.2 3.6,15.2"/><polygon points="50,50 15.2,3.6 27.2,-3.3"/><polygon points="50,50 43.1,-7.6 56.9,-7.6"/><polygon points="50,50 72.8,-3.3 84.8,3.6"/><polygon points="50,50 96.4,15.2 103.3,27.2"/></g>$svg$, 'streak', 21, 0, true),
 ('it055_medal', '노력 메달', '25일 연속 출석', 'outfit', $svg$<path d="M42 68 L47 86 L53 86 L58 68Z" fill="#ef4444"/><polygon points="50.0,83.0 51.9,87.5 56.7,87.8 53.0,91.0 54.1,95.7 50.0,93.2 45.9,95.7 47.0,91.0 43.3,87.8 48.1,87.5" fill="#fbbf24"/>$svg$, 'streak', 25, 0, true),
 ('it056_sakura', '벚꽃잎', '30일 연속 출석', 'deco', $svg$<path d="M0 0 C-4 -4 -2 -9 0 -8 C2 -9 4 -4 0 0Z" fill="#f9a8d4" transform="translate(12 24) rotate(20)"/><path d="M0 0 C-4 -4 -2 -9 0 -8 C2 -9 4 -4 0 0Z" fill="#f9a8d4" transform="translate(24 12) rotate(-30)"/><path d="M0 0 C-4 -4 -2 -9 0 -8 C2 -9 4 -4 0 0Z" fill="#f9a8d4" transform="translate(86 28) rotate(40)"/><path d="M0 0 C-4 -4 -2 -9 0 -8 C2 -9 4 -4 0 0Z" fill="#f9a8d4" transform="translate(78 14) rotate(-10)"/><path d="M0 0 C-4 -4 -2 -9 0 -8 C2 -9 4 -4 0 0Z" fill="#f9a8d4" transform="translate(90 52) rotate(70)"/>$svg$, 'streak', 30, 0, true),
 ('it057_horns', '악마 뿔', '40일 연속 출석', 'hat', $svg$<path d="M30 28 C20 18 22 4 30 2 C28 12 36 18 40 22Z" fill="#ef4444"/><g transform="translate(100 0) scale(-1 1)"><path d="M30 28 C20 18 22 4 30 2 C28 12 36 18 40 22Z" fill="#ef4444"/></g>$svg$, 'streak', 40, 0, true),
 ('it058_fairy', '요정 날개', '50일 연속 출석', 'back', $svg$<path d="M34 66 C14 60 6 40 14 26 C26 30 34 46 38 60Z M66 66 C86 60 94 40 86 26 C74 30 66 46 62 60Z" fill="#a5f3fc" fill-opacity=".55" stroke="#22d3ee" stroke-width="1.4"/>$svg$, 'streak', 50, 0, true),
 ('it059_sash', '어깨띠', '60일 연속 출석', 'outfit', $svg$<path d="M20 78 L36 68 L92 100 L70 100Z" fill="#ec4899"/><circle cx="46" cy="82" r="4" fill="#fbbf24"/>$svg$, 'streak', 60, 0, true),
 ('it060_bolt', '번개', '75일 연속 출석', 'deco', $svg$<path d="M14 54 L6 70 H13 L10 84 L24 64 H16 L20 54Z" fill="#facc15"/><path d="M88 14 L80 30 H87 L84 44 L98 24 H90 L94 14Z" fill="#fde68a"/>$svg$, 'streak', 75, 0, true),
 ('it061_helmet', '기사 투구', '90일 연속 출석', 'hat', $svg$<path d="M22 44 C20 6 80 6 78 44 L72 40 C70 26 30 26 28 40Z" fill="#64748b"/><rect x="46" y="8" width="8" height="20" fill="#ef4444"/>$svg$, 'streak', 90, 0, true),
 ('it062_rainbow', '무지개', '120일 연속 출석', 'back', $svg$<path d="M6 76 A44 44 0 0 1 94 76" fill="none" stroke="#ef4444" stroke-width="4"/><path d="M10 76 A40 40 0 0 1 90 76" fill="none" stroke="#f97316" stroke-width="4"/><path d="M14 76 A36 36 0 0 1 86 76" fill="none" stroke="#facc15" stroke-width="4"/><path d="M18 76 A32 32 0 0 1 82 76" fill="none" stroke="#22c55e" stroke-width="4"/><path d="M22 76 A28 28 0 0 1 78 76" fill="none" stroke="#3b82f6" stroke-width="4"/><path d="M26 76 A24 24 0 0 1 74 76" fill="none" stroke="#8b5cf6" stroke-width="4"/>$svg$, 'streak', 120, 0, true),
 ('it063_rocket', '로켓', '150일 연속 출석', 'deco', $svg$<path d="M84 8 C92 14 92 28 88 36 H80 C76 28 76 14 84 8Z" fill="#ef4444"/><circle cx="84" cy="20" r="3.5" fill="#e2e8f0"/><path d="M80 36 L74 42 L80 40Z M88 36 L94 42 L88 40Z" fill="#e2e8f0"/><path d="M82 38 Q84 48 86 38Z" fill="#f97316"/>$svg$, 'streak', 150, 0, true),
 ('it064_visor', 'VR 바이저', '200일 연속 출석', 'face', $svg$<rect x="26" y="38" width="48" height="16" rx="7" fill="#111827"/><rect x="30" y="41" width="40" height="10" rx="4.5" fill="#22d3ee" fill-opacity=".65"/>$svg$, 'streak', 200, 0, true),
 ('it065_dragon', '용 날개', '300일 연속 출석', 'back', $svg$<path d="M32 68 L8 30 L22 40 L18 22 L32 40 L36 28 L40 56Z" fill="#22c55e"/><g transform="translate(100 0) scale(-1 1)"><path d="M32 68 L8 30 L22 40 L18 22 L32 40 L36 28 L40 56Z" fill="#22c55e"/></g><path d="M8 30 L22 40 M18 22 L32 40" stroke="#166534" stroke-width="1.5"/>$svg$, 'streak', 300, 0, true),
 ('it066_flames', '푸른 불꽃', '365일 연속 출석', 'deco', $svg$<path d="M12 90 C6 78 14 70 12 60 C20 68 22 78 18 90Z M88 90 C94 78 86 70 88 60 C80 68 78 78 82 90Z" fill="#38bdf8"/><path d="M13 90 C11 82 15 78 14 72 C18 77 18 84 16 90Z M87 90 C89 82 85 78 86 72 C82 77 82 84 84 90Z" fill="#e0f2fe"/>$svg$, 'streak', 365, 0, true),
 ('it067_flowercrown', '꽃 화관', 'Silver 티어 이상', 'hat', $svg$<circle cx="28" cy="34" r="5" fill="#ec4899"/><circle cx="28" cy="34" r="2" fill="#facc15"/><circle cx="34" cy="25" r="5" fill="#ec4899"/><circle cx="34" cy="25" r="2" fill="#facc15"/><circle cx="43" cy="20" r="5" fill="#ec4899"/><circle cx="43" cy="20" r="2" fill="#facc15"/><circle cx="57" cy="20" r="5" fill="#ec4899"/><circle cx="57" cy="20" r="2" fill="#facc15"/><circle cx="66" cy="25" r="5" fill="#ec4899"/><circle cx="66" cy="25" r="2" fill="#facc15"/><circle cx="72" cy="34" r="5" fill="#ec4899"/><circle cx="72" cy="34" r="2" fill="#facc15"/><path d="M26 36 Q50 12 74 36" fill="none" stroke="#16a34a" stroke-width="2"/>$svg$, 'tier', 1, 0, true),
 ('it068_badge', '별 배지', 'Silver 티어 이상', 'outfit', $svg$<circle cx="64" cy="86" r="7" fill="#3b82f6"/><polygon points="64.0,81.5 65.2,84.4 68.3,84.6 65.9,86.6 66.6,89.6 64.0,88.0 61.4,89.6 62.1,86.6 59.7,84.6 62.8,84.4" fill="#fbbf24"/>$svg$, 'tier', 1, 0, true),
 ('it069_chick', '병아리 친구', 'Silver 티어 이상', 'deco', $svg$<circle cx="84" cy="88" r="9" fill="#fde047"/><circle cx="81" cy="86" r="1.3" fill="#27272a"/><path d="M89 88 L96 90 L89 92Z" fill="#f97316"/><path d="M84 79 Q82 74 86 74" fill="none" stroke="#fde047" stroke-width="2"/>$svg$, 'tier', 1, 0, true),
 ('it070_monocle', '외눈 안경', 'Gold 티어 이상', 'face', $svg$<circle cx="60" cy="46" r="8.5" fill="#fef9c3" fill-opacity=".4" stroke="#b45309" stroke-width="2"/><path d="M60 54.5 Q64 70 70 78" fill="none" stroke="#94a3b8" stroke-width="1.2"/>$svg$, 'tier', 2, 0, true),
 ('it071_cape', '보랏빛 망토', 'Gold 티어 이상', 'back', $svg$<path d="M26 66 Q50 72 74 66 L97 100 L3 100Z" fill="#7c3aed"/><path d="M50 72 L50 100" stroke="#5b21b6" stroke-width="2"/>$svg$, 'tier', 2, 0, true),
 ('it072_book', '마법서', 'Gold 티어 이상', 'deco', $svg$<rect x="76" y="76" width="20" height="16" rx="2" fill="#7c3aed"/><rect x="78" y="78" width="16" height="3" fill="#ddd6fe"/><rect x="78" y="84" width="10" height="2" fill="#ddd6fe"/>$svg$, 'tier', 2, 0, true),
 ('it073_tophat', '신사 모자', 'Platinum 티어 이상', 'hat', $svg$<rect x="34" y="-2" width="32" height="30" rx="3" fill="#1f2937"/><rect x="34" y="18" width="32" height="6" fill="#ef4444"/><rect x="22" y="26" width="56" height="7" rx="3.5" fill="#1f2937"/>$svg$, 'tier', 3, 0, true),
 ('it074_tuxedo', '턱시도', 'Platinum 티어 이상', 'outfit', $svg$<path d="M40 68 L50 92 L60 68Z" fill="#ffffff"/><path d="M10 100 C12 76 32 68 40 68 L50 94 L38 100Z M90 100 C88 76 68 68 60 68 L50 94 L62 100Z" fill="#1f2937"/>$svg$, 'tier', 3, 0, true),
 ('it075_afropuff', '뭉게 구름 머리', 'Platinum 티어 이상', 'hair', $svg$<circle cx="50" cy="10" r="20" fill="#7c2d12"/><circle cx="30" cy="22" r="9" fill="#7c2d12"/><circle cx="70" cy="22" r="9" fill="#7c2d12"/>$svg$, 'tier', 3, 0, true),
 ('it076_batwings', '박쥐 날개', 'Platinum 티어 이상', 'back', $svg$<path d="M32 66 L10 44 L12 62 L4 56 L8 76 L18 72 L22 80 L34 74Z M68 66 L90 44 L88 62 L96 56 L92 76 L82 72 L78 80 L66 74Z" fill="#4c1d95" stroke="#a78bfa" stroke-width="1.2" stroke-linejoin="round"/>$svg$, 'tier', 3, 0, true),
 ('it077_crown', '은빛 왕관', 'Diamond 티어 이상', 'hat', $svg$<path d="M26 32 L28 8 L40 20 L50 2 L60 20 L72 8 L74 32Z" fill="#e2e8f0" stroke="#3b82f6" stroke-width="1.5" stroke-linejoin="round"/><circle cx="50" cy="22" r="3" fill="#3b82f6"/><circle cx="36" cy="26" r="2" fill="#3b82f6"/><circle cx="64" cy="26" r="2" fill="#3b82f6"/>$svg$, 'tier', 4, 0, true),
 ('it078_glasses3d', '3D 안경', 'Diamond 티어 이상', 'face', $svg$<rect x="30" y="40" width="18" height="12" rx="3" fill="#ef4444" fill-opacity=".7"/><rect x="52" y="40" width="18" height="12" rx="3" fill="#3b82f6" fill-opacity=".7"/><path d="M48 45 H52" stroke="#334155" stroke-width="2"/><rect x="30" y="40" width="40" height="12" rx="3" fill="none" stroke="#fff" stroke-width="1.6"/>$svg$, 'tier', 4, 0, true),
 ('it079_ghost', '유령 친구', 'Diamond 티어 이상', 'deco', $svg$<path d="M78 40 C78 22 94 22 94 40 V54 L90 50 L86 54 L82 50 L78 54Z" fill="#f8fafc"/><circle cx="83" cy="36" r="1.8" fill="#334155"/><circle cx="89" cy="36" r="1.8" fill="#334155"/>$svg$, 'tier', 4, 0, true),
 ('it080_crown', '에메랄드 왕관', 'Master 티어 이상', 'hat', $svg$<path d="M26 32 L28 8 L40 20 L50 2 L60 20 L72 8 L74 32Z" fill="#34d399" stroke="#047857" stroke-width="1.5" stroke-linejoin="round"/><circle cx="50" cy="22" r="3" fill="#047857"/><circle cx="36" cy="26" r="2" fill="#047857"/><circle cx="64" cy="26" r="2" fill="#047857"/>$svg$, 'tier', 5, 0, true),
 ('it081_armor', '은빛 어깨 갑옷', 'Master 티어 이상', 'outfit', $svg$<ellipse cx="22" cy="80" rx="13" ry="8" fill="#94a3b8"/><ellipse cx="78" cy="80" rx="13" ry="8" fill="#94a3b8"/><path d="M14 78 Q22 74 30 78 M70 78 Q78 74 86 78" fill="none" stroke="#e2e8f0" stroke-width="2"/>$svg$, 'tier', 5, 0, true),
 ('it082_moon', '달빛', 'Master 티어 이상', 'back', $svg$<path d="M64 4 A46 46 0 1 0 64 96 A36 36 0 1 1 64 4Z" fill="#a5b4fc"/><path d="M80 14 l1.4 3.4 3.6 .4 -2.7 2.4 .8 3.6 -3.1 -1.9 -3.1 1.9 .8 -3.6 -2.7 -2.4 3.6 -.4Z" fill="#fde047"/>$svg$, 'tier', 5, 0, true),
 ('it083_crown', '루비 왕관', 'Grandmaster 티어 이상', 'hat', $svg$<path d="M26 32 L28 8 L40 20 L50 2 L60 20 L72 8 L74 32Z" fill="#f87171" stroke="#7f1d1d" stroke-width="1.5" stroke-linejoin="round"/><circle cx="50" cy="22" r="3" fill="#7f1d1d"/><circle cx="36" cy="26" r="2" fill="#7f1d1d"/><circle cx="64" cy="26" r="2" fill="#7f1d1d"/>$svg$, 'tier', 6, 0, true),
 ('it084_angelwings', '황금 날개', 'Grandmaster 티어 이상', 'back', $svg$<path d="M30 68 C10 52 2 40 6 28 C16 32 24 38 36 54Z M70 68 C90 52 98 40 94 28 C84 32 76 38 64 54Z" fill="#fef08a" stroke="#fbbf24" stroke-width="1.5" stroke-linejoin="round"/>$svg$, 'tier', 6, 0, true),
 ('it085_sword', '전설의 검', 'Grandmaster 티어 이상', 'deco', $svg$<path d="M90 90 L90 52 L93 48 L96 52 L96 90Z" fill="#e2e8f0"/><rect x="85" y="88" width="16" height="4" rx="1" fill="#b45309"/><rect x="91" y="92" width="4" height="7" fill="#b45309"/>$svg$, 'tier', 6, 0, true),
 ('it086_ruff', '왕실 칼라', 'Grandmaster 티어 이상', 'outfit', $svg$<circle cx="30" cy="73" r="5.5" fill="#ffffff" stroke="#fca5a5" stroke-width="1"/><circle cx="38" cy="78" r="5.5" fill="#ffffff" stroke="#fca5a5" stroke-width="1"/><circle cx="50" cy="80" r="5.5" fill="#ffffff" stroke="#fca5a5" stroke-width="1"/><circle cx="62" cy="78" r="5.5" fill="#ffffff" stroke="#fca5a5" stroke-width="1"/><circle cx="70" cy="73" r="5.5" fill="#ffffff" stroke="#fca5a5" stroke-width="1"/>$svg$, 'tier', 6, 0, true),
 ('it087_trophy', '동메달 트로피', '랭킹 1등 1회', 'deco', $svg$<path d="M8 68 H24 V72 C24 80 20 84 16 84 C12 84 8 80 8 72Z" fill="#cd7f32"/><path d="M8 70 H4 Q4 78 10 78 M24 70 H28 Q28 78 22 78" fill="none" stroke="#cd7f32" stroke-width="1.8"/><rect x="13" y="84" width="6" height="5" fill="#7c2d12"/><rect x="9" y="89" width="14" height="4" rx="1.5" fill="#7c2d12"/>$svg$, 'rank1', 1, 0, true),
 ('it088_clownnose', '광대 코', '랭킹 1등 1회', 'face', $svg$<circle cx="50" cy="53" r="5" fill="#ef4444"/><circle cx="48.5" cy="51.5" r="1.4" fill="#fff" fill-opacity=".7"/>$svg$, 'rank1', 1, 0, true),
 ('it089_trophy', '은빛 트로피', '랭킹 1등 2회', 'deco', $svg$<path d="M8 68 H24 V72 C24 80 20 84 16 84 C12 84 8 80 8 72Z" fill="#e2e8f0"/><path d="M8 70 H4 Q4 78 10 78 M24 70 H28 Q28 78 22 78" fill="none" stroke="#e2e8f0" stroke-width="1.8"/><rect x="13" y="84" width="6" height="5" fill="#64748b"/><rect x="9" y="89" width="14" height="4" rx="1.5" fill="#64748b"/>$svg$, 'rank1', 2, 0, true),
 ('it090_clips', '별 머리핀', '랭킹 1등 2회', 'hair', $svg$<polygon points="32.0,27.0 33.3,30.2 36.8,30.5 34.1,32.7 34.9,36.0 32.0,34.2 29.1,36.0 29.9,32.7 27.2,30.5 30.7,30.2" fill="#fbbf24"/><polygon points="40.0,24.5 40.9,26.7 43.3,26.9 41.5,28.5 42.1,30.8 40.0,29.6 37.9,30.8 38.5,28.5 36.7,26.9 39.1,26.7" fill="#fde68a"/>$svg$, 'rank1', 2, 0, true),
 ('it091_medal', '금메달', '랭킹 1등 3회', 'outfit', $svg$<path d="M42 68 L47 86 L53 86 L58 68Z" fill="#fbbf24"/><polygon points="50.0,83.0 51.9,87.5 56.7,87.8 53.0,91.0 54.1,95.7 50.0,93.2 45.9,95.7 47.0,91.0 43.3,87.8 48.1,87.5" fill="#fef3c7"/>$svg$, 'rank1', 3, 0, true),
 ('it092_santa', '산타 모자', '랭킹 1등 4회', 'hat', $svg$<path d="M24 36 C26 8 60 0 82 22 Q70 14 62 18 Q74 28 76 36Z" fill="#ef4444"/><rect x="22" y="31" width="56" height="9" rx="4.5" fill="#ffffff"/><circle cx="82" cy="22" r="6" fill="#ffffff"/>$svg$, 'rank1', 4, 0, true),
 ('it093_trophy', '황금 트로피', '랭킹 1등 5회', 'deco', $svg$<path d="M8 68 H24 V72 C24 80 20 84 16 84 C12 84 8 80 8 72Z" fill="#fbbf24"/><path d="M8 70 H4 Q4 78 10 78 M24 70 H28 Q28 78 22 78" fill="none" stroke="#fbbf24" stroke-width="1.8"/><rect x="13" y="84" width="6" height="5" fill="#b45309"/><rect x="9" y="89" width="14" height="4" rx="1.5" fill="#b45309"/>$svg$, 'rank1', 5, 0, true),
 ('it094_beard', '수염 대마왕', '랭킹 1등 6회', 'face', $svg$<path d="M30 56 Q30 80 50 82 Q70 80 70 56 Q62 66 50 63 Q38 66 30 56Z" fill="#475569"/>$svg$, 'rank1', 6, 0, true),
 ('it095_coins', '금화 더미', '랭킹 1등 8회', 'deco', $svg$<ellipse cx="14" cy="92" rx="9" ry="3.5" fill="#b45309"/><rect x="5" y="86" width="18" height="6" fill="#fbbf24"/><ellipse cx="14" cy="86" rx="9" ry="3.5" fill="#fbbf24"/><ellipse cx="14" cy="80" rx="9" ry="3.5" fill="#b45309"/><rect x="5" y="74" width="18" height="6" fill="#fbbf24"/><ellipse cx="14" cy="74" rx="9" ry="3.5" fill="#fbbf24"/>$svg$, 'rank1', 8, 0, true),
 ('it096_dragon', '홍룡 날개', '랭킹 1등 10회', 'back', $svg$<path d="M32 68 L8 30 L22 40 L18 22 L32 40 L36 28 L40 56Z" fill="#ef4444"/><g transform="translate(100 0) scale(-1 1)"><path d="M32 68 L8 30 L22 40 L18 22 L32 40 L36 28 L40 56Z" fill="#ef4444"/></g><path d="M8 30 L22 40 M18 22 L32 40" stroke="#7f1d1d" stroke-width="1.5"/>$svg$, 'rank1', 10, 0, true),
 ('it097_crown', '챔피언 왕관', '랭킹 1등 15회', 'hat', $svg$<path d="M26 32 L28 8 L40 20 L50 2 L60 20 L72 8 L74 32Z" fill="#fbbf24" stroke="#ef4444" stroke-width="1.5" stroke-linejoin="round"/><circle cx="50" cy="22" r="3" fill="#ef4444"/><circle cx="36" cy="26" r="2" fill="#ef4444"/><circle cx="64" cy="26" r="2" fill="#ef4444"/>$svg$, 'rank1', 15, 0, true),
 ('it098_ninja', '닌자 마스크', '랭킹 1등 20회', 'face', $svg$<path d="M26 52 Q50 46 74 52 Q74 72 50 76 Q26 72 26 52Z" fill="#111827"/><path d="M30 56 Q50 52 70 56" fill="none" stroke="#4b5563" stroke-width="1.5"/>$svg$, 'rank1', 20, 0, true),
 ('it099_pizza', '우승 파티 피자', '랭킹 1등 30회', 'deco', $svg$<path d="M80 62 L98 62 L89 88Z" fill="#fbbf24"/><path d="M80 62 H98" stroke="#ef4444" stroke-width="3"/><circle cx="87" cy="70" r="2" fill="#ef4444"/><circle cx="91" cy="76" r="1.8" fill="#ef4444"/>$svg$, 'rank1', 30, 0, true),
 ('it100_sunburst', '전설의 후광', '랭킹 1등 50회', 'back', $svg$<g fill="#f0abfc" fill-opacity=".55"><polygon points="50,50 107.6,43.1 107.6,56.9"/><polygon points="50,50 103.3,72.8 96.4,84.8"/><polygon points="50,50 84.8,96.4 72.8,103.3"/><polygon points="50,50 56.9,107.6 43.1,107.6"/><polygon points="50,50 27.2,103.3 15.2,96.4"/><polygon points="50,50 3.6,84.8 -3.3,72.8"/><polygon points="50,50 -7.6,56.9 -7.6,43.1"/><polygon points="50,50 -3.3,27.2 3.6,15.2"/><polygon points="50,50 15.2,3.6 27.2,-3.3"/><polygon points="50,50 43.1,-7.6 56.9,-7.6"/><polygon points="50,50 72.8,-3.3 84.8,3.6"/><polygon points="50,50 96.4,15.2 103.3,27.2"/></g>$svg$, 'rank1', 50, 0, true)
on conflict (id) do nothing;
