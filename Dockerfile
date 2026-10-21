FROM python:3.11-slim

WORKDIR /BOT_LUMOS


COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


COPY . .

# Порт для Render
EXPOSE 8080

CMD ["python", "main.py"]