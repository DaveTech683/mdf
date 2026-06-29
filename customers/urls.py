# customers/urls.py

from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    path('categories/<str:items>/', views.categories, name='categories'),
    path('about/', views.about, name='about'),
    path('product/<int:pk>/', views.product, name='product'),
    path('logs/', views.logs, name='logs'),
    path('search/', views.search, name='search'),
    path('shipping/', views.shipping, name='shipping'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('admin_uploads/', views.admin_uploads, name='admin_uploads'),
    path('admin_cat_list/', views.admin_cat_list, name='admin_cat_list'),
    path('admin_cat_product_list/<int:pk>/', views.admin_cat_product_list, name='admin_cat_product_list'),
    path('contact/', views.contact, name='contact'),
    path('ship_info/', views.ship_info, name='ship_info'),
    path('pay_info/', views.pay_info, name='pay_info'),
    path('terms_info/', views.terms_info, name='terms_info'),
    path('price_filter/<str:items>/', views.filtering, name='filtering'),
    path('filter_prods/<str:items>/', views.filter_all, name='filter_all'),
    path('filter/', views.filters_all, name='filters_all'),
    path('newsletter/', views.newsletter, name='newsletter'),

    # ── Push notification endpoints (admin/staff only) ─────────────────
    path('push/subscribe/', views.push_subscribe, name='push_subscribe'),
    path('push/unsubscribe/', views.push_unsubscribe, name='push_unsubscribe'),
    path('push/vapid-public-key/', views.push_vapid_public_key, name='push_vapid_public_key'),
]