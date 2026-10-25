-- 제출함 "일괄 채점" 결과를 저장하려면 Supabase SQL Editor에서 한 번만 실행하세요.
-- 관리자만, 그리고 채점 결과(judge) 칸만 고칠 수 있어요.
grant update (judge) on public.submissions to authenticated;
drop policy if exists "submissions admin update" on public.submissions;
create policy "submissions admin update" on public.submissions
  for update to authenticated using (public.is_admin()) with check (public.is_admin());
