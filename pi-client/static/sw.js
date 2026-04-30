const CACHE_NAME = 'pitv-v4';
const SHELL_ASSETS = [
  '/static/manifest.json',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  'https://cdn.jsdelivr.net/npm/mpegts.js@1.7.3/dist/mpegts.min.js'
];

// Cache shell on install
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(SHELL_ASSETS))
  );
  self.skipWaiting();
});

// Clean old caches on activate
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Network-first for pages & API, cache-first for static assets only
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // Never cache video streams or proxied images
  if (url.pathname.includes('/iptv/') || url.pathname.endsWith('.ts') || url.pathname.endsWith('.m3u8') || url.pathname.startsWith('/stream/') || url.pathname.startsWith('/proxy/')) {
    return;
  }

  // HTML pages & API: network-first, fallback to cache
  if (url.pathname.startsWith('/api/') || e.request.mode === 'navigate' || url.pathname === '/') {
    e.respondWith(
      fetch(e.request)
        .then(resp => {
          const clone = resp.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
          return resp;
        })
        .catch(() => caches.match(e.request))
    );
    return;
  }

  // Static assets only: cache-first, fallback to network
  if (url.pathname.startsWith('/static/')) {
    e.respondWith(
      caches.match(e.request).then(cached => {
        if (cached) return cached;
        return fetch(e.request).then(resp => {
          if (resp.ok) {
            const clone = resp.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
          }
          return resp;
        });
      })
    );
    return;
  }

  // Everything else: network only
  e.respondWith(fetch(e.request));
});
