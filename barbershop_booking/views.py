from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Barbershop, Service, Employee, Appointment, Client
from .forms import ClientForm, AppointmentForm, PhoneVerificationForm
from barbershop_management.models import Barbershop, WorkingHours, DayOfWeek
from django.urls import reverse
import logging
logger = logging.getLogger(__name__)

from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils import timezone
from django.db.models import F
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


def appointment_details(request, barbershop_name, phone):
    print(
        f"Debug: appointment_details called with barbershop_name={barbershop_name}, phone={phone}")
    barbershop = get_object_or_404(Barbershop, name=barbershop_name)
    client = get_object_or_404(Client, phone=phone, barbershop=barbershop)

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.client = client
            appointment.barbershop = barbershop
            appointment.save()
            return redirect('barbershop_booking:booking_confirmation', appointment_id=appointment.id)
    else:
        form = AppointmentForm()

    services = Service.objects.filter(barbershop=barbershop)
    employees = Employee.objects.filter(barbershop=barbershop)

    return render(request, 'barbearia/booking/appointment_details.html', {
        'barbershop': barbershop,
        'client': client,
        'form': form,
        'services': services,
        'employees': employees
    })

def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'barbearia/booking/employee_list.html', {'employees': employees})


def employee_services(request, employee_id):
    employee = Employee.objects.get(id=employee_id)
    services = EmployeeService.objects.filter(employee=employee)
    return render(request, 'barbearia/booking/employee_services.html', {'employee': employee, 'services': services})


def employee_schedule(request, employee_id):
    appointments = Appointment.objects.filter(employee_id=employee_id).order_by('date', 'time')
    schedule_data = [
        {
            'date': appointment.date.strftime('%d/%m/%Y'),
            'time': appointment.time.strftime('%H:%M'),
            'service': appointment.service.name
        }
        for appointment in appointments
    ]
    return JsonResponse(schedule_data, safe=False)


def barbershop_presentation(request, barbershop_name):
    barbershop = get_object_or_404(Barbershop, Q(name__iexact=barbershop_name))

    services = Service.objects.filter(barbershop=barbershop)
    employees = Employee.objects.filter(barbershop=barbershop)
    working_hours = WorkingHours.objects.filter(barbershop=barbershop).select_related(
        'day_of_week').order_by('day_of_week__day')
    # Organize os horários de trabalho por dia
    # Obter todos os dias da semana
    all_days = DayOfWeek.objects.all().order_by('day')
    # Criar um dicionário com todos os dias, inicialmente sem horários
    working_hours_by_day = {day: [] for day in all_days}
    # Preencher o dicionário com os horários existentes
    for wh in working_hours:
        working_hours_by_day[wh.day_of_week].append(wh)
    # Adicionar uma mensagem para dias sem horário cadastrado
    for day, hours in working_hours_by_day.items():
        if not hours:
            if day not in barbershop.working_days.all():
                working_hours_by_day[day] = ["Fechado"]
            else:
                working_hours_by_day[day] = ["Horário não cadastrado"]
    phone_form = PhoneVerificationForm()
    context = {
        'barbershop': barbershop,
        'services': services,
        'employees': employees,
        'working_hours_by_day': working_hours_by_day,
        'phone_form': phone_form,
    }
    return render(request, 'barbearia/booking/barbershop_presentation.html', context)


def verify_phone(request, barbershop_name):
    if request.method == 'POST':
        form = PhoneVerificationForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            barbershop = get_object_or_404(Barbershop, name=barbershop_name)
            client = Client.objects.filter(phone=phone, barbershop=barbershop).first()
            
            if client:
                # Cliente existe, redirecionar para a tela de agendamento
                return redirect(reverse('barbershop_booking:client_booking', kwargs={'barbershop_name': barbershop_name, 'phone': phone}))
            else:
                # Cliente não existe, redirecionar para o cadastro
                return redirect(reverse('barbershop_booking:client_registration', kwargs={'barbershop_name': barbershop_name, 'phone': phone}))
    
    # Se o método não for POST, redirecionar de volta para a página da barbearia
    return redirect(reverse('barbershop_booking:barbershop_presentation', kwargs={'barbershop_name': barbershop_name}))

def client_registration(request, barbershop_name):
    barbershop = get_object_or_404(Barbershop, name=barbershop_name)
    
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.barbershop = barbershop
            client.save()
            return redirect(reverse('barbershop_booking:client_booking', kwargs={'barbershop_name': barbershop_name, 'phone': client.phone}))
    else:
        form = ClientForm()
    
    return render(request, 'barbearia/booking/client_registration.html', {
        'barbershop': barbershop,
        'form': form
    })


