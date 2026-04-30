const CACHE_NAME = 'pitv-v6';
const SHELL_ASSETS = [
  '/static/manifest.json',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
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

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // Never cache live video streams
  if (url.pathname.startsWith('/stream/') || url.pathname.includes('/iptv/') ||
      url.pathname.endsWith('.ts') || url.pathname.endsWith('.m3u8')) {
    return;
  }

  // Vite hashed assets: cache-first (immutable)
  if (url.pathname.startsWith('/static/dist/assets/')) {
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

  // Media assets: cache-first with network fallback
  if (url.pathname.startsWith('/static/Media/') || url.pathname.startsWith('/static/logos/')) {
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

  // Admin API: never cache. These responses are auth-bearing and used to
  // include the PIN; caching them parks credentials in CacheStorage where
  // any later browser-profile access can read them.
  if (url.pathname.startsWith('/admin/api/')) {
    e.respondWith(fetch(e.request));
    return;
  }

  // Public API: network-first, stale cache fallback.
  if (url.pathname.startsWith('/api/')) {
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

  // HTML navigations: network-first, fallback to cached SPA shell
  if (e.request.mode === 'navigate') {
    e.respondWith(
      fetch(e.request)
        .then(resp => {
          const clone = resp.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
          return resp;
        })
        .catch(() => caches.match('/') || caches.match(e.request))
    );
    return;
  }

  // Other static: cache-first
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
