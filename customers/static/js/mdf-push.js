/*
 * MDF Push Notification Client
 * Place at:  your_app/static/js/mdf-push.js
 * Include it only in admin templates (admin_cat_list.html, admin_uploads.html, etc.)
 */

(function () {
  'use strict';

  /* ── Helpers ─────────────────────────────────────────────────────────── */

  function urlBase64ToUint8Array(base64String) {
    var padding = '='.repeat((4 - (base64String.length % 4)) % 4);
    var base64  = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    var raw     = atob(base64);
    var output  = new Uint8Array(raw.length);
    for (var i = 0; i < raw.length; i++) output[i] = raw.charCodeAt(i);
    return output;
  }

  function getCsrfToken() {
    var cookie = document.cookie.split(';').find(function (c) { return c.trim().startsWith('csrftoken='); });
    return cookie ? cookie.trim().split('=')[1] : '';
  }

  function postJSON(url, body) {
    return fetch(url, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
      body:    JSON.stringify(body),
    });
  }

  /* ── Button state ────────────────────────────────────────────────────── */

  function setButtonState(btn, state) {
    if (!btn) return;
    if (state === 'on') {
      btn.textContent = '🔔 Notifications On';
      btn.classList.remove('mdf-push-btn--off');
      btn.classList.add('mdf-push-btn--on');
    } else if (state === 'off') {
      btn.textContent = '🔕 Enable Notifications';
      btn.classList.remove('mdf-push-btn--on');
      btn.classList.add('mdf-push-btn--off');
    } else {
      btn.textContent = '…';
      btn.disabled = true;
    }
  }

  /* ── Core logic ──────────────────────────────────────────────────────── */

  function subscribe(reg, btn) {
    fetch('/push/vapid-public-key/')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var appServerKey = urlBase64ToUint8Array(data.publicKey);
        return reg.pushManager.subscribe({
          userVisibleOnly:      true,
          applicationServerKey: appServerKey,
        });
      })
      .then(function (sub) {
        var json = sub.toJSON();
        return postJSON('/push/subscribe/', {
          endpoint: json.endpoint,
          keys:     json.keys,
        });
      })
      .then(function () {
        setButtonState(btn, 'on');
        console.log('MDF: push subscribed.');
      })
      .catch(function (err) {
        console.error('MDF: push subscribe failed —', err);
        setButtonState(btn, 'off');
      });
  }

  function unsubscribe(reg, btn) {
    reg.pushManager.getSubscription().then(function (sub) {
      if (!sub) { setButtonState(btn, 'off'); return; }

      postJSON('/push/unsubscribe/', { endpoint: sub.endpoint })
        .then(function () { return sub.unsubscribe(); })
        .then(function () {
          setButtonState(btn, 'off');
          console.log('MDF: push unsubscribed.');
        })
        .catch(function (err) {
          console.error('MDF: push unsubscribe failed —', err);
        });
    });
  }

  /* ── Init ────────────────────────────────────────────────────────────── */

  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.getElementById('mdf-push-toggle');

    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
      if (btn) { btn.textContent = 'Push not supported'; btn.disabled = true; }
      return;
    }

    navigator.serviceWorker.register('/sw.js').then(function (reg) {

      /* Reflect current subscription state on page load */
      reg.pushManager.getSubscription().then(function (sub) {
        setButtonState(btn, sub ? 'on' : 'off');
      });

      if (!btn) return;

      btn.addEventListener('click', function () {
        if (Notification.permission === 'denied') {
          alert('Notifications are blocked in your browser. Please allow them in your browser settings and try again.');
          return;
        }

        reg.pushManager.getSubscription().then(function (sub) {
          if (sub) {
            unsubscribe(reg, btn);
          } else {
            Notification.requestPermission().then(function (perm) {
              if (perm === 'granted') {
                subscribe(reg, btn);
              } else {
                alert('Permission not granted. Notifications will not be sent to this device.');
              }
            });
          }
        });
      });

    }).catch(function (err) {
      console.error('MDF: service worker registration failed —', err);
    });
  });

})();