from django.contrib import admin
from .models import Client, Appointment, Review, Notification, EmployeeService

# Register your models here.


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'barbershop', 'created_at')
    list_filter = ('barbershop', 'created_at')
    search_fields = ('name', 'phone', 'barbershop__name')
    date_hierarchy = 'created_at'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'employee', 'service', 'barbershop', 'date', 'time', 'status')
    list_filter = ('status', 'date', 'barbershop')
    search_fields = ('client__name', 'employee__user__username', 'service__name')
    date_hierarchy = 'date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('client', 'employee', 'service', 'barbershop')


admin.site.register(Review)
admin.site.register(Notification)
