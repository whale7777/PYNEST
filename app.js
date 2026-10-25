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

  const isAdmin = () => me && me.role === 'admin';

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
  function renderContent(text) {
    return String(text ?? '').split('```').map((part, i) => {
      if (i % 2 === 1) {
        const code = part.replace(/^(python|py|text|c|cpp|java|js)\r?\n/i, '').replace(/^\r?\n/, '');
        return `<pre><code>${esc(code)}</code></pre>`;
      }
      return part.trim() ? `<div class="txt">${esc(part)}</div>` : '';
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

  async function doSignup() {
    const id = $('#aid').value.trim().toLowerCase();
    const pw = $('#apw').value;
    if (!ID_RE.test(id)) return toast('ID는 영문 소문자, 숫자, _ 로 3~20자예요', true);
    if (pw.length < 6) return toast('비밀번호는 6자 이상이어야 해요', true);
    if (pw !== $('#apw2').value) return toast('비밀번호 확인이 달라요', true);
    const btn = $('#authBtn');
    btn.disabled = true;
    signingUp = true;
    const { error } = await sb.auth.signUp({ email: emailOf(id), password: pw, options: { data: { username: id } } });
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
    ['home', '🏠', '홈'], ['lectures', '🎬', '강의'], ['sets', '📄', '문제'],
    ['board/notice', '📢', '공지'], ['board/qna', '❓', '질문'], ['board/assignment', '📝', '과제'],
    ['board/free', '💬', '자유'],
    ['judge', '⚖️', '온라인 저지', true], ['live', '📡', '라이브', true],
  ];

  function renderShell() {
    const items = NAV.slice();
    if (isAdmin()) items.push(['review', '📥', '제출함'], ['admin', '🛠️', '관리자']);
    app.innerHTML = `
      <header class="top">
        <a class="brand" href="#/home">${esc(ICON)} ${esc(SITE)}</a>
        <div class="spacer"></div>
        <span class="who">${esc(me.username)}${isAdmin() ? ' (선생님)' : ''}</span>
        <button class="icon" id="themeBtn" title="다크모드 켜기/끄기"></button>
        <a class="icon" href="#/settings" title="설정">⚙️</a>
        <button class="ghost" id="logoutBtn">로그아웃</button>
      </header>
      <nav class="menu" id="menu">
        ${items.map(([k, ic, name, soon]) => `<a href="#/${k}" data-k="${k}" class="${soon ? 'soon' : ''}">${ic} ${name}</a>`).join('')}
      </nav>
      <main id="view"></main>`;
    setTheme(document.documentElement.dataset.theme || 'light');
    $('#themeBtn').onclick = toggleTheme;
    $('#logoutBtn').onclick = logout;
  }

  /* ---------- 라우터 ---------- */
  async function route(keepScroll = false) {
    if (!me || me.status !== 'approved' || !$('#view')) return;
    const y = window.scrollY;
    const [a, b, c] = (location.hash.replace(/^#\//, '') || 'home').split('/');
    const key = a === 'board' || a === 'write' ? `board/${b}` : a === 'lecture' ? 'lectures' : a === 'problems' ? 'board/problem' : a === 'set' ? 'sets' : a;
    document.querySelectorAll('#menu a').forEach((l) => l.classList.toggle('on', l.dataset.k === key));

    const pages = {
      home: () => pageHome(),
      lectures: () => pageLectures(),
      lecture: () => pageLecture(b),
      problems: () => pageBoard('problem'),
      sets: () => pageSets(),
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
  async function pageHome() {
    const [n, l, p] = await Promise.all([
      sb.from('posts_view').select('id,title,created_at').eq('board', 'notice').order('created_at', { ascending: false }).limit(3),
      sb.from('lectures').select('*').order('week', { ascending: false }).limit(1),
      sb.from('problem_sets').select('id,title,week').order('id', { ascending: false }).limit(1),
    ]);
    const lec = l.data && l.data[0];
    const prob = p.data && p.data[0];
    const notices = (n.data || []).map((x) => `<a class="row" href="#/post/${x.id}"><div class="row-main">${esc(x.title)}</div><div class="muted small">${fmt(x.created_at)}</div></a>`).join('')
      || '<p class="muted center pad">아직 공지가 없어요.</p>';
    return [`
      <h2>안녕, ${esc(me.username)}! 👋</h2>
      <div class="page-head"><h3>📢 최근 공지</h3><a href="#/board/notice">더 보기</a></div>
      <div class="card list">${notices}</div>
      <div class="grid2">
        <div class="card"><h3>🎬 최신 강의</h3>${lec ? `<p><span class="week">${lec.week}주차</span><a href="#/lecture/${lec.id}">${esc(lec.title)}</a></p>` : '<p class="muted">아직 없어요.</p>'}</div>
        <div class="card"><h3>📄 최신 문제</h3>${prob ? `<p>${prob.week ? `<span class="week">${prob.week}주차</span>` : ''}<a href="#/set/${prob.id}">${esc(prob.title)}</a></p>` : '<p class="muted">아직 없어요.</p>'}</div>
      </div>`];
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
      <p><a href="#/lectures">← 강의 목록</a>${isAdmin() ? ' <button class="link" id="editLec">✏️ 수정</button>' : ''}</p>
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
    notice: { name: '공지사항', icon: '📢', adminOnly: true, anon: false, week: false, desc: '' },
    problem: { name: '문제', icon: '📄', adminOnly: true, anon: false, week: true, desc: '주차별 문제 파일이에요. 궁금한 점은 댓글로 물어보세요.' },
    qna: { name: '질문 게시판', icon: '❓', adminOnly: false, anon: true, week: false, desc: '모르는 건 편하게 물어보세요. 익명으로도 쓸 수 있어요.' },
    assignment: { name: '과제 제출', icon: '📝', adminOnly: false, anon: false, week: false, desc: '내가 낸 과제는 나와 선생님만 볼 수 있어요. 코드는 ``` 로 감싸서 붙여넣거나 파일로 첨부하세요.' },
    free: { name: '자유게시판', icon: '💬', adminOnly: false, anon: true, week: false, desc: '자유롭게 이야기해요. 익명으로도 쓸 수 있어요.' },
  };

  async function pageBoard(key) {
    const B = BOARDS[key];
    let q = sb.from('posts_view')
      .select('id,title,created_at,author_name,anonymous,files,week')
      .eq('board', key);
    if (B.week) q = q.order('week', { ascending: false, nullsFirst: false });
    const { data, error } = await q.order('created_at', { ascending: false });
    if (error) throw error;
    const canWrite = !B.adminOnly || isAdmin();
    const rows = data.length ? data.map((p) => `
      <a class="row" href="#/post/${p.id}">
        <div class="row-main">${p.week ? `<span class="week">${p.week}주차</span>` : ''}<b>${esc(p.title)}</b>${(p.files || []).length ? ` <span title="첨부파일 ${(p.files || []).length}개">📎${(p.files || []).length}</span>` : ''}</div>
        <div class="muted small meta">${esc(p.author_name)}${p.anonymous && isAdmin() ? ' (익명 작성)' : ''} · ${fmt(p.created_at)}</div>
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
        <div class="c-head"><b>${esc(c.author_name)}</b>${c.by_admin ? ' <span class="badge">선생님</span>' : ''}
          <span class="muted small"> · ${fmt(c.created_at)}</span>
          ${c.is_mine || isAdmin() ? ` <button class="link danger" data-delc="${c.id}">삭제</button>` : ''}</div>
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
        <p class="muted small">${esc(p.author_name)}${p.anonymous && isAdmin() ? ' (익명 작성)' : ''} · ${fmt(p.created_at)}${p.updated_at ? ' (수정됨)' : ''}
          ${p.is_mine ? ` <a href="#/edit/${p.id}">수정</a>` : ''}
          ${p.is_mine || isAdmin() ? ' <button class="link danger" id="delPost">글 삭제</button>' : ''}</p>
        ${renderContent(p.content)}
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
    if (B.adminOnly && !isAdmin()) return ['<div class="card pad center">선생님만 쓸 수 있는 게시판이에요.</div>'];
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
    if (/^(elite|엘리트)/.test(k)) return 'ELITE';
    if (/^(adv|고급|상)/.test(k)) return 'Advanced';
    if (/^(int|중)/.test(k)) return 'Intermediate';
    return 'Beginner';
  };

  let openPanels = new Set(); // 열려 있는 '풀어보기' 칸 (문제 고유 번호)
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
  async function pageSets() {
    const [sr, ex, mine] = await Promise.all([
      sb.from('problem_sets').select('*').order('week', { ascending: true, nullsFirst: false }).order('id'),
      fetchAll((a, b) => sb.from('exercises').select('id,set_id').order('id').range(a, b)),
      isAdmin() ? Promise.resolve([]) : fetchAll((a, b) => sb.from('submissions').select('id,exercise_id,set_id').eq('user_id', me.id).order('id').range(a, b)),
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
        <div class="set-top">${s.week ? `<span class="week">${s.week}주차</span>` : ''}<h3>${esc(s.title)}</h3></div>
        ${s.description ? `<p class="muted small">${esc(s.description)}</p>` : ''}
        <div class="muted small">문제 ${t}개${isAdmin() ? '' : ` · 내가 푼 문제 ${d}개`}</div>
        ${isAdmin() ? '' : `<div class="bar"><i style="width:${t ? Math.round((d / t) * 100) : 0}%"></i></div>`}
      </a>`;
    }).join('') : '<div class="card pad center muted">아직 올라온 문제집이 없어요.</div>';

    return [`
      <div class="page-head"><h2>📄 문제</h2>${isAdmin() ? '<button class="primary" id="newSet">＋ 새 문제집</button>' : ''}</div>
      <p class="muted">문제를 하나씩 보고, <b class="redtxt">풀어보기</b>로 코드를 제출해요. 제출한 풀이는 선생님만 볼 수 있어요.</p>
      <div class="sets">${cards}</div>
      <p class="muted small"><a href="#/board/problem">📁 예전에 올린 문제 파일 보기</a></p>`,
    (v) => {
      const nb = $('#newSet', v);
      if (nb) nb.onclick = openNewSet;
    }];
  }

  function openNewSet() {
    let parsed = null;
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
      const { data: s, error } = await sb.from('problem_sets').insert({
        title: q('#nsTitle').value.trim(), short_name: q('#nsShort').value.trim() || null,
        week: Number(q('#nsWeek').value) || null, description: q('#nsDesc').value.trim() || null,
      }).select('id').single();
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
      toast('문제집을 만들었어요');
      location.hash = '#/set/' + s.id;
    };
  }

  /* ---------- 문제집 화면 ---------- */
  async function pageSet(rawId) {
    const id = Number(rawId);
    const admin = isAdmin();
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
          ${admin ? `<button class="ghost" data-hwstat="${h.id}">📊 제출 현황</button><button class="ghost" data-hwedit="${h.id}">✏️ 수정</button><button class="ghost" data-hwdel="${h.id}">🗑</button>` : ''}
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
      return `<article class="ex ${e.difficulty === 'ELITE' ? 'elite' : ''}" id="ex-${e.id}" data-hws="${(hwOf[e.id] || []).map((h) => h.id).join(',')}">
        <header class="ex-head">
          <span class="ex-no">${dispNo(e)}</span>
          <span class="dbadge d-${e.difficulty}">${e.difficulty}</span>
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
        <h2>${set.week ? `<span class="week">${set.week}주차</span>` : ''}${esc(set.title)}</h2>
      </div>
      ${set.description ? `<p class="muted">${esc(set.description)}</p>` : ''}
      <div class="form-actions" style="margin:0 0 12px">
        ${files.join('')}
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
          <p class="muted small" style="margin:4px 0">${canGrade ? '제출하면 자동으로 채점돼요. 채점 결과는 선생님도 볼 수 있어요. ' : ''}${answers.some((a) => a.type === 'm') ? '서술형 답은 선생님이 확인해요. ' : ''}${last ? '다시 내면 새 버전으로 쌓이고, 이전 풀이도 그대로 남아요.' : '제출한 풀이는 선생님만 볼 수 있어요.'}</p>
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
        const gradeBtn = $('[data-grade]', p);
        if (gradeBtn) gradeBtn.onclick = async () => {
          if (empty()) return toast('답을 입력하세요', true);
          lock(true);
          try {
            const g = await doGrade();
            p._graded = { sig: sig(), g };
            gradeMemo.set(eid, renderGrade(g.res, g.parts, answers, reveal));
            showJ(gradeMemo.get(eid));
          } catch (err) {
            showJ(renderRun({ status: 'LOAD', err: String(err.message || err) }));
          }
          lock(false);
        };
        $('[data-send]', p).onclick = async () => {
          if (empty()) return toast('내용을 입력하세요', true);
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
          toast(!judge ? '제출했어요! 👍' : judge.status === 'MANUAL' ? '제출했어요. 선생님이 확인할 거예요 👍' : judge.status === 'AC' ? '제출했어요! 자동 채점을 모두 통과했어요 🎉' : `제출했어요. 채점 결과는 ${judge.passed}/${judge.total} 통과예요`);
          route(true);
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
    'def judge_run(code, inp):',
    '    so, si, se = sys.stdout, sys.stdin, sys.stderr',
    '    out = io.StringIO()',
    '    sys.stdin = io.StringIO(inp)',
    '    sys.stdout = out',
    '    sys.stderr = io.StringIO()',
    '    err = None',
    '    try:',
    '        exec(compile(code, "main.py", "exec"), {"__name__": "__main__"})',
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
  try { postMessage(Object.assign({ id: d.id }, JSON.parse(run(d.code, d.input)))); }
  catch (e) { postMessage({ id: d.id, ok: false, out: '', err: String(e) }); }
};`;
  let jw = null;
  let jseq = 0;

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

  // 코드를 한 번 실행 → {status: OK | RE | TLE | LOAD, out, err}
  async function runOnce(code, input, limit = 3000) {
    let w;
    try { w = await jworker(); } catch (e) { return { status: 'LOAD', out: '', err: String(e.message || e) }; }
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
      w.postMessage({ id, code, input });
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
      return `<tr><td><b>${esc(p.username)}</b></td><td>${done} / ${all.length}</td>
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
    const cur = ex || { ...base, label: '', points: null, tags: [], source: '', body: '', check_point: '', answers: [] };
    const uniq = (k) => [...new Set(list.map((e) => e[k]).filter(Boolean))];
    const m = modal(`
      <h3>${ex ? `문제 수정 <span class="muted small">(고유 번호 ${ex.id})</span>` : '문제 추가'}</h3>
      <form id="exForm">
        <div class="grid2">
          <label>난이도<select id="fDiff">${DIFFS.map((d) => `<option ${cur.difficulty === d ? 'selected' : ''}>${d}</option>`).join('')}</select></label>
          <label>유형 (선택)<input type="text" id="fLabel" placeholder="예: 빈칸 채우기 · 서술형" value="${esc(cur.label || '')}"></label>
        </div>
        <div class="grid2">
          <label>배점 (선택)<input type="number" id="fPts" min="0" value="${cur.points ?? ''}"></label>
          <label>출처 (선택)<input type="text" id="fSrc" placeholder="예: 백준 2557번" value="${esc(cur.source || '')}"></label>
        </div>
        <label>태그 (쉼표로 구분, 선택)<input type="text" id="fTags" placeholder="예: 50자 이내, abs() 사용 금지" value="${esc((cur.tags || []).join(', '))}"></label>
        <div class="grid2">
          <label>챕터<input type="text" id="fCh" list="dlCh" value="${esc(cur.chapter || '')}"></label>
          <label>섹션<input type="text" id="fSec" list="dlSec" value="${esc(cur.section || '')}"></label>
        </div>
        <datalist id="dlCh">${uniq('chapter').map((x) => `<option value="${esc(x)}">`).join('')}</datalist>
        <datalist id="dlSec">${uniq('section').map((x) => `<option value="${esc(x)}">`).join('')}</datalist>
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

  /* ---------- 제출함 (선생님 전용) ---------- */
  async function pageReview(setId, userId) {
    if (!isAdmin()) return ['<div class="card pad center">선생님만 볼 수 있어요.</div>'];
    if (setId && userId) return reviewDetail(Number(setId), userId);

    const [sr, subs, pr] = await Promise.all([
      sb.from('problem_sets').select('id,title,short_name,week').order('week', { ascending: true, nullsFirst: false }).order('id'),
      fetchAll((a, b) => sb.from('submissions').select('id,set_id,user_id,exercise_id,created_at').order('id').range(a, b)),
      sb.from('profiles').select('id,username'),
    ]);
    if (sr.error) throw sr.error;
    if (pr.error) throw pr.error;
    const names = {};
    pr.data.forEach((p) => { names[p.id] = p.username; });
    const setMap = {};
    sr.data.forEach((s, i) => { setMap[s.id] = { ...s, order: i }; });

    const groups = {};
    subs.forEach((s) => {
      if (reviewSet && String(s.set_id) !== reviewSet) return;
      const k = `${s.set_id}:${s.user_id}`;
      const g = groups[k] || (groups[k] = { set_id: s.set_id, user_id: s.user_id, ex: new Set(), n: 0, last: s.created_at });
      g.ex.add(s.exercise_id);
      g.n += 1;
      if (s.created_at > g.last) g.last = s.created_at;
    });
    const list = Object.values(groups).filter((g) => setMap[g.set_id]).sort((a, b) =>
      (names[a.user_id] || '').localeCompare(names[b.user_id] || '') || setMap[a.set_id].order - setMap[b.set_id].order);

    const rows = list.length ? list.map((g) => `
      <a class="row" href="#/review/${g.set_id}/${g.user_id}">
        <div class="row-main"><b>${esc(names[g.user_id] || '(알 수 없음)')} - ${esc(shortOf(setMap[g.set_id]))}</b>
          <span class="muted small"> 푼 문제 ${g.ex.size}개 · 제출 ${g.n}회</span></div>
        <div class="muted small meta">최근 ${fmt(g.last)}</div>
      </a>`).join('') : '<p class="muted center pad">아직 제출된 풀이가 없어요.</p>';

    return [`
      <div class="page-head"><h2>📥 제출함</h2>
        <select id="rvSet" style="width:auto"><option value="">전체 문제집</option>${sr.data.map((s) => `<option value="${s.id}" ${String(s.id) === reviewSet ? 'selected' : ''}>${esc(shortOf(s))}</option>`).join('')}</select></div>
      <p class="muted">학생별·문제집별로 모아 두었어요. 누르면 푼 문제들이 나와요. 이 목록은 선생님만 볼 수 있어요.</p>
      <div class="card list">${rows}</div>`,
    (v) => { $('#rvSet', v).onchange = (e) => { reviewSet = e.target.value; route(); }; }];
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
    const title = `${pr.data.username} - ${shortOf(sr.data)}`;
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
          ${cs.map((c) => `<div class="tcomment"><span class="badge">선생님</span> <span class="muted small">${fmt(c.created_at)}</span> <button class="link danger" data-delcm="${c.id}">삭제</button><div class="txt">${esc(c.content)}</div></div>`).join('')}
          <form data-cform="${s.id}"><textarea style="min-height:70px" placeholder="이 풀이에 댓글 (학생이 볼 수 있어요)" required></textarea>
            <div class="form-actions"><button class="primary">댓글 달기</button></div></form>
        </div>`;
      }).join('');
      const nC = vers.reduce((n, s) => n + (s.submission_comments || []).length, 0);
      return `<details class="rv" data-rv="${e.id}" ${reviewOpen.has(e.id) ? 'open' : ''}>
        <summary><span class="ex-no sm">${dispNo(e)}</span> <span class="dbadge d-${e.difficulty}">${e.difficulty}</span>
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
      <p><a href="#/review">← 제출함</a></p>
      <div class="page-head"><h2>📄 ${esc(title)}</h2></div>
      <p class="muted">푼 문제 ${solved.length}개 · 문제를 누르면 풀이가 펼쳐져요.</p>
      <div class="card list rvlist">${solved.length ? solved.map(item).join('') : '<p class="muted center pad">제출한 문제가 없어요.</p>'}</div>`,
    (v) => {
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
      <div class="card"><h3>화면</h3><button class="ghost" id="themeBtn2">다크모드 켜기/끄기</button></div>`,
    (v) => {
      $('#themeBtn2', v).onclick = toggleTheme;
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

  /* ---------- 관리자 ---------- */
  async function pageAdmin() {
    if (!isAdmin()) return ['<div class="card pad center">선생님만 볼 수 있어요.</div>'];
    const tabs = [['members', '👥 회원'], ['lectures', '🎬 강의']];
    if (!tabs.some(([k]) => k === adminTab)) adminTab = 'members';
    const sub = { members: adminMembers, lectures: adminLectures }[adminTab];
    const [body, bind] = await sub();
    return [`
      <div class="page-head"><h2>🛠️ 관리자</h2></div>
      <div class="tabs">${tabs.map(([k, n]) => `<button data-atab="${k}" class="${adminTab === k ? 'on' : ''}">${n}</button>`).join('')}</div>
      <p class="muted small">문제집 만들기·문제 추가/수정은 <a href="#/sets">📄 문제</a> 메뉴에서, 학생 풀이는 <a href="#/review">📥 제출함</a>에서 봐요.</p>
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
    const line = (x, btns) => `<div class="row"><div class="row-main"><b>${esc(x.username)}</b> <span class="muted small">${fmt(x.created_at)}${x.role === 'admin' ? ' · 관리자' : ''}</span></div><div>${btns}</div></div>`;
    const block = (title, arr, btns) => `<h3>${title} (${arr.length})</h3><div class="card list">${arr.length ? arr.map((x) => line(x, btns(x))).join('') : '<p class="muted center pad">없어요.</p>'}</div>`;
    return [
      block('가입 신청 대기', pending, (x) => `<button class="primary" data-act="approve" data-id="${x.id}">승인</button> <button class="ghost" data-act="reject" data-id="${x.id}">거절</button>`)
      + block('승인된 학생', approved, (x) => `<button class="ghost" data-act="reset" data-name="${esc(x.username)}">비밀번호 초기화</button> <button class="ghost" data-act="reject" data-id="${x.id}">사용 중지</button>`)
      + block('거절/중지', rejected, (x) => `<button class="ghost" data-act="approve" data-id="${x.id}">다시 승인</button>`),
      (v) => {
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
    if (me.status === 'pending') return renderStatus('pending');
    if (me.status === 'rejected') return renderStatus('rejected');
    renderShell();
    route();
  }

  sb.auth.onAuthStateChange((event) => {
    if (event === 'SIGNED_OUT' && !signingUp) { me = null; renderAuth(); }
  });
  window.addEventListener('hashchange', () => route());
  boot();
})();
