-- =====================================================================
--  직원 권한(OWNER / ADMIN / TEACHER / MOD) — 민혁닷컴 + PyNest 공용
--  * 기존 표·정책·데이터는 지우거나 바꾸지 않고 "추가"만 해요. 여러 번 실행해도 안전해요.
--  * profiles.role 은 그대로(student/admin). 원래 관리자(imadmin)는 자동으로 OWNER 예요.
--  * 직원 역할은 새 표 staff_roles 에 저장돼요.
--
--  역할            할 수 있는 일
--  OWNER  (최상위)  전부 + ADMIN 임명/해임   (= profiles.role 이 admin 인 계정)
--  ADMIN           전부 (단, ADMIN 임명/해임·OWNER 변경은 불가)
--  TEACHER         자료·과목·단원(폴더)·파일 업로드 (PyNest: 강의·문제집·문제·숙제)
--  MOD             관리만: 공지, M패스 부여, 충전 승인, 회원 승인/중지, 글·댓글 삭제
--
--  권한 표를 바꾸고 싶으면 아래 staff_can() 함수의 case 문만 고치면 돼요.
-- =====================================================================

do $$
begin
  if to_regclass('public.profiles') is null then
    raise exception 'public.profiles 테이블이 없어요. PyNest 와 같은 Supabase 프로젝트인지 확인해주세요.';
  end if;
end $$;

-- ---------------------------------------------------------------------
-- 1) 직원 표 (직접 쓰기 금지 — 아래 함수로만 바꿀 수 있어요)
-- ---------------------------------------------------------------------
create table if not exists public.staff_roles (
  user_id uuid primary key references public.profiles(id) on delete cascade,
  username text not null default '',
  role text not null check (role in ('admin', 'teacher', 'mod')),
  granted_by uuid,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.staff_roles enable row level security;
revoke all on public.staff_roles from anon, authenticated;
grant select on public.staff_roles to authenticated;

-- ---------------------------------------------------------------------
-- 2) 역할 / 순위 / 권한 판정
-- ---------------------------------------------------------------------
-- 내 역할: 'owner' / 'admin' / 'teacher' / 'mod' / null (승인된 계정만)
create or replace function public.staff_role()
returns text
language sql stable security definer set search_path = public
as $$
  select case
    when exists (select 1 from public.profiles p where p.id = auth.uid() and p.role = 'admin' and p.status = 'approved') then 'owner'
    else (select s.role from public.staff_roles s join public.profiles p on p.id = s.user_id
           where s.user_id = auth.uid() and p.status = 'approved')
  end
$$;

-- 누구의 순위든 (승인 상태와 무관): owner 4 > admin 3 > teacher 2 > mod 1 > 일반 0
create or replace function public.staff_rank(p_uid uuid)
returns int
language sql stable security definer set search_path = public
as $$
  select case
    when exists (select 1 from public.profiles p where p.id = p_uid and p.role = 'admin') then 4
    else coalesce((select case s.role when 'admin' then 3 when 'teacher' then 2 when 'mod' then 1 else 0 end
                     from public.staff_roles s where s.user_id = p_uid), 0)
  end
$$;

-- 이 권한이 있나?
--   content      자료·과목·단원·파일·강의·문제집·문제·숙제 만들기/고치기
--   notice       공지 쓰기
--   pass         M패스 부여·회수·명단
--   charge       충전/패스 신청 승인·거절
--   finance_read 포인트·내역 보기 (읽기 전용)
--   members      회원 승인/중지
--   moderate     게시글·댓글 삭제
--   review       제출함·채점, 비공개(과제) 글 보기 (ADMIN 이상 + TEACHER)
--   live         라이브 방송·저지 관리
--   reset_pw     비밀번호 초기화 (자기보다 낮은 순위만)
--   roles_basic  TEACHER / MOD 임명·해임
--   roles_admin  ADMIN 임명·해임 (OWNER 만)
create or replace function public.staff_can(p_perm text)
returns boolean
language sql stable security definer set search_path = public
as $$
  select coalesce(case public.staff_role()
    when 'owner' then true
    when 'admin' then p_perm <> 'roles_admin'
    when 'teacher' then p_perm = any (array['content', 'review'])
    when 'mod' then p_perm = any (array['notice', 'pass', 'charge', 'finance_read', 'members', 'moderate'])
    else false
  end, false)
