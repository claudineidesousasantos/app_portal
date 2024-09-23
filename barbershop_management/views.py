from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from barbershop_booking.models import Appointment
from .models import Barbershop, Employee, Service, WorkingHours, Expense, Inventory, EmployeeService
from .forms import BarbershopForm, EmployeeForm, ServiceForm, WorkingHoursForm, ExpenseForm, InventoryForm, EmployeeServiceForm, LoginForm
from django.utils import timezone

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout

from django.db.models import OuterRef, Subquery
from django.db.models.functions import Concat
from django.db.models import CharField, Value


@login_required
def dashboard(request):
    """
    Exibe o dashboard principal para o usuário logado.

    Esta view mostra uma visão geral da barbearia do usuário, incluindo contagens
    de funcionários e serviços, bem como listas de funcionários e serviços recentes.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.

    Returns:
        HttpResponse: A resposta renderizada com o template do dashboard.

    Raises:
        Http404: Se a barbearia associada ao usuário não for encontrada.
    """
    barbershop = get_object_or_404(Barbershop, owner=request.user)
    context = {
        'barbershop': barbershop,
        'employees_count': Employee.objects.filter(barbershop=barbershop).count(),
        'services_count': Service.objects.filter(barbershop=barbershop).count(),
        'appointments_count': Appointment.objects.filter(barbershop=barbershop).count(),
        'recent_employees': Employee.objects.filter(barbershop=barbershop).order_by('-id')[:5],
        'recent_services': Service.objects.filter(barbershop=barbershop).order_by('-id')[:5],
    }
    return render(request, 'barbearia/management/dashboard.html', context)


@login_required
def barbershop_list(request):
    """
    Lista todas as barbearias associadas ao usuário logado.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.

    Returns:
        HttpResponse: A resposta renderizada com a lista de barbearias.
    """
    barbershops = Barbershop.objects.filter(owner=request.user)
    return render(request, 'barbearia/management/barbershop_list.html', {'barbershops': barbershops})


@login_required
def barbershop_detail(request, barbershop_id):
    """
    Exibe os detalhes de uma barbearia específica.

    Esta view mostra informações detalhadas sobre uma barbearia, incluindo
    seus funcionários e serviços.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        barbershop_id (int): O ID da barbearia a ser exibida.

    Returns:
        HttpResponse: A resposta renderizada com o template de detalhes da barbearia.

    Raises:
        Http404: Se a barbearia não for encontrada ou não pertencer ao usuário logado.
    """
    barbershop = get_object_or_404(
        Barbershop, id=barbershop_id, owner=request.user)
    employees = barbershop.employees.all()
    services = barbershop.services.all()
    expenses = barbershop.expenses.all()
    inventory = barbershop.inventory_items.all()
    context = {
        'barbershop': barbershop,
        'employees': employees,
        'services': services,
        'expenses': expenses,
        'inventory': inventory,
    }
    return render(request, 'barbearia/management/barbershop_detail.html', context)


@login_required
def barbershop_create(request):
    """
    Cria uma nova barbearia para o usuário logado.

    Esta view lida com a criação de uma nova barbearia, processando o formulário
    de criação e salvando os dados.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.

    Returns:
        HttpResponse: Redireciona para o dashboard em caso de sucesso ou
                      renderiza o formulário novamente em caso de erro.
    """
    if request.method == 'POST':
        form = BarbershopForm(request.POST)
        if form.is_valid():
            barbershop = form.save(commit=False)
            barbershop.owner = request.user
            barbershop.save()
            messages.success(request, 'Barbearia criada com sucesso.')
            return redirect('barbershop_management:barbershop_detail', barbershop_id=barbershop.id)
    else:
        form = BarbershopForm()
    return render(request, 'barbearia/management/barbershop_form.html', {'form': form})


