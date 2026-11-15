import random
from lib import run, nl
PROBS = []
def P(topic, title, diff, desc, inp, out, sol, ins, cond=None, gen=None, k=4, seed=7):
    rng = random.Random(seed + len(PROBS))
    ins = [nl(x) for x in ins]
    tries = 0
    while gen and k > 0 and tries < 200:
        tries += 1; g = nl(gen(rng))
        if g not in ins: ins.append(g); k -= 1
    assert len(ins) >= 6, (title, len(ins))
    assert len(set(ins)) == len(ins), ('dup input', title)
    tests = []
    for n, i in enumerate(ins):
        o = run(sol, i); assert o.strip(), (title, i)
        tests.append({'input': i, 'output': o, 'hidden': n >= 2})
    assert len({t['output'] for t in tests}) >= 2, ('outputs too similar', title)
    body = f"**{title}**\n\n{desc}\n\n"
    if cond: body += "```box 조건\n" + "\n".join("○ " + c for c in cond) + "\n```\n\n"
    body += f"**입력**\n{inp}\n\n**출력**\n{out}\n\n"
    for n, t in enumerate(tests[:2]):
        body += f"```io 예제 {n+1}\n" + "".join(">>> " + l + "\n" for l in t['input'].rstrip("\n").split("\n")) + t['output'] + "\n```\n\n"
    assert not any(p['title'] == title for p in PROBS), title
    PROBS.append({'topic': topic, 'title': title, 'difficulty': {'B': 'Beginner', 'I': 'Intermediate'}[diff], 'body': body.rstrip(), 'tests': tests, 'sol': sol})
R = lambda r, a, b: str(r.randint(a, b))
RL = lambda r, n, a, b: " ".join(str(r.randint(a, b)) for _ in range(n))
