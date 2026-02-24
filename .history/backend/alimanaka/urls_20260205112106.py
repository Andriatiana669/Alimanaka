from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from authentification.views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentification.urls')),
    path('api/', include('users.urls')),
    
    # Route racine - redirection auto
    path('', home_view, name='home'),
    
    # Servir le template Vue.js pour toutes les routes non-API
    re_path(r'^(?!api/|admin/|static/|media/).*$', 
            TemplateView.as_view(template_name='index.html')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)