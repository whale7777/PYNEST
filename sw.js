/* PyNest 서비스 워커 — 앱처럼 설치(홈 화면 추가)되게 하는 최소 버전이에요.
 * 파일을 캐시하지 않아서, 사이트를 업데이트하면 항상 최신 버전이 바로 열려요. */
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', (e) => {
  if (e.request.mode !== 'navigate') return;
  e.respondWith(fetch(e.request).catch(() => new Response('<meta charset="utf-8"><meta name="viewport" content="width=device-width"><body style="font-family:sans-serif;text-align:center;padding:40px"><h2>🐍 PyNest</h2><p>인터넷에 연결되어 있지 않아요.<br>연결한 뒤 다시 열어주세요.</p>', { headers: { 'content-type': 'text/html; charset=utf-8' } })));
});
