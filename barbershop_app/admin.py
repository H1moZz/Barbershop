from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Role, Service, Order, Discount

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'name', 'phone', 'role')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('name', 'email', 'phone', 'profile_photo', 'description')}),
        ('Роли', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'name', 'email', 'phone', 'password1', 'password2', 'profile_photo', 'description', 'role'),
        }),
    )
    search_fields = ('username', 'name', 'email')
    ordering = ('username',)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_name', 'description')
    search_fields = ('role_name',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration')
    search_fields = ('name',)
    list_filter = ('price', 'duration')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'service', 'barber', 'appointment_date', 'get_status_display')
    list_filter = ('status',)
    search_fields = ('client__username', 'service__name', 'barber__username')
    date_hierarchy = 'appointment_date'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('client', 'service', 'barber')
        }),
        ('Дата и время', {
            'fields': ('appointment_date', 'appointment_time')
        }),
        ('Статус и оплата', {
            'fields': ('status', 'discount', 'total_price')
        }),
    )
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    get_status_display.short_description = 'Статус'
    get_status_display.admin_order_field = 'status'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # если это существующий объект
            return ('total_price',)  # делаем total_price только для чтения
        return ()

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('discount_percent', 'valid_until')
    list_filter = ('valid_until',)
