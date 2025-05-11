FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN python manage.py migrate --noinput

RUN python manage.py collectstatic --noinput --clear

COPY entrypoint.sh /app/entrypoint.sh
COPY wait_for_db.py /app/wait_for_db.py 
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

CMD ["gunicorn", "banco_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2", "--worker-tmp-dir", "/dev/shm"]