-- ============================================================
--  v12: 가입 승인 기본값 "필요" + 가입 시 별명 + 내가 정하는 별명
--  (민혁닷컴 · PyNest 공용 Supabase 에 한 번만 실행. 여러 번 실행해도 안전해요)
-- ============================================================

-- 1) 별명 검사 (한 곳에서만 검사해요)
--    ok | invalid(길이·글자) | reserved(운영진 사칭 단어) | taken(다른 별명·다른 사람 ID 와 같음)
create or replace function public.nickname_check(p_nick text, p_uid uuid) returns text
language plpgsql stable security definer set search_path = public as $$
declare v text := btrim(coalesce(p_nick, ''));
begin
  if v = '' or length(v) > 20 or v !~ '^[0-9A-Za-z가-힣ㄱ-ㅎㅏ-ㅣ _.-]+$' then return 'invalid'; end if;
  if lower(v) in ('admin','owner','teacher','mod','관리자','운영자','선생님','민혁','운영진','staff') then return 'reserved'; end if;
  if exists (select 1 from public.profiles p where lower(p.username) = lower(v) and (p_uid is null or p.id <> p_uid)) then return 'taken'; end if;
  if exists (select 1 from public.nicknames n where lower(n.nickname) = lower(v) and (p_uid is null or n.user_id <> p_uid)) then return 'taken'; end if;
  return 'ok';
end $$;

-- 2) 가입 화면에서 미리 확인 (로그인 전이라 anon 도 호출 가능)
create or replace function public.nickname_available(p_nick text) returns text
language sql stable security definer set search_path = public as $$
  select public.nickname_check(p_nick, null);
$$;
grant execute on function public.nickname_available(text) to anon, authenticated;

-- 3) 내 별명 정하기/바꾸기/지우기 — 관리자가 정해 준 별명(set_by 가 내가 아님)은 못 바꿔요
create or replace function public.nickname_set_self(p_nick text) returns text
language plpgsql security definer set search_path = public as $$
declare v_uid uuid := auth.uid(); v text := btrim(coalesce(p_nick, '')); v_by uuid; v_has boolean; v_st text; r text;
begin
  if v_uid is null then return 'login'; end if;
  select status into v_st from public.profiles where id = v_uid;
  if v_st is null or v_st = 'rejected' then return 'login'; end if;
  select true, set_by into v_has, v_by from public.nicknames where user_id = v_uid;
  if coalesce(v_has, false) and v_by is distinct from v_uid then return 'locked'; end if;
  if v = '' then delete from public.nicknames where user_id = v_uid; return 'ok'; end if;
  r := public.nickname_check(v, v_uid);
  if r <> 'ok' then return r; end if;
  begin
    insert into public.nicknames (user_id, nickname, set_by) values (v_uid, v, v_uid)
      on conflict (user_id) do update set nickname = excluded.nickname, set_by = excluded.set_by, updated_at = now();
  exception when unique_violation then return 'taken'; end;
  return 'ok';
end $$;
grant execute on function public.nickname_set_self(text) to authenticated;

-- 4) 가입할 때 받은 별명을 같이 저장 (별명이 문제여도 가입 자체는 성공)
create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_nick text := btrim(coalesce(new.raw_user_meta_data ->> 'nickname', ''));
begin
  insert into public.profiles (id, username)
  values (new.id, lower(coalesce(new.raw_user_meta_data ->> 'username', split_part(new.email, '@', 1))));
  if v_nick <> '' and public.nickname_check(v_nick, new.id) = 'ok' then
    begin
      insert into public.nicknames (user_id, nickname, set_by) values (new.id, v_nick, new.id) on conflict do nothing;
    exception when others then null; end;
  end if;
  return new;
end $$;

-- 5) 가입 승인: 기본값 = "관리자 승인 필요"  (사이트 설정의 autoApprove 가 true 일 때만 자동 승인)
create or replace function public.mh_auto_approve() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if new.status = 'pending'
     and coalesce((select value ->> 'autoApprove' from public.mh_meta where key = 'site'), 'false') = 'true'
     and exists (select 1 from auth.users u where u.id = new.id and u.raw_user_meta_data ->> 'src' = 'mcom') then
    new.status := 'approved';
  end if;
  return new;
end $$;

