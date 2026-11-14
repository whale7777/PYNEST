"""L.O.T.C. 학습 코스 빌더 (pynest-learn-v2).

모든 출력(output 문제 정답, practice 테스트, reveal_run)은 여기서 python3 로 실제 실행해 만든다.
사용: from lotc import *  →  C = Course(...) → L = C.lesson(...) → L.xxx(...) → C.save(path)
"""
import json, os, re, subprocess, sys, tempfile

PY = sys.executable
ERRORS = []


def run(code, stdin='', timeout=10, files=None):
    """code 를 새 python 프로세스에서 실행 → (stdout, stderr, returncode)"""
    with tempfile.TemporaryDirectory() as d:
        for name, text in (files or {}).items():
            with open(os.path.join(d, name), 'w', encoding='utf-8') as f:
                f.write(text)
        p = os.path.join(d, 'main.py')
        with open(p, 'w', encoding='utf-8') as f:
            f.write(code)
        try:
            r = subprocess.run([PY, '-I', p], input=stdin, capture_output=True, text=True, timeout=timeout, cwd=d)
        except subprocess.TimeoutExpired:
            return '', 'TIMEOUT', -1
        return r.stdout, r.stderr, r.returncode


def norm(t):
    return '\n'.join(l.rstrip() for l in t.replace('\r', '').split('\n')).rstrip('\n')


def must_run(code, stdin='', where='', expect_error=False, files=None):
    out, err, rc = run(code, stdin, files=files)
    if expect_error:
        if rc == 0:
            ERRORS.append(f'{where}: 오류가 나야 하는데 정상 실행됨')
    elif rc != 0:
        ERRORS.append(f'{where}: 실행 오류\n{code}\n---\n{err[-600:]}')
    return out, err


# ---------------- 설명 블록 ----------------
def T(body):
    return {'type': 'text', 'body': body}


def CODE(code, title='', stdin='', run_=True, expect_error=False, files=None):
    must_run(code, stdin, f'code 블록 "{title or code[:30]}"', expect_error, files)
    b = {'type': 'code', 'code': code}
    if title: b['title'] = title
    if stdin: b['stdin'] = stdin
    if not run_: b['run'] = False
    return b


def CALL(style, body, title=''):
    b = {'type': 'callout', 'style': style, 'body': body}
    if title: b['title'] = title
    return b


TIP = lambda body, title='': CALL('tip', body, title)
WARN = lambda body, title='': CALL('warn', body, title)
KEY = lambda body, title='': CALL('key', body, title)
EXAM = lambda body, title='': CALL('exam', body, title)
THINK = lambda body, title='': CALL('think', body, title)


def side(title='', body='', code='', tone='', expect_error=False, check=True):
    if code and check:
        must_run(code, '', f'compare "{title}"', expect_error)
    d = {'title': title}
    if body: d['body'] = body
    if code: d['code'] = code
    if tone: d['tone'] = tone
    return d


def CMP(left, right):
    return {'type': 'compare', 'left': left, 'right': right}


def TABS(*tabs):
    out = []
    for t in tabs:
        title, body, code = (list(t) + ['', ''])[:3]
        if code: must_run(code, '', f'tabs "{title}"')
        d = {'title': title}
        if body: d['body'] = body
        if code: d['code'] = code
        out.append(d)
    return {'type': 'tabs', 'tabs': out}


def FLIP(*cards):
    return {'type': 'flip', 'cards': [list(c) for c in cards]}


def REVEAL(label, body='', code=''):
    d = {'type': 'reveal', 'label': label}
    if body: d['body'] = body
    if code: d['code'] = code
    return d


def REVEAL_RUN(label, code, body='', stdin='', files=None):
    """code 를 실행한 출력 결과를 정답으로 보여 준다."""
    out, _ = must_run(code, stdin, f'reveal "{label}"', files=files)
    shown = norm(out)
    d = {'type': 'reveal', 'label': label, 'code': shown}
    b = (body + '\n\n' if body else '') + '실행 결과 👇'
    d['body'] = b
    return d


def STEPS(*items):
    return {'type': 'steps', 'items': [i if isinstance(i, str) else {'title': i[0], 'body': i[1]} for i in items]}


def TRACE(code, title='', stdin='', notes=None):
    out, err = must_run(code, stdin, f'trace "{title}"')
    n = len(code.split('\n'))
    if n > 25:
        ERRORS.append(f'trace "{title}" 너무 김({n}줄)')
    d = {'type': 'trace', 'code': code, 'frames': []}
    if title: d['title'] = title
    if stdin: d['stdin'] = stdin
    if notes: d['notes'] = {str(k): v for k, v in notes.items()}
    return d


def IDX(name, value):
    return {'type': 'index', 'name': name, 'value': value}


