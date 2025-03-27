from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from barbershop_app.models import User, Role, Service
import time
from datetime import timezone, timedelta

class BarbershopSeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Инициализация драйвера Chrome
        cls.selenium = webdriver.Chrome()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        # Создаем роль клиента
        self.client_role = Role.objects.create(role_name='Клиент')
        # Создаем тестовую услугу
        self.test_service = Service.objects.create(
            name='Тестовая стрижка',
            description='Тестовое описание',
            price=1000,
            duration=30
        )

    def test_registration(self):
        """Тест регистрации нового пользователя"""
        # Открываем страницу регистрации
        self.selenium.get(f'{self.live_server_url}{reverse("register")}')

        # Заполняем форму регистрации
        username_input = self.selenium.find_element(By.NAME, 'username')
        username_input.send_keys('testuser')

        name_input = self.selenium.find_element(By.NAME, 'name')
        name_input.send_keys('Test User')

        email_input = self.selenium.find_element(By.NAME, 'email')
        email_input.send_keys('test@example.com')

        phone_input = self.selenium.find_element(By.NAME, 'phone')
        phone_input.send_keys('+79001234567')

        password1_input = self.selenium.find_element(By.NAME, 'password1')
        password1_input.send_keys('testpass123!')

        password2_input = self.selenium.find_element(By.NAME, 'password2')
        password2_input.send_keys('testpass123!')

        # Отправляем форму
        password2_input.send_keys(Keys.RETURN)

        # Проверяем, что мы перенаправлены на главную страницу
        WebDriverWait(self.selenium, 10).until(
            EC.url_to_be(f'{self.live_server_url}/')
        )

        # Проверяем, что пользователь создан в базе данных
        self.assertTrue(User.objects.filter(username='testuser').exists())