$$;

grant execute on function public.staff_role() to anon, authenticated;
grant execute on function public.staff_rank(uuid) to authenticated;
grant execute on function public.staff_can(text) to anon, authenticated;

-- 기존 민혁닷컴 관리자 판정: OWNER + ADMIN 도 관리자로 인정 (기존 정책이 전부 이 함수를 써요)
create or replace function public.mh_is_admin()
returns boolean
language sql stable security definer set search_path = public
as $$
  select coalesce(public.staff_role() in ('owner', 'admin'), false)
$$;

-- 직원 표 읽기: 내 것 / OWNER·ADMIN 은 전부
drop policy if exists staff_roles_read on public.staff_roles;
create policy staff_roles_read on public.staff_roles for select to authenticated
  using (user_id = auth.uid() or public.staff_can('roles_basic'));

-- ---------------------------------------------------------------------
-- 3) 역할 관리 함수 (OWNER / ADMIN 만)
-- ---------------------------------------------------------------------
-- 직원 목록 (OWNER 포함)
create or replace function public.staff_list()
returns table (uid uuid, uname text, urole text, since timestamptz)
language plpgsql stable security definer set search_path = public
as $$
begin
  if not public.staff_can('roles_basic') then raise exception 'not allowed'; end if;
  return query
    select p.id, p.username, 'owner'::text, p.created_at from public.profiles p where p.role = 'admin' and p.status = 'approved'
    union all
    select s.user_id, p.username, s.role, s.created_at from public.staff_roles s join public.profiles p on p.id = s.user_id;
end;
$$;

-- 역할 부여/변경/해임. p_role: admin / teacher / mod / none(해임)
-- 결과: ok / invalid / not_found / self / is_owner / forbidden
create or replace function public.staff_set_role(p_username text, p_role text)
returns text
language plpgsql security definer set search_path = public
as $$
declare
  v_caller uuid := auth.uid();
  v_tid uuid;
  v_tname text;
  v_cur text;
begin
  if v_caller is null or not public.staff_can('roles_basic') then raise exception 'not allowed'; end if;
  if p_role is null or p_role not in ('admin', 'teacher', 'mod', 'none') then return 'invalid'; end if;
  select p.id, p.username into v_tid, v_tname from public.profiles p
   where lower(p.username) = lower(trim(p_username)) limit 1;
  if v_tid is null then return 'not_found'; end if;
  if v_tid = v_caller then return 'self'; end if;
  if public.staff_rank(v_tid) >= 4 then return 'is_owner'; end if;
  select s.role into v_cur from public.staff_roles s where s.user_id = v_tid;
  if (p_role = 'admin' or v_cur = 'admin') and not public.staff_can('roles_admin') then return 'forbidden'; end if;
  if p_role = 'none' then
    delete from public.staff_roles where user_id = v_tid;
    return 'ok';
  end if;
  insert into public.staff_roles (user_id, username, role, granted_by)
    values (v_tid, v_tname, p_role, v_caller)
  on conflict (user_id) do update
    set role = excluded.role, username = excluded.username, granted_by = excluded.granted_by, updated_at = now();
  return 'ok';
end;
$$;

revoke all on function public.staff_list() from public, anon;
revoke all on function public.staff_set_role(text, text) from public, anon;
grant execute on function public.staff_list() to authenticated;
grant execute on function public.staff_set_role(text, text) to authenticated;

