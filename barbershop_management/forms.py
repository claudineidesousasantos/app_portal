from django import forms
from django.contrib.auth.models import User
from .models import Employee, Service, WorkingHours, EmployeeService, Expense, Inventory, Barbershop


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'phone', 'role',
                  'hire_date', 'is_active', 'barbershop']


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'duration', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
        }


class WorkingHoursForm(forms.ModelForm):
    class Meta:
        model = WorkingHours
        fields = ['barbershop', 'day_of_week', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }


class EmployeeServiceForm(forms.ModelForm):
    class Meta:
        model = EmployeeService
        fields = ['employee', 'service']


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['description', 'amount', 'date', 'expense_type', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['name', 'quantity', 'reorder_level', 'unit_price']
        widgets = {
            'unit_price': forms.NumberInput(attrs={'step': '0.01'}),
        }


class EmployeeSearchForm(forms.Form):
    search = forms.CharField(required=False, label='Search Employees')


class ServiceSearchForm(forms.Form):
    search = forms.CharField(required=False, label='Search Services')


class ExpenseSearchForm(forms.Form):
    start_date = forms.DateField(
        required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(
        required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    expense_type = forms.ChoiceField(
        choices=[('', 'All')] + Expense.EXPENSE_TYPES, required=False)


class InventorySearchForm(forms.Form):
    search = forms.CharField(required=False, label='Search Inventory')
    low_stock = forms.BooleanField(
        required=False, label='Show Low Stock Items')


class BarbershopForm(forms.ModelForm):
    class Meta:
        model = Barbershop
        # ajuste conforme necessário
        fields = ['name', 'address', 'phone', 'description', 'email']


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


