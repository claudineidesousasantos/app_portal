from django.urls import path
from . import views

app_name = 'barbershop_booking'

urlpatterns = [
    # URLs existentes
    # Card Serviços ajustar para incluir relação barbearia
    path('services/', views.service_list, name='service_list'),
    # Card Funcionarios ajustar
    path('employees/', views.employee_list, name='employee_list'),
    # Ajustar
    path('employees/<int:employee_id>/services/', views.employee_services, name='employee_services'),
    # API agendamentos
    path('employees/<int:employee_id>/schedule/', views.employee_schedule, name='employee_schedule'),
    # Pagina inicial barbearia cliente
    path('barbershop/<str:barbershop_name>/',
         views.barbershop_presentation, name='barbershop_presentation'),
    # API agendamentos por ID funcionario
    path('barbershop/employee/<int:employee_id>/schedule/',
         views.employee_schedule, name='employee_schedule'),
    # modelo de visualização dos agendamentos Calendario views.booking_process
    path('barbershop/<str:barbershop_name>/booking/',
         views.booking_process, name='booking_process'),
    # modelo de Agendamento cliente
    path('barbershop/<str:barbershop_name>/client_appointment/<str:phone>/',
         views.client_booking, name='client_booking'),
    # modelo de Agendamento cliente (sem uso)
    path('barbershop/<str:barbershop_name>/appointment/<str:phone>/',
         views.appointment_details, name='appointment_details'),

    path('<str:barbershop_name>/get-available-slots/<int:employee_id>/<str:date>/',
         views.get_available_slots, name='get_available_slots'),

    path('barbershop/<str:barbershop_name>/verify-phone/',
         views.verify_phone, name='verify_phone'),
    # Novas URLs para o processo de agendamento
    path('barbershop/<str:barbershop_name>/slots/<int:employee_id>/<str:date>/',
         views.get_available_slots, name='get_available_slots'),
    # modelo de Cadastro de cliente
    path('barbershop/<str:barbershop_name>/register/',
         views.client_registration, name='client_registration'),

]