-- ---------------------------------------------------------------------
-- 4) 회원(profiles) 보호: OWNER 가 아니면 "상태(승인/중지)"만 바꿀 수 있고,
--    자기보다 높거나 같은 순위의 계정 상태는 못 바꿔요. (SQL 에디터 등 로그인 없는 작업은 그대로 통과)
-- ---------------------------------------------------------------------
create or replace function public.profiles_guard()
returns trigger
language plpgsql security definer set search_path = public
as $$
declare
  v_caller uuid := auth.uid();
begin
  if v_caller is null then return new; end if;
  if public.is_admin() then return new; end if;
  if (to_jsonb(new) - 'status') is distinct from (to_jsonb(old) - 'status') then
    raise exception 'not allowed';
  end if;
  if new.status is distinct from old.status then
    if old.id = v_caller or public.staff_rank(v_caller) <= public.staff_rank(old.id) then
      raise exception 'not allowed';
    end if;
  end if;
  return new;
end;
$$;
drop trigger if exists profiles_guard on public.profiles;
create trigger profiles_guard before update on public.profiles
  for each row execute function public.profiles_guard();

-- ---------------------------------------------------------------------
-- 5) 민혁닷컴 — 새 정책 (기존 정책은 그대로, 아래는 "또 하나의 허용"으로 더해져요)
--    OWNER/ADMIN 은 위의 mh_is_admin() 덕분에 기존 정책으로 이미 전부 허용돼요.
-- ---------------------------------------------------------------------
-- TEACHER: 자료·프리미엄 링크·과목/단원(taxonomy)
drop policy if exists mh_files_staff on public.mh_files;
create policy mh_files_staff on public.mh_files for all to authenticated
  using (public.staff_can('content')) with check (public.staff_can('content'));
drop policy if exists mh_premium_staff on public.mh_premium;
create policy mh_premium_staff on public.mh_premium for all to authenticated
  using (public.staff_can('content')) with check (public.staff_can('content'));
drop policy if exists mh_meta_content on public.mh_meta;
create policy mh_meta_content on public.mh_meta for all to authenticated
  using (key = 'taxonomy' and public.staff_can('content'))
  with check (key = 'taxonomy' and public.staff_can('content'));

-- MOD: 공지 / M패스 명단 / 포인트·내역·신청 (읽기)
drop policy if exists mh_notices_staff on public.mh_notices;
create policy mh_notices_staff on public.mh_notices for all to authenticated
  using (public.staff_can('notice')) with check (public.staff_can('notice'));
drop policy if exists mh_pass_staff on public.mh_pass;
create policy mh_pass_staff on public.mh_pass for all to authenticated
  using (public.staff_can('pass')) with check (public.staff_can('pass'));
drop policy if exists mh_points_staff_read on public.mh_points;
create policy mh_points_staff_read on public.mh_points for select to authenticated using (public.staff_can('finance_read'));
drop policy if exists mh_ledger_staff_read on public.mh_ledger;
create policy mh_ledger_staff_read on public.mh_ledger for select to authenticated using (public.staff_can('finance_read'));
drop policy if exists mh_charges_staff_read on public.mh_charges;
create policy mh_charges_staff_read on public.mh_charges for select to authenticated using (public.staff_can('charge'));

-- 업로드 파일 보관함: TEACHER 도 올리기/바꾸기/지우기/읽기
drop policy if exists mh_files_obj_ins_staff on storage.objects;
create policy mh_files_obj_ins_staff on storage.objects for insert to authenticated
  with check (bucket_id = 'mh-files' and public.staff_can('content'));
drop policy if exists mh_files_obj_upd_staff on storage.objects;
create policy mh_files_obj_upd_staff on storage.objects for update to authenticated
  using (bucket_id = 'mh-files' and public.staff_can('content'))
  with check (bucket_id = 'mh-files' and public.staff_can('content'));
drop policy if exists mh_files_obj_del_staff on storage.objects;
create policy mh_files_obj_del_staff on storage.objects for delete to authenticated
  using (bucket_id = 'mh-files' and public.staff_can('content'));

create or replace function public.mh_can_read_object(p_name text)
returns boolean
language plpgsql stable security definer set search_path = public
as $$
declare
  v_id uuid;
  v_kind text;
  v_tier text;
  v_visible boolean;
