/*
 * MDF Push Notification Service Worker
 * Place this file at:  your_app/static/js/sw.js
 * It must be served from the ROOT of your domain, so in urls.py (project level)
 * add the route shown in the setup instructions.
 */

self.addEventListener('push', function (event) {
  if (!event.data) return;

  var data  = {};
  try { data = event.data.json(); } catch (e) { data = { title: 'MDF', body: event.data.text() }; }

  var title   = data.title || 'Modest Daily Fashion';
  var options = {
    body:    data.body  || 'You have a new notification.',
    icon:    '/static/img/pngwing.png',   // your MDF logo — update path if different
    badge:   '/static/img/pngwing.png',
    data:    { url: data.url || '/admin_cat_list/' },
    vibrate: [200, 100, 200],
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', function (event) {
  event.notification.close();
  var target = (event.notification.data && event.notification.data.url) || '/admin_cat_list/';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function (clientList) {
      for (var i = 0; i < clientList.length; i++) {
        var client = clientList[i];
        if (client.url.indexOf(target) !== -1 && 'focus' in client) {
          return client.focus();
        }
      }
      if (clients.openWindow) return clients.openWindow(target);
    })
  );
});