def client_booking(request, barbershop_name, phone):
    barbershop = get_object_or_404(Barbershop, name=barbershop_name)
    client = get_object_or_404(Client, phone=phone, barbershop=barbershop)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.client = client
            appointment.barbershop = barbershop
            appointment.created_at = timezone.now()

            
            # Verificar disponibilidade
            if is_slot_available(appointment.employee, appointment.date, appointment.time):
                appointment.save()
                return JsonResponse({'success': True, 'message': 'Agendamento realizado com sucesso.'})
            else:
                return JsonResponse({'success': False, 'message': 'Este horário não está mais disponível.'})
        else:
            # Se o formulário não for válido, retorne os erros
            errors = {field: error[0] for field, error in form.errors.items()}
            return JsonResponse({'success': False, 'errors': errors})
    else:
        form = AppointmentForm()

    context = {
        'barbershop': barbershop,
        'client': client,
        'form': form,
    }
    
    return render(request, 'barbearia/booking/client_booking.html', context)


def booking_process(request, barbershop_name):
    barbershop = get_object_or_404(Barbershop, name=barbershop_name)

    if request.method == 'POST':
        form = PhoneVerificationForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            client = Client.objects.filter(
                phone=phone, barbershop=barbershop).first()

            if client:
                # Cliente existe, redirecionar para a tela de agendamento
                return redirect(reverse('barbershop_booking:client_booking', kwargs={'barbershop_name': barbershop_name, 'phone': phone}))
            else:
                # Cliente não existe, redirecionar para o cadastro
                return redirect(reverse('barbershop_booking:client_registration', kwargs={'barbershop_name': barbershop_name, 'phone': phone}))
    else:
        form = PhoneVerificationForm()

    return render(request, 'barbearia/booking/booking_process.html', {
        'barbershop': barbershop,
        'form': form
    })

@require_GET
def get_available_slots(request, barbershop_name, employee_id, date):
    print(f"get_available_slots called with: barbershop_name={barbershop_name}, employee_id={employee_id}, date={date}")
    try:
        barbershop = get_object_or_404(Barbershop, name=barbershop_name)
        employee = get_object_or_404(Employee, id=employee_id, barbershop=barbershop)
        
        selected_date = datetime.strptime(date, '%Y-%m-%d').date()
        day_of_week = selected_date.weekday() 

        print(f"Barbershop working days: {[day.day for day in barbershop.working_days.all()]}")
        print(f"Day of week: {day_of_week}")

        if not barbershop.working_days.filter(day=day_of_week).exists():
            print(
                f"if 1: {barbershop.working_days.filter(day=day_of_week).exists()}")
            return JsonResponse({'available_slots': [], 'message': 'A barbearia está fechada neste dia.'})
        
        barbershop_hours = WorkingHours.objects.filter(
            barbershop=barbershop, day_of_week__day=day_of_week).first()
        print(f"Barbershop hours: {barbershop_hours}")

        if not barbershop_hours:
            print (f"if 2: {barbershop_hours}")
            return JsonResponse({'available_slots': [], 'message': 'Horário de funcionamento não definido para este dia.'})
        #employee_hours = employee.working_hours.filter(day_of_week=day_of_week).first()
        #print(f"Employee hours: {employee_hours}")
        #if not employee_hours:
        #    return JsonResponse({'available_slots': [], 'message': 'O funcionário não trabalha neste dia.'})

        start_time = barbershop_hours.start_time
        end_time = barbershop_hours.end_time
        print(f"Start time: {start_time}, End time: {end_time}")

        current_time = datetime.combine(selected_date, start_time)
        end_datetime = datetime.combine(selected_date, end_time)
        slot_duration = timedelta(minutes=30)

        available_slots = []
        while current_time < end_datetime:
            time_slot = current_time.time()
            if is_slot_available(employee, selected_date, time_slot):
                available_slots.append(time_slot.strftime('%H:%M'))
            current_time += slot_duration

        print(f"Returning available slots: {available_slots}")
        return JsonResponse({'available_slots': available_slots})
    except Exception as e:
        print(f"Error in get_available_slots: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def is_slot_available(employee, date, time):
    return not Appointment.objects.filter(
        employee=employee,
        date=date,
        time=time
    ).exists()