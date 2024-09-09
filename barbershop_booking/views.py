from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from barbershop_management.models import Service, Employee, Appointment

# Create your views here.

def service_list(request):
    services = Service.objects.all()
    return render(request, 'barbearia/booking/service_list.html', 
    {'services': services})

@login_required
def book_appointment(request):
    # Lógica para agendar um horário
    return render(request, 'barbershop_booking/book_appointment.html')

@login_required
def my_appointments(request):
    # Lógica para exibir os agendamentos do cliente
    return render(request, 'barbershop_booking/my_appointments.html')
