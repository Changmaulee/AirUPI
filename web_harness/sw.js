const CACHE_NAME = 'otm-brain-v2-force-top-input';

self.addEventListener('install', (e) => {
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.map((k) => caches.delete(k)) // Wipe old caches
    ))
  );
  self.clients.claim();
});

// Network-First: Always fetch fresh HTML from Vercel
self.addEventListener('fetch', (e) => {
  e.respondWith(
    fetch(e.request).catch(() => caches.match(e.request))
  );
});
