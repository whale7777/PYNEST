-- =====================================================================
--  PyNest V4.4.0 — 프로필 꾸미기 · 캐릭터 · DM · 사이트 알림 · 랭킹에 0점 학생도 표시
--  * 기존 표·데이터는 지우거나 바꾸지 않아요. 새 표/함수를 "추가"하고 rank_board 만 교체해요. 여러 번 실행해도 안전해요.
--  * v310_ranking.sql 이 먼저 적용돼 있어야 해요.
--
--  [DM] 학생↔학생, 학생↔선생님 모두 가능해요. 대화 내용은 선생님(OWNER)이 열람할 수 있어요 (앱 화면에도 안내가 떠요).
--       보낸 메시지는 지울 수 없고, 받는 사람이 상대를 차단할 수 있어요. 1분에 20개까지만 보낼 수 있어요.
--  [알림] 새 DM · 티어 승급 · 선생님 공지가 🔔 로 와요.
--  [랭킹] SOLVER/LISTENER 가 아닌 학생은 이번 주·달에 문제를 하나도 안 풀어도 0점으로 랭킹에 보여요.
-- =====================================================================

do $$
begin
  if to_regprocedure('public.rank_board(text)') is null or to_regprocedure('public.disp(uuid)') is null then
    raise exception 'v310_ranking.sql 을 먼저 실행해주세요.';
  end if;
end $$;

-- 1) 프로필 꾸미기 + 캐릭터 -------------------------------------------------
create table if not exists public.profile_ext (
  user_id uuid primary key references public.profiles(id) on delete cascade,
  bio text not null default '' check (length(bio) <= 200),
  title text not null default '' check (length(title) <= 16),
  accent text check (accent is null or accent ~ '^#[0-9a-fA-F]{6}$'),
  avatar jsonb check (avatar is null or length(avatar::text) <= 1500),
  last_tier int,
  updated_at timestamptz not null default now()
);
alter table public.profile_ext enable row level security;
revoke all on public.profile_ext from anon;
grant select, insert, update on public.profile_ext to authenticated;
drop policy if exists profile_ext_read on public.profile_ext;
create policy profile_ext_read on public.profile_ext for select to authenticated using (public.is_approved());
drop policy if exists profile_ext_ins on public.profile_ext;
create policy profile_ext_ins on public.profile_ext for insert to authenticated with check (user_id = auth.uid() and public.is_approved());
drop policy if exists profile_ext_upd on public.profile_ext;
create policy profile_ext_upd on public.profile_ext for update to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());

-- 2) 알림 ---------------------------------------------------------------------
create table if not exists public.notifications (
  id bigint generated always as identity primary key,
  user_id uuid not null references public.profiles(id) on delete cascade,
  kind text not null check (kind in ('dm', 'tier', 'notice')),
  title text not null check (length(title) between 1 and 80),
  body text not null default '' check (length(body) <= 300),
  link text not null default '' check (length(link) <= 120),
  ref text,                       -- 같은 사람이 보낸 DM 을 한 줄로 묶는 데 써요
  cnt int not null default 1,
  created_at timestamptz not null default now(),
  read_at timestamptz
);
create index if not exists notifications_user_idx on public.notifications (user_id, created_at desc);
alter table public.notifications enable row level security;
revoke all on public.notifications from anon;
grant select, delete on public.notifications to authenticated;
grant update (read_at) on public.notifications to authenticated;
drop policy if exists notifications_read on public.notifications;
create policy notifications_read on public.notifications for select to authenticated using (user_id = auth.uid());
drop policy if exists notifications_upd on public.notifications;
create policy notifications_upd on public.notifications for update to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
drop policy if exists notifications_del on public.notifications;
create policy notifications_del on public.notifications for delete to authenticated using (user_id = auth.uid());

