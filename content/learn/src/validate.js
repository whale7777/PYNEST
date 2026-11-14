// 사용: node validate.js file.json [out_normalized.json]
const fs = require('fs');
const src = fs.readFileSync(__dirname + '/../../../app.js', 'utf8');
const a = src.indexOf('  const LX_CALL'), b = src.indexOf('  function exportLearn');
const pre = "const learnTxt = (x) => String(x ?? '').replace(/\\r/g, '');\nconst LEARN_KINDS = ['ox','choice','short','fill'];\nconst TEST_MODES = { contains: '포함', nums: '숫자', nospace: '공백무시' };\nconst normTests = (arr) => (Array.isArray(arr) ? arr : []).filter((t) => t && (t.input != null || t.output != null)).map((t) => ({ input: String(t.input ?? ''), output: String(t.output ?? ''), hidden: !!t.hidden, ...(TEST_MODES[t.mode] ? { mode: t.mode } : {}) }));\nconst esc = (s) => String(s);\n";
const fn = new Function(pre + src.slice(a, b) + '\nreturn parseLearnJson;')();
const r = fn(fs.readFileSync(process.argv[2], 'utf8'));
console.log('OK', r.course.title, 'lessons', r.lessons.length, 'steps', r.nSteps, 'max', Math.max(...r.lessons.map(l => l.steps.length)));
if (process.argv[3]) fs.writeFileSync(process.argv[3], JSON.stringify(r));
