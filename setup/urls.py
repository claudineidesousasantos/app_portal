from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('portal.urls')),
    path('management/', include('barbershop_management.urls')),
    path('booking/', include('barbershop_booking.urls')),
    path('logout/', LogoutView.as_view(next_page='barbershop_management:login'), name='logout'),
    # Adicione a URL para a página inicial do portal aqui
    
]