-- 3) DM -----------------------------------------------------------------------
create table if not exists public.dm_messages (
  id bigint generated always as identity primary key,
  sender_id uuid not null references public.profiles(id) on delete cascade,
  recipient_id uuid not null references public.profiles(id) on delete cascade,
  body text not null check (length(btrim(body)) between 1 and 1000),
  created_at timestamptz not null default now(),
  read_at timestamptz,
  check (sender_id <> recipient_id)
);
create index if not exists dm_rcpt_idx on public.dm_messages (recipient_id, created_at desc);
create index if not exists dm_send_idx on public.dm_messages (sender_id, created_at desc);
alter table public.dm_messages enable row level security;
revoke all on public.dm_messages from anon, authenticated;
grant select on public.dm_messages to authenticated;
drop policy if exists dm_read on public.dm_messages;
create policy dm_read on public.dm_messages for select to authenticated
  using (sender_id = auth.uid() or recipient_id = auth.uid() or public.staff_role() = 'owner');

create table if not exists public.dm_blocks (
  blocker_id uuid not null references public.profiles(id) on delete cascade,
  blocked_id uuid not null references public.profiles(id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (blocker_id, blocked_id)
);
alter table public.dm_blocks enable row level security;
revoke all on public.dm_blocks from anon, authenticated;
grant select on public.dm_blocks to authenticated;
drop policy if exists dm_blocks_read on public.dm_blocks;
create policy dm_blocks_read on public.dm_blocks for select to authenticated using (blocker_id = auth.uid());

-- 보낼 수 있는 사람 목록 (승인된 모든 사용자). staff 는 선생님/직원 역할 이름.
create or replace function public.dm_contacts()
returns table (user_id uuid, name text, staff text, blocked boolean)
language sql stable security definer set search_path = public
as $$
  select p.id, public.disp(p.id),
         case when p.role = 'admin' then 'owner' else (select s.role from public.staff_roles s where s.user_id = p.id) end,
         exists (select 1 from public.dm_blocks b where b.blocker_id = auth.uid() and b.blocked_id = p.id)
    from public.profiles p
   where public.is_approved() and p.status = 'approved' and p.id <> auth.uid()
   order by 2
$$;

-- 보내기. 결과: ok / invalid / self / nouser / blocked / rate
create or replace function public.dm_send(p_to uuid, p_body text)
returns text
language plpgsql security definer set search_path = public
as $$
declare
  v_me uuid := auth.uid();
  v_body text := btrim(coalesce(p_body, ''));
  v_name text;
  v_nid bigint;
begin
  if v_me is null or not public.is_approved() then return 'nouser'; end if;
  if length(v_body) < 1 or length(v_body) > 1000 then return 'invalid'; end if;
  if p_to is null or p_to = v_me then return 'self'; end if;
  if not exists (select 1 from public.profiles where id = p_to and status = 'approved') then return 'nouser'; end if;
  if exists (select 1 from public.dm_blocks where blocker_id = p_to and blocked_id = v_me)
     and public.staff_role() is null then return 'blocked'; end if;
  if (select count(*) from public.dm_messages where sender_id = v_me and created_at > now() - interval '1 minute') >= 20 then return 'rate'; end if;
  insert into public.dm_messages (sender_id, recipient_id, body) values (v_me, p_to, v_body);
  v_name := public.disp(v_me);
  select id into v_nid from public.notifications
   where user_id = p_to and kind = 'dm' and ref = v_me::text and read_at is null order by id desc limit 1;
  if v_nid is not null then
    update public.notifications set cnt = cnt + 1, created_at = now(), body = left(v_body, 60) where id = v_nid;
  else
    insert into public.notifications (user_id, kind, title, body, link, ref)
    values (p_to, 'dm', left(coalesce(v_name, '누군가'), 30) || ' 님의 메시지', left(v_body, 60), '#/settings/dm/' || v_me::text, v_me::text);
  end if;
  return 'ok';
end;
$$;

-- 받은편지함(대화 목록)
create or replace function public.dm_inbox()
returns table (other uuid, name text, staff text, last_body text, last_at timestamptz, last_mine boolean, unread int)
language sql stable security definer set search_path = public
as $$
  with m as (
    select case when sender_id = auth.uid() then recipient_id else sender_id end as o, *
      from public.dm_messages
     where (sender_id = auth.uid() or recipient_id = auth.uid()) and public.is_approved()
  ), last as (
    select distinct on (o) o, body, created_at, (sender_id = auth.uid()) as mine from m order by o, created_at desc, id desc
  )
  select l.o, public.disp(l.o),
         case when p.role = 'admin' then 'owner' else (select s.role from public.staff_roles s where s.user_id = p.id) end,
         left(l.body, 80), l.created_at, l.mine,
         (select count(*)::int from m where m.o = l.o and m.recipient_id = auth.uid() and m.read_at is null)
    from last l join public.profiles p on p.id = l.o
   order by l.created_at desc
   limit 200
$$;

-- 대화 열기: 최근 100개(오래된 것부터), 받은 것은 읽음 처리
create or replace function public.dm_thread(p_other uuid)
returns table (id bigint, mine boolean, body text, created_at timestamptz, read_at timestamptz)
language plpgsql volatile security definer set search_path = public
as $$
#variable_conflict use_column
begin
  if not public.is_approved() then return; end if;
  update public.dm_messages set read_at = now()
   where recipient_id = auth.uid() and sender_id = p_other and read_at is null;
  update public.notifications set read_at = now()
   where user_id = auth.uid() and kind = 'dm' and ref = p_other::text and read_at is null;
  return query
    select x.id, x.mine, x.body, x.created_at, x.read_at from (
      select m.id, (m.sender_id = auth.uid()) as mine, m.body, m.created_at, m.read_at
        from public.dm_messages m
       where (m.sender_id = auth.uid() and m.recipient_id = p_other) or (m.sender_id = p_other and m.recipient_id = auth.uid())
       order by m.id desc limit 100) x
    order by x.id;
end;
$$;

create or replace function public.dm_unread()
returns int language sql stable security definer set search_path = public
as $$ select count(*)::int from public.dm_messages where recipient_id = auth.uid() and read_at is null and public.is_approved() $$;

create or replace function public.dm_block(p_uid uuid, p_on boolean)
returns void language plpgsql security definer set search_path = public
as $$
begin
  if not public.is_approved() or p_uid is null or p_uid = auth.uid() then return; end if;
  if p_on then
    insert into public.dm_blocks (blocker_id, blocked_id) values (auth.uid(), p_uid) on conflict do nothing;
  else
    delete from public.dm_blocks where blocker_id = auth.uid() and blocked_id = p_uid;
  end if;
end;
$$;

-- 선생님(OWNER) 열람: 대화 상대 쌍 목록 / 한 쌍의 대화
create or replace function public.dm_admin_pairs()
returns table (a uuid, a_name text, b uuid, b_name text, n int, last_at timestamptz)
language sql stable security definer set search_path = public
as $$
  select least(m.sender_id, m.recipient_id), public.disp(least(m.sender_id, m.recipient_id)),
         greatest(m.sender_id, m.recipient_id), public.disp(greatest(m.sender_id, m.recipient_id)),
         count(*)::int, max(m.created_at)
    from public.dm_messages m
   where public.staff_role() = 'owner'
   group by 1, 3
   order by max(m.created_at) desc
   limit 300
$$;
create or replace function public.dm_admin_thread(p_a uuid, p_b uuid)
returns table (id bigint, sender uuid, sender_name text, body text, created_at timestamptz)
language sql stable security definer set search_path = public
as $$
  select m.id, m.sender_id, public.disp(m.sender_id), m.body, m.created_at
    from public.dm_messages m
   where public.staff_role() = 'owner'
     and ((m.sender_id = p_a and m.recipient_id = p_b) or (m.sender_id = p_b and m.recipient_id = p_a))
   order by m.id desc limit 500
$$;

-- 4) 알림: 선생님 공지 / 티어 승급 확인 --------------------------------------------
create or replace function public.notify_all(p_title text, p_body text, p_link text default '')
returns int
language plpgsql security definer set search_path = public
as $$
declare n int;
begin
  if public.staff_role() is null or not public.staff_can('members') then raise exception 'forbidden'; end if;
  if length(btrim(coalesce(p_title, ''))) not between 1 and 80 then raise exception 'invalid'; end if;
  insert into public.notifications (user_id, kind, title, body, link)
  select p.id, 'notice', btrim(p_title), left(coalesce(p_body, ''), 300), left(coalesce(p_link, ''), 120)
    from public.profiles p where p.status = 'approved' and p.id <> auth.uid();
  get diagnostics n = row_count;
  return n;
