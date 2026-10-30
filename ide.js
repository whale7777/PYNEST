/* PyNest 코드 입력창 도우미 — 가벼운 IDE 기능 (외부 라이브러리 없이 textarea 위에서 동작해요)
 *  · 괄호/따옴표 자동 닫기 ( ) [ ] { } ' "  — 닫는 글자를 치면 건너뛰고, 지울 때는 한 쌍을 같이 지워요
 *  · 줄바꿈: 콜론(:) 뒤면 들여쓰기 +4 · return/pass/break/continue/raise 뒤면 -4 · 괄호 사이면 한 줄 비우고 닫기
 *  · Tab / Shift+Tab 으로 들여쓰기/내어쓰기(여러 줄 선택도 OK) · 앞쪽 공백에서 Backspace 는 4칸씩
 *  · Ctrl(⌘)+/ 로 주석 켜기/끄기
 *  · 들여쓰기 4칸마다 연한 세로줄 (VS Code 처럼 글자 앞 공백에만)
 *  사용: PYIDE.attach(textarea)
 */
(function () {
  'use strict';
  const IND = 4;
  const SP = ' '.repeat(IND);
  const PAIRS = { '(': ')', '[': ']', '{': '}', '"': '"', "'": "'" };
  const CLOSE = { ')': 1, ']': 1, '}': 1, '"': 1, "'": 1 };
  const isQuote = (c) => c === '"' || c === "'";
  const isWord = (c) => !!c && /[A-Za-z0-9_À-￿]/.test(c);

  function attach(ta) {
    if (!ta || ta._ide) return;
    ta._ide = true;
    ta.setAttribute('wrap', 'off');
    ta.setAttribute('spellcheck', 'false');
    ta.setAttribute('autocomplete', 'off');
    ta.setAttribute('autocorrect', 'off');
    ta.setAttribute('autocapitalize', 'off');

    /* ----- 들여쓰기 줄(뒤쪽 그림) ----- */
    const wrap = document.createElement('div');
    wrap.className = 'ide';
    const back = document.createElement('pre');
    back.className = 'ide-back';
    back.setAttribute('aria-hidden', 'true');
    ta.parentNode.insertBefore(wrap, ta);
    wrap.appendChild(back);
    wrap.appendChild(ta);
    ta.classList.add('ide-ta');

    let raf = 0;
    const paint = () => {
      raf = 0;
      const lines = ta.value.split('\n');
      let html = '';
      for (let i = 0; i < lines.length; i += 1) {
        const m = /^ +/.exec(lines[i]);
        if (m && m[0].length >= 1) html += '<i style="width:' + m[0].length + 'ch"></i>';
        html += '\n';
      }
      back.innerHTML = html;
      back.scrollTop = ta.scrollTop;
      back.scrollLeft = ta.scrollLeft;
    };
    const later = () => { if (!raf) raf = requestAnimationFrame(paint); };
    ta.addEventListener('input', later);
    ta.addEventListener('scroll', () => { back.scrollTop = ta.scrollTop; back.scrollLeft = ta.scrollLeft; });
    if (window.ResizeObserver) new ResizeObserver(later).observe(ta);
    // 값이 코드로 바뀌는 경우(불러오기 등)도 따라가요
    const desc = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value');
    if (desc && desc.set) {
      Object.defineProperty(ta, 'value', { configurable: true, get() { return desc.get.call(this); }, set(v) { desc.set.call(this, v); later(); } });
    }
    paint();

    /* ----- 편집 도우미 ----- */
    // 되돌리기(Ctrl+Z)가 되도록 브라우저 편집 명령을 써요
    let busy = false; // 내가 넣는 글자가 다시 이 처리기를 부르지 않게
    const put = (text) => {
      ta.focus();
      busy = true;
      let ok = false;
      try { ok = text === '' ? document.execCommand('delete') : document.execCommand('insertText', false, text); } catch (e) { ok = false; }
      busy = false;
      if (!ok) {
        const s = ta.selectionStart;
        ta.setRangeText(text, s, ta.selectionEnd, 'end');
        ta.dispatchEvent(new Event('input', { bubbles: true }));
      }
    };
    const lineStartOf = (v, pos) => v.lastIndexOf('\n', pos - 1) + 1;
    const lineEndOf = (v, pos) => { const i = v.indexOf('\n', pos); return i < 0 ? v.length : i; };
    const stripComment = (s) => s.replace(/\s*#.*$/, '');
    const inString = (s, quote) => { // 이 줄 앞부분에서 quote 가 "열린 채" 인지(홀수 개) 확인
      let n = 0;
      for (let i = 0; i < s.length; i += 1) {
        if (s[i] === '\\') { i += 1; continue; }
        if (s[i] === quote) n += 1;
      }
      return n % 2 === 1;
    };

    ta.addEventListener('beforeinput', (e) => {
      if (busy || e.isComposing || ta.readOnly) return;
      const v = ta.value;
      const a = ta.selectionStart;
      const b = ta.selectionEnd;
      const t = e.inputType;

      /* 글자 입력: 괄호/따옴표 */
      if (t === 'insertText' && e.data && e.data.length === 1) {
        const ch = e.data;
        const next = v[b];
        if (a === b && CLOSE[ch] && next === ch) { // 이미 닫는 글자가 있으면 건너뛰기
          e.preventDefault();
          ta.setSelectionRange(a + 1, a + 1);
          return;
        }
        if (PAIRS[ch]) {
          if (a !== b) { // 선택한 글자를 감싸기
            e.preventDefault();
            const sel = v.slice(a, b);
            put(ch + sel + PAIRS[ch]);
            ta.setSelectionRange(a + 1, a + 1 + sel.length);
            return;
          }
          const prev = v[a - 1];
          const lineBefore = v.slice(lineStartOf(v, a), a);
          const okNext = next === undefined || /[\s)\]};:,]/.test(next);
          if (!okNext) return;
          if (isQuote(ch)) {
            if (isWord(prev) || prev === ch || inString(lineBefore, ch)) return; // 글자 뒤(it's)·세 번째 따옴표·닫는 따옴표
          }
          e.preventDefault();
          put(ch + PAIRS[ch]);
          ta.setSelectionRange(a + 1, a + 1);
        }
        return;
      }

      /* 줄바꿈: 자동 들여쓰기 */
      if (t === 'insertLineBreak' || t === 'insertParagraph') {
        e.preventDefault();
        const ls = lineStartOf(v, a);
        const before = v.slice(ls, a);
        const indent = /^ */.exec(before)[0].length;
        const code = stripComment(before).replace(/\s+$/, '');
        const last = code.slice(-1);
        const nextCh = v[b];
        let ind = indent;
        if (last === ':') ind = indent + IND;
        else if (/[([{]$/.test(code)) ind = indent + IND;
        else if (/^\s*(return|pass|break|continue|raise)\b/.test(before) && a === b && v.slice(a, lineEndOf(v, a)).trim() === '' && indent >= IND) ind = indent - IND;
        const pad = ' '.repeat(ind);
        if (/[([{]$/.test(code) && nextCh && PAIRS[code.slice(-1)] === nextCh && a === b) {
          // (|)  →  줄을 비우고 닫는 괄호를 아래로
          put('\n' + pad + '\n' + ' '.repeat(indent));
          const p = a + 1 + pad.length;
          ta.setSelectionRange(p, p);
        } else {
          put('\n' + pad);
        }
        return;
      }

      /* Backspace: 한 쌍 지우기 · 앞쪽 공백은 4칸씩 */
      if (t === 'deleteContentBackward' && a === b && a > 0) {
        const prev = v[a - 1];
        const next = v[a];
        if (PAIRS[prev] && PAIRS[prev] === next && !(isQuote(prev) && isWord(v[a - 2]))) {
          e.preventDefault();
          ta.setSelectionRange(a - 1, a + 1);
          put('');
          return;
        }
        const ls = lineStartOf(v, a);
        const before = v.slice(ls, a);
        if (before.length > 0 && /^ +$/.test(before)) {
          const n = before.length % IND === 0 ? IND : before.length % IND;
          if (n > 1) {
            e.preventDefault();
            ta.setSelectionRange(a - n, a);
            put('');
          }
        }
      }
    });

    ta.addEventListener('keydown', (e) => {
      if (e.isComposing || ta.readOnly) return;
      const v = ta.value;
      const a = ta.selectionStart;
      const b = ta.selectionEnd;

      /* Tab / Shift+Tab */
      if (e.key === 'Tab' && !e.ctrlKey && !e.metaKey && !e.altKey) {
        e.preventDefault();
        const multi = v.slice(a, b).includes('\n');
        if (!e.shiftKey && !multi) { put(a === b ? SP.slice(0, IND - ((a - lineStartOf(v, a)) % IND)) : SP); return; }
        const ls = lineStartOf(v, a);
        const le = lineEndOf(v, b > a && v[b - 1] === '\n' ? b - 1 : b);
        const block = v.slice(ls, le);
        const out = block.split('\n').map((ln) => {
          if (!e.shiftKey) return ln.length ? SP + ln : ln;
          const m = /^ {1,4}/.exec(ln);
          return m ? ln.slice(m[0].length) : ln;
        }).join('\n');
        ta.setSelectionRange(ls, le);
        put(out);
        ta.setSelectionRange(ls, ls + out.length);
        return;
      }

      /* Ctrl(⌘)+/ : 주석 */
      if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        const ls = lineStartOf(v, a);
        const le = lineEndOf(v, b > a && v[b - 1] === '\n' ? b - 1 : b);
        const lines = v.slice(ls, le).split('\n');
        const allC = lines.filter((l) => l.trim()).every((l) => /^\s*#/.test(l));
        const out = lines.map((l) => {
          if (!l.trim()) return l;
          if (allC) return l.replace(/^(\s*)# ?/, '$1');
          const ind = /^ */.exec(l)[0];
          return ind + '# ' + l.slice(ind.length);
        }).join('\n');
        ta.setSelectionRange(ls, le);
        put(out);
        ta.setSelectionRange(ls, ls + out.length);
      }
    });
  }

  window.PYIDE = { attach };
})();
