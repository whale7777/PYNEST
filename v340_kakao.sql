-- =====================================================================
--  PyNest V3.4.0 — 카카오톡 챗봇 연동 (랭킹 · 내 프로필 · 티어)
--  * 새 표 3개 + 새 함수만 "추가"해요. 기존 표·데이터는 그대로예요. 여러 번 실행해도 안전해요.
--  * v310_ranking.sql, v320_tiers.sql 이 먼저 적용돼 있어야 해요.
--
--  구조: 카톡 채널 챗봇 → (스킬 서버) Supabase Edge Function "kakao-bot" → 아래 bot_* 함수(service_role 만 실행 가능)
--  본인 확인: PyNest 설정 화면에서 6자리 코드를 받아 → 챗봇에 "연동 123456" 입력 → 카톡 계정과 연결
--  * 카톡에는 별명(없으면 아이디)만 나가요. 직원 계정의 점수는 나가지 않아요.
-- =====================================================================

do $$
begin
  if to_regclass('public.profiles') is null or to_regprocedure('public.rk_scores(timestamptz)') is null
     or to_regclass('public.tiers') is null then
    raise exception 'v310_ranking.sql, v320_tiers.sql 을 먼저 실행해주세요.';
  end if;
end $$;

-- 1) 표 (앱에서 직접 읽을 수 없어요: 정책 없음 = 함수로만 접근)
create table if not exists public.kakao_links (
  user_id uuid primary key references public.profiles(id) on delete cascade,
  kakao_id text not null unique check (length(kakao_id) between 1 and 200),
  linked_at timestamptz not null default now()
);
create table if not exists public.kakao_codes (
  user_id uuid primary key references public.profiles(id) on delete cascade,
  code text not null check (code ~ '^[0-9]{6}$'),
  expires_at timestamptz not null
);
create table if not exists public.kakao_fails (
  kakao_id text primary key,
  n int not null default 0,
  since timestamptz not null default now()
);
alter table public.kakao_links enable row level security;
alter table public.kakao_codes enable row level security;
alter table public.kakao_fails enable row level security;
revoke all on public.kakao_links, public.kakao_codes, public.kakao_fails from anon, authenticated;

-- 2) 학생(로그인 사용자)이 쓰는 함수: 코드 받기 / 연동 상태 / 연동 해제
create or replace function public.kakao_issue_code()
returns text
language plpgsql security definer set search_path = public
as $$
declare v_code text;
begin
  if auth.uid() is null or not public.is_approved() then raise exception 'not allowed'; end if;
  v_code := lpad((floor(random() * 1000000))::int::text, 6, '0');
  insert into public.kakao_codes (user_id, code, expires_at)
  values (auth.uid(), v_code, now() + interval '10 minutes')
  on conflict (user_id) do update set code = excluded.code, expires_at = excluded.expires_at;
  return v_code;
end;
$$;

create or replace function public.kakao_status()
returns jsonb
language sql stable security definer set search_path = public
as $$
  select case when public.is_approved()
    then jsonb_build_object('linked', exists (select 1 from public.kakao_links where user_id = auth.uid()),
                            'linked_at', (select linked_at from public.kakao_links where user_id = auth.uid()))
    end
$$;

create or replace function public.kakao_unlink()
returns void
language plpgsql security definer set search_path = public
as $$
begin
  if auth.uid() is null then raise exception 'not allowed'; end if;
  delete from public.kakao_links where user_id = auth.uid();
  delete from public.kakao_codes where user_id = auth.uid();
end;
$$;

revoke all on function public.kakao_issue_code(), public.kakao_status(), public.kakao_unlink() from public, anon;
grant execute on function public.kakao_issue_code(), public.kakao_status(), public.kakao_unlink() to authenticated;

-- 3) 챗봇(Edge Function, service_role)만 쓰는 함수
-- 결과: ok / bad(코드 틀림·만료) / locked(10분 안에 5번 틀림)
create or replace function public.bot_link(p_kakao text, p_code text)
returns text
language plpgsql security definer set search_path = public
as $$
declare v_uid uuid; f record;
begin
  if p_kakao is null or btrim(p_kakao) = '' then return 'bad'; end if;
  select * into f from public.kakao_fails where kakao_id = p_kakao;
  if found and f.since < now() - interval '10 minutes' then
    delete from public.kakao_fails where kakao_id = p_kakao; f := null;
  end if;
  if f.kakao_id is not null and f.n >= 5 then return 'locked'; end if;

  select c.user_id into v_uid from public.kakao_codes c
    join public.profiles p on p.id = c.user_id and p.status = 'approved'
   where c.code = btrim(p_code) and c.expires_at > now();
  if v_uid is null then
    insert into public.kakao_fails (kakao_id, n, since) values (p_kakao, 1, now())
    on conflict (kakao_id) do update set n = public.kakao_fails.n + 1;
    return 'bad';
  end if;

  delete from public.kakao_links where kakao_id = p_kakao;           -- 이 카톡이 다른 계정에 묶여 있었다면 옮겨요
  insert into public.kakao_links (user_id, kakao_id) values (v_uid, p_kakao)
  on conflict (user_id) do update set kakao_id = excluded.kakao_id, linked_at = now();
  delete from public.kakao_codes where user_id = v_uid;
  delete from public.kakao_fails where kakao_id = p_kakao;
  return 'ok';
