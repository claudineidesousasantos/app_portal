from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from django.core.validators import RegexValidator
from django.utils.text import slugify

# Create your models here.


class Barbershop(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    description = models.TextField(verbose_name="Sobre nós", blank=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='owned_barbershops')
    code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_open = models.BooleanField(default=True, verbose_name="Aberto")
    slug = models.SlugField(unique=True, blank=True)
    
    DAYS_OF_WEEK = [
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    working_days = models.ManyToManyField(
        'DayOfWeek',
        related_name='barbershops',
        verbose_name="Dias de funcionamento"
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Employee(models.Model):
    """
    Representa um funcionário de uma barbearia.

    Este modelo não está vinculado a um usuário Django, permitindo um cadastro
    mais simples e direto de funcionários.

    Attributes:
        name (CharField): Nome completo do funcionário.
        phone (CharField): Número de telefone do funcionário.
        email (EmailField): Endereço de e-mail do funcionário.
        barbershop (ForeignKey): Barbearia onde o funcionário trabalha.
        role (CharField): Cargo ou função do funcionário na barbearia.
        hire_date (DateField): Data de contratação do funcionário.
        is_active (BooleanField): Indica se o funcionário está atualmente ativo.
    """
    ROLE_CHOICES = [
        ('barber', 'Barbeiro'),
        ('hairdresser', 'Cabeleireiro'),
        ('manicurist', 'Manicure'),
        ('receptionist', 'Recepcionista'),
        ('manager', 'Gerente'),
        ('other', 'Outro'),
    ]

    name = models.CharField(max_length=100, verbose_name="Nome completo")
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="O número de telefone deve estar no formato: '+999999999'. Até 15 dígitos permitidos."
    )
    phone = models.CharField(
        validators=[phone_regex], max_length=17, verbose_name="Telefone")
    barbershop = models.ForeignKey(
        'Barbershop',  # Assumindo que Barbershop está no mesmo app
        on_delete=models.CASCADE,
        related_name='employees',
        verbose_name="Barbearia"
    )
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, verbose_name="Cargo")
    hire_date = models.DateField(verbose_name="Data de contratação")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Funcionário"
        verbose_name_plural = "Funcionários"
        ordering = ['name']
        # Garante que um funcionário é único por telefone e barbearia
        unique_together = ['phone', 'barbershop']

    def __str__(self):
        return f"{self.name} - {self.get_role_display()}"

    def get_role_display_translated(self):
        return dict(self.ROLE_CHOICES)[self.role]


class Service(models.Model):
    barbershop = models.ForeignKey(
        Barbershop, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    duration = models.IntegerField(help_text="Duration in minutes")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.barbershop.name}"



class WorkingHours(models.Model):
    
    barbershop = models.ForeignKey('Barbershop', on_delete=models.CASCADE, related_name='working_hours')
    day_of_week = models.ForeignKey('DayOfWeek', on_delete=models.CASCADE, related_name='working_hours')
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('barbershop', 'day_of_week')

    def __str__(self):
        return f"{self.barbershop.name} - {self.day_of_week.name}: {self.start_time} - {self.end_time}"


class EmployeeService(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='services')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('employee', 'service')

    def __str__(self):
        return f"{self.employee} - {self.service}"


class Expense(models.Model):
    """
    Representa uma despesa da barbearia.

    Esta classe modela as despesas do negócio, permitindo o registro e categorização
    de diferentes tipos de gastos.

    Atributos:
        EXPENSE_TYPES (list): Lista de tuplas representando os tipos de despesas disponíveis.
        description (CharField): Breve descrição da despesa.
        amount (DecimalField): Valor da despesa.
        date (DateField): Data em que a despesa foi incorrida.
        expense_type (CharField): Tipo da despesa, escolhido a partir de EXPENSE_TYPES.
        notes (TextField): Campo opcional para notas adicionais sobre a despesa.

    Métodos:
        __str__: Retorna uma representação em string da despesa.
    """

    EXPENSE_TYPES = [
        ('supplies', 'Supplies'),
        ('equipment', 'Equipment'),
        ('utilities', 'Utilities'),
        ('rent', 'Rent'),
        ('salary', 'Salary'),
        ('other', 'Other'),
    ]

    barbershop = models.ForeignKey(
        Barbershop, on_delete=models.CASCADE, related_name='expenses')
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPES)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.description} - {self.barbershop.name}"


class Inventory(models.Model):
    """
    Representa um item no inventário da barbearia.

    Esta classe modela os produtos e suprimentos mantidos em estoque,
    permitindo o controle de quantidade, preço e reabastecimento.

    Atributos:
        name (CharField): Nome do item de inventário.
        quantity (IntegerField): Quantidade atual em estoque.
        reorder_level (IntegerField): Nível mínimo de estoque para reabastecimento.
        unit_price (DecimalField): Preço unitário do item.
        last_restocked (DateField): Data da última reposição de estoque.

    Métodos:
        __str__: Retorna uma representação em string do item de inventário.

    Meta:
        verbose_name_plural: Define o nome plural para "Inventories" na interface admin.
    """

    barbershop = models.ForeignKey(
        Barbershop, on_delete=models.CASCADE, related_name='inventory_items')
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    reorder_level = models.IntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    last_restocked = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.barbershop.name}"

    class Meta:
        verbose_name_plural = "Inventories"


class DayOfWeek(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    day = models.IntegerField(choices=DAYS_OF_WEEK, unique=True)
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name
