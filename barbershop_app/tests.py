from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Service, Order, Role, Discount
from .forms import OrderForm, AdminOrderForm
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

    def test_order_with_discount(self):
        """Тест создания заказа со скидкой"""
        order = Order.objects.create(
            client=self.client_user,
            barber=self.barber_user,
            service=self.service,
            appointment_date=datetime.now().date() + timedelta(days=1),
            appointment_time=datetime.now().time(),
            discount=self.discount,
            total_price=self.service.price * (Decimal('1') - Decimal(str(self.discount.discount_percent)) / Decimal('100'))
        )
        
        expected_price = Decimal('900.00')  # 1000 - 10%
        self.assertEqual(order.total_price, expected_price)

    def test_order_list_view(self):
        """Тест представления списка заказов"""
        # Создаем тестовый заказ
        Order.objects.create(
            client=self.client_user,
            barber=self.barber_user,
            service=self.service,
            appointment_date=datetime.now().date() + timedelta(days=1),
            appointment_time=datetime.now().time(),
            total_price=self.service.price
        )
        
        # Авторизуемся как клиент
        self.client.login(username='testclient', password='testpass12')
        
        # Получаем страницу со списком заказов
        response = self.client.get(reverse('order_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'barbershop_app/order_list.html')
        self.assertEqual(len(response.context['orders']), 1)

    def test_barber_availability(self):
        """Тест проверки доступности барбера"""
        # Создаем заказ на определенное время
        appointment_date = datetime.now().date() + timedelta(days=1)
        appointment_time = datetime.strptime('14:00', '%H:%M').time()
        
        Order.objects.create(
            client=self.client_user,
            barber=self.barber_user,
            service=self.service,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            total_price=self.service.price
        )
        
        # Авторизуемся
        self.client.login(username='testclient', password='testpass123')
        
        # Проверяем доступность барбера через API
        response = self.client.get(
            reverse('api_available_slots', args=[self.barber_user.id, appointment_date.strftime('%Y-%m-%d')])
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Проверяем, что время 14:00 отсутствует в доступных слотах
        self.assertNotIn('14:00', data['available_slots'])
        # Проверяем, что это время есть в списке занятых слотов
        booked_times = [slot['time'] for slot in data['booked_slots']]
        self.assertIn('14:00', booked_times)

    def test_order_form_validation(self):
        """Тест валидации формы заказа"""
        # Тестируем форму с правильными данными
        tomorrow = datetime.now().date() + timedelta(days=1)
        appointment_time = datetime.strptime('14:00', '%H:%M').time()
        form_data = {
            'client': self.client_user.id,
            'service': self.service.id,
            'barber': self.barber_user.id,
            'appointment_date': tomorrow,
            'appointment_time': appointment_time,
            'discount': self.discount.id if self.discount else '',
            'total_price': self.service.price
        }
        
        form = OrderForm(data=form_data, user=self.client_user)
        self.assertTrue(form.is_valid(), f"Форма невалидна. Ошибки: {form.errors}")
        
        # Тестируем форму с датой в прошлом
        yesterday = datetime.now().date() - timedelta(days=1)
        form_data['appointment_date'] = yesterday
        
        form = OrderForm(data=form_data, user=self.client_user)
        self.assertFalse(form.is_valid())
        self.assertIn('Нельзя создать заказ на прошедшее время', str(form.errors))

    def test_admin_order_form(self):
        """Тест формы заказа для администратора"""
        tomorrow = datetime.now().date() + timedelta(days=1)
        form_data = {
            'client': self.client_user.id,
            'service': self.service.id,
            'barber': self.barber_user.id,
            'appointment_date': tomorrow,
            'appointment_time': '14:00',
            'status': 'confirmed',
            'total_price': '1000.00'
        }
        
        form = AdminOrderForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Проверяем, что поле total_price доступно только для чтения
        self.assertTrue(form.fields['total_price'].widget.attrs.get('readonly'))
