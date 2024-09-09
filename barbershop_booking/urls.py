from django.urls import path
from . import views

app_name = 'barbershop_booking'

urlpatterns = [
    path('services/', views.service_list, name='service_list'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
]