end;
$$;

-- 앱을 열 때 한 번: 내 티어가 올랐으면 알림. (처음이거나 내려갔으면 조용히 기록만)
create or replace function public.tier_check_self()
returns void
language plpgsql security definer set search_path = public
as $$
declare
  v_me uuid := auth.uid();
  v_score int := 0;
  v_idx int;
  v_name text;
  v_old int;
begin
  if v_me is null or not public.is_approved() or public.staff_role() is not null then return; end if;
  if to_regclass('public.tiers') is null then return; end if;
  select coalesce(sum(x.pts), 0)::int into v_score from public.rk_scores(null) x where x.uid = v_me;
  select count(*)::int - 1, (array_agg(t.name order by t.min_score desc))[1]
    into v_idx, v_name from public.tiers t where t.min_score <= v_score;
  if v_idx is null or v_idx < 0 then return; end if;
  select last_tier into v_old from public.profile_ext where user_id = v_me;
  if not found then
    insert into public.profile_ext (user_id, last_tier) values (v_me, v_idx);
  elsif v_old is null or v_idx < v_old then
    update public.profile_ext set last_tier = v_idx where user_id = v_me;
  elsif v_idx > v_old then
    update public.profile_ext set last_tier = v_idx where user_id = v_me;
    insert into public.notifications (user_id, kind, title, body, link)
    values (v_me, 'tier', '🎉 ' || v_name || ' 티어로 승급했어요!', '지금까지 ' || v_score || '점', '#/u/' || v_me::text);
  end if;
