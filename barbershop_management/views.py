from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Employee, Service, WorkingHours, Appointment

# Create your views here.

@login_required
def dashboard(request):
    # Lógica para exibir o painel de controle
    return render(request, 'barbershop_management/dashboard.html')

@login_required
def manage_employees(request):
    # Lógica para gerenciar funcionários
    return render(request, 'barbershop_management/manage_employees.html')

@login_required
def manage_services(request):
    # Lógica para gerenciar serviços
    return render(request, 'barbershop_management/manage_services.html')

@login_required
def manage_working_hours(request):
    # Lógica para gerenciar horários de trabalho
    return render(request, 'barbershop_management/manage_working_hours.html')

@login_required
def view_appointments(request):
    # Lógica para visualizar agendamentos
    return render(request, 'barbershop_management/view_appointments.html')
