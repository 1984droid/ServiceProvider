"""
URL configuration for service provider application.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/', include('apps.authentication.urls')),
    path('api/', include('apps.customers.urls')),
    path('api/', include('apps.assets.urls')),
    path('api/', include('apps.organization.urls')),
    path('api/', include('apps.inspections.urls')),
    path('api/', include('apps.work_orders.urls')),

    # DRF browsable API auth
    path('api-auth/', include('rest_framework.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
