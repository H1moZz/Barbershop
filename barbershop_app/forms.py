from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import User, Role, Order, Service
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError

User = get_user_model()

class RegisterForm(UserCreationForm):
    name = forms.CharField(max_length=100, required=True, label='Полное имя')
    email = forms.EmailField(required=True, label='Email')
    phone = forms.CharField(max_length=20, required=True, label='Телефон')

    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.name = self.cleaned_data['name']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        # Устанавливаем роль "Клиент" по умолчанию
        client_role = Role.objects.get(role_name='Клиент')
        user.role = client_role
        if commit:
            user.save()
        return user

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['client', 'service', 'barber', 'appointment_date', 'appointment_time', 'discount']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, user=None, service_id=None, barber_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.user = user
            self.fields['client'].widget = forms.HiddenInput()
            self.fields['client'].initial = user
        
        # Если передан ID услуги, устанавливаем его как начальное значение
        if service_id:
            self.fields['service'].initial = service_id
            
        # Если передан ID мастера, устанавливаем его как начальное значение
        if barber_id:
            self.fields['barber'].initial = barber_id
            barber = User.objects.get(id=barber_id)
            self.fields['barber'].queryset = User.objects.filter(id=barber_id)
        else:
            self.fields['barber'].queryset = User.objects.filter(role__role_name='Мастер')

    def clean(self):
        cleaned_data = super().clean()
        appointment_date = cleaned_data.get('appointment_date')
        appointment_time = cleaned_data.get('appointment_time')
        barber = cleaned_data.get('barber')
        service = cleaned_data.get('service')

        if not all([appointment_date, appointment_time, barber, service]):
            return cleaned_data

        # Проверяем, что дата не в прошлом
        appointment_datetime = datetime.combine(appointment_date, appointment_time)
        if appointment_datetime < datetime.now():
            raise ValidationError('Нельзя создать заказ на прошедшее время')

        # Получаем продолжительность выбранной услуги
        service_duration = timedelta(minutes=service.duration)

        # Получаем время окончания текущей услуги
        end_time = (datetime.combine(appointment_date, appointment_time) + service_duration).time()

        # Проверяем пересечение с другими заказами
        conflicting_orders = Order.objects.filter(
            barber=barber,
            appointment_date=appointment_date,
            status__in=['pending', 'confirmed']
        ).exclude(pk=self.instance.pk if self.instance else None)

        for order in conflicting_orders:
            order_start = datetime.combine(order.appointment_date, order.appointment_time)
            order_end = order_start + timedelta(minutes=order.service.duration)
            current_start = datetime.combine(appointment_date, appointment_time)
            current_end = current_start + service_duration

            if (current_start < order_end and current_end > order_start):
                raise ValidationError(
                    f'Мастер занят с {order.appointment_time} до {order_end.time()}. '
                    f'Пожалуйста, выберите другое время.'
                )

        cleaned_data['total_price'] = service.price
        if cleaned_data.get('discount'):
            discount_percent = cleaned_data['discount'].discount_percent
            cleaned_data['total_price'] = service.price * (1 - discount_percent / 100)

        return cleaned_data

    def save(self, commit=True):
        order = super().save(commit=False)
        order.client = self.user
        order.total_price = self.cleaned_data['total_price']
        if commit:
            order.save()
        return order

class AdminUserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label='Пароль')
    
    class Meta:
        model = User
        fields = ['username', 'password', 'name', 'email', 'phone', 'role', 'profile_photo', 'description']
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user 

class AdminOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['client', 'service', 'barber', 'appointment_date', 'appointment_time', 'status', 'discount', 'total_price']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
            'status': forms.Select(choices=Order.STATUS_CHOICES),
        }

    def __init__(self, *args, service_id=None, barber_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['total_price'].widget.attrs['readonly'] = True
        
        # Если передан ID услуги, устанавливаем его как начальное значение
        if service_id:
            self.fields['service'].initial = service_id
            
        # Если передан ID мастера, устанавливаем его как начальное значение
        if barber_id:
            self.fields['barber'].initial = barber_id
            barber = User.objects.get(id=barber_id)
            self.fields['barber'].queryset = User.objects.filter(id=barber_id)
        else:
            self.fields['barber'].queryset = User.objects.filter(role__role_name='Мастер')

    def clean(self):
        cleaned_data = super().clean()
        appointment_date = cleaned_data.get('appointment_date')
        appointment_time = cleaned_data.get('appointment_time')
        barber = cleaned_data.get('barber')
        service = cleaned_data.get('service')

        if not all([appointment_date, appointment_time, barber, service]):
            return cleaned_data

        # Проверяем, что дата не в прошлом
        appointment_datetime = datetime.combine(appointment_date, appointment_time)
        if appointment_datetime < datetime.now():
            raise ValidationError('Нельзя создать заказ на прошедшее время')

        # Получаем продолжительность выбранной услуги
        service_duration = timedelta(minutes=service.duration)

        # Получаем время окончания текущей услуги
        end_time = (datetime.combine(appointment_date, appointment_time) + service_duration).time()

        # Проверяем пересечение с другими заказами
        conflicting_orders = Order.objects.filter(
            barber=barber,
            appointment_date=appointment_date,
            status__in=['pending', 'confirmed']
        ).exclude(pk=self.instance.pk if self.instance else None)

        for order in conflicting_orders:
            order_start = datetime.combine(order.appointment_date, order.appointment_time)
            order_end = order_start + timedelta(minutes=order.service.duration)
            current_start = datetime.combine(appointment_date, appointment_time)
            current_end = current_start + service_duration

            if (current_start < order_end and current_end > order_start):
                raise ValidationError(
                    f'Мастер занят с {order.appointment_time} до {order_end.time()}. '
                    f'Пожалуйста, выберите другое время.'
                )

        cleaned_data['total_price'] = service.price
        if cleaned_data.get('discount'):
            discount_percent = cleaned_data['discount'].discount_percent
            cleaned_data['total_price'] = service.price * (1 - discount_percent / 100)

        return cleaned_data

    def save(self, commit=True):
        order = super().save(commit=False)
        order.total_price = self.cleaned_data['total_price']
        if commit:
            order.save()
        return order 