begin
  if public.mh_is_admin() or public.staff_can('content') then return true; end if;
  begin
    v_id := split_part(p_name, '/', 1)::uuid;
  exception when others then
    return false;
  end;
  v_kind := split_part(split_part(p_name, '/', 2), '.', 1);
  select f.tier, f.visible into v_tier, v_visible from public.mh_files f where f.id = v_id;
  if not found or not v_visible then return false; end if;
  if v_kind = 'preview' then return true; end if;
  if v_tier = 'free' then return true; end if;
  return public.mh_owns(v_id);
end;
$$;

-- MOD: M패스 부여 / 충전·패스 신청 승인 (원래는 관리자만)
create or replace function public.mh_grant_pass(p_username text, p_expires date, p_memo text, p_quota int default 0, p_plan text default '')
returns text
language plpgsql security definer set search_path = public
as $$
declare
  v_id uuid;
  v_name text;
begin
  if not public.staff_can('pass') then raise exception 'admin only'; end if;
  select p.id, p.username into v_id, v_name
  from public.profiles p where lower(p.username) = lower(trim(p_username)) limit 1;
  if v_id is null then return 'not_found'; end if;
  insert into public.mh_pass (user_id, username, active, expires, memo, quota, used, plan)
  values (v_id, v_name, true, p_expires, coalesce(p_memo, ''), greatest(coalesce(p_quota, 0), 0), 0, coalesce(p_plan, ''))
  on conflict (user_id) do update
    set username = excluded.username, active = true, expires = excluded.expires, memo = excluded.memo,
        quota = excluded.quota, used = 0, plan = excluded.plan, updated_at = now();
  return 'ok';
end;
$$;

create or replace function public.mh_resolve_charge(p_id uuid, p_approve boolean)
returns text
language plpgsql security definer set search_path = public
as $$
declare
  c public.mh_charges%rowtype;
  v_bal int;
  v_r text;
begin
  if not public.staff_can('charge') then raise exception 'admin only'; end if;
  select * into c from public.mh_charges where id = p_id for update;
  if not found then return 'not_found'; end if;
  if c.status <> 'pending' then return 'already_done'; end if;
  if p_approve then
    if c.plan <> '' then
      v_r := public.mh_apply_pass(c.user_id, c.username, c.plan, 'M패스 계좌이체 ' || c.depositor);
      if v_r <> 'ok' then return 'plan_missing'; end if;
    else
      insert into public.mh_points (user_id, username, balance) values (c.user_id, c.username, 0)
        on conflict (user_id) do nothing;
      select balance into v_bal from public.mh_points where user_id = c.user_id for update;
      update public.mh_points set balance = v_bal + c.amount, updated_at = now() where user_id = c.user_id;
      insert into public.mh_ledger (user_id, username, delta, balance_after, kind, memo)
        values (c.user_id, c.username, c.amount, v_bal + c.amount, 'charge', left('충전 승인 ' || c.depositor, 120));
    end if;
    update public.mh_charges set status = 'done', resolved_at = now() where id = p_id;
  else
    update public.mh_charges set status = 'rejected', resolved_at = now() where id = p_id;
  end if;
  return 'ok';
end;
$$;

