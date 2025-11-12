###OLD SLOW and BIG BUILD

# FROM python:3.10
# WORKDIR /app
# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt
# COPY . .
# CMD ["python","app.py"]



# Build stage
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Runtime stage
FROM gcr.io/distroless/python3-debian12

WORKDIR /app
COPY --from=builder /app /app

CMD ["python3", "app.py"]