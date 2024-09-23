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
        fields = ['date', 'start_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
        }
