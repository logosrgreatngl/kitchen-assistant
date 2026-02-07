const CACHE_NAME = 'kitchen-assistant-v2';
const ASSETS = [
    '/',
    '/index.html',
    '/config.js',
    '/manifest.json'
];

self.addEventListener('install', (e) => {
    e.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
    );
    self.skipWaiting();
});

self.addEventListener('activate', (e) => {
    e.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
        )
    );
    self.clients.claim();
});

self.addEventListener('fetch', (e) => {
    if (e.request.method !== 'GET') return;
    // Don't cache API calls or music streams
    if (e.request.url.includes('/api/')) return;
    
    e.respondWith(
        fetch(e.request)
            .then(response => {
                const clone = response.clone();
                caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
                return response;
            })
            .catch(() => caches.match(e.request))
    );
});