# Generated by Django 5.1 on 2024-09-23 02:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('barbershop_management', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nome completo')),
                ('phone', models.CharField(max_length=20, verbose_name='Telefone')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Data de cadastro')),
                ('barbershop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clients', to='barbershop_management.barbershop', verbose_name='Barbearia')),
            ],
            options={
                'verbose_name': 'Cliente',
                'verbose_name_plural': 'Clientes',
                'ordering': ['-created_at'],
                'unique_together': {('phone', 'barbershop')},
            },
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('status', models.CharField(choices=[('scheduled', 'Scheduled'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='scheduled', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('barbershop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='barbershop_management.barbershop')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='barbershop_management.employee')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='barbershop_management.service')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='barbershop_booking.client')),
            ],
            options={
                'ordering': ['-date', '-start_time'],
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('appointment_reminder', 'Appointment Reminder'), ('appointment_confirmation', 'Appointment Confirmation'), ('appointment_cancellation', 'Appointment Cancellation')], max_length=30)),
                ('message', models.TextField()),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='barbershop_booking.appointment')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='barbershop_booking.client')),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('comment', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('appointment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='barbershop_booking.appointment')),
            ],
        ),
        migrations.CreateModel(
            name='EmployeeService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='booking_services', to='barbershop_management.employee')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='booking_services', to='barbershop_management.service')),
            ],
            options={
                'unique_together': {('employee', 'service')},
            },
        ),
    ]
