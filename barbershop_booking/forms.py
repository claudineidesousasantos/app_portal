from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Client, Appointment


class LoginForm(forms.Form):
    username = forms.CharField(label='Nome de usuário', max_length=150)
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)


class ClientSignUpForm(UserCreationForm):
    first_name = forms.CharField(label='Nome', max_length=30, required=True)
    last_name = forms.CharField(
        label='Sobrenome', max_length=30, required=True)
    phone = forms.CharField(label='Telefone', max_length=20, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'phone', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            Client.objects.create(user=user, phone=self.cleaned_data['phone'])
        return user

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['service', 'employee', 'date', 'time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        employee = cleaned_data.get('employee')

        if date and time and employee:
            barbershop = employee.barbershop
            day_of_week = date.weekday()

            # Verificar se a barbearia está aberta neste dia
            if not barbershop.working_days.filter(day=day_of_week).exists():
                raise forms.ValidationError("A barbearia está fechada neste dia.")

            # Verificar o horário de funcionamento
            working_hours = barbershop.working_hours.filter(day_of_week__day=day_of_week).first()
            if working_hours:
                if time < working_hours.start_time or time > working_hours.end_time:
                    raise forms.ValidationError("O horário selecionado está fora do horário de funcionamento.")
            else:
                raise forms.ValidationError("Não há horário de funcionamento definido para este dia.")

        return cleaned_data
    def save(self, commit=True):
        appointment = super().save(commit=False)
        if commit:
            appointment.save()
        return appointment


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'phone']

class PhoneVerificationForm(forms.Form):
    phone = forms.CharField(max_length=20, label="Telefone")
