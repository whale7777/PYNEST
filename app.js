'use strict';
(() => {
  const app = document.getElementById('app');

  if (!window.supabase || String(CONFIG.SUPABASE_URL).includes('여기에')) {
    app.innerHTML = '<div class="card" style="max-width:480px;margin:60px auto"><h2>설정이 필요해요</h2><p>config.js 파일에 Supabase 주소와 키를 넣어주세요. (README.md 4번)</p></div>';
    return;
  }

  const sb = window.supabase.createClient(CONFIG.SUPABASE_URL, CONFIG.SUPABASE_ANON_KEY);
  const SITE = CONFIG.SITE_NAME || 'PyNest';
  const ICON = CONFIG.SITE_ICON || '🐍';

  // 브라우저 탭 제목과 아이콘(파비콘)
  document.title = SITE;
  (() => {
    let l = document.querySelector('link[rel~="icon"]');
    if (!l) { l = document.createElement('link'); l.rel = 'icon'; document.head.appendChild(l); }
    l.href = CONFIG.SITE_LOGO || ('data:image/svg+xml,' + encodeURIComponent(
      `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">${ICON}</text></svg>`));
  })();

  /* ---------- 공통 도구 ---------- */
  const $ = (s, el = document) => el.querySelector(s);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const fmt = (d) => new Date(d).toLocaleString('ko-KR', { year: '2-digit', month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  // 함께 쓰는 서비스(민혁닷컴·Nestmate) 바로가기. 설정 > 계정·화면에서 끌 수 있고 기본은 켜짐
  const sideOn = () => { try { return localStorage.getItem('pn_side') !== '0'; } catch (e) { return true; } };
  const emailOf = (id) => `${id.toLowerCase()}@pyclass.site`; // ID를 가짜 이메일로 바꿔서 로그인에 사용
  const ID_RE = /^[a-z0-9_]{3,20}$/;
  const MAX_FILE = 50 * 1024 * 1024;
  const rand = () => Math.random().toString(36).slice(2, 8);

  let me = null;
  let signingUp = false;
  let navTok = 0;
  let adminTab = 'members';
  let lecEdit = null; // 수정 중인 강의 id

  /* ---------- 직원 권한 (OWNER / ADMIN / TEACHER / MOD) ----------
     staff_roles.sql 의 staff_can() 과 같은 표예요. 바꾸면 SQL 도 같이 바꿔요.
     content 강의·문제집·문제·숙제 · notice 공지 · members 회원 승인/중지 · moderate 글·댓글 삭제
     review 제출함·채점 · live 라이브 · reset_pw 비밀번호 초기화 · roles_basic TEACHER/MOD 임명 · roles_admin ADMIN 임명 */
  const ROLE_NAME = { owner: 'OWNER', admin: 'ADMIN', teacher: 'TEACHER', mod: 'MOD' };
  const ROLE_DESC = { owner: '최상위 · 모든 권한', admin: '모든 관리 (ADMIN 임명 제외)', teacher: '강의·문제집·문제·숙제·제출함', mod: '관리만 (회원·글·댓글)' };
  const PERMS = {
    owner: () => true,
    admin: (p) => p !== 'roles_admin',
    teacher: (p) => p === 'content' || p === 'review',
    mod: (p) => ['notice', 'pass', 'charge', 'finance_read', 'members', 'moderate'].includes(p),
  };
  const staffRole = () => (me && me.role === 'admin' ? 'owner' : (me && me.staff) || null);
  const can = (perm) => { const r = staffRole(); return !!(r && PERMS[r](perm)); };
  const isAdmin = () => ['owner', 'admin'].includes(staffRole()); // 모든 관리 기능 (OWNER / ADMIN)
  const staffTag = () => { const r = staffRole(); return r ? ` (${r === 'owner' ? '선생님' : ROLE_NAME[r]})` : ''; };

  /* ---------- 학생 등급 (student_tiers.sql 의 tier_allows() 와 같은 표예요. 바꾸면 SQL 도 같이 바꿔요) ----------
     STUDENT 전부 · SOLVER 문제만(강의·라이브 X) · LISTENER 강의·라이브만(문제·라이브 문제 X). 직원은 제한 없음 */
  const TIER_NAME = { student: 'STUDENT', solver: 'SOLVER', listener: 'LISTENER' };
  const TIER_DESC = { student: '모든 기능', solver: '문제만 (강의·라이브 제외)', listener: '문제·라이브 문제 제외 모두' };
  const TIER_OK = { student: () => true, solver: (f) => f === 'problem', listener: (f) => f === 'lecture' || f === 'live' };
  const myTier = () => (staffRole() ? 'student' : (me && me.tier) || 'student');
  const tierCan = (feat) => (TIER_OK[myTier()] || TIER_OK.student)(feat); // feat: lecture / problem / live / live_problem
  const tierTag = () => (myTier() === 'student' ? '' : ` · ${TIER_NAME[myTier()]}`);

  /* ---------- V3.1.0 : 티어 · 뱃지 · 이름(별명) · 난이도 ---------- */
  const APP_VERSION = '4.5.4f';
  // 안드로이드 앱(APK) 직접 내려받기 — 구글 드라이브 파일 ID (바꾸려면 이 ID만 고치세요)
  const APK_ID = '1BpEsJ6MbUUJK92qgSJaLRJ3Wq3kc4JcX';
  const APK_URL = `https://drive.google.com/uc?export=download&id=${APK_ID}`;
  // 누적 점수 → 티어. Bronze·Silver·Gold 는 V~I 5단계, Platinum~Master 는 X~I 10단계로 똑같이 나눠요.
  // 티어 표는 DB(tiers)에 있고 [관리 → 🏅 티어]에서 고쳐요. DB 표가 없을 때만 아래 기본표를 써요. (v320_tiers.sql 의 시작값과 같아요)
  const DEFAULT_TIERS = [
    { n: 'Bronze', min: 0, c: ['#f0b27a', '#9c5a1e'], g: 'circle' },
    { n: 'Silver', min: 2000, c: ['#f1f5f9', '#8795a8'], g: 'tri' },
    { n: 'Gold', min: 7000, c: ['#ffe27a', '#d19a00'], g: 'sq' },
    { n: 'Platinum', min: 22000, c: ['#8ff0e0', '#16a394'], g: 'dia' },
    { n: 'Diamond', min: 52000, c: ['#9fd4ff', '#2563eb'], g: 'hex' },
    { n: 'Master', min: 112000, c: ['#d9a8ff', '#7c2ae0'], g: 'star' },
    { n: 'Grandmaster', min: 200000, c: ['#ffb36b', '#c2410c'], g: 'flame' },
  ];
  let TIERS = DEFAULT_TIERS.slice();
  let TIER_ROWS = []; // DB 에서 읽은 티어 (id 포함)
  let TIER_DB = false; // tiers 표가 있나?
  // 단계: Bronze·Silver·Gold 는 5단계(V→I), 그 위 티어는 10단계(X→I), 맨 위 티어(Grandmaster)는 단계 없이 10만 점마다 이름 숫자가 올라가요 (200,000 = Grandmaster 200).
  const ROMAN5 = ['V', 'IV', 'III', 'II', 'I'];
  const ROMAN10 = ['X', 'IX', 'VIII', 'VII', 'VI', 'V', 'IV', 'III', 'II', 'I'];
  const GM_STEP = 100000;
  const tierLevels = (i) => (i >= TIERS.length - 1 ? 0 : /^(bronze|silver|gold)$/i.test(TIERS[i].n) ? 5 : 10); // 0 = 단계 없음(맨 위 티어)
  function tierOf(score) {
    const sc = Math.max(0, Number(score) || 0);
    let i = TIERS.length - 1;
    while (i > 0 && sc < TIERS[i].min) i -= 1;
    const t = TIERS[i];
    const L = tierLevels(i);
    if (!L) { // 맨 위 티어: Grandmaster 200, 300 …
      const n = Math.floor(sc / GM_STEP);
      const lo = Math.max(t.min, n * GM_STEP);
      return { i, lv: 0, roman: String(n * 100), name: `${t.n} ${n * 100}`, lo, hi: (n + 1) * GM_STEP, score: sc };
    }
    const R = L === 5 ? ROMAN5 : ROMAN10;
    const step = (TIERS[i + 1].min - t.min) / L;
    const lv = Math.min(L - 1, Math.floor((sc - t.min) / step));
    return { i, lv, roman: R[lv], name: `${t.n} ${R[lv]}`, lo: t.min + lv * step, hi: lv < L - 1 ? t.min + (lv + 1) * step : TIERS[i + 1].min, score: sc };
  }
  const tierStepText = (i, nextMin, curMin) => { // 안내/관리 화면용
    const L = tierLevels(i);
    return L ? `${L}단계 · 한 단계 ${Math.round(((nextMin - curMin) / L) * 10) / 10}점` : '단계 없음 · 10만 점마다 숫자가 올라가요';
  };

  // 뱃지 문양 (40×40 칸 안, 방패 가운데 위쪽). 이름은 티어 편집 화면의 선택 칸에 나와요.
  const GLYPH = {
    circle: ['동그라미', '<circle cx="20" cy="15" r="5.5"/>'],
    tri: ['삼각형', '<path d="M20 8.5 L26.5 20 H13.5 Z"/>'],
    sq: ['네모', '<rect x="14.5" y="9.5" width="11" height="11" rx="2"/>'],
    dia: ['마름모', '<path d="M20 7.5 L27.5 15 L20 22.5 L12.5 15 Z"/>'],
    hex: ['육각형', '<path d="M20 8 L26.6 11.8 V19.4 L20 23.2 L13.4 19.4 V11.8 Z"/>'],
    oct: ['팔각형', '<path d="M16.5 7.5 H23.5 L28.5 12.5 V18.5 L23.5 23.5 H16.5 L11.5 18.5 V12.5 Z"/>'],
    spark: ['반짝임', '<path d="M20 6.5 L22.4 12.6 L28.5 15 L22.4 17.4 L20 23.5 L17.6 17.4 L11.5 15 L17.6 12.6 Z"/>'],
    star: ['별', '<path d="M20 7.5 L22.5 12.8 L28.3 13.5 L24 17.5 L25.2 23.2 L20 20.3 L14.8 23.2 L16 17.5 L11.7 13.5 L17.5 12.8 Z"/>'],
    crown: ['왕관', '<path d="M12 21.5 L13 10.5 L17 15 L20 8 L23 15 L27 10.5 L28 21.5 Z"/>'],
    drop: ['물방울', '<path d="M20 6.5 C20 6.5 14 13 14 17 A6 6 0 0 0 26 17 C26 13 20 6.5 20 6.5 Z"/>'],
    gem: ['보석', '<path d="M14 11 L17 7.5 H23 L26 11 L20 23 Z"/>'],
    flame: ['불꽃', '<path d="M20 6.5 C21.5 11 26.5 12.5 26.5 17.5 A6.5 6.5 0 0 1 13.5 17.5 C13.5 14.5 15.5 13 16.5 10.5 C17.5 12 18.5 12.5 20 6.5 Z"/>'],
    bolt: ['번개', '<path d="M22.5 6.5 L13.5 16 H19 L17.5 23.5 L26.5 13.5 H21 Z"/>'],
    moon: ['달', '<path d="M24.5 7.5 A8 8 0 1 0 24.5 22.5 A6.5 6.5 0 1 1 24.5 7.5 Z"/>'],
    leaf: ['잎', '<path d="M13 22 C13 13 18 8 27.5 7.5 C27.5 16 23 22 13 22 Z"/>'],
    heart: ['하트', '<path d="M20 23 L12.8 15.5 A4 4 0 0 1 20 11 A4 4 0 0 1 27.2 15.5 Z"/>'],
    plus: ['십자', '<path d="M18 7.5 H22 V13 H27.5 V17 H22 V22.5 H18 V17 H12.5 V13 H18 Z"/>'],
    ring: ['고리', '<path fill-rule="evenodd" d="M20 8 A7 7 0 1 0 20 22 A7 7 0 1 0 20 8 Z M20 12 A3 3 0 1 1 20 18 A3 3 0 1 1 20 12 Z"/>'],
    chev: ['화살표', '<path d="M12 17.5 L20 9 L28 17.5 L25.5 20 L20 14.3 L14.5 20 Z"/>'],
  };
  const glyphSvg = (g) => (GLYPH[g] || GLYPH.circle)[1];
  const SHIELD = 'M20 2 L35.5 7.5 V20 C35.5 28.5 28.8 34.6 20 38 C11.2 34.6 4.5 28.5 4.5 20 V7.5 Z';
  const shieldSvg = (id, c1, c2, g, gold) => `<linearGradient id="${id}g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${c1}"/><stop offset="1" stop-color="${c2}"/></linearGradient>
      <symbol id="${id}" viewBox="0 0 40 40"><path d="${SHIELD}" fill="url(#${id}g)" stroke="${c2}" stroke-width="1.6" stroke-linejoin="round"/><g fill="#fff" fill-opacity=".93">${glyphSvg(g)}</g>${gold ? `<path d="${SHIELD}" fill="none" stroke="#ffe27a" stroke-width="1"/>` : ''}</symbol>`;
  function ensureDefs() { // 뱃지 그림(방패 + 문양)은 만들어 두고 계속 재사용해요. 티어가 바뀌면 다시 만들어요.
    let d = document.getElementById('tbDefs');
    if (!d) {
      d = document.createElement('div');
      d.id = 'tbDefs';
      d.style.cssText = 'position:absolute;width:0;height:0;overflow:hidden';
      document.body.appendChild(d);
    }
    d.innerHTML = `<svg width="0" height="0" aria-hidden="true"><defs>${TIERS.map((t, i) => shieldSvg(`tbs${i}`, t.c[0], t.c[1], t.g, i === TIERS.length - 1)).join('')}</defs></svg>`;
  }
  let pvSeq = 0;
  // 화면 어디서나 쓰는 "혼자 서 있는" 뱃지 (티어 편집 미리보기용)
  function tierPreview(c1, c2, g, roman = 'I', size = 40) {
    const id = `tpv${++pvSeq}`;
    return `<svg viewBox="0 0 40 40" width="${size}" height="${size}" aria-hidden="true"><defs>${shieldSvg(id, c1, c2, g, false)}</defs><use href="#${id}" width="40" height="40"/><text x="20" y="33" text-anchor="middle" font-size="9.5" font-weight="800" fill="#fff" stroke="rgba(0,0,0,.45)" stroke-width=".7" paint-order="stroke" font-family="system-ui,sans-serif">${esc(roman)}</text></svg>`;
  }
  function tierBadge(score, size = 20) {
    const k = tierOf(score);
    return `<span class="tbadge" title="${esc(k.name)} · ${k.score}점"><svg viewBox="0 0 40 40" width="${size}" height="${size}" role="img" aria-label="${esc(k.name)}"><use href="#tbs${k.i}" width="40" height="40"/><text x="20" y="33" text-anchor="middle" font-size="9.5" font-weight="800" fill="#fff" stroke="rgba(0,0,0,.45)" stroke-width=".7" paint-order="stroke" font-family="system-ui,sans-serif">${k.roman}</text></svg></span>`;
  }
  async function loadTiers() {
    try {
      const { data, error } = await sb.from('tiers').select('*').order('min_score');
      if (error || !data || !data.length || data[0].min_score !== 0) throw error || new Error('empty');
      TIER_ROWS = data;
      TIERS = data.map((t) => ({ n: t.name, min: t.min_score, c: [t.c1, t.c2], g: GLYPH[t.glyph] ? t.glyph : 'circle' }));
      TIER_DB = true;
    } catch (e) { TIER_ROWS = []; TIERS = DEFAULT_TIERS.slice(); TIER_DB = false; }
    ensureDefs();
  }

  // 학생 이름표 (별명 · 누적 점수). student_directory() — v310_ranking.sql 전이면 조용히 비어 있어요.
  let DIR = new Map();
  let DIR_OK = false;
  async function loadDir() {
    try {
      const { data, error } = await sb.rpc('student_directory');
      if (error || !data) throw error || new Error('no data');
      DIR = new Map(data.map((d) => [d.user_id, d]));
      DIR_OK = true;
    } catch (e) { DIR = new Map(); DIR_OK = false; }
  }
  const dname = (uid, fb = '') => { const d = DIR.get(uid); return d ? d.name : fb; }; // 직원에게는 "별명 (ID)"
  // SOLVER 등급 학생은 남에게 티어·프로필이 안 보여요 (v380_hide_solver.sql 이 점수를 -1 로 내려줘요)
  const hiddenUid = (uid) => DIR_OK && DIR.has(uid) && DIR.get(uid).score < 0;
  const badgeFor = (uid, size = 18) => (DIR_OK && DIR.has(uid) && !hiddenUid(uid) ? tierBadge(DIR.get(uid).score, size) : '');
  const who = (uid, name, link = true) => `${badgeFor(uid)}${link && uid && !hiddenUid(uid) ? `<a class="ulink" href="#/u/${uid}">${esc(name)}</a>` : `<span class="uname">${esc(name)}</span>`}`;
  const selfName = () => dname(me.id, me.username);
  const whoHtml = () => `${staffRole() ? esc(me.username) : `<a class="ulink" href="#/u/${me.id}">${badgeFor(me.id, 20)}${esc(selfName())}</a>`}${staffTag()}${tierTag()}`;

  // 난이도 표 (difficulties) — 표가 없으면 예전 4개로 동작
  let DIFF_LIST = [
    { name: 'Beginner', points: 5, color: '#16a34a', builtin: true }, { name: 'Intermediate', points: 10, color: '#2563eb', builtin: true },
    { name: 'Advanced', points: 20, color: '#7e22ce', builtin: true }, { name: 'ELITE', points: 30, color: '#db2777', builtin: true },
  ];
  let RK_READY = false;
  async function loadDiffs() {
    try {
      const { data, error } = await sb.from('difficulties').select('*').order('position').order('name');
      if (error || !data || !data.length) throw error || new Error('empty');
      DIFF_LIST = data;
      RK_READY = true;
    } catch (e) { RK_READY = false; }
  }
  // 문제 카드 배경: 난이도마다 달라요 (Bronze·Iron·Gold·Diamond·Ruby·Master 는 전용 무늬, 나머지는 난이도 색으로 은은하게)
  const DX_OWN = ['bronze', 'iron', 'gold', 'diamond', 'ruby', 'master'];
  const dxCls = (name) => (name === 'ELITE' ? '' : `dx ${DX_OWN.includes(String(name).toLowerCase()) ? `dx-${String(name).toLowerCase()}` : ''}`);
  const dxStyle = (name) => { const d = DIFF_LIST.find((x) => x.name === name); return d && /^#[0-9a-f]{6}$/i.test(d.color || '') ? ` style="--dc:${d.color}"` : ''; };
  const diffNames = () => DIFF_LIST.map((d) => d.name);
  const diffPts = (name) => { const d = DIFF_LIST.find((x) => x.name === name); return d ? d.points : 10; };
  const diffTag = (name, text) => {
    const t = text == null ? name : text;
    if (['Beginner', 'Intermediate', 'Advanced', 'ELITE'].includes(name)) return `<span class="dbadge d-${name}">${esc(t)}</span>`;
    const d = DIFF_LIST.find((x) => x.name === name);
    const c = (d && d.color) || '#64748b';
    return `<span class="dbadge" style="background:${esc(c)}26;color:${esc(c)}">${esc(t)}</span>`;
  };


  const lockedPage = (what) => ['<div class="card pad center"><h2>🔒 이용할 수 없어요</h2><p class="muted">내 등급(' + TIER_NAME[myTier()] + ')에서는 ' + esc(what) + ' 기능을 쓸 수 없어요.</p></div>'];

  function toast(msg, bad = false) {
    const t = document.createElement('div');
    t.className = 'toast' + (bad ? ' bad' : '');
    t.textContent = msg;
    $('#toasts').appendChild(t);
    setTimeout(() => t.remove(), 3000);
  }

  function setTheme(t) {
    document.documentElement.dataset.theme = t;
    try { localStorage.setItem('theme', t); } catch (e) { /* 무시 */ }
    const b = $('#themeBtn');
    if (b) b.textContent = t === 'dark' ? '☀️' : '🌙';
  }
  const toggleTheme = () => setTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark');

  // 글 내용 표시: ``` 로 감싼 부분은 코드 블록으로
  // 공지용 마크다운: # 제목 · **굵게** · *기울임* · ~~취소선~~ · `코드` · [링크](주소) · - 목록 · 1. 번호 · > 인용 · --- 구분선 · | 표 |
  function mdInline(raw) {
    return esc(raw)
      .replace(/`([^`\n]+)`/g, '<code class="ic">$1</code>')
      .replace(/\*\*([^*\n]+)\*\*/g, '<b>$1</b>')
      .replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, '$1<i>$2</i>')
      .replace(/~~([^~\n]+)~~/g, '<s>$1</s>')
      .replace(/\[([^\]\n]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
  }
  function mdBlock(text) {
    const L = String(text).replace(/\r/g, '').split('\n');
    const out = [];
    let i = 0;
    const isRow = (l) => /^\s*\|.*\|\s*$/.test(l);
    const cells = (l) => l.trim().replace(/^\||\|$/g, '').split('|').map((c) => c.trim());
    while (i < L.length) {
      const l = L[i];
      if (!l.trim()) { i += 1; continue; }
      let m;
      if ((m = l.match(/^(#{1,4})\s+(.*)$/))) { out.push(`<h${m[1].length + 1} class="md-h">${mdInline(m[2])}</h${m[1].length + 1}>`); i += 1; continue; }
      if (/^\s*(-{3,}|\*{3,})\s*$/.test(l)) { out.push('<hr class="md-hr">'); i += 1; continue; }
      if (isRow(l) && i + 1 < L.length && /^\s*\|?[\s:|-]+\|[\s:|-]*$/.test(L[i + 1]) && L[i + 1].includes('-')) {
        const head = cells(l);
        const rows = [];
        i += 2;
        while (i < L.length && isRow(L[i])) { rows.push(cells(L[i])); i += 1; }
        out.push(`<div class="mk-tablewrap"><table class="mk-table"><thead><tr>${head.map((c) => `<th>${mdInline(c)}</th>`).join('')}</tr></thead><tbody>${rows.map((r) => `<tr>${head.map((_, k) => `<td>${mdInline(r[k] || '')}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`);
        continue;
      }
      if (/^\s*>/.test(l)) {
        const q = [];
        while (i < L.length && /^\s*>/.test(L[i])) { q.push(L[i].replace(/^\s*>\s?/, '')); i += 1; }
        out.push(`<blockquote class="md-q">${q.map(mdInline).join('<br>')}</blockquote>`);
        continue;
      }
      if (/^\s*[-*+]\s+/.test(l) || /^\s*\d+[.)]\s+/.test(l)) {
        const ol = /^\s*\d+[.)]\s+/.test(l);
        const items = [];
        while (i < L.length && (ol ? /^\s*\d+[.)]\s+/ : /^\s*[-*+]\s+/).test(L[i])) { items.push(L[i].replace(ol ? /^\s*\d+[.)]\s+/ : /^\s*[-*+]\s+/, '')); i += 1; }
        out.push(`<${ol ? 'ol' : 'ul'} class="md-l">${items.map((t) => `<li>${mdInline(t)}</li>`).join('')}</${ol ? 'ol' : 'ul'}>`);
        continue;
      }
      const para = [];
      while (i < L.length && L[i].trim() && !/^(#{1,4}\s|\s*(-{3,}|\*{3,})\s*$|\s*>|\s*[-*+]\s+|\s*\d+[.)]\s+)/.test(L[i]) && !isRow(L[i])) { para.push(L[i]); i += 1; }
      if (!para.length) { para.push(L[i]); i += 1; }
      out.push(`<p class="md-p">${para.map(mdInline).join('<br>')}</p>`);
    }
    return `<div class="md">${out.join('')}</div>`;
  }
  function renderContent(text, md = false) {
    return String(text ?? '').split('```').map((part, i) => {
      if (i % 2 === 1) {
        const code = part.replace(/^(python|py|text|c|cpp|java|js)\r?\n/i, '').replace(/^\r?\n/, '');
        return `<pre><code>${esc(code)}</code></pre>`;
      }
      return part.trim() ? (md ? mdBlock(part) : `<div class="txt">${esc(part)}</div>`) : '';
    }).join('');
  }

  function ytId(url) {
    try {
      const u = new URL(url);
      let id = null;
      if (u.hostname.includes('youtu.be')) id = u.pathname.slice(1).split('/')[0];
      else if (u.searchParams.get('v')) id = u.searchParams.get('v');
      else {
        const m = u.pathname.match(/\/(embed|live|shorts)\/([\w-]+)/);
        if (m) id = m[2];
      }
      return id && /^[\w-]{6,20}$/.test(id) ? id : null;
    } catch (e) { return null; }
  }

  async function download(bucket, path, name) {
    const { data, error } = await sb.storage.from(bucket).createSignedUrl(path, 120, { download: name });
    if (error || !data) return toast('파일을 열 수 없어요', true);
    const a = document.createElement('a');
    a.href = data.signedUrl;
    a.download = name;
    document.body.appendChild(a);
    a.click();
    a.remove();
  }

  // 저장소에서 파일 지우기 (파일마다 저장소 이름이 다를 수 있어요)
  async function removeFiles(files) {
    const by = {};
    (files || []).forEach((f) => {
      const b = f.bucket || 'attachments';
      (by[b] = by[b] || []).push(f.path);
    });
    for (const b of Object.keys(by)) await sb.storage.from(b).remove(by[b]);
  }

  /* ---------- 로그인 / 가입 신청 ---------- */
  function renderAuth(tab = 'login') {
    document.body.classList.remove('shell', 'menu-open');
    const signup = tab === 'signup';
    app.innerHTML = `
      <div class="auth-wrap"><div class="card auth">
        <h1 class="logo">${esc(ICON)} ${esc(SITE)}</h1>
        <p class="muted center">파이썬 강의 사이트</p>
        <div class="tabs" style="justify-content:center">
          <button data-t="login" class="${signup ? '' : 'on'}">로그인</button>
          <button data-t="signup" class="${signup ? 'on' : ''}">가입 신청</button>
        </div>
        <form id="authForm">
          <label>ID<input type="text" id="aid" autocomplete="username" autocapitalize="none" placeholder="영문 소문자·숫자·_ (3~20자)" required></label>
          ${signup ? '<label>별명 <small class="muted">(사이트에 보여요 · 1~20자)</small><input type="text" id="anick" maxlength="20" autocomplete="nickname" placeholder="한글·영문·숫자" required></label>' : ''}
          <label>비밀번호<input type="password" id="apw" autocomplete="${signup ? 'new-password' : 'current-password'}" placeholder="6자 이상" required></label>
          ${signup ? '<label>비밀번호 확인<input type="password" id="apw2" autocomplete="new-password" required></label><p class="muted small">가입을 신청하면 선생님이 승인한 뒤에 사용할 수 있어요.</p>' : ''}
          <div class="form-actions"><button class="primary" id="authBtn" style="width:100%">${signup ? '가입 신청하기' : '로그인'}</button></div>
        </form>
      </div></div>`;
    app.querySelectorAll('[data-t]').forEach((b) => (b.onclick = () => renderAuth(b.dataset.t)));
    $('#authForm').onsubmit = (e) => { e.preventDefault(); signup ? doSignup() : doLogin(); };
  }

  async function doLogin() {
    const id = $('#aid').value.trim().toLowerCase();
    const pw = $('#apw').value;
    const btn = $('#authBtn');
    btn.disabled = true;
    const { error } = await sb.auth.signInWithPassword({ email: emailOf(id), password: pw });
    if (error) {
      btn.disabled = false;
      return toast('ID 또는 비밀번호가 맞지 않아요', true);
    }
    boot();
  }

  const NICK_RE = /^[0-9A-Za-z가-힣ㄱ-ㅎㅏ-ㅣ _.-]{1,20}$/;
  const NICK_MSG = { invalid: '별명은 한글·영문·숫자·공백·_ . - 로 1~20자예요', reserved: '운영진처럼 보이는 별명은 쓸 수 없어요', taken: '이미 쓰고 있는 별명이거나 다른 사람의 ID예요', locked: '선생님이 정해준 별명이라 바꿀 수 없어요', login: '로그인이 필요해요' };
  async function doSignup() {
    const id = $('#aid').value.trim().toLowerCase();
    const pw = $('#apw').value;
    if (!ID_RE.test(id)) return toast('ID는 영문 소문자, 숫자, _ 로 3~20자예요', true);
    if (pw.length < 6) return toast('비밀번호는 6자 이상이어야 해요', true);
    if (pw !== $('#apw2').value) return toast('비밀번호 확인이 달라요', true);
    const nick = $('#anick').value.trim().replace(/\s+/g, ' ');
    if (!NICK_RE.test(nick)) return toast(NICK_MSG.invalid, true);
    const av = await sb.rpc('nickname_available', { p_nick: nick }); // v350 SQL 전이면 검사 없이 통과
    if (!av.error && av.data !== 'ok') return toast(NICK_MSG[av.data] || '쓸 수 없는 별명이에요', true);
    const btn = $('#authBtn');
    btn.disabled = true;
    signingUp = true;
    const { error } = await sb.auth.signUp({ email: emailOf(id), password: pw, options: { data: { username: id, nickname: nick } } });
    await sb.auth.signOut();
    signingUp = false;
    if (error) {
      btn.disabled = false;
      const dup = /registered|already|exists/i.test(error.message);
      return toast(dup ? '이미 있는 ID예요' : '가입 신청에 실패했어요: ' + error.message, true);
    }
    renderAuth('login');
    toast('가입 신청 완료! 선생님이 승인하면 로그인할 수 있어요');
  }

  async function logout() {
    await sb.auth.signOut();
    try { sessionStorage.removeItem('pn_app'); } catch (e) {}
    location.replace('landing/'); // 로그아웃하면 소개 페이지로
  }

  function renderStatus(kind) {
    document.body.classList.remove('shell', 'menu-open');
    const pending = kind === 'pending';
    app.innerHTML = `
      <div class="auth-wrap"><div class="card auth center">
        <h2>${pending ? '⏳ 승인 대기 중이에요' : '🚫 사용할 수 없는 계정이에요'}</h2>
        <p class="muted">${pending ? '선생님이 가입을 승인하면 사이트를 쓸 수 있어요.' : '가입이 거절되었거나 사용이 중지된 계정이에요. 선생님께 문의해주세요.'}</p>
        <div class="form-actions" style="justify-content:center">
          ${pending ? '<button class="primary" id="reBtn">다시 확인</button>' : ''}
          <button class="ghost" id="loBtn">로그아웃</button>
        </div>
      </div></div>`;
    $('#loBtn').onclick = logout;
    if (pending) $('#reBtn').onclick = boot;
  }

  /* ---------- 앱 뼈대 ---------- */
  const NAV = [
    ['home', '🏠', '홈', '', '배우기'], ['learn', '📚', '학습', '', '배우기'], ['lectures', '🎬', '강의', '', '배우기'], ['sets', '📄', '문제', '', '배우기'], ['golive/', '📡', '라이브 · 저지', 'ext', '배우기'],
    ['ranking', '🏆', '랭킹', '', '경쟁'], ['exam', '📝', '시험', '', '경쟁'],
    ['board', '💬', '게시판', '', '소통'], ['market', '🛍️', '마켓', '', '소통'],
  ];

  function renderShell() {
    const items = NAV.filter(([k]) => (k === 'lectures' ? tierCan('lecture') : k === 'sets' ? tierCan('problem') : k === 'golive/' ? tierCan('live') : true));
    items.push(['me', '👤', '나', '', '내 공간']);
    if (can('review')) items.push(['review', '📥', '제출함', '', '내 공간']);
    if (staffRole()) items.push(['admin', '🛠️', '관리자', '', '내 공간']);
    let grp = '';
    const navHtml = items.map(([k, ic, name, soon, g]) => {
      const head = g !== grp ? `<div class="nav-grp">${g}</div>` : '';
      grp = g;
      return head + (soon === 'ext' ? `<a href="${k}" data-k="${k}"><i>${ic}</i> ${name}</a>` : `<a href="#/${k}" data-k="${k}"><i>${ic}</i> ${name}${k === 'me' ? '<span class="nbadge" data-bell hidden></span>' : ''}</a>`);
    }).join('');
    document.body.classList.add('shell');
    app.innerHTML = `
      <header class="top">
        <button class="icon" id="menuBtn" aria-label="메뉴" aria-expanded="false" title="메뉴">☰</button>
        <a class="brand" href="#/home">${esc(ICON)} ${esc(SITE)}</a>
        <div class="spacer"></div>
        <span id="gChips" class="gchips"></span>
        <span class="who">${whoHtml()}</span>
        ${sideOn() && CONFIG.NESTMATE_URL ? `<a class="icon shop" href="${esc(CONFIG.NESTMATE_URL)}" target="_blank" rel="noopener" title="Nestmate 바로가기">🪺<span class="lbl"> Nestmate</span></a>` : ''}
        ${sideOn() && CONFIG.SHOP_URL ? `<a class="icon shop" href="${esc(CONFIG.SHOP_URL)}" target="_blank" rel="noopener" title="${esc(CONFIG.SHOP_NAME || '민혁닷컴')} 바로가기">🛒<span class="lbl"> ${esc(CONFIG.SHOP_NAME || '민혁닷컴')}</span></a>` : ''}
        <button class="icon" id="themeBtn" title="다크모드 켜기/끄기"></button>
        <a class="icon bellbtn" href="#/me/notif" title="알림" aria-label="알림">🔔<span class="nbadge" data-bell hidden></span></a>
        <a class="avbtn" href="#/me" title="나 (프로필·캐릭터·설정)" aria-label="나"></a>
        <button class="ghost" id="logoutBtn">로그아웃</button>
      </header>
      <nav class="menu" id="menu">
        <a class="side-brand" href="#/home">${esc(ICON)} ${esc(SITE)}</a>
        ${navHtml}
      </nav>
      <div class="menu-back" id="menuBack"></div>
      <main id="view"></main>
      <nav class="tabbar" id="tabbar">
        <a href="#/home" data-k="home"><i>🏠</i>홈</a>
        <a href="#/learn" data-k="learn"><i>📚</i>학습</a>
        <a href="#/ranking" data-k="ranking"><i>🏆</i>랭킹</a>
        <a href="#/me" data-k="me"><i>👤</i>나<span class="nbadge" data-bell hidden></span></a>
        <button type="button" id="moreBtn"><i>☰</i>더보기</button>
      </nav>`;
    refreshHeadAv();
    const setMenu = (open) => { document.body.classList.toggle('menu-open', open); $('#menuBtn').setAttribute('aria-expanded', open ? 'true' : 'false'); };
    $('#menuBtn').onclick = () => setMenu(!document.body.classList.contains('menu-open'));
    $('#moreBtn').onclick = () => setMenu(!document.body.classList.contains('menu-open'));
    $('#menuBack').onclick = () => setMenu(false);
    $('#menu').onclick = (e) => { if (e.target.closest('a')) setMenu(false); };
    document.onkeydown = (e) => { if (e.key === 'Escape') setMenu(false); };
    setTheme(document.documentElement.dataset.theme || 'light');
    $('#themeBtn').onclick = toggleTheme;
    $('#logoutBtn').onclick = logout;
  }

  /* ---------- 라우터 ---------- */
  async function route(keepScroll = false) {
    if (!me || me.status !== 'approved' || !$('#view')) return;
    const y = window.scrollY;
    flushDrafts();
    const [a, b, c] = (location.hash.replace(/^#\//, '') || 'home').split('/');
    const key = a === 'settings' ? 'me' : a === 'u' ? 'ranking' : a === 'board' || a === 'write' ? (b === 'problem' ? 'board/problem' : 'board') : a === 'market' ? 'market' : a === 'lecture' ? 'lectures' : a === 'problems' ? 'board/problem' : a === 'set' || a === 'p' ? 'sets' : a;
    document.body.classList.remove('menu-open', 'exam-on');
    document.querySelectorAll('#menu a').forEach((l) => l.classList.toggle('on', l.dataset.k === key));
    document.querySelectorAll('#tabbar [data-k]').forEach((l) => l.classList.toggle('on', l.dataset.k === key));

    const pages = {
      home: () => pageHome(),
      lectures: () => pageLectures(),
      lecture: () => pageLecture(b),
      problems: () => pageBoard('problem'),
      sets: () => pageSets(),
      ranking: () => pageRanking(),
      u: () => pageProfile(b),
      set: () => pageSet(b),
      p: () => pageProblem(b, c),
      learn: () => pageLearn(b, c),
      review: () => pageReview(b, c),
      board: () => (b === 'problem' ? pageBoard('problem') : pageBoardAll(b)),
      market: () => pageMarket(b),
      exam: () => pageExam(b),
      post: () => pagePost(b),
      write: () => (BOARDS[b] ? pageWrite(b) : notFound()),
      edit: () => pageEdit(b),
      admin: () => pageAdmin(),
      settings: () => pageSettings(b, c),
      me: () => pageSettings(b, c),
      judge: () => pageSoon('⚖️ 온라인 저지', '코드를 제출하면 자동으로 채점해주는 기능이에요. 수업 시간에 선생님 노트북에서 돌리는 방식으로 곧 붙일 예정이에요.'),
      live: () => pageSoon('📡 라이브', '수업 시간에 실시간으로 강의를 보는 기능이에요. 곧 붙일 예정이에요.'),
    };

    const tok = ++navTok;
    const v = $('#view');
    v.innerHTML = '<p class="loading">불러오는 중…</p>';
    if (a === 'home' || a === 'ranking' || a === 'u') { // 점수가 바뀌었을 수 있어서 이름표를 새로 받아요
      await loadDir();
      const w = $('.who'); if (w) w.innerHTML = whoHtml();
      if (tok !== navTok) return;
    }
    // 학생 등급 제한 (직원은 해당 없음)
    const need = { lectures: ['lecture', '강의'], lecture: ['lecture', '강의'], sets: ['problem', '문제'], set: ['problem', '문제'], p: ['problem', '문제'], problems: ['problem', '문제'] }[a];
    if (need && !tierCan(need[0])) { v.innerHTML = lockedPage(need[1])[0]; return; }
    try {
      const [html, bind] = await (pages[a] || notFound)();
      if (tok !== navTok) return;
      v.innerHTML = html;
      if (bind) bind(v);
      window.scrollTo(0, keepScroll ? y : 0);
      refreshHeadAv();
      growRefresh(a === 'home' || a === 'me' || a === 'settings').then(() => { if (a === 'home' && tok === navTok) { injectHomeGrow(); injectEventBanner(); } });
      if (a === 'home') loadEvents().then(() => { if (tok === navTok) injectEventBanner(); });
    } catch (err) {
      if (tok !== navTok) return;
      console.error(err);
      v.innerHTML = '<div class="card pad center">불러오는 중에 문제가 생겼어요. 새로고침 해보세요.</div>';
    }
  }

  const notFound = async () => ['<div class="card pad center">페이지를 찾을 수 없어요.</div>'];
  const pageSoon = async (title, text) => [`<div class="card pad center"><h2>${title}</h2><p class="muted">${esc(text)}</p><span class="badge warn">준비 중</span></div>`];

  /* ---------- 홈 ---------- */
  async function homeStats() {
    try {
      const r = await sb.rpc('home_stats');
      if (!r.error && r.data) return r.data;
    } catch (e) { /* SQL 미적용 → 아래 대체 */ }
    // v330_home.sql 을 아직 안 돌렸을 때: 가능한 것만 계산
    const wk = new Date(Date.now() - 7 * 864e5).toISOString();
    const [t, w] = await Promise.all([
      sb.from('exercises').select('id', { count: 'exact', head: true }),
      sb.from('exercises').select('id', { count: 'exact', head: true }).gte('created_at', wk),
    ]);
    return { total: t.count || 0, week: w.count || 0, mine: null, unsolved: null, new_list: [], unsolved_list: [], fallback: true };
  }

  /* ---------- 공지 상단 고정 · 티어 승급 배너 (v390_tierup.sql) ---------- */
  let BAN_OK = false; // posts_view 에 banner 칸이 있으면 true (v453)
  const NB_KEY = 'pn_nban'; // 닫은 공지 배너 번호들
  const nbClosed = () => { try { return JSON.parse(localStorage.getItem(NB_KEY) || '[]'); } catch (e) { return []; } };
  let PIN_OK = false; // posts_view 에 pinned 칸이 있으면 true (v390 전이면 조용히 꺼져요)
  const koSort = (a, b) => String(a.title || '').localeCompare(String(b.title || ''), 'ko');
  // 공지 목록: 고정 글(가나다 순) 먼저, 나머지는 최신순
  function orderNotices(rows) {
    const pin = rows.filter((x) => x.pinned).sort(koSort);
    return pin.concat(rows.filter((x) => !x.pinned));
  }
  async function loadNotices(cols) {
    const r0 = await sb.from('posts_view').select(cols + ',pinned,banner').eq('board', 'notice').order('created_at', { ascending: false });
    if (!r0.error) { PIN_OK = true; BAN_OK = true; return r0; }
    const r = await sb.from('posts_view').select(cols + ',pinned').eq('board', 'notice').order('created_at', { ascending: false });
    if (!r.error) { PIN_OK = true; return r; }
    return sb.from('posts_view').select(cols).eq('board', 'notice').order('created_at', { ascending: false });
  }
  const TU_KEY = 'pn_tuban';
  const tuToken = (b) => `${b.post_id}:${b.count}`;
  function tuBannerHtml(b) {
    if (!b || !b.post_id) return '';
    try { if (localStorage.getItem(TU_KEY) === tuToken(b)) return ''; } catch (e) { /* 저장소 막힘: 그냥 보여줘요 */ }
    const L = b.list || [];
    const names = L.slice(0, 3).map((x) => esc(x.name));
    const more = b.count - names.length;
    const who2 = names.join(' · ') + (more > 0 ? ` 외 ${more}명` : '');
    const tiers = Array.from(new Set(L.map((x) => x.to)));
    const what = tiers.length === 1 ? `<b>${esc(tiers[0])}</b> 티어로 ` : '';
    return `<div class="tubanner" id="tuBan"><a class="tub-main" href="#/post/${b.post_id}"><span class="tub-ico">🎉</span><span class="tub-txt"><b>${who2}</b> 님이 ${what}승급했어요! <span class="tub-go">축하하러 가기 →</span></span></a><button type="button" class="tub-x" id="tuX" aria-label="닫기" title="닫기">✕</button></div>`;
  }

  // 📱 앱으로 설치 카드 (이미 앱/홈 화면 설치 상태면 숨김)
  function appCardHtml() {
    const inApp = window.Capacitor || window.matchMedia('(display-mode: standalone)').matches || navigator.standalone;
    if (inApp) return '';
    const ios = /iPhone|iPad|iPod/i.test(navigator.userAgent);
    return `<div class="card app-dl"><div class="app-dl-t"><b>📱 앱으로 쓰기</b><span class="muted small">웹을 고치면 앱도 같이 바뀌어요</span></div>
      ${ios ? '<p class="muted small" style="margin:6px 0">아이폰은 Safari 에서 <b>공유 ▸ 홈 화면에 추가</b> 를 누르면 앱처럼 쓸 수 있어요.</p>' : `<a class="primary btn" href="${APK_URL}" download>⬇️ 안드로이드 앱 다운로드 (APK)</a><p class="muted small" style="margin:6px 0 0">받은 뒤 열어서 설치해요. "출처를 알 수 없는 앱" 허용이 필요할 수 있어요.</p>`}</div>`;
  }

  async function pageHome() {
    const wantProb = tierCan('problem');
    const [n, l, p, st, tu, exl] = await Promise.all([
      loadNotices('id,title,created_at'),
      sb.from('lectures').select('*').order('week', { ascending: false }).limit(1),
      sb.from('problem_sets').select('id,title,week').order('id', { ascending: false }).limit(1),
      wantProb ? homeStats() : Promise.resolve(null),
      Promise.resolve(sb.rpc('tierup_banner')).then((r) => (r && !r.error ? r.data : null), () => null),
      Promise.resolve(sb.rpc('exam_list')).then((r) => (r && !r.error ? r.data : null), () => null),
    ]);
    const lec = l.data && l.data[0];
    const prob = p.data && p.data[0];
    const allN = n.data || [];
    const pinned = allN.filter((x) => x.pinned).sort(koSort);
    const homeN = pinned.concat(allN.filter((x) => !x.pinned).slice(0, 3));
    const notices = homeN.map((x) => `<a class="row${x.pinned ? ' pinned' : ''}" href="#/post/${x.id}"><div class="row-main">${x.pinned ? '<span class="pinmark">📌</span> ' : ''}${esc(x.title)}</div><div class="muted small">${fmt(x.created_at)}</div></a>`).join('')
      || '<p class="muted center pad">아직 공지가 없어요.</p>';
    const isStaff = !!staffRole();
    const nbShut = nbClosed();
    if (exl && exl.now) EX_OFF = Date.parse(exl.now) - Date.now();
    const exHtml = ((exl && exl.exams) || []).filter((x) => x.status === 'open' && ['lobby', 'live'].includes(exPhase(x)) && !(exPhase(x) === 'live' && !x.entered && false)).slice(0, 2).map((x) => `<a class="nban exban" href="#/exam/${x.id}"><span class="nb-main"><span class="nb-ico">📝</span><span class="nb-txt">${esc(x.title)} — ${exPhase(x) === 'live' ? '🔴 지금 진행 중! 들어가기' : '🚪 입장할 수 있어요 (' + hhmm(x.start_at) + ' 시작)'}</span></span></a>`).join('');
    const nbHtml = exHtml + allN.filter((x) => x.banner && !nbShut.includes(x.id)).slice(0, 3).map((x) => `<div class="nban" data-nb="${x.id}"><a class="nb-main" href="#/post/${x.id}"><span class="nb-ico">📣</span><span class="nb-txt">${esc(x.title)}</span></a><button type="button" class="nb-x" data-nbx="${x.id}" aria-label="닫기" title="닫기">✕</button></div>`).join('');
    const plist = (arr, empty) => (arr && arr.length ? arr.map((x) => `<a class="row hp" href="#/set/${x.set_id}" data-ex="${x.id}"><div class="row-main"><span class="hp-d">${esc(x.difficulty || '')}</span> ${esc(x.title || '(제목 없음)')}</div><div class="muted small">${esc(x.set_name || '')}</div></a>`).join('') : `<p class="muted center pad">${empty}</p>`);
    let probHtml = '';
    if (wantProb && st) {
      const pct = st.mine != null && st.total ? Math.round((st.mine / st.total) * 100) : 0;
      const num = (v) => (v == null ? '–' : v);
      probHtml = `
      <div class="page-head"><h3>🧩 문제 현황</h3><a href="#/sets">문제 보러가기</a></div>
      <div class="stat-grid">
        <a class="stat" href="#/sets"><div class="stat-n">${num(st.total)}</div><div class="stat-l">제공되는 문제</div></a>
        ${isStaff ? '' : `<a class="stat ok" href="#/sets"><div class="stat-n">${num(st.mine)}</div><div class="stat-l">내가 푼 문제</div></a>`}
        <div class="stat new"><div class="stat-n">${num(st.week)}</div><div class="stat-l">최근 한 주간 새 문제</div></div>
        <div class="stat hot"><div class="stat-n">${num(st.unsolved)}</div><div class="stat-l">아직 아무도 못 푼 문제</div></div>
      </div>
      ${!isStaff && st.mine != null ? `<div class="prog" title="${pct}%"><i style="width:${pct}%"></i></div><p class="muted small">전체의 ${pct}% 풀었어요</p>` : ''}
      ${st.fallback ? '<p class="muted small">※ 일부 숫자는 v330_home.sql 을 실행하면 보여요.</p>' : `
      <div class="grid2">
        <div class="card"><h3>🆕 최근 한 주간 생긴 문제</h3><div class="list">${plist(st.new_list, '이번 주 새 문제는 없어요.')}</div></div>
        <div class="card"><h3>🔥 아직 아무도 못 푼 문제</h3><div class="list">${plist(st.unsolved_list, '모든 문제가 누군가에게 풀렸어요!')}</div></div>
      </div>`}`;
    }
    return [`
      ${nbHtml}
      ${tuBannerHtml(tu)}
      <h2>안녕, ${esc(selfName())}! 👋</h2>
      ${appCardHtml()}
      ${probHtml}
      <div class="page-head"><h3>📢 최근 공지</h3><a href="#/board/notice">더 보기</a></div>
      <div class="card list">${notices}</div>
      <div class="grid2">
        ${tierCan('lecture') ? `<div class="card"><h3>🎬 최신 강의</h3>${lec ? `<p><span class="week">${lec.week}주차</span><a href="#/lecture/${lec.id}">${esc(lec.title)}</a></p>` : '<p class="muted">아직 없어요.</p>'}</div>` : ''}
        ${wantProb ? `<div class="card"><h3>📄 최신 문제집</h3>${prob ? `<p>${prob.week ? `<span class="week">${prob.week}주차</span>` : ''}<a href="#/set/${prob.id}">${esc(prob.title)}</a></p>` : '<p class="muted">아직 없어요.</p>'}</div>` : ''}
      </div>`, (v) => {
      v.querySelectorAll('a.hp').forEach((a) => a.addEventListener('click', () => { scrollToEx = 'ex-' + a.dataset.ex; }));
      v.querySelectorAll('[data-nbx]').forEach((x) => (x.onclick = (e) => {
        e.preventDefault();
        const id = Number(x.dataset.nbx);
        try { localStorage.setItem(NB_KEY, JSON.stringify(nbClosed().concat(id).slice(-100))); } catch (er) { /* 저장 못 해도 이번엔 닫혀요 */ }
        const el = x.closest('.nban'); if (el) el.remove();
      }));
      const tx = $('#tuX', v);
      if (tx) tx.onclick = (e) => {
        e.preventDefault();
        try { localStorage.setItem(TU_KEY, tuToken(tu)); } catch (er) { /* 저장 못 해도 이번엔 닫혀요 */ }
        $('#tuBan', v).remove();
      };
    }];
  }

  /* ---------- 강의 ---------- */
  async function pageLectures() {
    const { data, error } = await sb.from('lectures').select('*').order('week', { ascending: false }).order('id', { ascending: false });
    if (error) throw error;
    const rows = data.length ? data.map((x) => `<a class="row" href="#/lecture/${x.id}"><div class="row-main"><span class="week">${x.week}주차</span><b>${esc(x.title)}</b></div><div class="muted small meta">▶ 보기</div></a>`).join('')
      : '<p class="muted center pad">아직 올라온 강의가 없어요.</p>';
    return [`<div class="page-head"><h2>🎬 강의</h2></div><div class="card list">${rows}</div>`];
  }

  async function pageLecture(id) {
    const { data: x, error } = await sb.from('lectures').select('*').eq('id', Number(id)).maybeSingle();
    if (error) throw error;
    if (!x) return notFound();
    const vid = ytId(x.youtube_url);
    const player = vid
      ? `<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/${vid}" title="${esc(x.title)}" allow="accelerometer; encrypted-media; picture-in-picture; fullscreen" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>`
      : '<div class="card pad center">영상 주소를 읽을 수 없어요. 선생님께 알려주세요.</div>';
    return [`
      <p><a href="#/lectures">← 강의 목록</a>${can('content') ? ' <button class="link" id="editLec">✏️ 수정</button>' : ''}</p>
      <h2><span class="week">${x.week}주차</span>${esc(x.title)}</h2>
      ${player}
      ${x.description ? `<div class="card">${renderContent(x.description)}</div>` : ''}`,
    (v) => {
      const eb = $('#editLec', v);
      if (eb) eb.onclick = () => { adminTab = 'lectures'; lecEdit = x.id; location.hash = '#/admin'; };
    }];
  }

  /* ---------- 게시판 ---------- */
  const BOARDS = {
    notice: { name: '공지사항', icon: '📢', adminOnly: true, perm: 'notice', anon: false, week: false, desc: '' },
    problem: { name: '문제', icon: '📄', adminOnly: true, perm: 'content', anon: false, week: true, desc: '주차별 문제 파일이에요. 궁금한 점은 댓글로 물어보세요.' },
    qna: { name: '질문 게시판', icon: '❓', adminOnly: false, anon: true, week: false, desc: '모르는 건 편하게 물어보세요. 익명으로도 쓸 수 있어요.' },
    assignment: { name: '과제 제출', icon: '📝', adminOnly: false, anon: false, week: false, desc: '내가 낸 과제는 나와 선생님만 볼 수 있어요. 코드는 ``` 로 감싸서 붙여넣거나 파일로 첨부하세요.' },
    free: { name: '자유게시판', icon: '💬', adminOnly: false, anon: true, week: false, desc: '자유롭게 이야기해요. 익명으로도 쓸 수 있어요.' },
  };

  async function pageBoard(key) {
    const B = BOARDS[key];
    const mk = (cols) => {
      let q = sb.from('posts_view').select(cols).eq('board', key);
      if (B.week) q = q.order('week', { ascending: false, nullsFirst: false });
      return q.order('created_at', { ascending: false });
    };
    const base = 'id,title,created_at,author_name,author_id,anonymous,files,week';
    let res = key === 'notice' ? await mk(base + ',pinned') : { error: true };
    if (key === 'notice' && !res.error) PIN_OK = true;
    if (res.error) res = await mk(base);
    const { data: raw, error } = res;
    if (error) throw error;
    const data = key === 'notice' ? orderNotices(raw) : raw;
    const canWrite = !B.adminOnly || can(B.perm);
    const rows = data.length ? data.map((p) => `
      <a class="row${p.pinned ? ' pinned' : ''}" href="#/post/${p.id}">
        <div class="row-main">${p.pinned ? '<span class="pinmark">📌</span> ' : ''}${p.week ? `<span class="week">${p.week}주차</span>` : ''}<b>${esc(p.title)}</b>${(p.files || []).length ? ` <span title="첨부파일 ${(p.files || []).length}개">📎${(p.files || []).length}</span>` : ''}</div>
        <div class="muted small meta">${who(p.author_id, p.author_name, false)}${p.anonymous && can('review') ? ' (익명 작성)' : ''} · ${fmt(p.created_at)}</div>
      </a>`).join('') : '<p class="muted center pad">아직 글이 없어요.</p>';
    return [`
      <div class="page-head"><h2>${B.icon} ${B.name}</h2>${canWrite ? `<a class="btn" href="#/write/${key}">글쓰기</a>` : ''}</div>
      ${B.desc ? `<p class="muted">${esc(B.desc)}</p>` : ''}
      <div class="card list">${rows}</div>`];
  }

  /* ---------- 게시판 (공지·질문·과제·자유를 하나로) ---------- */
  const BOARD_TABS = ['notice', 'qna', 'assignment', 'free'];
  const BOARD_SHORT = { notice: '공지', qna: '질문', assignment: '과제', free: '자유' };
  async function pageBoardAll(f) {
    const cur = BOARD_TABS.includes(f) ? f : '';
    const base = 'id,board,title,created_at,author_name,author_id,anonymous,files,week';
    const mk = (cols) => sb.from('posts_view').select(cols).in('board', cur ? [cur] : BOARD_TABS).order('created_at', { ascending: false }).limit(400);
    let res = await mk(base + ',pinned,banner');
    if (!res.error) { PIN_OK = true; BAN_OK = true; } else { res = await mk(base + ',pinned'); if (!res.error) PIN_OK = true; else res = await mk(base); }
    if (res.error) throw res.error;
    const raw = res.data || [];
    const pin = raw.filter((x) => x.pinned && x.board === 'notice').sort(koSort);
    const data = pin.concat(raw.filter((x) => !(x.pinned && x.board === 'notice')));
    const wTo = cur && (cur !== 'notice' || can('notice')) ? cur : 'free';
    const tabs = `<div class="bd-tabs"><a class="${cur ? '' : 'on'}" href="#/board">전체</a>${BOARD_TABS.map((k) => `<a class="${cur === k ? 'on' : ''}" href="#/board/${k}">${BOARDS[k].icon} ${BOARD_SHORT[k]}</a>`).join('')}</div>`;
    const rows = data.length ? data.map((p) => `
      <a class="row${p.pinned && p.board === 'notice' ? ' pinned' : ''}" href="#/post/${p.id}" data-t="${esc((p.title || '').toLowerCase())}">
        <div class="row-main"><span class="bd-tag t-${p.board}">${BOARD_SHORT[p.board] || ''}</span>${p.pinned && p.board === 'notice' ? '<span class="pinmark">📌</span> ' : ''}${p.banner ? '<span title="홈 배너">📣</span> ' : ''}<b>${esc(p.title)}</b>${(p.files || []).length ? ' <span title="첨부파일">📎</span>' : ''}</div>
        <div class="muted small meta">${who(p.author_id, p.author_name, false)}${p.anonymous && can('review') ? ' (익명 작성)' : ''} · ${fmt(p.created_at)}</div>
      </a>`).join('') : '<p class="muted center pad">아직 글이 없어요.</p>';
    return [`
      <div class="page-head"><h2>💬 게시판</h2><a class="btn" href="#/write/${wTo}">글쓰기</a></div>
      ${tabs}
      ${cur && BOARDS[cur].desc ? `<p class="muted small">${esc(BOARDS[cur].desc)}</p>` : ''}
      <input type="search" id="bdQ" class="bd-q" placeholder="제목 검색" autocomplete="off">
      <div class="card list" id="bdList">${rows}</div>`,
    (v) => {
      const q = $('#bdQ', v);
      if (q) q.oninput = () => {
        const t = q.value.trim().toLowerCase();
        v.querySelectorAll('#bdList a.row').forEach((a) => { a.style.display = !t || (a.dataset.t || '').includes(t) ? '' : 'none'; });
      };
    }];
  }

  async function pagePost(rawId) {
    const id = Number(rawId);
    const { data: p, error } = await sb.from('posts_view').select('*').eq('id', id).maybeSingle();
    if (error) throw error;
    if (!p) return notFound();
    const B = BOARDS[p.board];
    const files = p.files || [];
    const { data: cs } = await sb.from('comments_view').select('*').eq('post_id', id).order('created_at');

    const comments = (cs || []).map((c) => `
      <div class="comment">
        <div class="c-head">${who(c.author_id, c.author_name)}${c.by_admin ? ' <span class="badge">선생님</span>' : ''}
          <span class="muted small"> · ${fmt(c.created_at)}</span>
          ${c.is_mine || can('moderate') ? ` <button class="link danger" data-delc="${c.id}">삭제</button>` : ''}</div>
        <div class="txt">${esc(c.content)}</div>
      </div>`).join('');

    const commentBox = p.allow_comments ? `
      <form id="cForm" style="margin-top:12px">
        <textarea id="cText" style="min-height:80px" placeholder="댓글을 입력하세요" required></textarea>
        <div class="form-actions">
          <button class="primary">댓글 달기</button>
          ${B.anon ? '<label class="inline" style="margin:0"><input type="checkbox" id="cAnon"> 익명으로</label>' : ''}
        </div>
      </form>` : '<p class="muted small">이 글은 댓글을 달 수 없어요.</p>';

    return [`
      <p><a href="#/board/${p.board}">← 게시판 · ${B.name}</a></p>
      <div class="card">
        <h2 class="post-title${p.pinned ? ' pinned' : ''}">${p.pinned ? '<span class="pinmark">📌</span> ' : ''}${p.week ? `<span class="week">${p.week}주차</span>` : ''}${esc(p.title)}</h2>
        <p class="muted small">${who(p.author_id, p.author_name)}${p.anonymous && can('review') ? ' (익명 작성)' : ''} · ${fmt(p.created_at)}${p.updated_at ? ' (수정됨)' : ''}
          ${p.is_mine ? ` <a href="#/edit/${p.id}">수정</a>` : ''}
          ${p.board === 'notice' && p.is_mine && can('notice') && 'pinned' in p ? ` <button class="link" id="pinPost">${p.pinned ? '📌 고정 해제' : '📌 상단 고정'}</button>` : ''}
          ${p.board === 'notice' && can('notice') && 'banner' in p ? ` <button class="link" id="banPost">${p.banner ? '📣 배너 내리기' : '📣 홈 배너로 띄우기'}</button>` : ''}
          ${p.is_mine || can('moderate') ? ' <button class="link danger" id="delPost">글 삭제</button>' : ''}</p>
        ${renderContent(p.content, p.board === 'notice')}
        ${files.length ? `<div class="attach">${files.map((f, i) => `<div class="file-row">📎 <button class="link" data-file="${i}">${esc(f.name || '첨부파일')}</button></div>`).join('')}</div>` : ''}
      </div>
      <div class="card"><h3>댓글 ${cs ? cs.length : 0}</h3>${comments}${commentBox}</div>`,
    (v) => {
      v.querySelectorAll('[data-file]').forEach((b) => (b.onclick = () => {
        const f = files[Number(b.dataset.file)];
        if (f) download(f.bucket || 'attachments', f.path, f.name || 'file');
      }));

      const pp = $('#pinPost', v);
      if (pp) pp.onclick = async () => {
        pp.disabled = true;
        const { data: ok, error: pe } = await sb.from('posts').update({ pinned: !p.pinned }).eq('id', id).select('id');
        if (pe || !ok || !ok.length) { pp.disabled = false; return toast('고정을 바꾸지 못했어요', true); }
        toast(p.pinned ? '고정을 풀었어요' : '맨 위에 빨갛게 고정했어요');
        route(true);
      };

      const bp = $('#banPost', v);
      if (bp) bp.onclick = async () => {
        bp.disabled = true;
        const { data: ok, error: be } = await sb.from('posts').update({ banner: !p.banner }).eq('id', id).select('id');
        if (be || !ok || !ok.length) { bp.disabled = false; return toast('배너를 바꾸지 못했어요 (내가 쓴 공지만 바꿀 수 있어요)', true); }
        try { localStorage.setItem(NB_KEY, JSON.stringify(nbClosed().filter((x) => x !== id))); } catch (er) { /* 무시 */ }
        toast(p.banner ? '배너를 내렸어요' : '홈 배너로 띄웠어요');
        route(true);
      };

      const dp = $('#delPost', v);
      if (dp) dp.onclick = async () => {
        if (!confirm('이 글을 삭제할까요?')) return;
        const { error: e } = await sb.from('posts').delete().eq('id', id);
        if (e) return toast('삭제하지 못했어요', true);
        await removeFiles(files);
        location.hash = '#/board/' + p.board;
      };

      v.querySelectorAll('[data-delc]').forEach((b) => (b.onclick = async () => {
        if (!confirm('댓글을 삭제할까요?')) return;
        const { error: e } = await sb.from('comments').delete().eq('id', Number(b.dataset.delc));
        if (e) return toast('삭제하지 못했어요', true);
        route(true);
      }));

      const cf = $('#cForm', v);
      if (cf) cf.onsubmit = async (e) => {
        e.preventDefault();
        const text = $('#cText', v).value.trim();
        if (!text) return;
        const btn = $('button.primary', cf);
        btn.disabled = true;
        const { error: er } = await sb.from('comments').insert({
          post_id: id, author_id: me.id, content: text, anonymous: !!($('#cAnon', v) && $('#cAnon', v).checked),
        });
        if (er) { btn.disabled = false; return toast('댓글을 달지 못했어요', true); }
        route(true);
      };
    }];
  }

  // 글 쓰기 / 글 수정 (post가 있으면 수정)
  async function pageWrite(key, post = null) {
    const B = BOARDS[key];
    const editing = !!post;
    if (B.adminOnly && !can(B.perm)) return ['<div class="card pad center">선생님만 쓸 수 있는 게시판이에요.</div>'];
    const old = editing ? (post.files || []) : [];
    if (key === 'notice' && !PIN_OK) { const pr = await sb.from('posts_view').select('pinned').limit(1); if (!pr.error) PIN_OK = true; }
    if (key === 'notice' && !BAN_OK) { const br = await sb.from('posts_view').select('banner').limit(1); if (!br.error) BAN_OK = true; }
    const pinBox = key === 'notice' && PIN_OK && can('notice');
    const banBox = key === 'notice' && BAN_OK && can('notice');
    const catTabs = editing ? '' : `<div class="bd-tabs">${BOARD_TABS.filter((k) => !BOARDS[k].adminOnly || can(BOARDS[k].perm)).map((k) => `<a class="${k === key ? 'on' : ''}" href="#/write/${k}">${BOARDS[k].icon} ${BOARD_SHORT[k]}</a>`).join('')}</div>`;
    return [`
      <p><a href="#/${editing ? 'post/' + post.id : 'board/' + key}">← ${editing ? '글로 돌아가기' : '게시판'}</a></p>
      <div class="card">
        <h2>${B.icon} ${editing ? B.name + ' 글 수정' : '글쓰기'}</h2>
        ${catTabs}
        <form id="wForm">
          ${B.week ? `<label>주차<input type="number" id="wWeek" min="1" value="${post && post.week ? post.week : ''}" required></label>` : ''}
          <label>제목<input type="text" id="wTitle" maxlength="120" value="${esc(post ? post.title : '')}" required></label>
          <label>내용${B.week ? ' (설명)' : ''}
            ${key === 'assignment' ? '<button type="button" class="link" id="codeBtn">+ 코드 블록 넣기</button>' : ''}
            <textarea id="wBody" class="${key === 'assignment' ? 'code' : ''}" placeholder="${key === 'assignment' ? '코드는 ```python 으로 시작해서 ``` 로 끝내면 코드 모양으로 보여요.' : ''}">${esc(post ? post.content : '')}</textarea>
          </label>
          ${old.length ? `<label>올려둔 파일 <span class="muted small">(체크하면 삭제돼요)</span></label>
            ${old.map((f, i) => `<label class="inline file-row"><input type="checkbox" data-rm="${i}"> 📎 ${esc(f.name || '파일')}</label>`).join('')}` : ''}
          <label>파일 첨부 (선택, 여러 개 가능, 파일당 50MB 이하)<input type="file" id="wFile" multiple></label>
          <div class="form-actions" style="flex-direction:column;align-items:flex-start">
            <label class="inline"><input type="checkbox" id="wComments" ${!editing || post.allow_comments ? 'checked' : ''}> 댓글 허용</label>
            ${pinBox ? `<label class="inline"><input type="checkbox" id="wPin" ${editing && post.pinned ? 'checked' : ''}> 📌 상단에 빨갛게 고정</label>` : ''}
            ${banBox ? `<label class="inline"><input type="checkbox" id="wBan" ${editing && post.banner ? 'checked' : ''}> 📣 홈 화면 배너로 띄우기 <span class="muted small">(학생이 ✕ 로 닫을 수 있어요)</span></label>` : ''}
            ${B.anon ? `<label class="inline"><input type="checkbox" id="wAnon" ${editing && post.anonymous ? 'checked' : ''}> 익명으로 올리기</label>` : ''}
            <button class="primary" id="wBtn" style="margin-top:6px">${editing ? '수정 저장' : '올리기'}</button>
          </div>
        </form>
      </div>`,
    (v) => {
      const cb = $('#codeBtn', v);
      if (cb) cb.onclick = () => {
        const t = $('#wBody', v);
        const s = t.selectionStart;
        const ins = '```python\n\n```\n';
        t.value = t.value.slice(0, s) + ins + t.value.slice(t.selectionEnd);
        t.focus();
        t.selectionStart = t.selectionEnd = s + 10;
      };
      $('#wForm', v).onsubmit = async (e) => {
        e.preventDefault();
        const title = $('#wTitle', v).value.trim();
        const content = $('#wBody', v).value;
        const picked = Array.from($('#wFile', v).files);
        const week = B.week ? Number($('#wWeek', v).value) : null;
        const removed = new Set(Array.from(v.querySelectorAll('[data-rm]:checked')).map((c) => Number(c.dataset.rm)));
        const kept = old.filter((_, i) => !removed.has(i));
        const gone = old.filter((_, i) => removed.has(i));
        if (!title) return toast('제목을 입력하세요', true);
        if (B.week && !(week >= 1)) return toast('주차를 입력하세요', true);
        if (!content.trim() && !kept.length && !picked.length) return toast('내용이나 파일 중 하나는 있어야 해요', true);
        if (picked.some((f) => f.size > MAX_FILE)) return toast('파일은 하나당 50MB 이하만 올릴 수 있어요', true);

        const btn = $('#wBtn', v);
        btn.disabled = true;
        const uploaded = [];
        for (const file of picked) {
          const ext = (file.name.match(/\.[A-Za-z0-9]{1,8}$/) || [''])[0];
          const path = `${key}/${me.id}/${Date.now()}_${rand()}${ext}`;
          const { error: ue } = await sb.storage.from('attachments').upload(path, file);
          if (ue) {
            await removeFiles(uploaded);
            btn.disabled = false;
            return toast(`"${file.name}" 파일을 올리지 못했어요`, true);
          }
          uploaded.push({ path, name: file.name });
        }

        const row = {
          title, content,
          anonymous: !!($('#wAnon', v) && $('#wAnon', v).checked),
          allow_comments: $('#wComments', v).checked,
          files: kept.concat(uploaded),
        };
        if (B.week) row.week = week;
        if ($('#wPin', v)) row.pinned = $('#wPin', v).checked;
        if ($('#wBan', v)) row.banner = $('#wBan', v).checked;

        let newId = null;
        if (editing) {
          row.updated_at = new Date().toISOString();
          const { data, error: ue2 } = await sb.from('posts').update(row).eq('id', post.id).select('id');
          if (ue2 || !data || !data.length) {
            await removeFiles(uploaded);
            btn.disabled = false;
            return toast('수정하지 못했어요', true);
          }
          newId = post.id;
          await removeFiles(gone);
        } else {
          row.board = key;
          row.author_id = me.id;
          const { data, error: ie } = await sb.from('posts').insert(row).select('id').single();
          if (ie || !data) {
            await removeFiles(uploaded);
            btn.disabled = false;
            return toast('글을 올리지 못했어요', true);
          }
          newId = data.id;
        }
        location.hash = '#/post/' + newId;
      };
    }];
  }

  async function pageEdit(rawId) {
    const { data: p, error } = await sb.from('posts_view').select('*').eq('id', Number(rawId)).maybeSingle();
    if (error) throw error;
    if (!p || !p.is_mine || !BOARDS[p.board]) return notFound();
    return pageWrite(p.board, p);
  }

  /* ---------- 문제집 : 서식 그리기 ---------- */
  const DIFFS = ['Beginner', 'Intermediate', 'Advanced', 'ELITE'];
  const normDiff = (d) => {
    const k = String(d ?? '').trim().toLowerCase();
    const own = DIFF_LIST.find((x) => x.name.toLowerCase() === k);
    if (own) return own.name;
    if (/^(elite|엘리트)/.test(k)) return 'ELITE';
    if (/^(adv|고급|상)/.test(k)) return 'Advanced';
    if (/^(int|중)/.test(k)) return 'Intermediate';
    return 'Beginner';
  };

  let openPanels = new Set(); // 열려 있는 '풀어보기' 칸 (문제 고유 번호)
  const sentSig = new Map(); // 문제별로 마지막에 낸 답 (자동 제출 때 같은 답을 또 내지 않게)
  let reviewOpen = new Set(); // 제출함에서 펼쳐 둔 문제
  const reviewVer = new Map(); // 제출함에서 보고 있는 버전
  let reviewSet = '';
  let scrollToEx = null;
  /* 설명 글(set_notes) · 편집 기능 켜고 끄기(관리자 ▸ ✏️ 편집, 이 브라우저에 저장) */
  let curNotes = [];
  let NOTES_OK = null;
  const ADM_KEY = 'pn_adm';
  const admOpt = (k) => { try { return (JSON.parse(localStorage.getItem(ADM_KEY) || '{}') || {})[k] !== false; } catch (e) { return true; } };
  const admSet = (k, v) => {
    let o = {};
    try { o = JSON.parse(localStorage.getItem(ADM_KEY) || '{}') || {}; } catch (e) { o = {}; }
    o[k] = v;
    try { localStorage.setItem(ADM_KEY, JSON.stringify(o)); } catch (e) { /* 저장 못 해도 이번엔 적용돼요 */ }
  };
  let hwFilter = null; // 숙제만 보기 (숙제 id)
  let testsColumn = null; // exercises.tests 열이 있는지 (update4.sql)
  let answersColumn = null; // exercises.answers 열이 있는지 (update5.sql)
  const gradeMemo = new Map(); // 문제별 마지막 채점 결과(화면 다시 그려도 유지)

  // 1000개씩 끊어서 전부 가져오기
  async function fetchAll(make) {
    const out = [];
    for (let from = 0; ; from += 1000) {
      const { data, error } = await make(from, from + 999);
      if (error) throw error;
      out.push(...data);
      if (data.length < 1000) break;
    }
    return out;
  }

  const inline = (s) => esc(s)
    .replace(/`([^`\n]+)`/g, '<code class="ic">$1</code>')
    .replace(/\*\*([^*\n]+)\*\*/g, '<b>$1</b>');

  function parseBlocks(text) {
    const lines = String(text ?? '').replace(/\r/g, '').split('\n');
    const out = [];
    let buf = [];
    let fence = null;
    const flush = () => { if (buf.length) { out.push({ t: 'p', text: buf.join('\n') }); buf = []; } };
    for (const ln of lines) {
      if (fence) {
        if (ln.trim() === '```') { out.push({ t: fence.kind, title: fence.title, text: fence.lines.join('\n') }); fence = null; } else fence.lines.push(ln);
        continue;
      }
      const m = ln.match(/^```[ \t]*([A-Za-z]*)[ \t]*(.*)$/);
      if (m) { flush(); fence = { kind: (m[1] || 'code').toLowerCase(), title: m[2].trim(), lines: [] }; continue; }
      buf.push(ln);
    }
    if (fence) out.push({ t: fence.kind, title: fence.title, text: fence.lines.join('\n') });
    flush();
    return out;
  }

  // 문제 서식 → HTML (형식 설명은 문제형식.md)
  function renderMarkup(text) {
    return parseBlocks(text).map((b) => {
      const t = b.text;
      if (b.t === 'p') return t.trim() ? `<div class="mk-p">${inline(t.replace(/^\n+|\n+$/g, ''))}</div>` : '';
      if (b.t === 'program') {
        const lines = t.split('\n').map((l) => `<span class="pl">${esc(l).replace(/[㉠-㉿]/g, '<span class="blank">$&</span>') || ' '}</span>`).join('');
        return `<div class="mk-prog">${b.title ? `<div class="cap">${esc(b.title)}</div>` : ''}<pre><code>${lines}</code></pre></div>`;
      }
      if (b.t === 'io' || b.t === 'out') {
        const html = t.split('\n').map((l) => (/^>>>/.test(l) ? `<span class="in">${esc(l)}</span>` : esc(l))).join('\n');
        return `<div class="mk-io"><div class="cap">${esc(b.title || (b.t === 'io' ? '입력 · 출력 예' : '출력 결과'))}</div><pre><code>${html}</code></pre></div>`;
      }
      if (b.t === 'box') {
        return `<div class="mk-box">${b.title ? `<div class="cap">${esc(b.title)}</div>` : ''}<div class="mk-p">${inline(t)}</div></div>`;
      }
      if (b.t === 'table') {
        const rows = t.split('\n').filter((r) => r.trim() !== '')
          .map((r) => r.split('|').map((c) => c.replace(/^ /, '').replace(/ $/, '').replace(/\\n/g, '\n')));
        const head = rows.shift() || [];
        return `<div class="mk-tablewrap">${b.title ? `<div class="cap">${esc(b.title)}</div>` : ''}<table class="mk-table"><thead><tr>${head.map((c) => `<th>${esc(c)}</th>`).join('')}</tr></thead><tbody>${rows.map((r) => `<tr>${r.map((c) => `<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
      }
      return `<pre class="mk-code"><code>${esc(t)}</code></pre>`;
    }).join('');
  }

  /* ---------- 문제집 : 번호/목차 계산 ---------- */
  // 화면에 보이는 번호는 순서대로 자동 계산, 고유 번호(id)는 그대로예요.
  function layoutEx(list) {
    const normal = list.filter((e) => e.difficulty !== 'ELITE');
    const elite = list.filter((e) => e.difficulty === 'ELITE');
    normal.forEach((e, i) => { e.no = i + 1; });
    elite.forEach((e, i) => { e.no = i + 1; });
    const chapters = [];
    normal.forEach((e) => {
      const cname = e.chapter || '';
      let ch = chapters[chapters.length - 1];
      if (!ch || ch.name !== cname) { ch = { name: cname, sections: [], idx: chapters.length }; chapters.push(ch); }
      const sname = e.section || '';
      let sc = ch.sections[ch.sections.length - 1];
      if (!sc || sc.name !== sname) { sc = { name: sname, items: [], idx: ch.sections.length }; ch.sections.push(sc); }
      sc.items.push(e);
    });
    return { normal, elite, chapters };
  }
  /* 문제 사이사이에 설명 글을 끼워 넣은 순서 (화면·내보내기 공용) */
  function mergeFlow(L, notes) {
    const nn = (notes || []).filter((n) => n.area !== 'elite');
    let p = 0;
    L.chapters.forEach((ch) => ch.sections.forEach((sc) => {
      sc.flow = [];
      sc.items.forEach((e) => {
        while (p < nn.length && nn[p].position < e.position) sc.flow.push({ note: nn[p++] });
        sc.flow.push({ ex: e });
      });
    }));
    L.tail = nn.slice(p);
    const en = (notes || []).filter((n) => n.area === 'elite');
    let q = 0;
    L.eliteFlow = [];
    L.elite.forEach((e) => {
      while (q < en.length && en[q].position < e.position) L.eliteFlow.push({ note: en[q++] });
      L.eliteFlow.push({ ex: e });
    });
    en.slice(q).forEach((n) => L.eliteFlow.push({ note: n }));
    return L;
  }
  // 한 구역(normal / elite)의 문제+글을 순서대로
  function zoneItems(exs, notes, zone) {
    const a = exs.filter((e) => (e.difficulty === 'ELITE') === (zone === 'elite')).map((e) => ({ kind: 'ex', id: e.id, pos: e.position, o: e }));
    const b = (notes || []).filter((n) => (n.area === 'elite') === (zone === 'elite')).map((n) => ({ kind: 'note', id: n.id, pos: n.position, o: n }));
    return a.concat(b).sort((x, y) => x.pos - y.pos || (x.kind === y.kind ? x.id - y.id : x.kind === 'ex' ? -1 : 1));
  }
  const noteHtml = (text) => renderContent(text, true);
  const dispNo = (e) => (e.difficulty === 'ELITE' ? `E${e.no}` : String(e.no));
  const splitChapter = (s) => { const i = s.indexOf(' · '); return i < 0 ? [s, ''] : [s.slice(0, i), s.slice(i + 3)]; };
  const shortOf = (s) => s.short_name || ((String(s.title).match(/\[(.+?)\]/) || [])[1]) || s.title;
  const firstLine = (body) => {
    const l = String(body || '').split('\n').find((x) => x.trim() && !x.startsWith('```')) || '';
    return l.replace(/[`*]/g, '').slice(0, 70);
  };

  function modal(html) {
    const bg = document.createElement('div');
    bg.className = 'modal-bg';
    bg.innerHTML = `<div class="card modal"><button class="icon modal-x" type="button" title="닫기">✕</button>${html}</div>`;
    document.body.appendChild(bg);
    const close = () => bg.remove();
    $('.modal-x', bg).onclick = close;
    return { el: bg, close };
  }

  /* ---------- 문제집 : JSON 읽기/내보내기 ---------- */
  function parseSetJson(text) {
    let d;
    try { d = JSON.parse(text); } catch (e) { throw new Error('JSON 파일을 읽을 수 없어요 (형식 오류)'); }
    if (!d || typeof d !== 'object') throw new Error('올바른 문제집 파일이 아니에요');
    if (d.format && d.format !== 'pynest-problemset-v1') throw new Error('지원하지 않는 형식이에요: ' + d.format);
    const rows = [];
    const notes = [];
    let seq = 0;
    const isText = (p) => p && typeof p === 'object' && ['text', 'note', 'md', 'markdown'].includes(String(p.type || '').toLowerCase());
    const addNote = (p, elite) => {
      const body = String(typeof p === 'string' ? p : (p.body ?? p.text ?? p.content ?? '')).trim();
      if (!body) return; // 빈 글은 건너뛰어요
      seq += 1;
      notes.push({ body, area: elite ? 'elite' : 'normal', position: seq * 1000 });
    };
    const add = (p, chapter, section, forceElite) => {
      if (isText(p)) return addNote(p, forceElite);
      const body = String(p.body ?? '').trim();
      if (!body) throw new Error(`${rows.length + 1}번째 문제의 body(문제 내용)가 비어 있어요`);
      seq += 1;
      const pts = p.points === '' || p.points == null ? null : Number(p.points);
      rows.push({
        chapter: chapter || null, section: section || null,
        difficulty: forceElite ? 'ELITE' : normDiff(p.difficulty),
        label: p.label || null, points: Number.isFinite(pts) ? pts : null,
        tags: Array.isArray(p.tags) ? p.tags.map(String) : [],
        source: p.source || null, body, check_point: p.check || p.check_point || null,
        tests: normTests(p.tests), answers: normAnswers(p.answers), position: seq * 1000,
      });
    };
    (d.chapters || []).forEach((ch) => {
      const cname = [ch.title, ch.subtitle].filter(Boolean).join(' · ');
      if (ch.intro) addNote(ch.intro, false); // 챕터 앞 설명 글
      (ch.sections || []).forEach((s) => {
        if (s.intro) addNote(s.intro, false); // 섹션 앞 설명 글
        (s.problems || []).forEach((p) => add(p, cname, s.title, false));
      });
    });
    (d.problems || []).forEach((p) => add(p, p.chapter, p.section, false));
    if (d.elite_intro) addNote(d.elite_intro, true);
    (d.elite || []).forEach((p) => add(p, null, null, true));
    if (!rows.length && !notes.length) throw new Error('문제도 설명 글도 하나도 없어요');
    return {
      title: d.title || '', short: d.short_name || '', week: d.week || '', desc: d.description || '', rows, notes,
      nElite: rows.filter((r) => r.difficulty === 'ELITE').length,
    };
  }

  function exportSet(set, list, notes) {
    const L = mergeFlow(layoutEx(list.map((e) => ({ ...e }))), notes);
    const prob = (e) => ({ difficulty: e.difficulty, label: e.label || '', points: e.points, tags: e.tags || [], source: e.source || '', body: e.body, check: e.check_point || '', tests: e.tests || [], answers: e.answers || [] });
    const text = (n) => ({ type: 'text', body: n.body });
    const flowOut = (f) => f.map((x) => (x.note ? text(x.note) : prob(x.ex)));
    const chapters = L.chapters.map((ch) => {
      const [title, subtitle] = splitChapter(ch.name);
      return { title, subtitle, sections: ch.sections.map((sc) => ({ title: sc.name, problems: flowOut(sc.flow) })) };
    });
    // 마지막 문제 뒤의 글은 마지막 섹션 끝에 (문제가 하나도 없으면 problems 에)
    const extra = {};
    if (L.tail.length) {
      const lc = chapters[chapters.length - 1];
      if (lc) lc.sections[lc.sections.length - 1].problems.push(...L.tail.map(text));
      else extra.problems = L.tail.map(text);
    }
    const out = {
      format: 'pynest-problemset-v1', title: set.title, short_name: set.short_name || '', week: set.week, description: set.description || '',
      chapters, ...extra,
      elite: flowOut(L.eliteFlow),
    };
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([JSON.stringify(out, null, 1)], { type: 'application/json' }));
    a.download = `${shortOf(set)}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  }

  /* ---------- 문제집 목록 ---------- */
  // 문제 보기 방식: 'sets' 문제집별 / 'num' 번호(절대번호)순
  let setsView = 'sets';
  try { if (localStorage.getItem('pn_sets_view') === 'num') setsView = 'num'; } catch (e) { /* 무시 */ }
  let numQ = '';
  let numDiff = '';
  let numLimit = 100;

  const resumeChips = (sid) => {
    const nDr = [...DR.map.values()].filter((d) => d.s === sid).length;
    return `${LP.map.has(sid) ? ' · <span class="chip">📍 이어서 풀기</span>' : ''}${nDr ? ` · <span class="chip">💾 임시 저장 ${nDr}</span>` : ''}`;
  };
  async function pageSets() {
    const num = setsView === 'num';
    const [sr, ex, mine] = await Promise.all([
      sb.from('problem_sets').select('*').order('week', { ascending: true, nullsFirst: false }).order('id'),
      fetchAll((a, b) => sb.from('exercises').select(num ? 'id,set_id,difficulty,body' : 'id,set_id').order('id').range(a, b)),
      can('content') ? Promise.resolve([]) : fetchAll((a, b) => sb.from('submissions').select('id,exercise_id,set_id').eq('user_id', me.id).order('id').range(a, b)),
      can('content') ? Promise.resolve() : Promise.all([loadDrafts(), loadLast()]).catch(() => {}),
    ]);
    if (sr.error) throw sr.error;
    const total = {};
    ex.forEach((e) => { total[e.set_id] = (total[e.set_id] || 0) + 1; });
    const solved = {};
    const seen = new Set();
    mine.forEach((s) => { if (!seen.has(s.exercise_id)) { seen.add(s.exercise_id); solved[s.set_id] = (solved[s.set_id] || 0) + 1; } });

    const cards = sr.data.length ? sr.data.map((s) => {
      const t = total[s.id] || 0;
      const d = solved[s.id] || 0;
      return `<a class="card set-card" href="#/set/${s.id}">
        <div class="set-top">${s.week ? `<span class="week">${s.week}주차</span>` : ''}<h3>${esc(s.title)}</h3>${can('content') ? pubChip(s.is_public) : ''}</div>
        ${s.description ? `<p class="muted small">${esc(s.description)}</p>` : ''}
        <div class="muted small">문제 ${t}개${can('content') ? '' : ` · 내가 푼 문제 ${d}개`}${can('content') ? '' : resumeChips(s.id)}</div>
        ${can('content') ? '' : `<div class="bar"><i style="width:${t ? Math.round((d / t) * 100) : 0}%"></i></div>`}
      </a>`;
    }).join('') : '<div class="card pad center muted">아직 올라온 문제집이 없어요.</div>';

    // 번호로 보기: 모든 문제를 고유 번호(#id) 순서로
    const setBy = new Map(sr.data.map((x) => [x.id, x]));
    const doneEx = new Set(mine.map((x) => x.exercise_id));
    const numRows = (rows) => rows.slice(0, numLimit).map((e) => {
      const st = setBy.get(e.set_id);
      return `<a class="row numrow" href="#/set/${e.set_id}" data-ex="${e.id}" data-set="${e.set_id}">
        <div class="row-main"><span class="ex-no sm">#${e.id}</span> ${diffTag(e.difficulty)} <span class="numtitle">${esc(firstLine(e.body).replace(/^\*\*|\*\*$/g, '') || '(제목 없음)')}</span></div>
        <div class="muted small">${doneEx.has(e.id) ? '<span class="done">✓ 풀었어요</span> · ' : ''}${st ? esc(shortOf(st)) : ''}</div></a>`;
    }).join('');
    const numMatch = (e) => (!numDiff || e.difficulty === numDiff)
      && (!numQ || String(e.id) === numQ.replace(/^#/, '') || firstLine(e.body).toLowerCase().includes(numQ.toLowerCase()));
    const numBody = () => {
      const rows = ex.filter(numMatch);
      return `${numRows(rows) || '<p class="muted center pad">조건에 맞는 문제가 없어요.</p>'}${rows.length > numLimit ? `<div class="center pad"><button class="ghost" id="numMore">더 보기 (${rows.length - numLimit}개 남음)</button></div>` : ''}`;
    };
    const diffOpts = ['', ...new Set(ex.map((e) => e.difficulty))];
    const view = num
      ? `<div class="card numtools"><input type="search" id="numQ" placeholder="번호(예: 123) 또는 제목 검색" value="${esc(numQ)}">
          <select id="numD">${diffOpts.map((d) => `<option value="${esc(d)}" ${d === numDiff ? 'selected' : ''}>${d ? esc(d) : '모든 난이도'}</option>`).join('')}</select></div>
         <div class="card list" id="numList">${numBody()}</div>`
      : `<div class="sets">${cards}</div>`;
    return [`
      <div class="page-head"><h2>📄 문제</h2>${can('content') ? '<span><button class="ghost" id="newSetLive" title="라이브에서 냈던 문제를 골라 새 문제집으로 만들어요">📡 라이브 문제로 만들기</button> <button class="primary" id="newSet">＋ 새 문제집</button></span>' : ''}</div>
      <div class="tabs"><button data-sv="sets" class="${num ? '' : 'on'}">📚 문제집으로 보기</button><button data-sv="num" class="${num ? 'on' : ''}">🔢 번호로 보기</button></div>
      <p class="muted">${num ? `모든 문제를 <b>고유 번호</b> 순서로 보여줘요 (총 ${ex.length}문제). 눌러서 문제집 안의 그 문제로 이동해요.` : '문제를 하나씩 보고, <b class="redtxt">풀어보기</b>로 코드를 제출해요. 제출한 풀이는 선생님만 볼 수 있어요.'}</p>
      ${view}
      <p class="muted small"><a href="#/board/problem">📁 예전에 올린 문제 파일 보기</a></p>`,
    (v) => {
      const nb = $('#newSet', v);
      if (nb) nb.onclick = openNewSet;
      const nl = $('#newSetLive', v);
      if (nl) nl.onclick = () => openLiveImport(null, []);
      v.querySelectorAll('[data-sv]').forEach((b) => (b.onclick = () => {
        setsView = b.dataset.sv;
        try { localStorage.setItem('pn_sets_view', setsView); } catch (e) { /* 무시 */ }
        numLimit = 100;
        route();
      }));
      if (!num) return;
      const redraw = () => {
        $('#numList', v).innerHTML = numBody();
        bindNum();
      };
      const bindNum = () => {
        v.querySelectorAll('.numrow').forEach((a) => (a.onclick = () => { scrollToEx = 'ex-' + a.dataset.ex; }));
        const mb = $('#numMore', v);
        if (mb) mb.onclick = () => { numLimit += 200; redraw(); };
      };
      $('#numQ', v).oninput = (e) => { numQ = e.target.value.trim(); numLimit = 100; redraw(); };
      $('#numD', v).onchange = (e) => { numDiff = e.target.value; numLimit = 100; redraw(); };
      bindNum();
    }];
  }

  // 비공개/공개 칸(v350_publish.sql)이 있는지 한 번만 확인해요
  let PUB_READY = null;
  async function pubReady() {
    if (PUB_READY !== null) return PUB_READY;
    try { const r = await sb.from('problem_sets').select('is_public').limit(1); PUB_READY = !r.error; } catch (e) { PUB_READY = false; }
    return PUB_READY;
  }
  const pubChip = (on) => (on === false ? '<span class="chip privchip" title="학생에게 안 보여요">🔒 비공개</span>' : '');

  async function openNewSet() {
    let parsed = null;
    const pr = await pubReady();
    const m = modal(`
      <h3>새 문제집 만들기</h3>
      <form id="nsForm">
        <label>문제집 파일 (.json, 선택) <span class="muted small">— 클로드가 만들어준 파일을 올리면 문제가 한꺼번에 들어가요</span>
          <input type="file" id="nsFile" accept=".json,application/json"></label>
        <p class="muted small" id="nsInfo"></p>
        <div class="grid2">
          <label>제목<input type="text" id="nsTitle" required placeholder="예: Python [A]"></label>
          <label>주차<input type="number" id="nsWeek" min="1"></label>
        </div>
        <div class="grid2">
          <label>짧은 이름 <span class="muted small">(제출함에 "student1 - A" 처럼 표시)</span><input type="text" id="nsShort" placeholder="A"></label>
          <span></span>
        </div>
        <label>설명 (선택)<textarea id="nsDesc" style="min-height:70px"></textarea></label>
        ${pr ? `<div class="pubpick"><div class="muted small">공개 설정</div>
          <label class="inline"><input type="radio" name="nsPub" value="0" checked> 🔒 <b>비공개</b>로 올리기 <span class="muted small">— 학생에게 안 보여요. 확인하고 고친 뒤 나중에 공개해요</span></label>
          <label class="inline"><input type="radio" name="nsPub" value="1"> 🌐 <b>바로 게시</b> <span class="muted small">— 지금 바로 학생에게 보여요</span></label></div>` : ''}
        <div class="form-actions"><button class="primary" id="nsBtn">만들기</button><button type="button" class="ghost" id="nsCancel">취소</button></div>
      </form>`);
    const q = (s) => $(s, m.el);
    q('#nsCancel').onclick = m.close;
    q('#nsFile').onchange = async (e) => {
      parsed = null;
      const f = e.target.files[0];
      if (!f) { q('#nsInfo').textContent = ''; return; }
      try {
        parsed = parseSetJson(await f.text());
        q('#nsInfo').textContent = `✅ 일반 ${parsed.rows.length - parsed.nElite}문제 + ELITE ${parsed.nElite}문제${parsed.notes.length ? ` + 설명 글 ${parsed.notes.length}개` : ''}를 읽었어요.`;
        if (parsed.title) q('#nsTitle').value = parsed.title;
        if (parsed.week) q('#nsWeek').value = parsed.week;
        q('#nsShort').value = parsed.short || ((parsed.title.match(/\[(.+?)\]/) || [])[1] || '');
        q('#nsDesc').value = parsed.desc;
      } catch (err) {
        q('#nsInfo').textContent = '⚠️ ' + err.message;
        e.target.value = '';
      }
    };
    q('#nsForm').onsubmit = async (e) => {
      e.preventDefault();
      const btn = q('#nsBtn');
      btn.disabled = true;
      const setRow = {
        title: q('#nsTitle').value.trim(), short_name: q('#nsShort').value.trim() || null,
        week: Number(q('#nsWeek').value) || null, description: q('#nsDesc').value.trim() || null,
      };
      if (pr) setRow.is_public = (m.el.querySelector('input[name="nsPub"]:checked') || { value: '1' }).value === '1';
      const { data: s, error } = await sb.from('problem_sets').insert(setRow).select('id').single();
      if (error || !s) { btn.disabled = false; return toast('만들지 못했어요', true); }
      if (parsed) {
        const rows = parsed.rows.map((r) => ({ ...r, set_id: s.id }));
        for (let i = 0; i < rows.length; i += 100) {
          let { error: ie } = await sb.from('exercises').insert(rows.slice(i, i + 100));
          if (ie && /tests|answers/.test(ie.message || '')) {
            const chunk = rows.slice(i, i + 100);
            const strip = (omit) => chunk.map((r) => { const c = { ...r }; omit.forEach((k) => delete c[k]); return c; });
            ({ error: ie } = await sb.from('exercises').insert(strip(['answers'])));
            if (ie && /tests/.test(ie.message || '')) ({ error: ie } = await sb.from('exercises').insert(strip(['answers', 'tests'])));
            if (!ie && i === 0) toast('자동 채점 정보는 update4.sql, update5.sql을 실행한 뒤에 저장돼요', true);
          }
          if (ie) {
            await sb.from('problem_sets').delete().eq('id', s.id);
            btn.disabled = false;
            return toast('문제를 넣지 못했어요: ' + ie.message, true);
          }
        }
      }
      if (parsed && parsed.notes.length) {
        const ne = await insertNoteRows(parsed.notes.map((n) => ({ ...n, set_id: s.id })));
        if (ne) toast('설명 글은 v3911_notes.sql 을 실행한 뒤에 저장돼요', true);
      }
      m.close();
      toast(pr && setRow.is_public === false ? '비공개로 만들었어요. 확인한 뒤 [🌐 공개하기]를 눌러주세요' : '문제집을 만들었어요');
      location.hash = '#/set/' + s.id;
    };
  }


  /* ---------- 문제 단독 화면 (백준처럼 문제만 크게) ---------- */
  async function pageProblem(rawId, sub) {
    const eid = Number(rawId);
    if (!eid) return notFound();
    const admin = can('content');
    const er = await sb.from('exercises').select('*').eq('id', eid).maybeSingle();
    if (er.error) throw er.error;
    const e = er.data;
    if (!e) return notFound();
    testsColumn = 'tests' in e;
    answersColumn = 'answers' in e;
    const [sr, all, subs] = await Promise.all([
      sb.from('problem_sets').select('*').eq('id', e.set_id).maybeSingle(),
      fetchAll((a, b) => sb.from('exercises').select('id,position,chapter,section,difficulty,is_public,label,body').eq('set_id', e.set_id).order('position').order('id').range(a, b)),
      admin ? Promise.resolve([]) : fetchAll((a, b) => sb.from('submissions')
        .select('*,submission_comments(id,content,created_at)').eq('exercise_id', eid).eq('user_id', me.id).order('id').range(a, b)),
    ]);
    const set = sr.data;
    if (!set) return notFound();
    if (!admin) { await loadDrafts(e.set_id).catch(() => {}); setLast(e.set_id, eid); } // V4.4.1 임시 저장 · 마지막 위치
    const L = layoutEx(all.map((x) => ({ ...x })));
    const order = L.normal.concat(L.elite);
    const idx = order.findIndex((x) => x.id === eid);
    const cur = order[idx];
    e.no = cur ? cur.no : 1;
    const prev = order[idx - 1];
    const next = order[idx + 1];
    const tests = e.tests || [];
    const answers = e.answers || [];
    const tags = (e.tags || []).map((t) => `<span class="chip">${esc(t)}</span>`).join('');
    const samples = tests.filter((t) => !t.hidden);
    const hasIo = /^```\s*(io|out)\b/m.test(String(e.body || ''));
    const cp = (t) => String(t == null ? '' : t).replace(/\n$/, '');
    const sampleHtml = samples.length && !hasIo ? `<h2 class="pro-h">예제</h2>${samples.slice(0, 5).map((t, i) => `
      <div class="pro-ex"><div><div class="pro-cap">예제 입력 ${i + 1} <button class="link" data-cp="in${i}">복사</button></div><pre><code>${esc(cp(t.input))}</code></pre></div>
      <div><div class="pro-cap">예제 출력 ${i + 1} <button class="link" data-cp="out${i}">복사</button></div><pre><code>${esc(cp(t.output))}</code></pre></div></div>`).join('')}` : '';
    const pick = `<select class="pro-pick" data-pick title="번호로 문제 고르기">${order.map((x) => `<option value="${x.id}"${x.id === eid ? ' selected' : ''}>${dispNo(x)}번 · ${esc((x.label || firstLine(x.body) || '').slice(0, 40))}</option>`).join('')}</select>`;
    const nav = `<div class="pro-nav">
      ${prev ? `<a class="ghost btnlike" href="#/p/${prev.id}">← 이전 (${dispNo(prev)})</a>` : '<span></span>'}
      <span class="pro-mid"><a class="ghost btnlike" href="#/set/${set.id}" data-back>📋 목록</a> ${pick}</span>
      ${next ? `<a class="ghost btnlike" href="#/p/${next.id}">다음 (${dispNo(next)}) →</a>` : '<span></span>'}</div>`;
    return [`
      <div class="pro-top"><a href="#/set/${set.id}" data-back>← ${esc(set.title)}</a>${pick}</div>
      <article class="pro">
        <h1 class="pro-title"><span class="pro-no">${dispNo(e)}번</span> ${e.label ? esc(e.label) : esc(shortOf(set))}</h1>
        <div class="pro-meta">
          ${diffTag(e.difficulty)}
          ${admin ? pubChip(e.is_public) : ''}
          ${e.points ? `<span class="chip pts">${e.points}점</span>` : ''}
          ${tests.length || answers.some((x) => x.type !== 'm') ? '<span class="chip judgechip" title="제출하면 자동으로 채점돼요">⚖️ 자동 채점</span>' : answers.length ? '<span class="chip judgechip">✍️ 서술</span>' : ''}
          ${tags}${e.source ? `<span class="muted small">${esc(e.source)}</span>` : ''}
        </div>
        <h2 class="pro-h">문제</h2>
        <div class="ex-body pro-body">${renderMarkup(e.body)}</div>
        ${sampleHtml}
        ${e.check_point ? `<div class="ex-check">💡 <b>확인 포인트</b> ${inline(e.check_point)}</div>` : ''}
        ${admin ? `<p class="muted small">고유 번호 ${e.id}${tests.length ? ` · 테스트 ${tests.length}개` : ''}${answers.length ? ` · 정답 칸 ${answers.length}개` : ''} · 수정·삭제는 <a href="#/set/${set.id}" data-back>문제집 화면</a>에서 해요.</p>`
          : `<h2 class="pro-h">풀어보기</h2><div class="ex-panel pro-panel" id="panel-${e.id}"></div>`}
        ${nav}
      </article>`,
    (v) => {
      v.querySelectorAll('[data-back]').forEach((a) => a.addEventListener('click', () => { scrollToEx = 'ex-' + eid; }));
      v.querySelectorAll('[data-pick]').forEach((sel) => (sel.onchange = () => { location.hash = '#/p/' + sel.value; }));
      v.querySelectorAll('[data-cp]').forEach((b) => (b.onclick = async () => {
        const m = /^(in|out)(\d+)$/.exec(b.dataset.cp);
        const t = samples[Number(m[2])];
        try { await navigator.clipboard.writeText(cp(m[1] === 'in' ? t.input : t.output)); toast('복사했어요'); } catch (er) { toast('복사하지 못했어요', true); }
      }));
      if (!admin) {
        const mount = makeSolver({ [eid]: e }, { [eid]: subs }, !!set.answer_public);
        const pn = mount(eid);
        if (pn) pn.hidden = false;
        // 내 기록에서 들어왔으면(#/p/번호/s제출번호) 그 풀이를 펼쳐서 보여줘요
        const sm = /^s(\d+)?$/.exec(sub || '');
        if (sm && subs.length) {
          const one = sm[1] ? subs.find((x) => x.id === Number(sm[1])) : null;
          const target = one || subs[subs.length - 1];
          const d = [...v.querySelectorAll('details.ver')].find((x) => { const b2 = $('summary b', x); return b2 && b2.textContent === 'v' + target.version; });
          if (d) { d.open = true; setTimeout(() => d.scrollIntoView({ behavior: 'smooth', block: 'center' }), 120); d.classList.add('flash'); }
        }
      }
    }];
  }

  /* ---------- 문제 넣기 도우미: JSON 으로 추가 · 라이브 문제 가져오기 ---------- */
  // exercises 에 한꺼번에 넣어요 (칸이 아직 없는 DB 면 그 칸만 빼고 다시 시도)
  async function insertExRows(rows) {
    for (let i = 0; i < rows.length; i += 100) {
      const chunk = rows.slice(i, i + 100);
      const omit = [];
      let r = await sb.from('exercises').insert(chunk);
      while (r.error && omit.length < 4) {
        const msg = r.error.message || '';
        const k = ['is_public', 'answers', 'tests', 'rank_points'].find((x) => !omit.includes(x) && msg.includes(x));
        if (!k) break;
        omit.push(k);
        r = await sb.from('exercises').insert(chunk.map((row) => { const c = { ...row }; omit.forEach((o) => delete c[o]); return c; }));
      }
      if (r.error) return r.error;
    }
    return null;
  }
  const pubPickHtml = (name) => `<div class="pubpick"><div class="muted small">공개 설정</div>
    <label class="inline"><input type="radio" name="${name}" value="0" checked> 🔒 <b>비공개</b>로 넣기 <span class="muted small">— 학생에게 안 보여요. 확인하고 나중에 공개해요</span></label>
    <label class="inline"><input type="radio" name="${name}" value="1"> 🌐 <b>바로 게시</b> <span class="muted small">— 지금 바로 학생에게 보여요</span></label></div>`;

  async function openAddJson(set, exs) {
    const pr = await pubReady();
    let parsed = null;
    const m = modal(`
      <h3>＋ JSON으로 문제 추가</h3>
      <p class="muted small">"${esc(set.title)}" 문제집 <b>맨 뒤</b>에 문제를 붙여요. 지금 있는 문제와 학생 제출물은 그대로예요. 형식은 문제집 JSON(pynest-problemset-v1)과 같아요 — <code class="ic">problems</code> 나 <code class="ic">chapters</code>, <code class="ic">elite</code> 에 문제를 담으면 돼요.</p>
      <label>JSON 붙여넣기<textarea id="ajText" class="code" style="min-height:220px" spellcheck="false" placeholder='{ "format": "pynest-problemset-v1", "problems": [ { "difficulty": "Beginner", "body": "...", "tests": [ { "input": "1 2", "output": "3" } ] } ] }'></textarea></label>
      <label>또는 파일 선택 <input type="file" id="ajFile" accept=".json,application/json"></label>
      <p class="muted small" id="ajInfo"></p>
      ${pr ? pubPickHtml('ajPub') : ''}
      <div class="form-actions"><button class="primary" id="ajBtn" disabled>추가하기</button><button type="button" class="ghost" id="ajCancel">취소</button></div>`);
    const q = (x) => $(x, m.el);
    const check = () => {
      parsed = null;
      const t = q('#ajText').value.trim();
      q('#ajBtn').disabled = true;
      if (!t) { q('#ajInfo').textContent = ''; return; }
      try {
        parsed = parseSetJson(t);
        q('#ajInfo').textContent = `✅ 일반 ${parsed.rows.length - parsed.nElite}문제 + ELITE ${parsed.nElite}문제${parsed.notes.length ? ` + 설명 글 ${parsed.notes.length}개` : ''}를 읽었어요.`;
        q('#ajBtn').disabled = false;
      } catch (err) { q('#ajInfo').textContent = '⚠️ ' + err.message; }
    };
    q('#ajText').oninput = check;
    q('#ajFile').onchange = async (e) => {
      const f = e.target.files[0];
      if (!f) return;
      q('#ajText').value = await f.text();
      check();
    };
    q('#ajCancel').onclick = m.close;
    q('#ajBtn').onclick = async () => {
      if (!parsed) return;
      const btn = q('#ajBtn');
      btn.disabled = true;
      const maxPos = Math.max(exs.reduce((mx, e) => Math.max(mx, e.position), 0), curNotes.reduce((mx, n) => Math.max(mx, n.position), 0));
      const lastNormal = exs.filter((e) => e.difficulty !== 'ELITE').pop();
      const isPub = pr ? (m.el.querySelector('input[name="ajPub"]:checked') || { value: '1' }).value === '1' : true;
      const rows = parsed.rows.map((r) => {
        const o = { ...r, set_id: set.id, position: maxPos + r.position };
        if (!o.chapter && !o.section && o.difficulty !== 'ELITE' && lastNormal) { o.chapter = lastNormal.chapter; o.section = lastNormal.section; }
        if (pr) o.is_public = isPub;
        return o;
      });
      const err = rows.length ? await insertExRows(rows) : null;
      if (err) { btn.disabled = false; return toast('문제를 넣지 못했어요: ' + err.message, true); }
      let noteMsg = '';
      if (parsed.notes.length) {
        const ne = await insertNoteRows(parsed.notes.map((n) => ({ ...n, set_id: set.id, position: maxPos + n.position, is_public: pr ? isPub : true })));
        noteMsg = ne ? ' (설명 글은 v3911_notes.sql 을 실행한 뒤에 넣을 수 있어요)' : ` + 설명 글 ${parsed.notes.length}개`;
      }
      m.close();
      toast(`${rows.length}문제를 추가했어요${noteMsg}${pr && !isPub ? ' (비공개 — 확인 후 공개해 주세요)' : ''}`);
      route(true);
    };
  }

  // 라이브에서 냈던 문제를 골라 문제집으로. target 이 있으면 그 문제집 뒤에 추가, 없으면 새 문제집을 만들어요.
  async function openLiveImport(target, exs) {
    const pr = await pubReady();
    const m = modal('<h3>📡 라이브 문제 가져오기</h3><p class="loading">불러오는 중…</p>');
    let sess;
    let lps;
    try {
      [sess, lps] = await Promise.all([
        fetchAll((a, b) => sb.from('live_sessions').select('id,title,created_at').order('created_at').range(a, b)),
        fetchAll((a, b) => sb.from('live_problems').select('*').order('session_id').order('position').order('id').range(a, b)),
      ]);
    } catch (err) { m.close(); return toast('라이브 문제를 불러오지 못했어요', true); }
    if (!lps.length) { m.close(); return toast('가져올 라이브 문제가 아직 없어요', true); }
    const have = new Set((exs || []).map((e) => normFlat(e.body)));
    const groups = sess.map((x) => ({ s: x, items: lps.filter((p) => p.session_id === x.id) })).filter((g) => g.items.length);
    const stTxt = { open: '진행중', closed: '마감', draft: '비공개' };
    const body = groups.map((g, gi) => `<div class="li-group">
      <label class="inline li-head"><input type="checkbox" data-g="${gi}"> <b>${esc(g.s.title || '라이브')}</b> <span class="muted small">${fmt(g.s.created_at)} · ${g.items.length}문제</span></label>
      ${g.items.map((p) => `<label class="inline li-row"><input type="checkbox" data-p="${p.id}" ${p.status === 'draft' || have.has(normFlat(p.body)) ? '' : 'checked'}>
        <span class="muted small">${esc(stTxt[p.status] || p.status || '')}</span> ${p.difficulty ? diffTag(p.difficulty) : ''} <span class="li-t">${esc(p.title || firstLine(p.body))}</span>${have.has(normFlat(p.body)) ? ' <span class="chip">이미 있음</span>' : ''}</label>`).join('')}
    </div>`).join('');
    m.el.querySelector('.modal').innerHTML = `<button class="icon modal-x" type="button" title="닫기">✕</button>
      <h3>📡 라이브 문제 가져오기</h3>
      <p class="muted small">${target ? `"${esc(target.title)}" 문제집 <b>맨 뒤</b>에 넣어요.` : '골라서 <b>새 문제집</b>을 만들어요.'} 수업(라이브) 이름이 장(CHAPTER) 이름이 되고, 문제 내용·정답·채점 테스트·난이도가 그대로 복사돼요. 라이브 쪽 문제는 그대로 남아요.</p>
      <div class="li-list">${body}</div>
      <p class="muted small" id="liCnt"></p>
      ${target ? '' : `<div class="grid2"><label>제목<input type="text" id="liTitle" required placeholder="예: 10월 라이브 문제 모음"></label><label>주차<input type="number" id="liWeek" min="1"></label></div>
        <label>짧은 이름 <input type="text" id="liShort" placeholder="L1"></label>`}
      ${pr ? pubPickHtml('liPub') : ''}
      <div class="form-actions"><button class="primary" id="liBtn">${target ? '문제 추가하기' : '문제집 만들기'}</button><button type="button" class="ghost" id="liCancel">취소</button></div>`;
    $('.modal-x', m.el).onclick = m.close;
    const q = (x) => $(x, m.el);
    const pick = () => [...m.el.querySelectorAll('input[data-p]:checked')].map((c) => Number(c.dataset.p));
    const count = () => { q('#liCnt').textContent = `${pick().length}문제 선택`; };
    m.el.querySelectorAll('input[data-g]').forEach((c) => (c.onchange = () => {
      m.el.querySelectorAll('.li-group')[Number(c.dataset.g)].querySelectorAll('input[data-p]').forEach((x) => { x.checked = c.checked; });
      count();
    }));
    m.el.querySelectorAll('input[data-p]').forEach((c) => (c.onchange = count));
    count();
    q('#liCancel').onclick = m.close;
    q('#liBtn').onclick = async () => {
      const ids = new Set(pick());
      if (!ids.size) return toast('가져올 문제를 골라 주세요', true);
      const isPub = pr ? (m.el.querySelector('input[name="liPub"]:checked') || { value: '1' }).value === '1' : true;
      let title = '';
      if (!target) { title = q('#liTitle').value.trim(); if (!title) return toast('문제집 제목을 입력하세요', true); }
      const btn = q('#liBtn');
      btn.disabled = true;
      let setId = target ? target.id : null;
      if (!target) {
        const setRow = { title, short_name: q('#liShort').value.trim() || null, week: Number(q('#liWeek').value) || null, description: null };
        if (pr) setRow.is_public = isPub;
        const { data: ns, error } = await sb.from('problem_sets').insert(setRow).select('id').single();
        if (error || !ns) { btn.disabled = false; return toast('문제집을 만들지 못했어요', true); }
        setId = ns.id;
      }
      const base = (exs || []).reduce((mx, e) => Math.max(mx, e.position), 0);
      let n = 0;
      const rows = [];
      groups.forEach((g) => g.items.forEach((p) => {
        if (!ids.has(p.id)) return;
        n += 1;
        const r = {
          set_id: setId, position: base + n * 1000, chapter: g.s.title || '라이브', section: null,
          difficulty: normDiff(p.difficulty), label: p.title ? String(p.title).slice(0, 40) : null, points: null, tags: [],
          source: '라이브: ' + (g.s.title || ''), body: p.body, check_point: null, tests: normTests(p.tests), answers: normAnswers(p.answers),
        };
        if (p.rank_points != null) r.rank_points = p.rank_points;
        if (pr) r.is_public = isPub;
        rows.push(r);
      }));
      const err = await insertExRows(rows);
      if (err) {
        if (!target) await sb.from('problem_sets').delete().eq('id', setId);
        btn.disabled = false;
        return toast('문제를 넣지 못했어요: ' + err.message, true);
      }
      m.close();
      toast(`${rows.length}문제를 ${target ? '추가' : '넣어 문제집을 만들'}었어요${pr && !isPub ? ' (비공개 — 확인 후 공개해 주세요)' : ''}`);
      if (target) route(true); else location.hash = '#/set/' + setId;
    };
  }

  /* ---------- 문제집 화면 ---------- */
  async function pageSet(rawId) {
    const id = Number(rawId);
    const admin = can('content');
    const [sr, exs, subs, hwr, nr] = await Promise.all([
      sb.from('problem_sets').select('*').eq('id', id).maybeSingle(),
      fetchAll((a, b) => sb.from('exercises').select('*').eq('set_id', id).order('position').order('id').range(a, b)),
      admin ? Promise.resolve([]) : fetchAll((a, b) => sb.from('submissions')
        .select('*,submission_comments(id,content,created_at)')
        .eq('set_id', id).eq('user_id', me.id).order('id').range(a, b)),
      sb.from('homeworks').select('*,homework_items(exercise_id)').eq('set_id', id).order('id'),
      sb.from('set_notes').select('*').eq('set_id', id).order('position').order('id'),
      admin ? Promise.resolve() : Promise.all([loadDrafts(id), loadLast()]).catch(() => {}), // 임시 저장 · 마지막 위치 (V4.4.1)
    ]);
    if (sr.error) throw sr.error;
    const set = sr.data;
    if (!set) return notFound();
    NOTES_OK = !nr.error; // v3911_notes.sql 전이면 설명 글만 조용히 없어요
    const notes = NOTES_OK ? nr.data : [];
    curNotes = notes;
    if (exs.length) { testsColumn = 'tests' in exs[0]; answersColumn = 'answers' in exs[0]; }
    if (set && 'is_public' in set) PUB_READY = true;
    const L = mergeFlow(layoutEx(exs), notes);
    const subsBy = {};
    subs.forEach((s) => { (subsBy[s.exercise_id] = subsBy[s.exercise_id] || []).push(s); });

    /* 숙제 (update3.sql 전이면 그냥 없는 걸로) */
    const hws = (hwr.error ? [] : hwr.data).map((h) => ({ ...h, ids: new Set((h.homework_items || []).map((i) => i.exercise_id)) }));
    if (hwFilter != null && !hws.some((h) => h.id === hwFilter)) hwFilter = null;
    const hwOf = {};
    hws.forEach((h) => h.ids.forEach((i) => { (hwOf[i] = hwOf[i] || []).push(h); }));
    const allEx = L.normal.concat(L.elite);
    const hwHtml = (hws.length || admin) ? `<div class="hw-wrap">${hws.map((h) => {
      const items = allEx.filter((e) => h.ids.has(e.id));
      const done = items.filter((e) => subsBy[e.id]).length;
      return `<div class="card hw">
        <div class="hw-top"><b>📌 ${esc(h.title)}</b>${h.due_date ? ` <span class="chip">마감 ${esc(h.due_date)}</span>` : ''}</div>
        <div class="muted small">문제 ${esc(rangeText(items)) || '(없음)'} · ${items.length}개</div>
        ${admin ? '' : `<div class="bar"><i style="width:${items.length ? Math.round((done / items.length) * 100) : 0}%"></i></div><div class="small">제출 ${done} / ${items.length}</div>`}
        <div class="form-actions" style="margin-top:8px">
          <button class="ghost" data-hwfilter="${h.id}">이 숙제만 보기</button>
          ${admin ? `${can('review') ? `<button class="ghost" data-hwstat="${h.id}">📊 제출 현황</button>` : ''}<button class="ghost" data-hwedit="${h.id}">✏️ 수정</button><button class="ghost" data-hwdel="${h.id}">🗑</button>` : ''}
        </div></div>`;
    }).join('')}${admin ? '<button class="ghost" id="addHw">＋ 숙제 만들기</button>' : ''}</div>` : '';

    /* 목차 */
    const toc = L.chapters.map((ch) => {
      const [t, sub] = splitChapter(ch.name);
      const secs = ch.sections.filter((sc) => sc.name).map((sc) => {
        const a = sc.items[0].no;
        const b = sc.items[sc.items.length - 1].no;
        return `<button class="toc-link sec" data-go="sec-${ch.idx}-${sc.idx}">${esc(sc.name)} <span class="muted small">${a === b ? a : `${a}–${b}`}</span></button>`;
      }).join('');
      return `<div class="toc-ch"><button class="toc-link ch" data-go="ch-${ch.idx}">${esc(t || '문제')}${sub ? ` <span class="muted small">${esc(sub)}</span>` : ''}</button>${secs}</div>`;
    }).join('') + (L.elite.length ? `<div class="toc-ch"><button class="toc-link elite" data-go="elite">✦ ELITE <span class="small">${L.elite.length}문제</span></button></div>` : '');

    /* 설명 글 카드 */
    const gripBtn = admin && admOpt('drag') ? '<button class="icon drag-grip" type="button" title="끌어서 순서 바꾸기">⠿</button>' : '';
    const dblTip = admin && admOpt('dbl') ? ' title="더블클릭하면 바로 고칠 수 있어요"' : '';
    const noteCard = (n) => `<article class="ex note${n.is_public === false ? ' note-priv' : ''}" id="note-${n.id}" data-kind="note" data-id="${n.id}" data-zone="${n.area === 'elite' ? 'elite' : 'normal'}">
      ${admin ? `<header class="ex-head"><span class="chip">📝 설명 글</span>${pubChip(n.is_public)}<span class="spacer"></span>
        <span class="tools">${gripBtn}<button class="icon" data-nedit="${n.id}" title="수정">✏️</button><button class="icon" data-nadd="note:${n.id}" title="이 글 아래에 설명 글 추가">📝</button><button class="icon" data-addnote="${n.id}" title="이 글 아래에 문제 추가">＋</button><button class="icon" data-ndel="${n.id}" title="삭제">🗑</button></span></header>` : ''}
      <div class="ex-body note-body"${dblTip}>${noteHtml(n.body)}</div></article>`;
    const flowHtml = (f, card0) => f.map((x) => (x.note ? noteCard(x.note) : card0(x.ex))).join('');

    /* 문제 카드 */
    const card = (e) => {
      const vers = subsBy[e.id] || [];
      const last = vers[vers.length - 1];
      const hasC = vers.some((s) => (s.submission_comments || []).length);
      const tags = (e.tags || []).map((t) => `<span class="chip">${esc(t)}</span>`).join('');
      return `<article class="ex ${e.difficulty === 'ELITE' ? 'elite' : dxCls(e.difficulty)}"${dxStyle(e.difficulty)} id="ex-${e.id}" data-kind="ex" data-id="${e.id}" data-zone="${e.difficulty === 'ELITE' ? 'elite' : 'normal'}" data-hws="${(hwOf[e.id] || []).map((h) => h.id).join(',')}">
        <header class="ex-head">
          <a class="ex-no" href="#/p/${e.id}" title="이 문제만 크게 보기">${dispNo(e)}</a>
          ${diffTag(e.difficulty)}
          ${admin ? pubChip(e.is_public) : ''}
          ${e.label ? `<span class="chip">${esc(e.label)}</span>` : ''}
          ${e.points ? `<span class="chip pts">${e.points}점</span>` : ''}
          ${(e.tests || []).length || (e.answers || []).some((x) => x.type !== 'm') ? '<span class="chip judgechip" title="제출하면 자동으로 채점돼요">⚖️ 자동 채점</span>' : (e.answers || []).length ? '<span class="chip judgechip" title="선생님이 확인해요">✍️ 서술</span>' : ''}
          ${tags}
          ${(hwOf[e.id] || []).map((h) => `<span class="chip hwchip">📌 ${esc(h.title)}</span>`).join('')}
          ${e.source ? `<span class="muted small">${esc(e.source)}</span>` : ''}
          <span class="spacer"></span>
          ${admin ? `<span class="tools">${gripBtn}
            <button class="icon" data-up="${e.id}" title="위로">↑</button><button class="icon" data-down="${e.id}" title="아래로">↓</button>
            <button class="icon" data-edit="${e.id}" title="수정">✏️</button><button class="icon" data-add="${e.id}" title="이 문제 아래에 추가">＋</button>${NOTES_OK ? `<button class="icon" data-nadd="ex:${e.id}" title="이 문제 아래에 설명 글 추가">📝</button>` : ''}
            <button class="icon" data-del="${e.id}" title="삭제">🗑</button></span>` : ''}
        </header>
        <div class="ex-body"${dblTip}>${renderMarkup(e.body)}</div>
        ${e.check_point ? `<div class="ex-check">💡 <b>확인 포인트</b> ${inline(e.check_point)}</div>` : ''}
        ${admin ? `<div class="muted small">고유 번호 ${e.id}${(e.tests || []).length ? ` · 테스트 ${e.tests.length}개` : ''}${(e.answers || []).length ? ` · 정답 칸 ${e.answers.length}개` : ''}</div>
        ${(e.answers || []).length ? `<details class="keybox"><summary>🔑 정답 보기</summary><pre><code>${esc(answersToText(e.answers))}</code></pre></details>` : ''}` : `
        <div class="ex-foot">
          <button class="solve" data-solve="${e.id}">✍️ 풀어보기</button>
          <a class="ghost btnlike" href="#/p/${e.id}" title="이 문제만 따로 크게 보기">↗ 문제만 보기</a>
          ${last ? `<span class="done">✅ 제출함 · v${last.version}</span> ${judgeBadge(last.judge)}${hasC ? ' <span class="badge">💬 선생님 댓글</span>' : ''}` : ''}
        </div>
        <div class="ex-panel" id="panel-${e.id}" hidden></div>`}
      </article>`;
    };

    const normalHtml = L.chapters.map((ch) => {
      const [t, sub] = splitChapter(ch.name);
      return `<h2 class="ch-h" id="ch-${ch.idx}"><span class="ch-no">CHAPTER ${ch.idx + 1}</span>${esc(t)}${sub ? `<small>${esc(sub)}</small>` : ''}</h2>`
        + ch.sections.map((sc) => `${sc.name ? `<h3 class="sec-h" id="sec-${ch.idx}-${sc.idx}">${esc(sc.name)}</h3>` : ''}${flowHtml(sc.flow, card)}`).join('');
    }).join('') + L.tail.map(noteCard).join('');

    const eliteHtml = (L.elite.length || L.eliteFlow.length || admin) ? `
      <section class="elite-zone" id="elite">
        <div class="elite-title">✦ ELITE ✦</div>
        <p class="elite-sub">가장 어려운 문제들이에요. 코드를 읽고, 추론하고, 설명해 보세요.</p>
        ${flowHtml(L.eliteFlow, card)}
        ${admin ? '<div class="center"><button class="ghost" id="addElite">＋ ELITE 문제 추가</button></div>' : ''}
      </section>` : '';

    const files = [];
    if (set.original_file) files.push(`<button class="ghost" data-dl="original_file">📄 원본 PDF</button>`);
    if (set.answer_file && (set.answer_public || admin)) files.push(`<button class="ghost" data-dl="answer_file">🔑 정답 PDF${set.answer_public ? '' : ' (비공개)'}</button>`);

    return [`
      <p><a href="#/sets">← 문제 목록</a></p>
      <div class="page-head">
        <h2>${set.week ? `<span class="week">${set.week}주차</span>` : ''}${esc(set.title)} ${admin ? pubChip(set.is_public) : ''}</h2>
      </div>
      ${admin && set.is_public === false ? '<div class="privbar">🔒 이 문제집은 <b>비공개</b>예요. 학생에게는 목록에도, 주소로도 안 보여요. 다 고쳤으면 <b>🌐 공개하기</b>를 눌러주세요.</div>' : ''}
      ${set.description ? `<p class="muted">${esc(set.description)}</p>` : ''}
      <div class="form-actions" style="margin:0 0 12px">
        ${files.join('')}
        ${admin && 'is_public' in set ? (set.is_public === false ? '<button class="primary" id="togPub">🌐 공개하기</button>' : '<button class="ghost" id="togPub">🔒 비공개로 바꾸기</button>') : ''}${exs.some((e) => e.is_public === false) && admin ? '<button class="ghost" id="pubAllEx" title="이 문제집의 비공개 문제를 모두 공개해요">🌐 비공개 문제 모두 공개</button>' : ''}
        ${admin ? '<button class="ghost" id="addEx">＋ 문제 추가</button><button class="ghost" id="addNote" title="문제 사이에 마크다운으로 쓰는 설명 글을 넣어요">📝 설명 글 추가</button><button class="ghost" id="addJson" title="JSON을 붙여넣거나 파일로 올려 문제를 이 문제집 맨 뒤에 추가해요">＋ JSON으로 추가</button><button class="ghost" id="addLive" title="라이브에서 냈던 문제를 골라 이 문제집에 추가해요">📡 라이브 문제 가져오기</button><button class="ghost" id="setCfg">⚙️ 문제집 설정</button><button class="ghost" id="expSet">⬇️ JSON 내보내기</button><button class="ghost" id="autoTests" title="입출력 예시가 있는 문제에 채점 테스트를 한꺼번에 만들어요">⚖️ 예시로 채점 만들기</button><button class="ghost" id="impKey" title="JSON 파일의 정답·채점 테스트를 같은 문제에 덮어써요 (학생 제출물은 그대로)">🔑 정답·채점 가져오기</button><input type="file" id="impKeyFile" accept=".json,application/json" hidden><a class="ghost btnlike" href="#/review">📥 제출함</a>' : ''}
      </div>
      ${hwHtml}
      <details class="card toc" open><summary>📑 목차 <span class="muted small">(누르면 그 위치로 이동해요)</span></summary>${toc || '<p class="muted">문제가 없어요.</p>'}</details>
      <div id="exlist" class="${hwFilter != null ? 'hw-only' : ''}">${normalHtml}${eliteHtml}</div>
      <button class="to-top" id="toTop" title="맨 위(목차)로">↑</button>`,
    (v) => {
      const go = (idv) => { const el = document.getElementById(idv); if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' }); };
      v.querySelectorAll('[data-go]').forEach((b) => (b.onclick = () => go(b.dataset.go)));
      $('#toTop', v).onclick = () => window.scrollTo({ top: 0, behavior: 'smooth' });
      v.querySelectorAll('[data-dl]').forEach((b) => (b.onclick = () => {
        const f = set[b.dataset.dl];
        if (f) download(f.bucket || 'sets', f.path, f.name || 'file.pdf');
      }));
      const hadTarget = !!scrollToEx;
      if (scrollToEx) { const t = scrollToEx; scrollToEx = null; setTimeout(() => go(t), 50); }

      /* 숙제만 보기 */
      const applyHw = () => {
        const list = $('#exlist', v);
        list.classList.toggle('hw-only', hwFilter != null);
        list.querySelectorAll('.ex').forEach((c) => c.classList.toggle('hw-on', hwFilter != null && (c.dataset.hws || '').split(',').includes(String(hwFilter))));
        v.querySelectorAll('[data-hwfilter]').forEach((b) => {
          const on = Number(b.dataset.hwfilter) === hwFilter;
          b.textContent = on ? '✕ 필터 해제' : '이 숙제만 보기';
          b.classList.toggle('on', on);
        });
      };
      v.querySelectorAll('[data-hwfilter]').forEach((b) => (b.onclick = () => {
        const hid = Number(b.dataset.hwfilter);
        hwFilter = hwFilter === hid ? null : hid;
        applyHw();
        if (hwFilter != null) go('exlist');
      }));
      applyHw();

      if (admin) return bindSetAdmin(v, set, exs, hws, L);

      /* 마지막으로 풀거나 본 문제로 이동 + 위치 기록 (V4.4.1) */
      const lastRec = LP.map.get(id);
      const lastEx = lastRec ? L.normal.concat(L.elite).find((x) => x.id === lastRec.e) : null;
      if (lastEx && !hadTarget && hwFilter == null && document.getElementById('ex-' + lastEx.id)) {
        const bar = document.createElement('div');
        bar.className = 'resume-bar';
        bar.innerHTML = `📍 마지막으로 보던 <b>${esc(String(dispNo(lastEx)))}번</b> 문제로 이동했어요 <button type="button" class="link" data-rs-top>처음부터 보기</button> <button type="button" class="link" data-rs-x aria-label="닫기">✕</button>`;
        $('#exlist', v).before(bar);
        const closeBar = () => bar.remove();
        $('[data-rs-x]', bar).onclick = closeBar;
        $('[data-rs-top]', bar).onclick = () => { closeBar(); window.scrollTo({ top: 0, behavior: 'smooth' }); };
        setTimeout(() => { const el = document.getElementById('ex-' + lastEx.id); if (el) { el.scrollIntoView({ block: 'start' }); el.classList.add('flash'); setTimeout(() => el.classList.remove('flash'), 2200); } }, 120);
        setTimeout(closeBar, 12000);
      }
      v.addEventListener('focusin', (ev) => { const c = ev.target.closest && ev.target.closest('article.ex[data-kind="ex"]'); if (c) setLast(id, Number(c.dataset.id)); });
      {
        const list = $('#exlist', v);
        let tm = 0;
        const onScroll = () => {
          if (!document.body.contains(list)) { window.removeEventListener('scroll', onScroll); return; }
          clearTimeout(tm);
          tm = setTimeout(() => {
            const hit = [...list.querySelectorAll('article.ex[data-kind="ex"]')].find((c) => c.getBoundingClientRect().bottom > 140);
            if (hit && hit.getBoundingClientRect().top < window.innerHeight * 0.6) setLast(id, Number(hit.dataset.id));
          }, 1200);
        };
        window.addEventListener('scroll', onScroll, { passive: true });
      }

      /* 풀어보기 */
      const exMap = {};
      exs.forEach((x) => { exMap[x.id] = x; });
      const reveal = !!set.answer_public;
      const mount = makeSolver(exMap, subsBy, reveal);
      v.querySelectorAll('[data-solve]').forEach((b) => (b.onclick = () => {
        const eid = Number(b.dataset.solve);
        const p = mount(eid);
        if (!p) return;
        p.hidden = !p.hidden;
        if (p.hidden) openPanels.delete(eid); else { openPanels.add(eid); const f = $('textarea', p); if (f) f.focus(); }
      }));
      openPanels.forEach((eid) => { const p = mount(eid); if (p) p.hidden = false; });
    }];
  }

  /* ---------- V4.4.1 : 문제 임시 저장 · 문제집 마지막 위치 (v441_drafts.sql — 없으면 이 브라우저에만 저장해요) ---------- */
  const DR = { map: new Map(), srv: true, tm: new Map(), stm: new Map(), pend: new Map() };
  const lsObj = (k) => { try { return JSON.parse(localStorage.getItem(k) || '{}') || {}; } catch (e) { return {}; } };
  const lsPut = (k, o) => { try { localStorage.setItem(k, JSON.stringify(o)); } catch (e) { /* 저장소가 막혀도 서버 저장은 시도해요 */ } };
  const drLsKey = () => `pn_dr_${me.id}`;
  const lpLsKey = () => `pn_lp_${me.id}`;
  const drEmpty = (c, v) => !String(c || '').trim() && !(v || []).some((x) => String(x || '').trim());
  // 내 임시 저장을 읽어와요 (setId 가 있으면 그 문제집 것만 서버에서, 없으면 전부)
  async function loadDrafts(setId) {
    const loc = lsObj(drLsKey());
    Object.entries(loc).forEach(([id, d]) => {
      const cur = DR.map.get(Number(id));
      if (!cur || (d.t || 0) > (cur.t || 0)) DR.map.set(Number(id), d);
    });
    if (!DR.srv) return;
    let q = sb.from('problem_drafts').select('exercise_id,set_id,code,vals,updated_at').eq('user_id', me.id);
    if (setId) q = q.eq('set_id', setId);
    const { data, error } = await q;
    if (error) { DR.srv = false; return; }
    (data || []).forEach((r) => {
      const t = Date.parse(r.updated_at) || 0;
      const cur = DR.map.get(r.exercise_id);
      if (!cur || t >= (cur.t || 0)) DR.map.set(r.exercise_id, { c: r.code || '', v: Array.isArray(r.vals) ? r.vals : [], t, s: r.set_id });
    });
  }
  function drWriteLocal() {
    const o = {};
    DR.map.forEach((d, id) => { o[id] = d; });
    lsPut(drLsKey(), o);
  }
  function drPushServer(eid) {
    const d = DR.map.get(eid);
    if (!DR.srv || !d) return;
    DR.pend.delete(eid);
    sb.from('problem_drafts').upsert({ user_id: me.id, exercise_id: eid, set_id: d.s || null, code: d.c.slice(0, 30000), vals: d.v, updated_at: new Date(d.t).toISOString() }, { onConflict: 'user_id,exercise_id' })
      .then((r) => { if (r && r.error) DR.srv = false; }, () => { DR.srv = false; });
  }
  function saveDraft(eid, setId, code, vals, now = false) {
    if (drEmpty(code, vals)) return deleteDraft(eid);
    const d = { c: String(code), v: (vals || []).map(String), t: Date.now(), s: setId || null };
    DR.map.set(eid, d);
    DR.pend.set(eid, true);
    clearTimeout(DR.tm.get(eid)); clearTimeout(DR.stm.get(eid));
    const doLocal = () => { drWriteLocal(); };
    if (now) { doLocal(); drPushServer(eid); } else {
      doLocal(); // 이 브라우저에는 글자를 칠 때마다 바로 (새로고침돼도 남도록)
      DR.stm.set(eid, setTimeout(() => drPushServer(eid), 3000));
    }
    return d.t;
  }
  function deleteDraft(eid) {
    clearTimeout(DR.tm.get(eid)); clearTimeout(DR.stm.get(eid));
    DR.pend.delete(eid);
    if (!DR.map.has(eid)) return null;
    DR.map.delete(eid);
    drWriteLocal();
    if (DR.srv) sb.from('problem_drafts').delete().eq('user_id', me.id).eq('exercise_id', eid).then(() => {}, () => {});
    return null;
  }
  function flushDrafts() { // 화면을 옮기거나 닫을 때, 아직 못 보낸 임시 저장을 바로 저장해요
    if (!me || !DR.pend.size) return;
    DR.pend.forEach((_, eid) => { clearTimeout(DR.tm.get(eid)); clearTimeout(DR.stm.get(eid)); drPushServer(eid); });
    drWriteLocal();
  }
  window.addEventListener('pagehide', flushDrafts);
  document.addEventListener('visibilitychange', () => { if (document.hidden) flushDrafts(); });
  const hhmm = (t) => new Date(t).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });

  // 문제집마다 "마지막으로 풀거나 본 문제"
  const LP = { map: new Map(), srv: true, stm: new Map() };
  async function loadLast(all) {
    const loc = lsObj(lpLsKey());
    Object.entries(loc).forEach(([sid, d]) => { const cur = LP.map.get(Number(sid)); if (!cur || d.t > cur.t) LP.map.set(Number(sid), d); });
    if (!LP.srv) return;
    const { data, error } = await sb.from('set_last').select('set_id,exercise_id,updated_at').eq('user_id', me.id);
    if (error) { LP.srv = false; return; }
    (data || []).forEach((r) => {
      const t = Date.parse(r.updated_at) || 0;
      const cur = LP.map.get(r.set_id);
      if (!cur || t >= cur.t) LP.map.set(r.set_id, { e: r.exercise_id, t });
    });
    return all;
  }
  function setLast(setId, eid) {
    if (!setId || !eid || !me || can('content')) return;
    const cur = LP.map.get(setId);
    if (cur && cur.e === eid && Date.now() - cur.t < 20000) return;
    const d = { e: eid, t: Date.now() };
    LP.map.set(setId, d);
    const o = lsObj(lpLsKey());
    o[setId] = d;
    lsPut(lpLsKey(), o);
    if (!LP.srv) return;
    clearTimeout(LP.stm.get(setId));
    LP.stm.set(setId, setTimeout(() => {
      sb.from('set_last').upsert({ user_id: me.id, set_id: setId, exercise_id: eid, updated_at: new Date(d.t).toISOString() }, { onConflict: 'user_id,set_id' })
        .then((r) => { if (r && r.error) LP.srv = false; }, () => { LP.srv = false; });
    }, 1500));
  }

  /* 문제 풀이 칸(코드 입력 · 실행 · 채점 · 제출) — 문제집 화면과 문제 단독 화면이 같이 써요 */
  function makeSolver(exMap, subsBy, reveal) {
    return (eid) => {
        const p = document.getElementById('panel-' + eid);
        if (!p || p.dataset.ready) return p;
        const ex = exMap[eid];
        const tests = ex.tests || [];
        const answers = ex.answers || [];
        const autoParts = answers.some((a) => a.type !== 'm');
        const showCode = tests.length > 0 || !answers.length;
        const canRun = tests.length > 0 || (!answers.length && /작성하시오|작성하여라|출력하여라|만드시오|구현하시오/.test(ex.body));
        const canGrade = tests.length > 0 || autoParts;
        const vers = subsBy[eid] || [];
        const last = vers[vers.length - 1];
        const lastU = last ? unpackSubmission(last.code, answers.length) : { code: '', vals: [] };
        // 임시 저장 (제출한 풀이보다 새롭고, 제출한 것과 다를 때만 불러와요)
        let useDr = null;
        const dr0 = DR.map.get(eid);
        if (dr0) {
          const stale = last && Date.parse(last.created_at) > (dr0.t || 0);
          const same = dr0.c === lastU.code && answers.every((_, i) => String((dr0.v || [])[i] || '') === String(lastU.vals[i] || ''));
          if (stale || same) deleteDraft(eid); else useDr = dr0;
        }
        const initCode = useDr ? useDr.c : lastU.code;
        const initVal = (i) => (useDr ? String((useDr.v || [])[i] || '') : lastU.vals[i] || '');
        const hist = vers.slice().reverse().map((s, i) => {
          const cs = (s.submission_comments || []).slice().sort((x, y) => x.created_at.localeCompare(y.created_at));
          return `<details class="ver" ${i === 0 && cs.length ? 'open' : ''}>
            <summary><b>v${s.version}</b> <span class="muted small">${fmt(s.created_at)}</span> ${judgeBadge(s.judge)}${cs.length ? ` <span class="badge">💬 ${cs.length}</span>` : ''}</summary>
            <pre><code>${esc(s.code)}</code></pre>
            ${cs.map((c) => `<div class="tcomment"><span class="badge">선생님</span> <span class="muted small">${fmt(c.created_at)}</span><div class="txt">${esc(c.content)}</div></div>`).join('')}
          </details>`;
        }).join('');
        const sample = tests.find((t) => !t.hidden);
        const partsInputs = answers.map((a, i) => {
          const lines = a.type === 'm' ? 4 : Math.min(6, Math.max(1, a.value.split('\n').length));
          const hint = a.type === 'c' ? '번호를 써요 (예: 2 또는 1, 3)' : a.type === 'm' ? '서술형은 선생님이 확인해요' : a.type === 'x' ? '코드 한 줄' : '';
          return `<label class="part"><span class="plabel">${esc(a.label || i + 1)}${a.type === 'm' ? ' <span class="badge">서술</span>' : ''}</span>
            <textarea class="pans code" data-i="${i}" rows="${lines}" spellcheck="false" placeholder="${esc(hint)}">${esc(initVal(i))}</textarea></label>`;
        }).join('');
        const nAuto = tests.length + answers.filter((a) => a.type !== 'm').length;
        p.innerHTML = `
          <div class="draft-bar" ${useDr ? '' : 'hidden'}>💾 임시 저장한 내용을 불러왔어요 <span class="muted small">(${useDr ? fmt(useDr.t) : ''})</span> <button type="button" class="link" data-dr-clear>지우고 ${last ? '낸 풀이로' : '빈 칸으로'}</button></div>
          ${showCode ? `<textarea class="code" rows="10" spellcheck="false" placeholder="여기에 완성한 코드(또는 답)를 쓰세요. 서술형 답도 여기에 써요.">${esc(initCode)}</textarea>` : ''}
          ${canRun ? `<details class="stdin-box"><summary>⌨️ 입력값 <span class="muted small">(실행해보기에서 input()에 들어갈 값 · 한 줄에 하나씩)</span></summary>
            <textarea class="stdin" rows="3" spellcheck="false">${esc(sample ? sample.input : '')}</textarea></details>` : ''}
          ${answers.length ? `<div class="parts">${showCode ? '<div class="muted small">아래 칸에도 답을 써 주세요</div>' : ''}${partsInputs}</div>` : ''}
          <div class="form-actions">
            <button class="ghost" data-dr-save type="button" title="이 문제의 풀이를 임시로 저장해요. 적는 동안 자동으로도 저장돼요">💾 임시 저장</button>
            ${canRun ? '<button class="ghost" data-run>▶ 실행해보기</button>' : ''}
            ${canGrade ? `<button class="ghost" data-grade>✅ 채점하기 <span class="muted small">(${nAuto}개 항목)</span></button>` : ''}
            <button class="solve" data-send>제출하기${last ? ` (v${last.version + 1})` : ''}</button>
            <span class="muted small" data-dr-st></span>
          </div>
          <p class="muted small" style="margin:4px 0">${canGrade ? '제출하면 자동으로 채점돼요. <b>채점하기</b>에서 모두 통과하면 자동으로 제출돼요. 채점 결과는 선생님도 볼 수 있어요. ' : ''}${answers.some((a) => a.type === 'm') ? '서술형 답은 선생님이 확인해요. ' : ''}${last ? '다시 내면 새 버전으로 쌓이고, 이전 풀이도 그대로 남아요.' : '제출한 풀이는 선생님만 볼 수 있어요.'}</p>
          <div class="judge-out" hidden></div>
          ${hist ? `<div class="vers"><div class="muted small">내가 낸 풀이</div>${hist}</div>` : ''}`;
        p.dataset.ready = '1';
        const ta = $('textarea.code:not(.pans)', p);
        const partEls = [...p.querySelectorAll('textarea.pans')];
        const getCode = () => (ta ? ta.value : '');
        const getVals = () => partEls.map((t) => t.value);
        const tabKey = (el) => {
          el.onkeydown = (ev) => {
            if (ev.key === 'Tab') {
              ev.preventDefault();
              const st = el.selectionStart;
              el.value = el.value.slice(0, st) + '    ' + el.value.slice(el.selectionEnd);
              el.selectionStart = el.selectionEnd = st + 4;
            }
          };
        };
        if (ta) { if (window.PYIDE) window.PYIDE.attach(ta); else tabKey(ta); }
        {
          const stEl = $('[data-dr-st]', p);
          const bar = $('.draft-bar', p);
          const mark = (t) => { if (stEl) stEl.textContent = t ? `💾 임시 저장됨 · ${hhmm(t)}` : ''; };
          if (useDr) mark(useDr.t);
          const onEdit = () => { mark(saveDraft(eid, ex.set_id, getCode(), getVals())); setLast(ex.set_id, eid); };
          [ta, ...partEls].filter(Boolean).forEach((el) => el.addEventListener('input', onEdit));
          $('[data-dr-save]', p).onclick = () => {
            const t = saveDraft(eid, ex.set_id, getCode(), getVals(), true);
            if (!t) return toast('저장할 내용이 없어요', true);
            mark(t); toast('임시 저장했어요 💾');
          };
          const clr = $('[data-dr-clear]', p);
          if (clr) clr.onclick = () => {
            if (!confirm('임시 저장한 내용을 지우고 처음 상태로 돌릴까요?')) return;
            deleteDraft(eid);
            if (ta) ta.value = lastU.code;
            partEls.forEach((t, i) => { t.value = lastU.vals[i] || ''; });
            bar.hidden = true; mark(0);
          };
        }
        partEls.forEach(tabKey);
        const jo = $('.judge-out', p);
        const showJ = (html) => { jo.hidden = false; jo.innerHTML = html; };
        if (gradeMemo.has(eid)) showJ(gradeMemo.get(eid));
        let busy = false;
        const lock = (on) => { busy = on; p.querySelectorAll('[data-run],[data-grade],[data-send]').forEach((b) => { b.disabled = on; }); };
        const prep = '⏳ 파이썬을 준비하는 중… (처음 한 번은 몇 초 걸려요)';
        const empty = () => !getCode().trim() && !getVals().some((x) => x.trim());
        const sig = () => getCode() + '\u0000' + JSON.stringify(getVals());
        // 코드 테스트 + 답 칸 채점 → { res, parts, judge }
        const doGrade = async () => {
          const parts = answers.length ? gradeParts(answers, getVals()) : null;
          let res = null;
          if (tests.length) {
            if (!getCode().trim()) res = { status: 'WA', passed: 0, total: tests.length, cases: tests.map((t) => ({ ok: false, st: 'WA', mode: t.mode || '', hidden: !!t.hidden, input: t.input || '', expected: t.output || '', got: '', err: '' })) };
            else {
              showJ(`<span class="muted">${prep}</span>`);
              res = await gradeAll(getCode(), tests, (i, n) => showJ(`<span class="muted">⏳ 채점 중… ${i + 1} / ${n}</span>`));
            }
          }
          return { res, parts, judge: summarize(res, parts) };
        };

        const runBtn = $('[data-run]', p);
        if (runBtn) runBtn.onclick = async () => {
          if (!getCode().trim()) return toast('코드를 입력하세요', true);
          lock(true);
          showJ(`<span class="muted">${prep}</span>`);
          const r = await runOnce(getCode(), ($('.stdin', p) || { value: '' }).value.replace(/\n?$/, '\n'));
          showJ(renderRun(r));
          lock(false);
        };
        // 제출 (직접 누르거나, 자동 채점을 모두 통과하면 자동으로)
        const submitIt = async (auto) => {
          const code = answers.length ? packSubmission(getCode(), answers, getVals()) : getCode();
          if (code.length > 30000) return toast('너무 길어요 (3만 자 이하)', true);
          if (busy) return;
          lock(true);
          let judge = null;
          if (canGrade || answers.length) {
            try {
              const g = p._graded && p._graded.sig === sig() ? p._graded.g : await doGrade();
              judge = g.judge;
              gradeMemo.set(eid, renderGrade(g.res, g.parts, answers, reveal));
              showJ(gradeMemo.get(eid));
            } catch (err) { toast('채점 도구를 불러오지 못해서 채점 없이 제출해요', true); }
          }
          let { error } = await sb.from('submissions').insert({ exercise_id: eid, user_id: me.id, code, judge });
          if (error && /judge/.test(error.message || '')) ({ error } = await sb.from('submissions').insert({ exercise_id: eid, user_id: me.id, code }));
          if (error) { lock(false); return toast('제출하지 못했어요: ' + error.message, true); }
          sentSig.set(eid, sig());
          deleteDraft(eid);
          toast(auto ? '✅ 모두 통과! 자동으로 제출했어요 🎉' : !judge ? '제출했어요! 👍' : judge.status === 'MANUAL' ? '제출했어요. 선생님이 확인할 거예요 👍' : judge.status === 'AC' ? '제출했어요! 자동 채점을 모두 통과했어요 🎉' : `제출했어요. 채점 결과는 ${judge.passed}/${judge.total} 통과예요`);
          route(true);
        };
        const gradeBtn = $('[data-grade]', p);
        if (gradeBtn) gradeBtn.onclick = async () => {
          if (empty()) return toast('답을 입력하세요', true);
          lock(true);
          let g = null;
          try {
            g = await doGrade();
            p._graded = { sig: sig(), g };
            gradeMemo.set(eid, renderGrade(g.res, g.parts, answers, reveal));
            showJ(gradeMemo.get(eid));
          } catch (err) {
            g = null;
            showJ(renderRun({ status: 'LOAD', err: String(err.message || err) }));
          }
          lock(false);
          // 자동 채점을 전부 통과(서술형 칸 없음)하면 따로 누르지 않아도 제출해요. 같은 답을 다시 내지는 않아요.
          if (g && g.judge.status === 'AC' && !g.judge.manual && sentSig.get(eid) !== sig()) await submitIt(true);
        };
        $('[data-send]', p).onclick = () => {
          if (empty()) return toast('내용을 입력하세요', true);
          submitIt(false);
        };
        return p;
    };
  }

  /* ---------- 자동 채점 (학생 브라우저에서 파이썬 실행: Pyodide) ---------- */
  const PY_URL = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/';
  const PY_BOOT = [
    'import sys, io, json, builtins',
    'def _inp(prompt=""):',
    '    s = sys.stdin.readline()',
    '    if s == "":',
    '        raise EOFError("EOF when reading a line")',
    '    return s.rstrip("\\n")',
    'builtins.input = _inp',
    'def judge_run(code, inp, pre="[]"):',
    '    so, si, se = sys.stdout, sys.stdin, sys.stderr',
    '    out = io.StringIO()',
    '    sys.stdin = io.StringIO(inp)',
    '    sys.stdout = out',
    '    sys.stderr = io.StringIO()',
    '    err = None',
    '    try:',
    '        g = {"__name__": "__main__"}',
    '        stage = None',
    '        for b in json.loads(pre or "[]"):',
    '            stage = b.get("n") or "이름 없음"',
    '            exec(compile(b.get("c", ""), "prelude.py", "exec"), g)',
    '        stage = None',
    '        out.seek(0)',
    '        out.truncate(0)',
    '        exec(compile(code, "main.py", "exec"), g)',
    '    except SystemExit:',
    '        pass',
    '    except BaseException as e:',
    '        line = getattr(e, "lineno", None) if isinstance(e, SyntaxError) else None',
    '        tb = e.__traceback__',
    '        while tb is not None:',
    '            if tb.tb_frame.f_code.co_filename == "main.py":',
    '                line = tb.tb_lineno',
    '            tb = tb.tb_next',
    '        msg = e.msg if isinstance(e, SyntaxError) else str(e)',
    '        err = (str(line) + "번째 줄 · " if line else "") + type(e).__name__ + (": " + msg if msg else "")',
    '        if stage is not None:',
    '            err = "[공용 함수 \'" + stage + "\' 오류] " + type(e).__name__ + (": " + msg if msg else "")',
    '    finally:',
    '        sys.stdout, sys.stdin, sys.stderr = so, si, se',
    '    return json.dumps({"ok": err is None, "out": out.getvalue()[:20000], "err": err})',
  ].join('\n');
  const WORKER_SRC = `importScripts(${JSON.stringify(PY_URL + 'pyodide.js')});
const PY = ${JSON.stringify(PY_BOOT)};
let run = null;
(async () => {
  try {
    const py = await loadPyodide({ indexURL: ${JSON.stringify(PY_URL)} });
    py.runPython(PY);
    run = py.globals.get('judge_run');
    postMessage({ ready: true });
  } catch (e) { postMessage({ fatal: String(e) }); }
})();
onmessage = (ev) => {
  const d = ev.data;
  try { postMessage(Object.assign({ id: d.id }, JSON.parse(run(d.code, d.input, d.pre || '[]')))); }
  catch (e) { postMessage({ id: d.id, ok: false, out: '', err: String(e) }); }
};`;
  let jw = null;
  let jseq = 0;
  // 선생님이 미리 만들어 둔 공용 함수 (v370_prelude.sql). 학생 코드를 돌리기 전에 먼저 불러와져요.
  let PRE_ROWS = [];
  let PRE_JSON = '[]';
  const preScope = (list, scopes) => JSON.stringify(list.filter((x) => x.enabled !== false && scopes.includes(x.scope) && String(x.code || '').trim()).map((x) => ({ n: x.name || '', c: x.code })));
  async function loadPre() {
    try {
      const { data, error } = await sb.from('prelude_funcs').select('*').order('position').order('id');
      PRE_ROWS = error || !data ? [] : data;
    } catch (e) { PRE_ROWS = []; }
    PRE_JSON = preScope(PRE_ROWS, ['all']);
  }

  function jworker() {
    if (jw) return jw.p;
    const w = new Worker(URL.createObjectURL(new Blob([WORKER_SRC], { type: 'text/javascript' })));
    const p = new Promise((res, rej) => {
      const to = setTimeout(() => rej(new Error('불러오기 시간 초과')), 90000);
      w.addEventListener('message', (ev) => {
        if (ev.data.ready) { clearTimeout(to); res(w); } else if (ev.data.fatal) { clearTimeout(to); rej(new Error(ev.data.fatal)); }
      });
      w.addEventListener('error', () => { clearTimeout(to); rej(new Error('실행 도구 오류')); });
    });
    jw = { w, p };
    p.catch(() => { if (jw && jw.w === w) { w.terminate(); jw = null; } });
    return p;
  }

  // input( ... ) 안에 뭘 적었든 상관없게: 괄호 안(안내 문구)을 비우고 input() 으로 실행해요.
  // 따옴표 없이 쓴 input(점수써라) 같은 코드도 NameError/문법 오류 없이 돌아가요. 줄 번호는 그대로 유지돼요.
  function relaxInput(code) {
    const src = String(code ?? '');
    const isId = (c) => /[A-Za-z0-9_À-￿]/.test(c || '');
    let out = '';
    let i = 0;
    const n = src.length;
    // 따옴표 문자열 하나를 끝까지 건너뛴 끝 위치(없으면 -1)
    const skipStr = (p) => {
      const q = src[p];
      const tri = src.startsWith(q.repeat(3), p);
      let k = p + (tri ? 3 : 1);
      while (k < n) {
        if (src[k] === '\\') { k += 2; continue; }
        if (tri ? src.startsWith(q.repeat(3), k) : src[k] === q) return k + (tri ? 3 : 1);
        if (!tri && src[k] === '\n') return -1;
        k += 1;
      }
      return -1;
    };
    while (i < n) {
      const c = src[i];
      if (c === '#') { const e = src.indexOf('\n', i); const end = e < 0 ? n : e; out += src.slice(i, end); i = end; continue; }
      if (c === '"' || c === "'") { const e = skipStr(i); if (e < 0) { out += c; i += 1; continue; } out += src.slice(i, e); i = e; continue; }
      if (src.startsWith('input', i) && !isId(src[i - 1]) && src[i - 1] !== '.' && !isId(src[i + 5])) {
        let j = i + 5;
        while (src[j] === ' ' || src[j] === '\t') j += 1;
        if (src[j] === '(') {
          // 짝이 맞는 닫는 괄호 찾기 (문자열 안의 괄호는 무시)
          let depth = 1;
          let k = j + 1;
          while (k < n && depth > 0) {
            const d = src[k];
            if (d === '"' || d === "'") { const e = skipStr(k); if (e > 0) { k = e; continue; } }
            if (d === '(') depth += 1;
            else if (d === ')') depth -= 1;
            k += 1;
          }
          if (depth === 0) {
            const inner = src.slice(j + 1, k - 1);
            out += 'input(' + inner.replace(/[^\n]/g, '') + ')';
            i = k;
            continue;
          }
        }
      }
      out += c;
      i += 1;
    }
    return out;
  }

  // 코드를 한 번 실행 → {status: OK | RE | TLE | LOAD, out, err}
  async function runOnce(code, input, limit = 3000) {
    let w;
    try { w = await jworker(); } catch (e) { return { status: 'LOAD', out: '', err: String(e.message || e) }; }
    code = relaxInput(code);
    return new Promise((resolve) => {
      const id = ++jseq;
      const on = (ev) => {
        if (ev.data.id !== id) return;
        clearTimeout(timer);
        w.removeEventListener('message', on);
        resolve(ev.data.ok ? { status: 'OK', out: ev.data.out } : { status: 'RE', out: ev.data.out, err: ev.data.err });
      };
      const timer = setTimeout(() => {
        w.removeEventListener('message', on);
        w.terminate();
        jw = null;
        resolve({ status: 'TLE', out: '' });
      }, limit);
      w.addEventListener('message', on);
      w.postMessage({ id, code, input, pre: PRE_JSON });
    });
  }

  const normOut = (t) => String(t ?? '').replace(/\r/g, '').split('\n').map((l) => l.replace(/\s+$/, '')).join('\n').replace(/\n+$/, '');

  const NUMRE = /-?\d+(?:\.\d+)?/g;
  const TEST_MODES = { contains: '포함', nums: '숫자', nospace: '공백무시' };
  function cmpOut(mode, got, exp) {
    if (mode === 'contains') return normOut(got).includes(normOut(exp));
    if (mode === 'nospace') return String(got ?? '').replace(/\s+/g, '') === String(exp ?? '').replace(/\s+/g, '');
    if (mode === 'nums') {
      const a = String(got ?? '').match(NUMRE) || [];
      const b = String(exp ?? '').match(NUMRE) || [];
      return a.length === b.length && b.every((x, i) => Math.abs(Number(a[i]) - Number(x)) <= 1e-6 * Math.max(1, Math.abs(Number(x))));
    }
    return normOut(got) === normOut(exp);
  }

  async function gradeAll(code, tests, onStep) {
    const cases = [];
    let passed = 0;
    let status = 'AC';
    for (let i = 0; i < tests.length; i += 1) {
      if (onStep) onStep(i, tests.length);
      const t = tests[i];
      const r = await runOnce(code, t.input || '');
      if (r.status === 'LOAD') throw new Error(r.err);
      const st = r.status === 'OK' ? (cmpOut(t.mode, r.out, t.output) ? 'AC' : 'WA') : r.status;
      cases.push({ ok: st === 'AC', st, mode: t.mode || '', hidden: !!t.hidden, input: t.input || '', expected: t.output || '', got: r.out || '', err: r.err || '' });
      if (st === 'AC') passed += 1; else if (status === 'AC') status = st;
      if (st === 'TLE') {
        for (let k = i + 1; k < tests.length; k += 1) cases.push({ ok: false, st: 'SKIP', hidden: !!tests[k].hidden, input: '', expected: '', got: '', err: '' });
        break;
      }
    }
    return { status, passed, total: tests.length, cases };
  }

  const ST_TEXT = { WA: '틀렸어요', RE: '실행 오류', TLE: '시간 초과 (3초)', SKIP: '실행 안 함' };
  const judgeBadge = (j) => {
    if (!j) return '';
    if (j.teacher) return j.teacher === 'ok' ? '<span class="badge ok">✅ 선생님 확인 · 통과</span>' : '<span class="badge bad">❌ 선생님 확인 · 오답</span>';
    if (j.status === 'MANUAL') return '<span class="badge">✍️ 선생님 확인 대기</span>';
    const man = j.manual ? ` <span class="badge">✍️ 서술 ${j.manual}개 확인 대기</span>` : '';
    return (j.status === 'AC' ? `<span class="badge ok">✅ 통과 ${j.passed}/${j.total}</span>` : `<span class="badge bad">❌ ${j.passed}/${j.total}</span>`) + man;
  };

  function renderRun(r) {
    if (r.status === 'LOAD') return `<div class="jsum bad">⚠️ 파이썬 실행 도구를 불러오지 못했어요.<br><span class="small">인터넷 연결을 확인해 보세요. (${esc(r.err)})</span></div>`;
    if (r.status === 'TLE') return '<div class="jsum bad">⏱ 시간 초과 (3초) — 무한 반복이 아닌지 확인해 보세요.</div>';
    return `<div class="muted small">출력</div><pre class="jout"><code>${esc(r.out) || '(출력 없음)'}</code></pre>${r.status === 'RE' ? `<div class="jsum bad">❌ ${esc(r.err)}</div>` : ''}`;
  }

  const MODE_HINT = { contains: ' (이 내용이 출력에 들어 있으면 통과)', nums: ' (숫자만 비교해요)', nospace: ' (공백은 무시해요)' };

  function summarize(res, parts) {
    const passed = (res ? res.passed : 0) + (parts ? parts.passed : 0);
    const total = (res ? res.total : 0) + (parts ? parts.total : 0);
    const manual = parts ? parts.manual : 0;
    let status = 'AC';
    if (total === 0) status = 'MANUAL';
    else if (passed !== total) status = res && res.status !== 'AC' && res.status !== 'WA' ? res.status : 'WA';
    return { status, passed, total, manual };
  }

  function casesHtml(res) {
    let opened = false;
    return res.cases.map((c, i) => {
      const open = !c.ok && c.st !== 'SKIP' && !opened;
      if (open) opened = true;
      let inner;
      if (c.st === 'SKIP') inner = '';
      else if (c.hidden) inner = `<p class="muted small">숨겨진 테스트라 입력과 정답은 보여주지 않아요.</p>${c.st === 'RE' ? `<div class="jsum bad">${esc(c.err)}</div>` : ''}`;
      else {
        inner = `<div class="jgrid"><div><b>입력</b><pre><code>${esc(c.input) || '(없음)'}</code></pre></div>
          <div><b>기대 출력${MODE_HINT[c.mode] || ''}</b><pre><code>${esc(c.expected) || '(없음)'}</code></pre></div>
          <div><b>내 출력</b><pre><code>${esc(c.got) || '(없음)'}</code></pre></div></div>${c.st === 'RE' ? `<div class="jsum bad">${esc(c.err)}</div>` : ''}`;
      }
      return `<details class="jcase ${c.ok ? 'ok' : 'bad'}" ${open ? 'open' : ''}><summary>${c.ok ? '✅' : c.st === 'SKIP' ? '⏭' : '❌'} 테스트 ${i + 1}${c.hidden ? ' (숨김)' : ''}${c.ok ? '' : ` · ${ST_TEXT[c.st] || ''}`}</summary>${inner}</details>`;
    }).join('');
  }

  function partsHtml(parts, answers, reveal) {
    return `<div class="parts-res">${parts.items.map((it, i) => {
      const a = answers[i];
      const icon = it.manual ? '✍️' : it.ok ? '✅' : '❌';
      const cls = it.manual ? 'man' : it.ok ? 'ok' : 'bad';
      const right = reveal && (it.manual || !it.ok)
        ? `<details class="small"><summary>${it.manual ? '모범 답안 보기' : '정답 보기'}</summary><pre><code>${esc(a.value)}${(a.alts || []).length && !it.manual ? '\n\n(다른 정답) ' + esc(a.alts.join('  /  ')) : ''}</code></pre></details>` : '';
      return `<div class="prow ${cls}">${icon} <b>${esc(a.label || i + 1)}</b>${it.manual ? ' <span class="muted small">선생님이 확인해요</span>' : it.ok ? '' : ' <span class="muted small">다시 확인해 보세요</span>'}${right}</div>`;
    }).join('')}</div>`;
  }

  function renderGrade(res, parts, answers, reveal) {
    const s = summarize(res, parts);
    const man = s.manual ? ` · ✍️ 서술 ${s.manual}개는 선생님이 확인해요` : '';
    const head = s.status === 'MANUAL' ? '<div class="jsum">✍️ 서술형 문제예요. 제출하면 선생님이 확인해요.</div>'
      : s.status === 'AC' ? `<div class="jsum ok">✅ 자동 채점은 모두 통과했어요! (${s.passed}/${s.total})${man}</div>`
        : `<div class="jsum bad">❌ ${s.passed} / ${s.total} 통과${man}</div>`;
    return head + (parts ? partsHtml(parts, answers, reveal) : '') + (res ? casesHtml(res) : '');
  }

  /* ---------- 정답 (결과 예측 · 빈칸 · 객관식 · 서술) ---------- */
  const ANS_TYPES = { t: '글자 그대로', c: '번호 선택', k: '키워드 포함', x: '식·코드 한 줄', m: '서술(선생님 확인)' };
  const normAnswers = (arr) => (Array.isArray(arr) ? arr : []).filter((a) => a && a.value != null && ANS_TYPES[a.type])
    .map((a) => ({ label: String(a.label ?? ''), type: a.type, value: String(a.value), alts: Array.isArray(a.alts) ? a.alts.map(String) : [] }));

  const CHOICE_MAP = { '①': 1, '②': 2, '③': 3, '④': 4, '⑤': 5, '가': 1, '나': 2, '다': 3, '라': 4, '마': 5, 'ㄱ': 1, 'ㄴ': 2, 'ㄷ': 3, 'ㄹ': 4, 'ㅁ': 5 };
  const normChoice = (t) => [...new Set([...String(t ?? '')].map((ch) => CHOICE_MAP[ch] || (/[1-9]/.test(ch) ? Number(ch) : 0)).filter(Boolean))].sort().join('');
  const normLines = (t) => String(t ?? '').replace(/\r/g, '').split('\n').map((l) => l.trim().replace(/\s+/g, ' ')).join('\n').replace(/^\n+|\n+$/g, '');
  const normFlat = (t) => String(t ?? '').replace(/\s+/g, ' ').trim();
  function normExpr(t) {
    let out = '';
    let q = '';
    for (const ch of String(t ?? '').replace(/\r/g, '').trim()) {
      if (q) { if (ch === q) { out += '"'; q = ''; } else out += ch; }
      else if (ch === '"' || ch === "'") { q = ch; out += '"'; }
      else if (!/\s/.test(ch)) out += ch;
    }
    return out;
  }

  // 한 칸 채점 → true / false / null(서술: 선생님이 확인)
  function checkPart(a, val) {
    if (a.type === 'm') return null;
    const v = String(val ?? '');
    if (!v.trim()) return false;
    const all = [a.value, ...(a.alts || [])];
    if (a.type === 't') return all.some((x) => normLines(x) === normLines(v) || normFlat(x) === normFlat(v));
    if (a.type === 'c') { const g = normChoice(v); return !!g && all.some((x) => normChoice(x) === g); }
    if (a.type === 'k') {
      const lv = v.toLowerCase().replace(/\s+/g, '');
      return all.some((x) => x.split(';').map((k) => k.trim().toLowerCase().replace(/\s+/g, '')).filter(Boolean).every((k) => lv.includes(k)));
    }
    if (a.type === 'x') return all.some((x) => normExpr(x) === normExpr(v));
    return false;
  }

  function gradeParts(answers, vals) {
    const items = answers.map((a, i) => {
      const r = checkPart(a, vals[i]);
      return { ok: r === true, manual: r === null };
    });
    const auto = items.filter((x) => !x.manual);
    return { items, passed: auto.filter((x) => x.ok).length, total: auto.length, manual: items.length - auto.length };
  }

  const PART_MARK = '#### 답안 ####';
  function packSubmission(code, answers, vals) {
    const body = answers.map((a, i) => `### ${a.label || i + 1}\n${vals[i] || ''}`).join('\n\n');
    return (code.trim() ? code.replace(/\s+$/, '') + '\n\n' : '') + PART_MARK + '\n' + body;
  }
  function unpackSubmission(text, n) {
    const t = String(text ?? '');
    const i = t.indexOf(PART_MARK);
    const vals = Array(n).fill('');
    if (i < 0) return { code: t, vals };
    t.slice(i + PART_MARK.length).split(/^### /m).slice(1).forEach((sec, k) => {
      if (k < n) { const nl = sec.indexOf('\n'); vals[k] = nl < 0 ? '' : sec.slice(nl + 1).replace(/\n+$/, ''); }
    });
    return { code: t.slice(0, i).replace(/\s+$/, ''), vals };
  }

  function answersToText(answers) {
    return answers.map((a) => [`@ ${a.label} | ${a.type}`, a.value, ...(a.alts || []).map((x) => '~ ' + x)].join('\n')).join('\n');
  }
  function textToAnswers(text) {
    const out = [];
    let cur = null;
    String(text ?? '').replace(/\r/g, '').split('\n').forEach((l) => {
      const m = l.match(/^@\s*(.*?)\s*\|\s*([tckxm])\s*$/);
      if (m) { cur = { label: m[1], type: m[2], vl: [], alts: [] }; out.push(cur); return; }
      if (!cur) return;
      if (l.startsWith('~ ')) cur.alts.push(l.slice(2)); else cur.vl.push(l);
    });
    return out.map((c) => {
      while (c.vl.length && c.vl[c.vl.length - 1] === '') c.vl.pop();
      return { label: c.label, type: c.type, value: c.vl.join('\n'), alts: c.alts };
    }).filter((a) => a.value !== '');
  }

  /* ---------- 테스트 케이스 글자 ↔ 데이터 ---------- */
  const normTests = (arr) => (Array.isArray(arr) ? arr : []).filter((t) => t && (t.input != null || t.output != null))
    .map((t) => ({ input: String(t.input ?? ''), output: String(t.output ?? ''), hidden: !!t.hidden, ...(TEST_MODES[t.mode] ? { mode: t.mode } : {}) }));

  function testsToText(tests) {
    return tests.map((t) => {
      const ins = t.input === '' ? [] : t.input.replace(/\n$/, '').split('\n').map((l) => '>>> ' + l);
      const outs = t.output === '' ? [] : t.output.split('\n');
      return [`---${t.hidden ? ' 숨김' : ''}${TEST_MODES[t.mode] ? ' ' + TEST_MODES[t.mode] : ''}`, ...ins, ...outs].join('\n');
    }).join('\n');
  }

  function textToTests(text) {
    const cases = [];
    let cur = null;
    String(text ?? '').replace(/\r/g, '').split('\n').forEach((l) => {
      const m = l.match(/^---((?:\s+(?:숨김|포함|숫자|공백무시))*)\s*$/);
      if (m) {
        const tk = m[1].split(/\s+/).filter(Boolean);
        cur = { hidden: tk.includes('숨김'), mode: tk.includes('포함') ? 'contains' : tk.includes('숫자') ? 'nums' : tk.includes('공백무시') ? 'nospace' : '', ins: [], outs: [] };
        cases.push(cur);
        return;
      }
      if (!cur) { if (!l.trim()) return; cur = { hidden: false, mode: '', ins: [], outs: [] }; cases.push(cur); }
      if (l.startsWith('>>>')) cur.ins.push(l.slice(3).replace(/^ /, '')); else cur.outs.push(l);
    });
    return cases.map((c) => {
      while (c.outs.length && c.outs[c.outs.length - 1] === '') c.outs.pop();
      return { input: c.ins.length ? c.ins.join('\n') + '\n' : '', output: c.outs.join('\n'), hidden: c.hidden, ...(c.mode ? { mode: c.mode } : {}) };
    }).filter((t) => t.input || t.output);
  }

  // 문제 본문의 입출력 예시(io/out 블록)에서 테스트 만들기
  function testsFromBody(body) {
    const bl = parseBlocks(body);
    const io = bl.filter((b) => b.t === 'io');
    const tests = [];
    if (io.length) {
      io.forEach((b) => {
        const ls = b.text.split('\n').filter((l) => l.trim());
        if (ls.length && ls.every((l) => l.includes('→'))) {
          ls.forEach((l) => { const [a, o] = l.replace(/^>>> ?/, '').split('→'); tests.push({ input: a.trim() + '\n', output: o.trim(), hidden: false }); });
          return;
        }
        let cur = null;
        b.text.split('\n').forEach((l) => {
          if (l.startsWith('>>>')) {
            if (!cur || cur.outs.length) { cur = { ins: [], outs: [] }; tests.push(cur); }
            cur.ins.push(l.replace(/^>>> ?/, ''));
          } else { if (!cur) { cur = { ins: [], outs: [] }; tests.push(cur); } cur.outs.push(l); }
        });
      });
      return tests.map((c) => (c.ins ? {
        input: c.ins.length ? c.ins.join('\n') + '\n' : '', output: c.outs.filter((l) => l.trim() !== '(출력 없음)').join('\n').replace(/\n+$/, ''), hidden: false,
      } : c));
    }
    const out = bl.filter((b) => b.t === 'out');
    if (out.length === 1 && !body.includes('입력')) return [{ input: '', output: out[0].text.replace(/\n+$/, ''), hidden: false }];
    return [];
  }

  /* ---------- 숙제 ---------- */
  // 번호 목록을 "1–5, 12, E1" 처럼 줄여서 보여주기
  function rangeText(list) {
    const out = [];
    for (let i = 0; i < list.length;) {
      let j = i;
      while (j + 1 < list.length && (list[j + 1].difficulty === 'ELITE') === (list[i].difficulty === 'ELITE') && list[j + 1].no === list[j].no + 1) j += 1;
      out.push(i === j ? dispNo(list[i]) : `${dispNo(list[i])}–${dispNo(list[j])}`);
      i = j + 1;
    }
    return out.join(', ');
  }

  // "1-5, 12, 20~25, E1" → 문제 고유 번호 모음
  function parseNums(text, all) {
    const tn = {};
    const te = {};
    all.forEach((e) => { (e.difficulty === 'ELITE' ? te : tn)[e.no] = e.id; });
    const ids = new Set();
    const bad = [];
    String(text).split(/[,\s]+/).filter(Boolean).forEach((tok) => {
      const m = tok.match(/^(E?)(\d+)(?:[-–~]E?(\d+))?$/i);
      if (!m) { bad.push(tok); return; }
      const tbl = m[1] ? te : tn;
      const a = Number(m[2]);
      const b = m[3] ? Number(m[3]) : a;
      if (b < a) { bad.push(tok); return; }
      for (let k = a; k <= b; k += 1) { if (tbl[k]) ids.add(tbl[k]); else bad.push((m[1] ? 'E' : '') + k); }
    });
    return { ids, bad };
  }

  async function saveHomework(set, hw, title, due, ids) {
    let hid = hw ? hw.id : null;
    if (hw) {
      const { error } = await sb.from('homeworks').update({ title, due_date: due || null }).eq('id', hid);
      if (error) return false;
      const { error: de } = await sb.from('homework_items').delete().eq('homework_id', hid);
      if (de) return false;
    } else {
      const { data, error } = await sb.from('homeworks').insert({ set_id: set.id, title, due_date: due || null }).select('id').single();
      if (error || !data) return false;
      hid = data.id;
    }
    const rows = [...ids].map((eid) => ({ homework_id: hid, exercise_id: eid }));
    for (let i = 0; i < rows.length; i += 100) {
      const { error } = await sb.from('homework_items').insert(rows.slice(i, i + 100));
      if (error) return false;
    }
    return true;
  }

  function openHwEditor(set, L, hw, draft) {
    const all = L.normal.concat(L.elite);
    const cur = draft || { title: hw ? hw.title : '', due: hw ? hw.due_date || '' : '', ids: hw ? new Set(hw.ids) : new Set() };
    const m = modal(`
      <h3>${hw ? '숙제 수정' : '숙제 만들기'}</h3>
      <form id="hwForm">
        <div class="grid2">
          <label>숙제 이름<input type="text" id="hTitle" required placeholder="예: 10/24 숙제" value="${esc(cur.title)}"></label>
          <label>마감일 (선택)<input type="date" id="hDue" value="${esc(cur.due)}"></label>
        </div>
        <label>문제 번호로 입력 <span class="muted small">예: 1-5, 12, 20-25 (ELITE는 E1, E2)</span>
          <input type="text" id="hNums" value="${esc(rangeText(all.filter((e) => cur.ids.has(e.id))))}"></label>
        <p class="muted small" id="hInfo"></p>
        <div class="form-actions">
          <button class="primary" id="hSave">저장</button>
          <button type="button" class="ghost" id="hPick">📌 문제 보면서 고르기</button>
          <button type="button" class="ghost" id="hCancel">취소</button>
        </div>
      </form>`);
    const q = (s) => $(s, m.el);
    const info = () => {
      const r = parseNums(q('#hNums').value, all);
      q('#hInfo').textContent = `${r.ids.size}개 선택${r.bad.length ? ` · ⚠️ 없는 번호: ${r.bad.join(', ')}` : ''}`;
      return r;
    };
    info();
    q('#hNums').oninput = info;
    q('#hCancel').onclick = m.close;
    const read = () => ({ title: q('#hTitle').value.trim(), due: q('#hDue').value, ids: info().ids });
    q('#hPick').onclick = () => { const d = read(); m.close(); startPick(set, L, hw, d); };
    q('#hwForm').onsubmit = async (e) => {
      e.preventDefault();
      const d = read();
      const r = info();
      if (r.bad.length && !confirm(`없는 번호(${r.bad.join(', ')})는 빼고 저장할까요?`)) return;
      if (!d.ids.size) return toast('문제를 하나 이상 골라주세요', true);
      q('#hSave').disabled = true;
      if (!(await saveHomework(set, hw, d.title, d.due, d.ids))) { q('#hSave').disabled = false; return toast('저장하지 못했어요', true); }
      m.close();
      toast('숙제를 저장했어요');
      route(true);
    };
  }

  // 문제 카드 위에 체크박스를 띄워서 직접 고르기
  function startPick(set, L, hw, draft) {
    const ids = new Set(draft.ids);
    const cards = Array.from(document.querySelectorAll('#exlist .ex'));
    const bar = document.createElement('div');
    bar.className = 'pickbar';
    document.body.appendChild(bar);
    const upd = () => { $('.pn', bar).textContent = ids.size; };
    bar.innerHTML = `<span>📌 ${esc(draft.title || '새 숙제')} · <b class="pn">0</b>개 선택</span>
      <button class="primary" id="pkSave">저장</button><button class="ghost" id="pkCancel">취소</button>`;
    cards.forEach((c) => {
      const eid = Number(c.id.replace('ex-', ''));
      const lab = document.createElement('label');
      lab.className = 'pick';
      lab.innerHTML = `<input type="checkbox" ${ids.has(eid) ? 'checked' : ''}>`;
      c.classList.toggle('picked', ids.has(eid));
      $('input', lab).onchange = (e) => {
        if (e.target.checked) ids.add(eid); else ids.delete(eid);
        c.classList.toggle('picked', e.target.checked);
        upd();
      };
      c.querySelector('.ex-head').prepend(lab);
    });
    upd();
    const end = () => {
      bar.remove();
      cards.forEach((c) => { c.classList.remove('picked'); const l = $('.pick', c); if (l) l.remove(); });
    };
    $('#pkCancel', bar).onclick = () => { end(); openHwEditor(set, L, hw, { ...draft, ids }); };
    $('#pkSave', bar).onclick = async () => {
      if (!draft.title) { end(); return openHwEditor(set, L, hw, { ...draft, ids }); }
      if (!ids.size) return toast('문제를 하나 이상 골라주세요', true);
      $('#pkSave', bar).disabled = true;
      if (!(await saveHomework(set, hw, draft.title, draft.due, ids))) { $('#pkSave', bar).disabled = false; return toast('저장하지 못했어요', true); }
      end();
      toast('숙제를 저장했어요');
      route(true);
    };
  }

  async function openHwStat(set, L, hw) {
    const all = L.normal.concat(L.elite).filter((e) => hw.ids.has(e.id));
    const [subs, pr] = await Promise.all([
      fetchAll((a, b) => sb.from('submissions').select('id,exercise_id,user_id').eq('set_id', set.id).order('id').range(a, b)),
      sb.from('profiles').select('id,username,role,status').eq('status', 'approved').neq('role', 'admin').order('username'),
    ]);
    if (pr.error) return toast('불러오지 못했어요', true);
    const by = {};
    subs.forEach((s) => { (by[s.user_id] = by[s.user_id] || new Set()).add(s.exercise_id); });
    const rows = pr.data.map((p) => {
      const have = by[p.id] || new Set();
      const miss = all.filter((e) => !have.has(e.id));
      const done = all.length - miss.length;
      return `<tr><td><b>${esc(dname(p.id, p.username))}</b></td><td>${done} / ${all.length}</td>
        <td>${miss.length ? `<span class="muted small">안 푼 문제: ${esc(rangeText(miss))}</span>` : '✅ 완료'}</td></tr>`;
    }).join('');
    modal(`<h3>📊 ${esc(hw.title)} 제출 현황</h3>
      <div class="mk-tablewrap"><table class="mk-table stat"><thead><tr><th>학생</th><th>제출</th><th>상태</th></tr></thead><tbody>${rows || '<tr><td colspan="3">학생이 없어요.</td></tr>'}</tbody></table></div>
      <p class="muted small">한 번이라도 제출한 문제는 푼 걸로 세요.</p>`);
  }

  /* ---------- 설명 글 · 끌어서 옮기기 · 더블클릭 수정 ---------- */
  async function insertNoteRows(rows) {
    for (let i = 0; i < rows.length; i += 100) {
      const { error } = await sb.from('set_notes').insert(rows.slice(i, i + 100));
      if (error) return error;
    }
    return null;
  }
  const NOTES_SQL_MSG = '설명 글은 먼저 v3911_notes.sql 을 Supabase SQL Editor 에서 한 번 실행해야 써요';

  function openNoteEditor(set, note, defaults) {
    const m = modal(`<h3>${note ? '📝 설명 글 수정' : '📝 설명 글 추가'}</h3>
      <p class="muted small">마크다운으로 써요 — <code class="ic"># 제목</code> · <code class="ic">**굵게**</code> · <code class="ic">- 목록</code> · <code class="ic">1. 번호</code> · <code class="ic">\`코드\`</code> · 코드 블록(\`\`\`) · 표 · <code class="ic">&gt; 인용</code> · <code class="ic">---</code></p>
      <label>내용<textarea id="ntBody" class="code" style="min-height:200px" spellcheck="false" placeholder="여기에 설명을 써요. 문제 사이에 끼어 들어가요.">${esc(note ? note.body : '')}</textarea></label>
      <div class="muted small">미리보기</div><div id="ntPrev" class="note-body note-prev"></div>
      <label class="inline"><input type="checkbox" id="ntPub" ${!note || note.is_public !== false ? 'checked' : ''}> 학생에게 보이기 <span class="muted small">(문제집 자체가 비공개면 이 설정과 상관없이 안 보여요)</span></label>
      <div class="form-actions"><button class="primary" id="ntSave">저장</button><button type="button" class="ghost" id="ntCancel">취소</button></div>`);
    const q = (x) => $(x, m.el);
    const prev = () => { q('#ntPrev').innerHTML = noteHtml(q('#ntBody').value) || '<span class="muted">(비어 있어요)</span>'; };
    q('#ntBody').oninput = prev;
    prev();
    q('#ntBody').focus();
    q('#ntCancel').onclick = m.close;
    q('#ntSave').onclick = async () => {
      const body = q('#ntBody').value.trim();
      if (!body) return toast('내용을 써 주세요', true);
      if (body.length > 30000) return toast('너무 길어요 (3만 자 이하)', true);
      const btn = q('#ntSave');
      btn.disabled = true;
      const row = { body, is_public: q('#ntPub').checked };
      const r = note
        ? await sb.from('set_notes').update({ ...row, updated_at: new Date().toISOString() }).eq('id', note.id).select('id').single()
        : await sb.from('set_notes').insert({ ...row, set_id: set.id, position: defaults.position, area: defaults.area }).select('id').single();
      if (r.error) { btn.disabled = false; return toast('저장하지 못했어요: ' + r.error.message, true); }
      scrollToEx = 'note-' + r.data.id;
      m.close();
      toast('저장했어요');
      route(true);
    };
  }

  function bindNotesDragEdit(v, set, exs) {
    const notes = curNotes;
    const list = $('#exlist', v);
    if (!list) return;
    const zoneOf = (el) => (el.dataset.zone === 'elite' ? 'elite' : 'normal');
    const itemOf = (el) => ({ kind: el.dataset.kind, id: Number(el.dataset.id) });
    const zi = (zone) => zoneItems(exs, notes, zone);
    const posAfter = (zone, kind, id) => {
      const arr = zi(zone);
      const i = arr.findIndex((x) => x.kind === kind && x.id === id);
      const nx = arr[i + 1];
      return nx ? (arr[i].pos + nx.pos) / 2 : arr[i].pos + 1000;
    };
    const needNotes = () => { if (NOTES_OK) return true; toast(NOTES_SQL_MSG, true); return false; };

    /* 설명 글 추가·수정·삭제 */
    const an = $('#addNote', v);
    if (an) an.onclick = () => {
      if (!needNotes()) return;
      const arr = zi('normal');
      openNoteEditor(set, null, { position: arr.length ? arr[arr.length - 1].pos + 1000 : 1000, area: 'normal' });
    };
    v.querySelectorAll('[data-nadd]').forEach((b) => (b.onclick = () => {
      if (!needNotes()) return;
      const [kind, id] = b.dataset.nadd.split(':');
      const el = b.closest('.ex');
      openNoteEditor(set, null, { position: posAfter(zoneOf(el), kind, Number(id)), area: zoneOf(el) });
    }));
    v.querySelectorAll('[data-nedit]').forEach((b) => (b.onclick = () => openNoteEditor(set, notes.find((n) => n.id === Number(b.dataset.nedit)), null)));
    v.querySelectorAll('[data-ndel]').forEach((b) => (b.onclick = async () => {
      if (!confirm('이 설명 글을 삭제할까요?')) return;
      const { error } = await sb.from('set_notes').delete().eq('id', Number(b.dataset.ndel));
      if (error) return toast('삭제하지 못했어요', true);
      toast('삭제했어요');
      route(true);
    }));
    v.querySelectorAll('[data-addnote]').forEach((b) => (b.onclick = () => { // 설명 글 아래에 문제 추가
      const n = notes.find((x) => x.id === Number(b.dataset.addnote));
      const zone = n.area === 'elite' ? 'elite' : 'normal';
      const arr = zi(zone);
      const i = arr.findIndex((x) => x.kind === 'note' && x.id === n.id);
      const g = arr.slice(i + 1).find((x) => x.kind === 'ex') || arr.slice(0, i).reverse().find((x) => x.kind === 'ex');
      openExEditor(set, exs, null, {
        position: posAfter(zone, 'note', n.id), difficulty: zone === 'elite' ? 'ELITE' : (g ? g.o.difficulty : 'Beginner'),
        chapter: zone === 'elite' || !g ? '' : g.o.chapter, section: zone === 'elite' || !g ? '' : g.o.section,
      });
    }));

    /* 글을 더블클릭해서 그 자리에서 수정 */
    if (admOpt('dbl')) {
      list.addEventListener('dblclick', (ev) => {
        const body = ev.target.closest('.ex-body');
        if (!body || !list.contains(body) || body.querySelector('textarea.inline-edit')) return;
        if (ev.target.closest('a,button,textarea,input,summary,select')) return;
        const card = body.closest('.ex');
        if (!card) return;
        const { kind, id } = itemOf(card);
        const obj = kind === 'note' ? notes.find((n) => n.id === id) : exs.find((e) => e.id === id);
        if (!obj) return;
        const sel = window.getSelection();
        if (sel) sel.removeAllRanges();
        const keep = body.innerHTML;
        body.innerHTML = `<textarea class="inline-edit code" spellcheck="false"></textarea>
          <div class="form-actions"><button class="primary" type="button" data-ie-save>저장</button><button class="ghost" type="button" data-ie-cancel>취소</button><span class="muted small">Ctrl+Enter 저장 · Esc 취소</span></div>`;
        const ta = $('textarea', body);
        ta.value = obj.body;
        ta.rows = Math.min(30, Math.max(4, obj.body.split('\n').length + 2));
        ta.focus();
        const cancel = () => { body.innerHTML = keep; };
        const save = async () => {
          const val = ta.value.trim();
          if (!val) return toast('내용이 비어 있어요', true);
          if (val === obj.body.trim()) return cancel();
          ta.disabled = true;
          const { error } = await sb.from(kind === 'note' ? 'set_notes' : 'exercises').update({ body: val }).eq('id', id);
          if (error) { ta.disabled = false; return toast('저장하지 못했어요: ' + error.message, true); }
          obj.body = val;
          body.innerHTML = kind === 'note' ? noteHtml(val) : renderMarkup(val);
          toast('저장했어요');
        };
        $('[data-ie-save]', body).onclick = save;
        $('[data-ie-cancel]', body).onclick = cancel;
        ta.onkeydown = (e) => {
          if (e.key === 'Escape') { e.preventDefault(); cancel(); }
          else if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); save(); }
        };
      });
    }

    /* 끌어서 순서 바꾸기 (마우스·터치 둘 다) */
    if (!admOpt('drag')) return;
    list.querySelectorAll('.drag-grip').forEach((g) => (g.onpointerdown = (ev) => {
      if (ev.button != null && ev.button !== 0) return;
      const el = g.closest('.ex');
      if (!el) return;
      ev.preventDefault();
      const me2 = itemOf(el);
      const myZone = zoneOf(el);
      const strict = me2.kind === 'ex'; // 문제는 같은 구역(일반/ELITE) 안에서만
      let tgt = null;
      let before = true;
      let lastY = ev.clientY;
      let raf = 0;
      el.classList.add('dragging');
      document.body.classList.add('dragging-ex');
      const clear = () => list.querySelectorAll('.drop-before,.drop-after').forEach((x) => x.classList.remove('drop-before', 'drop-after'));
      const pick = (y) => {
        let best = null;
        let bd = 1e9;
        list.querySelectorAll('.ex[data-kind]').forEach((c) => {
          if (c === el || (strict && zoneOf(c) !== myZone)) return;
          const r = c.getBoundingClientRect();
          if (!r.height) return;
          const d = y < r.top ? r.top - y : y > r.bottom ? y - r.bottom : 0;
          if (d < bd) { bd = d; best = c; }
        });
        clear();
        tgt = best;
        if (best) {
          const r = best.getBoundingClientRect();
          before = y < r.top + r.height / 2;
          best.classList.add(before ? 'drop-before' : 'drop-after');
        }
      };
      const loop = () => {
        raf = requestAnimationFrame(loop);
        if (lastY < 70) window.scrollBy(0, -Math.ceil((70 - lastY) / 4));
        else if (lastY > window.innerHeight - 70) window.scrollBy(0, Math.ceil((lastY - (window.innerHeight - 70)) / 4));
        pick(lastY);
      };
      raf = requestAnimationFrame(loop);
      const onMove = (e) => { lastY = e.clientY; };
      const end = () => {
        cancelAnimationFrame(raf);
        window.removeEventListener('pointermove', onMove);
        window.removeEventListener('pointerup', onUp);
        window.removeEventListener('pointercancel', onCancel);
        window.removeEventListener('keydown', onKey);
        el.classList.remove('dragging');
        document.body.classList.remove('dragging-ex');
        clear();
      };
      const onCancel = () => end();
      const onKey = (e) => { if (e.key === 'Escape') end(); };
      const onUp = async () => {
        const t = tgt;
        const bef = before;
        end();
        if (!t) return;
        const dz = zoneOf(t);
        const ti = itemOf(t);
        const arr = zi(dz).filter((x) => !(x.kind === me2.kind && x.id === me2.id));
        let at = arr.findIndex((x) => x.kind === ti.kind && x.id === ti.id);
        if (at < 0) return;
        if (!bef) at += 1;
        const prev = arr[at - 1];
        const next = arr[at];
        let pos;
        let renum = false;
        if (prev && next) { pos = (prev.pos + next.pos) / 2; if (next.pos - prev.pos < 1e-6) renum = true; }
        else if (prev) pos = prev.pos + 1000;
        else if (next) pos = next.pos > 2 ? next.pos / 2 : next.pos - 1000;
        else pos = 1000;
        const moved = zi(myZone).find((x) => x.kind === me2.kind && x.id === me2.id);
        let extra = {};
        if (me2.kind === 'note') extra = { area: dz };
        else if (dz === 'normal') {
          const g = arr.slice(at).find((x) => x.kind === 'ex') || arr.slice(0, at).reverse().find((x) => x.kind === 'ex');
          if (g) extra = { chapter: g.o.chapter, section: g.o.section };
        }
        const tbl = (k) => (k === 'ex' ? 'exercises' : 'set_notes');
        const ops = [];
        if (!renum) ops.push(() => sb.from(tbl(me2.kind)).update({ position: pos, ...extra }).eq('id', me2.id));
        else {
          const full = arr.slice();
          full.splice(at, 0, moved);
          full.forEach((x, i) => ops.push(() => sb.from(tbl(x.kind)).update(x === moved ? { position: (i + 1) * 1000, ...extra } : { position: (i + 1) * 1000 }).eq('id', x.id)));
        }
        for (let i = 0; i < ops.length; i += 10) {
          const res = await Promise.all(ops.slice(i, i + 10).map((f) => f()));
          if (res.some((r) => r.error)) return toast('순서를 바꾸지 못했어요', true);
        }
        scrollToEx = el.id;
        route(true);
      };
      window.addEventListener('pointermove', onMove);
      window.addEventListener('pointerup', onUp);
      window.addEventListener('pointercancel', onCancel);
      window.addEventListener('keydown', onKey);
    }));
  }

  /* ---------- 문제집 : 선생님 도구 (추가/수정/삭제/순서/설정) ---------- */
  function bindSetAdmin(v, set, exs, hws, L) {
    const byId = (i) => exs.find((e) => e.id === Number(i));
    const lastNormal = exs.filter((e) => e.difficulty !== 'ELITE').pop();
    const maxPos = Math.max(exs.reduce((m, e) => Math.max(m, e.position), 0), curNotes.reduce((m, n) => Math.max(m, n.position), 0));
    bindNotesDragEdit(v, set, exs);

    $('#addEx', v).onclick = () => openExEditor(set, exs, null, {
      position: maxPos + 1000, difficulty: 'Beginner',
      chapter: lastNormal ? lastNormal.chapter : '', section: lastNormal ? lastNormal.section : '',
    });
    const ae = $('#addElite', v);
    if (ae) ae.onclick = () => openExEditor(set, exs, null, { position: maxPos + 1000, difficulty: 'ELITE', chapter: '', section: '' });
    $('#setCfg', v).onclick = () => openSetCfg(set);
    $('#addJson', v).onclick = () => openAddJson(set, exs);
    $('#addLive', v).onclick = () => openLiveImport(set, exs);
    const tp = $('#togPub', v);
    if (tp) tp.onclick = async () => {
      const to = set.is_public === false;
      if (!confirm(to ? `"${set.title}" 문제집을 학생에게 공개할까요?` : `"${set.title}" 문제집을 비공개로 바꿀까요?\n학생에게는 바로 안 보여요. (제출 기록은 그대로 남아요)`)) return;
      const { error } = await sb.from('problem_sets').update({ is_public: to }).eq('id', set.id);
      if (error) return toast('바꾸지 못했어요: ' + error.message, true);
      toast(to ? '공개했어요! 이제 학생에게 보여요 🌐' : '비공개로 바꿨어요 🔒');
      route(true);
    };
    const pa = $('#pubAllEx', v);
    if (pa) pa.onclick = async () => {
      const n = exs.filter((e) => e.is_public === false).length;
      if (!confirm(`비공개 문제 ${n}개를 모두 공개할까요?`)) return;
      const { error } = await sb.from('exercises').update({ is_public: true }).eq('set_id', set.id).eq('is_public', false);
      if (error) return toast('공개하지 못했어요: ' + error.message, true);
      toast('공개했어요 🌐'); route(true);
    };
    const ah = $('#addHw', v);
    if (ah) ah.onclick = () => openHwEditor(set, L, null);
    const hwById = (i) => hws.find((h) => h.id === Number(i));
    v.querySelectorAll('[data-hwedit]').forEach((b) => (b.onclick = () => openHwEditor(set, L, hwById(b.dataset.hwedit))));
    v.querySelectorAll('[data-hwstat]').forEach((b) => (b.onclick = () => openHwStat(set, L, hwById(b.dataset.hwstat))));
    v.querySelectorAll('[data-hwdel]').forEach((b) => (b.onclick = async () => {
      const h = hwById(b.dataset.hwdel);
      if (!confirm(`"${h.title}" 숙제를 삭제할까요? (문제와 학생 풀이는 그대로 남아요)`)) return;
      const { error } = await sb.from('homeworks').delete().eq('id', h.id);
      if (error) return toast('삭제하지 못했어요', true);
      route(true);
    }));
    $('#expSet', v).onclick = () => exportSet(set, exs, curNotes);
    $('#impKey', v).onclick = () => {
      if (testsColumn === false || answersColumn === false) return toast('먼저 update4.sql, update5.sql을 실행해 주세요', true);
      $('#impKeyFile', v).click();
    };
    $('#impKeyFile', v).onchange = async (ev) => {
      const f = ev.target.files[0];
      ev.target.value = '';
      if (!f) return;
      let parsed;
      try { parsed = parseSetJson(await f.text()); } catch (e) { return toast(e.message, true); }
      const pool = new Map();
      parsed.rows.forEach((r) => { const k = normFlat(r.body); if (!pool.has(k)) pool.set(k, []); pool.get(k).push(r); });
      const todo = [];
      exs.forEach((e) => {
        const list = pool.get(normFlat(e.body));
        const r = list && list.shift();
        if (r && (r.tests.length || r.answers.length)) todo.push({ e, r });
      });
      if (!todo.length) return toast('이 문제집과 내용이 같은 문제를 찾지 못했어요. 문제집을 지우고 JSON으로 다시 가져와 보세요.', true);
      const miss = exs.length - todo.length;
      if (!confirm(`${todo.length}문제의 채점 테스트와 정답을 덮어쓸까요?\n(문제 내용과 학생 제출물은 그대로예요${miss ? ` · 내용이 달라 건너뛰는 문제 ${miss}개` : ''})`)) return;
      const btn = $('#impKey', v);
      btn.disabled = true;
      for (let i = 0; i < todo.length; i += 10) {
        const res = await Promise.all(todo.slice(i, i + 10).map((x) => sb.from('exercises').update({ tests: x.r.tests, answers: x.r.answers }).eq('id', x.e.id)));
        if (res.some((r) => r.error)) { btn.disabled = false; return toast('저장하지 못했어요 (update4.sql, update5.sql을 실행했나요?)', true); }
      }
      toast(`${todo.length}문제에 정답·채점을 넣었어요${miss ? ` (건너뜀 ${miss})` : ''}`);
      route(true);
    };
    $('#autoTests', v).onclick = async (ev) => {
      if (testsColumn === false) return toast('먼저 update4.sql을 실행해 주세요', true);
      const todo = exs.map((e) => ({ e, t: (e.tests || []).length ? [] : testsFromBody(e.body) })).filter((x) => x.t.length);
      if (!todo.length) return toast('새로 만들 테스트가 없어요 (이미 있거나 입출력 예시가 없어요)');
      if (!confirm(`입출력 예시가 있는 ${todo.length}문제에 자동 채점 테스트를 만들까요?\n(이미 테스트가 있는 문제는 그대로 둬요)`)) return;
      ev.target.disabled = true;
      for (let i = 0; i < todo.length; i += 10) {
        const res = await Promise.all(todo.slice(i, i + 10).map((x) => sb.from('exercises').update({ tests: x.t }).eq('id', x.e.id)));
        if (res.some((r) => r.error)) { ev.target.disabled = false; return toast('저장하지 못했어요 (update4.sql을 실행했나요?)', true); }
      }
      toast(`${todo.length}문제에 채점 테스트를 만들었어요`);
      route(true);
    };

    v.querySelectorAll('[data-edit]').forEach((b) => (b.onclick = () => openExEditor(set, exs, byId(b.dataset.edit), null)));
    v.querySelectorAll('[data-add]').forEach((b) => (b.onclick = () => {
      const e = byId(b.dataset.add);
      const zi = zoneItems(exs, curNotes, e.difficulty === 'ELITE' ? 'elite' : 'normal');
      const nx = zi[zi.findIndex((x) => x.kind === 'ex' && x.id === e.id) + 1];
      openExEditor(set, exs, null, {
        position: nx ? (e.position + nx.pos) / 2 : e.position + 1000,
        difficulty: e.difficulty, chapter: e.chapter, section: e.section,
      });
    }));
    const move = async (id, dir) => {
      const e = byId(id);
      const peers = exs.filter((x) => (x.difficulty === 'ELITE') === (e.difficulty === 'ELITE'));
      const o = peers[peers.findIndex((x) => x.id === e.id) + dir];
      if (!o) return;
      const [r1, r2] = await Promise.all([
        sb.from('exercises').update({ position: o.position, chapter: o.chapter, section: o.section }).eq('id', e.id),
        sb.from('exercises').update({ position: e.position }).eq('id', o.id),
      ]);
      if (r1.error || r2.error) return toast('순서를 바꾸지 못했어요', true);
      scrollToEx = 'ex-' + e.id;
      route(true);
    };
    v.querySelectorAll('[data-up]').forEach((b) => (b.onclick = () => move(b.dataset.up, -1)));
    v.querySelectorAll('[data-down]').forEach((b) => (b.onclick = () => move(b.dataset.down, 1)));
    v.querySelectorAll('[data-del]').forEach((b) => (b.onclick = async () => {
      const e = byId(b.dataset.del);
      if (!confirm(`${dispNo(e)}번 문제를 삭제할까요?\n이 문제에 학생들이 제출한 풀이도 함께 삭제돼요.`)) return;
      const { error } = await sb.from('exercises').delete().eq('id', e.id);
      if (error) return toast('삭제하지 못했어요', true);
      toast('삭제했어요');
      route(true);
    }));
  }

  const SNIPS = {
    '코드': '```\n코드\n```\n',
    '입출력': '```io\n>>> 입력값\n출력값\n```\n',
    '출력': '```out\n출력 결과\n```\n',
    '프로그램(줄번호)': '```program\nprint("hi")\n```\n',
    '조건 박스': '```box 조건\n○ 조건 하나\n○ 조건 둘\n```\n',
    '표': '```table 실행예시\n구분 | 입력 | 출력\n예시 1 | 3 | 9\n```\n',
  };

  function openExEditor(set, list, ex, base) {
    const cur = ex || { ...base, label: '', points: null, tags: [], source: '', body: '', check_point: '', answers: [], is_public: false };
    const hasPub = !!ex ? 'is_public' in ex : PUB_READY === true;
    const uniq = (k) => [...new Set(list.map((e) => e[k]).filter(Boolean))];
    const m = modal(`
      <h3>${ex ? `문제 수정 <span class="muted small">(고유 번호 ${ex.id})</span>` : '문제 추가'}</h3>
      <form id="exForm">
        <div class="grid2">
          <label>난이도<select id="fDiff">${(RK_READY ? diffNames() : DIFFS).map((d) => `<option ${cur.difficulty === d ? 'selected' : ''}>${esc(d)}</option>`).join('')}</select></label>
          <label>유형 (선택)<input type="text" id="fLabel" placeholder="예: 빈칸 채우기 · 서술형" value="${esc(cur.label || '')}"></label>
        </div>
        <div class="grid2">
          <label>배점 (선택)<input type="number" id="fPts" min="0" value="${cur.points ?? ''}"></label>
          <label>출처 (선택)<input type="text" id="fSrc" placeholder="예: 백준 2557번" value="${esc(cur.source || '')}"></label>
        </div>
        ${RK_READY ? `<label>🏆 랭킹 점수 (선택) <span class="muted small">— 비워 두면 난이도 점수를 써요</span><input type="number" id="fRank" min="0" placeholder="${diffPts(cur.difficulty)}" value="${cur.rank_points ?? ''}"></label>` : ''}
        <label>태그 (쉼표로 구분, 선택)<input type="text" id="fTags" placeholder="예: 50자 이내, abs() 사용 금지" value="${esc((cur.tags || []).join(', '))}"></label>
        <div class="grid2">
          <label>챕터<input type="text" id="fCh" list="dlCh" value="${esc(cur.chapter || '')}"></label>
          <label>섹션<input type="text" id="fSec" list="dlSec" value="${esc(cur.section || '')}"></label>
        </div>
        <datalist id="dlCh">${uniq('chapter').map((x) => `<option value="${esc(x)}">`).join('')}</datalist>
        <datalist id="dlSec">${uniq('section').map((x) => `<option value="${esc(x)}">`).join('')}</datalist>
        ${hasPub ? `<label>공개 설정<select id="fPub"><option value="0" ${cur.is_public === false ? 'selected' : ''}>🔒 비공개 (학생에게 안 보여요)</option><option value="1" ${cur.is_public === false ? '' : 'selected'}>🌐 바로 게시</option></select></label>` : ''}
        <label>문제 내용</label>
        <div class="snips">${Object.keys(SNIPS).map((k) => `<button type="button" class="ghost" data-snip="${esc(k)}">${esc(k)}</button>`).join('')}</div>
        <textarea id="fBody" class="code" style="min-height:220px" required>${esc(cur.body)}</textarea>
        <label>미리보기</label><div id="fPrev" class="ex-body prev"></div>
        <label>자동 채점 테스트 (선택) <span class="muted small">— 비워 두면 채점 없이 제출만 받아요</span></label>
        <div class="snips">
          <button type="button" class="ghost" id="tFromBody">문제의 입출력 예시 가져오기</button>
          <button type="button" class="ghost" id="tFill">정답 코드로 기대 출력 채우기</button>
        </div>
        <textarea id="fTests" class="code" style="min-height:130px" spellcheck="false" placeholder="---&#10;>>> 5&#10;25&#10;--- 숨김&#10;>>> 7&#10;49">${esc(testsToText(cur.tests || []))}</textarea>
        <p class="muted small" style="margin:2px 0">한 테스트는 <b>---</b> 줄로 시작해요. <b>&gt;&gt;&gt;</b> 로 시작하는 줄은 입력(input() 한 번에 한 줄), 나머지 줄은 기대 출력이에요. <b>--- 숨김</b> 은 학생에게 입력·정답을 안 보여주는 테스트예요.</p>
        <div id="tRefBox" hidden>
          <label>정답 코드 <span class="muted small">(저장되지 않아요. 기대 출력이 빈 테스트의 출력을 이 코드로 채워요)</span></label>
          <textarea id="fRef" class="code" style="min-height:110px" spellcheck="false"></textarea>
          <div class="form-actions"><button type="button" class="ghost" id="tRun">▶ 실행해서 채우기</button></div>
        </div>
        <label>정답 칸 (선택) <span class="muted small">— 결과 예측·빈칸·객관식·서술형 답을 적어 두면 학생 화면에 답 칸이 생기고 채점돼요</span></label>
        <textarea id="fAns" class="code" style="min-height:110px" spellcheck="false" placeholder="@ (가) | t&#10;실행 결과&#10;~ 다른 정답&#10;@ 객관식 | c&#10;3">${esc(answersToText(cur.answers || []))}</textarea>
        <p class="muted small" style="margin:2px 0"><b>@ 이름 | 유형</b> 줄로 칸을 만들고, 아래 줄이 정답이에요. <b>~ </b> 로 시작하는 줄은 다른 정답이에요. 유형: <b>t</b> 글자 그대로(공백 정리) · <b>c</b> 번호 선택(①②, 1,2, 가나) · <b>k</b> 키워드 포함(<b>;</b> 로 여러 개) · <b>x</b> 코드 한 줄(공백·따옴표 무시) · <b>m</b> 서술(선생님이 확인)</p>
        <label>확인 포인트 (선택)<textarea id="fCheck" style="min-height:60px">${esc(cur.check_point || '')}</textarea></label>
        <div class="form-actions"><button class="primary" id="fSave">저장</button><button type="button" class="ghost" id="fCancel">취소</button></div>
      </form>`);
    const q = (s) => $(s, m.el);
    const prev = () => { q('#fPrev').innerHTML = renderMarkup(q('#fBody').value) || '<span class="muted small">(비어 있어요)</span>'; };
    prev();
    q('#fBody').oninput = prev;
    q('#fCancel').onclick = m.close;
    q('#tFromBody').onclick = () => {
      const t = testsFromBody(q('#fBody').value);
      if (!t.length) return toast('본문에서 입출력 예시를 찾지 못했어요', true);
      q('#fTests').value = testsToText(t);
    };
    q('#tFill').onclick = () => { q('#tRefBox').hidden = !q('#tRefBox').hidden; };
    q('#tRun').onclick = async () => {
      const ref = q('#fRef').value;
      if (!ref.trim()) return toast('정답 코드를 입력하세요', true);
      const tests = textToTests(q('#fTests').value);
      const btn = q('#tRun');
      btn.disabled = true;
      btn.textContent = '⏳ 실행 중…';
      for (const t of tests) {
        if (t.output) continue;
        const r = await runOnce(ref, t.input);
        if (r.status !== 'OK') { toast(r.status === 'LOAD' ? '실행 도구를 불러오지 못했어요' : `정답 코드 실행 실패: ${r.err || r.status}`, true); break; }
        t.output = r.out.replace(/\s+$/, '');
      }
      q('#fTests').value = testsToText(tests);
      btn.disabled = false;
      btn.textContent = '▶ 실행해서 채우기';
    };
    m.el.querySelectorAll('[data-snip]').forEach((b) => (b.onclick = () => {
      const t = q('#fBody');
      const s = t.selectionStart;
      const pre = s > 0 && t.value[s - 1] !== '\n' ? '\n' : '';
      t.value = t.value.slice(0, s) + pre + SNIPS[b.dataset.snip] + t.value.slice(t.selectionEnd);
      t.focus();
      prev();
    }));
    q('#exForm').onsubmit = async (e) => {
      e.preventDefault();
      const body = q('#fBody').value.trim();
      if (!body) return toast('문제 내용을 입력하세요', true);
      const pts = q('#fPts').value;
      const row = {
        difficulty: q('#fDiff').value, label: q('#fLabel').value.trim() || null,
        points: pts === '' ? null : Number(pts), source: q('#fSrc').value.trim() || null,
        tags: q('#fTags').value.split(',').map((x) => x.trim()).filter(Boolean),
        chapter: q('#fCh').value.trim() || null, section: q('#fSec').value.trim() || null,
        body, check_point: q('#fCheck').value.trim() || null,
      };
      const tests = textToTests(q('#fTests').value);
      if (testsColumn !== false) row.tests = tests;
      else if (tests.length) toast('테스트는 update4.sql을 실행한 뒤에 저장돼요', true);
      const answers = textToAnswers(q('#fAns').value);
      if (answersColumn !== false) row.answers = answers;
      else if (answers.length) toast('정답은 update5.sql을 실행한 뒤에 저장돼요', true);
      if (q('#fPub')) row.is_public = q('#fPub').value === '1';
      if (RK_READY && q('#fRank')) { const rp = q('#fRank').value; row.rank_points = rp === '' ? null : Number(rp); }
      const btn = q('#fSave');
      btn.disabled = true;
      let id = ex ? ex.id : null;
      if (ex) {
        const { error } = await sb.from('exercises').update({ ...row, updated_at: new Date().toISOString() }).eq('id', ex.id);
        if (error) { btn.disabled = false; return toast('저장하지 못했어요', true); }
      } else {
        const { data, error } = await sb.from('exercises').insert({ ...row, set_id: set.id, position: base.position }).select('id').single();
        if (error || !data) { btn.disabled = false; return toast('추가하지 못했어요', true); }
        id = data.id;
      }
      m.close();
      toast(ex ? '수정했어요' : '추가했어요. 번호는 자동으로 정리돼요');
      scrollToEx = 'ex-' + id;
      route(true);
    };
  }

  function openSetCfg(set) {
    const fileRow = (key, label, f) => `
      <label>${label}</label>
      ${f ? `<label class="inline file-row"><input type="checkbox" id="rm_${key}"> 📎 ${esc(f.name || 'file.pdf')} <span class="muted small">(체크하면 삭제)</span></label>` : '<p class="muted small" style="margin:2px 0">올린 파일이 없어요.</p>'}
      <input type="file" id="up_${key}" accept="application/pdf,.pdf">`;
    const m = modal(`
      <h3>⚙️ 문제집 설정</h3>
      <form id="cfgForm">
        <div class="grid2">
          <label>제목<input type="text" id="cTitle" required value="${esc(set.title)}"></label>
          <label>주차<input type="number" id="cWeek" min="1" value="${set.week ?? ''}"></label>
        </div>
        <label>짧은 이름 <span class="muted small">(제출함에서 "student1 - A")</span><input type="text" id="cShort" value="${esc(set.short_name || '')}"></label>
        <label>설명<textarea id="cDesc" style="min-height:70px">${esc(set.description || '')}</textarea></label>
        ${fileRow('original_file', '문제 원본 PDF (선택)', set.original_file)}
        ${fileRow('answer_file', '정답 PDF (선택)', set.answer_file)}
        <label class="inline"><input type="checkbox" id="cPub" ${set.answer_public ? 'checked' : ''}> 정답 PDF를 학생에게 공개</label>
        <div class="form-actions"><button class="primary" id="cSave">저장</button><button type="button" class="ghost" id="cCancel">취소</button>
          <span class="spacer"></span><button type="button" class="danger-btn" id="cDel">문제집 삭제</button></div>
      </form>`);
    const q = (s) => $(s, m.el);
    q('#cCancel').onclick = m.close;
    q('#cDel').onclick = async () => {
      if (!confirm(`"${set.title}" 문제집을 삭제할까요?\n문제와 학생들의 제출 기록이 모두 삭제돼요. 되돌릴 수 없어요.`)) return;
      const ans = prompt('정말 삭제하려면 "삭제"라고 입력하세요');
      if (ans !== '삭제') return;
      const { error } = await sb.from('problem_sets').delete().eq('id', set.id);
      if (error) return toast('삭제하지 못했어요', true);
      await removeFiles([set.original_file, set.answer_file].filter(Boolean).map((f) => ({ ...f, bucket: 'sets' })));
      m.close();
      location.hash = '#/sets';
    };
    q('#cfgForm').onsubmit = async (e) => {
      e.preventDefault();
      const btn = q('#cSave');
      btn.disabled = true;
      const upd = {
        title: q('#cTitle').value.trim(), week: Number(q('#cWeek').value) || null,
        short_name: q('#cShort').value.trim() || null, description: q('#cDesc').value.trim() || null,
        answer_public: q('#cPub').checked, updated_at: new Date().toISOString(),
      };
      const trash = [];
      const fresh = [];
      for (const [key, kind] of [['original_file', 'original'], ['answer_file', 'answer']]) {
        const picked = q('#up_' + key).files[0];
        const rm = q('#rm_' + key);
        if (picked) {
          if (picked.size > MAX_FILE) { btn.disabled = false; return toast('파일은 50MB 이하만 올릴 수 있어요', true); }
          const path = `${set.id}/${kind}/${Date.now()}_${rand()}.pdf`;
          const { error } = await sb.storage.from('sets').upload(path, picked, { contentType: 'application/pdf' });
          if (error) { await removeFiles(fresh); btn.disabled = false; return toast(`"${picked.name}" 파일을 올리지 못했어요`, true); }
          upd[key] = { path, name: picked.name, bucket: 'sets' };
          fresh.push({ path, bucket: 'sets' });
          if (set[key]) trash.push({ ...set[key], bucket: 'sets' });
        } else if (rm && rm.checked) {
          upd[key] = null;
          trash.push({ ...set[key], bucket: 'sets' });
        }
      }
      const { error } = await sb.from('problem_sets').update(upd).eq('id', set.id);
      if (error) { await removeFiles(fresh); btn.disabled = false; return toast('저장하지 못했어요', true); }
      await removeFiles(trash);
      m.close();
      toast('저장했어요');
      route(true);
    };
  }

  /* ---------- 제출함 (선생님 전용): 학생별 → 문제집별 ---------- */
  const SQL_REGRADE = 'grant update (judge) on public.submissions to authenticated;\ncreate policy "submissions admin update" on public.submissions for update to authenticated using (public.is_admin()) with check (public.is_admin());';

  // 예전(칸이 나뉘기 전)에 낸 제출은 답이 통째로 한 덩어리 글로 저장돼 있어요. 칸별로 안전하게 나눌 수 있을 때만 나누고, 못 나누면 null.
  function legacyVals(text, answers) {
    const t = String(text ?? '').replace(/\r/g, '');
    const n = answers.length;
    if (n === 1) return [t.trim()];
    const lines = t.split('\n');
    // 1) "(가) 큼" 처럼 칸 이름으로 시작하는 줄 기준 (칸 이름의 첫 단어가 서로 달라야 안전해요)
    const norm = (x) => String(x).replace(/[()\[\]\s.:：]/g, '');
    const tok = answers.map((a) => norm(String(a.label || '').trim().split(/\s+/)[0] || ''));
    if (tok.every((x) => x && x.length <= 6) && new Set(tok).size === n) {
      const at = [];
      let from = 0;
      for (let i = 0; i < n; i += 1) {
        let k = -1;
        for (let j = from; j < lines.length; j += 1) {
          const m = lines[j].match(/^\s*[(\[]?\s*([^\s)\]:：.]{1,6})\s*[)\]:：.]?\s?(.*)$/);
          if (m && norm(m[1]) === tok[i]) { k = j; break; }
        }
        if (k < 0) { at.length = 0; break; }
        at.push(k); from = k + 1;
      }
      if (at.length === n) {
        return at.map((k, i) => {
          const first = lines[k].replace(/^\s*[(\[]?\s*[^\s)\]:：.]{1,6}\s*[)\]:：.]?\s?/, '');
          return [first, ...lines.slice(k + 1, i + 1 < n ? at[i + 1] : lines.length)].join('\n').trim();
        });
      }
    }
    // 2) 칸 수와 비어 있지 않은 줄 수가 같으면 한 줄에 한 칸
    const ne = lines.map((l) => l.trim()).filter(Boolean);
    if (ne.length === n) return ne;
    return null;
  }

  // 채점할 수 있는 문제인가? (테스트 또는 자동 채점 답칸이 있어야 해요. 서술형만 있으면 건너뛰어요)
  const gradable = (ex) => !!ex && ((ex.tests || []).length > 0 || (ex.answers || []).some((a) => a.type !== 'm'));

  // 채점 안 된 제출(judge 없음)을 한꺼번에 채점해서 저장. force=true 면 이미 채점된 것도 다시.
  let lastBulk = ''; // 채점이 끝난 뒤 화면을 새로 그려도 결과를 보여주기 위해
  const pgHTML = (i, n, note, done) => {
    const pct = n ? Math.round((i / n) * 100) : 0;
    return `<div class="pg ${done ? 'done' : ''}"><div class="pg-bar"><i style="width:${pct}%"></i></div><div class="pg-t"><b>${pct}%</b> · ${i} / ${n}건${note ? ` · <span class="muted">${note}</span>` : ''}</div></div>`;
  };
  async function bulkGrade(subs, exMap, statusEl, force = false, names = {}) {
    const todo = subs.filter((s) => (force || !s.judge) && !(s.judge && s.judge.teacher) && gradable(exMap[s.exercise_id])); // 선생님이 직접 판정한 건 다시 채점하지 않아요
    if (!todo.length) { toast('채점할 제출이 없어요'); if (statusEl) statusEl.innerHTML = ''; return null; }
    if (statusEl) statusEl.innerHTML = pgHTML(0, todo.length, '준비 중…');
    const out = { ok: 0, ac: 0, fail: 0, man: 0, total: todo.length };
    for (let i = 0; i < todo.length; i += 1) {
      const sub = todo[i];
      const ex = exMap[sub.exercise_id];
      const tests = ex.tests || [];
      const answers = ex.answers || [];
      if (statusEl) statusEl.innerHTML = pgHTML(i, todo.length, `${esc(names[sub.user_id] || '')} 채점 중…${i === 0 ? ' (처음엔 파이썬을 준비하느라 몇 초 걸려요)' : ''}`);
      await new Promise((r) => setTimeout(r, 0)); // 화면이 갱신되도록 잠깐 양보
      let u = unpackSubmission(sub.code, answers.length);
      let useParts = answers.length > 0;
      if (answers.length && !String(sub.code).includes(PART_MARK)) { // 예전 형식
        if (tests.length) useParts = false; // 코드 문제는 코드 테스트만
        else {
          const lv = legacyVals(sub.code, answers);
          if (!lv) { // 칸을 나눌 수 없는 자유 서술 → 선생님 확인 대기로 표시 (틀림으로 처리하지 않아요)
            const judge = { status: 'MANUAL', passed: 0, total: 0, manual: answers.length };
            const { data, error } = await sb.from('submissions').update({ judge }).eq('id', sub.id).select('id');
            if (error || !data || !data.length) { if (statusEl) statusEl.innerHTML = `<div class="bad-t">⚠️ 채점 결과를 저장하지 못했어요. (${esc(error ? error.message : '권한 없음')})</div>`; return out; }
            sub.judge = judge; out.man = (out.man || 0) + 1; out.ok += 1;
            continue;
          }
          u = { code: '', vals: lv };
        }
      }
      let res = null;
      if (tests.length) {
        if (!u.code.trim()) res = { status: 'WA', passed: 0, total: tests.length, cases: [] };
        else {
          try { res = await gradeAll(u.code, tests); }
          catch (e) { if (statusEl) statusEl.innerHTML = `<span class="bad-t">⚠️ 파이썬 실행 도구를 불러오지 못했어요. 인터넷 연결을 확인하고 다시 눌러주세요. (${esc(e.message || e)})</span>`; return out; }
        }
      }
      const parts = useParts ? gradeParts(answers, u.vals) : null;
      const judge = summarize(res, parts);
      const { data, error } = await sb.from('submissions').update({ judge }).eq('id', sub.id).select('id');
      if (error || !data || !data.length) {
        if (statusEl) statusEl.innerHTML = `<div class="bad-t">⚠️ 채점 결과를 저장하지 못했어요. Supabase SQL Editor에서 아래를 한 번만 실행해 주세요.<pre><code>${esc(SQL_REGRADE)}</code></pre></div>`;
        return out;
      }
      sub.judge = judge;
      out.ok += 1;
      if (judge.status === 'AC') out.ac += 1; else if (judge.status === 'MANUAL') out.man += 1; else out.fail += 1;
    }
    return out;
  }

  // 일괄 채점 버튼 연결: sel = 버튼, getSubs = 대상 제출들, exMap
  function bindBulk(v, getSubs, exMap, names = {}) {
    const st = $('#bgStatus', v);
    lastBulk = '';
    v.querySelectorAll('[data-bulkgrade]').forEach((btn) => (btn.onclick = async () => {
      const force = btn.dataset.bulkgrade === 'all';
      if (force && !confirm('이미 채점된 제출까지 모두 다시 채점할까요?')) return;
      btn.disabled = true;
      document.querySelectorAll('[data-bulkgrade]').forEach((b) => { b.disabled = true; });
      const r = await bulkGrade(getSubs(), exMap, st, force, names);
      document.querySelectorAll('[data-bulkgrade]').forEach((b) => { b.disabled = false; });
      if (!r || !r.ok) return;
      lastBulk = pgHTML(r.total, r.total, `완료 · 통과 ${r.ac} · 미통과 ${r.fail}${r.man ? ` · 선생님 확인 대기 ${r.man}` : ''}`, true);
      toast(`채점 완료: ${r.ok}건 (통과 ${r.ac} · 미통과 ${r.fail}${r.man ? ` · 선생님 확인 대기 ${r.man}` : ''})`);
      route(true);
    }));
  }

  async function loadReviewData() {
    const [sr, subs, pr, exs] = await Promise.all([
      sb.from('problem_sets').select('id,title,short_name,week').order('week', { ascending: true, nullsFirst: false }).order('id'),
      fetchAll((a, b) => sb.from('submissions').select('id,set_id,user_id,exercise_id,created_at,judge,code').order('id').range(a, b)),
      sb.from('profiles').select('id,username'),
      fetchAll((a, b) => sb.from('exercises').select('id,set_id,tests,answers').order('id').range(a, b)),
    ]);
    if (sr.error) throw sr.error;
    if (pr.error) throw pr.error;
    const names = {};
    pr.data.forEach((p) => { names[p.id] = dname(p.id, p.username); });
    const setMap = {};
    sr.data.forEach((s, i) => { setMap[s.id] = { ...s, order: i }; });
    const exMap = {};
    exs.forEach((e) => { exMap[e.id] = e; });
    return { sets: sr.data, subs: subs.filter((s) => setMap[s.set_id]), names, setMap, exMap };
  }
  const pendingOf = (subs, exMap) => subs.filter((s) => !s.judge && gradable(exMap[s.exercise_id]));
  // 선생님이 직접 봐야 하는 제출: 서술형(채점 없음)이거나 자동 채점이 확인 대기로 남긴 것
  const waitingOf = (s, exMap) => {
    const j = s.judge;
    if (j && j.teacher) return false;
    if (!j) return !gradable(exMap[s.exercise_id]);
    return j.status === 'MANUAL' || j.manual > 0;
  };
  const waitBadge = (n) => (n ? ` <span class="badge wait">✍️ 확인 대기 ${n}</span>` : '');
  const pendBadge = (n) => (n ? ` <span class="badge warn">미채점 ${n}</span>` : '');
  const bulkBar = (n, label) => `<div class="card bulkbar"><div><b>${label}</b> <span class="muted small">테스트/자동 채점 답이 있는 문제만 채점해요. 서술형은 건너뛰어요.</span></div>
    <div class="form-actions"><button class="primary" data-bulkgrade="pending" ${n ? '' : 'disabled'}>⚖️ 미채점 ${n}건 일괄 채점</button><button class="ghost" data-bulkgrade="all" title="이미 채점된 것도 다시 채점해요">전체 다시 채점</button></div>
    <div id="bgStatus" class="small">${lastBulk}</div></div>`;

  async function pageReview(setId, userId) {
    if (!can('review')) return ['<div class="card pad center">선생님만 볼 수 있어요.</div>'];
    if (setId === 'u' && userId) return reviewStudent(userId);
    if (setId && userId) return reviewDetail(Number(setId), userId);

    const { subs, names, exMap } = await loadReviewData();
    const stu = {};
    subs.forEach((s) => {
      const g = stu[s.user_id] || (stu[s.user_id] = { id: s.user_id, sets: new Set(), ex: new Set(), n: 0, last: s.created_at, pend: 0 });
      g.sets.add(s.set_id); g.ex.add(s.exercise_id); g.n += 1;
      if (s.created_at > g.last) g.last = s.created_at;
      if (!s.judge && gradable(exMap[s.exercise_id])) g.pend += 1;
      if (waitingOf(s, exMap)) g.wait = (g.wait || 0) + 1;
    });
    const list = Object.values(stu).sort((a, b) => (names[a.id] || '').localeCompare(names[b.id] || ''));
    const pend = pendingOf(subs, exMap).length;
    const rows = list.length ? list.map((g) => `
      <a class="row" data-nm="${esc((names[g.id] || '').toLowerCase())}" href="#/review/u/${g.id}">
        <div class="row-main"><b>👤 ${esc(names[g.id] || '(알 수 없음)')}</b>${pendBadge(g.pend)}${waitBadge(g.wait)}
          <span class="muted small"> 문제집 ${g.sets.size}개 · 푼 문제 ${g.ex.size}개 · 제출 ${g.n}회</span></div>
        <div class="muted small meta">최근 ${fmt(g.last)}</div>
      </a>`).join('') : '<p class="muted center pad">아직 제출된 풀이가 없어요.</p>';
    return [`
      <div class="page-head"><h2>📥 제출함</h2><input type="search" id="rvQ" placeholder="학생 이름 검색" style="width:auto;min-width:160px"></div>
      <p class="muted">학생별로 모아 두었어요. 학생을 누르면 그 학생이 푼 문제집이 나와요. 이 목록은 선생님만 볼 수 있어요.</p>
      ${bulkBar(pend, '전체 학생')}
      <div class="card list" id="rvList">${rows}</div>`,
    (v) => {
      $('#rvQ', v).oninput = (e) => {
        const q = e.target.value.trim().toLowerCase();
        v.querySelectorAll('#rvList .row').forEach((r) => { r.style.display = q && !r.dataset.nm.includes(q) ? 'none' : ''; });
      };
      bindBulk(v, () => subs, exMap, names);
    }];
  }

  async function reviewStudent(userId) {
    const { sets, subs: all, names, setMap, exMap } = await loadReviewData();
    if (!names[userId]) return notFound();
    const subs = all.filter((s) => s.user_id === userId);
    const groups = {};
    subs.forEach((s) => {
      const g = groups[s.set_id] || (groups[s.set_id] = { set_id: s.set_id, ex: new Set(), n: 0, last: s.created_at, pend: 0, ac: 0, judged: 0 });
      g.ex.add(s.exercise_id); g.n += 1;
      if (s.created_at > g.last) g.last = s.created_at;
      if (!s.judge && gradable(exMap[s.exercise_id])) g.pend += 1;
      if (waitingOf(s, exMap)) g.wait = (g.wait || 0) + 1;
    });
    const list = Object.values(groups).sort((a, b) => setMap[a.set_id].order - setMap[b.set_id].order);
    const pend = pendingOf(subs, exMap).length;
    const rows = list.length ? list.map((g) => `
      <a class="row" href="#/review/${g.set_id}/${userId}">
        <div class="row-main"><b>📄 ${esc(shortOf(setMap[g.set_id]))}</b> <span class="muted small">${esc(setMap[g.set_id].title)}</span>${pendBadge(g.pend)}${waitBadge(g.wait)}
          <span class="muted small"> 푼 문제 ${g.ex.size}개 · 제출 ${g.n}회</span></div>
        <div class="muted small meta">최근 ${fmt(g.last)}</div>
      </a>`).join('') : '<p class="muted center pad">이 학생이 제출한 풀이가 없어요.</p>';
    return [`
      <p><a href="#/review">← 제출함</a></p>
      <div class="page-head"><h2>👤 ${esc(names[userId])}</h2></div>
      <p class="muted">푼 문제집 ${list.length}개 · 문제집을 누르면 푼 문제들이 나와요.</p>
      ${bulkBar(pend, `${esc(names[userId])} 학생`)}
      <div class="card list">${rows}</div>`,
    (v) => bindBulk(v, () => subs, exMap, names)];
  }

  async function reviewDetail(setId, userId) {
    const [sr, pr, exs, subs] = await Promise.all([
      sb.from('problem_sets').select('id,title,short_name').eq('id', setId).maybeSingle(),
      sb.from('profiles').select('id,username').eq('id', userId).maybeSingle(),
      fetchAll((a, b) => sb.from('exercises').select('*').eq('set_id', setId).order('position').order('id').range(a, b)),
      fetchAll((a, b) => sb.from('submissions')
        .select('*,submission_comments(id,content,created_at)')
        .eq('set_id', setId).eq('user_id', userId).order('id').range(a, b)),
    ]);
    if (sr.error) throw sr.error;
    if (!sr.data || !pr.data) return notFound();
    const L = layoutEx(exs);
    const subsBy = {};
    subs.forEach((s) => { (subsBy[s.exercise_id] = subsBy[s.exercise_id] || []).push(s); });
    const exMapD = {};
    exs.forEach((e) => { exMapD[e.id] = e; });
    const pendD = pendingOf(subs, exMapD).length;
    const title = `${dname(pr.data.id, pr.data.username)} - ${shortOf(sr.data)}`;
    const solved = L.normal.concat(L.elite).filter((e) => subsBy[e.id]);

    const item = (e) => {
      const vers = subsBy[e.id];
      const sel = vers.find((s) => s.id === reviewVer.get(e.id)) || vers[vers.length - 1];
      const tabs = vers.map((s) => `<button class="${s.id === sel.id ? 'on' : ''}" data-vt="${e.id}:${s.id}">v${s.version}${s.judge ? (s.judge.status === 'AC' ? ' ✅' : ' ❌') : ''}</button>`).join('');
      const panes = vers.map((s) => {
        const cs = (s.submission_comments || []).slice().sort((a, b) => a.created_at.localeCompare(b.created_at));
        return `<div class="vpane" data-vp="${e.id}:${s.id}" ${s.id === sel.id ? '' : 'hidden'}>
          <div class="muted small">v${s.version} · ${fmt(s.created_at)} ${judgeBadge(s.judge)} <button class="link danger" data-delsub="${s.id}">이 제출 삭제</button></div>
          <pre><code>${esc(s.code)}</code></pre>
          <div class="tverdict"><span class="muted small">👩‍🏫 선생님 판정</span>
            <button class="ghost sm okb" data-verdict="${s.id}:ok">✅ 맞음</button><button class="ghost sm badb" data-verdict="${s.id}:bad">❌ 틀림</button>
            ${s.judge ? `<button class="link" data-verdict="${s.id}:reset" title="판정·채점 결과를 지우고 미채점으로 돌려요">↩ 지우기</button>` : ''}</div>
          ${cs.map((c) => `<div class="tcomment"><span class="badge">선생님</span> <span class="muted small">${fmt(c.created_at)}</span> <button class="link danger" data-delcm="${c.id}">삭제</button><div class="txt">${esc(c.content)}</div></div>`).join('')}
          <form data-cform="${s.id}"><textarea style="min-height:70px" placeholder="이 풀이에 댓글 (학생이 볼 수 있어요)" required></textarea>
            <div class="form-actions"><button class="primary">댓글 달기</button></div></form>
        </div>`;
      }).join('');
      const nC = vers.reduce((n, s) => n + (s.submission_comments || []).length, 0);
      return `<details class="rv" data-rv="${e.id}" ${reviewOpen.has(e.id) ? 'open' : ''}>
        <summary><span class="ex-no sm">${dispNo(e)}</span> ${diffTag(e.difficulty)}
          <span class="rv-t">${esc(firstLine(e.body))}</span>
          ${judgeBadge(vers[vers.length - 1].judge)} <span class="muted small">v${vers[vers.length - 1].version} · ${fmt(vers[vers.length - 1].created_at)}${nC ? ` · 💬${nC}` : ''}</span></summary>
        <div class="rv-body">
          <details class="rv-prob"><summary>문제 보기</summary><div class="ex-body">${renderMarkup(e.body)}</div></details>
          ${vers.length > 1 ? `<div class="tabs vtabs">${tabs}</div>` : ''}
          ${panes}
        </div>
      </details>`;
    };

    return [`
      <p><a href="#/review/u/${userId}">← ${esc(dname(pr.data.id, pr.data.username))} 학생</a> · <a href="#/review">제출함</a></p>
      <div class="page-head"><h2>📄 ${esc(title)}</h2></div>
      <p class="muted">푼 문제 ${solved.length}개 · 문제를 누르면 풀이가 펼쳐져요.</p>
      ${bulkBar(pendD, '이 문제집')}
      <div class="card list rvlist">${solved.length ? solved.map(item).join('') : '<p class="muted center pad">제출한 문제가 없어요.</p>'}</div>`,
    (v) => {
      bindBulk(v, () => subs, exMapD);
      v.querySelectorAll('[data-rv]').forEach((d) => d.addEventListener('toggle', () => {
        const id = Number(d.dataset.rv);
        if (d.open) reviewOpen.add(id); else reviewOpen.delete(id);
      }));
      v.querySelectorAll('[data-vt]').forEach((b) => (b.onclick = () => {
        const [eid, sid] = b.dataset.vt.split(':').map(Number);
        reviewVer.set(eid, sid);
        v.querySelectorAll(`[data-vt^="${eid}:"]`).forEach((x) => x.classList.toggle('on', x === b));
        v.querySelectorAll(`[data-vp^="${eid}:"]`).forEach((x) => { x.hidden = x.dataset.vp !== b.dataset.vt; });
      }));
      v.querySelectorAll('[data-cform]').forEach((f) => (f.onsubmit = async (e) => {
        e.preventDefault();
        const text = $('textarea', f).value.trim();
        if (!text) return;
        const btn = $('button', f);
        btn.disabled = true;
        const { error } = await sb.from('submission_comments').insert({ submission_id: Number(f.dataset.cform), author_id: me.id, content: text });
        if (error) { btn.disabled = false; return toast('댓글을 달지 못했어요', true); }
        toast('댓글을 달았어요');
        route(true);
      }));
      v.querySelectorAll('[data-verdict]').forEach((b) => (b.onclick = async () => {
        const [sid, kind] = b.dataset.verdict.split(':');
        const sub = subs.find((x) => String(x.id) === sid);
        if (!sub) return;
        const base = sub.judge || { passed: 0, total: 0, manual: 0 };
        let judge = null;
        if (kind === 'ok') judge = { status: 'AC', passed: base.total > 0 ? base.total : 1, total: base.total > 0 ? base.total : 1, manual: 0, teacher: 'ok' };
        else if (kind === 'bad') { const t = base.total > 0 ? base.total : 1; judge = { status: 'WA', passed: Math.min(base.passed || 0, t - 1), total: t, manual: 0, teacher: 'bad' }; }
        b.disabled = true;
        const { data, error } = await sb.from('submissions').update({ judge }).eq('id', sub.id).select('id');
        if (error || !data || !data.length) { b.disabled = false; return toast('저장하지 못했어요 (관리자 권한 SQL 확인)', true); }
        toast(kind === 'ok' ? '맞음으로 판정했어요' : kind === 'bad' ? '틀림으로 판정했어요' : '판정을 지웠어요');
        route(true);
      }));
      v.querySelectorAll('[data-delcm]').forEach((b) => (b.onclick = async () => {
        if (!confirm('댓글을 삭제할까요?')) return;
        const { error } = await sb.from('submission_comments').delete().eq('id', Number(b.dataset.delcm));
        if (error) return toast('삭제하지 못했어요', true);
        route(true);
      }));
      v.querySelectorAll('[data-delsub]').forEach((b) => (b.onclick = async () => {
        if (!confirm('이 제출(버전)을 삭제할까요? 학생에게서도 사라져요.')) return;
        const { error } = await sb.from('submissions').delete().eq('id', Number(b.dataset.delsub));
        if (error) return toast('삭제하지 못했어요', true);
        route(true);
      }));
    }];
  }

  /* ====================================================================
     📚 학습 (V4.1.0) — 설명 → O/X·확인 문제 → 실습, 단계별로 진행
     JSON 형식: pynest-learn-v1 (LEARN_JSON_GUIDE.md)
     ==================================================================== */
  let LEARN_OK = null;
  const LEARN_KINDS = ['ox', 'choice', 'short', 'fill'];
  const XP_EXPLAIN = 1;
  const XP_QUIZ = 10;
  const XP_PRACTICE = 30;
  const learnTxt = (x) => String(x ?? '').replace(/\r/g, '');
  const KST_DAY = (t = Date.now()) => new Date(t + 9 * 3600e3).toISOString().slice(0, 10);
  const lrNorm = (s) => String(s ?? '').trim().replace(/\s+/g, ' ').toLowerCase();
  function streakOf(days) {
    let n = 0;
    let t = Date.now();
    if (!days.has(KST_DAY(t))) t -= 86400e3; // 오늘 아직 안 했으면 어제부터 세요
    while (days.has(KST_DAY(t))) { n += 1; t -= 86400e3; }
    return n;
  }

  /* ----- JSON 읽기 ----- */
  function normLearnStep(s, at) {
    const bad = (m) => { throw new Error(`${at}: ${m}`); };
    if (!s || typeof s !== 'object') bad('단계가 객체({ })가 아니에요');
    let type = String(s.type || '').toLowerCase();
    let kind = String(s.kind || '').toLowerCase();
    if (LEARN_KINDS.includes(type)) { kind = type; type = 'quiz'; } // {"type":"ox"} 처럼 줄여 써도 돼요
    if (['code', 'text', 'concept', 'md'].includes(type)) type = 'explain';
    if (type === 'exercise' || type === 'problem') type = 'practice';
    const title = String(s.title || '');
    if (type === 'explain') {
      const body = learnTxt(s.body ?? s.text ?? '').trim();
      const code = s.code == null ? '' : learnTxt(s.code).replace(/\s+$/, '');
      if (!body && !code) bad('explain 에는 body(설명) 가 필요해요');
      return { type, title, body, code, run: s.run !== false };
    }
    if (type === 'quiz') {
      const question = learnTxt(s.question ?? s.body ?? '').trim();
      if (!question && kind !== 'fill') bad('quiz 에는 question 이 필요해요');
      const out = { type, kind, title, question, explanation: learnTxt(s.explanation ?? '').trim() };
      if (kind === 'ox') {
        const a = s.answer;
        const t = typeof a === 'string' ? ['o', 'true', '참', '맞다', '맞음', 'yes'].includes(a.trim().toLowerCase()) : !!a;
        if (typeof a === 'string' && !['o', 'x', 'true', 'false', '참', '거짓', '맞다', '틀리다', '맞음', '틀림', 'yes', 'no'].includes(a.trim().toLowerCase())) bad('ox 의 answer 는 true/false (또는 "O"/"X") 로 써요');
        if (a === undefined || a === null) bad('ox 에는 answer(true/false) 가 필요해요');
        out.answer = t;
      } else if (kind === 'choice') {
        const opts = (Array.isArray(s.options) ? s.options : []).map((x) => String(x));
        if (opts.length < 2 || opts.length > 8) bad('choice 의 options 는 2~8개여야 해요');
        const arr = (Array.isArray(s.answer) ? s.answer : [s.answer]).map(Number);
        if (!arr.length || arr.some((n) => !Number.isInteger(n) || n < 1 || n > opts.length)) bad(`choice 의 answer 는 1~${opts.length} 번호예요 (여러 개면 [1,3])`);
        out.options = opts;
        out.answer = [...new Set(arr)].sort((a, b) => a - b);
      } else if (kind === 'short') {
        const a = String(s.answer ?? '').trim();
        if (!a) bad('short 에는 answer(정답 글자) 가 필요해요');
        out.answer = a;
        out.alts = (Array.isArray(s.alts) ? s.alts : []).map(String).filter((x) => x.trim());
      } else if (kind === 'fill') {
        const code = learnTxt(s.code ?? s.question ?? '').replace(/\s+$/, '');
        const n = code.split('___').length - 1;
        if (!n) bad('fill 의 code 에는 빈칸 ___ 이 하나 이상 있어야 해요');
        const ans = (Array.isArray(s.answers) ? s.answers : [s.answer]).map((x) => (Array.isArray(x) ? x : [x]).map(String).filter((y) => y.trim() !== ''));
        if (ans.length !== n || ans.some((x) => !x.length)) bad(`fill 의 answers 는 빈칸 개수(${n}개)만큼 필요해요 (칸마다 정답 하나, 또는 ["정답","다른정답"])`);
        out.code = code;
        out.answers = ans;
      } else bad('quiz 의 kind 는 ox / choice / short / fill 중 하나예요');
      return out;
    }
    if (type === 'practice') {
      const body = learnTxt(s.body ?? s.question ?? '').trim();
      if (!body) bad('practice 에는 body(문제 내용) 가 필요해요');
      return {
        type, title, body, starter: learnTxt(s.starter ?? '').replace(/\s+$/, ''), tests: normTests(s.tests),
        hints: (Array.isArray(s.hints) ? s.hints : []).map((h) => learnTxt(h).trim()).filter(Boolean),
        solution: learnTxt(s.solution ?? '').replace(/\s+$/, ''), explanation: learnTxt(s.explanation ?? '').trim(),
        stdin: learnTxt(s.stdin ?? ''),
      };
    }
    return bad('type 은 explain / quiz / practice 중 하나예요');
  }
  function normLearnLesson(l, i) {
    const at = `${i + 1}번째 레슨`;
    if (!l || typeof l !== 'object') throw new Error(`${at}이 객체가 아니에요`);
    const title = String(l.title || '').trim();
    if (!title) throw new Error(`${at}에 title 이 필요해요`);
    if (!Array.isArray(l.steps) || !l.steps.length) throw new Error(`${at}("${title}")에 steps 가 하나도 없어요`);
    if (l.steps.length > 80) throw new Error(`${at}("${title}")의 단계가 너무 많아요 (80개 이하)`);
    const m = Number(l.minutes);
    const rp = l.rank_points === undefined || l.rank_points === null || l.rank_points === '' ? null : Number(l.rank_points);
    if (rp !== null && (!Number.isInteger(rp) || rp < 0 || rp > 100000)) throw new Error(`${at}("${title}")의 rank_points 는 0 이상의 정수예요`);
    return {
      title, rank_points: rp, summary: learnTxt(l.summary ?? '').trim(), minutes: Number.isFinite(m) && m > 0 ? Math.round(m) : null,
      steps: l.steps.map((s, k) => normLearnStep(s, `"${title}" ${k + 1}번째 단계`)),
    };
  }
  function parseLearnJson(text) {
    let d;
    try { d = JSON.parse(text); } catch (e) { throw new Error('JSON 형식 오류예요 (쉼표·따옴표를 확인해 보세요)'); }
    if (!d || typeof d !== 'object') throw new Error('올바른 학습 파일이 아니에요');
    if (d.format && d.format !== 'pynest-learn-v1') throw new Error('지원하지 않는 형식이에요: ' + d.format);
    const lessons = (Array.isArray(d.lessons) ? d.lessons : d.title && d.steps ? [d] : []).map(normLearnLesson);
    if (!lessons.length) throw new Error('레슨(lessons)이 하나도 없어요');
    const c = d.course && typeof d.course === 'object' ? d.course : null;
    return {
      course: c ? { title: String(c.title || '').trim(), description: learnTxt(c.description ?? '').trim(), sequential: c.sequential !== false, rank_points: Math.max(0, Math.min(100000, Math.round(Number(c.rank_points) || 0))) } : null,
      lessons, nSteps: lessons.reduce((n, l) => n + l.steps.length, 0),
    };
  }
  function exportLearn(course, lessons) {
    const out = {
      format: 'pynest-learn-v1',
      course: { title: course.title, description: course.description || '', sequential: course.sequential !== false, rank_points: course.rank_points || 0 },
      lessons: lessons.map((l) => ({ title: l.title, minutes: l.minutes || undefined, rank_points: l.rank_points == null ? undefined : l.rank_points, summary: l.summary || '', steps: l.steps })),
    };
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([JSON.stringify(out, null, 1)], { type: 'application/json' }));
    a.download = `learn-${course.title.replace(/[^\w가-힣-]+/g, '_').slice(0, 40) || 'course'}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  }

  /* ----- 공통 조각 ----- */
  const lrPts = (lesson, course) => (lesson && lesson.rank_points != null ? lesson.rank_points : (course && course.rank_points) || 0);
  const lrPtsChip = (n) => (n > 0 ? `<span class="chip pts" title="이 레슨을 끝내면 랭킹·티어 점수가 올라요">🏆 +${n}점</span>` : '');
  // rank_points 칸이 아직 없는 DB(v420 전)면 그 칸만 빼고 다시 시도해요
  async function lrWrite(make) {
    let r = await make(false);
    let dropped = false;
    if (r.error && /rank_points/.test(r.error.message || '')) { r = await make(true); dropped = !r.error; }
    if (dropped && !lrWrite.warned) { lrWrite.warned = true; toast('랭킹 점수 칸은 v420_learn_points.sql 을 실행한 뒤에 저장돼요', true); }
    return r;
  }
  const learnMissing = () => [`<div class="card pad center"><h2>📚 학습</h2><p class="muted">${can('content') ? '먼저 <b>v410_learn.sql</b> 을 Supabase SQL Editor 에서 한 번 실행해 주세요.' : '학습 기능을 준비하고 있어요. 조금만 기다려 주세요!'}</p></div>`];
  const lrMd = (t) => renderContent(t, true);
  const learnAddXp = (n) => { if (n > 0) { try { Promise.resolve(sb.rpc('learn_add_xp', { p_xp: n })).catch(() => {}); } catch (e) { /* 무시 */ } } };
  const codeKey = (lid, i) => `pn_lc_${me.id.slice(0, 8)}_${lid}_${i}`;
  const lrSave = (k, v) => { try { sessionStorage.setItem(k, v); } catch (e) { /* 무시 */ } try { localStorage.setItem('pn_lr_' + k, v); } catch (e) { /* 무시 */ } };
  const lrLoad = (k) => { let v = null; try { v = sessionStorage.getItem(k); } catch (e) { /* 무시 */ } if (v == null) { try { v = localStorage.getItem('pn_lr_' + k); } catch (e) { /* 무시 */ } } return v; };

  // 실행해 볼 수 있는 코드 칸 (설명 단계용·실습용 공통). opts: {key, rows, stdin}
  function lrCodeBox(root, initial, opts = {}) {
    const ta = $('textarea.lr-code', root);
    ta.value = initial;
    if (window.PYIDE) window.PYIDE.attach(ta);
    const out = $('.lr-out', root);
    const run = $('[data-lrrun]', root);
    const stdin = $('.lr-stdin', root);
    if (opts.key) ta.addEventListener('input', () => lrSave(opts.key, ta.value));
    if (run) run.onclick = async () => {
      if (!ta.value.trim()) return toast('코드를 입력하세요', true);
      run.disabled = true;
      out.hidden = false;
      out.innerHTML = '<span class="muted">⏳ 파이썬을 준비하는 중… (처음 한 번은 몇 초 걸려요)</span>';
      const r = await runOnce(ta.value, (stdin ? stdin.value : '').replace(/\n?$/, '\n'));
      out.innerHTML = renderRun(r);
      run.disabled = false;
    };
    const reset = $('[data-lrreset]', root);
    if (reset) reset.onclick = () => { ta.value = initial; ta.dispatchEvent(new Event('input', { bubbles: true })); };
    return ta;
  }
  const lrCodeBoxHtml = (rows, { stdin = false, reset = true } = {}) => `<textarea class="code lr-code" rows="${rows}" spellcheck="false"></textarea>
    ${stdin ? '<details class="stdin-box"><summary>⌨️ 입력값 <span class="muted small">(input() 에 들어갈 값 · 한 줄에 하나씩)</span></summary><textarea class="lr-stdin" rows="2" spellcheck="false"></textarea></details>' : ''}
    <div class="lr-btns"><button class="ghost" type="button" data-lrrun>▶ 실행해 보기</button>${reset ? '<button class="ghost" type="button" data-lrreset>↺ 처음 코드로</button>' : ''}</div><div class="lr-out judge-out" hidden></div>`;

  /* ----- 확인 문제 (O/X · 객관식 · 단답 · 빈칸) — 학습 화면과 오답 복습이 같이 써요 ----- */
  const quizAnswerText = (st) => {
    if (st.kind === 'ox') return st.answer ? 'O (맞아요)' : 'X (틀려요)';
    if (st.kind === 'choice') return st.answer.map((n) => `${n}. ${st.options[n - 1]}`).join(' / ');
    if (st.kind === 'short') return st.answer;
    return st.answers.map((a) => a[0]).join(' , ');
  };
  function quizHtml(st) {
    let inner = '';
    if (st.kind === 'ox') {
      inner = '<div class="lr-ox"><button type="button" class="lr-o" data-ox="1">⭕<span>맞아요</span></button><button type="button" class="lr-x" data-ox="0">❌<span>틀려요</span></button></div>';
    } else if (st.kind === 'choice') {
      const multi = st.answer.length > 1;
      inner = `${multi ? '<p class="muted small">정답이 여러 개예요. 모두 골라요.</p>' : ''}<div class="lr-opts">${st.options.map((o, i) => `<label class="lr-opt"><input type="${multi ? 'checkbox' : 'radio'}" name="lrc" value="${i + 1}"><span class="lr-no">${i + 1}</span><span>${mdInline(o)}</span></label>`).join('')}</div><div class="form-actions"><button class="primary" type="button" data-qcheck>정답 확인</button></div>`;
    } else if (st.kind === 'short') {
      inner = '<input class="lr-short" type="text" autocomplete="off" spellcheck="false" placeholder="정답을 입력하세요"><div class="form-actions"><button class="primary" type="button" data-qcheck>정답 확인</button></div>';
    } else {
      const parts = st.code.split('___');
      inner = `<pre class="lr-fill"><code>${parts.map((p, i) => esc(p) + (i < parts.length - 1 ? '<input class="lr-blank" type="text" autocomplete="off" spellcheck="false" size="6" aria-label="빈칸 ' + (i + 1) + '">' : '')).join('')}</code></pre><div class="form-actions"><button class="primary" type="button" data-qcheck>정답 확인</button></div>`;
    }
    return `${st.question ? `<div class="lr-q">${lrMd(st.question)}</div>` : ''}${inner}<div class="lr-fb" hidden></div>`;
  }
  // cb.onWrong() : 틀릴 때마다 / cb.onDone({tries, peek}) : 맞히거나 정답을 열어 보았을 때
  function mountQuiz(root, st, cb) {
    root.innerHTML = quizHtml(st);
    const fb = $('.lr-fb', root);
    let tries = 0;
    let over = false;
    const lock = () => { root.querySelectorAll('input,button[data-ox],[data-qcheck]').forEach((e) => { e.disabled = true; }); };
    const finish = (peek) => { over = true; lock(); cb.onDone({ tries, peek }); };
    const showFb = (ok, peek) => {
      fb.hidden = false;
      fb.className = 'lr-fb ' + (ok ? 'ok' : 'bad');
      const ex = st.explanation ? `<div class="lr-ex">${lrMd(st.explanation)}</div>` : '';
      if (ok) fb.innerHTML = `<b>${tries === 1 ? '🎉 정답이에요!' : '✅ 정답이에요!'}</b>${ex}`;
      else if (peek) fb.innerHTML = `<b>💡 정답은</b> <code class="ic">${esc(quizAnswerText(st))}</code>${ex}`;
      else fb.innerHTML = `<b>${tries >= 2 ? '🤔 아직이에요. 설명을 다시 읽고 도전해 보세요!' : '😅 아쉬워요, 다시 해 볼까요?'}</b>${tries >= 2 ? '<div class="form-actions"><button class="ghost" type="button" data-peek>정답 보기</button></div>' : ''}`;
      const pk = $('[data-peek]', fb);
      if (pk) pk.onclick = () => { showFb(false, true); finish(true); };
    };
    const judge = (ok) => {
      if (over) return;
      tries += 1;
      if (ok) { showFb(true); finish(false); } else { cb.onWrong(); showFb(false, false); }
    };
    root.querySelectorAll('[data-ox]').forEach((b) => (b.onclick = () => judge((b.dataset.ox === '1') === st.answer)));
    const chk = $('[data-qcheck]', root);
    if (chk) chk.onclick = () => {
      if (st.kind === 'choice') {
        const picked = [...root.querySelectorAll('input[name="lrc"]:checked')].map((x) => Number(x.value)).sort((a, b) => a - b);
        if (!picked.length) return toast('먼저 하나를 골라 보세요', true);
        judge(picked.length === st.answer.length && picked.every((v, i) => v === st.answer[i]));
      } else if (st.kind === 'short') {
        const v = lrNorm($('.lr-short', root).value);
        if (!v) return toast('정답을 입력해 보세요', true);
        judge([st.answer, ...(st.alts || [])].some((a) => lrNorm(a) === v));
      } else {
        const vals = [...root.querySelectorAll('.lr-blank')].map((x) => lrNorm(x.value));
        if (vals.some((x) => !x)) return toast('모든 빈칸을 채워 보세요', true);
        judge(st.answers.every((alts, i) => alts.some((a) => lrNorm(a) === vals[i])));
      }
    };
    root.querySelectorAll('.lr-short,.lr-blank').forEach((inp) => inp.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); if (chk) chk.click(); } }));
    const first = $('.lr-short,.lr-blank', root);
    if (first) first.focus();
  }
  // 이미 푼 확인문제를 다시 볼 때
  const quizSolvedHtml = (st) => `${st.question ? `<div class="lr-q">${lrMd(st.question)}</div>` : ''}${st.kind === 'fill' ? `<pre class="lr-fill"><code>${esc(st.code)}</code></pre>` : ''}
    <div class="lr-fb ok"><b>✅ 이미 푼 문제예요</b><div>정답: <code class="ic">${esc(quizAnswerText(st))}</code></div>${st.explanation ? `<div class="lr-ex">${lrMd(st.explanation)}</div>` : ''}</div>`;

  /* ----- 학습 홈 ----- */
  async function pageLearn(b, c) {
    if (b === 'c') return pageLearnCourse(c);
    if (b === 'l') return pageLearnLesson(c);
    if (b === 'r') return pageLearnReview();
    return pageLearnHome();
  }
  const wrongList = (p) => (p && Array.isArray(p.wrong) ? p.wrong : []);

  async function pageLearnHome() {
    const staff = can('content');
    const cr = await sb.from('learn_courses').select('*').order('position').order('id');
    if (cr.error) { LEARN_OK = false; return learnMissing(); }
    LEARN_OK = true;
    const [lr, pr, dr] = await Promise.all([
      sb.from('learn_lessons').select('id,course_id,position,title,is_public,minutes').order('position').order('id'),
      sb.from('learn_progress').select('lesson_id,cur,wrong,xp,completed,updated_at').eq('user_id', me.id),
      sb.from('learn_days').select('day,xp').eq('user_id', me.id),
    ]);
    const lessons = lr.data || [];
    const prog = new Map((pr.data || []).map((p) => [p.lesson_id, p]));
    const days = dr.data || [];
    const totalXp = days.reduce((s, d) => s + d.xp, 0);
    const today = (days.find((d) => d.day === KST_DAY()) || { xp: 0 }).xp;
    const streak = streakOf(new Set(days.map((d) => d.day)));
    const nDone = [...prog.values()].filter((p) => p.completed).length;
    const nWrong = [...prog.values()].reduce((s, p) => s + wrongList(p).length, 0);
    const byC = {};
    lessons.forEach((l) => { (byC[l.course_id] = byC[l.course_id] || []).push(l); });

    // 이어서 하기: 가장 최근에 하던 레슨 → 없으면 첫 코스의 다음 레슨
    let resume = null;
    const going = lessons.filter((l) => { const p = prog.get(l.id); return p && !p.completed && p.updated_at; }).sort((a, b) => String(prog.get(b.id).updated_at).localeCompare(String(prog.get(a.id).updated_at)));
    if (going.length) resume = going[0];
    else {
      for (const c of cr.data) {
        const ls = byC[c.id] || [];
        const nx = ls.find((l) => !(prog.get(l.id) || {}).completed);
        if (nx) { resume = nx; break; }
      }
    }
    const resumeCourse = resume ? cr.data.find((c) => c.id === resume.course_id) : null;

    const cards = cr.data.map((c) => {
      const ls = byC[c.id] || [];
      const done = ls.filter((l) => (prog.get(l.id) || {}).completed).length;
      const pct = ls.length ? Math.round((done / ls.length) * 100) : 0;
      return `<a class="card lr-course" href="#/learn/c/${c.id}">
        <div class="set-top"><h3>${esc(c.title)}</h3>${staff ? pubChip(c.is_public) : ''}${pct === 100 && ls.length ? '<span class="chip">🏅 완료</span>' : ''}${lrPtsChip(c.rank_points || 0)}</div>
        ${c.description ? `<p class="muted small">${esc(c.description)}</p>` : ''}
        <div class="muted small">레슨 ${ls.length}개 · 완료 ${done}개</div>
        <div class="bar"><i style="width:${pct}%"></i></div></a>`;
    }).join('') || `<div class="card pad center muted">${staff ? '아직 코스가 없어요. [＋ JSON으로 코스 추가] 로 만들어 보세요.' : '아직 열린 학습 코스가 없어요.'}</div>`;

    return [`
      <div class="page-head"><h2>📚 학습</h2></div>
      <div class="lr-stats">
        <div class="card lr-stat"><b>🔥 ${streak}일</b><span class="muted small">연속 학습</span></div>
        <div class="card lr-stat"><b>⭐ ${totalXp} XP</b><span class="muted small">오늘 +${today}</span></div>
        <div class="card lr-stat"><b>✅ ${nDone}개</b><span class="muted small">완료한 레슨</span></div>
      </div>
      ${resume && resumeCourse ? `<a class="card lr-resume" href="#/learn/l/${resume.id}"><span class="muted small">${(prog.get(resume.id) || {}).updated_at ? '이어서 학습하기' : '학습 시작하기'}</span><b>${esc(resume.title)}</b><span class="muted small">${esc(resumeCourse.title)}</span><span class="lr-go">▶</span></a>` : ''}
      ${nWrong ? `<a class="card lr-review" href="#/learn/r">🔁 <b>오답 복습</b> <span class="muted small">— 틀렸던 확인 문제 ${nWrong}개를 다시 풀어 봐요</span></a>` : ''}
      ${staff ? '<div class="form-actions" style="margin:0 0 12px"><button class="ghost" id="lrAddCourse">＋ JSON으로 코스 추가</button><a class="ghost btnlike" href="LEARN_JSON_GUIDE.md" target="_blank" rel="noopener">📖 JSON 형식 안내</a></div>' : ''}
      <div class="lr-courses">${cards}</div>`,
    (v) => { const b = $('#lrAddCourse', v); if (b) b.onclick = () => openLearnAdd(null); }];
  }

  /* ----- 코스 화면 (로드맵) ----- */
  async function pageLearnCourse(rawId) {
    const id = Number(rawId);
    const staff = can('content');
    const cr = await sb.from('learn_courses').select('*').eq('id', id).maybeSingle();
    if (cr.error) return learnMissing();
    const course = cr.data;
    if (!course) return notFound();
    const [lr, pr, sr] = await Promise.all([
      sb.from('learn_lessons').select('*').eq('course_id', id).order('position').order('id'),
      sb.from('learn_progress').select('lesson_id,cur,done,xp,completed').eq('user_id', me.id),
      staff ? sb.from('learn_progress').select('lesson_id,completed') : Promise.resolve({ data: [] }),
    ]);
    const lessons = lr.data || [];
    const prog = new Map((pr.data || []).map((p) => [p.lesson_id, p]));
    const stat = {};
    (sr.data || []).forEach((p) => { const s = (stat[p.lesson_id] = stat[p.lesson_id] || { started: 0, done: 0 }); s.started += 1; if (p.completed) s.done += 1; });
    const seq = course.sequential !== false && !staff;
    const doneN = lessons.filter((l) => (prog.get(l.id) || {}).completed).length;
    const rows = lessons.map((l, i) => {
      const p = prog.get(l.id);
      const prevOk = i === 0 || (prog.get(lessons[i - 1].id) || {}).completed;
      const locked = seq && !prevOk;
      const nd = p ? Object.keys(p.done || {}).length : 0;
      const st = p && p.completed ? '<span class="chip done">✅ 완료</span>' : locked ? '<span class="chip">🔒 앞 레슨을 먼저 끝내요</span>' : nd ? `<span class="chip">▶ ${nd} / ${l.steps.length} 단계</span>` : '<span class="chip">시작 전</span>';
      const sx = stat[l.id];
      return `<div class="lr-node ${p && p.completed ? 'done' : ''} ${locked ? 'locked' : ''}">
        <div class="lr-circle">${p && p.completed ? '✓' : i + 1}</div>
        <div class="lr-node-main">
          ${locked ? `<b>${esc(l.title)}</b>` : `<a href="#/learn/l/${l.id}"><b>${esc(l.title)}</b></a>`}
          <div class="muted small">${l.steps.length}단계${l.minutes ? ` · 약 ${l.minutes}분` : ''} ${l.rank_points != null && l.rank_points !== course.rank_points ? lrPtsChip(l.rank_points) : ''} ${staff ? pubChip(l.is_public) : ''}${staff && sx ? ` · 시작 ${sx.started}명 · 완료 ${sx.done}명` : ''}</div>
          ${st}
        </div>
        ${staff ? `<span class="tools"><button class="icon" data-lup="${l.id}" title="위로">↑</button><button class="icon" data-ldown="${l.id}" title="아래로">↓</button><button class="icon" data-lpub="${l.id}" title="공개/비공개">${l.is_public ? '🌐' : '🔒'}</button><button class="icon" data-ledit="${l.id}" title="JSON 으로 수정">✏️</button><button class="icon" data-ldel="${l.id}" title="삭제">🗑</button></span>` : ''}
      </div>`;
    }).join('') || '<p class="muted center pad">레슨이 아직 없어요.</p>';

    return [`
      <p><a href="#/learn">← 학습</a></p>
      <div class="page-head"><h2>${esc(course.title)} ${staff ? pubChip(course.is_public) : ''}</h2></div>
      ${course.description ? `<p class="muted">${esc(course.description)}</p>` : ''}
      <div class="muted small" style="margin-bottom:6px">레슨 ${lessons.length}개 · 완료 ${doneN}개${course.sequential !== false ? ' · 순서대로 열려요' : ''} ${course.rank_points > 0 ? `· <span class="chip pts">🏆 레슨 1개 완료마다 랭킹 +${course.rank_points}점</span>` : ''}</div>
      <div class="bar" style="margin-bottom:14px"><i style="width:${lessons.length ? Math.round((doneN / lessons.length) * 100) : 0}%"></i></div>
      ${staff ? `<div class="form-actions" style="margin:0 0 12px"><button class="ghost" id="lcPub">${course.is_public ? '🔒 비공개로 바꾸기' : '🌐 공개하기'}</button><button class="ghost" id="lcEdit">✏️ 코스 정보</button><button class="ghost" id="lcAdd">＋ JSON으로 레슨 추가</button><button class="ghost" id="lcExp">⬇️ JSON 내보내기</button><button class="ghost" id="lcDel">🗑 코스 삭제</button></div>` : ''}
      <div class="card lr-road">${rows}</div>`,
    (v) => {
      if (!staff) return;
      const L = (i) => lessons.find((x) => x.id === Number(i));
      $('#lcPub', v).onclick = async () => {
        const { error } = await sb.from('learn_courses').update({ is_public: !course.is_public }).eq('id', id);
        if (error) return toast('바꾸지 못했어요', true);
        toast(course.is_public ? '비공개로 바꿨어요 🔒' : '공개했어요 🌐'); route(true);
      };
      $('#lcEdit', v).onclick = () => openCourseEdit(course);
      $('#lcAdd', v).onclick = () => openLearnAdd(course, lessons);
      $('#lcExp', v).onclick = () => exportLearn(course, lessons);
      $('#lcDel', v).onclick = async () => {
        if (!confirm(`"${course.title}" 코스를 삭제할까요?\n레슨과 학생 진도도 함께 삭제돼요.`)) return;
        const { error } = await sb.from('learn_courses').delete().eq('id', id);
        if (error) return toast('삭제하지 못했어요', true);
        toast('삭제했어요'); location.hash = '#/learn';
      };
      const swap = async (lid, dir) => {
        const i = lessons.findIndex((x) => x.id === Number(lid));
        const o = lessons[i + dir];
        if (i < 0 || !o) return;
        const e = lessons[i];
        const [r1, r2] = await Promise.all([
          sb.from('learn_lessons').update({ position: o.position }).eq('id', e.id),
          sb.from('learn_lessons').update({ position: e.position }).eq('id', o.id),
        ]);
        if (r1.error || r2.error) return toast('순서를 바꾸지 못했어요', true);
        route(true);
      };
      v.querySelectorAll('[data-lup]').forEach((b) => (b.onclick = () => swap(b.dataset.lup, -1)));
      v.querySelectorAll('[data-ldown]').forEach((b) => (b.onclick = () => swap(b.dataset.ldown, 1)));
      v.querySelectorAll('[data-lpub]').forEach((b) => (b.onclick = async () => {
        const l = L(b.dataset.lpub);
        const { error } = await sb.from('learn_lessons').update({ is_public: !l.is_public }).eq('id', l.id);
        if (error) return toast('바꾸지 못했어요', true);
        route(true);
      }));
      v.querySelectorAll('[data-ledit]').forEach((b) => (b.onclick = () => openLessonEdit(L(b.dataset.ledit))));
      v.querySelectorAll('[data-ldel]').forEach((b) => (b.onclick = async () => {
        const l = L(b.dataset.ldel);
        if (!confirm(`"${l.title}" 레슨을 삭제할까요? (학생 진도도 같이 삭제돼요)`)) return;
        const { error } = await sb.from('learn_lessons').delete().eq('id', l.id);
        if (error) return toast('삭제하지 못했어요', true);
        route(true);
      }));
    }];
  }

  /* ----- 선생님: JSON 으로 코스·레슨 추가 / 수정 ----- */
  function openLearnAdd(course, existing) {
    let parsed = null;
    const m = modal(`<h3>${course ? `＋ "${esc(course.title)}" 에 레슨 추가` : '＋ JSON으로 코스 추가'}</h3>
      <p class="muted small">형식은 <b>pynest-learn-v1</b> 이에요 (LEARN_JSON_GUIDE.md). ${course ? '<code class="ic">lessons</code> 의 레슨들이 이 코스 <b>맨 뒤</b>에 붙어요.' : '<code class="ic">course</code> 와 <code class="ic">lessons</code> 가 필요해요.'}</p>
      <label>JSON 붙여넣기<textarea id="laText" class="code" style="min-height:220px" spellcheck="false" placeholder='{ "format": "pynest-learn-v1", "course": { "title": "파이썬 첫걸음" }, "lessons": [ { "title": "print 배우기", "steps": [ { "type": "explain", "body": "..." } ] } ] }'></textarea></label>
      <label>또는 파일 선택 <input type="file" id="laFile" accept=".json,application/json"></label>
      <p class="muted small" id="laInfo"></p>
      ${pubPickHtml('laPub')}
      <div class="form-actions"><button class="primary" id="laBtn" disabled>추가하기</button><button type="button" class="ghost" id="laCancel">취소</button></div>`);
    const q = (x) => $(x, m.el);
    const check = () => {
      parsed = null;
      q('#laBtn').disabled = true;
      const t = q('#laText').value.trim();
      if (!t) { q('#laInfo').textContent = ''; return; }
      try {
        parsed = parseLearnJson(t);
        if (!course && !(parsed.course && parsed.course.title)) { parsed = null; throw new Error('새 코스에는 course.title 이 필요해요'); }
        q('#laInfo').textContent = `✅ ${parsed.course && !course ? `코스 "${parsed.course.title}" · ` : ''}레슨 ${parsed.lessons.length}개 · 단계 ${parsed.nSteps}개를 읽었어요.`;
        q('#laBtn').disabled = false;
      } catch (err) { q('#laInfo').textContent = '⚠️ ' + err.message; }
    };
    q('#laText').oninput = check;
    q('#laFile').onchange = async (e) => { const f = e.target.files[0]; if (f) { q('#laText').value = await f.text(); check(); } };
    q('#laCancel').onclick = m.close;
    q('#laBtn').onclick = async () => {
      if (!parsed) return;
      const btn = q('#laBtn');
      btn.disabled = true;
      const pub = (m.el.querySelector('input[name="laPub"]:checked') || { value: '0' }).value === '1';
      let cid = course ? course.id : null;
      if (!course) {
        const { data: mx } = await sb.from('learn_courses').select('position').order('position', { ascending: false }).limit(1);
        const r = await lrWrite((drop) => sb.from('learn_courses').insert({
          title: parsed.course.title, description: parsed.course.description, sequential: parsed.course.sequential,
          is_public: pub, position: ((mx && mx[0] && mx[0].position) || 0) + 1000,
          ...(drop ? {} : { rank_points: parsed.course.rank_points }),
        }).select('id').single());
        if (r.error) { btn.disabled = false; return toast('코스를 만들지 못했어요: ' + r.error.message, true); }
        cid = r.data.id;
      }
      const base = (existing || []).reduce((mx, l) => Math.max(mx, l.position), 0);
      const rows = parsed.lessons.map((l, i) => ({ ...l, course_id: cid, position: base + (i + 1) * 1000, is_public: course ? pub : true }));
      const { error } = await lrWrite((drop) => sb.from('learn_lessons').insert(drop ? rows.map(({ rank_points, ...o }) => o) : rows));
      if (error) {
        if (!course) await sb.from('learn_courses').delete().eq('id', cid);
        btn.disabled = false;
        return toast('레슨을 넣지 못했어요: ' + error.message, true);
      }
      m.close();
      toast(`레슨 ${rows.length}개를 추가했어요${pub ? '' : ' (비공개 — 확인 후 공개해 주세요)'}`);
      if (course) route(true); else location.hash = '#/learn/c/' + cid;
    };
  }
  function openLessonEdit(lesson) {
    const cur = { title: lesson.title, minutes: lesson.minutes || undefined, rank_points: lesson.rank_points == null ? undefined : lesson.rank_points, summary: lesson.summary || '', steps: lesson.steps };
    const m = modal(`<h3>✏️ 레슨 수정 (JSON)</h3>
      <p class="muted small">이 레슨 하나의 JSON 이에요. 고친 뒤 저장하면 바뀌어요. 이미 푼 학생의 진도는 단계 번호 기준으로 그대로 남아요 — 단계를 끼워 넣거나 빼면 어긋날 수 있어요.</p>
      <label>레슨 JSON<textarea id="leText" class="code" style="min-height:360px" spellcheck="false"></textarea></label>
      <p class="muted small" id="leInfo"></p>
      <div class="form-actions"><button class="primary" id="leSave">저장</button><button type="button" class="ghost" id="leCancel">취소</button></div>`);
    const q = (x) => $(x, m.el);
    q('#leText').value = JSON.stringify(cur, null, 1);
    q('#leCancel').onclick = m.close;
    q('#leSave').onclick = async () => {
      let l;
      try { l = parseLearnJson(JSON.stringify({ lessons: [JSON.parse(q('#leText').value)] })).lessons[0]; } catch (e) { q('#leInfo').textContent = '⚠️ ' + (e.message.includes('JSON') || e instanceof SyntaxError ? 'JSON 형식 오류예요' : e.message); return; }
      const { error } = await lrWrite((drop) => sb.from('learn_lessons').update({ title: l.title, summary: l.summary, minutes: l.minutes, steps: l.steps, ...(drop ? {} : { rank_points: l.rank_points }) }).eq('id', lesson.id));
      if (error) return toast('저장하지 못했어요: ' + error.message, true);
      m.close(); toast('저장했어요'); route(true);
    };
  }
  function openCourseEdit(c) {
    const m = modal(`<h3>✏️ 코스 정보</h3>
      <label>제목<input type="text" id="ceTitle" value="${esc(c.title)}"></label>
      <label>설명<textarea id="ceDesc" style="min-height:80px">${esc(c.description || '')}</textarea></label>
      <label class="inline"><input type="checkbox" id="ceSeq" ${c.sequential !== false ? 'checked' : ''}> 앞 레슨을 끝내야 다음 레슨이 열려요 <span class="muted small">(선생님은 항상 모두 열려요)</span></label>
      <label>🏆 랭킹 점수 <span class="muted small">— 이 코스의 레슨을 <b>하나 끝낼 때마다</b> 받는 점수 (0 이면 랭킹·티어에 반영 안 해요). 레슨마다 따로 정하려면 레슨 JSON 의 <code class="ic">rank_points</code></span>
        <input type="number" id="ceRank" min="0" max="100000" step="1" value="${Number(c.rank_points) || 0}" ${'rank_points' in c ? '' : 'disabled'}></label>
      ${'rank_points' in c ? '' : '<p class="muted small">⚠️ 먼저 v420_learn_points.sql 을 Supabase 에서 한 번 실행해야 점수를 정할 수 있어요.</p>'}
      <div class="form-actions"><button class="primary" id="ceSave">저장</button><button type="button" class="ghost" id="ceCancel">취소</button></div>`);
    const q = (x) => $(x, m.el);
    q('#ceCancel').onclick = m.close;
    q('#ceSave').onclick = async () => {
      const title = q('#ceTitle').value.trim();
      if (!title) return toast('제목을 써 주세요', true);
      const rk = Math.max(0, Math.min(100000, Math.round(Number(q('#ceRank').value) || 0)));
      const { error } = await sb.from('learn_courses').update({ title, description: q('#ceDesc').value.trim(), sequential: q('#ceSeq').checked, ...('rank_points' in c ? { rank_points: rk } : {}) }).eq('id', c.id);
      if (error) return toast('저장하지 못했어요', true);
      m.close(); route(true);
    };
  }

  /* ----- 레슨 화면 (한 단계씩) ----- */
  async function pageLearnLesson(rawId) {
    const id = Number(rawId);
    const staff = can('content');
    const lr = await sb.from('learn_lessons').select('*').eq('id', id).maybeSingle();
    if (lr.error) return learnMissing();
    const lesson = lr.data;
    if (!lesson) return notFound();
    const [cr, sib, pr] = await Promise.all([
      sb.from('learn_courses').select('*').eq('id', lesson.course_id).maybeSingle(),
      sb.from('learn_lessons').select('id,title,position,is_public').eq('course_id', lesson.course_id).order('position').order('id'),
      sb.from('learn_progress').select('*').eq('lesson_id', id).eq('user_id', me.id).maybeSingle(),
    ]);
    const course = cr.data || { id: lesson.course_id, title: '코스' };
    const sibs = sib.data || [];
    const at = sibs.findIndex((x) => x.id === id);
    if (course.sequential !== false && !staff && at > 0) {
      const pp = await sb.from('learn_progress').select('completed').eq('user_id', me.id).eq('lesson_id', sibs[at - 1].id).maybeSingle();
      if (!(pp.data && pp.data.completed)) return [`<div class="card pad center"><h2>🔒 잠겨 있어요</h2><p class="muted">앞 레슨 "${esc(sibs[at - 1].title)}" 을(를) 먼저 끝내 주세요.</p><a class="ghost btnlike" href="#/learn/c/${course.id}">← 코스로</a></div>`];
    }
    const steps = lesson.steps || [];
    if (!steps.length) return notFound();
    const P = pr.data
      ? { cur: pr.data.cur || 0, done: pr.data.done || {}, wrong: wrongList(pr.data).slice(), xp: pr.data.xp || 0, completed: !!pr.data.completed, completed_at: pr.data.completed_at }
      : { cur: 0, done: {}, wrong: [], xp: 0, completed: false, completed_at: null };
    const nextLesson = sibs.slice(at + 1).find((x) => staff || x.is_public);
    const rankPts = lrPts(lesson, course);

    return [`
      <p><a href="#/learn/c/${course.id}">← ${esc(course.title)}</a></p>
      <div class="card lr-wrap" id="lrWrap">
        <div class="lr-top"><b>${esc(lesson.title)}</b><span class="spacer"></span>${lrPtsChip(rankPts)}<span class="chip" id="lrXp">⭐ 0 XP</span></div>
        <div class="lr-bar"><i id="lrBar"></i></div>
        <div class="lr-dots" id="lrDots"></div>
        <div id="lrStep" class="lr-step"></div>
        <div class="lr-nav" id="lrNav"><button class="ghost" id="lrPrev">← 이전</button><span class="spacer"></span><button class="ghost" id="lrNext">다음 →</button></div>
      </div>`,
    (v) => {
      const n = steps.length;
      let cur = 0;
      const box = $('#lrStep', v);
      const doneCount = () => steps.filter((_, k) => P.done[k]).length;
      const reach = () => { for (let k = 0; k < n; k += 1) if (!P.done[k]) return k; return n - 1; };
      const saveProg = async () => {
        const row = { user_id: me.id, lesson_id: id, cur: P.cur, done: P.done, wrong: P.wrong, xp: P.xp, completed: P.completed, updated_at: new Date().toISOString() };
        if (P.completed) { if (!P.completed_at) P.completed_at = new Date().toISOString(); row.completed_at = P.completed_at; }
        const { error } = await sb.from('learn_progress').upsert(row, { onConflict: 'user_id,lesson_id' });
        if (error && !saveProg.warned) { saveProg.warned = true; toast('진도를 저장하지 못했어요 (v410_learn.sql 을 실행했나요?)', true); }
      };
      const updateTop = () => {
        $('#lrBar', v).style.width = `${Math.round((doneCount() / n) * 100)}%`;
        $('#lrXp', v).textContent = `⭐ ${P.xp} XP`;
        const r = reach();
        $('#lrDots', v).innerHTML = steps.map((s, k) => `<button type="button" class="lr-dot ${P.done[k] ? 'ok' : ''} ${k === cur ? 'cur' : ''}" data-dot="${k}" ${k > r && !P.completed ? 'disabled' : ''} title="${k + 1}. ${esc(s.title || ({ explain: '개념', quiz: '확인', practice: '실습' })[s.type])}">${({ explain: '📖', quiz: '❓', practice: '💻' })[s.type]}</button>`).join('');
        v.querySelectorAll('[data-dot]').forEach((b) => (b.onclick = () => show(Number(b.dataset.dot))));
      };
      const updateNav = () => {
        const ok = !!P.done[cur];
        const nx = $('#lrNext', v);
        nx.textContent = cur >= n - 1 ? '완료 🎉' : '다음 →';
        nx.className = ok || steps[cur].type === 'explain' ? 'primary' : 'ghost';
        $('#lrPrev', v).disabled = cur === 0;
      };
      const markDone = async (k, info) => {
        if (P.done[k]) return;
        P.done[k] = info;
        let gain = info.xp || 0;
        if (!P.completed && steps.every((_, j) => P.done[j])) { P.completed = true; gain += 10; } // 레슨 완료 보너스
        P.xp += gain;
        learnAddXp(gain);
        await saveProg();
        updateTop();
        updateNav();
      };
      const finish = () => {
        $('#lrNav', v).hidden = true;
        const first = steps.filter((s, k) => s.type === 'quiz' && P.done[k] && (P.done[k].t || 1) <= 1 && !P.done[k].peek).length;
        const qn = steps.filter((s) => s.type === 'quiz').length;
        box.innerHTML = `<div class="lr-finish"><div class="lr-big">🎉</div><h2>레슨 완료!</h2>
          <p class="muted">${esc(lesson.title)}</p>
          <div class="lr-stats"><div class="card lr-stat"><b>⭐ ${P.xp}</b><span class="muted small">이 레슨 XP</span></div>${rankPts > 0 ? `<div class="card lr-stat"><b>🏆 +${rankPts}</b><span class="muted small">랭킹 점수</span></div>` : ''}${qn ? `<div class="card lr-stat"><b>🎯 ${first} / ${qn}</b><span class="muted small">첫 시도 정답</span></div>` : ''}</div>
          ${lesson.summary ? `<div class="lr-sum"><h3>📌 핵심 정리</h3>${lrMd(lesson.summary)}</div>` : ''}
          <div class="form-actions" style="justify-content:center">${nextLesson ? `<a class="primary btnlike" href="#/learn/l/${nextLesson.id}">다음 레슨 ▶</a>` : ''}${P.wrong.length ? '<a class="ghost btnlike" href="#/learn/r">🔁 틀린 문제 복습</a>' : ''}<a class="ghost btnlike" href="#/learn/c/${course.id}">코스로 돌아가기</a><button class="ghost" id="lrAgain" type="button">↺ 처음부터 다시 보기</button></div></div>`;
        $('#lrAgain', v).onclick = () => { $('#lrNav', v).hidden = false; show(0); };
        updateTop();
      };

      const show = (i) => {
        cur = Math.max(0, Math.min(i, n - 1));
        P.cur = cur;
        const st = steps[cur];
        const done = P.done[cur];
        const label = { explain: '📖 개념', quiz: '❓ 확인 문제', practice: '💻 실습' }[st.type];
        box.innerHTML = `<div class="lr-kind">${label} <span class="muted small">${cur + 1} / ${n}</span></div>${st.title ? `<h3 class="lr-title">${esc(st.title)}</h3>` : ''}<div class="lr-slot"></div>`;
        const slot = $('.lr-slot', box);
        if (st.type === 'explain') {
          slot.innerHTML = `${st.body ? `<div class="lr-md">${lrMd(st.body)}</div>` : ''}${st.code ? (st.run ? `<div class="lr-codebox">${lrCodeBoxHtml(Math.min(14, Math.max(3, st.code.split('\n').length + 1)))}</div>` : `<pre><code>${esc(st.code)}</code></pre>`) : ''}`;
          if (st.code && st.run) lrCodeBox(slot, st.code);
        } else if (st.type === 'quiz') {
          if (done) slot.innerHTML = quizSolvedHtml(st);
          else {
            mountQuiz(slot, st, {
              onWrong: () => { if (!P.wrong.includes(cur)) { P.wrong.push(cur); saveProg(); } },
              onDone: ({ tries, peek }) => markDone(cur, { xp: peek ? 0 : tries <= 1 ? XP_QUIZ : 5, t: tries, ...(peek ? { peek: true } : {}) }),
            });
          }
        } else mountPractice(slot, st, cur, done);
        updateTop();
        updateNav();
        saveProg();
        window.scrollTo({ top: Math.max(0, $('#lrWrap', v).getBoundingClientRect().top + window.scrollY - 70), behavior: 'smooth' });
      };
      function mountPractice(slot, st, k, done) {
        const hints = st.hints || [];
        slot.innerHTML = `<div class="lr-md">${lrMd(st.body)}</div>
          ${done ? '<div class="lr-fb ok"><b>✅ 이미 통과한 실습이에요</b> 다시 풀어 봐도 돼요.</div>' : ''}
          <div class="lr-codebox">${lrCodeBoxHtml(10, { stdin: true })}</div>
          <div class="lr-btns">${st.tests.length ? '<button class="primary" type="button" data-lrgrade>✅ 채점하기</button>' : ''}${hints.length ? `<button class="ghost" type="button" data-lrhint>💡 힌트 보기 (0/${hints.length})</button>` : ''}${st.solution ? `<button class="ghost" type="button" data-lrsol ${done ? '' : 'disabled'}>🔑 정답 코드 ${done ? '' : '(채점 3번 시도 후)'}</button>` : ''}</div>
          <div class="lr-hints"></div><div class="lr-grade judge-out" hidden></div><div class="lr-sol" hidden></div>`;
        const key = codeKey(id, k);
        const ta = lrCodeBox(slot, lrLoad(key) != null ? lrLoad(key) : st.starter, { key });
        if (st.stdin) $('.lr-stdin', slot).value = st.stdin;
        else { const smp = st.tests.find((t) => !t.hidden); if (smp) $('.lr-stdin', slot).value = smp.input; }
        let tries = 0;
        let used = 0;
        const solBtn = $('[data-lrsol]', slot);
        const showSol = () => {
          const s = $('.lr-sol', slot);
          s.hidden = false;
          s.innerHTML = `<div class="muted small">정답 코드 (예시)</div><pre><code>${esc(st.solution)}</code></pre>${st.explanation ? `<div class="lr-ex">${lrMd(st.explanation)}</div>` : ''}`;
        };
        if (done && st.solution) showSol();
        const hb = $('[data-lrhint]', slot);
        if (hb) hb.onclick = () => {
          if (used >= hints.length) return;
          used += 1;
          $('.lr-hints', slot).innerHTML = hints.slice(0, used).map((h, i) => `<div class="lr-hint">💡 <b>힌트 ${i + 1}</b> ${lrMd(h)}</div>`).join('');
          hb.textContent = `💡 힌트 보기 (${used}/${hints.length})`;
          if (used >= hints.length) hb.disabled = true;
        };
        if (solBtn) solBtn.onclick = async () => {
          if (!P.done[k] && !confirm('정답 코드를 보면 이 실습의 XP를 받을 수 없어요. 볼까요?')) return;
          showSol();
          solBtn.disabled = true;
          if (!P.done[k]) await markDone(k, { xp: 0, t: tries, peek: true });
        };
        const gb = $('[data-lrgrade]', slot);
        if (gb) gb.onclick = async () => {
          const code = ta.value;
          const out = $('.lr-grade', slot);
          if (!code.trim()) return toast('코드를 입력하세요', true);
          gb.disabled = true;
          tries += 1;
          out.hidden = false;
          out.innerHTML = '<span class="muted">⏳ 파이썬을 준비하는 중… (처음 한 번은 몇 초 걸려요)</span>';
          try {
            const res = await gradeAll(code, st.tests, (i2, n2) => { out.innerHTML = `<span class="muted">⏳ 채점 중… ${i2 + 1} / ${n2}</span>`; });
            out.innerHTML = renderGrade(res, null, [], false);
            if (res.status === 'AC') {
              if (!P.done[k]) await markDone(k, { xp: Math.max(10, XP_PRACTICE - 5 * used), t: tries, h: used });
              if (st.solution) showSol(); else if (st.explanation) { const s = $('.lr-sol', slot); s.hidden = false; s.innerHTML = `<div class="lr-ex">${lrMd(st.explanation)}</div>`; }
              if (solBtn) solBtn.disabled = true;
              out.insertAdjacentHTML('afterbegin', '<div class="lr-fb ok"><b>🎉 통과했어요!</b> 아래 "다음"으로 넘어가요.</div>');
            } else if (tries >= 3 && solBtn) { solBtn.disabled = false; solBtn.textContent = '🔑 정답 코드 보기'; }
          } catch (e) { out.innerHTML = renderRun({ status: 'LOAD', err: e.message }); }
          gb.disabled = false;
        };
      }

      $('#lrPrev', v).onclick = () => show(cur - 1);
      $('#lrNext', v).onclick = async () => {
        const st = steps[cur];
        if (!P.done[cur]) {
          if (st.type === 'explain') await markDone(cur, { xp: XP_EXPLAIN });
          else if (st.type === 'practice' && !st.tests.length) await markDone(cur, { xp: 5 });
          else return toast(st.type === 'quiz' ? '먼저 문제를 풀어 보세요' : '먼저 채점을 통과해 보세요 (막히면 힌트·정답 코드를 쓸 수 있어요)', true);
        }
        if (cur >= n - 1) return finish();
        show(cur + 1);
      };
      // 처음 열 때: 끝낸 레슨은 처음부터, 하던 레슨은 하던 곳(아직 못 푼 첫 단계까지만)에서
      if (P.completed) { P.cur = 0; show(0); } else show(Math.min(P.cur, reach()));
    }];
  }

  /* ----- 오답 복습: 틀렸던 확인 문제만 모아서 다시 ----- */
  async function pageLearnReview() {
    const pr = await sb.from('learn_progress').select('*').eq('user_id', me.id);
    if (pr.error) return learnMissing();
    const rows = (pr.data || []).filter((p) => wrongList(p).length);
    const empty = ['<p><a href="#/learn">← 학습</a></p><div class="card pad center"><h2>🔁 오답 복습</h2><p class="muted">복습할 문제가 없어요. 잘하고 있어요! 🎉</p></div>'];
    if (!rows.length) return empty;
    const lr = await sb.from('learn_lessons').select('id,title,steps').in('id', rows.map((p) => p.lesson_id));
    const lmap = new Map((lr.data || []).map((l) => [l.id, l]));
    const queue = [];
    rows.forEach((p) => wrongList(p).forEach((k) => {
      const l = lmap.get(p.lesson_id);
      const st = l && l.steps[k];
      if (st && st.type === 'quiz') queue.push({ p, k, st, title: l.title });
    }));
    if (!queue.length) return empty;
    queue.sort(() => Math.random() - 0.5);
    return [`<p><a href="#/learn">← 학습</a></p><div class="card lr-wrap"><div class="lr-top"><b>🔁 오답 복습</b><span class="spacer"></span><span class="chip" id="rvCnt"></span></div><div class="lr-bar"><i id="rvBar"></i></div><div id="rvBox" class="lr-step"></div></div>`,
      (v) => {
        let i = 0;
        let fixed = 0;
        const box = $('#rvBox', v);
        const show = () => {
          $('#rvBar', v).style.width = `${Math.round((i / queue.length) * 100)}%`;
          $('#rvCnt', v).textContent = `${Math.min(i + 1, queue.length)} / ${queue.length}`;
          if (i >= queue.length) {
            box.innerHTML = `<div class="lr-finish"><div class="lr-big">🎉</div><h2>복습 끝!</h2><p class="muted">${fixed}개를 다시 맞혔어요.</p><div class="form-actions" style="justify-content:center"><a class="primary btnlike" href="#/learn">학습으로</a></div></div>`;
            return;
          }
          const q = queue[i];
          box.innerHTML = `<div class="lr-kind">❓ 확인 문제 <span class="muted small">${esc(q.title)}</span></div><div class="lr-slot"></div><div class="form-actions" id="rvNext" hidden><button class="primary" type="button">다음 →</button></div>`;
          mountQuiz($('.lr-slot', box), q.st, {
            onWrong: () => {},
            onDone: async ({ tries, peek }) => {
              if (!peek && tries <= 3) {
                fixed += 1;
                learnAddXp(3);
                q.p.wrong = wrongList(q.p).filter((x) => x !== q.k);
                await sb.from('learn_progress').update({ wrong: q.p.wrong }).eq('user_id', me.id).eq('lesson_id', q.p.lesson_id);
              }
              const nx = $('#rvNext', box);
              nx.hidden = false;
              $('button', nx).onclick = () => { i += 1; show(); };
            },
          });
        };
        show();
      }];
  }

  /* ---------- ⚙️ 설정 › 내 기록 (푼 문제 · 제출 · 학습) — 누르면 그 문제/제출/레슨으로 이동 ---------- */
  async function loadMyRecords() {
    const subs = await fetchAll((a, b) => sb.from('submissions').select('id,exercise_id,set_id,version,judge,created_at').eq('user_id', me.id).order('id', { ascending: false }).range(a, b));
    const inChunks = async (table, cols, ids) => {
      const out = [];
      for (let i = 0; i < ids.length; i += 150) {
        const r = await sb.from(table).select(cols).in('id', ids.slice(i, i + 150));
        if (r.error) return { error: r.error, data: out };
        out.push(...(r.data || []));
      }
      return { data: out };
    };
    await loadDrafts().catch(() => {}); // 임시 저장 (V4.4.1)
    const exIds = [...new Set(subs.map((s) => s.exercise_id).concat([...DR.map.keys()]))];
    const exs = (await inChunks('exercises', 'id,set_id,difficulty,body,label,rank_points', exIds)).data;
    const exMap = new Map(exs.map((e) => [e.id, e]));
    const setIds = [...new Set(exs.map((e) => e.set_id))];
    const sets = (await inChunks('problem_sets', 'id,title,short_name', setIds)).data;
    const setMap = new Map(sets.map((x) => [x.id, x]));
    // 학습
    let prog = [];
    let lessons = [];
    let courses = [];
    const pr = await sb.from('learn_progress').select('lesson_id,xp,completed,completed_at,updated_at,done').eq('user_id', me.id);
    if (!pr.error) {
      prog = pr.data || [];
      const lids = prog.map((p) => p.lesson_id);
      if (lids.length) {
        let lr = await inChunks('learn_lessons', 'id,title,course_id,rank_points', lids);
        if (lr.error) lr = await inChunks('learn_lessons', 'id,title,course_id', lids);
        lessons = lr.data;
        let cr = await inChunks('learn_courses', 'id,title,rank_points', [...new Set(lessons.map((l) => l.course_id))]);
        if (cr.error) cr = await inChunks('learn_courses', 'id,title', [...new Set(lessons.map((l) => l.course_id))]);
        courses = cr.data;
      }
    }
    return { subs, exMap, setMap, prog, lessons, courses, learnOk: !pr.error, drafts: [...DR.map.entries()].map(([eid, d]) => ({ eid, d })).filter((x) => exMap.has(x.eid)).sort((a, b) => (b.d.t || 0) - (a.d.t || 0)) };
  }

  function bindMyRecords(root) {
    const card = $('#recCard', root);
    if (!card) return;
    const body = $('#recBody', card);
    let loaded = false;
    const title = (e) => (e ? (firstLine(e.body).replace(/^\*+|\*+$/g, '').trim() || e.label || '(제목 없음)') : '(삭제된 문제)');
    const AC = (s) => s.judge && s.judge.status === 'AC' && !s.judge.teacher_bad;
    card.addEventListener('toggle', async () => {
      if (!card.open || loaded) return;
      loaded = true;
      let d;
      try { d = await loadMyRecords(); } catch (e) { body.innerHTML = '<span class="muted">기록을 불러오지 못했어요. 새로고침 해보세요.</span>'; loaded = false; return; }
      const { subs, exMap, setMap } = d;
      let drafts = d.drafts || [];
      // 문제별 모음 (subs 는 최신순)
      const by = new Map();
      subs.forEach((s) => { if (!by.has(s.exercise_id)) by.set(s.exercise_id, []); by.get(s.exercise_id).push(s); });
      const solved = [];
      const trying = [];
      by.forEach((list, eid) => {
        const oldestAc = list.slice().reverse().find((s) => s.judge && (s.judge.teacher === 'ok' || (s.judge.status === 'AC' && s.judge.teacher !== 'bad')));
        if (oldestAc) solved.push({ eid, sub: oldestAc, n: list.length });
        else trying.push({ eid, sub: list[0], n: list.length });
      });
      solved.sort((a, b) => String(b.sub.created_at).localeCompare(String(a.sub.created_at)));
      trying.sort((a, b) => String(b.sub.created_at).localeCompare(String(a.sub.created_at)));
      const lmap = new Map(d.lessons.map((l) => [l.id, l]));
      const cmap = new Map(d.courses.map((c) => [c.id, c]));
      const learnRows = d.prog.map((p) => ({ p, l: lmap.get(p.lesson_id) })).filter((x) => x.l)
        .sort((a, b) => String(b.p.completed_at || b.p.updated_at).localeCompare(String(a.p.completed_at || a.p.updated_at)));
      const lDone = learnRows.filter((x) => x.p.completed);
      const lPts = lDone.reduce((s, x) => s + lrPts(x.l, cmap.get(x.l.course_id)), 0);

      const exRow = (eid, sub, extra) => {
        const e = exMap.get(eid);
        const st = e ? setMap.get(e.set_id) : null;
        return `<a class="row rec-row" href="#/p/${eid}/s${sub.id}">
          <div class="row-main">${e ? diffTag(e.difficulty) : ''} <b>#${eid}</b> <span class="numtitle">${esc(title(e))}</span></div>
          <div class="muted small">${st ? esc(shortOf(st)) + ' · ' : ''}${extra} · ${fmt(sub.created_at)}</div></a>`;
      };
      const tabs = {
        solved: () => solved.map((x) => exRow(x.eid, x.sub, `✅ 푼 문제 · 제출 ${x.n}번`)).join('') || '<p class="muted center pad">아직 푼 문제가 없어요.</p>',
        trying: () => trying.map((x) => exRow(x.eid, x.sub, `${judgeBadge(x.sub.judge) || '제출함'} · 제출 ${x.n}번`)).join('') || '<p class="muted center pad">도전 중인 문제가 없어요. 👍</p>',
        draft: () => drafts.map(({ eid, d: dd }) => {
          const e = exMap.get(eid);
          const st = e ? setMap.get(e.set_id) : null;
          const snip = String(dd.c || (dd.v || []).find((x) => String(x).trim()) || '').split('\n').find((l) => l.trim()) || '';
          return `<a class="row rec-row" href="#/p/${eid}"><div class="row-main">${e ? diffTag(e.difficulty) : ''} <b>#${eid}</b> <span class="numtitle">${esc(title(e))}</span>
            <div class="muted small dr-snip">${esc(snip.slice(0, 80))}</div></div>
            <div class="muted small">${st ? esc(shortOf(st)) + ' · ' : ''}💾 ${fmt(dd.t)} <button type="button" class="link" data-dd="${eid}">삭제</button></div></a>`;
        }).join('') || '<p class="muted center pad">임시 저장한 문제가 없어요. 풀이 칸에 적으면 자동으로 저장돼요 💾</p>',
        subs: () => subs.map((s) => exRow(s.exercise_id, s, `v${s.version} ${judgeBadge(s.judge) || ''}`)).join('') || '<p class="muted center pad">낸 제출이 없어요.</p>',
        learn: () => (d.learnOk ? learnRows.map(({ p, l }) => {
          const c = cmap.get(l.course_id);
          const pts = lrPts(l, c);
          const n = Object.keys(p.done || {}).length;
          return `<a class="row rec-row" href="#/learn/l/${l.id}"><div class="row-main">📚 <b>${esc(l.title)}</b> <span class="muted small">${c ? esc(c.title) : ''}</span></div>
            <div class="muted small">${p.completed ? `✅ 완료 · ${fmt(p.completed_at || p.updated_at)}` : `▶ 진행 중 (${n}단계 끝냄) · ${fmt(p.updated_at)}`} · ⭐ ${p.xp || 0} XP${p.completed && pts > 0 ? ` · 🏆 랭킹 +${pts}점` : ''}</div></a>`;
        }).join('') || '<p class="muted center pad">아직 시작한 학습이 없어요. <a href="#/learn">📚 학습</a>에서 시작해 보세요!</p>' : '<p class="muted center pad">학습 기록을 아직 볼 수 없어요.</p>'),
      };
      const tabDef = [['solved', `✅ 푼 문제 ${solved.length}`], ['trying', `🛠 도전 중 ${trying.length}`], ['draft', `💾 임시 저장 ${drafts.length}`], ['subs', `📤 제출 ${subs.length}`], ['learn', `📚 학습 ${lDone.length}`]];
      let cur = 'solved';
      let limit = 30;
      const draw = () => {
        const html = tabs[cur]();
        body.innerHTML = `<div class="lr-stats rec-sum"><div class="card lr-stat"><b>${solved.length}</b><span class="muted small">푼 문제</span></div><div class="card lr-stat"><b>${subs.length}</b><span class="muted small">낸 제출</span></div><div class="card lr-stat"><b>${lDone.length}</b><span class="muted small">끝낸 레슨</span></div>${lPts ? `<div class="card lr-stat"><b>🏆 ${lPts}</b><span class="muted small">학습으로 얻은 점수</span></div>` : ''}</div>
          <div class="tabs">${tabDef.map(([k, n]) => `<button type="button" data-rt="${k}" class="${cur === k ? 'on' : ''}">${n}</button>`).join('')}</div>
          <div class="rec-list"></div>`;
        const list = $('.rec-list', body);
        const nodes = document.createElement('div');
        nodes.innerHTML = html;
        const rows = [...nodes.children];
        list.append(...rows.slice(0, limit));
        if (rows.length > limit) {
          const more = document.createElement('div');
          more.className = 'center pad';
          more.innerHTML = `<button class="ghost" type="button">더 보기 (${rows.length - limit}개 남음)</button>`;
          more.firstChild.onclick = () => { limit += 30; draw(); };
          list.append(more);
        }
        body.querySelectorAll('[data-rt]').forEach((b) => (b.onclick = () => { cur = b.dataset.rt; limit = 30; draw(); }));
        body.querySelectorAll('[data-dd]').forEach((b) => (b.onclick = (ev) => {
          ev.preventDefault(); ev.stopPropagation();
          if (!confirm('이 문제의 임시 저장을 지울까요?')) return;
          deleteDraft(Number(b.dataset.dd));
          drafts = drafts.filter((x) => x.eid !== Number(b.dataset.dd));
          draw();
        }));
      };
      draw();
    });
  }


  /* ---------- V4.4.0 : 캐릭터 · 프로필 꾸미기 · DM · 알림 (v440_social.sql) ---------- */
  const SOC_HINT = '아직 준비되지 않았어요. 선생님이 v440_social.sql 을 Supabase SQL Editor 에서 한 번 실행하면 쓸 수 있어요.';
  // ---- V4.5.1 캐릭터 아이템: 그림(SVG 조각)은 안전한 도형만 남기고 쓰기
  const ITEMS = new Map(); // id → {id,name,slot,svg(정리된 것)}
  const ITEM_SLOTS = [['hat', '모자', '🎩'], ['hair', '머리', '💇'], ['face', '얼굴', '😎'], ['outfit', '옷', '👕'], ['back', '뒤(날개·망토)', '🪽'], ['deco', '장식', '✨']];
  const SVG_TAGS = new Set(['g', 'path', 'circle', 'ellipse', 'rect', 'line', 'polyline', 'polygon', 'defs', 'lineargradient', 'radialgradient', 'stop']);
  const SVG_ATTR = /^(d|cx|cy|r|rx|ry|x|y|x1|y1|x2|y2|width|height|points|fill|fill-opacity|fill-rule|clip-rule|stroke|stroke-width|stroke-opacity|stroke-linecap|stroke-linejoin|stroke-dasharray|opacity|transform|id|offset|stop-color|stop-opacity|gradientunits|gradienttransform)$/i;
  function cleanSvg(str) {
    try {
      const doc = new DOMParser().parseFromString(`<svg xmlns="http://www.w3.org/2000/svg">${str}</svg>`, 'image/svg+xml');
      if (doc.querySelector('parsererror')) return '';
      const walk = (n) => {
        Array.from(n.children).forEach((c) => {
          if (!SVG_TAGS.has(c.localName.toLowerCase())) { c.remove(); return; }
          Array.from(c.attributes).forEach((at) => {
            if (!SVG_ATTR.test(at.name) || /javascript:|data:|url\(\s*[^#\s)]/i.test(at.value)) c.removeAttribute(at.name);
          });
          walk(c);
        });
      };
      walk(doc.documentElement);
      return Array.from(doc.documentElement.childNodes).map((x) => new XMLSerializer().serializeToString(x)).join('').replace(/ xmlns="[^"]*"/g, '');
    } catch (e) { return ''; }
  }
  // 학생이 올린 SVG 파일/붙여넣기 → 100×100 칸 도형 조각으로 (viewBox 가 달라도 맞춰 줘요)
  function extractSvg(text) {
    const t = String(text || '').trim();
    if (!t) return '';
    if (!/<svg[\s>]/i.test(t)) return t;
    const doc = new DOMParser().parseFromString(t, 'image/svg+xml');
    if (doc.querySelector('parsererror')) return '';
    const root = doc.documentElement;
    const vb = (root.getAttribute('viewBox') || '').split(/[\s,]+/).map(Number);
    const has = vb.length === 4 && vb.every((n) => Number.isFinite(n)) && vb[2] > 0 && vb[3] > 0;
    const w = has ? vb[2] : parseFloat(root.getAttribute('width')) || 100;
    const h = has ? vb[3] : parseFloat(root.getAttribute('height')) || 100;
    const x0 = has ? vb[0] : 0;
    const y0 = has ? vb[1] : 0;
    const inner = Array.from(root.childNodes).map((n) => new XMLSerializer().serializeToString(n)).join('').replace(/ xmlns(:\w+)?="[^"]*"/g, '');
    const sx = 100 / w;
    const sy = 100 / h;
    return Math.abs(sx - 1) < 1e-6 && Math.abs(sy - 1) < 1e-6 && !x0 && !y0 ? inner : `<g transform="scale(${sx.toFixed(5)} ${sy.toFixed(5)}) translate(${-x0} ${-y0})">${inner}</g>`;
  }
  function itemPreview(slot, rawSvg, size = 80, av) { // 아직 등록되지 않은 그림을 내 캐릭터에 입혀서 보여줘요
    const base = av || normAv(null, 'preview');
    ITEMS.set('__pv', { id: '__pv', name: '', slot, svg: cleanSvg(rawSvg) });
    const h = avatarSvg({ ...base, items: { [slot]: '__pv' } }, size);
    ITEMS.delete('__pv');
    return h;
  }
  let EVENTS = [];
  async function loadEvents() {
    try { const { data, error } = await sb.rpc('event_active'); EVENTS = error || !Array.isArray(data) ? [] : data; } catch (e) { EVENTS = []; }
  }
  const evLeft = (e) => { const ms = new Date(e.ends_at).getTime() - Date.now(); const d = Math.floor(ms / 864e5); return d >= 1 ? `D-${d}` : `${Math.max(0, Math.floor(ms / 36e5))}시간 남음`; };
  function injectEventBanner() {
    const v = $('#view');
    if (!v || !EVENTS.length || $('.ev-banner', v) || !/^#\/home|^#?\/?$/.test(location.hash || '#/home')) return;
    const box = document.createElement('div');
    box.innerHTML = EVENTS.map((e) => `<a class="card ev-banner tone-${esc(e.tone)}" href="#/me/avatar"><span class="ev-emoji">${esc(e.emoji)}</span><span class="ev-t"><b>${esc(e.title)}</b>${Number(e.mult) > 1 ? ` <span class="ev-mult">💎 ×${Number(e.mult)}</span>` : ''}${e.items > 0 ? ` <span class="ev-mult">🎁 한정 ${e.items}</span>` : ''}<br><span class="small">${esc(e.descr || '')} <span class="muted">· ${evLeft(e)} (~${new Date(e.ends_at).toLocaleString('ko-KR', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' })})</span></span></span></a>`).join('');
    while (box.lastChild) v.insertBefore(box.lastChild, v.firstChild);
  }
  const IT = (a, slot) => { const id = a.items && a.items[slot]; const it = id && ITEMS.get(id); return it && it.slot === slot ? `<g>${it.svg}</g>` : ''; };
  async function loadItems() {
    try {
      const { data, error } = await sb.from('avatar_items').select('id,name,slot,svg').eq('status', 'active');
      if (error) throw error;
      ITEMS.clear();
      (data || []).forEach((x) => { const sv = cleanSvg(x.svg); if (sv) ITEMS.set(x.id, { id: x.id, name: x.name, slot: x.slot, svg: sv }); });
    } catch (e) { /* v451_items.sql 전이면 아이템 없이 동작해요 */ }
  }
  const AV = {
    skin: ['#ffe0c7', '#f7cba4', '#e8b48a', '#c98d62', '#a56a43', '#7a4a2c'],
    hairColor: ['#2b2b2b', '#5b3a1e', '#9a6a2f', '#e0b04a', '#d6453d', '#3b6fd8', '#8a4fd8', '#f2f2f2'],
    outfitColor: ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#334155', '#f8fafc'],
    bg: ['#dbeafe', '#fee2e2', '#d1fae5', '#fef3c7', '#ede9fe', '#fce7f3', '#e2e8f0', '#1e293b'],
    hair: [['none', '없음'], ['short', '짧은 머리'], ['spiky', '뾰족 머리'], ['long', '긴 머리'], ['bun', '똥머리'], ['curly', '곱슬']],
    eyes: [['dot', '동그란 눈'], ['happy', '웃는 눈'], ['sleepy', '졸린 눈'], ['wide', '큰 눈'], ['wink', '윙크']],
    mouth: [['smile', '미소'], ['open', '활짝'], ['flat', '무표정'], ['tongue', '메롱'], ['o', '오']],
    outfit: [['tee', '티셔츠'], ['hoodie', '후드'], ['suit', '정장'], ['stripe', '줄무늬']],
    hat: [['none', '없음'], ['cap', '야구모자'], ['beanie', '비니'], ['headband', '헤어밴드'], ['crown', '왕관 (Gold~)', 2], ['wizard', '마법사 모자 (Platinum~)', 3]],
    acc: [['none', '없음'], ['glasses', '안경'], ['bow', '리본'], ['shades', '선글라스 (Silver~)', 1], ['headphone', '헤드폰 (Silver~)', 1]],
  };
  const AV_KEYS = ['skin', 'hairColor', 'outfitColor', 'bg', 'hair', 'eyes', 'mouth', 'outfit', 'hat', 'acc', 'hatColor'];
  const avHash = (s) => { let h = 2166136261; for (const ch of String(s)) { h ^= ch.charCodeAt(0); h = Math.imul(h, 16777619); } return h >>> 0; };
  const avPick = (arr, h, k) => arr[(h >>> k) % arr.length];
  const avCode = (list) => list.map((x) => x[0]);
  function defAvatar(seed) {
    const h = avHash(seed || 'x');
    return { skin: avPick(AV.skin, h, 1), hairColor: avPick(AV.hairColor.slice(0, 6), h, 3), outfitColor: avPick(AV.outfitColor, h, 5), bg: avPick(AV.bg.slice(0, 7), h, 7),
      hair: avPick(['short', 'spiky', 'long', 'bun', 'curly'], h, 9), eyes: avPick(avCode(AV.eyes), h, 11), mouth: avPick(['smile', 'open', 'smile', 'tongue'], h, 13),
      outfit: avPick(avCode(AV.outfit), h, 15), hat: 'none', acc: 'none', hatColor: avPick(AV.outfitColor, h, 17) };
  }
  function normAv(a, seed) {
    const d = defAvatar(seed);
    const o = a && typeof a === 'object' ? a : {};
    const r = {};
    AV_KEYS.forEach((k) => { r[k] = typeof o[k] === 'string' ? o[k] : d[k]; });
    const hex = /^#[0-9a-f]{6}$/i;
    ['skin', 'hairColor', 'outfitColor', 'bg', 'hatColor'].forEach((k) => { if (!hex.test(r[k])) r[k] = d[k]; });
    [['hair', AV.hair], ['eyes', AV.eyes], ['mouth', AV.mouth], ['outfit', AV.outfit], ['hat', AV.hat], ['acc', AV.acc]].forEach(([k, l]) => { if (!avCode(l).includes(r[k])) r[k] = d[k]; });
    r.items = {};
    if (o.items && typeof o.items === 'object') ITEM_SLOTS.forEach(([k]) => { if (typeof o.items[k] === 'string' && /^[a-z0-9_]{2,40}$/.test(o.items[k])) r.items[k] = o.items[k]; });
    return r;
  }
  function avatarSvg(av, size = 64) {
    const a = av;
    const sk = a.skin; const hc = a.hairColor; const oc = a.outfitColor; const dark = 'rgba(0,0,0,.22)';
    let s = `<rect width="100" height="100" rx="22" fill="${a.bg}"/>`;
    const iHat = IT(a, 'hat'); const iHair = IT(a, 'hair'); const iFace = IT(a, 'face');
    const hairK = iHair ? 'none' : a.hair; // 아이템을 입으면 같은 자리의 기본 모양은 빠져요
    const hasHat = !!iHat || a.hat !== 'none';
    s += IT(a, 'back');
    // 옷
    s += `<path d="M10 100 C12 76 32 68 50 68 C68 68 88 76 90 100 Z" fill="${oc}"/>`;
    if (a.outfit === 'hoodie') s += `<path d="M30 74 Q50 90 70 74 Q50 66 30 74Z" fill="${dark}"/><path d="M45 82 V94 M55 82 V94" stroke="#fff" stroke-opacity=".8" stroke-width="2" stroke-linecap="round"/>`;
    else if (a.outfit === 'suit') s += `<path d="M38 68 L50 90 L62 68 Z" fill="#fff"/><path d="M47 72 L50 90 L53 72 Z" fill="#ef4444"/><path d="M10 100 C12 76 32 68 38 68 L50 92 L40 100Z M90 100 C88 76 68 68 62 68 L50 92 L60 100Z" fill="${dark}"/>`;
    else if (a.outfit === 'stripe') s += `<g stroke="#fff" stroke-opacity=".55" stroke-width="3"><path d="M14 82 H86 M12 90 H88 M12 98 H88"/></g><path d="M40 68 Q50 78 60 68Z" fill="${dark}"/>`;
    else s += `<path d="M40 68 Q50 78 60 68Z" fill="${dark}"/>`;
    s += `<rect x="43" y="56" width="14" height="14" rx="5" fill="${sk}"/><path d="M43 64 Q50 70 57 64 V60 H43Z" fill="${dark}"/>`;
    s += IT(a, 'outfit');
    // 뒷머리
    if (hairK === 'long') s += `<path d="M23 50 C20 14 80 14 77 50 L80 80 Q50 88 20 80Z" fill="${hc}"/>`;
    if (hairK === 'bun' && !hasHat) s += `<circle cx="50" cy="11" r="10" fill="${hc}"/>`;
    // 얼굴
    s += `<circle cx="26.5" cy="48" r="5" fill="${sk}"/><circle cx="73.5" cy="48" r="5" fill="${sk}"/><ellipse cx="50" cy="46" rx="24" ry="26" fill="${sk}"/>`;
    s += `<ellipse cx="35" cy="55" rx="4.5" ry="3" fill="#ff7a8a" fill-opacity=".35"/><ellipse cx="65" cy="55" rx="4.5" ry="3" fill="#ff7a8a" fill-opacity=".35"/>`;
    // 눈
    const eyeC = '#27272a';
    const E = {
      dot: `<circle cx="40" cy="46" r="3.2" fill="${eyeC}"/><circle cx="60" cy="46" r="3.2" fill="${eyeC}"/>`,
      happy: `<path d="M35.5 47.5 Q40 41.5 44.5 47.5 M55.5 47.5 Q60 41.5 64.5 47.5" fill="none" stroke="${eyeC}" stroke-width="2.6" stroke-linecap="round"/>`,
      sleepy: `<path d="M35.5 46 H44.5 M55.5 46 H64.5" stroke="${eyeC}" stroke-width="2.8" stroke-linecap="round"/><path d="M36 49 Q40 51 44 49 M56 49 Q60 51 64 49" fill="none" stroke="${dark}" stroke-width="1.2"/>`,
      wide: `<circle cx="40" cy="46" r="5.4" fill="#fff"/><circle cx="60" cy="46" r="5.4" fill="#fff"/><circle cx="40.8" cy="46.4" r="3" fill="${eyeC}"/><circle cx="60.8" cy="46.4" r="3" fill="${eyeC}"/><circle cx="42" cy="45" r="1" fill="#fff"/><circle cx="62" cy="45" r="1" fill="#fff"/>`,
      wink: `<circle cx="40" cy="46" r="3.2" fill="${eyeC}"/><path d="M55.5 47.5 Q60 41.5 64.5 47.5" fill="none" stroke="${eyeC}" stroke-width="2.6" stroke-linecap="round"/>`,
    };
    s += E[a.eyes] || E.dot;
    const M = {
      smile: `<path d="M42 58 Q50 66 58 58" fill="none" stroke="#7a2e2e" stroke-width="2.6" stroke-linecap="round"/>`,
      open: `<path d="M41 57 Q50 71 59 57Z" fill="#7a1f2b"/><path d="M44 62 Q50 66 56 62" fill="#ff8da1"/>`,
      flat: `<path d="M43 61 H57" stroke="#7a2e2e" stroke-width="2.6" stroke-linecap="round"/>`,
      tongue: `<path d="M42 58 Q50 66 58 58" fill="none" stroke="#7a2e2e" stroke-width="2.6" stroke-linecap="round"/><path d="M50 62.5 Q50 70 55 68.5 Q57 64 55 61Z" fill="#ff6b81"/>`,
      o: `<ellipse cx="50" cy="61" rx="3.2" ry="4" fill="#7a1f2b"/>`,
    };
    s += M[a.mouth] || M.smile;
    s += iFace;
    // 앞머리
    const H = {
      short: `<path d="M25 48 C20 2 80 2 75 48 C68 36 58 31 50 31 C42 31 32 36 25 48Z" fill="${hc}"/>`,
      spiky: `<path d="M26 46 L24 28 L34 34 L38 18 L46 30 L52 14 L58 30 L66 18 L68 34 L76 28 L74 46 C68 38 58 33 50 33 C42 33 32 38 26 46Z" fill="${hc}"/>`,
      long: `<path d="M25 52 C19 2 81 2 75 52 C70 38 62 31 50 31 C38 31 30 38 25 52Z" fill="${hc}"/>`,
      bun: `<path d="M25 48 C20 2 80 2 75 48 C68 36 58 31 50 31 C42 31 32 36 25 48Z" fill="${hc}"/>`,
      curly: `<g fill="${hc}"><circle cx="30" cy="34" r="9"/><circle cx="42" cy="26" r="9"/><circle cx="55" cy="25" r="9"/><circle cx="68" cy="33" r="9"/><circle cx="24" cy="44" r="6"/><circle cx="76" cy="44" r="6"/></g>`,
    };
    // 모자를 쓰면 머리카락이 머리 모양 밖으로 삐져나오지 않게 잘라요
    if (hairK !== 'none') s += hasHat ? `<defs><clipPath id="pn-hc"><ellipse cx="50" cy="47" rx="27" ry="29"/></clipPath></defs><g clip-path="url(#pn-hc)">${H[hairK] || ''}</g>` : H[hairK] || '';
    s += iHair;
    // 모자
    const hcol = a.hatColor;
    const T = {
      cap: `<path d="M24 38 C26 10 74 10 76 38 Z" fill="${hcol}"/><path d="M66 34 H93 Q93 42 66 41Z" fill="${hcol}"/><path d="M66 34 H93 Q93 42 66 41Z" fill="${dark}"/>`,
      beanie: `<path d="M24 38 C24 10 76 10 76 38 Z" fill="${hcol}"/><rect x="22" y="33" width="56" height="8" rx="4" fill="${dark}"/><circle cx="50" cy="11" r="5" fill="${hcol}"/>`,
      headband: `<path d="M24 36 Q50 24 76 36 L76 42 Q50 30 24 42Z" fill="${hcol}"/>`,
      crown: `<path d="M28 30 L30 10 L40 20 L50 6 L60 20 L70 10 L72 30 Z" fill="#fbbf24" stroke="#d97706" stroke-width="1.5" stroke-linejoin="round"/><circle cx="50" cy="22" r="2.4" fill="#ef4444"/>`,
      wizard: `<path d="M26 34 L50 -4 L74 34 Z" fill="#6d28d9"/><rect x="22" y="31" width="56" height="7" rx="3.5" fill="#4c1d95"/><path d="M48 14 l2 4 4 .5 -3 3 .8 4 -3.8 -2 -3.8 2 .8 -4 -3 -3 4 -.5Z" fill="#fde047"/>`,
    };
    if (a.hat !== 'none' && !iHat) s += T[a.hat] || '';
    s += iHat;
    // 액세서리
    const C = {
      glasses: `<g fill="#bfdbfe" fill-opacity=".35" stroke="#334155" stroke-width="2"><circle cx="40" cy="46" r="7.5"/><circle cx="60" cy="46" r="7.5"/></g><path d="M47.5 46 H52.5" stroke="#334155" stroke-width="2"/>`,
      shades: `<g fill="#111827"><rect x="31" y="40" width="18" height="11" rx="4"/><rect x="51" y="40" width="18" height="11" rx="4"/></g><path d="M49 44 H51" stroke="#111827" stroke-width="2"/>`,
      headphone: `<path d="M24 50 C22 14 78 14 76 50" fill="none" stroke="#475569" stroke-width="4" stroke-linecap="round"/><rect x="19" y="42" width="9" height="16" rx="4" fill="#ef4444"/><rect x="72" y="42" width="9" height="16" rx="4" fill="#ef4444"/>`,
      bow: `<path d="M50 70 L38 63 V77 Z M50 70 L62 63 V77 Z" fill="#ec4899"/><circle cx="50" cy="70" r="3.4" fill="#be185d"/>`,
    };
    if (a.acc !== 'none' && !iFace) s += C[a.acc] || '';
    s += IT(a, 'deco');
    return `<svg class="avsvg" viewBox="0 0 100 100" width="${size}" height="${size}" role="img" aria-label="캐릭터">${s}</svg>`;
  }
  // 프로필 꾸미기 · 캐릭터 정보 (profile_ext) 캐시
  const EXT = new Map();
  let EXT_OK = true;
  async function loadExt(ids) {
    const need = [...new Set((ids || []).filter((x) => x && !EXT.has(x)))];
    for (let i = 0; i < need.length && EXT_OK; i += 150) {
      const part = need.slice(i, i + 150);
      const { data, error } = await sb.from('profile_ext').select('user_id,bio,title,accent,avatar').in('user_id', part);
      if (error) { EXT_OK = false; return; }
      part.forEach((id) => EXT.set(id, null));
      (data || []).forEach((r) => EXT.set(r.user_id, r));
    }
  }
  const avatarOf = (uid) => normAv((EXT.get(uid) || {}).avatar, uid);
  const avatarHtml = (uid, size = 32) => (EXT_OK ? `<span class="av" style="width:${size}px;height:${size}px">${avatarSvg(avatarOf(uid), size)}</span>` : '');
  const myTierIdx = () => (staffRole() ? 99 : tierOf((DIR.get(me.id) || {}).score || 0).i);

  // 알림 (🔔) · DM 안 읽은 수
  let NOTIF_OK = true;
  let notifSeen = null;
  let notifTimer = 0;
  const NOTE_ICON = { dm: '💬', tier: '🎉', notice: '📣' };
  const bnOn = () => { try { return localStorage.getItem('pn_bn') === '1' && 'Notification' in window && Notification.permission === 'granted'; } catch (e) { return false; } };
  function setBadge(sel, n) {
    document.querySelectorAll(sel).forEach((el) => { el.textContent = n > 99 ? '99+' : String(n); el.hidden = !(n > 0); });
  }
  async function pollNotif(first = false) {
    if (!NOTIF_OK || !me || me.status !== 'approved') return;
    const { data, error } = await sb.from('notifications').select('id,kind,title,body,link,cnt,created_at').is('read_at', null).order('id', { ascending: false }).limit(50);
    if (error) { NOTIF_OK = false; return; }
    const list = data || [];
    setBadge('[data-bell]', list.length);
    setBadge('[data-nb="notif"]', list.length);
    const dmN = list.filter((x) => x.kind === 'dm').reduce((s, x) => s + (x.cnt || 1), 0);
    setBadge('[data-nb="dm"]', dmN);
    const top = list.reduce((m, x) => Math.max(m, Number(x.id)), 0);
    if (notifSeen == null || first) { notifSeen = top; return; }
    const fresh = list.filter((x) => Number(x.id) > notifSeen).reverse();
    notifSeen = Math.max(notifSeen, top);
    fresh.forEach((x) => {
      toast(`${NOTE_ICON[x.kind] || '🔔'} ${x.title}`);
      if (bnOn() && document.hidden) { try { new Notification(x.title, { body: x.body || '', tag: 'pn' + x.id }); } catch (e) { /* 일부 브라우저는 지원 안 함 */ } }
    });
    const cur = $('#view');
    if (fresh.length && cur && cur.querySelector('[data-sp="dm"]:not([hidden])')) cur.dispatchEvent(new CustomEvent('pn-dm-refresh'));
  }
  function startNotif() {
    clearInterval(notifTimer);
    NOTIF_OK = true;
    notifSeen = null;
    sb.rpc('tier_check_self').then(() => pollNotif(true), () => pollNotif(true));
    notifTimer = setInterval(() => { if (!document.hidden) pollNotif(); }, 25000);
  }
  document.addEventListener('visibilitychange', () => { if (!document.hidden) pollNotif(); });
  // 가로로 넘치는 탭 줄은 마우스 휠로도 좌우로 움직여요
  document.addEventListener('wheel', (ev) => {
    if (ev.ctrlKey || Math.abs(ev.deltaY) <= Math.abs(ev.deltaX)) return;
    const bar = ev.target && ev.target.closest ? ev.target.closest('.tabs, [class*="tabs"], .tabbar-x') : null;
    if (!bar) return;
    const cs = getComputedStyle(bar);
    if (!/(auto|scroll)/.test(cs.overflowX) || bar.scrollWidth <= bar.clientWidth + 1) return;
    const max = bar.scrollWidth - bar.clientWidth;
    const goingRight = ev.deltaY > 0;
    if ((goingRight && bar.scrollLeft >= max - 1) || (!goingRight && bar.scrollLeft <= 0)) return; // 끝이면 페이지가 스크롤돼요
    bar.scrollLeft += ev.deltaY;
    ev.preventDefault();
  }, { passive: false });
  const nlBr = (t) => esc(t).replace(/\n/g, '<br>');
  const timeAgo = (d) => {
    const s = Math.max(0, (Date.now() - new Date(d).getTime()) / 1000);
    return s < 60 ? '방금' : s < 3600 ? `${Math.floor(s / 60)}분 전` : s < 86400 ? `${Math.floor(s / 3600)}시간 전` : s < 86400 * 7 ? `${Math.floor(s / 86400)}일 전` : fmt(d);
  };
  const DM_ERR = { invalid: '1~1000자로 써주세요', self: '나에게는 보낼 수 없어요', nouser: '받는 사람을 찾을 수 없어요', blocked: '상대가 메시지를 받지 않아요', rate: '너무 빨리 보내고 있어요. 잠시 뒤에 다시 보내주세요' };

  // ---- 설정 탭: 프로필 꾸미기
  async function initProfTab(el) {
    await loadExt([me.id]);
    if (!EXT_OK) { el.innerHTML = `<div class="card pad muted">${SOC_HINT}</div>`; return; }
    const e0 = EXT.get(me.id) || {};
    el.innerHTML = `<div class="card"><h3>✨ 프로필 꾸미기</h3>
      <p class="muted small">내 프로필 화면에 보여요. 다른 학생도 볼 수 있으니 개인정보(전화번호, 학교 등)는 쓰지 마세요.</p>
      <form id="pfForm">
        <label>칭호 <span class="muted small">(최대 16자)</span><input type="text" id="pfTitle" maxlength="16" value="${esc(e0.title || '')}" placeholder="예) 파이썬 입문 중"></label>
        <label>소개 <span class="muted small">(최대 200자)</span><textarea id="pfBio" rows="3" maxlength="200" placeholder="한 줄 소개나 목표를 써보세요">${esc(e0.bio || '')}</textarea></label>
        <label class="inline"><input type="checkbox" id="pfAccOn" ${e0.accent ? 'checked' : ''}> 프로필 포인트 색 <input type="color" id="pfAcc" value="${esc(e0.accent || '#3b82f6')}"></label>
        <div class="form-actions"><button class="primary">저장</button></div>
      </form>
      <h4>미리보기</h4><div id="pfPrev"></div></div>`;
    const prev = () => {
      const acc = $('#pfAccOn', el).checked ? $('#pfAcc', el).value : '';
      $('#pfPrev', el).innerHTML = `<div class="card prof" ${acc ? `style="border-top:5px solid ${esc(acc)}"` : ''}><div class="prof-top">${avatarHtml(me.id, 64)}<div><h3 style="margin:0">${esc(selfName())}</h3>${$('#pfTitle', el).value.trim() ? `<span class="chip" ${acc ? `style="background:${esc(acc)}22;color:${esc(acc)}"` : ''}>${esc($('#pfTitle', el).value.trim())}</span>` : ''}</div></div>${$('#pfBio', el).value.trim() ? `<p class="prof-bio">${nlBr($('#pfBio', el).value.trim())}</p>` : ''}</div>`;
    };
    ['#pfTitle', '#pfBio', '#pfAcc', '#pfAccOn'].forEach((s) => { $(s, el).oninput = prev; $(s, el).onchange = prev; });
    prev();
    $('#pfForm', el).onsubmit = async (ev) => {
      ev.preventDefault();
      const row = { user_id: me.id, title: $('#pfTitle', el).value.trim().slice(0, 16), bio: $('#pfBio', el).value.trim().slice(0, 200), accent: $('#pfAccOn', el).checked ? $('#pfAcc', el).value : null, updated_at: new Date().toISOString() };
      const { error } = await sb.from('profile_ext').upsert(row, { onConflict: 'user_id' });
      if (error) return toast('저장하지 못했어요: ' + error.message, true);
      EXT.set(me.id, { ...(EXT.get(me.id) || {}), ...row });
      toast('프로필을 저장했어요');
    };
  }

  /* ---------- 📝 시험 (v454_exam.sql) ---------- */
  let EX_OFF = 0; // 서버 시계와 내 시계 차이(ms)
  const exNow = () => Date.now() + EX_OFF;
  async function exSync() {
    const t0 = Date.now();
    const { data } = await sb.rpc('exam_clock');
    if (data) EX_OFF = new Date(data).getTime() - (t0 + Date.now()) / 2;
  }
  const exCd = (ms) => { const s = Math.max(0, Math.ceil(ms / 1000)); const h = Math.floor(s / 3600); const m = Math.floor((s % 3600) / 60); return `${h ? h + ':' : ''}${String(m).padStart(h ? 2 : 1, '0')}:${String(s % 60).padStart(2, '0')}`; };
  const exPhase = (e) => {
    const t = exNow(); const s = Date.parse(e.start_at); const en = Date.parse(e.end_at);
    return t < s - e.entry_min * 60000 ? 'soon' : t < s ? 'lobby' : t < en ? 'live' : 'over';
  };
  const EX_PH = { soon: ['🕒 예정', ''], lobby: ['🚪 입장 가능', 'ok'], live: ['🔴 진행 중', 'bad'], over: ['🏁 종료', ''] };
  const exRewardText = (r) => {
    r = r || {};
    const pts = (r.pt_rank || []).map((x, i) => `${i + 1}위 💎${x}`).join(' · ');
    return `${pts || '순위 보상 없음'}${r.pt_join ? ` · 참가 💎${r.pt_join}` : ''}${r.item_first || r.item_top3 || r.item_join ? ' · 🎈 풍선 장식' : ''}`;
  };

  async function pageExam(id) {
    await exSync();
    if (id) return pageExamRoom(Number(id));
    const { data, error } = await sb.rpc('exam_list');
    if (error || !data) return ['<div class="page-head"><h2>📝 시험</h2></div><div class="card pad muted">시험은 아직 준비되지 않았어요. 선생님이 v454_exam.sql 을 실행하면 열려요.</div>'];
    const list = data.exams || [];
    const card = (e) => {
      const ph = exPhase(e); const [t, cls] = EX_PH[ph];
      return `<a class="card ex-card" href="#/exam/${e.id}"><div class="ex-chead"><b>${esc(e.title)}</b><span class="badge ${cls}">${t}${e.status === 'draft' ? ' · 비공개' : ''}</span></div>
        <div class="muted small">🗓️ ${fmt(e.start_at)} 시작 · ⏱ ${e.duration_min}분 · 문제 ${e.n_problems}개 · 응시 ${e.n_entries}명</div>
        <div class="muted small">🎁 ${esc(exRewardText(e.reward))}</div>
        ${e.entered && ph !== 'over' ? '<div class="small" style="color:var(--primary)">✅ 입장했어요</div>' : ''}
        ${e.my_rank ? `<div class="small"><b>내 결과: ${e.my_rank}위 · ${e.my_score}점</b></div>` : ''}</a>`;
    };
    return [`<div class="page-head"><h2>📝 시험</h2></div>
      <p class="muted small">시작 시각에 모두 같이 시작해요. 입장은 시작 전부터 할 수 있어요. 채점은 자동이고, 순위에 따라 💎 와 🎈 풍선 장식을 받아요.</p>
      ${list.length ? list.map(card).join('') : '<div class="card pad center muted">예정된 시험이 없어요.</div>'}`];
  }

  async function pageExamRoom(id) {
    const { data: E0, error } = await sb.rpc('exam_get', { p_id: id });
    if (error || !E0) return [`<p><a href="#/exam">← 시험 목록</a></p><div class="card pad center muted">시험을 찾을 수 없어요.</div>`];
    return [`<p id="exBack"><a href="#/exam">← 시험 목록</a></p><div id="exBox"></div>`, (v) => bindExam(v, E0)];
  }

  function bindExam(v, E0) {
    let E = E0;
    const box = $('#exBox', v);
    let cur = null; let timer = 0; let roomApi = null; let ending = false;
    const alive = () => document.body.contains(box);
    const stop = () => { clearInterval(timer); document.body.classList.remove('exam-on'); };
    const adm = can('content');
    let keepIdx = 0; let lastRev = Date.now();

    const head = () => `<div class="card"><h2 style="margin:0 0 4px">${esc(E.title)}</h2><div class="muted small">🗓️ ${fmt(E.start_at)} ~ ${hhmm(E.end_at)} (${E.duration_min}분) · 문제 ${E.n_problems}개 · 응시 ${E.n_entries}명</div>${E.descr ? `<div style="margin-top:8px">${renderContent(E.descr, true)}</div>` : ''}<div class="muted small" style="margin-top:6px">🎁 ${esc(exRewardText(E.reward))}</div></div>`;

    const refetch = async () => { const { data } = await sb.rpc('exam_get', { p_id: E.id }); if (data) E = data; };

    const drawSoon = () => {
      box.innerHTML = `${head()}<div class="card center ex-wait"><div class="muted">입장은 시작 ${E.entry_min >= 60 ? (E.entry_min / 60) + '시간' : E.entry_min + '분'} 전부터 할 수 있어요</div><div class="ex-big" data-cd="entry">--</div><div class="muted small">${hhmm(Date.parse(E.start_at) - E.entry_min * 60000)} 에 열려요</div></div>`;
    };
    const drawLobby = () => {
      try { jworker().catch(() => {}); } catch (e) { /* 파이썬 미리 준비 */ }
      box.innerHTML = `${head()}<div class="card center ex-wait">
        ${E.entered ? '<div class="ex-ok">✅ 입장 완료!</div><div class="muted">시작되면 문제가 자동으로 열려요. 이 화면을 닫지 마세요.</div>' : '<div class="muted">지금 입장하면 시작 시각에 같이 시작해요.</div>'}
        <div class="ex-big" data-cd="start">--</div>
        ${E.entered ? '' : '<button class="primary" id="exEnter" type="button">🚪 입장하기</button>'}
        <ul class="ex-rules muted small"><li>모든 사람이 같은 시각에 시작하고 같은 시각에 끝나요.</li><li>코드 문제는 자동 채점이에요. 제출은 여러 번 해도 되고, 문제마다 가장 높은 점수가 반영돼요.</li><li>부분 점수가 있어요 (통과한 테스트 비율).</li><li>✍️ 서술형 문제는 선생님이 직접 채점해요. 마지막으로 제출한 답이 채점돼요.</li><li>끝나는 순간 마지막으로 쓴 코드를 자동으로 채점해서 내요.</li></ul></div>`;
      bindEnter();
    };
    const bindEnter = () => {
      const b = $('#exEnter', box);
      if (b) b.onclick = async () => {
        b.disabled = true;
        const { data } = await sb.rpc('exam_enter', { p_id: E.id });
        const M = { early: '아직 입장 시간이 아니에요', closed: '이미 끝난 시험이에요', nouser: '학생 계정만 입장할 수 있어요' };
        if (data !== 'ok') { b.disabled = false; return toast(M[data] || '입장하지 못했어요', true); }
        toast('입장했어요!');
        await refetch(); cur = null; tick(true);
      };
    };

    // ---------- 시험 보는 화면
    const drawLive = () => {
      if (!E.entered && !adm) {
        box.innerHTML = `${head()}<div class="card center ex-wait"><div class="ex-ok">🔴 시험이 시작됐어요!</div><div class="muted">늦게 들어와도 끝나는 시각은 같아요.</div><div class="ex-big" data-cd="end">--</div><button class="primary" id="exEnter" type="button">🚪 지금 입장하기</button></div>`;
        bindEnter(); return;
      }
      const P = E.problems || [];
      if (!P.length) { box.innerHTML = `${head()}<div class="card center ex-wait"><div class="muted">문제를 불러오는 중…</div></div>`; setTimeout(async () => { if (alive()) { await refetch(); cur = null; tick(true); } }, 1200); return; }
      document.body.classList.add('exam-on');
      const sentCode = {}; const best = {};
      const key = (pid) => `pn_exd_${E.id}_${pid}`;
      const code = {};
      P.forEach((p) => {
        const m = (E.mine || {})[p.id];
        let d = null; try { d = localStorage.getItem(key(p.id)); } catch (e) { /* 저장소 막힘 */ }
        code[p.id] = d != null ? d : (m ? m.code : '');
        if (m) { best[p.id] = { passed: m.passed, total: m.total }; sentCode[p.id] = m.code; }
      });
      let kIdx = keepIdx; if (!kIdx) { try { kIdx = Number(localStorage.getItem(`pn_exi_${E.id}`)) || 0; } catch (e) { kIdx = 0; } }
      let idx = Math.max(0, Math.min(kIdx, P.length - 1)); let busy = false; let view = 'prob';
      const isEs = (p) => p.kind === 'essay';
      const sc = (p) => { if (isEs(p)) return 0; const b = best[p.id]; return b && b.total ? Math.floor((p.points * b.passed) / b.total) : 0; };
      const totalSc = () => P.reduce((s, p) => s + sc(p), 0);
      const maxSc = P.filter((p) => !isEs(p)).reduce((s, p) => s + p.points, 0);
      const esPts = P.filter(isEs).reduce((s, p) => s + p.points, 0);
      box.innerHTML = `<div class="ex-top"><b>${esc(E.title)}</b><span class="ex-timer" data-cd="end">--</span><span class="chip" id="exScore"></span><button class="ghost" type="button" id="exList">📋 문제 목록</button></div>
        <div class="ex-room" data-view="prob" id="exRoom">
          <div class="ex-left"><div class="ex-ptabs" id="exTabs"></div><div id="exProb"></div></div>
          <div class="ex-right"><textarea class="code" id="exCode" spellcheck="false" placeholder="여기에 파이썬 코드를 작성하세요"></textarea>
            <details class="ex-in"><summary>직접 실행해 보기 (입력값)</summary><textarea id="exIn" rows="3" placeholder="input() 으로 읽을 값을 줄마다 적어요"></textarea></details>
            <div class="ex-btns"><button class="ghost" id="exRun" type="button">▶ 실행</button><button class="solve" id="exSend" type="button">✅ 채점하고 제출</button></div>
            <div class="judge-out" id="exOut" hidden></div></div></div>
        <div class="ex-bar"><button type="button" data-v="prob">📄<span>문제</span></button><button type="button" data-v="code">⌨️<span>코드</span></button><button type="button" id="bRun">▶<span>실행</span></button><button type="button" id="bSend">✅<span>제출</span></button><button type="button" id="bList">📋<span>목록</span></button></div>`;
      const ta = $('#exCode', box);
      if (window.PYIDE) window.PYIDE.attach(ta);
      const out = $('#exOut', box);
      const showOut = (h) => { out.hidden = false; out.innerHTML = h; };
      const drawScore = () => { $('#exScore', box).textContent = `내 점수 ${totalSc()} / ${maxSc}${esPts ? ` (+서술형 ${esPts}점)` : ''}`; };
      const drawTabs = () => {
        $('#exTabs', box).innerHTML = P.map((p, i) => { const b = best[p.id]; const full = b && b.total && b.passed === b.total; const mark = isEs(p) ? (sentCode[p.id] ? ' ✍️✅' : ' ✍️') : full ? ' ✅' : b ? ' ◐' : ''; return `<button type="button" data-i="${i}" class="${i === idx ? 'on' : ''}">${i + 1}${mark}</button>`; }).join('');
        box.querySelectorAll('[data-i]').forEach((b) => (b.onclick = () => pick(Number(b.dataset.i))));
      };
      const saveCur = () => { code[P[idx].id] = ta.value; try { localStorage.setItem(key(P[idx].id), ta.value); } catch (e) { /* 무시 */ } };
      let firstPick = true;
      const pick = (i) => {
        if (!firstPick) saveCur(); // 맨 처음엔 빈 입력창 값으로 저장된 글을 덮어쓰지 않게
        firstPick = false; idx = i; keepIdx = i; try { localStorage.setItem(`pn_exi_${E.id}`, String(i)); } catch (e) { /* 무시 */ } const p = P[idx];
        $('#exRoom', box).classList.toggle('essay', isEs(p));
        ta.placeholder = isEs(p) ? '여기에 답을 글로 써요 (서술형)' : '여기에 파이썬 코드를 작성하세요';
        $('#exProb', box).innerHTML = `<h3>${idx + 1}. ${esc(p.title || '문제')} <span class="chip">${p.points}점</span></h3><div class="ex-body">${renderContent(p.body || '', true)}</div><p class="muted small">${isEs(p) ? '✍️ 서술형 · 선생님이 채점해요' + (sentCode[p.id] ? ' · 제출함' : '') : `내 점수: ${sc(p)} / ${p.points}`}</p>`;
        ta.value = code[p.id] || '';
        out.hidden = true; drawTabs(); drawScore();
      };
      ta.addEventListener('input', saveCur);
      window.addEventListener('pagehide', () => { try { if (!firstPick) saveCur(); } catch (e) { /* 이미 닫힘 */ } });
      document.addEventListener('visibilitychange', () => { if (document.hidden) { try { if (!firstPick) saveCur(); } catch (e) { /* 이미 닫힘 */ } } });
      const setView = (vw) => { view = vw; $('#exRoom', box).dataset.view = vw; box.querySelectorAll('.ex-bar [data-v]').forEach((b) => b.classList.toggle('on', b.dataset.v === vw)); };
      box.querySelectorAll('.ex-bar [data-v]').forEach((b) => (b.onclick = () => setView(b.dataset.v)));
      setView('prob');
      const lock = (on) => { busy = on; box.querySelectorAll('#exRun,#exSend,#bRun,#bSend').forEach((b) => { b.disabled = on; }); };
      const doSubmit = async (i, silent) => {
        const p = P[i]; const c = i === idx ? ta.value : (code[p.id] || '');
        if (!c.trim()) { if (!silent) toast(isEs(p) ? '답을 입력하세요' : '코드를 입력하세요', true); return null; }
        const tests = p.tests || [];
        if (isEs(p)) {
          const { data: d2 } = await sb.rpc('exam_submit', { p_problem: p.id, p_code: c, p_passed: 0, p_total: 0 });
          if (d2 && d2.status === 'ok') { sentCode[p.id] = c; best[p.id] = { passed: 0, total: 0 }; drawTabs(); drawScore(); }
          return { res: { status: 'ES', passed: 0, total: 0 }, st: d2 && d2.status };
        }
        if (!silent) showOut('<span class="muted">⏳ 채점 중… (처음 한 번은 파이썬 준비로 몇 초 걸려요)</span>');
        const res = await gradeAll(c, tests, (k, n) => { if (!silent) showOut(`<span class="muted">⏳ 채점 중… ${k + 1} / ${n}</span>`); });
        const { data } = await sb.rpc('exam_submit', { p_problem: p.id, p_code: c, p_passed: res.passed, p_total: res.total });
        const st = data && data.status;
        if (st === 'ok') {
          sentCode[p.id] = c;
          const b = best[p.id];
          if (!b || res.total === 0 || res.passed / (res.total || 1) >= b.passed / (b.total || 1)) best[p.id] = { passed: res.passed, total: res.total };
          drawTabs(); drawScore();
        }
        return { res, st };
      };
      const sendBtn = async () => {
        if (busy) return; lock(true);
        try {
          const r = await doSubmit(idx, false);
          if (r) {
            const M = { closed: '시험이 끝났어요', early: '아직 시작 전이에요', nouser: adm ? '관리자는 제출이 기록되지 않아요 (채점 결과만 보여요)' : '제출하지 못했어요', limit: '제출 횟수 한도를 넘었어요' };
            const p = P[idx];
            if (r.res.status === 'ES') { showOut(`<div class="jsum ${r.st === 'ok' ? 'ok' : 'bad'}"><b>${r.st === 'ok' ? '✅ 답안을 제출했어요' : '⚠️ ' + (M[r.st] || '제출하지 못했어요')}</b> · 고쳐 쓰고 다시 내면 마지막 답이 채점돼요</div>`); pick(idx); }
            else {
            showOut(`<div class="jsum ${r.res.status === 'AC' ? 'ok' : 'bad'}"><b>${r.res.status === 'AC' ? '✅ 모두 통과!' : `❌ ${r.res.passed} / ${r.res.total} 통과`}</b> · 이 문제 ${sc(p)} / ${p.points}점${r.st && r.st !== 'ok' ? ` · ⚠️ ${M[r.st] || '기록 실패'}` : ' · 제출 완료'}</div>${casesHtml(r.res)}`);
            pick(idx);
            showOut(out.innerHTML);
            }
          }
        } catch (e) { showOut(`<div class="jsum bad">⚠️ ${esc(e.message || e)}</div>`); }
        lock(false);
      };
      const runBtn = async () => {
        if (busy) return;
        if (!ta.value.trim()) return toast('코드를 입력하세요', true);
        lock(true); showOut('<span class="muted">⏳ 실행 중…</span>');
        const r = await runOnce(ta.value, ($('#exIn', box).value || '').replace(/\n?$/, '\n'));
        showOut(renderRun(r)); lock(false);
        if (view === 'code') out.scrollIntoView({ block: 'nearest' });
      };
      $('#exSend', box).onclick = sendBtn; $('#bSend', box).onclick = sendBtn;
      $('#exRun', box).onclick = runBtn; $('#bRun', box).onclick = runBtn;
      const openList = () => {
        const m = modal(`<h3>📋 문제 목록</h3><div class="list">${P.map((p, i) => `<button type="button" class="row ex-lrow" data-go="${i}"><div class="row-main"><b>${i + 1}. ${esc(p.title || '문제')}</b></div><div class="muted small">${isEs(p) ? (sentCode[p.id] ? '✍️ 제출함' : '✍️ 서술형') : `${sc(p)} / ${p.points}점`}</div></button>`).join('')}</div><p><b>합계 ${totalSc()} / ${maxSc}점</b>${esPts ? ` <span class="muted small">(+서술형 ${esPts}점)</span>` : ''}</p>`);
        m.el.querySelectorAll('[data-go]').forEach((b) => (b.onclick = () => { m.close(); pick(Number(b.dataset.go)); setView('prob'); }));
      };
      $('#exList', box).onclick = openList; $('#bList', box).onclick = openList;
      pick(idx);
      roomApi = {
        save: () => saveCur(),
        // 시간이 다 되면 아직 안 낸 코드를 채점해서 내요
        async finish(msg) {
          saveCur();
          const need = P.map((p, i) => i).filter((i) => (code[P[i].id] || '').trim() && code[P[i].id] !== sentCode[P[i].id]);
          if (!need.length) return;
          msg('⏳ 마지막 코드를 채점해서 내는 중…');
          const t0 = Date.now();
          for (const i of need) {
            if (Date.now() - t0 > 11000) break;
            try { await doSubmit(i, true); } catch (e) { /* 다음 문제 */ }
          }
        },
      };
    };

    // ---------- 결과 화면
    const drawOver = async () => {
      document.body.classList.remove('exam-on');
      if (!E.entered && !adm) { box.innerHTML = `${head()}<div class="card center muted pad">이 시험은 끝났어요. 응시하지 않았어요.</div>`; return; }
      box.innerHTML = `${head()}<div class="card center muted pad" id="exRes">📊 결과를 정리하는 중…</div>`;
      let b = null;
      for (let k = 0; alive(); k += 1) {
        const { data } = await sb.rpc('exam_board', { p_id: E.id });
        if (data && data.ready) { b = data; break; }
        if (data && data.grading) { const el = $('#exRes', box); if (el) el.innerHTML = '✍️ 선생님이 서술형 문제를 채점하고 있어요.<br><span class="small">채점이 끝나면 순위가 나와요. 이 화면은 자동으로 바뀌어요.</span>'; }
        else if (k >= 20) break;
        await new Promise((r) => setTimeout(r, data && data.grading ? 10000 : 2500));
      }
      if (!b || !alive()) return;
      const [rv] = await Promise.all([Promise.resolve(sb.rpc('exam_review', { p_id: E.id })).then((r) => (r && r.data) || [], () => [])]);
      growRefresh(true); loadItems();
      const me = (b.rows || []).find((r) => r.me);
      const meHtml = me ? `<div class="card center ex-me"><div class="muted">내 결과</div><div class="ex-big">${me.rank}위 <span class="muted small">/ ${b.n}명</span></div><div><b>${me.score}점</b> · 푼 문제 ${me.solved}개</div><div class="muted small">🎁 ${esc(exRewardText(E.reward))}</div>
        <label class="inline" style="justify-content:center;margin-top:8px"><input type="checkbox" id="exPub" ${E.public === false ? '' : 'checked'}> 내 이름과 점수를 순위표에 공개</label></div>` : `<div class="card center muted pad">${adm ? '관리자 보기예요.' : '순위가 없어요 (제출한 기록이 없어요).'}</div>`;
      const rows = (b.rows || []).map((r) => `<div class="row ex-rrow${r.me ? ' me' : ''}"><div class="row-main"><span class="ex-rk">${r.rank <= 3 ? ['🥇', '🥈', '🥉'][r.rank - 1] : r.rank}</span> ${r.hidden && !r.me ? '<span class="muted">🔒 비공개</span>' : `<b>${esc(r.name || '')}</b>${r.hidden ? ' <span class="muted small">(나만 보여요)</span>' : ''}`}</div><div><b>${r.score}</b><span class="muted small">점 · ${r.solved}문제</span></div></div>`).join('') || '<p class="muted center pad">참가자가 없어요.</p>';
      box.innerHTML = `${head()}${meHtml}<div class="card list"><h3 style="padding:14px 18px 0;margin:0">🏆 순위표</h3>${rows}</div>
        ${rv.length ? `<div class="card"><h3>📄 문제와 내 풀이</h3>${rv.map((r, i) => { const p = (E.problems || []).find((x) => x.id === r.problem_id) || {}; return `<details class="ex-rv"><summary><b>${i + 1}. ${esc(r.title || '문제')}</b> <span class="muted small">${r.kind === 'essay' ? '✍️ ' : ''}내 점수 ${r.graded === false ? '채점 전' : r.score} / ${r.points}</span></summary><div class="ex-body">${renderContent(p.body || '', true)}</div>${r.code ? `<div class="muted small">${r.kind === 'essay' ? '내 답안' : '내 최고 점수 코드'}</div><pre><code>${esc(r.code)}</code></pre>` : '<p class="muted small">제출한 코드가 없어요.</p>'}</details>`; }).join('')}</div>` : ''}`;
      const pub = $('#exPub', box);
      if (pub) pub.onchange = async () => {
        const { data } = await sb.rpc('exam_set_public', { p_id: E.id, p_on: pub.checked });
        toast(data === 'ok' ? (pub.checked ? '순위표에 공개했어요' : '비공개로 바꿨어요') : '바꾸지 못했어요', data !== 'ok');
        E.public = pub.checked; drawOver();
      };
    };

    const tick = async (force) => {
      const ph = exPhase(E);
      if (ph !== cur || force) {
        const prev = cur;
        cur = ph;
        if (prev === 'live' && ph === 'over' && roomApi && !ending) {
          ending = true;
          box.insertAdjacentHTML('afterbegin', '<div class="ex-over" id="exOverMsg">⏰ 시험 종료!</div>');
          await roomApi.finish((m) => { const el = $('#exOverMsg', box); if (el) el.textContent = m; });
          roomApi = null; ending = false;
        }
        if (ph === 'live' || ph === 'over') await refetch();
        if (!alive()) return;
        if (ph === 'soon') drawSoon(); else if (ph === 'lobby') drawLobby(); else if (ph === 'live') drawLive(); else drawOver();
      }
      if (cur === 'live' && roomApi && Date.now() - lastRev > 25000) {
        lastRev = Date.now();
        try {
          const { data: rv2 } = await sb.rpc('exam_rev', { p_id: E.id });
          if (typeof rv2 === 'number' && rv2 !== E.rev && roomApi) {
            roomApi.save(); await refetch();
            if (alive()) { cur = null; toast('📣 선생님이 문제를 고쳤어요! 화면이 새로 바뀌었어요', false); tick(true); return; }
          }
        } catch (e) { /* 다음에 다시 */ }
      }
      const t = exNow();
      box.querySelectorAll('[data-cd]').forEach((el) => {
        const k = el.dataset.cd;
        const target = k === 'entry' ? Date.parse(E.start_at) - E.entry_min * 60000 : k === 'start' ? Date.parse(E.start_at) : Date.parse(E.end_at);
        el.textContent = exCd(target - t);
        if (k === 'end') el.classList.toggle('warn', target - t < 300000);
      });
    };
    tick(true);
    timer = setInterval(() => { if (!alive()) { stop(); return; } tick(false); }, 500);
  }

  /* ---------- 🛍️ 마켓 (학생 마켓 · 상점 · 내 상품) ---------- */
  async function pageMarket(tabKey) {
    const tabs = [['', '🛍️ 학생 마켓'], ['shop', '🏪 상점'], ['mine', '✏️ 내 상품']];
    const tk = tabs.some(([k]) => k === tabKey) ? tabKey : '';
    await loadExt([me.id]);
    if (!ITEMS.size) await loadItems();
    const av = normAv((EXT.get(me.id) || {}).avatar, me.id);
    let cat = null;
    const loadCat = async () => { const { data, error } = await sb.rpc('item_catalog'); cat = error || !data ? null : data; };
    await loadCat();
    const head = `<div class="page-head"><h2>🛍️ 마켓</h2><span class="chip" id="mkPy">💎 ${cat ? cat.py : 0}</span></div>
      <div class="tabs it-tabs mk-tabs">${tabs.map(([k, n]) => `<a class="${k === tk ? 'on' : ''}" href="#/market${k ? '/' + k : ''}">${n}</a>`).join('')}</div>`;
    if (!cat) return [`${head}<div class="card pad muted">마켓은 아직 준비되지 않았어요. 선생님이 v451b · v452 SQL 을 실행하면 열려요.</div>`];
    if (tk === 'mine') {
      return [`${head}<div class="card"><div id="mkMine"></div></div>`, (v) => {
        const again = async () => { await Promise.all([loadCat(), loadItems()]); renderMyProducts($('#mkMine', v), av, again); };
        renderMyProducts($('#mkMine', v), av, again);
      }];
    }
    let slot = ''; let sort = 'hot'; let q = '';
    const pool = () => cat.items.filter((i) => ITEMS.has(i.id) && (tk === 'shop' ? !i.market && (i.kind === 'price' || (i.kind === 'event' && i.price > 0)) : i.market));
    return [`${head}
      <p class="muted small">${tk === 'shop' ? '파이포인트(💎)로 살 수 있는 선생님 상점이에요.' : '친구들이 직접 그린 아이템이에요. 팔리면 만든 친구에게 💎 가 들어가요!'}</p>
      <div class="mk-bar"><div class="bd-tabs" id="mkSlots"></div>
        <select id="mkSort" aria-label="정렬"><option value="hot">🔥 인기순</option><option value="low">💎 낮은 가격</option><option value="high">💎 높은 가격</option><option value="name">가나다</option></select>
        <input type="search" id="mkQ" class="bd-q" placeholder="이름 검색" autocomplete="off"></div>
      <div class="it-grid mk-grid" id="mkGrid"></div>`,
    (v) => {
      const draw = () => {
        const all = pool();
        $('#mkSlots', v).innerHTML = [['', '전체', '']].concat(ITEM_SLOTS).map(([k, n, ic]) => `<a href="#" data-sl="${k}" class="${k === slot ? 'on' : ''}">${ic} ${n}${k ? ` ${all.filter((i) => i.slot === k).length}` : ` ${all.length}`}</a>`).join('');
        let list = all.filter((i) => (!slot || i.slot === slot) && (!q || (i.name || '').toLowerCase().includes(q)));
        list = list.slice().sort(sort === 'low' ? (a, b) => a.price - b.price : sort === 'high' ? (a, b) => b.price - a.price : sort === 'name' ? (a, b) => String(a.name).localeCompare(String(b.name), 'ko') : (a, b) => (b.sales || 0) - (a.sales || 0) || b.price - a.price);
        $('#mkGrid', v).innerHTML = list.map((i) => {
          const mine = i.creator === me.id;
          const st = mine ? '내 상품' : i.owned ? '보유 중' : `💎 ${i.price}`;
          return `<button type="button" class="it-tile ${i.owned ? 'own' : cat.py >= i.price ? 'can' : 'lock'}" data-mk="${esc(i.id)}" title="${esc(i.descr || i.name)}"><span class="it-pv">${avatarSvg({ ...av, items: { ...av.items, [i.slot]: i.id } }, 64)}</span><b>${esc(i.name)}</b>${i.market && i.creator ? `<span class="it-by">by ${esc(dname(i.creator, '친구'))}${i.sales ? ` · ${i.sales}개 판매` : ''}</span>` : ''}<span class="it-st">${st}</span></button>`;
        }).join('') || '<p class="muted center pad" style="grid-column:1/-1">조건에 맞는 아이템이 없어요.</p>';
        v.querySelectorAll('[data-sl]').forEach((a) => (a.onclick = (e) => { e.preventDefault(); slot = a.dataset.sl; draw(); }));
        v.querySelectorAll('[data-mk]').forEach((b) => (b.onclick = () => open(cat.items.find((x) => x.id === b.dataset.mk))));
      };
      const open = (i) => {
        if (!i) return;
        const mine = i.creator === me.id;
        const can = !i.owned && !mine && !staffRole();
        const m = modal(`<h3>${esc(i.name)}</h3>
          <div class="mk-big">${avatarSvg({ ...av, items: { ...av.items, [i.slot]: i.id } }, 200)}</div>
          <p class="muted small center">내 캐릭터가 입어본 모습이에요</p>
          ${i.descr ? `<p>${esc(i.descr)}</p>` : ''}
          <p class="muted small">${esc((ITEM_SLOTS.find(([k]) => k === i.slot) || [])[1] || i.slot)}${i.creator ? ` · by ${esc(dname(i.creator, '친구'))}` : ''}${i.sales ? ` · ${i.sales}개 판매` : ''}</p>
          <div class="form-actions"><button class="ghost" id="mkClose" type="button">닫기</button>${can ? `<button class="primary" id="mkBuy" type="button">💎 ${i.price} 에 사기</button>` : `<a class="btn" href="#/me/avatar">${i.owned || mine ? '👕 입으러 가기' : ''}</a>`}</div>`);
        $('#mkClose', m.el).onclick = () => m.close();
        const bb = $('#mkBuy', m.el);
        if (bb) bb.onclick = async () => {
          if (cat.py < i.price) return toast('파이포인트가 부족해요', true);
          bb.disabled = true;
          const { data: r, error } = await sb.rpc('item_buy', { p_item: i.id });
          if (error) { bb.disabled = false; return toast('사지 못했어요: ' + error.message, true); }
          toast(r === 'ok' ? `🛍️ ${i.name} 을(를) 샀어요!` : r === 'poor' ? '파이포인트가 부족해요' : r === 'have' ? '이미 가지고 있어요' : '사지 못했어요', r !== 'ok');
          m.close();
          growRefresh(true);
          await loadCat();
          const py = $('#mkPy', v); if (py) py.textContent = `💎 ${cat.py}`;
          draw();
        };
      };
      $('#mkSort', v).onchange = (e) => { sort = e.target.value; draw(); };
      $('#mkQ', v).oninput = (e) => { q = e.target.value.trim().toLowerCase(); draw(); };
      draw();
    }];
  }

  async function renderMyProducts(m, av, again) {
    m.innerHTML = '<p class="muted small">불러오는 중…</p>';
    const { data, error } = await sb.rpc('market_mine');
    if (error) { m.innerHTML = '<p class="muted small">마켓은 아직 준비되지 않았어요. (관리자가 v452_market_events.sql 을 실행하면 열려요)</p>'; return; }
    const list = data || [];
    const ST = { pending: '⏳ 심사 중', active: '🛍️ 판매 중', rejected: '❌ 반려', hidden: '내림' };
    m.innerHTML = `<p class="muted small">내가 그린 아이템을 올리면 선생님이 확인한 뒤 마켓에 올라가요. 팔릴 때마다 <b>가격의 80%</b>가 내 파이포인트로 들어와요 (수수료 20%).</p>
      <button class="primary" id="mkNew" type="button">✏️ 새 아이템 올리기</button>
      <div class="mk-list">${list.map((x) => `<div class="mk-row"><span class="it-pv">${itemPreview(x.slot, x.svg, 64, av)}</span><div class="mk-info"><b>${esc(x.name)}</b> <span class="chip">${ST[x.status] || x.status}</span><br><span class="muted small">${esc((ITEM_SLOTS.find(([k]) => k === x.slot) || [])[1] || x.slot)} · 💎 ${x.price} · ${x.sales}개 판매 · 수익 💎 ${x.earned}${x.note ? ` · 반려 사유: ${esc(x.note)}` : ''}</span></div><div>${x.status === 'pending' || x.status === 'rejected' ? `<button class="ghost" data-mkedit="${esc(x.id)}" type="button">수정</button> ` : ''}${x.status === 'active' || x.status === 'pending' ? `<button class="ghost" data-mkoff="${esc(x.id)}" type="button">내리기</button>` : ''}</div></div>`).join('') || '<p class="muted small">아직 올린 아이템이 없어요.</p>'}</div>`;
    $('#mkNew', m).onclick = () => openMarketForm(null, av, again);
    m.querySelectorAll('[data-mkedit]').forEach((b) => (b.onclick = () => openMarketForm(list.find((x) => x.id === b.dataset.mkedit), av, again)));
    m.querySelectorAll('[data-mkoff]').forEach((b) => (b.onclick = async () => {
      if (!confirm('마켓에서 내릴까요? (이미 산 친구들은 계속 쓸 수 있어요)')) return;
      await sb.rpc('market_withdraw', { p_id: b.dataset.mkoff });
      again();
    }));
    }

  // ---- 설정 탭: 캐릭터 꾸미기
  async function initAvatarTab(el) {
    await loadExt([me.id]);
    if (!EXT_OK) { el.innerHTML = `<div class="card pad muted">${SOC_HINT}</div>`; return; }
    const saved = (EXT.get(me.id) || {}).avatar;
    let av = normAv(saved, me.id);
    const tIdx = myTierIdx();
    const SW = [['skin', '피부', AV.skin], ['hairColor', '머리 색', AV.hairColor], ['bg', '배경', AV.bg], ['outfitColor', '옷 색', AV.outfitColor], ['hatColor', '모자 색', AV.outfitColor]];
    const OP = [['hair', '머리 모양', AV.hair], ['eyes', '눈', AV.eyes], ['mouth', '입', AV.mouth], ['outfit', '옷', AV.outfit], ['hat', '모자', AV.hat], ['acc', '소품', AV.acc]];
    el.innerHTML = `<div class="card"><h3>🧑‍🎤 캐릭터 꾸미기</h3>
      <p class="muted small">랭킹·프로필·메시지에 내 캐릭터가 보여요. 티어가 오르면 새 모자와 소품이 열려요!</p>
      <div class="av-ed"><div class="av-prev" id="avPrev"></div><div class="av-ctl" id="avCtl"></div></div>
      <div id="avItems" class="av-items"></div>
      <div class="form-actions"><button class="ghost" id="avRand" type="button">🎲 랜덤</button><button class="ghost" id="avUndo" type="button">되돌리기</button><button class="primary" id="avSave" type="button">저장</button></div></div>`;
    let cat = null; // 아이템 목록 (item_catalog)
    let tab = 'hat';
    const REPL = { hair: 'hair', hat: 'hat', acc: 'face' }; // 아이템을 입으면 기본 모양이 사라지는 자리
    const CATS = [
      { k: 'look', n: '🎨 피부·배경', sw: ['skin', 'bg'] },
      { k: 'hair', n: '💇 머리', sw: ['hairColor'], op: 'hair', slots: ['hair'] },
      { k: 'eyes', n: '👀 눈', op: 'eyes' },
      { k: 'mouth', n: '👄 입', op: 'mouth' },
      { k: 'outfit', n: '👕 옷', sw: ['outfitColor'], op: 'outfit', slots: ['outfit'] },
      { k: 'hat', n: '🎩 모자', sw: ['hatColor'], op: 'hat', slots: ['hat'] },
      { k: 'acc', n: '😎 얼굴·소품', op: 'acc', slots: ['face', 'deco'] },
      { k: 'back', n: '🪽 뒤', slots: ['back'] },
    ];
    const lockTxt = (i) => (i.kind === 'score' ? `🔒 ${Number(i.val).toLocaleString()}점` : i.kind === 'tier' ? `🔒 ${esc((TIERS[i.val] || {}).n || '티어')}` : i.kind === 'streak' ? `🔒 ${i.val}일 연속` : i.kind === 'rank1' ? `🔒 1등 ${i.val}회` : i.kind === 'reward' ? '🏅 특별 보상' : i.kind === 'event' ? '🎪 행사 한정' : '🔒');
    const itemTile = (i) => {
      const on = av.items[i.slot] === i.id;
      const buyable = i.kind === 'price' || (i.kind === 'event' && i.ev && i.price > 0);
      const st = on ? '착용 중' : i.owned ? '입기' : i.can_claim ? '🎁 받기' : buyable ? `💎 ${i.price}${i.kind === 'event' ? ' 🎪' : ''}` : lockTxt(i);
      const cls = on ? 'on' : i.owned ? 'own' : i.can_claim || (buyable && cat.py >= i.price) ? 'can' : 'lock';
      return `<button type="button" class="it-tile ${cls}" data-it="${esc(i.id)}" title="${esc(i.descr || i.name)}"><span class="it-pv">${avatarSvg({ ...av, items: { ...av.items, [i.slot]: i.id } }, 56)}</span><b>${esc(i.name)}</b>${i.market && i.creator ? `<span class="it-by">by ${esc(dname(i.creator, '친구'))}</span>` : ''}<span class="it-st">${st}</span></button>`;
    };
    const dropItem = (slot) => { const n = { ...av.items }; delete n[slot]; av = { ...av, items: n }; };
    const drawItems = () => {
      const box = $('#avItems', el);
      if (!box) return;
      if (!cat) { box.innerHTML = '<p class="muted small">아이템은 관리자가 v451 · v452 SQL 을 실행하면 열려요.</p>'; return; }
      const claimable = cat.items.filter((i) => !i.owned && i.can_claim);
      box.innerHTML = `<p class="muted small">💎 ${cat.py} · ${Number(cat.score).toLocaleString()}점 · 🔥 최고 ${cat.streak || 0}일 · 🥇 ${cat.wins || 0}회 · <a href="#/market">🛍️ 마켓 가기</a></p>
        ${claimable.length ? `<button type="button" class="primary" id="itAll">🎁 받을 수 있는 아이템 ${claimable.length}개 모두 받기</button>` : ''}`;
      const all = $('#itAll', box);
      if (all) all.onclick = async () => {
        all.disabled = true;
        let ok = 0;
        for (const i of claimable) { const { data } = await sb.rpc('item_claim', { p_item: i.id }); if (data === 'ok') ok += 1; }
        toast(`🎁 ${ok}개를 받았어요!`);
        await loadCat(); draw();
      };
    };
    const itemClick = async (id) => {
      const i = cat && cat.items.find((x) => x.id === id);
      if (!i) return;
      if (i.owned) {
        if (av.items[i.slot] === i.id) dropItem(i.slot); else av = { ...av, items: { ...av.items, [i.slot]: i.id } };
        return draw();
      }
      if (i.can_claim) {
        const { data: r, error } = await sb.rpc('item_claim', { p_item: i.id });
        if (error || r !== 'ok') return toast('받지 못했어요', true);
        toast(`🎁 ${i.name} 을(를) 받았어요!`);
      } else if (i.kind === 'price' || (i.kind === 'event' && i.ev && i.price > 0)) {
        if (cat.py < i.price) return toast('파이포인트가 부족해요', true);
        if (!confirm(`${i.name} 을(를) 💎 ${i.price} 에 살까요?`)) return;
        const { data: r, error } = await sb.rpc('item_buy', { p_item: i.id });
        if (error) return toast('사지 못했어요: ' + error.message, true);
        toast(r === 'ok' ? `🛍️ ${i.name} 을(를) 샀어요!` : r === 'poor' ? '파이포인트가 부족해요' : r === 'have' ? '이미 가지고 있어요' : '사지 못했어요', r !== 'ok');
        growRefresh(true);
      } else return toast(i.kind === 'reward' ? '특별 문제를 풀면 받을 수 있어요' : '조건을 채우면 열려요');
      await loadCat(); draw();
    };
    const loadCat = async () => {
      const { data, error } = await sb.rpc('item_catalog');
      cat = error || !data ? null : data;
    };
    const draw = () => {
      drawItems();
      $('#avPrev', el).innerHTML = avatarSvg(av, 150);
      const C = CATS.find((x) => x.k === tab) || CATS[0];
      const swHtml = (C.sw || []).map((k) => { const row = SW.find((x) => x[0] === k); return `<div class="av-row"><b>${row[1]}</b><div class="av-sw">${row[2].map((c) => `<button type="button" class="swatch ${av[k] === c ? 'on' : ''}" data-sw="${k}" data-v="${c}" style="background:${c}" aria-label="${row[1]} ${c}"></button>`).join('')}</div></div>`; }).join('');
      let grid = '';
      if (C.op) {
        const list = OP.find((x) => x[0] === C.op)[2];
        const rs = REPL[C.op];
        grid += list.map(([v, nm, need]) => {
          const lock = need != null && tIdx < need;
          const on = av[C.op] === v && !(rs && av.items[rs]);
          const pv = avatarSvg({ ...av, [C.op]: v, items: rs ? Object.fromEntries(Object.entries(av.items).filter(([k]) => k !== rs)) : av.items }, 56);
          return `<button type="button" class="it-tile ${on ? 'on' : lock ? 'lock' : 'own'}" data-op="${C.op}" data-v="${v}" ${lock ? 'disabled' : ''} title="${esc(nm)}"><span class="it-pv">${pv}</span><b>${esc(nm.replace(/ \(.*\)$/, ''))}</b><span class="it-st">${on ? '착용 중' : lock ? '🔒 티어' : '입기'}</span></button>`;
        }).join('');
      }
      if (cat) {
        (C.slots || []).forEach((sl) => {
          const items = cat.items.filter((i) => i.slot === sl && ITEMS.has(i.id) && (!i.market || i.owned));
          if (!(C.op && REPL[C.op] === sl)) grid += `<button type="button" class="it-tile ${av.items[sl] ? 'own' : 'on'}" data-it-none="${sl}"><span class="it-pv">🚫</span><b>${C.slots.length > 1 ? (ITEM_SLOTS.find((x) => x[0] === sl) || [])[1] + ' 벗기' : '벗기'}</b><span class="it-st">${av.items[sl] ? '벗기' : '없음'}</span></button>`;
          grid += items.map(itemTile).join('');
        });
      }
      $('#avCtl', el).innerHTML = `<div class="tabs it-tabs av-cats">${CATS.map((x) => `<button type="button" data-cat="${x.k}" class="${x.k === tab ? 'on' : ''}">${x.n}</button>`).join('')}</div>${swHtml}${grid ? `<div class="it-grid">${grid}</div>` : ''}${C.slots && !cat ? '<p class="muted small">🎁 아이템은 선생님이 SQL 을 실행하면 열려요.</p>' : ''}<p class="muted small">🎁 받기 · 💎 사기 · 🔒 잠김. 저장을 눌러야 적용돼요.</p>`;
      el.querySelectorAll('[data-cat]').forEach((b) => (b.onclick = () => { tab = b.dataset.cat; draw(); }));
      el.querySelectorAll('[data-sw]').forEach((b) => (b.onclick = () => { av[b.dataset.sw] = b.dataset.v; draw(); }));
      el.querySelectorAll('[data-op]').forEach((b) => (b.onclick = () => { av[b.dataset.op] = b.dataset.v; if (REPL[b.dataset.op]) dropItem(REPL[b.dataset.op]); draw(); }));
      el.querySelectorAll('[data-it-none]').forEach((b) => (b.onclick = () => { dropItem(b.dataset.itNone); draw(); }));
      el.querySelectorAll('[data-it]').forEach((b) => (b.onclick = () => itemClick(b.dataset.it)));
    };
    draw();
    loadCat().then(draw);
    $('#avRand', el).onclick = () => {
      const r = (arr) => arr[Math.floor(Math.random() * arr.length)];
      const ok = (list) => list.filter(([, , need]) => need == null || tIdx >= need).map((x) => x[0]);
      const keepItems = av.items;
      av = { items: keepItems, skin: r(AV.skin), hairColor: r(AV.hairColor), outfitColor: r(AV.outfitColor), bg: r(AV.bg), hatColor: r(AV.outfitColor), hair: r(ok(AV.hair).filter((v) => v !== 'none')), eyes: r(ok(AV.eyes)), mouth: r(ok(AV.mouth)), outfit: r(ok(AV.outfit)), hat: r(['none', ...ok(AV.hat)]), acc: r(['none', ...ok(AV.acc)]) };
      draw();
    };
    $('#avUndo', el).onclick = () => { av = normAv(saved, me.id); draw(); };
    $('#avSave', el).onclick = async () => {
      const row = { user_id: me.id, avatar: av, updated_at: new Date().toISOString() };
      const { error } = await sb.from('profile_ext').upsert(row, { onConflict: 'user_id' });
      if (error) return toast('저장하지 못했어요: ' + error.message, true);
      EXT.set(me.id, { ...(EXT.get(me.id) || {}), avatar: { ...av } });
      toast('캐릭터를 저장했어요');
    };
  }

  // ---- 설정 탭: 메시지(DM)
  async function initDmTab(el, openUid) {
    let contacts = [];
    let cur = null; // { uid, name, staff, blocked }
    el.innerHTML = '<div class="card"><p class="muted small">불러오는 중…</p></div>';
    const { data: cs, error: ce } = await sb.rpc('dm_contacts');
    if (ce) { el.innerHTML = `<div class="card pad muted">${SOC_HINT}</div>`; return; }
    contacts = cs || [];
    await loadExt(contacts.map((c) => c.user_id));
    const byId = (id) => contacts.find((c) => c.user_id === id);
    const sTag = (s) => (s ? `<span class="badge">${s === 'owner' ? '선생님' : esc(ROLE_NAME[s] || s)}</span>` : '');
    el.innerHTML = `<div class="card dm-card">
      <div class="dm-note">🔒 <b>선생님이 대화 내용을 볼 수 있어요.</b> 비밀번호·전화번호 같은 개인정보는 보내지 마세요. 보낸 메시지는 지울 수 없어요.</div>
      <div class="dm-wrap"><div class="dm-side" id="dmSide"></div><div class="dm-main" id="dmMain"><p class="muted center pad">왼쪽에서 대화를 고르거나 새 대화를 시작해요.</p></div></div></div>`;
    const side = $('#dmSide', el); const main = $('#dmMain', el);
    const wrap = $('.dm-wrap', el);
    async function drawSide() {
      const { data, error } = await sb.rpc('dm_inbox');
      const items = error ? [] : data || [];
      side.innerHTML = `<button class="primary dm-new" id="dmNew" type="button">✏️ 새 대화</button>
        <div id="dmPick" hidden><input type="search" id="dmQ" placeholder="이름 검색" autocomplete="off"><div class="dm-pick" id="dmPickList"></div></div>
        <div class="dm-list">${items.map((x) => `<button type="button" class="dm-item ${cur && cur.uid === x.other ? 'on' : ''}" data-u="${x.other}">${avatarHtml(x.other, 34)}<span class="dm-it"><b>${esc(x.name || '?')}</b> ${sTag(x.staff)}<br><span class="muted small">${x.last_mine ? '나: ' : ''}${esc(x.last_body)}</span></span>${x.unread > 0 ? `<span class="nbadge">${x.unread}</span>` : ''}</button>`).join('') || '<p class="muted small pad">아직 대화가 없어요.</p>'}</div>`;
      side.querySelectorAll('[data-u]').forEach((b) => (b.onclick = () => openThread(b.dataset.u)));
      $('#dmNew', side).onclick = () => {
        const p = $('#dmPick', side); p.hidden = !p.hidden;
        if (!p.hidden) { $('#dmQ', side).focus(); fillPick(''); }
      };
      $('#dmQ', side).oninput = (ev) => fillPick(ev.target.value);
    }
    function fillPick(q) {
      const k = q.trim().toLowerCase();
      const list = contacts.filter((c) => !k || String(c.name).toLowerCase().includes(k)).slice(0, 40);
      const box = $('#dmPickList', side);
      box.innerHTML = list.map((c) => `<button type="button" class="dm-item" data-pu="${c.user_id}">${avatarHtml(c.user_id, 28)}<span class="dm-it"><b>${esc(c.name)}</b> ${sTag(c.staff)}</span></button>`).join('') || '<p class="muted small pad">없어요</p>';
      box.querySelectorAll('[data-pu]').forEach((b) => (b.onclick = () => { $('#dmPick', side).hidden = true; openThread(b.dataset.pu); }));
    }
    async function loadThread(scroll) {
      if (!cur) return;
      const { data, error } = await sb.rpc('dm_thread', { p_other: cur.uid });
      const box = $('#dmMsgs', main);
      if (!box) return;
      if (error) { box.innerHTML = '<p class="muted center pad">불러오지 못했어요</p>'; return; }
      const atEnd = box.scrollHeight - box.scrollTop - box.clientHeight < 80;
      box.innerHTML = (data || []).map((m) => `<div class="dm-msg ${m.mine ? 'mine' : ''}"><div class="dm-bub">${nlBr(m.body)}</div><div class="muted small">${timeAgo(m.created_at)}${m.mine && m.read_at ? ' · 읽음' : ''}</div></div>`).join('') || '<p class="muted center pad">첫 메시지를 보내봐요 👋</p>';
      if (scroll || atEnd) box.scrollTop = box.scrollHeight;
      pollNotif();
    }
    async function openThread(uid) {
      const c = byId(uid) || { user_id: uid, name: '?', staff: null, blocked: false };
      cur = { uid, name: c.name, staff: c.staff, blocked: !!c.blocked };
      wrap.classList.add('open');
      main.innerHTML = `<div class="dm-head"><button class="ghost dm-back" id="dmBack" type="button">←</button>${avatarHtml(uid, 34)}<b>${esc(cur.name)}</b> ${sTag(cur.staff)}<span class="spacer"></span>${cur.staff ? '' : `<button class="ghost small" id="dmBlock" type="button">${cur.blocked ? '차단 해제' : '차단'}</button>`}</div>
        <div class="dm-msgs" id="dmMsgs"><p class="muted center pad">불러오는 중…</p></div>
        <form class="dm-form" id="dmForm"><textarea id="dmText" rows="2" maxlength="1000" placeholder="메시지 (Enter 전송, Shift+Enter 줄바꿈)"></textarea><button class="primary">보내기</button></form>`;
      $('#dmBack', main).onclick = () => { wrap.classList.remove('open'); cur = null; drawSide(); };
      const bl = $('#dmBlock', main);
      if (bl) bl.onclick = async () => {
        const on = !cur.blocked;
        if (on && !confirm(`${cur.name} 님을 차단할까요? 이 사람이 보내는 메시지를 받지 않아요.`)) return;
        const r = await sb.rpc('dm_block', { p_uid: cur.uid, p_on: on });
        if (r.error) return toast('바꾸지 못했어요', true);
        cur.blocked = on; const cc = byId(cur.uid); if (cc) cc.blocked = on;
        bl.textContent = on ? '차단 해제' : '차단';
        toast(on ? '차단했어요' : '차단을 풀었어요');
      };
      const ta = $('#dmText', main);
      ta.onkeydown = (ev) => { if (ev.key === 'Enter' && !ev.shiftKey && !ev.isComposing) { ev.preventDefault(); $('#dmForm', main).requestSubmit(); } };
      $('#dmForm', main).onsubmit = async (ev) => {
        ev.preventDefault();
        const body = ta.value.trim();
        if (!body) return;
        const btn = $('#dmForm button', main); btn.disabled = true;
        const { data: r, error } = await sb.rpc('dm_send', { p_to: cur.uid, p_body: body });
        btn.disabled = false;
        if (error) return toast('보내지 못했어요: ' + error.message, true);
        if (r !== 'ok') return toast(DM_ERR[r] || '보내지 못했어요', true);
        ta.value = '';
        await loadThread(true); drawSide(); ta.focus();
      };
      await loadThread(true);
      drawSide();
    }
    el.__dmOpen = openThread;
    await drawSide();
    if (openUid) await openThread(openUid);
    const tick = setInterval(() => {
      if (!document.body.contains(el)) return clearInterval(tick);
      if (el.hidden || document.hidden) return;
      if (cur) loadThread(false);
      drawSide();
    }, 8000);
    $('#view').addEventListener('pn-dm-refresh', () => { if (cur) loadThread(false); drawSide(); });
  }

  // ---- 설정 탭: 알림
  async function initNotifTab(el) {
    el.innerHTML = '<div class="card"><p class="muted small">불러오는 중…</p></div>';
    const draw = async () => {
      const { data, error } = await sb.from('notifications').select('id,kind,title,body,link,cnt,created_at,read_at').order('id', { ascending: false }).limit(60);
      if (error) { el.innerHTML = `<div class="card pad muted">${SOC_HINT}</div>`; return; }
      const list = data || [];
      const canBn = 'Notification' in window;
      el.innerHTML = `<div class="card"><div class="page-head"><h3>🔔 알림</h3><span class="spacer"></span>
        <button class="ghost small" id="ntAll" type="button">모두 읽음</button> <button class="ghost small" id="ntClr" type="button">읽은 알림 지우기</button></div>
        ${canBn ? `<label class="inline"><input type="checkbox" id="ntBn" ${bnOn() ? 'checked' : ''}> 다른 탭을 보고 있을 때 브라우저 알림도 받기 <span class="muted small">(이 사이트가 열려 있을 때만 와요)</span></label>` : ''}
        <div class="list nt-list">${list.map((n) => `<button type="button" class="row nt ${n.read_at ? '' : 'unread'}" data-n="${n.id}" data-l="${esc(n.link)}"><span class="nt-ic">${NOTE_ICON[n.kind] || '🔔'}</span><span class="row-main"><b>${esc(n.title)}</b>${n.cnt > 1 ? ` <span class="nbadge">${n.cnt}</span>` : ''}<br><span class="muted small">${esc(n.body)}</span></span><span class="muted small">${timeAgo(n.created_at)}</span></button>`).join('') || '<p class="muted center pad">알림이 없어요.</p>'}</div></div>`;
      el.querySelectorAll('[data-n]').forEach((b) => (b.onclick = async () => {
        await sb.from('notifications').update({ read_at: new Date().toISOString() }).eq('id', b.dataset.n).is('read_at', null);
        pollNotif(true);
        if (b.dataset.l) { if (location.hash === b.dataset.l) route(); else location.hash = b.dataset.l; } else draw();
      }));
      $('#ntAll', el).onclick = async () => { await sb.from('notifications').update({ read_at: new Date().toISOString() }).is('read_at', null); pollNotif(true); draw(); };
      $('#ntClr', el).onclick = async () => { await sb.from('notifications').delete().not('read_at', 'is', null); draw(); };
      const bn = $('#ntBn', el);
      if (bn) bn.onchange = async () => {
        if (bn.checked) {
          const p = Notification.permission === 'granted' ? 'granted' : await Notification.requestPermission();
          if (p !== 'granted') { bn.checked = false; toast('브라우저에서 알림을 허용해야 해요', true); return; }
          try { localStorage.setItem('pn_bn', '1'); } catch (e) { /* 저장 안 돼도 이번 방문엔 동작 */ }
          toast('브라우저 알림을 켰어요');
        } else { try { localStorage.setItem('pn_bn', '0'); } catch (e) { /* 무시 */ } }
      };
    };
    await draw();
  }

  // ---- 관리자: DM 열람 + 공지 알림
  async function adminSocial() {
    const { data: pairs, error } = await sb.rpc('dm_admin_pairs');
    if (error) return [`<div class="card pad center">${SOC_HINT}</div>`];
    const rows = (pairs || []).map((p) => `<button type="button" class="row dmp" data-a="${p.a}" data-b="${p.b}"><span class="row-main"><b>${esc(p.a_name)}</b> ↔ <b>${esc(p.b_name)}</b></span><span class="muted small">${p.n}개 · ${timeAgo(p.last_at)}</span></button>`).join('');
    return [`
      <div class="card"><h3>📣 공지 알림 보내기</h3><p class="muted small">승인된 모든 사용자에게 🔔 알림이 가요.</p>
        <form id="ntForm"><label>제목<input type="text" id="ntT" maxlength="80" required></label>
          <label>내용 <span class="muted small">(선택)</span><input type="text" id="ntB" maxlength="300"></label>
          <label>눌렀을 때 이동할 곳 <span class="muted small">(선택, 예: #/board/notice)</span><input type="text" id="ntL" maxlength="120" placeholder="#/board/notice"></label>
          <div class="form-actions"><button class="primary">보내기</button></div></form></div>
      <div class="card"><h3>💬 DM 열람</h3><p class="muted small">학생들의 대화를 읽을 수 있어요. 대화는 지워지지 않아요. 선생님(OWNER)만 볼 수 있고, 학생에게는 열람 가능하다고 안내돼 있어요.</p>
        <div class="list">${rows || '<p class="muted center pad">아직 오간 메시지가 없어요.</p>'}</div><div id="dmView"></div></div>`,
    (v) => {
      $('#ntForm', v).onsubmit = async (e) => {
        e.preventDefault();
        const link = $('#ntL', v).value.trim();
        if (link && !/^#\//.test(link)) return toast('이동할 곳은 #/ 로 시작해야 해요 (예: #/board/notice)', true);
        if (!confirm('모든 사용자에게 알림을 보낼까요?')) return;
        const { data, error: er } = await sb.rpc('notify_all', { p_title: $('#ntT', v).value.trim(), p_body: $('#ntB', v).value.trim(), p_link: link });
        if (er) return toast('보내지 못했어요: ' + er.message, true);
        e.target.reset(); toast(`${data}명에게 보냈어요`);
      };
      v.querySelectorAll('.dmp').forEach((b) => (b.onclick = async () => {
        const { data, error: er } = await sb.rpc('dm_admin_thread', { p_a: b.dataset.a, p_b: b.dataset.b });
        if (er) return toast('불러오지 못했어요', true);
        $('#dmView', v).innerHTML = `<h4>${esc(b.querySelector('.row-main').textContent)}</h4><div class="dm-msgs adm">${(data || []).slice().reverse().map((m) => `<div class="dm-msg ${m.sender === b.dataset.a ? '' : 'mine'}"><div class="muted small">${esc(m.sender_name)} · ${fmt(m.created_at)}</div><div class="dm-bub">${nlBr(m.body)}</div></div>`).join('')}</div>`;
      }));
    }];
  }

  /* ---------- V4.5.0 성장: 파이포인트 · 연속 학습 · 배지 (v450_growth.sql) ---------- */
  let GROW = null;
  let GROW_OK = true;
  let growAt = 0;
  const GROW_HINT = '아직 준비되지 않았어요. (관리자가 v450_growth.sql 을 실행하면 쓸 수 있어요)';
  const kstDay = (d = new Date()) => new Date(d).toLocaleDateString('sv-SE', { timeZone: 'Asia/Seoul' });
  const PY_WHY = { solve: '문제를 맞췄어요', learn: '학습 레슨 완료', rank_week: '주간 랭킹 보상', rank_month: '월간 랭킹 보상', admin: '선생님이 조정', shield: '연속 학습 방어권', exam_rank: '시험 순위 보상', item_reward: '아이템 보상', event_claim: '행사 보상', item_buy: '아이템 구입', market_sale: '마켓 판매 수익', market_buy: '마켓 구입', badge: '🎖️ 배지 보상', gacha: '🎰 뽑기', gift_out: '🎁 선물 보냄', gift_in: '🎁 선물 받음' };
  function growChips() {
    const el = $('#gChips');
    if (!el) return;
    if (!GROW || !GROW.student) { el.innerHTML = ''; return; }
    const s = GROW.streak || {};
    el.innerHTML = `<a class="gchip ${s.today ? 'on' : 'off'}" href="#/me/streak" title="${s.today ? '오늘 학습 완료!' : '오늘 학습하면 연속 학습이 이어져요'}">🔥 ${s.streak || 0}</a><a class="gchip py" href="#/me/wallet" title="파이포인트">💎 ${GROW.py || 0}</a>`;
  }
  function refreshHeadAv() {
    const b = $('.avbtn');
    if (b && me) b.innerHTML = avatarHtml(me.id, 34) || '👤';
  }
  async function growRefresh(force) {
    if (!GROW_OK || !me || me.status !== 'approved') return;
    if (!force && Date.now() - growAt < 20000) return;
    growAt = Date.now();
    const { data, error } = await sb.rpc('growth_boot');
    if (error) { if (/Could not find|does not exist|42883|PGRST202/.test(`${error.code || ''} ${error.message || ''}`)) GROW_OK = false; return; }
    if (!data) return;
    GROW = data;
    growChips();
    (data.new_badges || []).forEach((b) => toast(`🎖️ 새 배지! ${b.icon} ${b.name}${b.reward ? ` · 💎 +${b.reward}` : ''}`));
  }
  function injectHomeGrow() {
    const v = $('#view');
    if (!v || !GROW || !GROW.student || $('.home-grow', v) || !/^#\/home|^#?\/?$/.test(location.hash || '#/home')) return;
    const s = GROW.streak || {};
    const msg = s.today ? `오늘 학습 완료! ${s.streak}일째 이어가는 중이에요 🎉`
      : s.rescue > 0 ? `어제를 놓쳤지만 방어권 ${s.rescue}개가 자동으로 지켜줘요 🛡️ 오늘 학습하면 이어져요`
        : s.streak > 0 ? `${s.streak}일 연속 중! 오늘 학습하면 ${s.streak + 1}일이 돼요`
          : '오늘 문제 하나만 풀어도 연속 학습이 시작돼요';
    const el = document.createElement('a');
    el.className = `card home-grow ${s.today ? 'done' : ''}`;
    el.href = '#/me/streak';
    el.innerHTML = `<span class="hg-ic">${s.today ? '🔥' : '🕯️'}</span><span class="hg-t"><b>${esc(msg)}</b><br><span class="muted small">💎 ${GROW.py || 0} · 🛡️ ${GROW.shields || 0} · 눌러서 내 성장 보기</span></span>`;
    v.insertBefore(el, v.firstChild);
  }

  // ---- 나 > 내 정보 (허브)
  async function initHubTab(el) {
    await Promise.all([loadExt([me.id]), growRefresh(true)]);
    const staff = !!staffRole();
    const d = DIR.get(me.id) || {};
    const sc = Math.max(0, Number(d.score) || 0);
    const k = tierOf(sc);
    const pct = Math.max(0, Math.min(100, Math.round(((sc - k.lo) / Math.max(1, k.hi - k.lo)) * 100)));
    const s = (GROW && GROW.streak) || {};
    let nb = 0;
    if (!staff && GROW_OK) { const { count } = await sb.from('user_badges').select('badge_id', { count: 'exact', head: true }).eq('user_id', me.id); nb = count || 0; }
    const TILES = [['avatar', '🧑‍🎤', '캐릭터 꾸미기'], ['prof', '✨', '프로필'], ['badges', '🎖️', '배지'], ['streak', '🔥', '연속 학습'], ['wallet', '💎', '파이포인트'], ['dm', '💬', '메시지'], ['notif', '🔔', '알림'], ['rec', '📋', '내 풀이·임시저장'], ['ide', '⌨️', '코드 편집기'], ['acct', '⚙️', '계정·화면']];
    el.innerHTML = `<div class="card me-hero">
        <div class="me-av">${avatarHtml(me.id, 84)}</div>
        <div class="me-info"><h3 style="margin:0">${esc(selfName())} ${staff ? staffTag() : ''}</h3>
          ${staff ? '<p class="muted small">선생님 계정이에요.</p>' : `<div class="me-tier">${tierBadge(sc, 26)} <b>${esc(k.name)}</b> <span class="muted small">${sc.toLocaleString()}점</span></div>
          <div class="prog"><i style="width:${pct}%;background:var(--primary)"></i></div>
          <p class="muted small" style="margin:4px 0 0">다음 단계까지 ${Math.max(0, Math.ceil(k.hi - sc)).toLocaleString()}점</p>`}</div></div>
      ${staff || !GROW_OK ? '' : `<div class="stat-grid">
        <a class="stat hot" href="#/me/streak"><div class="stat-n">🔥 ${s.streak || 0}</div><div class="stat-l">연속 학습(일)</div></a>
        <a class="stat new" href="#/me/wallet"><div class="stat-n">💎 ${(GROW && GROW.py) || 0}</div><div class="stat-l">파이포인트</div></a>
        <a class="stat ok" href="#/me/badges"><div class="stat-n">🎖️ ${nb}</div><div class="stat-l">내 배지</div></a></div>`}
      <div class="me-grid">${TILES.map(([kk, ic, nm]) => `<button type="button" class="me-tile" data-go="${kk}"><span class="me-ic">${ic}</span>${nm}</button>`).join('')}</div>
      <div class="form-actions" style="justify-content:center"><button class="ghost" id="meLogout" type="button">로그아웃</button></div>`;
    el.querySelectorAll('[data-go]').forEach((b) => (b.onclick = () => $('#view').dispatchEvent(new CustomEvent('pn-tab', { detail: b.dataset.go }))));
    $('#meLogout', el).onclick = logout;
  }

  // ---- 나 > 연속 학습
  async function initStreakTab(el) {
    el.innerHTML = '<p class="muted center pad">불러오는 중…</p>';
    const { data: s, error } = GROW_OK ? await sb.rpc('streak_info') : { error: true };
    if (error || !s) { el.innerHTML = `<div class="card pad muted">${GROW_HINT}</div>`; return; }
    if (GROW && GROW.student === false) { el.innerHTML = '<div class="card pad muted">선생님 계정에는 연속 학습이 없어요.</div>'; return; }
    const cfg = (GROW && GROW.cfg) || {};
    const price = Number(cfg.shield_price) || 600;
    const max = Number(cfg.shield_max) || 2;
    const marks = new Map((s.days || []).map((x) => [x.d, x.k]));
    const today = kstDay();
    const t0 = new Date(`${today}T00:00:00Z`);
    const dow = (t0.getUTCDay() + 6) % 7;
    const cells = [];
    for (let i = -(dow + 28); i < 7 - dow; i += 1) {
      const dt = new Date(t0.getTime() + i * 864e5).toISOString().slice(0, 10);
      const k = marks.get(dt);
      cells.push(`<div class="cal-c ${k ? `k-${k}` : ''} ${dt === today ? 'today' : ''} ${dt > today ? 'fut' : ''}" title="${dt}">${k === 'shield' ? '🛡️' : k ? '🔥' : ''}<span>${Number(dt.slice(8))}</span></div>`);
    }
    const msg = s.today ? '오늘 학습 완료! 내일도 이어가요 🎉'
      : s.rescue > 0 ? `놓친 ${s.rescue}일은 방어권이 자동으로 지켜줘요 🛡️ 오늘 학습하면 연속이 이어져요`
        : s.broken ? '연속 학습이 끊겼어요. 오늘부터 다시 시작해봐요!'
          : s.streak > 0 ? '오늘 학습하면 연속 기록이 늘어나요' : '문제를 풀거나 학습 레슨을 하면 출석이에요';
    el.innerHTML = `<div class="card streak-hero ${s.today ? 'done' : ''}"><div class="sh-n">🔥 ${s.streak}</div><div><b>일 연속 학습</b><br><span class="muted small">${esc(msg)}</span></div></div>
      <div class="stat-grid"><div class="stat"><div class="stat-n">${s.best}</div><div class="stat-l">최고 기록(일)</div></div>
        <div class="stat"><div class="stat-n">🛡️ ${s.shields}/${max}</div><div class="stat-l">방어권</div></div>
        <div class="stat"><div class="stat-n">💎 ${(GROW && GROW.py) || 0}</div><div class="stat-l">파이포인트</div></div></div>
      <div class="card"><h3>🛡️ 연속 학습 방어권</h3>
        <p class="muted small">하루를 놓쳐도 방어권이 있으면 자동으로 쓰여서 연속 기록이 이어져요. 최대 ${max}개까지 가질 수 있어요.</p>
        <button class="primary" id="shBuy" type="button" ${s.shields >= max ? 'disabled' : ''}>💎 ${price}로 방어권 사기</button></div>
      <div class="card"><h3>최근 5주</h3><div class="cal"><b>월</b><b>화</b><b>수</b><b>목</b><b>금</b><b>토</b><b>일</b>${cells.join('')}</div>
        <p class="muted small" style="margin:8px 0 0">🔥 학습한 날 · 🛡️ 방어권으로 지킨 날</p></div>`;
    $('#shBuy', el).onclick = async () => {
      const { data: r, error: er } = await sb.rpc('py_buy_shield');
      if (er) return toast('처리하지 못했어요: ' + er.message, true);
      const M = { ok: '방어권을 샀어요! 🛡️', full: '방어권을 이미 최대로 가지고 있어요', poor: '파이포인트가 부족해요', nouser: '학생 계정만 살 수 있어요' };
      toast(M[r] || '처리하지 못했어요', r !== 'ok');
      await growRefresh(true);
      initStreakTab(el);
    };
  }

  // ---- 나 > 파이포인트
  async function initWalletTab(el) {
    el.innerHTML = '<p class="muted center pad">불러오는 중…</p>';
    if (!GROW_OK) { el.innerHTML = `<div class="card pad muted">${GROW_HINT}</div>`; return; }
    await growRefresh(true);
    const [lg, cf] = await Promise.all([
      sb.from('py_ledger').select('delta,reason,note,created_at').eq('user_id', me.id).order('id', { ascending: false }).limit(40),
      sb.from('py_config').select('key,val'),
    ]);
    if (lg.error) { el.innerHTML = `<div class="card pad muted">${GROW_HINT}</div>`; return; }
    const C = {}; (cf.data || []).forEach((r) => { C[r.key] = r.val; });
    const rng = (v) => (Array.isArray(v) ? `${v[0]}~${v[1]}` : '?');
    const lst = (v) => (Array.isArray(v) ? v.map((x, i) => `${i + 1}위 ${x}`).join(' · ') : '?');
    el.innerHTML = `<div class="card streak-hero"><div class="sh-n">💎 ${(GROW && GROW.py) || 0}</div><div><b>파이포인트</b><br><span class="muted small">랭킹 점수와는 따로 모으는 재화예요</span></div></div>
      <div class="card"><h3>어떻게 모아요?</h3><ul class="py-how">
        <li>📅 <b>주간 랭킹</b> ${esc(lst(C.week_rank))} <span class="muted small">(동점이면 나눠 가져요)</span></li>
        <li>🗓️ <b>월간 랭킹</b> ${esc(lst(C.month_rank))}</li>
        <li>✅ <b>문제를 처음 맞출 때</b> 랜덤 ${esc(rng(C.solve_rand))}</li>
        <li>📚 <b>학습 레슨을 끝낼 때</b> 랜덤 ${esc(rng(C.learn_rand))}</li>
        <li>🎖️ <b>배지를 받을 때</b> 배지마다 💎 보상 <a href="#/me/badges">(배지 보기)</a></li>
        <li>🎁 시험 순위 · 행사 · 선생님 지급</li>${(typeof EVENTS !== 'undefined' && EVENTS.filter((e) => Number(e.mult) > 1).map((e) => `<li>${esc(e.emoji)} <b>${esc(e.title)}</b> 행사 중! 문제·학습 보상 💎 ×${Number(e.mult)}</li>`).join('')) || ''}</ul>
        <h3>어디에 써요?</h3><ul class="py-how"><li>🛡️ 연속 학습 방어권 (${esc(String(C.shield_price ?? 600))})</li><li>🧑‍🎤 캐릭터 꾸미기 아이템·🛍️ 마켓 <a href="#/me/avatar">(구경하기)</a></li></ul>
        <a class="btn" href="#/me/streak">🛡️ 방어권 사러 가기</a></div>
      <div class="card list"><h3 style="padding:14px 18px 0;margin:0">최근 내역</h3>${(lg.data || []).map((x) => `<div class="row"><div class="row-main"><b>${esc(PY_WHY[x.reason] || x.reason)}</b> <span class="muted small">${esc(x.note || '')}</span><br><span class="muted small">${fmt(x.created_at)}</span></div><b class="${x.delta > 0 ? 'py-up' : 'py-down'}">${x.delta > 0 ? '+' : ''}${x.delta}</b></div>`).join('') || '<p class="muted center pad">아직 내역이 없어요. 문제를 풀면 모여요!</p>'}</div>`;
    renderPyShop(el);
  }

  // ---- 💎 쓰는 곳: 뽑기 · 선물 (v453b_economy.sql)
  async function renderPyShop(el) {
    const { data: info, error } = await sb.rpc('py_shop_info');
    if (error || !info) return;
    const box = document.createElement('div');
    box.className = 'card';
    box.id = 'pyShop';
    const g = info.gift || {};
    const others = Array.from(DIR.entries()).filter(([id]) => id !== me.id).map(([id, d]) => [id, d.name || '?']).sort((a, b) => String(a[1]).localeCompare(String(b[1]), 'ko'));
    const left = (info.sent_today != null ? Math.max(0, (g.daily || 0) - info.sent_today) : g.daily);
    box.innerHTML = `<h3>🛒 파이포인트 쓰는 곳</h3>
      <div class="py-shop">
        <div class="py-prod"><span class="py-ic">🎰</span><div><b>일반 뽑기</b><br><span class="muted small">상점 아이템 중 아직 없는 것 하나 · 남은 후보 ${info.left_basic}개</span></div><button class="primary" data-gacha="basic" ${info.left_basic ? '' : 'disabled'}>💎 ${(info.gacha || {}).basic}</button></div>
        <div class="py-prod"><span class="py-ic">🌈</span><div><b>고급 뽑기</b><br><span class="muted small">조건부 아이템까지 전부 후보 (점수·티어 잠금도 풀려요!) · 남은 후보 ${info.left_premium}개</span></div><button class="primary" data-gacha="premium" ${info.left_premium ? '' : 'disabled'}>💎 ${(info.gacha || {}).premium}</button></div>
        <div class="py-prod"><span class="py-ic">🛡️</span><div><b>연속 학습 방어권</b><br><span class="muted small">하루 놓쳐도 연속이 이어져요</span></div><a class="btn" href="#/me/streak">사러 가기</a></div>
        <div class="py-prod"><span class="py-ic">🛍️</span><div><b>아이템 · 마켓</b><br><span class="muted small">상점 아이템 가격은 기본 가격의 ×${Number(info.mult)} 배예요</span></div><a class="btn" href="#/market">구경하기</a></div>
      </div>
      <h4>🎁 친구에게 선물하기</h4>
      <form id="gfForm" class="gf-form">
        <select id="gfTo" required><option value="">받을 친구</option>${others.map(([id, n]) => `<option value="${id}">${esc(n)}</option>`).join('')}</select>
        <input type="number" id="gfAmt" min="${g.min || 10}" max="${g.max || 500}" placeholder="💎 ${g.min || 10}~${g.max || 500}" required>
        <button class="primary">보내기</button></form>
      <p class="muted small">수수료 ${g.fee ?? 10}% 가 빠지고 나머지가 친구에게 가요 · 오늘 더 보낼 수 있는 양 💎 ${left}</p>`;
    el.appendChild(box);
    const done = async () => { await growRefresh(true); initWalletTab(el); };
    box.querySelectorAll('[data-gacha]').forEach((b) => (b.onclick = async () => {
      const tier = b.dataset.gacha;
      if (!confirm(`💎 ${(info.gacha || {})[tier]} 로 ${tier === 'basic' ? '일반' : '고급'} 뽑기를 할까요?`)) return;
      b.disabled = true;
      const { data, error: e } = await sb.rpc('py_gacha', { p_tier: tier });
      if (e || !data) { b.disabled = false; return toast('뽑지 못했어요', true); }
      if (data.status !== 'ok') { b.disabled = false; return toast(data.status === 'poor' ? '파이포인트가 부족해요' : data.status === 'empty' ? '뽑을 수 있는 아이템이 없어요' : '뽑지 못했어요', true); }
      await loadItems();
      const slotN = (ITEM_SLOTS.find(([k]) => k === data.item.slot) || [])[1] || '';
      const m = modal(`<h3>🎉 뽑았어요!</h3><div class="mk-big">${avatarSvg({ ...normAv((EXT.get(me.id) || {}).avatar, me.id), items: { [data.item.slot]: data.item.id } }, 180)}</div><p class="center"><b>${esc(data.item.name)}</b> <span class="muted small">(${esc(slotN)})</span></p><div class="form-actions"><button class="ghost" id="gcOk" type="button">좋아요</button><a class="btn" href="#/me/avatar" id="gcGo">입으러 가기</a></div>`);
      $('#gcOk', m.el).onclick = () => { m.close(); done(); };
      $('#gcGo', m.el).onclick = () => m.close();
    }));
    $('#gfForm', box).onsubmit = async (ev) => {
      ev.preventDefault();
      const to = $('#gfTo', box).value; const amt = parseInt($('#gfAmt', box).value, 10);
      const nm = $('#gfTo', box).selectedOptions[0].textContent;
      if (!confirm(`${nm} 님에게 💎 ${amt} 를 보낼까요? (수수료 ${g.fee ?? 10}%)`)) return;
      const { data, error: e } = await sb.rpc('py_gift', { p_to: to, p_amt: amt });
      if (e) return toast('보내지 못했어요', true);
      const MSG = { ok: '🎁 선물을 보냈어요!', poor: '파이포인트가 부족해요', amount: `💎 ${g.min || 10}~${g.max || 500} 사이로 보내주세요`, daily: '오늘 보낼 수 있는 양을 넘었어요', nouser: '받을 수 없는 친구예요' };
      toast(MSG[data] || '보내지 못했어요', data !== 'ok');
      if (data === 'ok') done();
    };
  }

  // ---- 나 > 배지
  const BADGE_GROUP = [['score', '🏆 점수'], ['solved', '🧩 문제 풀이'], ['streak', '🔥 연속 학습'], ['learn', '📚 학습'], ['exam_join', '📝 시험'], ['exam_first', '📝 시험'], ['pypoint', '💎 파이포인트'], ['tier', '🏅 티어'], ['rank1', '🥇 랭킹 1등'], ['items', '🎒 아이템'], ['sales', '🛍️ 마켓'], ['market_made', '🛍️ 마켓'], ['attend', '📅 출석'], ['event', '🎉 행사'], ['shield', '🛡️ 방어권'], ['posts', '💬 게시판'], ['comments', '💬 게시판'], ['manual', '🎁 특별']];
  let BD_RW = {}; // 배지 id → 보상 💎
  const badgeTile = (b, got) => `<div class="bdg tone-${esc(b.tone)} ${got ? 'on' : ''}" title="${esc(b.descr)}"><div class="bdg-ic">${esc(b.icon)}</div><b>${esc(b.name)}</b><span class="muted small">${got ? `${fmt(got)} 획득` : esc(b.descr)}</span>${BD_RW[b.id] > 0 ? `<span class="bdg-rw">💎 ${got ? '' : '+'}${BD_RW[b.id]}</span>` : ''}</div>`;
  async function initBadgesTab(el) {
    el.innerHTML = '<p class="muted center pad">불러오는 중…</p>';
    if (!GROW_OK) { el.innerHTML = `<div class="card pad muted">${GROW_HINT}</div>`; return; }
    await growRefresh(true);
    const [d, u, rw] = await Promise.all([sb.from('badge_defs').select('*').order('position').order('id'), sb.from('user_badges').select('badge_id,earned_at').eq('user_id', me.id), Promise.resolve(sb.rpc('badge_reward_map')).catch(() => null)]);
    BD_RW = (rw && rw.data) || {};
    if (d.error) { el.innerHTML = `<div class="card pad muted">${GROW_HINT}</div>`; return; }
    const got = new Map((u.data || []).map((x) => [x.badge_id, x.earned_at]));
    const defs = d.data || [];
    const seen = new Set();
    const sections = BADGE_GROUP.map(([k, title]) => {
      const kinds = BADGE_GROUP.filter(([, t]) => t === title).map(([x]) => x);
      if (seen.has(title)) return '';
      seen.add(title);
      const arr = defs.filter((b) => kinds.includes(b.kind));
      const arr2 = arr.slice().sort((x, y) => (got.has(y.id) ? 1 : 0) - (got.has(x.id) ? 1 : 0));
      return arr.length ? `<h3>${title} <span class="muted small">${arr.filter((b) => got.has(b.id)).length} / ${arr.length}</span></h3><div class="bdg-grid">${arr2.map((b) => badgeTile(b, got.get(b.id))).join('')}</div>` : '';
    }).join('');
    el.innerHTML = `<div class="card streak-hero"><div class="sh-n">🎖️ ${got.size}</div><div><b>/ ${defs.length} 배지</b><br><span class="muted small">조건을 채우면 자동으로 받아요</span></div></div>${sections}`;
  }

  // ---- 관리자 > 시험 (만들기 · 문제 · 보상 · 결과)
  let exEditId = null;
  async function adminExam() {
    const { data: L, error } = await sb.rpc('exam_list');
    if (error || !L) return [`<div class="card pad muted">시험은 선생님이 v454_exam.sql 을 실행하면 열려요.</div>`];
    await exSync();
    let cur = null; // 편집 중인 시험 (없으면 새로 만들기)
    if (exEditId) { const { data } = await sb.rpc('exam_admin_get', { p_id: exEditId }); cur = data; if (!cur) exEditId = null; }
    const R = (cur && cur.reward) || { pt_rank: [300, 200, 100], pt_join: 50, item_first: 'exam_balloon_gold', item_top3: 'exam_balloon_silver', item_join: 'exam_balloon_blue' };
    const loc = (iso) => { const d = new Date(iso); const p = (n) => String(n).padStart(2, '0'); return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`; };
    const defStart = loc(new Date(Date.now() + 36e5 * 24).toISOString());
    const rows = (L.exams || []).map((e) => { const ph = exPhase(e); return `<div class="row"><div class="row-main"><b>${esc(e.title)}</b> <span class="badge ${EX_PH[ph][1]}">${EX_PH[ph][0]}</span> <span class="chip">${e.status === 'open' ? '공개' : '비공개'}</span><br><span class="muted small">${fmt(e.start_at)} · ${e.duration_min}분 · 문제 ${e.n_problems} · 응시 ${e.n_entries}${e.n_essay ? ` · 서술형 ${e.n_essay}` : ''}${e.settled ? ' · 정산 완료' : ''}</span></div><div><a class="ghost btn" href="#/exam/${e.id}">보기</a> <button class="ghost" data-exnote="${e.id}" type="button">📣 알림</button>${e.n_essay ? ` <button class="ghost" data-exgrade="${e.id}" type="button">✍️ 채점${e.settled ? ' 보기' : ''}</button>` : ''} <button class="ghost" data-exedit="${e.id}" type="button">수정</button> <button class="ghost danger" data-exdel="${e.id}" type="button">삭제</button></div></div>`; }).join('') || '<p class="muted center pad">아직 시험이 없어요.</p>';
    return [`
      <div class="card list"><h3 style="padding:14px 18px 0;margin:0">📝 시험 목록</h3>${rows}</div>
      <div class="card"><h3>${cur ? `✏️ 시험 수정 · #${cur.id}` : '➕ 새 시험 만들기'}</h3>
        ${cur && cur.settled ? '<p class="muted">정산이 끝난 시험은 고칠 수 없어요.</p>' : ''}
        <form id="exForm">
          <label>제목<input type="text" id="exTitle" maxlength="60" required value="${esc(cur ? cur.title : '')}" placeholder="예) 1학기 중간고사"></label>
          <label>안내 글 <span class="muted small">(마크다운)</span><textarea id="exDesc" rows="3" maxlength="2000" placeholder="시험 범위, 주의사항 등">${esc(cur ? cur.descr : '')}</textarea></label>
          <div class="ga-grid">
            <label>시작 시각<input type="datetime-local" id="exStart" required value="${cur ? loc(cur.start_at) : defStart}"></label>
            <label>시험 시간(분)<input type="number" id="exDur" min="5" max="600" value="${cur ? cur.duration_min : 60}"></label>
            <label>입장 가능(시작 몇 분 전부터)<input type="number" id="exEntry" min="0" max="1440" value="${cur ? cur.entry_min : 60}"></label>
            <label>공개 상태<select id="exStatus"><option value="draft" ${cur && cur.status === 'open' ? '' : 'selected'}>비공개 (준비 중)</option><option value="open" ${cur && cur.status === 'open' ? 'selected' : ''}>공개 (학생에게 보임)</option></select></label>
          </div>
          <h4>🎁 보상</h4>
          <div class="ga-grid">
            <label>순위별 💎 <span class="muted small">(쉼표로: 1위,2위,3위…)</span><input type="text" id="exPts" value="${esc((R.pt_rank || []).join(','))}"></label>
            <label>참가 💎<input type="number" id="exJoin" min="0" value="${R.pt_join || 0}"></label>
            <label>1등 아이템 ID<input type="text" id="exI1" value="${esc(R.item_first || '')}"></label>
            <label>3등 안 아이템 ID<input type="text" id="exI3" value="${esc(R.item_top3 || '')}"></label>
            <label>참가 아이템 ID<input type="text" id="exIj" value="${esc(R.item_join || '')}"></label>
          </div>
          <p class="muted small">아이템 ID 는 🎁 아이템 탭에서 확인해요. 기본: 금빛·은빛·파란 풍선 장식. 비우면 주지 않아요.</p>
          <h4>📄 문제 <span class="muted small" id="exCnt"></span></h4>
          <div id="exProbs"></div>
          <div class="form-actions" style="justify-content:flex-start"><button class="ghost" type="button" id="exAdd">+ 문제 직접 추가</button><button class="ghost" type="button" id="exImp">📥 문제집에서 가져오기</button></div>
          ${cur ? '<label class="inline"><input type="checkbox" id="exFix" checked> 저장하면 응시자에게 📣 "문제가 수정됐어요" 알림 보내기</label><p class="muted small">시험 중에 문제를 고쳐도 제출 기록은 그대로예요. 응시자 화면은 30초 안에 알아서 바뀌어요. 채점 테스트를 바꿨다면 학생이 다시 제출해야 새 기준으로 점수가 나와요.</p>' : ''}
          <div class="form-actions"><button class="ghost" type="button" id="exNew">새로 쓰기</button><button class="primary">${cur ? '저장' : '만들기'}</button></div>
        </form></div>`,
    (v) => {
      const probs = cur ? cur.problems.map((p) => ({ ...p, tests: JSON.stringify(p.tests || [], null, 1) })) : [];
      const drawP = () => {
        $('#exCnt', v).textContent = `(${probs.length}개 · 합계 ${probs.reduce((s, p) => s + (Number(p.points) || 0), 0)}점)`;
        $('#exProbs', v).innerHTML = probs.map((p, i) => `<div class="card ex-pe"><div class="ex-pehead"><b>${i + 1}번</b><select data-f="kind" data-i="${i}" title="문제 종류"><option value="code" ${p.kind === 'essay' ? '' : 'selected'}>💻 코드</option><option value="essay" ${p.kind === 'essay' ? 'selected' : ''}>✍️ 서술형</option></select><input type="text" data-f="title" data-i="${i}" maxlength="100" placeholder="문제 제목" value="${esc(p.title || '')}"><input type="number" data-f="points" data-i="${i}" min="1" max="1000" value="${p.points || 100}" style="width:80px" title="배점"><button type="button" class="ghost" data-up="${i}">↑</button><button type="button" class="ghost" data-dn="${i}">↓</button><button type="button" class="ghost danger" data-rm="${i}">✕</button></div>
          <textarea data-f="body" data-i="${i}" rows="5" placeholder="문제 설명 (마크다운)">${esc(p.body || '')}</textarea>
          ${p.kind === 'essay' ? `<textarea data-f="rubric" data-i="${i}" rows="3" placeholder="채점 기준 (선생님만 보여요) 예) 핵심 개념 2가지를 쓰면 각 25점">${esc(p.rubric || '')}</textarea>` : `<details><summary class="muted small">채점 테스트 (JSON) — [{"input":"1 2","output":"3","hidden":false}, …]</summary><textarea class="code" data-f="tests" data-i="${i}" rows="6">${esc(p.tests)}</textarea></details>`}</div>`).join('') || '<p class="muted small">아직 문제가 없어요.</p>';
        v.querySelectorAll('[data-f]').forEach((el) => (el.oninput = () => { probs[Number(el.dataset.i)][el.dataset.f] = el.value; if (el.dataset.f === 'kind') drawP(); if (el.dataset.f === 'points') $('#exCnt', v).textContent = `(${probs.length}개 · 합계 ${probs.reduce((s, p) => s + (Number(p.points) || 0), 0)}점)`; }));
        v.querySelectorAll('[data-rm]').forEach((b) => (b.onclick = () => { probs.splice(Number(b.dataset.rm), 1); drawP(); }));
        v.querySelectorAll('[data-up]').forEach((b) => (b.onclick = () => { const i = Number(b.dataset.up); if (i > 0) { [probs[i - 1], probs[i]] = [probs[i], probs[i - 1]]; drawP(); } }));
        v.querySelectorAll('[data-dn]').forEach((b) => (b.onclick = () => { const i = Number(b.dataset.dn); if (i < probs.length - 1) { [probs[i + 1], probs[i]] = [probs[i], probs[i + 1]]; drawP(); } }));
      };
      drawP();
      $('#exAdd', v).onclick = () => { probs.push({ kind: 'code', title: '', body: '', points: 100, tests: '[\n {"input":"","output":""}\n]' }); drawP(); };
      $('#exNew', v).onclick = () => { exEditId = null; route(true); };
      $('#exImp', v).onclick = async () => {
        const { data: sets } = await sb.from('problem_sets').select('id,title,week').order('id', { ascending: false });
        const m = modal(`<h3>📥 문제집에서 가져오기</h3><label>문제집<select id="imSet"><option value="">— 고르세요 —</option>${(sets || []).map((s) => `<option value="${s.id}">${esc(s.title)}</option>`).join('')}</select></label><div id="imList" class="list" style="max-height:50vh;overflow:auto"></div><div class="form-actions"><button class="primary" id="imGo" type="button">선택한 문제 가져오기</button></div><p class="muted small">제목·설명·채점 테스트를 복사해요. 가져온 뒤 배점을 고쳐 주세요. (채점 테스트가 없는 문제는 가져와도 자동 채점이 안 돼요)</p>`);
        let exs = [];
        $('#imSet', m.el).onchange = async (e) => {
          const sid = Number(e.target.value); if (!sid) { $('#imList', m.el).innerHTML = ''; return; }
          const { data } = await sb.from('exercises').select('id,position,label,difficulty,body,tests').eq('set_id', sid).order('position').order('id');
          exs = data || [];
          $('#imList', m.el).innerHTML = exs.map((x, i) => `<label class="row inline"><input type="checkbox" data-im="${i}"> <span class="row-main"><b>${esc(x.label || '#' + x.id)}</b> <span class="muted small">${esc(x.difficulty || '')} · 테스트 ${(x.tests || []).length}개 · ${esc((x.body || '').replace(/\s+/g, ' ').slice(0, 50))}</span></span></label>`).join('') || '<p class="muted small">문제가 없어요.</p>';
        };
        $('#imGo', m.el).onclick = () => {
          m.el.querySelectorAll('[data-im]:checked').forEach((c) => { const x = exs[Number(c.dataset.im)]; probs.push({ kind: 'code', title: x.label || `문제 ${probs.length + 1}`, body: x.body || '', points: 100, tests: JSON.stringify(x.tests || [], null, 1) }); });
          m.close(); drawP();
        };
      };
      v.querySelectorAll('[data-exnote]').forEach((b) => (b.onclick = () => {
        const id = Number(b.dataset.exnote);
        const m = modal(`<h3>📣 시험 알림 보내기</h3><label>내용 <span class="muted small">(200자)</span><textarea id="nfMsg" rows="3" maxlength="200" placeholder="예) 3번 문제 예시 출력이 틀려서 고쳤어요"></textarea></label><label>받는 사람<select id="nfScope"><option value="entrants">입장한 응시자</option><option value="all">모든 학생</option></select></label><div class="form-actions"><button class="primary" id="nfGo" type="button">📣 보내기</button></div>`);
        $('#nfGo', m.el).onclick = async () => {
          const msg = $('#nfMsg', m.el).value.trim(); if (!msg) return toast('내용을 입력하세요', true);
          const { data } = await sb.rpc('exam_notify', { p_id: id, p_msg: msg, p_scope: $('#nfScope', m.el).value });
          if (typeof data !== 'number' || data < 0) return toast('보내지 못했어요', true);
          m.close(); toast(`${data}명에게 알림을 보냈어요`);
        };
      }));
      v.querySelectorAll('[data-exgrade]').forEach((b) => (b.onclick = async () => {
        const id = Number(b.dataset.exgrade);
        const ex = (L.exams || []).find((x) => x.id === id) || {};
        const { data: es } = await sb.rpc('exam_essays', { p_id: id });
        if (!es) return toast('불러오지 못했어요', true);
        const left = () => es.reduce((n, p) => n + p.answers.filter((a) => a.answer != null && a.score == null).length, 0);
        const m = modal(`<h3>✍️ 서술형 채점 · ${esc(ex.title || '')}</h3><p class="muted small" id="gdInfo"></p><div style="max-height:62vh;overflow:auto">${es.map((p, pi) => `<div class="card"><b>${esc(p.title || '문제')}</b> <span class="chip">${p.points}점</span><div class="ex-body small">${renderContent(p.body || '', true)}</div>${p.rubric ? `<div class="muted small">📋 기준: ${esc(p.rubric)}</div>` : ''}${p.answers.map((a, ai) => `<div class="row" style="align-items:flex-start;gap:8px"><div class="row-main"><b>${esc(a.name || '')}</b><pre style="white-space:pre-wrap;margin:4px 0">${a.answer == null ? '(제출 안 함)' : esc(a.answer)}</pre></div><div><input type="number" min="0" max="${p.points}" data-g="${pi}:${ai}" value="${a.score == null ? '' : a.score}" placeholder="점수" style="width:70px" ${ex.settled ? 'disabled' : ''}></div></div>`).join('') || '<p class="muted small">응시자가 없어요.</p>'}</div>`).join('') || '<p class="muted">서술형 문제가 없어요.</p>'}</div>${ex.settled ? '<p class="muted">정산이 끝나서 고칠 수 없어요.</p>' : '<div class="form-actions"><button class="primary" id="gdFin" type="button">✅ 채점 끝 · 정산하기</button></div><p class="muted small">점수를 쓰고 칸을 벗어나면 저장돼요. 점수를 안 쓴 답은 0점이에요. 정산하면 순위와 보상이 확정돼요.</p>'}`);
        const info = () => { const el = $('#gdInfo', m.el); if (el) el.textContent = `아직 점수를 안 쓴 답 ${left()}개`; };
        info();
        m.el.querySelectorAll('[data-g]').forEach((inp) => (inp.onchange = async () => {
          const [pi, ai] = inp.dataset.g.split(':').map(Number); const p = es[pi]; const a = p.answers[ai];
          if (inp.value === '') return;
          const { data } = await sb.rpc('exam_grade', { p_problem: p.id, p_user: a.uid, p_score: parseInt(inp.value, 10) });
          if (data !== 'ok') { toast({ score: `0~${p.points} 사이로 써요`, settled: '이미 정산됐어요' }[data] || '저장하지 못했어요', true); return; }
          a.score = parseInt(inp.value, 10); info();
        }));
        const fin = $('#gdFin', m.el);
        if (fin) fin.onclick = async () => {
          if (!confirm(`정산할까요? 점수 안 쓴 답 ${left()}개는 0점으로 처리돼요. 정산 뒤에는 고칠 수 없어요.`)) return;
          fin.disabled = true;
          const { data } = await sb.rpc('exam_finalize', { p_id: id });
          if (data === 'ok' || data === 'done') { m.close(); toast('정산했어요! 순위와 보상이 나갔어요'); route(true); }
          else { fin.disabled = false; toast(data === 'wait' ? '시험이 끝난 직후(20초)부터 정산할 수 있어요' : '정산하지 못했어요', true); }
        };
      }));
      v.querySelectorAll('[data-exedit]').forEach((b) => (b.onclick = () => { exEditId = Number(b.dataset.exedit); route(true); window.scrollTo(0, document.body.scrollHeight); }));
      v.querySelectorAll('[data-exdel]').forEach((b) => (b.onclick = async () => {
        if (!confirm('이 시험과 제출 기록, 결과가 모두 지워져요. 지울까요?')) return;
        const { data } = await sb.rpc('exam_delete', { p_id: Number(b.dataset.exdel) });
        if (data !== 'ok') return toast('지우지 못했어요', true);
        if (exEditId === Number(b.dataset.exdel)) exEditId = null;
        route(true);
      }));
      $('#exForm', v).onsubmit = async (ev) => {
        ev.preventDefault();
        let plist;
        try {
          plist = probs.map((p, i) => {
            const t = typeof p.tests === 'string' ? JSON.parse(p.tests || '[]') : (p.tests || []);
            if (p.kind !== 'essay' && (!Array.isArray(t) || t.some((x) => !x || typeof x !== 'object'))) throw new Error(`${i + 1}번 문제의 채점 테스트 형식이 올바르지 않아요`);
            return { id: p.id || null, kind: p.kind === 'essay' ? 'essay' : 'code', rubric: p.kind === 'essay' ? (p.rubric || '') : '', title: p.title || '', body: p.body || '', points: Math.max(1, Math.min(1000, parseInt(p.points, 10) || 100)), tests: p.kind === 'essay' ? [] : t.map((x) => ({ input: String(x.input ?? ''), output: String(x.output ?? ''), ...(x.mode ? { mode: x.mode } : {}), ...(x.hidden ? { hidden: true } : {}) })) };
          });
        } catch (e) { return toast(e.message.includes('JSON') ? '채점 테스트 JSON 형식 오류: ' + e.message : e.message, true); }
        const pts = $('#exPts', v).value.split(',').map((x) => parseInt(x.trim(), 10)).filter((n) => Number.isFinite(n) && n >= 0);
        const nz = (id) => ($(id, v).value.trim() || null);
        const p = { id: cur ? cur.id : null, title: $('#exTitle', v).value.trim(), descr: $('#exDesc', v).value, start_at: new Date($('#exStart', v).value).toISOString(),
          duration_min: parseInt($('#exDur', v).value, 10) || 60, entry_min: parseInt($('#exEntry', v).value, 10) || 0, status: $('#exStatus', v).value,
          reward: { pt_rank: pts, pt_join: parseInt($('#exJoin', v).value, 10) || 0, item_first: nz('#exI1'), item_top3: nz('#exI3'), item_join: nz('#exIj') }, problems: plist };
        if (!p.title) return toast('제목을 입력하세요', true);
        if (p.status === 'open' && !plist.length) return toast('문제를 하나 이상 넣고 공개해 주세요', true);
        const { data, error: e2 } = await sb.rpc('exam_save', { p });
        if (e2 || !data || data.status !== 'ok') return toast({ forbidden: '권한이 없어요', settled: '정산이 끝난 시험은 고칠 수 없어요', invalid: '값이 올바르지 않아요' }[data && data.status] || '저장하지 못했어요', true);
        toast('시험을 저장했어요');
        if (cur && $('#exFix', v) && $('#exFix', v).checked && cur.n_entries > 0) { await sb.rpc('exam_notify', { p_id: data.id, p_msg: '문제가 수정됐어요. 화면이 자동으로 바뀌어요. 바뀐 문제를 확인하세요!', p_scope: 'entrants' }); }
        exEditId = data.id; route(true);
      };
    }];
  }

  // ---- 관리자 > 배지 (만들기 · 고치기 · 지우기 · 몇 명이 받았는지)
  const BD_KINDS = [['score', '랭킹 점수', '점'], ['solved', '푼 문제 수', '문제'], ['streak', '연속 학습', '일'], ['attend', '학습한 날 수(누적)', '일'], ['learn', '끝낸 레슨 수', '개'], ['exam_join', '시험 응시 횟수', '회'], ['exam_first', '시험 1등 횟수', '회'],
    ['pypoint', '누적 파이포인트', '💎'], ['tier', '티어 단계 (0=맨 아래)', '단계'], ['rank1', '랭킹 1등 횟수', '회'], ['items', '모은 아이템 수', '개'], ['sales', '마켓 판매 횟수', '회'], ['market_made', '마켓 등록 개수', '개'],
    ['event', '행사 보상 횟수', '회'], ['shield', '방어권 구매 개수', '개'], ['posts', '게시판 글 수', '개'], ['comments', '댓글 수', '개'], ['manual', '직접 지급 (선생님이 줘요)', '']];
  const BD_ICONS = '🏅 🎖️ 🥇 🥈 🥉 🏆 👑 ⭐ 🌟 💫 ✨ 🔥 💎 🚀 🎯 🧩 💪 🧠 📚 🎓 📝 💡 🎉 🎊 🛡️ 🎒 🛍️ 🎨 🤝 💬 📅 🌱 🌳 🏔️ 🌋 🐍 🐛 🧪 🍀 🌈 ❤️ 🎁 🦄 🐱 🐶 🦊 🐼'.split(' ');
  async function adminBadges() {
    const [bd, ub, rw] = await Promise.all([sb.from('badge_defs').select('*').order('position').order('id'), sb.from('user_badges').select('badge_id'), Promise.resolve(sb.rpc('badge_reward_map')).catch(() => null)]);
    BD_RW = (rw && rw.data) || {};
    if (bd.error) return [`<div class="card pad muted">${GROW_HINT}</div>`];
    const defs = bd.data || [];
    const cnt = {}; (ub.data || []).forEach((x) => { cnt[x.badge_id] = (cnt[x.badge_id] || 0) + 1; });
    const TONES = ['blue', 'green', 'orange', 'purple', 'red', 'gold', 'teal', 'pink'];
    const KN = (k) => (BD_KINDS.find(([x]) => x === k) || [k, k, ''])[1];
    return [`
      <div class="card"><h3>🎖️ 배지 만들기 <span class="muted small">(지금 ${defs.length}개)</span></h3>
        <p class="muted small">조건을 정하면 학생이 조건을 채울 때 <b>자동으로</b> 받아요. “직접 지급”은 선생님이 [🏆 성장] 탭에서 학생에게 줘요.</p>
        <form id="bdForm">
          <div class="bd-prevrow"><div id="bdPrev"></div>
            <div class="bd-fields">
              <label>이름<input type="text" id="bdName" maxlength="30" required placeholder="예) 100문제 돌파"></label>
              <label>설명<input type="text" id="bdDesc" maxlength="120" placeholder="예) 문제를 100개 맞췄어요"></label>
            </div></div>
          <label>아이콘 <input type="text" id="bdIcon" maxlength="8" value="🏅" style="width:90px"></label>
          <div class="bd-icons">${BD_ICONS.map((e) => `<button type="button" data-ic="${e}">${e}</button>`).join('')}</div>
          <div class="ga-grid">
            <label>조건<select id="bdKind">${BD_KINDS.map(([k, n]) => `<option value="${k}">${n}</option>`).join('')}</select></label>
            <label>기준 값 <span class="muted small" id="bdUnit"></span><input type="number" id="bdTh" min="0" value="10"></label>
            <label>색<select id="bdTone">${TONES.map((t) => `<option>${t}</option>`).join('')}</select></label>
            <label>보상 💎 <span class="muted small">(비우면 색 기본값)</span><input type="number" id="bdRw" min="0" max="100000" placeholder="기본값"></label>
            <label>고유 ID <span class="muted small">(비우면 자동)</span><input type="text" id="bdId" pattern="[a-z0-9_]{2,40}" placeholder="자동"></label>
          </div>
          <div class="form-actions"><button class="ghost" type="button" id="bdNew">새로 쓰기</button><button class="primary">저장</button></div>
        </form></div>
      <div class="card"><h3>📋 배지 목록</h3>
        <div class="mk-bar"><select id="bdFk"><option value="">모든 조건</option>${BD_KINDS.map(([k, n]) => `<option value="${k}">${n}</option>`).join('')}</select><input type="search" id="bdFq" class="bd-q" placeholder="이름 검색"></div>
        <div id="bdList" class="bdg-grid"></div></div>`,
    (v) => {
      const prev = () => {
        const k = $('#bdKind', v).value; const u = (BD_KINDS.find(([x]) => x === k) || [])[2] || '';
        $('#bdUnit', v).textContent = u ? `(${u})` : '';
        $('#bdTh', v).disabled = k === 'manual';
        $('#bdPrev', v).innerHTML = badgeTile({ tone: $('#bdTone', v).value, descr: $('#bdDesc', v).value, icon: $('#bdIcon', v).value || '🏅', name: $('#bdName', v).value || '이름' }, new Date());
      };
      ['#bdName', '#bdDesc', '#bdIcon', '#bdKind', '#bdTone'].forEach((s) => { $(s, v).oninput = prev; $(s, v).onchange = prev; });
      v.querySelectorAll('[data-ic]').forEach((b) => (b.onclick = () => { $('#bdIcon', v).value = b.dataset.ic; prev(); }));
      const list = () => {
        const fk = $('#bdFk', v).value; const fq = $('#bdFq', v).value.trim().toLowerCase();
        $('#bdList', v).innerHTML = defs.filter((b) => (!fk || b.kind === fk) && (!fq || b.name.toLowerCase().includes(fq))).map((b) => `<div class="bdg tone-${esc(b.tone)} on"><div class="bdg-ic">${esc(b.icon)}</div><b>${esc(b.name)}</b><span class="muted small">${esc(KN(b.kind))}${b.kind === 'manual' ? '' : ' ' + Number(b.threshold).toLocaleString()} · ${cnt[b.id] || 0}명 · 💎${BD_RW[b.id] ?? 0}</span><span><button class="link" data-bedit="${esc(b.id)}" type="button">수정</button> <button class="link danger" data-bdel="${esc(b.id)}" type="button">삭제</button></span></div>`).join('') || '<p class="muted small">없어요.</p>';
        v.querySelectorAll('[data-bedit]').forEach((b) => (b.onclick = () => {
          const d = defs.find((x) => x.id === b.dataset.bedit);
          $('#bdId', v).value = d.id; $('#bdId', v).readOnly = true; $('#bdName', v).value = d.name; $('#bdIcon', v).value = d.icon; $('#bdDesc', v).value = d.descr;
          $('#bdKind', v).value = d.kind; $('#bdTh', v).value = d.threshold; $('#bdTone', v).value = d.tone; $('#bdRw', v).value = d.reward == null ? '' : d.reward;
          prev(); $('#bdForm', v).scrollIntoView({ behavior: 'smooth', block: 'center' });
        }));
        v.querySelectorAll('[data-bdel]').forEach((b) => (b.onclick = async () => {
          const d = defs.find((x) => x.id === b.dataset.bdel);
          if (!confirm(`“${d.name}” 배지를 지울까요? 학생들이 받은 기록(${cnt[d.id] || 0}명)도 같이 사라져요.`)) return;
          const { data, error } = await sb.rpc('badge_delete', { p_id: d.id });
          if (error) return toast('지우지 못했어요', true);
          if (data !== 'ok') return toast('기본으로 들어 있는 배지는 지울 수 없어요 (고치는 건 돼요)', true);
          toast('지웠어요'); route(true);
        }));
      };
      $('#bdFk', v).onchange = list; $('#bdFq', v).oninput = list;
      $('#bdNew', v).onclick = () => { $('#bdForm', v).reset(); $('#bdId', v).readOnly = false; prev(); };
      $('#bdForm', v).onsubmit = async (e) => {
        e.preventDefault();
        const name = $('#bdName', v).value.trim();
        if (!name) return toast('이름을 써주세요', true);
        let id = $('#bdId', v).value.trim();
        if (!id) id = 'c_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 5);
        const k = $('#bdKind', v).value;
        const th = k === 'manual' ? 0 : parseInt($('#bdTh', v).value, 10);
        if (k !== 'manual' && !(th > 0)) return toast('기준 값은 1 이상으로 적어주세요', true);
        const old = defs.find((x) => x.id === id);
        const p = { id, name, icon: $('#bdIcon', v).value.trim() || '🏅', descr: $('#bdDesc', v).value.trim(), kind: k, threshold: th, tone: $('#bdTone', v).value, position: old ? old.position : 1000, reward: $('#bdRw', v).value === '' ? null : parseInt($('#bdRw', v).value, 10) };
        const { data, error } = await sb.rpc('badge_upsert', { p });
        if (error || data !== 'ok') return toast(data === 'invalid' ? '저장하지 못했어요 (입력값을 확인해주세요. 새 조건은 v453 SQL 실행이 필요해요)' : '저장하지 못했어요', true);
        toast('배지를 저장했어요'); route(true);
      };
      prev(); list();
    }];
  }

  // ---- 관리자 > 성장 (점수·파이포인트·배지·보상 설정)
  async function adminGrowth() {
    const [pr, bd, cf] = await Promise.all([
      sb.from('profiles').select('id,username').eq('status', 'approved').neq('role', 'admin'),
      sb.from('badge_defs').select('*').order('position').order('id'),
      sb.from('py_config').select('key,val'),
    ]);
    if (bd.error || cf.error) return [`<div class="card pad muted">${GROW_HINT}</div>`];
    const studs = (pr.data || []).filter((x) => x.id !== me.id).map((x) => ({ id: x.id, name: dname(x.id, x.username) })).sort((a, b) => a.name.localeCompare(b.name, 'ko'));
    const defs = bd.data || [];
    const KINDS = [['score', '랭킹 점수'], ['solved', '푼 문제 수'], ['streak', '연속 학습(일)'], ['learn', '끝낸 레슨 수'], ['exam_join', '시험 응시'], ['exam_first', '시험 1등'], ['pypoint', '누적 파이포인트'], ['manual', '직접 지급']];
    const TONES = ['blue', 'green', 'orange', 'purple', 'red', 'gold', 'teal', 'pink'];
    const CFG = [['week_rank', '주간 랭킹 1·2·3위 보상', '[30,20,10]'], ['month_rank', '월간 랭킹 1·2·3위 보상', '[100,60,30]'], ['solve_rand', '문제 맞출 때 랜덤 (최소,최대)', '[2,6]'], ['learn_rand', '레슨 끝낼 때 랜덤 (최소,최대)', '[3,8]'], ['shield_price', '방어권 가격', '600'], ['shield_max', '방어권 최대 개수', '2'], ['badge_reward', '🎖️ 배지 보상 (색별 기본 💎)', '{"blue":10,"green":15,"teal":20,"orange":30,"red":40,"purple":60,"pink":80,"gold":150}'], ['item_price_mult', '🛍️ 상점 아이템 가격 배율 (기본 가격 × 이 값)', '30'], ['gacha', '🎰 뽑기 가격', '{"basic":1500,"premium":5000}'], ['gift', '🎁 선물 (수수료 %, 최소, 최대, 하루 한도)', '{"fee":10,"min":100,"max":5000,"daily":10000}']];
    const CV = {}; (cf.data || []).forEach((r) => { CV[r.key] = JSON.stringify(r.val); });
    return [`
      <div class="card"><h3>👤 학생 점수·파이포인트</h3>
        <label>학생<select id="gaUser"><option value="">— 고르세요 —</option>${studs.map((s) => `<option value="${s.id}">${esc(s.name)}</option>`).join('')}</select></label>
        <div id="gaInfo" class="muted small" style="margin:8px 0">학생을 고르면 현재 상태가 보여요.</div>
        <div class="ga-grid">
          <form id="gaScore"><h4>🏆 랭킹 점수 조정</h4><input type="number" id="gaSv" placeholder="+100 / -50" required><input type="text" id="gaSn" maxlength="100" placeholder="사유 (학생에게 알림으로 가요)"><button class="primary">적용</button></form>
          <form id="gaPy"><h4>💎 파이포인트 지급/차감</h4><input type="number" id="gaPv" placeholder="+50 / -20" required><input type="text" id="gaPn" maxlength="100" placeholder="사유"><button class="primary">적용</button></form>
          <form id="gaBadge"><h4>🎖️ 배지 지급/회수</h4><select id="gaBd">${defs.map((b) => `<option value="${esc(b.id)}">${esc(b.icon)} ${esc(b.name)}</option>`).join('')}</select><div class="form-actions"><button class="primary" data-on="1">지급</button><button class="ghost" data-on="0">회수</button></div></form>
        </div></div>
      <div class="card"><h3>🎖️ 배지 만들기·고치기</h3><p class="muted small">배지 만들기는 위쪽 <b>🎖️ 배지</b> 탭으로 옮겼어요. (지급/회수는 여기서 계속 할 수 있어요)</p><button class="ghost" id="gaGoBd" type="button">🎖️ 배지 탭 열기</button></div>
      <div class="card"><h3>⚙️ 파이포인트 보상 설정</h3><p class="muted small">JSON 형식 그대로 적어요. 예) 주간 보상 [30,20,10]</p>
        ${CFG.map(([k, n, ph]) => `<div class="cfg-row"><label style="flex:1">${n}<input type="text" data-cfg="${k}" value="${esc(CV[k] || ph)}"></label><button class="ghost" data-cfgsave="${k}" type="button">저장</button></div>`).join('')}</div>`,
    (v) => {
      const MSG = { forbidden: '권한이 없어요', invalid: '값이 올바르지 않아요', nouser: '학생을 찾을 수 없어요', ok: '적용했어요' };
      const pick = () => $('#gaUser', v).value;
      const info = async () => {
        const u = pick();
        const box = $('#gaInfo', v);
        if (!u) { box.textContent = '학생을 고르면 현재 상태가 보여요.'; return; }
        const { data, error } = await sb.rpc('admin_user_wallet', { p_uid: u });
        if (error || !data) { box.textContent = '불러오지 못했어요'; return; }
        box.innerHTML = `<b>🏆 ${data.score.toLocaleString()}점 · 💎 ${data.balance} · 🛡️ ${data.shields}</b><br>${(data.adjust || []).slice(0, 5).map((a) => `점수 ${a.delta > 0 ? '+' : ''}${a.delta} (${esc(a.note || '-')}) · ${fmt(a.created_at)}`).join('<br>') || '점수 조정 기록 없음'}`;
      };
      $('#gaUser', v).onchange = info;
      const run = async (rpc, args, form) => {
        if (!pick()) return toast('학생을 먼저 고르세요', true);
        const { data, error } = await sb.rpc(rpc, args);
        if (error) return toast('처리하지 못했어요: ' + error.message, true);
        toast(MSG[data] || String(data), data !== 'ok');
        if (data === 'ok') { if (form) form.reset(); info(); await loadDir(); }
      };
      $('#gaScore', v).onsubmit = (e) => { e.preventDefault(); run('admin_adjust_score', { p_uid: pick(), p_delta: parseInt($('#gaSv', v).value, 10), p_note: $('#gaSn', v).value }, e.target); };
      $('#gaPy', v).onsubmit = (e) => { e.preventDefault(); run('admin_grant_py', { p_uid: pick(), p_delta: parseInt($('#gaPv', v).value, 10), p_note: $('#gaPn', v).value }, e.target); };
      $('#gaBadge', v).onsubmit = (e) => { e.preventDefault(); run('badge_award', { p_uid: pick(), p_id: $('#gaBd', v).value, p_on: e.submitter && e.submitter.dataset.on === '1' }); };
      $('#gaGoBd', v).onclick = () => { adminTab = 'badges'; route(); };
      v.querySelectorAll('[data-cfgsave]').forEach((b) => (b.onclick = async () => {
        const k = b.dataset.cfgsave;
        let val;
        try { val = JSON.parse($(`[data-cfg="${k}"]`, v).value); } catch (e) { return toast('JSON 형식이 올바르지 않아요', true); }
        const { data, error } = await sb.rpc('py_cfg_set', { p_key: k, p_val: val });
        if (error || data !== 'ok') return toast('저장하지 못했어요', true);
        toast('저장했어요');
      }));
    }];
  }

  // ---- 마켓: 학생이 아이템 올리기
  const MK_ERR = { nouser: '학생 계정만 올릴 수 있어요', price: '가격은 100~20000 이에요', many: '심사 대기는 5개까지 가능해요', limit: '올릴 수 있는 개수(40개)를 넘었어요', invalid: '그림이나 입력값을 확인해주세요 (도형만 가능, 8000자 이하)' };
  function openMarketForm(ex, av, done) {
    const m = modal(`<h3>${ex ? '✏️ 아이템 고쳐서 다시 올리기' : '✏️ 새 아이템 올리기'}</h3>
      <p class="muted small">SVG 그림 파일을 고르거나 코드를 붙여넣어요. 도형(path·circle·rect…)만 쓸 수 있고, 글자·이미지·스크립트는 지워져요. 선생님이 확인하면 마켓에 올라가요.</p>
      <div class="mk-form">
        <div class="mk-prev" id="mkPrev"></div>
        <div class="mk-fields">
          <label>이름<input type="text" id="mkName" maxlength="30" value="${esc(ex ? ex.name : '')}"></label>
          <label>자리<select id="mkSlot">${ITEM_SLOTS.map(([k, n]) => `<option value="${k}" ${ex && ex.slot === k ? 'selected' : ''}>${n}</option>`).join('')}</select></label>
          <label>가격 💎 (100~20000) <span class="muted small">— 팔리면 80% 가 내 몫이에요</span><input type="number" id="mkPrice" min="100" max="20000" value="${ex ? ex.price : 500}"></label>
          <label>설명 (선택)<input type="text" id="mkDesc" maxlength="120" value="${esc(ex ? ex.descr : '')}"></label>
        </div></div>
      <label>그림 파일 (.svg)<input type="file" id="mkFile" accept=".svg,image/svg+xml"></label>
      <label>또는 SVG 코드 붙여넣기<textarea id="mkSvg" class="code" rows="6" placeholder='<svg viewBox="0 0 100 100"><circle cx="50" cy="10" r="8" fill="#f00"/></svg>'>${esc(ex ? ex.svg : '')}</textarea></label>
      <p class="muted small">그림 칸은 가로·세로 100 기준이에요. 얼굴 중심은 (50,46), 머리 꼭대기는 y=20 근처예요. 자세한 건 선생님께 받은 AVATAR_ITEM_GUIDE.md 를 보세요.</p>
      <div class="form-actions"><button class="primary" id="mkGo" type="button">${ex ? '다시 올리기' : '올리기'}</button></div>`);
    const root = m.el;
    const cur = () => cleanSvg(extractSvg($('#mkSvg', root).value));
    const prev = () => { const sv = $('#mkSvg', root).value.trim() ? cur() : ''; $('#mkPrev', root).innerHTML = sv ? itemPreview($('#mkSlot', root).value, sv, 130, av) : '<span class="muted small">미리보기</span>'; };
    ['input', 'change'].forEach((ev) => { $('#mkSvg', root).addEventListener(ev, prev); $('#mkSlot', root).addEventListener(ev, prev); });
    $('#mkFile', root).onchange = async (e) => { const f = e.target.files[0]; if (f) { $('#mkSvg', root).value = await f.text(); prev(); } };
    prev();
    $('#mkGo', root).onclick = async () => {
      const svg = cur();
      const name = $('#mkName', root).value.trim();
      if (!name) return toast('이름을 적어주세요', true);
      if (!svg) return toast('그림이 비었거나 읽을 수 없어요', true);
      const { data, error } = await sb.rpc('market_submit', { p: { id: ex ? ex.id : null, name, slot: $('#mkSlot', root).value, price: parseInt($('#mkPrice', root).value, 10), descr: $('#mkDesc', root).value.trim(), svg } });
      if (error) return toast('올리지 못했어요: ' + error.message, true);
      if (data !== 'ok') return toast(MK_ERR[data] || '올리지 못했어요', true);
      toast('올렸어요! 선생님이 확인하면 마켓에 올라가요 🛍️');
      m.close();
      if (done) done();
    };
  }

  // ---- 관리자 > 마켓·행사
  const toLocalInput = (d) => { const x = new Date(d); return new Date(x.getTime() - x.getTimezoneOffset() * 6e4).toISOString().slice(0, 16); };
  async function adminMarket() {
    const [pd, ev, it] = await Promise.all([
      sb.from('avatar_items').select('*').eq('market', true).eq('status', 'pending').order('created_at'),
      sb.from('events').select('*').order('starts_at', { ascending: false }),
      sb.from('avatar_items').select('id,name,slot,kind,event_id,price,market,status').eq('market', false).neq('status', 'hidden'),
    ]);
    if (pd.error || ev.error) return ['<div class="card pad muted">아직 준비되지 않았어요. (관리자가 v452_market_events.sql 을 실행하면 쓸 수 있어요)</div>'];
    const pend = pd.data || [];
    const evs = ev.data || [];
    const its = it.data || [];
    const TONES = ['orange', 'red', 'gold', 'green', 'teal', 'blue', 'purple', 'pink'];
    const now = Date.now();
    const evState = (e) => (e.status !== 'on' ? '꺼짐' : new Date(e.ends_at) <= now ? '종료' : new Date(e.starts_at) > now ? '예정' : '진행 중');
    return [`
      <div class="card"><h3>🛍️ 마켓 심사 대기 (${pend.length})</h3>
        ${pend.map((x) => `<div class="mk-row"><span class="it-pv">${itemPreview(x.slot, x.svg, 72)}</span><div class="mk-info"><b>${esc(x.name)}</b> <span class="chip">${esc((ITEM_SLOTS.find(([k]) => k === x.slot) || [])[1] || x.slot)}</span> 💎 ${x.price}<br><span class="muted small">by ${esc(dname(x.created_by, '?'))} · ${fmt(x.created_at)}${x.descr ? ` · ${esc(x.descr)}` : ''}</span></div><div><button class="primary" data-mkok="${esc(x.id)}" type="button">승인</button> <button class="ghost" data-mkno="${esc(x.id)}" type="button">반려</button></div></div>`).join('') || '<p class="muted">심사 대기 중인 아이템이 없어요.</p>'}</div>
      <div class="card"><h3>🎪 행사 만들기·고치기</h3>
        <form id="evForm"><input type="hidden" id="evId"><div class="ga-grid">
          <label>제목<input type="text" id="evTitle" maxlength="40" required placeholder="가을 할로윈 행사"></label>
          <label>이모지<input type="text" id="evEmoji" maxlength="8" value="🎃"></label>
          <label>배너 색<select id="evTone">${TONES.map((t) => `<option>${t}</option>`).join('')}</select></label>
          <label>시작<input type="datetime-local" id="evFrom" required value="${toLocalInput(new Date())}"></label>
          <label>끝<input type="datetime-local" id="evTo" required value="${toLocalInput(new Date(Date.now() + 7 * 864e5))}"></label>
          <label>파이포인트 배수 (1=그대로, 2=2배)<input type="number" id="evMult" min="1" max="10" step="0.5" value="1"></label></div>
          <label>설명<input type="text" id="evDesc" maxlength="300" placeholder="행사 기간 동안 문제 풀이·학습 보상 파이포인트가 2배!"></label>
          <label class="inline"><input type="checkbox" id="evOn" checked> 켜기 (끄면 기간이어도 열리지 않아요)</label>
          <div class="form-actions"><button class="primary">저장</button><button class="ghost" type="button" id="evReset">새로 쓰기</button></div></form></div>
      <div class="card"><h3>🎪 행사 목록 (${evs.length})</h3>
        ${evs.map((e) => `<div class="mk-row"><span class="it-pv">${esc(e.emoji)}</span><div class="mk-info"><b>${esc(e.title)}</b> <span class="chip">${evState(e)}</span>${Number(e.py_mult) > 1 ? ` <span class="chip">💎 ×${Number(e.py_mult)}</span>` : ''}<br><span class="muted small">${fmt(e.starts_at)} ~ ${fmt(e.ends_at)} · 한정 아이템 ${its.filter((x) => x.event_id === e.id).map((x) => esc(x.name)).join(', ') || '없음'}</span></div><div><button class="ghost" data-evedit="${e.id}" type="button">수정</button> <button class="ghost" data-evnote="${e.id}" type="button">📣 알림</button> <button class="link danger" data-evdel="${e.id}" type="button">삭제</button></div></div>`).join('') || '<p class="muted">행사가 없어요.</p>'}</div>
      <div class="card"><h3>🎁 행사 한정 아이템 붙이기</h3>
        <p class="muted small">고른 아이템의 얻는 조건이 "행사 한정"으로 바뀌어요. 가격 0 = 행사 중 무료 받기, 가격 &gt; 0 = 행사 중 파이포인트로 구입. 행사가 끝나면 새로 못 얻고, 이미 가진 건 계속 써요.</p>
        <div class="ga-grid"><label>행사<select id="eiEv">${evs.map((e) => `<option value="${e.id}">${esc(e.emoji)} ${esc(e.title)}</option>`).join('')}</select></label>
          <label>아이템<select id="eiItem">${its.map((x) => `<option value="${esc(x.id)}">${esc(x.name)}${x.kind === 'event' ? ' (행사)' : ''}</option>`).join('')}</select></label>
          <label>가격 💎<input type="number" id="eiPrice" min="0" value="0"></label></div>
        <div class="form-actions"><button class="primary" id="eiGo" type="button">붙이기</button></div></div>`,
    (v) => {
      const reload = () => route(true);
      v.querySelectorAll('[data-mkok]').forEach((b) => (b.onclick = async () => { const { data } = await sb.rpc('market_review', { p_id: b.dataset.mkok, p_ok: true, p_note: '' }); if (data === 'ok') { await loadItems(); toast('승인했어요'); reload(); } else toast('처리하지 못했어요', true); }));
      v.querySelectorAll('[data-mkno]').forEach((b) => (b.onclick = async () => {
        const note = prompt('반려 사유를 적어주세요 (학생에게 알림으로 가요)', '');
        if (note === null) return;
        const { data } = await sb.rpc('market_review', { p_id: b.dataset.mkno, p_ok: false, p_note: note });
        if (data === 'ok') { toast('반려했어요'); reload(); } else toast('처리하지 못했어요', true);
      }));
      const fill = (e) => {
        $('#evId', v).value = e ? e.id : ''; $('#evTitle', v).value = e ? e.title : ''; $('#evEmoji', v).value = e ? e.emoji : '🎃';
        $('#evTone', v).value = e ? e.tone : 'orange'; $('#evFrom', v).value = toLocalInput(e ? e.starts_at : new Date());
        $('#evTo', v).value = toLocalInput(e ? e.ends_at : new Date(Date.now() + 7 * 864e5)); $('#evMult', v).value = e ? e.py_mult : 1;
        $('#evDesc', v).value = e ? e.descr : ''; $('#evOn', v).checked = e ? e.status === 'on' : true;
      };
      v.querySelectorAll('[data-evedit]').forEach((b) => (b.onclick = () => { fill(evs.find((e) => String(e.id) === b.dataset.evedit)); $('#evForm', v).scrollIntoView({ behavior: 'smooth', block: 'center' }); }));
      $('#evReset', v).onclick = () => fill(null);
      $('#evForm', v).onsubmit = async (e) => {
        e.preventDefault();
        const p = { id: $('#evId', v).value || null, title: $('#evTitle', v).value.trim(), emoji: $('#evEmoji', v).value.trim() || '🎉', tone: $('#evTone', v).value, descr: $('#evDesc', v).value.trim(),
          starts_at: new Date($('#evFrom', v).value).toISOString(), ends_at: new Date($('#evTo', v).value).toISOString(), py_mult: Number($('#evMult', v).value) || 1, status: $('#evOn', v).checked ? 'on' : 'off' };
        if (new Date(p.ends_at) <= new Date(p.starts_at)) return toast('끝나는 시각이 시작보다 늦어야 해요', true);
        const { data, error } = await sb.rpc('event_upsert', { p });
        if (error || data !== 'ok') return toast('저장하지 못했어요 (입력값을 확인해주세요)', true);
        toast('행사를 저장했어요'); loadEvents(); reload();
      };
      v.querySelectorAll('[data-evdel]').forEach((b) => (b.onclick = async () => { if (!confirm('행사를 지울까요? (붙어 있던 아이템은 그대로 남아요)')) return; const { data } = await sb.rpc('event_delete', { p_id: Number(b.dataset.evdel) }); if (data === 'ok') { loadEvents(); reload(); } }));
      v.querySelectorAll('[data-evnote]').forEach((b) => (b.onclick = async () => {
        const e = evs.find((x) => String(x.id) === b.dataset.evnote);
        if (!confirm(`모든 학생에게 "${e.emoji} ${e.title}" 알림을 보낼까요?`)) return;
        const { data, error } = await sb.rpc('notify_all', { p_title: `${e.emoji} ${e.title}`, p_body: e.descr || '행사가 열렸어요!', p_link: '#/home' });
        if (error) return toast('보내지 못했어요: ' + error.message, true);
        toast(`${data}명에게 보냈어요`);
      }));
      $('#eiGo', v).onclick = async () => {
        const evId = Number($('#eiEv', v).value);
        if (!evId) return toast('행사를 먼저 만들어주세요', true);
        const { data, error } = await sb.rpc('event_item_set', { p_event: evId, p_item: $('#eiItem', v).value, p_price: parseInt($('#eiPrice', v).value, 10) || 0 });
        if (error || data !== 'ok') return toast('붙이지 못했어요', true);
        await loadItems(); toast('붙였어요'); reload();
      };
    }];
  }

  // ---- 관리자 > 아이템 (업로드 · 목록 · 문제 보상 · 지급)
  const ITEM_FMT = 'pynest-avatar-item-v1';
  function parseItemJson(text) {
    let d;
    try { d = JSON.parse(text); } catch (e) { throw new Error('JSON 형식 오류예요'); }
    if (d && !Array.isArray(d) && d.format && d.format !== ITEM_FMT) throw new Error('지원하지 않는 형식이에요: ' + d.format);
    const arr = Array.isArray(d) ? d : d && Array.isArray(d.items) ? d.items : d && d.id ? [d] : null;
    if (!arr || !arr.length) throw new Error('items 목록이 없어요');
    const KINDS = ['free', 'score', 'streak', 'tier', 'rank1', 'price', 'reward', 'event'];
    return arr.map((x, n) => {
      const u = x.unlock || {};
      const kind = u.type || x.kind || 'free';
      const label = `#${n + 1}${x.id ? ` (${x.id})` : ''}`;
      if (!/^[a-z0-9_]{2,40}$/.test(String(x.id || ''))) throw new Error(`${label}: id 는 영문 소문자·숫자·_ 2~40자예요`);
      if (!x.name || String(x.name).length > 30) throw new Error(`${label}: name 은 1~30자예요`);
      if (!ITEM_SLOTS.some(([k]) => k === x.slot)) throw new Error(`${label}: slot 은 ${ITEM_SLOTS.map(([k]) => k).join(' / ')} 중 하나예요`);
      if (!KINDS.includes(kind)) throw new Error(`${label}: unlock.type 은 ${KINDS.join(' / ')} 중 하나예요`);
      if (typeof x.svg !== 'string' || !cleanSvg(x.svg)) throw new Error(`${label}: svg 가 비었거나 쓸 수 없는 내용이에요 (도형만 가능)`);
      const price = Number(u.price ?? x.price ?? 0) || 0;
      if (kind === 'price' && price <= 0) throw new Error(`${label}: price 유형은 unlock.price 가 필요해요`);
      return { id: x.id, name: String(x.name), descr: String(x.descr || ''), slot: x.slot, svg: x.svg, kind, val: Number(u.value ?? x.val ?? 0) || 0, price, status: x.status === 'hidden' ? 'hidden' : 'active' };
    });
  }
  async function adminItems() {
    const [it, rw, ps, ex, pr] = await Promise.all([
      sb.from('avatar_items').select('*').order('slot').order('id'),
      sb.from('exercise_rewards').select('exercise_id,item_id'),
      sb.from('problem_sets').select('id,title').order('id', { ascending: false }),
      sb.from('exercises').select('id,set_id,position,label,difficulty').order('position'),
      sb.from('profiles').select('id,username').eq('status', 'approved').neq('role', 'admin'),
    ]);
    if (it.error) return [`<div class="card pad muted">아직 준비되지 않았어요. (관리자가 v451_items.sql 을 실행하면 쓸 수 있어요)</div>`];
    const items = it.data || [];
    const rewards = rw.data || [];
    const sets = ps.data || [];
    const exs = ex.data || [];
    const studs = (pr.data || []).filter((x) => x.id !== me.id).map((x) => ({ id: x.id, name: dname(x.id, x.username) })).sort((a, b) => a.name.localeCompare(b.name, 'ko'));
    const base = normAv(null, 'preview');
    const pv = (i) => { ITEMS.set('__pv', { id: '__pv', name: '', slot: i.slot, svg: cleanSvg(i.svg) }); const h = avatarSvg({ ...base, items: { [i.slot]: '__pv' } }, 56); ITEMS.delete('__pv'); return h; };
    const KN = { free: '기본', score: '점수', streak: '연속 출석', tier: '티어', rank1: '1등 횟수', price: '구입', reward: '문제 보상', event: '행사' };
    const cond = (i) => (i.kind === 'score' ? `${Number(i.val).toLocaleString()}점 이상` : i.kind === 'tier' ? `${(TIERS[i.val] || {}).n || i.val} 티어 이상` : i.kind === 'streak' ? `${i.val}일 연속` : i.kind === 'rank1' ? `1등 ${i.val}회` : i.kind === 'price' ? `💎 ${i.price}` : '');
    const rwBy = new Map(rewards.map((r) => [String(r.exercise_id), r.item_id]));
    return [`
      <div class="card"><h3>📤 아이템 올리기 (JSON)</h3>
        <p class="muted small">형식 <code>${ITEM_FMT}</code> — 파일을 고르거나 아래에 붙여넣어요. 같은 id 로 다시 올리면 덮어써요. 그림(svg)은 <b>100×100 칸</b> 기준 도형(path·circle·rect 등)만 쓸 수 있어요. 자세한 설명은 AVATAR_ITEM_GUIDE.md</p>
        <input type="file" id="itFile" accept=".json,application/json">
        <textarea id="itJson" class="code" rows="8" placeholder='{"format":"pynest-avatar-item-v1","items":[{"id":"red_cap","name":"빨간 모자","slot":"hat","svg":"<path d=\\"M24 38 C26 10 74 10 76 38Z\\" fill=\\"#ef4444\\"/>","unlock":{"type":"price","price":30}}]}'></textarea>
        <div class="form-actions"><button class="ghost" id="itPrev" type="button">미리보기</button><button class="primary" id="itUp" type="button">올리기</button><button class="ghost" id="itSample" type="button">예시 넣기</button></div>
        <div id="itPrevBox" class="it-grid"></div></div>
      <div class="card"><h3>🎁 아이템 목록 (${items.length})</h3>
        <div class="it-grid adm">${items.map((i) => `<div class="it-tile ${i.status === 'hidden' ? 'lock' : 'own'}"><span class="it-pv">${pv(i)}</span><b>${esc(i.name)}</b><span class="muted small">${esc((ITEM_SLOTS.find(([k]) => k === i.slot) || [])[1] || i.slot)} · ${KN[i.kind]} ${esc(cond(i))}</span><span class="muted small">${esc(i.id)}${i.status === 'hidden' ? ' · 숨김' : ''}</span><span><button class="link" data-itex="${esc(i.id)}" type="button">JSON</button> ${i.status === 'hidden' ? `<button class="link" data-itshow="${esc(i.id)}" type="button">보이기</button>` : ''} <button class="link danger" data-itdel="${esc(i.id)}" type="button">${i.builtin ? '숨김' : '삭제'}</button></span></div>`).join('')}</div></div>
      <div class="card"><h3>🏅 문제 보상 연결</h3>
        <p class="muted small">그 문제를 처음 맞춘 학생에게 아이템을 줘요. (이미 푼 학생에게는 지급되지 않아요)</p>
        <div class="ga-grid"><label>문제집<select id="rwSet"><option value="">— 고르세요 —</option>${sets.map((s2) => `<option value="${s2.id}">${esc(s2.title)}</option>`).join('')}</select></label>
          <label>문제<select id="rwEx"><option value="">— 문제집을 먼저 —</option></select></label>
          <label>보상 아이템<select id="rwItem"><option value="">(없음 — 연결 해제)</option>${items.filter((i) => i.status === 'active').map((i) => `<option value="${esc(i.id)}">${esc(i.name)}</option>`).join('')}</select></label></div>
        <div class="form-actions"><button class="primary" id="rwSave" type="button">연결 저장</button></div>
        <div id="rwList" class="muted small">${rewards.length ? rewards.map((r) => { const e = exs.find((x) => x.id === r.exercise_id); const s2 = e && sets.find((x) => x.id === e.set_id); return `<div>${esc(s2 ? s2.title : '?')} › #${e ? Math.round(e.position / 1000) : '?'} ${esc((e && e.difficulty) || '')} → <b>${esc((items.find((i) => i.id === r.item_id) || {}).name || r.item_id)}</b> <button class="link danger" data-rwdel="${r.exercise_id}" type="button">해제</button></div>`; }).join('') : '연결된 문제가 없어요.'}</div></div>
      <div class="card"><h3>🎀 학생에게 아이템 선물</h3>
        <div class="ga-grid"><label>학생<select id="gvUser"><option value="">— 고르세요 —</option>${studs.map((s2) => `<option value="${s2.id}">${esc(s2.name)}</option>`).join('')}</select></label>
          <label>아이템<select id="gvItem">${items.filter((i) => i.status === 'active').map((i) => `<option value="${esc(i.id)}">${esc(i.name)}</option>`).join('')}</select></label></div>
        <div class="form-actions"><button class="primary" id="gvBtn" type="button">선물하기</button></div></div>`,
    (v) => {
      const SAMPLE = { format: ITEM_FMT, items: [{ id: 'red_cap', name: '빨간 야구모자', descr: '시작이 반이다', slot: 'hat', svg: '<path d="M24 38 C26 10 74 10 76 38Z" fill="#ef4444"/><path d="M66 34 H93 Q93 42 66 41Z" fill="#b91c1c"/>', unlock: { type: 'price', price: 30 } }] };
      $('#itSample', v).onclick = () => { $('#itJson', v).value = JSON.stringify(SAMPLE, null, 2); };
      $('#itFile', v).onchange = async (e) => { const f = e.target.files[0]; if (f) $('#itJson', v).value = await f.text(); };
      const parse = () => { try { return parseItemJson($('#itJson', v).value); } catch (e) { toast(e.message, true); return null; } };
      $('#itPrev', v).onclick = () => {
        const arr = parse();
        if (!arr) return;
        $('#itPrevBox', v).innerHTML = arr.map((i) => `<div class="it-tile own"><span class="it-pv">${pv(i)}</span><b>${esc(i.name)}</b><span class="muted small">${esc(i.slot)} · ${KN[i.kind]} ${esc(cond(i))}</span></div>`).join('');
      };
      $('#itUp', v).onclick = async () => {
        const arr = parse();
        if (!arr) return;
        let ok = 0;
        for (const i of arr) {
          const { data, error } = await sb.rpc('item_upsert', { p: i });
          if (error || data !== 'ok') { toast(`${i.id}: 올리지 못했어요 (도형·값을 확인해주세요)`, true); continue; }
          ok += 1;
        }
        if (ok) { toast(`${ok}개 올렸어요`); await loadItems(); route(true); }
      };
      v.querySelectorAll('[data-itex]').forEach((b) => (b.onclick = () => {
        const i = items.find((x) => x.id === b.dataset.itex);
        $('#itJson', v).value = JSON.stringify({ format: ITEM_FMT, items: [{ id: i.id, name: i.name, descr: i.descr, slot: i.slot, svg: i.svg, unlock: { type: i.kind, value: i.val, price: i.price } }] }, null, 2);
        $('#itJson', v).scrollIntoView({ behavior: 'smooth', block: 'center' });
      }));
      v.querySelectorAll('[data-itdel]').forEach((b) => (b.onclick = async () => {
        if (!confirm('이 아이템을 지울까요? (기본 아이템은 숨겨져요) 가진 학생의 기록도 같이 사라져요.')) return;
        const { data, error } = await sb.rpc('item_delete', { p_id: b.dataset.itdel });
        if (error || data !== 'ok') return toast('처리하지 못했어요', true);
        await loadItems(); route(true);
      }));
      v.querySelectorAll('[data-itshow]').forEach((b) => (b.onclick = async () => {
        const i = items.find((x) => x.id === b.dataset.itshow);
        const { data } = await sb.rpc('item_upsert', { p: { ...i, status: 'active' } });
        if (data === 'ok') { await loadItems(); route(true); }
      }));
      $('#rwSet', v).onchange = () => {
        const sid = Number($('#rwSet', v).value);
        $('#rwEx', v).innerHTML = '<option value="">— 문제 고르기 —</option>' + exs.filter((e) => e.set_id === sid).map((e) => `<option value="${e.id}">#${Math.round(e.position / 1000)} ${esc(e.difficulty)} ${esc(e.label || '')}${rwBy.has(String(e.id)) ? ' ★' : ''}</option>`).join('');
      };
      $('#rwEx', v).onchange = () => { $('#rwItem', v).value = rwBy.get($('#rwEx', v).value) || ''; };
      $('#rwSave', v).onclick = async () => {
        const e = $('#rwEx', v).value;
        if (!e) return toast('문제를 고르세요', true);
        const { data, error } = await sb.rpc('reward_set', { p_ex: Number(e), p_item: $('#rwItem', v).value });
        if (error || data !== 'ok') return toast('저장하지 못했어요', true);
        toast('저장했어요'); route(true);
      };
      v.querySelectorAll('[data-rwdel]').forEach((b) => (b.onclick = async () => {
        const { data } = await sb.rpc('reward_set', { p_ex: Number(b.dataset.rwdel), p_item: '' });
        if (data === 'ok') route(true);
      }));
      $('#gvBtn', v).onclick = async () => {
        const u = $('#gvUser', v).value;
        if (!u) return toast('학생을 고르세요', true);
        const { data, error } = await sb.rpc('item_give_admin', { p_uid: u, p_item: $('#gvItem', v).value });
        if (error || data !== 'ok') return toast('선물하지 못했어요', true);
        toast('선물했어요 🎁');
      };
    }];
  }

  /* ---------- 설정 ---------- */
  let setTab = 'hub';
  async function pageSettings(tab, extra) {
    const STABS = [['hub', '🏠 내 정보'], ['streak', '🔥 연속 학습'], ['badges', '🎖️ 배지'], ['wallet', '💎 파이포인트'], ['avatar', '🧑‍🎤 캐릭터'], ['prof', '✨ 프로필'], ['dm', '💬 메시지'], ['notif', '🔔 알림'], ['rec', '📋 내 기록'], ['acct', '⚙️ 계정'], ['ide', '⌨️ 편집기']];
    setTab = STABS.some(([k]) => k === tab) ? tab : 'hub'; // 탭 없이 들어오면 항상 내 정보부터
    const dmUid = tab === 'dm' && /^[0-9a-f-]{36}$/i.test(extra || '') ? extra : '';
    return [`
      <h2>👤 나</h2>
      <div class="tabs" id="stabs">${STABS.map(([k, n]) => `<button data-st="${k}" class="${setTab === k ? 'on' : ''}">${n}${k === 'dm' || k === 'notif' ? `<span class="nbadge" data-nb="${k}" hidden></span>` : ''}</button>`).join('')}</div>
      <section data-sp="hub" ${setTab === 'hub' ? '' : 'hidden'} id="spHub"></section>
      <section data-sp="streak" ${setTab === 'streak' ? '' : 'hidden'} id="spStreak"></section>
      <section data-sp="badges" ${setTab === 'badges' ? '' : 'hidden'} id="spBadges"></section>
      <section data-sp="wallet" ${setTab === 'wallet' ? '' : 'hidden'} id="spWallet"></section>
      <section data-sp="acct" ${setTab === 'acct' ? '' : 'hidden'}>
      <div class="card">
        <h3>비밀번호 바꾸기</h3>
        <form id="pwForm">
          <label>새 비밀번호<input type="password" id="np1" autocomplete="new-password" placeholder="6자 이상" required></label>
          <label>새 비밀번호 확인<input type="password" id="np2" autocomplete="new-password" required></label>
          <div class="form-actions"><button class="primary">바꾸기</button></div>
        </form>
      </div>
      <div class="card" id="nickCard">
        <h3>🏷️ 별명</h3>
        <form id="nickForm"><div class="form-actions" style="gap:8px"><input type="text" id="nickIn" maxlength="20" placeholder="한글·영문·숫자 1~20자" style="flex:1" disabled><button class="primary" id="nickBtn" disabled>저장</button></div></form>
        <p class="muted small" id="nickNote">불러오는 중…</p>
      </div>
      <div class="card"><h3>화면</h3><button class="ghost" id="themeBtn2">다크모드 켜기/끄기</button></div>
      <div class="card"><h3>함께 쓰는 서비스</h3><label class="row" style="gap:10px;align-items:center"><input type="checkbox" id="sideTg" ${sideOn() ? 'checked' : ''}><span>상단에 민혁닷컴·Nestmate 바로가기 보이기</span></label><p class="muted small">PyNest만 쓰신다면 꺼 두셔도 됩니다. 같은 계정으로 로그인할 수 있는 별도 사이트입니다.</p></div>
      <div class="card" id="kkCard"><h3>💬 카카오톡 연동</h3><p class="muted small">PyNest 카카오톡 채널 챗봇에서 랭킹·내 프로필·티어를 볼 수 있어요.</p><div id="kkBody" class="muted small">불러오는 중…</div></div>
      </section>
      <section data-sp="prof" ${setTab === 'prof' ? '' : 'hidden'} id="spProf"></section>
      <section data-sp="avatar" ${setTab === 'avatar' ? '' : 'hidden'} id="spAvatar"></section>
      <section data-sp="dm" ${setTab === 'dm' ? '' : 'hidden'} id="spDm"></section>
      <section data-sp="notif" ${setTab === 'notif' ? '' : 'hidden'} id="spNotif"></section>
      <section data-sp="rec" ${setTab === 'rec' ? '' : 'hidden'}>
      <details class="card" id="recCard"><summary><h3 style="display:inline">📋 내 풀이·학습 기록</h3> <span class="muted small">— 누르면 그 문제·제출·레슨으로 이동해요</span></summary>
        <div id="recBody" class="muted small" style="margin-top:10px">불러오는 중…</div></details>
      </section>
      <section data-sp="ide" ${setTab === 'ide' ? '' : 'hidden'}>
      <div class="card" id="ideCard"><h3>⌨️ 코드 입력창 (IDE) 기능</h3>
        <p class="muted small">코드 쓰는 칸의 편의 기능을 골라서 켜고 꺼요. 이 기기(브라우저)에 저장되고, 문제집·라이브 모두 같이 적용돼요.</p>
        <div id="ideOpts"></div>
        <label>써보기<textarea id="ideTry" class="code" rows="6" placeholder="여기서 바로 시험해 보세요. 예) print( 를 치고 Enter, if x: 를 치고 Enter"></textarea></label>
      </div>
      </section>`,
    (v) => {
      $('#themeBtn2', v).onclick = toggleTheme;
      $('#sideTg', v).onchange = (e) => { try { localStorage.setItem('pn_side', e.target.checked ? '1' : '0'); } catch (x) {} renderShell(); toast(e.target.checked ? '바로가기를 켰습니다.' : '바로가기를 껐습니다.'); };
      bindMyRecords(v);
      const inited = {};
      const INIT = { hub: () => initHubTab($('#spHub', v)), streak: () => initStreakTab($('#spStreak', v)), badges: () => initBadgesTab($('#spBadges', v)), wallet: () => initWalletTab($('#spWallet', v)), prof: () => initProfTab($('#spProf', v)), avatar: () => initAvatarTab($('#spAvatar', v)), dm: () => initDmTab($('#spDm', v), dmUid), notif: () => initNotifTab($('#spNotif', v)), rec: () => { const rc = $('#recCard', v); if (rc && !rc.open) rc.open = true; } };
      const showTab = (k, push) => {
        setTab = k;
        v.querySelectorAll('[data-st]').forEach((b) => b.classList.toggle('on', b.dataset.st === k));
        v.querySelectorAll('[data-sp]').forEach((sec) => { sec.hidden = sec.dataset.sp !== k; });
        if (push) { try { history.replaceState(null, '', `#/me/${k}`); } catch (e) { /* 주소 표시는 없어도 돼요 */ } }
        if (INIT[k] && !inited[k]) { inited[k] = true; INIT[k](); }
      };
      v.querySelectorAll('[data-st]').forEach((b) => (b.onclick = () => { showTab(b.dataset.st, true); window.scrollTo(0, 0); }));
      v.addEventListener('pn-tab', (e) => { showTab(e.detail, true); window.scrollTo(0, 0); });
      showTab(setTab, false);
      pollNotif(true);
      if (window.PYIDE) {
        const IDE_OPTS = [
          ['close', '괄호·따옴표 자동 닫기', '( 를 치면 ) 가 같이 생기고, ) 를 치면 건너뛰어요. 지울 때는 한 쌍이 같이 지워져요'],
          ['split', '괄호 사이에서 Enter → 닫는 괄호를 아래 줄로', '끄면 괄호 안 내용만 내려오고 닫는 괄호는 그 줄 끝에 그대로 있어요  f(↵  →  f(\\n    )'],
          ['indent', '줄바꿈 자동 들여쓰기', '콜론(:) 뒤에는 4칸 더, return·pass·break 뒤에는 4칸 덜 들여써요'],
          ['tab', 'Tab / Shift+Tab 들여쓰기', '여러 줄을 선택하고 눌러도 돼요. 끄면 Tab 이 다음 칸으로 이동해요'],
          ['bksp', '스마트 Backspace', '앞쪽 공백은 4칸씩 지워요'],
          ['comment', 'Ctrl(⌘)+/ 주석 켜기/끄기', ''],
          ['guide', '들여쓰기 세로줄', '4칸마다 연한 줄을 보여줘요'],
          ['lines', '줄 번호', '코드 왼쪽에 줄 번호를 보여줘요'],
          ['curline', '현재 줄 강조', '커서가 있는 줄을 연하게 칠해요'],
          ['linecmd', '줄 편집 단축키', 'Ctrl(⌘)+D 줄 복제 · Alt+↑/↓ 줄 옮기기 · Ctrl(⌘)+Shift+K 줄 지우기 · Ctrl(⌘)+Enter 아래에 새 줄(Shift 는 위) · Home 은 글자 시작↔줄 맨앞'],
        ];
        const cur = window.PYIDE.get();
        $('#ideOpts', v).innerHTML = IDE_OPTS.map(([k, t, d]) => `<label class="inline ideopt"><input type="checkbox" data-ide="${k}" ${cur[k] !== false ? 'checked' : ''}> <span><b>${esc(t)}</b>${d ? `<br><span class="muted small">${esc(d)}</span>` : ''}</span></label>`).join('')
          + '<div class="form-actions"><button class="ghost" id="ideReset" type="button">기본값으로</button></div>';
        v.querySelectorAll('[data-ide]').forEach((c) => (c.onchange = () => window.PYIDE.set({ [c.dataset.ide]: c.checked })));
        $('#ideReset', v).onclick = () => {
          window.PYIDE.set(window.PYIDE.defaults);
          v.querySelectorAll('[data-ide]').forEach((c) => { c.checked = window.PYIDE.defaults[c.dataset.ide] !== false; });
          toast('기본값으로 돌렸어요');
        };
        window.PYIDE.attach($('#ideTry', v));
      } else { const ic = $('#ideCard', v); if (ic) ic.remove(); }
      const nickDraw = async () => {
        const { data: nr, error: ne } = await sb.from('nicknames').select('nickname,set_by').eq('user_id', me.id).maybeSingle();
        if (ne) { $('#nickNote', v).textContent = '아직 준비되지 않았어요. (관리자가 v350_nickname_signup.sql 을 실행하면 쓸 수 있어요)'; return; }
        const locked = !!nr && nr.set_by !== me.id; // 선생님이 정해준 별명은 못 바꿔요
        $('#nickIn', v).value = nr ? nr.nickname : '';
        $('#nickIn', v).disabled = locked;
        $('#nickBtn', v).disabled = locked;
        $('#nickNote', v).textContent = locked ? '🔒 선생님이 정해준 별명이라 바꿀 수 없어요.' : '랭킹·게시판 등에 보이는 이름이에요. 비우고 저장하면 별명이 없어져요.';
      };
      nickDraw();
      $('#nickForm', v).onsubmit = async (e) => {
        e.preventDefault();
        const nick = $('#nickIn', v).value.trim().replace(/\s+/g, ' ');
        if (nick && !NICK_RE.test(nick)) return toast(NICK_MSG.invalid, true);
        const { data: r, error: er } = await sb.rpc('nickname_set_self', { p_nick: nick });
        if (er) return toast('저장하지 못했어요: ' + er.message, true);
        if (r !== 'ok') return toast(NICK_MSG[r] || '저장하지 못했어요', true);
        await loadDir(); nickDraw();
        toast(nick ? '별명을 저장했어요' : '별명을 지웠어요');
      };
      const kk = $('#kkBody', v);
      const kkDraw = async () => {
        const { data, error } = await sb.rpc('kakao_status');
        if (error || !data) { kk.innerHTML = '아직 준비되지 않았어요. (관리자가 v340_kakao.sql 을 실행하면 쓸 수 있어요)'; return; }
        kk.className = '';
        kk.innerHTML = data.linked
          ? `<p>✅ 연동돼 있어요 <span class="muted small">(${fmt(data.linked_at)})</span></p><button class="ghost" id="kkOff">연동 해제</button>`
          : '<button class="primary" id="kkNew">연동 코드 받기</button><div id="kkCode"></div>';
        const off = $('#kkOff', kk);
        if (off) off.onclick = async () => { if (!confirm('카카오톡 연동을 해제할까요?')) return; const r = await sb.rpc('kakao_unlink'); if (r.error) return toast('해제하지 못했어요', true); toast('연동을 해제했어요'); kkDraw(); };
        const nw = $('#kkNew', kk);
        if (nw) nw.onclick = async () => {
          const r = await sb.rpc('kakao_issue_code');
          if (r.error || !r.data) return toast('코드를 만들지 못했어요', true);
          $('#kkCode', kk).innerHTML = `<p class="kk-code">${esc(r.data)}</p><p class="muted small">10분 안에 PyNest 카카오톡 채널 채팅창에 <b>연동 ${esc(r.data)}</b> 라고 보내주세요.</p>`;
        };
      };
      kkDraw();
      $('#pwForm', v).onsubmit = async (e) => {
        e.preventDefault();
        const a = $('#np1', v).value;
        if (a.length < 6) return toast('비밀번호는 6자 이상이어야 해요', true);
        if (a !== $('#np2', v).value) return toast('비밀번호 확인이 달라요', true);
        const { error } = await sb.auth.updateUser({ password: a });
        if (error) return toast('바꾸지 못했어요: ' + error.message, true);
        e.target.reset();
        toast('비밀번호를 바꿨어요');
      };
    }];
  }

  /* ---------- 랭킹 · 프로필 (V3.1.0) ---------- */
  let rankTab = 'week';
  const sqlHint = (what, file = 'v310_ranking.sql') => [`<div class="card pad center">${what}<br><span class="muted small">Supabase SQL Editor 에서 <b>${file}</b> 을 한 번 실행해주세요.</span></div>`];
  function periodText(p) {
    const d = new Date(Date.now() + 9 * 3600e3); // 한국 시간 (UTC getter 로 읽어요)
    if (p === 'month') return `${d.getUTCFullYear()}년 ${d.getUTCMonth() + 1}월`;
    const dow = (d.getUTCDay() + 6) % 7;
    const st = new Date(d.getTime() - dow * 864e5);
    const en = new Date(st.getTime() + 6 * 864e5);
    const f = (x) => `${x.getUTCMonth() + 1}/${x.getUTCDate()}`;
    return `${f(st)} (월) ~ ${f(en)} (일)`;
  }

  // 화면 위쪽에 내려오는 작은 안내 배너 (새 창 X). 바깥을 누르거나 ✕ / Esc 로 닫아요.
  function showTierInfo() {
    const old = document.getElementById('tierBanner');
    if (old) { old.remove(); return; }
    const rows = TIERS.map((t, i) => {
      const nx = TIERS[i + 1];
            return `<tr><td>${tierBadge(t.min, 24)}</td><td><b>${esc(t.n)}</b></td><td>${t.min.toLocaleString()}점~</td><td class="muted">${tierStepText(i, nx ? nx.min : 0, t.min)}</td></tr>`;
    }).join('');
    const dif = DIFF_LIST.map((d) => `${diffTag(d.name)} <b>${d.points}</b>`).join(' &nbsp; ');
    const el = document.createElement('div');
    el.id = 'tierBanner';
    el.className = 'tier-banner';
    el.setAttribute('role', 'dialog');
    el.innerHTML = `<button class="icon tb-x" type="button" aria-label="닫기">✕</button>
      <h3>🏅 티어 기준</h3>
      <p class="muted small">푼 문제의 점수를 모두 더한 <b>누적 점수</b>로 티어가 정해져요. 각 티어는 V → IV → III → II → I 다섯 단계예요 (I이 가장 높아요).</p>
      <div class="tb-scroll"><table class="tb-table"><thead><tr><th></th><th>티어</th><th>시작 점수</th><th>한 단계</th></tr></thead><tbody>${rows}</tbody></table></div>
      <h4>문제 점수</h4><p class="small">${dif}</p>
      <p class="muted small">같은 문제는 처음 맞춘 한 번만 점수를 받아요. 주간·월간 랭킹은 그 기간에 새로 받은 점수의 합이에요.</p>`;
    document.body.appendChild(el);
    const close = () => { el.remove(); document.removeEventListener('keydown', onKey); document.removeEventListener('mousedown', onDown, true); };
    const onKey = (e) => { if (e.key === 'Escape') close(); };
    const onDown = (e) => { if (!el.contains(e.target) && e.target.id !== 'rkInfo') close(); };
    $('.tb-x', el).onclick = close;
    window.addEventListener('hashchange', close, { once: true });
    document.addEventListener('keydown', onKey);
    setTimeout(() => document.addEventListener('mousedown', onDown, true), 0);
  }

  async function pageRanking() {
    const { data, error } = await sb.rpc('rank_board', { p_period: rankTab });
    if (error) return sqlHint('랭킹을 불러올 수 없어요.');
    const unit = rankTab === 'week' ? '이번 주' : '이번 달';
    const medal = ['🥇', '🥈', '🥉'];
    await loadExt(data.map((r) => r.user_id));
    const rows = data.map((r) => `
      <a class="row rk ${r.user_id === me.id ? 'me' : ''}" href="#/u/${r.user_id}">
        <div class="rk-no top${r.rnk <= 3 ? r.rnk : 0}">${r.rnk <= 3 ? medal[r.rnk - 1] : r.rnk}</div>
        <div class="row-main rk-who">${avatarHtml(r.user_id, 30)}${tierBadge(r.score, 28)}<b>${esc(r.name)}</b></div>
        <div class="rk-val"><b>${r.pts}</b><span class="muted small"> 점</span><div class="muted small">${r.solved}문제</div></div>
      </a>`).join('');
    const mine = data.find((r) => r.user_id === me.id);
    const note = staffRole() ? '' : mine
      ? `<p class="muted small">내 순위: <b>${mine.rnk}등</b> · ${unit} ${mine.pts}점 (${mine.solved}문제)${mine.pts === 0 ? ' — 문제를 풀면 점수가 올라요! 💪' : ''}</p>`
      : `<p class="muted small">${unit}에는 아직 푼 문제가 없어요. 지금 도전해봐요! 💪</p>`;
    return [`
      <div class="page-head"><h2>🏆 랭킹</h2><button class="info-btn" id="rkInfo" type="button" title="티어 기준 보기" aria-label="티어 기준 보기">i</button></div>
      <div class="tabs"><button data-rk="week" class="${rankTab === 'week' ? 'on' : ''}">주간</button><button data-rk="month" class="${rankTab === 'month' ? 'on' : ''}">월간</button></div>
      <p class="muted small">${unit} · ${periodText(rankTab)} — 이 기간에 새로 맞춘 문제의 점수 합 순이에요 (같은 문제는 한 번만 세요). 점수가 정해진 📚 학습 레슨을 끝내면 그 점수도 더해져요.</p>
      ${note}
      <div class="card list">${rows || '<p class="muted center pad">아직 랭킹에 오른 사람이 없어요.</p>'}</div>`,
    (v) => {
      v.querySelectorAll('[data-rk]').forEach((b) => (b.onclick = () => { rankTab = b.dataset.rk; route(); }));
      $('#rkInfo', v).onclick = showTierInfo;
    }];
  }

  async function pageProfile(uid) {
    if (!/^[0-9a-f-]{36}$/i.test(uid || '')) return notFound();
    const { data: p, error } = await sb.rpc('user_profile', { p_uid: uid });
    if (error) return sqlHint('프로필을 불러올 수 없어요.');
    if (!p) return notFound();
    if (p.staff) {
      return [`<div class="card pad center"><h2>${esc(p.name)}</h2><p><span class="badge">${p.staff === 'owner' ? '선생님' : ROLE_NAME[p.staff] || esc(p.staff)}</span></p></div>`];
    }
    const k = tierOf(p.score);
    const pct = k.hi == null ? 100 : Math.max(0, Math.min(100, Math.round(((p.score - k.lo) / (k.hi - k.lo)) * 100)));
    const next = k.hi == null ? '최고 단계예요! 👑' : `다음 <b>${esc(tierOf(k.hi).name)}</b> 까지 ${k.hi - p.score}점`;
    const rk = (x) => (x.rank ? `${x.rank}등` : '-');
    const recent = (p.recent || []).map((r) => `
      <div class="row"><div class="row-main">${r.live
        ? `${r.difficulty ? diffTag(r.difficulty, `${r.difficulty} 라이브`) : '<span class="dbadge">라이브</span>'} <span class="muted small">(#${r.id})</span> <span>${esc(r.set_title || '라이브')}</span>`
        : `${diffTag(r.difficulty, `${r.difficulty} ${r.no}`)} <span class="muted small">(#${r.id})</span>
        ${tierCan('problem') ? `<a href="#/set/${r.set_id}">${esc(shortOf({ short_name: r.set_short, title: r.set_title || '' }))}</a>` : `<span>${esc(shortOf({ short_name: r.set_short, title: r.set_title || '' }))}</span>`}`}</div>
        <div class="muted small">+${r.pts}점 · ${fmt(r.at)}</div></div>`).join('') || '<p class="muted center pad">아직 푼 문제가 없어요.</p>';
    await loadExt([uid]);
    const ex = EXT.get(uid) || {};
    const acc = /^#[0-9a-f]{6}$/i.test(ex.accent || '') ? ex.accent : '';
    const byd = (p.by_diff || []).map((d) => `${diffTag(d.difficulty)} <b>${d.n}</b>`).join(' &nbsp; ') || '<span class="muted small">-</span>';
    return [`
      <p><a href="#/ranking">← 랭킹</a></p>
      <div class="card prof" ${acc ? `style="border-top:5px solid ${acc}"` : ''}>
        <div class="prof-top">${tierBadge(p.score, 84)}${EXT_OK ? avatarHtml(uid, 84) : ''}
          <div><h2 style="margin:0">${esc(p.name)}</h2>${ex.title ? `<span class="chip" ${acc ? `style="background:${acc}22;color:${acc}"` : ''}>${esc(ex.title)}</span>` : ''}
            <div class="prof-tier">${esc(k.name)} <span class="muted small">· ${p.score}점</span></div>
            <div class="pbar" title="${p.score} / ${k.hi == null ? '∞' : k.hi}"><i style="width:${pct}%"></i></div>
            <div class="muted small">${next}</div></div></div>
        <div class="grid3 prof-stats">
          <div><div class="muted small">푼 문제</div><b>${p.solved}</b></div>
          <div><div class="muted small">이번 주</div><b>${p.week.pts}</b><span class="muted small">점 · ${p.week.solved}문제 · ${rk(p.week)}</span></div>
          <div><div class="muted small">이번 달</div><b>${p.month.pts}</b><span class="muted small">점 · ${p.month.solved}문제 · ${rk(p.month)}</span></div>
        </div>
        <div class="prof-diff">${byd}</div>
        ${ex.bio ? `<p class="prof-bio">${nlBr(ex.bio)}</p>` : ''}
        <div class="form-actions">${uid === me.id ? '<a class="ghost btnlike" href="#/settings/prof">✨ 프로필·캐릭터 꾸미기</a>' : '<a class="primary btnlike" href="#/settings/dm/' + uid + '">💬 메시지 보내기</a>'}</div>
      </div>
      <h3>최근 푼 문제</h3><div class="card list">${recent}</div>`];
  }

  /* ---------- 관리자 ---------- */
  async function pageAdmin() {
    const tabs = [];
    if (can('members')) tabs.push(['members', '👥 회원']);
    if (can('content')) tabs.push(['lectures', '🎬 강의']);
    if (can('content')) tabs.push(['diff', '🎯 난이도']);
    if (can('content')) tabs.push(['pre', '🧩 공용 함수']);
    if (can('content')) tabs.push(['edit', '✏️ 편집']);
    if (isAdmin()) tabs.push(['growth', '🏆 성장']);
    if (isAdmin()) tabs.push(['badges', '🎖️ 배지']);
    if (can('content')) tabs.push(['exam', '📝 시험']);
    if (isAdmin()) tabs.push(['items', '🎁 아이템']);
    if (isAdmin()) tabs.push(['market', '🛍️ 마켓·행사']);
    if (isAdmin()) tabs.push(['tier', '🏅 티어']);
    if (staffRole()) tabs.push(['nick', '🏷️ 별명']);
    if (staffRole() === 'owner') tabs.push(['social', '💬 DM·알림']);
    if (can('roles_basic')) tabs.push(['staff', '🎖️ 권한']);
    if (!tabs.length) return ['<div class="card pad center">선생님만 볼 수 있어요.</div>'];
    if (!tabs.some(([k]) => k === adminTab)) adminTab = tabs[0][0];
    const sub = { members: adminMembers, lectures: adminLectures, diff: adminDiff, pre: adminPre, edit: adminEdit, tier: adminTiers, growth: adminGrowth, badges: adminBadges, exam: adminExam, items: adminItems, market: adminMarket, nick: adminNick, social: adminSocial, staff: adminStaff }[adminTab];
    const [body, bind] = await sub();
    const r = staffRole();
    return [`
      <div class="page-head"><h2>🛠️ 관리자 <span class="chip">${esc(ROLE_NAME[r])}</span></h2></div>
      <div class="tabs">${tabs.map(([k, n]) => `<button data-atab="${k}" class="${adminTab === k ? 'on' : ''}">${n}</button>`).join('')}</div>
      <p class="muted small">${can('content') ? '문제집 만들기·문제 추가/수정은 <a href="#/sets">📄 문제</a> 메뉴에서' : ''}${can('content') && can('review') ? ', ' : ''}${can('review') ? '학생 풀이는 <a href="#/review">📥 제출함</a>에서' : ''}${can('content') || can('review') ? ' 봐요.' : `내 역할: ${esc(ROLE_DESC[r])}`}</p>
      ${body}`,
    (v) => {
      v.querySelectorAll('[data-atab]').forEach((b) => (b.onclick = () => { adminTab = b.dataset.atab; lecEdit = null; route(); }));
      if (bind) bind(v);
    }];
  }

  async function adminMembers() {
    const { data, error } = await sb.from('profiles').select('*').order('created_at', { ascending: false });
    if (error) throw error;
    const pending = data.filter((x) => x.status === 'pending');
    const approved = data.filter((x) => x.status === 'approved' && x.id !== me.id);
    const rejected = data.filter((x) => x.status === 'rejected');
    // 직원 역할 표시 (OWNER / ADMIN 만 목록을 볼 수 있어요)
    const staffBy = {};
    if (can('roles_basic')) { const { data: st } = await sb.rpc('staff_list'); (st || []).forEach((t) => { staffBy[t.uname] = t.urole; }); }
    const rankOf = (x) => (x.role === 'admin' ? 4 : { admin: 3, teacher: 2, mod: 1 }[staffBy[x.username]] || 0);
    const myRank = { owner: 4, admin: 3, teacher: 2, mod: 1 }[staffRole()] || 0;
    // 학생 등급 (student_tiers.sql 전이면 조용히 없음)
    const tierBy = {};
    let tierOk = false;
    if (can('members')) { const { data: tl, error: tle } = await sb.rpc('student_tier_list'); if (!tle) { tierOk = true; (tl || []).forEach((t) => { tierBy[t.uname] = t.tier; }); } }
    const tagOf = (x) => (x.role === 'admin' ? ' · OWNER' : staffBy[x.username] ? ` · ${ROLE_NAME[staffBy[x.username]]}` : tierBy[x.username] ? ` · ${TIER_NAME[tierBy[x.username]]}` : '');
    const tierBtns = (x) => (!tierOk || rankOf(x) > 0 ? '' : ['student', 'solver', 'listener'].filter((t) => (tierBy[x.username] || 'student') !== t).map((t) => `<button class="ghost" data-tier="${esc(x.username)}|${t}" title="${esc(TIER_DESC[t])}">${TIER_NAME[t]}</button>`).join(' ') + ' ');
    const line = (x, btns) => `<div class="row"><div class="row-main"><b>${esc(dname(x.id, x.username))}</b> <span class="muted small">${fmt(x.created_at)}${tagOf(x)}</span></div><div>${btns}</div></div>`;
    const block = (title, arr, btns) => `<h3>${title} (${arr.length})</h3><div class="card list">${arr.length ? arr.map((x) => line(x, btns(x))).join('') : '<p class="muted center pad">없어요.</p>'}</div>`;
    return [
      block('가입 신청 대기', pending, (x) => `<button class="primary" data-act="approve" data-id="${x.id}">승인</button> <button class="ghost" data-act="reject" data-id="${x.id}">거절</button>`)
      + (tierOk ? '<p class="muted small">학생 등급 — STUDENT 모든 기능 · SOLVER 문제만(강의·라이브 제외) · LISTENER 강의·라이브만(문제·라이브 문제 제외)</p>' : '')
      + block('승인된 학생', approved, (x) => (rankOf(x) >= myRank ? '<span class="muted small">상위/동급 계정</span>' : `${tierBtns(x)}${can('reset_pw') ? `<button class="ghost" data-act="reset" data-name="${esc(x.username)}">비밀번호 초기화</button> ` : ''}<button class="ghost" data-act="reject" data-id="${x.id}">사용 중지</button>`))
      + block('거절/중지', rejected, (x) => `<button class="ghost" data-act="approve" data-id="${x.id}">다시 승인</button>`),
      (v) => {
        v.querySelectorAll('[data-tier]').forEach((b) => (b.onclick = async () => {
          const [name, t] = b.dataset.tier.split('|');
          const { data: r, error: er } = await sb.rpc('student_set_tier', { p_username: name, p_tier: t });
          if (er) return toast('처리하지 못했어요: ' + er.message, true);
          const msg = { not_found: '가입된 ID가 아니에요', is_staff: '직원 계정에는 등급이 없어요', invalid: '등급이 올바르지 않아요' };
          if (r !== 'ok') return toast(msg[r] || '처리하지 못했어요', true);
          toast(`${name} → ${TIER_NAME[t]} (${TIER_DESC[t]})`);
          route(true);
        }));
        v.querySelectorAll('[data-act]').forEach((b) => (b.onclick = async () => {
          const act = b.dataset.act;
          if (act === 'reset') {
            const pw = prompt(`${b.dataset.name}의 새 비밀번호를 입력하세요 (6자 이상)`);
            if (!pw) return;
            if (pw.length < 6) return toast('6자 이상으로 입력하세요', true);
            const { error: e } = await sb.rpc('admin_reset_password', { target_username: b.dataset.name, new_password: pw });
            return e ? toast('초기화 실패: ' + e.message, true) : toast('비밀번호를 바꿨어요. 학생에게 알려주세요');
          }
          const status = act === 'approve' ? 'approved' : 'rejected';
          const { error: e } = await sb.from('profiles').update({ status }).eq('id', b.dataset.id);
          if (e) return toast('처리하지 못했어요', true);
          toast(act === 'approve' ? '승인했어요' : '처리했어요');
          route(true);
        }));
      }];
  }

  async function adminStaff() {
    const { data, error } = await sb.rpc('staff_list');
    if (error) return [`<div class="card pad center">권한 표가 아직 없어요.<br><span class="muted small">Supabase SQL Editor 에서 <b>staff_roles.sql</b> 을 한 번 실행해주세요.</span></div>`];
    const order = { owner: 0, admin: 1, teacher: 2, mod: 3 };
    const rows = [...data].sort((a, b) => (order[a.urole] ?? 9) - (order[b.urole] ?? 9) || a.uname.localeCompare(b.uname));
    const opts = [['teacher', 'TEACHER · 강의·문제집·문제·숙제·제출함'], ['mod', 'MOD · 관리만']];
    if (can('roles_admin')) opts.unshift(['admin', 'ADMIN · 모든 관리']);
    const line = (x) => {
      const fixed = x.urole === 'owner' || x.uname === me.username;
      const editable = !fixed && (x.urole !== 'admin' || can('roles_admin'));
      const sw = (r, label) => (x.urole !== r && (r !== 'admin' || can('roles_admin')) ? `<button class="ghost" data-srole="${esc(x.uname)}|${r}">${label}</button> ` : '');
      return `<div class="row"><div class="row-main"><span class="badge">${ROLE_NAME[x.urole] || esc(x.urole)}</span> <b>${esc(x.uname)}</b> <span class="muted small">${esc(ROLE_DESC[x.urole] || '')}${x.uname === me.username ? ' · 나' : ''}</span></div>
        <div>${editable ? `${sw('admin', 'ADMIN으로')}${sw('teacher', 'TEACHER로')}${sw('mod', 'MOD로')}<button class="ghost" data-srole="${esc(x.uname)}|none">해임</button>` : ''}</div></div>`;
    };
    return [`
      <div class="card">
        <h3>역할 부여</h3>
        <p class="muted small">민혁닷컴과 <b>같은 권한</b>이에요. 여기서 정하면 두 사이트에 모두 적용돼요. (가입된 ID만 가능)</p>
        <div class="muted small" style="margin-bottom:8px">OWNER 최상위 · ADMIN 모든 관리 · TEACHER 강의·문제집·문제·숙제 · MOD 회원·글·댓글 관리</div>
        <form id="sForm"><div class="grid2">
          <label>ID<input type="text" id="sName" maxlength="20" autocapitalize="none" placeholder="student01" required></label>
          <label>역할<select id="sRole">${opts.map(([v, l]) => `<option value="${v}">${l}</option>`).join('')}</select></label>
        </div><div class="form-actions"><button class="primary">역할 부여</button></div></form>
      </div>
      <h3>직원 (${rows.length})</h3><div class="card list">${rows.map(line).join('') || '<p class="muted center pad">없어요.</p>'}</div>`,
    (v) => {
      const setRole = async (name, role) => {
        if (role === 'none' && !confirm(`${name} 님의 직원 권한을 해임할까요?`)) return;
        const { data: r, error: er } = await sb.rpc('staff_set_role', { p_username: name, p_role: role });
        if (er) return toast('처리하지 못했어요: ' + er.message, true);
        const msg = { not_found: '가입된 ID가 아니에요', self: '자기 자신의 역할은 바꿀 수 없어요', is_owner: 'OWNER 는 바꿀 수 없어요', forbidden: 'ADMIN 임명·해임은 OWNER 만 할 수 있어요', invalid: '역할이 올바르지 않아요' };
        if (r !== 'ok') return toast(msg[r] || '처리하지 못했어요', true);
        toast(role === 'none' ? '해임했어요' : `${ROLE_NAME[role]} 로 지정했어요`);
        route(true);
      };
      $('#sForm', v).onsubmit = (e) => {
        e.preventDefault();
        const name = $('#sName', v).value.trim().toLowerCase();
        if (!ID_RE.test(name)) return toast('ID 형식이 이상해요', true);
        setRole(name, $('#sRole', v).value);
      };
      v.querySelectorAll('[data-srole]').forEach((b) => (b.onclick = () => { const [n, r] = b.dataset.srole.split('|'); setRole(n, r); }));
    }];
  }

  // 🏅 티어 — 이름 · 시작 점수 · 색 · 뱃지 문양을 직접 추가/수정/삭제 (OWNER / ADMIN)
  /* ---------- 공용 함수 (학생 코드 앞에 미리 불러오는 함수) ---------- */
  /* 문제집 편집 기능 켜고 끄기 (이 브라우저에 저장돼요) */
  async function adminEdit() {
    const OPTS = [
      ['drag', '↕️ 끌어서 순서 바꾸기', '문제·설명 글 카드 오른쪽 위 ⠿ 를 잡고 끌어요. 문제는 일반/ELITE 구역 안에서, 설명 글은 어디로든 옮길 수 있어요. 마우스·터치 둘 다 돼요.'],
      ['dbl', '🖱️ 더블클릭으로 바로 수정', '문제·설명 글의 본문을 더블클릭하면 그 자리에서 고쳐요. Ctrl+Enter 저장, Esc 취소. (✏️ 버튼은 그대로 써도 돼요)'],
    ];
    return [`<div class="card pad"><h3>✏️ 문제집 편집 기능</h3>
      <p class="muted small">문제집 화면에서 쓰는 편집 도우미를 켜고 꺼요. 이 브라우저에만 저장되고, 바꾸면 문제집 화면을 다시 열 때부터 적용돼요. 학생 화면에는 영향이 없어요.</p>
      ${OPTS.map(([k, t, d]) => `<label class="inline ideopt"><input type="checkbox" data-adm="${k}" ${admOpt(k) ? 'checked' : ''}> <span><b>${esc(t)}</b><br><span class="muted small">${esc(d)}</span></span></label>`).join('')}
    </div>`, (v) => {
      v.querySelectorAll('[data-adm]').forEach((c) => (c.onchange = () => { admSet(c.dataset.adm, c.checked); toast(c.checked ? '켰어요' : '껐어요'); }));
    }];
  }

  async function adminPre() {
    const { data, error } = await sb.from('prelude_funcs').select('*').order('position').order('id');
    if (error) return sqlHint('공용 함수 표가 아직 없어요.', 'v370_prelude.sql');
    PRE_ROWS = data;
    PRE_JSON = preScope(PRE_ROWS, ['all']);
    const card = (x) => `<div class="card prerow" ${x ? `data-pid="${x.id}"` : 'data-new="1"'}>
      <div class="pre-top">
        <select data-f="scope" title="어디에서 쓸 수 있는 함수인가요?">
          <option value="all" ${!x || x.scope === 'all' ? 'selected' : ''}>🌐 공용 (모든 문제 + 라이브)</option>
          <option value="live" ${x && x.scope === 'live' ? 'selected' : ''}>📡 라이브만</option>
        </select>
        <input type="text" data-f="name" maxlength="80" placeholder="메모(이름) — 예: 리스트 안을 모두 정수로 바꾸는 함수" value="${esc(x ? x.name : '')}">
        <label class="inline pre-on"><input type="checkbox" data-f="enabled" ${!x || x.enabled ? 'checked' : ''}> 사용</label>
      </div>
      <textarea class="code" data-f="code" spellcheck="false" placeholder="def to_ints(lst):&#10;    return [int(x) for x in lst]">${esc(x ? x.code : '')}</textarea>
      <div class="form-actions">
        <button class="primary" data-psave>저장</button>
        <button class="ghost" data-ptest title="이 함수를 불러와 보고 오류가 없는지 확인해요">▶ 오류 확인</button>
        <span class="muted small" data-pmsg></span>
        <span class="spacer"></span>
        <button class="ghost" data-pdel>삭제</button>
      </div></div>`;
    return [`
      <div class="card">
        <h3>🧩 공용 함수</h3>
        <p class="muted small" style="margin:0">여기에 함수를 미리 만들어 두면, 학생이 코드를 <b>실행·채점·제출</b>할 때 이 함수들이 <b>먼저 불러와져서</b> 학생은 함수 이름만 쓰면 돼요. (예: <code>to_ints(lst)</code>) 문제 본문에 "<code>to_ints()</code> 를 써서 풀어보세요"처럼 쓰는 건 직접 적어주세요. 왼쪽 위에서 <b>🌐 공용</b>(모든 문제와 라이브) 또는 <b>📡 라이브만</b>을 골라요. 함수 코드는 학생 브라우저에서 실행돼서 정답을 숨기는 용도는 아니에요.</p>
      </div>
      <div id="preList">${data.map(card).join('')}</div>
      <div class="form-actions"><button class="primary" id="preAdd">＋ 함수 추가</button></div>`,
    (v) => {
      const list = $('#preList', v);
      const bindRow = (row) => {
        const f = (k) => row.querySelector(`[data-f="${k}"]`);
        const msg = (t, bad) => { const m = row.querySelector('[data-pmsg]'); m.textContent = t; m.style.color = bad ? 'var(--danger, #dc2626)' : ''; };
        const ta = f('code');
        ta.addEventListener('keydown', (ev) => {
          if (ev.key === 'Tab') { ev.preventDefault(); const st = ta.selectionStart; ta.value = ta.value.slice(0, st) + '    ' + ta.value.slice(ta.selectionEnd); ta.selectionStart = ta.selectionEnd = st + 4; }
        });
        row.querySelector('[data-ptest]').onclick = async () => {
          const code = ta.value;
          if (!code.trim()) return msg('코드를 입력하세요', true);
          msg('⏳ 확인 중…');
          const r = await runOnce(code + '\n', '');
          if (r.status === 'OK') msg('✅ 오류 없이 불러와져요');
          else if (r.status === 'LOAD') msg('실행 도구를 불러오지 못했어요', true);
          else if (r.status === 'TLE') msg('시간이 너무 오래 걸려요 (무한 반복인지 확인)', true);
          else msg('❌ ' + (r.err || '오류'), true);
        };
        row.querySelector('[data-psave]').onclick = async () => {
          const body = { scope: f('scope').value, name: f('name').value.trim(), code: ta.value, enabled: f('enabled').checked };
          if (!body.code.trim()) return msg('코드를 입력하세요', true);
          const isNew = row.dataset.new === '1';
          let r;
          if (isNew) {
            const pos = [...list.children].indexOf(row);
            r = await sb.from('prelude_funcs').insert({ ...body, position: (pos + 1) * 10 }).select('id').single();
          } else r = await sb.from('prelude_funcs').update({ ...body, updated_at: new Date().toISOString() }).eq('id', Number(row.dataset.pid));
          if (r.error) return msg('저장하지 못했어요: ' + r.error.message, true);
          if (isNew && r.data) { row.dataset.pid = r.data.id; delete row.dataset.new; }
          await loadPre();
          msg('✅ 저장했어요');
          toast('저장했어요');
        };
        row.querySelector('[data-pdel]').onclick = async () => {
          if (row.dataset.new === '1') { row.remove(); return; }
          if (!confirm(`"${f('name').value || '이름 없는 함수'}" 함수를 삭제할까요?`)) return;
          const { error: de } = await sb.from('prelude_funcs').delete().eq('id', Number(row.dataset.pid));
          if (de) return toast('삭제하지 못했어요', true);
          row.remove();
          await loadPre();
          toast('삭제했어요');
        };
      };
      list.querySelectorAll('.prerow').forEach(bindRow);
      $('#preAdd', v).onclick = () => {
        const t = document.createElement('div');
        t.innerHTML = card(null);
        const row = t.firstElementChild;
        list.appendChild(row);
        bindRow(row);
        row.querySelector('[data-f="name"]').focus();
        row.scrollIntoView({ behavior: 'smooth', block: 'center' });
      };
    }];
  }

  async function adminTiers() {
    await loadTiers();
    if (!TIER_DB) return sqlHint('티어 표가 아직 없어요.', 'v320_tiers.sql');
    const glyphOpts = (sel) => Object.entries(GLYPH).map(([k, [nm]]) => `<option value="${k}" ${k === sel ? 'selected' : ''}>${nm}</option>`).join('');
    const rows = TIER_ROWS.map((t, i) => {
      const next = TIER_ROWS[i + 1];
            return `<div class="card tierrow" data-tid="${t.id}">
        <div class="tr-prev">${tierPreview(t.c1, t.c2, t.glyph, tierLevels(i) ? 'I' : '200', 44)}</div>
        <div class="tr-form">
          <div class="grid2">
            <label>이름<input type="text" maxlength="24" data-f="name" value="${esc(t.name)}"></label>
            <label>시작 점수<input type="number" min="0" max="10000000" data-f="min" value="${t.min_score}" ${t.min_score === 0 ? 'readonly title="가장 낮은 티어는 0점에서 시작해요"' : ''}></label>
          </div>
          <div class="tr-line">
            <label>색 <input type="color" data-f="c1" value="${esc(t.c1)}"> <input type="color" data-f="c2" value="${esc(t.c2)}"></label>
            <label>문양 <select data-f="glyph">${glyphOpts(t.glyph)}</select></label>
            <span class="muted small">${next ? `다음 티어(${esc(next.name)})까지 · ${tierStepText(i, next.min_score, t.min_score)}` : `가장 높은 티어 · ${tierStepText(i, 0, 0)}`}</span>
            <span class="spacer"></span>
            <button class="ghost" data-tsave="${t.id}">저장</button>
            ${t.min_score === 0 ? '' : `<button class="ghost" data-tdel="${t.id}">삭제</button>`}
          </div>
        </div></div>`;
    }).join('');
    return [`
      <div class="card">
        <h3>티어 추가</h3>
        <p class="muted small">누적 점수가 <b>시작 점수</b> 이상이면 그 티어예요. 각 티어는 V → IV → III → II → I 다섯 단계로 나뉘고(I 이 가장 높음), 다음 티어의 시작 점수까지를 5등분해요. 이름과 시작 점수는 겹치면 안 돼요. 저장하면 모든 학생의 티어가 바로 다시 계산돼요.</p>
        <form id="tForm">
          <div class="grid2">
            <label>이름<input type="text" id="tName" maxlength="24" placeholder="예: Titan" required></label>
            <label>시작 점수<input type="number" id="tMin" min="1" max="10000000" value="25000" required></label>
          </div>
          <div class="tr-line">
            <label>색 <input type="color" id="tC1" value="#7dd3fc"> <input type="color" id="tC2" value="#0369a1"></label>
            <label>문양 <select id="tG">${glyphOpts('star')}</select></label>
            <span class="tr-prev" id="tPrev"></span>
            <span class="spacer"></span>
            <button class="primary">추가</button>
          </div>
        </form>
      </div>
      <h3>티어 (${TIER_ROWS.length})</h3>
      <div class="tierlist">${rows}</div>`,
    (v) => {
      const done = async (msg) => { toast(msg); await loadTiers(); route(true); };
      const err = (e, fb) => toast(e.code === '23505' ? '같은 이름이거나 같은 시작 점수의 티어가 이미 있어요' : e.code === '42501' || /row-level/.test(e.message || '') ? '권한이 없어요' : /base tier/.test(e.message || '') ? '0점에서 시작하는 가장 낮은 티어는 바꾸거나 지울 수 없어요' : `${fb}: ${e.message}`, true);
      const prev = () => { $('#tPrev', v).innerHTML = tierPreview($('#tC1', v).value, $('#tC2', v).value, $('#tG', v).value, 'I', 40); };
      ['#tC1', '#tC2', '#tG'].forEach((k) => { $(k, v).oninput = prev; });
      prev();
      $('#tForm', v).onsubmit = async (e) => {
        e.preventDefault();
        const name = $('#tName', v).value.trim();
        const min = Number($('#tMin', v).value);
        if (!name || !Number.isInteger(min) || min < 1) return toast('이름과 시작 점수(1 이상의 정수)를 확인해주세요', true);
        const { error } = await sb.from('tiers').insert({ name, min_score: min, c1: $('#tC1', v).value, c2: $('#tC2', v).value, glyph: $('#tG', v).value });
        if (error) return err(error, '추가하지 못했어요');
        done(`${name} 티어를 추가했어요`);
      };
      v.querySelectorAll('.tierrow').forEach((row) => {
        const f = (k) => $(`[data-f="${k}"]`, row);
        const upd = () => { $('.tr-prev', row).innerHTML = tierPreview(f('c1').value, f('c2').value, f('glyph').value, 'I', 44); };
        ['c1', 'c2', 'glyph'].forEach((k) => { f(k).oninput = upd; });
        const sv = $('[data-tsave]', row);
        sv.onclick = async () => {
          const name = f('name').value.trim();
          const min = Number(f('min').value);
          if (!name || !Number.isInteger(min) || min < 0) return toast('이름과 시작 점수(0 이상의 정수)를 확인해주세요', true);
          const { data, error } = await sb.from('tiers').update({ name, min_score: min, c1: f('c1').value, c2: f('c2').value, glyph: f('glyph').value }).eq('id', row.dataset.tid).select('id');
          if (error) return err(error, '저장하지 못했어요');
          if (!data || !data.length) return toast('저장하지 못했어요', true);
          done('티어를 저장했어요');
        };
        const dl = $('[data-tdel]', row);
        if (dl) dl.onclick = async () => {
          if (!confirm(`${f('name').value} 티어를 삭제할까요?\n이 티어였던 학생은 한 단계 아래 티어로 바뀌어요.`)) return;
          const { error } = await sb.from('tiers').delete().eq('id', row.dataset.tid);
          if (error) return err(error, '삭제하지 못했어요');
          done('삭제했어요');
        };
      });
    }];
  }

  // 🏷️ 별명 — 학생 ID 대신 보일 이름 (직원 누구나). 직원에게는 항상 "별명 (ID)" 로 보여요.
  async function adminNick() {
    await loadDir();
    if (!DIR_OK) return sqlHint('별명 기능이 아직 켜지지 않았어요.');
    const arr = [...DIR.values()].sort((a, b) => (a.nick ? 0 : 1) - (b.nick ? 0 : 1) || String(a.uname || a.name).localeCompare(String(b.uname || b.name)));
    const rows = arr.map((d) => `<div class="row" data-q="${esc(`${d.nick || ''} ${d.uname || ''}`.toLowerCase())}">
      <div class="row-main">${tierBadge(d.score, 22)} ${d.nick ? `<b>${esc(d.nick)}</b> <span class="muted small">(${esc(d.uname)})</span>` : `<b>${esc(d.uname)}</b> <span class="muted small">별명 없음</span>`}</div>
      <div><button class="ghost" data-nick="${esc(d.uname)}|${esc(d.nick || '')}">${d.nick ? '변경' : '별명 정하기'}</button></div></div>`).join('');
    return [`
      <div class="card">
        <h3>별명 정하기</h3>
        <p class="muted small">학생들에게는 <b>별명</b>만 보이고(글·댓글·랭킹·프로필), 선생님들에게는 <b>별명 (ID)</b> 로 같이 보여요. 비워서 저장하면 별명이 지워지고 ID로 돌아가요. 다른 사람의 ID와 같은 별명은 쓸 수 없어요. (최대 20자)</p>
        <input type="search" id="nkQ" placeholder="별명 또는 ID 검색">
      </div>
      <h3>학생 (${arr.length})</h3><div class="card list" id="nkList">${rows || '<p class="muted center pad">승인된 학생이 없어요.</p>'}</div>`,
    (v) => {
      $('#nkQ', v).oninput = (e) => {
        const q = e.target.value.trim().toLowerCase();
        v.querySelectorAll('#nkList [data-q]').forEach((r) => { r.hidden = !!q && !r.dataset.q.includes(q); });
      };
      v.querySelectorAll('[data-nick]').forEach((b) => (b.onclick = async () => {
        const [uname, cur] = b.dataset.nick.split('|');
        const nick = prompt(`${uname} 의 별명 (비우면 삭제)`, cur);
        if (nick === null) return;
        const { data: r, error: er } = await sb.rpc('nickname_set', { p_username: uname, p_nick: nick });
        if (er) return toast('처리하지 못했어요: ' + er.message, true);
        const msg = { not_found: '가입된 ID가 아니에요', invalid: '별명은 20자까지예요', taken: '이미 쓰고 있는 별명(또는 다른 사람의 ID)이에요' };
        if (r !== 'ok') return toast(msg[r] || '처리하지 못했어요', true);
        toast(nick.trim() ? '별명을 저장했어요' : '별명을 지웠어요');
        route(true);
      }));
    }];
  }

  // 🎯 난이도 — 난이도별 랭킹 점수 + 직접 만드는 난이도
  async function adminDiff() {
    await loadDiffs();
    if (!RK_READY) return sqlHint('난이도 표가 아직 없어요.');
    const rows = DIFF_LIST.map((d) => `<div class="row"><div class="row-main">${diffTag(d.name)} <span class="muted small">${d.builtin ? '기본' : '직접 만듦'}</span></div>
      <div class="diffctl"><input type="number" min="0" max="100000" value="${d.points}" data-dp="${esc(d.name)}" aria-label="${esc(d.name)} 점수"> <span class="muted small">점</span>
        <button class="ghost" data-dsave="${esc(d.name)}">저장</button>${d.builtin ? '' : ` <button class="ghost" data-ddel="${esc(d.name)}">삭제</button>`}</div></div>`).join('');
    return [`
      <div class="card">
        <h3>난이도 추가</h3>
        <p class="muted small">문제의 난이도 선택 칸에 바로 나와요. 이름은 24자까지예요.</p>
        <form id="dForm"><div class="grid2">
          <label>이름<input type="text" id="dName" maxlength="24" placeholder="예: Expert" required></label>
          <label>점수<input type="number" id="dPts" min="0" max="100000" value="50" required></label>
        </div>
        <label>색 <input type="color" id="dColor" value="#0ea5e9"></label>
        <div class="form-actions"><button class="primary">추가</button></div></form>
      </div>
      <h3>난이도별 점수</h3>
      <p class="muted small">문제를 맞히면 이 점수가 쌓여서 티어가 올라가요. 문제를 만들 때 <b>🏆 랭킹 점수</b>를 직접 쓰면 그 문제만 그 점수예요. 점수를 바꾸면 모든 학생 점수가 바로 다시 계산돼요.</p>
      <div class="card list">${rows}</div>`,
    (v) => {
      const done = async (msg) => { toast(msg); await loadDiffs(); route(true); };
      $('#dForm', v).onsubmit = async (e) => {
        e.preventDefault();
        const name = $('#dName', v).value.trim();
        if (!name) return;
        if (DIFF_LIST.some((d) => d.name.toLowerCase() === name.toLowerCase())) return toast('이미 있는 난이도예요', true);
        const { error: er } = await sb.from('difficulties').insert({ name, points: Number($('#dPts', v).value), color: $('#dColor', v).value, position: 100 + DIFF_LIST.length });
        if (er) return toast('추가하지 못했어요: ' + er.message, true);
        done(`${name} 난이도를 추가했어요`);
      };
      v.querySelectorAll('[data-dsave]').forEach((b) => (b.onclick = async () => {
        const inp = v.querySelector(`[data-dp="${CSS.escape(b.dataset.dsave)}"]`);
        const pts = Number(inp.value);
        if (!Number.isFinite(pts) || pts < 0) return toast('점수를 확인해주세요', true);
        const { data: r, error: er } = await sb.from('difficulties').update({ points: pts }).eq('name', b.dataset.dsave).select('name');
        if (er || !r || !r.length) return toast('저장하지 못했어요', true);
        done('점수를 저장했어요');
      }));
      v.querySelectorAll('[data-ddel]').forEach((b) => (b.onclick = async () => {
        if (!confirm(`${b.dataset.ddel} 난이도를 삭제할까요?`)) return;
        const { error: er } = await sb.from('difficulties').delete().eq('name', b.dataset.ddel);
        if (er) return toast(er.code === '23503' ? '이 난이도를 쓰는 문제가 있어서 지울 수 없어요' : '삭제하지 못했어요', true);
        done('삭제했어요');
      }));
    }];
  }

  async function adminLectures() {
    const { data, error } = await sb.from('lectures').select('*').order('week', { ascending: false }).order('id', { ascending: false });
    if (error) throw error;
    const ed = lecEdit ? data.find((x) => x.id === lecEdit) : null;
    if (lecEdit && !ed) lecEdit = null;
    const rows = data.length ? data.map((x) => `<div class="row"><div class="row-main"><span class="week">${x.week}주차</span>${esc(x.title)}</div><div><button class="ghost" data-edit="${x.id}">수정</button> <button class="ghost" data-del="${x.id}">삭제</button></div></div>`).join('') : '<p class="muted center pad">아직 없어요.</p>';
    return [`
      <div class="card">
        <h3>${ed ? '강의 수정' : '강의 추가'}</h3>
        <form id="lForm">
          <div class="grid2">
            <label>주차<input type="number" id="lWeek" min="1" value="${ed ? ed.week : ''}" required></label>
            <label>제목<input type="text" id="lTitle" value="${esc(ed ? ed.title : '')}" required></label>
          </div>
          <label>YouTube 링크 (일부 공개 영상 주소)<input type="url" id="lUrl" placeholder="https://youtu.be/..." value="${esc(ed ? ed.youtube_url : '')}" required></label>
          <label>설명 (선택)<textarea id="lDesc" style="min-height:80px">${esc(ed ? ed.description || '' : '')}</textarea></label>
          <div class="form-actions"><button class="primary">${ed ? '수정 저장' : '추가'}</button>${ed ? '<button type="button" class="ghost" id="lCancel">취소</button>' : ''}</div>
        </form>
      </div>
      <h3>등록된 강의</h3><div class="card list">${rows}</div>`,
    (v) => {
      $('#lForm', v).onsubmit = async (e) => {
        e.preventDefault();
        const url = $('#lUrl', v).value.trim();
        if (!ytId(url)) return toast('YouTube 링크를 읽을 수 없어요', true);
        const row = {
          week: Number($('#lWeek', v).value), title: $('#lTitle', v).value.trim(),
          youtube_url: url, description: $('#lDesc', v).value.trim() || null,
        };
        if (ed) {
          const { data: r, error: er } = await sb.from('lectures').update(row).eq('id', ed.id).select('id');
          if (er || !r || !r.length) return toast('수정하지 못했어요', true);
          lecEdit = null;
          toast('강의를 수정했어요');
        } else {
          const { error: er } = await sb.from('lectures').insert(row);
          if (er) return toast('추가하지 못했어요', true);
          toast('강의를 추가했어요');
        }
        route();
      };
      const cc = $('#lCancel', v);
      if (cc) cc.onclick = () => { lecEdit = null; route(); };
      v.querySelectorAll('[data-edit]').forEach((b) => (b.onclick = () => { lecEdit = Number(b.dataset.edit); route(); }));
      v.querySelectorAll('[data-del]').forEach((b) => (b.onclick = async () => {
        if (!confirm('이 강의를 삭제할까요?')) return;
        const { error: er } = await sb.from('lectures').delete().eq('id', Number(b.dataset.del));
        if (er) return toast('삭제하지 못했어요', true);
        route(true);
      }));
    }];
  }

  /* ---------- 시작 ---------- */
  async function boot() {
    const { data: { session } } = await sb.auth.getSession();
    if (!session) {
      me = null;
      try { if (!sessionStorage.getItem('pn_app')) { location.replace('landing/'); return; } } catch (e) {} // 앱을 켰는데 로그인이 안 돼 있으면 소개 페이지로
      return renderAuth();
    }
    const { data, error } = await sb.from('profiles').select('*').eq('id', session.user.id).maybeSingle();
    if (error || !data) { await sb.auth.signOut(); return renderAuth(); }
    me = data;
    me.staff = null;
    if (me.status === 'approved' && me.role !== 'admin') { // 직원 역할 (staff_roles.sql 전이면 조용히 없음)
      try { const { data: r, error: re } = await sb.rpc('staff_role'); me.staff = re || !r ? null : String(r); } catch (e) { me.staff = null; }
    }
    me.tier = 'student';
    if (me.status === 'approved' && !me.staff && me.role !== 'admin') { // 학생 등급 (student_tiers.sql 전이면 조용히 student)
      try { const { data: t, error: te } = await sb.rpc('my_tier'); me.tier = te || !t ? 'student' : String(t); } catch (e) { me.tier = 'student'; }
    }
    if (me.status === 'pending') return renderStatus('pending');
    if (me.status === 'rejected') return renderStatus('rejected');
    await Promise.all([loadDir(), loadDiffs(), loadTiers(), loadPre()]); // SQL 을 아직 안 돌렸으면 조용히 기본값으로 동작해요
    ensureDefs();
    await Promise.all([loadExt([me.id]), loadItems(), loadEvents()]);
    renderShell();
    route();
    startNotif();
  }

  /* 하단 버전 표시 — 누르면 업데이트 시각, 5번 연속 누르면 패치 노트 (이스터에그) */
  (function verFoot() {
    const el = document.getElementById('verfoot');
    if (!el) return;
    const list = window.PYNEST_PATCHES || [];
    const cur = list[0] || { v: APP_VERSION, at: '' };
    el.innerHTML = `<button type="button" class="vf-btn" title="">PyNest V${esc(cur.v)}</button><span class="vf-at"></span>`;
    const btn = el.firstChild;
    const at = el.lastChild;
    let n = 0;
    let tm = 0;
    let hide = 0;
    btn.onclick = () => {
      n += 1;
      clearTimeout(tm);
      tm = setTimeout(() => { n = 0; }, 2500);
      at.textContent = cur.at ? ` · 업데이트 ${cur.at}` : '';
      clearTimeout(hide);
      hide = setTimeout(() => { at.textContent = ''; }, 4000);
      if (n >= 5) {
        n = 0;
        at.textContent = '';
        if (document.querySelector('.pn-modal')) return;
        const m = modal(`<h2>📜 패치 노트</h2><p class="muted small">V1.0.0 부터 지금까지 (한국 시간)</p>
          <div class="pn-list">${list.map((p) => `<section class="pn-ver"><h3>V${esc(p.v)} <span class="muted small">${esc(p.at)}</span></h3><p class="pn-t">${esc(p.t)}</p><ul>${p.items.map((i) => `<li>${esc(i)}</li>`).join('')}</ul></section>`).join('')}</div>`);
        m.el.classList.add('pn-modal'); // ✕ 버튼으로만 닫아요 (연타해도 안 닫혀요)
      }
    };
  })();

  sb.auth.onAuthStateChange((event) => {
    if (event === 'SIGNED_OUT' && !signingUp) { me = null; clearInterval(notifTimer); EXT.clear(); renderAuth(); }
  });
  // 새 버전이 올라왔는지 확인해서, 화면을 옮길 때 자동으로 새로고침 (시험 보는 중엔 건너뜀)
  let VCHK = Date.now();
  async function checkNewVersion() {
    if (Date.now() - VCHK < 90000) return;
    VCHK = Date.now();
    try {
      if (document.body.classList.contains('exam-on') || /^#\/exam\/\d+/.test(location.hash)) return;
      const r = await fetch('app.js', { cache: 'reload' });
      const m = /const APP_VERSION = '([^']+)'/.exec(await r.text());
      if (m && m[1] !== APP_VERSION) { flushDrafts(); location.reload(); }
    } catch (e) { /* 오프라인이면 그냥 둠 */ }
  }
  window.addEventListener('hashchange', () => { checkNewVersion(); route(); });

  // ⬇️ 당겨서 새로고침 (터치 화면): 맨 위에서 아래로 끌면 동그라미가 내려오며 진해지고, 충분히 끌었다 놓으면 새로고침
  (function pullToRefresh() {
    const TH = 70; // 이만큼(=끈 거리의 절반) 넘게 끌면 새로고침
    let el = null; let sy = 0; let sx = 0; let armed = false; let pull = 0; let busy = false;
    const mk = () => {
      if (el) return el;
      el = document.createElement('div');
      el.id = 'ptr';
      el.setAttribute('aria-hidden', 'true');
      el.innerHTML = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M20 12a8 8 0 1 1-2.6-5.9"/><path d="M20 4v5h-5"/></svg>';
      document.body.appendChild(el);
      return el;
    };
    const paint = (p, anim) => {
      const e = mk();
      e.style.transition = anim ? 'transform .2s, opacity .2s' : 'none';
      e.style.opacity = String(Math.min(1, p / TH));
      e.style.transform = `translate(-50%, ${p - 48}px)`;
      const s = e.firstChild; if (!e.classList.contains('spin')) s.style.transform = `rotate(${p * 4}deg)`;
      e.classList.toggle('ready', p >= TH);
    };
    const blocked = (t) => {
      if (document.body.classList.contains('exam-on') || /^#\/exam\/\d+/.test(location.hash) || document.querySelector('.modal-bg') || document.body.classList.contains('menu-open')) return true;
      for (let n = t; n && n !== document.body; n = n.parentElement) {
        const tag = n.tagName;
        if (tag === 'TEXTAREA' || tag === 'INPUT' || tag === 'SELECT' || tag === 'PRE' || tag === 'VIDEO' || tag === 'IFRAME') return true;
        if (n.scrollTop > 0) return true; // 안쪽에서 스크롤 중인 상자
      }
      return false;
    };
    document.addEventListener('touchstart', (e) => {
      armed = false; pull = 0;
      if (busy || e.touches.length !== 1 || (window.scrollY || document.documentElement.scrollTop) > 0 || blocked(e.target)) return;
      sy = e.touches[0].clientY; sx = e.touches[0].clientX; armed = true;
    }, { passive: true });
    document.addEventListener('touchmove', (e) => {
      if (!armed || busy) return;
      const dy = e.touches[0].clientY - sy; const dx = e.touches[0].clientX - sx;
      if (dy <= 0 || Math.abs(dx) > dy) { if (pull) { pull = 0; paint(0, true); } if (dy <= 0) armed = pull > 0; return; }
      if ((window.scrollY || document.documentElement.scrollTop) > 0) { armed = false; paint(0, true); return; }
      pull = Math.min(dy * 0.5, 110);
      if (e.cancelable) e.preventDefault();
      paint(pull, false);
    }, { passive: false });
    const end = () => {
      if (!armed) return; armed = false;
      if (pull >= TH && !busy) {
        busy = true;
        const e = mk(); e.classList.add('spin'); e.style.opacity = '1'; e.style.transition = 'transform .2s'; e.style.transform = 'translate(-50%, 24px)';
        try { flushDrafts(); } catch (er) { /* 임시 저장 실패해도 새로고침은 해요 */ }
        setTimeout(() => location.reload(), 350);
      } else if (pull > 0) { paint(0, true); }
      pull = 0;
    };
    document.addEventListener('touchend', end, { passive: true });
    document.addEventListener('touchcancel', end, { passive: true });
  })();
  document.addEventListener('visibilitychange', () => { const t = document.activeElement && document.activeElement.tagName; if (!document.hidden && t !== 'TEXTAREA' && t !== 'INPUT') checkNewVersion(); });
  boot();
})();
