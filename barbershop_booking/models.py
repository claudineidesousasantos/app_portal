from django.db import models
from django.contrib.auth.models import User
from barbershop_management.models import Employee, Service, Barbershop


class Client(models.Model):
    """
    Representa um cliente no sistema de agendamento de barbearia.

    Este modelo usa o telefone e a barbearia como chave composta,
    permitindo que o mesmo número de telefone seja usado em diferentes barbearias.

    Attributes:
        name (CharField): Nome completo do cliente.
        phone (CharField): Número de telefone do cliente.
        barbershop (ForeignKey): Barbearia da qual o cliente é cliente.
        created_at (DateTimeField): Data e hora de criação do registro do cliente.
    """
    name = models.CharField(max_length=100, verbose_name="Nome completo")
    phone = models.CharField(max_length=20, verbose_name="Telefone")
    barbershop = models.ForeignKey(
        Barbershop, 
        on_delete=models.CASCADE, 
        related_name='clients',
        verbose_name="Barbearia"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de cadastro")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['-created_at']
        unique_together = ['phone', 'barbershop']  # Chave composta

    def __str__(self):
        return f"{self.name} - {self.phone} ({self.barbershop.name})"


class EmployeeService(models.Model):
    """
    Representa a associação entre um funcionário e os serviços que ele pode realizar.

    Attributes:
        employee (ForeignKey): Funcionário associado.
        service (ForeignKey): Serviço que o funcionário pode realizar.
    """
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='booking_services')
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name='booking_services')

    class Meta:
        unique_together = ('employee', 'service')

    def __str__(self):
        return f"{self.employee} - {self.service}"


class Appointment(models.Model):
    """
    Representa um agendamento de serviço na barbearia.

    Attributes:
        client (ForeignKey): Cliente que fez o agendamento.
        employee (ForeignKey): Funcionário designado para o serviço.
        service (ForeignKey): Serviço agendado.
        barbershop (ForeignKey): Barbearia onde o serviço será realizado.
        date (DateField): Data do agendamento.
        start_time (TimeField): Hora de início do agendamento.
        end_time (TimeField): Hora de término do agendamento.
        status (CharField): Status atual do agendamento (agendado, concluído, cancelado).
        created_at (DateTimeField): Data e hora de criação do agendamento.
        updated_at (DateTimeField): Data e hora da última atualização do agendamento.
    """
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='appointments')
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name='appointments')
    barbershop = models.ForeignKey(
        Barbershop, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client} - {self.service} on {self.date} at {self.start_time}"

    class Meta:
        ordering = ['-date', '-start_time']


class Review(models.Model):
    """
    Representa uma avaliação feita por um cliente após um serviço.

    Attributes:
        appointment (OneToOneField): Agendamento associado à avaliação.
        rating (IntegerField): Classificação numérica do serviço (1-5).
        comment (TextField): Comentário opcional do cliente sobre o serviço.
        created_at (DateTimeField): Data e hora de criação da avaliação.
    """
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.appointment}"


class Notification(models.Model):
    """
    Representa uma notificação enviada a um cliente.

    Attributes:
        client (ForeignKey): Cliente que receberá a notificação.
        appointment (ForeignKey): Agendamento associado à notificação.
        type (CharField): Tipo de notificação (lembrete, confirmação, cancelamento).
        message (TextField): Conteúdo da notificação.
        sent_at (DateTimeField): Data e hora de envio da notificação.
        is_read (BooleanField): Indica se a notificação foi lida pelo cliente.
    """
    TYPE_CHOICES = [
        ('appointment_reminder', 'Appointment Reminder'),
        ('appointment_confirmation', 'Appointment Confirmation'),
        ('appointment_cancellation', 'Appointment Cancellation'),
    ]

    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='notifications')
    appointment = models.ForeignKey(
        Appointment, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.type} for {self.client} - {self.appointment}"