def SLC(name, value, start=None, stop=None, step=None):
    d = {'type': 'slice', 'name': name, 'value': value}
    if start is not None: d['start'] = start
    if stop is not None: d['stop'] = stop
    if step is not None: d['step'] = step
    return d


# ---------------- 레슨 ----------------
class Lesson:
    def __init__(self, course, title, minutes, summary):
        self.course, self.title, self.minutes, self.summary = course, title, minutes, summary
        self.steps = []

    def _w(self, m):
        return f'[{self.course.letter}] "{self.title}" {len(self.steps) + 1}단계: {m}'

    def review(self, title, *parts):
        self.steps.append({'type': 'review', 'title': title, 'parts': [list(p) for p in parts]})
        return self

    def explain(self, title, *parts):
        self.steps.append({'type': 'explain', 'title': title, 'parts': [list(p) for p in parts]})
        return self

    def _q(self, kind, question, explanation, review=False, **kw):
        d = {'type': 'quiz', 'kind': kind, 'question': question}
        d.update(kw)
        if explanation: d['explanation'] = explanation
        if review: d['review'] = True
        self.steps.append(d)
        return self

    def ox(self, q, answer, expl, review=False):
        return self._q('ox', q, expl, review, answer=bool(answer))

    def choice(self, q, options, answer, expl, review=False):
        return self._q('choice', q, expl, review, options=options, answer=answer)

    def short(self, q, answer, expl, alts=None, review=False, check_code=None, stdin=''):
        """check_code 를 주면 실행 출력(strip)이 answer 와 같은지 검사"""
        if check_code is not None:
            out, _ = must_run(check_code, stdin, self._w('short check'))
            if norm(out).strip() != str(answer).strip():
                ERRORS.append(self._w(f'short 정답 불일치: 실행={norm(out)!r} 정답={answer!r}'))
        d = dict(answer=str(answer))
        if alts: d['alts'] = alts
        return self._q('short', q, expl, review, **d)

    def fill(self, q, code, answers, expl, review=False, expect=None, stdin='', expect_error=False):
        """expect 를 주면: 빈칸을 첫 정답으로 채워 실행한 출력이 expect 와 같은지 검사
        (expect=True 면 오류 없이 실행되는지만)"""
        if expect is not None:
            filled = code
            for a in answers:
                filled = filled.replace('___', a[0] if isinstance(a, list) else a, 1)
            out, _ = must_run(filled, stdin, self._w('fill check'), expect_error=expect_error)
            if expect is not True and norm(out) != norm(expect):
                ERRORS.append(self._w(f'fill 출력 불일치: 실행={norm(out)!r} 기대={expect!r}'))
        answers = [a if isinstance(a, list) else [a] for a in answers]
        return self._q('fill', q, expl, review, code=code, answers=answers)

    def match(self, q, pairs, expl, review=False):
        return self._q('match', q, expl, review, pairs=[list(p) for p in pairs])

    def order(self, q, items, expl, review=False, mono=True, check=False, expect=None, stdin=''):
        if check:
            out, _ = must_run('\n'.join(items), stdin, self._w('order check'))
            if expect is not None and norm(out) != norm(expect):
                ERRORS.append(self._w(f'order 출력 불일치: {norm(out)!r} vs {expect!r}'))
        d = dict(items=items)
        if not mono: d['mono'] = False
        return self._q('order', q, expl, review, **d)

    def bucket(self, q, categories, items, expl, review=False):
        return self._q('bucket', q, expl, review, categories=categories, items=[list(i) for i in items])

    def output(self, q, code, expl, review=False, stdin='', alts=None, run_code=None, files=None):
        """정답 = code 를 실제 실행한 출력. 해설의 {out} 은 출력으로 바뀜.
        run_code: 화면 code 와 다른 실제 실행 코드(예: input 대신 값 고정)"""
        out, _ = must_run(run_code or code, stdin, self._w('output'), files=files)
        ans = norm(out)
        if not ans.strip():
            ERRORS.append(self._w('output 정답이 비었음'))
        d = dict(code=code, answer=ans)
        if alts: d['alts'] = alts
        return self._q('output', q, (expl or '').replace('{out}', ans), review, **d)

    def spot(self, q, code, answer, expl, review=False, error_line=None, stdin=''):
        """error_line 을 주면 실행했을 때 그 줄에서 예외가 나는지 검사"""
        if error_line is not None:
            out, err, rc = run(code, stdin)
            m = re.findall(r'line (\d+)', err)
            if rc == 0 or not m or int(m[-1]) != error_line:
                ERRORS.append(self._w(f'spot 오류 줄 불일치: rc={rc} err={err[-200:]!r}'))
        return self._q('spot', q, expl, review, code=code, answer=answer)

    def essay(self, q, model, rubric, review=False):
        return self._q('essay', q, '', review, model=model, rubric=rubric)

    def practice(self, title, body, starter, solution, inputs, hidden, hints, explanation,
                 starter_may_pass=False, mode=None):
        """inputs/hidden: 입력 문자열 목록. 출력은 solution 실행으로 생성.
        body 의 {ex} → 첫 공개 테스트 실행예시, {ex2} → 두 번째."""
        tests = []
        where = f'[{self.course.letter}] "{self.title}" 실습 "{title}"'
        for hid, lst in ((False, inputs), (True, hidden)):
            for inp in lst:
                if inp and not inp.endswith('\n'): inp += '\n'
                out, err, rc = run(solution, inp)
                if rc != 0:
                    ERRORS.append(f'{where}: solution 오류 입력={inp!r}\n{err[-500:]}')
                t = {'input': inp, 'output': norm(out)}
                if hid: t['hidden'] = True
                if mode: t['mode'] = mode
                tests.append(t)
        if not starter_may_pass:
            ok_all = True
            for t in tests:
                out, err, rc = run(starter, t['input'])
                if rc != 0 or norm(out) != t['output']:
                    ok_all = False
                    break
            if ok_all:
                ERRORS.append(f'{where}: starter 가 모든 테스트를 통과함')
        vis = [t for t in tests if not t.get('hidden')]

        def ex(t, k):
            i = t['input'].rstrip('\n') or '(입력 없음)'
            return f'**[실행예시 {k}]**\n\n입력\n```\n{i}\n```\n출력\n```\n{t["output"]}\n```'
        if '{ex}' in body: body = body.replace('{ex}', ex(vis[0], 1))
        if '{ex2}' in body: body = body.replace('{ex2}', ex(vis[1], 2))
        if '{ex3}' in body: body = body.replace('{ex3}', ex(vis[2], 3))
        self.steps.append({'type': 'practice', 'title': title, 'body': body, 'starter': starter,
                           'tests': tests, 'hints': hints, 'solution': solution, 'explanation': explanation})
        return self

    def check(self):
        w = lambda m: ERRORS.append(f'[{self.course.letter}] "{self.title}": {m}')
        qs = [s for s in self.steps if s['type'] == 'quiz']
        ps = [s for s in self.steps if s['type'] == 'practice']
        if len(qs) < 6: w(f'확인 문제 {len(qs)}개 (<6)')
        if not ps: w('practice 없음')
        if len(self.steps) > 120: w('단계 120 초과')
        kinds = {s['kind'] for s in qs}
        if kinds <= {'ox', 'choice'}: w('ox/choice 만 있음')
        for s in self.steps:
            if s['type'] in ('explain', 'review'):
                for p in s['parts']:
                    tools = [b for b in p if b['type'] != 'text']
                    for b in p:
                        if b['type'] == 'text' and b['body'].count('\n') > 9:
                            w(f'"{s.get("title")}" 글 묶음이 너무 김')

    def data(self):
        return {'title': self.title, 'minutes': self.minutes, 'summary': self.summary, 'steps': self.steps}


