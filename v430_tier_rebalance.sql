-- =====================================================================
--  PyNest V4.3.0 — 티어 7개 · 티어당 10단계 · 난이도 점수 재조정
--  * 학생·제출·문제 데이터는 하나도 지우지 않아요. 티어 표와 난이도 점수 "값"만 바꿔요.
--  * 점수는 그때그때 계산되니 실행하는 순간 모두의 티어가 새 기준으로 다시 정해져요.
--  * 여러 번 실행해도 같은 결과예요. (관리 › 🏅 티어 / 난이도 화면에서 나중에 숫자를 고칠 수도 있어요)
--
--  티어: Bronze 0 · Silver 2,000 · Gold 7,000 · Platinum 22,000 · Diamond 52,000 · Master 112,000 · Grandmaster 200,000
--        (Bronze·Silver·Gold 는 V→I 5단계, Platinum·Diamond·Master 는 X→I 10단계,
--         Grandmaster 는 단계 없이 10만 점마다 Grandmaster 200 · 300 · 400 … — 앱 코드가 계산해요)
-- =====================================================================

do $$
begin
  if to_regclass('public.tiers') is null or to_regclass('public.difficulties') is null then
    raise exception 'v310_ranking.sql / v320_tiers.sql 을 먼저 실행해주세요.';
  end if;
end $$;

-- 1) 난이도 점수
update public.difficulties d set points = v.p
  from (values ('Beginner',10),('Bronze',20),('Intermediate',35),('Advanced',60),('ELITE',100),
               ('Iron',160),('Gold',250),('Diamond',500),('Ruby',1000),('Master',2000)) v(n,p)
 where d.name = v.n;

-- 2) 티어: 남길 7개 말고는 정리 (Grandmaster 350 은 이름만 바꿔 Grandmaster 로 써요)
delete from public.tiers
 where name not in ('Bronze','Silver','Gold','Platinum','Diamond','Master','Grandmaster','Grandmaster 350');

do $$
begin
  if exists (select 1 from public.tiers where name = 'Grandmaster 350')
     and not exists (select 1 from public.tiers where name = 'Grandmaster') then
    update public.tiers set name = 'Grandmaster' where name = 'Grandmaster 350';
  elsif exists (select 1 from public.tiers where name = 'Grandmaster 350') then
    delete from public.tiers where name = 'Grandmaster 350';
  end if;
end $$;

-- 혹시 빠진 티어가 있으면 기본 색·문양으로 채워요 (시작 점수는 아래에서 정해져요)
insert into public.tiers (name, min_score, c1, c2, glyph)
select v.n, 9500000 + v.o, v.c1, v.c2, v.g
  from (values ('Silver',1,'#f1f5f9','#8795a8','tri'),('Gold',2,'#ffe27a','#d19a00','sq'),('Platinum',3,'#8ff0e0','#16a394','dia'),
               ('Diamond',4,'#9fd4ff','#2563eb','hex'),('Master',5,'#d9a8ff','#7c2ae0','star'),('Grandmaster',6,'#ffb36b','#c2410c','flame')) v(n,o,c1,c2,g)
 where not exists (select 1 from public.tiers t where t.name = v.n);

-- 시작 점수는 서로 겹치면 안 돼서, 임시값으로 옮긴 뒤 한 번에 정해요
update public.tiers set min_score = 9000000 + id where name <> 'Bronze';
update public.tiers t set min_score = v.m
  from (values ('Silver',2000),('Gold',7000),('Platinum',22000),('Diamond',52000),('Master',112000),('Grandmaster',200000)) v(n,m)
 where t.name = v.n;
update public.tiers set min_score = 0 where name = 'Bronze';