-- ---------------------------------------------------------------------
-- 6) PyNest — 새 정책 (기존 is_admin() 정책은 그대로 = OWNER)
-- ---------------------------------------------------------------------
-- 콘텐츠: 강의 · 문제집 · 문제 · 문제(연습) · 숙제  (TEACHER / ADMIN)
do $$
declare t text;
begin
  foreach t in array array['lectures', 'problem_sets', 'problems', 'exercises', 'homeworks', 'homework_items'] loop
    if to_regclass('public.' || t) is not null then
      execute format('drop policy if exists staff_content on public.%I', t);
      execute format('create policy staff_content on public.%I for all to authenticated using (public.staff_can(%L)) with check (public.staff_can(%L))', t, 'content', 'content');
    end if;
  end loop;
  -- 라이브 방송·저지 (ADMIN)
  foreach t in array array['live_sessions', 'live_problems'] loop
    if to_regclass('public.' || t) is not null then
      execute format('drop policy if exists staff_live on public.%I', t);
      execute format('create policy staff_live on public.%I for all to authenticated using (public.staff_can(%L)) with check (public.staff_can(%L))', t, 'live', 'live');
    end if;
  end loop;
  foreach t in array array['live_presence', 'live_submissions'] loop
    if to_regclass('public.' || t) is not null then
      execute format('drop policy if exists staff_live_read on public.%I', t);
      execute format('create policy staff_live_read on public.%I for select to authenticated using (public.staff_can(%L))', t, 'live');
      execute format('drop policy if exists staff_live_del on public.%I', t);
      execute format('create policy staff_live_del on public.%I for delete to authenticated using (public.staff_can(%L))', t, 'live');
    end if;
  end loop;
end $$;

-- 제출함 · 채점 (ADMIN)
drop policy if exists staff_review_select on public.submissions;
create policy staff_review_select on public.submissions for select to authenticated using (public.staff_can('review'));
drop policy if exists staff_review_update on public.submissions;
create policy staff_review_update on public.submissions for update to authenticated
  using (public.staff_can('review')) with check (public.staff_can('review'));
drop policy if exists staff_review_delete on public.submissions;
create policy staff_review_delete on public.submissions for delete to authenticated using (public.staff_can('review'));
drop policy if exists staff_subcomments_select on public.submission_comments;
create policy staff_subcomments_select on public.submission_comments for select to authenticated using (public.staff_can('review'));
drop policy if exists staff_subcomments_insert on public.submission_comments;
create policy staff_subcomments_insert on public.submission_comments for insert to authenticated
  with check (public.staff_can('review') and author_id = auth.uid());
drop policy if exists staff_subcomments_delete on public.submission_comments;
create policy staff_subcomments_delete on public.submission_comments for delete to authenticated using (public.staff_can('review'));

-- 게시판: 공지(notice 권한)·문제(content 권한) 글쓰기, 글·댓글 삭제(moderate 권한)
drop policy if exists staff_posts_insert on public.posts;
create policy staff_posts_insert on public.posts for insert to authenticated
  with check (public.is_approved() and author_id = auth.uid()
    and ((board = 'notice' and public.staff_can('notice')) or (board = 'problem' and public.staff_can('content'))));
drop policy if exists staff_posts_update on public.posts;
create policy staff_posts_update on public.posts for update to authenticated
  using (author_id = auth.uid() and public.is_approved())
  with check (public.is_approved() and author_id = auth.uid()
    and ((board = 'notice' and public.staff_can('notice')) or (board = 'problem' and public.staff_can('content'))));
drop policy if exists staff_posts_delete on public.posts;
create policy staff_posts_delete on public.posts for delete to authenticated using (public.staff_can('moderate'));
drop policy if exists staff_comments_delete on public.comments;
create policy staff_comments_delete on public.comments for delete to authenticated using (public.staff_can('moderate'));

-- 회원 승인/중지 (MOD / ADMIN) — 상태 외에는 profiles_guard 가 막아요
drop policy if exists staff_profiles_select on public.profiles;
create policy staff_profiles_select on public.profiles for select to authenticated using (public.staff_can('members'));
drop policy if exists staff_profiles_update on public.profiles;
create policy staff_profiles_update on public.profiles for update to authenticated
  using (public.staff_can('members')) with check (public.staff_can('members'));

-- 업로드 보관함 (PyNest)
drop policy if exists staff_problems_bucket on storage.objects;
create policy staff_problems_bucket on storage.objects for all to authenticated
  using (bucket_id = 'problems' and public.staff_can('content'))
  with check (bucket_id = 'problems' and public.staff_can('content'));
