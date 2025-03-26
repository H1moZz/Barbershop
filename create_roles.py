import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from barbershop_app.models import Role

# Создаем базовые роли
roles = [
    {'role_name': 'Администратор', 'description': 'Полный доступ к системе'},
    {'role_name': 'Мастер', 'description': 'Работа с заказами и клиентами'},
    {'role_name': 'Клиент', 'description': 'Запись на услуги'},
]

for role_data in roles:
    Role.objects.get_or_create(
        role_name=role_data['role_name'],
        defaults={'description': role_data['description']}
    ) 