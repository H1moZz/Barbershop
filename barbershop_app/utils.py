from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from datetime import datetime
import os

def generate_receipt_pdf(order, output_path):
    """Генерирует PDF-чек для заказа"""
    # Создаем PDF-документ
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # Регистрируем системный шрифт Arial
    arial_path = "C:/Windows/Fonts/arial.ttf"  # Путь к системному шрифту Arial
    pdfmetrics.registerFont(TTFont('Arial', arial_path))
    
    # Настройка шрифта для заголовка
    c.setFont('Arial', 20)
    
    # Заголовок
    c.drawString(2*cm, height-3*cm, "Чек заказа")
    
    # Основная информация - уменьшаем шрифт и межстрочный интервал
    c.setFont('Arial', 10)
    line_height = 0.5*cm  # Уменьшаем межстрочный интервал
    section_spacing = 0.8*cm  # Отступ между секциями
    y = height - 4*cm
    
    # Информация о заказе
    c.drawString(2*cm, y, f"Номер заказа: {order.id}")
    y -= line_height
    c.drawString(2*cm, y, f"Дата заказа: {order.order_date.strftime('%d.%m.%Y %H:%M')}")
    y -= line_height
    c.drawString(2*cm, y, f"Статус: {order.get_status_display()}")
    y -= section_spacing
    
    # Информация о клиенте
    c.setFont('Arial', 11)  # Немного увеличиваем шрифт для подзаголовков
    c.drawString(2*cm, y, "Информация о клиенте:")
    c.setFont('Arial', 10)  # Возвращаем обычный размер
    y -= line_height
    c.drawString(2*cm, y, f"Имя: {order.client.name}")
    y -= line_height
    c.drawString(2*cm, y, f"Телефон: {order.client.phone}")
    y -= section_spacing
    
    # Информация об услуге
    c.setFont('Arial', 11)
    c.drawString(2*cm, y, "Информация об услуге:")
    c.setFont('Arial', 10)
    y -= line_height
    c.drawString(2*cm, y, f"Услуга: {order.service.name}")
    y -= line_height
    c.drawString(2*cm, y, f"Мастер: {order.barber.name}")
    y -= line_height
    c.drawString(2*cm, y, f"Дата записи: {order.appointment_date.strftime('%d.%m.%Y')}")
    y -= line_height
    c.drawString(2*cm, y, f"Время записи: {order.appointment_time.strftime('%H:%M')}")
    y -= section_spacing
    
    # Информация о стоимости
    c.setFont('Arial', 11)
    c.drawString(2*cm, y, "Стоимость:")
    c.setFont('Arial', 10)
    y -= line_height
    c.drawString(2*cm, y, f"Базовая стоимость: {order.service.price} руб.")
    if order.discount:
        y -= line_height
        c.drawString(2*cm, y, f"Скидка: {order.discount.discount_percent}%")
    y -= line_height
    c.drawString(2*cm, y, f"Итоговая стоимость: {order.total_price} руб.")
    
    # Подпись
    y -= section_spacing
    c.line(2*cm, y, width-2*cm, y)
    y -= line_height
    c.drawString(2*cm, y, "Спасибо за ваш заказ!")
    
    # Сохраняем PDF
    c.save() 