-- 6) 승인 전(pending) 회원은 구매·M패스 받기·업로드 파일 다운로드 불가 (서버에서도 막아요)
create or replace function public.mh_can_read_object(p_name text) returns boolean
language plpgsql stable security definer set search_path = public as $$
declare v_id uuid; v_kind text; v_tier text; v_visible boolean;
begin
  if public.mh_is_admin() or public.staff_can('content') then return true; end if;
  if auth.uid() is not null and not public.is_approved() then return false; end if;
  begin v_id := split_part(p_name, '/', 1)::uuid; exception when others then return false; end;
  v_kind := split_part(split_part(p_name, '/', 2), '.', 1);
  select f.tier, f.visible into v_tier, v_visible from public.mh_files f where f.id = v_id;
  if not found or not v_visible then return false; end if;
  if v_kind = 'preview' then return true; end if;
  if v_tier = 'free' then return true; end if;
  return public.mh_owns(v_id);
end $$;

-- 구매 / M패스 받기: 승인 전이면 'pending'
create or replace function public.mh_buy_file(p_file uuid) returns text
language plpgsql security definer set search_path = public as $$
declare
  v_uid uuid := auth.uid(); v_price int; v_title text; v_visible boolean;
  v_name text; v_status text; v_bal int;
begin
  if v_uid is null then return 'login'; end if;
  select p.username, p.status into v_name, v_status from public.profiles p where p.id = v_uid;
  if v_status = 'rejected' then return 'blocked'; end if;
  if v_status is distinct from 'approved' then return 'pending'; end if;
  select f.price, f.title, f.visible into v_price, v_title, v_visible from public.mh_files f where f.id = p_file;
  if not found or not v_visible then return 'not_found'; end if;
  if public.mh_is_admin() or public.mh_owns(p_file) then return 'already'; end if;
  if v_price <= 0 then return 'not_for_sale'; end if;

  insert into public.mh_points (user_id, username, balance) values (v_uid, coalesce(v_name, ''), 0)
    on conflict (user_id) do nothing;
  select balance into v_bal from public.mh_points where user_id = v_uid for update;
  if v_bal < v_price then return 'insufficient'; end if;

  update public.mh_points set balance = balance - v_price, updated_at = now() where user_id = v_uid;
  insert into public.mh_purchases (user_id, file_id, price) values (v_uid, p_file, v_price)
    on conflict (user_id, file_id) do update
      set price = excluded.price, created_at = now(), expires_at = now() + interval '30 days';
  delete from public.mh_dl where user_id = v_uid and file_id = p_file;
  insert into public.mh_ledger (user_id, username, delta, balance_after, kind, file_id, memo)
    values (v_uid, coalesce(v_name, ''), -v_price, v_bal - v_price, 'purchase', p_file, left(v_title, 120));
  return 'ok';
end $$;

create or replace function public.mh_claim_file(p_file uuid) returns text
language plpgsql security definer set search_path = public as $$
declare
  v_uid uuid := auth.uid(); v_tier text; v_visible boolean; v_row public.mh_pass%rowtype; v_st text;
begin
  if v_uid is null then return 'login'; end if;
  select status into v_st from public.profiles where id = v_uid;
  if v_st = 'rejected' then return 'blocked'; end if;
  if v_st is distinct from 'approved' then return 'pending'; end if;
  select f.tier, f.visible into v_tier, v_visible from public.mh_files f where f.id = p_file;
  if not found or not v_visible then return 'not_found'; end if;
  if v_tier = 'free' then return 'free'; end if;
  if public.mh_is_admin() or public.mh_owns(p_file) then return 'already'; end if;
  select * into v_row from public.mh_pass m where m.user_id = v_uid for update;
  if not found or not v_row.active
     or (v_row.expires is not null and v_row.expires < (now() at time zone 'Asia/Seoul')::date) then
    return 'no_pass';
  end if;
  if v_row.used >= v_row.quota then return 'no_quota'; end if;
  update public.mh_pass set used = used + 1, updated_at = now() where user_id = v_uid;
  insert into public.mh_purchases (user_id, file_id, price) values (v_uid, p_file, 0)
    on conflict (user_id, file_id) do update
      set price = 0, created_at = now(), expires_at = now() + interval '30 days';
  delete from public.mh_dl where user_id = v_uid and file_id = p_file;
  return 'ok';
end $$;
