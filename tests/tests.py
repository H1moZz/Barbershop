from django.test import TestCase
from django.contrib.auth import get_user_model
from barbershop_app.models import Service, Order, Role, Discount
from barbershop_app.forms import OrderForm, AdminOrderForm
from datetime import datetime, timedelta
from decimal import Decimal

User = get_user_model()

class BarbershopTestCase(TestCase):
    def setUp(self):
        # Создаем роли
        self.client_role = Role.objects.create(role_name='Клиент')
        self.barber_role = Role.objects.create(role_name='Мастер')
        
        # Создаем тестовых пользователей
        self.client_user = User.objects.create_user(
            username='testclient',
            password='testpass12',
            name='Test Client',
            email='client@test.com',
            phone='1234567890',
            role=self.client_role
        )
        
        self.barber_user = User.objects.create_user(
            username='testbarber',
            password='testpass123',
            name='Test Barber',
            email='barber@test.com',
            phone='0987654321',
            role=self.barber_role
        )
        
        # Создаем тестовую услугу
        self.service = Service.objects.create(
            name='Test Haircut',
            description='Test haircut service',
            price=Decimal('1000.00'),
            duration=30
        )
        
        # Создаем тестовую скидку
        self.discount = Discount.objects.create(
            discount_percent=10,
            valid_until=datetime.now().date() + timedelta(days=30)
        )

    def test_service_creation(self):
        """Тест создания услуги"""
        self.assertEqual(self.service.name, 'Test Haircut')
        self.assertEqual(self.service.price, Decimal('1000.00'))
        self.assertEqual(self.service.duration, 30)

    def test_order_creation(self):
        """Тест создания заказа"""
        order = Order.objects.create(
            client=self.client_user,
            barber=self.barber_user,
            service=self.service,
            appointment_date=datetime.now().date() + timedelta(days=1),
            appointment_time=datetime.now().time(),
            total_price=self.service.price
        )
        
        self.assertEqual(order.client, self.client_user)
        self.assertEqual(order.barber, self.barber_user)
        self.assertEqual(order.service, self.service)
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.total_price, Decimal('1000.00'))

