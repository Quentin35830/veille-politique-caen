FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "mistralai>=1.5.0" "mistralai-workflows[mistralai]"

COPY src/ ./src/

CMD ["python", "src/entrypoints/worker.py"]
