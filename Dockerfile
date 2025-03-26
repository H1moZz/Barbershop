# Используем Python 3.9
FROM python:3.9-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        python3-pip \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем директорию для статических файлов
RUN mkdir -p /app/staticfiles /app/media

# Даем права на запись
RUN chmod -R 755 /app/staticfiles /app/media

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 