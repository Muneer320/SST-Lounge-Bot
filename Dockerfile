FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.lock.txt ./
RUN python -m pip install --no-cache-dir -r requirements.lock.txt

COPY . .
RUN mkdir -p /app/database /app/logs && \
    useradd --create-home bot && \
    chown -R bot:bot /app/database /app/logs
USER bot

CMD ["python", "run.py"]
