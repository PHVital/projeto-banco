#!/bin/sh

python /app/wait_for_db.py # Chame o script Python

echo "Aplicando migrações do banco de dados..."
python manage.py migrate --noinput

echo "Iniciando Gunicorn..."
# Use exec para que Gunicorn se torne o processo principal (PID 1) e receba sinais corretamente
exec gunicorn banco_project.wsgi:application --bind 0.0.0.0:8000 --workers 2 --threads 2 --worker-tmp-dir /dev/shm