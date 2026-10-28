-- =====================================================================
--  V3.9.0 — 티어 승급 배너 · 자동 공지 · 공지 상단 고정(빨간색)
--  * 기존 표·글·데이터는 그대로예요. "추가"만 하고, 여러 번 실행해도 안전해요.
--  * 큰 티어가 올라갔을 때만 승급이에요 (Bronze → Silver ○ / IV → III ✕).
--  * 승급자가 있는 날은 공지가 자동으로 하루에 한 개 올라가고(같은 날엔 같은 글이 갱신돼요),
--    홈에는 닫을 수 있는 배너가 떠요. 선생님/직원/SOLVER 등급 학생은 승급 소식에서 빠져요.
--  * 공지 상단 고정: 내가 쓴 공지만 고정할 수 있어요. 여러 개면 가나다 순으로 빨갛게 맨 위에 떠요.
--  * staff_roles.sql, student_tiers.sql, v310_ranking.sql, v320_tiers.sql, v320b_live_points.sql 이 먼저 실행된 상태여야 해요.
-- =====================================================================

do $$
begin
  if to_regclass('public.posts') is null or to_regclass('public.posts_view') is null
     or to_regclass('public.tiers') is null or to_regclass('public.rk_solved') is null
     or to_regclass('public.rk_live_solved') is null or to_regclass('public.student_tiers') is null then
    raise exception 'v310 / v320 / v320b / student_tiers.sql 을 먼저 실행해주세요.';
  end if;
end $$;

-- 1) 글에 "고정" 표시와 "자동 글 이름표" 칸 추가
alter table public.posts add column if not exists pinned boolean not null default false;
alter table public.posts add column if not exists auto_key text;
create unique index if not exists posts_auto_key_uidx on public.posts (auto_key) where auto_key is not null;

-- 2) 안전장치: 고정은 "공지 권한이 있는 직원이 올린 공지"만, auto_key 는 아래 자동 함수만 쓸 수 있어요
create or replace function public.posts_guard()
returns trigger
language plpgsql security definer set search_path = public
as $$
begin
  if new.pinned and not (new.board = 'notice' and public.staff_can('notice')) then
    new.pinned := false;
  end if;
  if new.auto_key is not null and coalesce(current_setting('pynest.autopost', true), '') <> '1' then
    new.auto_key := case when tg_op = 'UPDATE' then old.auto_key else null end;
  end if;
  return new;
end;
$$;
drop trigger if exists posts_guard_trg on public.posts;
create trigger posts_guard_trg before insert or update on public.posts
  for each row execute function public.posts_guard();

-- 3) 글 보기(posts_view)에 pinned 를 맨 뒤에 추가 (기존 칸은 그대로)
create or replace view public.posts_view as
 select p.id, p.board, p.title, p.content, p.anonymous, p.allow_comments, p.week, p.files, p.created_at, p.updated_at,
        (p.author_id = auth.uid()) as is_mine,
        case when (p.anonymous and (p.author_id <> auth.uid()) and (not public.staff_can('review'::text))) then '익명'::text
             else public.disp(p.author_id) end as author_name,
        case when (p.anonymous and (p.author_id <> auth.uid()) and (not public.staff_can('review'::text))) then null::uuid
             else p.author_id end as author_id,
        p.pinned
   from (public.posts p join public.profiles pr on pr.id = p.author_id)
  where public.is_approved() and ((p.board <> 'assignment'::text) or (p.author_id = auth.uid()) or public.staff_can('review'::text));

-- 4) 큰 티어 번호 (0 = 맨 아래 티어) / 번호 → 이름
create or replace function public.tier_major(p_score int)
returns int
language sql stable security definer set search_path = public
as $$
  select greatest((select count(*)::int from public.tiers t where t.min_score <= greatest(coalesce(p_score, 0), 0)) - 1, 0)
$$;
create or replace function public.tier_name_of(p_idx int)
returns text
language sql stable security definer set search_path = public
as $$
  select t.name from public.tiers t order by t.min_score offset greatest(coalesce(p_idx, 0), 0) limit 1
$$;
revoke all on function public.tier_major(int), public.tier_name_of(int) from public, anon, authenticated;

