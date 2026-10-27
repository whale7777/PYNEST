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
  const APP_VERSION = '3.8.0';
  // 누적 점수 → 티어. 각 티어는 V(낮음) ~ I(높음) 5단계로 똑같이 나눠요.
  // 티어 표는 DB(tiers)에 있고 [관리 → 🏅 티어]에서 고쳐요. DB 표가 없을 때만 아래 기본표를 써요. (v320_tiers.sql 의 시작값과 같아요)
  const DEFAULT_TIERS = [
    { n: 'Bronze', min: 0, c: ['#f0b27a', '#9c5a1e'], g: 'circle' },
    { n: 'Silver', min: 100, c: ['#f1f5f9', '#8795a8'], g: 'tri' },
    { n: 'Gold', min: 500, c: ['#ffe27a', '#d19a00'], g: 'sq' },
    { n: 'Platinum', min: 1500, c: ['#8ff0e0', '#16a394'], g: 'dia' },
    { n: 'Diamond', min: 3500, c: ['#9fd4ff', '#2563eb'], g: 'hex' },
    { n: 'Sapphire', min: 5000, c: ['#7aa2ff', '#1e3a8a'], g: 'drop' },
    { n: 'Emerald', min: 7000, c: ['#7df2a8', '#0e8a4f'], g: 'spark' },
    { n: 'Amethyst', min: 9500, c: ['#f0abfc', '#a21caf'], g: 'gem' },
    { n: 'Master', min: 12000, c: ['#d9a8ff', '#7c2ae0'], g: 'star' },
    { n: 'Grandmaster', min: 15000, c: ['#ffb36b', '#c2410c'], g: 'flame' },
    { n: 'Obsidian', min: 17500, c: ['#9ca3af', '#111827'], g: 'oct' },
    { n: 'The Programmer', min: 20000, c: ['#ff8aa8', '#e11d48'], g: 'crown' },
  ];
  let TIERS = DEFAULT_TIERS.slice();
  let TIER_ROWS = []; // DB 에서 읽은 티어 (id 포함)
  let TIER_DB = false; // tiers 표가 있나?
  const ROMAN = ['V', 'IV', 'III', 'II', 'I']; // I 이 가장 높아요
  function tierOf(score) {
    const sc = Math.max(0, Number(score) || 0);
    let i = TIERS.length - 1;
    while (i > 0 && sc < TIERS[i].min) i -= 1;
    const t = TIERS[i];
    const nextMin = i < TIERS.length - 1 ? TIERS[i + 1].min : null;
    const step = nextMin != null ? (nextMin - t.min) / 5 : 2000;
    const lv = Math.min(4, Math.floor((sc - t.min) / step));
    return { i, lv, roman: ROMAN[lv], name: `${t.n} ${ROMAN[lv]}`, lo: t.min + lv * step, hi: lv < 4 ? t.min + (lv + 1) * step : nextMin, score: sc };
  }
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
  }

  function renderStatus(kind) {
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
    ['home', '🏠', '홈'], ['lectures', '🎬', '강의'], ['sets', '📄', '문제'], ['ranking', '🏆', '랭킹'],
    ['board/notice', '📢', '공지'], ['board/qna', '❓', '질문'], ['board/assignment', '📝', '과제'],
    ['board/free', '💬', '자유'],
    ['golive/', '📡', '라이브 · 저지', 'ext'],
  ];

  function renderShell() {
    const items = NAV.filter(([k]) => (k === 'lectures' ? tierCan('lecture') : k === 'sets' ? tierCan('problem') : k === 'golive/' ? tierCan('live') : true));
    if (can('review')) items.push(['review', '📥', '제출함']);
    if (staffRole()) items.push(['admin', '🛠️', '관리자']);
    app.innerHTML = `
      <header class="top">
        <button class="icon" id="menuBtn" aria-label="메뉴" aria-expanded="false" title="메뉴">☰</button>
        <a class="brand" href="#/home">${esc(ICON)} ${esc(SITE)}</a>
        <div class="spacer"></div>
        <span class="who">${whoHtml()}</span>
        ${CONFIG.SHOP_URL ? `<a class="icon shop" href="${esc(CONFIG.SHOP_URL)}" target="_blank" rel="noopener" title="${esc(CONFIG.SHOP_NAME || '민혁닷컴')} 바로가기">🛒<span class="lbl"> ${esc(CONFIG.SHOP_NAME || '민혁닷컴')}</span></a>` : ''}
        <button class="icon" id="themeBtn" title="다크모드 켜기/끄기"></button>
        <a class="icon" href="#/settings" title="설정">⚙️</a>
        <button class="ghost" id="logoutBtn">로그아웃</button>
      </header>
      <nav class="menu" id="menu">
        ${items.map(([k, ic, name, soon]) => (soon === 'ext' ? `<a href="${k}" data-k="${k}">${ic} ${name}</a>` : `<a href="#/${k}" data-k="${k}" class="${soon ? 'soon' : ''}">${ic} ${name}</a>`)).join('')}
      </nav>
      <div class="menu-back" id="menuBack"></div>
      <main id="view"></main>`;
    const setMenu = (open) => { document.body.classList.toggle('menu-open', open); $('#menuBtn').setAttribute('aria-expanded', open ? 'true' : 'false'); };
    $('#menuBtn').onclick = () => setMenu(!document.body.classList.contains('menu-open'));
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
    const [a, b, c] = (location.hash.replace(/^#\//, '') || 'home').split('/');
    const key = a === 'u' ? 'ranking' : a === 'board' || a === 'write' ? `board/${b}` : a === 'lecture' ? 'lectures' : a === 'problems' ? 'board/problem' : a === 'set' ? 'sets' : a;
    document.body.classList.remove('menu-open');
    document.querySelectorAll('#menu a').forEach((l) => l.classList.toggle('on', l.dataset.k === key));

    const pages = {
      home: () => pageHome(),
      lectures: () => pageLectures(),
      lecture: () => pageLecture(b),
      problems: () => pageBoard('problem'),
      sets: () => pageSets(),
      ranking: () => pageRanking(),
      u: () => pageProfile(b),
      set: () => pageSet(b),
      review: () => pageReview(b, c),
      board: () => (BOARDS[b] ? pageBoard(b) : notFound()),
      post: () => pagePost(b),
      write: () => (BOARDS[b] ? pageWrite(b) : notFound()),
      edit: () => pageEdit(b),
      admin: () => pageAdmin(),
      settings: () => pageSettings(),
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
    const need = { lectures: ['lecture', '강의'], lecture: ['lecture', '강의'], sets: ['problem', '문제'], set: ['problem', '문제'], problems: ['problem', '문제'] }[a];
    if (need && !tierCan(need[0])) { v.innerHTML = lockedPage(need[1])[0]; return; }
    try {
      const [html, bind] = await (pages[a] || notFound)();
      if (tok !== navTok) return;
      v.innerHTML = html;
      if (bind) bind(v);
      window.scrollTo(0, keepScroll ? y : 0);
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

  async function pageHome() {
    const wantProb = tierCan('problem');
    const [n, l, p, st] = await Promise.all([
      sb.from('posts_view').select('id,title,created_at').eq('board', 'notice').order('created_at', { ascending: false }).limit(3),
      sb.from('lectures').select('*').order('week', { ascending: false }).limit(1),
      sb.from('problem_sets').select('id,title,week').order('id', { ascending: false }).limit(1),
      wantProb ? homeStats() : Promise.resolve(null),
    ]);
    const lec = l.data && l.data[0];
    const prob = p.data && p.data[0];
    const notices = (n.data || []).map((x) => `<a class="row" href="#/post/${x.id}"><div class="row-main">${esc(x.title)}</div><div class="muted small">${fmt(x.created_at)}</div></a>`).join('')
      || '<p class="muted center pad">아직 공지가 없어요.</p>';
    const isStaff = !!staffRole();
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
      <h2>안녕, ${esc(selfName())}! 👋</h2>
      ${probHtml}
      <div class="page-head"><h3>📢 최근 공지</h3><a href="#/board/notice">더 보기</a></div>
      <div class="card list">${notices}</div>
      <div class="grid2">
        ${tierCan('lecture') ? `<div class="card"><h3>🎬 최신 강의</h3>${lec ? `<p><span class="week">${lec.week}주차</span><a href="#/lecture/${lec.id}">${esc(lec.title)}</a></p>` : '<p class="muted">아직 없어요.</p>'}</div>` : ''}
        ${wantProb ? `<div class="card"><h3>📄 최신 문제집</h3>${prob ? `<p>${prob.week ? `<span class="week">${prob.week}주차</span>` : ''}<a href="#/set/${prob.id}">${esc(prob.title)}</a></p>` : '<p class="muted">아직 없어요.</p>'}</div>` : ''}
      </div>`, (v) => {
      v.querySelectorAll('a.hp').forEach((a) => a.addEventListener('click', () => { scrollToEx = 'ex-' + a.dataset.ex; }));
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
    let q = sb.from('posts_view')
      .select('id,title,created_at,author_name,author_id,anonymous,files,week')
      .eq('board', key);
    if (B.week) q = q.order('week', { ascending: false, nullsFirst: false });
    const { data, error } = await q.order('created_at', { ascending: false });
    if (error) throw error;
    const canWrite = !B.adminOnly || can(B.perm);
    const rows = data.length ? data.map((p) => `
      <a class="row" href="#/post/${p.id}">
        <div class="row-main">${p.week ? `<span class="week">${p.week}주차</span>` : ''}<b>${esc(p.title)}</b>${(p.files || []).length ? ` <span title="첨부파일 ${(p.files || []).length}개">📎${(p.files || []).length}</span>` : ''}</div>
        <div class="muted small meta">${who(p.author_id, p.author_name, false)}${p.anonymous && can('review') ? ' (익명 작성)' : ''} · ${fmt(p.created_at)}</div>
      </a>`).join('') : '<p class="muted center pad">아직 글이 없어요.</p>';
    return [`
      <div class="page-head"><h2>${B.icon} ${B.name}</h2>${canWrite ? `<a class="btn" href="#/write/${key}">글쓰기</a>` : ''}</div>
      ${B.desc ? `<p class="muted">${esc(B.desc)}</p>` : ''}
      <div class="card list">${rows}</div>`];
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
      <p><a href="#/board/${p.board}">← ${B.name}</a></p>
      <div class="card">
        <h2 class="post-title">${p.week ? `<span class="week">${p.week}주차</span>` : ''}${esc(p.title)}</h2>
        <p class="muted small">${who(p.author_id, p.author_name)}${p.anonymous && can('review') ? ' (익명 작성)' : ''} · ${fmt(p.created_at)}${p.updated_at ? ' (수정됨)' : ''}
          ${p.is_mine ? ` <a href="#/edit/${p.id}">수정</a>` : ''}
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
    return [`
      <p><a href="#/${editing ? 'post/' + post.id : 'board/' + key}">← ${editing ? '글로 돌아가기' : B.name}</a></p>
      <div class="card">
        <h2>${B.icon} ${B.name} ${editing ? '글 수정' : '글쓰기'}</h2>
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
    const add = (p, chapter, section, forceElite) => {
      const body = String(p.body ?? '').trim();
      if (!body) throw new Error(`${rows.length + 1}번째 문제의 body(문제 내용)가 비어 있어요`);
      const pts = p.points === '' || p.points == null ? null : Number(p.points);
      rows.push({
        chapter: chapter || null, section: section || null,
        difficulty: forceElite ? 'ELITE' : normDiff(p.difficulty),
        label: p.label || null, points: Number.isFinite(pts) ? pts : null,
        tags: Array.isArray(p.tags) ? p.tags.map(String) : [],
        source: p.source || null, body, check_point: p.check || p.check_point || null,
        tests: normTests(p.tests), answers: normAnswers(p.answers),
      });
    };
    (d.chapters || []).forEach((ch) => {
      const cname = [ch.title, ch.subtitle].filter(Boolean).join(' · ');
      (ch.sections || []).forEach((s) => (s.problems || []).forEach((p) => add(p, cname, s.title, false)));
    });
    (d.problems || []).forEach((p) => add(p, p.chapter, p.section, false));
    (d.elite || []).forEach((p) => add(p, null, null, true));
    if (!rows.length) throw new Error('문제가 하나도 없어요');
    rows.forEach((r, i) => { r.position = (i + 1) * 1000; });
    return {
      title: d.title || '', short: d.short_name || '', week: d.week || '', desc: d.description || '', rows,
      nElite: rows.filter((r) => r.difficulty === 'ELITE').length,
    };
  }

  function exportSet(set, list) {
    const L = layoutEx(list.map((e) => ({ ...e })));
    const prob = (e) => ({ difficulty: e.difficulty, label: e.label || '', points: e.points, tags: e.tags || [], source: e.source || '', body: e.body, check: e.check_point || '', tests: e.tests || [], answers: e.answers || [] });
    const out = {
      format: 'pynest-problemset-v1', title: set.title, short_name: set.short_name || '', week: set.week, description: set.description || '',
      chapters: L.chapters.map((ch) => {
        const [title, subtitle] = splitChapter(ch.name);
        return { title, subtitle, sections: ch.sections.map((sc) => ({ title: sc.name, problems: sc.items.map(prob) })) };
      }),
      elite: L.elite.map(prob),
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

  async function pageSets() {
    const num = setsView === 'num';
    const [sr, ex, mine] = await Promise.all([
      sb.from('problem_sets').select('*').order('week', { ascending: true, nullsFirst: false }).order('id'),
      fetchAll((a, b) => sb.from('exercises').select(num ? 'id,set_id,difficulty,body' : 'id,set_id').order('id').range(a, b)),
      can('content') ? Promise.resolve([]) : fetchAll((a, b) => sb.from('submissions').select('id,exercise_id,set_id').eq('user_id', me.id).order('id').range(a, b)),
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
        <div class="muted small">문제 ${t}개${can('content') ? '' : ` · 내가 푼 문제 ${d}개`}</div>
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
      <div class="page-head"><h2>📄 문제</h2>${can('content') ? '<button class="primary" id="newSet">＋ 새 문제집</button>' : ''}</div>
      <div class="tabs"><button data-sv="sets" class="${num ? '' : 'on'}">📚 문제집으로 보기</button><button data-sv="num" class="${num ? 'on' : ''}">🔢 번호로 보기</button></div>
      <p class="muted">${num ? `모든 문제를 <b>고유 번호</b> 순서로 보여줘요 (총 ${ex.length}문제). 눌러서 문제집 안의 그 문제로 이동해요.` : '문제를 하나씩 보고, <b class="redtxt">풀어보기</b>로 코드를 제출해요. 제출한 풀이는 선생님만 볼 수 있어요.'}</p>
      ${view}
      <p class="muted small"><a href="#/board/problem">📁 예전에 올린 문제 파일 보기</a></p>`,
    (v) => {
      const nb = $('#newSet', v);
      if (nb) nb.onclick = openNewSet;
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
        q('#nsInfo').textContent = `✅ 일반 ${parsed.rows.length - parsed.nElite}문제 + ELITE ${parsed.nElite}문제를 읽었어요.`;
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
      m.close();
      toast(pr && setRow.is_public === false ? '비공개로 만들었어요. 확인한 뒤 [🌐 공개하기]를 눌러주세요' : '문제집을 만들었어요');
      location.hash = '#/set/' + s.id;
    };
  }

  /* ---------- 문제집 화면 ---------- */
  async function pageSet(rawId) {
    const id = Number(rawId);
    const admin = can('content');
    const [sr, exs, subs, hwr] = await Promise.all([
      sb.from('problem_sets').select('*').eq('id', id).maybeSingle(),
      fetchAll((a, b) => sb.from('exercises').select('*').eq('set_id', id).order('position').order('id').range(a, b)),
      admin ? Promise.resolve([]) : fetchAll((a, b) => sb.from('submissions')
        .select('*,submission_comments(id,content,created_at)')
        .eq('set_id', id).eq('user_id', me.id).order('id').range(a, b)),
      sb.from('homeworks').select('*,homework_items(exercise_id)').eq('set_id', id).order('id'),
    ]);
    if (sr.error) throw sr.error;
    const set = sr.data;
    if (!set) return notFound();
    if (exs.length) { testsColumn = 'tests' in exs[0]; answersColumn = 'answers' in exs[0]; }
    if (set && 'is_public' in set) PUB_READY = true;
    const L = layoutEx(exs);
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

    /* 문제 카드 */
    const card = (e) => {
      const vers = subsBy[e.id] || [];
      const last = vers[vers.length - 1];
      const hasC = vers.some((s) => (s.submission_comments || []).length);
      const tags = (e.tags || []).map((t) => `<span class="chip">${esc(t)}</span>`).join('');
      return `<article class="ex ${e.difficulty === 'ELITE' ? 'elite' : dxCls(e.difficulty)}"${dxStyle(e.difficulty)} id="ex-${e.id}" data-hws="${(hwOf[e.id] || []).map((h) => h.id).join(',')}">
        <header class="ex-head">
          <span class="ex-no">${dispNo(e)}</span>
          ${diffTag(e.difficulty)}
          ${admin ? pubChip(e.is_public) : ''}
          ${e.label ? `<span class="chip">${esc(e.label)}</span>` : ''}
          ${e.points ? `<span class="chip pts">${e.points}점</span>` : ''}
          ${(e.tests || []).length || (e.answers || []).some((x) => x.type !== 'm') ? '<span class="chip judgechip" title="제출하면 자동으로 채점돼요">⚖️ 자동 채점</span>' : (e.answers || []).length ? '<span class="chip judgechip" title="선생님이 확인해요">✍️ 서술</span>' : ''}
          ${tags}
          ${(hwOf[e.id] || []).map((h) => `<span class="chip hwchip">📌 ${esc(h.title)}</span>`).join('')}
          ${e.source ? `<span class="muted small">${esc(e.source)}</span>` : ''}
          <span class="spacer"></span>
          ${admin ? `<span class="tools">
            <button class="icon" data-up="${e.id}" title="위로">↑</button><button class="icon" data-down="${e.id}" title="아래로">↓</button>
            <button class="icon" data-edit="${e.id}" title="수정">✏️</button><button class="icon" data-add="${e.id}" title="이 문제 아래에 추가">＋</button>
            <button class="icon" data-del="${e.id}" title="삭제">🗑</button></span>` : ''}
        </header>
        <div class="ex-body">${renderMarkup(e.body)}</div>
        ${e.check_point ? `<div class="ex-check">💡 <b>확인 포인트</b> ${inline(e.check_point)}</div>` : ''}
        ${admin ? `<div class="muted small">고유 번호 ${e.id}${(e.tests || []).length ? ` · 테스트 ${e.tests.length}개` : ''}${(e.answers || []).length ? ` · 정답 칸 ${e.answers.length}개` : ''}</div>
        ${(e.answers || []).length ? `<details class="keybox"><summary>🔑 정답 보기</summary><pre><code>${esc(answersToText(e.answers))}</code></pre></details>` : ''}` : `
        <div class="ex-foot">
          <button class="solve" data-solve="${e.id}">✍️ 풀어보기</button>
          ${last ? `<span class="done">✅ 제출함 · v${last.version}</span> ${judgeBadge(last.judge)}${hasC ? ' <span class="badge">💬 선생님 댓글</span>' : ''}` : ''}
        </div>
        <div class="ex-panel" id="panel-${e.id}" hidden></div>`}
      </article>`;
    };

    const normalHtml = L.chapters.map((ch) => {
      const [t, sub] = splitChapter(ch.name);
      return `<h2 class="ch-h" id="ch-${ch.idx}"><span class="ch-no">CHAPTER ${ch.idx + 1}</span>${esc(t)}${sub ? `<small>${esc(sub)}</small>` : ''}</h2>`
        + ch.sections.map((sc) => `${sc.name ? `<h3 class="sec-h" id="sec-${ch.idx}-${sc.idx}">${esc(sc.name)}</h3>` : ''}${sc.items.map(card).join('')}`).join('');
    }).join('');

    const eliteHtml = (L.elite.length || admin) ? `
      <section class="elite-zone" id="elite">
        <div class="elite-title">✦ ELITE ✦</div>
        <p class="elite-sub">가장 어려운 문제들이에요. 코드를 읽고, 추론하고, 설명해 보세요.</p>
        ${L.elite.map(card).join('')}
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
        ${admin ? '<button class="ghost" id="addEx">＋ 문제 추가</button><button class="ghost" id="setCfg">⚙️ 문제집 설정</button><button class="ghost" id="expSet">⬇️ JSON 내보내기</button><button class="ghost" id="autoTests" title="입출력 예시가 있는 문제에 채점 테스트를 한꺼번에 만들어요">⚖️ 예시로 채점 만들기</button><button class="ghost" id="impKey" title="JSON 파일의 정답·채점 테스트를 같은 문제에 덮어써요 (학생 제출물은 그대로)">🔑 정답·채점 가져오기</button><input type="file" id="impKeyFile" accept=".json,application/json" hidden><a class="ghost btnlike" href="#/review">📥 제출함</a>' : ''}
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

      /* 풀어보기 */
      const exMap = {};
      exs.forEach((x) => { exMap[x.id] = x; });
      const reveal = !!set.answer_public;
      const mount = (eid) => {
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
            <textarea class="pans code" data-i="${i}" rows="${lines}" spellcheck="false" placeholder="${esc(hint)}">${esc(lastU.vals[i] || '')}</textarea></label>`;
        }).join('');
        const nAuto = tests.length + answers.filter((a) => a.type !== 'm').length;
        p.innerHTML = `
          ${showCode ? `<textarea class="code" rows="10" spellcheck="false" placeholder="여기에 완성한 코드(또는 답)를 쓰세요. 서술형 답도 여기에 써요.">${esc(lastU.code)}</textarea>` : ''}
          ${canRun ? `<details class="stdin-box"><summary>⌨️ 입력값 <span class="muted small">(실행해보기에서 input()에 들어갈 값 · 한 줄에 하나씩)</span></summary>
            <textarea class="stdin" rows="3" spellcheck="false">${esc(sample ? sample.input : '')}</textarea></details>` : ''}
          ${answers.length ? `<div class="parts">${showCode ? '<div class="muted small">아래 칸에도 답을 써 주세요</div>' : ''}${partsInputs}</div>` : ''}
          <div class="form-actions">
            ${canRun ? '<button class="ghost" data-run>▶ 실행해보기</button>' : ''}
            ${canGrade ? `<button class="ghost" data-grade>✅ 채점하기 <span class="muted small">(${nAuto}개 항목)</span></button>` : ''}
            <button class="solve" data-send>제출하기${last ? ` (v${last.version + 1})` : ''}</button>
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
        if (ta) tabKey(ta);
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

  /* ---------- 문제집 : 선생님 도구 (추가/수정/삭제/순서/설정) ---------- */
  function bindSetAdmin(v, set, exs, hws, L) {
    const byId = (i) => exs.find((e) => e.id === Number(i));
    const lastNormal = exs.filter((e) => e.difficulty !== 'ELITE').pop();
    const maxPos = exs.reduce((m, e) => Math.max(m, e.position), 0);

    $('#addEx', v).onclick = () => openExEditor(set, exs, null, {
      position: maxPos + 1000, difficulty: 'Beginner',
      chapter: lastNormal ? lastNormal.chapter : '', section: lastNormal ? lastNormal.section : '',
    });
    const ae = $('#addElite', v);
    if (ae) ae.onclick = () => openExEditor(set, exs, null, { position: maxPos + 1000, difficulty: 'ELITE', chapter: '', section: '' });
    $('#setCfg', v).onclick = () => openSetCfg(set);
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
    $('#expSet', v).onclick = () => exportSet(set, exs);
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
      const peers = exs.filter((x) => (x.difficulty === 'ELITE') === (e.difficulty === 'ELITE'));
      const nx = peers[peers.findIndex((x) => x.id === e.id) + 1];
      openExEditor(set, exs, null, {
        position: nx ? (e.position + nx.position) / 2 : e.position + 1000,
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

  /* ---------- 설정 ---------- */
  async function pageSettings() {
    return [`
      <h2>⚙️ 설정</h2>
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
      <div class="card" id="kkCard"><h3>💬 카카오톡 연동</h3><p class="muted small">PyNest 카카오톡 채널 챗봇에서 랭킹·내 프로필·티어를 볼 수 있어요.</p><div id="kkBody" class="muted small">불러오는 중…</div></div>
      <p class="muted small center">PyNest V${APP_VERSION}</p>`,
    (v) => {
      $('#themeBtn2', v).onclick = toggleTheme;
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
      const step = nx ? Math.round(((nx.min - t.min) / 5) * 10) / 10 : 2000;
      return `<tr><td>${tierBadge(t.min, 24)}</td><td><b>${esc(t.n)}</b></td><td>${t.min.toLocaleString()}점~</td><td class="muted">${step}점씩</td></tr>`;
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
    const rows = data.map((r) => `
      <a class="row rk ${r.user_id === me.id ? 'me' : ''}" href="#/u/${r.user_id}">
        <div class="rk-no top${r.rnk <= 3 ? r.rnk : 0}">${r.rnk <= 3 ? medal[r.rnk - 1] : r.rnk}</div>
        <div class="row-main rk-who">${tierBadge(r.score, 28)}<b>${esc(r.name)}</b></div>
        <div class="rk-val"><b>${r.pts}</b><span class="muted small"> 점</span><div class="muted small">${r.solved}문제</div></div>
      </a>`).join('');
    const mine = data.find((r) => r.user_id === me.id);
    const note = staffRole() ? '' : mine
      ? `<p class="muted small">내 순위: <b>${mine.rnk}등</b> · ${unit} ${mine.pts}점 (${mine.solved}문제)</p>`
      : `<p class="muted small">${unit}에는 아직 푼 문제가 없어요. 지금 도전해봐요! 💪</p>`;
    return [`
      <div class="page-head"><h2>🏆 랭킹</h2><button class="info-btn" id="rkInfo" type="button" title="티어 기준 보기" aria-label="티어 기준 보기">i</button></div>
      <div class="tabs"><button data-rk="week" class="${rankTab === 'week' ? 'on' : ''}">주간</button><button data-rk="month" class="${rankTab === 'month' ? 'on' : ''}">월간</button></div>
      <p class="muted small">${unit} · ${periodText(rankTab)} — 이 기간에 새로 맞춘 문제의 점수 합 순이에요 (같은 문제는 한 번만 세요).</p>
      ${note}
      <div class="card list">${rows || '<p class="muted center pad">아직 아무도 문제를 풀지 않았어요.</p>'}</div>`,
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
    const byd = (p.by_diff || []).map((d) => `${diffTag(d.difficulty)} <b>${d.n}</b>`).join(' &nbsp; ') || '<span class="muted small">-</span>';
    return [`
      <p><a href="#/ranking">← 랭킹</a></p>
      <div class="card prof">
        <div class="prof-top">${tierBadge(p.score, 84)}
          <div><h2 style="margin:0">${esc(p.name)}</h2>
            <div class="prof-tier">${esc(k.name)} <span class="muted small">· ${p.score}점</span></div>
            <div class="pbar" title="${p.score} / ${k.hi == null ? '∞' : k.hi}"><i style="width:${pct}%"></i></div>
            <div class="muted small">${next}</div></div></div>
        <div class="grid3 prof-stats">
          <div><div class="muted small">푼 문제</div><b>${p.solved}</b></div>
          <div><div class="muted small">이번 주</div><b>${p.week.pts}</b><span class="muted small">점 · ${p.week.solved}문제 · ${rk(p.week)}</span></div>
          <div><div class="muted small">이번 달</div><b>${p.month.pts}</b><span class="muted small">점 · ${p.month.solved}문제 · ${rk(p.month)}</span></div>
        </div>
        <div class="prof-diff">${byd}</div>
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
    if (isAdmin()) tabs.push(['tier', '🏅 티어']);
    if (staffRole()) tabs.push(['nick', '🏷️ 별명']);
    if (can('roles_basic')) tabs.push(['staff', '🎖️ 권한']);
    if (!tabs.length) return ['<div class="card pad center">선생님만 볼 수 있어요.</div>'];
    if (!tabs.some(([k]) => k === adminTab)) adminTab = tabs[0][0];
    const sub = { members: adminMembers, lectures: adminLectures, diff: adminDiff, pre: adminPre, tier: adminTiers, nick: adminNick, staff: adminStaff }[adminTab];
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
      const step = next ? Math.round(((next.min_score - t.min_score) / 5) * 10) / 10 : null;
      return `<div class="card tierrow" data-tid="${t.id}">
        <div class="tr-prev">${tierPreview(t.c1, t.c2, t.glyph, 'I', 44)}</div>
        <div class="tr-form">
          <div class="grid2">
            <label>이름<input type="text" maxlength="24" data-f="name" value="${esc(t.name)}"></label>
            <label>시작 점수<input type="number" min="0" max="10000000" data-f="min" value="${t.min_score}" ${t.min_score === 0 ? 'readonly title="가장 낮은 티어는 0점에서 시작해요"' : ''}></label>
          </div>
          <div class="tr-line">
            <label>색 <input type="color" data-f="c1" value="${esc(t.c1)}"> <input type="color" data-f="c2" value="${esc(t.c2)}"></label>
            <label>문양 <select data-f="glyph">${glyphOpts(t.glyph)}</select></label>
            <span class="muted small">${step == null ? '가장 높은 티어 · 한 단계 2000점' : `다음 티어(${esc(next.name)})까지 · 한 단계 ${step}점`}</span>
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
    if (!session) { me = null; return renderAuth(); }
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
    renderShell();
    route();
  }

  sb.auth.onAuthStateChange((event) => {
    if (event === 'SIGNED_OUT' && !signingUp) { me = null; renderAuth(); }
  });
  window.addEventListener('hashchange', () => route());
  boot();
})();
