from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from .models import Service, Order, Discount, Role
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q
from .forms import RegisterForm, OrderForm, AdminUserCreateForm, AdminOrderForm
from django.core.exceptions import ValidationError
from django.http import JsonResponse, FileResponse
from datetime import datetime, timedelta, time
from .utils import generate_receipt_pdf
import os
from django.conf import settings

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешно завершена!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'barbershop_app/register.html', {'form': form})

def is_admin(user):
    return user.is_staff

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

# Представления для пользователей
class UserListView(StaffRequiredMixin, ListView):
    model = User
    template_name = 'barbershop_app/user_list.html'
    context_object_name = 'users'

class UserCreateView(StaffRequiredMixin, CreateView):
    model = User
    form_class = AdminUserCreateForm
    template_name = 'barbershop_app/user_form.html'
    success_url = reverse_lazy('user_list')

class UserUpdateView(StaffRequiredMixin, UpdateView):
    model = User
    template_name = 'barbershop_app/user_form.html'
    fields = ['username', 'name', 'email', 'phone', 'role']
    success_url = reverse_lazy('user_list')

class UserDeleteView(StaffRequiredMixin, DeleteView):
    model = User
    template_name = 'barbershop_app/user_confirm_delete.html'
    success_url = reverse_lazy('user_list')

# Представления для услуг
class ServiceListView(ListView):
    model = Service
    template_name = 'barbershop_app/service_list.html'
    context_object_name = 'services'

class ServiceCreateView(StaffRequiredMixin, CreateView):
    model = Service
    template_name = 'barbershop_app/service_form.html'
    fields = ['name', 'description', 'price', 'duration']
    success_url = reverse_lazy('service_list')

class ServiceUpdateView(StaffRequiredMixin, UpdateView):
    model = Service
    template_name = 'barbershop_app/service_form.html'
    fields = ['name', 'description', 'price', 'duration']
    success_url = reverse_lazy('service_list')

class ServiceDeleteView(StaffRequiredMixin, DeleteView):
    model = Service
    template_name = 'barbershop_app/service_confirm_delete.html'
    success_url = reverse_lazy('service_list')

# Представления для заказов
class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'barbershop_app/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(Q(client=self.request.user) | Q(barber=self.request.user))

@login_required
def create_order(request, service_id=None, barber_id=None):
    # Выбираем форму в зависимости от типа пользователя
    form_class = AdminOrderForm if request.user.is_staff else OrderForm
    
    if request.method == 'POST':
        # Для AdminOrderForm не передаем user
        if request.user.is_staff:
            form = form_class(request.POST, service_id=service_id, barber_id=barber_id)
        else:
            form = form_class(request.POST, user=request.user, service_id=service_id, barber_id=barber_id)
            
        if form.is_valid():
            try:
                order = form.save()
                messages.success(request, 'Заказ успешно создан!')
                return redirect('order_list')
            except ValidationError as e:
                messages.error(request, str(e))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        # Для AdminOrderForm не передаем user
        if request.user.is_staff:
            form = form_class(service_id=service_id, barber_id=barber_id)
        else:
            form = form_class(user=request.user, service_id=service_id, barber_id=barber_id)
    
    return render(request, 'barbershop_app/order_form.html', {
        'form': form,
        'service_id': service_id,
        'barber_id': barber_id,
        'is_admin': request.user.is_staff
    })

@login_required
def update_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    # Проверяем права доступа
    if not request.user.is_staff and request.user != order.client and request.user != order.barber:
        messages.error(request, 'У вас нет прав для редактирования этого заказа')
        return redirect('order_list')
    
    if request.method == 'POST':
        # Используем разные формы для админа и обычных пользователей
        if request.user.is_staff:
            form = AdminOrderForm(request.POST, instance=order)
        else:
            form = OrderForm(request.POST, user=order.client, instance=order)
            
        if form.is_valid():
            order = form.save()
            messages.success(request, 'Заказ успешно обновлен!')
            return redirect('order_list')
    else:
        # Используем разные формы для админа и обычных пользователей
        if request.user.is_staff:
            form = AdminOrderForm(instance=order)
        else:
            form = OrderForm(user=order.client, instance=order)
    
    return render(request, 'barbershop_app/order_form.html', {
        'form': form,
        'order': order,
        'is_admin': request.user.is_staff
    })

class OrderDeleteView(StaffRequiredMixin, DeleteView):
    model = Order
    template_name = 'barbershop_app/order_confirm_delete.html'
    success_url = reverse_lazy('order_list')

# Представления для скидок
class DiscountListView(ListView):
    model = Discount
    template_name = 'barbershop_app/discount_list.html'
    context_object_name = 'discounts'

class DiscountCreateView(StaffRequiredMixin, CreateView):
    model = Discount
    template_name = 'barbershop_app/discount_form.html'
    fields = ['discount_percent', 'valid_until']
    success_url = reverse_lazy('discount_list')

class DiscountUpdateView(StaffRequiredMixin, UpdateView):
    model = Discount
    template_name = 'barbershop_app/discount_form.html'
    fields = ['discount_percent', 'valid_until']
    success_url = reverse_lazy('discount_list')

class DiscountDeleteView(StaffRequiredMixin, DeleteView):
    model = Discount
    template_name = 'barbershop_app/discount_confirm_delete.html'
    success_url = reverse_lazy('discount_list')

# Домашняя страница
def home(request):
    barbers = User.objects.filter(role__role_name='Мастер').select_related('role')
    return render(request, 'barbershop_app/home.html', {'barbers': barbers})

