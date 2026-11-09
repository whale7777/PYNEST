/* PyNest · 파이썬 자유 연구소 (연구 탭)
 *  - 브라우저 안에서 파이썬(Pyodide)을 자유롭게 실행
 *  - PyPI 패키지 검색 → 설치(micropip) → import
 *  사용: window.PYLAB.page() → [html, bind]
 */
(function () {
  'use strict';
  const PY_URL = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/';
  const KEY_CODE = 'pn_lab_code';
  const KEY_STDIN = 'pn_lab_stdin';
  const OUT_MAX = 200000;

  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const lsGet = (k, d) => { try { const v = localStorage.getItem(k); return v == null ? d : v; } catch (e) { return d; } };
  const lsSet = (k, v) => { try { localStorage.setItem(k, v); } catch (e) { /* 무시 */ } };

  /* ---------- 파이썬 쪽 도우미 ---------- */
  const PY_BOOT = [
    'import sys, io, json, builtins, ast, importlib.util, importlib.metadata, base64, os, warnings',
    'os.environ["MPLBACKEND"] = "AGG"',
    'warnings.filterwarnings("ignore", message=".*non-interactive.*")',
    'def lab_missing(code):',
    '    try:',
    '        tree = ast.parse(code)',
    '    except SyntaxError:',
    '        return "[]"',
    '    names = set()',
    '    for n in ast.walk(tree):',
    '        if isinstance(n, ast.Import):',
    '            for a in n.names: names.add(a.name.split(".")[0])',
    '        elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:',
    '            names.add(n.module.split(".")[0])',
    '    miss = []',
    '    for m in sorted(names):',
    '        try:',
    '            if importlib.util.find_spec(m) is None: miss.append(m)',
    '        except Exception:',
    '            miss.append(m)',
    '    return json.dumps(miss)',
    'def lab_setin(inp):',
    '    sys.stdin = io.StringIO(inp)',
    '    def _inp(prompt=""):',
    '        if prompt: sys.stdout.write(str(prompt))',
    '        s = sys.stdin.readline()',
    '        if s == "": raise EOFError("EOF when reading a line (아래 \'입력\' 칸이 비어 있어요)")',
    '        s = s.rstrip("\\n")',
    '        sys.stdout.write(s + "\\n")',
    '        return s',
    '    builtins.input = _inp',
    'def lab_figs():',
    '    out = []',
    '    if "matplotlib.pyplot" in sys.modules:',
    '        plt = sys.modules["matplotlib.pyplot"]',
    '        for n in plt.get_fignums():',
    '            b = io.BytesIO()',
    '            plt.figure(n).savefig(b, format="png", dpi=110, bbox_inches="tight")',
    '            out.append(base64.b64encode(b.getvalue()).decode())',
    '        plt.close("all")',
    '    return json.dumps(out)',
    'def lab_tops(dist):',
    '    tops = []',
    '    try:',
    '        d = importlib.metadata.distribution(dist)',
    '        t = d.read_text("top_level.txt")',
    '        if t:',
    '            tops = [x.strip() for x in t.split() if x.strip() and not x.startswith("_")]',
    '        else:',
    '            for f in (d.files or []):',
    '                p = str(f).split("/")[0]',
    '                if p.endswith(".py"): p = p[:-3]',
    '                if p and not p.endswith((".dist-info", ".data", ".libs")) and not p.startswith("_") and p not in tops: tops.append(p)',
    '    except Exception:',
    '        pass',
    '    return json.dumps(tops[:6])',
  ].join('\n');

  /* ---------- 워커 (별도 스레드: 화면이 안 멈춰요) ---------- */
  function workerMain() {
    /* global PY_URL, PY_BOOT, importScripts, loadPyodide */
    importScripts(PY_URL + 'pyodide.js');
    let py = null;
    const say = (m) => postMessage(m);
    const ALIAS = { PIL: 'pillow', cv2: 'opencv-python', sklearn: 'scikit-learn', yaml: 'pyyaml', bs4: 'beautifulsoup4', dateutil: 'python-dateutil', slugify: 'python-slugify', skimage: 'scikit-image', Crypto: 'pycryptodome', attr: 'attrs', serial: 'pyserial', docx: 'python-docx', dotenv: 'python-dotenv', jwt: 'pyjwt' };
    (async () => {
      try {
        py = await loadPyodide({ indexURL: PY_URL });
        await py.loadPackage('micropip');
        py.runPython(PY_BOOT, { filename: '<lab>' });
        say({ t: 'ready', version: py.version });
      } catch (e) { say({ t: 'fatal', s: String(e) }); }
    })();

    const tops = (dist) => { try { return JSON.parse(py.globals.get('lab_tops')(dist)); } catch (e) { return []; } };

    async function install(name, quiet) {
      const mp = py.pyimport('micropip');
      if (!quiet) say({ t: 'log', s: '📦 ' + name + ' 설치 중…' });
      try {
        await mp.install(name);
        const t = tops(name);
        say({ t: 'pkg', name, tops: t, ok: true });
        if (!quiet) say({ t: 'log', s: '✅ ' + name + ' 설치 완료' + (t.length ? ' → import ' + t.join(', ') : '') });
        return true;
      } catch (e) {
        let m = String(e.message || e);
        m = m.split('\n').filter(Boolean).slice(-1)[0] || m;
        say({ t: 'pkg', name, ok: false, err: m });
        say({ t: 'log', s: '⚠️ ' + name + ' 설치 못 했어요: ' + m, bad: true });
        return false;
      }
    }

    function fmtErr(e) {
      const raw = String(e && e.message ? e.message : e);
      let i = raw.indexOf('File "<exec>"');
      if (i < 0) i = raw.indexOf('File "/lib/');
      const body = (i >= 0 ? 'Traceback (most recent call last):\n  ' + raw.slice(i) : raw).replace(/ {2}File "<lab>".*\n(?: {4}.*\n)*/g, '').replace(/File "<exec>"/g, 'File "main.py"');
      return body.trim();
    }

    onmessage = async (ev) => {
      const d = ev.data;
      if (!py) { say({ t: 'done', id: d.id, err: '아직 파이썬을 불러오는 중이에요. 잠깐만요!' }); return; }
      if (d.t === 'install') {
        const ok = await install(d.name);
        say({ t: 'installed', id: d.id, ok, name: d.name });
        return;
      }
      if (d.t !== 'run') return;
      const t0 = Date.now();
      let err = null, figs = [];
      try {
        const dO = new TextDecoder(), dE = new TextDecoder();
        py.setStdout({ write: (b) => { say({ t: 'out', s: dO.decode(b, { stream: true }) }); return b.length; } });
        py.setStderr({ write: (b) => { say({ t: 'out', s: dE.decode(b, { stream: true }), bad: true }); return b.length; } });
        // 1) 파이오다이드 기본 제공 패키지 (numpy, pandas, matplotlib …)
        try { await py.loadPackagesFromImports(d.code, { messageCallback: () => {}, errorCallback: () => {} }); } catch (e) { /* 아래에서 다시 확인 */ }
        // 2) 그래도 없는 것은 PyPI 에서 (순수 파이썬 패키지만 가능)
        const miss = JSON.parse(py.globals.get('lab_missing')(d.code));
        for (const m of miss) await install(ALIAS[m] || m);
        // 3) 실행
        py.globals.get('lab_setin')(d.stdin || '');
        const ns = py.toPy({ __name__: '__main__' });
        try { await py.runPythonAsync(d.code, { globals: ns }); }
        finally { ns.destroy(); }
      } catch (e) {
        const m = String(e && e.message ? e.message : e);
        if (!/SystemExit/.test(m)) err = fmtErr(e);
      }
      try { figs = JSON.parse(py.globals.get('lab_figs')()); } catch (e) { /* 그림 없음 */ }
      say({ t: 'done', id: d.id, err, figs, ms: Date.now() - t0 });
    };
  }
  const WORKER_SRC = 'const PY_URL=' + JSON.stringify(PY_URL) + ';\nconst PY_BOOT=' + JSON.stringify(PY_BOOT) + ';\n(' + workerMain.toString() + ')();';

  /* ---------- 워커 관리 ---------- */
  let W = null;          // {w, ready:Promise}
  let listener = null;   // 지금 화면이 듣는 함수
  const installed = new Map(); // 설치한 패키지 → import 이름들
  let seq = 0;

  function startWorker() {
    if (W) return W.ready;
    const w = new Worker(URL.createObjectURL(new Blob([WORKER_SRC], { type: 'text/javascript' })));
    const ready = new Promise((res, rej) => {
      const to = setTimeout(() => rej(new Error('파이썬을 불러오는 데 너무 오래 걸려요. 인터넷을 확인해 주세요.')), 120000);
      w.addEventListener('message', (ev) => {
        const d = ev.data;
        if (d.t === 'ready') { clearTimeout(to); res(w); } else if (d.t === 'fatal') { clearTimeout(to); rej(new Error(d.s)); }
      });
      w.addEventListener('error', () => { clearTimeout(to); rej(new Error('실행 도구 오류')); });
    });
    w.addEventListener('message', (ev) => {
      const d = ev.data;
      if (d.t === 'pkg' && d.ok) installed.set(d.name, d.tops || []);
      if (listener) listener(d);
    });
    W = { w, ready };
    ready.catch(() => { if (W && W.w === w) { w.terminate(); W = null; } });
    return ready;
  }
  function killWorker() {
    if (W) { W.w.terminate(); W = null; }
    installed.clear();
  }

  /* ---------- PyPI 검색 ---------- */
  // PyPI 의 검색 페이지는 브라우저에서 바로 열 수 없어서, ① 파이오다이드 기본 패키지 ② 추천 목록 ③ PyPI 정확한 이름 조회 를 합쳐서 보여줘요.
  const CURATED = [
    ['rich', '터미널을 알록달록 예쁘게 (표·진행바·색 글씨)'], ['tabulate', '표를 깔끔하게 출력'], ['prettytable', '표 만들기'],
    ['colorama', '색깔 글씨'], ['termcolor', '색깔 글씨 (간단)'], ['tqdm', '진행 막대'], ['pyfiglet', '글씨를 큰 아스키 아트로'], ['art', '아스키 아트 모음'], ['cowsay', '말하는 소 😄'],
    ['python-dateutil', '날짜 계산·파싱'], ['arrow', '쉬운 날짜·시간'], ['pendulum', '날짜·시간 라이브러리'], ['pytz', '시간대(타임존)'], ['humanize', '"3분 전" 같은 사람 말투 변환'],
    ['faker', '가짜 이름·주소·글 만들기'], ['emoji', '이모지 변환'], ['qrcode', 'QR 코드 만들기'], ['pypinyin', '한자→병음'], ['jamo', '한글 자모 분리·합치기'], ['unidecode', '글자를 영문으로'], ['python-slugify', '문자열을 URL 주소로'],
    ['sympy', '기호 수학 (방정식·미적분)'], ['mpmath', '아주 정밀한 계산'], ['networkx', '그래프(점·선) 알고리즘'], ['sortedcontainers', '정렬 유지되는 리스트·딕셔너리'], ['more-itertools', 'itertools 확장'], ['toolz', '함수형 도구'], ['bidict', '양방향 딕셔너리'],
    ['numpy', '숫자 배열 계산'], ['pandas', '표 데이터 분석'], ['matplotlib', '그래프 그리기'], ['scipy', '과학 계산'], ['scikit-learn', '머신러닝'], ['pillow', '이미지 다루기'],
    ['beautifulsoup4', 'HTML 읽기'], ['jinja2', '템플릿 엔진'], ['markdown', '마크다운 → HTML'], ['pyyaml', 'YAML 읽기·쓰기'], ['toml', 'TOML 읽기·쓰기'], ['pygments', '코드 색칠'], ['click', '명령줄 도구 만들기'],
    ['rapidfuzz', '비슷한 글자 찾기 (빠름)'], ['fuzzywuzzy', '비슷한 글자 찾기'], ['parse', 'format 거꾸로 (글에서 값 뽑기)'], ['attrs', '클래스 간단하게'], ['pyparsing', '문법 해석기 만들기'], ['textblob', '간단한 글 분석'], ['cryptography', '암호화'],
  ].map(([name, desc]) => ({ name, desc, src: '추천' }));

  let LOCK = null; // 파이오다이드 기본 패키지
  async function loadLock() {
    if (LOCK) return LOCK;
    try {
      const r = await fetch(PY_URL + 'pyodide-lock.json');
      const j = await r.json();
      LOCK = Object.values(j.packages || {}).filter((p) => p && p.name && !p.shared_library && p.package_type !== 'cpython_module').map((p) => ({ name: p.name, version: p.version, imports: p.imports || [], src: '기본' }));
    } catch (e) { LOCK = []; }
    return LOCK;
  }
  const norm = (s) => String(s).toLowerCase().replace(/[-_.]+/g, '-').trim();

  async function pypiInfo(name) {
    try {
      const r = await fetch('https://pypi.org/pypi/' + encodeURIComponent(name) + '/json');
      if (!r.ok) return null;
      const j = await r.json();
      const i = j.info || {};
      const urls = j.urls || [];
      const wheels = urls.filter((u) => u.packagetype === 'bdist_wheel');
      const pure = wheels.some((u) => /-py[23]?(\.py[23])*-none-any\.whl$/.test(u.filename) || /-none-any\.whl$/.test(u.filename));
      return { name: i.name || name, version: i.version, desc: i.summary || '', home: i.project_url || i.home_page || ('https://pypi.org/project/' + name + '/'), pure, hasWheel: wheels.length > 0, requires: i.requires_python || '' };
    } catch (e) { return null; }
  }

  async function search(q) {
    q = q.trim().replace(/^(python\s+-m\s+)?pip\s+install\s+/i, '').replace(/^import\s+/i, '').trim();
    if (!q) return { list: [], exact: null };
    const n = norm(q);
    const lock = await loadLock();
    const hit = (p) => norm(p.name).includes(n) || (p.imports || []).some((m) => m.toLowerCase().includes(n)) || (p.desc || '').toLowerCase().includes(q.toLowerCase());
    const seen = new Set();
    const list = [];
    for (const p of CURATED.concat(lock)) {
      const k = norm(p.name);
      if (seen.has(k) || !hit(p)) continue;
      seen.add(k);
      const c = CURATED.find((x) => norm(x.name) === k);
      list.push({ name: p.name, version: p.version || '', desc: (c && c.desc) || '', builtin: lock.some((x) => norm(x.name) === k), imports: p.imports || [] });
    }
    list.sort((a, b) => (norm(a.name) === n ? -1 : norm(b.name) === n ? 1 : (norm(a.name).startsWith(n) ? -1 : 0) - (norm(b.name).startsWith(n) ? -1 : 0)));
    const exact = /^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(q.replace(/\s+/g, '-')) ? await pypiInfo(q.replace(/\s+/g, '-')) : null;
    return { list: list.slice(0, 30), exact };
  }

  /* ---------- 예제 ---------- */
  const EXAMPLES = [
    ['👋 안녕 파이썬', 'for i in range(1, 4):\n    print(i, "번째 인사 🐍")\n\nprint(sum(range(1, 101)))\n'],
    ['⌨️ input() 쓰기', 'name = input("이름이 뭐야? ")\nage = int(input("몇 살? "))\nprint(f"{name}은(는) 내년에 {age + 1}살이네!")\n', '철수\n15'],
    ['📈 그래프 (numpy + matplotlib)', 'import numpy as np\nimport matplotlib.pyplot as plt\n\nx = np.linspace(0, 2 * np.pi, 200)\nplt.plot(x, np.sin(x), label="sin")\nplt.plot(x, np.cos(x), label="cos")\nplt.legend()\nplt.title("sin & cos")\nplt.show()\n'],
    ['🎨 rich 로 예쁜 표 (PyPI 설치)', 'from rich.console import Console\nfrom rich.table import Table\n\nt = Table(title="오늘의 연구")\nt.add_column("패키지")\nt.add_column("하는 일")\nt.add_row("rich", "터미널 꾸미기")\nt.add_row("sympy", "기호 수학")\nConsole(force_terminal=False, width=50).print(t)\n'],
    ['🧮 sympy 로 방정식', 'from sympy import symbols, solve, diff, integrate, sin\n\nx = symbols("x")\nprint("해:", solve(x**2 - 5*x + 6, x))\nprint("미분:", diff(x**3 + sin(x), x))\nprint("적분:", integrate(x**2, x))\n'],
    ['🐼 pandas 표 다루기', 'import pandas as pd\n\ndf = pd.DataFrame({"이름": ["가", "나", "다"], "점수": [90, 75, 88]})\nprint(df)\nprint("평균:", df["점수"].mean())\nprint(df.sort_values("점수", ascending=False))\n'],
  ];

  /* ---------- 화면 ---------- */
  function page() {
    const code0 = lsGet(KEY_CODE, EXAMPLES[0][1]);
    const open0 = /\binput\s*\(/.test(code0);
    const html = `
    <div class="lab">
      <div class="lab-head">
        <div>
          <h1>🔬 파이썬 자유 연구소</h1>
          <p class="muted small">내 브라우저 안에서 파이썬을 마음껏 돌려요. 없는 패키지는 PyPI 에서 찾아서 설치하고 <code>import</code> 하면 끝!</p>
        </div>
        <span class="lab-state" id="labState">파이썬 깨우는 중…</span>
      </div>
      <div class="lab-grid">
        <div class="lab-main">
          <div class="card lab-card">
            <div class="lab-bar">
              <select id="labEx" aria-label="예제 불러오기"><option value="">📂 예제 불러오기</option>${EXAMPLES.map((e, i) => `<option value="${i}">${esc(e[0])}</option>`).join('')}</select>
              <span class="grow"></span>
              <button class="ghost" id="labStop" hidden>⏹ 중지</button>
              <button class="primary" id="labRun">▶ 실행 <small class="muted-k">Ctrl+Enter</small></button>
            </div>
            <textarea id="labCode" class="lab-code" rows="14" spellcheck="false">${esc(code0)}</textarea>
            <details class="lab-stdin"${open0 ? ' open' : ''}><summary>⌨️ 입력 (input() 에 넣을 값, 한 줄에 하나)</summary><textarea id="labIn" rows="3" placeholder="예) 철수">${esc(lsGet(KEY_STDIN, ''))}</textarea></details>
          </div>
          <div class="card lab-card">
            <div class="lab-bar"><b>출력</b><span class="grow"></span><span class="muted small" id="labTime"></span><button class="link" id="labClear">지우기</button></div>
            <pre class="lab-out" id="labOut"><span class="lab-dim">▶ 실행을 누르면 결과가 여기에 나와요.</span></pre>
            <div class="lab-figs" id="labFigs"></div>
          </div>
        </div>
        <aside class="lab-side">
          <div class="card lab-card">
            <b>📦 패키지 검색 (PyPI)</b>
            <p class="muted small" style="margin:4px 0 8px">이름이나 하고 싶은 일로 검색해요. <code>import</code> 만 써도 없는 패키지는 알아서 설치해 줘요.</p>
            <div class="lab-sbox"><input type="text" id="labQ" placeholder="예) rich, 표, qrcode, sympy" autocomplete="off"><button class="primary" id="labSearch">검색</button></div>
            <div id="labRes" class="lab-res"><p class="muted small">검색어를 넣어보세요. 비워두고 검색하면 추천 목록이 나와요.</p></div>
          </div>
          <div class="card lab-card">
            <b>✅ 이번에 설치한 패키지</b>
            <div id="labInst" class="lab-inst"><span class="muted small">아직 없어요.</span></div>
          </div>
          <div class="card lab-card lab-note">
            <b>ℹ️ 알아두기</b>
            <ul class="small muted">
              <li>실행은 내 기기 안에서만 돌아가요. 새로고침하면 설치한 패키지는 다시 설치돼요.</li>
              <li>순수 파이썬 패키지는 거의 다 돼요. 컴파일이 필요한 패키지는 파이오다이드 기본 제공(numpy·pandas·scipy 등)만 돼요.</li>
              <li><code>requests</code> 같은 인터넷 접속은 브라우저 제한으로 안 돼요. 파일 저장도 이번 실행 동안만 유지돼요.</li>
              <li>무한 반복이면 <b>중지</b>를 눌러요. 그러면 파이썬이 새로 시작돼요.</li>
            </ul>
          </div>
        </aside>
      </div>
    </div>`;
    return Promise.resolve([html, bind]);
  }

  function bind(v) {
    const $ = (s) => v.querySelector(s);
    const ta = $('#labCode');
    if (window.PYIDE) window.PYIDE.attach(ta);
    const stateEl = $('#labState'), outEl = $('#labOut'), figsEl = $('#labFigs'), timeEl = $('#labTime');
    const runBtn = $('#labRun'), stopBtn = $('#labStop');
    let running = false, runId = 0, outLen = 0, t0 = 0, tick = null;

    const setState = (txt, cls) => { stateEl.textContent = txt; stateEl.className = 'lab-state ' + (cls || ''); };
    const append = (s, cls) => {
      if (outLen === 0) outEl.textContent = '';
      if (outLen > OUT_MAX) return;
      outLen += s.length;
      if (outLen > OUT_MAX) s = s.slice(0, s.length - (outLen - OUT_MAX)) + '\n… (출력이 너무 길어서 여기서 잘랐어요)\n';
      const sp = document.createElement('span');
      if (cls) sp.className = cls;
      sp.textContent = s;
      outEl.appendChild(sp);
      outEl.scrollTop = outEl.scrollHeight;
    };
    const renderInst = () => {
      const box = $('#labInst');
      if (!installed.size) { box.innerHTML = '<span class="muted small">아직 없어요.</span>'; markInstalled(); return; }
      box.innerHTML = [...installed].map(([n, tops]) => `<div class="lab-ipk"><b>${esc(n)}</b>${tops.length ? `<code>import ${esc(tops[0])}</code><button class="link" data-ins="${esc(tops[0])}">코드에 넣기</button>` : ''}</div>`).join('');
      markInstalled();
    };
    const markInstalled = () => v.querySelectorAll('[data-inst]').forEach((b) => {
      const ok = installed.has(b.dataset.inst) || [...installed.keys()].some((k) => norm(k) === norm(b.dataset.inst));
      if (ok) { b.textContent = '설치됨 ✓'; b.disabled = true; }
    });
    const insertImport = (mod) => {
      if (!mod) return;
      const line = 'import ' + mod;
      if (ta.value.split('\n').some((l) => l.trim() === line)) { ta.focus(); return; }
      ta.value = line + '\n' + ta.value;
      ta.dispatchEvent(new Event('input', { bubbles: true }));
      lsSet(KEY_CODE, ta.value);
    };

    const onMsg = (d) => {
      if (!v.isConnected) { return; }
      if (d.t === 'out') append(d.s, d.bad ? 'lab-err' : '');
      else if (d.t === 'log') append(d.s + '\n', d.bad ? 'lab-err' : 'lab-dim');
      else if (d.t === 'pkg') renderInst();
      else if (d.t === 'done' && d.id === runId) finish(d);
    };
    listener = onMsg;

    function finish(d) {
      running = false; clearInterval(tick);
      runBtn.disabled = false; stopBtn.hidden = true;
      if (d.err) { append((outLen && !outEl.textContent.endsWith('\n') ? '\n' : '') + d.err + '\n', 'lab-err'); setState('오류가 났어요', 'bad'); }
      else setState('끝! ✨', 'ok');
      if (outLen === 0) outEl.innerHTML = '<span class="lab-dim">(출력 없음)</span>';
      (d.figs || []).forEach((b64) => { const im = document.createElement('img'); im.src = 'data:image/png;base64,' + b64; im.alt = '그래프'; figsEl.appendChild(im); });
      timeEl.textContent = ((d.ms || 0) / 1000).toFixed(2) + '초';
    }

    async function run() {
      if (running) return;
      const code = ta.value;
      lsSet(KEY_CODE, code); lsSet(KEY_STDIN, $('#labIn').value);
      if (/\binput\s*\(/.test(code) && !$('#labIn').value.trim()) $('.lab-stdin').open = true;
      outEl.textContent = ''; outLen = 0; figsEl.innerHTML = ''; timeEl.textContent = '';
      running = true; runBtn.disabled = true; stopBtn.hidden = false;
      t0 = Date.now();
      setState('파이썬 준비 중…', 'busy');
      try { await startWorker(); } catch (e) { running = false; runBtn.disabled = false; stopBtn.hidden = true; append(String(e.message || e) + '\n', 'lab-err'); setState('불러오기 실패', 'bad'); return; }
      listener = onMsg;
      const id = ++seq; runId = id;
      tick = setInterval(() => { timeEl.textContent = ((Date.now() - t0) / 1000).toFixed(0) + '초째…'; }, 500);
      setState('실행 중…', 'busy');
      W.w.postMessage({ t: 'run', id, code, stdin: $('#labIn').value });
    }
    function stop() {
      if (!running) return;
      killWorker();
      running = false; clearInterval(tick); runBtn.disabled = false; stopBtn.hidden = true;
      append('\n⏹ 중지했어요. (파이썬이 새로 시작돼요)\n', 'lab-err');
      setState('중지됨', 'bad'); timeEl.textContent = '';
      renderInst();
      startWorker().then(() => { if (!running) setState('준비 완료', 'ok'); }).catch(() => {});
    }

    runBtn.onclick = run;
    stopBtn.onclick = stop;
    ta.addEventListener('keydown', (e) => { if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); run(); } });
    ta.addEventListener('input', () => lsSet(KEY_CODE, ta.value));
    $('#labClear').onclick = () => { outEl.innerHTML = '<span class="lab-dim">▶ 실행을 누르면 결과가 여기에 나와요.</span>'; outLen = 0; figsEl.innerHTML = ''; timeEl.textContent = ''; };
    $('#labEx').onchange = (e) => {
      const i = e.target.value; if (i === '') return;
      const ex = EXAMPLES[+i];
      ta.value = ex[1]; ta.dispatchEvent(new Event('input', { bubbles: true })); lsSet(KEY_CODE, ta.value); e.target.value = '';
      if (ex[2] != null) { $('#labIn').value = ex[2]; $('.lab-stdin').open = true; }
    };

    /* 검색 */
    const res = $('#labRes');
    let qTok = 0;
    const row = (p, kind) => {
      const badge = p.builtin ? '<span class="lab-b b-in">기본 제공</span>' : kind === 'pure' ? '<span class="lab-b b-ok">순수 파이썬 · 설치 가능</span>' : kind === 'maybe' ? '<span class="lab-b b-warn">컴파일 필요할 수 있어요</span>' : '';
      const imp = p.imports && p.imports.length ? p.imports[0] : p.name.replace(/-/g, '_');
      const btn = p.builtin ? `<button class="ghost" data-use="${esc(imp)}">코드에 import</button>` : `<button class="primary" data-pip="${esc(p.name)}" data-inst="${esc(p.name)}">설치</button>`;
      return `<div class="lab-pk"><div class="lab-pk-t"><b>${esc(p.name)}</b>${p.version ? `<span class="muted small"> ${esc(p.version)}</span>` : ''} ${badge}</div>${p.desc ? `<div class="small muted">${esc(p.desc)}</div>` : ''}<div class="lab-pk-a">${btn}${p.home ? `<a class="small" href="${esc(p.home)}" target="_blank" rel="noopener">PyPI ↗</a>` : ''}</div></div>`;
    };
    async function doSearch() {
      const q = $('#labQ').value;
      const tok = ++qTok;
      res.innerHTML = '<p class="muted small">찾는 중…</p>';
      let r;
      if (!q.trim()) { const lock = await loadLock(); r = { list: CURATED.slice(0, 14).map((c) => ({ name: c.name, desc: c.desc, version: '', builtin: lock.some((x) => norm(x.name) === norm(c.name)), imports: [] })), exact: null, rec: true }; }
      else r = await search(q);
      if (tok !== qTok) return;
      const parts = [];
      if (r.exact) {
        const ex = r.exact;
        const dupe = r.list.some((p) => norm(p.name) === norm(ex.name));
        if (!dupe || !r.list.find((p) => norm(p.name) === norm(ex.name)).builtin) parts.push(`<div class="lab-sec">PyPI 에서 찾았어요</div>` + row({ name: ex.name, version: ex.version, desc: ex.desc, home: ex.home, builtin: r.list.some((p) => norm(p.name) === norm(ex.name) && p.builtin), imports: (r.list.find((p) => norm(p.name) === norm(ex.name)) || {}).imports }, ex.pure ? 'pure' : 'maybe'));
      }
      const rest = r.list.filter((p) => !(r.exact && norm(p.name) === norm(r.exact.name)));
      if (rest.length) parts.push(`<div class="lab-sec">${r.rec ? '추천 패키지' : '관련 패키지'}</div>` + rest.map((p) => row(Object.assign({ home: 'https://pypi.org/project/' + p.name + '/' }, p), '')).join(''));
      if (!parts.length) parts.push('<p class="muted small">비슷한 패키지를 못 찾았어요. 철자를 확인하거나 PyPI 에 있는 정확한 이름을 넣어보세요.</p>');
      res.innerHTML = parts.join('');
      markInstalled();
    }
    $('#labSearch').onclick = doSearch;
    $('#labQ').addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); doSearch(); } });

    res.addEventListener('click', async (e) => {
      const use = e.target.closest('[data-use]');
      if (use) { insertImport(use.dataset.use); return; }
      const b = e.target.closest('[data-pip]');
      if (!b || b.disabled) return;
      const name = b.dataset.pip;
      b.disabled = true; b.textContent = '설치 중…';
      try { await startWorker(); } catch (er) { b.disabled = false; b.textContent = '설치'; append(String(er.message || er) + '\n', 'lab-err'); return; }
      listener = onMsg;
      const id = ++seq;
      const h = (ev) => {
        const d = ev.data;
        if (d.t === 'installed' && d.name === name) {
          W && W.w.removeEventListener('message', h);
          if (d.ok) { b.textContent = '설치됨 ✓'; const t = installed.get(name) || []; if (t[0]) { b.insertAdjacentHTML('afterend', `<button class="ghost" data-use="${esc(t[0])}">import ${esc(t[0])} 넣기</button>`); } }
          else { b.disabled = false; b.textContent = '다시 시도'; }
        }
      };
      W.w.addEventListener('message', h);
      W.w.postMessage({ t: 'install', id, name });
    });
    v.addEventListener('click', (e) => { const i = e.target.closest('[data-ins]'); if (i) insertImport(i.dataset.ins); });

    renderInst();
    setState('파이썬 깨우는 중…', 'busy');
    startWorker().then(() => { if (v.isConnected && !running) setState('준비 완료', 'ok'); }).catch((e) => { if (v.isConnected) setState('불러오기 실패', 'bad'); });
  }

  window.PYLAB = { page };
})();