@login_required
def barbershop_edit(request, barbershop_id):
    """
    Edita uma barbearia existente.

    Esta view lida com a edição de uma barbearia existente, processando o formulário
    de edição e salvando os dados atualizados.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        barbershop_id (int): O ID da barbearia a ser editada.

    Returns:
        HttpResponse: Redireciona para o dashboard em caso de sucesso ou
                      renderiza o formulário novamente em caso de erro.

    Raises:
        Http404: Se a barbearia não for encontrada ou não pertencer ao usuário logado.
    """
    barbershop = get_object_or_404(
        Barbershop, id=barbershop_id, owner=request.user)
    if request.method == 'POST':
        form = BarbershopForm(request.POST, instance=barbershop)
        if form.is_valid():
            form.save()
            messages.success(request, 'Barbearia atualizada com sucesso.')
            return redirect('barbershop_management:barbershop_detail', barbershop_id=barbershop.id)
    else:
        form = BarbershopForm(instance=barbershop)
    return render(request, 'barbearia/management/barbershop_form.html', {'form': form, 'barbershop': barbershop})


@login_required
def employee_list(request, barbershop_id):
    """
    Lista todos os funcionários de uma barbearia específica.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        barbershop_id (int): O ID da barbearia cujos funcionários serão listados.

    Returns:
        HttpResponse: A resposta renderizada com a lista de funcionários.

    Raises:
        Http404: Se a barbearia não for encontrada ou não pertencer ao usuário logado.
    """
    barbershop = get_object_or_404(Barbershop, id=barbershop_id)
    
    # Subconsulta para o próximo agendamento
    next_appointment = Appointment.objects.filter(
        employee=OuterRef('pk'),
        date__gte=timezone.now().date(),
        status='scheduled'  # Ajuste conforme necessário
    ).order_by('date', 'start_time').values('date', 'start_time')[:1]

    # Anotação para formatar a data e hora
    employees = Employee.objects.filter(barbershop=barbershop).annotate(
        next_appointment_date=Subquery(next_appointment.values('date')),
        next_appointment_time=Subquery(next_appointment.values('start_time'))
    ).annotate(
        next_appointment=Concat(
            'next_appointment_date',
            Value(' '),
            'next_appointment_time',
            output_field=CharField()
        )
    )
    
    context = {
        'barbershop': barbershop,
        'employees': employees,
    }
    return render(request, 'barbearia/management/employee_list.html', context)

@login_required
def employee_detail(request, employee_id):
    """
    Exibe os detalhes de um funcionário específico.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        employee_id (int): O ID do funcionário a ser exibido.

    Returns:
        HttpResponse: A resposta renderizada com o template de detalhes do funcionário.

    Raises:
        Http404: Se o funcionário não for encontrado.
    """
    employee = get_object_or_404(Employee, id=employee_id)
    return render(request, 'barbearia/management/employee_detail.html', {'employee': employee})


@login_required
def employee_create(request, barbershop_id):
    """
    Cria um novo funcionário para uma barbearia específica.

    Esta view lida com a criação de um novo funcionário, processando o formulário
    de criação e salvando os dados.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        barbershop_id (int): O ID da barbearia para a qual o funcionário será criado.

    Returns:
        HttpResponse: Redireciona para a lista de funcionários em caso de sucesso ou
                      renderiza o formulário novamente em caso de erro.

    Raises:
        Http404: Se a barbearia não for encontrada ou não pertencer ao usuário logado.
    """
    barbershop = get_object_or_404(
        Barbershop, id=barbershop_id, owner=request.user)
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.barbershop = barbershop
            employee.save()
            messages.success(request, 'Funcionário adicionado com sucesso.')
            return redirect('barbershop_management:employee_list', barbershop_id=barbershop.id)
    else:
        form = EmployeeForm()
    return render(request, 'barbearia/management/employee_form.html', {'form': form, 'barbershop': barbershop})


