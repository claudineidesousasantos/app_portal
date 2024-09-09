from django.urls import path
from . import views

app_name = 'barbershop_management'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('employees/', views.manage_employees, name='manage_employees'),
    path('services/', views.manage_services, name='manage_services'),
    path('working-hours/', views.manage_working_hours, name='manage_working_hours'),
    path('appointments/', views.view_appointments, name='view_appointments'),
]
