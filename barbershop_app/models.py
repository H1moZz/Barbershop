from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class Role(models.Model):
    role_name = models.CharField(max_length=50, verbose_name='Название роли')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')

    def __str__(self):
        return self.role_name

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Роль')
    name = models.CharField(max_length=255, verbose_name='Полное имя')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон')
    email = models.EmailField('Email', max_length=50, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True, verbose_name='Фото профиля')
    description = models.TextField(blank=True, null=True, verbose_name='О себе')

    def __str__(self):
        return self.name or self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

class Service(models.Model):
    name = models.CharField('Название услуги', max_length=50)
    description = models.CharField('Описание', max_length=255, blank=True, null=True)
    price = models.DecimalField('Стоимость', max_digits=8, decimal_places=2)
    duration = models.IntegerField('Длительность (мин.)')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

class Discount(models.Model):
    discount_percent = models.DecimalField('Процент скидки', max_digits=5, decimal_places=2)
    valid_until = models.DateField('Действует до', blank=True, null=True)

    def __str__(self):
        return f"Скидка {self.discount_percent}%"

    class Meta:
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('confirmed', 'Подтвержден'),
        ('completed', 'Завершен'),
        ('canceled', 'Отменен'),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_orders', verbose_name='Клиент')
    barber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='barber_orders', verbose_name='Мастер')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name='Услуга')
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Скидка')
    order_date = models.DateTimeField('Дата заказа', auto_now_add=True)
    appointment_date = models.DateField('Дата записи')
    appointment_time = models.TimeField('Время записи')
    total_price = models.DecimalField('Итоговая стоимость', max_digits=10, decimal_places=2)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Заказ {self.id} - {self.client.name}"

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-order_date']