@login_required
def employee_update(request, barbershop_id, employee_id):
    """
    Edita um funcionário existente.

    Esta view lida com a edição de um funcionário existente, processando o formulário
    de edição e salvando os dados atualizados.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        barbershop_id (int): O ID da barbearia à qual o funcionário pertence.
        employee_id (int): O ID do funcionário a ser editado.

    Returns:
        HttpResponse: Redireciona para a lista de funcionários em caso de sucesso ou
                      renderiza o formulário novamente em caso de erro.

    Raises:
        Http404: Se o funcionário não for encontrado ou não pertencer à barbearia especificada.
    """
    barbershop = get_object_or_404(Barbershop, id=barbershop_id)
    employee = get_object_or_404(Employee, id=employee_id, barbershop=barbershop)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Funcionário atualizado com sucesso.')
            return redirect('barbershop_management:employee_list', barbershop_id=barbershop.id)
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'barbearia/management/employee_form.html', {'form': form, 'barbershop': barbershop, 'employee': employee})


@login_required
@require_POST
def employee_delete(request, barbershop_id, employee_id):
    """
    Exclui um funcionário existente.

    Esta view lida com a exclusão de um funcionário existente, confirmando a ação
    e redirecionando para a lista de funcionários.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        barbershop_id (int): O ID da barbearia à qual o funcionário pertence.
        employee_id (int): O ID do funcionário a ser excluído.

    Returns:
        HttpResponse: Redireciona para a lista de funcionários em caso de sucesso ou
                      renderiza o template de confirmação de exclusão em caso de erro.

    Raises:
        Http404: Se o funcionário não for encontrado ou não pertencer à barbearia especificada.
    """
    barbershop = get_object_or_404(Barbershop, id=barbershop_id)
    employee = get_object_or_404(Employee, id=employee_id, barbershop=barbershop)
    employee.delete()
    return JsonResponse({'status': 'success'})

# Service views


@login_required
def service_list(request, barbershop_id):
    """
    Lista todos os serviços de uma barbearia específica.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        barbershop_id (int): O ID da barbearia cujos serviços serão listados.

    Returns:
        HttpResponse: A resposta renderizada com a lista de serviços.

    Raises:
        Http404: Se a barbearia não for encontrada ou não pertencer ao usuário logado.
    """
    barbershop = get_object_or_404(Barbershop, id=barbershop_id)
    services = Service.objects.filter(barbershop=barbershop)
    return render(request, 'barbearia/management/service_list.html', {'barbershop': barbershop, 'services': services})


@login_required
def service_create(request, barbershop_id):
    """
    Cria um novo serviço para uma barbearia específica.

    Esta view lida com a criação de um novo serviço, processando o formulário
    de criação e salvando os dados.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        barbershop_id (int): O ID da barbearia para a qual o serviço será criado.

    Returns:
        HttpResponse: Redireciona para a lista de serviços em caso de sucesso ou
                      renderiza o formulário novamente em caso de erro.

    Raises:
        Http404: Se a barbearia não for encontrada ou não pertencer ao usuário logado.
    """
    barbershop = get_object_or_404(Barbershop, id=barbershop_id)
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.barbershop = barbershop
            service.save()
            return redirect('barbershop_management:services', barbershop_id=barbershop.id)
    else:
        form = ServiceForm()
    return render(request, 'barbearia/management/service_form.html', {'form': form, 'barbershop': barbershop})


@login_required
def service_update(request, barbershop_id, service_id):
    """
    Edita um serviço existente.

    Esta view lida com a edição de um serviço existente, processando o formulário
    de edição e salvando os dados atualizados.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        barbershop_id (int): O ID da barbearia à qual o serviço pertence.
        service_id (int): O ID do serviço a ser editado.

    Returns:
        HttpResponse: Redireciona para a lista de serviços em caso de sucesso ou
                      renderiza o formulário novamente em caso de erro.

    Raises:
        Http404: Se o serviço não for encontrado ou não pertencer à barbearia especificada.
    """
    barbershop = get_object_or_404(Barbershop, id=barbershop_id)
    service = get_object_or_404(Service, id=service_id, barbershop=barbershop)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('barbershop_management:services', barbershop_id=barbershop.id)
    else:
        form = ServiceForm(instance=service)
    return render(request, 'barbearia/management/service_form.html', {'form': form, 'barbershop': barbershop, 'service': service})