end;
$$;

create or replace function public.bot_unlink(p_kakao text)
returns boolean
language plpgsql security definer set search_path = public
as $$
declare n int;
begin
  delete from public.kakao_links where kakao_id = p_kakao;
  get diagnostics n = row_count;
  return n > 0;
end;
$$;

-- 티어 표 (이름, 시작 점수)
create or replace function public.bot_tiers()
returns jsonb
language sql stable security definer set search_path = public
as $$
  select coalesce(jsonb_agg(jsonb_build_object('n', name, 'min', min_score) order by min_score), '[]'::jsonb) from public.tiers
$$;

-- 랭킹 TOP 10 + (연동돼 있으면) 내 순위. p_period: week / month / all
create or replace function public.bot_rank(p_period text, p_kakao text default null)
returns jsonb
language plpgsql stable security definer set search_path = public
as $$
declare v_from timestamptz; v_me uuid; v_top jsonb; v_mine jsonb; v_cnt int;
begin
  if p_period not in ('week', 'month', 'all') then return null; end if;
  v_from := case when p_period = 'all' then null else public.rk_period_start(p_period) end;
  select user_id into v_me from public.kakao_links where kakao_id = p_kakao;

  with r as (
    select s.uid, s.solved, s.pts, (rank() over (order by s.pts desc))::int as rnk
      from public.rk_scores(v_from) s where s.pts > 0
  )
  select (select count(*) from r),
         (select coalesce(jsonb_agg(jsonb_build_object('name', coalesce(n.nickname, p.username), 'solved', r.solved, 'pts', r.pts, 'rnk', r.rnk)
                          order by r.pts desc, r.solved desc, coalesce(n.nickname, p.username)), '[]'::jsonb)
            from (select * from r order by pts desc, solved desc limit 10) r
            join public.profiles p on p.id = r.uid left join public.nicknames n on n.user_id = r.uid),
         (select jsonb_build_object('pts', r.pts, 'solved', r.solved, 'rnk', r.rnk) from r where r.uid = v_me)
    into v_cnt, v_top, v_mine;

  return jsonb_build_object('period', p_period, 'count', v_cnt, 'top', v_top, 'me', v_mine, 'linked', v_me is not null);
end;
$$;

-- 내 프로필 (연동 안 됐으면 null). 직원 계정은 점수 없이 역할만.
create or replace function public.bot_me(p_kakao text)
returns jsonb
language plpgsql stable security definer set search_path = public
as $$
declare
  v_uid uuid; v_p public.profiles; v_staff text; v_nick text;
  v_tot record; v_w record; v_m record; v_rw int; v_rm int; v_by jsonb;
  v_ws timestamptz := public.rk_period_start('week');
  v_ms timestamptz := public.rk_period_start('month');
begin
  select user_id into v_uid from public.kakao_links where kakao_id = p_kakao;
  if v_uid is null then return null; end if;
  select * into v_p from public.profiles where id = v_uid and status = 'approved';
  if not found then return null; end if;
  select nickname into v_nick from public.nicknames where user_id = v_uid;
  v_staff := case when v_p.role = 'admin' then 'owner' else (select sr.role from public.staff_roles sr where sr.user_id = v_uid) end;
  if v_staff is not null then
    return jsonb_build_object('name', coalesce(v_nick, v_p.username), 'staff', v_staff);
  end if;

  select * into v_tot from public.rk_scores(null) where uid = v_uid;
  select * into v_w from public.rk_scores(v_ws) where uid = v_uid;
  select * into v_m from public.rk_scores(v_ms) where uid = v_uid;
  select 1 + count(*) into v_rw from public.rk_scores(v_ws) x where x.pts > coalesce(v_w.pts, 0);
  select 1 + count(*) into v_rm from public.rk_scores(v_ms) x where x.pts > coalesce(v_m.pts, 0);
  select coalesce(jsonb_agg(jsonb_build_object('difficulty', t.difficulty, 'n', t.n) order by t.n desc), '[]'::jsonb)
    into v_by from (select r.difficulty, count(*)::int as n from public.rk_solved r where r.user_id = v_uid group by r.difficulty) t;

  return jsonb_build_object(
    'name', coalesce(v_nick, v_p.username),
    'score', coalesce(v_tot.pts, 0), 'solved', coalesce(v_tot.solved, 0),
    'week', jsonb_build_object('solved', coalesce(v_w.solved, 0), 'pts', coalesce(v_w.pts, 0), 'rank', case when coalesce(v_w.pts, 0) > 0 then v_rw end),
    'month', jsonb_build_object('solved', coalesce(v_m.solved, 0), 'pts', coalesce(v_m.pts, 0), 'rank', case when coalesce(v_m.pts, 0) > 0 then v_rm end),
    'by_diff', v_by);
end;
$$;

-- bot_* 는 service_role(= Edge Function 의 비밀 키)만 실행할 수 있어요. 학생 앱에서는 호출할 수 없어요.
revoke all on function public.bot_link(text, text), public.bot_unlink(text), public.bot_tiers(),
  public.bot_rank(text, text), public.bot_me(text) from public, anon, authenticated;
grant execute on function public.bot_link(text, text), public.bot_unlink(text), public.bot_tiers(),
  public.bot_rank(text, text), public.bot_me(text) to service_role;
