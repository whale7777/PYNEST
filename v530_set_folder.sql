-- PyNest V5.3.0 — 📁 문제집 폴더 (목록을 폴더별로 묶어서 보여줘요). 여러 번 실행해도 안전해요.
alter table public.problem_sets add column if not exists folder text check (folder is null or length(folder) <= 60);
