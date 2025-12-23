# 1. Base image Python
FROM python:3.12-slim

# 2. Cài thư viện hệ thống cần thiết để build một số package native
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Set working directory trong container
WORKDIR /app

# 4. Copy requirements và cài đặt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy toàn bộ source code backend vào container
COPY . .


