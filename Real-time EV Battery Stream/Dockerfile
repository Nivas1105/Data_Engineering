FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY logger.py .
COPY certs/ ./certs/
CMD ["python", "logger.py"]