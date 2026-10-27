// 카카오톡 챗봇 명령 처리 (순수 로직 — DB 는 db 객체로 받아요)
export interface Tier { n: string; min: number }
export interface Db {
  link(kakao: string, code: string): Promise<string>;
  unlink(kakao: string): Promise<boolean>;
  rank(period: 'week' | 'month' | 'all', kakao: string): Promise<any>;
  me(kakao: string): Promise<any>;
  tiers(): Promise<Tier[]>;
}
export interface Reply { text: string; quick?: string[] }

export const DEFAULT_TIERS: Tier[] = [
  { n: 'Bronze', min: 0 }, { n: 'Silver', min: 100 }, { n: 'Gold', min: 500 }, { n: 'Platinum', min: 1500 },
  { n: 'Diamond', min: 3500 }, { n: 'Sapphire', min: 5000 }, { n: 'Emerald', min: 7000 }, { n: 'Amethyst', min: 9500 },
  { n: 'Master', min: 12000 }, { n: 'Grandmaster', min: 15000 }, { n: 'Obsidian', min: 17500 }, { n: 'The Programmer', min: 20000 },
];
const ROMAN = ['V', 'IV', 'III', 'II', 'I']; // I 이 가장 높아요 (앱과 같은 계산)

export function tierOf(score: number, tiers: Tier[]) {
  const T = tiers.length ? [...tiers].sort((a, b) => a.min - b.min) : DEFAULT_TIERS;
  const sc = Math.max(0, Number(score) || 0);
  let i = T.length - 1;
  while (i > 0 && sc < T[i].min) i -= 1;
  const nextMin = i < T.length - 1 ? T[i + 1].min : null;
  const step = nextMin != null ? (nextMin - T[i].min) / 5 : 2000;
  const lv = Math.min(4, Math.floor((sc - T[i].min) / step));
  const hi = lv < 4 ? T[i].min + (lv + 1) * step : nextMin;
  const nextName = hi == null ? null : tierOf(hi, T).name;
  return { name: `${T[i].n} ${ROMAN[lv]}`, hi, nextName, left: hi == null ? null : Math.ceil(hi - sc) };
}

const QUICK = ['랭킹', '월간랭킹', '내 프로필', '티어'];
const medal = (r: number) => (r === 1 ? '🥇' : r === 2 ? '🥈' : r === 3 ? '🥉' : `${r}위`);
const PERIOD: Record<string, string> = { week: '주간', month: '월간', all: '누적' };

export function normalize(u: string) {
  return (u || '').normalize('NFC').trim().replace(/\s+/g, ' ');
}

export async function handle(utterance: string, kakao: string, db: Db): Promise<Reply> {
  const u = normalize(utterance);
  const k = u.replace(/\s/g, '').toLowerCase();

  const m = u.match(/^연동\s*(\d{6})$/);
  if (m) {
    const r = await db.link(kakao, m[1]);
    if (r === 'ok') return { text: '✅ 연동됐어요! 이제 "내 프로필"로 내 점수랑 티어를 볼 수 있어요.', quick: QUICK };
    if (r === 'locked') return { text: '코드를 여러 번 틀려서 10분 동안 잠겼어요. 잠시 후 다시 해주세요.' };
    return { text: '코드가 맞지 않거나 만료됐어요. PyNest [설정 → 카카오톡 연동]에서 새 코드를 받아 "연동 123456" 처럼 보내주세요. (코드는 10분 동안만 유효해요)' };
  }
  if (k === '연동해제' || k === '연동끊기') {
    return { text: (await db.unlink(kakao)) ? '연동을 해제했어요.' : '연동된 계정이 없어요.', quick: QUICK };
  }
  if (/^(랭킹|순위|주간랭킹|주간|월간랭킹|월간|전체랭킹|누적랭킹|누적)$/.test(k)) {
    const period = /월간/.test(k) ? 'month' : /전체|누적/.test(k) ? 'all' : 'week';
    const r = await db.rank(period, kakao);
    const title = `🏆 ${PERIOD[period]} 랭킹`;
    if (!r || !r.top || !r.top.length) return { text: `${title}\n아직 점수를 낸 사람이 없어요.`, quick: QUICK };
    const lines = r.top.map((x: any) => `${medal(x.rnk)} ${x.name} · ${x.pts}점 (${x.solved}문제)`);
    let t = `${title}\n${lines.join('\n')}`;
    if (r.me) t += `\n\n👉 나: ${r.me.rnk}위 · ${r.me.pts}점 (${r.me.solved}문제)`;
    else if (r.linked) t += `\n\n👉 나: ${PERIOD[period]} 점수가 아직 없어요.`;
    else t += '\n\n내 순위도 보려면 PyNest 설정에서 코드를 받아 "연동 123456" 을 보내보세요.';
    return { text: t, quick: QUICK };
  }
  if (/^(내프로필|프로필|내정보)$/.test(k)) {
    const me = await db.me(kakao);
    if (!me) return { text: '아직 PyNest 계정과 연동되지 않았어요.\nPyNest [설정 → 카카오톡 연동]에서 6자리 코드를 받아 "연동 123456" 처럼 보내주세요.', quick: ['도움말', '랭킹'] };
    if (me.staff) return { text: `👤 ${me.name}\n선생님 계정은 점수·랭킹에 포함되지 않아요.`, quick: QUICK };
    const t = tierOf(me.score, await db.tiers());
    const bd = (me.by_diff || []).slice(0, 5).map((x: any) => `${x.difficulty} ${x.n}`).join(' · ');
    const rk = (x: any) => (x.rank ? `${x.rank}위 · ` : '') + `${x.pts}점 (${x.solved}문제)`;
    const next = t.hi == null ? '최고 단계예요! 👑' : `다음 ${t.nextName} 까지 ${t.left}점`;
    return {
      text: `👤 ${me.name}\n🛡️ ${t.name} · 누적 ${me.score}점 (${me.solved}문제)\n${next}\n\n📅 이번 주  ${rk(me.week)}\n🗓️ 이번 달  ${rk(me.month)}${bd ? `\n\n난이도별: ${bd}` : ''}`,
      quick: QUICK,
    };
  }
  if (/^(티어|티어표|등급)$/.test(k)) {
    const tiers = await db.tiers();
    const T = (tiers.length ? [...tiers].sort((a, b) => a.min - b.min) : DEFAULT_TIERS);
    let t = '🛡️ 티어 기준 (누적 점수, 각 티어는 V→I 5단계)\n' + T.map((x) => `${x.n}  ${x.min}점~`).join('\n');
    const me = await db.me(kakao);
    if (me && !me.staff) t += `\n\n👉 내 티어: ${tierOf(me.score, tiers).name} (${me.score}점)`;
    return { text: t, quick: QUICK };
  }
  return {
    text: '안녕하세요, PyNest 봇이에요! 🐍\n\n• 랭킹 / 월간랭킹 / 전체랭킹\n• 내 프로필\n• 티어\n• 연동 123456  (PyNest 설정에서 받은 코드)\n• 연동해제',
    quick: QUICK,
  };
}

// 카카오 오픈빌더 스킬 응답 (simpleText 는 1000자 제한)
export function toKakao(r: Reply) {
  const out: any = { version: '2.0', template: { outputs: [{ simpleText: { text: r.text.slice(0, 990) } }] } };
  if (r.quick && r.quick.length) out.template.quickReplies = r.quick.slice(0, 10).map((l) => ({ label: l.slice(0, 14), action: 'message', messageText: l }));
  return out;
}
