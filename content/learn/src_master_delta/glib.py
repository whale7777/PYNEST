import lib, subprocess, sys, tempfile, os
from lib import *
# 검증용 파이썬: 사이트(Pyodide 0.26.4 = py3.12, numpy 1.26.4, pandas 2.2.0, sklearn 1.4.2)와 같은 버전의 venv 가 있으면 그것으로 실행
PY = os.environ.get('PYNEST_PY') or sys.executable
def _run(code, stdin=''):
    with tempfile.TemporaryDirectory() as d:
        r = subprocess.run([PY, '-I', '-W', 'ignore', '-c', code], input=stdin, capture_output=True, text=True, timeout=60, cwd=d)
    if r.returncode != 0: raise RuntimeError(r.stderr[-600:] + '\n--- code ---\n' + code + '\n--- stdin ---\n' + stdin)
    return '\n'.join(l.rstrip() for l in r.stdout.rstrip().split('\n'))
lib.run = _run
run = _run
def D(s): return s.strip('\n')
def err(code, stdin=''):
    """일부러 오류가 나는 코드의 예외 이름을 실제 실행으로 확인 (spot·서술형 정답 검증용)"""
    with tempfile.TemporaryDirectory() as d:
        r = subprocess.run([PY, '-I', '-W', 'ignore', '-c', code], input=stdin, capture_output=True, text=True, timeout=60, cwd=d)
    assert r.returncode != 0, code
    return r.stderr.strip().split('\n')[-1].split(':')[0]
def errline(code, stdin=''):
    """예외가 난 줄 번호 (spot 정답 검증용)"""
    import re
    with tempfile.TemporaryDirectory() as d:
        r = subprocess.run([PY, '-I', '-W', 'ignore', '-c', code], input=stdin, capture_output=True, text=True, timeout=60, cwd=d)
    assert r.returncode != 0, code
    return int(re.findall(r'File "<string>", line (\d+)', r.stderr)[-1])
