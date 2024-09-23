from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from barbershop_management.models import Barbershop, Employee, Service

class BarbershopManagementViewsTestCase(TestCase):
    def setUp(self):
        # Criar um usuário para os testes
        self.user = User.objects.create_user(username='testuser', password='12345')
        
        # Criar uma barbearia para os testes
        self.barbershop = Barbershop.objects.create(
            name='Test Barbershop',
            owner=self.user,
            address='123 Test St',
            phone='1234567890'
        )
        
        # Criar alguns funcionários e serviços para os testes
        self.employee1 = Employee.objects.create(name='John Doe', barbershop=self.barbershop)
        self.employee2 = Employee.objects.create(name='Jane Doe', barbershop=self.barbershop)
        
        self.service1 = Service.objects.create(name='Haircut', price=20.00, barbershop=self.barbershop)
        self.service2 = Service.objects.create(name='Shave', price=15.00, barbershop=self.barbershop)
        
        # Criar um cliente para fazer requisições
        self.client = Client()

    def test_dashboard_view_authenticated(self):
        # Fazer login
        self.client.login(username='testuser', password='12345')
        
        # Fazer uma requisição GET para o dashboard
        response = self.client.get(reverse('barbershop_management:dashboard'))
        
        # Verificar se a resposta é 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Verificar se o template correto está sendo usado
        self.assertTemplateUsed(response, 'barbearia/management/dashboard.html')
        
        # Verificar se os dados corretos estão no contexto
        self.assertEqual(response.context['barbershop'], self.barbershop)
        self.assertEqual(response.context['employees_count'], 2)
        self.assertEqual(response.context['services_count'], 2)
        self.assertIn(self.employee1, response.context['recent_employees'])
        self.assertIn(self.employee2, response.context['recent_employees'])
        self.assertIn(self.service1, response.context['recent_services'])
        self.assertIn(self.service2, response.context['recent_services'])

    def test_dashboard_view_unauthenticated(self):
        # Tentar acessar o dashboard sem fazer login
        response = self.client.get(reverse('barbershop_management:dashboard'))
        
        # Verificar se o usuário é redirecionado para a página de login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response['Location'])

    def test_employee_list_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('barbershop_management:employee_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'barbearia/management/employee_list.html')
        self.assertContains(response, 'John Doe')
        self.assertContains(response, 'Jane Doe')

    def test_service_list_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('barbershop_management:service_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'barbearia/management/service_list.html')
        self.assertContains(response, 'Haircut')
        self.assertContains(response, 'Shave')

    def test_employee_create_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('barbershop_management:employee_create'), {
            'name': 'New Employee',
            'phone': '9876543210',
            'barbershop': self.barbershop.id
        })
        self.assertEqual(response.status_code, 302)  # Redirecionamento após criação
        self.assertTrue(Employee.objects.filter(name='New Employee').exists())

    def test_service_create_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('barbershop_management:service_create'), {
            'name': 'New Service',
            'price': 25.00,
            'barbershop': self.barbershop.id
        })
        self.assertEqual(response.status_code, 302)  # Redirecionamento após criação
        self.assertTrue(Service.objects.filter(name='New Service').exists())