@login_required
@require_POST
def service_delete(request, barbershop_id, service_id):
    """
    Exclui um serviço existente.

    Esta view lida com a exclusão de um serviço existente, confirmando a ação
    e redirecionando para a lista de serviços.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        barbershop_id (int): O ID da barbearia à qual o serviço pertence.
        service_id (int): O ID do serviço a ser excluído.

    Returns:
        HttpResponse: Redireciona para a lista de serviços em caso de sucesso ou
                      renderiza o template de confirmação de exclusão em caso de erro.

    Raises:
        Http404: Se o serviço não for encontrado ou não pertencer à barbearia especificada.
    """
    barbershop = get_object_or_404(Barbershop, id=barbershop_id)
    service = get_object_or_404(Service, id=service_id, barbershop=barbershop)
    service.delete()
    return JsonResponse({'status': 'success'})

# WorkingHours views


@login_required
def working_hours_list(request, barbershop_id):
    """
    Lista todos os horários de trabalho de uma barbearia específica.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        barbershop_id (int): O ID da barbearia cujos horários de trabalho serão listados.

    Returns:
        HttpResponse: A resposta renderizada com a lista de horários de trabalho.

    Raises:
        Http404: Se a barbearia não for encontrada ou não pertencer ao usuário logado.
    """
    barbershop = get_object_or_404(
        Barbershop, id=barbershop_id, owner=request.user)
    working_hours = WorkingHours.objects.filter(
        employee__barbershop=barbershop)
    return render(request, 'barbearia/management/working_hours_list.html', {'barbershop': barbershop, 'working_hours': working_hours})


@login_required
def working_hours_create(request, barbershop_id):
    """
    Cria um novo horário de trabalho para uma barbearia específica.

    Esta view lida com a criação de um novo horário de trabalho, processando o formulário
    de criação e salvando os dados.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        barbershop_id (int): O ID da barbearia para a qual o horário de trabalho será criado.

    Returns:
        HttpResponse: Redireciona para a lista de horários de trabalho em caso de sucesso ou
                      renderiza o formulário novamente em caso de erro.

    Raises:
        Http404: Se a barbearia não for encontrada ou não pertencer ao usuário logado.
    """
    barbershop = get_object_or_404(
        Barbershop, id=barbershop_id, owner=request.user)
    if request.method == 'POST':
        form = WorkingHoursForm(request.POST)
        if form.is_valid():
            working_hours = form.save(commit=False)
            working_hours.employee = form.cleaned_data['employee']
            working_hours.save()
            messages.success(
                request, 'Horário de trabalho adicionado com sucesso.')
            return redirect('barbershop_management:working_hours_list', barbershop_id=barbershop.id)
    else:
        form = WorkingHoursForm()
    return render(request, 'barbearia/management/working_hours_form.html', {'form': form, 'barbershop': barbershop})


@login_required
def working_hours_edit(request, working_hours_id):
    """
    Edita um horário de trabalho existente.

    Esta view lida com a edição de um horário de trabalho existente, processando o formulário
    de edição e salvando os dados atualizados.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        working_hours_id (int): O ID do horário de trabalho a ser editado.

    Returns:
        HttpResponse: Redireciona para o dashboard em caso de sucesso ou
                      renderiza o formulário novamente em caso de erro.

    Raises:
        Http404: Se o horário de trabalho não for encontrado.
    """
    working_hours = get_object_or_404(WorkingHours, id=working_hours_id)
    if request.method == 'POST':
        form = WorkingHoursForm(request.POST, instance=working_hours)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Horário de trabalho atualizado com sucesso.')
            return redirect('barbershop_management:working_hours_list', barbershop_id=working_hours.employee.barbershop.id)
    else:
        form = WorkingHoursForm(instance=working_hours)
    return render(request, 'barbearia/management/working_hours_form.html', {'form': form, 'working_hours': working_hours})


