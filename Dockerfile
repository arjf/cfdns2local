FROM python:3.11-slim as builder
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -t /app

COPY cfdns2local.py .
RUN chmod +x cfdns2local.py

FROM gcr.io/distroless/python3
WORKDIR /app
COPY --from=builder /app /app
ENV PYTHONUNBUFFERED=1
CMD ["cfdns2local.py"]