drop policy if exists staff_sets_bucket on storage.objects;
create policy staff_sets_bucket on storage.objects for all to authenticated
  using (bucket_id = 'sets' and public.staff_can('content'))
  with check (bucket_id = 'sets' and public.staff_can('content'));
drop policy if exists staff_attach_read on storage.objects;
create policy staff_attach_read on storage.objects for select to authenticated
  using (bucket_id = 'attachments' and public.staff_can('review'));
drop policy if exists staff_attach_delete on storage.objects;
create policy staff_attach_delete on storage.objects for delete to authenticated
  using (bucket_id = 'attachments' and public.staff_can('moderate'));
drop policy if exists staff_attach_insert on storage.objects;
create policy staff_attach_insert on storage.objects for insert to authenticated
  with check (bucket_id = 'attachments' and public.is_approved() and (storage.foldername(name))[2] = auth.uid()::text
    and (((storage.foldername(name))[1] = 'notice' and public.staff_can('notice'))
      or ((storage.foldername(name))[1] = 'problem' and public.staff_can('content'))));

-- 비공개(과제) 글과 익명 작성자 표시는 "review" 권한(OWNER/ADMIN/TEACHER)에게만 — 기존 is_admin() 자리에 staff_can('review')
create or replace function public.can_comment(pid bigint)
returns boolean
language sql stable security definer set search_path = public
as $$
  select public.is_approved() and exists (
    select 1 from public.posts p
    where p.id = pid and p.allow_comments
      and (p.board <> 'assignment' or p.author_id = auth.uid() or public.staff_can('review')))
$$;

create or replace view public.posts_view as
 SELECT p.id, p.board, p.title, p.content, p.anonymous, p.allow_comments, p.week, p.files, p.created_at, p.updated_at,
    (p.author_id = auth.uid()) AS is_mine,
    CASE WHEN (p.anonymous AND (p.author_id <> auth.uid()) AND (NOT public.staff_can('review'))) THEN '익명'::text ELSE pr.username END AS author_name
   FROM (public.posts p JOIN public.profiles pr ON ((pr.id = p.author_id)))
  WHERE (public.is_approved() AND ((p.board <> 'assignment'::text) OR (p.author_id = auth.uid()) OR public.staff_can('review')));

create or replace view public.comments_view as
 SELECT c.id, c.post_id, c.content, c.anonymous, c.created_at,
    (c.author_id = auth.uid()) AS is_mine,
    (((pr.role = 'admin'::text) OR EXISTS (SELECT 1 FROM public.staff_roles sr WHERE sr.user_id = pr.id AND sr.role IN ('admin', 'teacher'))) AND (NOT c.anonymous)) AS by_admin,
    CASE WHEN (c.anonymous AND (c.author_id <> auth.uid()) AND (NOT public.staff_can('review'))) THEN '익명'::text ELSE pr.username END AS author_name
   FROM ((public.comments c JOIN public.profiles pr ON ((pr.id = c.author_id))) JOIN public.posts p ON ((p.id = c.post_id)))
  WHERE (public.is_approved() AND ((p.board <> 'assignment'::text) OR (p.author_id = auth.uid()) OR public.staff_can('review')));

-- 비밀번호 초기화: OWNER 는 누구나(전과 같아요), ADMIN 은 자기보다 낮은 순위(학생·TEACHER·MOD)만
create or replace function public.admin_reset_password(target_username text, new_password text)
returns void
language plpgsql security definer set search_path = public, extensions
as $$
declare
  v_tid uuid;
begin
  if not (public.is_admin() or public.staff_can('reset_pw')) then raise exception 'not allowed'; end if;
  if length(new_password) < 6 then raise exception 'password too short'; end if;
  select id into v_tid from public.profiles where username = lower(target_username);
  if v_tid is null then return; end if;
  if not public.is_admin() and public.staff_rank(v_tid) >= public.staff_rank(auth.uid()) then
    raise exception 'not allowed';
  end if;
  update auth.users
     set encrypted_password = crypt(new_password, gen_salt('bf')), updated_at = now()
   where id = v_tid;
end $$;