@login_required
def working_hours_delete(request, working_hours_id):
    """
    Exclui um horário de trabalho existente.

    Esta view lida com a exclusão de um horário de trabalho existente, confirmando a ação
    e redirecionando para a lista de horários de trabalho.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        working_hours_id (int): O ID do horário de trabalho a ser excluído.

    Returns:
        HttpResponse: Redireciona para a lista de horários de trabalho em caso de sucesso ou
                      renderiza o template de confirmação de exclusão em caso de erro.

    Raises:
        Http404: Se o horário de trabalho não for encontrado.
    """
    working_hours = get_object_or_404(WorkingHours, id=working_hours_id)
    barbershop = working_hours.employee.barbershop
    if request.method == 'POST':
        working_hours.delete()
        messages.success(request, 'Horário de trabalho excluído com sucesso.')
        return redirect('barbershop_management:working_hours_list', barbershop_id=barbershop.id)
    return render(request, 'barbearia/management/working_hours_confirm_delete.html', {'working_hours': working_hours})

# Expense views


@login_required
def expense_list(request, barbershop_id):
    """
    Lista todas as despesas de uma barbearia específica.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        barbershop_id (int): O ID da barbearia cujas despesas serão listadas.

    Returns:
        HttpResponse: A resposta renderizada com a lista de despesas.

    Raises:
        Http404: Se a barbearia não for encontrada ou não pertencer ao usuário logado.
    """
    barbershop = get_object_or_404(
        Barbershop, id=barbershop_id, owner=request.user)
    expenses = barbershop.expenses.all()
    return render(request, 'barbearia/management/expense_list.html', {'barbershop': barbershop, 'expenses': expenses})


@login_required
def expense_create(request, barbershop_id):
    """
    Cria uma nova despesa para uma barbearia específica.

    Esta view lida com a criação de uma nova despesa, processando o formulário
    de criação e salvando os dados.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        barbershop_id (int): O ID da barbearia para a qual a despesa será criada.

    Returns:
        HttpResponse: Redireciona para a lista de despesas em caso de sucesso ou
                      renderiza o formulário novamente em caso de erro.

    Raises:
        Http404: Se a barbearia não for encontrada ou não pertencer ao usuário logado.
    """
    barbershop = get_object_or_404(
        Barbershop, id=barbershop_id, owner=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.barbershop = barbershop
            expense.save()
            messages.success(request, 'Despesa adicionada com sucesso.')
            return redirect('barbershop_management:expense_list', barbershop_id=barbershop.id)
    else:
        form = ExpenseForm()
    return render(request, 'barbearia/management/expense_form.html', {'form': form, 'barbershop': barbershop})


@login_required
def expense_edit(request, expense_id):
    """
    Edita uma despesa existente.

    Esta view lida com a edição de uma despesa existente, processando o formulário
    de edição e salvando os dados atualizados.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        expense_id (int): O ID da despesa a ser editada.

    Returns:
        HttpResponse: Redireciona para o dashboard em caso de sucesso ou
                      renderiza o formulário novamente em caso de erro.

    Raises:
        Http404: Se a despesa não for encontrada.
    """
    expense = get_object_or_404(Expense, id=expense_id)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Despesa atualizada com sucesso.')
            return redirect('barbershop_management:expense_list', barbershop_id=expense.barbershop.id)
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'barbearia/management/expense_form.html', {'form': form, 'expense': expense})


@login_required
def expense_delete(request, expense_id):
    """
    Exclui uma despesa existente.

    Esta view lida com a exclusão de uma despesa existente, confirmando a ação
    e redirecionando para a lista de despesas.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        expense_id (int): O ID da despesa a ser excluída.

    Returns:
        HttpResponse: Redireciona para a lista de despesas em caso de sucesso ou
                      renderiza o template de confirmação de exclusão em caso de erro.

    Raises:
        Http404: Se a despesa não for encontrada.
    """
    expense = get_object_or_404(Expense, id=expense_id)
    barbershop = expense.barbershop
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Despesa excluída com sucesso.')
        return redirect('barbershop_management:expense_list', barbershop_id=barbershop.id)
    return render(request, 'barbearia/management/expense_confirm_delete.html', {'expense': expense})

# Inventory views


