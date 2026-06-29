
from django.contrib import admin
from django.urls import path, include
from . import settings
from django.conf.urls.static import static
import os
from django.conf import settings
from django.http import HttpResponse


def service_worker(request):
    """
    Reads sw.js out of your static files and serves it at the root with
    the right content-type + the header that tells the browser this worker
    is allowed to control the whole origin.
    """
    sw_path = os.path.join(settings.BASE_DIR, 'customers', 'static', 'js', 'sw.js')
    with open(sw_path, 'r') as f:
        content = f.read()
    response = HttpResponse(content, content_type='application/javascript')
    response['Service-Worker-Allowed'] = '/'
    return response




urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('social_django.urls', namespace='social')),  
    path('', include('customers.urls')),
    path('cart/', include('cart.urls')),
    path('payment/', include('payment.urls')),
    path('sw.js', service_worker, name='service_worker'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # path('admin_cat_list/', include('customers.urls')),







# NOTE FOR PRODUCTION: this view re-reads the file from disk on every
# request, which is fine for a tiny static file but if you want it served
# more efficiently, configure your web server (nginx/Apache) to serve
# /sw.js directly from your static root and just set the
# "Service-Worker-Allowed: /" response header there instead.
