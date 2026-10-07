FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    DB_PATH=/data/journal.db

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Non-root user, and a /data folder it owns (this is where the volume mounts).
RUN useradd --uid 1000 appuser && mkdir /data && chown appuser /data
USER appuser

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]