from django.urls import path
from . import views

app_name = 'barbershop_booking'

urlpatterns = [
    # URLs existentes
    path('services/', views.service_list, name='service_list'),
    path('book/<int:employee_id>/<int:service_id>/', views.book_appointment, name='book_appointment'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('register/', views.register, name='register'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/<int:employee_id>/services/', views.employee_services, name='employee_services'),
    path('employees/<int:employee_id>/schedule/', views.employee_schedule, name='employee_schedule'),
    path('booking/<str:barbershop_code>/', views.booking, name='booking'),
    
    # Nova URL para a apresentação da barbearia
    path('barbershop/<int:barbershop_id>/', views.barbershop_presentation, name='barbershop_presentation'),
]
