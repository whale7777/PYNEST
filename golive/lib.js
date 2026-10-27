'use strict';
/* 자동 생성 파일: PyNest app.js 의 채점·서식 엔진을 그대로 가져온 것이에요. 직접 고치지 마세요. */
(() => {
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const fmt = (d) => new Date(d).toLocaleString('ko-KR', { year: '2-digit', month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' });
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
  // 선생님이 미리 만들어 둔 공용 함수 (v370_prelude.sql). rows 는 이미 범위를 거른 목록이에요.
  let PRE_JSON = '[]';
  const setPre = (rows) => { PRE_JSON = JSON.stringify((rows || []).filter((x) => x.enabled !== false && String(x.code || '').trim()).map((x) => ({ n: x.name || '', c: x.code }))); };

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

  window.PYJ = { esc, fmt, inline, parseBlocks, renderMarkup, runOnce, gradeAll, cmpOut, renderRun, renderGrade, judgeBadge, summarize,
    setPre, normTests, testsToText, textToTests, testsFromBody, normAnswers, answersToText, textToAnswers, gradeParts, packSubmission, unpackSubmission, checkPart };
})();
