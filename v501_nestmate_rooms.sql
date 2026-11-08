-- Nestmate 방 만들기·참여·채팅 (Supabase 프로젝트에는 이미 적용됨 · 마이그레이션 nestmate_rooms_v1)
-- 방은 마지막 "사람 있음" 신호(nm_room_ping)로부터 5분이 지나면 다음 조회 때 자동으로 닫히고, 닫힌 방의 채팅은 지워집니다.
create table if not exists public.nm_rooms (
  id uuid primary key default gen_random_uuid(),
  name text not null check (char_length(name) between 1 and 30),
  owner uuid not null,
  chat_on boolean not null default true,
  created_at timestamptz not null default now(),
  last_active timestamptz not null default now(),
  closed_at timestamptz
);
create table if not exists public.nm_messages (
  id bigint generated always as identity primary key,
  room_id uuid not null references public.nm_rooms(id) on delete cascade,
  user_id uuid not null,
  body text not null check (char_length(body) between 1 and 500),
  created_at timestamptz not null default now()
);
create index if not exists nm_messages_room_idx on public.nm_messages (room_id, id);
alter table public.nm_rooms enable row level security;
alter table public.nm_messages enable row level security;
revoke all on public.nm_rooms, public.nm_messages from anon, authenticated;
-- 함수(nm_room_sweep / nm_room_list / nm_room_create / nm_room_ping / nm_room_set_chat / nm_room_close / nm_chat_send / nm_chat_list)는
-- 모두 security definer RPC 이고 authenticated 에게만 실행 권한이 있습니다. 전체 정의는 Supabase 의 마이그레이션 nestmate_rooms_v1 에서 확인하세요.
