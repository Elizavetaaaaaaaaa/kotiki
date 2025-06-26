FROM python:3.11-alpine

# Установка зависимостей системы
RUN apk add --no-cache gcc musl-dev

WORKDIR /app

# Копируем файл с зависимостями и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Создаём директорию для базы данных и даём права
RUN mkdir -p /app/data

# Копируем исходники приложения
COPY app.py .
COPY wsgi.py .

# Указываем команду запуска Gunicorn с eventlet для поддержки WebSocket
CMD ["gunicorn", "-w", "1", "-k", "eventlet", "-b", "0.0.0.0:5000", "wsgi:application"]