# Профиль пользователя
@login_required
def profile(request):
    # Получаем заказы, где пользователь является клиентом
    client_orders = Order.objects.filter(client=request.user).order_by('-order_date')
    
    # Получаем заказы, где пользователь является мастером
    barber_orders = None
    if request.user.role and request.user.role.role_name == 'Мастер':
        barber_orders = Order.objects.filter(barber=request.user).order_by('-order_date')
    
    return render(request, 'barbershop_app/profile.html', {
        'client_orders': client_orders,
        'barber_orders': barber_orders,
        'user': request.user
    })

@login_required
def profile_update(request):
    if request.method == 'POST':
        user = request.user
        user.name = request.POST.get('name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        user.description = request.POST.get('description')
        
        # Обработка фото профиля
        if 'profile_photo' in request.FILES:
            user.profile_photo = request.FILES['profile_photo']
        
        user.save()
        messages.success(request, 'Профиль успешно обновлен!')
        return redirect('profile')
    return redirect('profile')

def get_barbers_by_service(request, service_id):
    User = get_user_model()
    barbers = User.objects.filter(
        role__role_name='Мастер',
        is_active=True
    ).values('id', 'name')
    return JsonResponse(list(barbers), safe=False)

def get_available_time_slots(request):
    date_str = request.GET.get('date')
    barber_id = request.GET.get('barber_id')
    service_id = request.GET.get('service_id')
    
    if not all([date_str, barber_id, service_id]):
        return JsonResponse({'error': 'Не все параметры предоставлены'}, status=400)
    
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        barber = User.objects.get(id=barber_id, role__role_name='Мастер')
        service = Service.objects.get(id=service_id)
    except (ValueError, User.DoesNotExist, Service.DoesNotExist):
        return JsonResponse({'error': 'Неверные параметры'}, status=400)

    # Получаем все заказы мастера на выбранную дату
    existing_orders = Order.objects.filter(
        barber=barber,
        appointment_date=selected_date,
        status__in=['pending', 'confirmed']
    ).order_by('appointment_time')

    # Создаем временные слоты с 9:00 до 21:00 с интервалом в 30 минут
    available_slots = []
    booked_slots = []  # Список занятых слотов
    current_time = time(9, 0)  # Начало рабочего дня
    end_time = time(21, 0)     # Конец рабочего дня
    service_duration = timedelta(minutes=service.duration)

    while current_time < end_time:
        slot_start = datetime.combine(selected_date, current_time)
        slot_end = slot_start + service_duration

        # Проверяем, не пересекается ли слот с существующими заказами
        is_available = True
        for order in existing_orders:
            order_start = datetime.combine(selected_date, order.appointment_time)
            order_end = order_start + timedelta(minutes=order.service.duration)
            
            if (slot_start < order_end and slot_end > order_start):
                is_available = False
                # Добавляем информацию о занятом слоте
                booked_slots.append({
                    'time': current_time.strftime('%H:%M'),
                    'service_name': order.service.name,
                    'duration': order.service.duration
                })
                break

        # Если текущее время больше времени слота на сегодняшний день, 
        # помечаем слот как недоступный
        if selected_date == datetime.now().date() and current_time < datetime.now().time():
            is_available = False

        if is_available:
            available_slots.append(current_time.strftime('%H:%M'))

        # Переходим к следующему слоту (каждые 30 минут)
        current_time = (datetime.combine(datetime.min, current_time) + timedelta(minutes=30)).time()

    return JsonResponse({
        'available_slots': available_slots,
        'booked_slots': booked_slots
    })

def get_available_slots(request, barber_id, date):
    """API эндпоинт для получения доступных временных слотов"""
    try:
        # Преобразуем строку даты в объект datetime
        selected_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Получаем все заказы барбера на выбранную дату
        booked_slots = Order.objects.filter(
            barber_id=barber_id,
            appointment_date=selected_date
        ).values('appointment_time', 'service__duration')

        # Преобразуем заказы в формат для фронтенда
        booked_slots_data = []
        for slot in booked_slots:
            time = slot['appointment_time']
            duration = slot['service__duration'] or 60
            booked_slots_data.append({
                'time': time.strftime('%H:%M'),
                'duration': duration
            })

        # Генерируем все возможные временные слоты
        available_slots = []
        start_time = datetime.strptime('09:00', '%H:%M').time()
        end_time = datetime.strptime('21:00', '%H:%M').time()
        
        current_time = datetime.combine(selected_date, start_time)
        end_datetime = datetime.combine(selected_date, end_time)

        while current_time < end_datetime:
            time_str = current_time.strftime('%H:%M')
            
            # Проверяем, не занят ли этот слот
            is_available = True
            for booked in booked_slots_data:
                booked_time = datetime.strptime(booked['time'], '%H:%M').time()
                booked_datetime = datetime.combine(selected_date, booked_time)
                booked_end = booked_datetime + timedelta(minutes=booked['duration'])
                
                if (current_time >= booked_datetime and 
                    current_time < booked_end):
                    is_available = False
                    break

            if is_available:
                available_slots.append(time_str)
            
            current_time += timedelta(minutes=30)  # Шаг в 30 минут

        return JsonResponse({
            'available_slots': available_slots,
            'booked_slots': booked_slots_data
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def generate_receipt(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    
    # Проверяем права доступа
    if not request.user.is_staff and request.user != order.client and request.user != order.barber:
        messages.error(request, 'У вас нет прав для просмотра этого чека')
        return redirect('order_list')
    
    # Создаем директорию для чеков, если её нет
    receipts_dir = os.path.join(settings.MEDIA_ROOT, 'receipts')
    os.makedirs(receipts_dir, exist_ok=True)
    
    # Генерируем имя файла
    filename = f'receipt_order_{order.id}.pdf'
    filepath = os.path.join(receipts_dir, filename)
    
    # Генерируем PDF
    generate_receipt_pdf(order, filepath)
    
    # Отправляем файл пользователю
    response = FileResponse(open(filepath, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