class Course:
    def __init__(self, letter, scope_text):
        self.letter = letter
        self.title = f'L.O.T.C. [{letter}]'
        self.description = ('L.O.T.C. : Logic of Test Completion (시험 완성의 논리)\n'
                            '정보 시험의 완전 분석과 설명을 담았습니다.\n'
                            f'{letter}단계에서는 ({scope_text})의 내용을 담았습니다. '
                            '개념은 L.O.T.C., 실전은 ACE 문제집을 풀어 공부해주세요!')
        self.lessons = []

    def lesson(self, title, minutes, summary):
        L = Lesson(self, title, minutes, summary)
        self.lessons.append(L)
        return L

    def save(self, path):
        for i, L in enumerate(self.lessons):
            L.check()
            if i > 0 and L.steps[0]['type'] != 'review':
                ERRORS.append(f'[{self.letter}] "{L.title}": 첫 단계가 review 가 아님')
        d = {'format': 'pynest-learn-v2',
             'course': {'title': self.title, 'description': self.description,
                        'sequential': False, 'rank_points': 150},
             'lessons': [L.data() for L in self.lessons]}
        if ERRORS:
            print('\n\n'.join(ERRORS))
            print(f'\n❌ 오류 {len(ERRORS)}개 — 저장 안 함')
            sys.exit(1)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        nq = sum(1 for L in self.lessons for s in L.steps if s['type'] == 'quiz')
        npr = sum(1 for L in self.lessons for s in L.steps if s['type'] == 'practice')
        print(f'✅ {path}: 레슨 {len(self.lessons)}, 확인문제 {nq}, 실습 {npr}, 단계 {sum(len(L.steps) for L in self.lessons)}')
