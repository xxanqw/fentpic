const CACHE_NAME = 'fentpic-cache-v1';
const CACHE_URLS = [
    '/static/fplogo.png',
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(CACHE_URLS))
    );
});

self.addEventListener('fetch', (event) => {
    if (event.request.url.match(/\.(jpg|jpeg|png|gif|webp)$/)) {
        event.respondWith(
            caches.match(event.request)
                .then(response => {
                    if (response) {
                        return response;
                    }
                    return fetch(event.request).then(response => {
                        return caches.open(CACHE_NAME).then(cache => {
                            cache.put(event.request, response.clone());
                            return response;
                        });
                    });
                })
        );
    }
});