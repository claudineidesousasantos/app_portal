from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee, Service, EmployeeService, Appointment
from .forms import AppointmentForm
from barbershop_management.models import Barbershop, WorkingHours
import logging
logger = logging.getLogger(__name__)
# Create your views here.


def service_list(request):
    services = Service.objects.all()
    return render(request, 'barbearia/booking/service_list.html',
                  {'services': services})


def book_appointment(request, employee_id, service_id):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.client = request.user.client_profile
            appointment.employee_id = employee_id
            appointment.service_id = service_id
            appointment.save()
            return redirect('barbershop_booking:my_appointments')
    else:
        form = AppointmentForm()
    return render(request, 'barbearia/booking/book_appointment.html', {'form': form})


def my_appointments(request):
    appointments = Appointment.objects.filter(
        client=request.user.client_profile)
    return render(request, 'barbearia/booking/my_appointments.html', {'appointments': appointments})


def register(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        client_form = ClientForm(request.POST)
        if user_form.is_valid() and client_form.is_valid():
            user = user_form.save()
            client = client_form.save(commit=False)
            client.user = user
            client.save()
            login(request, user)
            return redirect('barbershop_booking:employee_list')
    else:
        user_form = UserCreationForm()
        client_form = ClientForm()
    return render(request, 'barbearia/booking/register.html', {'user_form': user_form, 'client_form': client_form})


def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'barbearia/booking/employee_list.html', {'employees': employees})


def employee_services(request, employee_id):
    employee = Employee.objects.get(id=employee_id)
    services = EmployeeService.objects.filter(employee=employee)
    return render(request, 'barbearia/booking/employee_services.html', {'employee': employee, 'services': services})


def employee_schedule(request, employee_id):
    employee = Employee.objects.get(id=employee_id)
    appointments = Appointment.objects.filter(employee=employee)
    return render(request, 'barbearia/booking/employee_schedule.html', {'employee': employee, 'appointments': appointments})


def booking(request, barbershop_code):
    barbershop = get_object_or_404(Barbershop, code=barbershop_code)
    # Aqui você pode implementar a lógica de agendamento
    return render(request, 'barbershop_booking/booking.html', {'barbershop': barbershop})


def barbershop_presentation(request, barbershop_id):
    barbershop = get_object_or_404(Barbershop, id=barbershop_id)
    services = Service.objects.filter(barbershop=barbershop)
    employees = Employee.objects.filter(barbershop=barbershop)
    working_hours = WorkingHours.objects.filter(
        barbershop=barbershop).order_by('day_of_week__day')

    context = {
        'barbershop': barbershop,
        'services': services,
        'employees': employees,
        'working_hours': working_hours,
    }
    return render(request, 'barbearia/booking/barbershop_presentation.html', context)
