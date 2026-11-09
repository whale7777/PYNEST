/* 당겨서 새로고침 — 맨 위에서 아래로 끌어당기면 동그라미가 나오고, 놓으면 새로고침해요 (터치 화면 전용) */
(function () {
  if (window.__pnPtr) return; window.__pnPtr = 1;
  if (!('ontouchstart' in window) && !(navigator.maxTouchPoints > 0)) return;
  // 앱(APK)·홈 화면에 설치한 화면에서만 켜요. 일반 브라우저는 자체 당겨서 새로고침이 있어요.
  var inApp = /PyNestApp/.test(navigator.userAgent) || (window.matchMedia && matchMedia('(display-mode: standalone)').matches) || navigator.standalone === true;
  if (!inApp) return;
  var TH = 64, MAXP = 96;
  var st = document.createElement('style');
  st.textContent = '.ptr{position:fixed;left:50%;top:calc(env(safe-area-inset-top,0px) + 6px);width:40px;height:40px;margin-left:-20px;border-radius:50%;' +
    'background:var(--card,var(--bg,#fff));color:var(--primary,var(--blue,#3b6cf6));box-shadow:0 4px 16px rgba(20,27,45,.22);border:1px solid var(--border,var(--line,rgba(0,0,0,.08)));' +
    'display:flex;align-items:center;justify-content:center;z-index:99999;pointer-events:none;opacity:0;transform:translateY(-60px)}' +
    '.ptr svg{width:22px;height:22px}.ptr.go svg{animation:ptrspin .7s linear infinite}.ptr.back{transition:transform .22s,opacity .22s}' +
    '@keyframes ptrspin{to{transform:rotate(360deg)}}@media (prefers-reduced-motion:reduce){.ptr.go svg{animation-duration:1.6s}}';
  document.head.appendChild(st);
  var el = document.createElement('div'); el.className = 'ptr'; el.setAttribute('aria-hidden', 'true');
  el.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M20 12a8 8 0 1 1-2.6-5.9"/><path d="M20 4v5h-5" stroke-linejoin="round"/></svg>';
  function add() { document.body.appendChild(el); }
  if (document.body) add(); else document.addEventListener('DOMContentLoaded', add);

  var y0 = 0, pull = 0, on = false, busy = false, x0 = 0, intent = 0;
  var BLOCK = 'textarea,input,select,canvas,.lab-win,.modal,[data-noptr],[contenteditable="true"],.CodeMirror,iframe';
  function atTop() { return (window.scrollY || document.documentElement.scrollTop || 0) <= 0; }
  function scrolledInner(t) {
    for (var n = t; n && n !== document.body && n.nodeType === 1; n = n.parentElement) {
      var cs = getComputedStyle(n);
      if ((cs.overflowY === 'auto' || cs.overflowY === 'scroll') && n.scrollHeight > n.clientHeight && n.scrollTop > 0) return true;
    }
    return false;
  }
  function show(p) {
    var d = Math.min(MAXP, p * 0.55);
    el.style.opacity = String(Math.min(1, p / 30));
    el.style.transform = 'translateY(' + (d - 50) + 'px) rotate(' + Math.round(p * 3) + 'deg)';
  }
  function hide() { el.classList.add('back'); el.style.opacity = '0'; el.style.transform = 'translateY(-60px)'; setTimeout(function () { el.classList.remove('back', 'go'); }, 240); }

  document.addEventListener('touchstart', function (e) {
    on = false; pull = 0;
    if (busy || e.touches.length !== 1) return;
    if (document.body.classList.contains('exam-on')) return;
    var t = e.target;
    if (t.closest && t.closest(BLOCK)) return;
    if (!atTop() || scrolledInner(t)) return;
    y0 = e.touches[0].clientY; x0 = e.touches[0].clientX; on = true; intent = 0;
  }, { passive: true });

  document.addEventListener('touchmove', function (e) {
    if (!on || busy) return;
    var dy = e.touches[0].clientY - y0, dx = Math.abs(e.touches[0].clientX - x0);
    // 처음 움직임이 위쪽이거나 옆이면 일반 스크롤이에요. 아래로 확실히 끌 때만 당기기로 봐요.
    if (intent === 0) {
      if (dy < -3 || dx > 12) { on = false; return; }
      if (dy > 12 && dy > dx * 1.5 && atTop()) intent = 1; else return;
    }
    if (!atTop() || dy <= 0) { on = false; if (pull) { pull = 0; hide(); } return; }
    pull = dy - 12;
    show(pull);
  }, { passive: true });

  function end() {
    if (!on) return; on = false;
    if (intent === 1 && pull >= TH) {
      busy = true; el.classList.add('go'); el.classList.add('back'); el.style.opacity = '1'; el.style.transform = 'translateY(' + (TH * 0.55 - 6) + 'px)';
      setTimeout(function () { location.reload(); }, 350);
      setTimeout(function () { busy = false; hide(); }, 6000);
    } else if (pull) hide();
    pull = 0;
  }
  document.addEventListener('touchend', end, { passive: true });
  document.addEventListener('touchcancel', function () { on = false; if (pull) hide(); pull = 0; }, { passive: true });
})();
