from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentification.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('', include('dashboard.urls')),  # La racine pointe aussi vers le dashboard
]