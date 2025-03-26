import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from barbershop_app.models import Service

# Список базовых услуг барбершопа
services = [
    {
        'name': 'Мужская стрижка',
        'description': 'Классическая мужская стрижка с использованием ножниц и машинки. Включает мытье головы и укладку.',
        'price': 1500,
        'duration': 60
    },
    {
        'name': 'Стрижка машинкой',
        'description': 'Быстрая стрижка под одну насадку или несколько насадок машинкой.',
        'price': 1000,
        'duration': 30
    },
    {
        'name': 'Стрижка бороды',
        'description': 'Моделирование и стрижка бороды с использованием машинки и ножниц. Включает обработку контуров.',
        'price': 800,
        'duration': 30
    },
    {
        'name': 'Королевское бритье',
        'description': 'Классическое бритье опасной бритвой с распариванием, использованием горячих полотенец и уходом за кожей.',
        'price': 1200,
        'duration': 45
    },
    {
        'name': 'Комплекс (стрижка + борода)',
        'description': 'Мужская стрижка и моделирование бороды. Включает мытье головы и укладку.',
        'price': 2000,
        'duration': 90
    },
    {
        'name': 'Детская стрижка',
        'description': 'Стрижка для мальчиков до 12 лет. Включает мытье головы и укладку.',
        'price': 1000,
        'duration': 45
    },
    {
        'name': 'Укладка',
        'description': 'Мытье головы и укладка волос с использованием профессиональных средств.',
        'price': 500,
        'duration': 30
    },
    {
        'name': 'Камуфляж седины',
        'description': 'Окрашивание седых волос в натуральный цвет с эффектом естественности.',
        'price': 2500,
        'duration': 60
    },
    {
        'name': 'Тонирование бороды',
        'description': 'Окрашивание бороды для придания равномерного цвета и маскировки седины.',
        'price': 1500,
        'duration': 45
    },
    {
        'name': 'VIP-уход',
        'description': 'Комплексный уход включающий стрижку, бритье, уход за лицом и массаж головы.',
        'price': 3500,
        'duration': 120
    }
]

# Добавляем услуги в базу данных
for service_data in services:
    Service.objects.get_or_create(
        name=service_data['name'],
        defaults={
            'description': service_data['description'],
            'price': service_data['price'],
            'duration': service_data['duration']
        }
    )

print('Услуги успешно добавлены в базу данных!') 