@login_required
def inventory_list(request, barbershop_id):
    """
    Lista todos os itens de inventário de uma barbearia específica.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        barbershop_id (int): O ID da barbearia cujos itens de inventário serão listados.

    Returns:
        HttpResponse: A resposta renderizada com a lista de itens de inventário.

    Raises:
        Http404: Se a barbearia não for encontrada ou não pertencer ao usuário logado.
    """
    barbershop = get_object_or_404(
        Barbershop, id=barbershop_id, owner=request.user)
    inventory_items = barbershop.inventory_items.all()
    return render(request, 'barbearia/management/inventory_list.html', {'barbershop': barbershop, 'inventory_items': inventory_items})


@login_required
def inventory_create(request, barbershop_id):
    """
    Cria um novo item de inventário para uma barbearia específica.

    Esta view lida com a criação de um novo item de inventário, processando o formulário
    de criação e salvando os dados.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        barbershop_id (int): O ID da barbearia para a qual o item de inventário será criado.

    Returns:
        HttpResponse: Redireciona para a lista de itens de inventário em caso de sucesso ou
                      renderiza o formulário novamente em caso de erro.

    Raises:
        Http404: Se a barbearia não for encontrada ou não pertencer ao usuário logado.
    """
    barbershop = get_object_or_404(
        Barbershop, id=barbershop_id, owner=request.user)
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            inventory = form.save(commit=False)
            inventory.barbershop = barbershop
            inventory.save()
            messages.success(
                request, 'Item de inventário adicionado com sucesso.')
            return redirect('barbershop_management:inventory_list', barbershop_id=barbershop.id)
    else:
        form = InventoryForm()
    return render(request, 'barbearia/management/inventory_form.html', {'form': form, 'barbershop': barbershop})


@login_required
def inventory_edit(request, inventory_id):
    """
    Edita um item de inventário existente.

    Esta view lida com a edição de um item de inventário existente, processando o formulário
    de edição e salvando os dados atualizados.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        inventory_id (int): O ID do item de inventário a ser editado.

    Returns:
        HttpResponse: Redireciona para o dashboard em caso de sucesso ou
                      renderiza o formulário novamente em caso de erro.

    Raises:
        Http404: Se o item de inventário não for encontrado.
    """
    inventory = get_object_or_404(Inventory, id=inventory_id)
    if request.method == 'POST':
        form = InventoryForm(request.POST, instance=inventory)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Item de inventário atualizado com sucesso.')
            return redirect('barbershop_management:inventory_list', barbershop_id=inventory.barbershop.id)
    else:
        form = InventoryForm(instance=inventory)
    return render(request, 'barbearia/management/inventory_form.html', {'form': form, 'inventory': inventory})


@login_required
def inventory_delete(request, inventory_id):
    """
    Exclui um item de inventário existente.

    Esta view lida com a exclusão de um item de inventário existente, confirmando a ação
    e redirecionando para a lista de itens de inventário.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        inventory_id (int): O ID do item de inventário a ser excluído.

    Returns:
        HttpResponse: Redireciona para a lista de itens de inventário em caso de sucesso ou
                      renderiza o template de confirmação de exclusão em caso de erro.

    Raises:
        Http404: Se o item de inventário não for encontrado.
    """
    inventory = get_object_or_404(Inventory, id=inventory_id)
    barbershop = inventory.barbershop
    if request.method == 'POST':
        inventory.delete()
        messages.success(request, 'Item de inventário excluído com sucesso.')
        return redirect('barbershop_management:inventory_list', barbershop_id=barbershop.id)
    return render(request, 'barbearia/management/inventory_confirm_delete.html', {'inventory': inventory})


@login_required
def employee_service_list(request, barbershop_id):
    """
    Lista todos os serviços de funcionários de uma barbearia específica.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        barbershop_id (int): O ID da barbearia cujos serviços de funcionários serão listados.

    Returns:
        HttpResponse: A resposta renderizada com a lista de serviços de funcionários.

    Raises:
        Http404: Se a barbearia não for encontrada ou não pertencer ao usuário logado.
    """
    barbershop = get_object_or_404(
        Barbershop, id=barbershop_id, owner=request.user)
    employee_services = EmployeeService.objects.filter(
        employee__barbershop=barbershop)
    return render(request, 'barbearia/management/employee_service_list.html', {'barbershop': barbershop, 'employee_services': employee_services})


