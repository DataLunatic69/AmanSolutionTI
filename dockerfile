
FROM python:3.11-slim


WORKDIR /app


RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*


COPY pyproject.toml .


RUN pip install --no-cache-dir flask flask-sqlalchemy gunicorn requests pyyaml aiohttp email-validator psycopg2-binary


COPY . .


RUN mkdir -p logs


ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV PORT=5000


EXPOSE 5000


CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "main:app"]