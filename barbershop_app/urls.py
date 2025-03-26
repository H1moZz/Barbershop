from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    home, profile, profile_update, register,
    UserListView, UserCreateView, UserUpdateView, UserDeleteView,
    ServiceListView, ServiceCreateView, ServiceUpdateView, ServiceDeleteView,
    OrderListView, create_order, update_order, OrderDeleteView, generate_receipt,
    DiscountListView, DiscountCreateView, DiscountUpdateView, DiscountDeleteView,
    get_barbers_by_service, get_available_time_slots, get_available_slots
)

urlpatterns = [
    path('', home, name='home'),
    path('profile/', profile, name='profile'),
    path('profile/update/', profile_update, name='profile_update'),
    
    # Аутентификация
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', register, name='register'),
    
    # Пользователи
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/add/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    
    # Услуги
    path('services/', ServiceListView.as_view(), name='service_list'),
    path('services/add/', ServiceCreateView.as_view(), name='service_create'),
    path('services/<int:pk>/edit/', ServiceUpdateView.as_view(), name='service_update'),
    path('services/<int:pk>/delete/', ServiceDeleteView.as_view(), name='service_delete'),
    
    # Заказы
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/create/', create_order, name='order_create'),
    path('orders/create/<int:service_id>/', create_order, name='order_create_with_service'),
    path('orders/create/barber/<int:barber_id>/', create_order, name='order_create_with_barber'),
    path('orders/create/barber/<int:barber_id>/service/<int:service_id>/', create_order, name='order_create_with_barber_service'),
    path('orders/<int:pk>/edit/', update_order, name='order_update'),
    path('orders/<int:pk>/delete/', OrderDeleteView.as_view(), name='order_delete'),
    path('orders/<int:order_id>/receipt/', generate_receipt, name='generate_receipt'),
    
    # Скидки
    path('discounts/', DiscountListView.as_view(), name='discount_list'),
    path('discounts/add/', DiscountCreateView.as_view(), name='discount_create'),
    path('discounts/<int:pk>/edit/', DiscountUpdateView.as_view(), name='discount_update'),
    path('discounts/<int:pk>/delete/', DiscountDeleteView.as_view(), name='discount_delete'),

    path('api/barbers-by-service/<int:service_id>/', get_barbers_by_service, name='barbers_by_service'),
    path('api/available-time-slots/', get_available_time_slots, name='available_time_slots'),
    path('api/available-slots/<int:barber_id>/<str:date>/', get_available_slots, name='api_available_slots'),
] 