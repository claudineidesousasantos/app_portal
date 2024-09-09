from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('portal.urls')),
    path('management/', include('barbershop_management.urls')),
    path('booking/', include('barbershop_booking.urls')),
    # Adicione a URL para a página inicial do portal aqui
    
]
