// ══════════════════════════════════════════════════════════════════
//  MediCheck PWA — Service Worker v3.0
//  Estrategia: App Shell + Cache-First para estáticos
//              Network-First para API
//              Fallback offline.html cuando no hay red
// ══════════════════════════════════════════════════════════════════

const CACHE_VERSION  = 'medicheck-v3';
const OFFLINE_URL    = '/offline.html';

// ─── Recursos que se cachean en la instalación (App Shell) ────────
// Estos son los archivos que hacen que la app "arranque" sin internet
const APP_SHELL = [
  '/offline.html',
  '/manifest.json',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
];

// ─── Rutas que NUNCA se cachean ───────────────────────────────────
// El HTML principal siempre viene de la red para evitar versiones viejas
const NEVER_CACHE = ['/', '/index.html'];

// ─── Rutas de API: siempre red, con fallback JSON de error ────────
const API_PREFIX = '/api/';

// ── INSTALACIÓN ───────────────────────────────────────────────────
// Se ejecuta una sola vez cuando el SW se instala
// Descarga y guarda el App Shell en caché
self.addEventListener('install', (event) => {
  console.log('[MediCheck SW] Instalando v3...');
  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then((cache) => cache.addAll(APP_SHELL))
      .then(() => {
        console.log('[MediCheck SW] App Shell cacheado ✓');
        return self.skipWaiting(); // Activar inmediatamente sin esperar
      })
  );
});

// ── ACTIVACIÓN ────────────────────────────────────────────────────
// Se ejecuta cuando el SW toma control. Borra cachés viejos.
self.addEventListener('activate', (event) => {
  console.log('[MediCheck SW] Activando v3...');
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key !== CACHE_VERSION)
          .map((key) => {
            console.log('[MediCheck SW] Borrando caché viejo:', key);
            return caches.delete(key);
          })
      )
    ).then(() => {
      console.log('[MediCheck SW] Activo y controlando ✓');
      return self.clients.claim(); // Tomar control de todas las pestañas abiertas
    })
  );
});

// ── INTERCEPCIÓN DE PETICIONES (fetch) ────────────────────────────
// Aquí es donde decidimos: ¿usamos caché o vamos a la red?
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Solo manejar peticiones del mismo origen (no CDNs externos)
  if (url.origin !== self.location.origin) return;

  // Solo manejar GET (no POST, PUT, DELETE — esos siempre van a la red)
  if (request.method !== 'GET') return;

  // ── 1. HTML principal → siempre red ──────────────────────────
  if (NEVER_CACHE.includes(url.pathname)) {
    event.respondWith(
      fetch(request).catch(() => caches.match(OFFLINE_URL))
    );
    return;
  }

  // ── 2. API → Network-First con fallback JSON ──────────────────
  // Los datos médicos NUNCA deben venir de caché (podrían estar desactualizados)
  if (url.pathname.startsWith(API_PREFIX)) {
    event.respondWith(networkFirstAPI(request));
    return;
  }

  // ── 3. Rutas de la app Vue (/dashboard, /historial, etc.) ─────
  // Intentar red primero; si falla, dar la app (que cargará con JS)
  if (url.pathname.startsWith('/') && !url.pathname.includes('.')) {
    event.respondWith(networkFirstPage(request));
    return;
  }

  // ── 4. Recursos estáticos (JS, CSS, imágenes, fuentes) ────────
  // Caché primero: más rápido y funciona offline
  event.respondWith(cacheFirstStatic(request));
});

// ── ESTRATEGIA: Network-First para API ────────────────────────────
async function networkFirstAPI(request) {
  try {
    const response = await fetch(request);
    return response;
  } catch {
    return new Response(
      JSON.stringify({
        error: 'Sin conexión. Verifica tu internet e intenta de nuevo.',
        offline: true
      }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// ── ESTRATEGIA: Network-First para páginas Vue ────────────────────
async function networkFirstPage(request) {
  try {
    const response = await fetch(request);
    // Si la respuesta es válida, cachearla para el futuro
    if (response.ok) {
      const cache = await caches.open(CACHE_VERSION);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    // Sin red: mostrar página offline
    const cached = await caches.match(request);
    return cached || caches.match(OFFLINE_URL);
  }
}

// ── ESTRATEGIA: Cache-First para recursos estáticos ───────────────
async function cacheFirstStatic(request) {
  const cached = await caches.match(request);
  if (cached) return cached;

  try {
    const response = await fetch(request);
    // Guardar en caché solo respuestas válidas
    if (response.ok && response.status === 200) {
      const cache = await caches.open(CACHE_VERSION);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    // Si falla y no hay caché, ir a offline
    return caches.match(OFFLINE_URL);
  }
}

// ── PUSH NOTIFICATIONS ────────────────────────────────────────────
// Se ejecuta cuando el servidor manda una notificación push
self.addEventListener('push', (event) => {
  if (!event.data) return;

  let data;
  try {
    data = event.data.json();
  } catch {
    data = { title: 'MediCheck', body: event.data.text() };
  }

  const options = {
    body:    data.body  || 'Tienes una nueva notificación de MediCheck',
    icon:    '/icons/icon-192.png',
    badge:   '/icons/icon-192.png',
    vibrate: [100, 50, 100],
    tag:     data.tag   || 'medicheck-notif',   // Reemplaza notif anterior del mismo tipo
    renotify: true,
    data: { url: data.url || '/dashboard' },
    actions: [
      { action: 'abrir',  title: '📋 Abrir' },
      { action: 'cerrar', title: 'Cerrar'   }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(data.title || 'MediCheck', options)
  );
});

// ── CLICK EN NOTIFICACIÓN ─────────────────────────────────────────
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  if (event.action === 'cerrar') return;

  const destino = event.notification.data?.url || '/dashboard';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((windowClients) => {
        // Si ya hay una pestaña abierta, enfocarla
        for (const client of windowClients) {
          if ('focus' in client) {
            client.navigate(destino);
            return client.focus();
          }
        }
        // Si no hay pestaña, abrir una nueva
        return clients.openWindow(destino);
      })
  );
});

// ── SYNC EN BACKGROUND ────────────────────────────────────────────
// Cuando vuelve la conexión, podría sincronizar datos pendientes
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-consultas') {
    console.log('[MediCheck SW] Sincronizando datos pendientes...');
    // Aquí se pueden enviar datos guardados offline cuando vuelve la red
  }
});