end;
$$;

-- 5) 랭킹: 일반 학생(SOLVER·LISTENER 아님)은 0점이어도 보여요 ---------------------------
do $$
declare v_ex text := '';
begin
  if to_regclass('public.student_tiers') is not null then
    v_ex := ' and not exists (select 1 from public.student_tiers st where st.user_id = p.id)';
  end if;
  execute format($f$
    create or replace function public.rank_board(p_period text)
    returns table (user_id uuid, name text, solved int, pts int, rnk int, score int)
    language sql stable security definer set search_path = public
    as $b$
      with per as (select * from public.rk_scores(public.rk_period_start(p_period))),
           tot as (select * from public.rk_scores(null)),
           everyone as (
             select p.id as uid from public.profiles p
              where p.status = 'approved' and p.role <> 'admin'
                and not exists (select 1 from public.staff_roles sr where sr.user_id = p.id)
                %s
             union
             select uid from per
           ),
           j as (
             select e.uid, coalesce(per.solved, 0) as solved, coalesce(per.pts, 0) as pts
               from everyone e left join per on per.uid = e.uid
           )
      select j.uid, public.disp(j.uid), j.solved, j.pts,
             (rank() over (order by j.pts desc))::int,
             coalesce(tot.pts, 0)
        from j left join tot on tot.uid = j.uid
       where public.is_approved() and p_period in ('week', 'month')
       order by j.pts desc, j.solved desc, 2
    $b$
  $f$, v_ex);
end $$;
revoke all on function public.rank_board(text) from public, anon;
grant execute on function public.rank_board(text) to authenticated;

revoke all on function public.dm_contacts(), public.dm_send(uuid, text), public.dm_inbox(), public.dm_thread(uuid), public.dm_unread(),
  public.dm_block(uuid, boolean), public.dm_admin_pairs(), public.dm_admin_thread(uuid, uuid),
  public.notify_all(text, text, text), public.tier_check_self() from public, anon;
grant execute on function public.dm_contacts(), public.dm_send(uuid, text), public.dm_inbox(), public.dm_thread(uuid), public.dm_unread(),
  public.dm_block(uuid, boolean), public.dm_admin_pairs(), public.dm_admin_thread(uuid, uuid),
  public.notify_all(text, text, text), public.tier_check_self() to authenticated;
