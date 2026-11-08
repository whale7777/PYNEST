-- v5.0.0 Nestmate (같은 계정으로 쓰는 스터디 공간)
-- Supabase 프로젝트에는 이미 적용되어 있고, 새 프로젝트로 옮길 때 다시 실행하세요.
-- 접속 현황·스터디룸 신호는 Realtime 비공개 채널(nestmate*)로 오가고, 이 SQL은 그 권한과 설정을 만듭니다.
create table if not exists public.nm_settings (
  id int primary key default 1 check (id = 1),
  notice text not null default '',
  room_locked boolean not null default false,
  room_max int not null default 8 check (room_max between 2 and 12),
  updated_at timestamptz not null default now()
);
insert into public.nm_settings (id) values (1) on conflict do nothing;
alter table public.nm_settings enable row level security;
revoke all on public.nm_settings from anon;
grant select, update on public.nm_settings to authenticated;
drop policy if exists nm_settings_read on public.nm_settings;
create policy nm_settings_read on public.nm_settings for select to authenticated using (public.is_approved());
drop policy if exists nm_settings_upd on public.nm_settings;
create policy nm_settings_upd on public.nm_settings for update to authenticated
  using (public.is_admin() or public.staff_can('notice')) with check (public.is_admin() or public.staff_can('notice'));

create or replace function public.nm_names(p_ids uuid[])
returns table (id uuid, username text, avatar jsonb)
language sql stable security definer set search_path = public as $$
  select p.id, p.username, e.avatar
  from public.profiles p
  left join public.profile_ext e on e.user_id = p.id
  where public.is_approved() and p.status = 'approved' and p.id = any (p_ids[1:60]);
$$;
revoke all on function public.nm_names(uuid[]) from public, anon;
grant execute on function public.nm_names(uuid[]) to authenticated;

create or replace function public.nm_me()
returns jsonb language sql stable security definer set search_path = public as $$
  select jsonb_build_object('id', auth.uid(), 'approved', public.is_approved(),
    'admin', (public.is_admin() or public.staff_can('notice')),
    'username', (select username from public.profiles where id = auth.uid()));
$$;
revoke all on function public.nm_me() from public, anon;
grant execute on function public.nm_me() to authenticated;

drop policy if exists nm_rt_read on realtime.messages;
create policy nm_rt_read on realtime.messages for select to authenticated
  using (realtime.topic() like 'nestmate%' and public.is_approved());
drop policy if exists nm_rt_write on realtime.messages;
create policy nm_rt_write on realtime.messages for insert to authenticated
  with check (realtime.topic() like 'nestmate%' and public.is_approved());