@login_required
def employee_service_create(request, barbershop_id):
    """
    Cria um novo serviço de funcionário para uma barbearia específica.

    Esta view lida com a criação de um novo serviço de funcionário, processando o formulário
    de criação e salvando os dados.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        barbershop_id (int): O ID da barbearia para a qual o serviço de funcionário será criado.

    Returns:
        HttpResponse: Redireciona para a lista de serviços de funcionários em caso de sucesso ou
                      renderiza o formulário novamente em caso de erro.

    Raises:
        Http404: Se a barbearia não for encontrada ou não pertencer ao usuário logado.
    """
    barbershop = get_object_or_404(
        Barbershop, id=barbershop_id, owner=request.user)
    if request.method == 'POST':
        form = EmployeeServiceForm(request.POST)
        if form.is_valid():
            employee_service = form.save(commit=False)
            employee_service.save()
            messages.success(
                request, 'Serviço do funcionário adicionado com sucesso.')
            return redirect('barbershop_management:employee_service_list', barbershop_id=barbershop.id)
    else:
        form = EmployeeServiceForm()
    return render(request, 'barbearia/management/employee_service_form.html', {'form': form, 'barbershop': barbershop})


@login_required
def employee_service_delete(request, employee_service_id):
    """
    Exclui um serviço de funcionário existente.

    Esta view lida com a exclusão de um serviço de funcionário existente, confirmando a ação
    e redirecionando para a lista de serviços de funcionários.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        employee_service_id (int): O ID do serviço de funcionário a ser excluído.

    Returns:
        HttpResponse: Redireciona para a lista de serviços de funcionários em caso de sucesso ou
                      renderiza o template de confirmação de exclusão em caso de erro.

    Raises:
        Http404: Se o serviço de funcionário não for encontrado.
    """
    employee_service = get_object_or_404(
        EmployeeService, id=employee_service_id)
    barbershop = employee_service.employee.barbershop
    if request.method == 'POST':
        employee_service.delete()
        messages.success(
            request, 'Serviço do funcionário excluído com sucesso.')
        return redirect('barbershop_management:employee_service_list', barbershop_id=barbershop.id)
    return render(request, 'barbearia/management/employee_service_confirm_delete.html', {'employee_service': employee_service})


@login_required
def generate_booking_link(request, barbershop_id):
    """
    Gera um link de agendamento para uma barbearia específica.

    Esta view gera um link de agendamento único para uma barbearia, que pode ser compartilhado
    com clientes para permitir que eles façam agendamentos online.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        barbershop_id (int): O ID da barbearia para a qual o link de agendamento será gerado.

    Returns:
        HttpResponse: Redireciona para o link de agendamento gerado.

    Raises:
        Http404: Se a barbearia não for encontrada ou não pertencer ao usuário logado.
    """
    barbershop = get_object_or_404(
        Barbershop, id=barbershop_id, owner=request.user)
    booking_url = request.build_absolute_uri(
        reverse('barbershop_booking:booking', args=[barbershop.code])
    )
    # Você pode retornar esta URL em uma resposta JSON, renderizar em um template,
    # ou redirecionar diretamente para a página de agendamento
    return redirect(booking_url)


def login_view(request):
    """
    Lida com o processo de login de usuário.

    Esta view processa o formulário de login, autentica o usuário e o redireciona
    para o dashboard em caso de sucesso.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.

    Returns:
        HttpResponse: Redireciona para o dashboard em caso de sucesso ou
                      renderiza o formulário de login novamente em caso de erro.
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('barbershop_management:dashboard')
            else:
                messages.error(request, 'Usuário ou senha inválidos.')
    else:
        form = LoginForm()
    return render(request, 'barbearia/management/login.html', {'form': form})


def presentation(request):
    """
    Renderiza a página de apresentação do app de gerenciamento de barbearias.

    Esta view exibe uma visão geral do aplicativo e pergunta se o usuário é assinante,
    direcionando-o para o login ou para a página de planos.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.

    Returns:
        HttpResponse: A resposta renderizada com o template de apresentação.
    """
    return render(request, 'barbearia/management/presentation.html')
