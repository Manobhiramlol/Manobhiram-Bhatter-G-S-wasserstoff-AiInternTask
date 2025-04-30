FROM python:3.9-slim

WORKDIR /app

COPY backend/ .

RUN pip install --no-cache-dir -r requirements.txt

COPY backend /app/backend

EXPOSE 8000

ENV PYTHONUNBUFFERED 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]