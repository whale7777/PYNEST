'use strict';
(() => {
  const app = document.getElementById('app');
  if (!window.supabase || !window.PYJ || String(CONFIG.SUPABASE_URL).includes('여기에')) {
    app.innerHTML = '<div class="card" style="max-width:480px;margin:60px auto"><h2>설정이 필요해요</h2><p>PyNest 의 config.js 에 Supabase 주소와 키가 들어 있어야 해요.</p></div>';
    return;
  }
  const sb = window.supabase.createClient(CONFIG.SUPABASE_URL, CONFIG.SUPABASE_ANON_KEY);
  const {
    esc, fmt, renderMarkup, runOnce, gradeAll, renderRun, renderGrade, judgeBadge, summarize, testsToText, textToTests, testsFromBody,
    normTests, normAnswers, answersToText, textToAnswers, gradeParts, packSubmission, unpackSubmission,
  } = window.PYJ;

  const $ = (s, el = document) => el.querySelector(s);
  const emailOf = (id) => `${id.toLowerCase()}@pyclass.site`;
  let me = null;
  let navTok = 0;
  let LIVE = null; // 진행 중인 사이트 방송 (다른 페이지로 이동해도 유지돼요)
  let liveUi = null; // 지금 열려 있는 방송 콘솔이 화면을 다시 그리는 함수
  let timers = [];
  const isAdmin = () => !!me && (me.role === 'admin' || me.staff === 'admin'); // OWNER / ADMIN (직원 역할은 staff_roles.sql)
  const clearTimers = () => { timers.forEach(clearInterval); timers = []; };
  const every = (fn, ms) => { timers.push(setInterval(fn, ms)); };
  let cleanups = [];
  const runCleanups = () => { const c = cleanups; cleanups = []; c.forEach((f) => { try { f(); } catch (e) { /* 무시 */ } }); };
  const rand = () => Math.random().toString(36).slice(2, 10);
  const ICE = (typeof CONFIG !== 'undefined' && CONFIG.ICE_SERVERS) || [{ urls: 'stun:stun.l.google.com:19302' }, { urls: 'stun:stun1.l.google.com:19302' }];
  const WEBRTC = 'webrtc'; // stream_url 이 이 값이면 "사이트에서 바로 방송"

  /* ---------- 사이트 직접 방송 (WebRTC) : 신호는 Supabase Realtime 으로 주고받아요 ---------- */
  function startViewer(sesId, vid, onState, q0 = 'auto') {
    const me0 = rand();
    let pc = null;
    let hostId = null;
    let got = false;
    let stopped = false;
    let pend = [];
    let want = q0;
    let graceT = null;
    const ch = sb.channel(`live-${sesId}`, { config: { broadcast: { self: false } } });
    const send = (m) => ch.send({ type: 'broadcast', event: 'sig', payload: { ...m, from: me0 } });
    const hello = () => { if (!got && !stopped) send({ t: 'hello' }); };
    const sendQ = () => { if (hostId && want) send({ t: 'q', to: hostId, v: want }); };
    ch.on('broadcast', { event: 'sig' }, async ({ payload: m }) => {
      if (stopped || (m.to && m.to !== me0)) return;
      if (m.t === 'host-up') hello();
      else if (m.t === 'host-down') { got = false; clearTimeout(graceT); if (pc) pc.close(); pc = null; vid.srcObject = null; onState('ended'); }
      else if (m.t === 'offer') {
        if (pc) pc.close();
        clearTimeout(graceT);
        pend = [];
        hostId = m.from;
        pc = new RTCPeerConnection({ iceServers: ICE });
        const mine = pc;
        mine.ontrack = (e) => { vid.srcObject = e.streams[0]; got = true; onState('live', e.streams[0]); setTimeout(sendQ, 300); };
        mine.onicecandidate = (e) => { if (e.candidate) send({ t: 'ice', to: hostId, c: e.candidate.toJSON() }); };
        mine.onconnectionstatechange = () => {
          if (mine !== pc) return;
          const st = mine.connectionState;
          if (st === 'connected') { clearTimeout(graceT); if (got) onState('live', vid.srcObject); }
          else if (st === 'disconnected') {
            // 잠깐 끊긴 건 저절로 돌아오는 경우가 많아서 6초는 기다려 줘요
            onState('retry');
            clearTimeout(graceT);
            graceT = setTimeout(() => { if (mine === pc && mine.connectionState !== 'connected') { got = false; hello(); } }, 6000);
          } else if (st === 'failed' || st === 'closed') { clearTimeout(graceT); got = false; onState('retry'); hello(); }
        };
        await mine.setRemoteDescription(m.sdp);
        pend.forEach((c) => mine.addIceCandidate(c).catch(() => {}));
        pend = [];
        const ans = await mine.createAnswer();
        await mine.setLocalDescription(ans);
        send({ t: 'answer', to: hostId, sdp: mine.localDescription.toJSON() });
      } else if (m.t === 'ice') {
        if (pc && pc.remoteDescription) pc.addIceCandidate(m.c).catch(() => {}); else pend.push(m.c);
      }
    }).subscribe((st) => { if (st === 'SUBSCRIBED') hello(); });
    const iv = setInterval(hello, 4000);
    const stop = () => { stopped = true; clearInterval(iv); clearTimeout(graceT); if (pc) pc.close(); sb.removeChannel(ch); };
    stop.setQuality = (q) => { want = q; sendQ(); };
    return stop;
  }

  /* 화질 단계: 시청자가 고르면 선생님 브라우저가 그 학생에게 보내는 영상만 줄여요 */
  const QUALITY = {
    auto: { label: '자동', br: 1000000 },
    720: { label: '720p', h: 720, br: 1200000 },
    480: { label: '480p', h: 480, br: 600000 },
    360: { label: '360p (데이터 절약)', h: 360, br: 350000 },
    240: { label: '240p (아주 느린 망)', h: 240, br: 150000, fps: 10 },
    audio: { label: '소리만', off: true, br: 100000 },
  };
  const QORDER = ['auto', '720', '480', '360', '240', 'audio'];
  function applyQuality(pc, key) {
    const cfg = QUALITY[key] || QUALITY.auto;
    pc.getSenders().forEach((sn) => {
      if (!sn.track || sn.track.kind !== 'video') return;
      const pr = sn.getParameters();
      pr.encodings = pr.encodings && pr.encodings.length ? pr.encodings : [{}];
      const e = pr.encodings[0];
      e.active = !cfg.off;
      e.maxBitrate = cfg.br;
      const h = (sn.track.getSettings && sn.track.getSettings().height) || 0;
      e.scaleResolutionDownBy = cfg.h && h > cfg.h ? h / cfg.h : 1;
      if (cfg.fps) e.maxFramerate = cfg.fps; else delete e.maxFramerate;
      sn.setParameters(pr).catch(() => {});
    });
  }

  /* ---------- 되감기: 시청자 브라우저가 받은 방송을 5분 조각으로 잠깐 저장해 둬요 (서버 사용 없음) ---------- */
  function makeDvr() {
    const SEG = 300000; // 조각 길이 5분
    const CAP = 300 * 1048576; // 기기 메모리 보호: 최대 약 300MB (넘으면 가장 오래된 조각부터 지움)
    const segs = [];
    let rec = null;
    let strm = null;
    let timer = null;
    let deb = null;
    let ntr = 0;
    const ok = !!window.MediaRecorder;
    const mimeOf = () => ['video/webm;codecs=vp8,opus', 'video/webm', 'video/mp4'].find((m) => MediaRecorder.isTypeSupported(m)) || '';
    function open() {
      try {
        const mime = mimeOf();
        const r = new MediaRecorder(strm, { ...(mime ? { mimeType: mime } : {}), videoBitsPerSecond: 900000 });
        const seg = { t0: Date.now(), t1: null, chunks: [], size: 0, type: r.mimeType || mime || 'video/webm', blob: null };
        segs.push(seg);
        r.ondataavailable = (e) => { if (e.data && e.data.size) { seg.chunks.push(e.data); seg.size += e.data.size; seg.blob = null; } };
        r.onstop = () => { seg.t1 = Date.now(); };
        r.start(1000);
        rec = r;
        clearTimeout(timer);
        timer = setTimeout(rotate, SEG);
        let total = segs.reduce((a, s) => a + s.size, 0);
        while (segs.length > 1 && total > CAP) total -= segs.shift().size;
      } catch (e) { rec = null; }
    }
    function rotate() {
      if (!strm || !strm.active) return;
      const old = rec;
      open();
      try { if (old && old.state !== 'inactive') old.stop(); } catch (e) { /* 무시 */ }
    }
    function finish() {
      clearTimeout(timer);
      if (rec && rec.state !== 'inactive') { try { rec.stop(); } catch (e) { /* 무시 */ } }
      rec = null;
    }
    // 오디오·비디오 트랙이 따로 들어오므로 잠깐 기다렸다가 한 번에 시작해요
    function attach(stream) {
      if (!ok || !stream) return;
      clearTimeout(deb);
      deb = setTimeout(() => {
        const n = stream.getTracks().length;
        if (stream === strm && n === ntr && rec && rec.state === 'recording') return;
        finish();
        strm = stream;
        ntr = n;
        if (n) open();
      }, 800);
    }
    const blob = (seg) => { if (!seg.blob) seg.blob = new Blob(seg.chunks, { type: seg.type }); return seg.blob; };
    const avail = () => (segs.length ? Math.floor((Date.now() - segs[0].t0) / 1000) : 0);
    // "라이브보다 behind 초 전" 위치 → 어느 조각의 몇 초인지
    function locate(behind) {
      if (!segs.length) return null;
      const now = Date.now();
      const target = now - behind * 1000;
      for (const s of segs) {
        const end = s.t1 || now;
        if (target >= s.t0 && target <= end) return { seg: s, off: (target - s.t0) / 1000 };
        if (target < s.t0) return { seg: s, off: 0 };
      }
      const last = segs[segs.length - 1];
      return { seg: last, off: Math.max(0, (now - last.t0) / 1000 - 1) };
    }
    const next = (seg) => segs[segs.indexOf(seg) + 1] || null;
    function dispose() { clearTimeout(deb); finish(); segs.length = 0; strm = null; }
    return { ok, attach, blob, avail, locate, next, dispose, segs };
  }

  function startHost(sesId, stream, onCount) {
    const hostId = 'h' + rand();
    const peers = new Map();
    const pend = new Map();
    const qual = new Map();
    const graces = new Map();
    const ch = sb.channel(`live-${sesId}`, { config: { broadcast: { self: false } } });
    const send = (m) => ch.send({ type: 'broadcast', event: 'sig', payload: { ...m, from: hostId } });
    const count = () => onCount([...peers.values()].filter((pc) => pc.connectionState === 'connected').length, peers.size);
    async function makePeer(pid) {
      if (peers.has(pid)) peers.get(pid).close();
      const pc = new RTCPeerConnection({ iceServers: ICE });
      peers.set(pid, pc);
      pend.set(pid, []);
      stream.getTracks().forEach((t) => pc.addTrack(t, stream));
      pc.onicecandidate = (e) => { if (e.candidate) send({ t: 'ice', to: pid, c: e.candidate.toJSON() }); };
      pc.onconnectionstatechange = () => {
        const st = pc.connectionState;
        clearTimeout(graces.get(pid));
        if (['failed', 'closed'].includes(st) && peers.get(pid) === pc) peers.delete(pid);
        else if (st === 'disconnected') graces.set(pid, setTimeout(() => { if (peers.get(pid) === pc && pc.connectionState !== 'connected') { pc.close(); peers.delete(pid); count(); } }, 12000));
        count();
      };
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      applyQuality(pc, qual.get(pid) || 'auto');
      send({ t: 'offer', to: pid, sdp: pc.localDescription.toJSON() });
    }
    ch.on('broadcast', { event: 'sig' }, async ({ payload: m }) => {
      if (m.to && m.to !== hostId) return;
      if (m.t === 'hello') makePeer(m.from).catch(() => {});
      else if (m.t === 'q') {
        qual.set(m.from, QUALITY[m.v] ? m.v : 'auto');
        const pc = peers.get(m.from);
        if (pc) applyQuality(pc, qual.get(m.from));
      } else if (m.t === 'answer') {
        const pc = peers.get(m.from);
        if (!pc) return;
        await pc.setRemoteDescription(m.sdp).catch(() => {});
        (pend.get(m.from) || []).forEach((c) => pc.addIceCandidate(c).catch(() => {}));
        pend.set(m.from, []);
      } else if (m.t === 'ice') {
        const pc = peers.get(m.from);
        if (pc && pc.remoteDescription) pc.addIceCandidate(m.c).catch(() => {});
        else if (pend.has(m.from)) pend.get(m.from).push(m.c);
      }
    }).subscribe((st) => { if (st === 'SUBSCRIBED') send({ t: 'host-up' }); });
    const iv = setInterval(count, 2000);
    return () => {
      clearInterval(iv);
      graces.forEach((t) => clearTimeout(t));
      send({ t: 'host-down' });
      setTimeout(() => { peers.forEach((pc) => pc.close()); peers.clear(); sb.removeChannel(ch); }, 400);
    };
  }

  function toast(msg, bad = false) {
    const t = document.createElement('div');
    t.className = 'toast' + (bad ? ' bad' : '');
    t.textContent = msg;
    $('#toasts').appendChild(t);
    setTimeout(() => t.remove(), 3500);
  }
  function setTheme(t) {
    document.documentElement.dataset.theme = t;
    try { localStorage.setItem('theme', t); } catch (e) { /* 무시 */ }
    const b = $('#themeBtn');
    if (b) b.textContent = t === 'dark' ? '☀️' : '🌙';
  }
  function modal(html) {
    const bg = document.createElement('div');
    bg.className = 'modal-bg';
    bg.innerHTML = `<div class="card modal"><button class="icon modal-x" title="닫기">✕</button>${html}</div>`;
    document.body.appendChild(bg);
    const close = () => bg.remove();
    $('.modal-x', bg).onclick = close;
    return { el: bg, close };
  }
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

  // 방송 주소 → 임베드 주소 (유튜브 영상/라이브/채널 주소, 또는 임베드 주소 그대로)
  function embedUrl(u) {
    const s = String(u || '').trim();
    if (!s) return '';
    if (/^[\w-]{11}$/.test(s)) return `https://www.youtube.com/embed/${s}?autoplay=1&rel=0`;
    try {
      const x = new URL(s);
      let id = null;
      if (x.hostname.includes('youtu.be')) id = x.pathname.slice(1).split('/')[0];
      else if (x.searchParams.get('v')) id = x.searchParams.get('v');
      else {
        const m = x.pathname.match(/\/(embed|live|shorts)\/([\w-]+)/);
        if (m && m[2] !== 'live_stream') id = m[2];
        const c = x.pathname.match(/\/channel\/([\w-]+)/);
        if (!id && c) return `https://www.youtube.com/embed/live_stream?channel=${c[1]}&autoplay=1`;
      }
      if (id) return `https://www.youtube.com/embed/${id}?autoplay=1&rel=0`;
      if (x.protocol === 'https:') return s;
    } catch (e) { /* 무시 */ }
    return '';
  }
  const videoHtml = (url, live, ended) => {
    const src = embedUrl(url);
    if (src) return `<div class="vwrap"><iframe src="${esc(src)}" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe></div>`;
    return `<div class="vwrap"><div class="vph"><div>${live ? '방송 주소가 아직 없어요' : ended ? '다시보기 주소가 아직 없어요' : '📡 방송 준비 중이에요<br><span class="small">선생님이 방송을 시작하면 여기에 나와요</span>'}</div></div></div>`;
  };

  /* ---------- 로그인 ---------- */
  function renderAuth() {
    clearTimers();
    app.innerHTML = `
      <div class="auth-wrap"><div class="card auth">
        <h1 class="logo">🎥 PyNest Live</h1>
        <p class="muted center">PyNest 아이디로 로그인하세요</p>
        <form id="authForm">
          <label>ID<input type="text" id="aid" autocomplete="username" autocapitalize="none" required></label>
          <label>비밀번호<input type="password" id="apw" autocomplete="current-password" required></label>
          <div class="form-actions"><button class="primary" id="authBtn" style="width:100%">로그인</button></div>
        </form>
        <p class="muted small center">계정이 없다면 <a href="../">PyNest</a> 에서 가입 신청을 해 주세요.</p>
      </div></div>`;
    $('#authForm').onsubmit = async (e) => {
      e.preventDefault();
      const btn = $('#authBtn');
      btn.disabled = true;
      const { error } = await sb.auth.signInWithPassword({ email: emailOf($('#aid').value.trim()), password: $('#apw').value });
      if (error) { btn.disabled = false; return toast('ID 또는 비밀번호가 맞지 않아요', true); }
      boot();
    };
  }
  function renderStatus(pending) {
    app.innerHTML = `<div class="auth-wrap"><div class="card auth center"><h2>${pending ? '⏳ 승인 대기 중이에요' : '🚫 사용할 수 없는 계정이에요'}</h2>
      <p class="muted">${pending ? '선생님이 가입을 승인하면 쓸 수 있어요.' : '선생님께 문의해 주세요.'}</p>
      <div class="form-actions" style="justify-content:center">${pending ? '<button class="primary" id="reBtn">다시 확인</button>' : ''}<button class="ghost" id="loBtn">로그아웃</button></div></div></div>`;
    $('#loBtn').onclick = () => sb.auth.signOut();
    if (pending) $('#reBtn').onclick = boot;
  }
  function renderShell() {
    app.innerHTML = `
      <header class="top">
        <a class="brand" href="#/">🎥 PyNest Live</a>
        <div class="spacer"></div>
        <a class="ghost btnlike" href="../" style="padding:6px 10px">← PyNest</a>
        ${isAdmin() ? '<a class="ghost btnlike" href="#/admin" style="padding:6px 10px">🛠 관리</a>' : ''}
        <span class="who">${esc(me.username)}${isAdmin() ? ' (선생님)' : ''}</span>
        <button class="icon" id="themeBtn" title="다크모드"></button>
        <button class="ghost" id="logoutBtn">로그아웃</button>
      </header>
      <main id="view" class="live"></main>`;
    setTheme(document.documentElement.dataset.theme || 'light');
    $('#themeBtn').onclick = () => setTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark');
    $('#logoutBtn').onclick = () => sb.auth.signOut();
  }

  /* ---------- 라우터 ---------- */
  async function route() {
    if (!me || me.status !== 'approved' || !$('#view')) return;
    clearTimers();
    runCleanups();
    const [a, b] = (location.hash.replace(/^#\//, '') || '').split('/');
    const v = $('#view');
    const tok = ++navTok;
    v.innerHTML = '<p class="loading">불러오는 중…</p>';
    try {
      let r;
      if (a === 's') r = await pageSession(b);
      else if (a === 'admin' && isAdmin()) r = b ? await pageConsole(b) : await pageAdmin();
      else r = await pageHome();
      if (tok !== navTok) return;
      v.innerHTML = r[0];
      if (r[1]) r[1](v, tok);
    } catch (err) {
      console.error(err);
      if (tok === navTok) v.innerHTML = '<div class="card pad center">불러오는 중에 문제가 생겼어요. 새로고침 해보세요.<br><span class="muted small">update6.sql 을 실행했는지 확인해 주세요.</span></div>';
    }
  }

  /* ---------- 홈 ---------- */
  async function pageHome() {
    const { data, error } = await sb.from('live_sessions').select('*').order('id', { ascending: false });
    if (error) throw error;
    const live = data.filter((s) => s.is_live);
    const rest = data.filter((s) => !s.is_live);
    const liveHtml = live.length ? live.map((s) => `<div class="card" style="border-color:#dc2626">
        <div class="live-head"><span class="badge live">● LIVE</span><h2>${esc(s.title)}</h2></div>
        <a class="primary btnlike" href="#/s/${s.id}">입장하기 →</a></div>`).join('')
      : '<div class="card center pad"><h2>📡 지금은 방송 중이 아니에요</h2><p class="muted">선생님이 방송을 시작하면 여기에 입장 버튼이 나와요.</p></div>';
    const list = rest.length ? `<div class="card" style="padding:0"><div style="padding:14px 14px 4px"><b>지난 방송 · 다시보기</b></div>${rest.map((s) => `<div class="sessrow">
        <div><b>${esc(s.title)}</b> <span class="muted small">${s.started_at ? fmt(s.started_at) : fmt(s.created_at)}</span>${s.ended_at || s.replay_url ? '' : ' <span class="badge warn">준비 중</span>'}</div>
        <a class="ghost btnlike" href="#/s/${s.id}" style="padding:6px 12px">${s.ended_at || s.replay_url ? '다시보기 · 문제' : '열기'}</a></div>`).join('')}</div>` : '';
    return [liveHtml + list];
  }

  /* ---------- 학생 : 라이브 화면 ---------- */
  async function pageSession(rawId) {
    const sid = Number(rawId);
    const { data: ses, error } = await sb.from('live_sessions').select('*').eq('id', sid).maybeSingle();
    if (error) throw error;
    if (!ses) return ['<div class="card pad center">방송을 찾을 수 없어요.</div>'];
    return [`
      <div class="live-grid">
        <section class="card" id="vcol">
          <div class="live-head"><span id="liveBadge"></span><h2>${esc(ses.title)}</h2></div>
          <div id="video"></div>
          <p class="muted small" id="vnote" style="margin:8px 0 0"></p>
        </section>
        <section class="card" id="pcol">
          <div class="ptabs" id="ptabs"></div>
          <div id="pview" class="live-prob"><p class="muted">선생님이 문제를 열면 여기에 나와요 ✍️</p></div>
        </section>
      </div>`, (v, tok) => bindSession(v, tok, ses)];
  }

  function bindSession(v, tok, ses0) {
    let ses = ses0;
    let probs = [];
    let subs = [];
    let sel = null;
    let sig = '';
    let vsig = '';
    const seen = new Set();
    let first = true;
    const drafts = new Map();
    const memo = new Map();

    let stopViewer = null;
    cleanups.push(() => { if (stopViewer) stopViewer(); });
    const drawVideo = () => {
      const s = `${ses.stream_url}|${ses.replay_url}|${ses.is_live}|${ses.ended_at}`;
      if (s === vsig) return;
      vsig = s;
      if (stopViewer) { stopViewer(); stopViewer = null; }
      const direct = ses.stream_url === WEBRTC;
      const replay = !ses.is_live && (ses.ended_at || ses.replay_url);
      $('#liveBadge', v).innerHTML = ses.is_live ? '<span class="badge live">● LIVE</span>' : replay ? '<span class="badge">다시보기</span>' : '<span class="badge warn">준비 중</span>';
      if (direct && ses.is_live) {
        let savedQ = 'auto';
        try { savedQ = localStorage.getItem('golive_q') || 'auto'; } catch (e) { /* 무시 */ }
        if (!QUALITY[savedQ]) savedQ = 'auto';
        const dvr = makeDvr();
        $('#video', v).innerHTML = `<div class="vwrap"><video id="lv" autoplay playsinline muted controls></video><video id="rv" playsinline controls hidden></video><div class="vph" id="vstat">📡 방송에 연결하는 중…</div></div>
          <div class="dvr">
            <div class="dvr-row">
              <button class="ghost" id="unm">🔊 소리 켜기</button>
              ${dvr.ok ? '<button class="ghost" id="rb30" title="30초 전으로">⏪ 30초</button><button class="ghost" id="rb10" title="10초 전으로">⏪ 10초</button><button class="ghost" id="rf10" title="10초 앞으로">10초 ⏩</button><button class="primary" id="golv">● 라이브로</button>' : ''}
              <label class="qsel">화질 <select id="qsel">${QORDER.map((k) => `<option value="${k}" ${k === savedQ ? 'selected' : ''}>${QUALITY[k].label}</option>`).join('')}</select></label>
            </div>
            ${dvr.ok ? '<div class="dvr-row"><input type="range" id="dseek" min="0" max="0" value="0" step="1" disabled><span id="dpos" class="muted small">LIVE</span></div>' : '<p class="muted small" style="margin:6px 0 0">이 브라우저는 되감기를 지원하지 않아요 (최신 크롬 권장)</p>'}
          </div>`;
        const lv = $('#lv', v);
        const rv = $('#rv', v);
        let mode = 'live';
        let curSeg = null;
        let curUrl = '';
        let prevMuted = true;
        let seeking = false;
        const mm = (sec) => { sec = Math.max(0, Math.round(sec)); return `${Math.floor(sec / 60)}:${String(sec % 60).padStart(2, '0')}`; };
        const behindNow = () => (mode === 'live' || !curSeg ? 0 : Math.max(0, (Date.now() - (curSeg.t0 + rv.currentTime * 1000)) / 1000));
        const goLive = () => {
          if (mode === 'live') return;
          mode = 'live';
          rv.pause();
          rv.hidden = true;
          if (curUrl) { URL.revokeObjectURL(curUrl); curUrl = ''; }
          rv.removeAttribute('src');
          lv.muted = prevMuted;
          lv.play().catch(() => {});
          paint();
        };
        const loadSeg = (seg, off) => new Promise((res) => {
          if (curUrl) URL.revokeObjectURL(curUrl);
          curUrl = URL.createObjectURL(dvr.blob(seg));
          curSeg = seg;
          rv.onloadedmetadata = () => {
            const go = () => {
              const d = Number.isFinite(rv.duration) ? rv.duration : off + 1;
              rv.currentTime = Math.max(0, Math.min(off, d - 0.3));
              rv.play().catch(() => {});
              res();
            };
            if (!Number.isFinite(rv.duration)) { // MediaRecorder 파일은 길이 정보가 없어서 한번 끝까지 보내 길이를 알아내요
              rv.ontimeupdate = () => { rv.ontimeupdate = null; go(); };
              rv.currentTime = 1e101;
            } else go();
          };
          rv.src = curUrl;
        });
        const rewindTo = async (behind) => {
          const maxB = dvr.avail();
          behind = Math.max(0, Math.min(behind, maxB));
          if (behind < 2) { goLive(); return; }
          const loc = dvr.locate(behind);
          if (!loc) return;
          seeking = true;
          if (mode === 'live') { prevMuted = lv.muted; lv.muted = true; }
          mode = 'rew';
          rv.hidden = false;
          rv.muted = false;
          await loadSeg(loc.seg, loc.off);
          seeking = false;
          paint();
        };
        rv.onended = () => {
          const nx = curSeg && dvr.next(curSeg);
          if (nx) loadSeg(nx, 0); else goLive();
        };
        const sk = $('#dseek', v);
        const paint = () => {
          if (!sk) return;
          const a = dvr.avail();
          const b = behindNow();
          sk.disabled = a < 6;
          sk.max = String(a);
          if (!seeking && document.activeElement !== sk) sk.value = String(Math.max(0, a - b));
          $('#dpos', v).textContent = mode === 'live' ? `LIVE · 되감기 ${mm(a)}` : `라이브보다 ${mm(b)} 전`;
          $('#golv', v).hidden = mode === 'live';
        };
        if (sk) {
          sk.onchange = () => rewindTo(dvr.avail() - Number(sk.value));
          $('#rb30', v).onclick = () => rewindTo(behindNow() + 30);
          $('#rb10', v).onclick = () => rewindTo(behindNow() + 10);
          $('#rf10', v).onclick = () => rewindTo(behindNow() - 10);
          $('#golv', v).onclick = goLive;
          $('#golv', v).hidden = true;
        }
        const posIv = setInterval(paint, 700);
        $('#unm', v).onclick = () => { prevMuted = false; if (mode === 'live') { lv.muted = false; lv.play().catch(() => {}); } $('#unm', v).hidden = true; };
        const stopV = startViewer(ses.id, lv, (st, strm) => {
          const el = $('#vstat', v);
          if (!el) return;
          el.hidden = st === 'live';
          el.innerHTML = st === 'ended' ? '방송이 잠시 멈췄어요' : st === 'retry' ? '🔄 다시 연결하는 중…' : '📡 방송에 연결하는 중…';
          if (st === 'live' && strm) dvr.attach(strm);
        }, savedQ);
        $('#qsel', v).onchange = (e) => {
          const q = e.target.value;
          stopV.setQuality(q);
          try { localStorage.setItem('golive_q', q); } catch (er) { /* 무시 */ }
          toast(`화질: ${QUALITY[q].label}`);
        };
        stopViewer = () => {
          stopV();
          clearInterval(posIv);
          dvr.dispose();
          if (curUrl) URL.revokeObjectURL(curUrl);
        };
      } else if (direct) {
        $('#video', v).innerHTML = videoHtml(replay ? ses.replay_url : '', false, replay);
      } else {
        $('#video', v).innerHTML = videoHtml(replay ? (ses.replay_url || ses.stream_url) : ses.stream_url, ses.is_live, replay);
      }
      $('#vnote', v).textContent = ses.is_live ? (direct ? '선생님 화면이 직접 연결돼요. 소리가 안 나면 "소리 켜기"를, 놓친 부분은 ⏪ 버튼이나 아래 막대로 되감아 보세요. (되감기는 내가 입장한 뒤부터 저장돼요)' : '영상이 몇 초 늦게 보일 수 있어요. 문제는 방송과 상관없이 바로 풀 수 있어요.') : '';
    };

    const mySubs = (pid) => subs.filter((s) => s.problem_id === pid);
    const stateOf = (pid) => { const m = mySubs(pid); return m.some((s) => s.ok) ? 'ok' : m.length ? 'bad' : ''; };

    const drawTabs = () => {
      $('#ptabs', v).innerHTML = probs.map((p, i) => `<button data-p="${p.id}" class="${p.id === sel ? 'on' : ''} ${p.status}">${esc(p.title) || `문제 ${i + 1}`}<span class="dot ${stateOf(p.id) || p.status}"></span></button>`).join('');
      v.querySelectorAll('[data-p]').forEach((b) => (b.onclick = () => { sel = Number(b.dataset.p); drawTabs(); drawProblem(); }));
    };

    const drawProblem = () => {
      const p = probs.find((x) => x.id === sel);
      const pv = $('#pview', v);
      if (!p) { pv.innerHTML = '<p class="muted">선생님이 문제를 열면 여기에 나와요 ✍️</p>'; return; }
      const tests = normTests(p.tests);
      const answers = normAnswers(p.answers);
      const open = p.status === 'open';
      const showCode = tests.length > 0 || !answers.length;
      const canGrade = tests.length > 0 || answers.some((a) => a.type !== 'm');
      const d = drafts.get(p.id) || { code: '', vals: [] };
      const sample = tests.find((t) => !t.hidden);
      const ms = mySubs(p.id);
      const st = stateOf(p.id);
      pv.innerHTML = `
        <h3>${esc(p.title) || '문제'} ${open ? '<span class="badge ok">진행 중</span>' : '<span class="badge">마감</span>'}
          ${st === 'ok' ? '<span class="badge ok">✅ 맞았어요</span>' : st === 'bad' ? `<span class="badge bad">❌ ${ms.length}번 제출</span>` : ''}</h3>
        <div class="ex-body">${renderMarkup(p.body)}</div>
        ${showCode ? `<textarea class="code" id="cd" spellcheck="false" placeholder="여기에 코드를 쓰세요" ${open ? '' : 'readonly'}>${esc(d.code)}</textarea>
          <details class="stdin-box"><summary>⌨️ 입력값 <span class="muted small">(실행해보기용 · 한 줄에 하나씩)</span></summary>
          <textarea class="stdin" id="sin" rows="3" spellcheck="false">${esc(sample ? sample.input : '')}</textarea></details>` : ''}
        ${answers.length ? `<div class="parts">${answers.map((a, i) => `<label class="part"><span class="plabel">${esc(a.label || i + 1)}${a.type === 'm' ? ' <span class="badge">서술</span>' : ''}</span>
          <textarea class="pans code" data-i="${i}" rows="${a.type === 'm' ? 4 : Math.min(6, Math.max(1, a.value.split('\n').length))}" spellcheck="false" ${open ? '' : 'readonly'}>${esc(d.vals[i] || '')}</textarea></label>`).join('')}</div>` : ''}
        <div class="form-actions">
          ${showCode ? '<button class="ghost" id="rb">▶ 실행해보기</button>' : ''}
          ${canGrade ? '<button class="ghost" id="gb">✅ 채점하기</button>' : ''}
          <button class="solve" id="sb" ${open ? '' : 'disabled'}>${open ? '제출하기' : '마감됐어요'}</button>
        </div>
        <div class="judge-out" id="jo" ${memo.has(p.id) ? '' : 'hidden'}>${memo.get(p.id) || ''}</div>`;
      const cd = $('#cd', pv);
      const partEls = [...pv.querySelectorAll('textarea.pans')];
      const getCode = () => (cd ? cd.value : '');
      const getVals = () => partEls.map((t) => t.value);
      const save = () => drafts.set(p.id, { code: getCode(), vals: getVals() });
      [cd, ...partEls].filter(Boolean).forEach((el) => {
        el.addEventListener('input', save);
        el.addEventListener('keydown', (ev) => {
          if (ev.key === 'Tab') { ev.preventDefault(); const s0 = el.selectionStart; el.value = el.value.slice(0, s0) + '    ' + el.value.slice(el.selectionEnd); el.selectionStart = el.selectionEnd = s0 + 4; save(); }
        });
      });
      const jo = $('#jo', pv);
      const showJ = (h) => { jo.hidden = false; jo.innerHTML = h; };
      const lock = (on) => pv.querySelectorAll('#rb,#gb,#sb').forEach((b) => { b.disabled = on || (b.id === 'sb' && !open); });
      const prep = '<span class="muted">⏳ 파이썬을 준비하는 중… (처음 한 번은 몇 초 걸려요)</span>';
      const doGrade = async () => {
        const parts = answers.length ? gradeParts(answers, getVals()) : null;
        let res = null;
        if (tests.length) {
          if (!getCode().trim()) res = { status: 'WA', passed: 0, total: tests.length, cases: tests.map((t) => ({ ok: false, st: 'WA', mode: t.mode || '', hidden: !!t.hidden, input: t.input || '', expected: t.output || '', got: '', err: '' })) };
          else { showJ(prep); res = await gradeAll(getCode(), tests, (i, n) => showJ(`<span class="muted">⏳ 채점 중… ${i + 1} / ${n}</span>`)); }
        }
        return { res, parts, judge: summarize(res, parts) };
      };
      const rb = $('#rb', pv);
      if (rb) rb.onclick = async () => {
        if (!getCode().trim()) return toast('코드를 입력하세요', true);
        lock(true); showJ(prep);
        showJ(renderRun(await runOnce(getCode(), ($('#sin', pv) || { value: '' }).value.replace(/\n?$/, '\n'))));
        lock(false);
      };
      const gb = $('#gb', pv);
      if (gb) gb.onclick = async () => {
        if (!getCode().trim() && !getVals().some((x) => x.trim())) return toast('답을 입력하세요', true);
        lock(true);
        try { const g = await doGrade(); memo.set(p.id, renderGrade(g.res, g.parts, answers, !open)); showJ(memo.get(p.id)); } catch (e) { showJ(renderRun({ status: 'LOAD', err: String(e.message || e) })); }
        lock(false);
      };
      $('#sb', pv).onclick = async () => {
        if (!getCode().trim() && !getVals().some((x) => x.trim())) return toast('내용을 입력하세요', true);
        lock(true);
        let judge = null;
        try { const g = await doGrade(); judge = g.judge; memo.set(p.id, renderGrade(g.res, g.parts, answers, false)); showJ(memo.get(p.id)); } catch (e) { toast('채점 도구를 불러오지 못해서 채점 없이 제출해요', true); }
        const code = answers.length ? packSubmission(getCode(), answers, getVals()) : getCode();
        const { error } = await sb.from('live_submissions').insert({ problem_id: p.id, user_id: me.id, code, judge });
        lock(false);
        if (error) return toast(/closed/.test(error.message || '') ? '이미 마감된 문제예요' : '제출하지 못했어요: ' + error.message, true);
        toast(!judge ? '제출했어요!' : judge.status === 'AC' ? '제출했어요! 정답이에요 🎉' : judge.status === 'MANUAL' ? '제출했어요. 선생님이 확인해요' : `제출했어요. ${judge.passed}/${judge.total} 통과`);
        await refresh();
      };
    };

    async function refresh() {
      if (tok !== navTok) return;
      const [sr, pr, ur] = await Promise.all([
        sb.from('live_sessions').select('*').eq('id', ses.id).maybeSingle(),
        sb.from('live_problems').select('*').eq('session_id', ses.id).order('position'),
        sb.from('live_submissions').select('id,problem_id,ok,judge,created_at').eq('user_id', me.id).eq('session_id', ses.id),
      ]);
      if (sr.data) ses = sr.data;
      if (pr.data) probs = pr.data;
      if (ur.data) subs = ur.data;
      drawVideo();
      const opened = probs.filter((p) => p.status === 'open' && !seen.has(p.id));
      probs.forEach((p) => seen.add(p.id));
      if (opened.length && !first) toast(`📣 새 문제가 열렸어요: ${opened[0].title || '문제'}`);
      const pick = opened.length ? opened[opened.length - 1].id : null;
      const s = probs.map((p) => `${p.id}:${p.status}:${p.title}:${stateOf(p.id)}`).join('|');
      const ps = probs.find((p) => p.id === sel);
      if (!ps || (pick && !first)) sel = pick || (probs.filter((p) => p.status === 'open').pop() || probs[probs.length - 1] || {}).id || null;
      if (s !== sig) {
        const prevSel = $('#pview', v).dataset.k;
        sig = s;
        drawTabs();
        const key = `${sel}:${(probs.find((p) => p.id === sel) || {}).status}:${stateOf(sel)}`;
        if (key !== prevSel) { drawProblem(); $('#pview', v).dataset.k = key; }
      }
      first = false;
    }

    const beat = async () => {
      if (isAdmin() || !ses.is_live) return;
      await sb.from('live_presence').upsert({ session_id: ses.id, user_id: me.id, last_seen: new Date().toISOString() }, { onConflict: 'session_id,user_id' });
    };
    refresh().then(beat);
    every(refresh, 4000);
    every(beat, 20000);
  }

  /* ---------- 관리자 : 방송 목록 ---------- */
  async function pageAdmin() {
    const { data, error } = await sb.from('live_sessions').select('*').order('id', { ascending: false });
    if (error) throw error;
    return [`
      <div class="card">
        <div class="live-head"><h2>🛠 라이브 관리</h2><span class="spacer"></span><button class="primary" id="newS">＋ 새 방송 만들기</button></div>
        <p class="muted small" style="margin:0">방송(회차)마다 문제를 따로 만들어요. 방송을 만들고 → 문제를 올리고 → OBS로 송출하면서 문제를 열어요.</p>
      </div>
      <div class="card" style="padding:0">${data.length ? data.map((s) => `<div class="sessrow">
        <div>${s.is_live ? '<span class="badge live">● LIVE</span> ' : ''}<b>${esc(s.title)}</b> <span class="muted small">${fmt(s.created_at)}</span></div>
        <div><a class="primary btnlike" href="#/admin/${s.id}" style="padding:6px 12px">관리 콘솔</a>
          <a class="ghost btnlike" href="#/s/${s.id}" style="padding:6px 12px">학생 화면</a>
          <button class="ghost" data-delS="${s.id}">🗑</button></div></div>`).join('') : '<p class="muted center pad">아직 방송이 없어요.</p>'}</div>`,
    (v) => {
      $('#newS', v).onclick = () => {
        const m = modal(`<h3>새 방송</h3><form id="f"><label>제목<input type="text" id="t" placeholder="예: 10/26 수업 · 반복문" required></label>
          <label>방송 주소 (선택 · 나중에 넣어도 돼요)<input type="text" id="u" placeholder="유튜브 라이브 주소"></label>
          <div class="form-actions"><button class="primary">만들기</button></div></form>`);
        $('#f', m.el).onsubmit = async (e) => {
          e.preventDefault();
          const { data: d, error: er } = await sb.from('live_sessions').insert({ title: $('#t', m.el).value.trim(), stream_url: $('#u', m.el).value.trim() || null }).select('id').single();
          if (er) return toast('만들지 못했어요 (update6.sql 실행했나요?)', true);
          m.close(); location.hash = `#/admin/${d.id}`;
        };
      };
      v.querySelectorAll('[data-delS]').forEach((b) => (b.onclick = async () => {
        if (!confirm('이 방송과 문제, 학생 제출을 모두 삭제할까요? 되돌릴 수 없어요.')) return;
        const { error: er } = await sb.from('live_sessions').delete().eq('id', Number(b.dataset.dels));
        if (er) return toast('삭제하지 못했어요', true);
        route();
      }));
    }];
  }

  /* ---------- 관리자 : 방송 콘솔 (송출 설정 · 문제 · 실시간 현황) ---------- */
  const PSTAT = { draft: '초안', open: '진행 중', closed: '마감' };

  async function pageConsole(rawId) {
    const sid = Number(rawId);
    const { data: ses0, error } = await sb.from('live_sessions').select('*').eq('id', sid).maybeSingle();
    if (error) throw error;
    if (!ses0) return ['<div class="card pad center">방송을 찾을 수 없어요.</div>'];
    return [`
      <p><a href="#/admin">← 방송 목록</a></p>
      <div class="card" id="cfg"></div>
      <div class="card" id="bc"></div>
      <div class="card" id="plist"></div>
      <div class="card" id="mon"></div>`, (v, tok) => bindConsole(v, tok, ses0)];
  }

  function bindConsole(v, tok, ses0) {
    let ses = ses0;
    let probs = [];
    let subs = [];
    let pres = [];
    let names = {};
    let roster = [];
    let monSel = null;
    let allStudents = false;
    const drawn = { cfg: '', plist: '' };

    /* --- 송출 설정 --- */
    async function patchSes(o, msg) {
      const { data, error } = await sb.from('live_sessions').update(o).eq('id', ses.id).select().maybeSingle();
      if (error) { toast('저장하지 못했어요', true); return false; }
      if (data) ses = data;
      drawn.cfg = '';
      drawCfg();
      if (msg) toast(msg);
      return true;
    }
    async function endAll() {
      await sb.from('live_problems').update({ status: 'closed' }).eq('session_id', ses.id).eq('status', 'open');
      await patchSes({ is_live: false, ended_at: new Date().toISOString(), replay_url: ses.replay_url || (ses.stream_url === WEBRTC ? null : ses.stream_url) }, '방송을 종료했어요');
      refresh();
    }
    let bc = LIVE && LIVE.sesId === ses.id ? LIVE : null;
    const drawCfg = () => {
      const key = JSON.stringify([ses.title, ses.stream_url, ses.replay_url, ses.is_live, ses.ended_at]);
      if (drawn.cfg === key) return;
      drawn.cfg = key;
      $('#cfg', v).innerHTML = `
        <div class="live-head">${ses.is_live ? '<span class="badge live">● LIVE</span>' : ses.ended_at ? '<span class="badge">종료됨</span>' : '<span class="badge warn">방송 전</span>'}<h2>${esc(ses.title)}</h2></div>
        <div class="grid2">
          <label>제목<input type="text" id="cT" value="${esc(ses.title)}"></label>
          <label>방송 주소 (유튜브 라이브 / 채널 주소)<input type="text" id="cU" value="${esc(ses.stream_url || '')}" placeholder="https://www.youtube.com/watch?v=…  또는 …/channel/UC…"></label>
        </div>
        <label>다시보기(녹화) 주소 <span class="muted small">— 비우면 방송 주소를 그대로 써요. 방송이 끝난 뒤 유튜브에 올라온 영상 주소를 넣으면 돼요</span>
          <input type="text" id="cR" value="${esc(ses.replay_url || '')}"></label>
        <div class="form-actions">
          <button class="ghost" id="cSave">💾 저장</button>
          ${ses.is_live ? '<button class="danger-btn" id="cEnd">⏹ 방송 종료</button>' : '<button class="primary" id="cStart">🔴 방송 시작 (학생에게 열기)</button>'}
          <a class="ghost btnlike" href="#/s/${ses.id}" target="_blank" rel="noopener">학생 화면 보기 ↗</a>
        </div>
        <details style="margin-top:10px"><summary><b>📡 OBS로 방송하고 녹화하는 방법</b></summary>
          <ol class="help-steps small">
            <li><b>유튜브 스튜디오</b> → 만들기 → <b>라이브 스트리밍</b> → 스트림 키를 복사해요. 공개 범위는 <b>일부 공개</b>로 하면 링크를 아는 사람만 볼 수 있어요.</li>
            <li><b>OBS</b> → 설정 → 방송 → 서비스 <code>YouTube - RTMPS</code> → 스트림 키 붙여넣기.</li>
            <li>OBS에서 <b>방송 시작</b>. 유튜브 스튜디오에서 <b>라이브 시작</b>을 눌러요.</li>
            <li>위 <b>방송 주소</b> 칸에 라이브 영상 주소를 붙여넣고 <b>저장</b> → <b>방송 시작(학생에게 열기)</b>. (<code>/channel/채널ID</code> 주소를 넣으면 매번 주소를 안 바꿔도 돼요)</li>
            <li><b>녹화</b>: 유튜브가 방송 끝나면 자동으로 영상을 남겨요(다시보기). 따로 파일로도 남기려면 OBS 설정 → 출력 → 녹화 경로를 정하고 <b>녹화 시작</b>을 같이 눌러요.</li>
            <li>방송이 끝나면 <b>방송 종료</b>를 눌러요. 열려 있던 문제는 자동으로 마감되고, 학생들은 다시보기 영상으로 복습할 수 있어요.</li>
          </ol></details>`;
      const q = (s) => $(s, $('#cfg', v));
      const patch = patchSes;
      const vals = () => ({ title: q('#cT').value.trim() || ses.title, stream_url: q('#cU').value.trim() || null, replay_url: q('#cR').value.trim() || null });
      q('#cSave').onclick = () => patch(vals(), '저장했어요');
      const st = q('#cStart');
      if (st) st.onclick = () => patch({ ...vals(), is_live: true, started_at: ses.started_at || new Date().toISOString(), ended_at: null }, '방송을 시작했어요. 학생들이 입장할 수 있어요');
      const en = q('#cEnd');
      if (en) en.onclick = async () => {
        if (!confirm('방송을 종료할까요? 열려 있는 문제는 마감돼요.')) return;
        if (bc) { await bc.stop(); return; }
        const o = vals();
        await sb.from('live_problems').update({ status: 'closed' }).eq('session_id', ses.id).eq('status', 'open');
        await patch({ ...o, is_live: false, ended_at: new Date().toISOString(), replay_url: o.replay_url || o.stream_url }, '방송을 종료했어요');
        refresh();
      };
    };

    /* --- 사이트에서 바로 방송 (WebRTC) --- */
    const drawBc = (fileLink = '') => {
      const on = !!bc;
      $('#bc', v).innerHTML = `
        <div class="live-head"><h2>📹 사이트에서 바로 방송하기</h2>${on ? '<span class="badge live">● 송출 중</span>' : ''}</div>
        <p class="muted small" style="margin-top:0">유튜브 없이 이 화면에서 바로 방송해요. <b>방송하는 동안 이 탭을 닫거나 새로고침하지 마세요.</b> 라이브 사이트 안에서 다른 메뉴로 가는 건 괜찮아요. 다른 일은 <b>새 탭·새 창</b>에서 하세요. (폰은 화면 공유가 안 되고 백그라운드에서 멈출 수 있어서 컴퓨터를 권해요)</p>
        <div class="grid2">
          <div>
            <label style="margin:0"><input type="radio" name="bcSrc" value="screen" checked ${on ? 'disabled' : ''} style="width:auto"> 🖥 화면 공유 <span class="muted small">(화면·창·탭 선택)</span></label>
            <label style="margin:0 0 0 22px"><input type="checkbox" id="bcSys" checked ${on ? 'disabled' : ''} style="width:auto"> 컴퓨터 소리도 같이 <span class="muted small">(크롬에서 "소리 공유" 체크)</span></label>
            <label style="margin:6px 0 0"><input type="radio" name="bcSrc" value="cam" ${on ? 'disabled' : ''} style="width:auto"> 🎥 카메라 / <b>OBS 가상 카메라</b></label>
            <select id="bcCam" ${on ? 'disabled' : ''} style="margin-left:22px;width:calc(100% - 22px)"><option value="">기본 카메라</option></select>
          </div>
          <div>
            <label style="margin:0"><input type="checkbox" id="bcMic" checked ${on ? 'disabled' : ''} style="width:auto"> 🎤 마이크</label>
            <select id="bcMicSel" ${on ? 'disabled' : ''} style="margin-left:22px;width:calc(100% - 22px)"><option value="">기본 마이크</option></select>
            <label style="margin:10px 0 0"><input type="checkbox" id="bcRec" checked ${on ? 'disabled' : ''} style="width:auto"> ⏺ 방송하면서 내 컴퓨터에 녹화(.webm)</label>
          </div>
        </div>
        <video id="bcPrev" muted autoplay playsinline style="width:100%;max-width:420px;background:#000;border-radius:10px;margin-top:10px;${on ? '' : 'display:none'}"></video>
        <div class="form-actions">
          ${on ? '<button class="danger-btn" id="bcStop">⏹ 사이트 방송 종료</button>' : '<button class="primary" id="bcStart">▶ 사이트 방송 시작</button><button class="ghost" id="bcDev">🔄 카메라·마이크 목록 새로고침</button>'}
          <span id="bcN" class="muted small">${on ? '시청 0명' : ''}</span>
        </div>
        ${fileLink}
        <details style="margin-top:8px"><summary class="small"><b>이 방식의 한계</b></summary>
          <ul class="small help-steps"><li>학생 화면으로 <b>내 컴퓨터에서 직접</b> 영상을 보내는 방식이라(서버 없음) 동시에 약 <b>20명 안팎</b>까지 안정적이에요. 내 인터넷 업로드 속도가 중요해요 (학생 1명당 약 1Mbps).</li>
          <li>학교 와이파이처럼 막힌 망에서는 연결이 안 될 수 있어요. 그럴 땐 <code>config.js</code> 에 TURN 서버(<code>ICE_SERVERS</code>)를 넣으세요. 학생이 느리면 시청 화면의 <b>화질</b>을 낮추게 하세요.</li><li>되감기는 각 학생 브라우저에 최근 방송이 저장돼서 되는 거예요. 입장하기 <b>전</b> 내용은 되감을 수 없고, 전체는 종료 후 녹화 파일(다시보기)로 보세요.</li>
          <li>다시보기: 종료하면 녹화 파일(.webm)이 내려받아져요. 유튜브 등에 올린 뒤 위 "다시보기 주소"에 넣으면 학생들이 볼 수 있어요.</li></ul></details>`;
      const q = (x) => $(x, $('#bc', v));
      const fillDev = async () => {
        try {
          const dv = await navigator.mediaDevices.enumerateDevices();
          const opt = (k, d, i) => `<option value="${esc(d.deviceId)}">${esc(d.label || `${k} ${i + 1}`)}</option>`;
          q('#bcCam').innerHTML = '<option value="">기본 카메라</option>' + dv.filter((d) => d.kind === 'videoinput').map((d, i) => opt('카메라', d, i)).join('');
          q('#bcMicSel').innerHTML = '<option value="">기본 마이크</option>' + dv.filter((d) => d.kind === 'audioinput').map((d, i) => opt('마이크', d, i)).join('');
        } catch (e) { /* 무시 */ }
      };
      if (!on) fillDev();
      if (q('#bcDev')) q('#bcDev').onclick = async () => {
        try { (await navigator.mediaDevices.getUserMedia({ audio: true, video: true })).getTracks().forEach((t) => t.stop()); } catch (e) { toast('카메라·마이크 사용을 허용해 주세요', true); }
        fillDev();
      };
      if (q('#bcStart')) q('#bcStart').onclick = startBroadcast;
      if (on) { q('#bcStop').onclick = () => bc.stop(); q('#bcPrev').srcObject = bc.stream; }
    };

    async function startBroadcast() {
      if (LIVE) return toast('이미 사이트 방송이 진행 중이에요', true);
      if (!navigator.mediaDevices || !window.RTCPeerConnection) return toast('이 브라우저는 방송을 지원하지 않아요. 최신 크롬을 쓰세요', true);
      const q = (x) => $(x, $('#bc', v));
      const src = q('input[name="bcSrc"]:checked').value;
      const opened = [];
      const atracks = [];
      let vtrack = null;
      try {
        if (src === 'screen') {
          const d = await navigator.mediaDevices.getDisplayMedia({ video: { frameRate: { ideal: 15, max: 30 }, width: { max: 1920 } }, audio: q('#bcSys').checked });
          opened.push(d);
          [vtrack] = d.getVideoTracks();
          if ('contentHint' in vtrack) vtrack.contentHint = 'detail';
          d.getAudioTracks().forEach((t) => atracks.push(t));
        } else {
          const id = q('#bcCam').value;
          const c = await navigator.mediaDevices.getUserMedia({ video: { ...(id ? { deviceId: { exact: id } } : {}), width: { ideal: 1280 }, height: { ideal: 720 }, frameRate: { ideal: 24 } } });
          opened.push(c);
          [vtrack] = c.getVideoTracks();
        }
        if (q('#bcMic').checked) {
          const id = q('#bcMicSel').value;
          const m = await navigator.mediaDevices.getUserMedia({ audio: { ...(id ? { deviceId: { exact: id } } : {}), echoCancellation: true, noiseSuppression: true } });
          opened.push(m);
          m.getAudioTracks().forEach((t) => atracks.push(t));
        }
      } catch (e) {
        opened.forEach((st) => st.getTracks().forEach((t) => t.stop()));
        return toast(e && e.name === 'NotAllowedError' ? '화면·카메라·마이크 사용이 허용되지 않았어요' : '장치를 열지 못했어요: ' + (e.message || e), true);
      }
      let actx = null;
      let atrack = atracks[0] || null;
      if (atracks.length > 1) {
        actx = new (window.AudioContext || window.webkitAudioContext)();
        const dest = actx.createMediaStreamDestination();
        atracks.forEach((t) => actx.createMediaStreamSource(new MediaStream([t])).connect(dest));
        [atrack] = dest.stream.getAudioTracks();
      }
      const stream = new MediaStream([vtrack, ...(atrack ? [atrack] : [])]);
      const recOn = q('#bcRec').checked && window.MediaRecorder;
      const ok = await patchSes({ stream_url: WEBRTC, is_live: true, started_at: ses.started_at || new Date().toISOString(), ended_at: null }, '사이트 방송을 시작했어요. 학생들이 입장할 수 있어요');
      if (!ok) { opened.forEach((st) => st.getTracks().forEach((t) => t.stop())); return; }
      const stopHost = startHost(ses.id, stream, (n, total) => { const el = $('#bcN', v); if (el) el.textContent = `시청 ${n}명 (연결 시도 ${total}명)`; });
      let rec = null;
      const chunks = [];
      if (recOn) {
        try {
          const mime = ['video/webm;codecs=vp8,opus', 'video/webm'].find((m) => MediaRecorder.isTypeSupported(m));
          rec = new MediaRecorder(stream, { ...(mime ? { mimeType: mime } : {}), videoBitsPerSecond: 1500000 });
          rec.ondataavailable = (e) => { if (e.data && e.data.size) chunks.push(e.data); };
          rec.start(5000);
        } catch (e) { rec = null; }
      }
      // 방송 중 화면이 꺼지거나 컴퓨터가 잠들지 않게
      let wl = null;
      const lock = async () => { try { if (navigator.wakeLock && !done) wl = await navigator.wakeLock.request('screen'); } catch (e) { /* 무시 */ } };
      const onVis = () => { if (document.visibilityState === 'visible') lock(); };
      const sid = ses.id;
      const sTitle = ses.title;
      const rpl = ses.replay_url || null;
      let done = false;
      lock();
      document.addEventListener('visibilitychange', onVis);
      const stop = async () => {
        if (done) return;
        done = true;
        document.removeEventListener('visibilitychange', onVis);
        if (wl) { wl.release().catch(() => {}); wl = null; }
        window.onbeforeunload = null;
        stopHost();
        let link = '';
        if (rec && rec.state !== 'inactive') {
          await new Promise((res) => { rec.onstop = res; rec.stop(); });
        }
        if (chunks.length) {
          const blob = new Blob(chunks, { type: 'video/webm' });
          const url = URL.createObjectURL(blob);
          const name = `${(sTitle || 'live').replace(/[\\/:*?"<>|\s]+/g, '_')}_${new Date().toISOString().slice(0, 16).replace(/[:T]/g, '-')}.webm`;
          const a = document.createElement('a');
          a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove();
          link = `<div class="card" style="margin:10px 0 0"><b>⏺ 녹화 파일</b> <span class="muted small">(${(blob.size / 1048576).toFixed(0)}MB · 자동으로 내려받지 않았다면 눌러 주세요)</span><br><a class="primary btnlike" href="${url}" download="${esc(name)}" style="margin-top:6px">💾 ${esc(name)}</a></div>`;
        }
        opened.forEach((st) => st.getTracks().forEach((t) => t.stop()));
        stream.getTracks().forEach((t) => t.stop());
        if (actx) actx.close().catch(() => {});
        LIVE = null;
        // 콘솔을 닫았거나 다른 페이지에 있어도 끝낼 수 있게 화면과 무관하게 직접 저장해요
        await sb.from('live_problems').update({ status: 'closed' }).eq('session_id', sid).eq('status', 'open');
        await sb.from('live_sessions').update({ is_live: false, ended_at: new Date().toISOString(), replay_url: rpl }).eq('id', sid);
        toast('방송을 종료했어요');
        if (liveUi) liveUi(link);
      };
      bc = { sesId: sid, stream, stop };
      LIVE = bc;
      vtrack.addEventListener('ended', stop);
      window.onbeforeunload = () => '방송 중이에요. 나가면 방송이 끊겨요.';
      drawBc();
    }
    // 방송은 다른 페이지로 옮겨 가도 끊기지 않아요 (탭을 닫거나 새로고침하면 끊겨요)
    const ui = async (link = '') => {
      if (tok !== navTok) return;
      bc = LIVE && LIVE.sesId === ses.id ? LIVE : null;
      const { data } = await sb.from('live_sessions').select('*').eq('id', ses.id).maybeSingle();
      if (data) ses = data;
      drawn.cfg = '';
      drawCfg();
      drawBc(link);
      refresh();
    };
    liveUi = ui;
    cleanups.push(() => { if (liveUi === ui) liveUi = null; });
    drawBc();

    /* --- 문제 목록 --- */
    const drawPlist = () => {
      const key = JSON.stringify(probs.map((p) => [p.id, p.title, p.status, p.position]));
      if (drawn.plist === key) return;
      drawn.plist = key;
      $('#plist', v).innerHTML = `
        <div class="live-head"><h2>📝 문제</h2><span class="spacer"></span>
          <button class="ghost" id="pImp">📥 PyNest 문제집에서 가져오기</button><button class="primary" id="pAdd">＋ 문제 추가</button></div>
        ${probs.length ? probs.map((p, i) => `<div class="prow-admin">
          <span class="chip">${i + 1}</span><span class="t"><b>${esc(p.title) || '(제목 없음)'}</b> <span class="badge ${p.status === 'open' ? 'ok' : p.status === 'closed' ? '' : 'warn'}">${PSTAT[p.status]}</span>
            <span class="muted small">${(p.tests || []).length ? `테스트 ${p.tests.length}` : ''} ${(p.answers || []).length ? `정답칸 ${p.answers.length}` : ''}</span></span>
          ${p.status === 'open' ? `<button class="ghost" data-st="${p.id}:closed">⏹ 마감</button>` : `<button class="primary" data-st="${p.id}:open">▶ ${p.status === 'closed' ? '다시 열기' : '문제 열기'}</button>`}
          <button class="icon" data-up="${p.id}" title="위로">↑</button><button class="icon" data-down="${p.id}" title="아래로">↓</button>
          <button class="icon" data-ed="${p.id}" title="수정">✏️</button><button class="icon" data-dl="${p.id}" title="삭제">🗑</button></div>`).join('')
          : '<p class="muted">아직 문제가 없어요. 추가하거나 PyNest 문제집에서 가져오세요.</p>'}`;
      const q = $('#plist', v);
      $('#pAdd', q).onclick = () => openEditor(null);
      $('#pImp', q).onclick = openImport;
      q.querySelectorAll('[data-st]').forEach((b) => (b.onclick = async () => {
        const [id, st] = b.dataset.st.split(':');
        const o = { status: st };
        if (st === 'open') o.opened_at = new Date().toISOString();
        const { error } = await sb.from('live_problems').update(o).eq('id', Number(id));
        if (error) return toast('바꾸지 못했어요', true);
        if (st === 'open') monSel = Number(id);
        toast(st === 'open' ? '문제를 열었어요. 학생 화면에 바로 나와요' : '마감했어요');
        refresh();
      }));
      const swap = async (id, dir) => {
        const i = probs.findIndex((p) => p.id === Number(id));
        const o = probs[i + dir];
        if (!o) return;
        await Promise.all([sb.from('live_problems').update({ position: o.position }).eq('id', probs[i].id), sb.from('live_problems').update({ position: probs[i].position }).eq('id', o.id)]);
        refresh();
      };
      q.querySelectorAll('[data-up]').forEach((b) => (b.onclick = () => swap(b.dataset.up, -1)));
      q.querySelectorAll('[data-down]').forEach((b) => (b.onclick = () => swap(b.dataset.down, 1)));
      q.querySelectorAll('[data-ed]').forEach((b) => (b.onclick = () => openEditor(probs.find((p) => p.id === Number(b.dataset.ed)))));
      q.querySelectorAll('[data-dl]').forEach((b) => (b.onclick = async () => {
        if (!confirm('이 문제와 학생 제출을 삭제할까요?')) return;
        const { error } = await sb.from('live_problems').delete().eq('id', Number(b.dataset.dl));
        if (error) return toast('삭제하지 못했어요', true);
        refresh();
      }));
    };

    const SN = { '코드': '```\n코드\n```\n', '입출력': '```io\n>>> 입력값\n출력값\n```\n', '출력': '```out\n출력 결과\n```\n', '조건 박스': '```box 조건\n○ 조건 하나\n```\n' };
    function openEditor(p) {
      const cur = p || { title: '', body: '', tests: [], answers: [] };
      const m = modal(`<h3>${p ? '문제 수정' : '문제 추가'}</h3>
        <form id="f">
          <label>제목<input type="text" id="eT" value="${esc(cur.title)}" placeholder="예: 문제 1 · 두 수의 합" required></label>
          <label>문제 내용</label>
          <div class="snips">${Object.keys(SN).map((k) => `<button type="button" class="ghost" data-sn="${esc(k)}">${esc(k)}</button>`).join('')}</div>
          <textarea id="eB" class="code" style="min-height:180px" required>${esc(cur.body)}</textarea>
          <label>미리보기</label><div id="eP" class="ex-body prev"></div>
          <label>자동 채점 테스트 (선택)</label>
          <div class="snips"><button type="button" class="ghost" id="eFrom">문제의 입출력 예시 가져오기</button></div>
          <textarea id="eTe" class="code" style="min-height:110px" spellcheck="false" placeholder="---&#10;>>> 5&#10;25&#10;--- 숨김&#10;>>> 7&#10;49">${esc(testsToText(normTests(cur.tests)))}</textarea>
          <p class="muted small" style="margin:2px 0"><b>---</b> 로 테스트를 나누고, <b>&gt;&gt;&gt;</b> 줄은 입력, 나머지는 기대 출력이에요. <b>--- 숨김</b>(학생에게 안 보임), <b>--- 포함</b> · <b>--- 숫자</b> · <b>--- 공백무시</b> 도 쓸 수 있어요.</p>
          <label>정답 칸 (선택) <span class="muted small">— 결과 예측·빈칸·객관식·서술형</span></label>
          <textarea id="eA" class="code" style="min-height:90px" spellcheck="false" placeholder="@ 실행 결과 | t&#10;3 2 8 7&#10;@ 정답 | c&#10;2,3">${esc(answersToText(normAnswers(cur.answers)))}</textarea>
          <p class="muted small" style="margin:2px 0"><b>@ 이름 | 유형</b> 줄 아래가 정답, <b>~ </b> 줄은 다른 정답. 유형: <b>t</b> 글자 그대로 · <b>c</b> 번호 · <b>k</b> 키워드(;로 여러 개) · <b>x</b> 코드 한 줄 · <b>m</b> 서술(선생님 확인)</p>
          <div class="form-actions"><button class="primary">저장</button><button type="button" class="ghost" id="eC">취소</button></div>
        </form>`);
      const q = (s) => $(s, m.el);
      const prev = () => { q('#eP').innerHTML = renderMarkup(q('#eB').value) || '<span class="muted small">(비어 있어요)</span>'; };
      prev();
      q('#eB').oninput = prev;
      q('#eC').onclick = m.close;
      q('#eFrom').onclick = () => { const t = testsFromBody(q('#eB').value); if (!t.length) return toast('본문에서 입출력 예시를 찾지 못했어요', true); q('#eTe').value = testsToText(t); };
      m.el.querySelectorAll('[data-sn]').forEach((b) => (b.onclick = () => {
        const t = q('#eB'); const s0 = t.selectionStart;
        t.value = t.value.slice(0, s0) + (s0 > 0 && t.value[s0 - 1] !== '\n' ? '\n' : '') + SN[b.dataset.sn] + t.value.slice(t.selectionEnd);
        t.focus(); prev();
      }));
      q('#f').onsubmit = async (e) => {
        e.preventDefault();
        const row = { title: q('#eT').value.trim(), body: q('#eB').value.trim(), tests: textToTests(q('#eTe').value), answers: textToAnswers(q('#eA').value) };
        const r = p ? await sb.from('live_problems').update(row).eq('id', p.id)
          : await sb.from('live_problems').insert({ ...row, session_id: ses.id, position: probs.reduce((mx, x) => Math.max(mx, x.position), 0) + 1000 });
        if (r.error) return toast('저장하지 못했어요: ' + r.error.message, true);
        m.close(); toast('저장했어요'); refresh();
      };
    }

    async function openImport() {
      const { data: sets, error } = await sb.from('problem_sets').select('id,title,short_name').order('id');
      if (error || !sets.length) return toast('가져올 PyNest 문제집이 없어요', true);
      const m = modal(`<h3>📥 PyNest 문제집에서 가져오기</h3>
        <label>문제집<select id="iS">${sets.map((s) => `<option value="${s.id}">${esc(s.title)}</option>`).join('')}</select></label>
        <div id="iL" class="muted" style="margin-top:8px">불러오는 중…</div>
        <div class="form-actions"><button class="primary" id="iGo" disabled>선택한 문제 가져오기</button></div>`);
      let exs = [];
      const load = async () => {
        $('#iL', m.el).textContent = '불러오는 중…';
        const { data } = await sb.from('exercises').select('*').eq('set_id', Number($('#iS', m.el).value)).order('position').range(0, 999);
        exs = data || [];
        let n = 0; let e = 0;
        exs.forEach((x) => { x.no = x.difficulty === 'ELITE' ? `E${++e}` : String(++n); });
        $('#iL', m.el).innerHTML = `<div style="max-height:320px;overflow:auto;border:1px solid var(--border);border-radius:10px;padding:6px">${exs.map((x) => {
          const fl = (String(x.body).split('\n').find((l) => l.trim() && !l.startsWith('```')) || '').replace(/[`*]/g, '').slice(0, 60);
          return `<label style="display:flex;gap:8px;align-items:center;padding:3px 4px;margin:0"><input type="checkbox" data-x="${x.id}" style="width:auto"><span class="chip">${x.no}</span><span class="small">${esc(fl)}</span>${(x.tests || []).length || (x.answers || []).length ? ' <span class="chip">⚖️</span>' : ''}</label>`;
        }).join('')}</div>`;
        $('#iGo', m.el).disabled = false;
      };
      $('#iS', m.el).onchange = load;
      load();
      $('#iGo', m.el).onclick = async () => {
        const pick = [...m.el.querySelectorAll('[data-x]:checked')].map((c) => exs.find((x) => x.id === Number(c.dataset.x)));
        if (!pick.length) return toast('가져올 문제를 고르세요', true);
        const setName = (sets.find((s) => s.id === Number($('#iS', m.el).value)) || {}).short_name || '';
        let pos = probs.reduce((mx, x) => Math.max(mx, x.position), 0);
        const rows = pick.map((x) => ({ session_id: ses.id, position: (pos += 1000), title: `${setName} ${x.no}번`.trim(), body: x.body, tests: x.tests || [], answers: x.answers || [] }));
        const { error: er } = await sb.from('live_problems').insert(rows);
        if (er) return toast('가져오지 못했어요: ' + er.message, true);
        m.close(); toast(`${rows.length}문제를 가져왔어요 (초안 상태예요)`); refresh();
      };
    }

    /* --- 실시간 현황 --- */
    const mm = (ms) => `${Math.floor(ms / 60000)}:${String(Math.floor(ms / 1000) % 60).padStart(2, '0')}`;
    const drawMon = () => {
      const mon = $('#mon', v);
      const nonDraft = probs.filter((p) => p.status !== 'draft');
      if (!nonDraft.length) { mon.innerHTML = '<h2>📊 실시간 현황</h2><p class="muted">문제를 열면 학생별 결과가 여기에 실시간으로 보여요.</p>'; return; }
      if (!nonDraft.some((p) => p.id === monSel)) monSel = (nonDraft.filter((p) => p.status === 'open').pop() || nonDraft[nonDraft.length - 1]).id;
      const p = probs.find((x) => x.id === monSel);
      const now = Date.now();
      const online = new Set(pres.filter((r) => now - new Date(r.last_seen).getTime() < 60000).map((r) => r.user_id));
      const mine = subs.filter((s) => s.problem_id === p.id);
      const by = {};
      mine.forEach((s) => { (by[s.user_id] = by[s.user_id] || []).push(s); });
      const okL = []; const badL = [];
      Object.entries(by).forEach(([uid, l]) => {
        l.sort((a, b) => a.created_at.localeCompare(b.created_at));
        const first = l.find((s) => s.ok);
        if (first) okL.push({ uid, l, first }); else badL.push({ uid, l });
      });
      okL.sort((a, b) => a.first.created_at.localeCompare(b.first.created_at));
      badL.sort((a, b) => b.l[b.l.length - 1].created_at.localeCompare(a.l[a.l.length - 1].created_at));
      const base = allStudents ? roster.map((r) => r.id) : [...online];
      const wait = base.filter((uid) => !by[uid]);
      const nm = (uid) => esc(names[uid] || '(알 수 없음)');
      const t0 = p.opened_at ? new Date(p.opened_at).getTime() : null;
      const btn = (uid, right, cls = '') => `<button class="who ${cls}" data-u="${uid}"><span>${nm(uid)}${online.has(uid) ? ' <span class="muted small">●</span>' : ''}</span><span class="muted small">${right}</span></button>`;
      mon.innerHTML = `
        <div class="live-head"><h2>📊 실시간 현황</h2><span class="muted small">4초마다 자동 갱신</span></div>
        <div class="ptabs">${nonDraft.map((x) => `<button data-m="${x.id}" class="${x.id === p.id ? 'on' : ''} ${x.status}">${esc(x.title) || '문제'} <span class="dot ${x.status}"></span></button>`).join('')}</div>
        <div class="mon-stats"><span class="badge">접속 ${online.size}명</span><span class="badge ok">✅ 맞음 ${okL.length}</span><span class="badge bad">❌ 실패 ${badL.length}</span><span class="badge warn">⏳ 아직 ${wait.length}</span>
          <label style="margin:0;display:inline-flex;gap:6px;align-items:center"><input type="checkbox" id="mAll" style="width:auto" ${allStudents ? 'checked' : ''}> 전체 학생 기준</label></div>
        <div class="mon-cols">
          <div class="mon-col ok"><h4>✅ 맞은 사람 (${okL.length})</h4>${okL.map((r, i) => btn(r.uid, `${i + 1}등${t0 ? ' · ' + mm(new Date(r.first.created_at).getTime() - t0) : ''} · ${r.l.length}번`)).join('') || '<span class="muted small">아직 없어요</span>'}</div>
          <div class="mon-col bad"><h4>❌ 풀었지만 못 맞힌 사람 (${badL.length})</h4>${badL.map((r) => { const j = r.l[r.l.length - 1].judge; return btn(r.uid, `${j && j.total ? `${j.passed}/${j.total} · ` : ''}${r.l.length}번`); }).join('') || '<span class="muted small">없어요</span>'}</div>
          <div class="mon-col wait"><h4>⏳ 아직 안 푼 사람 (${wait.length})</h4>${wait.map((uid) => btn(uid, '')).join('') || '<span class="muted small">없어요</span>'}</div>
        </div>
        <p class="muted small" style="margin-bottom:0">● 는 지금 접속 중이에요. 이름을 누르면 제출한 코드를 볼 수 있어요.</p>`;
      mon.querySelectorAll('[data-m]').forEach((b) => (b.onclick = () => { monSel = Number(b.dataset.m); drawMon(); }));
      $('#mAll', mon).onchange = (e) => { allStudents = e.target.checked; drawMon(); };
      mon.querySelectorAll('[data-u]').forEach((b) => (b.onclick = () => showSubs(b.dataset.u, p)));
    };

    async function showSubs(uid, p) {
      const { data } = await sb.from('live_submissions').select('*').eq('problem_id', p.id).eq('user_id', uid).order('id', { ascending: false });
      modal(`<h3>${esc(names[uid] || '')} · ${esc(p.title)}</h3>${(data || []).length ? data.map((s, i) => `<details ${i === 0 ? 'open' : ''}><summary>${fmt(s.created_at)} ${judgeBadge(s.judge)}${s.ok ? ' ✅' : ''}</summary><pre><code>${esc(s.code)}</code></pre></details>`).join('') : '<p class="muted">제출이 없어요.</p>'}`);
    }

    let busy = false;
    async function refresh() {
      if (tok !== navTok || busy) return;
      busy = true;
      try {
        const [sr, pr, subr, prer] = await Promise.all([
          sb.from('live_sessions').select('*').eq('id', ses.id).maybeSingle(),
          sb.from('live_problems').select('*').eq('session_id', ses.id).order('position'),
          fetchAll((a, b) => sb.from('live_submissions').select('id,problem_id,user_id,ok,judge,created_at').eq('session_id', ses.id).order('id').range(a, b)),
          sb.from('live_presence').select('*').eq('session_id', ses.id),
        ]);
        if (sr.data) ses = sr.data;
        if (pr.data) probs = pr.data;
        if (tok !== navTok) { busy = false; return; }
        subs = subr;
        pres = prer.data || [];
        if (!roster.length) {
          const { data } = await sb.from('profiles').select('id,username,role,status').eq('status', 'approved').neq('role', 'admin').order('username');
          if (tok !== navTok) { busy = false; return; }
          roster = data || [];
          roster.forEach((r) => { names[r.id] = r.username; });
        }
        if (tok !== navTok) { busy = false; return; }
        drawCfg(); drawPlist(); drawMon();
      } catch (e) { console.error(e); }
      busy = false;
    }
    refresh();
    every(refresh, 4000);
  }

  /* ---------- 시작 ---------- */
  async function boot() {
    const { data: { session } } = await sb.auth.getSession();
    if (!session) { me = null; return renderAuth(); }
    const { data, error } = await sb.from('profiles').select('*').eq('id', session.user.id).maybeSingle();
    if (error || !data) { await sb.auth.signOut(); return renderAuth(); }
    me = data;
    me.staff = null;
    if (me.status === 'approved' && me.role !== 'admin') {
      try { const { data: r, error: re } = await sb.rpc('staff_role'); me.staff = re || !r ? null : String(r); } catch (e) { me.staff = null; }
    }
    if (me.status === 'pending') return renderStatus(true);
    if (me.status === 'rejected') return renderStatus(false);
    renderShell();
    route();
  }
  sb.auth.onAuthStateChange((ev) => { if (ev === 'SIGNED_OUT') { me = null; renderAuth(); } });
  window.addEventListener('hashchange', route);
  boot();
})();
