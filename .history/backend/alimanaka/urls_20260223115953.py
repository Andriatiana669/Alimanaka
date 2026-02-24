from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.admin_site import alimanaka_admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentification.urls')),
    path('alimanaka-admin/', alimanaka_admin.urls),
    path('api/conges/', include('conges.urls')),
    path('api/', include('users.urls')),
    path('api/retards/', include('retards.urls')),
    path('api/permissions/', include('permissions.urls')),
    path('api/repos-medicaux/', include('reposmedicale.urls')),
    
    # Plus de catch-all pour Vue.js ! Django ne sert que l'API
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)