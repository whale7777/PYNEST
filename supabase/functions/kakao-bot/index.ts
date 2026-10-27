// PyNest 카카오톡 챗봇 스킬 서버 (Supabase Edge Function)
// 배포: supabase functions deploy kakao-bot --no-verify-jwt
// 비밀값: supabase secrets set BOT_SECRET=아무_긴_문자열   (SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY 는 자동으로 들어있어요)
// 카카오 오픈빌더 스킬 설정의 [헤더값]에 x-bot-secret = 위 BOT_SECRET 을 넣어요.
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.45.4';
import { handle, toKakao, type Db } from './logic.ts';

const sb = createClient(Deno.env.get('SUPABASE_URL')!, Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!, { auth: { persistSession: false } });
const must = async (p: PromiseLike<{ data: any; error: any }>) => { const { data, error } = await p; if (error) throw error; return data; };
const db: Db = {
  link: (kakao, code) => must(sb.rpc('bot_link', { p_kakao: kakao, p_code: code })),
  unlink: (kakao) => must(sb.rpc('bot_unlink', { p_kakao: kakao })),
  rank: (period, kakao) => must(sb.rpc('bot_rank', { p_period: period, p_kakao: kakao })),
  me: (kakao) => must(sb.rpc('bot_me', { p_kakao: kakao })),
  tiers: async () => (await must(sb.rpc('bot_tiers'))) || [],
};
const json = (o: unknown, status = 200) => new Response(JSON.stringify(o), { status, headers: { 'content-type': 'application/json; charset=utf-8' } });

Deno.serve(async (req) => {
  const secret = Deno.env.get('BOT_SECRET');
  if (!secret || req.headers.get('x-bot-secret') !== secret) return json({ error: 'forbidden' }, 403);
  try {
    const body = await req.json();
    const kakao = body?.userRequest?.user?.id;
    const utter = body?.userRequest?.utterance ?? '';
    if (!kakao) return json({ error: 'no user' }, 400);
    return json(toKakao(await handle(utter, String(kakao), db)));
  } catch (e) {
    console.error(e);
    return json(toKakao({ text: '앗, 지금은 불러오지 못했어요. 잠시 후 다시 시도해주세요.' }));
  }
});
