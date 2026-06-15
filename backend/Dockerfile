FROM python:3.11-slim

# Java is required by apktool and jadx
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jre-headless \
    unzip \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Fetch apktool and jadx into tools/ (gitignored, not committed)
RUN mkdir -p tools && \
    wget -q -O tools/apktool.jar https://github.com/iBotPeaches/Apktool/releases/download/v2.9.3/apktool_2.9.3.jar && \
    wget -q -O /tmp/jadx.zip https://github.com/skylot/jadx/releases/download/v1.5.0/jadx-1.5.0.zip && \
    unzip -q /tmp/jadx.zip -d tools/jadx && \
    rm /tmp/jadx.zip && \
    chmod +x tools/jadx/bin/jadx tools/jadx/bin/jadx-gui

COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

COPY . .

ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
