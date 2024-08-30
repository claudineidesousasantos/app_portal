from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('portal.urls')),
    # path('gestao_barbearia/', include('gestao_barbearia.urls')),
    # path('cliente_barbearia/', include('cliente_barbearia.urls')),
]
