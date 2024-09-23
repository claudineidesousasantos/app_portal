from django.contrib import admin
from .models import Barbershop, Employee, Service, WorkingHours, EmployeeService, Expense, Inventory, DayOfWeek
from django.db import models
from django.forms import ModelForm
from django.contrib.admin.widgets import FilteredSelectMultiple

class BarbershopAdminForm(ModelForm):
    class Meta:
        model = Barbershop
        fields = '__all__'
        widgets = {
            'working_days': FilteredSelectMultiple("Dias de trabalho", is_stacked=False),
        }

@admin.register(Barbershop)
class BarbershopAdmin(admin.ModelAdmin):
    form = BarbershopAdminForm
    filter_horizontal = ('working_days',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'barbershop', 'role', 'hire_date', 'is_active')
    list_filter = ('barbershop', 'role', 'is_active', 'hire_date')
    search_fields = ('name', 'phone', 'email', 'barbershop__name')
    date_hierarchy = 'hire_date'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('barbershop')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'barbershop', 'description', 'price', 'duration', 'is_active')
    list_filter = ('barbershop', 'is_active')
    search_fields = ('name', 'description', 'barbershop__name')

@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = ('barbershop', 'day_of_week', 'start_time', 'end_time')
    list_filter = ('barbershop', 'day_of_week')

@admin.register(EmployeeService)
class EmployeeServiceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'service')
    list_filter = ('employee__barbershop', 'service')
    search_fields = ('employee__name', 'service__name')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('barbershop', 'description', 'amount', 'date', 'expense_type')
    list_filter = ('barbershop', 'expense_type', 'date')
    search_fields = ('description', 'barbershop__name')
    date_hierarchy = 'date'

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('barbershop', 'name', 'quantity', 'reorder_level', 'unit_price', 'last_restocked')
    list_filter = ('barbershop', 'last_restocked')
    search_fields = ('name', 'barbershop__name')
    date_hierarchy = 'last_restocked'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('barbershop')

admin.site.register(DayOfWeek)
