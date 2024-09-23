from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

app_name = 'barbershop_management'

urlpatterns = [
    path('', views.presentation, name='presentation'),
    # Dashboard
    path('barbershops/', views.dashboard, name='dashboard'),

    # Barbershop URLs
    path('barbershops/', views.barbershop_list, name='barbershop_list'),
    path('barbershops/create/', views.barbershop_create, name='barbershop_create'),
    path('barbershops/<int:barbershop_id>/',
         views.barbershop_detail, name='barbershop_detail'),
    path('barbershops/<int:barbershop_id>/edit/',
         views.barbershop_edit, name='barbershop_edit'),

    # Employee URLs
    path('barbershops/<int:barbershop_id>/employees/',
         views.employee_list, name='employee_list'),
    path('employees/<int:employee_id>/',
         views.employee_detail, name='employee_detail'),
    path('barbershops/<int:barbershop_id>/employees/create/',
         views.employee_create, name='employee_create'),
    path('barbershops/<int:barbershop_id>/employees/<int:employee_id>/delete/', views.employee_delete, name='employee_delete'),
    path('barbershops/<int:barbershop_id>/employees/<int:employee_id>/update/',
         views.employee_update, name='employee_update'),

    # Service URLs
    path('barbershops/<int:barbershop_id>/services/',
         views.service_list, name='services'),
    path('barbershops/<int:barbershop_id>/services/create/',
         views.service_create, name='service_create'),
    path('barbershops/<int:barbershop_id>/services/<int:service_id>/update/',
         views.service_update, name='service_update'),
    path('barbershops/<int:barbershop_id>/services/<int:service_id>/delete/',
         views.service_delete, name='service_delete'),

    # WorkingHours URLs
    path('barbershops/<int:barbershop_id>/working-hours/',
         views.working_hours_list, name='working_hours_list'),
    path('barbershops/<int:barbershop_id>/working-hours/create/',
         views.working_hours_create, name='working_hours_create'),
    path('working-hours/<int:working_hours_id>/edit/',
         views.working_hours_edit, name='working_hours_edit'),
    path('working-hours/<int:working_hours_id>/delete/',
         views.working_hours_delete, name='working_hours_delete'),

    # Expense URLs
    path('barbershops/<int:barbershop_id>/expenses/',
         views.expense_list, name='expense_list'),
    path('barbershops/<int:barbershop_id>/expenses/create/',
         views.expense_create, name='expense_create'),
    path('expenses/<int:expense_id>/edit/',
         views.expense_edit, name='expense_edit'),
    path('expenses/<int:expense_id>/delete/',
         views.expense_delete, name='expense_delete'),

    # Inventory URLs
    path('barbershops/<int:barbershop_id>/inventory/',
         views.inventory_list, name='inventory_list'),
    path('barbershops/<int:barbershop_id>/inventory/create/',
         views.inventory_create, name='inventory_create'),
    path('inventory/<int:inventory_id>/edit/',
         views.inventory_edit, name='inventory_edit'),
    path('inventory/<int:inventory_id>/delete/',
         views.inventory_delete, name='inventory_delete'),

    # EmployeeService URLs
    path('barbershops/<int:barbershop_id>/employee-services/',
         views.employee_service_list, name='employee_service_list'),
    path('barbershops/<int:barbershop_id>/employee-services/create/',
         views.employee_service_create, name='employee_service_create'),
    path('employee-services/<int:employee_service_id>/delete/',
         views.employee_service_delete, name='employee_service_delete'),

    # Generate Booking Link
    path('barbershops/<int:barbershop_id>/generate-booking-link/',
         views.generate_booking_link, name='generate_booking_link'),

    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
