'use strict';
(() => {
  const app = document.getElementById('app');

  if (!window.supabase || String(CONFIG.SUPABASE_URL).includes('여기에')) {
    app.innerHTML = '<div class="card" style="max-width:480px;margin:60px auto"><h2>설정이 필요해요</h2><p>config.js 파일에 Supabase 주소와 키를 넣어주세요. (README.md 4번)</p></div>';
    return;
  }

  const sb = window.supabase.createClient(CONFIG.SUPABASE_URL, CONFIG.SUPABASE_ANON_KEY);
  const SITE = CONFIG.SITE_NAME || 'PyNest';

  /* ---------- 공통 도구 ---------- */
  const $ = (s, el = document) => el.querySelector(s);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const fmt = (d) => new Date(d).toLocaleString('ko-KR', { year: '2-digit', month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  const emailOf = (id) => `${id.toLowerCase()}@pyclass.site`; // ID를 가짜 이메일로 바꿔서 로그인에 사용
  const ID_RE = /^[a-z0-9_]{3,20}$/;
  const rand = () => Math.random().toString(36).slice(2, 8);

  let me = null;
  let signingUp = false;
  let navTok = 0;
  let adminTab = 'members';

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

  /* ---------- 로그인 / 가입 신청 ---------- */
  function renderAuth(tab = 'login') {
    const signup = tab === 'signup';
    app.innerHTML = `
      <div class="auth-wrap"><div class="card auth">
        <h1 class="logo">🐍 ${esc(SITE)}</h1>
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
    ['home', '🏠', '홈'], ['lectures', '🎬', '강의'], ['problems', '📄', '문제'],
    ['board/notice', '📢', '공지'], ['board/qna', '❓', '질문'], ['board/assignment', '📝', '과제'],
    ['judge', '⚖️', '온라인 저지', true], ['live', '📡', '라이브', true],
  ];

  function renderShell() {
    const items = NAV.slice();
    if (isAdmin()) items.push(['admin', '🛠️', '관리자']);
    app.innerHTML = `
      <header class="top">
        <a class="brand" href="#/home">🐍 ${esc(SITE)}</a>
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
    const [a, b] = (location.hash.replace(/^#\//, '') || 'home').split('/');
    const key = a === 'board' || a === 'write' ? `board/${b}` : a === 'lecture' ? 'lectures' : a;
    document.querySelectorAll('#menu a').forEach((l) => l.classList.toggle('on', l.dataset.k === key));

    const pages = {
      home: () => pageHome(),
      lectures: () => pageLectures(),
      lecture: () => pageLecture(b),
      problems: () => pageProblems(),
      board: () => (BOARDS[b] ? pageBoard(b) : notFound()),
      post: () => pagePost(b),
      write: () => (BOARDS[b] ? pageWrite(b) : notFound()),
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
      sb.from('problems').select('*').order('week', { ascending: false }).limit(1),
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
        <div class="card"><h3>📄 최신 문제</h3>${prob ? `<p><span class="week">${prob.week}주차</span><a href="#/problems">${esc(prob.title)}</a></p>` : '<p class="muted">아직 없어요.</p>'}</div>
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
      <p><a href="#/lectures">← 강의 목록</a></p>
      <h2><span class="week">${x.week}주차</span>${esc(x.title)}</h2>
      ${player}
      ${x.description ? `<div class="card">${renderContent(x.description)}</div>` : ''}`];
  }

  /* ---------- 문제 PDF ---------- */
  async function pageProblems() {
    const { data, error } = await sb.from('problems').select('*').order('week', { ascending: false }).order('id', { ascending: false });
    if (error) throw error;
    const rows = data.length ? data.map((x) => `<div class="row"><div class="row-main"><span class="week">${x.week}주차</span><b>${esc(x.title)}</b></div><button class="primary" data-dl="${x.id}">다운로드</button></div>`).join('')
      : '<p class="muted center pad">아직 올라온 문제가 없어요.</p>';
    return [`<div class="page-head"><h2>📄 문제</h2></div><div class="card list">${rows}</div>`, (v) => {
      v.querySelectorAll('[data-dl]').forEach((b) => (b.onclick = () => {
        const x = data.find((d) => String(d.id) === b.dataset.dl);
        if (x) download('problems', x.file_path, x.file_name);
      }));
    }];
  }

  /* ---------- 게시판 ---------- */
  const BOARDS = {
    notice: { name: '공지사항', icon: '📢', adminOnly: true, anon: false, desc: '' },
    qna: { name: '질문 게시판', icon: '❓', adminOnly: false, anon: true, desc: '모르는 건 편하게 물어보세요. 익명으로도 쓸 수 있어요.' },
    assignment: { name: '과제 제출', icon: '📝', adminOnly: false, anon: false, desc: '내가 낸 과제는 나와 선생님만 볼 수 있어요. 코드는 ``` 로 감싸서 붙여넣거나 파일로 첨부하세요.' },
  };

  async function pageBoard(key) {
    const B = BOARDS[key];
    const { data, error } = await sb.from('posts_view')
      .select('id,title,created_at,author_name,anonymous,file_path')
      .eq('board', key).order('created_at', { ascending: false });
    if (error) throw error;
    const canWrite = !B.adminOnly || isAdmin();
    const rows = data.length ? data.map((p) => `
      <a class="row" href="#/post/${p.id}">
        <div class="row-main"><b>${esc(p.title)}</b>${p.file_path ? ' <span title="첨부파일">📎</span>' : ''}</div>
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
          ${p.board === 'qna' ? '<label class="inline" style="margin:0"><input type="checkbox" id="cAnon"> 익명으로</label>' : ''}
        </div>
      </form>` : '<p class="muted small">이 글은 댓글을 달 수 없어요.</p>';

    return [`
      <p><a href="#/board/${p.board}">← ${B.name}</a></p>
      <div class="card">
        <h2 class="post-title">${esc(p.title)}</h2>
        <p class="muted small">${esc(p.author_name)}${p.anonymous && isAdmin() ? ' (익명 작성)' : ''} · ${fmt(p.created_at)}
          ${p.is_mine || isAdmin() ? ' <button class="link danger" id="delPost">글 삭제</button>' : ''}</p>
        ${renderContent(p.content)}
        ${p.file_path ? `<div class="attach">📎 <button class="link" id="dlFile">${esc(p.file_name || '첨부파일')}</button></div>` : ''}
      </div>
      <div class="card"><h3>댓글 ${cs ? cs.length : 0}</h3>${comments}${commentBox}</div>`,
    (v) => {
      const dl = $('#dlFile', v);
      if (dl) dl.onclick = () => download('attachments', p.file_path, p.file_name || 'file');

      const dp = $('#delPost', v);
      if (dp) dp.onclick = async () => {
        if (!confirm('이 글을 삭제할까요?')) return;
        const { error: e } = await sb.from('posts').delete().eq('id', id);
        if (e) return toast('삭제하지 못했어요', true);
        if (p.file_path) await sb.storage.from('attachments').remove([p.file_path]);
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

  async function pageWrite(key) {
    const B = BOARDS[key];
    if (B.adminOnly && !isAdmin()) return ['<div class="card pad center">선생님만 쓸 수 있는 게시판이에요.</div>'];
    return [`
      <p><a href="#/board/${key}">← ${B.name}</a></p>
      <div class="card">
        <h2>${B.icon} ${B.name} 글쓰기</h2>
        <form id="wForm">
          <label>제목<input type="text" id="wTitle" maxlength="120" required></label>
          <label>내용
            ${key === 'assignment' ? '<button type="button" class="link" id="codeBtn">+ 코드 블록 넣기</button>' : ''}
            <textarea id="wBody" class="${key === 'assignment' ? 'code' : ''}" placeholder="${key === 'assignment' ? '코드는 ```python 으로 시작해서 ``` 로 끝내면 코드 모양으로 보여요.' : ''}"></textarea>
          </label>
          <label>파일 첨부 (선택, 10MB 이하)<input type="file" id="wFile"></label>
          <div class="form-actions" style="flex-direction:column;align-items:flex-start">
            <label class="inline"><input type="checkbox" id="wComments" checked> 댓글 허용</label>
            ${B.anon ? '<label class="inline"><input type="checkbox" id="wAnon"> 익명으로 올리기</label>' : ''}
            <button class="primary" id="wBtn" style="margin-top:6px">올리기</button>
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
        const file = $('#wFile', v).files[0];
        if (!title) return toast('제목을 입력하세요', true);
        if (!content.trim() && !file) return toast('내용이나 파일 중 하나는 있어야 해요', true);
        if (file && file.size > 10 * 1024 * 1024) return toast('파일은 10MB 이하만 올릴 수 있어요', true);
        const btn = $('#wBtn', v);
        btn.disabled = true;
        let file_path = null;
        let file_name = null;
        if (file) {
          const ext = (file.name.match(/\.[A-Za-z0-9]{1,8}$/) || [''])[0];
          file_path = `${key}/${me.id}/${Date.now()}_${rand()}${ext}`;
          file_name = file.name;
          const { error: ue } = await sb.storage.from('attachments').upload(file_path, file);
          if (ue) { btn.disabled = false; return toast('파일을 올리지 못했어요', true); }
        }
        const { data, error: ie } = await sb.from('posts').insert({
          board: key, title, content, author_id: me.id,
          anonymous: !!($('#wAnon', v) && $('#wAnon', v).checked),
          allow_comments: $('#wComments', v).checked,
          file_path, file_name,
        }).select('id').single();
        if (ie || !data) {
          if (file_path) await sb.storage.from('attachments').remove([file_path]);
          btn.disabled = false;
          return toast('글을 올리지 못했어요', true);
        }
        location.hash = '#/post/' + data.id;
      };
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
    const tabs = [['members', '👥 회원'], ['lectures', '🎬 강의'], ['problems', '📄 문제']];
    const sub = { members: adminMembers, lectures: adminLectures, problems: adminProblems }[adminTab];
    const [body, bind] = await sub();
    return [`
      <div class="page-head"><h2>🛠️ 관리자</h2></div>
      <div class="tabs">${tabs.map(([k, n]) => `<button data-atab="${k}" class="${adminTab === k ? 'on' : ''}">${n}</button>`).join('')}</div>
      ${body}`,
    (v) => {
      v.querySelectorAll('[data-atab]').forEach((b) => (b.onclick = () => { adminTab = b.dataset.atab; route(); }));
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
    const rows = data.length ? data.map((x) => `<div class="row"><div class="row-main"><span class="week">${x.week}주차</span>${esc(x.title)}</div><button class="ghost" data-del="${x.id}">삭제</button></div>`).join('') : '<p class="muted center pad">아직 없어요.</p>';
    return [`
      <div class="card">
        <h3>강의 추가</h3>
        <form id="lForm">
          <div class="grid2">
            <label>주차<input type="number" id="lWeek" min="1" required></label>
            <label>제목<input type="text" id="lTitle" required></label>
          </div>
          <label>YouTube 링크 (일부 공개 영상 주소)<input type="url" id="lUrl" placeholder="https://youtu.be/..." required></label>
          <label>설명 (선택)<textarea id="lDesc" style="min-height:80px"></textarea></label>
          <div class="form-actions"><button class="primary">추가</button></div>
        </form>
      </div>
      <h3>등록된 강의</h3><div class="card list">${rows}</div>`,
    (v) => {
      $('#lForm', v).onsubmit = async (e) => {
        e.preventDefault();
        const url = $('#lUrl', v).value.trim();
        if (!ytId(url)) return toast('YouTube 링크를 읽을 수 없어요', true);
        const { error: er } = await sb.from('lectures').insert({
          week: Number($('#lWeek', v).value), title: $('#lTitle', v).value.trim(),
          youtube_url: url, description: $('#lDesc', v).value.trim() || null,
        });
        if (er) return toast('추가하지 못했어요', true);
        toast('강의를 추가했어요');
        route();
      };
      v.querySelectorAll('[data-del]').forEach((b) => (b.onclick = async () => {
        if (!confirm('이 강의를 삭제할까요?')) return;
        const { error: er } = await sb.from('lectures').delete().eq('id', Number(b.dataset.del));
        if (er) return toast('삭제하지 못했어요', true);
        route(true);
      }));
    }];
  }

  async function adminProblems() {
    const { data, error } = await sb.from('problems').select('*').order('week', { ascending: false }).order('id', { ascending: false });
    if (error) throw error;
    const rows = data.length ? data.map((x) => `<div class="row"><div class="row-main"><span class="week">${x.week}주차</span>${esc(x.title)}</div><button class="ghost" data-del="${x.id}">삭제</button></div>`).join('') : '<p class="muted center pad">아직 없어요.</p>';
    return [`
      <div class="card">
        <h3>문제 PDF 올리기</h3>
        <form id="pForm">
          <div class="grid2">
            <label>주차<input type="number" id="pWeek" min="1" required></label>
            <label>제목<input type="text" id="pTitle" required></label>
          </div>
          <label>PDF 파일<input type="file" id="pFile" accept="application/pdf,.pdf" required></label>
          <div class="form-actions"><button class="primary" id="pBtn">올리기</button></div>
        </form>
      </div>
      <h3>올라간 문제</h3><div class="card list">${rows}</div>`,
    (v) => {
      $('#pForm', v).onsubmit = async (e) => {
        e.preventDefault();
        const f = $('#pFile', v).files[0];
        if (!f) return;
        if (!f.name.toLowerCase().endsWith('.pdf')) return toast('PDF 파일만 올릴 수 있어요', true);
        const btn = $('#pBtn', v);
        btn.disabled = true;
        const path = `${Date.now()}_${rand()}.pdf`;
        const { error: ue } = await sb.storage.from('problems').upload(path, f, { contentType: 'application/pdf' });
        if (ue) { btn.disabled = false; return toast('파일을 올리지 못했어요', true); }
        const { error: ie } = await sb.from('problems').insert({
          week: Number($('#pWeek', v).value), title: $('#pTitle', v).value.trim(), file_path: path, file_name: f.name,
        });
        if (ie) {
          await sb.storage.from('problems').remove([path]);
          btn.disabled = false;
          return toast('등록하지 못했어요', true);
        }
        toast('문제를 올렸어요');
        route();
      };
      v.querySelectorAll('[data-del]').forEach((b) => (b.onclick = async () => {
        if (!confirm('이 문제를 삭제할까요?')) return;
        const x = data.find((d) => String(d.id) === b.dataset.del);
        const { error: er } = await sb.from('problems').delete().eq('id', Number(b.dataset.del));
        if (er) return toast('삭제하지 못했어요', true);
        if (x) await sb.storage.from('problems').remove([x.file_path]);
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
