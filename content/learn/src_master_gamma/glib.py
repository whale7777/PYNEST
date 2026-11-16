import lib, subprocess, sys, tempfile
from lib import *
def _run(code, stdin=''):
    with tempfile.TemporaryDirectory() as d:
        r = subprocess.run([sys.executable, '-I', '-c', code], input=stdin, capture_output=True, text=True, timeout=20, cwd=d)
    if r.returncode != 0: raise RuntimeError(r.stderr[-600:] + '\n--- code ---\n' + code + '\n--- stdin ---\n' + stdin)
    return '\n'.join(l.rstrip() for l in r.stdout.rstrip().split('\n'))
lib.run = _run
run = _run
def D(s): return s.strip('\n')
