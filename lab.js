/* PyNest · 파이썬 자유 연구소 (연구 탭)
 *  - 브라우저 안에서 파이썬(Pyodide)을 자유롭게 실행
 *  - PyPI 패키지 검색 → 설치(micropip) → import, 상시 설치 패키지 설정
 *  - matplotlib 그래프 · turtle 그림은 팝업 창으로
 *  - 작업 공간(파일 만들기·올리기·내려받기): 내 브라우저 메모리에만 있고 서버 DB 는 쓰지 않아요
 *  사용: window.PYLAB.page() → [html, bind],  window.PYLAB.bindSettings(el)
 */
(function () {
  'use strict';
  const PY_URL = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/';
  const KEY_CODE = 'pn_lab_code';
  const KEY_STDIN = 'pn_lab_stdin';
  const KEY_LIBS = 'pn_lab_libs';
  const OUT_MAX = 200000;
  const Q_TOTAL = 30 * 1024 * 1024; // 작업 공간 전체
  const Q_FILE = 10 * 1024 * 1024;  // 파일 하나
  const Q_COUNT = 100;              // 파일 개수
  const LIB_MAX = 12;
  const KEY_VIEW = 'pn_lab_view';
  const getMode = () => (lsGet(KEY_VIEW, 'popup') === 'inline' ? 'inline' : 'popup');
  const setMode = (m) => lsSet(KEY_VIEW, m === 'inline' ? 'inline' : 'popup');

  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const lsGet = (k, d) => { try { const v = localStorage.getItem(k); return v == null ? d : v; } catch (e) { return d; } };
  const lsSet = (k, v) => { try { localStorage.setItem(k, v); } catch (e) { /* 무시 */ } };
  const norm = (s) => String(s).toLowerCase().replace(/[-_.]+/g, '-').trim();
  const fmtSize = (n) => (n < 1024 ? n + ' B' : n < 1048576 ? (n / 1024).toFixed(1) + ' KB' : (n / 1048576).toFixed(1) + ' MB');

  /* ---------- 상시 설치 패키지 (이 기기에 저장) ---------- */
  function getLibs() { try { const a = JSON.parse(lsGet(KEY_LIBS, '[]')); return Array.isArray(a) ? a.filter((x) => typeof x === 'string').slice(0, LIB_MAX) : []; } catch (e) { return []; } }
  function setLibs(a) { lsSet(KEY_LIBS, JSON.stringify(a.slice(0, LIB_MAX))); }

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
    '    sys.modules.pop("turtle", None)',
    '    _home.clear()',
    '    if "matplotlib.pyplot" in sys.modules: sys.modules["matplotlib.pyplot"].close("all")',
    '    sys.stdin = io.StringIO(inp)',
    '    def _inp(prompt=""):',
    '        if prompt: sys.stdout.write(str(prompt))',
    '        s = sys.stdin.readline()',
    '        if s == "": raise EOFError("EOF when reading a line (아래 \'입력\' 칸이 비어 있어요)")',
    '        s = s.rstrip("\\n")',
    '        sys.stdout.write(s + "\\n")',
    '        return s',
    '    builtins.input = _inp',
    '_home = {}',
    'def lab_figs(keep=False):',
    '    out = []',
    '    if "matplotlib.pyplot" in sys.modules:',
    '        plt = sys.modules["matplotlib.pyplot"]',
    '        for n in plt.get_fignums():',
    '            fig = plt.figure(n)',
    '            b = io.BytesIO()',
    '            if keep:',
    '                for i, ax in enumerate(fig.axes):',
    '                    try: _home[(n, i)] = (ax.get_xlim(), ax.get_ylim())',
    '                    except Exception: pass',
    '                fig.savefig(b, format="png")',
    '            else:',
    '                fig.savefig(b, format="png", dpi=110, bbox_inches="tight")',
    '            out.append({"n": n, "png": base64.b64encode(b.getvalue()).decode(), "w": int(fig.bbox.width), "h": int(fig.bbox.height)})',
    '        if not keep: plt.close("all")',
    '    return json.dumps(out)',
    'def _axes_at(fig, x, fy):',
    '    for ax in reversed(fig.axes):',
    '        try:',
    '            if ax.get_visible() and ax.get_window_extent().contains(x, fy): return ax',
    '        except Exception: pass',
    '    return None',
    'def _png(fig):',
    '    b = io.BytesIO()',
    '    fig.savefig(b, format="png")',
    '    return base64.b64encode(b.getvalue()).decode()',
    'def _lab_mpl(p):',
    '    plt = sys.modules["matplotlib.pyplot"]',
    '    fig = plt.figure(p["n"])',
    '    a = p["a"]',
    '    x = p.get("x", 0)',
    '    fy = fig.bbox.height - p.get("y", 0)',
    '    if a == "reset":',
    '        for i, ax in enumerate(fig.axes):',
    '            h = _home.get((p["n"], i))',
    '            if h:',
    '                ax.set_xlim(h[0]); ax.set_ylim(h[1])',
    '        return {"png": _png(fig)}',
    '    ax = _axes_at(fig, x, fy)',
    '    if ax is None: return {"txt": ""}',
    '    inv = ax.transData.inverted()',
    '    if a == "pos":',
    '        xd, yd = inv.transform((x, fy))',
    '        return {"txt": ax.format_coord(xd, yd).strip()}',
    '    if getattr(ax, "name", "") != "rectilinear": return {"txt": "(이 그래프는 확대·이동을 지원하지 않아요)"}',
    '    xl, yl = ax.get_xlim(), ax.get_ylim()',
    '    if a == "zoom":',
    '        f = float(p["f"])',
    '        xd, yd = inv.transform((x, fy))',
    '        if ax.get_xscale() == "linear": ax.set_xlim(xd + (xl[0] - xd) * f, xd + (xl[1] - xd) * f)',
    '        if ax.get_yscale() == "linear": ax.set_ylim(yd + (yl[0] - yd) * f, yd + (yl[1] - yd) * f)',
    '    elif a == "pan":',
    '        d0 = inv.transform((x, fy))',
    '        d1 = inv.transform((x + p["dx"], fy - p["dy"]))',
    '        if ax.get_xscale() == "linear": ax.set_xlim(xl[0] - (d1[0] - d0[0]), xl[1] - (d1[0] - d0[0]))',
    '        if ax.get_yscale() == "linear": ax.set_ylim(yl[0] - (d1[1] - d0[1]), yl[1] - (d1[1] - d0[1]))',
    '    return {"png": _png(fig)}',
    'def lab_event(kind, payload):',
    '    p = json.loads(payload)',
    '    out = {}',
    '    t = sys.modules.get("turtle")',
    '    try:',
    '        if kind == "mpl":',
    '            out = _lab_mpl(p)',
    '        elif t is not None and hasattr(t, "_lab_event"):',
    '            t._lab_event(kind, p)',
    '    except BaseException as e:',
    '        import traceback',
    '        out["err"] = "".join(traceback.format_exception_only(type(e), e)).strip()',
    '    if t is not None and hasattr(t, "_lab_pop"): out["ops"] = t._lab_pop()',
    '    return json.dumps(out)',
    'def lab_turtle():',
    '    t = sys.modules.get("turtle")',
    '    if t is None or not hasattr(t, "_lab_pop"): return "[]"',
    '    return json.dumps(t._lab_pop())',
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

  /* ---------- turtle 대체 모듈 (브라우저에는 tkinter 가 없어서, 그림 명령을 모아 팝업 창에서 그려요) ---------- */
  const TURTLE_PY = String.raw`# PyNest 연구소용 turtle: 명령을 기록해서 팝업 캔버스에서 다시 그려요.
import math

_ops = []
_MAX = 300000
_cm = [1.0]
_nid = [0]
_def = [None]
_scr = [None]
_kh = {}
_clk = [None]
_tm = {}
_tmid = [0]
_all = []
_drag = [None]


class Terminator(Exception):
    pass


def _emit(o):
    if len(_ops) > _MAX:
        raise RuntimeError("터틀 명령이 너무 많아요 (30만 개 넘음)")
    _ops.append(o)


def _lab_pop():
    o = list(_ops)
    del _ops[:]
    return o


def _near(t, x, y, r=18):
    return math.hypot(t._x - x, t._y - y) <= r * max(t._sx, t._sy, 1)


def _lab_event(kind, p):
    if kind == "key":
        k, ph = p["key"], p["ph"]
        fn = _kh.get((k, ph)) or _kh.get((k.lower(), ph)) or _kh.get((None, ph))
        if fn:
            fn()
    elif kind == "click":
        x, y = p["x"], p["y"]
        for t in list(_all):
            if t._onclick and _near(t, x, y):
                t._onclick(x, y)
        if _clk[0]:
            _clk[0](x, y)
    elif kind == "down":
        _drag[0] = None
        for t in list(_all):
            if t._ondrag and _near(t, p["x"], p["y"]):
                _drag[0] = t
    elif kind == "drag":
        t = _drag[0]
        if t is not None and t._ondrag:
            t._ondrag(p["x"], p["y"])
    elif kind == "up":
        _drag[0] = None
    elif kind == "timer":
        fn = _tm.pop(p["id"], None)
        if fn:
            fn()


def _bindk(key, ph, fun):
    _emit(["EVT"])
    if fun is None:
        _kh.pop((key, ph), None)
    else:
        _kh[(key, ph)] = fun


def _col(*a):
    c = a[0] if len(a) == 1 else a
    if isinstance(c, str):
        return c.replace(" ", "")
    r, g, b = c
    if _cm[0] != 255 and max(r, g, b) <= 1:
        r, g, b = r * 255, g * 255, b * 255
    return "rgb(%d,%d,%d)" % (r, g, b)


class Turtle:
    def __init__(self, shape="classic", undobuffersize=1000, visible=True):
        self._id = _nid[0]
        _nid[0] += 1
        self._x = 0.0
        self._y = 0.0
        self._h = 0.0
        self._down = True
        self._pc = "black"
        self._fc = "black"
        self._size = 1
        self._shape = shape
        self._sx = 1
        self._sy = 1
        self._vis = visible
        self._fill = None
        self._onclick = None
        self._ondrag = None
        _all.append(self)
        self._ap()
        _emit(["SP", self._id, 3])
        if not visible:
            _emit(["V", self._id, 0])

    def _ap(self):
        _emit(["A", self._id, self._shape, self._sx, self._sy, self._pc, self._fc])

    def _move(self, x, y):
        if self._fill is not None:
            self._fill.append((x, y))
        if self._down:
            _emit(["L", self._id, self._x, self._y, x, y, self._pc, self._size])
        else:
            _emit(["G", self._id, x, y])
        self._x, self._y = x, y

    def forward(self, d):
        r = math.radians(self._h)
        self._move(self._x + d * math.cos(r), self._y + d * math.sin(r))
    fd = forward

    def backward(self, d):
        self.forward(-d)
    bk = back = backward

    def left(self, a):
        self._h = (self._h + a) % 360
        _emit(["H", self._id, self._h])
    lt = left

    def right(self, a):
        self.left(-a)
    rt = right

    def goto(self, x, y=None):
        if y is None:
            x, y = x
        self._move(float(x), float(y))
    setpos = setposition = goto

    def setx(self, x):
        self._move(float(x), self._y)

    def sety(self, y):
        self._move(self._x, float(y))

    def setheading(self, a):
        self._h = a % 360
        _emit(["H", self._id, self._h])
    seth = setheading

    def home(self):
        self.goto(0, 0)
        self.setheading(0)

    def circle(self, radius, extent=None, steps=None):
        if extent is None:
            extent = 360
        if steps is None:
            frac = abs(extent) / 360.0
            steps = 1 + int(min(11 + abs(radius) / 6.0, 59.0) * frac)
        w = 1.0 * extent / steps
        w2 = 0.5 * w
        l = 2.0 * radius * math.sin(math.radians(w2))
        if radius < 0:
            l, w, w2 = -l, -w, -w2
        self.left(w2)
        for _ in range(steps):
            self.forward(l)
            self.left(w)
        self.right(w2)

    def dot(self, size=None, *color):
        if size is None:
            size = max(self._size + 4, 2 * self._size)
        c = _col(*color) if color else self._pc
        _emit(["D", self._id, self._x, self._y, size, c])

    def stamp(self):
        _emit(["ST", self._id, self._x, self._y, self._h])
        return self._id

    def write(self, arg, move=False, align="left", font=("Arial", 8, "normal")):
        _emit(["W", self._id, self._x, self._y, str(arg), list(font), self._pc, align])

    def penup(self):
        self._down = False
    pu = up = penup

    def pendown(self):
        self._down = True
    pd = down = pendown

    def isdown(self):
        return self._down

    def pensize(self, w=None):
        if w is None:
            return self._size
        self._size = w
    width = pensize

    def pencolor(self, *a):
        if not a:
            return self._pc
        self._pc = _col(*a)
        self._ap()

    def fillcolor(self, *a):
        if not a:
            return self._fc
        self._fc = _col(*a)
        self._ap()

    def color(self, *a):
        if not a:
            return (self._pc, self._fc)
        if len(a) == 2:
            self._pc, self._fc = _col(a[0]), _col(a[1])
        else:
            self._pc = self._fc = _col(*a)
        self._ap()

    def begin_fill(self):
        self._fill = [(self._x, self._y)]

    def end_fill(self):
        if self._fill and len(self._fill) >= 3:
            _emit(["F", self._id, [[p[0], p[1]] for p in self._fill], self._fc])
        self._fill = None

    def filling(self):
        return self._fill is not None

    def speed(self, s=None):
        names = {"fastest": 0, "fast": 10, "normal": 6, "slow": 3, "slowest": 1}
        if s is None:
            return self._speed if hasattr(self, "_speed") else 3
        if isinstance(s, str):
            s = names.get(s, 3)
        s = int(s)
        if s > 10 or s < 0.5:
            s = 0
        self._speed = s
        _emit(["SP", self._id, s])

    def shape(self, name=None):
        if name is None:
            return self._shape
        self._shape = name
        self._ap()

    def shapesize(self, sx=None, sy=None, outline=None):
        if sx is None:
            return (self._sx, self._sy)
        self._sx = sx
        self._sy = sx if sy is None else sy
        self._ap()
    turtlesize = shapesize

    def hideturtle(self):
        self._vis = False
        _emit(["V", self._id, 0])
    ht = hideturtle

    def showturtle(self):
        self._vis = True
        _emit(["V", self._id, 1])
    st = showturtle

    def isvisible(self):
        return self._vis

    def clear(self):
        _emit(["CLR", self._id])

    def reset(self):
        _emit(["CLR", self._id])
        self._pc = self._fc = "black"
        self._size = 1
        self._ap()
        self.home()

    def position(self):
        return (self._x, self._y)
    pos = position

    def xcor(self):
        return self._x

    def ycor(self):
        return self._y

    def heading(self):
        return self._h

    def distance(self, x, y=None):
        if y is None:
            if hasattr(x, "_x"):
                x, y = x._x, x._y
            else:
                x, y = x
        return math.hypot(x - self._x, y - self._y)

    def towards(self, x, y=None):
        if y is None:
            if hasattr(x, "_x"):
                x, y = x._x, x._y
            else:
                x, y = x
        return math.degrees(math.atan2(y - self._y, x - self._x)) % 360

    def getscreen(self):
        return Screen()

    def clone(self):
        t = Turtle(self._shape)
        t._x, t._y, t._h = self._x, self._y, self._h
        t._pc, t._fc, t._size, t._down = self._pc, self._fc, self._size, self._down
        t._ap()
        return t

    def setundobuffer(self, *a):
        pass

    def undo(self):
        pass

    def degrees(self, *a):
        pass

    def radians(self):
        pass

    def onclick(self, fun, btn=1, add=None):
        _emit(["EVT"])
        self._onclick = fun

    def onrelease(self, *a, **k):
        pass

    def ondrag(self, fun, btn=1, add=None):
        _emit(["EVT"])
        self._ondrag = fun


Pen = Turtle


class RawTurtle(Turtle):
    def __init__(self, canvas=None, shape="classic", undobuffersize=1000, visible=True):
        Turtle.__init__(self, shape, undobuffersize, visible)


class _Screen:
    def bgcolor(self, *a):
        if not a:
            return "white"
        _emit(["bg", _col(*a)])

    def title(self, t):
        _emit(["T", str(t)])

    def setup(self, *a, **k):
        pass

    def screensize(self, *a, **k):
        return (600, 600)

    def window_width(self):
        return 600

    def window_height(self):
        return 600

    def tracer(self, n=None, delay=None):
        if n is None:
            return 1
        _emit(["I", 1 if n == 0 else 0])

    def update(self):
        pass

    def delay(self, *a):
        pass

    def colormode(self, m=None):
        if m is None:
            return _cm[0]
        _cm[0] = 255 if m == 255 else 1.0

    def mode(self, *a):
        pass

    def clear(self):
        _emit(["CLR", -1])
    clearscreen = clear

    def reset(self):
        _emit(["CLR", -1])

    def mainloop(self):
        pass
    done = exitonclick = bye = mainloop

    def listen(self, *a, **k):
        pass

    def onkeypress(self, fun, key=None):
        _bindk(key, "down", fun)

    def onkey(self, fun, key):
        _bindk(key, "up", fun)
    onkeyrelease = onkey

    def onscreenclick(self, fun, btn=1, add=None):
        _emit(["EVT"])
        _clk[0] = fun
    onclick = onscreenclick

    def ontimer(self, fun, t=0):
        _tmid[0] += 1
        _tm[_tmid[0]] = fun
        _emit(["TM", _tmid[0], int(t)])

    def textinput(self, title, prompt):
        return input(str(prompt) + " ")

    def numinput(self, title, prompt, *a, **k):
        return float(input(str(prompt) + " "))

    def register_shape(self, *a, **k):
        pass
    addshape = register_shape

    def getcanvas(self):
        return None

    def turtles(self):
        return []


TurtleScreen = _Screen


def Screen():
    if _scr[0] is None:
        _scr[0] = _Screen()
    return _scr[0]


def _t():
    if _def[0] is None:
        _def[0] = Turtle()
    return _def[0]


def _mk_t(n):
    def f(*a, **k):
        return getattr(_t(), n)(*a, **k)
    f.__name__ = n
    return f


def _mk_s(n):
    def f(*a, **k):
        return getattr(Screen(), n)(*a, **k)
    f.__name__ = n
    return f


for _n in ("forward fd backward bk back left lt right rt goto setpos setposition setx sety setheading seth home circle dot stamp write "
           "penup pu up pendown pd down isdown pensize width pencolor fillcolor color begin_fill end_fill filling speed shape shapesize "
           "turtlesize hideturtle ht showturtle st isvisible clear reset position pos xcor ycor heading distance towards getscreen clone "
           "setundobuffer undo degrees radians onclick onrelease ondrag").split():
    globals()[_n] = _mk_t(_n)

for _n in ("bgcolor title setup screensize window_width window_height tracer update delay colormode mode clearscreen mainloop done "
           "exitonclick bye listen onkey onkeypress onkeyrelease onscreenclick ontimer textinput numinput register_shape addshape "
           "getcanvas turtles").split():
    globals()[_n] = _mk_s(_n)
`;

  /* ---------- 워커 (별도 스레드: 화면이 안 멈춰요) ---------- */
  function workerMain() {
    /* global PY_URL, PY_BOOT, TURTLE_PY, QUOTA, importScripts, loadPyodide */
    importScripts(PY_URL + 'pyodide.js');
    let py = null;
    const DIR = '/home/lab';
    const say = (m, tr) => postMessage(m, tr || []);
    const ALIAS = { PIL: 'pillow', cv2: 'opencv-python', sklearn: 'scikit-learn', yaml: 'pyyaml', bs4: 'beautifulsoup4', dateutil: 'python-dateutil', slugify: 'python-slugify', skimage: 'scikit-image', Crypto: 'pycryptodome', attr: 'attrs', serial: 'pyserial', docx: 'python-docx', dotenv: 'python-dotenv', jwt: 'pyjwt' };
    (async () => {
      try {
        py = await loadPyodide({ indexURL: PY_URL });
        await py.loadPackage('micropip');
        py.runPython(PY_BOOT, { filename: '<lab>' });
        py.FS.mkdirTree('/lab_lib');
        py.FS.writeFile('/lab_lib/turtle.py', TURTLE_PY);
        py.FS.mkdirTree(DIR);
        py.runPython('import sys, os\nsys.path.insert(0, "/lab_lib")\nos.chdir("' + DIR + '")', { filename: '<lab>' });
        say({ t: 'ready', version: py.version });
      } catch (e) { say({ t: 'fatal', s: String(e) }); }
    })();

    const tops = (dist) => { try { return JSON.parse(py.globals.get('lab_tops')(dist)); } catch (e) { return []; } };

    function clearDir(dir) {
      for (const n of py.FS.readdir(dir)) {
        if (n === '.' || n === '..') continue;
        const p = dir + '/' + n;
        if (py.FS.isDir(py.FS.stat(p).mode)) { clearDir(p); py.FS.rmdir(p); } else py.FS.unlink(p);
      }
    }
    function writeFiles(files) {
      for (const [p, b] of files) {
        const full = DIR + '/' + p;
        py.FS.mkdirTree(full.slice(0, full.lastIndexOf('/')));
        py.FS.writeFile(full, b);
      }
    }
    function snapshot() {
      const out = [];
      let total = 0;
      (function walk(d, rel) {
        for (const n of py.FS.readdir(d)) {
          if (n === '.' || n === '..' || n === '__pycache__') continue;
          const f = d + '/' + n, r = rel ? rel + '/' + n : n;
          if (py.FS.isDir(py.FS.stat(f).mode)) walk(f, r);
          else { const u = py.FS.readFile(f).slice(); total += u.length; out.push([r, u]); }
        }
      })(DIR, '');
      return { out, total };
    }

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
      let body = (i >= 0 ? 'Traceback (most recent call last):\n  ' + raw.slice(i) : raw).replace(/ {2}File "<lab>".*\n(?: {4}.*\n)*/g, '').replace(/File "<exec>"/g, 'File "main.py"');
      if (/No module named '_?tkinter'/.test(body)) body += '\n💡 tkinter 같은 창(GUI)은 브라우저에서 못 써요. turtle 과 matplotlib 은 팝업 창으로 떠요!';
      return body.trim();
    }

    onmessage = async (ev) => {
      const d = ev.data;
      if (!py) { say({ t: 'done', id: d.id, err: '아직 파이썬을 불러오는 중이에요. 잠깐만요!' }); return; }
      if (d.t === 'install') {
        const ok = await install(d.name, d.quiet);
        say({ t: 'installed', id: d.id, ok, name: d.name });
        return;
      }
      if (d.t === 'ev') {
        let r = {};
        try { r = JSON.parse(py.globals.get('lab_event')(d.kind, d.payload)); } catch (e) { r = { err: String(e) }; }
        say(Object.assign({ t: 'evdone', id: d.id }, r));
        return;
      }
      if (d.t !== 'run') return;
      const t0 = Date.now();
      let err = null, figs = [], turtle = [], files = null, over = 0;
      try {
        clearDir(DIR);
        writeFiles(d.files || []);
      } catch (e) { err = '작업 공간을 준비하지 못했어요: ' + e; }
      if (!err) {
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
      }
      try { figs = JSON.parse(py.globals.get('lab_figs')(!!d.inline)); } catch (e) { /* 그림 없음 */ }
      try { turtle = JSON.parse(py.globals.get('lab_turtle')()); } catch (e) { /* 터틀 없음 */ }
      const tr = [];
      try {
        const s = snapshot();
        if (s.total > QUOTA) over = s.total;
        else { files = s.out; s.out.forEach((f) => tr.push(f[1].buffer)); }
      } catch (e) { /* 파일 없음 */ }
      say({ t: 'done', id: d.id, err, figs, turtle, files, over, ms: Date.now() - t0 }, tr);
    };
  }
  const WORKER_SRC = 'const PY_URL=' + JSON.stringify(PY_URL) + ';\nconst PY_BOOT=' + JSON.stringify(PY_BOOT) + ';\nconst TURTLE_PY=' + JSON.stringify(TURTLE_PY) + ';\nconst QUOTA=' + Q_TOTAL + ';\n(' + workerMain.toString() + ')();';

  /* ---------- 워커 관리 ---------- */
  let W = null;          // {w, ready, pre}
  let listener = null;   // 지금 화면이 듣는 함수
  const installed = new Map(); // 설치한 패키지 → import 이름들
  const waiters = new Map();   // 설치 요청 id → resolve
  let seq = 0;

  function reqInstall(name, quiet) {
    return new Promise((res) => { const id = ++seq; waiters.set(id, res); W.w.postMessage({ t: 'install', id, name, quiet }); });
  }

  function reqEv(kind, payload) {
    return new Promise((res) => { if (!W) { res(null); return; } const id = ++seq; waiters.set(id, res); W.w.postMessage({ t: 'ev', id, kind, payload: JSON.stringify(payload) }); });
  }

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
      if (d.t === 'installed' || d.t === 'evdone') { const r = waiters.get(d.id); if (r) { waiters.delete(d.id); r(d); } }
      if (listener) listener(d);
    });
    const me = { w, ready, pre: null };
    W = me;
    // 상시 설치 패키지: 파이썬이 켜지면 차례로 설치해요
    me.pre = ready.then(async () => {
      const libs = getLibs();
      for (let i = 0; i < libs.length; i++) {
        if (W !== me) return;
        if (listener) listener({ t: 'preload', i: i + 1, n: libs.length, name: libs[i] });
        await reqInstall(libs[i], true);
      }
      if (listener) listener({ t: 'preload', done: true, n: libs.length });
    }).catch(() => {});
    ready.catch(() => { if (W === me) { w.terminate(); W = null; } });
    return ready;
  }
  const ensureReady = () => startWorker().then(() => W && W.pre);
  function killWorker() {
    if (W) { W.w.terminate(); W = null; }
    waiters.forEach((r) => r({ ok: false })); waiters.clear();
    installed.clear();
  }

  /* ---------- 작업 공간 (내 브라우저 메모리) ---------- */
  const FS = new Map(); // 경로 → Uint8Array
  const fsTotal = () => { let n = 0; FS.forEach((u) => { n += u.length; }); return n; };
  function cleanPath(p) {
    p = String(p || '').replace(/\\/g, '/').replace(/^\/+/, '').replace(/\/{2,}/g, '/').trim();
    if (!p || p.endsWith('/') || p.split('/').some((s) => s === '..' || s === '.' || s === '' || s === '__pycache__')) return null;
    if (p.length > 120) return null;
    return p;
  }
  // 반환: 오류 문장 (없으면 null)
  function fsPut(path, u8) {
    const p = cleanPath(path);
    if (!p) return '파일 이름이 올바르지 않아요: ' + path;
    if (u8.length > Q_FILE) return `${p}: 파일 하나는 ${fmtSize(Q_FILE)}까지예요.`;
    const prev = FS.has(p) ? FS.get(p).length : 0;
    if (!FS.has(p) && FS.size >= Q_COUNT) return `파일은 ${Q_COUNT}개까지 둘 수 있어요.`;
    if (fsTotal() - prev + u8.length > Q_TOTAL) return `작업 공간(${fmtSize(Q_TOTAL)})이 가득 차요. 안 쓰는 파일을 지워주세요.`;
    FS.set(p, u8);
    return null;
  }

  function crc32(u8) {
    let c, crc = 0xFFFFFFFF;
    if (!crc32.t) { crc32.t = []; for (let n = 0; n < 256; n++) { c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; crc32.t[n] = c >>> 0; } }
    for (let i = 0; i < u8.length; i++) crc = crc32.t[(crc ^ u8[i]) & 0xFF] ^ (crc >>> 8);
    return (crc ^ 0xFFFFFFFF) >>> 0;
  }
  function makeZip(entries) { // [[이름, Uint8Array]] → Blob (압축 없이 묶기)
    const enc = new TextEncoder(), parts = [], cds = [];
    let off = 0;
    for (const [name, data] of entries) {
      const nb = enc.encode(name), crc = crc32(data);
      const lh = new DataView(new ArrayBuffer(30));
      lh.setUint32(0, 0x04034b50, true); lh.setUint16(4, 20, true); lh.setUint16(6, 0x0800, true); lh.setUint16(8, 0, true);
      lh.setUint16(10, 0, true); lh.setUint16(12, 33, true); lh.setUint32(14, crc, true); lh.setUint32(18, data.length, true); lh.setUint32(22, data.length, true);
      lh.setUint16(26, nb.length, true); lh.setUint16(28, 0, true);
      const ch = new DataView(new ArrayBuffer(46));
      ch.setUint32(0, 0x02014b50, true); ch.setUint16(4, 20, true); ch.setUint16(6, 20, true); ch.setUint16(8, 0x0800, true); ch.setUint16(10, 0, true);
      ch.setUint16(12, 0, true); ch.setUint16(14, 33, true); ch.setUint32(16, crc, true); ch.setUint32(20, data.length, true); ch.setUint32(24, data.length, true);
      ch.setUint16(28, nb.length, true); ch.setUint32(42, off, true);
      parts.push(lh.buffer, nb, data);
      cds.push(ch.buffer, nb);
      off += 30 + nb.length + data.length;
    }
    let cdSize = 0; cds.forEach((b) => { cdSize += b.byteLength !== undefined ? b.byteLength : b.length; });
    const end = new DataView(new ArrayBuffer(22));
    end.setUint32(0, 0x06054b50, true); end.setUint16(8, entries.length, true); end.setUint16(10, entries.length, true); end.setUint32(12, cdSize, true); end.setUint32(16, off, true);
    return new Blob([...parts, ...cds, end.buffer], { type: 'application/zip' });
  }
  function saveBlob(blob, name) {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 5000);
  }

  /* ---------- 팝업 창 (그래프 · 터틀) ---------- */
  const wins = [];
  let zTop = 9000;
  function closeWin(w) {
    const i = wins.indexOf(w); if (i >= 0) wins.splice(i, 1);
    if (w._onClose) { try { w._onClose(); } catch (e) { /* 무시 */ } }
    w.remove();
  }
  function closeAllWins() { wins.slice().forEach(closeWin); }
  function openWin(title, node, o = {}) {
    const w = document.createElement('div');
    w.className = 'lab-win';
    w.innerHTML = '<div class="lab-win-h"><b></b><span class="grow"></span><button type="button" class="lab-win-x" aria-label="닫기">✕</button></div><div class="lab-win-b"></div>';
    w.querySelector('b').textContent = title;
    w.querySelector('.lab-win-b').appendChild(node);
    const n = wins.length % 6;
    w.style.left = (90 + n * 30) + 'px'; w.style.top = (100 + n * 30) + 'px'; w.style.width = Math.min(o.w || 640, innerWidth - 16) + 'px';
    w.style.zIndex = ++zTop;
    document.body.appendChild(w);
    wins.push(w);
    const h = w.querySelector('.lab-win-h');
    let dx = 0, dy = 0, drag = false;
    h.addEventListener('pointerdown', (e) => {
      w.style.zIndex = ++zTop;
      if (e.target.closest('button') || innerWidth < 700) return;
      drag = true; const r = w.getBoundingClientRect(); dx = e.clientX - r.left; dy = e.clientY - r.top;
      try { h.setPointerCapture(e.pointerId); } catch (er) { /* 무시 */ }
    });
    h.addEventListener('pointermove', (e) => { if (!drag) return; w.style.left = Math.max(0, Math.min(innerWidth - 80, e.clientX - dx)) + 'px'; w.style.top = Math.max(0, Math.min(innerHeight - 40, e.clientY - dy)) + 'px'; });
    h.addEventListener('pointerup', () => { drag = false; });
    w.querySelector('.lab-win-x').onclick = () => closeWin(w);
    return w;
  }

  const dataUrlToBlob = (u) => { const bin = atob(u.split(',')[1]), a = new Uint8Array(bin.length); for (let k = 0; k < bin.length; k++) a[k] = bin.charCodeAt(k); return new Blob([a], { type: 'image/png' }); };

  /* 그래프: interactive=false → 그림만 (팝업), true → 휠 확대·끌어서 이동·좌표 표시 (웹 안) */
  function figView(figs, interactive) {
    const box = document.createElement('div');
    box.className = 'lab-figbox';
    figs.forEach((f, idx) => {
      const fig = document.createElement('figure');
      const img = document.createElement('img');
      img.src = 'data:image/png;base64,' + f.png; img.alt = '그래프 ' + (idx + 1); img.draggable = false;
      const bar = document.createElement('div'); bar.className = 'lab-fbar2';
      const mk = (txt, fn) => { const b = document.createElement('button'); b.type = 'button'; b.className = 'ghost'; b.textContent = txt; b.onclick = fn; return b; };
      const coord = document.createElement('span'); coord.className = 'muted small lab-coord';
      const save = mk('💾 PNG 저장', () => saveBlob(dataUrlToBlob(img.src), 'figure' + (idx + 1) + '.png'));
      if (!interactive) { bar.append(save); fig.append(img, bar); box.appendChild(fig); return; }
      let busy = false, pend = null;
      async function send(p) {
        if (busy) { if (p.a === 'pan' && pend && pend.a === 'pan') { pend.dx += p.dx; pend.dy += p.dy; } else if (p.a !== 'pos') pend = p; return; }
        busy = true;
        const r = await reqEv('mpl', Object.assign({ n: f.n }, p));
        if (r && r.png) img.src = 'data:image/png;base64,' + r.png;
        if (r && r.txt !== undefined) coord.textContent = r.txt;
        if (r && r.err) coord.textContent = r.err;
        busy = false;
        if (pend) { const q = pend; pend = null; send(q); }
      }
      const mp = (e) => { const r = img.getBoundingClientRect(); return { x: (e.clientX - r.left) * img.naturalWidth / r.width, y: (e.clientY - r.top) * img.naturalHeight / r.height }; };
      const cx = () => ({ x: img.naturalWidth / 2, y: img.naturalHeight / 2 });
      bar.append(mk('＋', () => send(Object.assign({ a: 'zoom', f: 0.7 }, cx()))), mk('－', () => send(Object.assign({ a: 'zoom', f: 1.4 }, cx()))), mk('🏠 처음으로', () => send({ a: 'reset' })), save, coord);
      let down = null;
      img.addEventListener('wheel', (e) => { e.preventDefault(); send(Object.assign({ a: 'zoom', f: e.deltaY < 0 ? 0.8 : 1.25 }, mp(e))); }, { passive: false });
      img.addEventListener('pointerdown', (e) => { down = mp(e); img.setPointerCapture(e.pointerId); img.classList.add('grab'); });
      img.addEventListener('pointermove', (e) => {
        const q = mp(e);
        if (down) { send({ a: 'pan', x: down.x, y: down.y, dx: q.x - down.x, dy: q.y - down.y }); down = q; } else if (!busy) send(Object.assign({ a: 'pos' }, q));
      });
      const up = () => { down = null; img.classList.remove('grab'); };
      img.addEventListener('pointerup', up); img.addEventListener('pointercancel', up);
      const hint = document.createElement('div'); hint.className = 'muted small'; hint.textContent = '🖱️ 휠로 확대·축소 · 끌어서 이동 · 올려두면 좌표가 보여요';
      fig.append(bar, img, hint); box.appendChild(fig);
    });
    return box;
  }
  function figWindow(figs) {
    return openWin('📈 그래프 (Figure ' + figs.length + '개)', figView(figs, false), { w: 680 });
  }

  /* 터틀 그림 재생기: 파이썬이 기록한 명령을 캔버스에서 차례로 그려요.
     interactive=true 이면 키보드·마우스·타이머를 파이썬에 보내서 새 그림 명령을 받아 이어서 그려요. onErr(문장) 은 콜백 오류 표시용 */
  function turtleView(ops, interactive, onErr) {
    ops = ops.slice();
    const box = document.createElement('div');
    box.className = 'lab-turtle';
    box.innerHTML = `<canvas width="600" height="600"${interactive ? ' tabindex="0"' : ''}></canvas>${interactive ? '<div class="muted small lab-thint">🖱️ 그림을 한 번 클릭하면 키보드가 먹어요. (방향키·글자·클릭·끌기)</div>' : ''}<div class="lab-turtle-bar">${interactive ? '' : '<button type="button" class="ghost" data-a="replay">🔁 다시 그리기</button>'}<button type="button" class="ghost" data-a="skip">⏩ 바로 완성</button><button type="button" class="ghost" data-a="save">💾 PNG 저장</button></div>`;
    const canvas = box.querySelector('canvas'), ctx = canvas.getContext('2d');
    const W = 600, H = 600;
    const layer = document.createElement('canvas'); layer.width = W; layer.height = H;
    const lx = layer.getContext('2d');
    const HAS = { SP: 1, V: 1, A: 1, H: 1, G: 1, L: 1, F: 1, D: 1, W: 1, ST: 1 };
    const SPD = [1e9, 4, 8, 14, 20, 28, 40, 55, 75, 100, 140];
    let i = 0, partial = null, bg = 'white', tur = {}, instant = false, raf = 0, dead = false;
    const timers = new Set();
    const X = (x) => W / 2 + x, Y = (y) => H / 2 - y;
    const T = (id) => tur[id] || (tur[id] = { x: 0, y: 0, h: 0, show: true, shape: 'classic', sx: 1, sy: 1, pc: 'black', fc: 'black', sp: 3 });
    function reset() { cancelAnimationFrame(raf); raf = 0; i = 0; partial = null; bg = 'white'; tur = {}; instant = false; lx.clearRect(0, 0, W, H); }
    function sprite(c, t, x, y, h) {
      c.save(); c.translate(X(x), Y(y)); c.rotate(-h * Math.PI / 180); c.scale(t.sx, t.sy);
      c.fillStyle = t.fc; c.strokeStyle = t.pc; c.lineWidth = 1.5; c.beginPath();
      if (t.shape === 'circle') c.arc(0, 0, 10, 0, 6.2832);
      else if (t.shape === 'square') c.rect(-10, -10, 20, 20);
      else if (t.shape === 'triangle') { c.moveTo(10, 0); c.lineTo(-5, 8.66); c.lineTo(-5, -8.66); c.closePath(); }
      else if (t.shape === 'arrow') { c.moveTo(10, 0); c.lineTo(-10, 8); c.lineTo(-10, -8); c.closePath(); }
      else if (t.shape === 'turtle') { c.ellipse(0, 0, 11, 8, 0, 0, 6.2832); c.fill(); c.stroke(); c.beginPath(); c.arc(13, 0, 4, 0, 6.2832); }
      else { c.moveTo(10, 0); c.lineTo(-10, 6); c.lineTo(-6, 0); c.lineTo(-10, -6); c.closePath(); }
      c.fill(); c.stroke(); c.restore();
    }
    function apply(op) {
      switch (op[0]) {
        case 'bg': bg = op[1]; break;
        case 'I': instant = !!op[1]; break;
        case 'CLR': lx.clearRect(0, 0, W, H); break;
        case 'SP': T(op[1]).sp = op[2]; break;
        case 'V': T(op[1]).show = !!op[2]; break;
        case 'A': { const t = T(op[1]); t.shape = op[2]; t.sx = op[3]; t.sy = op[4]; t.pc = op[5]; t.fc = op[6]; break; }
        case 'H': T(op[1]).h = op[2]; break;
        case 'G': { const t = T(op[1]); t.x = op[2]; t.y = op[3]; break; }
        case 'L': { const t = T(op[1]); lx.strokeStyle = op[6]; lx.lineWidth = op[7]; lx.lineCap = 'round'; lx.beginPath(); lx.moveTo(X(op[2]), Y(op[3])); lx.lineTo(X(op[4]), Y(op[5])); lx.stroke(); t.x = op[4]; t.y = op[5]; break; }
        case 'F': lx.fillStyle = op[3]; lx.beginPath(); op[2].forEach((p, k) => (k ? lx.lineTo(X(p[0]), Y(p[1])) : lx.moveTo(X(p[0]), Y(p[1])))); lx.closePath(); lx.fill(); break;
        case 'D': lx.fillStyle = op[5]; lx.beginPath(); lx.arc(X(op[2]), Y(op[3]), op[4] / 2, 0, 6.2832); lx.fill(); break;
        case 'W': {
          const f = op[5] || ['Arial', 8, 'normal'];
          lx.fillStyle = op[6]; lx.font = (/bold/.test(f[2] || '') ? 'bold ' : '') + (/italic/.test(f[2] || '') ? 'italic ' : '') + Math.round((f[1] || 8) * 1.33) + 'px ' + (f[0] || 'Arial');
          lx.textAlign = op[7] === 'center' ? 'center' : op[7] === 'right' ? 'right' : 'left'; lx.fillText(op[4], X(op[2]), Y(op[3])); break;
        }
        case 'ST': sprite(lx, T(op[1]), op[2], op[3], op[4]); break;
        case 'T': box.dataset.title = op[1]; break;
        default: break;
      }
    }
    function render() {
      ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H); ctx.drawImage(layer, 0, 0);
      Object.keys(tur).forEach((k) => { const t = tur[k]; if (t.show) sprite(ctx, t, t.x, t.y, t.h); });
    }
    function frame() {
      if (dead) return;
      const t0 = performance.now();
      let budget = null;
      while (i < ops.length && performance.now() - t0 < 14) {
        const op = ops[i];
        const tt = HAS[op[0]] ? T(op[1]) : null;
        const per = instant || !tt ? 1e9 : SPD[Math.max(0, Math.min(10, Math.round(tt.sp)))];
        if (op[0] === 'L' && per < 1e9) {
          const len = Math.hypot(op[4] - op[2], op[5] - op[3]);
          if (len === 0) { apply(op); i++; continue; }
          if (!partial) partial = { d: 0 };
          if (budget === null) budget = per;
          const adv = Math.min(len - partial.d, budget);
          const a = partial.d / len, b = (partial.d + adv) / len;
          const x0 = op[2] + (op[4] - op[2]) * a, y0 = op[3] + (op[5] - op[3]) * a, x1 = op[2] + (op[4] - op[2]) * b, y1 = op[3] + (op[5] - op[3]) * b;
          lx.strokeStyle = op[6]; lx.lineWidth = op[7]; lx.lineCap = 'round'; lx.beginPath(); lx.moveTo(X(x0), Y(y0)); lx.lineTo(X(x1), Y(y1)); lx.stroke();
          tt.x = x1; tt.y = y1; partial.d += adv; budget -= adv;
          if (partial.d >= len - 1e-9) { tt.x = op[4]; tt.y = op[5]; partial = null; i++; }
          if (budget <= 0) break;
        } else {
          apply(op); i++;
          if (per < 1e9 && (op[0] === 'H' || op[0] === 'D' || op[0] === 'W')) { if (budget === null) budget = per; budget -= 4; if (budget <= 0) break; }
        }
      }
      render();
      if (i < ops.length) raf = requestAnimationFrame(() => { raf = 0; frame(); });
    }
    const kick = () => { if (!raf && !dead) raf = requestAnimationFrame(() => { raf = 0; frame(); }); };
    function finishNow() {
      cancelAnimationFrame(raf); raf = 0; partial = null;
      while (i < ops.length) { apply(ops[i]); i++; }
      render();
    }

    /* 상호작용: 이벤트를 파이썬으로 보내고, 돌아온 새 명령을 이어 붙여요 */
    const q = []; let pumping = false;
    function schedule(list) {
      list.forEach((op) => { if (op[0] === 'TM') { const h = setTimeout(() => { timers.delete(h); ev('timer', { id: op[1] }); }, Math.max(0, op[2])); timers.add(h); } });
    }
    function push(list) { ops.push(...list); schedule(list); kick(); }
    async function pump() {
      if (pumping) return;
      pumping = true;
      while (q.length && !dead) {
        const [k, p] = q.shift();
        const r = await reqEv(k, p);
        if (r) { if (r.err && onErr) onErr(r.err); if (r.ops && r.ops.length) push(r.ops); }
      }
      pumping = false;
    }
    function ev(kind, p) {
      if (dead || q.length > 60) return;
      if (kind === 'drag' && q.length && q[q.length - 1][0] === 'drag') q[q.length - 1] = [kind, p]; else q.push([kind, p]);
      pump();
    }
    if (interactive) {
      const KN = { ArrowUp: 'Up', ArrowDown: 'Down', ArrowLeft: 'Left', ArrowRight: 'Right', Enter: 'Return', ' ': 'space', Backspace: 'BackSpace' };
      const pt = (e) => { const r = canvas.getBoundingClientRect(); return { x: (e.clientX - r.left) * W / r.width - W / 2, y: H / 2 - (e.clientY - r.top) * H / r.height }; };
      const key = (e, ph) => { if (['Shift', 'Control', 'Alt', 'Meta', 'CapsLock'].includes(e.key)) return; e.preventDefault(); ev('key', { key: KN[e.key] || e.key, ph }); };
      canvas.addEventListener('keydown', (e) => key(e, 'down'));
      canvas.addEventListener('keyup', (e) => key(e, 'up'));
      let down = null;
      canvas.addEventListener('pointerdown', (e) => { canvas.focus(); down = { cx: e.clientX, cy: e.clientY, moved: false }; try { canvas.setPointerCapture(e.pointerId); } catch (er) { /* 무시 */ } ev('down', pt(e)); });
      canvas.addEventListener('pointermove', (e) => { if (!down) return; if (Math.hypot(e.clientX - down.cx, e.clientY - down.cy) > 5) down.moved = true; if (down.moved) ev('drag', pt(e)); });
      canvas.addEventListener('pointerup', (e) => { if (!down) return; const d = down; down = null; ev('up', pt(e)); if (!d.moved) ev('click', pt(e)); });
    }
    box.addEventListener('click', (e) => {
      const b = e.target.closest('[data-a]'); if (!b) return;
      if (b.dataset.a === 'replay') { reset(); frame(); }
      else if (b.dataset.a === 'skip') finishNow();
      else if (b.dataset.a === 'save') canvas.toBlob((bl) => bl && saveBlob(bl, 'turtle.png'));
    });
    box._dispose = () => { dead = true; cancelAnimationFrame(raf); timers.forEach(clearTimeout); timers.clear(); q.length = 0; };
    box._hasEvents = ops.some((o) => o[0] === 'TM' || o[0] === 'EVT');
    reset(); schedule(ops); frame();
    return box;
  }
  function turtleWindow(ops) {
    const box = turtleView(ops, false);
    const w = openWin('🐢 터틀 그림', box, { w: 640 });
    w._onClose = box._dispose;
    return w;
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

  async function pypiInfo(name) {
    try {
      const r = await fetch('https://pypi.org/pypi/' + encodeURIComponent(name) + '/json');
      if (!r.ok) return null;
      const j = await r.json();
      const i = j.info || {};
      const urls = j.urls || [];
      const wheels = urls.filter((u) => u.packagetype === 'bdist_wheel');
      const pure = wheels.some((u) => /-none-any\.whl$/.test(u.filename));
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
    ['🐢 turtle 그림 (팝업)', 'import turtle\n\nt = turtle.Turtle()\nt.speed(6)\nt.pensize(2)\ncolors = ["red", "orange", "gold", "green", "blue", "purple"]\nfor i in range(36):\n    t.pencolor(colors[i % 6])\n    t.circle(80)\n    t.left(10)\nt.hideturtle()\nturtle.done()\n'],
    ['📈 그래프 (팝업)', 'import numpy as np\nimport matplotlib.pyplot as plt\n\nx = np.linspace(0, 2 * np.pi, 200)\nplt.plot(x, np.sin(x), label="sin")\nplt.plot(x, np.cos(x), label="cos")\nplt.legend()\nplt.title("sin & cos")\nplt.show()\n'],
    ['📁 파일 쓰고 읽기', 'with open("메모.txt", "w", encoding="utf-8") as f:\n    f.write("안녕, 작업 공간!\\n")\n    f.write("이 파일은 오른쪽 작업 공간에서 내려받을 수 있어요.\\n")\n\nprint(open("메모.txt", encoding="utf-8").read())\n'],
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
      <div class="lab-warn">⚠️ <b>새로고침하거나 창을 닫으면 작업 공간의 파일과 설치한 패키지가 모두 사라져요.</b> 필요한 파일은 ⬇ 내려받아 두세요. (코드는 이 기기에 남아요)</div>
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
            <div class="lab-bar"><b>출력</b><span class="grow"></span><span class="muted small" id="labTime"></span><select id="labMode" class="lab-mode" title="그래프·터틀 결과를 보여주는 방식"><option value="popup">🪟 팝업</option><option value="inline">🧩 웹 안 (상호작용)</option></select><button class="link" id="labClear">지우기</button></div>
            <pre class="lab-out" id="labOut"><span class="lab-dim">▶ 실행을 누르면 결과가 여기에 나와요.</span></pre>
            <div class="lab-chips" id="labChips"></div>
          </div>
          <div class="card lab-card" id="labViewCard" hidden>
            <div class="lab-bar"><b>🖼 결과 화면</b><span class="muted small">상호작용 가능</span></div>
            <div id="labViewBody"></div>
          </div>
        </div>
        <aside class="lab-side">
          <div class="card lab-card" id="labFiles">
            <div class="lab-bar"><b>📁 내 작업 공간</b><span class="grow"></span><span class="muted small" id="labUse"></span></div>
            <div class="lab-meter"><i id="labMeter"></i></div>
            <p class="muted small" style="margin:6px 0 8px">파이썬 코드에서 <code>open("파일이름")</code> 으로 바로 읽고 써요. 이 기기의 메모리에만 있고 서버에는 저장되지 않아요.</p>
            <div class="lab-fbar">
              <button class="ghost" id="labNew" type="button">＋ 새 파일</button>
              <button class="ghost" id="labUp" type="button">⬆ 올리기</button>
              <button class="ghost" id="labZip" type="button">⬇ 전체 받기</button>
              <input type="file" id="labFile" multiple hidden>
            </div>
            <div class="lab-edit" id="labEdit" hidden>
              <input type="text" id="labEName" placeholder="파일 이름 (예: data.txt, 폴더/a.csv)">
              <textarea id="labEBody" rows="6" spellcheck="false" placeholder="내용"></textarea>
              <div class="lab-fbar"><button class="primary" id="labESave" type="button">저장</button><button class="ghost" id="labECancel" type="button">취소</button></div>
            </div>
            <div id="labList" class="lab-list"></div>
            <div class="lab-drop" id="labDrop">여기로 파일을 끌어다 놓아도 돼요</div>
          </div>
          <div class="card lab-card">
            <b>📦 패키지 검색 (PyPI)</b>
            <p class="muted small" style="margin:4px 0 8px">이름이나 하고 싶은 일로 검색해요. <code>import</code> 만 써도 없는 패키지는 알아서 설치해 줘요.</p>
            <div class="lab-sbox"><input type="text" id="labQ" placeholder="예) rich, 표, qrcode, sympy" autocomplete="off"><button class="primary" id="labSearch">검색</button></div>
            <div id="labRes" class="lab-res"><p class="muted small">검색어를 넣어보세요. 비워두고 검색하면 추천 목록이 나와요.</p></div>
          </div>
          <div class="card lab-card">
            <b>✅ 설치한 패키지</b>
            <div id="labInst" class="lab-inst"><span class="muted small">아직 없어요.</span></div>
            <p class="muted small" style="margin:8px 0 0">📌 을 누르면 <b>상시 설치</b>로 등록돼서 연구소를 열 때마다 자동으로 설치돼요. (설정 → 코드 입력창 탭에서 관리)</p>
          </div>
          <div class="card lab-card lab-note">
            <b>ℹ️ 알아두기</b>
            <ul class="small muted">
              <li>그래프(matplotlib)와 turtle 그림은 기본으로 팝업 창에 떠요(그림만). 출력 옆 선택이나 설정에서 <b>웹 안</b>으로 바꾸면 turtle 키보드·클릭·타이머, 그래프 확대·이동이 돼요.</li>
              <li>순수 파이썬 패키지는 거의 다 돼요. 컴파일이 필요한 패키지는 파이오다이드 기본 제공(numpy·pandas·scipy 등)만 돼요.</li>
              <li><code>requests</code> 같은 인터넷 접속, <code>tkinter</code>·pygame 같은 창(GUI)은 브라우저 제한으로 안 돼요. turtle 의 이벤트는 웹 안 모드에서만 돼요.</li>
              <li>무한 반복이면 <b>중지</b>를 눌러요. 파이썬이 새로 시작돼도 작업 공간 파일은 그대로예요.</li>
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
    const stateEl = $('#labState'), outEl = $('#labOut'), timeEl = $('#labTime'), chipsEl = $('#labChips');
    const runBtn = $('#labRun'), stopBtn = $('#labStop');
    let running = false, runId = 0, outLen = 0, t0 = 0, tick = null, last = { figs: [], turtle: [] }, pre = '';

    // 새로고침·닫기 경고
    const bu = (e) => { if (FS.size || [...installed.keys()].some((k) => !getLibs().includes(k))) { e.preventDefault(); e.returnValue = ''; return ''; } return undefined; };
    window.addEventListener('beforeunload', bu);
    const leave = () => { if (location.hash.replace(/^#\//, '').split('/')[0] !== 'lab') { window.removeEventListener('beforeunload', bu); window.removeEventListener('hashchange', leave); closeAllWins(); clearInline(); if (listener === onMsg) listener = null; } };
    window.addEventListener('hashchange', leave);

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
    const busy = (b) => { ['#labNew', '#labUp', '#labZip', '#labESave'].forEach((s) => { const e = $(s); if (e) e.disabled = b; }); $('#labList').classList.toggle('lock', b); };

    /* --- 설치한 패키지 --- */
    const renderInst = () => {
      const box = $('#labInst');
      const libs = getLibs().map(norm);
      if (!installed.size) { box.innerHTML = '<span class="muted small">아직 없어요.</span>'; markInstalled(); return; }
      box.innerHTML = [...installed].map(([n, tops]) => `<div class="lab-ipk"><b>${esc(n)}</b>${tops.length ? `<code>import ${esc(tops[0])}</code><button class="link" data-ins="${esc(tops[0])}">코드에 넣기</button>` : ''}<button class="link lab-pin${libs.includes(norm(n)) ? ' on' : ''}" data-pin="${esc(n)}" title="상시 설치 켜기/끄기">📌${libs.includes(norm(n)) ? ' 상시' : ''}</button></div>`).join('');
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

    /* --- 작업 공간 --- */
    const renderFiles = () => {
      const tot = fsTotal();
      $('#labUse').textContent = `${fmtSize(tot)} / ${fmtSize(Q_TOTAL)} · ${FS.size}개`;
      $('#labMeter').style.width = Math.min(100, tot / Q_TOTAL * 100) + '%';
      const names = [...FS.keys()].sort();
      $('#labList').innerHTML = names.length ? names.map((n) => `<div class="lab-fr"><span class="lab-fn" title="${esc(n)}">📄 ${esc(n)}</span><span class="muted small">${fmtSize(FS.get(n).length)}</span><span class="lab-fa"><button class="link" data-fdl="${esc(n)}" title="내려받기">⬇</button><button class="link" data-fed="${esc(n)}" title="보기·고치기">✏️</button><button class="link danger" data-frm="${esc(n)}" title="지우기">🗑</button></span></div>`).join('') : '<p class="muted small" style="margin:8px 0 0">아직 파일이 없어요. ＋ 새 파일이나 ⬆ 올리기로 시작해요.</p>';
    };
    const fsErr = (m) => { setState(m, 'bad'); setTimeout(() => { if (!running) setState('준비 완료', 'ok'); }, 4000); };
    const addFiles = async (list) => {
      const errs = [];
      for (const f of list) { const e = fsPut(f.name, new Uint8Array(await f.arrayBuffer())); if (e) errs.push(e); }
      renderFiles();
      if (errs.length) fsErr(errs[0]);
    };
    const isText = (u) => { try { const s = new TextDecoder('utf-8', { fatal: true }).decode(u); return s.indexOf('\u0000') < 0; } catch (e) { return false; } };
    let editing = null;
    const openEdit = (name, body) => { editing = name; $('#labEdit').hidden = false; $('#labEName').value = name || ''; $('#labEBody').value = body || ''; $('#labEName').focus(); };
    $('#labNew').onclick = () => openEdit('', '');
    $('#labECancel').onclick = () => { $('#labEdit').hidden = true; editing = null; };
    $('#labESave').onclick = () => {
      const name = cleanPath($('#labEName').value);
      if (!name) { fsErr('파일 이름이 올바르지 않아요'); return; }
      const e = fsPut(name, new TextEncoder().encode($('#labEBody').value));
      if (e) { fsErr(e); return; }
      if (editing && editing !== name) FS.delete(editing);
      $('#labEdit').hidden = true; editing = null; renderFiles();
    };
    $('#labUp').onclick = () => $('#labFile').click();
    $('#labFile').onchange = (e) => { addFiles([...e.target.files]); e.target.value = ''; };
    $('#labZip').onclick = () => { if (!FS.size) { fsErr('내려받을 파일이 없어요'); return; } saveBlob(makeZip([...FS].sort((a, b) => (a[0] < b[0] ? -1 : 1))), 'workspace.zip'); };
    $('#labList').addEventListener('click', (e) => {
      const dl = e.target.closest('[data-fdl]'), ed = e.target.closest('[data-fed]'), rm = e.target.closest('[data-frm]');
      if (dl) saveBlob(new Blob([FS.get(dl.dataset.fdl)]), dl.dataset.fdl.split('/').pop());
      else if (ed) { const u = FS.get(ed.dataset.fed); if (isText(u)) openEdit(ed.dataset.fed, new TextDecoder().decode(u)); else fsErr('글자 파일이 아니어서 볼 수 없어요. ⬇ 로 받아 보세요'); }
      else if (rm) { FS.delete(rm.dataset.frm); renderFiles(); }
    });
    const drop = $('#labDrop'), card = $('#labFiles');
    ['dragenter', 'dragover'].forEach((t) => card.addEventListener(t, (e) => { e.preventDefault(); drop.classList.add('on'); }));
    ['dragleave', 'drop'].forEach((t) => card.addEventListener(t, (e) => { e.preventDefault(); drop.classList.remove('on'); }));
    card.addEventListener('drop', (e) => { if (!running && e.dataTransfer && e.dataTransfer.files.length) addFiles([...e.dataTransfer.files]); });

    /* --- 결과 창 --- */
    let inlineDisp = [];
    const clearInline = () => { inlineDisp.forEach((f) => f()); inlineDisp = []; $('#labViewBody').innerHTML = ''; $('#labViewCard').hidden = true; };
    const onTurtleErr = (m) => append('\n' + m + '\n', 'lab-err');
    const showResults = (figs, turtle) => {
      last = { figs, turtle };
      closeAllWins(); clearInline();
      const inline = getMode() === 'inline';
      if (inline) {
        if (!turtle.length && !figs.length) return;
        const body = $('#labViewBody');
        if (turtle.length) { const t = turtleView(turtle, true, onTurtleErr); inlineDisp.push(t._dispose); body.appendChild(t); }
        if (figs.length) body.appendChild(figView(figs, true));
        $('#labViewCard').hidden = false;
        chipsEl.innerHTML = '';
        return;
      }
      if (turtle.length) {
        const w = turtleWindow(turtle);
        if (w.querySelector('.lab-turtle') && w.querySelector('.lab-turtle')._hasEvents) append('\n💡 이 그림은 키보드·마우스·타이머를 써요. 팝업에서는 움직이지 않아요. 출력 옆 선택(또는 설정)에서 "웹 안"으로 바꾸면 움직여요.\n', 'lab-dim');
      }
      if (figs.length) figWindow(figs);
      chipsEl.innerHTML = (turtle.length ? '<button class="ghost" data-open="t">🐢 터틀 창 다시 열기</button>' : '') + (figs.length ? '<button class="ghost" data-open="f">📈 그래프 창 다시 열기</button>' : '');
    };
    chipsEl.addEventListener('click', (e) => {
      const b = e.target.closest('[data-open]'); if (!b) return;
      if (b.dataset.open === 't') turtleWindow(last.turtle); else figWindow(last.figs);
    });

    const onMsg = (d) => {
      if (!v.isConnected) return;
      if (d.t === 'out') append(d.s, d.bad ? 'lab-err' : '');
      else if (d.t === 'log') append(d.s + '\n', d.bad ? 'lab-err' : 'lab-dim');
      else if (d.t === 'pkg') renderInst();
      else if (d.t === 'preload') {
        if (d.done) { if (!running) setState('준비 완료', 'ok'); renderInst(); } else setState(`상시 패키지 설치 중 (${d.i}/${d.n}) ${d.name}`, 'busy');
      } else if (d.t === 'done' && d.id === runId) finish(d);
    };
    listener = onMsg;

    function finish(d) {
      running = false; clearInterval(tick);
      runBtn.disabled = false; stopBtn.hidden = true; busy(false);
      if (d.files) { FS.clear(); d.files.forEach(([p, b]) => FS.set(p, new Uint8Array(b))); renderFiles(); }
      if (d.err) { append((outLen && !outEl.textContent.endsWith('\n') ? '\n' : '') + d.err + '\n', 'lab-err'); setState('오류가 났어요', 'bad'); }
      else setState('끝! ✨', 'ok');
      if (d.over) { append(`\n⚠️ 작업 공간(${fmtSize(Q_TOTAL)})을 넘어서 이번 실행에서 만든 파일은 저장하지 못했어요. (${fmtSize(d.over)})\n`, 'lab-err'); }
      if (outLen === 0) outEl.innerHTML = '<span class="lab-dim">(출력 없음)</span>';
      showResults(d.figs || [], d.turtle || []);
      timeEl.textContent = ((d.ms || 0) / 1000).toFixed(2) + '초';
    }

    async function run() {
      if (running) return;
      const code = ta.value;
      lsSet(KEY_CODE, code); lsSet(KEY_STDIN, $('#labIn').value);
      if (/\binput\s*\(/.test(code) && !$('#labIn').value.trim()) $('.lab-stdin').open = true;
      outEl.textContent = ''; outLen = 0; chipsEl.innerHTML = ''; timeEl.textContent = '';
      closeAllWins(); clearInline();
      running = true; runBtn.disabled = true; stopBtn.hidden = false; busy(true);
      t0 = Date.now();
      setState('파이썬 준비 중…', 'busy');
      try { await ensureReady(); } catch (e) { running = false; runBtn.disabled = false; stopBtn.hidden = true; busy(false); append(String(e.message || e) + '\n', 'lab-err'); setState('불러오기 실패', 'bad'); return; }
      if (!running) return;
      listener = onMsg;
      const id = ++seq; runId = id;
      tick = setInterval(() => { timeEl.textContent = ((Date.now() - t0) / 1000).toFixed(0) + '초째…'; }, 500);
      setState('실행 중…', 'busy');
      W.w.postMessage({ t: 'run', id, code, stdin: $('#labIn').value, files: [...FS], inline: getMode() === 'inline' });
    }
    function stop() {
      if (!running) return;
      killWorker();
      running = false; clearInterval(tick); runBtn.disabled = false; stopBtn.hidden = true; busy(false);
      append('\n⏹ 중지했어요. (파이썬이 새로 시작돼요. 이번 실행에서 만든 파일은 저장되지 않았어요)\n', 'lab-err');
      setState('중지됨', 'bad'); timeEl.textContent = '';
      renderInst();
      ensureReady().then(() => { if (!running) setState('준비 완료', 'ok'); }).catch(() => {});
    }

    runBtn.onclick = run;
    stopBtn.onclick = stop;
    ta.addEventListener('keydown', (e) => { if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); run(); } });
    ta.addEventListener('input', () => lsSet(KEY_CODE, ta.value));
    $('#labClear').onclick = () => { outEl.innerHTML = '<span class="lab-dim">▶ 실행을 누르면 결과가 여기에 나와요.</span>'; outLen = 0; chipsEl.innerHTML = ''; timeEl.textContent = ''; };
    $('#labEx').onchange = (e) => {
      const i = e.target.value; if (i === '') return;
      const ex = EXAMPLES[+i];
      ta.value = ex[1]; ta.dispatchEvent(new Event('input', { bubbles: true })); lsSet(KEY_CODE, ta.value); e.target.value = '';
      if (ex[2] != null) { $('#labIn').value = ex[2]; $('.lab-stdin').open = true; }
    };

    /* --- 검색 --- */
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
        const same = r.list.find((p) => norm(p.name) === norm(ex.name));
        if (!same || !same.builtin) parts.push('<div class="lab-sec">PyPI 에서 찾았어요</div>' + row({ name: ex.name, version: ex.version, desc: ex.desc, home: ex.home, builtin: !!(same && same.builtin), imports: same ? same.imports : [] }, ex.pure ? 'pure' : 'maybe'));
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
      try { await ensureReady(); } catch (er) { b.disabled = false; b.textContent = '설치'; append(String(er.message || er) + '\n', 'lab-err'); return; }
      listener = onMsg;
      const d = await reqInstall(name, false);
      if (d.ok) { b.textContent = '설치됨 ✓'; const t = installed.get(name) || []; if (t[0]) b.insertAdjacentHTML('afterend', `<button class="ghost" data-use="${esc(t[0])}">import ${esc(t[0])} 넣기</button>`); renderInst(); }
      else { b.disabled = false; b.textContent = '다시 시도'; }
    });
    v.addEventListener('click', (e) => {
      const i = e.target.closest('[data-ins]'); if (i) { insertImport(i.dataset.ins); return; }
      const p = e.target.closest('[data-pin]');
      if (p) {
        const n = p.dataset.pin, libs = getLibs();
        const k = libs.findIndex((x) => norm(x) === norm(n));
        if (k >= 0) libs.splice(k, 1); else if (libs.length >= LIB_MAX) { fsErr(`상시 설치는 ${LIB_MAX}개까지예요`); return; } else libs.push(n);
        setLibs(libs); renderInst();
      }
    });

    $('#labMode').value = getMode();
    $('#labMode').onchange = (e) => setMode(e.target.value);
    renderInst(); renderFiles();
    setState('파이썬 깨우는 중…', 'busy');
    ensureReady().then(() => { if (v.isConnected && !running) setState('준비 완료', 'ok'); }).catch(() => { if (v.isConnected) setState('불러오기 실패', 'bad'); });
  }

  /* ---------- 설정 화면: 상시 설치 패키지 ---------- */
  function bindSettings(el, toast) {
    if (!el) return;
    const say = toast || (() => {});
    const draw = () => {
      const libs = getLibs();
      const mode = getMode();
      el.innerHTML = `<h3>🔬 연구소 설정</h3>
        <b>그래프·터틀 결과를 보여주는 방식</b>
        <label class="inline ideopt"><input type="radio" name="labView" value="popup" ${mode === 'popup' ? 'checked' : ''}> <span><b>🪟 팝업 창 (기본)</b><br><span class="muted small">따로 뜬 창에 그림만 보여줘요. 끌어서 옮길 수 있어요. 상호작용은 없어요.</span></span></label>
        <label class="inline ideopt"><input type="radio" name="labView" value="inline" ${mode === 'inline' ? 'checked' : ''}> <span><b>🧩 웹 페이지 안 (상호작용)</b><br><span class="muted small">출력 아래에 결과 화면이 생겨요. turtle 은 방향키·글자·클릭·끌기·ontimer 가 움직이고, 그래프는 휠 확대·끌어서 이동·좌표 표시가 돼요.</span></span></label>
        <h3 style="margin-top:18px">📦 상시 설치 패키지</h3>
        <p class="muted small">여기에 넣은 패키지는 연구소(연구 탭)를 열 때마다 자동으로 설치돼요. 새로고침하면 설치한 패키지가 사라지니까, 늘 쓰는 것만 등록해 두세요. (최대 ${LIB_MAX}개 · 이 기기에 저장 · 많을수록 시작이 느려져요)</p>
        <div class="lab-sbox"><input type="text" id="labLibIn" placeholder="패키지 이름 (예: rich, sympy, python-dateutil)" autocomplete="off"><button class="primary" id="labLibAdd" type="button">추가</button></div>
        <p class="small muted" id="labLibMsg" style="margin:6px 0 0"></p>
        <div class="lab-libs">${libs.length ? libs.map((n) => `<span class="lab-chip">${esc(n)} <button class="link danger" type="button" data-rm="${esc(n)}" aria-label="${esc(n)} 빼기">✕</button></span>`).join('') : '<span class="muted small">아직 없어요.</span>'}</div>`;
      el.querySelectorAll('[name=labView]').forEach((r) => { r.onchange = () => { if (r.checked) { setMode(r.value); say(r.value === 'inline' ? '웹 안에 보여줄게요' : '팝업으로 보여줄게요'); } }; });
      const msg = el.querySelector('#labLibMsg');
      el.querySelector('#labLibAdd').onclick = async () => {
        const name = el.querySelector('#labLibIn').value.trim().replace(/^pip\s+install\s+/i, '');
        if (!name) return;
        const cur = getLibs();
        if (cur.some((x) => norm(x) === norm(name))) { msg.textContent = '이미 등록돼 있어요.'; return; }
        if (cur.length >= LIB_MAX) { msg.textContent = `최대 ${LIB_MAX}개까지예요.`; return; }
        msg.textContent = '확인하는 중…';
        const lock = await loadLock();
        const builtin = lock.some((p) => norm(p.name) === norm(name));
        const info = builtin ? { pure: true } : await pypiInfo(name);
        if (!info) { msg.textContent = 'PyPI 에서 그 이름을 못 찾았어요. 철자를 확인해 주세요.'; return; }
        cur.push(name); setLibs(cur);
        say(builtin || info.pure ? '등록했어요' : '등록했어요 (컴파일이 필요해서 설치가 안 될 수도 있어요)');
        draw();
      };
      el.querySelector('#labLibIn').addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); el.querySelector('#labLibAdd').click(); } });
      el.querySelectorAll('[data-rm]').forEach((b) => { b.onclick = () => { setLibs(getLibs().filter((x) => x !== b.dataset.rm)); draw(); }; });
    };
    draw();
  }

  window.PYLAB = { page, bindSettings, libs: getLibs };
})();