-- 5) 그날(한국 시간) 큰 티어가 오른 학생들
create or replace function public.tier_promos(p_day date)
returns table (uid uuid, name text, from_idx int, to_idx int, from_tier text, to_tier text)
language sql stable security definer set search_path = public
as $$
  with t as (select (p_day::timestamp at time zone 'Asia/Seoul') as t0),
  ev as (
    select user_id, pts, solved_at from public.rk_solved
    union all
    select user_id, pts, solved_at from public.rk_live_solved
  ),
  sc as (
    select e.user_id,
           coalesce(sum(e.pts) filter (where e.solved_at < t.t0), 0)::int as b,
           coalesce(sum(e.pts) filter (where e.solved_at < t.t0 + interval '1 day'), 0)::int as a
      from ev e cross join t group by e.user_id
  )
  select x.user_id, coalesce(n.nickname, p.username),
         public.tier_major(x.b), public.tier_major(x.a),
         public.tier_name_of(public.tier_major(x.b)), public.tier_name_of(public.tier_major(x.a))
    from sc x
    join public.profiles p on p.id = x.user_id and p.status = 'approved' and p.role <> 'admin'
    left join public.nicknames n on n.user_id = x.user_id
   where public.tier_major(x.a) > public.tier_major(x.b)
     and not exists (select 1 from public.staff_roles sr where sr.user_id = p.id)
     and not exists (select 1 from public.student_tiers st where st.user_id = p.id and st.tier = 'solver')
$$;
revoke all on function public.tier_promos(date) from public, anon, authenticated;

-- 6) 홈 배너용: 어제·오늘 승급자를 확인해서 자동 공지를 만들고(없으면)/갱신하고(있으면), 배너 정보를 돌려줘요
create or replace function public.tierup_banner()
returns jsonb
language plpgsql security definer set search_path = public
as $$
declare
  v_today date := (now() at time zone 'Asia/Seoul')::date;
  v_day date;
  v_admin uuid;
  v_n int;
  v_body text;
  v_key text;
  v_id bigint;
  v_out jsonb := null;
begin
  if not public.is_approved() then return null; end if;
  select id into v_admin from public.profiles where role = 'admin' and status = 'approved' order by created_at limit 1;
  if v_admin is null then return null; end if;
  perform set_config('pynest.autopost', '1', true);

  foreach v_day in array array[v_today - 1, v_today] loop
    select count(*)::int,
           '오늘 티어가 올라간 친구들을 축하해요! 🎉' || E'\n\n' ||
           string_agg('- **' || regexp_replace(q.name, '[*_`\[\]|<>]', '', 'g') || '** : ' || q.from_tier || ' → ' || q.to_tier,
                      E'\n' order by q.to_idx desc, q.name)
      into v_n, v_body
      from public.tier_promos(v_day) q;
    if v_n > 0 then
      v_key := 'tierup-' || to_char(v_day, 'YYYY-MM-DD');
      insert into public.posts (board, title, content, author_id, anonymous, allow_comments, auto_key)
        values ('notice', '🎉 티어 승급 소식 (' || to_char(v_day, 'FMMM"월" FMDD"일"') || ')', v_body, v_admin, false, true, v_key)
      on conflict (auto_key) where auto_key is not null do update
        set content = excluded.content, updated_at = now()
        where posts.board = 'notice' and posts.content is distinct from excluded.content;
      select id into v_id from public.posts where auto_key = v_key;
      v_out := jsonb_build_object(
        'post_id', v_id, 'day', v_day, 'count', v_n,
        'list', (select coalesce(jsonb_agg(jsonb_build_object('name', q.name, 'from', q.from_tier, 'to', q.to_tier)
                                  order by q.to_idx desc, q.name), '[]'::jsonb)
                   from (select * from public.tier_promos(v_day) order by to_idx desc, name limit 5) q));
    end if;
  end loop;
  perform set_config('pynest.autopost', '', true);
  return v_out;  -- 오늘 승급자가 있으면 오늘 것, 없으면 어제 것, 둘 다 없으면 null
end;
$$;
revoke all on function public.tierup_banner() from public, anon;
grant execute on function public.tierup_banner() to authenticated;
