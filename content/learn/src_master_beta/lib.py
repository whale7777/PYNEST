import subprocess, sys, json, re
def run(code, stdin=''):
    r = subprocess.run([sys.executable, '-I', '-c', code], input=stdin, capture_output=True, text=True, timeout=10)
    if r.returncode != 0: raise RuntimeError(r.stderr[-600:] + '\n--- code ---\n' + code + '\n--- stdin ---\n' + stdin)
    return '\n'.join(l.rstrip() for l in r.stdout.rstrip().split('\n'))
def nl(s): return s if s == '' or s.endswith('\n') else s + '\n'
# ---------- 설명 블록 ----------
def T(b): return {'type': 'text', 'body': b}
def C(c, title='', stdin='', runnable=True):
    run(c, nl(stdin)); d = {'type': 'code', 'code': c}
    if title: d['title'] = title
    if stdin: d['stdin'] = stdin
    if not runnable: d['run'] = False
    return d
def CX(c, title=''):  # 일부러 오류 나는 코드 (실행 검증 안 함)
    d = {'type': 'code', 'code': c};
    if title: d['title'] = title
    return d
def call(style, body, title=''):
    d = {'type': 'callout', 'style': style, 'body': body}
    if title: d['title'] = title
    return d
key = lambda b, t='': call('key', b, t); tip = lambda b, t='': call('tip', b, t); warn = lambda b, t='': call('warn', b, t); exam = lambda b, t='': call('exam', b, t); think = lambda b, t='': call('think', b, t)
def cmp(lt, lc, rt, rc, lb='', rb='', tones=('good', 'bad')):
    return {'type': 'compare', 'left': {'title': lt, 'code': lc, 'body': lb, 'tone': tones[0]}, 'right': {'title': rt, 'code': rc, 'body': rb, 'tone': tones[1]}}
def tabs(*ts): return {'type': 'tabs', 'tabs': [{'title': t[0], 'body': t[1], 'code': t[2] if len(t) > 2 else ''} for t in ts]}
def flip(*cs): return {'type': 'flip', 'cards': [list(c) for c in cs]}
def rev(label, body='', code=''): return {'type': 'reveal', 'label': label, 'body': body, 'code': code}
def steps(*it): return {'type': 'steps', 'items': [x if isinstance(x, str) else {'title': x[0], 'body': x[1]} for x in it]}
def trace(code, title='', stdin=''):
    run(code, nl(stdin)); d = {'type': 'trace', 'code': code, 'frames': []}
    if title: d['title'] = title
    if stdin: d['stdin'] = stdin
    return d
def idx(name, value): return {'type': 'index', 'name': name, 'value': value}
def slc(name, value, a='', b='', c=''): return {'type': 'slice', 'name': name, 'value': value, 'start': a, 'stop': b, 'step': c}
def explain(title, *parts): return {'type': 'explain', 'title': title, 'parts': [list(p) for p in parts]}
def review(title, *parts): return {'type': 'review', 'title': title, 'parts': [list(p) for p in parts]}
# ---------- 확인 문제 ----------
def _q(kind, q, ex, **kw):
    d = {'type': 'quiz', 'kind': kind, 'question': q, **kw}
    if ex: d['explanation'] = ex
    return d
def ox(q, a, ex='', **kw): return _q('ox', q, ex, answer=a, **kw)
def ch(q, opts, a, ex='', **kw): return _q('choice', q, ex, options=opts, answer=a, **kw)
def sh(q, a, ex='', alts=(), **kw): return _q('short', q, ex, answer=str(a), alts=[str(x) for x in alts], **kw)
def fill(q, code, answers, ex='', stdin=None, expect=None, **kw):
    full = code
    for a in answers: full = full.replace('___', a[0] if isinstance(a, list) else a, 1)
    o = run(full, nl(stdin or ''))
    if expect is not None: assert o == expect, (o, expect)
    return _q('fill', q, ex, code=code, answers=[a if isinstance(a, list) else [a] for a in answers], **kw)
def match(q, pairs, ex='', **kw): return _q('match', q, ex, pairs=[list(p) for p in pairs], **kw)
def order(q, items, ex='', code=True, stdin='', **kw):
    if code: run('\n'.join(items), nl(stdin))
    return _q('order', q, ex, items=items, **({} if code or kw.get('mono') else {'mono': False}), **{k: v for k, v in kw.items() if k != 'mono'})
def bucket(q, cats, items, ex='', **kw): return _q('bucket', q, ex, categories=cats, items=[list(i) for i in items], **kw)
def outq(q, code, ex='', stdin='', **kw):
    a = run(code, nl(stdin)); assert a.strip(), code
    return _q('output', q, ex, code=code, answer=a, **kw)
def spot(q, code, a, ex='', **kw): return _q('spot', q, ex, code=code, answer=a, **kw)
def essay(q, model, rubric, ex='', **kw): return _q('essay', q, ex, model=model, rubric=rubric, **kw)
def io_block(title, i, o):
    return '```io ' + title + '\n' + ''.join('>>> ' + l + '\n' for l in i.rstrip('\n').split('\n') if i) + o + '\n```'
def prac(title, body, solution, inputs, starter='', hints=(), ex='', show=2):
    tests = []
    for k, i in enumerate(inputs):
        i = nl(i); o = run(solution, i); assert o.strip(), (title, i)
        tests.append({'input': i, 'output': o, 'hidden': k >= show})
    assert len({t['output'] for t in tests}) > 1 or len(tests) == 1, title
    if starter:
        try: assert any(run(starter, t['input']) != t['output'] for t in tests), title
        except RuntimeError: pass
    body = body + '\n\n' + '\n\n'.join(io_block(f'실행 예시 {k+1}', t['input'], t['output']) for k, t in enumerate(tests[:show]))
    return {'type': 'practice', 'title': title, 'body': body, 'starter': starter, 'tests': tests, 'hints': list(hints), 'solution': solution, 'explanation': ex, 'stdin': tests[0]['input']}
def lesson(title, minutes, summary, *steps_):
    return {'title': title, 'minutes': minutes, 'summary': summary, 'steps': list(steps_)}
